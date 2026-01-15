"""Patient History Schemas for STORY-011: Patient History View

This module defines Pydantic schemas for comprehensive patient history display.
Includes demographics, encounters, allergies, medications, lab results, and more.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class EncounterType(str, Enum):
    """Types of medical encounters"""
    OUTPATIENT = "outpatient"
    INPATIENT = "inpatient"
    EMERGENCY = "emergency"
    TELEPHONE = "telephone"


class EncounterStatus(str, Enum):
    """Status of an encounter"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AllergySeverity(str, Enum):
    """Severity levels for allergies"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    LIFE_THREATENING = "life_threatening"


# ============================================================================
# Encounter History Schemas
# ============================================================================

class EncounterHistoryItem(BaseModel):
    """Single encounter in patient history"""
    id: int
    encounter_number: str
    encounter_type: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    department_name: Optional[str] = None
    doctor_name: Optional[str] = None
    chief_complaint: Optional[str] = None
    primary_diagnosis: Optional[str] = None
    notes_count: int = 0

    class Config:
        from_attributes = True


class EncounterTimelineItem(BaseModel):
    """Timeline item for encounter visualization"""
    date: datetime
    encounter_id: int
    encounter_type: str
    department: str
    doctor: Optional[str] = None
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None


# ============================================================================
# Allergy Schemas
# ============================================================================

class PatientAllergy(BaseModel):
    """Patient allergy information"""
    id: int
    allergen: str
    allergy_type: str  # drug, food, environment, other
    severity: AllergySeverity
    reaction: Optional[str] = None
    diagnosed_date: Optional[date] = None
    diagnosed_by: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Medication Schemas
# ============================================================================

class CurrentMedication(BaseModel):
    """Current patient medication"""
    id: int
    medication_name: str
    dosage: str
    frequency: str
    route: str
    start_date: date
    end_date: Optional[date] = None
    prescriber: Optional[str] = None
    is_active: bool = True
    indication: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Lab Result Schemas
# ============================================================================

class LabResultSummary(BaseModel):
    """Summary of lab results"""
    id: int
    test_name: str
    test_date: datetime
    status: str  # pending, completed, abnormal, critical
    has_abnormal_values: bool = False
    ordered_by: Optional[str] = None
    facility_name: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Vital Signs Schemas
# ============================================================================

class VitalSignsRecord(BaseModel):
    """Vital signs measurement"""
    id: int
    recorded_at: datetime
    temperature: Optional[float] = None  # Celsius
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None  # bpm
    respiratory_rate: Optional[int] = None  # breaths/min
    oxygen_saturation: Optional[float] = None  # %
    weight: Optional[float] = None  # kg
    height: Optional[float] = None  # cm
    bmi: Optional[float] = None
    recorded_by: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Immunization Schemas
# ============================================================================

class ImmunizationRecord(BaseModel):
    """Patient immunization/vaccination record"""
    id: int
    vaccine_name: str
    vaccination_date: date
    facility_name: Optional[str] = None
    dose_number: Optional[int] = None
    total_doses: Optional[int] = None
    next_due_date: Optional[date] = None
    lot_number: Optional[str] = None
    adverse_events: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Surgical History Schemas
# ============================================================================

class SurgicalHistory(BaseModel):
    """Past surgical procedures"""
    id: int
    procedure_name: str
    procedure_date: date
    facility_name: Optional[str] = None
    surgeon: Optional[str] = None
    indication: Optional[str] = None
    complications: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Family History Schemas
# ============================================================================

class FamilyHistory(BaseModel):
    """Family medical history"""
    id: int
    relationship: str  # mother, father, sibling, etc.
    condition: str
    age_of_onset: Optional[int] = None
    is_alive: Optional[bool] = None
    age_at_death: Optional[int] = None
    cause_of_death: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Social History Schemas
# ============================================================================

class SocialHistory(BaseModel):
    """Social and lifestyle history"""
    id: int
    smoking_status: Optional[str] = None  # never, former, current
    smoking_pack_years: Optional[float] = None
    alcohol_consumption: Optional[str] = None  # none, occasional, regular, heavy
    alcohol_units_per_week: Optional[int] = None
    occupation: Optional[str] = None
    employer: Optional[str] = None
    education_level: Optional[str] = None
    marital_status: Optional[str] = None
    living_arrangement: Optional[str] = None  # alone, family, care facility
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Chronic Conditions Schemas
# ============================================================================

class ChronicCondition(BaseModel):
    """Chronic medical conditions"""
    id: int
    condition_name: str
    icd10_code: Optional[str] = None
    diagnosed_date: Optional[date] = None
    diagnosed_by: Optional[str] = None
    is_active: bool = True
    severity: Optional[str] = None
    last_exacerbation: Optional[date] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Main Patient History Response
# ============================================================================

class PatientHistoryResponse(BaseModel):
    """Comprehensive patient history response for STORY-011

    This schema aggregates all patient historical data into a single response,
    optimized for quick loading and display in clinical workflows.
    """
    # Basic Demographics
    patient_id: int
    medical_record_number: str
    full_name: str
    date_of_birth: date
    age: int
    gender: str
    blood_type: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None

    # Emergency Contacts
    emergency_contacts: List[dict] = Field(default_factory=list)

    # Insurance Information
    primary_insurance: Optional[dict] = None
    insurance_status: str = "Unknown"

    # Medical History Sections
    allergies: List[PatientAllergy] = Field(default_factory=list)
    current_medications: List[CurrentMedication] = Field(default_factory=list)
    chronic_conditions: List[ChronicCondition] = Field(default_factory=list)

    # Encounter History
    recent_encounters: List[EncounterHistoryItem] = Field(default_factory=list)
    total_encounters: int = 0
    last_encounter_date: Optional[datetime] = None
    last_department: Optional[str] = None
    last_doctor: Optional[str] = None

    # Timeline (chronological)
    encounter_timeline: List[EncounterTimelineItem] = Field(default_factory=list)

    # Lab Results
    recent_lab_results: List[LabResultSummary] = Field(default_factory=list)
    recent_vital_signs: List[VitalSignsRecord] = Field(default_factory=list)

    # Surgical History
    surgical_history: List[SurgicalHistory] = Field(default_factory=list)

    # Immunizations
    immunization_records: List[ImmunizationRecord] = Field(default_factory=list)

    # Family History
    family_history: List[FamilyHistory] = Field(default_factory=list)

    # Social History
    social_history: Optional[SocialHistory] = None

    # Metadata
    data_completeness: dict = Field(default_factory=dict)
    last_updated: datetime

    class Config:
        from_attributes = True


class PatientHistorySummary(BaseModel):
    """Lightweight patient history summary for quick reference

    Used in patient lists, search results, and quick views.
    """
    patient_id: int
    medical_record_number: str
    full_name: str
    age: int
    gender: str
    blood_type: Optional[str] = None

    # Quick indicators
    has_allergies: bool = False
    allergy_count: int = 0
    has_chronic_conditions: bool = False
    chronic_condition_count: int = 0
    medication_count: int = 0

    # Last visit info
    last_visit_date: Optional[datetime] = None
    last_visit_type: Optional[str] = None
    last_department: Optional[str] = None

    # Flags
    has_unpaid_bills: bool = False
    has_pending_appointments: bool = False
    insurance_status: str = "Unknown"

    class Config:
        from_attributes = True


class PatientHistoryFilter(BaseModel):
    """Filter parameters for patient history queries"""
    include_allergies: bool = True
    include_medications: bool = True
    include_conditions: bool = True
    include_encounters: bool = True
    include_lab_results: bool = True
    include_vital_signs: bool = True
    include_surgical_history: bool = True
    include_immunizations: bool = True
    include_family_history: bool = True
    include_social_history: bool = True

    encounter_limit: int = Field(default=10, ge=1, le=50)
    lab_results_limit: int = Field(default=10, ge=1, le=50)
    vital_signs_limit: int = Field(default=5, ge=1, le=20)


class PatientHistoryExportRequest(BaseModel):
    """Request for exporting patient history"""
    format: str = Field("pdf", pattern="^(pdf|html|json)$")
    include_sections: List[str] = Field(default_factory=list)
    language: str = Field("id", pattern="^(id|en)$")
    include_images: bool = False
