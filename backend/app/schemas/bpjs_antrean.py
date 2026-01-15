"""BPJS Antrean schemas for online queue registration and management.

This module defines Pydantic schemas for BPJS Antrean (online queue) integration,
including booking registration, queue status updates, task management, and
synchronization logs.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class BookingStatus(str, Enum):
    """Statuses for BPJS queue bookings"""
    BOOKED = "booked"
    CHECKED_IN = "checked_in"
    SERVING = "serving"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """Types of tasks in queue workflow"""
    REGISTRATION = "registration"
    CONSULTATION = "consultation"
    PHARMACY = "pharmacy"
    LAB = "lab"
    RADIOLOGY = "radiology"


class TaskStatus(str, Enum):
    """Statuses for individual tasks"""
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SyncStatus(str, Enum):
    """Statuses for BPJS synchronization"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


# =============================================================================
# Request Schemas for BPJS API Integration
# =============================================================================

class AntreanUpdateRequest(BaseModel):
    """Schema for updating queue status via BPJS API"""
    kodebooking: str = Field(..., min_length=1, max_length=50, description="Kode booking dari BPJS")
    jenispoli: str = Field(..., min_length=1, max_length=50, description="Jenis poli")
    kodepoli: str = Field(..., min_length=1, max_length=10, description="Kode poli faskes")
    nomorantrean: int = Field(..., ge=1, description="Nomor antrian")
    angkaantrean: int = Field(..., ge=1, description="Angka antrian")
    keterangan: Optional[str] = Field(None, max_length=255, description="Keterangan status")
    status: int = Field(..., ge=0, le=100, description="Status antrian (0-100)")

    @validator('kodebooking')
    def validate_kodebooking(cls, v):
        """Validate booking code format"""
        if not v or not v.strip():
            raise ValueError('Kode booking tidak boleh kosong')
        return v.strip().upper()

    @validator('status')
    def validate_status(cls, v):
        """Validate status is within valid range"""
        if not 0 <= v <= 100:
            raise ValueError('Status harus bernilai 0-100')
        return v


class AntreanSisaRequest(BaseModel):
    """Schema for requesting remaining queue count via BPJS API"""
    kodepoli: str = Field(..., min_length=1, max_length=10, description="Kode poli faskes")
    tanggalperiksa: date = Field(..., description="Tanggal periksa")

    @validator('kodepoli')
    def validate_kodepoli(cls, v):
        """Validate poli code format"""
        if not v or not v.strip():
            raise ValueError('Kode poli tidak boleh kosong')
        return v.strip().upper()


class AntreanListRequest(BaseModel):
    """Schema for requesting queue list via BPJS API"""
    kodepoli: Optional[str] = Field(None, max_length=10, description="Kode poli faskes (opsional)")
    tanggalperiksa: Optional[date] = Field(None, description="Tanggal periksa (opsional)")

    @validator('kodepoli')
    def validate_kodepoli(cls, v):
        """Validate poli code format if provided"""
        if v is not None and not v.strip():
            raise ValueError('Kode poli tidak valid')
        return v.strip().upper() if v else None


class AntreanBatalRequest(BaseModel):
    """Schema for cancelling booking via BPJS API"""
    kodebooking: str = Field(..., min_length=1, max_length=50, description="Kode booking yang akan dibatalkan")
    keterangan: Optional[str] = Field(None, max_length=255, description="Alasan pembatalan")

    @validator('kodebooking')
    def validate_kodebooking(cls, v):
        """Validate booking code format"""
        if not v or not v.strip():
            raise ValueError('Kode booking tidak boleh kosong')
        return v.strip().upper()


class AntreanCheckinRequest(BaseModel):
    """Schema for patient check-in via BPJS API"""
    kodebooking: str = Field(..., min_length=1, max_length=50, description="Kode booking untuk check-in")
    waktu: datetime = Field(..., description="Waktu check-in")
    jenispoli: str = Field(..., min_length=1, max_length=50, description="Jenis poli")

    @validator('kodebooking')
    def validate_kodebooking(cls, v):
        """Validate booking code format"""
        if not v or not v.strip():
            raise ValueError('Kode booking tidak boleh kosong')
        return v.strip().upper()


