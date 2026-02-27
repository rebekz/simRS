"""Billing and Invoice models for STORY-027: Billing and Invoice Management

This module defines the database models for managing patient billing, invoices,
and payment processing in the SIMRS system.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Numeric, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from app.db.session import Base


class InvoiceType(str, Enum):
    """Invoice type options"""
    OUTPATIENT = "outpatient"
    INPATIENT = "inpatient"
    PHARMACY = "pharmacy"
    RADIOLOGY = "radiology"
    LAB = "lab"


class PayerType(str, Enum):
    """Payer type options"""
    BPJS = "bpjs"
    ASURANSI = "asuransi"
    UMUM = "umum"
    CORPORATE = "corporate"


class PackageType(str, Enum):
    """Package type options for BPJS billing"""
    INA_CBG = "ina_cbg"
    FEE_FOR_SERVICE = "fee_for_service"
    PACKAGE_RATE = "package_rate"


class InvoiceStatus(str, Enum):
    """Invoice status options"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    PARTIAL_PAID = "partial_paid"
    CANCELLED = "cancelled"
    WRITTEN_OFF = "written_off"


class InvoiceItemType(str, Enum):
    """Invoice item type options"""
    PROFESSIONAL_FEE = "professional_fee"
    HOTEL_SERVICE = "hotel_service"
    DRUG = "drug"
    LAB = "lab"
    RADIOLOGY = "radiology"
    PROCEDURE = "procedure"
    SUPPLY = "supply"
    OTHER = "other"


class BillingRuleType(str, Enum):
    """Billing rule type options"""
    DISCOUNT = "discount"
    SURCHARGE = "surcharge"
    CO_PAYMENT = "co_payment"
    DEDUCTIBLE = "deductible"


