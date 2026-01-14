"""BPJS Claims schemas for e-Claim submission and management.

This module defines Pydantic schemas for BPJS electronic claims (e-Claim),
including claim submission, claim items, supporting documents, submission logs,
verification queries, and claim statistics.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class ClaimType(str, Enum):
    """Types of BPJS claims"""
    INPATIENT = "inpatient"
    OUTPATIENT = "outpatient"
    EMERGENCY = "emergency"
    DENTAL = "dental"
    PHARMACY = "pharmacy"
    LABORATORY = "laboratory"
    RADIOLOGY = "radiology"


class ClaimStatus(str, Enum):
    """Workflow statuses for BPJS claims"""
    DRAFT = "draft"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    PENDING_SUBMISSION = "pending_submission"
    SUBMITTED = "submitted"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PARTIALLY_APPROVED = "partially_approved"
    PAID = "paid"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class DocumentType(str, Enum):
    """Types of supporting documents for BPJS claims"""
    SEP = "sep"  # Surat Eligibilitas Peserta
    MEDICAL_REPORT = "medical_report"
    LAB_RESULTS = "lab_results"
    RADIOLOGY_REPORT = "radiology_report"
    OPERATIVE_REPORT = "operative_report"
    DISCHARGE_SUMMARY = "discharge_summary"
    DEATH_CERTIFICATE = "death_certificate"
    BIRTH_CERTIFICATE = "birth_certificate"
    INVOICE = "invoice"
    PRESCRIPTION = "prescription"
    REFERRAL = "referral"
    OTHER = "other"


class QueryType(str, Enum):
    """Types of BPJS verification queries"""
    ELIGIBILITY = "eligibility"
    CLAIM_STATUS = "claim_status"
    PARTICIPANT_DATA = "participant_data"
    REFERRAL_VALIDATION = "referral_validation"
    DIAGNOSIS_VALIDATION = "diagnosis_validation"
    PROCEDURE_VALIDATION = "procedure_validation"
    CLAIM_HISTORY = "claim_history"


# =============================================================================
# BPJSClaim Schemas
# =============================================================================

class BPJSClaimBase(BaseModel):
    """Base BPJS claim schema"""
    patient_id: int
    encounter_id: int
    sep_number: str = Field(..., min_length=1, max_length=50, description="SEP number from BPJS")
    claim_type: ClaimType
    claim_date: date = Field(..., description="Date of service/claim")
    diagnosis_code: str = Field(..., min_length=1, max_length=10, description="Primary diagnosis code (ICD-10)")
    procedure_code: Optional[str] = Field(None, max_length=10, description="Primary procedure code")
    treatment_class: str = Field(..., min_length=1, max_length=5, description="Treatment class (1, 2, 3, VVIP, VIP)")
    facility_code: str = Field(..., min_length=1, max_length=20, description="Healthcare facility code")
    bpjs_card_number: str = Field(..., min_length=13, max_length=13, description="BPJS card number")
    total_claimed: Decimal = Field(..., ge=0, decimal_places=2, description="Total amount claimed")
    total_approved: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Total amount approved by BPJS")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    internal_notes: Optional[str] = Field(None, max_length=1000, description="Internal notes")
    submission_date: Optional[date] = Field(None, description="Date submitted to BPJS")
    response_date: Optional[date] = Field(None, description="Date BPJS responded")

    @validator('sep_number')
    def validate_sep_number(cls, v):
        """Validate SEP number format"""
        if not v or not v.strip():
            raise ValueError('SEP number cannot be empty')
        return v.strip().upper()

    @validator('bpjs_card_number')
    def validate_bpjs_card_number(cls, v):
        """Validate BPJS card number is 13 digits"""
        if not v.isdigit():
            raise ValueError('BPJS card number must contain only digits')
        if len(v) != 13:
            raise ValueError('BPJS card number must be exactly 13 digits')
        return v

    @validator('treatment_class')
    def validate_treatment_class(cls, v):
        """Validate treatment class"""
        valid_classes = ['1', '2', '3', 'VVIP', 'VIP']
        if v.upper() not in valid_classes:
            raise ValueError(f'Treatment class must be one of: {", ".join(valid_classes)}')
        return v.upper()

    @validator('response_date')
    def validate_response_date(cls, v, values):
        """Validate response date is after submission date"""
        if v is not None and 'submission_date' in values:
            submission_date = values.get('submission_date')
            if submission_date is not None and v < submission_date:
                raise ValueError('Response date cannot be before submission date')
        return v


class BPJSClaimCreate(BPJSClaimBase):
    """Schema for creating BPJS claim"""
    items: List['BPJSClaimItemCreate'] = Field(..., min_items=1)
    documents: List['BPJSClaimDocumentCreate'] = Field(default_factory=list)

    @validator('items')
    def validate_items(cls, v):
        """Validate items list is not empty"""
        if not v:
            raise ValueError('Claim must have at least one item')
        return v


class BPJSClaimUpdate(BaseModel):
    """Schema for updating BPJS claim"""
    claim_type: Optional[ClaimType] = None
    claim_date: Optional[date] = None
    diagnosis_code: Optional[str] = Field(None, min_length=1, max_length=10)
    procedure_code: Optional[str] = Field(None, max_length=10)
    treatment_class: Optional[str] = Field(None, min_length=1, max_length=5)
    total_claimed: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    total_approved: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    notes: Optional[str] = Field(None, max_length=1000)
    internal_notes: Optional[str] = Field(None, max_length=1000)
    submission_date: Optional[date] = None
    response_date: Optional[date] = None
    items: Optional[List['BPJSClaimItemCreate']] = None
    documents: Optional[List['BPJSClaimDocumentCreate']] = None

    @validator('treatment_class')
    def validate_treatment_class(cls, v):
        """Validate treatment class"""
        if v is not None:
            valid_classes = ['1', '2', '3', 'VVIP', 'VIP']
            if v.upper() not in valid_classes:
                raise ValueError(f'Treatment class must be one of: {", ".join(valid_classes)}')
            return v.upper()
        return v

    @validator('response_date')
    def validate_response_date(cls, v, values):
        """Validate response date logic"""
        # Note: Full validation requires checking against submission_date from database
        return v


class BPJSClaimResponse(BPJSClaimBase):
    """Schema for BPJS claim response"""
    id: int
    claim_number: str = Field(..., description="Generated claim number")
    status: ClaimStatus
    bpjs_response_code: Optional[str] = Field(None, max_length=50)
    bpjs_response_message: Optional[str] = Field(None, max_length=500)
    rejection_reason: Optional[str] = Field(None, max_length=1000)
    items: List['BPJSClaimItemResponse'] = Field(default_factory=list)
    documents: List['BPJSClaimDocumentResponse'] = Field(default_factory=list)
    submission_logs: List['BPJSSubmissionLogResponse'] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class BPJSClaimListResponse(BaseModel):
    """Schema for paginated BPJS claim list response"""
    items: List[BPJSClaimResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# BPJSClaimItem Schemas
# =============================================================================

class BPJSClaimItemBase(BaseModel):
    """Base BPJS claim item schema"""
    item_type: str = Field(..., min_length=1, max_length=100, description="Type of service/item")
    item_code: Optional[str] = Field(None, max_length=50, description="Service/item code")
    item_name: str = Field(..., min_length=1, max_length=255, description="Service/item name")
    quantity: Decimal = Field(..., gt=0, decimal_places=2, description="Quantity provided")
    unit_price: Decimal = Field(..., ge=0, decimal_places=2, description="Price per unit")
    claimed_amount: Decimal = Field(..., ge=0, decimal_places=2, description="Total amount claimed")
    approved_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Amount approved by BPJS")
    service_date: date = Field(..., description="Date service was provided")
    doctor_name: Optional[str] = Field(None, max_length=255, description="Doctor who provided service")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")

    @validator('quantity')
    def validate_quantity(cls, v):
        """Validate quantity is positive"""
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

    @validator('claimed_amount')
    def validate_claimed_amount(cls, v, values):
        """Validate claimed amount matches quantity * unit_price"""
        if 'quantity' in values and 'unit_price' in values:
            expected = values['quantity'] * values['unit_price']
            if v != expected:
                raise ValueError(f'Claimed amount must equal quantity × unit price ({expected})')
        return v


class BPJSClaimItemCreate(BPJSClaimItemBase):
    """Schema for creating BPJS claim item"""
    pass


class BPJSClaimItemUpdate(BaseModel):
    """Schema for updating BPJS claim item"""
    item_type: Optional[str] = Field(None, min_length=1, max_length=100)
    item_code: Optional[str] = Field(None, max_length=50)
    item_name: Optional[str] = Field(None, min_length=1, max_length=255)
    quantity: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    unit_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    claimed_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    approved_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    service_date: Optional[date] = None
    doctor_name: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field(None, max_length=500)

    @validator('quantity')
    def validate_quantity(cls, v):
        """Validate quantity is positive"""
        if v is not None and v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class BPJSClaimItemResponse(BPJSClaimItemBase):
    """Schema for BPJS claim item response"""
    id: int
    claim_id: int
    rejection_reason: Optional[str] = Field(None, max_length=500)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# BPJSClaimDocument Schemas
# =============================================================================

class BPJSClaimDocumentBase(BaseModel):
    """Base BPJS claim document schema"""
    document_type: DocumentType
    document_name: str = Field(..., min_length=1, max_length=255, description="Document name/title")
    file_url: str = Field(..., min_length=1, max_length=500, description="URL to document file")
    file_size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    mime_type: Optional[str] = Field(None, max_length=100, description="File MIME type")
    upload_date: date = Field(..., description="Date document was uploaded")
    uploaded_by: int = Field(..., description="ID of user who uploaded")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")

    @validator('file_size')
    def validate_file_size(cls, v):
        """Validate file size is reasonable (max 10MB)"""
        if v is not None and v > 10 * 1024 * 1024:
            raise ValueError('File size cannot exceed 10MB')
        return v


class BPJSClaimDocumentCreate(BPJSClaimDocumentBase):
    """Schema for creating BPJS claim document"""
    pass


class BPJSClaimDocumentUpdate(BaseModel):
    """Schema for updating BPJS claim document"""
    document_type: Optional[DocumentType] = None
    document_name: Optional[str] = Field(None, min_length=1, max_length=255)
    file_url: Optional[str] = Field(None, min_length=1, max_length=500)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)

    @validator('file_size')
    def validate_file_size(cls, v):
        """Validate file size is reasonable (max 10MB)"""
        if v is not None and v > 10 * 1024 * 1024:
            raise ValueError('File size cannot exceed 10MB')
        return v


class BPJSClaimDocumentResponse(BPJSClaimDocumentBase):
    """Schema for BPJS claim document response"""
    id: int
    claim_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# BPJSSubmissionLog Schemas
# =============================================================================

class BPJSSubmissionLogBase(BaseModel):
    """Base BPJS submission log schema"""
    submission_type: str = Field(..., min_length=1, max_length=50, description="Type of submission (create/update/query)")
    endpoint: str = Field(..., min_length=1, max_length=255, description="BPJS API endpoint")
    request_payload: Dict[str, Any] = Field(..., description="Request payload sent to BPJS")
    response_code: Optional[str] = Field(None, max_length=50, description="HTTP response code")
    response_body: Optional[Dict[str, Any]] = Field(None, description="Response body from BPJS")
    success: bool = Field(..., description="Whether submission was successful")
    error_message: Optional[str] = Field(None, max_length=1000, description="Error message if failed")
    processing_time_ms: Optional[int] = Field(None, ge=0, description="Processing time in milliseconds")
    submitted_at: datetime = Field(..., description="Timestamp of submission")
    submitted_by: int = Field(..., description="ID of user who submitted")

    @validator('processing_time_ms')
    def validate_processing_time(cls, v):
        """Validate processing time is reasonable (max 5 minutes)"""
        if v is not None and v > 5 * 60 * 1000:
            raise ValueError('Processing time cannot exceed 5 minutes')
        return v


class BPJSSubmissionLogCreate(BPJSSubmissionLogBase):
    """Schema for creating BPJS submission log"""
    pass


class BPJSSubmissionLogResponse(BPJSSubmissionLogBase):
    """Schema for BPJS submission log response"""
    id: int
    claim_id: int

    class Config:
        from_attributes = True


# =============================================================================
# BPJSVerificationQuery Schemas
# =============================================================================

class BPJSVerificationQueryBase(BaseModel):
    """Base BPJS verification query schema"""
    query_type: QueryType
    query_date: date = Field(..., description="Date query was made")
    patient_id: int
    bpjs_card_number: str = Field(..., min_length=13, max_length=13)
    query_params: Dict[str, Any] = Field(default_factory=dict, description="Parameters sent to BPJS")
    query_result: Optional[Dict[str, Any]] = Field(None, description="Result from BPJS")
    is_valid: Optional[bool] = Field(None, description="Whether verification was valid")
    notes: Optional[str] = Field(None, max_length=1000)

    @validator('bpjs_card_number')
    def validate_bpjs_card_number(cls, v):
        """Validate BPJS card number is 13 digits"""
        if not v.isdigit():
            raise ValueError('BPJS card number must contain only digits')
        if len(v) != 13:
            raise ValueError('BPJS card number must be exactly 13 digits')
        return v


class BPJSVerificationQueryCreate(BPJSVerificationQueryBase):
    """Schema for creating BPJS verification query"""
    pass


class BPJSVerificationQueryUpdate(BaseModel):
    """Schema for updating BPJS verification query"""
    query_result: Optional[Dict[str, Any]] = None
    is_valid: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)


class BPJSVerificationQueryResponse(BPJSVerificationQueryBase):
    """Schema for BPJS verification query response"""
    id: int
    queried_by: int = Field(..., description="ID of user who made query")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Additional Schemas
# =============================================================================

class eClaimData(BaseModel):
    """Schema for e-Claim submission data"""
    metadata: Dict[str, Any] = Field(..., description="e-Claim metadata")
    claim_data: Dict[str, Any] = Field(..., description="Main claim data")
    patient_data: Dict[str, Any] = Field(..., description="Patient information")
    service_data: Dict[str, Any] = Field(..., description="Service/procedure data")
    financial_data: Dict[str, Any] = Field(..., description="Financial information")

    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate required metadata fields"""
        required_fields = ['cons_id', 'signature', 'timestamp']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Metadata must include {field}')
        return v


