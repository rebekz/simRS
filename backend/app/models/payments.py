"""Payment processing models for STORY-028: Payment Processing

This module defines the database models for managing payment transactions,
allocations, patient deposits, deposit usage, and refunds in the SIMRS system.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Numeric, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from app.db.session import Base


class PaymentTransactionStatus(str, Enum):
    """Payment transaction status options"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethod(str, Enum):
    """Payment method options"""
    CASH = "cash"
    TRANSFER = "transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BPJS = "bpjs"
    INSURANCE = "insurance"
    E_WALLET = "e_wallet"


class PaymentGateway(str, Enum):
    """Payment gateway options"""
    MANUAL = "manual"
    MIDTRANS = "midtrans"
    XENDIT = "xendit"
    OY = "oy"
    STRIPE = "stripe"


class PatientDepositStatus(str, Enum):
    """Patient deposit status options"""
    ACTIVE = "active"
    EXHAUSTED = "exhausted"
    FROZEN = "frozen"
    CLOSED = "closed"


class RefundStatus(str, Enum):
    """Refund status options"""
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"


class PaymentTransaction(Base):
    """Payment transaction model for managing payment records

    This model stores comprehensive payment transaction data including
    payment method details, gateway information, approval codes, and
    settlement tracking.
    """
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_number = Column(String(50), unique=True, index=True, nullable=False, comment="Unique transaction number")
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="RESTRICT"), nullable=True, index=True, comment="Reference to invoice")
    payment_date = Column(DateTime(timezone=True), nullable=False, index=True, comment="Payment date and time")
    payment_method = Column(String(20), nullable=False, index=True, comment="Payment method (cash, transfer, credit_card, debit_card, bpjs, insurance, e_wallet)")

    # Payment amounts
    amount = Column(Numeric(12, 2), nullable=False, comment="Payment amount")

    # Payment details
    reference_number = Column(String(100), nullable=True, index=True, comment="Payment reference/transaction number from payment provider")
    approval_code = Column(String(100), nullable=True, comment="Approval code from payment gateway")
    bank_name = Column(String(100), nullable=True, comment="Bank name for card/transfer payments")
    card_last_4 = Column(String(4), nullable=True, comment="Last 4 digits of card")

    # Payment gateway information
    payment_gateway = Column(String(20), nullable=True, index=True, comment="Payment gateway used (manual, midtrans, xendit, oy, stripe)")
    payment_gateway_response = Column(JSON, nullable=True, comment="Full payment gateway response in JSON format")

    # Status and workflow
    status = Column(String(20), nullable=False, index=True, default="pending", comment="Payment status (pending, completed, failed, refunded, partially_refunded)")
    processed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="User who processed the payment")

    # Settlement information
    settlement_date = Column(Date, nullable=True, index=True, comment="Date payment was settled")
    settlement_reference = Column(String(100), nullable=True, comment="Settlement reference number")

    # Notes
    notes = Column(Text, nullable=True, comment="Payment notes or additional information")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    invoice = relationship("Invoice", backref="payment_transactions")
    processor = relationship("User", foreign_keys=[processed_by])
    allocations = relationship("PaymentAllocation", back_populates="payment_transaction", cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="payment_transaction", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_payment_transactions_transaction_number", "transaction_number"),
        Index("ix_payment_transactions_invoice_id", "invoice_id"),
        Index("ix_payment_transactions_payment_date", "payment_date"),
        Index("ix_payment_transactions_payment_method", "payment_method"),
        Index("ix_payment_transactions_status", "status"),
        Index("ix_payment_transactions_reference_number", "reference_number"),
        Index("ix_payment_transactions_payment_gateway", "payment_gateway"),
        Index("ix_payment_transactions_settlement_date", "settlement_date"),
    )


class PaymentAllocation(Base):
    """Payment allocation model for tracking payment distribution across invoices

    This model stores how payment transactions are allocated to specific invoices,
    supporting partial payments and payment splitting across multiple invoices.
    """
    __tablename__ = "payment_allocations"

    id = Column(Integer, primary_key=True, index=True)
    payment_transaction_id = Column(Integer, ForeignKey("payment_transactions.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to payment transaction")
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="RESTRICT"), nullable=False, index=True, comment="Reference to invoice")
    allocated_amount = Column(Numeric(12, 2), nullable=False, comment="Amount allocated from payment to this invoice")
    allocation_date = Column(DateTime(timezone=True), nullable=False, index=True, comment="Date and time of allocation")
    allocated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="User who made the allocation")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    payment_transaction = relationship("PaymentTransaction", back_populates="allocations")
    invoice = relationship("Invoice", backref="payment_allocations")
    allocator = relationship("User", foreign_keys=[allocated_by])

    # Indexes
    __table_args__ = (
        Index("ix_payment_allocations_payment_transaction_id", "payment_transaction_id"),
        Index("ix_payment_allocations_invoice_id", "invoice_id"),
        Index("ix_payment_allocations_allocation_date", "allocation_date"),
    )


