"""Admission Workflow Models for STORY-021

This module provides SQLAlchemy models for:
- Patient admission workflow
- Bed selection and assignment
- Room transfer workflow
- BPJS SEP updates
- Admission documentation
- Estimated discharge tracking
- Discharge criteria tracking
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text, Boolean, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


# =============================================================================
# Admission Order Model
# =============================================================================

class AdmissionOrder(Base):
    """Admission order model - main record for patient admissions"""
    __tablename__ = "admission_orders"

    id = Column(Integer, primary_key=True, index=True)

    # Patient and Doctor
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Order Information
    order_number = Column(String(50), nullable=False, unique=True)
    admission_type = Column(
        SQLEnum("emergency", "urgent", "elective", "transfer", name="admissiontype"),
        nullable=False
    )
    priority = Column(String(20), nullable=False, default="routine")
    status = Column(
        SQLEnum("pending", "admitted", "transferred", "discharged", "cancelled", "deceased",
                name="admissionstatus"),
        nullable=False,
        default="pending"
    )

    # Clinical Information
    chief_complaint = Column(Text, nullable=False)
    diagnosis = Column(Text, nullable=True)
    admission_reason = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)

    # Room Preferences
    requested_room_class = Column(String(10), nullable=True)
    requested_ward_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    # Dates
    admission_date = Column(DateTime(timezone=True), nullable=True)
    expected_discharge_date = Column(Date, nullable=True)
    discharge_date = Column(DateTime(timezone=True), nullable=True)

    # BPJS
    bpjs_sep_number = Column(String(50), nullable=True, unique=True)

    # Bed Assignment
    assigned_bed_id = Column(Integer, ForeignKey("beds.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    patient = relationship("Patient", backref="admissions")
    doctor = relationship("User", foreign_keys=[doctor_id], backref="admission_orders")
    requested_ward = relationship("Department", foreign_keys=[requested_ward_id])
    assigned_bed = relationship("Bed", backref="admission")
    transfers = relationship("RoomTransfer", back_populates="admission", cascade="all, delete-orphan")
    documentation = relationship("AdmissionDocumentation", back_populates="admission", uselist=False, cascade="all, delete-orphan")
    discharge_assessments = relationship("DischargeReadinessAssessment", back_populates="admission", cascade="all, delete-orphan")


# =============================================================================
# Room Transfer Model
# =============================================================================

class RoomTransfer(Base):
    """Room transfer model tracking room/bed changes"""
    __tablename__ = "room_transfers"

    id = Column(Integer, primary_key=True, index=True)

    # Admission
    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    # Beds
    from_bed_id = Column(Integer, ForeignKey("beds.id"), nullable=False)
    to_bed_id = Column(Integer, ForeignKey("beds.id"), nullable=False)

    # Transfer Information
    reason = Column(Text, nullable=False)
    transfer_type = Column(String(20), nullable=False, default="routine")
    status = Column(
        SQLEnum("requested", "approved", "in_progress", "completed", "cancelled",
                name="roomtransferstatus"),
        nullable=False,
        default="requested"
    )

    # Request
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Approval
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Completion
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", back_populates="transfers")
    patient = relationship("Patient", backref="room_transfers")
    from_bed = relationship("Bed", foreign_keys=[from_bed_id])
    to_bed = relationship("Bed", foreign_keys=[to_bed_id])
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    completed_by = relationship("User", foreign_keys=[completed_by_id])


# =============================================================================
# Admission Documentation Model
# =============================================================================

class AdmissionDocumentation(Base):
    """Admission documentation model"""
    __tablename__ = "admission_documentation"

    id = Column(Integer, primary_key=True, index=True)
    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, unique=True)

    # Documentation
    admission_notes = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)  # JSON array as text
    current_medications = Column(Text, nullable=True)  # JSON array as text
    advance_directives = Column(Text, nullable=True)
    emergency_contact = Column(String(200), nullable=True)
    insurance_info = Column(Text, nullable=True)  # JSON as text

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", back_populates="documentation")


# =============================================================================
# Admission Document Model (Generated Documents)
# =============================================================================

class AdmissionDocument(Base):
    """Generated admission documents model"""
    __tablename__ = "admission_documents"

    id = Column(Integer, primary_key=True, index=True)
    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False)

    # Document Information
    document_type = Column(String(50), nullable=False)  # admission_order, consent_form, etc
    document_url = Column(String(500), nullable=False)
    document_title = Column(String(200), nullable=False)

    # Generation
    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="generated_documents")
    generated_by = relationship("User", backref="documents_generated")


# =============================================================================
# Discharge Readiness Assessment Model
# =============================================================================

class DischargeReadinessAssessment(Base):
    """Discharge readiness assessment model"""
    __tablename__ = "discharge_readiness_assessments"

    id = Column(Integer, primary_key=True, index=True)
    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False)

    # Assessment
    is_ready = Column(Boolean, nullable=False, default=False)
    readiness_score = Column(Float, nullable=False)  # 0-100 scale
    criteria_met = Column(Text, nullable=True)  # JSON array as text
    criteria_not_met = Column(Text, nullable=True)  # JSON array as text
    barriers_to_discharge = Column(Text, nullable=True)  # JSON array as text
    required_follow_up = Column(Text, nullable=True)  # JSON array as text

    # Assessor
    assessed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    admission = relationship("AdmissionOrder", back_populates="discharge_assessments")
    assessed_by = relationship("User", backref="discharge_assessments")


# =============================================================================
# Bed Change History Model
# =============================================================================

class BedChangeHistory(Base):
    """Bed change history model - tracks all bed changes"""
    __tablename__ = "bed_change_history"

    id = Column(Integer, primary_key=True, index=True)
    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    # Bed Information
    from_bed_id = Column(Integer, ForeignKey("beds.id"), nullable=True)
    to_bed_id = Column(Integer, ForeignKey("beds.id"), nullable=True)

    # Change Information
    change_type = Column(String(50), nullable=False)  # admission, transfer, discharge
    change_reason = Column(Text, nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="bed_changes")
    patient = relationship("Patient", backref="bed_changes")
    from_bed = relationship("Bed", foreign_keys=[from_bed_id])
    to_bed = relationship("Bed", foreign_keys=[to_bed_id])
    changed_by = relationship("User", backref="bed_changes_made")
