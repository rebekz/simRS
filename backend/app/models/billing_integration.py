"""Billing System Integration Models for STORY-024-07

This module provides database models for:
- External billing system connections
- Claims submission and tracking
- Payment reconciliation
- Insurance company integration

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON, Float, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class ClaimStatus:
    """Claim status constants"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    PROCESSING = "processing"
    APPROVED = "approved"
    PARTIALLY_APPROVED = "partially_approved"
    REJECTED = "rejected"
    DENIED = "denied"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    CANCELLED = "cancelled"


class PaymentStatus:
    """Payment status constants"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"
class BillingSystem(Base):
    """External billing system registration model

    Stores connection details for external billing systems
    and insurance company portals.
    """
    __tablename__ = "billing_systems"

    id = Column(Integer, primary_key=True, index=True)
    system_id = Column(String(100), unique=True, nullable=False, index=True, comment="Internal system ID")
    system_code = Column(String(100), unique=True, nullable=False, index=True, comment="System code")

    # System identification
    system_name = Column(String(255), nullable=False, comment="Billing system name")
    system_type = Column(String(50), nullable=False, index=True, comment="System type (clearinghouse, insurance, payer)")
    organization = Column(String(255), nullable=True, comment="Organization name")
    payer_id = Column(String(100), nullable=True, index=True, comment="Payer ID")

    # Contact information
    contact_name = Column(String(255), nullable=True, comment="Contact name")
    contact_email = Column(String(255), nullable=True, comment="Contact email")
    contact_phone = Column(String(50), nullable=True, comment="Contact phone")

    # Connection settings
    protocol = Column(String(50), nullable=False, comment="Communication protocol")
    endpoint_url = Column(String(500), nullable=True, comment="Endpoint URL")
    auth_type = Column(String(50), nullable=True, comment="Authentication type")
    auth_credentials = Column(JSON, nullable=True, comment="Encrypted credentials")

    # Configuration
    edi_config = Column(JSON, nullable=True, comment="EDI configuration")
    mapping_config = Column(JSON, nullable=True, comment="Data mapping configuration")
    supported_formats = Column(JSON, nullable=True, comment="Supported claim formats")

    # BPJS-specific
    is_bpjs = Column(Boolean, default=False, nullable=False, index=True, comment="Is BPJS system")
    bpjs_sep_type = Column(String(50), nullable=True, comment="BPJS SEP type")

    # Status
    status = Column(String(50), nullable=False, index=True, default="active", comment="Connection status")
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether system is active")

    # Error handling
    error_message = Column(Text, nullable=True, comment="Current error message")
    last_error_at = Column(DateTime(timezone=True), nullable=True, comment="Last error timestamp")

    # Testing
    test_mode = Column(Boolean, default=False, nullable=False, comment="Test mode flag")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    claims = relationship("ClaimSubmission", back_populates="billing_system", cascade="all, delete-orphan")

    __table_args__ = (
        {"extend_existing": True, "comment": "External billing system connections"},
    )


class ClaimSubmission(Base):
    """Claim submission tracking model

    Tracks claims submitted to external billing systems
    and insurance companies.
    """
    __tablename__ = "claim_submissions"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(String(100), unique=True, nullable=False, index=True, comment="Submission ID")
    claim_number = Column(String(100), unique=True, nullable=False, index=True, comment="Claim number")

    # Entity mapping
    billing_system_id = Column(Integer, ForeignKey("billing_systems.id"), nullable=False, index=True, comment="Billing system ID")
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True, comment="SIMRS invoice ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True, index=True, comment="Encounter ID")

    # Claim details
    claim_type = Column(String(50), nullable=False, index=True, comment="Claim type (institutional, professional, dental)")
    service_type = Column(String(50), nullable=True, comment="Service type code")
    claim_amount = Column(Float, nullable=False, comment="Total claim amount")
    patient_responsibility = Column(Float, nullable=True, comment="Patient responsibility amount")

    # Dates
    service_start_date = Column(DateTime(timezone=True), nullable=False, comment="Service start date")
    service_end_date = Column(DateTime(timezone=True), nullable=False, comment="Service end date")
    admission_date = Column(DateTime(timezone=True), nullable=True, comment="Admission date")
    discharge_date = Column(DateTime(timezone=True), nullable=True, comment="Discharge date")

    # Provider information
    billing_provider_npi = Column(String(50), nullable=True, comment="Billing provider NPI")
    rendering_provider_npi = Column(String(50), nullable=True, comment="Rendering provider NPI")
    facility_id = Column(String(50), nullable=True, comment="Facility ID")

    # Diagnosis
    principal_diagnosis = Column(String(50), nullable=True, comment="Principal diagnosis code")
    principal_diagnosis_desc = Column(String(255), nullable=True, comment="Principal diagnosis description")
    admitting_diagnosis = Column(String(50), nullable=True, comment="Admitting diagnosis code")
    other_diagnoses = Column(JSON, nullable=True, comment="Other diagnosis codes")

    # Procedures
    procedures = Column(JSON, nullable=True, comment="Procedure codes and charges")

    # Claim content
    claim_data = Column(JSON, nullable=False, comment="Complete claim data")
    edi_837_content = Column(Text, nullable=True, comment="EDI 837 file content")
    attachment_data = Column(JSON, nullable=True, comment="Attachment documents")

    # Status tracking
    status = Column(String(50), nullable=False, index=True, default=ClaimStatus.DRAFT, comment="Claim status")
    status_history = Column(JSON, nullable=True, comment="Status change history")

    # Submission tracking
    submitted_at = Column(DateTime(timezone=True), nullable=True, comment="Claim submitted timestamp")
    acknowledged_at = Column(DateTime(timezone=True), nullable=True, comment="Acknowledgment timestamp")
    processed_at = Column(DateTime(timezone=True), nullable=True, comment="Processing completed timestamp")

    # Payer response
    payer_claim_number = Column(String(100), nullable=True, index=True, comment="Payer claim number")
    payer_response_code = Column(String(50), nullable=True, comment="Payer response code")
    payer_response_message = Column(Text, nullable=True, comment="Payer response message")
    response_data = Column(JSON, nullable=True, comment="Complete payer response")

    # Adjudication
    adjudication_date = Column(DateTime(timezone=True), nullable=True, comment="Adjudication date")
    approved_amount = Column(Float, nullable=True, comment="Approved amount")
    denied_amount = Column(Float, nullable=True, comment="Denied amount")
    patient_responsibility_amount = Column(Float, nullable=True, comment="Patient responsibility after adjudication")
    insurance_payment_amount = Column(Float, nullable=True, comment="Insurance payment amount")
    deductible_amount = Column(Float, nullable=True, comment="Deductible amount")
    coinsurance_amount = Column(Float, nullable=True, comment="Coinsurance amount")

    # Explanation of Benefits (EOB)
    eob_data = Column(JSON, nullable=True, comment="EOB data")
    eob_document_id = Column(String(100), nullable=True, comment="EOB document ID")

    # Error handling
    error_code = Column(String(50), nullable=True, comment="Error code")
    error_message = Column(Text, nullable=True, comment="Error message")
    rejection_reasons = Column(JSON, nullable=True, comment="Rejection reasons")

    # Retry
    retry_count = Column(Integer, nullable=False, default=0, comment="Number of retry attempts")
    next_retry_at = Column(DateTime(timezone=True), nullable=True, comment="Next retry timestamp")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    billing_system = relationship("BillingSystem", back_populates="claims")
    payments = relationship("ClaimPayment", back_populates="claim", cascade="all, delete-orphan")

    __table_args__ = (
        {"extend_existing": True, "comment": "Claim submission tracking"},
    )


class ClaimPayment(Base):
    """Claim payment tracking model

    Tracks payments received for submitted claims.
    """
    __tablename__ = "claim_payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String(100), unique=True, nullable=False, index=True, comment="Payment ID")

    # Entity mapping
    claim_submission_id = Column(Integer, ForeignKey("claim_submissions.id"), nullable=False, index=True, comment="Claim submission ID")
    billing_system_id = Column(Integer, ForeignKey("billing_systems.id"), nullable=False, index=True, comment="Billing system ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")

    # Payment details
    payment_amount = Column(Float, nullable=False, comment="Payment amount")
    payment_date = Column(DateTime(timezone=True), nullable=False, comment="Payment date")
    payment_method = Column(String(50), nullable=True, comment="Payment method")
    payment_reference = Column(String(100), nullable=True, index=True, comment="Payment reference/check number")

    # Payer information
    payer_name = Column(String(255), nullable=True, comment="Payer name")
    payer_id = Column(String(100), nullable=True, comment="Payer ID")
    check_number = Column(String(100), nullable=True, comment="Check number")
    electronic_remittance_advice = Column(Text, nullable=True, comment="ERA/X835 content")

    # Allocation
    allocated_amount = Column(Float, nullable=True, comment="Amount allocated to invoice")
    write_off_amount = Column(Float, nullable=True, comment="Write-off amount")
    adjustment_reason = Column(String(255), nullable=True, comment="Adjustment reason")

    # Status
    status = Column(String(50), nullable=False, index=True, default=PaymentStatus.PENDING, comment="Payment status")
    reconciled_at = Column(DateTime(timezone=True), nullable=True, comment="Reconciliation timestamp")

    # Reconciliation
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True, index=True, comment="Applied to invoice")
    reconciliation_notes = Column(Text, nullable=True, comment="Reconciliation notes")

    # Metadata
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    claim = relationship("ClaimSubmission", back_populates="payments")

    __table_args__ = (
        {"extend_existing": True, "comment": "Claim payment tracking"},
    )


class ClaimAdjustment(Base):
    """Claim adjustment model

    Stores adjustments made to claims during adjudication.
    """
    __tablename__ = "claim_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    adjustment_id = Column(String(100), unique=True, nullable=False, index=True, comment="Adjustment ID")

    # Entity mapping
    claim_submission_id = Column(Integer, ForeignKey("claim_submissions.id"), nullable=False, index=True, comment="Claim submission ID")
    payment_id = Column(Integer, ForeignKey("claim_payments.id"), nullable=True, index=True, comment="Associated payment")

    # Adjustment details
    adjustment_category = Column(String(50), nullable=False, comment="Adjustment category (contractual, other)")
    adjustment_group_code = Column(String(10), nullable=False, comment="Group code (COA, COB, etc.)")
    adjustment_reason_code = Column(String(50), nullable=False, comment="Reason code")
    adjustment_amount = Column(Float, nullable=False, comment="Adjustment amount")
    adjustment_quantity = Column(Float, nullable=True, comment="Adjustment quantity")

    # Description
    adjustment_description = Column(String(255), nullable=False, comment="Adjustment description")
    original_line_amount = Column(Float, nullable=True, comment="Original line amount")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Claim adjustments"},
    )


class RemittanceAdvice(Base):
    """Remittance advice model

    Stores electronic remittance advice (ERA/X835) data.
    """
    __tablename__ = "remittance_advice"

    id = Column(Integer, primary_key=True, index=True)
    remittance_id = Column(String(100), unique=True, nullable=False, index=True, comment="Remittance ID")

    # Entity mapping
    billing_system_id = Column(Integer, ForeignKey("billing_systems.id"), nullable=False, index=True, comment="Billing system ID")

    # Remittance details
    remittance_date = Column(DateTime(timezone=True), nullable=False, comment="Remittance date")
    total_payment_amount = Column(Float, nullable=False, comment="Total payment amount")
    payment_count = Column(Integer, nullable=False, default=0, comment="Number of payments")

    # Payer information
    payer_name = Column(String(255), nullable=False, comment="Payer name")
    payer_id = Column(String(100), nullable=False, comment="Payer ID")
    trace_number = Column(String(100), nullable=True, index=True, comment="Trace number")

    # Content
    x835_content = Column(Text, nullable=False, comment="X835 EDI content")
    parsed_data = Column(JSON, nullable=False, comment="Parsed remittance data")

    # Processing
    processed_at = Column(DateTime(timezone=True), nullable=True, comment="Processing timestamp")
    processing_status = Column(String(50), nullable=False, index=True, default="pending", comment="Processing status")
    error_message = Column(Text, nullable=True, comment="Processing error")

    # File storage
    file_path = Column(String(500), nullable=True, comment="Stored file path")

    # Metadata
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Electronic remittance advice"},
    )


class ClaimAttachment(Base):
    """Claim attachment model

    Stores supporting documents attached to claims.
    """
    __tablename__ = "claim_attachments"

    id = Column(Integer, primary_key=True, index=True)
    attachment_id = Column(String(100), unique=True, nullable=False, index=True, comment="Attachment ID")

    # Entity mapping
    claim_submission_id = Column(Integer, ForeignKey("claim_submissions.id"), nullable=False, index=True, comment="Claim submission ID")

    # Attachment details
    attachment_type = Column(String(50), nullable=False, comment="Attachment type (medical_record, image, etc.)")
    attachment_category = Column(String(50), nullable=True, comment="Attachment category")
    file_name = Column(String(255), nullable=False, comment="File name")
    file_type = Column(String(100), nullable=False, comment="File type/MIME type")
    file_size = Column(Integer, nullable=True, comment="File size in bytes")

    # Storage
    file_path = Column(String(500), nullable=False, comment="File storage path")
    file_url = Column(String(500), nullable=True, comment="File access URL")

    # Submission
    submitted_to_payer = Column(Boolean, default=False, nullable=False, comment="Submitted to payer")
    payer_attachment_id = Column(String(100), nullable=True, index=True, comment="Payer attachment ID")

    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Claim attachments"},
    )
