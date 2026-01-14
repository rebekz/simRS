"""create BPJS SEP tables for STORY-019

Revision ID: 20250114000007
Create Date: 2026-01-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '20250114000007'
down_revision: Union[str, None] = '20250114000006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '20250114000006'


def upgrade() -> None:
    # Create bpjs_sep table
    op.create_table(
        'bpjs_sep',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('encounter_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('sep_number', sa.String(length=50), nullable=True),
        sa.Column('sep_date', sa.Date(), nullable=False),
        sa.Column('service_type', sa.String(length=10), nullable=False),
        sa.Column('bpjs_card_number', sa.String(length=13), nullable=False),
        sa.Column('patient_name', sa.String(length=255), nullable=False),
        sa.Column('mrn', sa.String(length=50), nullable=True),
        sa.Column('ppk_code', sa.String(length=20), nullable=False),
        sa.Column('polyclinic_code', sa.String(length=20), nullable=True),
        sa.Column('treatment_class', sa.String(length=10), nullable=True),
        sa.Column('initial_diagnosis_code', sa.String(length=10), nullable=False),
        sa.Column('initial_diagnosis_name', sa.String(length=255), nullable=False),
        sa.Column('doctor_code', sa.String(length=20), nullable=True),
        sa.Column('doctor_name', sa.String(length=255), nullable=True),
        sa.Column('referral_number', sa.String(length=50), nullable=True),
        sa.Column('referral_ppk_code', sa.String(length=20), nullable=True),
        sa.Column('is_executive', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('cob_flag', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('patient_phone', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('bpjs_response', JSONB(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.Column('deletion_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bpjs_sep_id'), 'bpjs_sep', ['id'], unique=False)
    op.create_index(op.f('ix_bpjs_sep_encounter_id'), 'bpjs_sep', ['encounter_id'], unique=False)
    op.create_index(op.f('ix_bpjs_sep_patient_id'), 'bpjs_sep', ['patient_id'], unique=False)
    op.create_index(op.f('ix_bpjs_sep_sep_date'), 'bpjs_sep', ['sep_date'], unique=False)
    op.create_index(op.f('ix_bpjs_sep_sep_number'), 'bpjs_sep', ['sep_number'], unique=True)
    op.create_index(op.f('ix_bpjs_sep_status'), 'bpjs_sep', ['status'], unique=False)

    # Create bpjs_sep_history table
    op.create_table(
        'bpjs_sep_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sep_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('previous_status', sa.String(length=20), nullable=True),
        sa.Column('new_status', sa.String(length=20), nullable=True),
        sa.Column('previous_data', JSONB(), nullable=True),
        sa.Column('new_data', JSONB(), nullable=True),
        sa.Column('bpjs_request', JSONB(), nullable=True),
        sa.Column('bpjs_response', JSONB(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('changed_by', sa.Integer(), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['sep_id'], ['bpjs_sep.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bpjs_sep_history_sep_id'), 'bpjs_sep_history', ['sep_id'], unique=False)


def downgrade() -> None:
    # Drop bpjs_sep_history table
    op.drop_index(op.f('ix_bpjs_sep_history_sep_id'), table_name='bpjs_sep_history')
    op.drop_table('bpjs_sep_history')

    # Drop bpjs_sep table
    op.drop_index(op.f('ix_bpjs_sep_status'), table_name='bpjs_sep')
    op.drop_index(op.f('ix_bpjs_sep_sep_number'), table_name='bpjs_sep')
    op.drop_index(op.f('ix_bpjs_sep_sep_date'), table_name='bpjs_sep')
    op.drop_index(op.f('ix_bpjs_sep_patient_id'), table_name='bpjs_sep')
    op.drop_index(op.f('ix_bpjs_sep_encounter_id'), table_name='bpjs_sep')
    op.drop_index(op.f('ix_bpjs_sep_id'), table_name='bpjs_sep')
    op.drop_table('bpjs_sep')