class ClaimValidationResult(BaseModel):
    """Schema for claim validation result"""
    is_valid: bool = Field(..., description="Overall validation status")
    validation_errors: List[str] = Field(default_factory=list, description="List of validation errors")
    validation_warnings: List[str] = Field(default_factory=list, description="List of validation warnings")
    can_submit: bool = Field(..., description="Whether claim can be submitted")
    missing_documents: List[str] = Field(default_factory=list, description="List of missing required documents")
    invalid_fields: Dict[str, str] = Field(default_factory=dict, description="Map of invalid fields and reasons")
    estimated_approval_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Estimated approval amount")


class ClaimSubmissionResult(BaseModel):
    """Schema for claim submission result"""
    success: bool = Field(..., description="Whether submission was successful")
    claim_id: int = Field(..., description="Internal claim ID")
    claim_number: str = Field(..., description="Generated claim number")
    bpjs_claim_number: Optional[str] = Field(None, description="BPJS claim number (if assigned)")
    submission_date: datetime = Field(..., description="Submission timestamp")
    bpjs_response_code: Optional[str] = Field(None, description="BPJS response code")
    bpjs_response_message: Optional[str] = Field(None, description="BPJS response message")
    next_action: Optional[str] = Field(None, description="Recommended next action")
    estimated_processing_days: Optional[int] = Field(None, ge=0, description="Estimated processing time in days")


