"""
Master Data Schemas

This module contains Pydantic schemas for master data management
including ICD-10 codes, LOINC codes, drugs, procedures, room classes, and insurance.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


# ICD-10 Code Schemas

class ICD10CodeBase(BaseModel):
    """Base ICD-10 code schema."""
    code: str = Field(..., max_length=10, description="ICD-10 code (e.g., A00, J01)")
    code_full: str = Field(..., max_length=20, description="Full code with decimal (e.g., A00.0)")
    chapter: str = Field(..., description="Chapter (I-XXII)")
    block: Optional[str] = Field(None, description="Block code range")
    description_indonesian: str = Field(..., description="Description in Indonesian")
    description_english: Optional[str] = Field(None, description="Description in English")
    severity: Optional[str] = Field(None, description="Severity level if applicable")
    inclusion_terms: Optional[List[str]] = Field(None, description="Inclusion terms")
    exclusion_terms: Optional[List[str]] = Field(None, description="Exclusion terms")
    notes: Optional[str] = Field(None, description="Additional notes")
    is_common: bool = Field(default=False, description="Mark as commonly used")


class ICD10CodeCreate(ICD10CodeBase):
    """Schema for creating ICD-10 codes."""
    pass


class ICD10CodeUpdate(BaseModel):
    """Schema for updating ICD-10 codes."""
    description_indonesian: Optional[str] = None
    description_english: Optional[str] = None
    severity: Optional[str] = None
    inclusion_terms: Optional[List[str]] = None
    exclusion_terms: Optional[List[str]] = None
    notes: Optional[str] = None
    is_common: Optional[bool] = None
    is_active: Optional[bool] = None


class ICD10CodeResponse(ICD10CodeBase):
    """Schema for ICD-10 code response."""
    id: int
    usage_count: int = Field(default=0, description="Usage tracking")
    is_active: bool = Field(default=True, description="Active status")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ICD10CodeSearchResponse(BaseModel):
    """Schema for ICD-10 code search results."""
    total: int
    results: List[ICD10CodeResponse]
    search_time_ms: Optional[int] = None


# LOINC Code Schemas

class LOINCCodeBase(BaseModel):
    """Base LOINC code schema."""
    loinc_num: str = Field(..., max_length=50, description="LOINC number")
    component: str = Field(..., description="Analyte/component name")
    property_attr: Optional[str] = Field(None, max_length=50, description="Property (e.g., MassConc, NCln)")
    time_aspect: Optional[str] = Field(None, max_length=50, description="Time aspect (e.g., Pt, 24h)")
    system: Optional[str] = Field(None, max_length=50, description="System (e.g., Serum, Urine)")
    scale_type: Optional[str] = Field(None, max_length=50, description="Scale type (e.g., Qn, Ord)")
    method_type: Optional[str] = Field(None, max_length=50, description="Method type")
    class_name: Optional[str] = Field(None, description="LOINC class")
    status: Optional[str] = Field(None, description="Status (ACTIVE, TRIAL, DISCOURAGED)")
    short_name: Optional[str] = Field(None, max_length=255, description="Short name")
    long_common_name: Optional[str] = Field(None, description="Long common name")
    example_units: Optional[str] = Field(None, max_length=100, description="Example units")
    units_and_range: Optional[str] = Field(None, description="Reference range")
    is_common: bool = Field(default=False, description="Mark as commonly used")


class LOINCCodeCreate(LOINCCodeBase):
    """Schema for creating LOINC codes."""
    pass


class LOINCCodeUpdate(BaseModel):
    """Schema for updating LOINC codes."""
    component: Optional[str] = None
    long_common_name: Optional[str] = None
    example_units: Optional[str] = None
    units_and_range: Optional[str] = None
    is_common: Optional[bool] = None
    is_active: Optional[bool] = None


class LOINCCodeResponse(LOINCCodeBase):
    """Schema for LOINC code response."""
    id: int
    usage_count: int = Field(default=0, description="Usage tracking")
    is_active: bool = Field(default=True, description="Active status")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LOINCCodeSearchResponse(BaseModel):
    """Schema for LOINC code search results."""
    total: int
    results: List[LOINCCodeResponse]
    search_time_ms: Optional[int] = None


# Drug Formulary Schemas

class DrugFormularyBase(BaseModel):
    """Base drug formulary schema."""
    generic_name: str = Field(..., max_length=255, description="Generic (scientific) name")
    brand_names: Optional[List[str]] = Field(None, description="List of brand names")
    dosage_form: Optional[str] = Field(None, max_length=50, description="Tablet, capsule, injection, etc.")
    strength: Optional[str] = Field(None, max_length=100, description="Strength (e.g., 500mg, 5mg/mL)")
    bpjs_code: Optional[str] = Field(None, max_length=50, description="BPJS formularium code")
    bpjs_covered: bool = Field(default=True, description="Covered by BPJS")
    atc_code: Optional[str] = Field(None, max_length=20, description="Anatomical Therapeutic Chemical code")
    atc_level: Optional[int] = Field(None, ge=1, le=5, description="ATC classification level (1-5)")
    ekatalog_code: Optional[str] = Field(None, max_length=50, description="e-Katalog LKPP code")
    manufacturer: Optional[str] = Field(None, max_length=255, description="Manufacturer name")
    is_narcotic: bool = Field(default=False, description="Narcotic drug")
    is_antibiotic: bool = Field(default=False, description="Antibiotic")
    requires_prescription: bool = Field(default=True, description="Requires prescription")
    cold_chain_required: bool = Field(default=False, description="Requires cold storage")
    storage_conditions: Optional[str] = Field(None, description="Storage requirements")
    default_dosage: Optional[str] = Field(None, max_length=100, description="Default dosage guideline")
    default_frequency: Optional[str] = Field(None, max_length=50, description="Default frequency")
    default_route: Optional[str] = Field(None, max_length=50, description="Default route (oral, IV, IM, etc.)")
    contraindications: Optional[List[str]] = Field(None, description="Contraindications")
    interactions: Optional[List[str]] = Field(None, description="Drug interactions")
    side_effects: Optional[List[str]] = Field(None, description="Common side effects")


class DrugFormularyCreate(DrugFormularyBase):
    """Schema for creating drug formulary entries."""
    pass


class DrugFormularyUpdate(BaseModel):
    """Schema for updating drug formulary entries."""
    generic_name: Optional[str] = None
    brand_names: Optional[List[str]] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    bpjs_code: Optional[str] = None
    bpjs_covered: Optional[bool] = None
    atc_code: Optional[str] = None
    ekatalog_code: Optional[str] = None
    manufacturer: Optional[str] = None
    is_narcotic: Optional[bool] = None
    is_antibiotic: Optional[bool] = None
    requires_prescription: Optional[bool] = None
    cold_chain_required: Optional[bool] = None
    storage_conditions: Optional[str] = None
    default_dosage: Optional[str] = None
    default_frequency: Optional[str] = None
    default_route: Optional[str] = None
    contraindications: Optional[List[str]] = None
    interactions: Optional[List[str]] = None
    side_effects: Optional[List[str]] = None
    is_active: Optional[bool] = None


class DrugFormularyResponse(DrugFormularyBase):
    """Schema for drug formulary response."""
    id: int
    is_active: bool = Field(default=True, description="Active status")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DrugFormularySearchResponse(BaseModel):
    """Schema for drug formulary search results."""
    total: int
    results: List[DrugFormularyResponse]
    search_time_ms: Optional[int] = None


# Procedure Code Schemas

class ProcedureCodeBase(BaseModel):
    """Base procedure code schema."""
    code: str = Field(..., max_length=50, description="Procedure code")
    code_system: str = Field(..., description="ICD-9-CM, LOINC, or LOCAL")
    code_type: Optional[str] = Field(None, description="LAB, RADIOLOGY, SURGERY, THERAPY")
    description_indonesian: str = Field(..., description="Description in Indonesian")
    description_english: Optional[str] = Field(None, description="Description in English")
    category: Optional[str] = Field(None, max_length=100, description="Procedure category")
    department: Optional[str] = Field(None, max_length=100, description="Performing department")
    bpjs_tariff_code: Optional[str] = Field(None, max_length=50, description="BPJS tariff code")
    bpjs_covered: bool = Field(default=True, description="Covered by BPJS")
    default_price: Optional[float] = Field(None, ge=0, description="Default procedure price")
    is_surgical: bool = Field(default=False, description="Surgical procedure")
    requires_authorization: bool = Field(default=False, description="Requires pre-authorization")
    preparation_instructions: Optional[str] = Field(None, description="Patient preparation instructions")
    contraindications: Optional[List[str]] = Field(None, description="Contraindications")
    risks: Optional[List[str]] = Field(None, description="Associated risks")
    is_common: bool = Field(default=False, description="Mark as commonly used")


class ProcedureCodeCreate(ProcedureCodeBase):
    """Schema for creating procedure codes."""
    pass


class ProcedureCodeUpdate(BaseModel):
    """Schema for updating procedure codes."""
    description_indonesian: Optional[str] = None
    description_english: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    bpjs_tariff_code: Optional[str] = None
    bpjs_covered: Optional[bool] = None
    default_price: Optional[float] = None
    is_surgical: Optional[bool] = None
    requires_authorization: Optional[bool] = None
    preparation_instructions: Optional[str] = None
    contraindications: Optional[List[str]] = None
    risks: Optional[List[str]] = None
    is_common: Optional[bool] = None
    is_active: Optional[bool] = None


class ProcedureCodeResponse(ProcedureCodeBase):
    """Schema for procedure code response."""
    id: int
    usage_count: int = Field(default=0, description="Usage tracking")
    is_active: bool = Field(default=True, description="Active status")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProcedureCodeSearchResponse(BaseModel):
    """Schema for procedure code search results."""
    total: int
    results: List[ProcedureCodeResponse]
    search_time_ms: Optional[int] = None


# Room Class Schemas

class RoomClassBase(BaseModel):
    """Base room class schema."""
    code: str = Field(..., max_length=20, description="Room class code (VVIP, VIP, 1, 2, 3)")
    name: str = Field(..., max_length=100, description="Room class name")
    name_indonesian: str = Field(..., max_length=100, description="Name in Indonesian")
    description: Optional[str] = Field(None, description="Description")
    daily_rate: float = Field(..., ge=0, description="Daily room rate")
    bpjs_package_rate: Optional[float] = Field(None, ge=0, description="BPJS INA-CBG package rate")
    capacity: int = Field(default=1, ge=1, description="Bed capacity per room")
    has_ac: bool = Field(default=False, description="Air conditioning")
    has_tv: bool = Field(default=False, description="Television")
    has_bathroom: bool = Field(default=True, description="Private bathroom")
    has_refrigerator: bool = Field(default=False, description="Refrigerator")
    amenities: Optional[List[str]] = Field(None, description="Additional amenities")
    nurses_station_distance: Optional[str] = Field(None, max_length=50, description="Proximity to nurses station")
    visitation_hours: Optional[str] = Field(None, max_length=100, description="Visitation hours")
    max_visitors: int = Field(default=2, ge=0, description="Maximum visitors")


class RoomClassCreate(RoomClassBase):
    """Schema for creating room classes."""
    pass


class RoomClassUpdate(BaseModel):
    """Schema for updating room classes."""
    name: Optional[str] = None
    name_indonesian: Optional[str] = None
    description: Optional[str] = None
    daily_rate: Optional[float] = None
    bpjs_package_rate: Optional[float] = None
    capacity: Optional[int] = None
    has_ac: Optional[bool] = None
    has_tv: Optional[bool] = None
    has_bathroom: Optional[bool] = None
    has_refrigerator: Optional[bool] = None
    amenities: Optional[List[str]] = None
    nurses_station_distance: Optional[str] = None
    visitation_hours: Optional[str] = None
    max_visitors: Optional[int] = None
    is_active: Optional[bool] = None


class RoomClassResponse(RoomClassBase):
    """Schema for room class response."""
    id: int
    is_active: bool = Field(default=True, description="Active status")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Insurance Company Schemas

class InsuranceCompanyBase(BaseModel):
    """Base insurance company schema."""
    code: str = Field(..., max_length=50, description="Insurance company code")
    name: str = Field(..., max_length=255, description="Insurance company name")
    insurance_type: str = Field(..., description="BPJS, ASURANSI, UMUM, CORPORATE")
    address: Optional[str] = Field(None, description="Company address")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone")
    email: Optional[str] = Field(None, max_length=255, description="Contact email")
    website: Optional[str] = Field(None, max_length=255, description="Website")
    contact_person: Optional[str] = Field(None, max_length=255, description="Contact person name")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Contact person phone")
    claims_address: Optional[str] = Field(None, description="Claims submission address")
    claims_email: Optional[str] = Field(None, max_length=255, description="Claims email")
    claims_phone: Optional[str] = Field(None, max_length=50, description="Claims phone")
    payment_terms: Optional[int] = Field(None, ge=0, description="Payment terms in days")
    credit_limit: Optional[float] = Field(None, ge=0, description="Credit limit")
    notes: Optional[str] = Field(None, description="Additional notes")


class InsuranceCompanyCreate(InsuranceCompanyBase):
    """Schema for creating insurance companies."""
    pass


class InsuranceCompanyUpdate(BaseModel):
    """Schema for updating insurance companies."""
    name: Optional[str] = None
    insurance_type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    claims_address: Optional[str] = None
    claims_email: Optional[str] = None
    claims_phone: Optional[str] = None
    payment_terms: Optional[int] = None
    credit_limit: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class InsuranceCompanyResponse(InsuranceCompanyBase):
    """Schema for insurance company response."""
    id: int
    is_active: bool = Field(default=True, description="Active status")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Insurance Plan Schemas

class InsurancePlanBase(BaseModel):
    """Base insurance plan schema."""
    company_id: int = Field(..., description="Insurance company ID")
    plan_code: str = Field(..., max_length=50, description="Plan code")
    plan_name: str = Field(..., max_length=255, description="Plan name")
    plan_type: Optional[str] = Field(None, description="INDIVIDUAL, FAMILY, CORPORATE")
    coverage_type: Optional[str] = Field(None, description="INPATIENT, OUTPATIENT, COMPREHENSIVE")
    deductible_amount: float = Field(default=0, ge=0, description="Annual deductible")
    co_insurance_percentage: int = Field(default=0, ge=0, le=100, description="Co-insurance %")
    co_pay_amount: float = Field(default=0, ge=0, description="Co-pay amount")
    out_of_pocket_max: Optional[float] = Field(None, ge=0, description="Annual out-of-pocket maximum")
    coverage_limit: Optional[float] = Field(None, ge=0, description="Annual coverage limit")
    pre_authorization_required: bool = Field(default=False, description="Pre-authorization required")
    network_type: Optional[str] = Field(None, description="Network type (PPO, HMO, EPO)")
    effective_date: Optional[datetime] = Field(None, description="Plan effective date")
    expiration_date: Optional[datetime] = Field(None, description="Plan expiration date")


class InsurancePlanCreate(InsurancePlanBase):
    """Schema for creating insurance plans."""
    pass


class InsurancePlanUpdate(BaseModel):
    """Schema for updating insurance plans."""
    plan_name: Optional[str] = None
    plan_type: Optional[str] = None
    coverage_type: Optional[str] = None
    deductible_amount: Optional[float] = None
    co_insurance_percentage: Optional[int] = None
    co_pay_amount: Optional[float] = None
    out_of_pocket_max: Optional[float] = None
    coverage_limit: Optional[float] = None
    pre_authorization_required: Optional[bool] = None
    network_type: Optional[str] = None
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class InsurancePlanResponse(InsurancePlanBase):
    """Schema for insurance plan response."""
    id: int
    is_active: bool = Field(default=True, description="Active status")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Reference Data Schemas

class ReferenceDataBase(BaseModel):
    """Base reference data schema."""
    category: str = Field(..., max_length=100, description="Data category")
    code: str = Field(..., max_length=100, description="Reference code")
    name: str = Field(..., max_length=255, description="Reference name")
    name_indonesian: Optional[str] = Field(None, max_length=255, description="Name in Indonesian")
    description: Optional[str] = Field(None, description="Description")
    parent_id: Optional[int] = Field(None, description="Parent reference for hierarchy")
    display_order: int = Field(default=0, description="Display order")
    attributes: Optional[Dict[str, Any]] = Field(None, description="Additional attributes")


class ReferenceDataCreate(ReferenceDataBase):
    """Schema for creating reference data."""
    pass


class ReferenceDataUpdate(BaseModel):
    """Schema for updating reference data."""
    name: Optional[str] = None
    name_indonesian: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    display_order: Optional[int] = None
    attributes: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ReferenceDataResponse(ReferenceDataBase):
    """Schema for reference data response."""
    id: int
    is_active: bool = Field(default=True, description="Active status")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Master Data Statistics Schemas

class MasterDataStatistics(BaseModel):
    """Schema for master data statistics."""
    icd10_codes_total: int = 0
    icd10_codes_active: int = 0
    loinc_codes_total: int = 0
    loinc_codes_active: int = 0
    drugs_total: int = 0
    drugs_active: int = 0
    procedures_total: int = 0
    procedures_active: int = 0
    insurance_companies_total: int = 0
    insurance_companies_active: int = 0
    insurance_plans_total: int = 0
    insurance_plans_active: int = 0
    room_classes_total: int = 0
    room_classes_active: int = 0


class DataImportRequest(BaseModel):
    """Schema for data import request."""
    data_type: str = Field(..., description="Type of data to import (icd10, loinc, drugs, procedures)")
    source_file: Optional[str] = Field(None, description="Source file path or URL")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Inline data to import")
    overwrite: bool = Field(default=False, description="Overwrite existing data")
    batch_size: int = Field(default=100, ge=1, le=1000, description="Batch size for imports")


class DataImportResponse(BaseModel):
    """Schema for data import response."""
    data_type: str
    total_records: int
    success_count: int
    failed_count: int
    errors: List[str] = Field(default_factory=list)
    import_time_seconds: float
