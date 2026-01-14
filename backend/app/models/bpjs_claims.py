"""BPJS Claims Database Models for STORY-029: BPJS Claims Management

This module defines the database models for managing BPJS (Badan Penyelenggara
Jaminan Sosial) claims, including claim submission, verification, payment tracking,
and document management.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Numeric, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from app.db.session import Base


class BPJSClaimType(str, Enum):
    """BPJS claim type options"""
    INA_CBG = "ina_cbg"
    FEE_FOR_SERVICE = "fee_for_service"
    RATU_MINIMAL = "ratu_minimal"


class BPJSClaimStatus(str, Enum):
    """BPJS claim status options"""
    DRAFT = "draft"
    READY = "ready"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    VERIFIED = "verified"
    REVISION_REQUESTED = "revision_requested"
    PAID = "paid"
    CANCELLED = "cancelled"


class BPJSClaimItemType(str, Enum):
    """BPJS claim item type options"""
    MEDICAL = "medical"
    ADMINISTRATION = "administration"
    CAPITAL = "capital"


class BPJSDocumentType(str, Enum):
    """BPJS document type options"""
    SEP = "sep"
    RESUME = "resume"
    DPJP = "dpjp"
    INVOICE = "invoice"
    OTHER = "other"


class BPJSSubmissionStatus(str, Enum):
    """BPJS submission status options"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class BPJSQueryStatus(str, Enum):
    """BPJS verification query status options"""
    PENDING = "pending"
    RESPONDED = "responded"
    CLOSED = "closed"


class BPJSClaim(Base):
    """BPJS Claim model for managing BPJS insurance claims

    This model stores comprehensive claim data including claim details,
    submission information, verification responses, and payment tracking.
    """
    __tablename__ = "bpjs_claims"

    id = Column(Integer, primary_key=True, index=True)

    # Claim identification
    claim_number = Column(String(50), unique=True, index=True, nullable=False, comment="Unique claim number")
    encounter_id = Column(Integer, ForeignKey("encounters.id", ondelete="RESTRICT"), nullable=False, index=True, comment="Reference to encounter")
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True, index=True, comment="Reference to invoice")
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True, comment="Reference to patient")

    # Claim classification
    claim_type = Column(String(20), nullable=False, index=True, comment="Type of claim (ina_cbg, fee_for_service, ratu_minimal)")

    # Submission dates
    submission_date = Column(Date, nullable=True, index=True, comment="Planned submission date")
    deadline_date = Column(Date, nullable=True, index=True, comment="BPJS submission deadline")
    submitted_to_bpjs_at = Column(DateTime(timezone=True), nullable=True, comment="Actual submission timestamp")

    # Package and tariff information
    package_type = Column(String(50), nullable=True, comment="Package type description")
    drg_code = Column(String(20), nullable=True, index=True, comment="Diagnosis Related Group code")
    case_mix_group = Column(String(50), nullable=True, comment="Case mix group classification")
    tariff = Column(Numeric(12, 2), nullable=True, comment="BPJS tariff amount")

    # Financial amounts
    package_amount = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Package amount claimed")
    provider_amount = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Provider fee amount")
    patient_amount = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Patient responsibility amount")
    topup_amount = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Additional top-up amount")

    # Status and workflow
    status = Column(String(20), nullable=False, index=True, default="draft", comment="Claim status")

    # BPJS API responses
    submission_response = Column(JSON, nullable=True, comment="BPJS submission response data")
    verification_response = Column(JSON, nullable=True, comment="BPJS verification response data")
    rejection_reason = Column(Text, nullable=True, comment="Reason for rejection")

    # E-Claim file
    eclaim_file_path = Column(String(500), nullable=True, comment="Path to generated E-Claim file")
    submission_count = Column(Integer, nullable=False, default=0, comment="Number of submission attempts")

    # BPJS reference numbers
    bpjs_claim_id = Column(String(50), nullable=True, index=True, comment="BPJS claim ID")
    sep_number = Column(String(50), nullable=True, index=True, comment="SEP (Surat Eligibilitas Peserta) number")

    # Verification and approval
    verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="Verified by user ID")
    verified_at = Column(DateTime(timezone=True), nullable=True, comment="Verification timestamp")
    approved_amount = Column(Numeric(12, 2), nullable=True, comment="Final approved amount by BPJS")
    approved_at = Column(DateTime(timezone=True), nullable=True, comment="Approval timestamp")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    encounter = relationship("Encounter", backref="bpjs_claims")
    invoice = relationship("Invoice", backref="bpjs_claims")
    patient = relationship("Patient", backref="bpjs_claims")
    verifier = relationship("User", foreign_keys=[verified_by])
    items = relationship("BPJSClaimItem", back_populates="claim", cascade="all, delete-orphan")
    documents = relationship("BPJSClaimDocument", back_populates="claim", cascade="all, delete-orphan")
    submission_logs = relationship("BPJSSubmissionLog", back_populates="claim", cascade="all, delete-orphan")
    verification_queries = relationship("BPJSVerificationQuery", back_populates="claim", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_bpjs_claims_claim_number", "claim_number"),
        Index("ix_bpjs_claims_encounter_id", "encounter_id"),
        Index("ix_bpjs_claims_invoice_id", "invoice_id"),
        Index("ix_bpjs_claims_patient_id", "patient_id"),
        Index("ix_bpjs_claims_claim_type", "claim_type"),
        Index("ix_bpjs_claims_status", "status"),
        Index("ix_bpjs_claims_submission_date", "submission_date"),
        Index("ix_bpjs_claims_drg_code", "drg_code"),
        Index("ix_bpjs_claims_bpjs_claim_id", "bpjs_claim_id"),
        Index("ix_bpjs_claims_sep_number", "sep_number"),
    )


