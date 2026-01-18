"""Procedure Code Catalog Models for STORY-018: Lab/Radiology Ordering

This module provides database models for:
- LOINC codes (laboratory tests)
- ICD-10-PCS codes (procedures)
- Local lab codes
- Local radiology codes
Follows patterns from ICD10 code catalog
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


# =============================================================================
# Procedure Code Enums
# =============================================================================

class ProcedureCodeType:
    """Procedure code type constants"""
    LOINC = "loinc"  # Laboratory tests
    ICD10_PCS = "icd10_pcs"  # ICD-10 Procedure Coding System
    LOCAL_LAB = "local_lab"  # Local laboratory codes
    LOCAL_RADIO = "local_radio"  # Local radiology codes
    CPT4 = "cpt4"  # CPT-4 / HCPCS codes


# =============================================================================
# Procedure Code Models
# =============================================================================

class ProcedureCode(Base):
    """
    Unified procedure code catalog for lab tests and radiology procedures.

    Supports multiple coding systems:
    - LOINC: Laboratory test codes
    - ICD-10-PCS: Procedure codes
    - CPT-4: Current Procedural Terminology
    - Local codes: Hospital-specific lab and radiology codes
    """
    __tablename__ = "procedure_codes"

    id = Column(Integer, primary_key=True, index=True)

    # Code identification
    code_type = Column(String(20), nullable=False, index=True)  # loinc, icd10_pcs, local_lab, local_radio, cpt4
    code = Column(String(50), nullable=False, index=True)
    code_system = Column(String(100), nullable=True)  # Official code system name
    code_system_version = Column(String(50), nullable=True)  # e.g., "2.74" for LOINC

    # Display information
    display_name = Column(String(255), nullable=False)  # Short display name
    full_name = Column(Text, nullable=True)  # Full descriptive name
    synonym = Column(JSONB, nullable=True)  # Alternative names/synonyms

    # Classification
    category = Column(String(100), nullable=True, index=True)  # e.g., "hematology", "imaging"
    subcategory = Column(String(100), nullable=True, index=True)  # e.g., "cbc", "xray"
    department = Column(String(100), nullable=True)  # e.g., "laboratory", "radiology"

    # Detailed description
    description = Column(Text, nullable=True)  # Full description
    clinical_indication = Column(Text, nullable=True)  # When to order
    specimen_requirements = Column(JSONB, nullable=True)  # Specimen type, volume, container
    preparation_instructions = Column(Text, nullable=True)  # Patient prep (fasting, etc.)

    # Technical details
    methodology = Column(String(255), nullable=True)  # Test method (for lab)
    modality = Column(String(50), nullable=True)  # Imaging modality (for radiology)
    body_system = Column(String(100), nullable=True)  # Body system examined
    loinc_system = Column(String(100), nullable=True)  # LOINC system (e.g., "Blood")
    loinc_scale = Column(String(50), nullable=True)  # Qn, Ord, Nom, etc.
    loinc_time_aspect = Column(String(50), nullable=True)  # Pt, Pt^n, etc.
    loinc_properties = Column(JSONB, nullable=True)  # Additional LOINC properties

    # Reference and units
    reference_range = Column(String(255), nullable=True)  # Normal range
    unit = Column(String(50), nullable=True)  # Unit of measure (for lab)
    critical_values = Column(JSONB, nullable=True)  # Critical value ranges
    interpretive_info = Column(Text, nullable=True)

    # Cost and coverage
    base_cost = Column(Integer, nullable=True)  # Base cost in IDR
    bpjs_tariff = Column(Integer, nullable=True)  # BPJS tariff
    bpjs_code = Column(String(50), nullable=True)  # BPJS procedure code
    is_bpjs_covered = Column(Boolean, default=True, nullable=False)

    # Operational
    is_active = Column(Boolean, server_default="true", nullable=False, index=True)
    is_orderable = Column(Boolean, server_default="true", nullable=False)  # Can be ordered directly
    requires_approval = Column(Boolean, default=False, nullable=False)  # Requires prior approval
    requires_contrast = Column(Boolean, default=False, nullable=False)  # For radiology
    estimated_duration_minutes = Column(Integer, nullable=True)
    turnaround_time_hours = Column(Integer, nullable=True)  # Expected TAT

    # Usage tracking
    usage_count = Column(Integer, server_default="0", nullable=False)
    is_common = Column(Boolean, server_default="false", nullable=False, index=True)
    is_favorite = Column(Boolean, server_default="false", nullable=False)

    # External mappings
    icd10_pcs_code = Column(String(20), nullable=True)  # Related ICD-10-PCS code
    cpt_code = Column(String(20), nullable=True)  # Related CPT-4 code
    snomed_ct_code = Column(String(50), nullable=True)  # SNOMED CT mapping
    ndc_code = Column(String(20), nullable=True)  # National Drug Code (for reagents)

    # Metadata and notes
    procedure_metadata = Column(JSONB, nullable=True)  # Additional metadata
    notes = Column(Text, nullable=True)
    warnings = Column(Text, nullable=True)  # Safety warnings

    # System fields
    created_at = Column("created_at", String(50), nullable=False)
    updated_at = Column("updated_at", String(50), nullable=False)


class ProcedureCodeUserFavorite(Base):
    """User's favorite procedure codes."""
    __tablename__ = "procedure_code_user_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    procedure_code_id = Column(Integer, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    frequency = Column(Integer, server_default="0", nullable=False)  # Usage frequency
    created_at = Column(String(50), nullable=False)
