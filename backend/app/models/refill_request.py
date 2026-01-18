"""Prescription Refill Request Model

Model for tracking patient prescription refill requests via patient portal.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
from enum import Enum


class RefillRequestStatus(str, Enum):
    """Status of refill request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    READY_FOR_PICKUP = "ready_for_pickup"
    COMPLETED = "completed"
    EXPIRED = "expired"


class PrescriptionRefillRequest(Base):
    """Prescription refill request model for patient portal

    Tracks refill requests submitted by patients through the patient portal.
    """
    __tablename__ = "prescription_refill_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(50), unique=True, nullable=False, index=True, comment="Unique request number (e.g., REFILL-2025-001234)")

    # References
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)

    # Request details
    status = Column(String(20), nullable=False, default="pending", index=True)
    items = Column(JSON, nullable=False, comment="List of refill items requested")
    notes = Column(Text, nullable=True, comment="Additional notes from patient")
    preferred_pickup_date = Column(Date, nullable=True, comment="Patient's preferred pickup date")

    # Processing
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Staff who reviewed the request")
    reviewed_at = Column(DateTime(timezone=True), nullable=True, comment="When request was reviewed")
    rejection_reason = Column(Text, nullable=True, comment="Reason if request was rejected")
    approval_notes = Column(Text, nullable=True, comment="Notes from approving staff")

    # Fulfillment
    approved_at = Column(DateTime(timezone=True), nullable=True, comment="When request was approved")
    ready_for_pickup_at = Column(DateTime(timezone=True), nullable=True, comment="When prescription ready for pickup")
    picked_up_at = Column(DateTime(timezone=True), nullable=True, comment="When patient picked up medication")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True, comment="Request expiration if not processed")

    # Relationships
    patient = relationship("Patient", backref="refill_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class PrescriptionRefillItem(Base):
    """Individual items in a refill request

    Tracks each medication requested in a refill request.
    """
    __tablename__ = "prescription_refill_items"

    id = Column(Integer, primary_key=True, index=True)
    refill_request_id = Column(Integer, ForeignKey("prescription_refill_requests.id"), nullable=False, index=True)

    # Original prescription reference
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, index=True)
    prescription_item_id = Column(Integer, ForeignKey("prescription_items.id"), nullable=False, index=True)

    # Medication details
    drug_id = Column(Integer, ForeignKey("drugs.id"), nullable=False)
    drug_name = Column(String(255), nullable=False)
    quantity_requested = Column(Integer, nullable=False, comment="Quantity requested by patient")
    quantity_approved = Column(Integer, nullable=True, comment="Quantity approved by prescriber")

    # Processing
    status = Column(String(50), nullable=False, default="pending", comment="Item-level status")
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    refill_request = relationship("PrescriptionRefillRequest")
    prescription = relationship("Prescription", foreign_keys=[prescription_id])
    prescription_item = relationship("PrescriptionItem", foreign_keys=[prescription_item_id])
    drug = relationship("Drug", foreign_keys=[drug_id])
