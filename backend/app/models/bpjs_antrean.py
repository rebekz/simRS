"""BPJS Antrean Database Models

Modul ini mendefinisikan model database untuk mengelola sinkronisasi antrian BPJS
(Badan Penyelenggara Jaminan Sosial) melalui API Antrean, termasuk pencatatan
panggilan API, manajemen booking Mobile JKN, pelacakan status, dan manajemen tugas.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from app.db.session import Base


class BPJSSyncStatus(str, Enum):
    """Status sinkronisasi API BPJS"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class BPJSBookingStatus(str, Enum):
    """Status booking antrian BPJS"""
    BOOKED = "booked"
    CHECKED_IN = "checked-in"
    SERVING = "serving"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BPJSTaskType(str, Enum):
    """Jenis tugas antrian BPJS"""
    REGISTRATION = "registration"
    CONSULTATION = "consultation"
    PHARMACY = "pharmacy"
    LAB = "lab"


class BPJSTaskStatus(str, Enum):
    """Status tugas antrian BPJS"""
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"


class BPJSAntreanSyncLog(Base):
    """Model Log Sinkronisasi BPJS Antrean untuk audit trail pemanggilan API

    Model ini menyimpan riwayat panggilan API BPJS Antrean, termasuk
    data request/response, pelacakan error, dan informasi percobaan ulang.
    """
    __tablename__ = "bpjs_antrean_sync_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Detail endpoint API
    endpoint = Column(String(255), nullable=False, index=True, comment="Endpoint API BPJS yang dipanggil")
    http_method = Column(String(10), nullable=False, comment="HTTP method (GET, POST, PUT, DELETE)")

    # Data request dan response
    request_payload = Column(JSON, nullable=True, comment="Payload request yang dikirim ke API BPJS")
    response_payload = Column(JSON, nullable=True, comment="Response yang diterima dari API BPJS")

    # Status pemanggilan
    status = Column(String(20), nullable=False, index=True, comment="Status sinkronisasi (success, failed, pending)")
    http_status_code = Column(Integer, nullable=True, comment="HTTP status code dari response")
    bpjs_response_code = Column(String(20), nullable=True, comment="Kode response spesifik dari BPJS")

    # Error tracking
    error_message = Column(Text, nullable=True, comment="Pesan error jika terjadi kegagalan")
    retry_count = Column(Integer, nullable=False, default=0, comment="Jumlah percobaan ulang")

    # Metadata tambahan
    execution_time_ms = Column(Integer, nullable=True, comment="Waktu eksekusi dalam milidetik")
    referenced_entity_type = Column(String(50), nullable=True, comment="Tipe entitas yang terkait (booking, task, dll)")
    referenced_entity_id = Column(Integer, nullable=True, comment="ID entitas yang terkait")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Timestamp pembuatan record")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Timestamp update terakhir record")

    # Indexes
    __table_args__ = (
        Index("ix_bpjs_antrean_sync_logs_endpoint", "endpoint"),
        Index("ix_bpjs_antrean_sync_logs_status", "status"),
        Index("ix_bpjs_antrean_sync_logs_created_at", "created_at"),
        Index("ix_bpjs_antrean_sync_logs_referenced_entity", "referenced_entity_type", "referenced_entity_id"),
    )


