"""Consultation Workflow schemas for STORY-016: Doctor Consultation Workflow

This module defines Pydantic schemas for the doctor consultation workflow.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date


# Consultation Session Management
class ConsultationSessionCreate(BaseModel):
    """Schema for starting a consultation session."""
    patient_id: int
    encounter_type: str = Field(default="outpatient", description="Type of encounter")
    department: Optional[str] = Field(None, description="Department/clinic")
    chief_complaint: Optional[str] = Field(None, description="Chief complaint")


class ConsultationSessionResponse(BaseModel):
    """Schema for consultation session response."""
    encounter_id: int
    patient_id: int
    status: str
    start_time: datetime
    encounter_type: str
    department: Optional[str] = None

    class Config:
        from_attributes = True


# Patient Summary for Consultation
class ConsultationPatientSummary(BaseModel):
    """Schema for patient summary displayed during consultation."""
    patient_id: int
    medical_record_number: str
    full_name: str
    date_of_birth: date
    age: int
    gender: str
    phone: str
    email: Optional[str] = None
    blood_type: Optional[str] = None
    marital_status: Optional[str] = None
    religion: Optional[str] = None
    occupation: Optional[str] = None
    address: Optional[str] = None

    # Insurance info
    insurance_type: Optional[str] = None
    insurance_number: Optional[str] = None
    insurance_expiry: Optional[date] = None

    # Clinical summary
    last_visit_date: Optional[date] = None
    chronic_problems: List[str] = []
    active_allergies: List[str] = []
    current_medications: List[str] = []


# Consultation Documentation
class ConsultationDocumentationUpdate(BaseModel):
    """Schema for updating consultation documentation."""
    encounter_id: int
    chief_complaint: Optional[str] = None
    present_illness: Optional[str] = None
    physical_examination: Optional[str] = None
    vital_signs: Optional[Dict[str, Any]] = None
    clinical_note_id: Optional[int] = None  # Link to clinical note


# Quick Diagnosis Entry
class QuickDiagnosisCreate(BaseModel):
    """Schema for quick diagnosis entry during consultation."""
    encounter_id: int
    icd10_code_id: int
    diagnosis_name: str
    diagnosis_type: str = Field(default="primary", description="primary, secondary, admission, discharge")
    is_chronic: bool = False


# Treatment Plan
class TreatmentPlanCreate(BaseModel):
    """Schema for creating treatment plan."""
    encounter_id: int
    treatment_type: str
    treatment_name: str
    description: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    route: Optional[str] = None
    is_active: bool = True


# Consultation Completion
class ConsultationCompletion(BaseModel):
    """Schema for completing a consultation."""
    encounter_id: int
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[date] = None
    next_appointment_date: Optional[date] = None
    next_appointment_department: Optional[str] = None


class ConsultationCompletionResponse(BaseModel):
    """Schema for consultation completion response."""
    encounter_id: int
    status: str
    end_time: datetime
    duration_minutes: Optional[int] = None
    diagnoses_count: int
    treatments_count: int
    clinical_note_signed: bool


# Consultation Templates
class ConsultationTemplateResponse(BaseModel):
    """Schema for consultation template."""
    id: str
    name: str
    specialty: str
    template: Dict[str, Any]
    description: Optional[str] = None


# Patient Education Materials
class EducationMaterialResponse(BaseModel):
    """Schema for patient education material."""
    id: str
    title: str
    description: Optional[str] = None
    icd10_codes: List[str] = []
    content_type: str  # text, video, pdf
    content_url: Optional[str] = None
    content: Optional[str] = None
    language: str = "id"
