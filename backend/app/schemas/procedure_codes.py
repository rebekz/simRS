"""Procedure Code Schemas for Lab and Radiology Services

This module provides Pydantic schemas for managing procedure codes:
- Laboratory test codes
- Radiology/imaging procedure codes
- Procedure code search and autocomplete
- BPJS coverage mapping
- Pricing information
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# =============================================================================
# Procedure Code Enums
# =============================================================================

class ProcedureCodeType(str, Enum):
    """Types of procedure codes"""
    LABORATORY = "laboratory"  # Lab tests
    RADIOLOGY = "radiology"  # Imaging studies
    PATHOLOGY = "pathology"  # Pathology services
    CARDIOLOGY = "cardiology"  # Cardiac procedures
    ENDOSCOPY = "endoscopy"  # Endoscopic procedures
    THERAPEUTIC = "therapeutic"  # Therapeutic procedures
    DIAGNOSTIC = "diagnostic"  # Diagnostic procedures


class ProcedureStatus(str, Enum):
    """Procedure code status"""
    ACTIVE = "active"  # Available for ordering
    INACTIVE = "inactive"  # Not available
    DEPRECATED = "deprecated"  # Replaced by newer code
    TESTING = "testing"  # Under testing


class SpecimenRequirement(str, Enum):
    """Specimen requirements for lab procedures"""
    BLOOD = "blood"
    SERUM = "serum"
    PLASMA = "plasma"
    URINE = "urine"
    SWAB = "swab"
    TISSUE = "tissue"
    CEREOSPINAL_FLUID = "cerebrospinal_fluid"
    SPUTUM = "sputum"
    STOOL = "stool"
    NONE = "none"  # For radiology


# =============================================================================
# Procedure Code Schemas
# =============================================================================

class ProcedureCodeBase(BaseModel):
    """Base procedure code schema"""
    code: str = Field(..., description="Unique procedure code (e.g., 'CBC', 'CTABD')")
    name: str = Field(..., description="Full procedure name")
    code_type: ProcedureCodeType
    category: Optional[str] = Field(None, description="Category/subcategory (e.g., 'Hematology', 'CT Imaging')")
    description: Optional[str] = Field(None, description="Detailed description")


class ProcedureCodeCreate(ProcedureCodeBase):
    """Schema for creating a procedure code"""
    bpjs_code: Optional[str] = Field(None, description="BPJS procedure code if applicable")
    bpjs_covered: bool = Field(True, description="Covered by BPJS")
    bpjs_description: Optional[str] = Field(None, description="BPJS description if different")

    # Pricing
    standard_cost: Optional[float] = Field(None, description="Standard cost for self-pay")
    bpjs_tariff: Optional[float] = Field(None, description="BPJS tariff amount")
    cost_to_patient: Optional[float] = Field(None, description="Patient cost after BPJS")

    # Lab-specific
    specimen_requirement: Optional[SpecimenRequirement] = None
    specimen_container: Optional[str] = Field(None, description="Container type (e.g., 'Red top tube', 'Urine cup')")
    fasting_required: bool = Field(False, description="Patient must fast before test")
    fasting_duration_hours: Optional[int] = Field(None, ge=1, description="Hours of fasting required")
    turnaround_time_hours: Optional[int] = Field(None, ge=1, description="Expected turnaround time")
    sample_stability_hours: Optional[int] = Field(None, description="Sample stability period")

    # Radiology-specific
    modality: Optional[str] = Field(None, description="Modality (e.g., 'CT', 'MRI', 'XRAY')")
    contrast_required: bool = Field(False, description="Contrast required")
    contrast_type: Optional[str] = Field(None, description="Type of contrast if required")
    study_duration_minutes: Optional[int] = Field(None, ge=1, description="Expected study duration")

    # Clinical information
    clinical_indications: Optional[List[str]] = Field(None, description="Common clinical indications")
    reference_range: Optional[str] = Field(None, description="Normal reference range")
    unit_of_measure: Optional[str] = Field(None, description="Result unit (e.g., 'mg/dL', 'g/dL')")

    # Ordering rules
    requires_prior_auth: bool = Field(False, description="Requires prior authorization")
    age_min: Optional[int] = Field(None, description="Minimum patient age")
    age_max: Optional[int] = Field(None, description="Maximum patient age")
    gender_specific: Optional[str] = Field(None, description="Gender restriction: 'male', 'female', 'both'")
    pregnancy_contraindicated: bool = Field(False, description="Contraindicated in pregnancy")

    # Additional metadata
    synonyms: Optional[List[str]] = Field(None, description="Alternative names for search")
    keywords: Optional[List[str]] = Field(None, description="Search keywords")
    loinc_code: Optional[str] = Field(None, description="LOINC code for lab tests")
    snomed_code: Optional[str] = Field(None, description="SNOMED CT code")
    cpt_code: Optional[str] = Field(None, description="CPT code")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate procedure code format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Procedure code cannot be empty")
        return v.upper().strip()

    @field_validator("age_max")
    @classmethod
    def validate_age_range(cls, v: Optional[int], info) -> Optional[int]:
        """Validate age range"""
        if v is not None and "age_min" in info.data and info.data["age_min"] is not None:
            if v <= info.data["age_min"]:
                raise ValueError("age_max must be greater than age_min")
        return v


class ProcedureCodeUpdate(BaseModel):
    """Schema for updating a procedure code"""
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProcedureStatus] = None

    # BPJS and pricing
    bpjs_code: Optional[str] = None
    bpjs_covered: Optional[bool] = None
    bpjs_description: Optional[str] = None
    standard_cost: Optional[float] = None
    bpjs_tariff: Optional[float] = None
    cost_to_patient: Optional[float] = None

    # Lab-specific
    specimen_requirement: Optional[SpecimenRequirement] = None
    specimen_container: Optional[str] = None
    fasting_required: Optional[bool] = None
    fasting_duration_hours: Optional[int] = None
    turnaround_time_hours: Optional[int] = None
    sample_stability_hours: Optional[int] = None

    # Radiology-specific
    modality: Optional[str] = None
    contrast_required: Optional[bool] = None
    contrast_type: Optional[str] = None
    study_duration_minutes: Optional[int] = None

    # Clinical information
    clinical_indications: Optional[List[str]] = None
    reference_range: Optional[str] = None
    unit_of_measure: Optional[str] = None

    # Ordering rules
    requires_prior_auth: Optional[bool] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    gender_specific: Optional[str] = None
    pregnancy_contraindicated: Optional[bool] = None

    # Metadata
    synonyms: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    loinc_code: Optional[str] = None
    snomed_code: Optional[str] = None
    cpt_code: Optional[str] = None


class ProcedureCodeResponse(ProcedureCodeBase):
    """Schema for procedure code response"""
    id: int
    status: ProcedureStatus

    # BPJS and pricing
    bpjs_code: Optional[str] = None
    bpjs_covered: bool
    bpjs_description: Optional[str] = None
    standard_cost: Optional[float] = None
    bpjs_tariff: Optional[float] = None
    cost_to_patient: Optional[float] = None

    # Lab-specific
    specimen_requirement: Optional[SpecimenRequirement] = None
    specimen_container: Optional[str] = None
    fasting_required: bool
    fasting_duration_hours: Optional[int] = None
    turnaround_time_hours: Optional[int] = None
    sample_stability_hours: Optional[int] = None

    # Radiology-specific
    modality: Optional[str] = None
    contrast_required: bool
    contrast_type: Optional[str] = None
    study_duration_minutes: Optional[int] = None

    # Clinical information
    clinical_indications: Optional[List[str]] = None
    reference_range: Optional[str] = None
    unit_of_measure: Optional[str] = None

    # Ordering rules
    requires_prior_auth: bool
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    gender_specific: Optional[str] = None
    pregnancy_contraindicated: bool

    # Metadata
    synonyms: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    loinc_code: Optional[str] = None
    snomed_code: Optional[str] = None
    cpt_code: Optional[str] = None

    # Usage statistics
    order_count_last_30_days: Optional[int] = None
    order_count_last_90_days: Optional[int] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Procedure Code List Schemas
# =============================================================================

class ProcedureCodeListResponse(BaseModel):
    """Schema for procedure code list response with pagination"""
    procedures: List[ProcedureCodeResponse]
    total: int
    page: int
    page_size: int
    filters_applied: Optional[Dict[str, Any]] = None


# =============================================================================
# Procedure Code Search Schemas
# =============================================================================

class ProcedureCodeSearchResponse(BaseModel):
    """Schema for procedure code search result"""
    id: int
    code: str
    name: str
    code_type: ProcedureCodeType
    category: Optional[str] = None
    bpjs_covered: bool
    standard_cost: Optional[float] = None

    # Quick reference fields
    specimen_requirement: Optional[SpecimenRequirement] = None
    fasting_required: bool = False
    turnaround_time_hours: Optional[int] = None
    contrast_required: bool = False
    modality: Optional[str] = None

    # Relevance score for search ranking
    relevance_score: Optional[float] = None


class ProcedureCodeSearchRequest(BaseModel):
    """Schema for procedure code search request"""
    query: str = Field(..., min_length=2, description="Search query")
    code_type: Optional[ProcedureCodeType] = Field(None, description="Filter by code type")
    category: Optional[str] = Field(None, description="Filter by category")
    bpjs_covered_only: bool = Field(False, description="Only show BPJS covered procedures")
    active_only: bool = Field(True, description="Only show active procedures")
    include_deprecated: bool = Field(False, description="Include deprecated codes")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class ProcedureCodeSearchResults(BaseModel):
    """Schema for procedure code search response"""
    query: str
    results: List[ProcedureCodeSearchResponse]
    total: int
    page: int
    page_size: int
    did_you_mean: Optional[List[str]] = Field(None, description="Suggestions for typos")


# =============================================================================
# Procedure Code Autocomplete Schemas
# =============================================================================

class ProcedureCodeAutocompleteRequest(BaseModel):
    """Schema for procedure code autocomplete request"""
    query: str = Field(..., min_length=1, description="Partial code or name")
    code_type: Optional[ProcedureCodeType] = None
    max_results: int = Field(10, ge=1, le=50)


class ProcedureCodeAutocompleteResponse(BaseModel):
    """Schema for procedure code autocomplete response"""
    suggestions: List[Dict[str, Any]]  # Each dict has: code, name, code_type
    query: str


# =============================================================================
# Procedure Code Group Schemas
# =============================================================================

class ProcedureCodeGroup(BaseModel):
    """Schema for a group of related procedure codes (e.g., panels, bundles)"""
    id: int
    group_code: str = Field(..., description="Group code (e.g., 'BMP', 'CMP', 'CTCHEST')")
    group_name: str = Field(..., description="Group name (e.g., 'Basic Metabolic Panel')")
    group_type: ProcedureCodeType
    description: Optional[str] = None
    procedure_codes: List[str] = Field(..., description="List of constituent procedure codes")
    discount_percentage: Optional[float] = Field(None, description="Discount if ordered as group")
    is_active: bool = True


class ProcedureCodeGroupCreate(BaseModel):
    """Schema for creating a procedure code group"""
    group_code: str
    group_name: str
    group_type: ProcedureCodeType
    description: Optional[str] = None
    procedure_codes: List[str] = Field(..., min_items=2)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)


class ProcedureCodeGroupResponse(BaseModel):
    """Schema for procedure code group response with details"""
    id: int
    group_code: str
    group_name: str
    group_type: ProcedureCodeType
    description: Optional[str] = None
    procedure_codes: List[ProcedureCodeSearchResponse]
    discount_percentage: Optional[float] = None
    total_standard_cost: Optional[float] = None
    discounted_cost: Optional[float] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Procedure Code Favorites Schemas
# =============================================================================

class ProviderFavoriteProcedure(BaseModel):
    """Schema for provider's frequently ordered procedures"""
    provider_id: int
    procedure_code_id: int
    order_count: int
    last_ordered: Optional[datetime] = None
    procedure_details: Optional[ProcedureCodeSearchResponse] = None


class ProviderFavoriteProceduresResponse(BaseModel):
    """Schema for provider's favorite procedures list"""
    provider_id: int
    favorites: List[ProviderFavoriteProcedure]
    total: int
