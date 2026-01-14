"""Create prescription tables for STORY-017

Revision ID: 20250114000011
Revises: 20250114000010
Create Date: 2025-01-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, ENUM


# revision identifiers, used by Alembic.
revision: str = '20250114000011'
down_revision: Union[str, None] = '20250114000010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '20250114000010'


def upgrade() -> None:
    # Create enums
    prescription_status_enum = ENUM(
        'draft', 'active', 'on_hold', 'completed', 'cancelled', 'entered_in_error',
        name='prescriptionstatus', create_type=True
    )
    prescription_status_enum.create(op.get_bind())

    prescription_item_type_enum = ENUM(
        'simple', 'compound', 'supply',
        name='prescriptionitemtype', create_type=True
    )
    prescription_item_type_enum.create(op.get_bind())

    dispense_status_enum = ENUM(
        'pending', 'partial', 'dispensed', 'not_dispensed',
        name='dispensestatus', create_type=True
    )
    dispense_status_enum.create(op.get_bind())

    # Create prescriptions table
    op.create_table(
        'prescriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prescription_number', sa.String(length=50), nullable=False),
        sa.Column('barcode', sa.String(length=100), nullable=True),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('encounter_id', sa.Integer(), nullable=False),
        sa.Column('prescriber_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('draft', 'active', 'on_hold', 'completed', 'cancelled', 'entered_in_error', name='prescriptionstatus'), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='routine'),
        sa.Column('diagnosis', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('submitted_to_pharmacy', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('submitted_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_fully_dispensed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('dispensed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by_id', sa.Integer(), nullable=True),
        sa.Column('verified_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('bpjs_coverage_estimate', sa.Float(), nullable=True),
        sa.Column('patient_cost_estimate', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['prescriber_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['verified_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prescriptions_barcode'), 'prescriptions', ['barcode'], unique=True)
    op.create_index(op.f('ix_prescriptions_encounter_id'), 'prescriptions', ['encounter_id'], unique=False)
    op.create_index(op.f('ix_prescriptions_patient_id'), 'prescriptions', ['patient_id'], unique=False)
    op.create_index(op.f('ix_prescriptions_prescriber_id'), 'prescriptions', ['prescriber_id'], unique=False)
    op.create_index(op.f('ix_prescriptions_prescription_number'), 'prescriptions', ['prescription_number'], unique=True)
    op.create_index(op.f('ix_prescriptions_status'), 'prescriptions', ['status'], unique=False)

    # Create prescription_items table
    op.create_table(
        'prescription_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prescription_id', sa.Integer(), nullable=False),
        sa.Column('item_type', sa.Enum('simple', 'compound', 'supply', name='prescriptionitemtype'), nullable=False),
        sa.Column('drug_id', sa.Integer(), nullable=False),
        sa.Column('drug_name', sa.String(length=255), nullable=False),
        sa.Column('generic_name', sa.String(length=255), nullable=False),
        sa.Column('dosage', sa.String(length=100), nullable=False),
        sa.Column('dose_unit', sa.String(length=50), nullable=False),
        sa.Column('frequency', sa.String(length=100), nullable=False),
        sa.Column('route', sa.String(length=50), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('quantity_dispensed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('compound_name', sa.String(length=255), nullable=True),
        sa.Column('compound_components', JSON(), nullable=True),
        sa.Column('indication', sa.Text(), nullable=True),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.Column('is_prn', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('dispense_status', sa.Enum('pending', 'partial', 'dispensed', 'not_dispensed', name='dispensestatus'), nullable=False),
        sa.Column('dispensed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dispenser_id', sa.Integer(), nullable=True),
        sa.Column('refills_allowed', sa.Integer(), nullable=True),
        sa.Column('refills_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['dispenser_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['drug_id'], ['drugs.id'], ),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prescription_items_prescription_id'), 'prescription_items', ['prescription_id'], unique=False)

    # Create prescription_transmissions table
    op.create_table(
        'prescription_transmissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prescription_id', sa.Integer(), nullable=False),
        sa.Column('transmission_id', sa.String(length=100), nullable=False),
        sa.Column('target_pharmacy_id', sa.Integer(), nullable=True),
        sa.Column('target_pharmacy_name', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='queued'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_ready_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prescription_transmissions_prescription_id'), 'prescription_transmissions', ['prescription_id'], unique=False)
    op.create_index(op.f('ix_prescription_transmissions_transmission_id'), 'prescription_transmissions', ['transmission_id'], unique=True)

    # Create prescription_verification_logs table
    op.create_table(
        'prescription_verification_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prescription_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('verifier_id', sa.Integer(), nullable=False),
        sa.Column('verifier_name', sa.String(length=255), nullable=False),
        sa.Column('verifier_role', sa.String(length=50), nullable=False),
        sa.Column('issues_found', JSON(), nullable=True),
        sa.Column('requires_intervention', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('intervention_notes', sa.Text(), nullable=True),
        sa.Column('interactions_overridden', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('override_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ),
        sa.ForeignKeyConstraint(['verifier_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prescription_verification_logs_prescription_id'), 'prescription_verification_logs', ['prescription_id'], unique=False)

    # Create prescription_print_logs table
    op.create_table(
        'prescription_print_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prescription_id', sa.Integer(), nullable=False),
        sa.Column('printed_by_id', sa.Integer(), nullable=False),
        sa.Column('printed_by_name', sa.String(length=255), nullable=False),
        sa.Column('print_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('included_barcode', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('included_diagnosis', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('included_instructions', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('document_url', sa.String(length=500), nullable=True),
        sa.Column('document_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['printed_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prescription_print_logs_prescription_id'), 'prescription_print_logs', ['prescription_id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_prescription_print_logs_prescription_id'), table_name='prescription_print_logs')
    op.drop_table('prescription_print_logs')

    op.drop_index(op.f('ix_prescription_verification_logs_prescription_id'), table_name='prescription_verification_logs')
    op.drop_table('prescription_verification_logs')

    op.drop_index(op.f('ix_prescription_transmissions_transmission_id'), table_name='prescription_transmissions')
    op.drop_index(op.f('ix_prescription_transmissions_prescription_id'), table_name='prescription_transmissions')
    op.drop_table('prescription_transmissions')

    op.drop_index(op.f('ix_prescription_items_prescription_id'), table_name='prescription_items')
    op.drop_table('prescription_items')

    op.drop_index(op.f('ix_prescriptions_status'), table_name='prescriptions')
    op.drop_index(op.f('ix_prescriptions_prescription_number'), table_name='prescriptions')
    op.drop_index(op.f('ix_prescriptions_prescriber_id'), table_name='prescriptions')
    op.drop_index(op.f('ix_prescriptions_patient_id'), table_name='prescriptions')
    op.drop_index(op.f('ix_prescriptions_encounter_id'), table_name='prescriptions')
    op.drop_index(op.f('ix_prescriptions_barcode'), table_name='prescriptions')
    op.drop_table('prescriptions')

    # Drop enums
    sa.Enum(name='dispensestatus').drop(op.get_bind())
    sa.Enum(name='prescriptionitemtype').drop(op.get_bind())
    sa.Enum(name='prescriptionstatus').drop(op.get_bind())
