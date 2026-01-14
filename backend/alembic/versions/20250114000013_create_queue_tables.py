"""Create queue management tables for STORY-010

Revision ID: 20250114000013
Revises: 20250114000012
Create Date: 2025-01-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, ENUM


# revision identifiers, used by Alembic.
revision: str = '20250114000013'
down_revision: Union[str, None] = '20250114000012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '20250114000012'


def upgrade() -> None:
    # Create enums
    queue_department_enum = ENUM(
        'poli', 'farmasi', 'lab', 'radiologi', 'kasir',
        name='queuedepartment', create_type=True
    )
    queue_department_enum.create(op.get_bind())

    queue_status_enum = ENUM(
        'waiting', 'called', 'served', 'skipped', 'cancelled',
        name='queuestatus', create_type=True
    )
    queue_status_enum.create(op.get_bind())

    queue_priority_enum = ENUM(
        'normal', 'priority', 'emergency',
        name='queuepriority', create_type=True
    )
    queue_priority_enum.create(op.get_bind())

    # Create queue_tickets table
    op.create_table(
        'queue_tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_number', sa.String(length=20), unique=True, nullable=False),
        sa.Column('department', sa.Enum('poli', 'farmasi', 'lab', 'radiologi', 'kasir', name='queuedepartment'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('priority', sa.Enum('normal', 'priority', 'emergency', name='queuepriority'), nullable=False),
        sa.Column('status', sa.Enum('waiting', 'called', 'served', 'skipped', 'cancelled', name='queuestatus'), nullable=False),
        sa.Column('poli_id', sa.Integer(), nullable=True),
        sa.Column('doctor_id', sa.Integer(), nullable=True),
        sa.Column('appointment_id', sa.Integer(), nullable=True),
        sa.Column('queue_position', sa.Integer(), nullable=True),
        sa.Column('people_ahead', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('serving_counter', sa.Integer(), nullable=True),
        sa.Column('service_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('service_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_wait_minutes', sa.Integer(), nullable=True),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('called_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('served_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['poli_id'], ['polis.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_queue_tickets_date'), 'queue_tickets', ['date'], unique=False)
    op.create_index(op.f('ix_queue_tickets_department'), 'queue_tickets', ['department'], unique=False)
    op.create_index(op.f('ix_queue_tickets_doctor_id'), 'queue_tickets', ['doctor_id'], unique=False)
    op.create_index(op.f('ix_queue_tickets_patient_id'), 'queue_tickets', ['patient_id'], unique=False)
    op.create_index(op.f('ix_queue_tickets_poli_id'), 'queue_tickets', ['poli_id'], unique=False)
    op.create_index(op.f('ix_queue_tickets_priority'), 'queue_tickets', ['priority'], unique=False)
    op.create_index(op.f('ix_queue_tickets_status'), 'queue_tickets', ['status'], unique=False)
    op.create_index(op.f('ix_queue_tickets_ticket_number'), 'queue_tickets', ['ticket_number'], unique=True)

    # Create queue_recalls table
    op.create_table(
        'queue_recalls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('counter', sa.Integer(), nullable=False),
        sa.Column('announced', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('recall_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('called_by_id', sa.Integer(), nullable=False),
        sa.Column('patient_present', sa.Boolean(), nullable=True),
        sa.Column('no_show_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['called_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['ticket_id'], ['queue_tickets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_queue_recalls_ticket_id'), 'queue_recalls', ['ticket_id'], unique=False)

    # Create queue_notifications table
    op.create_table(
        'queue_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('notification_type', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('delivery_status', sa.String(length=50), nullable=True),
        sa.Column('delivery_receipt_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['queue_tickets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_queue_notifications_ticket_id'), 'queue_notifications', ['ticket_id'], unique=False)

    # Create queue_statistics_cache table
    op.create_table(
        'queue_statistics_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('department', sa.Enum('poli', 'farmasi', 'lab', 'radiologi', 'kasir', name='queuedepartment'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total_issued', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_served', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_waiting', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_skipped', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_cancelled', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_wait_time_minutes', sa.Float(), nullable=True),
        sa.Column('average_service_time_minutes', sa.Float(), nullable=True),
        sa.Column('normal_served', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('priority_served', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('emergency_served', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('hourly_distribution', JSON(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('department', 'date')
    )

    # Create queue_settings table
    op.create_table(
        'queue_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('department', sa.Enum('poli', 'farmasi', 'lab', 'radiologi', 'kasir', name='queuedepartment'), unique=True, nullable=False),
        sa.Column('max_concurrent', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('counters', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('average_service_time_minutes', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('enable_sms', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('enable_whatsapp', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sms_on_issue', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sms_on_call', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sms_on_reminder', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('enable_display', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('display_refresh_interval_seconds', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('show_bpjs', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('show_doctor_name', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('show_counter', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('priority_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('priority_categories', JSON(), nullable=True),
        sa.Column('enable_offline', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('offline_sync_interval_minutes', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create queue_transfers table
    op.create_table(
        'queue_transfers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('from_department', sa.Enum('poli', 'farmasi', 'lab', 'radiologi', 'kasir', name='queuedepartment'), nullable=False),
        sa.Column('to_department', sa.Enum('poli', 'farmasi', 'lab', 'radiologi', 'kasir', name='queuedepartment'), nullable=False),
        sa.Column('from_poli_id', sa.Integer(), nullable=True),
        sa.Column('to_poli_id', sa.Integer(), nullable=True),
        sa.Column('from_doctor_id', sa.Integer(), nullable=True),
        sa.Column('to_doctor_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('transferred_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['from_doctor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['ticket_id'], ['queue_tickets.id'], ),
        sa.ForeignKeyConstraint(['to_doctor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['transferred_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables
    op.drop_table('queue_transfers')
    op.drop_table('queue_settings')
    op.drop_table('queue_statistics_cache')
    op.drop_index(op.f('ix_queue_notifications_ticket_id'), table_name='queue_notifications')
    op.drop_table('queue_notifications')
    op.drop_index(op.f('ix_queue_recalls_ticket_id'), table_name='queue_recalls')
    op.drop_table('queue_recalls')
    op.drop_index(op.f('ix_queue_tickets_ticket_number'), table_name='queue_tickets')
    op.drop_index(op.f('ix_queue_tickets_status'), table_name='queue_tickets')
    op.drop_index(op.f('ix_queue_tickets_priority'), table_name='queue_tickets')
    op.drop_index(op.f('ix_queue_tickets_poli_id'), table_name='queue_tickets')
    op.drop_index(op.f('ix_queue_tickets_patient_id'), table_name='queue_tickets')
    op.drop_index(op.f('ix_queue_tickets_doctor_id'), table_name='queue_tickets')
    op.drop_index(op.f('ix_queue_tickets_department'), table_name='queue_tickets')
    op.drop_index(op.f('ix_queue_tickets_date'), table_name='queue_tickets')
    op.drop_table('queue_tickets')

    # Drop enums
    sa.Enum(name='queuepriority').drop(op.get_bind())
    sa.Enum(name='queuestatus').drop(op.get_bind())
    sa.Enum(name='queuedepartment').drop(op.get_bind())