class BPJSAntreanBooking(Base):
    """Model Booking Antrian BPJS untuk manajemen booking Mobile JKN

    Model ini menyimpan data booking antrian dari aplikasi Mobile JKN,
    termasuk detail pasien, poli, dokter, jadwal, dan status pelacakan
    selama proses pelayanan.
    """
    __tablename__ = "bpjs_antrean_bookings"

    id = Column(Integer, primary_key=True, index=True)

    # Identifikasi booking
    booking_code = Column(String(100), unique=True, nullable=False, index=True, comment="Kode booking dari BPJS")
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True, index=True, comment="Referensi ke appointment internal")

    # Referensi ke entitas lain
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True, comment="Referensi ke pasien")
    # TODO: poli_id = Column(Integer, ForeignKey("polis.id", ondelete="RESTRICT"), nullable=False, index=True) - Poli model not yet defined
    poli_id = Column(Integer, nullable=False, index=True, comment="Poli ID (reference to Poli model when implemented)")
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="Referensi ke dokter")

    # Jadwal booking
    booking_date = Column(DateTime(timezone=True), nullable=False, index=True, comment="Tanggal dan waktu booking")
    booking_time = Column(Time, nullable=False, comment="Waktu booking")
    estimated_time = Column(DateTime(timezone=True), nullable=True, comment="Perkiraan waktu pelayanan")

    # Status dan workflow
    status = Column(String(20), nullable=False, index=True, default="booked", comment="Status booking (booked, checked-in, serving, completed, cancelled)")

    # Informasi BPJS
    bpjs_task_id = Column(Integer, nullable=True, index=True, comment="ID tugas dari sistem BPJS")
    referral_number = Column(String(100), nullable=True, index=True, comment="Nomor rujukan BPJS")
    sep_number = Column(String(50), nullable=True, index=True, comment="Nomor SEP (Surat Eligibilitas Peserta)")

    # Pelacakan waktu pelayanan
    checkin_time = Column(DateTime(timezone=True), nullable=True, comment="Waktu check-in pasien")
    service_start_time = Column(DateTime(timezone=True), nullable=True, comment="Waktu mulai pelayanan")
    service_end_time = Column(DateTime(timezone=True), nullable=True, comment="Waktu selesai pelayanan")

    # Sinkronisasi dengan BPJS
    sync_status = Column(String(20), nullable=False, default="pending", comment="Status sinkronisasi dengan BPJS")
    last_sync_at = Column(DateTime(timezone=True), nullable=True, comment="Timestamp sinkronisasi terakhir")
    sync_error_message = Column(Text, nullable=True, comment="Pesan error dari sinkronisasi BPJS")

    # Metadata tambahan
    bpjs_response_data = Column(JSON, nullable=True, comment="Response data lengkap dari BPJS")
    cancellation_reason = Column(Text, nullable=True, comment="Alasan pembatalan booking")
    cancelled_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="User yang membatalkan")
    cancelled_at = Column(DateTime(timezone=True), nullable=True, comment="Timestamp pembatalan")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Timestamp pembuatan record")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Timestamp update terakhir record")

    # Relationships
    appointment = relationship("Appointment", backref="bpjs_antrean_booking")
    patient = relationship("Patient", backref="bpjs_antrean_bookings")
    # TODO: poli = relationship("Poli", backref="bpjs_antrean_bookings") - Poli model not yet defined
    # TODO: doctor = relationship("Doctor", backref="bpjs_antrean_bookings") - Doctor model not yet defined (use User instead)
    canceller = relationship("User", foreign_keys=[cancelled_by])
    tasks = relationship("BPJSAntreanTask", back_populates="booking", cascade="all, delete-orphan")
    status_updates = relationship("BPJSAntreanStatusUpdate", back_populates="booking", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_bpjs_antrean_bookings_booking_code", "booking_code"),
        Index("ix_bpjs_antrean_bookings_appointment_id", "appointment_id"),
        Index("ix_bpjs_antrean_bookings_patient_id", "patient_id"),
        Index("ix_bpjs_antrean_bookings_poli_id", "poli_id"),
        Index("ix_bpjs_antrean_bookings_doctor_id", "doctor_id"),
        Index("ix_bpjs_antrean_bookings_booking_date", "booking_date"),
        Index("ix_bpjs_antrean_bookings_status", "status"),
        Index("ix_bpjs_antrean_bookings_bpjs_task_id", "bpjs_task_id"),
        Index("ix_bpjs_antrean_bookings_referral_number", "referral_number"),
        Index("ix_bpjs_antrean_bookings_sep_number", "sep_number"),
    )


