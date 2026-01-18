"""LIS (Laboratory Information System) Integration Models for STORY-024-03

This module provides database models for:
- LIS order tracking and status
- LIS results storage
- LIS configuration and mapping
- LIS error tracking and retry logic

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum as SQLEnum, JSON, Float, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class LISOrderStatus:
    """LIS order status constants"""
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    ERROR = "error"


class LISOrder(Base):
    """LIS order tracking model

    Tracks lab orders sent to external LIS systems with status updates
    and result linking.
    """
    __tablename__ = "lis_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), unique=True, nullable=False, index=True, comment="Internal order ID")
    lis_order_number = Column(String(100), nullable=True, index=True, comment="LIS system order number")
    placer_order_number = Column(String(100), nullable=True, index=True, comment="Placer order number (ORM^O01)")
    filler_order_number = Column(String(100), nullable=True, index=True, comment="Filler order number (LIS)")

    # Entity mapping
    lab_order_id = Column(Integer, ForeignKey("lab_orders.id"), nullable=False, index=True, comment="SIMRS lab order ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")

    # Order details
    priority = Column(String(20), nullable=False, default="routine", comment="Order priority (routine, urgent, STAT)")
    specimens = Column(JSON, nullable=True, comment="Specimen information")
    tests = Column(JSON, nullable=True, comment="Test codes and descriptions")

    # Status tracking
    status = Column(String(50), nullable=False, index=True, default=LISOrderStatus.PENDING, comment="Order status")
    status_history = Column(JSON, nullable=True, comment="Status change history")

    # Transmission tracking
    sent_at = Column(DateTime(timezone=True), nullable=True, comment="Order sent to LIS timestamp")
    acknowledged_at = Column(DateTime(timezone=True), nullable=True, comment="LIS acknowledgment timestamp")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="Order completion timestamp")

    # Result tracking
    results_received = Column(Integer, nullable=False, default=0, comment="Number of results received")
    results_expected = Column(Integer, nullable=False, default=0, comment="Expected number of results")
    critical_value = Column(Boolean, default=False, nullable=False, comment="Critical value flag")

    # Error handling
    error_message = Column(Text, nullable=True, comment="Error message if failed")
    retry_count = Column(Integer, nullable=False, default=0, comment="Number of retry attempts")
    last_retry_at = Column(DateTime(timezone=True), nullable=True, comment="Last retry timestamp")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    results = relationship("LISResult", back_populates="order", cascade="all, delete-orphan")

    __table_args__ = (
        {"extend_existing": True, "comment": "LIS order tracking for lab integration"},
    )


class LISResult(Base):
    """LIS result storage model

    Stores lab results received from LIS systems with full
    observation data and reference ranges.
    """
    __tablename__ = "lis_results"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(String(100), unique=True, nullable=False, index=True, comment="Result identifier")
    lis_order_id = Column(Integer, ForeignKey("lis_orders.id"), nullable=False, index=True, comment="LIS order ID")
    filler_order_number = Column(String(100), nullable=True, index=True, comment="Filler order number")

    # Entity mapping
    lab_order_id = Column(Integer, ForeignKey("lab_orders.id"), nullable=True, index=True, comment="SIMRS lab order ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")

    # Test information
    test_code = Column(String(50), nullable=False, index=True, comment="Test code")
    test_name = Column(String(255), nullable=False, comment="Test name")
    specimen = Column(String(100), nullable=True, comment="Specimen type")

    # Result data
    result_value = Column(String(1000), nullable=True, comment="Result value")
    result_value_numeric = Column(Float, nullable=True, comment="Numeric result value")
    unit = Column(String(50), nullable=True, comment="Unit of measure")

    # Reference range and flags
    reference_range_low = Column(Float, nullable=True, comment="Reference range low")
    reference_range_high = Column(Float, nullable=True, comment="Reference range high")
    reference_range_text = Column(String(255), nullable=True, comment="Reference range text")
    abnormal_flag = Column(String(10), nullable=True, comment="Abnormal flag (H, L, N, A)")
    critical_flag = Column(Boolean, default=False, nullable=False, comment="Critical value flag")

    # Result status
    result_status = Column(String(50), nullable=False, index=True, comment="Result status (final, preliminary, corrected)")
    performed_at = Column(DateTime(timezone=True), nullable=True, comment="Test performed timestamp")
    verified_at = Column(DateTime(timezone=True), nullable=True, comment="Result verified timestamp")
    verified_by = Column(String(100), nullable=True, comment="Verifying clinician")

    # Comments and notes
    comments = Column(Text, nullable=True, comment="Result comments")
    notes = Column(Text, nullable=True, comment="Additional notes")

    # Raw HL7 message
    raw_message = Column(Text, nullable=False, comment="Raw HL7 ORU^R01 message")

    # Processing
    is_imported = Column(Boolean, default=False, nullable=False, index=True, comment="Imported to SIMRS")
    imported_at = Column(DateTime(timezone=True), nullable=True, comment="Import timestamp")
    import_error = Column(Text, nullable=True, comment="Import error message")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    order = relationship("LISOrder", back_populates="results")

    __table_args__ = (
        {"extend_existing": True, "comment": "LIS lab results storage"},
    )


class LISSampleStatus:
    """LIS sample status constants"""
    COLLECTED = "collected"
    RECEIVED = "received"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class LISSample(Base):
    """LIS sample tracking model

    Tracks sample status through the LIS workflow from
    collection to completion.
    """
    __tablename__ = "lis_samples"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String(100), unique=True, nullable=False, index=True, comment="Sample identifier")
    barcode = Column(String(100), nullable=False, unique=True, index=True, comment="Sample barcode")
    lis_order_id = Column(Integer, ForeignKey("lis_orders.id"), nullable=False, index=True, comment="LIS order ID")

    # Sample details
    specimen_type = Column(String(100), nullable=False, comment="Specimen type (blood, urine, etc.)")
    collection_date = Column(DateTime(timezone=True), nullable=True, comment="Collection date/time")
    collector = Column(String(255), nullable=True, comment="Person who collected sample")

    # Status tracking
    status = Column(String(50), nullable=False, index=True, default=LISSampleStatus.COLLECTED, comment="Sample status")
    location = Column(String(100), nullable=True, comment="Current sample location")
    received_at = Column(DateTime(timezone=True), nullable=True, comment="Sample received at LIS")

    # Rejection handling
    rejection_reason = Column(Text, nullable=True, comment="Reason for sample rejection")
    rejected_at = Column(DateTime(timezone=True), nullable=True, comment="Rejection timestamp")
    rejected_by = Column(String(255), nullable=True, comment="Person who rejected sample")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "LIS sample tracking"},
    )


class LISMapping(Base):
    """LIS configuration and mapping model

    Stores mappings between SIMRS codes and LIS system codes
    for tests, locations, and clinicians.
    """
    __tablename__ = "lis_mappings"

    id = Column(Integer, primary_key=True, index=True)
    mapping_type = Column(String(50), nullable=False, index=True, comment="Mapping type (test, location, clinician)")
    simrs_code = Column(String(100), nullable=False, index=True, comment="SIMRS code")
    simrs_name = Column(String(255), nullable=False, comment="SIMRS name")
    lis_code = Column(String(100), nullable=False, comment="LIS system code")
    lis_name = Column(String(255), nullable=False, comment="LIS system name")

    # Additional mapping data
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether mapping is active")
    mapping_config = Column(JSON, nullable=True, comment="Additional mapping configuration")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "LIS system code mappings"},
    )


class LISConfiguration(Base):
    """LIS system configuration model

    Stores connection settings and preferences for LIS integration.
    """
    __tablename__ = "lis_configurations"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True, comment="Configuration key")

    # Connection settings
    host = Column(String(255), nullable=True, comment="LIS system host")
    port = Column(Integer, nullable=True, comment="LIS system port")
    facility = Column(String(100), nullable=True, comment="Sending facility")
    application = Column(String(100), nullable=True, comment="Sending application")

    # Message settings
    message_format = Column(String(20), nullable=False, default="HL7_2.5", comment="Message format version")
    encoding_chars = Column(String(10), nullable=False, default="^~\\&", comment="HL7 encoding characters")

    # Processing settings
    timeout_seconds = Column(Integer, nullable=False, default=30, comment="Connection timeout")
    retry_attempts = Column(Integer, nullable=False, default=3, comment="Retry attempts on failure")
    retry_delay_seconds = Column(Integer, nullable=False, default=60, comment="Delay between retries")
    enable_auto_retry = Column(Boolean, default=False, nullable=False, comment="Enable automatic retry")

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether configuration is active")
    test_mode = Column(Boolean, default=False, nullable=False, comment="Test mode (don't send real messages)")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "LIS system configuration"},
    )
