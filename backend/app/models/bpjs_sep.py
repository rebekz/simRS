"""BPJS SEP (Surat Eligibilitas Peserta) Tracking Model for STORY-019

This module defines the database model for tracking BPJS SEP creation,
updates, and history for proper claim management.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.session import Base


class SEPStatus:
    """SEP status constants"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    UPDATED = "updated"
    CANCELLED = "cancelled"
    ERROR = "error"


class BPJSSEP(Base):
    """BPJS SEP tracking model for managing SEP lifecycle"""
    __tablename__ = "bpjs_sep"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)

    # SEP information
    sep_number = Column(String(50), unique=True, nullable=True, index=True)
    sep_date = Column(Date, nullable=False, index=True)
    service_type = Column(String(10), nullable=False)  # RI (Rawat Inap) or RJ (Rawat Jalan)

    # Patient information (stored for reference)
    bpjs_card_number = Column(String(13), nullable=False)
    patient_name = Column(String(255), nullable=False)
    mrn = Column(String(50), nullable=True)  # Medical Record Number

    # Facility and service information
    ppk_code = Column(String(20), nullable=False)  # Healthcare facility code
    polyclinic_code = Column(String(20), nullable=True)  # Destination polyclinic (for RJ)
    treatment_class = Column(String(10), nullable=True)  # Kelas rawat

    # Medical information
    initial_diagnosis_code = Column(String(10), nullable=False)  # ICD-10 code
    initial_diagnosis_name = Column(String(255), nullable=False)
    doctor_code = Column(String(20), nullable=True)  # DPJP (Dokter Penanggung Jawab)
    doctor_name = Column(String(255), nullable=True)

    # Referral information
    referral_number = Column(String(50), nullable=True)
    referral_ppk_code = Column(String(20), nullable=True)

    # Service flags
    is_executive = Column(Boolean, server_default=False, nullable=False)
    cob_flag = Column(Boolean, server_default=False, nullable=False)  # COB (Coordination of Benefits)

    # Additional information
    notes = Column(Text, nullable=True)  # Catatan
    patient_phone = Column(String(20), nullable=True)  # No Telp

    # Status tracking
    status = Column(String(20), server_default=SEPStatus.DRAFT, nullable=False, index=True)

    # BPJS API response data (stored for reference)
    bpjs_response = Column(JSONB, nullable=True)

    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)

    # Soft delete
    is_deleted = Column(Boolean, server_default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deletion_reason = Column(Text, nullable=True)

    # Relationships
    encounter = relationship("Encounter", foreign_keys=[encounter_id])
    patient = relationship("Patient", foreign_keys=[patient_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    deleter = relationship("User", foreign_keys=[deleted_by])

    # History relationship
    history = relationship("BPJSSEPHistory", back_populates="sep", cascade="all, delete-orphan")


class BPJSSEPHistory(Base):
    """BPJS SEP change history for audit trail"""
    __tablename__ = "bpjs_sep_history"

    id = Column(Integer, primary_key=True, index=True)
    sep_id = Column(Integer, ForeignKey("bpjs_sep.id", ondelete="CASCADE"), nullable=False, index=True)

    # Change tracking
    action = Column(String(20), nullable=False)  # created, updated, cancelled, etc.
    previous_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=True)

    # SEP data snapshot (before and after)
    previous_data = Column(JSONB, nullable=True)
    new_data = Column(JSONB, nullable=True)

    # BPJS API interaction
    bpjs_request = Column(JSONB, nullable=True)  # Request sent to BPJS API
    bpjs_response = Column(JSONB, nullable=True)  # Response from BPJS API

    # Change metadata
    reason = Column(Text, nullable=True)  # Reason for change
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)

    # Relationships
    sep = relationship("BPJSSEP", back_populates="history")
    user = relationship("User", foreign_keys=[changed_by])
