"""Encounter, Diagnosis, and Treatment models for STORY-011: Patient History View

This module defines the database models for patient encounters, diagnoses, and treatments.
All models include timestamps and proper relationships.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.session import Base


class EncounterType:
    """Encounter type constants"""
    OUTPATIENT = "outpatient"
    INPATIENT = "inpatient"
    EMERGENCY = "emergency"
    TELEPHONE = "telephone"
    HOME_VISIT = "home_visit"


class EncounterStatus:
    """Encounter status constants"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


class DiagnosisType:
    """Diagnosis type constants"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ADMISSION = "admission"
    DISCHARGE = "discharge"


class TreatmentType:
    """Treatment type constants"""
    MEDICATION = "medication"
    PROCEDURE = "procedure"
    THERAPY = "therapy"
    VACCINATION = "vaccination"
    OTHER = "other"


class Encounter(Base):
    """Patient encounter model for tracking visits"""
    __tablename__ = "encounters"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_type = Column(String(50), nullable=False)
    encounter_date = Column(Date, nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    department = Column(String(100), nullable=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    chief_complaint = Column(Text, nullable=True)
    present_illness = Column(Text, nullable=True)
    physical_examination = Column(Text, nullable=True)
    vital_signs = Column(JSONB, nullable=True)
    status = Column(String(20), server_default="active", nullable=False, index=True)
    is_urgent = Column(Boolean, server_default=False, nullable=False)
    bpjs_sep_number = Column(String(50), nullable=True)
    satusehat_encounter_id = Column(String(100), nullable=True, index=True, comment="SATUSEHAT FHIR Encounter resource ID")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="encounters")
    doctor = relationship("User", foreign_keys=[doctor_id])
    diagnoses = relationship("Diagnosis", back_populates="encounter", cascade="all, delete-orphan")
    treatments = relationship("Treatment", back_populates="encounter", cascade="all, delete-orphan")


class Diagnosis(Base):
    """Diagnosis model for patient diagnoses within encounters"""
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id", ondelete="CASCADE"), nullable=False, index=True)
    icd_10_code = Column(String(10), nullable=False, index=True)
    diagnosis_name = Column(String(500), nullable=False)
    diagnosis_type = Column(String(20), server_default="primary", nullable=False, index=True)
    is_chronic = Column(Boolean, server_default=False, nullable=False)
    satusehat_condition_id = Column(String(100), nullable=True, index=True, comment="SATUSEHAT FHIR Condition resource ID")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)

    # Relationships
    encounter = relationship("Encounter", back_populates="diagnoses")


class Treatment(Base):
    """Treatment model for patient treatments within encounters"""
    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id", ondelete="CASCADE"), nullable=False, index=True)
    treatment_type = Column(String(50), nullable=False, index=True)
    treatment_name = Column(String(500), nullable=False)
    dosage = Column(String(100), nullable=True)
    frequency = Column(String(100), nullable=True)
    duration = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, server_default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)

    # Relationships
    encounter = relationship("Encounter", back_populates="treatments")
