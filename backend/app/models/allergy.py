"""Allergy Tracking model for STORY-013: Allergy Tracking

This module defines the database model for patient allergy tracking with
severity classification, reaction recording, and source documentation.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


# Allergy type enum
allergy_type_enum = ENUM(
    'drug',
    'food',
    'environmental',
    'other',
    name='allergy_type',
    create_type=True,
)


# Allergy severity enum
allergy_severity_enum = ENUM(
    'mild',
    'moderate',
    'severe',
    'life_threatening',
    name='allergy_severity',
    create_type=True,
)


# Allergy source enum (how the allergy was identified)
allergy_source_enum = ENUM(
    'patient_reported',
    'tested',
    'observed',
    'inferred',
    name='allergy_source',
    create_type=True,
)


# Allergy status enum
allergy_status_enum = ENUM(
    'active',
    'resolved',
    'unconfirmed',
    name='allergy_status',
    create_type=True,
)


class Allergy(Base):
    """Patient allergy record for clinical safety and adverse reaction prevention."""
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)

    # Allergy classification
    allergy_type = Column(allergy_type_enum, nullable=False, index=True)
    allergen = Column(String(500), nullable=False, index=True)  # Substance causing allergy
    allergen_code = Column(String(100), nullable=True, index=True)  # Standard code (e.g., RxNorm, UNII)

    # Severity and reaction
    severity = Column(allergy_severity_enum, nullable=False, index=True)
    reaction = Column(Text, nullable=False)  # Description of reaction
    reaction_details = Column(JSONB, nullable=True)  # Structured reaction data (symptoms, timing, etc.)

    # Status and onset
    status = Column(allergy_status_enum, nullable=False, index=True, default='active')
    onset_date = Column(Date, nullable=True)  # When allergy was first observed
    resolved_date = Column(Date, nullable=True)  # When allergy was resolved (if applicable)

    # Source documentation
    source = Column(allergy_source_enum, nullable=False, default='patient_reported')
    source_notes = Column(Text, nullable=True)  # Additional details about source

    # Clinical context
    clinical_notes = Column(Text, nullable=True)  # Additional clinical information
    alternatives = Column(JSONB, nullable=True)  # Safe alternatives (list of medications/substances)

    # Attribution
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Physician verification
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # System fields
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)

    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id], backref="allergies")
    recorder = relationship("User", foreign_keys=[recorded_by])
    verifier = relationship("User", foreign_keys=[verified_by])
