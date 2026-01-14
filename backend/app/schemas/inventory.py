"""Pharmacy Inventory schemas for STORY-024

This module defines Pydantic schemas for drug master file, inventory management,
stock transactions, and purchase orders.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# =============================================================================
# Drug Master Schemas
# =============================================================================

class DrugBase(BaseModel):
    """Base drug schema"""
    generic_name: str = Field(..., max_length=255)
    brand_names: Optional[List[str]] = None
    dosage_form: str = Field(..., max_length=50)
    strength: Optional[str] = Field(None, max_length=50)
    route: Optional[str] = Field(None, max_length=50)
    bpjs_code: Optional[str] = Field(None, max_length=50)
    ekatalog_code: Optional[str] = Field(None, max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=255)
    country_of_origin: Optional[str] = Field(None, max_length=100)
    min_stock_level: int = Field(default=10, ge=0)
    max_stock_level: int = Field(default=1000, ge=0)
    reorder_point: int = Field(default=20, ge=0)
    lead_time_days: int = Field(default=7, ge=0)
    purchase_price: Optional[Decimal] = Field(None, ge=0)
    selling_price: Optional[Decimal] = Field(None, ge=0)
    bpjs_price: Optional[Decimal] = Field(None, ge=0)
    is_narcotic: bool = False
    is_antibiotic: bool = False
    requires_prescription: bool = True
    requires_cold_chain: bool = False
    storage_conditions: Optional[str] = None
    shelf_life_months: Optional[int] = None
    atc_code: Optional[str] = Field(None, max_length=20)
    therapeutic_class: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class DrugCreate(DrugBase):
    """Schema for creating a new drug"""
    drug_code: str = Field(..., max_length=50)


class DrugUpdate(BaseModel):
    """Schema for updating a drug"""
    generic_name: Optional[str] = Field(None, max_length=255)
    brand_names: Optional[List[str]] = None
    dosage_form: Optional[str] = Field(None, max_length=50)
    strength: Optional[str] = Field(None, max_length=50)
    route: Optional[str] = Field(None, max_length=50)
    bpjs_code: Optional[str] = Field(None, max_length=50)
    ekatalog_code: Optional[str] = Field(None, max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=255)
    min_stock_level: Optional[int] = Field(None, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    reorder_point: Optional[int] = Field(None, ge=0)
    lead_time_days: Optional[int] = Field(None, ge=0)
    purchase_price: Optional[Decimal] = Field(None, ge=0)
    selling_price: Optional[Decimal] = Field(None, ge=0)
    bpjs_price: Optional[Decimal] = Field(None, ge=0)
    is_narcotic: Optional[bool] = None
    is_antibiotic: Optional[bool] = None
    requires_prescription: Optional[bool] = None
    requires_cold_chain: Optional[bool] = None
    storage_conditions: Optional[str] = None
    shelf_life_months: Optional[int] = None
    atc_code: Optional[str] = Field(None, max_length=20)
    therapeutic_class: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DrugResponse(DrugBase):
    """Schema for drug response"""
    id: int
    drug_code: str
    current_stock: int = 0
    is_below_min_stock: bool = False
    is_near_expiry: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DrugListResponse(BaseModel):
    """Schema for drug list response"""
    drugs: List[DrugResponse]
    total: int
    page: int
    page_size: int


# =============================================================================
# Drug Batch Schemas
# =============================================================================

class DrugBatchCreate(BaseModel):
    """Schema for creating a drug batch"""
    drug_id: int
    batch_number: str = Field(..., max_length=100)
    manufacturing_date: Optional[date] = None
    expiry_date: date
    quantity: int = Field(..., ge=0)
    bin_location: Optional[str] = Field(None, max_length=50)
    unit_cost: Optional[Decimal] = Field(None, ge=0)


class DrugBatchResponse(BaseModel):
    """Schema for drug batch response"""
    id: int
    drug_id: int
    batch_number: str
    manufacturing_date: Optional[date]
    expiry_date: date
    quantity: int
    initial_quantity: int
    bin_location: Optional[str]
    is_quarantined: bool
    days_to_expiry: Optional[int] = None
    is_expired: bool = False
    is_near_expiry: bool = False

    class Config:
        from_attributes = True


# =============================================================================
# Stock Transaction Schemas
# =============================================================================

class StockTransactionItemCreate(BaseModel):
    """Schema for creating stock transaction item"""
    drug_id: int
    batch_id: Optional[int] = None
    quantity: int
    unit_cost: Optional[Decimal] = None
    reason: Optional[str] = Field(None, max_length=255)


class StockTransactionCreate(BaseModel):
    """Schema for creating stock transaction"""
    transaction_type: str = Field(..., regex="^(purchase|sale|adjustment|transfer|return|expiry)$")
    transaction_date: date
    reference_number: Optional[str] = Field(None, max_length=100)
    reference_type: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    items: List[StockTransactionItemCreate]


class StockTransactionResponse(BaseModel):
    """Schema for stock transaction response"""
    id: int
    transaction_number: str
    transaction_type: str
    transaction_date: date
    reference_number: Optional[str]
    status: str
    total_cost: Optional[Decimal]
    items: List[DrugBatchResponse]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Supplier Schemas
# =============================================================================

class SupplierBase(BaseModel):
    """Base supplier schema"""
    supplier_code: str = Field(..., max_length=50)
    supplier_name: str = Field(..., max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    is_bpjs_supplier: bool = False
    bpjs_facility_code: Optional[str] = Field(None, max_length=50)
    payment_terms: Optional[str] = Field(None, max_length=50)
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    is_active: bool = True


class SupplierCreate(SupplierBase):
    """Schema for creating a supplier"""
    pass


class SupplierUpdate(BaseModel):
    """Schema for updating a supplier"""
    supplier_name: Optional[str] = Field(None, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    is_bpjs_supplier: Optional[bool] = None
    bpjs_facility_code: Optional[str] = Field(None, max_length=50)
    payment_terms: Optional[str] = Field(None, max_length=50)
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    """Schema for supplier response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Purchase Order Schemas
# =============================================================================