class PatientDeposit(Base):
    """Patient deposit model for managing prepayments and patient balances

    This model stores patient deposit funds that can be used for future services,
    tracking deposit balance and usage history.
    """
    __tablename__ = "patient_deposits"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True, comment="Reference to patient")
    deposit_number = Column(String(50), unique=True, index=True, nullable=False, comment="Unique deposit number")
    deposit_date = Column(DateTime(timezone=True), nullable=False, index=True, comment="Deposit date and time")
    amount = Column(Numeric(12, 2), nullable=False, comment="Initial deposit amount")

    # Payment details
    payment_method = Column(String(20), nullable=False, index=True, comment="Payment method used for deposit")
    reference_number = Column(String(100), nullable=True, comment="Payment reference number")

    # Status and balance
    status = Column(String(20), nullable=False, index=True, default="active", comment="Deposit status (active, exhausted, frozen, closed)")
    remaining_balance = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Remaining balance available for use")

    # Notes
    notes = Column(Text, nullable=True, comment="Deposit notes or terms")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    patient = relationship("Patient", backref="deposits")
    usage_records = relationship("DepositUsage", back_populates="patient_deposit", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_patient_deposits_deposit_number", "deposit_number"),
        Index("ix_patient_deposits_patient_id", "patient_id"),
        Index("ix_patient_deposits_deposit_date", "deposit_date"),
        Index("ix_patient_deposits_status", "status"),
    )


class DepositUsage(Base):
    """Deposit usage model for tracking how patient deposits are applied

    This model records each instance where a patient deposit is used to
    pay for services, maintaining an audit trail of deposit utilization.
    """
    __tablename__ = "deposit_usage"

    id = Column(Integer, primary_key=True, index=True)
    patient_deposit_id = Column(Integer, ForeignKey("patient_deposits.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to patient deposit")
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="RESTRICT"), nullable=False, index=True, comment="Reference to invoice paid with deposit")
    amount_used = Column(Numeric(12, 2), nullable=False, comment="Amount used from deposit")
    used_date = Column(DateTime(timezone=True), nullable=False, index=True, comment="Date and time of usage")
    used_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="User who processed the deposit usage")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    patient_deposit = relationship("PatientDeposit", back_populates="usage_records")
    invoice = relationship("Invoice", backref="deposit_usage_records")
    user = relationship("User", foreign_keys=[used_by])

    # Indexes
    __table_args__ = (
        Index("ix_deposit_usage_patient_deposit_id", "patient_deposit_id"),
        Index("ix_deposit_usage_invoice_id", "invoice_id"),
        Index("ix_deposit_usage_used_date", "used_date"),
    )


class Refund(Base):
    """Refund model for managing payment refunds

    This model tracks refund requests, approvals, and processing for
    payment transactions, maintaining a complete refund audit trail.
    """
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    payment_transaction_id = Column(Integer, ForeignKey("payment_transactions.id", ondelete="RESTRICT"), nullable=False, index=True, comment="Reference to payment transaction")
    refund_number = Column(String(50), unique=True, index=True, nullable=False, comment="Unique refund number")
    refund_date = Column(DateTime(timezone=True), nullable=False, index=True, comment="Refund request date and time")
    amount = Column(Numeric(12, 2), nullable=False, comment="Refund amount")

    # Refund details
    reason = Column(Text, nullable=False, comment="Reason for refund")
    status = Column(String(20), nullable=False, index=True, default="requested", comment="Refund status (requested, approved, rejected, processed)")

    # Approval workflow
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="User who approved the refund")
    approved_at = Column(DateTime(timezone=True), nullable=True, comment="Approval timestamp")

    # Processing details
    processed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="User who processed the refund")
    processed_at = Column(DateTime(timezone=True), nullable=True, comment="Processing completion timestamp")
    reference_number = Column(String(100), nullable=True, comment="Refund transaction reference number")

    # Notes
    notes = Column(Text, nullable=True, comment="Additional refund notes or processing details")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    payment_transaction = relationship("PaymentTransaction", back_populates="refunds")
    approver = relationship("User", foreign_keys=[approved_by])
    processor = relationship("User", foreign_keys=[processed_by])

    # Indexes
    __table_args__ = (
        Index("ix_refunds_refund_number", "refund_number"),
        Index("ix_refunds_payment_transaction_id", "payment_transaction_id"),
        Index("ix_refunds_refund_date", "refund_date"),
        Index("ix_refunds_status", "status"),
        Index("ix_refunds_reference_number", "reference_number"),
    )
