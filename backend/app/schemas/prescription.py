"""Electronic Prescription Schemas for STORY-017

This module provides Pydantic schemas for electronic prescribing:
- Prescription creation and management
- Prescription items (individual drugs)
- Drug search with auto-complete
- Interaction checking integration
- BPJS coverage status
- Prescription printing with barcode
"""
from typing import List, Optional, Dict
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum

from app.schemas.medication import Route, InteractionSeverity, DrugInteraction


# =============================================================================
# Prescription Enums
# =============================================================================

class PrescriptionStatus(str, Enum):
    """Prescription status following FHIR MedicationRequest status"""
    DRAFT = "draft"  # Being composed
    ACTIVE = "active"  # Ready for dispensing
    ON_HOLD = "on_hold"  # Temporarily suspended
    COMPLETED = "completed"  # Fully dispensed
    CANCELLED = "cancelled"  # Cancelled by prescriber
    ENTERED_IN_ERROR = "entered_in_error"


class PrescriptionItemType(str, Enum):
    """Type of prescription item"""
    SIMPLE = "simple"  # Single drug
    COMPOUND = "compound"  # Racikan (mixed preparation)
    SUPPLY = "supply"  # Medical supplies (not drugs)


class DispenseStatus(str, Enum):
    """Dispensing status for prescription items"""
    PENDING = "pending"  # Not yet dispensed
    PARTIAL = "partial"  # Partially dispensed
    DISPENSED = "dispensed"  # Fully dispensed
    NOT_DISPENSED = "not_dispensed"  # Not dispensed (cancelled)


# =============================================================================
# Drug Search Schemas
# =============================================================================

class DrugSearchResult(BaseModel):
    """Schema for drug search result"""
    id: int
    name: str
    generic_name: str
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    bpjs_code: Optional[str] = None
    is_narcotic: bool = False
    is_antibiotic: bool = False
    requires_prescription: bool = True
    stock_available: Optional[int] = None
    therapeutic_class: Optional[str] = None


class DrugSearchResponse(BaseModel):
    """Schema for drug search response"""
    query: str
    results: List[DrugSearchResult]
    total: int
    page: int
    page_size: int


# =============================================================================
# Prescription Item Schemas
# =============================================================================

class PrescriptionItemBase(BaseModel):
    """Base prescription item schema"""
    drug_id: int
    drug_name: str
    generic_name: str
    dosage: str = Field(..., description="Dose amount (e.g., '500', '10')")
    dose_unit: str = Field(..., description="Unit (e.g., 'mg', 'ml', 'tablet')")
    frequency: str = Field(..., description="Frequency (e.g., '3x sehari', 'SORE')")
    route: Route
    duration_days: Optional[int] = Field(None, description="Duration in days")
    quantity: Optional[int] = Field(None, description="Total quantity to dispense")
    indication: Optional[str] = Field(None, description="Reason for use")


class PrescriptionCompoundItem(BaseModel):
    """Component drug in compound prescription (racikan)"""
    drug_id: int
    drug_name: str
    generic_name: str
    dosage: str
    dose_unit: str
    quantity: int  # Amount in compound


class PrescriptionItemCreate(PrescriptionItemBase):
    """Schema for creating a prescription item"""
    item_type: PrescriptionItemType = PrescriptionItemType.SIMPLE
    compound_name: Optional[str] = Field(None, description="Name for compound (racikan)")
    compound_components: Optional[List[PrescriptionCompoundItem]] = Field(
        None, description="Components if item_type is compound"
    )
    special_instructions: Optional[str] = None
    is_prn: bool = Field(False, description="Pro re nata (as needed)")


class PrescriptionItemUpdate(BaseModel):
    """Schema for updating a prescription item"""
    dosage: Optional[str] = None
    dose_unit: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[Route] = None
    duration_days: Optional[int] = None
    quantity: Optional[int] = None
    indication: Optional[str] = None
    special_instructions: Optional[str] = None


class PrescriptionItemResponse(PrescriptionItemBase):
    """Schema for prescription item response"""
    id: int
    prescription_id: int
    item_type: PrescriptionItemType
    compound_name: Optional[str] = None
    compound_components: Optional[List[Dict]] = None  # Stored as JSON
    special_instructions: Optional[str] = None
    is_prn: bool

    # Dispensing status
    dispense_status: DispenseStatus
    quantity_dispensed: Optional[int] = None
    dispensed_date: Optional[datetime] = None
    dispenser_id: Optional[int] = None
    dispenser_name: Optional[str] = None

    # Drug details
    bpjs_code: Optional[str] = None
    bpjs_covered: bool = True
    is_narcotic: bool = False
    is_antibiotic: bool = False

    # Calculated fields
    days_supply: Optional[int] = None
    refills_allowed: Optional[int] = None
    refills_used: int = 0

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Prescription Schemas
# =============================================================================

class PrescriptionBase(BaseModel):
    """Base prescription schema"""
    patient_id: int
    encounter_id: int
    prescriber_id: int


