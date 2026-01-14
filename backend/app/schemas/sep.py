"""BPJS SEP (Surat Eligibilitas Peserta) schemas for STORY-019

This module defines Pydantic schemas for BPJS SEP management, including
creation, updating, cancellation, and history tracking.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date


# =============================================================================
# SEP Creation Schemas
# =============================================================================

class SEPCreate(BaseModel):
    """Schema for creating a new SEP."""
    encounter_id: int = Field(..., description="Encounter ID to link SEP to")
    patient_id: int = Field(..., description="Patient ID")

    # Required SEP fields
    bpjs_card_number: str = Field(..., min_length=13, max_length=13, description="BPJS card number")
    sep_date: date = Field(..., description="SEP date")
    service_type: str = Field(..., description="Service type: RI (Rawat Inap) or RJ (Rawat Jalan)")
    ppk_code: str = Field(..., description="Healthcare facility code")
    initial_diagnosis_code: str = Field(..., min_length=3, max_length=3, description="Initial ICD-10 code")
    initial_diagnosis_name: str = Field(..., description="Initial diagnosis name")

    # Optional SEP fields
    polyclinic_code: Optional[str] = Field(None, description="Polyclinic code (for RJ)")
    treatment_class: Optional[str] = Field(None, description="Treatment class (1, 2, 3, VVIP, VIP)")
    mrn: Optional[str] = Field(None, description="Medical record number")

    # Doctor information
    doctor_code: Optional[str] = Field(None, description="Doctor code (DPJP)")
    doctor_name: Optional[str] = Field(None, description="Doctor name")

    # Referral information
    referral_number: Optional[str] = Field(None, description="Referral number")
    referral_ppk_code: Optional[str] = Field(None, description="Referral PPK code")

    # Service flags
    is_executive: bool = Field(default=False, description="Executive service flag")
    cob_flag: bool = Field(default=False, description="COB (Coordination of Benefits) flag")

    # Additional information
    notes: Optional[str] = Field(None, max_length=200, description="Additional notes")
    patient_phone: Optional[str] = Field(None, description="Patient phone number")

    # User information
    user: str = Field(..., description="User creating the SEP")

    @validator('service_type')
    def validate_service_type(cls, v):
        """Validate service type"""
        valid_types = ['RI', 'RJ', 'RAWAT INAP', 'RAWAT JALAN']
        if v.upper() not in valid_types:
            raise ValueError(f'Service type must be one of: {", ".join(valid_types)}')
        # Normalize to short form
        return 'RI' if v.upper() in ['RI', 'RAWAT INAP'] else 'RJ'

    @validator('bpjs_card_number')
    def validate_card_number(cls, v):
        """Validate BPJS card number"""
        if not v.isdigit():
            raise ValueError('BPJS card number must contain only digits')
        return v

    @validator('initial_diagnosis_code')
    def validate_diagnosis_code(cls, v):
        """Validate ICD-10 code format"""
        if not v.isalnum():
            raise ValueError('ICD-10 code must be alphanumeric')
        return v.upper()


class SEPResponse(BaseModel):
    """Schema for SEP creation/update response."""
    sep_id: int
    sep_number: Optional[str] = None
    encounter_id: int
    patient_id: int
    status: str
    message: str = Field(default="SEP processed successfully")

    # SEP information
    sep_date: date
    service_type: str
    bpjs_card_number: str
    initial_diagnosis_code: str
    initial_diagnosis_name: str

    # Response details
    bpjs_response: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# SEP Update Schemas
# =============================================================================

class SEPUpdate(BaseModel):
    """Schema for updating an existing SEP."""
    sep_id: int = Field(..., description="SEP ID to update")

    # Updatable fields
    polyclinic_code: Optional[str] = Field(None, description="Polyclinic code")
    treatment_class: Optional[str] = Field(None, description="Treatment class")
    doctor_code: Optional[str] = Field(None, description="Doctor code")
    doctor_name: Optional[str] = Field(None, description="Doctor name")

    # Medical information updates
    initial_diagnosis_code: Optional[str] = Field(None, min_length=3, max_length=3)
    initial_diagnosis_name: Optional[str] = Field(None)

    # Additional information
    notes: Optional[str] = Field(None, max_length=200)
    patient_phone: Optional[str] = Field(None)

    # User information
    user: str = Field(..., description="User updating the SEP")
    reason: Optional[str] = Field(None, description="Reason for update")


class SEPUpdateResponse(BaseModel):
    """Schema for SEP update response."""
    sep_id: int
    sep_number: str
    previous_status: str
    new_status: str
    message: str = Field(default="SEP updated successfully")
    bpjs_response: Optional[Dict[str, Any]] = None
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# SEP Cancellation Schemas
# =============================================================================

class SEPCancel(BaseModel):
    """Schema for cancelling a SEP."""
    sep_id: int = Field(..., description="SEP ID to cancel")
    sep_number: str = Field(..., description="SEP number to cancel")
    user: str = Field(..., description="User requesting cancellation")
    reason: str = Field(..., description="Reason for cancellation")


class SEPCancelResponse(BaseModel):
    """Schema for SEP cancellation response."""
    sep_id: int
    sep_number: str
    status: str
    message: str = Field(default="SEP cancelled successfully")
    bpjs_response: Optional[Dict[str, Any]] = None
    cancelled_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# SEP Information Schemas
# =============================================================================

class SEPInfo(BaseModel):
    """Schema for SEP information display."""
    sep_id: int
    sep_number: Optional[str] = None
    encounter_id: int
    patient_id: int
    patient_name: str
    bpjs_card_number: str
    sep_date: date
    service_type: str
    ppk_code: str
    polyclinic_code: Optional[str] = None
    treatment_class: Optional[str] = None
    initial_diagnosis_code: str
    initial_diagnosis_name: str
    doctor_name: Optional[str] = None
    referral_number: Optional[str] = None
    is_executive: bool
    cob_flag: bool
    notes: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SEPSummary(BaseModel):
    """Schema for SEP summary (list view)."""
    sep_id: int
    sep_number: Optional[str] = None
    patient_name: str
    bpjs_card_number: str
    sep_date: date
    service_type: str
    initial_diagnosis: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# SEP History Schemas
# =============================================================================

class SEPHistoryEntry(BaseModel):
    """Schema for SEP history entry."""
    history_id: int
    sep_id: int
    action: str
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    reason: Optional[str] = None
    changed_by: Optional[int] = None
    changed_by_name: Optional[str] = None
    changed_at: datetime

    class Config:
        from_attributes = True


class SEPHistory(BaseModel):
    """Schema for SEP history response."""
    sep_id: int
    sep_number: Optional[str] = None
    history: List[SEPHistoryEntry]

    class Config:
        from_attributes = True


# =============================================================================
# SEP Validation Schemas
# =============================================================================

class SEPValidationRequest(BaseModel):
    """Schema for validating SEP data before creation."""
    bpjs_card_number: str = Field(..., min_length=13, max_length=13)
    sep_date: date
    service_type: str
    ppk_code: str
    initial_diagnosis_code: str
    polyclinic_code: Optional[str] = None

    @validator('service_type')
    def validate_service_type(cls, v):
        """Validate service type"""
        valid_types = ['RI', 'RJ', 'RAWAT INAP', 'RAWAT JALAN']
        if v.upper() not in valid_types:
            raise ValueError(f'Service type must be one of: {", ".join(valid_types)}')
        return 'RI' if v.upper() in ['RI', 'RAWAT INAP'] else 'RJ'


class SEPValidationResponse(BaseModel):
    """Schema for SEP validation response."""
    is_valid: bool
    message: str
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    patient_eligibility: Optional[Dict[str, Any]] = None


# =============================================================================
# SEP List Schemas
# =============================================================================

class SEPListQuery(BaseModel):
    """Schema for SEP list query parameters."""
    patient_id: Optional[int] = None
    encounter_id: Optional[int] = None
    status: Optional[str] = None
    service_type: Optional[str] = None
    sep_number: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SEPListResponse(BaseModel):
    """Schema for SEP list response."""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[SEPSummary]


# =============================================================================
# SEP Statistics Schemas
# =============================================================================

class SEPStatistics(BaseModel):
    """Schema for SEP statistics."""
    total_seps: int
    active_seps: int
    draft_seps: int
    submitted_seps: int
    approved_seps: int
    updated_seps: int
    cancelled_seps: int
    error_seps: int
    outpatient_seps: int
    inpatient_seps: int
    today_count: int
    this_month_count: int


# =============================================================================
# Auto-population Data Schemas
# =============================================================================

class SEPAutoPopulateData(BaseModel):
    """Schema for auto-populated SEP data from consultation."""
    encounter_id: int
    patient_id: int
    patient_name: str
    bpjs_card_number: str
    sep_date: date
    service_type: str  # Determined from encounter type
    ppk_code: str  # From hospital settings
    department: str  # From encounter
    doctor_code: Optional[str] = None  # From encounter
    doctor_name: Optional[str] = None  # From encounter
    chief_complaint: Optional[str] = None  # From encounter
    initial_diagnosis_code: Optional[str] = None  # From encounter diagnoses
    initial_diagnosis_name: Optional[str] = None  # From encounter diagnoses
    mrn: Optional[str] = None  # From patient
    patient_phone: Optional[str] = None  # From patient


class SEPAutoPopulateRequest(BaseModel):
    """Request schema for auto-generating SEP from consultation."""
    encounter_id: int = Field(..., description="Encounter ID to generate SEP from")
    polyclinic_code: Optional[str] = Field(None, description="Override polyclinic code")
    treatment_class: Optional[str] = Field(None, description="Override treatment class")
    notes: Optional[str] = Field(None, max_length=200, description="Additional notes")
    user: str = Field(..., description="User creating the SEP")


class SEPAutoPopulateResponse(BaseModel):
    """Response schema for auto-generated SEP."""
    sep_data: SEPAutoPopulateData
    validation: SEPValidationResponse
    can_create: bool
    missing_fields: List[str] = Field(default_factory=list)
