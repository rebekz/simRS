"""Medication List Schemas for STORY-014

This module provides Pydantic schemas for patient medication tracking:
- Current medications (active prescriptions)
- Past medications (discontinued prescriptions)
- Drug interaction checking
- Duplicate therapy warnings
- Medication reconciliation
"""
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


# =============================================================================
# Medication Enums
# =============================================================================

class MedicationStatus(str, Enum):
    """Medication status following FHIR MedicationStatement status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered_in_error"
    INTENDED = "intended"
    STOPPED = "stopped"
    ON_HOLD = "on_hold"


class InteractionSeverity(str, Enum):
    """Drug interaction severity levels"""
    CONTRAINDICATED = "contraindicated"
    SEVERE = "severe"
    MODERATE = "moderate"
    MILD = "mild"
    UNKNOWN = "unknown"


class InteractionType(str, Enum):
    """Types of drug interactions"""
    DRUG_DRUG = "drug_drug"
    DRUG_DISEASE = "drug_disease"
    DRUG_ALLERGY = "drug_allergy"
    DRUG_FOOD = "drug_food"
    THERAPEUTIC_DUPLICATION = "therapeutic_duplication"


class Route(str, Enum):
    """Routes of medication administration"""
    ORAL = "oral"
    INTRAVENOUS = "intravenous"
    INTRAMUSCULAR = "intramuscular"
    SUBCUTANEOUS = "subcutaneous"
    TOPICAL = "topical"
    INHALATION = "inhalation"
    NASAL = "nasal"
    OPHTHALMIC = "ophthalmic"
    OTIC = "otic"
    RECTAL = "rectal"
    VAGINAL = "vaginal"
    OTHER = "other"


# =============================================================================
# Medication Schemas
# =============================================================================

class MedicationBase(BaseModel):
    """Base medication schema"""
    drug_id: int
    drug_name: str
    generic_name: str
    dosage: Optional[str] = None
    dose_unit: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[Route] = None
    indication: Optional[str] = None  # Reason for use
    prescriber_id: Optional[int] = None
    prescription_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class MedicationCreate(MedicationBase):
    """Schema for creating a new medication entry"""
    encounter_id: Optional[int] = None
    status: MedicationStatus = MedicationStatus.ACTIVE
    notes: Optional[str] = None
    batch_number: Optional[str] = None  # For tracking specific drug batch
    manufacturer: Optional[str] = None


class MedicationUpdate(BaseModel):
    """Schema for updating medication information"""
    dosage: Optional[str] = None
    dose_unit: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[Route] = None
    indication: Optional[str] = None
    status: Optional[MedicationStatus] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None
    discontinuation_reason: Optional[str] = None


class MedicationResponse(MedicationBase):
    """Schema for medication response"""
    id: int
    patient_id: int
    encounter_id: Optional[int] = None
    status: MedicationStatus
    notes: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturer: Optional[str] = None
    discontinuation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Drug details from inventory
    bpjs_code: Optional[str] = None
    is_narcotic: bool = False
    is_antibiotic: bool = False
    requires_prescription: bool = True

    # Prescriber details
    prescriber_name: Optional[str] = None

    class Config:
        from_attributes = True


class MedicationListResponse(BaseModel):
    """Schema for medication list response"""
    patient_id: int
    current_medications: List[MedicationResponse]
    past_medications: List[MedicationResponse]
    total_current: int
    total_past: int


# =============================================================================
# Drug Interaction Schemas
# =============================================================================

class DrugInteraction(BaseModel):
    """Schema for drug interaction alert"""
    id: int
    interaction_type: InteractionType
    severity: InteractionSeverity
    drug_1_id: int
    drug_1_name: str
    drug_2_id: Optional[int] = None
    drug_2_name: Optional[str] = None
    disease_code: Optional[str] = None  # For drug-disease interactions
    allergy_id: Optional[int] = None  # For drug-allergy interactions
    description: str
    recommendation: str
    references: Optional[List[str]] = None
    requires_override: bool = True


class DrugInteractionCheckRequest(BaseModel):
    """Schema for drug interaction check request"""
    patient_id: int
    drug_ids: List[int]


class DrugInteractionCheckResponse(BaseModel):
    """Schema for drug interaction check response"""
    patient_id: int
    has_interactions: bool
    interactions: List[DrugInteraction]
    total_interactions: int
    by_severity: dict[str, int]  # {"severe": 2, "moderate": 1}


class DuplicateTherapyWarning(BaseModel):
    """Schema for duplicate therapy warning"""
    drug_1_id: int
    drug_1_name: str
    drug_2_id: int
    drug_2_name: str
    therapeutic_class: str
    severity: str  # "exact_duplicate", "similar_therapy"
    recommendation: str


# =============================================================================
# Medication Reconciliation Schemas
# =============================================================================

class MedicationReconciliationItem(BaseModel):
    """Schema for medication reconciliation item"""
    medication_id: Optional[int] = None
    drug_name: str
    current_status: str  # "taking", "not_taking", "changed_dose", "stopped"
    new_dosage: Optional[str] = None
    new_frequency: Optional[str] = None
    discrepancies: Optional[List[str]] = None  # List of discrepancy types
    notes: Optional[str] = None


class MedicationReconciliationRequest(BaseModel):
    """Schema for medication reconciliation request"""
    patient_id: int
    encounter_id: int
    reconciliation_date: date = Field(default_factory=date.today)
    source: str = Field(..., description="Source of medication list: 'patient_reported', 'pharmacy_records', 'referral'")
    medications: List[MedicationReconciliationItem]
    reconciled_by: int  # User ID performing reconciliation
    notes: Optional[str] = None


class MedicationReconciliationResponse(BaseModel):
    """Schema for medication reconciliation response"""
    id: int
    patient_id: int
    encounter_id: int
    reconciliation_date: date
    source: str
    total_medications: int
    discrepancies_found: int
    medications_continued: int
    medications_modified: int
    medications_stopped: int
    medications_added: int
    reconciled_by: int
    reconciled_by_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


class MedicationHistoryResponse(BaseModel):
    """Schema for medication history response"""
    patient_id: int
    medications: List[MedicationResponse]
    total_count: int
    date_range: Optional[dict[str, date]] = None  # {"from": date, "to": date}


# =============================================================================
# Medication Details Schemas
# =============================================================================

class MedicationDetailResponse(MedicationResponse):
    """Extended medication response with full details"""
    # Batch information
    batch_expiry_date: Optional[date] = None
    batch_quantity: Optional[int] = None

    # Supply information
    days_supply: Optional[int] = None
    refills_remaining: Optional[int] = None

    # Pharmacy information
    dispensed_by: Optional[str] = None
    dispensed_date: Optional[date] = None

    # Cost information
    unit_cost: Optional[float] = None
    total_cost: Optional[float] = None


class MedicationAdministrationRecord(BaseModel):
    """Schema for medication administration record (PRN)"""
    id: int
    medication_id: int
    drug_name: str
    scheduled_time: datetime
    administered_time: Optional[datetime] = None
    administered_by: Optional[int] = None
    administered_by_name: Optional[str] = None
    dosage_given: Optional[str] = None
    route: Optional[Route] = None
    status: str  # "scheduled", "administered", "missed", "refused", "held"
    notes: Optional[str] = None
    created_at: datetime