class PrescriptionCreate(PrescriptionBase):
    """Schema for creating a new prescription"""
    notes: Optional[str] = Field(None, description="General prescription notes")
    diagnosis: Optional[str] = Field(None, description="Primary diagnosis (ICD-10)")
    items: List[PrescriptionItemCreate] = Field(..., min_items=1, max_items=20)
    priority: str = Field("routine", description="priority: routine, urgent, stat")
    is_draft: bool = Field(False, description="Save as draft (not yet submitted)")

    @field_validator("items")
    @classmethod
    def validate_items(cls, items: List[PrescriptionItemCreate]) -> List[PrescriptionItemCreate]:
        """Validate prescription items"""
        for item in items:
            # Compound prescriptions must have components
            if item.item_type == PrescriptionItemType.COMPOUND:
                if not item.compound_components or len(item.compound_components) < 2:
                    raise ValueError(
                        "Compound prescriptions (racikan) must have at least 2 component drugs"
                    )
        return items


class PrescriptionUpdate(BaseModel):
    """Schema for updating prescription"""
    notes: Optional[str] = None
    diagnosis: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[PrescriptionStatus] = None


class PrescriptionResponse(PrescriptionBase):
    """Schema for prescription response"""
    id: int
    prescription_number: str  # Human-readable (e.g., "RX-2025-001234")
    status: PrescriptionStatus
    notes: Optional[str] = None
    diagnosis: Optional[str] = None
    priority: str

    # Patient and encounter details
    patient_name: Optional[str] = None
    patient_bpjs_number: Optional[str] = None
    encounter_type: Optional[str] = None

    # Prescriber details
    prescriber_name: Optional[str] = None
    prescriber_license: Optional[str] = None

    # Items
    items: List[PrescriptionItemResponse]

    # Summary
    total_items: int
    total_items_dispensed: int
    narcotic_count: int
    antibiotic_count: int

    # Dispensing
    is_fully_dispensed: bool = False
    submitted_to_pharmacy: bool = False
    submitted_date: Optional[datetime] = None
    dispensed_date: Optional[datetime] = None

    # Verification
    verified_by_id: Optional[int] = None
    verified_by_name: Optional[str] = None
    verified_date: Optional[datetime] = None

    # Barcode
    barcode: Optional[str] = None
    barcode_url: Optional[str] = None  # URL to barcode image

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
# Prescription Interaction Check Schemas
# =============================================================================

class PrescriptionInteractionCheck(BaseModel):
    """Schema for prescription interaction check result"""
    has_interactions: bool
    total_interactions: int
    contraindicated_count: int = 0
    severe_count: int = 0
    moderate_count: int = 0
    mild_count: int = 0
    interactions: List[DrugInteraction] = []
    can_prescribe: bool = True  # If false, requires override
    override_required: bool = False
    override_reason: Optional[str] = None


# =============================================================================
# Prescription Print Schemas
# =============================================================================

class PrescriptionPrintRequest(BaseModel):
    """Schema for prescription print request"""
    prescription_id: int
    include_barcode: bool = True
    include_diagnosis: bool = True
    include_instructions: bool = True
    copies: int = Field(1, ge=1, le=5)


class PrescriptionPrintResponse(BaseModel):
    """Schema for prescription print response"""
    prescription_id: int
    prescription_number: str
    print_url: str  # URL to PDF or printable view
    barcode_url: Optional[str] = None
    generated_at: datetime
    expires_at: Optional[datetime] = None  # Link expiry for security


# =============================================================================
# Prescription List Schemas
# =============================================================================

class PrescriptionListResponse(BaseModel):
    """Schema for prescription list response"""
    prescriptions: List[PrescriptionResponse]
    total: int
    page: int
    page_size: int
    filters_applied: Optional[Dict] = None


# =============================================================================
# Dose Calculation Helper Schemas
# =============================================================================

class DoseCalculationRequest(BaseModel):
    """Schema for dose calculation request"""
    drug_id: int
    patient_weight_kg: Optional[float] = None
    patient_age_years: Optional[int] = None
    target_dose_mg: Optional[float] = None
    concentration_mg_ml: Optional[float] = None
    desired_dose: Optional[str] = None  # e.g., "500 mg", "10 mg/kg"


class DoseCalculationResponse(BaseModel):
    """Schema for dose calculation response"""
    drug_name: str
    calculated_dose: Optional[str] = None
    calculated_quantity: Optional[int] = None
    concentration: Optional[str] = None
    instructions: Optional[str] = None
    warnings: List[str] = []
    max_dose_exceeded: bool = False


# =============================================================================
# BPJS Coverage Schemas
# =============================================================================

class BPJSCoverageStatus(BaseModel):
    """Schema for BPJS coverage status"""
    drug_name: str
    generic_name: str
    bpjs_code: Optional[str] = None
    is_covered: bool
    coverage_type: Optional[str] = None  # "full", "partial", "not_covered"
    restrictions: Optional[List[str]] = None
    prior_auth_required: bool = False
    patient_cost_estimate: Optional[float] = None


# =============================================================================
# Pharmacy Transmission Schemas
# =============================================================================

class PrescriptionTransmissionRequest(BaseModel):
    """Schema for transmitting prescription to pharmacy"""
    prescription_id: int
    target_pharmacy_id: Optional[int] = None  # None for default hospital pharmacy
    priority: str = "routine"
    notes: Optional[str] = None


class PrescriptionTransmissionResponse(BaseModel):
    """Schema for prescription transmission response"""
    prescription_id: int
    transmission_id: str
    status: str  # "queued", "sent", "acknowledged", "failed"
    sent_at: datetime
    acknowledged_at: Optional[datetime] = None
    pharmacy_name: Optional[str] = None
    estimated_ready_time: Optional[datetime] = None