class AntreanKesimpulanRequest(BaseModel):
    """Schema for completing service via BPJS API"""
    kodebooking: str = Field(..., min_length=1, max_length=50, description="Kode booking yang selesai")
    hasilpelayanan: str = Field(..., min_length=1, max_length=1000, description="Hasil pelayanan")
    keterangan: Optional[str] = Field(None, max_length=255, description="Keterangan tambahan")

    @validator('kodebooking')
    def validate_kodebooking(cls, v):
        """Validate booking code format"""
        if not v or not v.strip():
            raise ValueError('Kode booking tidak boleh kosong')
        return v.strip().upper()

    @validator('hasilpelayanan')
    def validate_hasilpelayanan(cls, v):
        """Validate service result is not empty"""
        if not v or not v.strip():
            raise ValueError('Hasil pelayanan tidak boleh kosong')
        return v.strip()


# =============================================================================
# Response Schemas for BPJS API Integration
# =============================================================================

class AntreanUpdateResponse(BaseModel):
    """Schema for update queue status response from BPJS"""
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata response dari BPJS")
    response: Optional[Dict[str, Any]] = Field(None, description="Response detail dari BPJS")
    success: bool = Field(..., description="Status keberhasilan update")
    message: str = Field(..., description="Pesan response")


class AntreanSisaResponse(BaseModel):
    """Schema for remaining queue info response from BPJS"""
    nomorantrean: int = Field(..., ge=0, description="Nomor antrian terakhir")
    sisaantrean: int = Field(..., ge=0, description="Sisa antrian")
    antreanpanggil: Optional[int] = Field(None, ge=0, description="Antrian yang sedang dipanggil")
    keterangan: Optional[str] = Field(None, description="Keterangan tambahan")
    totalantrean: int = Field(..., ge=0, description="Total antrian")


class AntreanListResponse(BaseModel):
    """Schema for queue list response from BPJS"""
    list: Optional[List[Dict[str, Any]]] = Field(None, description="Daftar antrian")
    total: int = Field(..., ge=0, description="Total antrian")
    tanggalperiksa: date = Field(..., description="Tanggal periksa")
    kodepoli: str = Field(..., description="Kode poli")


class AntreanStatusResponse(BaseModel):
    """Schema for general status response from BPJS"""
    status: bool = Field(..., description="Status response dari BPJS")
    message: str = Field(..., description="Pesan status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata tambahan")
    data: Optional[Dict[str, Any]] = Field(None, description="Data tambahan")


class AntreanErrorResponse(BaseModel):
    """Schema for error response from BPJS API"""
    status: bool = Field(False, description="Status error")
    message: str = Field(..., description="Pesan error")
    error_code: Optional[str] = Field(None, description="Kode error BPJS")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata error")


# =============================================================================
# Internal Schemas for BPJSAntreanBooking
# =============================================================================

class BPJSAntreanBookingBase(BaseModel):
    """Base BPJS antrean booking schema"""
    patient_id: int = Field(..., description="ID pasien")
    booking_code: str = Field(..., min_length=1, max_length=50, description="Kode booking dari BPJS")
    poli_code: str = Field(..., min_length=1, max_length=10, description="Kode poli faskes")
    poli_name: str = Field(..., min_length=1, max_length=100, description="Nama poli")
    doctor_code: Optional[str] = Field(None, max_length=20, description="Kode dokter")
    doctor_name: Optional[str] = Field(None, max_length=255, description="Nama dokter")
    appointment_date: date = Field(..., description="Tanggal janji temu")
    appointment_time: str = Field(..., min_length=1, max_length=10, description="Jam janji temu")
    queue_number: int = Field(..., ge=1, description="Nomor antrian")
    queue_angka: int = Field(..., ge=1, description="Angka antrian")
    booking_status: BookingStatus = Field(..., description="Status booking")
    bpjs_card_number: str = Field(..., min_length=13, max_length=13, description="Nomor kartu BPJS")
    referral_number: Optional[str] = Field(None, max_length=50, description="Nomor rujukan")
    notes: Optional[str] = Field(None, max_length=500, description="Catatan tambahan")
    checkin_time: Optional[datetime] = Field(None, description="Waktu check-in")
    service_start_time: Optional[datetime] = Field(None, description="Waktu mulai pelayanan")
    service_end_time: Optional[datetime] = Field(None, description="Waktu selesai pelayanan")
    bpjs_sync_status: SyncStatus = Field(default=SyncStatus.PENDING, description="Status sinkronisasi BPJS")
    bpjs_sync_message: Optional[str] = Field(None, max_length=500, description="Pesan sinkronisasi BPJS")

    @validator('booking_code')
    def validate_booking_code(cls, v):
        """Validate booking code format"""
        if not v or not v.strip():
            raise ValueError('Kode booking tidak boleh kosong')
        return v.strip().upper()

    @validator('bpjs_card_number')
    def validate_bpjs_card_number(cls, v):
        """Validate BPJS card number is 13 digits"""
        if not v.isdigit():
            raise ValueError('Nomor kartu BPJS harus berisi angka saja')
        if len(v) != 13:
            raise ValueError('Nomor kartu BPJS harus 13 digit')
        return v

    @validator('poli_code')
    def validate_poli_code(cls, v):
        """Validate poli code format"""
        if not v or not v.strip():
            raise ValueError('Kode poli tidak boleh kosong')
        return v.strip().upper()

    @validator('service_end_time')
    def validate_service_end_time(cls, v, values):
        """Validate service end time is after start time"""
        if v is not None and 'service_start_time' in values:
            start_time = values.get('service_start_time')
            if start_time is not None and v < start_time:
                raise ValueError('Waktu selesai tidak boleh sebelum waktu mulai')
        return v


