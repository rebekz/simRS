"""Admission Workflow Schemas for STORY-021

This module provides Pydantic schemas for:
- Patient admission workflow
- Bed selection and assignment
- Room transfer workflow
- BPJS SEP updates
- Admission documentation
- Estimated discharge tracking
- Discharge criteria tracking
"""
from typing import List, Optional, Dict
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# Admission Enums
# =============================================================================

class AdmissionType(str, Enum):
    """Types of admission"""
    EMERGENCY = "emergency"  # UGD
    URGENT = "urgent"  # Gawat
    ELECTIVE = "elective"  # Rencana
    TRANSFER = "transfer"  # Rujukan


class AdmissionStatus(str, Enum):
    """Admission workflow status"""
    PENDING = "pending"  # Menunggu
    ADMITTED = "admitted"  # Ditrawat
    TRANSFERRED = "transferred"  # Dipindahkan
    DISCHARGED = "discharged"  # Dipulangkan
    CANCELLED = "cancelled"  # Dibatalkan
    DECEASED = "deceased"  # Meninggal


class RoomTransferStatus(str, Enum):
    """Room transfer workflow status"""
    REQUESTED = "requested"  # Diminta
    APPROVED = "approved"  # Disetujui
    IN_PROGRESS = "in_progress"  # Sedang proses
    COMPLETED = "completed"  # Selesai
    CANCELLED = "cancelled"  # Dibatalkan


class DischargeCriteria(str, Enum):
    """Discharge readiness criteria"""
    CLINICAL_STABILITY = "clinical_stability"  # Klinis stabil
    VITAL_SIGNS_NORMAL = "vital_signs_normal"  # Tanda vital normal
    MEDICATION_RECONCILED = "medication_reconciled"  # Obat direkonsiliasi
    EDUCATION_COMPLETED = "education_completed"  # Edukasi selesai
    FOLLOW_UP_SCHEDULED = "follow_up_scheduled"  # Follow-up dijadwalkan


# =============================================================================
# Admission Order Schemas
# =============================================================================

class AdmissionOrderBase(BaseModel):
    """Base admission order schema"""
    patient_id: int
    doctor_id: int
    admission_type: AdmissionType
    requested_room_class: Optional[str] = None
    requested_ward_id: Optional[int] = None
    priority: str = Field("routine", description="emergency, urgent, routine")
    chief_complaint: str = Field(..., description="Keluhan utama")
    diagnosis: Optional[str] = Field(None, description="Diagnosa awal")
    admission_reason: str = Field(..., description="Alasan masuk")
    expected_discharge_date: Optional[date] = None
    notes: Optional[str] = None


class AdmissionOrderCreate(AdmissionOrderBase):
    """Schema for creating admission order"""
    bpjs_sep_number: Optional[str] = Field(None, description="BPJS SEP number if already exists")


class AdmissionOrderResponse(AdmissionOrderBase):
    """Schema for admission order response"""
    id: int
    order_number: str
    status: AdmissionStatus
    bpjs_sep_number: Optional[str] = None

    # Doctor info
    doctor_name: Optional[str] = None

    # Patient info
    patient_name: Optional[str] = None
    patient_mrn: Optional[str] = None

    # Admission details
    admission_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None

    # Bed assignment
    assigned_bed_id: Optional[int] = None
    assigned_bed_number: Optional[str] = None
    assigned_room_number: Optional[str] = None
    assigned_room_class: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Bed Selection Schemas
# =============================================================================

class BedSelectionRequest(BaseModel):
    """Schema for bed selection during admission"""
    admission_order_id: int
    bed_id: int
    assign_for_isolation: bool = False
    notes: Optional[str] = None


class BedSelectionResponse(BaseModel):
    """Schema for bed selection response"""
    admission_id: int
    patient_id: int
    patient_name: str
    bed_id: int
    bed_number: str
    room_number: str
    room_class: str
    ward_id: int
    assigned_at: datetime
    assigned_by: str
    expected_discharge_date: Optional[date] = None
    notes: Optional[str] = None


