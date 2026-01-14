"""Pharmacy Inventory Management models for STORY-024

This module defines the database models for drug master file and inventory tracking,
including stock levels, expiry dates, batch numbers, and transactions.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.session import Base


class Drug(Base):
    """Drug master file containing all drug information"""
    __tablename__ = "drugs"

    id = Column(Integer, primary_key=True, index=True)

    # Drug identification
    generic_name = Column(String(255), nullable=False, index=True)
    brand_names = Column(JSONB, nullable=True)  # List of brand names
    drug_code = Column(String(50), unique=True, nullable=False, index=True)  # Internal code

    # Drug classification
    dosage_form = Column(String(50), nullable=False, index=True)  # tablet, capsule, injection, syrup, etc.
    strength = Column(String(50), nullable=True)  # e.g., "500mg", "10mg/ml"
    route = Column(String(50), nullable=True)  # oral, parenteral, topical, etc.

    # Regulatory and pricing
    bpjs_code = Column(String(50), nullable=True, index=True)  # BPJS drug code
    ekatalog_code = Column(String(50), nullable=True)  # e-Katalog code
    nforma_code = Column(String(50), nullable=True)  # NFORMA code

    # Manufacturer information
    manufacturer = Column(String(255), nullable=True)
    country_of_origin = Column(String(100), nullable=True)

    # Inventory management
    min_stock_level = Column(Integer, nullable=False, default=10)
    max_stock_level = Column(Integer, nullable=False, default=1000)
    reorder_point = Column(Integer, nullable=False, default=20)
    lead_time_days = Column(Integer, nullable=False, default=7)  # Average lead time for restocking

    # Pricing (in IDR)
    purchase_price = Column(Numeric(12, 2), nullable=True)  # Last purchase price
    selling_price = Column(Numeric(12, 2), nullable=True)  # Retail selling price
    bpjs_price = Column(Numeric(12, 2), nullable=True)  # BPJS claim price

    # Drug properties
    is_narcotic = Column(Boolean, server_default=False, nullable=False)  # Controlled substance
    is_antibiotic = Column(Boolean, server_default=False, nullable=False)
    requires_prescription = Column(Boolean, server_default=True, nullable=False)
    requires_cold_chain = Column(Boolean, server_default=False, nullable=False)

    # Storage requirements
    storage_conditions = Column(Text, nullable=True)  # e.g., "Store at 2-8°C"
    shelf_life_months = Column(Integer, nullable=True)  # Typical shelf life

    # Clinical information
    atc_code = Column(String(20), nullable=True, index=True)  # Anatomical Therapeutic Chemical code
    therapeutic_class = Column(String(100), nullable=True)
    generic_group = Column(String(100), nullable=True)

    # Description and notes
    description = Column(Text, nullable=True)
    indications = Column(Text, nullable=True)
    contraindications = Column(Text, nullable=True)
    warnings = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, server_default=True, nullable=False, index=True)

    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)

    # Relationships
    inventory_batches = relationship("DrugBatch", back_populates="drug", cascade="all, delete-orphan")
    stock_transactions = relationship("StockTransaction", back_populates="drug")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="drug")


class DrugBatch(Base):
    """Drug batch tracking for expiry and FIFO"""
    __tablename__ = "drug_batches"

    id = Column(Integer, primary_key=True, index=True)
    drug_id = Column(Integer, ForeignKey("drugs.id"), nullable=False, index=True)

    # Batch identification
    batch_number = Column(String(100), nullable=False, index=True)
    manufacturing_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=False, index=True)

    # Stock information
    quantity = Column(Integer, nullable=False, default=0)  # Current quantity in this batch
    initial_quantity = Column(Integer, nullable=False, default=0)  # Initial quantity received
    bin_location = Column(String(50), nullable=True)  # e.g., "A-01-03"

    # Pricing
    unit_cost = Column(Numeric(12, 2), nullable=True)

    # Status
    is_quarantined = Column(Boolean, server_default=False, nullable=False)  # Expired or defective
    quarantine_reason = Column(Text, nullable=True)

    # Audit fields
    received_date = Column(Date, nullable=False)
    received_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)

    # Relationships
    drug = relationship("Drug", back_populates="inventory_batches")
    supplier = relationship("Supplier", back_populates="batches")
    transaction_items = relationship("StockTransactionItem", back_populates="batch")


class Supplier(Base):
    """Drug supplier information"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    supplier_code = Column(String(50), unique=True, nullable=False)
    supplier_name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)

    # BPJS information
    is_bpjs_supplier = Column(Boolean, server_default=False, nullable=False)
    bpjs_facility_code = Column(String(50), nullable=True)

    # Payment terms
    payment_terms = Column(String(50), nullable=True)  # e.g., "NET 30"
    credit_limit = Column(Numeric(15, 2), nullable=True)

    # Status
    is_active = Column(Boolean, server_default=True, nullable=False)

    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)

    # Relationships
    batches = relationship("DrugBatch", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")


class StockTransaction(Base):
    """Stock transaction header for tracking inventory movements"""
    __tablename__ = "stock_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_number = Column(String(50), unique=True, nullable=False, index=True)
    transaction_type = Column(String(20), nullable=False, index=True)  # purchase, sale, adjustment, transfer, return, expiry
    transaction_date = Column(Date, nullable=False, index=True)

    # Reference documents
    reference_number = Column(String(100), nullable=True)  # PO number, invoice, etc.
    reference_type = Column(String(50), nullable=True)  # purchase_order, sales_return, etc.

    # Status
    status = Column(String(20), nullable=False, server_default="draft")  # draft, confirmed, cancelled
    notes = Column(Text, nullable=True)

    # Financial impact
    total_cost = Column(Numeric(15, 2), nullable=True)

    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)

    # Relationships
    drug = relationship("Drug", back_populates="stock_transactions")
    items = relationship("StockTransactionItem", back_populates="transaction", cascade="all, delete-orphan")


