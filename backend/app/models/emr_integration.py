"""EMR/EHR Integration Models for STORY-024-06

This module provides database models for:
- External EMR/EHR system connections
- Patient data exchange (CCD, CCR)
- Referral and consultation workflows
- Health Information Exchange (HIE) integration

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON, Enum as SQLEnum, Float, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class ExchangeProtocol:
    """Data exchange protocol constants"""
    HL7_V2 = "HL7_V2"
    HL7_FHIR = "HL7_FHIR"
    IHE = "IHE"
    CCD = "CCD"
    CCR = "CCR"
    SOAP = "SOAP"
    REST = "REST"
    DIRECT = "DIRECT"


class ExchangeStatus:
    """Exchange status constants"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class ExternalSystem(Base):
    """External EMR/EHR system registration model

    Stores connection details and configuration for external
    healthcare systems participating in data exchange.
    """
    __tablename__ = "external_systems"

    id = Column(Integer, primary_key=True, index=True)
    system_id = Column(String(100), unique=True, nullable=False, index=True, comment="Internal system ID")
    system_code = Column(String(100), unique=True, nullable=False, index=True, comment="External system code")

    # System identification
    system_name = Column(String(255), nullable=False, comment="External system name")
    system_type = Column(String(50), nullable=False, index=True, comment="System type (EHR, EMR, HIE, etc.)")
    organization = Column(String(255), nullable=True, comment="Organization name")
    facility_type = Column(String(50), nullable=True, comment="Facility type (hospital, clinic, lab)")

    # Location
    address = Column(String(500), nullable=True, comment="Physical address")
    city = Column(String(100), nullable=True, comment="City")
    province = Column(String(100), nullable=True, comment="Province/state")
    country = Column(String(100), nullable=True, comment="Country")
    postal_code = Column(String(20), nullable=True, comment="Postal code")

    # Connection settings
    protocol = Column(String(50), nullable=False, comment="Exchange protocol")
    endpoint_url = Column(String(500), nullable=True, comment="Endpoint URL")
    auth_type = Column(String(50), nullable=True, comment="Authentication type")
    auth_credentials = Column(JSON, nullable=True, comment="Encrypted credentials")

    # Configuration
    connection_config = Column(JSON, nullable=True, comment="Connection configuration")
    mapping_config = Column(JSON, nullable=True, comment="Data mapping configuration")
    supported_formats = Column(JSON, nullable=True, comment="Supported data formats")

    # Status
    status = Column(String(50), nullable=False, index=True, default="active", comment="Connection status")
    last_tested_at = Column(DateTime(timezone=True), nullable=True, comment="Last connection test")
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether connection is active")

    # Error handling
    error_message = Column(Text, nullable=True, comment="Current error message")
    failed_attempts = Column(Integer, nullable=False, default=0, comment="Number of failed attempts")
    last_error_at = Column(DateTime(timezone=True), nullable=True, comment="Last error timestamp")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    exchanges = relationship("DataExchange", back_populates="external_system", cascade="all, delete-orphan")

    __table_args__ = (
        {"extend_existing": True, "comment": "External EMR/EHR system connections"},
    )


