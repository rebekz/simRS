"""Payment Processing Schemas

This module defines Pydantic schemas for payment management, including:
- Payment transactions and allocations
- Patient deposits and deposit usage
- Refunds and refund processing
- Payment summaries and reports
- Receipts and settlements
- Accounts receivable tracking
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class PaymentMethod(str, Enum):
    """Payment methods available"""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    ELECTRONIC_WALLET = "electronic_wallet"
    BPJS = "bpjs"
    INSURANCE = "insurance"
    CHECK = "check"
    DIRECT_DEBIT = "direct_debit"
    PATIENT_DEPOSIT = "patient_deposit"


class PaymentStatus(str, Enum):
    """Payment transaction statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"
    PARTIALLY_REFUNDED = "partially_refunded"


class RefundStatus(str, Enum):
    """Refund processing statuses"""
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# Payment Transaction Schemas
# =============================================================================

class PaymentTransactionBase(BaseModel):
    """Base payment transaction schema"""
    patient_id: int
    payment_method: PaymentMethod
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    payment_date: date
    reference_number: Optional[str] = Field(None, max_length=100)
    transaction_id: Optional[str] = Field(None, max_length=100)  # External payment gateway ID
    approval_code: Optional[str] = Field(None, max_length=100)
    card_last_four: Optional[str] = Field(None, max_length=4)
    bank_name: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = Field(None, max_length=50)
    check_number: Optional[str] = Field(None, max_length=50)
    payment_notes: Optional[str] = Field(None, max_length=1000)
    status: PaymentStatus = PaymentStatus.PENDING
    processed_at: Optional[datetime] = None
    failed_reason: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

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

    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate metadata is a dictionary"""
        if v is not None and not isinstance(v, dict):
            raise ValueError('Metadata must be a dictionary')
        return v


class PaymentTransactionCreate(PaymentTransactionBase):
    """Schema for creating payment transaction"""
    invoice_ids: Optional[List[int]] = Field(default_factory=list)
    encounter_id: Optional[int] = None

    @validator('invoice_ids')
    def validate_invoice_ids(cls, v):
        """Validate invoice IDs list"""
        if v is not None and not isinstance(v, list):
            raise ValueError('Invoice IDs must be a list')
        return v


class PaymentTransactionUpdate(BaseModel):
    """Schema for updating payment transaction"""
    payment_method: Optional[PaymentMethod] = None
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    payment_date: Optional[date] = None
    reference_number: Optional[str] = Field(None, max_length=100)
    transaction_id: Optional[str] = Field(None, max_length=100)
    approval_code: Optional[str] = Field(None, max_length=100)
    card_last_four: Optional[str] = Field(None, max_length=4)
    bank_name: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = Field(None, max_length=50)
    check_number: Optional[str] = Field(None, max_length=50)
    payment_notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[PaymentStatus] = None
    processed_at: Optional[datetime] = None
    failed_reason: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None

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

    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate metadata is a dictionary"""
        if v is not None and not isinstance(v, dict):
            raise ValueError('Metadata must be a dictionary')
        return v


