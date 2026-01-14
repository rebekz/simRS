"""BPJS Eligibility History model for STORY-008: BPJS Eligibility Verification

This module defines the database model for tracking BPJS eligibility verification history.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.session import Base


class BPJSEligibilityCheck(Base):
    """BPJS eligibility check history model."""
    __tablename__ = "bpjs_eligibility_checks"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)

    # Search criteria
    search_type = Column(String(10), nullable=False, index=True)  # 'card' or 'nik'
    search_value = Column(String(20), nullable=False, index=True)  # card number or NIK

    # BPJS API response
    is_eligible = Column(Boolean, nullable=False, index=True)
    response_code = Column(String(10), nullable=True)
    response_message = Column(String(500), nullable=True)

    # Participant information (cached from BPJS response)
    participant_info = Column(JSONB, nullable=True)

    # Verification metadata
    verified_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verification_method = Column(String(20), nullable=False)  # 'api', 'manual', 'override'

    # Manual override (if API was down or manual verification needed)
    is_manual_override = Column(Boolean, server_default="false", nullable=False)
    override_reason = Column(Text, nullable=True)
    override_approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    override_approved_at = Column(DateTime(timezone=True), nullable=True)

    # Cache metadata
    is_cached = Column(Boolean, server_default="false", nullable=False)
    cache_hit = Column(Boolean, server_default="false", nullable=False)

    # Error handling
    api_error = Column(Text, nullable=True)
    api_error_code = Column(String(50), nullable=True)
    retry_count = Column(Integer, server_default=0, nullable=False)
    last_retry_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)

    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id])
    verifier = relationship("User", foreign_keys=[verified_by])
    approver = relationship("User", foreign_keys=[override_approved_by])
