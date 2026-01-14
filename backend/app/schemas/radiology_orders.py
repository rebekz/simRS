"""Radiology Order Schemas for STORY-018

This module provides Pydantic schemas for radiology/imaging ordering:
- Radiology order creation and management
- Radiology order status tracking
- Imaging priority levels
- Imaging result integration
- BPJS coverage for imaging studies
- Contrast and safety screening
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# =============================================================================
# Radiology Order Enums
# =============================================================================

class RadiologyOrderStatus(str, Enum):
    """Radiology order status following FHIR ServiceRequest status"""
    DRAFT = "draft"  # Being composed
    ACTIVE = "active"  # Submitted to radiology
    ON_HOLD = "on_hold"  # Temporarily suspended
    COMPLETED = "completed"  # Study completed, report available
    CANCELLED = "cancelled"  # Cancelled by ordering provider
    ENTERED_IN_ERROR = "entered_in_error"
    IN_PROGRESS = "in_progress"  # Being performed
    SUSPENDED = "suspended"  # Scheduled or awaiting patient
    SCHEDULED = "scheduled"  # Appointment scheduled


class RadiologyPriority(str, Enum):
    """Radiology study priority levels"""
    ROUTINE = "routine"  # Normal scheduling (within 3-5 days)
    URGENT = "urgent"  # Expedited (within 24 hours)
    STAT = "stat"  # Immediate (within 1 hour)
    ASAP = "asap"  # As soon as available (today)
    PREAUTH = "preauth"  # Awaiting insurance prior authorization


class ModalityType(str, Enum):
    """Types of radiology modalities"""
    XRAY = "xray"  # X-ray radiography
    CT = "ct"  # Computed Tomography
    MRI = "mri"  # Magnetic Resonance Imaging
    ULTRASOUND = "ultrasound"  # Ultrasound
    MAMMOGRAPHY = "mammography"  # Mammography
    FLUOROSCOPY = "fluoroscopy"  # Fluoroscopy/Interventional
    NUCLEAR_MEDICINE = "nuclear_medicine"  # Nuclear medicine/PET
    DEXA = "dexa"  # Bone densitometry
    ANGIOGRAPHY = "angiography"  # Angiography


# =============================================================================
# Radiology Order Item Schemas
# =============================================================================

class RadiologyOrderItemBase(BaseModel):
    """Base radiology order item schema"""
    procedure_code_id: int
    procedure_code: str = Field(..., description="Procedure code (e.g., 'CXR', 'CTABD')")
    procedure_name: str = Field(..., description="Name of the imaging study")
    modality: ModalityType
    clinical_indication: Optional[str] = Field(None, description="Reason for imaging")
    body_part: Optional[str] = Field(None, description="Body part/region to be imaged")
    view_position: Optional[str] = Field(None, description="View or position (e.g., 'PA/Lateral', 'AP')")


class RadiologyOrderItemCreate(RadiologyOrderItemBase):
    """Schema for creating a radiology order item"""
    contrast_required: bool = Field(False, description="Contrast agent required")
    contrast_type: Optional[str] = Field(None, description="Type of contrast if required")
    special_instructions: Optional[str] = Field(None, description="Special instructions for technologist")
    is_surgical: bool = Field(False, description="Study for surgical planning")


class RadiologyOrderItemUpdate(BaseModel):
    """Schema for updating a radiology order item"""
    clinical_indication: Optional[str] = None
    body_part: Optional[str] = None
    view_position: Optional[str] = None
    contrast_required: Optional[bool] = None
    contrast_type: Optional[str] = None
    special_instructions: Optional[str] = None


class RadiologyOrderItemResponse(RadiologyOrderItemBase):
    """Schema for radiology order item response"""
    id: int
    radiology_order_id: int
    contrast_required: bool
    contrast_type: Optional[str] = None
    special_instructions: Optional[str] = None
    is_surgical: bool

    # Study information
    study_status: str = Field(..., description="Status of study: scheduled, in_progress, completed, cancelled")
    study_instance_uid: Optional[str] = Field(None, description="DICOM Study Instance UID")
    accession_number: Optional[str] = Field(None, description="Radiology accession number")
    study_date: Optional[date] = None
    study_time: Optional[datetime] = None
    performed_by: Optional[str] = None  # Technologist
    images_count: Optional[int] = None

    # Report information
    report_status: str = Field(..., description="Report status: pending, preliminary, final, amended")
    report_id: Optional[int] = None
    preliminary_report: Optional[str] = None
    preliminary_report_by: Optional[str] = None
    preliminary_report_date: Optional[datetime] = None
    final_report: Optional[str] = None
    final_report_by: Optional[str] = None  # Radiologist
    final_report_date: Optional[datetime] = None
    report_amended: bool = False
    amendment_reason: Optional[str] = None

    # Critical findings
    has_critical_findings: bool = False
    critical_findings_notified: bool = False
    critical_findings_notified_to: Optional[str] = None
    critical_findings_notified_at: Optional[datetime] = None

    # Procedure details
    bpjs_code: Optional[str] = None
    bpjs_covered: bool = True
    estimated_cost: Optional[float] = None

    # Images/Access
    image_urls: Optional[List[str]] = Field(None, description="URLs to view/download images")
    report_url: Optional[str] = Field(None, description="URL to PDF report")

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Radiology Order Schemas
# =============================================================================

class RadiologyOrderBase(BaseModel):
    """Base radiology order schema"""
    patient_id: int
    encounter_id: int
    ordering_provider_id: int


class RadiologyOrderCreate(RadiologyOrderBase):
    """Schema for creating a new radiology order"""
    items: List[RadiologyOrderItemCreate] = Field(..., min_items=1, max_items=20)
    priority: RadiologyPriority = RadiologyPriority.ROUTINE
    diagnosis: Optional[str] = Field(None, description="Primary diagnosis (ICD-10)")
    clinical_history: Optional[str] = Field(None, description="Relevant clinical history")
    special_instructions: Optional[str] = Field(None, description="General instructions for radiology")
    is_draft: bool = Field(False, description="Save as draft (not yet submitted)")

    # Patient safety screening
    pregnancy_status: Optional[str] = Field(None, description="Pregnancy status: unknown, not_pregnant, pregnant")
    pregnancy_trimester: Optional[int] = Field(None, ge=1, le=3, description="If pregnant")
    has_implants: bool = Field(False, description="Patient has implants (pacemaker, clips, etc)")
    implant_details: Optional[str] = Field(None, description="Details of implants if present")
    claustrophobia: bool = Field(False, description="Patient has claustrophobia (relevant for MRI)")
    contrast_allergy: bool = Field(False, description="Patient has contrast allergy")
    allergy_details: Optional[str] = Field(None, description="Details of contrast allergy")
    renal_impairment: bool = Field(False, description="Patient has renal impairment (contrast risk)")
    creatinine_level: Optional[float] = Field(None, description="Serum creatinine level if impaired")
    gfr: Optional[float] = Field(None, description="Glomerular filtration rate")

    # Scheduling
    preferred_date: Optional[date] = Field(None, description="Preferred appointment date")
    preferred_time_slot: Optional[str] = Field(None, description="Preferred time (morning, afternoon)")

    @field_validator("items")
    @classmethod
    def validate_items(cls, items: List[RadiologyOrderItemCreate]) -> List[RadiologyOrderItemCreate]:
        """Validate radiology order items"""
        procedure_codes = [item.procedure_code for item in items]
        if len(procedure_codes) != len(set(procedure_codes)):
            raise ValueError("Duplicate procedure codes are not allowed in a single order")
        return items

    @field_validator("preferred_date")
    @classmethod
    def validate_preferred_date(cls, v: Optional[date]) -> Optional[date]:
        """Validate preferred date is not in the past"""
        if v and v < datetime.now().date():
            raise ValueError("Preferred date cannot be in the past")
        return v


class RadiologyOrderUpdate(BaseModel):
    """Schema for updating radiology order"""
    priority: Optional[RadiologyPriority] = None
    status: Optional[RadiologyOrderStatus] = None
    diagnosis: Optional[str] = None
    clinical_history: Optional[str] = None
    special_instructions: Optional[str] = None
    preferred_date: Optional[date] = None
    preferred_time_slot: Optional[str] = None

    # Safety updates
    pregnancy_status: Optional[str] = None
    pregnancy_trimester: Optional[int] = None
    has_implants: Optional[bool] = None
    implant_details: Optional[str] = None
    claustrophobia: Optional[bool] = None
    contrast_allergy: Optional[bool] = None
    allergy_details: Optional[str] = None
    renal_impairment: Optional[bool] = None
    creatinine_level: Optional[float] = None
    gfr: Optional[float] = None


class RadiologyOrderResponse(RadiologyOrderBase):
    """Schema for radiology order response"""
    id: int
    order_number: str = Field(..., description="Human-readable order number (e.g., 'RAD-2025-001234')")
    status: RadiologyOrderStatus
    priority: RadiologyPriority
    diagnosis: Optional[str] = None
    clinical_history: Optional[str] = None
    special_instructions: Optional[str] = None

    # Patient and encounter details
    patient_name: Optional[str] = None
    patient_medical_record_number: Optional[str] = None
    patient_date_of_birth: Optional[date] = None
    patient_gender: Optional[str] = None
    patient_bpjs_number: Optional[str] = None
    encounter_type: Optional[str] = None
    encounter_date: Optional[datetime] = None

    # Ordering provider details
    ordering_provider_name: Optional[str] = None
    ordering_provider_license: Optional[str] = None

    # Items
    items: List[RadiologyOrderItemResponse]

    # Summary
    total_items: int
    items_completed: int
    items_in_progress: int
    items_scheduled: int
    items_pending: int
    has_critical_findings: bool = False

    # Safety screening
    pregnancy_status: Optional[str] = None
    pregnancy_trimester: Optional[int] = None
    has_implants: bool = False
    implant_details: Optional[str] = None
    claustrophobia: bool = False
    contrast_allergy: bool = False
    allergy_details: Optional[str] = None
    renal_impairment: bool = False
    creatinine_level: Optional[float] = None
    gfr: Optional[float] = None

    # Scheduling
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[datetime] = None
    appointment_confirmed: bool = False

    # Prior authorization
    prior_auth_required: bool = False
    prior_auth_status: Optional[str] = None  # "pending", "approved", "denied"
    prior_auth_number: Optional[str] = None

    # Results
    reports_available: bool = False
    reports_available_date: Optional[datetime] = None
    all_reports_complete: bool = False

    # Cost estimate
    estimated_cost: Optional[float] = None
    bpjs_coverage_estimate: Optional[float] = None
    patient_cost_estimate: Optional[float] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Radiology Order List Schemas
# =============================================================================

class RadiologyOrderListResponse(BaseModel):
    """Schema for radiology order list response with pagination"""
    orders: List[RadiologyOrderResponse]
    total: int
    page: int
    page_size: int
    filters_applied: Optional[Dict[str, Any]] = None


# =============================================================================
# Radiology Report Schemas
# =============================================================================

class RadiologyReportDetail(BaseModel):
    """Schema for detailed radiology report"""
    item_id: int
    procedure_code: str
    procedure_name: str
    modality: ModalityType
    body_part: Optional[str] = None
    study_date: Optional[date] = None
    accession_number: Optional[str] = None

    # Report content
    findings: Optional[str] = None
    impression: Optional[str] = None
    recommendation: Optional[str] = None

    # Status
    report_status: str
    report_type: str  # "preliminary", "final", "amended"
    radiologist: Optional[str] = None
    report_date: Optional[datetime] = None

    # Critical findings
    has_critical_findings: bool = False
    critical_findings: Optional[str] = None
    critical_findings_notified: bool = False
    critical_findings_notified_at: Optional[datetime] = None

    # Images
    images_count: Optional[int] = None
    image_urls: Optional[List[str]] = None


class RadiologyReport(BaseModel):
    """Schema for complete radiology report"""
    order_id: int
    order_number: str
    patient_id: int
    patient_name: str
    patient_medical_record_number: str
    patient_date_of_birth: Optional[date] = None
    patient_gender: Optional[str] = None
    ordering_provider_name: Optional[str] = None

    studies: List[RadiologyReportDetail]

    report_generated_date: datetime
    has_critical_findings: bool = False
    requires_follow_up: bool = False
    follow_up_recommendations: Optional[str] = None


# =============================================================================
# Radiology Scheduling Schemas
# =============================================================================

class RadiologyScheduleRequest(BaseModel):
    """Schema for scheduling radiology appointment"""
    order_id: int
    item_ids: Optional[List[int]] = Field(None, description="Specific items to schedule (all if not provided)")
    scheduled_date: date
    scheduled_time_slot: str = Field(..., description="Time slot (e.g., '08:00-09:00', '14:00-15:00')")
    send_reminder: bool = True


class RadiologyScheduleResponse(BaseModel):
    """Schema for radiology scheduling response"""
    order_id: int
    appointment_id: int
    scheduled_date: date
    scheduled_time_slot: str
    items_scheduled: int
    confirmation_code: Optional[str] = None
    preparation_instructions: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None


# =============================================================================
# Contrast Safety Screening Schema
# =============================================================================

class ContrastSafetyScreening(BaseModel):
    """Schema for contrast safety screening questionnaire"""
    patient_id: int
    has_contrast_allergy: bool
    allergy_details: Optional[str] = None
    has_renal_disease: bool
    has_diabetes: bool
    has_hypertension: bool
    age_over_65: bool
    pregnant: bool
    breastfeeding: bool
    creatinine_level: Optional[float] = None
    gfr: Optional[float] = None
    risk_level: str = Field(..., description="Risk level: low, medium, high")
    can_administer_contrast: bool
    premedication_required: bool = False
    premedication_details: Optional[str] = None
    screening_notes: Optional[str] = None