class PurchaseOrderItemCreate(BaseModel):
    """Schema for creating PO item"""
    drug_id: int
    quantity_ordered: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    notes: Optional[str] = None


class PurchaseOrderCreate(BaseModel):
    """Schema for creating purchase order"""
    supplier_id: int
    order_date: date
    expected_delivery_date: Optional[date] = None
    notes: Optional[str] = None
    items: List[PurchaseOrderItemCreate]


class PurchaseOrderResponse(BaseModel):
    """Schema for purchase order response"""
    id: int
    po_number: str
    supplier_id: int
    supplier_name: str
    order_date: date
    expected_delivery_date: Optional[date]
    status: str
    approval_status: str
    subtotal: Optional[Decimal]
    total: Optional[Decimal]
    items: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Inventory Summary Schemas
# =============================================================================

class InventorySummary(BaseModel):
    """Schema for inventory summary"""
    total_drugs: int
    total_items: int
    total_value: Decimal
    drugs_below_min: int
    drugs_near_expiry: int
    drugs_expired: int
    drugs_out_of_stock: int
    purchase_orders_pending: int
    purchase_orders_approved: int


class InventoryAlert(BaseModel):
    """Schema for inventory alert"""
    alert_type: str  # low_stock, near_expiry, expired
    drug_id: int
    drug_name: str
    drug_code: str
    current_stock: int
    message: str
    severity: str  # critical, warning, info


class StockLevelResponse(BaseModel):
    """Schema for stock level response"""
    drug_id: int
    drug_name: str
    drug_code: str
    generic_name: str
    dosage_form: str
    current_stock: int
    min_stock_level: int
    max_stock_level: int
    reorder_point: int
    is_below_min: bool
    batches: List[DrugBatchResponse]
    last_purchase_price: Optional[Decimal]
    total_value: Optional[Decimal]


# =============================================================================
# Search and Filter Schemas
# =============================================================================

class DrugSearchQuery(BaseModel):
    """Schema for drug search query"""
    search: Optional[str] = None
    dosage_form: Optional[str] = None
    therapeutic_class: Optional[str] = None
    is_narcotic: Optional[bool] = None
    is_antibiotic: Optional[bool] = None
    requires_prescription: Optional[bool] = None
    is_below_min_stock: Optional[bool] = None
    is_near_expiry: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class StockMovementQuery(BaseModel):
    """Schema for stock movement query"""
    drug_id: Optional[int] = None
    transaction_type: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
