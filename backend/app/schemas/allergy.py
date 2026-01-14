"""Allergy Tracking schemas for STORY-013: Allergy Tracking

This module defines Pydantic schemas for allergy tracking and alerting.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime


# Allergy Schemas
class AllergyBase(BaseModel):
    """Base allergy schema."""
    allergy_type: str = Field(..., description="Type of allergy (drug, food, environmental, other)")
    allergen: str = Field(..., min_length=1, max_length=500, description="Substance causing allergy")
    allergen_code: Optional[str] = Field(None, max_length=100, description="Standard code (RxNorm, UNII)")
    severity: str = Field(..., description="Severity level (mild, moderate, severe, life_threatening)")
    reaction: str = Field(..., min_length=1, description="Description of reaction")
    reaction_details: Optional[Dict[str, Any]] = Field(None, description="Structured reaction data")
    status: str = Field(default="active", description="Allergy status (active, resolved, unconfirmed)")
    onset_date: Optional[date] = Field(None, description="When allergy was first observed")
    resolved_date: Optional[date] = Field(None, description="When allergy was resolved")
    source: str = Field(default="patient_reported", description="How allergy was identified")
    source_notes: Optional[str] = Field(None, description="Additional details about source")
    clinical_notes: Optional[str] = Field(None, description="Additional clinical information")
    alternatives: Optional[List[str]] = Field(None, description="Safe alternatives")


class AllergyCreate(AllergyBase):
    """Schema for creating an allergy."""
    patient_id: int
    verified_by: Optional[int] = None


class AllergyUpdate(BaseModel):
    """Schema for updating an allergy."""
    allergy_type: Optional[str] = None
    allergen: Optional[str] = None
    allergen_code: Optional[str] = None
    severity: Optional[str] = None
    reaction: Optional[str] = None
    reaction_details: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    onset_date: Optional[date] = None
    resolved_date: Optional[date] = None
    source: Optional[str] = None
    source_notes: Optional[str] = None
    clinical_notes: Optional[str] = None
    alternatives: Optional[List[str]] = None
    verified_by: Optional[int] = None


class AllergyResponse(AllergyBase):
    """Schema for allergy response."""
    id: int
    patient_id: int
    recorded_by: int
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Attribution
    recorded_by_name: Optional[str] = None
    verified_by_name: Optional[str] = None

    class Config:
        from_attributes = True


# Patient Allergy Summary
class PatientAllergySummary(BaseModel):
    """Schema for patient allergy summary with alerts."""
    patient_id: int
    has_allergies: bool
    no_known_allergies: bool
    total_allergies: int
    active_allergies: int
    severe_allergies: int  # moderate, severe, or life_threatening
    drug_allergies: int
    food_allergies: int
    environmental_allergies: int
    allergies: List[AllergyResponse]

    # Alerts
    requires_alert: bool  # True if any severe or life_threatening allergies
    alert_message: Optional[str] = None


# Allergy Check for Prescriptions
class AllergyCheckRequest(BaseModel):
    """Schema for checking allergies against medications."""
    patient_id: int
    medications: List[str] = Field(..., min_length=1, description="List of medication names or codes to check")


class AllergyWarning(BaseModel):
    """Schema for a single allergy warning."""
    allergy_id: int
    allergen: str
    allergy_type: str
    severity: str
    reaction: str
    matched_medication: str
    is_contraindicated: bool = Field(
        ...,
        description="True if medication should NOT be prescribed (requires override)"
    )


class AllergyCheckResponse(BaseModel):
    """Schema for allergy check response."""
    patient_id: int
    has_allergy_interaction: bool
    warnings: List[AllergyWarning]
    can_prescribe: bool = Field(
        ...,
        description="False if any contraindicated medications found"
    )
    requires_override: bool = Field(
        ...,
        description="True if override needed for contraindicated medications"
    )


# No Known Allergies (NKA)
class NoKnownAllergiesCreate(BaseModel):
    """Schema for recording NKA (No Known Allergies)."""
    patient_id: int
    recorded_by: int
    clinical_notes: Optional[str] = Field(None, description="Optional notes about NKA status")


class NoKnownAllergiesResponse(BaseModel):
    """Schema for NKA response."""
    patient_id: int
    no_known_allergies: bool = True
    recorded_by: int
    recorded_by_name: Optional[str] = None
    recorded_at: datetime
    clinical_notes: Optional[str] = None


# Allergy Override
class AllergyOverrideRequest(BaseModel):
    """Schema for overriding allergy alert during prescription."""
    allergy_id: int
    medication: str
    override_reason: str = Field(..., min_length=10, description="Reason for overriding allergy alert")
    prescribed_by: int


class AllergyOverrideResponse(BaseModel):
    """Schema for allergy override confirmation."""
    allergy_id: int
    medication: str
    override_reason: str
    override_allowed: bool
    warning_message: str
    prescribed_by: int
    overridden_at: datetime
