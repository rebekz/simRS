"""Prescription Dispensing Models for STORY-025

This module provides database models for:
- Dispensing queue management
- Prescription verification records
- Drug scanning records
- Patient counseling documentation
- Dispensing labels
- Dispensing completion tracking
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Boolean, Enum as SQLEnum, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.schemas.dispensing import DispensingStatus, DispensePriority, VerificationStatus, DispenseStatus


# =============================================================================
# Dispense Models
# =============================================================================

class Dispense(Base):
    """Individual prescription item dispense record

    Tracks each time a prescription item is dispensed to a patient.
    Used for refill eligibility checking and dispensing history.
    """
    __tablename__ = "dispenses"

    id = Column(Integer, primary_key=True, index=True)
    prescription_item_id = Column(Integer, ForeignKey("prescription_items.id"), nullable=False, index=True)

    # Dispense details
    quantity_dispensed = Column(Integer, nullable=False, default=0)
    status = Column(SQLEnum(DispenseStatus), nullable=False, default=DispenseStatus.PENDING, index=True)

    # Dispensing information
    dispensed_at = Column(DateTime(timezone=True), nullable=True)  # When given to patient
    dispensed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    prescription_item = relationship("PrescriptionItem", backref="dispenses")
    dispensed_by = relationship("User", foreign_keys=[dispensed_by_id], backref="dispenses_performed")


# =============================================================================
# Dispensing Queue Models
# =============================================================================

class DispensingQueue(Base):
    """Dispensing queue model - tracks prescriptions through dispensing workflow"""
    __tablename__ = "dispensing_queue"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, unique=True, index=True)

    # Queue management
    status = Column(SQLEnum(DispensingStatus), default=DispensingStatus.QUEUED, nullable=False, index=True)
    priority = Column(SQLEnum(DispensePriority), nullable=False, index=True)
    queue_position = Column(Integer, nullable=True)  # Current position in queue
    estimated_ready_time = Column(DateTime(timezone=True), nullable=True)
    estimated_wait_minutes = Column(Integer, nullable=True)

    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)  # When dispensing started
    verified_at = Column(DateTime(timezone=True), nullable=True)  # When pharmacist verified
    completed_at = Column(DateTime(timezone=True), nullable=True)  # When ready for pickup
    dispensed_at = Column(DateTime(timezone=True), nullable=True)  # When given to patient

    # Assignments
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Pharmacist assigned
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Pharmacist who verified

    # Progress tracking
    total_items = Column(Integer, nullable=False, default=0)
    items_scanned = Column(Integer, nullable=False, default=0)
    items_verified = Column(Integer, nullable=False, default=0)

    # Notes
    dispensing_notes = Column(Text, nullable=True)
    hold_reason = Column(Text, nullable=True)  # If on hold
    cancellation_reason = Column(Text, nullable=True)  # If cancelled

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    prescription = relationship("Prescription", backref="dispensing_queue")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], backref="assigned_dispensing")
    verified_by = relationship("User", foreign_keys=[verified_by_id], backref="verified_dispensing")
    scans = relationship("DispensingScan", back_populates="dispensing", cascade="all, delete-orphan")
    labels = relationship("DispensingLabel", back_populates="dispensing", cascade="all, delete-orphan")


# =============================================================================
# Drug Scanning Models
# =============================================================================

class DispensingScan(Base):
    """Individual drug scan record for verification"""
    __tablename__ = "dispensing_scans"

    id = Column(Integer, primary_key=True, index=True)
    dispensing_id = Column(Integer, ForeignKey("dispensing_queue.id"), nullable=False, index=True)
    prescription_item_id = Column(Integer, ForeignKey("prescription_items.id"), nullable=False)

    # Scanned drug details
    scanned_barcode = Column(String(100), nullable=False)
    scanned_drug_id = Column(Integer, ForeignKey("drugs.id"), nullable=False)
    scanned_drug_name = Column(String(255), nullable=False)
    scanned_drug_batch = Column(String(100), nullable=True)  # Batch number scanned

    # Expected drug details (for verification)
    expected_drug_id = Column(Integer, nullable=False)
    expected_drug_name = Column(String(255), nullable=False)
    expected_quantity = Column(Integer, nullable=False)

    # Scan results
    is_match = Column(Boolean, nullable=False, default=True)
    quantity_scanned = Column(Integer, nullable=False, default=0)
    scan_verified = Column(Boolean, nullable=False, default=False)

    # Scanner
    scanned_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Warnings and errors
    warnings = Column(JSON, nullable=True)  # List of warning messages
    errors = Column(JSON, nullable=True)  # List of error messages

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    dispensing = relationship("DispensingQueue", back_populates="scans")
    scanned_by = relationship("User", foreign_keys=[scanned_by_id], backref="drug_scans")
    prescription_item = relationship("PrescriptionItem", backref="scans")


# =============================================================================
# Patient Counseling Models
# =============================================================================

class PatientCounseling(Base):
    """Patient counseling documentation"""
    __tablename__ = "patient_counseling"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, unique=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    # Counselor
    counselor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    counselor_name = Column(String(255), nullable=False)

    # Counseling date
    counseling_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Topics covered
    discussed_purpose = Column(Boolean, nullable=False, default=False)
    discussed_dosage = Column(Boolean, nullable=False, default=False)
    discussed_timing = Column(Boolean, nullable=False, default=False)
    discussed_side_effects = Column(Boolean, nullable=False, default=False)
    discussed_interactions = Column(Boolean, nullable=False, default=False)
    discussed_storage = Column(Boolean, nullable=False, default=False)
    discussed_special_instructions = Column(Boolean, nullable=False, default=False)

    # Patient understanding
    patient_understood = Column(Boolean, nullable=False, default=True)
    patient_questions = Column(JSON, nullable=True)  # List of questions asked
    concerns_raised = Column(JSON, nullable=True)  # List of concerns raised

    # Additional notes
    counseling_notes = Column(Text, nullable=True)
    follow_up_required = Column(Boolean, nullable=False, default=False)
    follow_up_notes = Column(Text, nullable=True)

    # Verification
    patient_signature = Column(Boolean, nullable=False, default=False)
    caregiver_name = Column(String(255), nullable=True)  # If patient is minor/incapacitated
    caregiver_relationship = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    prescription = relationship("Prescription", backref="counseling")
    patient = relationship("Patient", backref="counseling_records")
    counselor = relationship("User", foreign_keys=[counselor_id], backref="counseling_provided")


# =============================================================================
# Dispensing Label Models
# =============================================================================

class DispensingLabel(Base):
    """Generated dispensing labels"""
    __tablename__ = "dispensing_labels"

    id = Column(Integer, primary_key=True, index=True)
    dispensing_id = Column(Integer, ForeignKey("dispensing_queue.id"), nullable=False, index=True)
    prescription_item_id = Column(Integer, ForeignKey("prescription_items.id"), nullable=False)

    # Label data
    label_data = Column(JSON, nullable=False)  # All label information
    label_text = Column(Text, nullable=False)  # Formatted label text
    barcode = Column(String(100), unique=True, nullable=False)  # Label barcode
    warning_emoji = Column(String(10), nullable=True)  # ⚠️ emoji for warnings

    # Label generation
    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    print_count = Column(Integer, nullable=False, default=0)

    # Label expiry (for compounded medications)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    dispensing = relationship("DispensingQueue", back_populates="labels")
    generated_by = relationship("User", foreign_keys=[generated_by_id], backref="labels_generated")
    prescription_item = relationship("PrescriptionItem", backref="labels")


# =============================================================================
# Prescription Verification Record Models
# =============================================================================

class PrescriptionVerificationRecord(Base):
    """Detailed verification record for dispensed prescriptions"""
    __tablename__ = "prescription_verification_records"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, unique=True, index=True)
    dispensing_id = Column(Integer, ForeignKey("dispensing_queue.id"), nullable=False, unique=True)

    # Verification details
    verification_status = Column(SQLEnum(VerificationStatus), nullable=False, default=VerificationStatus.PENDING)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    verified_by_role = Column(String(50), nullable=False)  # "pharmacist", "supervisor"
    verified_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Patient verification
    patient_verified = Column(Boolean, nullable=False, default=True)
    patient_verification_method = Column(String(50), nullable=True)  # "barcode", "name_dob", "id_card"

    # Issues and interventions
    issues_found = Column(JSON, nullable=True)  # List of issues
    requires_intervention = Column(Boolean, nullable=False, default=False)
    intervention_notes = Column(Text, nullable=True)

    # Overrides
    interactions_overridden = Column(Boolean, nullable=False, default=False)
    override_reason = Column(Text, nullable=True)
    override_approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Supervisor approval

    # Verification notes
    verification_notes = Column(Text, nullable=True)
    can_proceed = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    prescription = relationship("Prescription", backref="verification_record")
    dispensing = relationship("DispensingQueue", backref="verification_record")
    verified_by = relationship("User", foreign_keys=[verified_by_id], backref="verifications_performed")
    override_approved_by = relationship("User", foreign_keys=[override_approved_by_id], backref="overrides_approved")


# =============================================================================
# Stock Check Log Models
# =============================================================================

class StockCheckLog(Base):
    """Log of stock availability checks during dispensing"""
    __tablename__ = "stock_check_logs"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, index=True)
    drug_id = Column(Integer, ForeignKey("drugs.id"), nullable=False)

    # Stock check details
    required_quantity = Column(Integer, nullable=False)
    available_quantity = Column(Integer, nullable=False)
    stock_available = Column(Boolean, nullable=False, default=True)

    # Resolution
    alternative_used = Column(Boolean, nullable=False, default=False)
    alternative_drug_id = Column(Integer, nullable=True)
    alternative_drug_name = Column(String(255), nullable=True)

    # Backorder
    backordered = Column(Boolean, nullable=False, default=False)
    estimated_restock_date = Column(Date, nullable=True)

    # Checked by
    checked_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    prescription = relationship("Prescription", backref="stock_checks")
    drug = relationship("Drug", backref="stock_checks")
    checked_by = relationship("User", foreign_keys=[checked_by_id], backref="stock_checks_performed")
