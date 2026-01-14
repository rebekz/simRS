"""ICD-10 and Problem List schemas for STORY-012: ICD-10 Problem List

This module defines Pydantic schemas for ICD-10 codes and problem list management.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import date, datetime


# ICD-10 Code Schemas
class ICD10CodeBase(BaseModel):
    """Base ICD-10 code schema."""
    code: str = Field(..., description="ICD-10 code")
    code_full: str = Field(..., description="Full ICD-10 code with decimal")
    chapter: str = Field(..., description="Chapter identifier (I-XXII)")
    block: str = Field(..., description="Block category")
    description_indonesian: str = Field(..., description="Indonesian description")
    description_english: Optional[str] = Field(None, description="English description")
    severity: Optional[str] = Field(None, description="Severity level")


class ICD10CodeCreate(ICD10CodeBase):
    """Schema for creating ICD-10 code."""
    pass


class ICD10CodeResponse(ICD10CodeBase):
    """Schema for ICD-10 code response."""
    id: int
    is_chapter: bool
    is_block: bool
    is_category: bool
    inclusion_terms: Optional[Dict[str, Any]] = None
    exclusion_terms: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    usage_count: int
    is_common: bool

    class Config:
        from_attributes = True


class ICD10SearchRequest(BaseModel):
    """Schema for ICD-10 search request."""
    query: str = Field(..., min_length=2, description="Search query (code or description)")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum results")
    chapter_filter: Optional[str] = Field(None, description="Filter by chapter")
    severity_filter: Optional[str] = Field(None, description="Filter by severity")
    common_only: bool = Field(default=False, description="Show only common codes")


class ICD10SearchResponse(BaseModel):
    """Schema for ICD-10 search response."""
    query: str
    results: List[ICD10CodeResponse]
    total: int
    search_time_ms: float


# Problem List Schemas
class ProblemListBase(BaseModel):
    """Base problem list schema."""
    icd10_code_id: int
    icd10_code: str
    problem_name: str
    description: Optional[str] = None
    status: str = Field(default="active", description="Problem status")
    onset_date: Optional[date] = None
    resolved_date: Optional[date] = None
    is_chronic: bool = False
    severity: Optional[str] = None
    clinical_notes: Optional[str] = None
    treatment_plan: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[date] = None
    certainty: Optional[str] = None


class ProblemListCreate(ProblemListBase):
    """Schema for creating a problem."""
    patient_id: int
    encounter_id: Optional[int] = None
    diagnosed_by: Optional[int] = None


class ProblemListUpdate(BaseModel):
    """Schema for updating a problem."""
    status: Optional[str] = None
    resolved_date: Optional[date] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    clinical_notes: Optional[str] = None
    treatment_plan: Optional[str] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[date] = None
    certainty: Optional[str] = None


class ProblemListResponse(ProblemListBase):
    """Schema for problem list response."""
    id: int
    patient_id: int
    encounter_id: Optional[int] = None
    diagnosed_by: Optional[int] = None
    recorded_by: int
    facility: Optional[str] = None
    chronicity_indicators: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    # ICD-10 code details
    icd10_description: Optional[str] = None
    icd10_chapter: Optional[str] = None

    # Attributions
    diagnosed_by_name: Optional[str] = None
    recorded_by_name: Optional[str] = None

    class Config:
        from_attributes = True


class PatientProblemListResponse(BaseModel):
    """Schema for patient problem list response."""
    patient_id: int
    medical_record_number: str
    full_name: str
    problems: List[ProblemListResponse]

    # Summary
    total_problems: int
    active_problems: int
    chronic_problems: int
    resolved_problems: int


class ICD10FavoriteCreate(BaseModel):
    """Schema for creating ICD-10 favorite."""
    icd10_code_id: int
    notes: Optional[str] = None


class ICD10FavoriteResponse(BaseModel):
    """Schema for ICD-10 favorite response."""
    id: int
    icd10_code_id: int
    notes: Optional[str] = None
    created_at: str

    # ICD-10 code details
    code: str
    description_indonesian: str

    class Config:
        from_attributes = True


class ICD10FavoritesListResponse(BaseModel):
    """Schema for user's ICD-10 favorites list."""
    user_id: int
    favorites: List[ICD10FavoriteResponse]
    total: int