class BPJSClaimItem(Base):
    """BPJS Claim Item model for individual claim line items

    This model stores detailed line items for each BPJS claim including
    medical services, administrative fees, and capital goods.
    """
    __tablename__ = "bpjs_claim_items"

    id = Column(Integer, primary_key=True, index=True)
    bpjs_claim_id = Column(Integer, ForeignKey("bpjs_claims.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to BPJS claim")

    # Item classification
    item_type = Column(String(20), nullable=False, index=True, comment="Type of item (medical, administration, capital)")

    # Item details
    item_code = Column(String(50), nullable=True, index=True, comment="Item/service code")
    item_name = Column(String(255), nullable=False, comment="Item/service name")

    # Financial amounts
    quantity = Column(Numeric(10, 2), nullable=False, default=1.00, comment="Quantity of items")
    unit_price = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Price per unit")
    total = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Total amount (quantity * unit_price)")

    # BPJS specific
    is_bpjs_covered = Column(Boolean, default=False, nullable=False, comment="Whether item is covered by BPJS")
    bpjs_tariff_code = Column(String(50), nullable=True, comment="BPJS tariff code")
    bpjs_package_code = Column(String(50), nullable=True, comment="BPJS package code")

    # Medical coding
    icd_10_code = Column(String(10), nullable=True, index=True, comment="ICD-10 diagnosis code")
    procedure_code = Column(String(20), nullable=True, index=True, comment="Medical procedure code")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    claim = relationship("BPJSClaim", back_populates="items")

    # Indexes
    __table_args__ = (
        Index("ix_bpjs_claim_items_bpjs_claim_id", "bpjs_claim_id"),
        Index("ix_bpjs_claim_items_item_type", "item_type"),
        Index("ix_bpjs_claim_items_item_code", "item_code"),
        Index("ix_bpjs_claim_items_icd_10_code", "icd_10_code"),
        Index("ix_bpjs_claim_items_procedure_code", "procedure_code"),
    )


class BPJSClaimDocument(Base):
    """BPJS Claim Document model for claim-related documents

    This model stores supporting documents required for BPJS claims
    such as SEP, resume medical, DPJP letters, and invoices.
    """
    __tablename__ = "bpjs_claim_documents"

    id = Column(Integer, primary_key=True, index=True)
    bpjs_claim_id = Column(Integer, ForeignKey("bpjs_claims.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to BPJS claim")

    # Document details
    document_type = Column(String(20), nullable=False, index=True, comment="Type of document (sep, resume, dpjp, invoice, other)")
    document_name = Column(String(255), nullable=False, comment="Document name/description")
    file_path = Column(String(500), nullable=False, comment="Path to stored file")
    file_size = Column(Integer, nullable=True, comment="File size in bytes")
    mime_type = Column(String(100), nullable=True, comment="MIME type of file")

    # Upload tracking
    uploaded_at = Column(DateTime(timezone=True), nullable=False, index=True, comment="Upload timestamp")
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="User ID who uploaded")

    # Verification
    verified = Column(Boolean, default=False, nullable=False, comment="Whether document has been verified")
    verified_at = Column(DateTime(timezone=True), nullable=True, comment="Verification timestamp")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    claim = relationship("BPJSClaim", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])

    # Indexes
    __table_args__ = (
        Index("ix_bpjs_claim_documents_bpjs_claim_id", "bpjs_claim_id"),
        Index("ix_bpjs_claim_documents_document_type", "document_type"),
        Index("ix_bpjs_claim_documents_uploaded_at", "uploaded_at"),
    )


