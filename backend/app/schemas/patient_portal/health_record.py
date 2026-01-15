"""Patient Portal Health Record Schemas

Pydantic schemas for personal health record access and display.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class SeverityLevel(str, Enum):
    """Allergy severity levels"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    LIFE_THREATENING = "life_threatening"


class AllergyStatus(str, Enum):
    """Allergy status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    UNCONFIRMED = "unconfirmed"


class AllergyType(str, Enum):
    """Allergy types"""
    DRUG = "drug"
    FOOD = "food"
    ENVIRONMENTAL = "environmental"
    OTHER = "other"


# Demographics Schemas
class PatientDemographics(BaseModel):
    """Patient demographic information"""
    medical_record_number: str
    full_name: str
    nik: Optional[str] = None
    date_of_birth: date
    gender: str
    blood_type: Optional[str] = None
    marital_status: Optional[str] = None
    religion: Optional[str] = None
    occupation: Optional[str] = None

    # Contact info
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Indonesia"

    # Insurance
    bpjs_card_number: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatientDemographicsUpdate(BaseModel):
    """Schema for updating patient demographics (requires approval)"""
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None


class DemographicsUpdateRequest(BaseModel):
    """Schema for requesting demographic updates"""
    changes: PatientDemographicsUpdate
    reason: Optional[str] = Field(None, max_length=500, description="Reason for update")


# Allergy Schemas
class AllergyItem(BaseModel):
    """Single allergy item"""
    id: int
    allergy_type: str
    allergen: str
    allergen_code: Optional[str] = None
    severity: str
    reaction: str
    reaction_details: Optional[dict] = None
    status: str
    onset_date: Optional[date] = None
    resolved_date: Optional[date] = None
    clinical_notes: Optional[str] = None
    alternatives: Optional[list] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AllergyList(BaseModel):
    """List of patient allergies"""
    active_allergies: List[AllergyItem]
    resolved_allergies: List[AllergyItem]
    total: int
    has_severe_allergies: bool


# Diagnosis Schemas
class DiagnosisItem(BaseModel):
    """Single diagnosis item"""
    id: int
    icd_10_code: str
    diagnosis_name: str
    diagnosis_type: str
    is_chronic: bool
    encounter_date: date
    department: Optional[str] = None
    notes: Optional[str] = None
    patient_friendly_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DiagnosisList(BaseModel):
    """List of patient diagnoses"""
    active_diagnoses: List[DiagnosisItem]
    resolved_diagnoses: List[DiagnosisItem]
    chronic_conditions: List[DiagnosisItem]
    total: int


# Medication Schemas
class MedicationItem(BaseModel):
    """Single medication item"""
    id: int
    treatment_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    is_active: bool
    encounter_date: date
    prescribed_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicationList(BaseModel):
    """List of patient medications"""
    current_medications: List[MedicationItem]
    past_medications: List[MedicationItem]
    total: int


# Vital Signs Schema
class VitalSignsItem(BaseModel):
    """Single vital signs recording"""
    encounter_date: date
    vital_signs: Optional[dict] = None
    department: Optional[str] = None


class VitalSignsHistory(BaseModel):
    """Vital signs history"""
    recordings: List[VitalSignsItem]
    latest: Optional[dict] = None


# Encounter History Schema
class EncounterSummary(BaseModel):
    """Summary of an encounter"""
    id: int
    encounter_type: str
    encounter_date: date
    department: Optional[str] = None
    doctor_name: Optional[str] = None
    chief_complaint: Optional[str] = None
    status: str
    diagnoses: List[DiagnosisItem] = []
    treatments: List[MedicationItem] = []

    model_config = ConfigDict(from_attributes=True)


class EncounterHistory(BaseModel):
    """Patient encounter history"""
    encounters: List[EncounterSummary]
    total: int
    admission_count: int = 0
    emergency_count: int = 0
    outpatient_count: int = 0


# Timeline Schema
class TimelineEventType(str, Enum):
    """Types of timeline events"""
    ENCOUNTER = "encounter"
    DIAGNOSIS = "diagnosis"
    MEDICATION = "medication"
    ALLERGY = "allergy"
    PROCEDURE = "procedure"
    HOSPITALIZATION = "hospitalization"
    SURGERY = "surgery"
    VACCINATION = "vaccination"


class TimelineEvent(BaseModel):
    """Single event in health timeline"""
    id: str
    event_type: TimelineEventType
    title: str
    description: Optional[str] = None
    date: date
    details: Optional[dict] = None


class HealthTimeline(BaseModel):
    """Patient health timeline"""
    events: List[TimelineEvent]
    total_events: int


# Complete Health Record Schema
class PersonalHealthRecord(BaseModel):
    """Complete personal health record"""
    demographics: PatientDemographics
    allergies: AllergyList
    diagnoses: DiagnosisList
    medications: MedicationList
    vital_signs: Optional[VitalSignsHistory] = None
    encounter_history: EncounterHistory
    timeline: HealthTimeline
    last_updated: datetime

    # Metadata
    data_accuracy_verified: bool = True
    record_completeness: Optional[str] = None


# Search Schema
class HealthRecordSearch(BaseModel):
    """Search query for health records"""
    keyword: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    event_types: Optional[List[TimelineEventType]] = None


class HealthRecordSearchResult(BaseModel):
    """Search results"""
    events: List[TimelineEvent]
    total: int
    query: HealthRecordSearch


# Export Schema
class ExportFormat(str, Enum):
    """Export format options"""
    PDF = "pdf"
    JSON = "json"


class HealthRecordExportRequest(BaseModel):
    """Request to export health records"""
    format: ExportFormat
    include_sections: Optional[List[str]] = Field(
        default=["demographics", "allergies", "diagnoses", "medications", "encounters"],
        description="Sections to include in export"
    )
    date_from: Optional[date] = None
    date_to: Optional[date] = None


class HealthRecordExportResponse(BaseModel):
    """Export response"""
    success: bool
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    message: str
