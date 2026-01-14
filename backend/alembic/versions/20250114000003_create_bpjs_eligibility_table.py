"""create BPJS eligibility checks table

Revision ID: 006
Revises: 005
Create Date: 2025-01-14 17:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create bpjs_eligibility_checks table
    op.create_table(
        'bpjs_eligibility_checks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('search_type', sa.String(length=10), nullable=False),
        sa.Column('search_value', sa.String(length=20), nullable=False),
        sa.Column('is_eligible', sa.Boolean(), nullable=False),
        sa.Column('response_code', sa.String(length=10), nullable=True),
        sa.Column('response_message', sa.String(length=500), nullable=True),
        sa.Column('participant_info', postgresql.JSONB(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('verified_by', sa.Integer(), nullable=True),
        sa.Column('verification_method', sa.String(length=20), nullable=False),
        sa.Column('is_manual_override', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('override_reason', sa.Text(), nullable=True),
        sa.Column('override_approved_by', sa.Integer(), nullable=True),
        sa.Column('override_approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_cached', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('cache_hit', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('api_error', sa.Text(), nullable=True),
        sa.Column('api_error_code', sa.String(length=50), nullable=True),
        sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('last_retry_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['override_approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_bpjs_eligibility_checks_patient_id'), 'bpjs_eligibility_checks', ['patient_id'], unique=False)
    op.create_index(op.f('ix_bpjs_eligibility_checks_search_type'), 'bpjs_eligibility_checks', ['search_type'], unique=False)
    op.create_index(op.f('ix_bpjs_eligibility_checks_search_value'), 'bpjs_eligibility_checks', ['search_value'], unique=False)
    op.create_index(op.f('ix_bpjs_eligibility_checks_is_eligible'), 'bpjs_eligibility_checks', ['is_eligible'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_bpjs_eligibility_checks_is_eligible'), table_name='bpjs_eligibility_checks')
    op.drop_index(op.f('ix_bpjs_eligibility_checks_search_value'), table_name='bpjs_eligibility_checks')
    op.drop_index(op.f('ix_bpjs_eligibility_checks_search_type'), table_name='bpjs_eligibility_checks')
    op.drop_index(op.f('ix_bpjs_eligibility_checks_patient_id'), table_name='bpjs_eligibility_checks')

    # Drop table
    op.drop_table('bpjs_eligibility_checks')
