"""Patient Portal Billing & Payments Schemas

Pydantic schemas for viewing and paying bills through patient portal.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from enum import Enum


class InvoiceStatus(str, Enum):
    """Status of invoice"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    PARTIAL_PAID = "partial_paid"
    CANCELLED = "cancelled"
    WRITTEN_OFF = "written_off"


class PayerType(str, Enum):
    """Type of payer"""
    BPJS = "bpjs"
    ASURANSI = "asuransi"
    UMUM = "umum"
    CORPORATE = "corporate"


class PaymentMethod(str, Enum):
    """Payment method options"""
    CASH = "cash"
    TRANSFER = "transfer"
    CREDIT_CARD = "credit_card"
    VIRTUAL_ACCOUNT = "virtual_account"
    EWALLET = "ewallet"
    QRIS = "qris"


class InvoiceItem(BaseModel):
    """Single line item on an invoice"""
    id: int
    item_type: str
    item_code: Optional[str] = None
    item_name: str
    description: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total: Decimal
    doctor_name: Optional[str] = None
    service_date: Optional[date] = None
    is_bpjs_covered: bool = False

    model_config = ConfigDict(from_attributes=True)


class InvoiceListItem(BaseModel):
    """Invoice for list view"""
    id: int
    invoice_number: str
    invoice_date: date
    invoice_type: str
    status: str
    total_amount: Decimal
    paid_amount: Decimal
    balance_due: Decimal
    due_date: Optional[date] = None
    is_overdue: bool = False
    payer_type: str

    model_config = ConfigDict(from_attributes=True)


class InvoiceDetail(BaseModel):
    """Detailed invoice information"""
    id: int
    invoice_number: str
    invoice_date: date
    invoice_type: str
    status: str
    due_date: Optional[date] = None
    payer_type: str
    insurance_company: Optional[str] = None
    policy_number: Optional[str] = None
    bpjs_membership_number: Optional[str] = None

    # Amounts
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    balance_due: Decimal

    # Items
    items: List[InvoiceItem]

    # Payment summary
    payment_history: List["PaymentRecord"]
    outstanding_balance: Decimal

    # Dates
    created_at: datetime
    approved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InvoiceListResponse(BaseModel):
    """Response for patient's invoices"""
    invoices: List[InvoiceListItem]
    total: int
    outstanding_balance: Decimal
    overdue_count: int
    overdue_amount: Decimal


class PaymentRecord(BaseModel):
    """Payment record"""
    id: int
    payment_date: datetime
    payment_method: str
    amount: Decimal
    reference_number: Optional[str] = None
    bank_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaymentInitiationRequest(BaseModel):
    """Request to initiate payment"""
    invoice_id: int
    payment_method: PaymentMethod
    amount: Decimal = Field(..., gt=0, description="Amount to pay")
    return_url: Optional[str] = Field(None, description="URL to redirect after payment")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v, info):
        # Ensure amount doesn't exceed typical limits
        if v > 100000000:  # 100 million IDR
            raise ValueError('Payment amount exceeds maximum allowed')
        return v


class PaymentInitiationResponse(BaseModel):
    """Response after initiating payment"""
    payment_id: str
    payment_url: Optional[str] = None
    qr_code: Optional[str] = None
    virtual_account_number: Optional[str] = None
    amount: Decimal
    expires_at: Optional[datetime] = None
    message: str


class PaymentStatusResponse(BaseModel):
    """Payment status response"""
    payment_id: str
    status: str
    amount_paid: Optional[Decimal] = None
    paid_at: Optional[datetime] = None
    payment_method: Optional[str] = None


class BPJSClaimStatus(BaseModel):
    """BPJS claim status information"""
    claim_id: Optional[str] = None
    claim_number: Optional[str] = None
    submission_date: Optional[date] = None
    status: str
    approved_amount: Optional[Decimal] = None
    rejection_reason: Optional[str] = None


class InsuranceExplanationOfBenefits(BaseModel):
    """Insurance explanation of benefits"""
    total_charged: Decimal
    total_allowed: Decimal
    insurance_paid: Decimal
    patient_responsibility: Decimal
    deductible: Decimal
    co_payment: Decimal
    co_insurance: Decimal
    not_covered: List[str]


class PaymentMethodConfig(BaseModel):
    """Payment method configuration"""
    method: PaymentMethod
    name: str
    is_available: bool
    fee_percentage: Optional[Decimal] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    description: Optional[str] = None