class DataExchange(Base):
    """Data exchange tracking model

    Tracks data exchange events with external systems.
    """
    __tablename__ = "data_exchanges"

    id = Column(Integer, primary_key=True, index=True)
    exchange_id = Column(String(100), unique=True, nullable=False, index=True, comment="Exchange ID")

    # Entity mapping
    external_system_id = Column(Integer, ForeignKey("external_systems.id"), nullable=False, index=True, comment="External system ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True, index=True, comment="Encounter ID")

    # Exchange details
    exchange_type = Column(String(50), nullable=False, index=True, comment="Exchange type (query, submit, notify)")
    exchange_direction = Column(String(20), nullable=False, comment="Direction (outbound, inbound)")
    document_type = Column(String(50), nullable=True, comment="Document type (CCD, CCR, ORU, etc.)")

    # Content
    request_data = Column(JSON, nullable=True, comment="Request data")
    response_data = Column(JSON, nullable=True, comment="Response data")
    document_content = Column(Text, nullable=True, comment="Document content (CCD/CCR)")
    document_id = Column(String(100), nullable=True, index=True, comment="Document identifier")

    # Status tracking
    status = Column(String(50), nullable=False, index=True, default=ExchangeStatus.PENDING, comment="Exchange status")
    status_history = Column(JSON, nullable=True, comment="Status change history")

    # Transmission tracking
    initiated_at = Column(DateTime(timezone=True), nullable=False, comment="Exchange initiated timestamp")
    sent_at = Column(DateTime(timezone=True), nullable=True, comment="Data sent timestamp")
    acknowledged_at = Column(DateTime(timezone=True), nullable=True, comment="Acknowledgment timestamp")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="Completion timestamp")

    # Error handling
    error_code = Column(String(50), nullable=True, comment="Error code")
    error_message = Column(Text, nullable=True, comment="Error message")
    retry_count = Column(Integer, nullable=False, default=0, comment="Number of retries")
    next_retry_at = Column(DateTime(timezone=True), nullable=True, comment="Next retry timestamp")

    # Quality metrics
    record_count = Column(Integer, nullable=True, comment="Number of records exchanged")
    validation_errors = Column(JSON, nullable=True, comment="Validation errors")

    # Metadata
    initiated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    external_system = relationship("ExternalSystem", back_populates="exchanges")

    __table_args__ = (
        {"extend_existing": True, "comment": "Data exchange tracking"},
    )


class PatientDataQuery(Base):
    """Patient data query model

    Stores queries for patient data from external systems.
    """
    __tablename__ = "patient_data_queries"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(String(100), unique=True, nullable=False, index=True, comment="Query ID")

    # Entity mapping
    external_system_id = Column(Integer, ForeignKey("external_systems.id"), nullable=False, index=True, comment="External system ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Local patient ID")
    external_patient_id = Column(String(100), nullable=True, index=True, comment="External patient ID")

    # Query parameters
    query_criteria = Column(JSON, nullable=True, comment="Query criteria")
    requested_data_types = Column(JSON, nullable=True, comment="Requested data types")
    date_range = Column(JSON, nullable=True, comment="Date range for query")

    # Response
    response_status = Column(String(50), nullable=False, index=True, comment="Response status")
    response_data = Column(JSON, nullable=True, comment="Response data")
    document_links = Column(JSON, nullable=True, comment="Links to received documents")

    # Metrics
    records_received = Column(Integer, nullable=False, default=0, comment="Number of records received")
    data_quality_score = Column(Float, nullable=True, comment="Data quality score")

    # Timestamps
    submitted_at = Column(DateTime(timezone=True), nullable=False, comment="Query submitted timestamp")
    responded_at = Column(DateTime(timezone=True), nullable=True, comment="Response received timestamp")
    expires_at = Column(DateTime(timezone=True), nullable=True, comment="Response expiry")

    # Metadata
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Patient data queries"},
    )


class Referral(Base):
    """Referral tracking model

    Tracks patient referrals to external providers/facilities.
    """
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    referral_id = Column(String(100), unique=True, nullable=False, index=True, comment="Referral ID")

    # Entity mapping
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True, index=True, comment="Encounter ID")
    external_system_id = Column(Integer, ForeignKey("external_systems.id"), nullable=True, index=True, comment="Referred to system")

    # Referral details
    referral_type = Column(String(50), nullable=False, comment="Referral type (consultation, transfer, admission)")
    priority = Column(String(50), nullable=False, comment="Priority (routine, urgent, emergent)")
    reason = Column(Text, nullable=False, comment="Reason for referral")

    # Provider information
    referring_provider_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Referring provider")
    referred_to_provider = Column(String(255), nullable=True, comment="Referred to provider")
    referred_to_facility = Column(String(255), nullable=True, comment="Referred to facility")

    # Clinical information
    diagnosis = Column(String(500), nullable=True, comment="Primary diagnosis")
    clinical_summary = Column(Text, nullable=True, comment="Clinical summary")
    attachments = Column(JSON, nullable=True, comment="Attached documents")

    # Data exchange
    data_exchange_id = Column(String(100), nullable=True, comment="Associated data exchange ID")
    documents_sent = Column(JSON, nullable=True, comment="Documents sent with referral")

    # Status tracking
    status = Column(String(50), nullable=False, index=True, default="pending", comment="Referral status")
    acknowledged_at = Column(DateTime(timezone=True), nullable=True, comment="Referral acknowledged")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="Referral completed")
    response_notes = Column(Text, nullable=True, comment="Response from receiving facility")

    # Timestamps
    referral_date = Column(DateTime(timezone=True), nullable=False, comment="Referral date")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Patient referrals"},
    )