class StockTransactionItem(Base):
    """Stock transaction line items"""
    __tablename__ = "stock_transaction_items"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("stock_transactions.id", ondelete="CASCADE"), nullable=False)
    drug_id = Column(Integer, ForeignKey("drugs.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("drug_batches.id"), nullable=True)

    # Quantity
    quantity = Column(Integer, nullable=False)  # Positive for incoming, negative for outgoing
    quantity_before = Column(Integer, nullable=False)  # Stock level before transaction
    quantity_after = Column(Integer, nullable=False)  # Stock level after transaction

    # Pricing
    unit_cost = Column(Numeric(12, 2), nullable=True)
    total_cost = Column(Numeric(12, 2), nullable=True)

    # Reason (for adjustments)
    reason = Column(String(255), nullable=True)

    # Relationships
    transaction = relationship("StockTransaction", back_populates="items")
    drug = relationship("Drug")
    batch = relationship("DrugBatch", back_populates="transaction_items")


class PurchaseOrder(Base):
    """Purchase order for drug procurement"""
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(50), unique=True, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    order_date = Column(Date, nullable=False, index=True)
    expected_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)

    # Status
    status = Column(String(20), nullable=False, server_default="draft")  # draft, sent, partially_received, received, cancelled
    approval_status = Column(String(20), nullable=False, server_default="pending")  # pending, approved, rejected

    # Financial
    subtotal = Column(Numeric(15, 2), nullable=True)
    tax = Column(Numeric(15, 2), nullable=True)
    discount = Column(Numeric(15, 2), nullable=True)
    total = Column(Numeric(15, 2), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
    supplier_notes = Column(Text, nullable=True)

    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)

    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    receipts = relationship("GoodsReceipt", back_populates="purchase_order")


class PurchaseOrderItem(Base):
    """Purchase order line items"""
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    drug_id = Column(Integer, ForeignKey("drugs.id"), nullable=False)

    # Order details
    quantity_ordered = Column(Integer, nullable=False)
    quantity_received = Column(Integer, server_default=0, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)

    # Subtotal
    subtotal = Column(Numeric(12, 2), nullable=False)

    # Notes
    notes = Column(Text, nullable=True)

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    drug = relationship("Drug")


class GoodsReceipt(Base):
    """Goods receipt note for receiving purchase orders"""
    __tablename__ = "goods_receipts"

    id = Column(Integer, primary_key=True, index=True)
    grn_number = Column(String(50), unique=True, nullable=False, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    receipt_date = Column(Date, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)

    # Invoice information
    invoice_number = Column(String(100), nullable=True)
    invoice_date = Column(Date, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
    received_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    checked_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Quality check

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="receipts")
    items = relationship("GoodsReceiptItem", back_populates="receipt", cascade="all, delete-orphan")


class GoodsReceiptItem(Base):
    """Goods receipt line items"""
    __tablename__ = "goods_receipt_items"

    id = Column(Integer, primary_key=True, index=True)
    grn_id = Column(Integer, ForeignKey("goods_receipts.id", ondelete="CASCADE"), nullable=False)
    drug_id = Column(Integer, ForeignKey("drugs.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("drug_batches.id"), nullable=True)

    # Receipt details
    quantity_received = Column(Integer, nullable=False)
    quantity_accepted = Column(Integer, nullable=False)  # After quality check
    quantity_rejected = Column(Integer, server_default=0, nullable=False)
    rejection_reason = Column(Text, nullable=True)

    # Batch information
    batch_number = Column(String(100), nullable=False)
    expiry_date = Column(Date, nullable=False)
    manufacturing_date = Column(Date, nullable=True)

    # Pricing
    unit_cost = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)

    # Relationships
    receipt = relationship("GoodsReceipt", back_populates="items")
    drug = relationship("Drug")


class NearExpiryAlert(Base):
    """Near expiry alert tracking"""
    __tablename__ = "near_expiry_alerts"

    id = Column(Integer, primary_key=True, index=True)
    drug_id = Column(Integer, ForeignKey("drugs.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("drug_batches.id"), nullable=False)

    # Alert details
    expiry_date = Column(Date, nullable=False, index=True)
    days_to_expiry = Column(Integer, nullable=False)  # Days until expiry
    current_quantity = Column(Integer, nullable=False)

    # Alert status
    is_notified = Column(Boolean, server_default=False, nullable=False)
    notification_date = Column(DateTime(timezone=True), nullable=True)

    # Action taken
    action_taken = Column(String(100), nullable=True)  # returned_to_supplier, discount, written_off
    action_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default="NOW()", nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
