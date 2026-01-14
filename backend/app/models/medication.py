"""Medication List Models for STORY-014

This module provides database models for:
- Patient medication tracking
- Drug interaction database
- Medication reconciliation
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Boolean, Enum as SQLEnum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.schemas.medication import MedicationStatus, InteractionSeverity, InteractionType


# =============================================================================
# Medication Models
# =============================================================================

class PatientMedication(Base):
    """Patient medication tracking model"""
    __tablename__ = "patient_medications"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True)

    # Drug information
    drug_id = Column(Integer, ForeignKey("drugs.id"), nullable=False, index=True)
    drug_name = Column(String(255), nullable=False)  # Denormalized for query performance
    generic_name = Column(String(255), nullable=False)

    # Prescription details
    dosage = Column(String(100), nullable=True)
    dose_unit = Column(String(50), nullable=True)
    frequency = Column(String(100), nullable=True)
    route = Column(String(50), nullable=True)
    indication = Column(Text, nullable=True)  # Reason for use

    # Prescriber information
    prescriber_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    prescription_date = Column(Date, nullable=True)

    # Status and dates
    status = Column(SQLEnum(MedicationStatus), default=MedicationStatus.ACTIVE, nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    # Additional details
    notes = Column(Text, nullable=True)
    discontinuation_reason = Column(Text, nullable=True)
    batch_number = Column(String(100), nullable=True)
    manufacturer = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", backref="medications")
    encounter = relationship("Encounter", backref="medications")
    drug = relationship("Drug", backref="patient_medications")
    prescriber = relationship("User", foreign_keys=[prescriber_id], backref="prescribed_medications")


# =============================================================================
# Drug Interaction Models
# =============================================================================

class DrugInteraction(Base):
    """Drug interaction database model"""
    __tablename__ = "drug_interactions"

    id = Column(Integer, primary_key=True, index=True)

    # Interaction details
    interaction_type = Column(SQLEnum(InteractionType), nullable=False, index=True)
    severity = Column(SQLEnum(InteractionSeverity), nullable=False, index=True)

    # Drug 1 (primary drug)
    drug_1_id = Column(Integer, ForeignKey("drugs.id"), nullable=False)
    drug_1_name = Column(String(255), nullable=False)  # Denormalized

    # Drug 2 (interacting drug) - null for disease/allergy interactions
    drug_2_id = Column(Integer, ForeignKey("drugs.id"), nullable=True)
    drug_2_name = Column(String(255), nullable=True)  # Denormalized

    # For drug-disease interactions
    disease_code = Column(String(20), nullable=True, index=True)  # ICD-10 code
    disease_name = Column(String(255), nullable=True)

    # For drug-allergy interactions
    allergy_id = Column(Integer, nullable=True)

    # Interaction details
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    references = Column(Text, nullable=True)  # JSON array of URLs/refs
    requires_override = Column(Boolean, default=True, nullable=False)

    # Evidence level
    evidence_level = Column(String(20), nullable=True)  # "A", "B", "C", "D", "X"

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    drug_1 = relationship("Drug", foreign_keys=[drug_1_id])
    drug_2 = relationship("Drug", foreign_keys=[drug_2_id])


class CustomInteractionRule(Base):
    """Custom interaction rules for hospital-specific policies"""
    __tablename__ = "custom_interaction_rules"

    id = Column(Integer, primary_key=True, index=True)

    # Rule details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    rule_type = Column(String(50), nullable=False)  # "contraindication", "caution", "restriction"

    # Drug combinations
    drug_ids = Column(Text, nullable=False)  # JSON array of drug IDs
    drug_names = Column(Text, nullable=True)  # JSON array of drug names for display

    # Conditions
    age_min = Column(Integer, nullable=True)
    age_max = Column(Integer, nullable=True)
    renal_dose_adjustment = Column(Boolean, default=False)
    hepatic_dose_adjustment = Column(Boolean, default=False)
    pregnancy_contraindication = Column(Boolean, default=False)
    breastfeeding_contraindication = Column(Boolean, default=False)

    # Rule details
    severity = Column(SQLEnum(InteractionSeverity), nullable=False)
    action_required = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])


# =============================================================================
# Medication Reconciliation Models
# =============================================================================

class MedicationReconciliation(Base):
    """Medication reconciliation record"""
    __tablename__ = "medication_reconciliations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False)

    # Reconciliation details
    reconciliation_date = Column(Date, nullable=False)
    source = Column(String(50), nullable=False)  # "patient_reported", "pharmacy_records", "referral"

    # Statistics
    total_medications = Column(Integer, nullable=False, default=0)
    discrepancies_found = Column(Integer, nullable=False, default=0)
    medications_continued = Column(Integer, nullable=False, default=0)
    medications_modified = Column(Integer, nullable=False, default=0)
    medications_stopped = Column(Integer, nullable=False, default=0)
    medications_added = Column(Integer, nullable=False, default=0)

    # Reconciler
    reconciled_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", backref="medication_reconciliations")
    encounter = relationship("Encounter", backref="medication_reconciliations")
    reconciler = relationship("User", foreign_keys=[reconciled_by], backref="reconciled_medications")


class MedicationReconciliationItem(Base):
    """Medication reconciliation line items"""
    __tablename__ = "medication_reconciliation_items"

    id = Column(Integer, primary_key=True, index=True)
    reconciliation_id = Column(Integer, ForeignKey("medication_reconciliations.id"), nullable=False)

    # Medication reference (can be new or existing)
    patient_medication_id = Column(Integer, ForeignKey("patient_medications.id"), nullable=True)
    drug_name = Column(String(255), nullable=False)

    # Reconciliation details
    current_status = Column(String(50), nullable=False)  # "taking", "not_taking", "changed_dose", "stopped"
    new_dosage = Column(String(100), nullable=True)
    new_frequency = Column(String(100), nullable=True)

    # Discrepancies (JSON array)
    discrepancies = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    reconciliation = relationship("MedicationReconciliation", backref="items")
    patient_medication = relationship("PatientMedication", backref="reconciliation_items")


# =============================================================================
# Medication Administration Models (for PRN/scheduled meds)
# =============================================================================

class MedicationAdministration(Base):
    """Medication administration record"""
    __tablename__ = "medication_administrations"

    id = Column(Integer, primary_key=True, index=True)
    patient_medication_id = Column(Integer, ForeignKey("patient_medications.id"), nullable=False)

    # Administration details
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    administered_time = Column(DateTime(timezone=True), nullable=True)
    administered_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Dose given
    dosage_given = Column(String(100), nullable=True)
    route = Column(String(50), nullable=True)

    # Status
    status = Column(String(20), nullable=False, default="scheduled")  # "scheduled", "administered", "missed", "refused", "held"
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    patient_medication = relationship("PatientMedication", backref="administrations")
    administrator = relationship("User", foreign_keys=[administered_by], backref="administered_medications")