class ConsultationRequest(Base):
    """Consultation request model

    Stores consultation requests sent to external providers.
    """
    __tablename__ = "consultation_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(100), unique=True, nullable=False, index=True, comment="Request ID")

    # Entity mapping
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False, index=True, comment="Encounter ID")
    external_system_id = Column(Integer, ForeignKey("external_systems.id"), nullable=True, index=True, comment="Consulted system")

    # Request details
    consultation_type = Column(String(100), nullable=False, comment="Type of consultation")
    specialty = Column(String(100), nullable=False, comment="Requested specialty")
    priority = Column(String(50), nullable=False, comment="Priority")
    clinical_question = Column(Text, nullable=False, comment="Clinical question")

    # Patient information
    patient_summary = Column(Text, nullable=True, comment="Patient summary")
    relevant_findings = Column(Text, nullable=True, comment="Relevant clinical findings")

    # Attachments
    attachments = Column(JSON, nullable=True, comment="Attached documents/images")

    # Response
    consultation_notes = Column(Text, nullable=True, comment="Consultation response notes")
    recommendations = Column(Text, nullable=True, comment="Consultant recommendations")
    consultant_name = Column(String(255), nullable=True, comment="Consultant name")

    # Status tracking
    status = Column(String(50), nullable=False, index=True, default="pending", comment="Request status")
    requested_at = Column(DateTime(timezone=True), nullable=False, comment="Request timestamp")
    responded_at = Column(DateTime(timezone=True), nullable=True, comment="Response timestamp")

    # Metadata
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Consultation requests"},
    )


class CCDDocument(Base):
    """Continuity of Care Document (CCD) model

    Stores CCD documents received from/sent to external systems.
    """
    __tablename__ = "ccd_documents"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(100), unique=True, nullable=False, index=True, comment="Document ID")

    # Entity mapping
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")
    external_system_id = Column(Integer, ForeignKey("external_systems.id"), nullable=True, index=True, comment="Source/destination system")

    # Document metadata
    document_type = Column(String(50), nullable=False, comment="Document type (CCD, CCR)")
    document_format = Column(String(50), nullable=False, comment="Document format (XML, JSON)")
    document_date = Column(DateTime(timezone=True), nullable=False, comment="Document date")
    document_version = Column(String(50), nullable=True, comment="Document version")

    # Content
    document_content = Column(Text, nullable=False, comment="Document content")
    parsed_data = Column(JSON, nullable=True, comment="Parsed CCD data")

    # Document sections
    sections = Column(JSON, nullable=True, comment="Document sections")
    problems = Column(JSON, nullable=True, comment="Problems/conditions")
    medications = Column(JSON, nullable=True, comment="Medications")
    allergies = Column(JSON, nullable=True, comment="Allergies")
    immunizations = Column(JSON, nullable=True, comment="Immunizations")
    vital_signs = Column(JSON, nullable=True, comment="Vital signs")
    results = Column(JSON, nullable=True, comment="Lab/results")
    procedures = Column(JSON, nullable=True, comment="Procedures")

    # Exchange tracking
    exchange_id = Column(String(100), nullable=True, comment="Associated exchange ID")
    direction = Column(String(20), nullable=False, comment="Direction (sent, received)")

    # Validation
    is_valid = Column(Boolean, nullable=True, comment="CCD validation status")
    validation_errors = Column(JSON, nullable=True, comment="Validation errors")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "CCD document storage"},
    )