class ClaimStatistics(BaseModel):
    """Schema for BPJS claim statistics"""
    total_claims: int = Field(..., description="Total number of claims")
    claims_by_status: Dict[str, int] = Field(default_factory=dict, description="Claims grouped by status")
    claims_by_type: Dict[str, int] = Field(default_factory=dict, description="Claims grouped by type")
    total_claimed: Decimal = Field(..., ge=0, decimal_places=2, description="Total amount claimed")
    total_approved: Decimal = Field(..., ge=0, decimal_places=2, description="Total amount approved")
    total_rejected: Decimal = Field(default=0, ge=0, decimal_places=2, description="Total amount rejected")
    approval_rate: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2, description="Approval rate percentage")
    average_processing_days: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Average processing time")
    pending_claims: int = Field(default=0, description="Number of pending claims")
    current_month_claims: int = Field(default=0, description="Claims submitted this month")
    current_month_claimed: Decimal = Field(default=0, ge=0, decimal_places=2, description="Amount claimed this month")
    previous_month_claims: int = Field(default=0, description="Claims submitted previous month")
    previous_month_claimed: Decimal = Field(default=0, ge=0, decimal_places=2, description="Amount claimed previous month")


# =============================================================================
# Forward references resolution
# =============================================================================

# Resolve forward references
BPJSClaimCreate.model_rebuild()
BPJSClaimUpdate.model_rebuild()
BPJSClaimResponse.model_rebuild()