class AvailableBedOption(BaseModel):
    """Schema for available bed option"""
    bed_id: int
    bed_number: str
    room_number: str
    room_class: str
    ward_id: int
    ward_name: str
    bed_type: str
    floor: int
    gender_type: str


# =============================================================================
# Room Transfer Schemas
# =============================================================================

class RoomTransferRequest(BaseModel):
    """Schema for requesting room transfer"""
    admission_id: int
    from_bed_id: int
    to_bed_id: int
    reason: str = Field(..., description="Alasan pemindahan")
    transfer_type: str = Field("routine", description="emergency, urgent, routine")
    requested_by_id: int
    notes: Optional[str] = None


class RoomTransferApproval(BaseModel):
    """Schema for approving room transfer"""
    transfer_request_id: int
    approved: bool
    approved_by_id: int
    notes: Optional[str] = None


class RoomTransferResponse(BaseModel):
    """Schema for room transfer response"""
    transfer_id: int
    admission_id: int
    patient_id: int
    patient_name: str
    from_bed: Dict
    to_bed: Dict
    reason: str
    transfer_type: str
    status: RoomTransferStatus
    requested_at: datetime
    requested_by: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


# =============================================================================
# Admission Documentation Schemas
# =============================================================================

class AdmissionDocumentation(BaseModel):
    """Schema for admission documentation"""
    admission_id: int
    admission_notes: Optional[str] = None
    allergies: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    advance_directives: Optional[str] = None
    emergency_contact: Optional[str] = None
    insurance_info: Optional[Dict] = None


class AdmissionDocumentResponse(BaseModel):
    """Schema for generated admission document"""
    document_id: int
    admission_id: int
    document_type: str = Field(..., description="admission_order, consent_form, etc")
    document_url: str
    generated_at: datetime
    generated_by: str


# =============================================================================
# Discharge Planning Schemas
# =============================================================================

class DischargeCriteriaChecklist(BaseModel):
    """Schema for discharge readiness checklist"""
    admission_id: int
    criteria_met: List[DischargeCriteria]
    criteria_not_met: List[DischargeCriteria]
    additional_notes: Optional[str] = None
    assessed_by_id: int
    assessed_at: datetime


class EstimatedDischargeUpdate(BaseModel):
    """Schema for updating estimated discharge date"""
    admission_id: int
    estimated_discharge_date: date
    reason: str = Field(..., description="Alasan perubahan")
    updated_by_id: int


class DischargeReadinessAssessment(BaseModel):
    """Schema for discharge readiness assessment"""
    admission_id: int
    is_ready: bool
    readiness_score: float = Field(..., ge=0, le=100, description="Skala kesiapan 0-100")
    barriers_to_discharge: Optional[List[str]] = None
    required_follow_up: Optional[List[str]] = None
    assessed_by_id: int
    assessed_at: datetime
    notes: Optional[str] = None


# =============================================================================
# BPJS SEP Update Schemas
# =============================================================================

class BPJSSEPUpdate(BaseModel):
    """Schema for BPJS SEP update during admission"""
    admission_id: int
    sep_number: str
    sep_date: date
    poly_type: str
    care_type: str = Field(..., description="Jenis perawatan")
    room_class: str
    facility_name: str
    referral_number: Optional[str] = None
    updated_by_id: int


class BPJSSEPResponse(BaseModel):
    """Schema for BPJS SEP update response"""
    sep_number: str
    admission_id: int
    update_status: str = Field(..., description="success, failed, pending")
    update_message: Optional[str] = None
    updated_at: datetime


# =============================================================================
# Admission Summary Schemas
# =============================================================================

class AdmissionSummary(BaseModel):
    """Schema for admission summary"""
    admission_id: int
    patient_id: int
    patient_name: str
    admission_type: str
    admission_date: datetime
    current_bed: Dict
    attending_doctor: str
    current_status: AdmissionStatus
    length_of_stay_days: int
    estimated_discharge_date: Optional[date] = None
    discharge_readiness_score: Optional[float] = None


class AdmissionListResponse(BaseModel):
    """Schema for admission list response"""
    admissions: List[AdmissionSummary]
    total: int
    active_admissions: int
    pending_admissions: int
