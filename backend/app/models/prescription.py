"""Electronic Prescription Models for STORY-017

This module provides database models for:
- Prescription management
- Prescription items (simple and compound/racikan)
- Prescription tracking and dispensing status
- Barcode generation
- Pharmacy transmission tracking
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Boolean, Enum as SQLEnum, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.schemas.prescription import PrescriptionStatus, PrescriptionItemType, DispenseStatus


# =============================================================================
# Prescription Models
# =============================================================================

class Prescription(Base):
    """Electronic prescription model"""
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)

    # Identifiers
    prescription_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "RX-2025-001234"
    barcode = Column(String(100), unique=True, nullable=True)  # Barcode for prescription

    # References
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False, index=True)
    prescriber_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Prescription details
    status = Column(SQLEnum(PrescriptionStatus), default=PrescriptionStatus.DRAFT, nullable=False, index=True)
    priority = Column(String(20), nullable=False, default="routine")  # "routine", "urgent", "stat"
    diagnosis = Column(Text, nullable=True)  # Primary diagnosis (ICD-10)
    notes = Column(Text, nullable=True)

    # Dispensing tracking
    submitted_to_pharmacy = Column(Boolean, default=False, nullable=False)
    submitted_date = Column(DateTime(timezone=True), nullable=True)
    is_fully_dispensed = Column(Boolean, default=False, nullable=False)
    dispensed_date = Column(DateTime(timezone=True), nullable=True)

    # Verification
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_date = Column(DateTime(timezone=True), nullable=True)

    # Cost estimates
    estimated_cost = Column(Float, nullable=True)
    bpjs_coverage_estimate = Column(Float, nullable=True)
    patient_cost_estimate = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", backref="prescriptions")
    encounter = relationship("Encounter", backref="prescriptions")
    prescriber = relationship("User", foreign_keys=[prescriber_id], backref="prescribed_prescriptions")
    verifier = relationship("User", foreign_keys=[verified_by_id], backref="verified_prescriptions")
    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")
    transmissions = relationship("PrescriptionTransmission", back_populates="prescription", cascade="all, delete-orphan")


class PrescriptionItem(Base):
    """Individual items in a prescription"""
    __tablename__ = "prescription_items"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, index=True)

    # Item type
    item_type = Column(SQLEnum(PrescriptionItemType), nullable=False, default=PrescriptionItemType.SIMPLE)

    # Drug information
    drug_id = Column(Integer, ForeignKey("drugs.id"), nullable=False)
    drug_name = Column(String(255), nullable=False)  # Denormalized
    generic_name = Column(String(255), nullable=False)  # Denormalized

    # Dosage information
    dosage = Column(String(100), nullable=False)  # e.g., "500", "10"
    dose_unit = Column(String(50), nullable=False)  # e.g., "mg", "ml", "tablet"
    frequency = Column(String(100), nullable=False)  # e.g., "3x sehari", "SORE"
    route = Column(String(50), nullable=False)  # oral, intravenous, etc.

    # Duration and quantity
    duration_days = Column(Integer, nullable=True)  # Duration in days
    quantity = Column(Integer, nullable=True)  # Total quantity to dispense
    quantity_dispensed = Column(Integer, default=0, nullable=False)

    # Compound prescription (racikan) details
    compound_name = Column(String(255), nullable=True)  # Name for compound (e.g., "Racikan Obat Batuk")
    compound_components = Column(JSON, nullable=True)  # List of component drugs

    # Additional information
    indication = Column(Text, nullable=True)  # Reason for use
    special_instructions = Column(Text, nullable=True)
    is_prn = Column(Boolean, default=False, nullable=False)  # Pro re nata (as needed)

    # Dispensing status
    dispense_status = Column(SQLEnum(DispenseStatus), default=DispenseStatus.PENDING, nullable=False)
    dispensed_date = Column(DateTime(timezone=True), nullable=True)
    dispenser_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Refills
    refills_allowed = Column(Integer, nullable=True)  # Number of refills allowed
    refills_used = Column(Integer, default=0, nullable=False)  # Number of refills used

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    prescription = relationship("Prescription", back_populates="items")
    drug = relationship("Drug", backref="prescription_items")
    dispenser = relationship("User", foreign_keys=[dispenser_id], backref="dispensed_items")


# =============================================================================
# Prescription Pharmacy Transmission Models
# =============================================================================

class PrescriptionTransmission(Base):
    """Tracking prescription transmission to pharmacy"""
    __tablename__ = "prescription_transmissions"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, index=True)

    # Transmission details
    transmission_id = Column(String(100), unique=True, nullable=False, index=True)  # Unique transmission ID
    target_pharmacy_id = Column(Integer, nullable=True)  # None for hospital pharmacy
    target_pharmacy_name = Column(String(255), nullable=True)

    # Status tracking
    status = Column(String(20), nullable=False, default="queued")  # "queued", "sent", "acknowledged", "failed"
    sent_at = Column(DateTime(timezone=True), nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

    # Estimated ready time
    estimated_ready_time = Column(DateTime(timezone=True), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)  # If transmission failed

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    prescription = relationship("Prescription", back_populates="transmissions")


# =============================================================================
# Prescription Verification Log Models
# =============================================================================

class PrescriptionVerificationLog(Base):
    """Log of prescription verification actions"""
    __tablename__ = "prescription_verification_logs"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, index=True)

    # Verification details
    action = Column(String(50), nullable=False)  # "verified", "flagged", "approved", "rejected"
    verifier_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    verifier_name = Column(String(255), nullable=False)
    verifier_role = Column(String(50), nullable=False)  # "pharmacist", "doctor", "supervisor"

    # Findings
    issues_found = Column(JSON, nullable=True)  # List of issues found during verification
    requires_intervention = Column(Boolean, default=False, nullable=False)
    intervention_notes = Column(Text, nullable=True)

    # Overrides
    interactions_overridden = Column(Boolean, default=False, nullable=False)
    override_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    prescription = relationship("Prescription", backref="verification_logs")
    verifier = relationship("User", foreign_keys=[verifier_id], backref="prescription_verifications")


# =============================================================================
# Prescription Print Log Models
# =============================================================================

class PrescriptionPrintLog(Base):
    """Log of prescription print events"""
    __tablename__ = "prescription_print_logs"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, index=True)

    # Print details
    printed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    printed_by_name = Column(String(255), nullable=False)
    print_count = Column(Integer, nullable=False, default=1)

    # Print options
    included_barcode = Column(Boolean, default=True, nullable=False)
    included_diagnosis = Column(Boolean, default=True, nullable=False)
    included_instructions = Column(Boolean, default=True, nullable=False)

    # Generated document
    document_url = Column(String(500), nullable=True)  # URL to PDF
    document_expires_at = Column(DateTime(timezone=True), nullable=True)  # Security: link expiry

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    prescription = relationship("Prescription", backref="print_logs")
    printer = relationship("User", foreign_keys=[printed_by_id], backref="prescription_prints")
