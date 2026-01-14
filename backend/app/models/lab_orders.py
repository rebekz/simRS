"""Lab Order Models for STORY-018: Lab/Radiology Ordering

This module provides database models for:
- Laboratory test ordering
- Lab order status tracking
- Specimen collection tracking
- LOINC code integration
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


# =============================================================================
# Lab Order Enums
# =============================================================================

class LabOrderStatus:
    """Lab order status constants"""
    ORDERED = "ordered"
    COLLECTED = "collected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LabPriority:
    """Lab priority constants"""
    ROUTINE = "routine"
    URGENT = "urgent"
    STAT = "stat"


# =============================================================================
# Lab Order Models
# =============================================================================

class LabOrder(Base):
    """Laboratory test order model"""
    __tablename__ = "lab_orders"

    id = Column(Integer, primary_key=True, index=True)

    # Identifiers
    order_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "LAB-2025-001234"
    barcode = Column(String(100), unique=True, nullable=True)  # Barcode for specimen tracking

    # References
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False, index=True)
    ordered_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Test details
    test_code = Column(String(50), nullable=False, index=True)  # Internal test code
    test_name = Column(String(255), nullable=False)  # Test name
    loinc_code = Column(String(50), nullable=True, index=True)  # LOINC code
    loinc_system = Column(String(100), nullable=True)  # LOINC system name

    # Priority and status
    priority = Column(String(20), nullable=False, default="routine")  # routine, urgent, stat
    status = Column(String(20), nullable=False, default="ordered", index=True)  # ordered, collected, processing, completed, cancelled

    # Clinical information
    clinical_indication = Column(Text, nullable=True)  # Reason for test
    specimen_type = Column(String(100), nullable=True)  # blood, urine, swab, etc.
    collection_instructions = Column(Text, nullable=True)  # Special instructions for collection
    fasting_required = Column(Boolean, default=False, nullable=False)
    fasting_hours = Column(Integer, nullable=True)

    # Collection tracking
    specimen_collected = Column(Boolean, default=False, nullable=False)
    collected_at = Column(DateTime(timezone=True), nullable=True)
    collected_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    specimen_id = Column(String(100), nullable=True)  # Specimen identifier

    # Processing tracking
    received_at = Column(DateTime(timezone=True), nullable=True)  # Received by lab
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Results
    results = Column(JSON, nullable=True)  # Test results
    results_interpretation = Column(Text, nullable=True)
    reference_range = Column(String(255), nullable=True)
    abnormal_flag = Column(Boolean, nullable=True)

    # Verification
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Additional information
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Integration
    satusehat_service_request_id = Column(String(100), nullable=True, index=True, comment="SATUSEHAT FHIR ServiceRequest resource ID")
    satusehat_observation_id = Column(String(100), nullable=True, index=True, comment="SATUSEHAT FHIR Observation resource ID")

    # Cost estimates
    estimated_cost = Column(Integer, nullable=True)
    bpjs_coverage_estimate = Column(Integer, nullable=True)
    patient_cost_estimate = Column(Integer, nullable=True)

    # Timestamps
    ordered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", backref="lab_orders")
    encounter = relationship("Encounter", backref="lab_orders")
    ordering_provider = relationship("User", foreign_keys=[ordered_by], backref="ordered_lab_tests")
    collector = relationship("User", foreign_keys=[collected_by_id], backref="collected_specimens")
    verifier = relationship("User", foreign_keys=[verified_by_id], backref="verified_lab_results")
    reviewer = relationship("User", foreign_keys=[reviewed_by_id], backref="reviewed_lab_results")