class BPJSSubmissionLog(Base):
    """BPJS Submission Log model for tracking claim submission attempts

    This model stores the history of BPJS API submission attempts,
    including request/response data and error tracking.
    """
    __tablename__ = "bpjs_submission_logs"

    id = Column(Integer, primary_key=True, index=True)
    bpjs_claim_id = Column(Integer, ForeignKey("bpjs_claims.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to BPJS claim")

    # Submission details
    submission_date = Column(DateTime(timezone=True), nullable=False, index=True, comment="Submission timestamp")
    status = Column(String(20), nullable=False, index=True, comment="Submission status (pending, success, failed, retrying)")

    # BPJS API data
    request_data = Column(JSON, nullable=True, comment="Request data sent to BPJS API")
    response_data = Column(JSON, nullable=True, comment="Response data received from BPJS API")

    # Error tracking
    error_message = Column(Text, nullable=True, comment="Error message if submission failed")
    retry_count = Column(Integer, nullable=False, default=0, comment="Number of retry attempts")
    success = Column(Boolean, nullable=False, default=False, comment="Whether submission was successful")

    # User tracking
    submitted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="User ID who submitted")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    claim = relationship("BPJSClaim", back_populates="submission_logs")
    submitter = relationship("User", foreign_keys=[submitted_by])

    # Indexes
    __table_args__ = (
        Index("ix_bpjs_submission_logs_bpjs_claim_id", "bpjs_claim_id"),
        Index("ix_bpjs_submission_logs_submission_date", "submission_date"),
        Index("ix_bpjs_submission_logs_status", "status"),
    )


class BPJSVerificationQuery(Base):
    """BPJS Verification Query model for tracking verification queries

    This model stores queries and clarifications requested during BPJS
    claim verification process, including responses and resolution tracking.
    """
    __tablename__ = "bpjs_verification_queries"

    id = Column(Integer, primary_key=True, index=True)
    bpjs_claim_id = Column(Integer, ForeignKey("bpjs_claims.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to BPJS claim")

    # Query details
    query_type = Column(String(50), nullable=False, comment="Type of query (e.g., documentation, medical, administrative)")
    query_text = Column(Text, nullable=False, comment="Query text/question from BPJS")

    # Response details
    response_text = Column(Text, nullable=True, comment="Response to the query")
    responded_at = Column(DateTime(timezone=True), nullable=True, comment="Response timestamp")
    responded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="User ID who responded")

    # Status tracking
    status = Column(String(20), nullable=False, index=True, default="pending", comment="Query status (pending, responded, closed)")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    claim = relationship("BPJSClaim", back_populates="verification_queries")
    responder = relationship("User", foreign_keys=[responded_by])

    # Indexes
    __table_args__ = (
        Index("ix_bpjs_verification_queries_bpjs_claim_id", "bpjs_claim_id"),
        Index("ix_bpjs_verification_queries_status", "status"),
        Index("ix_bpjs_verification_queries_created_at", "created_at"),
    )
