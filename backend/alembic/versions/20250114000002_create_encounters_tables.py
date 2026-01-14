"""Create encounters, diagnoses, and treatments tables for STORY-011

Revision ID: 005
Revises: 004
Create Date: 2026-01-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create encounters table
    op.create_table(
        'encounters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('encounter_type', sa.String(50), nullable=False),
        sa.Column('encounter_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('doctor_id', sa.Integer(), nullable=True),
        sa.Column('chief_complaint', sa.Text(), nullable=True),
        sa.Column('present_illness', sa.Text(), nullable=True),
        sa.Column('physical_examination', sa.Text(), nullable=True),
        sa.Column('vital_signs', postgresql.JSONB(), nullable=True),
        sa.Column('status', sa.String(20), server_default='active', nullable=False),
        sa.Column('is_urgent', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('bpjs_sep_number', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], name='fk_encounters_doctor'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], name='fk_encounters_patient'),
        sa.PrimaryKeyConstraint('id', name='pk_encounters')
    )
    op.create_index('ix_encounters_patient_id', 'encounters', ['patient_id'])
    op.create_index('ix_encounters_encounter_date', 'encounters', ['encounter_date'])
    op.create_index('ix_encounters_status', 'encounters', ['status'])
    op.create_index('ix_encounters_doctor_id', 'encounters', ['doctor_id'])
    op.create_index('ix_encounters_department', 'encounters', ['department'])

    # Create diagnoses table
    op.create_table(
        'diagnoses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('encounter_id', sa.Integer(), nullable=False),
        sa.Column('icd_10_code', sa.String(10), nullable=False),
        sa.Column('diagnosis_name', sa.String(500), nullable=False),
        sa.Column('diagnosis_type', sa.String(20), server_default='primary', nullable=False),
        sa.Column('is_chronic', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ondelete='CASCADE', name='fk_diagnoses_encounter'),
        sa.PrimaryKeyConstraint('id', name='pk_diagnoses')
    )
    op.create_index('ix_diagnoses_encounter_id', 'diagnoses', ['encounter_id'])
    op.create_index('ix_diagnoses_icd_10_code', 'diagnoses', ['icd_10_code'])
    op.create_index('ix_diagnoses_diagnosis_type', 'diagnoses', ['diagnosis_type'])

    # Create treatments table
    op.create_table(
        'treatments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('encounter_id', sa.Integer(), nullable=False),
        sa.Column('treatment_type', sa.String(50), nullable=False),
        sa.Column('treatment_name', sa.String(500), nullable=False),
        sa.Column('dosage', sa.String(100), nullable=True),
        sa.Column('frequency', sa.String(100), nullable=True),
        sa.Column('duration', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ondelete='CASCADE', name='fk_treatments_encounter'),
        sa.PrimaryKeyConstraint('id', name='pk_treatments')
    )
    op.create_index('ix_treatments_encounter_id', 'treatments', ['encounter_id'])
    op.create_index('ix_treatments_treatment_type', 'treatments', ['treatment_type'])
    op.create_index('ix_treatments_is_active', 'treatments', ['is_active'])


def downgrade() -> None:
    op.drop_table('treatments')
    op.drop_table('diagnoses')
    op.drop_table('encounters')