class BPJSAntreanBookingCreate(BPJSAntreanBookingBase):
    """Schema for creating BPJS antrean booking"""
    tasks: Optional[List['BPJSAntreanTaskCreate']] = Field(default_factory=list)


class BPJSAntreanBookingUpdate(BaseModel):
    """Schema for updating BPJS antrean booking"""
    poli_code: Optional[str] = Field(None, min_length=1, max_length=10)
    poli_name: Optional[str] = Field(None, min_length=1, max_length=100)
    doctor_code: Optional[str] = Field(None, max_length=20)
    doctor_name: Optional[str] = Field(None, max_length=255)
    appointment_date: Optional[date] = None
    appointment_time: Optional[str] = Field(None, min_length=1, max_length=10)
    booking_status: Optional[BookingStatus] = None
    referral_number: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)
    checkin_time: Optional[datetime] = None
    service_start_time: Optional[datetime] = None
    service_end_time: Optional[datetime] = None
    bpjs_sync_status: Optional[SyncStatus] = None
    bpjs_sync_message: Optional[str] = Field(None, max_length=500)
    tasks: Optional[List['BPJSAntreanTaskCreate']] = None

    @validator('poli_code')
    def validate_poli_code(cls, v):
        """Validate poli code format if provided"""
        if v is not None and not v.strip():
            raise ValueError('Kode poli tidak valid')
        return v.strip().upper() if v else None


class BPJSAntreanBookingResponse(BPJSAntreanBookingBase):
    """Schema for BPJS antrean booking response"""
    id: int
    tasks: List['BPJSAntreanTaskResponse'] = Field(default_factory=list)
    sync_logs: List['BPJSAntreanSyncLogResponse'] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


# =============================================================================
# Internal Schemas for BPJSAntreanTask
# =============================================================================

class BPJSAntreanTaskBase(BaseModel):
    """Base BPJS antrean task schema"""
    booking_id: int = Field(..., description="ID booking terkait")
    task_type: TaskType = Field(..., description="Jenis tugas")
    task_name: str = Field(..., min_length=1, max_length=255, description="Nama tugas")
    task_order: int = Field(..., ge=1, description="Urutan tugas")
    task_status: TaskStatus = Field(default=TaskStatus.WAITING, description="Status tugas")
    assigned_to: Optional[int] = Field(None, description="ID user yang ditugaskan")
    start_time: Optional[datetime] = Field(None, description="Waktu mulai tugas")
    end_time: Optional[datetime] = Field(None, description="Waktu selesai tugas")
    notes: Optional[str] = Field(None, max_length=500, description="Catatan tugas")

    @validator('task_name')
    def validate_task_name(cls, v):
        """Validate task name is not empty"""
        if not v or not v.strip():
            raise ValueError('Nama tugas tidak boleh kosong')
        return v.strip()

    @validator('end_time')
    def validate_end_time(cls, v, values):
        """Validate end time is after start time"""
        if v is not None and 'start_time' in values:
            start_time = values.get('start_time')
            if start_time is not None and v < start_time:
                raise ValueError('Waktu selesai tidak boleh sebelum waktu mulai')
        return v


