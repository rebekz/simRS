"""
Master Data Models

This module contains database models for managing master/reference data
including ICD-10 codes, LOINC codes, drugs, procedures, room classes, and insurance.

Key models:
- ICD10Code: ICD-10-CM Indonesia diagnosis codes
- LOINCCode: LOINC laboratory test codes
- DrugFormulary: Drug formulary with generic and brand names
- ProcedureCode: Medical procedure codes (ICD-9-CM, local codes)
- RoomClass: Room class configuration with rates
- InsuranceCompany: Insurance companies and plans
- ReferenceData: Generic reference data storage
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM, JSONB

from backend.app.db.base_class import Base


class ICD10Code(Base):
    """
    ICD-10-CM Indonesia diagnosis codes.

    This table stores the complete ICD-10-CM (Indonesia) diagnosis coding system
    used for classifying diseases and health problems.
    """
    __tablename__ = "icd10_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True, comment="ICD-10 code (e.g., A00, J01)")
    code_full = Column(String(20), nullable=False, comment="Full code with decimal (e.g., A00.0)")
    chapter = Column(String(20), nullable=False, index=True, comment="Chapter (I-XXII)")
    block = Column(String(20), nullable=True, comment="Block code range")
    description_indonesian = Column(Text, nullable=False, comment="Description in Indonesian")
    description_english = Column(Text, nullable=True, comment="Description in English")
    severity = Column(String(20), nullable=True, comment="Severity level if applicable")
    inclusion_terms = Column(JSONB, nullable=True, comment="Inclusion terms")
    exclusion_terms = Column(JSONB, nullable=True, comment="Exclusion terms")
    notes = Column(Text, nullable=True, comment="Additional notes")
    is_common = Column(Boolean, default=False, nullable=False, comment="Mark as commonly used")
    usage_count = Column(Integer, default=0, nullable=False, comment="Usage tracking")
    is_active = Column(Boolean, default=True, nullable=False, comment="Active status")
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    # Relationships
    diagnoses = relationship("Diagnosis", back_populates="icd10_code")


class LOINCCode(Base):
    """
    LOINC (Logical Observation Identifiers Names and Codes) laboratory test codes.

    This table stores LOINC codes for standardizing laboratory test identifiers.
    """
    __tablename__ = "loinc_codes"

    id = Column(Integer, primary_key=True, index=True)
    loinc_num = Column(String(50), unique=True, nullable=False, index=True, comment="LOINC number")
    component = Column(Text, nullable=False, comment="Analyte/component name")
    property_attr = Column(String(50), nullable=True, comment="Property (e.g., MassConc, NCln)")
    time_aspect = Column(String(50), nullable=True, comment="Time aspect (e.g., Pt, 24h)")
    system = Column(String(50), nullable=True, comment="System (e.g., Serum, Urine)")
    scale_type = Column(String(50), nullable=True, comment="Scale type (e.g., Qn, Ord)")
    method_type = Column(String(50), nullable=True, comment="Method type")
    class_name = Column(String(20), nullable=True, index=True, comment="LOINC class")
    status = Column(String(20), nullable=True, comment="Status (ACTIVE, TRIAL, DISCOURAGED)")
    short_name = Column(String(255), nullable=True, comment="Short name")
    long_common_name = Column(Text, nullable=True, comment="Long common name")
    example_units = Column(String(100), nullable=True, comment="Example units")
    units_and_range = Column(Text, nullable=True, comment="Reference range")
    is_common = Column(Boolean, default=False, nullable=False, comment="Mark as commonly used")
    usage_count = Column(Integer, default=0, nullable=False, comment="Usage tracking")
    is_active = Column(Boolean, default=True, nullable=False, comment="Active status")
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    # Index for full-text search
    __table_args__ = (
        Index('ix_loinc_codes_component_fulltext', 'component', postgresql_using='gin', postgresql_ops={'component': 'gin_trgm_ops'}),
    )


class DrugFormulary(Base):
    """
    Drug formulary with generic and brand names.

    This table stores the complete drug formulary including generic names,
    brand names, BPJS codes, ATC codes, and regulatory information.
    """
    __tablename__ = "drug_formulary"

    id = Column(Integer, primary_key=True, index=True)
    generic_name = Column(String(255), nullable=False, index=True, comment="Generic (scientific) name")
    brand_names = Column(JSONB, nullable=True, comment="List of brand names")
    dosage_form = Column(String(50), nullable=True, index=True, comment="Tablet, capsule, injection, etc.")
    strength = Column(String(100), nullable=True, comment="Strength (e.g., 500mg, 5mg/mL)")
    bpjs_code = Column(String(50), nullable=True, index=True, comment="BPJS formularium code")
    bpjs_covered = Column(Boolean, default=True, nullable=False, comment="Covered by BPJS")
    atc_code = Column(String(20), nullable=True, index=True, comment="Anatomical Therapeutic Chemical code")
    atc_level = Column(Integer, nullable=True, comment="ATC classification level (1-5)")
    ekatalog_code = Column(String(50), nullable=True, comment="e-Katalog LKPP code")
    manufacturer = Column(String(255), nullable=True, comment="Manufacturer name")
    is_narcotic = Column(Boolean, default=False, nullable=False, comment="Narcotic drug")
    is_antibiotic = Column(Boolean, default=False, nullable=False, comment="Antibiotic")
    requires_prescription = Column(Boolean, default=True, nullable=False, comment="Requires prescription")
    cold_chain_required = Column(Boolean, default=False, nullable=False, comment="Requires cold storage")
    storage_conditions = Column(Text, nullable=True, comment="Storage requirements")
    default_dosage = Column(String(100), nullable=True, comment="Default dosage guideline")
    default_frequency = Column(String(50), nullable=True, comment="Default frequency")
    default_route = Column(String(50), nullable=True, comment="Default route (oral, IV, IM, etc.)")
    contraindications = Column(JSONB, nullable=True, comment="Contraindications")
    interactions = Column(JSONB, nullable=True, comment="Drug interactions")
    side_effects = Column(JSONB, nullable=True, comment="Common side effects")
    is_active = Column(Boolean, default=True, nullable=False, comment="Active status")
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    # Index for full-text search
    __table_args__ = (
        Index('ix_drug_formulary_generic_name_fulltext', 'generic_name', postgresql_using='gin', postgresql_ops={'generic_name': 'gin_trgm_ops'}),
    )


class ProcedureCode(Base):
    """
    Medical procedure codes (ICD-9-CM and local codes).

    This table stores procedure codes for medical procedures, surgeries,
    diagnostic tests, and therapeutic interventions.
    """
    __tablename__ = "procedure_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment="Procedure code")
    code_system = Column(String(50), nullable=False, index=True, comment="ICD-9-CM, LOINC, or LOCAL")
    code_type = Column(String(50), nullable=True, index=True, comment="LAB, RADIOLOGY, SURGERY, THERAPY")
    description_indonesian = Column(Text, nullable=False, comment="Description in Indonesian")
    description_english = Column(Text, nullable=True, comment="Description in English")
    category = Column(String(100), nullable=True, index=True, comment="Procedure category")
    department = Column(String(100), nullable=True, index=True, comment="Performing department")
    bpjs_tariff_code = Column(String(50), nullable=True, comment="BPJS tariff code")
    bpjs_covered = Column(Boolean, default=True, nullable=False, comment="Covered by BPJS")
    default_price = Column(Numeric(15, 2), nullable=True, comment="Default procedure price")
    is_surgical = Column(Boolean, default=False, nullable=False, comment="Surgical procedure")
    requires_authorization = Column(Boolean, default=False, nullable=False, comment="Requires pre-authorization")
    preparation_instructions = Column(Text, nullable=True, comment="Patient preparation instructions")
    contraindications = Column(JSONB, nullable=True, comment="Contraindications")
    risks = Column(JSONB, nullable=True, comment="Associated risks")
    is_common = Column(Boolean, default=False, nullable=False, comment="Mark as commonly used")
    usage_count = Column(Integer, default=0, nullable=False, comment="Usage tracking")
    is_active = Column(Boolean, default=True, nullable=False, comment="Active status")
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    # Index for full-text search
    __table_args__ = (
        Index('ix_procedure_codes_description_fulltext', 'description_indonesian', postgresql_using='gin', postgresql_ops={'description_indonesian': 'gin_trgm_ops'}),
    )


class RoomClass(Base):
    """
    Room class configuration with rates.

    This table stores room classes (VVIP, VIP, Kelas 1-3) with their
    associated rates, amenities, and capacity information.
    """
    __tablename__ = "room_classes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, comment="Room class code (VVIP, VIP, 1, 2, 3)")
    name = Column(String(100), nullable=False, comment="Room class name")
    name_indonesian = Column(String(100), nullable=False, comment="Name in Indonesian")
    description = Column(Text, nullable=True, comment="Description")
    daily_rate = Column(Numeric(15, 2), nullable=False, comment="Daily room rate")
    bpjs_package_rate = Column(Numeric(15, 2), nullable=True, comment="BPJS INA-CBG package rate")
    capacity = Column(Integer, default=1, nullable=False, comment="Bed capacity per room")
    has_ac = Column(Boolean, default=False, nullable=False, comment="Air conditioning")
    has_tv = Column(Boolean, default=False, nullable=False, comment="Television")
    has_bathroom = Column(Boolean, default=True, nullable=False, comment="Private bathroom")
    has_refrigerator = Column(Boolean, default=False, nullable=False, comment="Refrigerator")
    amenities = Column(JSONB, nullable=True, comment="Additional amenities")
    nurses_station_distance = Column(String(50), nullable=True, comment="Proximity to nurses station")
    visitation_hours = Column(String(100), nullable=True, comment="Visitation hours")
    max_visitors = Column(Integer, default=2, nullable=False, comment="Maximum visitors")
    is_active = Column(Boolean, default=True, nullable=False, comment="Active status")
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)


class InsuranceCompany(Base):
    """
    Insurance companies and plans.

    This table stores insurance company information including BPJS,
    private insurance companies, and corporate plans.
    """
    __tablename__ = "insurance_companies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment="Insurance company code")
    name = Column(String(255), nullable=False, comment="Insurance company name")
    insurance_type = Column(String(50), nullable=False, index=True, comment="BPJS, ASURANSI, UMUM, CORPORATE")
    address = Column(Text, nullable=True, comment="Company address")
    phone = Column(String(50), nullable=True, comment="Contact phone")
    email = Column(String(255), nullable=True, comment="Contact email")
    website = Column(String(255), nullable=True, comment="Website")
    contact_person = Column(String(255), nullable=True, comment="Contact person name")
    contact_phone = Column(String(50), nullable=True, comment="Contact person phone")
    claims_address = Column(Text, nullable=True, comment="Claims submission address")
    claims_email = Column(String(255), nullable=True, comment="Claims email")
    claims_phone = Column(String(50), nullable=True, comment="Claims phone")
    payment_terms = Column(Integer, nullable=True, comment="Payment terms in days")
    credit_limit = Column(Numeric(15, 2), nullable=True, comment="Credit limit")
    is_active = Column(Boolean, default=True, nullable=False, comment="Active status")
    notes = Column(Text, nullable=True, comment="Additional notes")
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    # Relationships
    plans = relationship("InsurancePlan", back_populates="company", cascade="all, delete-orphan")


class InsurancePlan(Base):
    """
    Insurance plans and policies.

    This table stores specific insurance plans offered by insurance companies.
    """
    __tablename__ = "insurance_plans"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("insurance_companies.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_code = Column(String(50), nullable=False, comment="Plan code")
    plan_name = Column(String(255), nullable=False, comment="Plan name")
    plan_type = Column(String(50), nullable=True, comment="INDIVIDUAL, FAMILY, CORPORATE")
    coverage_type = Column(String(50), nullable=True, comment="INPATIENT, OUTPATIENT, COMPREHENSIVE")
    deductible_amount = Column(Numeric(15, 2), default=0, nullable=False, comment="Annual deductible")
    co_insurance_percentage = Column(Integer, default=0, nullable=False, comment="Co-insurance %")
    co_pay_amount = Column(Numeric(15, 2), default=0, nullable=False, comment="Co-pay amount")
    out_of_pocket_max = Column(Numeric(15, 2), nullable=True, comment="Annual out-of-pocket maximum")
    coverage_limit = Column(Numeric(15, 2), nullable=True, comment="Annual coverage limit")
    pre_authorization_required = Column(Boolean, default=False, nullable=False, comment="Pre-authorization required")
    network_type = Column(String(50), nullable=True, comment="Network type (PPO, HMO, EPO)")
    is_active = Column(Boolean, default=True, nullable=False, comment="Active status")
    effective_date = Column(DateTime(timezone=True), nullable=True, comment="Plan effective date")
    expiration_date = Column(DateTime(timezone=True), nullable=True, comment="Plan expiration date")
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    # Relationships
    company = relationship("InsuranceCompany", back_populates="plans")


class ReferenceData(Base):
    """
    Generic reference data storage.

    This table provides flexible storage for various types of reference data
    that don't require dedicated tables.
    """
    __tablename__ = "reference_data"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False, index=True, comment="Data category")
    code = Column(String(100), nullable=False, index=True, comment="Reference code")
    name = Column(String(255), nullable=False, comment="Reference name")
    name_indonesian = Column(String(255), nullable=True, comment="Name in Indonesian")
    description = Column(Text, nullable=True, comment="Description")
    parent_id = Column(Integer, ForeignKey("reference_data.id", ondelete="CASCADE"), nullable=True, index=True, comment="Parent reference for hierarchy")
    display_order = Column(Integer, default=0, nullable=False, comment="Display order")
    is_active = Column(Boolean, default=True, nullable=False, comment="Active status")
    attributes = Column(JSONB, nullable=True, comment="Additional attributes")
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    # Self-referential relationship for hierarchy
    parent = relationship("ReferenceData", remote_side=[id], backref="children")