class PaymentTransactionResponse(PaymentTransactionBase):
    """Schema for payment transaction response"""
    id: int
    payment_number: str
    patient_id: int
    patient_name: Optional[str] = None
    allocated_amount: Decimal = Field(default=0, decimal_places=2)
    unallocated_amount: Decimal = Field(default=0, decimal_places=2)
    refunded_amount: Decimal = Field(default=0, decimal_places=2)
    allocations: List['PaymentAllocationResponse'] = Field(default_factory=list)
    refunds: List['RefundResponse'] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class PaymentTransactionListResponse(BaseModel):
    """Schema for paginated payment transaction list"""
    items: List[PaymentTransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# Payment Allocation Schemas
# =============================================================================

class PaymentAllocationBase(BaseModel):
    """Base payment allocation schema"""
    payment_id: int
    invoice_id: int
    allocated_amount: Decimal = Field(..., gt=0, decimal_places=2)
    allocation_date: date
    notes: Optional[str] = Field(None, max_length=500)

    @validator('allocated_amount')
    def validate_allocated_amount(cls, v):
        """Validate allocated amount is positive"""
        if v <= 0:
            raise ValueError('Allocated amount must be greater than 0')
        return v


class PaymentAllocationCreate(PaymentAllocationBase):
    """Schema for creating payment allocation"""
    pass


class PaymentAllocationResponse(PaymentAllocationBase):
    """Schema for payment allocation response"""
    id: int
    payment_id: int
    invoice_id: int
    invoice_number: Optional[str] = None
    payment_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Patient Deposit Schemas
# =============================================================================

class PatientDepositBase(BaseModel):
    """Base patient deposit schema"""
    patient_id: int
    deposit_amount: Decimal = Field(..., gt=0, decimal_places=2)
    deposit_date: date
    payment_method: PaymentMethod
    reference_number: Optional[str] = Field(None, max_length=100)
    transaction_id: Optional[str] = Field(None, max_length=100)
    payment_notes: Optional[str] = Field(None, max_length=500)
    current_balance: Decimal = Field(default=0, ge=0, decimal_places=2)
    is_active: bool = True
    expiry_date: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('deposit_amount')
    def validate_deposit_amount(cls, v):
        """Validate deposit amount is positive"""
        if v <= 0:
            raise ValueError('Deposit amount must be greater than 0')
        return v

    @validator('current_balance')
    def validate_current_balance(cls, v):
        """Validate current balance is non-negative"""
        if v < 0:
            raise ValueError('Current balance cannot be negative')
        return v

    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate metadata is a dictionary"""
        if v is not None and not isinstance(v, dict):
            raise ValueError('Metadata must be a dictionary')
        return v


class PatientDepositCreate(PatientDepositBase):
    """Schema for creating patient deposit"""
    pass


class PatientDepositUpdate(BaseModel):
    """Schema for updating patient deposit"""
    deposit_amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    deposit_date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    reference_number: Optional[str] = Field(None, max_length=100)
    transaction_id: Optional[str] = Field(None, max_length=100)
    payment_notes: Optional[str] = Field(None, max_length=500)
    current_balance: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    is_active: Optional[bool] = None
    expiry_date: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('deposit_amount')
    def validate_deposit_amount(cls, v):
        """Validate deposit amount is positive"""
        if v is not None and v <= 0:
            raise ValueError('Deposit amount must be greater than 0')
        return v

    @validator('current_balance')
    def validate_current_balance(cls, v):
        """Validate current balance is non-negative"""
        if v is not None and v < 0:
            raise ValueError('Current balance cannot be negative')
        return v

    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate metadata is a dictionary"""
        if v is not None and not isinstance(v, dict):
            raise ValueError('Metadata must be a dictionary')
        return v


class PatientDepositResponse(PatientDepositBase):
    """Schema for patient deposit response"""
    id: int
    deposit_number: str
    patient_id: int
    patient_name: Optional[str] = None
    total_deposited: Decimal = Field(default=0, decimal_places=2)
    total_used: Decimal = Field(default=0, decimal_places=2)
    available_balance: Decimal = Field(default=0, decimal_places=2)
    usages: List['DepositUsageResponse'] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


# =============================================================================
# Deposit Usage Schemas
# =============================================================================

class DepositUsageBase(BaseModel):
    """Base deposit usage schema"""
    deposit_id: int
    invoice_id: int
    used_amount: Decimal = Field(..., gt=0, decimal_places=2)
    usage_date: date
    notes: Optional[str] = Field(None, max_length=500)

    @validator('used_amount')
    def validate_used_amount(cls, v):
        """Validate used amount is positive"""
        if v <= 0:
            raise ValueError('Used amount must be greater than 0')
        return v


class DepositUsageCreate(DepositUsageBase):
    """Schema for creating deposit usage"""
    pass


class DepositUsageResponse(DepositUsageBase):
    """Schema for deposit usage response"""
    id: int
    deposit_id: int
    deposit_number: Optional[str] = None
    invoice_id: int
    invoice_number: Optional[str] = None
    remaining_balance: Decimal = Field(default=0, decimal_places=2)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Refund Schemas
# =============================================================================

class RefundBase(BaseModel):
    """Base refund schema"""
    payment_id: int
    refund_amount: Decimal = Field(..., gt=0, decimal_places=2)
    refund_date: date
    refund_method: PaymentMethod
    refund_reason: str = Field(..., min_length=1, max_length=1000)
    reference_number: Optional[str] = Field(None, max_length=100)
    transaction_id: Optional[str] = Field(None, max_length=100)
    bank_name: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = Field(None, max_length=50)
    account_holder_name: Optional[str] = Field(None, max_length=255)
    status: RefundStatus = RefundStatus.PENDING
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('refund_amount')
    def validate_refund_amount(cls, v):
        """Validate refund amount is positive"""
        if v <= 0:
            raise ValueError('Refund amount must be greater than 0')
        return v

    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate metadata is a dictionary"""
        if v is not None and not isinstance(v, dict):
            raise ValueError('Metadata must be a dictionary')
        return v


class RefundCreate(RefundBase):
    """Schema for creating refund"""
    invoice_id: Optional[int] = None


class RefundUpdate(BaseModel):
    """Schema for updating refund"""
    refund_amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    refund_date: Optional[date] = None
    refund_method: Optional[PaymentMethod] = None
    refund_reason: Optional[str] = Field(None, min_length=1, max_length=1000)
    reference_number: Optional[str] = Field(None, max_length=100)
    transaction_id: Optional[str] = Field(None, max_length=100)
    bank_name: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = Field(None, max_length=50)
    account_holder_name: Optional[str] = Field(None, max_length=255)
    status: Optional[RefundStatus] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[Dict[str, Any]] = None

    @validator('refund_amount')
    def validate_refund_amount(cls, v):
        """Validate refund amount is positive"""
        if v is not None and v <= 0:
            raise ValueError('Refund amount must be greater than 0')
        return v

    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate metadata is a dictionary"""
        if v is not None and not isinstance(v, dict):
            raise ValueError('Metadata must be a dictionary')
        return v


class RefundResponse(RefundBase):
    """Schema for refund response"""
    id: int
    refund_number: str
    payment_id: int
    payment_number: Optional[str] = None
    invoice_id: Optional[int] = None
    invoice_number: Optional[str] = None
    patient_id: Optional[int] = None
    patient_name: Optional[str] = None
    approver_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


# =============================================================================
# Additional Payment Schemas
# =============================================================================

class PaymentSummary(BaseModel):
    """Schema for payment summary statistics"""
    total_payments: int
    total_amount: Decimal
    amount_by_method: Dict[str, Decimal] = Field(default_factory=dict)
    amount_by_status: Dict[str, Decimal] = Field(default_factory=dict)
    today_payments: int
    today_amount: Decimal
    week_payments: int
    week_amount: Decimal
    month_payments: int
    month_amount: Decimal
    pending_refunds: int
    pending_refund_amount: Decimal
    average_payment_amount: Decimal


class ReceiptData(BaseModel):
    """Schema for receipt data generation"""
    receipt_number: str
    receipt_date: datetime
    hospital_name: str
    hospital_address: str
    hospital_phone: str
    hospital_tax_id: Optional[str] = None
    patient_name: str
    patient_mrn: str
    payment_number: str
    payment_date: date
    payment_method: PaymentMethod
    amount_paid: Decimal
    amount_in_words: str
    invoice_numbers: List[str] = Field(default_factory=list)
    invoice_amounts: List[Decimal] = Field(default_factory=list)
    total_invoice_amount: Decimal
    change_amount: Optional[Decimal] = None
    cashier_name: str
    payment_notes: Optional[str] = None
    barcode: Optional[str] = None
    qr_code: Optional[str] = None

    class Config:
        from_attributes = True


class SettlementReport(BaseModel):
    """Schema for settlement report"""
    settlement_id: int
    settlement_date: date
    settlement_period_start: date
    settlement_period_end: date
    payment_method: PaymentMethod
    transaction_count: int
    total_amount: Decimal
    settled_amount: Decimal
    pending_amount: Decimal
    fee_amount: Decimal = Field(default=0, decimal_places=2)
    net_amount: Decimal
    currency: str = Field(default="IDR")
    settlement_reference: Optional[str] = None
    provider_reference: Optional[str] = None
    transactions: List[int] = Field(default_factory=list)  # Payment transaction IDs
    created_at: datetime
    generated_by: Optional[int] = None

    class Config:
        from_attributes = True


class AccountsReceivable(BaseModel):
    """Schema for accounts receivable tracking"""
    patient_id: int
    patient_name: str
    patient_mrn: str
    total_billed: Decimal = Field(default=0, decimal_places=2)
    total_paid: Decimal = Field(default=0, decimal_places=2)
    total_outstanding: Decimal = Field(default=0, decimal_places=2)
    current_balance: Decimal = Field(default=0, decimal_places=2)
    overdue_30_days: Decimal = Field(default=0, decimal_places=2)
    overdue_60_days: Decimal = Field(default=0, decimal_places=2)
    overdue_90_days: Decimal = Field(default=0, decimal_places=2)
    overdue_over_90_days: Decimal = Field(default=0, decimal_places=2)
    unpaid_invoices: int = 0
    oldest_unpaid_date: Optional[date] = None
    credit_status: str = Field(default="active")  # active, suspended, collections
    credit_limit: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    available_credit: Optional[Decimal] = Field(None, decimal_places=2)
    last_payment_date: Optional[date] = None
    last_payment_amount: Optional[Decimal] = None
    payment_history_summary: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AccountsReceivableListResponse(BaseModel):
    """Schema for paginated accounts receivable list"""
    items: List[AccountsReceivable]
    total: int
    page: int
    page_size: int
    total_pages: int
    summary: Optional[Dict[str, Any]] = None


class PaymentMethodSummary(BaseModel):
    """Schema for payment method summary statistics"""
    payment_method: PaymentMethod
    transaction_count: int
    total_amount: Decimal
    average_amount: Decimal
    success_rate: Decimal = Field(ge=0, le=100, decimal_places=2)
    failed_count: int
    failed_amount: Decimal
    refund_count: int
    refund_amount: Decimal


class DailyPaymentReport(BaseModel):
    """Schema for daily payment report"""
    report_date: date
    total_transactions: int
    total_amount: Decimal
    cash_amount: Decimal
    card_amount: Decimal
    transfer_amount: Decimal
    electronic_wallet_amount: Decimal
    deposit_amount: Decimal
    insurance_amount: Decimal
    other_amount: Decimal
    refunds_count: int
    refunds_amount: Decimal
    net_amount: Decimal
    previous_day_comparison: Optional[Decimal] = None
    transaction_breakdown: List[PaymentMethodSummary] = Field(default_factory=list)


# =============================================================================
# Batch Operations Schemas
# =============================================================================

class BatchPaymentAllocation(BaseModel):
    """Schema for batch payment allocation"""
    payment_id: int
    allocations: List[Dict[str, Any]] = Field(..., min_items=1)
    allocation_date: date
    notes: Optional[str] = Field(None, max_length=1000)

    @validator('allocations')
    def validate_allocations(cls, v):
        """Validate allocations list"""
        if not v:
            raise ValueError('At least one allocation must be provided')
        for allocation in v:
            if 'invoice_id' not in allocation or 'allocated_amount' not in allocation:
                raise ValueError('Each allocation must have invoice_id and allocated_amount')
        return v


class BatchRefundRequest(BaseModel):
    """Schema for batch refund request"""
    refunds: List[RefundCreate] = Field(..., min_items=1)
    batch_notes: Optional[str] = Field(None, max_length=1000)
    requested_by: int

    @validator('refunds')
    def validate_refunds(cls, v):
        """Validate refunds list"""
        if not v:
            raise ValueError('At least one refund must be provided')
        return v


# Update forward references
PaymentTransactionResponse.model_rebuild()
PatientDepositResponse.model_rebuild()
