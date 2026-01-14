"""Create admission workflow tables for STORY-021

Revision ID: 20250114000016
Revises: 20250114000015
Create Date: 2025-01-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = '20250114000016'
down_revision: Union[str, None] = '20250114000015'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '20250114000015'


def upgrade() -> None:
    # Create enums
    admission_type_enum = ENUM(
        'emergency', 'urgent', 'elective', 'transfer',
        name='admissiontype', create_type=True
    )
    admission_type_enum.create(op.get_bind())

    admission_status_enum = ENUM(
        'pending', 'admitted', 'transferred', 'discharged', 'cancelled', 'deceased',
        name='admissionstatus', create_type=True
    )
    admission_status_enum.create(op.get_bind())

    room_transfer_status_enum = ENUM(
        'requested', 'approved', 'in_progress', 'completed', 'cancelled',
        name='roomtransferstatus', create_type=True
    )
    room_transfer_status_enum.create(op.get_bind())

    # Create admission_orders table
    op.create_table(
        'admission_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(length=50), nullable=False),
        sa.Column('admission_type', sa.Enum('emergency', 'urgent', 'elective', 'transfer', name='admissiontype'), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='routine'),
        sa.Column('status', sa.Enum('pending', 'admitted', 'transferred', 'discharged', 'cancelled', 'deceased', name='admissionstatus'), nullable=False, server_default='pending'),
        sa.Column('chief_complaint', sa.Text(), nullable=False),
        sa.Column('diagnosis', sa.Text(), nullable=True),
        sa.Column('admission_reason', sa.Text(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('requested_room_class', sa.String(length=10), nullable=True),
        sa.Column('requested_ward_id', sa.Integer(), nullable=True),
        sa.Column('admission_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expected_discharge_date', sa.Date(), nullable=True),
        sa.Column('discharge_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('bpjs_sep_number', sa.String(length=50), nullable=True),
        sa.Column('assigned_bed_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assigned_bed_id'], ['beds.id'], ),
        sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['requested_ward_id'], ['departments.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number'),
        sa.UniqueConstraint('bpjs_sep_number')
    )
    op.create_index(op.f('ix_admission_orders_id'), 'admission_orders', ['id'], unique=False)
    op.create_index(op.f('ix_admission_orders_order_number'), 'admission_orders', ['order_number'], unique=True)
    op.create_index(op.f('ix_admission_orders_patient_id'), 'admission_orders', ['patient_id'], unique=False)
    op.create_index(op.f('ix_admission_orders_doctor_id'), 'admission_orders', ['doctor_id'], unique=False)
    op.create_index(op.f('ix_admission_orders_status'), 'admission_orders', ['status'], unique=False)

    # Create room_transfers table
    op.create_table(
        'room_transfers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('from_bed_id', sa.Integer(), nullable=False),
        sa.Column('to_bed_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('transfer_type', sa.String(length=20), nullable=False, server_default='routine'),
        sa.Column('status', sa.Enum('requested', 'approved', 'in_progress', 'completed', 'cancelled', name='roomtransferstatus'), nullable=False, server_default='requested'),
        sa.Column('requested_by_id', sa.Integer(), nullable=False),
        sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('approved_by_id', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_by_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['completed_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['from_bed_id'], ['beds.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['requested_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['to_bed_id'], ['beds.id'], ),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_room_transfers_id'), 'room_transfers', ['id'], unique=False)
    op.create_index(op.f('ix_room_transfers_admission_id'), 'room_transfers', ['admission_id'], unique=False)
    op.create_index(op.f('ix_room_transfers_status'), 'room_transfers', ['status'], unique=False)

    # Create admission_documentation table
    op.create_table(
        'admission_documentation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('admission_notes', sa.Text(), nullable=True),
        sa.Column('allergies', sa.Text(), nullable=True),
        sa.Column('current_medications', sa.Text(), nullable=True),
        sa.Column('advance_directives', sa.Text(), nullable=True),
        sa.Column('emergency_contact', sa.String(length=200), nullable=True),
        sa.Column('insurance_info', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('admission_id')
    )
    op.create_index(op.f('ix_admission_documentation_id'), 'admission_documentation', ['id'], unique=False)

    # Create admission_documents table (generated documents)
    op.create_table(
        'admission_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('document_url', sa.String(length=500), nullable=False),
        sa.Column('document_title', sa.String(length=200), nullable=False),
        sa.Column('generated_by_id', sa.Integer(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['generated_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admission_documents_id'), 'admission_documents', ['id'], unique=False)

    # Create discharge_readiness_assessments table
    op.create_table(
        'discharge_readiness_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('is_ready', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('readiness_score', sa.Float(), nullable=False),
        sa.Column('criteria_met', sa.Text(), nullable=True),
        sa.Column('criteria_not_met', sa.Text(), nullable=True),
        sa.Column('barriers_to_discharge', sa.Text(), nullable=True),
        sa.Column('required_follow_up', sa.Text(), nullable=True),
        sa.Column('assessed_by_id', sa.Integer(), nullable=False),
        sa.Column('assessed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['assessed_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discharge_readiness_assessments_id'), 'discharge_readiness_assessments', ['id'], unique=False)
    op.create_index(op.f('ix_discharge_readiness_assessments_admission_id'), 'discharge_readiness_assessments', ['admission_id'], unique=False)

    # Create bed_change_history table
    op.create_table(
        'bed_change_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('from_bed_id', sa.Integer(), nullable=True),
        sa.Column('to_bed_id', sa.Integer(), nullable=True),
        sa.Column('change_type', sa.String(length=50), nullable=False),
        sa.Column('change_reason', sa.Text(), nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('changed_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.Column('changed_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['from_bed_id'], ['beds.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['to_bed_id'], ['beds.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bed_change_history_id'), 'bed_change_history', ['id'], unique=False)
    op.create_index(op.f('ix_bed_change_history_admission_id'), 'bed_change_history', ['admission_id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_bed_change_history_admission_id'), table_name='bed_change_history')
    op.drop_index(op.f('ix_bed_change_history_id'), table_name='bed_change_history')
    op.drop_table('bed_change_history')

    op.drop_index(op.f('ix_discharge_readiness_assessments_admission_id'), table_name='discharge_readiness_assessments')
    op.drop_index(op.f('ix_discharge_readiness_assessments_id'), table_name='discharge_readiness_assessments')
    op.drop_table('discharge_readiness_assessments')

    op.drop_index(op.f('ix_admission_documents_id'), table_name='admission_documents')
    op.drop_table('admission_documents')

    op.drop_index(op.f('ix_admission_documentation_id'), table_name='admission_documentation')
    op.drop_table('admission_documentation')

    op.drop_index(op.f('ix_room_transfers_status'), table_name='room_transfers')
    op.drop_index(op.f('ix_room_transfers_admission_id'), table_name='room_transfers')
    op.drop_index(op.f('ix_room_transfers_id'), table_name='room_transfers')
    op.drop_table('room_transfers')

    op.drop_index(op.f('ix_admission_orders_status'), table_name='admission_orders')
    op.drop_index(op.f('ix_admission_orders_doctor_id'), table_name='admission_orders')
    op.drop_index(op.f('ix_admission_orders_patient_id'), table_name='admission_orders')
    op.drop_index(op.f('ix_admission_orders_order_number'), table_name='admission_orders')
    op.drop_index(op.f('ix_admission_orders_id'), table_name='admission_orders')
    op.drop_table('admission_orders')

    # Drop enums
    sa.Enum(name='roomtransferstatus').drop(op.get_bind())
    sa.Enum(name='admissionstatus').drop(op.get_bind())
    sa.Enum(name='admissiontype').drop(op.get_bind())
