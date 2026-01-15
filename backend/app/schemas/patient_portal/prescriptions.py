"""Patient Portal Prescription Refill Schemas

Pydantic schemas for prescription refill requests via patient portal.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class RefillRequestStatus(str, Enum):
    """Status of refill request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    READY_FOR_PICKUP = "ready_for_pickup"
    COMPLETED = "completed"
    EXPIRED = "expired"


class RefillEligibility(str, Enum):
    """Eligibility for refill"""
    ELIGIBLE = "eligible"
    TOO_SOON = "too_soon"
    EXPIRED = "expired"
    MAX_REFILLS_REACHED = "max_refills_reached"
    REQUIRES_NEW_PRESCRIPTION = "requires_new_prescription"


# Prescription Display Schemas
class MedicationInfo(BaseModel):
    """Medication information for a prescription item"""
    drug_id: int
    drug_name: str
    generic_name: str
    dosage: str
    dose_unit: str
    frequency: str
    route: str
    duration_days: Optional[int] = None
    quantity: int
    quantity_dispensed: int
    refills_allowed: int
    refills_used: int
    refills_remaining: int
    instructions: Optional[str] = None
    warnings: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class PrescriptionItem(BaseModel):
    """Prescription with items for refill request"""
    id: int
    prescription_number: str
    prescription_date: date
    prescriber_name: str
    diagnosis: Optional[str] = None
    status: str
    medications: List[MedicationInfo]
    is_fully_dispensed: bool
    can_refill: bool
    refills_remaining: int
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PrescriptionListResponse(BaseModel):
    """Response for patient's prescriptions"""
    active_prescriptions: List[PrescriptionItem]
    past_prescriptions: List[PrescriptionItem]
    total_active: int
    total_past: int


# Refill Request Schemas
class RefillItemRequest(BaseModel):
    """Single medication refill request"""
    prescription_id: int
    prescription_item_id: int
    drug_id: int
    drug_name: str
    quantity_requested: int = Field(..., ge=1, description="Quantity to request")
    reason_for_refill: str = Field(..., min_length=5, max_length=500)

    @field_validator('quantity_requested')
    @classmethod
    def validate_quantity(cls, v, info):
        # Ensure quantity doesn't exceed typical limits
        if v > 365:
            raise ValueError('Requested quantity exceeds maximum allowed')
        return v


class RefillRequestCreate(BaseModel):
    """Create a new refill request"""
    items: List[RefillItemRequest]
    notes: Optional[str] = Field(None, max_length=500)
    preferred_pickup_date: Optional[date] = None

    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one medication must be selected for refill')
        if len(v) > 10:
            raise ValueError('Cannot request more than 10 medications at once')
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "items": [
                {
                    "prescription_id": 123,
                    "prescription_item_id": 456,
                    "drug_id": 789,
                    "drug_name": "Amlodipine 10mg",
                    "quantity_requested": 30,
                    "reason_for_refill": "Running low on medication"
                }
            ],
            "notes": "Please call if any questions",
            "preferred_pickup_date": "2026-01-25"
        }
    })


class RefillRequestResponse(BaseModel):
    """Response after creating refill request"""
    request_id: int
    status: str
    message: str
    estimated_processing_time: Optional[str] = None
    items_count: int


class RefillRequestDetail(BaseModel):
    """Detailed refill request information"""
    id: int
    request_number: str
    patient_id: int
    items: List[RefillItemRequest]
    notes: Optional[str]
    preferred_pickup_date: Optional[date]
    status: str
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]
    approved_by: Optional[str]
    ready_for_pickup_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class RefillRequestListResponse(BaseModel):
    """List of refill requests"""
    requests: List[RefillRequestDetail]
    total: int
    pending: int
    approved: int
    rejected: int
    ready_for_pickup: int


# Eligibility Check Schemas
class RefillEligibilityCheck(BaseModel):
    """Eligibility check result for a medication"""
    prescription_item_id: int
    drug_name: str
    eligible: bool
    eligibility_status: str
    refills_remaining: int
    next_refill_date: Optional[date]
    message: str


# Medication Information Schemas
class MedicationDetail(BaseModel):
    """Detailed medication information"""
    drug_id: int
    drug_name: str
    generic_name: str
    dosage_form: Optional[str]
    strength: Optional[str]
    manufacturer: Optional[str]
    description: Optional[str]
    indications: List[str]
    contraindications: List[str]
    warnings: List[str]
    side_effects: List[str]
    drug_interactions: List[str]
    instructions_for_use: Optional[str]
    storage_requirements: Optional[str]


class DrugInteractionWarning(BaseModel):
    """Drug interaction warning"""
    severity: str  # "severe", "moderate", "mild"
    description: str
    interacting_drugs: List[str]