class BPJSAntreanTask(Base):
    """Model Tugas Antrian BPJS untuk manajemen tugas pelayanan

    Model ini menyimpan tugas-tugas yang terkait dengan booking antrian,
    seperti registrasi, konsultasi, farmasi, atau laboratorium dengan
    pelacakan status dan estimasi waktu.
    """
    __tablename__ = "bpjs_antrean_tasks"

    id = Column(Integer, primary_key=True, index=True)

    # Referensi ke booking
    booking_id = Column(Integer, ForeignKey("bpjs_antrean_bookings.id", ondelete="CASCADE"), nullable=False, index=True, comment="Referensi ke booking BPJS")

    # Identifikasi tugas
    task_id = Column(String(100), nullable=False, index=True, comment="ID tugas dari sistem BPJS")
    task_name = Column(String(255), nullable=False, comment="Nama tugas")

    # Klasifikasi tugas
    task_type = Column(String(20), nullable=False, index=True, comment="Jenis tugas (registration, consultation, pharmacy, lab)")

    # Status dan antrian
    status = Column(String(20), nullable=False, index=True, default="waiting", comment="Status tugas (waiting, active, completed)")
    queue_number = Column(Integer, nullable=True, comment="Nomor antrian")
    estimated_time = Column(DateTime(timezone=True), nullable=True, comment="Perkiraan waktu pelayanan")

    # Referensi ke entitas internal
    encounter_id = Column(Integer, ForeignKey("encounters.id", ondelete="SET NULL"), nullable=True, index=True, comment="Referensi ke encounter/kunjungan")
    prescription_id = Column(Integer, ForeignKey("prescriptions.id", ondelete="SET NULL"), nullable=True, index=True, comment="Referensi ke resep (untuk task farmasi)")
    lab_order_id = Column(Integer, ForeignKey("lab_orders.id", ondelete="SET NULL"), nullable=True, index=True, comment="Referensi ke pemeriksaan lab")

    # Pelacakan waktu
    started_at = Column(DateTime(timezone=True), nullable=True, comment="Waktu mulai pengerjaan tugas")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="Waktu selesai pengerjaan tugas")

    # Metadata tambahan
    bpjs_response_data = Column(JSON, nullable=True, comment="Response data lengkap dari BPJS")
    notes = Column(Text, nullable=True, comment="Catatan tambahan untuk tugas")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Timestamp pembuatan record")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Timestamp update terakhir record")

    # Relationships
    booking = relationship("BPJSAntreanBooking", back_populates="tasks")
    encounter = relationship("Encounter", backref="bpjs_antrean_tasks")
    prescription = relationship("Prescription", backref="bpjs_antrean_tasks")
    lab_order = relationship("LabOrder", backref="bpjs_antrean_tasks")

    # Indexes
    __table_args__ = (
        Index("ix_bpjs_antrean_tasks_booking_id", "booking_id"),
        Index("ix_bpjs_antrean_tasks_task_id", "task_id"),
        Index("ix_bpjs_antrean_tasks_task_type", "task_type"),
        Index("ix_bpjs_antrean_tasks_status", "status"),
        Index("ix_bpjs_antrean_tasks_encounter_id", "encounter_id"),
        Index("ix_bpjs_antrean_tasks_prescription_id", "prescription_id"),
        Index("ix_bpjs_antrean_tasks_lab_order_id", "lab_order_id"),
    )


class BPJSAntreanStatusUpdate(Base):
    """Model Update Status Antrian BPJS untuk pelacakan perubahan status

    Model ini menyimpan riwayat perubahan status booking antrian,
    termasuk respons dari BPJS dan pelacakan sinkronisasi.
    """
    __tablename__ = "bpjs_antrean_status_updates"

    id = Column(Integer, primary_key=True, index=True)

    # Referensi ke booking
    booking_id = Column(Integer, ForeignKey("bpjs_antrean_bookings.id", ondelete="CASCADE"), nullable=False, index=True, comment="Referensi ke booking BPJS")

    # Perubahan status
    old_status = Column(String(20), nullable=False, comment="Status sebelumnya")
    new_status = Column(String(20), nullable=False, index=True, comment="Status baru")

    # Waktu update
    update_time = Column(DateTime(timezone=True), nullable=False, index=True, comment="Waktu perubahan status")

    # Sinkronisasi dengan BPJS
    sync_status = Column(String(20), nullable=False, default="pending", comment="Status sinkronisasi dengan BPJS")

    # Respons BPJS
    bpjs_response = Column(JSON, nullable=True, comment="Respons lengkap dari API BPJS")
    error_message = Column(Text, nullable=True, comment="Pesan error jika sinkronisasi gagal")

    # Metadata tambahan
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="User yang melakukan update status")
    update_source = Column(String(50), nullable=False, default="system", comment="Sumber update (system, mobile_jkn, manual)")
    notes = Column(Text, nullable=True, comment="Catatan tambahan untuk update status")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Timestamp pembuatan record")

    # Relationships
    booking = relationship("BPJSAntreanBooking", back_populates="status_updates")
    updater = relationship("User", foreign_keys=[updated_by])

    # Indexes
    __table_args__ = (
        Index("ix_bpjs_antrean_status_updates_booking_id", "booking_id"),
        Index("ix_bpjs_antrean_status_updates_new_status", "new_status"),
        Index("ix_bpjs_antrean_status_updates_update_time", "update_time"),
        Index("ix_bpjs_antrean_status_updates_created_at", "created_at"),
    )
