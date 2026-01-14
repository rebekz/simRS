"""Create patient tables for STORY-006: New Patient Registration

Revision ID: 004
Revises: 003
Create Date: 2025-01-14

This migration creates the patients, emergency_contacts, and patient_insurances tables
to support patient registration and management functionality.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('medical_record_number', sa.String(length=20), nullable=False, comment='No. RM - Medical Record Number'),
        sa.Column('nik', sa.String(length=16), nullable=True, comment='Indonesian National ID Number'),
        sa.Column('full_name', sa.String(length=255), nullable=False, comment='Patient full name'),
        sa.Column('date_of_birth', sa.Date(), nullable=False, comment='Patient date of birth'),
        sa.Column('gender', sa.Enum('male', 'female', name='gender'), nullable=False, comment='Patient gender'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='Primary phone number'),
        sa.Column('email', sa.String(length=255), nullable=True, comment='Email address'),
        sa.Column('address', sa.Text(), nullable=True, comment='Residential address'),
        sa.Column('city', sa.String(length=100), nullable=True, comment='City of residence'),
        sa.Column('province', sa.String(length=100), nullable=True, comment='Province of residence'),
        sa.Column('postal_code', sa.String(length=10), nullable=True, comment='Postal code'),
        sa.Column('blood_type', sa.Enum('A', 'B', 'AB', 'O', 'none', name='bloodtype'), nullable=True, comment='Blood type'),
        sa.Column('marital_status', sa.Enum('single', 'married', 'widowed', 'divorced', name='maritalstatus'), nullable=True, comment='Marital status'),
        sa.Column('religion', sa.String(length=50), nullable=True, comment='Religion'),
        sa.Column('occupation', sa.String(length=100), nullable=True, comment='Occupation'),
        sa.Column('photo_url', sa.String(length=500), nullable=True, comment='URL to patient photo'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Patient active status'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record last update timestamp'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('medical_record_number', name='uq_patients_medical_record_number'),
        sa.UniqueConstraint('nik', name='uq_patients_nik')
    )
    op.create_index(op.f('ix_patients_id'), 'patients', ['id'], unique=False)
    op.create_index(op.f('ix_patients_medical_record_number'), 'patients', ['medical_record_number'], unique=True)
    op.create_index(op.f('ix_patients_nik'), 'patients', ['nik'], unique=True)
    op.create_index(op.f('ix_patients_date_of_birth'), 'patients', ['date_of_birth'], unique=False)
    op.create_index(op.f('ix_patients_phone'), 'patients', ['phone'], unique=False)

    # Create emergency_contacts table
    op.create_table(
        'emergency_contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False, comment='Reference to patient'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Emergency contact full name'),
        sa.Column('relationship', sa.String(length=100), nullable=False, comment='Relationship to patient'),
        sa.Column('phone', sa.String(length=20), nullable=False, comment='Emergency contact phone number'),
        sa.Column('address', sa.Text(), nullable=True, comment='Emergency contact address'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record last update timestamp'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_emergency_contacts_id'), 'emergency_contacts', ['id'], unique=False)
    op.create_index(op.f('ix_emergency_contacts_patient_id'), 'emergency_contacts', ['patient_id'], unique=False)

    # Create patient_insurances table
    op.create_table(
        'patient_insurances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False, comment='Reference to patient'),
        sa.Column('insurance_type', sa.Enum('bpjs', 'asuransi', 'umum', name='insurancetype'), nullable=False, comment='Type of insurance'),
        sa.Column('insurance_number', sa.String(length=100), nullable=True, comment='Insurance policy/member number'),
        sa.Column('member_name', sa.String(length=255), nullable=True, comment='Insurance member name'),
        sa.Column('expiry_date', sa.Date(), nullable=True, comment='Insurance policy expiry date'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record last update timestamp'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patient_insurances_id'), 'patient_insurances', ['id'], unique=False)
    op.create_index(op.f('ix_patient_insurances_patient_id'), 'patient_insurances', ['patient_id'], unique=False)


def downgrade() -> None:
    # Drop patient_insurances table
    op.drop_index(op.f('ix_patient_insurances_patient_id'), table_name='patient_insurances')
    op.drop_index(op.f('ix_patient_insurances_id'), table_name='patient_insurances')
    op.drop_table('patient_insurances')

    # Drop emergency_contacts table
    op.drop_index(op.f('ix_emergency_contacts_patient_id'), table_name='emergency_contacts')
    op.drop_index(op.f('ix_emergency_contacts_id'), table_name='emergency_contacts')
    op.drop_table('emergency_contacts')

    # Drop patients table
    op.drop_index(op.f('ix_patients_phone'), table_name='patients')
    op.drop_index(op.f('ix_patients_date_of_birth'), table_name='patients')
    op.drop_index(op.f('ix_patients_nik'), table_name='patients')
    op.drop_index(op.f('ix_patients_medical_record_number'), table_name='patients')
    op.drop_index(op.f('ix_patients_id'), table_name='patients')
    op.drop_table('patients')

    # Drop enum types (PostgreSQL specific)
    op.execute('DROP TYPE IF EXISTS insurancetype')
    op.execute('DROP TYPE IF EXISTS maritalstatus')
    op.execute('DROP TYPE IF EXISTS bloodtype')
    op.execute('DROP TYPE IF EXISTS gender')
