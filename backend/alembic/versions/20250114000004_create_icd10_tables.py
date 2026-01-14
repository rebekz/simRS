"""create ICD-10 codes and problem list tables for STORY-012

Revision ID: 007
Revises: 006
Create Date: 2025-01-14 18:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create icd10_codes table
    op.create_table(
        'icd10_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('code_full', sa.String(length=20), nullable=False),
        sa.Column('chapter', sa.String(length=10), nullable=False),
        sa.Column('block', sa.String(length=10), nullable=False),
        sa.Column('description_indonesian', sa.Text(), nullable=False),
        sa.Column('description_english', sa.Text(), nullable=True),
        sa.Column('is_chapter', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_block', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_category', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=True),
        sa.Column('inclusion_terms', postgresql.JSONB(), nullable=True),
        sa.Column('exclusion_terms', postgresql.JSONB(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('usage_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_common', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.String(length=50), nullable=False),
        sa.Column('updated_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for icd10_codes
    op.create_index(op.f('ix_icd10_codes_code'), 'icd10_codes', ['code'], unique=True)
    op.create_index(op.f('ix_icd10_codes_chapter'), 'icd10_codes', ['chapter'], unique=False)
    op.create_index(op.f('ix_icd10_codes_block'), 'icd10_codes', ['block'], unique=False)
    op.create_index(op.f('ix_icd10_codes_is_common'), 'icd10_codes', ['is_common'], unique=False)

    # Create GIN index for full-text search on descriptions
    op.execute('CREATE INDEX ix_icd10_codes_description_gin ON icd10_codes USING gin(to_tsvector(\'indonesian\', description_indonesian))')

    # Create problem_list table
    op.create_table(
        'problem_list',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('encounter_id', sa.Integer(), nullable=True),
        sa.Column('icd10_code_id', sa.Integer(), nullable=False),
        sa.Column('icd10_code', sa.String(length=10), nullable=False),
        sa.Column('problem_name', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', postgresql.PROBLEM_STATUS(name='problem_status'), nullable=False, server_default='active'),
        sa.Column('onset_date', sa.Date(), nullable=True),
        sa.Column('resolved_date', sa.Date(), nullable=True),
        sa.Column('is_chronic', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=True),
        sa.Column('diagnosed_by', sa.Integer(), nullable=True),
        sa.Column('recorded_by', sa.Integer(), nullable=False),
        sa.Column('facility', sa.String(length=100), nullable=True),
        sa.Column('clinical_notes', sa.Text(), nullable=True),
        sa.Column('treatment_plan', sa.Text(), nullable=True),
        sa.Column('follow_up_required', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('follow_up_date', sa.Date(), nullable=True),
        sa.Column('certainty', sa.String(length=20), nullable=True),
        sa.Column('chronicity_indicators', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['diagnosed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
        sa.ForeignKeyConstraint(['icd10_code_id'], ['icd10_codes.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['recorded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for problem_list
    op.create_index(op.f('ix_problem_list_patient_id'), 'problem_list', ['patient_id'], unique=False)
    op.create_index(op.f('ix_problem_list_encounter_id'), 'problem_list', ['encounter_id'], unique=False)
    op.create_index(op.f('ix_problem_list_icd10_code_id'), 'problem_list', ['icd10_code_id'], unique=False)
    op.create_index(op.f('ix_problem_list_icd10_code'), 'problem_list', ['icd10_code'], unique=False)
    op.create_index(op.f('ix_problem_list_status'), 'problem_list', ['status'], unique=False)
    op.create_index(op.f('ix_problem_list_is_chronic'), 'problem_list', ['is_chronic'], unique=False)

    # Create icd10_user_favorites table
    op.create_table(
        'icd10_user_favorites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('icd10_code_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['icd10_code_id'], ['icd10_codes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for icd10_user_favorites
    op.create_index(op.f('ix_icd10_user_favorites_user_id'), 'icd10_user_favorites', ['user_id'], unique=False)
    op.create_index(op.f('ix_icd10_user_favorites_icd10_code_id'), 'icd10_user_favorites', ['icd10_code_id'], unique=False)

    # Create unique constraint for user favorites (prevent duplicates)
    op.create_unique_constraint('uq_user_icd10_favorite', 'icd10_user_favorites', ['user_id', 'icd10_code_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_constraint('uq_user_icd10_favorite', 'icd10_user_favorites')
    op.drop_index(op.f('ix_icd10_user_favorites_icd10_code_id'), table_name='icd10_user_favorites')
    op.drop_index(op.f('ix_icd10_user_favorites_user_id'), table_name='icd10_user_favorites')
    op.drop_table('icd10_user_favorites')

    op.drop_index(op.f('ix_problem_list_is_chronic'), table_name='problem_list')
    op.drop_index(op.f('ix_problem_list_status'), table_name='problem_list')
    op.drop_index(op.f('ix_problem_list_icd10_code'), table_name='problem_list')
    op.drop_index(op.f('ix_problem_list_icd10_code_id'), table_name='problem_list')
    op.drop_index(op.f('ix_problem_list_encounter_id'), table_name='problem_list')
    op.drop_index(op.f('ix_problem_list_patient_id'), table_name='problem_list')
    op.drop_table('problem_list')

    op.execute('DROP INDEX IF EXISTS ix_icd10_codes_description_gin')
    op.drop_index(op.f('ix_icd10_codes_is_common'), table_name='icd10_codes')
    op.drop_index(op.f('ix_icd10_codes_block'), table_name='icd10_codes')
    op.drop_index(op.f('ix_icd10_codes_chapter'), table_name='icd10_codes')
    op.drop_index(op.f('ix_icd10_codes_code'), table_name='icd10_codes')
    op.drop_table('icd10_codes')
