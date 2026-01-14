"""Encounter schemas for STORY-011: Patient History View

This module defines Pydantic schemas for encounter, diagnosis, and treatment data.
All schemas support proper serialization and validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class DiagnosisBase(BaseModel):
    """Base diagnosis schema"""
    icd_10_code: str = Field(..., max_length=10)
    diagnosis_name: str = Field(..., max_length=500)
    diagnosis_type: str = Field(default="primary", max_length=20)
    is_chronic: bool = False
    notes: Optional[str] = None


class DiagnosisCreate(DiagnosisBase):
    """Schema for creating a diagnosis"""
    pass


class DiagnosisResponse(DiagnosisBase):
    """Schema for diagnosis response"""
    id: int
    encounter_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TreatmentBase(BaseModel):
    """Base treatment schema"""
    treatment_type: str = Field(..., max_length=50)
    treatment_name: str = Field(..., max_length=500)
    dosage: Optional[str] = Field(None, max_length=100)
    frequency: Optional[str] = Field(None, max_length=100)
    duration: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    is_active: bool = True


class TreatmentCreate(TreatmentBase):
    """Schema for creating a treatment"""
    pass


class TreatmentResponse(TreatmentBase):
    """Schema for treatment response"""
    id: int
    encounter_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EncounterBase(BaseModel):
    """Base encounter schema"""
    encounter_type: str = Field(..., max_length=50)
    encounter_date: date
    department: Optional[str] = Field(None, max_length=100)
    doctor_id: Optional[int] = None
    chief_complaint: Optional[str] = None
    present_illness: Optional[str] = None
    physical_examination: Optional[str] = None
    vital_signs: Optional[dict] = None
    status: str = Field(default="active", max_length=20)
    is_urgent: bool = False
    bpjs_sep_number: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class EncounterCreate(EncounterBase):
    """Schema for creating an encounter"""
    patient_id: int
    diagnoses: Optional[List[DiagnosisCreate]] = Field(default_factory=list)
    treatments: Optional[List[TreatmentCreate]] = Field(default_factory=list)


class EncounterUpdate(BaseModel):
    """Schema for updating an encounter (all fields optional)"""
    encounter_type: Optional[str] = Field(None, max_length=50)
    encounter_date: Optional[date] = None
    end_time: Optional[datetime] = None
    department: Optional[str] = Field(None, max_length=100)
    doctor_id: Optional[int] = None
    chief_complaint: Optional[str] = None
    present_illness: Optional[str] = None
    physical_examination: Optional[str] = None
    vital_signs: Optional[dict] = None
    status: Optional[str] = Field(None, max_length=20)
    is_urgent: Optional[bool] = None
    bpjs_sep_number: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    diagnoses: Optional[List[DiagnosisCreate]] = None
    treatments: Optional[List[TreatmentCreate]] = None


class DiagnosisWithEncounter(DiagnosisResponse):
    """Schema for diagnosis with encounter summary"""
    encounter_date: date
    encounter_type: str


class TreatmentWithEncounter(TreatmentResponse):
    """Schema for treatment with encounter summary"""
    encounter_date: date
    encounter_type: str


class EncounterResponse(EncounterBase):
    """Schema for full encounter data response"""
    id: int
    patient_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    diagnoses: List[DiagnosisResponse] = Field(default_factory=list)
    treatments: List[TreatmentResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class EncounterListResponse(BaseModel):
    """Schema for paginated encounter list response"""
    items: List[EncounterResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PatientHistoryResponse(BaseModel):
    """Schema for comprehensive patient history response"""
    patient_id: int
    medical_record_number: str
    full_name: str
    date_of_birth: date
    gender: str

    # Encounter summary
    total_encounters: int
    encounters: List[EncounterResponse]

    # Diagnoses history (all diagnoses from all encounters)
    all_diagnoses: List[DiagnosisWithEncounter]
    chronic_conditions: List[DiagnosisWithEncounter]

    # Treatments history (active treatments)
    active_treatments: List[TreatmentWithEncounter]
    all_treatments: List[TreatmentWithEncounter]

    # Last visit info
    last_visit_date: Optional[date] = None
    last_department: Optional[str] = None
    last_doctor_id: Optional[int] = None

    # Statistics
    total_diagnoses: int
    total_treatments: int
    chronic_condition_count: int


class PatientEncountersListResponse(BaseModel):
    """Schema for patient encounters list"""
    patient_id: int
    medical_record_number: str
    full_name: str
    encounters: List[EncounterResponse]
    total: int
