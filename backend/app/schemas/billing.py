"""Billing and Invoicing schemas

This module defines Pydantic schemas for billing management, including:
- Invoice and invoice items
- Billing rules and configurations
- Invoice approval workflow
- Payment processing
- Invoice summaries and previews
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class InvoiceType(str, Enum):
    """Types of invoices"""
    OUTPATIENT = "outpatient"
    INPATIENT = "inpatient"
    EMERGENCY = "emergency"
    PHARMACY = "pharmacy"
    LABORATORY = "laboratory"
    RADIOLOGY = "radiology"
    PROCEDURE = "procedure"
    CONSULTATION = "consultation"
    PACKAGE = "package"


class PayerType(str, Enum):
    """Types of payers"""
    PATIENT = "patient"
    BPJS = "bpjs"
    INSURANCE = "insurance"
    COMPANY = "company"
    GOVERNMENT = "government"
    CHARITY = "charity"


class PackageType(str, Enum):
    """Types of service packages"""
    MATERNITY = "maternity"
    SURGERY = "surgery"
    HEALTH_CHECKUP = "health_checkup"
    DENTAL = "dental"
    VACCINATION = "vaccination"
    PHYSIOTHERAPY = "physiotherapy"
    DIALYSIS = "dialysis"
    CUSTOM = "custom"


class InvoiceStatus(str, Enum):
    """Invoice workflow statuses"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    BILLED = "billed"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    WRITE_OFF = "write_off"


class PaymentMethod(str, Enum):
    """Payment methods"""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    ELECTRONIC_WALLET = "electronic_wallet"
    BPJS = "bpjs"
    INSURANCE = "insurance"
    CHECK = "check"
    DIRECT_DEBIT = "direct_debit"


class ItemType(str, Enum):
    """Types of invoice line items"""
    CONSULTATION_FEE = "consultation_fee"
    PROCEDURE_FEE = "procedure_fee"
    ROOM_CHARGE = "room_charge"
    NURSING_FEE = "nursing_fee"
    MEDICATION = "medication"
    LABORATORY = "laboratory"
    RADIOLOGY = "radiology"
    SUPPLY = "supply"
    EQUIPMENT = "equipment"
    THERAPY = "therapy"
    PACKAGE = "package"
    DISCOUNT = "discount"
    TAX = "tax"
    ADJUSTMENT = "adjustment"
    LATE_FEE = "late_fee"
    ADMINISTRATION_FEE = "administration_fee"


# =============================================================================
# Invoice Item Schemas
# =============================================================================

class InvoiceItemBase(BaseModel):
    """Base invoice item schema"""
    item_type: ItemType
    description: str = Field(..., min_length=1, max_length=500)
    quantity: Decimal = Field(..., gt=0, decimal_places=2)
    unit_price: Decimal = Field(..., ge=0, decimal_places=2)
    discount_percent: Decimal = Field(default=0, ge=0, le=100, decimal_places=2)
    tax_percent: Decimal = Field(default=0, ge=0, decimal_places=2)
    reference_id: Optional[str] = Field(None, max_length=100)  # e.g., drug_id, procedure_code
    reference_type: Optional[str] = Field(None, max_length=50)  # e.g., drug, procedure, room
    service_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)

    @validator('quantity')
    def validate_quantity(cls, v):
        """Validate quantity is positive"""
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class InvoiceItemCreate(InvoiceItemBase):
    """Schema for creating invoice item"""
    pass


class InvoiceItemUpdate(BaseModel):
    """Schema for updating invoice item"""
    item_type: Optional[ItemType] = None
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    quantity: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    unit_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    discount_percent: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    tax_percent: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    reference_id: Optional[str] = Field(None, max_length=100)
    reference_type: Optional[str] = Field(None, max_length=50)
    service_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)

    @validator('quantity')
    def validate_quantity(cls, v):
        """Validate quantity is positive"""
        if v is not None and v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class InvoiceItemResponse(InvoiceItemBase):
    """Schema for invoice item response"""
    id: int
    invoice_id: int
    subtotal: Decimal  # quantity * unit_price
    discount_amount: Decimal  # subtotal * discount_percent / 100
    tax_amount: Decimal  # (subtotal - discount_amount) * tax_percent / 100
    total: Decimal  # subtotal - discount_amount + tax_amount
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Payer Information Schema
# =============================================================================