class BPJSAntreanTaskCreate(BPJSAntreanTaskBase):
    """Schema for creating BPJS antrean task"""
    pass


class BPJSAntreanTaskUpdate(BaseModel):
    """Schema for updating BPJS antrean task"""
    task_type: Optional[TaskType] = None
    task_name: Optional[str] = Field(None, min_length=1, max_length=255)
    task_order: Optional[int] = Field(None, ge=1)
    task_status: Optional[TaskStatus] = None
    assigned_to: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)

    @validator('task_name')
    def validate_task_name(cls, v):
        """Validate task name if provided"""
        if v is not None and not v.strip():
            raise ValueError('Nama tugas tidak valid')
        return v.strip() if v else None


class BPJSAntreanTaskResponse(BPJSAntreanTaskBase):
    """Schema for BPJS antrean task response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Internal Schemas for BPJSAntreanSyncLog
# =============================================================================

class BPJSAntreanSyncLogBase(BaseModel):
    """Base BPJS antrean sync log schema"""
    booking_id: int = Field(..., description="ID booking terkait")
    sync_type: str = Field(..., min_length=1, max_length=50, description="Jenis sinkronisasi")
    endpoint: str = Field(..., min_length=1, max_length=255, description="Endpoint BPJS API")
    request_payload: Dict[str, Any] = Field(..., description="Payload request ke BPJS")
    response_code: Optional[str] = Field(None, max_length=50, description="Kode response BPJS")
    response_body: Optional[Dict[str, Any]] = Field(None, description="Body response dari BPJS")
    sync_status: SyncStatus = Field(..., description="Status sinkronisasi")
    error_message: Optional[str] = Field(None, max_length=1000, description="Pesan error jika gagal")
    processing_time_ms: Optional[int] = Field(None, ge=0, description="Waktu proses dalam milidetik")
    synced_at: datetime = Field(..., description="Waktu sinkronisasi")
    synced_by: int = Field(..., description="ID user yang melakukan sinkronisasi")

    @validator('processing_time_ms')
    def validate_processing_time(cls, v):
        """Validate processing time is reasonable (max 5 minutes)"""
        if v is not None and v > 5 * 60 * 1000:
            raise ValueError('Waktu proses tidak boleh lebih dari 5 menit')
        return v


class BPJSAntreanSyncLogCreate(BPJSAntreanSyncLogBase):
    """Schema for creating BPJS antrean sync log"""
    pass


class BPJSAntreanSyncLogResponse(BPJSAntreanSyncLogBase):
    """Schema for BPJS antrean sync log response"""
    id: int

    class Config:
        from_attributes = True


# =============================================================================
# Statistics and Analytics Schemas
# =============================================================================

class AntreanStatistics(BaseModel):
    """Schema for BPJS antrean statistics"""
    total_bookings: int = Field(..., description="Total booking antrian")
    bookings_by_status: Dict[str, int] = Field(default_factory=dict, description="Booking berdasarkan status")
    bookings_by_poli: Dict[str, int] = Field(default_factory=dict, description="Booking berdasarkan poli")
    today_bookings: int = Field(..., description="Booking hari ini")
    today_checked_in: int = Field(..., description="Pasien check-in hari ini")
    today_completed: int = Field(..., description="Pasien selesai dilayani hari ini")
    today_cancelled: int = Field(..., description="Booking dibatalkan hari ini")
    current_month_bookings: int = Field(..., description="Booking bulan ini")
    previous_month_bookings: int = Field(..., description="Booking bulan lalu")
    average_waiting_time_minutes: Optional[int] = Field(None, ge=0, description="Rata-rata waktu tunggu dalam menit")
    average_service_time_minutes: Optional[int] = Field(None, ge=0, description="Rata-rata waktu pelayanan dalam menit")
    sync_success_rate: Optional[float] = Field(None, ge=0, le=100, description="Tingkat keberhasilan sinkronisasi")
    active_tasks: int = Field(default=0, description="Tugas yang sedang aktif")
    pending_tasks: int = Field(default=0, description="Tugas yang menunggu")


class AntreanDashboardData(BaseModel):
    """Schema for comprehensive antrean dashboard data"""
    statistics: AntreanStatistics = Field(..., description="Statistik antrian")
    recent_bookings: List[BPJSAntreanBookingResponse] = Field(..., description="Booking terbaru")
    upcoming_appointments: List[BPJSAntreanBookingResponse] = Field(..., description="Janji temu mendatang")
    active_tasks: List[BPJSAntreanTaskResponse] = Field(..., description="Tugas aktif")
    poli_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribusi poli")
    hourly_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribusi per jam")
    status_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribusi status")


class AntreanValidationResult(BaseModel):
    """Schema for antrean booking validation result"""
    is_valid: bool = Field(..., description="Status validasi keseluruhan")
    validation_errors: List[str] = Field(default_factory=list, description="Daftar error validasi")
    validation_warnings: List[str] = Field(default_factory=list, description="Daftar warning validasi")
    can_book: bool = Field(..., description="Status apakah bisa melakukan booking")
    missing_requirements: List[str] = Field(default_factory=list, description="Persyaratan yang kurang")
    invalid_fields: Dict[str, str] = Field(default_factory=dict, description="Field yang tidak valid dan alasannya")
    available_slots: Optional[int] = Field(None, ge=0, description="Slot tersedia")
    estimated_queue_number: Optional[int] = Field(None, ge=1, description="Perkiraan nomor antrian")


class AntreanBookingResult(BaseModel):
    """Schema for antrean booking result"""
    success: bool = Field(..., description="Status keberhasilan booking")
    booking_id: int = Field(..., description="ID booking internal")
    booking_code: str = Field(..., description="Kode booking BPJS")
    queue_number: int = Field(..., description="Nomor antrian")
    queue_angka: int = Field(..., description="Angka antrian")
    estimated_wait_time_minutes: Optional[int] = Field(None, ge=0, description="Perkiraan waktu tunggu dalam menit")
    appointment_datetime: datetime = Field(..., description="Waktu janji temu")
    bpjs_response_code: Optional[str] = Field(None, description="Kode response BPJS")
    bpjs_response_message: Optional[str] = Field(None, description="Pesan response BPJS")
    next_action: Optional[str] = Field(None, description="Aksi selanjutnya yang disarankan")
    instructions: List[str] = Field(default_factory=list, description="Instruksi untuk pasien")


# =============================================================================
# Additional Helper Schemas
# =============================================================================

class AntreanPoliInfo(BaseModel):
    """Schema for poli information from BPJS"""
    kodepoli: str = Field(..., description="Kode poli")
    namapoli: str = Field(..., description="Nama poli")
    kodesubspesialis: Optional[str] = Field(None, description="Kode subspesialis")
    namasubspesialis: Optional[str] = Field(None, description="Nama subspesialis")
    kapasitas: int = Field(..., ge=1, description="Kapasitas poli")


class AntreanDoctorSchedule(BaseModel):
    """Schema for doctor schedule from BPJS"""
    kodepoli: str = Field(..., description="Kode poli")
    kodedokter: str = Field(..., description="Kode dokter")
    namadokter: str = Field(..., description="Nama dokter")
    jadwal: List[Dict[str, Any]] = Field(..., description="Jadwal praktik")
    kapasitas: int = Field(..., ge=1, description="Kapasitas pasien per jadwal")


class AntreanOperationTime(BaseModel):
    """Schema for operation time configuration"""
    poli_code: str = Field(..., description="Kode poli")
    day_of_week: int = Field(..., ge=0, le=6, description="Hari (0=Minggu, 6=Sabtu)")
    opening_time: str = Field(..., description="Jam buka")
    closing_time: str = Field(..., description="Jam tutup")
    break_start_time: Optional[str] = Field(None, description="Jam mulai istirahat")
    break_end_time: Optional[str] = Field(None, description="Jam selesai istirahat")
    max_queue: int = Field(..., ge=1, description="Maksimal antrian")

    @validator('day_of_week')
    def validate_day_of_week(cls, v):
        """Validate day of week range"""
        if not 0 <= v <= 6:
            raise ValueError('Hari harus bernilai 0-6')
        return v


# =============================================================================
# Forward references resolution
# =============================================================================

# Resolve forward references
BPJSAntreanBookingCreate.model_rebuild()
BPJSAntreanBookingUpdate.model_rebuild()
BPJSAntreanBookingResponse.model_rebuild()
