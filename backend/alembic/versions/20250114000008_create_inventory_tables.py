"""create pharmacy inventory tables for STORY-024

Revision ID: 20250114000008
Create Date: 2026-01-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '20250114000008'
down_revision: Union[str, None] = '20250114000007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '20250114000007'


def upgrade() -> None:
    # Create drugs table
    op.create_table(
        'drugs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('generic_name', sa.String(length=255), nullable=False),
        sa.Column('brand_names', JSONB(), nullable=True),
        sa.Column('drug_code', sa.String(length=50), nullable=False),
        sa.Column('dosage_form', sa.String(length=50), nullable=False),
        sa.Column('strength', sa.String(length=50), nullable=True),
        sa.Column('route', sa.String(length=50), nullable=True),
        sa.Column('bpjs_code', sa.String(length=50), nullable=True),
        sa.Column('ekatalog_code', sa.String(length=50), nullable=True),
        sa.Column('nforma_code', sa.String(length=50), nullable=True),
        sa.Column('manufacturer', sa.String(length=255), nullable=True),
        sa.Column('country_of_origin', sa.String(length=100), nullable=True),
        sa.Column('min_stock_level', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('max_stock_level', sa.Integer(), nullable=False, server_default='1000'),
        sa.Column('reorder_point', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('lead_time_days', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('purchase_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('selling_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('bpjs_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('is_narcotic', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_antibiotic', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('requires_prescription', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('requires_cold_chain', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('storage_conditions', sa.Text(), nullable=True),
        sa.Column('shelf_life_months', sa.Integer(), nullable=True),
        sa.Column('atc_code', sa.String(length=20), nullable=True),
        sa.Column('therapeutic_class', sa.String(length=100), nullable=True),
        sa.Column('generic_group', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('indications', sa.Text(), nullable=True),
        sa.Column('contraindications', sa.Text(), nullable=True),
        sa.Column('warnings', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('drug_code')
    )
    op.create_index(op.f('ix_drugs_id'), 'drugs', ['id'], unique=False)
    op.create_index(op.f('ix_drugs_generic_name'), 'drugs', ['generic_name'], unique=False)
    op.create_index(op.f('ix_drugs_drug_code'), 'drugs', ['drug_code'], unique=True)
    op.create_index(op.f('ix_drugs_dosage_form'), 'drugs', ['dosage_form'], unique=False)
    op.create_index(op.f('ix_drugs_is_active'), 'drugs', ['is_active'], unique=False)
    op.create_index(op.f('ix_drugs_bpjs_code'), 'drugs', ['bpjs_code'], unique=False)
    op.create_index(op.f('ix_drugs_atc_code'), 'drugs', ['atc_code'], unique=False)

    # Create drug_batches table
    op.create_table(
        'drug_batches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('drug_id', sa.Integer(), nullable=False),
        sa.Column('batch_number', sa.String(length=100), nullable=False),
        sa.Column('manufacturing_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('initial_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('bin_location', sa.String(length=50), nullable=True),
        sa.Column('unit_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('is_quarantined', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('quarantine_reason', sa.Text(), nullable=True),
        sa.Column('received_date', sa.Date(), nullable=False),
        sa.Column('received_by', sa.Integer(), nullable=True),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['drug_id'], ['drugs.id'], ),
        sa.ForeignKeyConstraint(['received_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_drug_batches_id'), 'drug_batches', ['id'], unique=False)
    op.create_index(op.f('ix_drug_batches_drug_id'), 'drug_batches', ['drug_id'], unique=False)
    op.create_index(op.f('ix_drug_batches_batch_number'), 'drug_batches', ['batch_number'], unique=False)
    op.create_index(op.f('ix_drug_batches_expiry_date'), 'drug_batches', ['expiry_date'], unique=False)

    # Create suppliers table
    op.create_table(
        'suppliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('supplier_code', sa.String(length=50), nullable=False),
        sa.Column('supplier_name', sa.String(length=255), nullable=False),
        sa.Column('contact_person', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('is_bpjs_supplier', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('bpjs_facility_code', sa.String(length=50), nullable=True),
        sa.Column('payment_terms', sa.String(length=50), nullable=True),
        sa.Column('credit_limit', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('supplier_code')
    )
    op.create_index(op.f('ix_suppliers_id'), 'suppliers', ['id'], unique=False)

    # Create stock_transactions table
    op.create_table(
        'stock_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_number', sa.String(length=50), nullable=False),
        sa.Column('transaction_type', sa.String(length=20), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('total_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('confirmed_by', sa.Integer(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['confirmed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_number')
    )
    op.create_index(op.f('ix_stock_transactions_id'), 'stock_transactions', ['id'], unique=False)
    op.create_index(op.f('ix_stock_transactions_transaction_number'), 'stock_transactions', ['transaction_number'], unique=True)
    op.create_index(op.f('ix_stock_transactions_transaction_type'), 'stock_transactions', ['transaction_type'], unique=False)
    op.create_index(op.f('ix_stock_transactions_transaction_date'), 'stock_transactions', ['transaction_date'], unique=False)

    # Create stock_transaction_items table
    op.create_table(
        'stock_transaction_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('drug_id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('quantity_before', sa.Integer(), nullable=False),
        sa.Column('quantity_after', sa.Integer(), nullable=False),
        sa.Column('unit_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('total_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['batch_id'], ['drug_batches.id'], ),
        sa.ForeignKeyConstraint(['drug_id'], ['drugs.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['stock_transactions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_transaction_items_id'), 'stock_transaction_items', ['id'], unique=False)
    op.create_index(op.f('ix_stock_transaction_items_transaction_id'), 'stock_transaction_items', ['transaction_id'], unique=False)

    # Create purchase_orders table
    op.create_table(
        'purchase_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('po_number', sa.String(length=50), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('order_date', sa.Date(), nullable=False),
        sa.Column('expected_delivery_date', sa.Date(), nullable=True),
        sa.Column('actual_delivery_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('approval_status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('subtotal', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('tax', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('discount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('supplier_notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('po_number')
    )
    op.create_index(op.f('ix_purchase_orders_id'), 'purchase_orders', ['id'], unique=False)
    op.create_index(op.f('ix_purchase_orders_po_number'), 'purchase_orders', ['po_number'], unique=True)
    op.create_index(op.f('ix_purchase_orders_order_date'), 'purchase_orders', ['order_date'], unique=False)

    # Create purchase_order_items table
    op.create_table(
        'purchase_order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('po_id', sa.Integer(), nullable=False),
        sa.Column('drug_id', sa.Integer(), nullable=False),
        sa.Column('quantity_ordered', sa.Integer(), nullable=False),
        sa.Column('quantity_received', sa.Integer(), server_default='0', nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('subtotal', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['drug_id'], ['drugs.id'], ),
        sa.ForeignKeyConstraint(['po_id'], ['purchase_orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_order_items_id'), 'purchase_order_items', ['id'], unique=False)
    op.create_index(op.f('ix_purchase_order_items_po_id'), 'purchase_order_items', ['po_id'], unique=False)

    # Create goods_receipts table
    op.create_table(
        'goods_receipts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('grn_number', sa.String(length=50), nullable=False),
        sa.Column('po_id', sa.Integer(), nullable=False),
        sa.Column('receipt_date', sa.Date(), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(length=100), nullable=True),
        sa.Column('invoice_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('received_by', sa.Integer(), nullable=True),
        sa.Column('checked_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['checked_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['po_id'], ['purchase_orders.id'], ),
        sa.ForeignKeyConstraint(['received_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('grn_number')
    )
    op.create_index(op.f('ix_goods_receipts_id'), 'goods_receipts', ['id'], unique=False)
    op.create_index(op.f('ix_goods_receipts_grn_number'), 'goods_receipts', ['grn_number'], unique=True)
    op.create_index(op.f('ix_goods_receipts_receipt_date'), 'goods_receipts', ['receipt_date'], unique=False)

    # Create goods_receipt_items table
    op.create_table(
        'goods_receipt_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('grn_id', sa.Integer(), nullable=False),
        sa.Column('drug_id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('quantity_received', sa.Integer(), nullable=False),
        sa.Column('quantity_accepted', sa.Integer(), nullable=False),
        sa.Column('quantity_rejected', sa.Integer(), server_default='0', nullable=False),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('batch_number', sa.String(length=100), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('manufacturing_date', sa.Date(), nullable=True),
        sa.Column('unit_cost', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('subtotal', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['drug_batches.id'], ),
        sa.ForeignKeyConstraint(['drug_id'], ['drugs.id'], ),
        sa.ForeignKeyConstraint(['grn_id'], ['goods_receipts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_goods_receipt_items_id'), 'goods_receipt_items', ['id'], unique=False)
    op.create_index(op.f('ix_goods_receipt_items_grn_id'), 'goods_receipt_items', ['grn_id'], unique=False)

    # Create near_expiry_alerts table
    op.create_table(
        'near_expiry_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('drug_id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('days_to_expiry', sa.Integer(), nullable=False),
        sa.Column('current_quantity', sa.Integer(), nullable=False),
        sa.Column('is_notified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notification_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('action_taken', sa.String(length=100), nullable=True),
        sa.Column('action_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['batch_id'], ['drug_batches.id'], ),
        sa.ForeignKeyConstraint(['drug_id'], ['drugs.id'], ),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_near_expiry_alerts_id'), 'near_expiry_alerts', ['id'], unique=False)
    op.create_index(op.f('ix_near_expiry_alerts_expiry_date'), 'near_expiry_alerts', ['expiry_date'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('near_expiry_alerts')
    op.drop_table('goods_receipt_items')
    op.drop_table('goods_receipts')
    op.drop_table('purchase_order_items')
    op.drop_table('purchase_orders')
    op.drop_table('stock_transaction_items')
    op.drop_table('stock_transactions')
    op.drop_table('suppliers')
    op.drop_table('drug_batches')
    op.drop_table('drugs')
