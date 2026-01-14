"""Create dispensing tables for STORY-025

Revision ID: 20250114000012
Revises: 20250114000011
Create Date: 2025-01-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, ENUM


# revision identifiers, used by Alembic.
revision: str = '20250114000012'
down_revision: Union[str, None] = '20250114000011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '20250114000011'


def upgrade() -> None:
    # Create enums
    dispensing_status_enum = ENUM(
        'queued', 'in_progress', 'awaiting_verification', 'verified', 'ready_for_pickup', 'dispensed', 'cancelled', 'on_hold',
        name='dispensingstatus', create_type=True
    )
    dispensing_status_enum.create(op.get_bind())

    dispense_priority_enum = ENUM(
        'stat', 'urgent', 'routine',
        name='dispensepriority', create_type=True
    )
    dispense_priority_enum.create(op.get_bind())

    verification_status_enum = ENUM(
        'pending', 'approved', 'flagged', 'rejected',
        name='verificationstatus', create_type=True
    )
    verification_status_enum.create(op.get_bind())

    # Create dispensing_queue table
    op.create_table(
        'dispensing_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prescription_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('queued', 'in_progress', 'awaiting_verification', 'verified', 'ready_for_pickup', 'dispensed', 'cancelled', 'on_hold', name='dispensingstatus'), nullable=False),
        sa.Column('priority', sa.Enum('stat', 'urgent', 'routine', name='dispensepriority'), nullable=False),
        sa.Column('queue_position', sa.Integer(), nullable=True),
        sa.Column('estimated_ready_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_wait_minutes', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dispensed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('verified_by_id', sa.Integer(), nullable=True),
        sa.Column('total_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('items_scanned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('items_verified', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('dispensing_notes', sa.Text(), nullable=True),
        sa.Column('hold_reason', sa.Text(), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ),
        sa.ForeignKeyConstraint(['verified_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('prescription_id')
    )
    op.create_index(op.f('ix_dispensing_queue_prescription_id'), 'dispensing_queue', ['prescription_id'], unique=True)
    op.create_index(op.f('ix_dispensing_queue_priority'), 'dispensing_queue', ['priority'], unique=False)
    op.create_index(op.f('ix_dispensing_queue_status'), 'dispensing_queue', ['status'], unique=False)

    # Create dispensing_scans table
    op.create_table(
        'dispensing_scans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dispensing_id', sa.Integer(), nullable=False),
        sa.Column('prescription_item_id', sa.Integer(), nullable=False),
        sa.Column('scanned_barcode', sa.String(length=100), nullable=False),
        sa.Column('scanned_drug_id', sa.Integer(), nullable=False),
        sa.Column('scanned_drug_name', sa.String(length=255), nullable=False),
        sa.Column('scanned_drug_batch', sa.String(length=100), nullable=True),
        sa.Column('expected_drug_id', sa.Integer(), nullable=False),
        sa.Column('expected_drug_name', sa.String(length=255), nullable=False),
        sa.Column('expected_quantity', sa.Integer(), nullable=False),
        sa.Column('is_match', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('quantity_scanned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('scan_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('scanned_by_id', sa.Integer(), nullable=False),
        sa.Column('warnings', JSON(), nullable=True),
        sa.Column('errors', JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['dispensing_id'], ['dispensing_queue.id'], ),
        sa.ForeignKeyConstraint(['expected_drug_id'], ['drugs.id'], ),
        sa.ForeignKeyConstraint(['prescription_item_id'], ['prescription_items.id'], ),
        sa.ForeignKeyConstraint(['scanned_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['scanned_drug_id'], ['drugs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dispensing_scans_dispensing_id'), 'dispensing_scans', ['dispensing_id'], unique=False)
    op.create_index(op.f('ix_dispensing_scans_prescription_item_id'), 'dispensing_scans', ['prescription_item_id'], unique=False)

    # Create patient_counseling table
    op.create_table(
        'patient_counseling',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prescription_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('counselor_id', sa.Integer(), nullable=False),
        sa.Column('counselor_name', sa.String(length=255), nullable=False),
        sa.Column('counseling_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('discussed_purpose', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('discussed_dosage', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('discussed_timing', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('discussed_side_effects', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('discussed_interactions', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('discussed_storage', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('discussed_special_instructions', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('patient_understood', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('patient_questions', JSON(), nullable=True),
        sa.Column('concerns_raised', JSON(), nullable=True),
        sa.Column('counseling_notes', sa.Text(), nullable=True),
        sa.Column('follow_up_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('follow_up_notes', sa.Text(), nullable=True),
        sa.Column('patient_signature', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('caregiver_name', sa.String(length=255), nullable=True),
        sa.Column('caregiver_relationship', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['counselor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('prescription_id')
    )
    op.create_index(op.f('ix_patient_counseling_patient_id'), 'patient_counseling', ['patient_id'], unique=False)
    op.create_index(op.f('ix_patient_counseling_prescription_id'), 'patient_counseling', ['prescription_id'], unique=True)

    # Create dispensing_labels table
    op.create_table(
        'dispensing_labels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dispensing_id', sa.Integer(), nullable=False),
        sa.Column('prescription_item_id', sa.Integer(), nullable=False),
        sa.Column('label_data', JSON(), nullable=False),
        sa.Column('label_text', sa.Text(), nullable=False),
        sa.Column('barcode', sa.String(length=100), nullable=False),
        sa.Column('warning_emoji', sa.String(length=10), nullable=True),
        sa.Column('generated_by_id', sa.Integer(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('print_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['dispensing_id'], ['dispensing_queue.id'], ),
        sa.ForeignKeyConstraint(['generated_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['prescription_item_id'], ['prescription_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dispensing_labels_barcode'), 'dispensing_labels', ['barcode'], unique=True)
    op.create_index(op.f('ix_dispensing_labels_dispensing_id'), 'dispensing_labels', ['dispensing_id'], unique=False)
    op.create_index(op.f('ix_dispensing_labels_prescription_item_id'), 'dispensing_labels', ['prescription_item_id'], unique=False)

    # Create prescription_verification_records table
    op.create_table(
        'prescription_verification_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prescription_id', sa.Integer(), nullable=False),
        sa.Column('dispensing_id', sa.Integer(), nullable=False),
        sa.Column('verification_status', sa.Enum('pending', 'approved', 'flagged', 'rejected', name='verificationstatus'), nullable=False),
        sa.Column('verified_by_id', sa.Integer(), nullable=False),
        sa.Column('verified_by_role', sa.String(length=50), nullable=False),
        sa.Column('verified_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('patient_verified', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('patient_verification_method', sa.String(length=50), nullable=True),
        sa.Column('issues_found', JSON(), nullable=True),
        sa.Column('requires_intervention', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('intervention_notes', sa.Text(), nullable=True),
        sa.Column('interactions_overridden', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('override_reason', sa.Text(), nullable=True),
        sa.Column('override_approved_by_id', sa.Integer(), nullable=True),
        sa.Column('verification_notes', sa.Text(), nullable=True),
        sa.Column('can_proceed', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['dispensing_id'], ['dispensing_queue.id'], ),
        sa.ForeignKeyConstraint(['override_approved_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ),
        sa.ForeignKeyConstraint(['verified_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dispensing_id'),
        sa.UniqueConstraint('prescription_id')
    )
    op.create_index(op.f('ix_prescription_verification_records_prescription_id'), 'prescription_verification_records', ['prescription_id'], unique=True)

    # Create stock_check_logs table
    op.create_table(
        'stock_check_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prescription_id', sa.Integer(), nullable=False),
        sa.Column('drug_id', sa.Integer(), nullable=False),
        sa.Column('required_quantity', sa.Integer(), nullable=False),
        sa.Column('available_quantity', sa.Integer(), nullable=False),
        sa.Column('stock_available', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('alternative_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('alternative_drug_id', sa.Integer(), nullable=True),
        sa.Column('alternative_drug_name', sa.String(length=255), nullable=True),
        sa.Column('backordered', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('estimated_restock_date', sa.Date(), nullable=True),
        sa.Column('checked_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['alternative_drug_id'], ['drugs.id'], ),
        sa.ForeignKeyConstraint(['checked_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['drug_id'], ['drugs.id'], ),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_check_logs_prescription_id'), 'stock_check_logs', ['prescription_id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_stock_check_logs_prescription_id'), table_name='stock_check_logs')
    op.drop_table('stock_check_logs')

    op.drop_index(op.f('ix_prescription_verification_records_prescription_id'), table_name='prescription_verification_records')
    op.drop_table('prescription_verification_records')

    op.drop_index(op.f('ix_dispensing_labels_prescription_item_id'), table_name='dispensing_labels')
    op.drop_index(op.f('ix_dispensing_labels_dispensing_id'), table_name='dispensing_labels')
    op.drop_index(op.f('ix_dispensing_labels_barcode'), table_name='dispensing_labels')
    op.drop_table('dispensing_labels')

    op.drop_index(op.f('ix_patient_counseling_prescription_id'), table_name='patient_counseling')
    op.drop_index(op.f('ix_patient_counseling_patient_id'), table_name='patient_counseling')
    op.drop_table('patient_counseling')

    op.drop_index(op.f('ix_dispensing_scans_prescription_item_id'), table_name='dispensing_scans')
    op.drop_index(op.f('ix_dispensing_scans_dispensing_id'), table_name='dispensing_scans')
    op.drop_table('dispensing_scans')

    op.drop_index(op.f('ix_dispensing_queue_status'), table_name='dispensing_queue')
    op.drop_index(op.f('ix_dispensing_queue_priority'), table_name='dispensing_queue')
    op.drop_index(op.f('ix_dispensing_queue_prescription_id'), table_name='dispensing_queue')
    op.drop_table('dispensing_queue')

    # Drop enums
    sa.Enum(name='verificationstatus').drop(op.get_bind())
    sa.Enum(name='dispensepriority').drop(op.get_bind())
    sa.Enum(name='dispensingstatus').drop(op.get_bind())
