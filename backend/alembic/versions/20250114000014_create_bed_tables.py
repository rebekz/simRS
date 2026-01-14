"""Create bed management tables for STORY-020

Revision ID: 20250114000014
Revises: 20250114000013
Create Date: 2025-01-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = '20250114000014'
down_revision: Union[str, None] = '20250114000013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '20250114000013'


def upgrade() -> None:
    # Create enums
    room_class_enum = ENUM(
        'vvip', 'vip', '1', '2', '3',
        name='roomclass', create_type=True
    )
    room_class_enum.create(op.get_bind())

    room_status_enum = ENUM(
        'clean', 'soiled', 'maintenance', 'isolation',
        name='roomstatus', create_type=True
    )
    room_status_enum.create(op.get_bind())

    bed_status_enum = ENUM(
        'available', 'occupied', 'maintenance', 'reserved',
        name='bedstatus', create_type=True
    )
    bed_status_enum.create(op.get_bind())

    gender_type_enum = ENUM(
        'male', 'female', 'mixed',
        name='gendertype', create_type=True
    )
    gender_type_enum.create(op.get_bind())

    bed_request_status_enum = ENUM(
        'pending', 'approved', 'assigned', 'cancelled', 'completed',
        name='bedrequeststatus', create_type=True
    )
    bed_request_status_enum.create(op.get_bind())

    # Create rooms table
    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ward_id', sa.Integer(), nullable=False),
        sa.Column('room_number', sa.String(length=50), nullable=False),
        sa.Column('room_class', sa.Enum('vvip', 'vip', '1', '2', '3', name='roomclass'), nullable=False),
        sa.Column('gender_type', sa.Enum('male', 'female', 'mixed', name='gendertype'), nullable=False),
        sa.Column('total_beds', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('floor', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('clean', 'soiled', 'maintenance', 'isolation', name='roomstatus'), nullable=False, server_default='clean'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ward_id'], ['wards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rooms_id'), 'rooms', ['id'], unique=False)
    op.create_index(op.f('ix_rooms_ward_class'), 'rooms', ['ward_id', 'room_class'], unique=False)
    op.create_index(op.f('ix_rooms_ward_number'), 'rooms', ['ward_id', 'room_number'], unique=False)
    op.create_index(op.f('ix_rooms_ward_id'), 'rooms', ['ward_id'], unique=False)
    op.create_index(op.f('ix_rooms_room_number'), 'rooms', ['room_number'], unique=False)

    # Create beds table
    op.create_table(
        'beds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('bed_number', sa.String(length=50), nullable=False),
        sa.Column('bed_type', sa.String(length=50), nullable=False, server_default='standard'),
        sa.Column('room_number', sa.String(length=50), nullable=False),
        sa.Column('ward_id', sa.Integer(), nullable=False),
        sa.Column('room_class', sa.String(length=10), nullable=False),
        sa.Column('gender_type', sa.String(length=10), nullable=False),
        sa.Column('floor', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('available', 'occupied', 'maintenance', 'reserved', name='bedstatus'), nullable=False, server_default='available'),
        sa.Column('current_patient_id', sa.Integer(), nullable=True),
        sa.Column('admission_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expected_discharge_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['current_patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_beds_id'), 'beds', ['id'], unique=False)
    op.create_index(op.f('ix_beds_room_bed'), 'beds', ['room_id', 'bed_number'], unique=False)
    op.create_index(op.f('ix_beds_status'), 'beds', ['status'], unique=False)
    op.create_index(op.f('ix_beds_ward_status'), 'beds', ['ward_id', 'status'], unique=False)
    op.create_index(op.f('ix_beds_room_id'), 'beds', ['room_id'], unique=False)
    op.create_index(op.f('ix_beds_current_patient_id'), 'beds', ['current_patient_id'], unique=False)

    # Create bed_assignments table
    op.create_table(
        'bed_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('bed_id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('assigned_by_id', sa.Integer(), nullable=False),
        sa.Column('expected_discharge_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('assign_for_isolation', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('discharged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('discharged_by_id', sa.Integer(), nullable=True),
        sa.Column('discharge_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['encounters.id'], ),
        sa.ForeignKeyConstraint(['assigned_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['bed_id'], ['beds.id'], ),
        sa.ForeignKeyConstraint(['discharged_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bed_assignments_id'), 'bed_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_bed_assignments_active'), 'bed_assignments', ['bed_id', 'discharged_at'], unique=False)
    op.create_index(op.f('ix_bed_assignments_bed'), 'bed_assignments', ['bed_id'], unique=False)
    op.create_index(op.f('ix_bed_assignments_patient'), 'bed_assignments', ['patient_id'], unique=False)
    op.create_index(op.f('ix_bed_assignments_admission_id'), 'bed_assignments', ['admission_id'], unique=False)

    # Create bed_transfers table
    op.create_table(
        'bed_transfers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('from_bed_id', sa.Integer(), nullable=False),
        sa.Column('to_bed_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('transfer_notes', sa.Text(), nullable=True),
        sa.Column('transferred_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('transferred_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['from_bed_id'], ['beds.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['to_bed_id'], ['beds.id'], ),
        sa.ForeignKeyConstraint(['transferred_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bed_transfers_id'), 'bed_transfers', ['id'], unique=False)
    op.create_index(op.f('ix_bed_transfers_date'), 'bed_transfers', ['transferred_at'], unique=False)
    op.create_index(op.f('ix_bed_transfers_patient'), 'bed_transfers', ['patient_id'], unique=False)

    # Create bed_requests table
    op.create_table(
        'bed_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('requested_by_id', sa.Integer(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='routine'),
        sa.Column('requested_room_class', sa.String(length=10), nullable=True),
        sa.Column('requested_ward_id', sa.Integer(), nullable=True),
        sa.Column('gender_preference', sa.String(length=10), nullable=True),
        sa.Column('medical_requirements', sa.Text(), nullable=True),
        sa.Column('expected_admission_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'approved', 'assigned', 'cancelled', 'completed', name='bedrequeststatus'), nullable=False, server_default='pending'),
        sa.Column('assigned_bed_id', sa.Integer(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('assigned_by_id', sa.Integer(), nullable=True),
        sa.Column('approved_by_id', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_by_id', sa.Integer(), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assigned_bed_id'], ['beds.id'], ),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['assigned_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['cancelled_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['requested_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['requested_ward_id'], ['wards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bed_requests_id'), 'bed_requests', ['id'], unique=False)
    op.create_index(op.f('ix_bed_requests_patient'), 'bed_requests', ['patient_id'], unique=False)
    op.create_index(op.f('ix_bed_requests_priority'), 'bed_requests', ['priority'], unique=False)
    op.create_index(op.f('ix_bed_requests_status'), 'bed_requests', ['status'], unique=False)

    # Create room_status_history table
    op.create_table(
        'room_status_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('clean', 'soiled', 'maintenance', 'isolation', name='roomstatus'), nullable=False),
        sa.Column('previous_status', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('clean_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('maintenance_reason', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_room_status_history_id'), 'room_status_history', ['id'], unique=False)
    op.create_index(op.f('ix_room_status_history_date'), 'room_status_history', ['updated_at'], unique=False)
    op.create_index(op.f('ix_room_status_history_room'), 'room_status_history', ['room_id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_room_status_history_room'), table_name='room_status_history')
    op.drop_index(op.f('ix_room_status_history_date'), table_name='room_status_history')
    op.drop_index(op.f('ix_room_status_history_id'), table_name='room_status_history')
    op.drop_table('room_status_history')

    op.drop_index(op.f('ix_bed_requests_status'), table_name='bed_requests')
    op.drop_index(op.f('ix_bed_requests_priority'), table_name='bed_requests')
    op.drop_index(op.f('ix_bed_requests_patient'), table_name='bed_requests')
    op.drop_index(op.f('ix_bed_requests_id'), table_name='bed_requests')
    op.drop_table('bed_requests')

    op.drop_index(op.f('ix_bed_transfers_patient'), table_name='bed_transfers')
    op.drop_index(op.f('ix_bed_transfers_date'), table_name='bed_transfers')
    op.drop_index(op.f('ix_bed_transfers_id'), table_name='bed_transfers')
    op.drop_table('bed_transfers')

    op.drop_index(op.f('ix_bed_assignments_admission_id'), table_name='bed_assignments')
    op.drop_index(op.f('ix_bed_assignments_patient'), table_name='bed_assignments')
    op.drop_index(op.f('ix_bed_assignments_bed'), table_name='bed_assignments')
    op.drop_index(op.f('ix_bed_assignments_active'), table_name='bed_assignments')
    op.drop_index(op.f('ix_bed_assignments_id'), table_name='bed_assignments')
    op.drop_table('bed_assignments')

    op.drop_index(op.f('ix_beds_current_patient_id'), table_name='beds')
    op.drop_index(op.f('ix_beds_room_id'), table_name='beds')
    op.drop_index(op.f('ix_beds_ward_status'), table_name='beds')
    op.drop_index(op.f('ix_beds_status'), table_name='beds')
    op.drop_index(op.f('ix_beds_room_bed'), table_name='beds')
    op.drop_index(op.f('ix_beds_id'), table_name='beds')
    op.drop_table('beds')

    op.drop_index(op.f('ix_rooms_room_number'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_ward_id'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_ward_number'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_ward_class'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_id'), table_name='rooms')
    op.drop_table('rooms')

    # Drop enums
    sa.Enum(name='bedrequeststatus').drop(op.get_bind())
    sa.Enum(name='gendertype').drop(op.get_bind())
    sa.Enum(name='bedstatus').drop(op.get_bind())
    sa.Enum(name='roomstatus').drop(op.get_bind())
    sa.Enum(name='roomclass').drop(op.get_bind())