class ApprovalStatus(str, Enum):
    """Approval status options"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PaymentMethod(str, Enum):
    """Payment method options"""
    CASH = "cash"
    TRANSFER = "transfer"
    CREDIT_CARD = "credit_card"
    BPJS = "bpjs"
    INSURANCE = "insurance"


class Invoice(Base):
    """Invoice model for managing patient billing invoices

    This model stores comprehensive invoice data including billing details,
    insurance information, package codes, and approval workflow status.
    """
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False, comment="Unique invoice number")
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True, comment="Reference to patient")
    encounter_id = Column(Integer, ForeignKey("encounters.id", ondelete="RESTRICT"), nullable=True, index=True, comment="Reference to encounter")

    # Invoice dates
    invoice_date = Column(Date, nullable=False, index=True, comment="Invoice creation date")
    due_date = Column(Date, nullable=True, index=True, comment="Payment due date")
    payment_due_date = Column(Date, nullable=True, comment="Final payment due date")

    # Invoice classification
    invoice_type = Column(String(20), nullable=False, index=True, comment="Type of invoice (outpatient, inpatient, pharmacy, radiology, lab)")
    billing_period_start = Column(Date, nullable=True, comment="Billing period start date")
    billing_period_end = Column(Date, nullable=True, comment="Billing period end date")

    # Financial amounts
    subtotal = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Subtotal before tax and discounts")
    tax_amount = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Tax amount")
    discount_amount = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Total discount amount")
    total_amount = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Final total amount")
    paid_amount = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Amount paid")
    balance_due = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Remaining balance")

    # Payer information
    payer_type = Column(String(20), nullable=False, index=True, comment="Type of payer (bpjs, asuransi, umum, corporate)")
    payer_id = Column(Integer, nullable=True, index=True, comment="Reference to payer entity")
    insurance_company = Column(String(255), nullable=True, comment="Insurance company name")
    policy_number = Column(String(100), nullable=True, index=True, comment="Insurance policy number")
    bpjs_membership_number = Column(String(50), nullable=True, index=True, comment="BPJS membership number")

    # Package information (BPJS)
    package_type = Column(String(20), nullable=True, comment="Package type (ina_cbg, fee_for_service, package_rate)")
    package_code = Column(String(50), nullable=True, index=True, comment="Package code")
    drg_code = Column(String(20), nullable=True, comment="Diagnosis Related Group code")
    case_mix_group = Column(String(50), nullable=True, comment="Case mix group classification")

    # Status and workflow
    status = Column(String(20), nullable=False, index=True, default="draft", comment="Invoice status")
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="Approved by user ID")
    approved_at = Column(DateTime(timezone=True), nullable=True, comment="Approval timestamp")
    rejected_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="Rejected by user ID")
    rejected_at = Column(DateTime(timezone=True), nullable=True, comment="Rejection timestamp")
    rejection_reason = Column(Text, nullable=True, comment="Reason for rejection")

    # Notes
    notes = Column(Text, nullable=True, comment="Public notes visible to patient")
    internal_notes = Column(Text, nullable=True, comment="Internal notes for billing staff")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    patient = relationship("Patient", backref="invoices")
    encounter = relationship("Encounter", backref="invoices")
    approver = relationship("User", foreign_keys=[approved_by])
    rejector = relationship("User", foreign_keys=[rejected_by])
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    approvals = relationship("InvoiceApproval", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_invoices_invoice_number", "invoice_number"),
        Index("ix_invoices_patient_id", "patient_id"),
        Index("ix_invoices_encounter_id", "encounter_id"),
        Index("ix_invoices_invoice_date", "invoice_date"),
        Index("ix_invoices_status", "status"),
        Index("ix_invoices_payer_type", "payer_type"),
    )


class InvoiceItem(Base):
    """Invoice item model for individual line items on an invoice

    This model stores detailed line items for each invoice including
    professional fees, services, drugs, and supplies.
    """
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to invoice")

    # Item details
    item_type = Column(String(50), nullable=False, index=True, comment="Type of item (professional_fee, hotel_service, drug, lab, radiology, procedure, supply, other)")
    item_code = Column(String(50), nullable=True, index=True, comment="Item/service code")
    item_name = Column(String(255), nullable=False, comment="Item/service name")
    description = Column(Text, nullable=True, comment="Item description")

    # Financial amounts
    quantity = Column(Numeric(10, 2), nullable=False, default=1.00, comment="Quantity of items")
    unit_price = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Price per unit")
    subtotal = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Subtotal (quantity * unit_price)")
    tax_amount = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Tax amount for this item")
    discount_amount = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Discount amount for this item")
    total = Column(Numeric(12, 2), nullable=False, default=0.00, comment="Total amount for this item")

    # Service details
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="Doctor ID for professional fees")
    department_id = Column(Integer, nullable=True, index=True, comment="Department ID for the service")
    service_date = Column(Date, nullable=True, index=True, comment="Date service was provided")

    # BPJS specific
    is_bpjs_covered = Column(Boolean, default=False, nullable=False, comment="Whether item is covered by BPJS")
    bpjs_tariff_code = Column(String(50), nullable=True, comment="BPJS tariff code")
    bpjs_package_code = Column(String(50), nullable=True, comment="BPJS package code")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    doctor = relationship("User", foreign_keys=[doctor_id])

    # Indexes
    __table_args__ = (
        Index("ix_invoice_items_invoice_id", "invoice_id"),
        Index("ix_invoice_items_item_type", "item_type"),
        Index("ix_invoice_items_item_code", "item_code"),
        Index("ix_invoice_items_doctor_id", "doctor_id"),
        Index("ix_invoice_items_service_date", "service_date"),
    )


class BillingRule(Base):
    """Billing rule model for automatic billing calculations

    This model stores rules for discounts, surcharges, co-payments,
    and deductibles based on payer type and package codes.
    """
    __tablename__ = "billing_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(255), nullable=False, comment="Rule name/description")
    rule_type = Column(String(20), nullable=False, index=True, comment="Type of rule (discount, surcharge, co_payment, deductible)")

    # Rule conditions
    payer_type = Column(String(20), nullable=True, index=True, comment="Applicable payer type")
    insurance_company = Column(String(255), nullable=True, comment="Applicable insurance company")
    package_code = Column(String(50), nullable=True, index=True, comment="Applicable package code")

    # Rule definition (JSON)
    condition_json = Column(JSON, nullable=True, comment="Rule conditions in JSON format")
    action_json = Column(JSON, nullable=True, comment="Rule actions in JSON format")

    # Rule properties
    priority = Column(Integer, nullable=False, default=0, comment="Rule priority (higher = applied first)")
    is_active = Column(Boolean, default=True, nullable=False, comment="Whether rule is active")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Indexes
    __table_args__ = (
        Index("ix_billing_rules_rule_type", "rule_type"),
        Index("ix_billing_rules_payer_type", "payer_type"),
        Index("ix_billing_rules_package_code", "package_code"),
        Index("ix_billing_rules_priority", "priority"),
    )


class InvoiceApproval(Base):
    """Invoice approval model for tracking approval workflow

    This model stores the approval history for each invoice,
    tracking who approved or rejected and when.
    """
    __tablename__ = "invoice_approvals"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to invoice")
    approver_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False, index=True, comment="User ID of approver")
    approval_status = Column(String(20), nullable=False, index=True, comment="Approval status (pending, approved, rejected)")
    comments = Column(Text, nullable=True, comment="Approval or rejection comments")
    approved_at = Column(DateTime(timezone=True), nullable=True, comment="Approval/rejection timestamp")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    invoice = relationship("Invoice", back_populates="approvals")
    approver = relationship("User", foreign_keys=[approver_id])

    # Indexes
    __table_args__ = (
        Index("ix_invoice_approvals_invoice_id", "invoice_id"),
        Index("ix_invoice_approvals_approver_id", "approver_id"),
        Index("ix_invoice_approvals_approval_status", "approval_status"),
        Index("ix_invoice_approvals_approved_at", "approved_at"),
    )


class Payment(Base):
    """Payment model for tracking invoice payments

    This model stores payment details for each invoice including
    payment method, amount, and transaction references.
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to invoice")
    payment_date = Column(DateTime(timezone=True), nullable=False, index=True, comment="Payment date and time")
    payment_method = Column(String(20), nullable=False, index=True, comment="Payment method (cash, transfer, credit_card, bpjs, insurance)")

    # Payment details
    amount = Column(Numeric(12, 2), nullable=False, comment="Payment amount")
    reference_number = Column(String(100), nullable=True, unique=True, comment="Payment reference/transaction number")
    bank_name = Column(String(100), nullable=True, comment="Bank name for transfers/credit cards")
    payment_gateway_response = Column(JSON, nullable=True, comment="Payment gateway response data")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    invoice = relationship("Invoice", back_populates="payments")

    # Indexes
    __table_args__ = (
        Index("ix_payments_invoice_id", "invoice_id"),
        Index("ix_payments_payment_date", "payment_date"),
        Index("ix_payments_payment_method", "payment_method"),
        Index("ix_payments_reference_number", "reference_number"),
    )
