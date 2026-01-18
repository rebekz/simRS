"""HL7 v2.x Integration Models for STORY-024-01

This module provides database models for:
- HL7 message storage and tracking
- HL7 acknowledgments (ACK/NAK)
- HL7 error tracking and diagnostics
- HL7 routing rules configuration

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum as SQLEnum, JSON, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class HL7MessageType:
    """HL7 message type constants"""
    ADT_A04 = "ADT^A04"  # Patient Register
    ADT_A08 = "ADT^A08"  # Patient Update
    ORM_O01 = "ORM^O01"  # Order Entry
    ORU_R01 = "ORU^R01"  # Observation Results
    DFT_P03 = "DFT^P03"  # Billing/Charge


class HL7MessageStatus:
    """HL7 message processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"
    QUARANTINED = "quarantined"


class HL7Message(Base):
    """HL7 message model for storing received/sent HL7 v2.x messages"""
    __tablename__ = "hl7_messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(100), unique=True, nullable=False, index=True, comment="Unique message identifier")
    message_type = Column(String(50), nullable=False, index=True, comment="HL7 message type (e.g., ADT^A04)")
    trigger_event = Column(String(50), nullable=False, index=True, comment="Trigger event")
    version = Column(String(20), nullable=False, default="2.5", comment="HL7 version (2.5, 2.5.1, 2.6)")

    # Message content
    raw_message = Column(Text, nullable=False, comment="Raw HL7 message text")
    parsed_message = Column(JSON, nullable=True, comment="Parsed message as JSON")

    # Message metadata
    sending_facility = Column(String(100), nullable=True, index=True, comment="Sending facility")
    sending_application = Column(String(100), nullable=True, index=True, comment="Sending application")
    receiving_facility = Column(String(100), nullable=True, comment="Receiving facility")
    receiving_application = Column(String(100), nullable=True, comment="Receiving application")
    message_datetime = Column(DateTime(timezone=True), nullable=True, comment="Message date/time from MSH segment")
    message_control_id = Column(String(100), nullable=True, index=True, comment="Message control ID")

    # Processing status
    status = Column(String(50), nullable=False, index=True, default=HL7MessageStatus.PENDING, comment="Processing status")
    processed_at = Column(DateTime(timezone=True), nullable=True, comment="Processing completion time")
    error_message = Column(Text, nullable=True, comment="Error message if processing failed")

    # Routing
    source_system = Column(String(100), nullable=True, comment="Source system identifier")
    target_system = Column(String(100), nullable=True, comment="Target system identifier")
    routing_rule_id = Column(Integer, ForeignKey("hl7_routing_rules.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    acknowledgment = relationship("HL7Acknowledgment", back_populates="message", uselist=False)
    routing_rule = relationship("HL7RoutingRule", back_populates="messages")
    errors = relationship("HL7Error", back_populates="message", cascade="all, delete-orphan")

    __table_args__ = (
        {"comment": "HL7 v2.x messages for healthcare system integration"},
    )


class HL7Acknowledgment(Base):
    """HL7 acknowledgment model for ACK/NAK responses"""
    __tablename__ = "hl7_acknowledgments"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("hl7_messages.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Acknowledgment content
    ack_type = Column(String(10), nullable=False, comment="ACK or NAK")
    ack_code = Column(String(10), nullable=False, comment="Acknowledgment code (AA, AE, AR, etc.)")
    raw_acknowledgment = Column(Text, nullable=False, comment="Raw HL7 acknowledgment message")
    parsed_acknowledgment = Column(JSON, nullable=True, comment="Parsed acknowledgment as JSON")

    # Error details (for NAK)
    error_code = Column(String(10), nullable=True, comment="HL7 error code")
    error_severity = Column(String(20), nullable=True, comment="Error severity")
    error_message = Column(Text, nullable=True, comment="Error description")

    # Acknowledgment metadata
    acknowledged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processing_time_ms = Column(Integer, nullable=True, comment="Processing time in milliseconds")

    # Relationships
    message = relationship("HL7Message", back_populates="acknowledgment")

    __table_args__ = (
        {"comment": "HL7 message acknowledgments"},
    )


class HL7Error(Base):
    """HL7 error model for tracking processing errors"""
    __tablename__ = "hl7_errors"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("hl7_messages.id", ondelete="CASCADE"), nullable=False, index=True)

    # Error details
    error_type = Column(String(50), nullable=False, index=True, comment="Error type (parsing, validation, routing, processing)")
    error_code = Column(String(50), nullable=True, comment="Error code")
    error_message = Column(Text, nullable=False, comment="Error description")
    error_segment = Column(String(10), nullable=True, comment="Segment where error occurred")
    error_field = Column(Integer, nullable=True, comment="Field number where error occurred")
    error_component = Column(Integer, nullable=True, comment="Component number where error occurred")

    # Stack trace for debugging
    stack_trace = Column(Text, nullable=True, comment="Stack trace for debugging")

    # Recovery
    is_retried = Column(Boolean, default=False, nullable=False, comment="Whether message has been retried")
    retry_count = Column(Integer, default=0, nullable=False, comment="Number of retry attempts")
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment="Error resolution time")
    resolution_notes = Column(Text, nullable=True, comment="Notes on error resolution")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    message = relationship("HL7Message", back_populates="errors")

    __table_args__ = (
        {"comment": "HL7 message processing errors"},
    )


class HL7RoutingRule(Base):
    """HL7 routing rule model for message routing configuration"""
    __tablename__ = "hl7_routing_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="Rule name")
    description = Column(Text, nullable=True, comment="Rule description")
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether rule is active")
    priority = Column(Integer, nullable=False, default=0, comment="Rule priority (higher = higher priority)")

    # Routing criteria
    message_type_filter = Column(String(50), nullable=True, comment="Filter by message type (e.g., ADT^A04)")
    sending_facility_filter = Column(String(100), nullable=True, comment="Filter by sending facility")
    sending_application_filter = Column(String(100), nullable=True, comment="Filter by sending application")
    receiving_facility_filter = Column(String(100), nullable=True, comment="Filter by receiving facility")
    receiving_application_filter = Column(String(100), nullable=True, comment="Filter by receiving application")
    custom_filter_expression = Column(Text, nullable=True, comment="Custom filter expression")

    # Routing action
    action = Column(String(50), nullable=False, comment="Routing action (forward, transform, broadcast, filter)")
    target_system = Column(String(100), nullable=True, comment="Target system identifier")
    target_endpoint = Column(String(500), nullable=True, comment="Target endpoint URL")
    transformation_rule = Column(JSON, nullable=True, comment="Message transformation rules")

    # Processing options
    requires_acknowledgment = Column(Boolean, default=True, nullable=False, comment="Whether to wait for ACK")
    timeout_seconds = Column(Integer, default=30, nullable=False, comment="Timeout for acknowledgment")
    retry_on_failure = Column(Boolean, default=False, nullable=False, comment="Whether to retry on failure")
    max_retries = Column(Integer, default=3, nullable=False, comment="Maximum retry attempts")

    # Statistics
    total_messages_processed = Column(Integer, default=0, nullable=False, comment="Total messages processed")
    successful_messages = Column(Integer, default=0, nullable=False, comment="Successfully processed messages")
    failed_messages = Column(Integer, default=0, nullable=False, comment="Failed messages")
    last_processed_at = Column(DateTime(timezone=True), nullable=True, comment="Last processing time")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    messages = relationship("HL7Message", back_populates="routing_rule")

    __table_args__ = (
        {"comment": "HL7 message routing rules"},
    )


class HL7SequenceNumber(Base):
    """HL7 sequence number tracking for message integrity"""
    __tablename__ = "hl7_sequence_numbers"

    id = Column(Integer, primary_key=True, index=True)
    facility_key = Column(String(200), nullable=False, unique=True, index=True, comment="Facility+Application unique key")
    last_sequence_number = Column(Integer, nullable=False, default=0, comment="Last used sequence number")

    # Metadata
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "HL7 message sequence number tracking"},
    )
