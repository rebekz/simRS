"""Problem List model for STORY-012: ICD-10 Problem List

This module defines the database model for patient problem/diagnosis tracking.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


# Problem status enum
problem_status_enum = ENUM(
    'active',
    'resolved',
    'chronic',
    'acute',
    name='problem_status',
    create_type=True,
)


class ProblemList(Base):
    """Patient problem/diagnosis list for clinical tracking."""
    __tablename__ = "problem_list"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True, index=True)

    # ICD-10 code reference
    icd10_code_id = Column(Integer, ForeignKey("icd10_codes.id"), nullable=False, index=True)
    icd10_code = Column(String(10), nullable=False, index=True)  # Denormalized for quick lookup

    # Problem details
    problem_name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)  # Additional clinical notes

    # Status tracking
    status = Column(problem_status_enum, nullable=False, index=True, default='active')
    onset_date = Column(Date, nullable=True)
    resolved_date = Column(Date, nullable=True)
    is_chronic = Column(Boolean, server_default="false", nullable=False, index=True)
    severity = Column(String(20), nullable=True)  # mild, moderate, severe

    # Attribution
    diagnosed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    facility = Column(String(100), nullable=True)

    # Clinical context
    clinical_notes = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)
    follow_up_required = Column(Boolean, server_default="false", nullable=False)
    follow_up_date = Column(Date, nullable=True)

    # Additional metadata
    certainty = Column(String(20), nullable=True)  # confirmed, probable, possible
    chronicity_indicators = Column(JSONB, nullable=True)  # Evidence of chronicity

    # System fields
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)

    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id])
    encounter = relationship("Encounter", foreign_keys=[encounter_id])
    diagnoser = relationship("User", foreign_keys=[diagnosed_by])
    recorder = relationship("User", foreign_keys=[recorded_by])
    icd10_reference = relationship("ICD10Code", foreign_keys=[icd10_code_id])