class PayerInformation(BaseModel):
    """Schema for payer details"""
    payer_type: PayerType
    payer_name: str = Field(..., min_length=1, max_length=255)
    payer_id: Optional[str] = Field(None, max_length=100)  # BPJS number, policy number, etc.
    insurance_company: Optional[str] = Field(None, max_length=255)
    policy_number: Optional[str] = Field(None, max_length=100)
    membership_number: Optional[str] = Field(None, max_length=100)
    coverage_percent: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    max_coverage_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    employer_name: Optional[str] = Field(None, max_length=255)
    employer_id: Optional[str] = Field(None, max_length=100)
    billing_address: Optional[str] = Field(None, max_length=500)
    billing_contact: Optional[str] = Field(None, max_length=255)
    billing_phone: Optional[str] = Field(None, max_length=20)
    billing_email: Optional[str] = Field(None, max_length=255)

    @validator('coverage_percent')
    def validate_coverage_percent(cls, v):
        """Validate coverage percentage is valid"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Coverage percent must be between 0 and 100')
        return v


# =============================================================================
# Invoice Schemas
# =============================================================================

class InvoiceBase(BaseModel):
    """Base invoice schema"""
    patient_id: int
    invoice_type: InvoiceType
    invoice_number: Optional[str] = Field(None, max_length=100)
    invoice_date: date
    due_date: Optional[date] = None
    encounter_id: Optional[int] = None
    payer_information: Optional[PayerInformation] = None
    subtotal: Decimal = Field(default=0, ge=0, decimal_places=2)
    discount_amount: Decimal = Field(default=0, ge=0, decimal_places=2)
    tax_amount: Decimal = Field(default=0, ge=0, decimal_places=2)
    total_amount: Decimal = Field(..., ge=0, decimal_places=2)
    paid_amount: Decimal = Field(default=0, ge=0, decimal_places=2)
    balance_due: Decimal = Field(..., decimal_places=2)
    notes: Optional[str] = Field(None, max_length=1000)
    internal_notes: Optional[str] = Field(None, max_length=1000)
    billing_period_start: Optional[date] = None
    billing_period_end: Optional[date] = None

    @validator('due_date')
    def validate_due_date(cls, v, values):
        """Validate due date is after invoice date"""
        if v is not None and 'invoice_date' in values and v < values['invoice_date']:
            raise ValueError('Due date cannot be before invoice date')
        return v

    @validator('billing_period_end')
    def validate_billing_period(cls, v, values):
        """Validate billing period end is after start"""
        if v is not None and 'billing_period_start' in values:
            start = values.get('billing_period_start')
            if start is not None and v < start:
                raise ValueError('Billing period end cannot be before start')
        return v


class InvoiceCreate(InvoiceBase):
    """Schema for creating invoice"""
    items: List[InvoiceItemCreate] = Field(..., min_items=1)

    @validator('items')
    def validate_items(cls, v):
        """Validate items list is not empty"""
        if not v:
            raise ValueError('Invoice must have at least one item')
        return v


class InvoiceUpdate(BaseModel):
    """Schema for updating invoice"""
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    payer_information: Optional[PayerInformation] = None
    subtotal: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    discount_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    tax_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    total_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    paid_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    balance_due: Optional[Decimal] = Field(None, decimal_places=2)
    notes: Optional[str] = Field(None, max_length=1000)
    internal_notes: Optional[str] = Field(None, max_length=1000)
    billing_period_start: Optional[date] = None
    billing_period_end: Optional[date] = None
    items: Optional[List[InvoiceItemCreate]] = None

    @validator('due_date')
    def validate_due_date(cls, v, values):
        """Validate due date logic"""
        # Note: Full validation requires checking against invoice_date from database
        return v

    @validator('billing_period_end')
    def validate_billing_period(cls, v, values):
        """Validate billing period logic"""
        # Note: Full validation requires checking against billing_period_start from database
        return v


class InvoiceResponse(InvoiceBase):
    """Schema for invoice response"""
    id: int
    status: InvoiceStatus
    invoice_number: str
    items: List[InvoiceItemResponse]
    payments: List['PaymentResponse'] = Field(default_factory=list)
    approvals: List['InvoiceApprovalResponse'] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    """Schema for paginated invoice list response"""
    items: List[InvoiceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# Invoice Summary Schema
# =============================================================================

class InvoiceSummary(BaseModel):
    """Schema for invoice summary (lightweight version)"""
    id: int
    invoice_number: str
    invoice_type: InvoiceType
    invoice_date: date
    due_date: Optional[date]
    patient_id: int
    patient_name: str
    status: InvoiceStatus
    total_amount: Decimal
    paid_amount: Decimal
    balance_due: Decimal
    is_overdue: bool = False
    days_overdue: Optional[int] = None
    payer_type: Optional[PayerType] = None

    class Config:
        from_attributes = True


# =============================================================================
# Charge Breakdown Schema
# =============================================================================

class ChargeBreakdown(BaseModel):
    """Schema for detailed charge breakdown"""
    item_type: ItemType
    description: str
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total: Decimal
    service_date: Optional[date]
    is_covered_by_insurance: bool = False
    insurance_coverage_amount: Optional[Decimal] = None
    patient_responsibility: Optional[Decimal] = None


# =============================================================================
# Billing Rule Schemas
# =============================================================================

class BillingRuleBase(BaseModel):
    """Base billing rule schema"""
    rule_name: str = Field(..., min_length=1, max_length=255)
    rule_code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    rule_type: str = Field(..., max_length=50)  # pricing, discount, tax, package
    item_type: Optional[ItemType] = None
    package_type: Optional[PackageType] = None
    payer_type: Optional[PayerType] = None
    is_active: bool = True
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    priority: int = Field(default=100, ge=1, le=999)

    @validator('rule_code')
    def validate_rule_code(cls, v):
        """Validate rule code format"""
        if not v or not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Rule code must contain only alphanumeric characters, underscores, and hyphens')
        return v

    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        """Validate expiry date is after effective date"""
        if v is not None and 'effective_date' in values:
            effective = values.get('effective_date')
            if effective is not None and v < effective:
                raise ValueError('Expiry date cannot be before effective date')
        return v


class BillingRuleCreate(BillingRuleBase):
    """Schema for creating billing rule"""
    conditions: Optional[Dict[str, Any]] = Field(default_factory=dict)
    actions: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('conditions')
    def validate_conditions(cls, v):
        """Validate conditions is a dict"""
        if v is not None and not isinstance(v, dict):
            raise ValueError('Conditions must be a dictionary')
        return v

    @validator('actions')
    def validate_actions(cls, v):
        """Validate actions is a dict"""
        if v is not None and not isinstance(v, dict):
            raise ValueError('Actions must be a dictionary')
        return v


class BillingRuleUpdate(BaseModel):
    """Schema for updating billing rule"""
    rule_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    rule_type: Optional[str] = Field(None, max_length=50)
    item_type: Optional[ItemType] = None
    package_type: Optional[PackageType] = None
    payer_type: Optional[PayerType] = None
    is_active: Optional[bool] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    priority: Optional[int] = Field(None, ge=1, le=999)
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[Dict[str, Any]] = None

    @validator('conditions')
    def validate_conditions(cls, v):
        """Validate conditions is a dict"""
        if v is not None and not isinstance(v, dict):
            raise ValueError('Conditions must be a dictionary')
        return v

    @validator('actions')
    def validate_actions(cls, v):
        """Validate actions is a dict"""
        if v is not None and not isinstance(v, dict):
            raise ValueError('Actions must be a dictionary')
        return v


class BillingRuleResponse(BillingRuleBase):
    """Schema for billing rule response"""
    id: int
    conditions: Dict[str, Any] = Field(default_factory=dict)
    actions: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


# =============================================================================
# Invoice Approval Schemas
# =============================================================================

class InvoiceApprovalBase(BaseModel):
    """Base invoice approval schema"""
    invoice_id: int
    approval_level: str = Field(..., max_length=50)  # supervisor, manager, finance, director
    approver_id: int
    approval_status: str = Field(..., max_length=50)  # pending, approved, rejected
    comments: Optional[str] = Field(None, max_length=1000)
    approved_at: Optional[datetime] = None

    @validator('approval_status')
    def validate_approval_status(cls, v):
        """Validate approval status"""
        valid_statuses = ['pending', 'approved', 'rejected']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Approval status must be one of: {", ".join(valid_statuses)}')
        return v.lower()


class InvoiceApprovalCreate(InvoiceApprovalBase):
    """Schema for creating invoice approval"""
    pass


class InvoiceApprovalResponse(InvoiceApprovalBase):
    """Schema for invoice approval response"""
    id: int
    invoice_id: int
    approver_name: Optional[str] = None
    approver_role: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Payment Schemas
# =============================================================================

class PaymentBase(BaseModel):
    """Base payment schema"""
    invoice_id: int
    payment_date: date
    payment_method: PaymentMethod
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    reference_number: Optional[str] = Field(None, max_length=100)
    bank_name: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = Field(None, max_length=50)
    check_number: Optional[str] = Field(None, max_length=50)
    card_last_four: Optional[str] = Field(None, max_length=4)
    transaction_id: Optional[str] = Field(None, max_length=100)
    approval_code: Optional[str] = Field(None, max_length=100)
    payment_notes: Optional[str] = Field(None, max_length=500)
    is_processed: bool = False
    processed_at: Optional[datetime] = None

    @validator('amount')
    def validate_amount(cls, v):
        """Validate payment amount is positive"""
        if v <= 0:
            raise ValueError('Payment amount must be greater than 0')
        return v

    @validator('card_last_four')
    def validate_card_last_four(cls, v):
        """Validate card last four digits"""
        if v is not None and (not v.isdigit() or len(v) != 4):
            raise ValueError('Card last four must be exactly 4 digits')
        return v


class PaymentCreate(PaymentBase):
    """Schema for creating payment"""
    pass


class PaymentUpdate(BaseModel):
    """Schema for updating payment"""
    payment_date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    reference_number: Optional[str] = Field(None, max_length=100)
    bank_name: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = Field(None, max_length=50)
    check_number: Optional[str] = Field(None, max_length=50)
    card_last_four: Optional[str] = Field(None, max_length=4)
    transaction_id: Optional[str] = Field(None, max_length=100)
    approval_code: Optional[str] = Field(None, max_length=100)
    payment_notes: Optional[str] = Field(None, max_length=500)
    is_processed: Optional[bool] = None
    processed_at: Optional[datetime] = None

    @validator('amount')
    def validate_amount(cls, v):
        """Validate payment amount is positive"""
        if v is not None and v <= 0:
            raise ValueError('Payment amount must be greater than 0')
        return v

    @validator('card_last_four')
    def validate_card_last_four(cls, v):
        """Validate card last four digits"""
        if v is not None and (not v.isdigit() or len(v) != 4):
            raise ValueError('Card last four must be exactly 4 digits')
        return v


class PaymentResponse(PaymentBase):
    """Schema for payment response"""
    id: int
    payment_number: str
    invoice_id: int
    invoice_number: Optional[str] = None
    patient_id: Optional[int] = None
    patient_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


# =============================================================================
# Invoice Preview Schema
# =============================================================================

class InvoicePreview(BaseModel):
    """Schema for invoice preview (pre-generation)"""
    patient_id: int
    patient_name: str
    patient_mrn: str
    invoice_type: InvoiceType
    invoice_date: date
    estimated_items: List[ChargeBreakdown]
    estimated_subtotal: Decimal
    estimated_discount: Decimal
    estimated_tax: Decimal
    estimated_total: Decimal
    insurance_coverage: Optional[Decimal] = None
    estimated_patient_responsibility: Decimal
    applicable_rules: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    information: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


# =============================================================================
# Additional Utility Schemas
# =============================================================================

class InvoiceStatistics(BaseModel):
    """Schema for invoice statistics"""
    total_invoices: int
    total_billed: Decimal
    total_paid: Decimal
    total_outstanding: Decimal
    total_overdue: Decimal
    average_invoice_amount: Decimal
    invoices_by_status: Dict[str, int]
    invoices_by_type: Dict[str, int]
    invoices_by_payer: Dict[str, int]
    current_month_revenue: Decimal
    previous_month_revenue: Decimal
    revenue_change_percent: Optional[Decimal] = None


class BillingDashboard(BaseModel):
    """Schema for billing dashboard summary"""
    today_invoices: int
    today_revenue: Decimal
    pending_approvals: int
    overdue_invoices: int
    overdue_amount: Decimal
    pending_payments: int
    pending_payment_amount: Decimal
    low_stock_alerts: int
    recent_invoices: List[InvoiceSummary]
    upcoming_payments: List[PaymentResponse]
    top_payers: List[Dict[str, Any]]
    revenue_trend: List[Dict[str, Any]]


class InvoiceBatchAction(BaseModel):
    """Schema for batch invoice operations"""
    invoice_ids: List[int] = Field(..., min_items=1)
    action: str = Field(..., pattern="^(approve|reject|cancel|write_off|send_reminder)$")
    reason: Optional[str] = Field(None, max_length=500)
    batch_notes: Optional[str] = Field(None, max_length=1000)

    @validator('invoice_ids')
    def validate_invoice_ids(cls, v):
        """Validate invoice IDs list"""
        if not v:
            raise ValueError('At least one invoice ID must be provided')
        return v


class InvoiceReminder(BaseModel):
    """Schema for invoice reminder"""
    invoice_id: int
    reminder_type: str = Field(..., pattern="^(due_soon|overdue|payment_confirmation|thank_you)$")
    recipient_email: str = Field(..., max_length=255)
    recipient_phone: Optional[str] = Field(None, max_length=20)
    subject: str = Field(..., max_length=255)
    message: str = Field(..., max_length=2000)
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    status: str = Field(default="pending", pattern="^(pending|sent|failed)$")


# Update forward references
InvoiceResponse.model_rebuild()
