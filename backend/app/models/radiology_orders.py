"""Radiology Order Models for STORY-018: Lab/Radiology Ordering

This module provides database models for:
- Radiology/imaging procedure ordering
- Radiology order status tracking
- Procedure scheduling
- Imaging protocol tracking
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


# =============================================================================
# Radiology Order Enums
# =============================================================================

class RadiologyOrderStatus:
    """Radiology order status constants"""
    ORDERED = "ordered"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RadiologyPriority:
    """Radiology priority constants"""
    ROUTINE = "routine"
    URGENT = "urgent"
    STAT = "stat"


# =============================================================================
# Radiology Order Models
# =============================================================================

class RadiologyOrder(Base):
    """Radiology/imaging procedure order model"""
    __tablename__ = "radiology_orders"

    id = Column(Integer, primary_key=True, index=True)

    # Identifiers
    order_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "RAD-2025-001234"
    accession_number = Column(String(100), unique=True, nullable=True)  # DICOM accession number

    # References
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False, index=True)
    ordered_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Procedure details
    procedure_code = Column(String(50), nullable=False, index=True)  # CPT-4 or local code
    procedure_name = Column(String(255), nullable=False)  # Procedure description
    modality = Column(String(50), nullable=True, index=True)  # CT, MRI, XRAY, US, etc.
    body_part = Column(String(100), nullable=True)  # Body part to be imaged
    view_position = Column(String(100), nullable=True)  # View/position (e.g., "PA and Lateral")

    # Priority and status
    priority = Column(String(20), nullable=False, default="routine")  # routine, urgent, stat
    status = Column(String(20), nullable=False, default="ordered", index=True)  # ordered, scheduled, in_progress, completed, cancelled

    # Clinical information
    clinical_indication = Column(Text, nullable=True)  # Reason for exam
    clinical_history = Column(Text, nullable=True)  # Relevant clinical history
    differential_diagnosis = Column(Text, nullable=True)  # What to look for
    question_to_answer = Column(Text, nullable=True)  # Specific clinical question

    # Patient safety considerations
    contrast_required = Column(Boolean, default=False, nullable=False)
    contrast_type = Column(String(100), nullable=True)  # IV, oral, rectal, etc.
    pregnancy_status = Column(String(50), nullable=True)  # pregnant, not pregnant, unknown
    gestational_age_weeks = Column(Integer, nullable=True)
    implanted_devices = Column(JSON, nullable=True)  # Pacemakers, metal implants, etc.
    allergies = Column(JSON, nullable=True)  # Contrast allergies, etc.
    renal_function_gfr = Column(Integer, nullable=True)  # For contrast safety

    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    scheduled_duration_minutes = Column(Integer, nullable=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    location = Column(String(100), nullable=True)  # Imaging suite/room
    equipment_id = Column(String(100), nullable=True)  # Equipment identifier

    # Procedure tracking
    check_in_at = Column(DateTime(timezone=True), nullable=True)
    procedure_started_at = Column(DateTime(timezone=True), nullable=True)
    procedure_completed_at = Column(DateTime(timezone=True), nullable=True)
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Technologist
    supervised_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Radiologist

    # Study information
    study_instance_uid = Column(String(100), unique=True, nullable=True)  # DICOM Study UID
    series_count = Column(Integer, nullable=True)
    image_count = Column(Integer, nullable=True)
    dicom_images_path = Column(String(500), nullable=True)  # Path to DICOM files

    # Results
    preliminary_report = Column(Text, nullable=True)
    preliminary_report_at = Column(DateTime(timezone=True), nullable=True)
    final_report = Column(Text, nullable=True)
    final_report_at = Column(DateTime(timezone=True), nullable=True)
    findings = Column(Text, nullable=True)
    impression = Column(Text, nullable=True)
    critical_findings = Column(Boolean, default=False, nullable=False)
    critical_findings_notified = Column(Boolean, default=False, nullable=False)
    critical_findings_notified_at = Column(DateTime(timezone=True), nullable=True)

    # Quality metrics
    radiation_dose_msv = Column(Integer, nullable=True)  # Effective dose in millisieverts
    contrast_volume_ml = Column(Integer, nullable=True)
    sedation_used = Column(Boolean, default=False, nullable=False)

    # Additional information
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Integration
    satusehat_service_request_id = Column(String(100), nullable=True, index=True, comment="SATUSEHAT FHIR ServiceRequest resource ID")
    satusehat_diagnostic_report_id = Column(String(100), nullable=True, index=True, comment="SATUSEHAT FHIR DiagnosticReport resource ID")

    # Cost estimates
    estimated_cost = Column(Integer, nullable=True)
    bpjs_coverage_estimate = Column(Integer, nullable=True)
    patient_cost_estimate = Column(Integer, nullable=True)

    # Timestamps
    ordered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", backref="radiology_orders")
    encounter = relationship("Encounter", backref="radiology_orders")
    ordering_provider = relationship("User", foreign_keys=[ordered_by], backref="ordered_radiology_exams")
    technologist = relationship("User", foreign_keys=[performed_by_id], backref="performed_radiology_exams")
    radiologist = relationship("User", foreign_keys=[supervised_by_id], backref="supervised_radiology_exams")
    appointment = relationship("Appointment", backref="radiology_orders")
