"""Create hospital configuration tables for STORY-039

Revision ID: 20250114000015
Revises: 20250114000014
Create Date: 2025-01-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = '20250114000015'
down_revision: Union[str, None] = '20250114000014'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '20250114000014'


def upgrade() -> None:
    # Create enums
    department_type_enum = ENUM(
        'ward', 'poli', 'unit', 'icu', 'er', 'or',
        name='departmenttype', create_type=True
    )
    department_type_enum.create(op.get_bind())

    staff_role_enum = ENUM(
        'doctor', 'nurse', 'midwife', 'pharmacist', 'lab_technician',
        'radiologist', 'administrator', 'receptionist', 'security', 'cleaning', 'other',
        name='staffrole', create_type=True
    )
    staff_role_enum.create(op.get_bind())

    doctor_specialization_enum = ENUM(
        'general_practitioner', 'internist', 'pediatrician', 'surgeon',
        'obstetrician', 'cardiologist', 'neurologist', 'orthopedist',
        'dermatologist', 'psychiatrist', 'ophthalmologist', 'ent_specialist',
        'urologist', 'anesthesiologist', 'radiologist', 'pathologist', 'other',
        name='doctorspecialization', create_type=True
    )
    doctor_specialization_enum.create(op.get_bind())

    shift_type_enum = ENUM(
        'morning', 'afternoon', 'night', 'flexible', 'on_call',
        name='shifttype', create_type=True
    )
    shift_type_enum.create(op.get_bind())

    # Create hospital_profiles table (singleton - only one row)
    op.create_table(
        'hospital_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('name_alias', sa.String(length=200), nullable=True),
        sa.Column('license_number', sa.String(length=100), nullable=False),
        sa.Column('address_line', sa.String(length=500), nullable=False),
        sa.Column('address_city', sa.String(length=100), nullable=False),
        sa.Column('address_province', sa.String(length=100), nullable=False),
        sa.Column('address_postal_code', sa.String(length=10), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False, server_default='Indonesia'),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('phone_alternate', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('bpjs_ppk_code', sa.String(length=20), nullable=False, unique=True),
        sa.Column('bpjs_pcare_code', sa.String(length=20), nullable=True),
        sa.Column('bpjs_antrian_code', sa.String(length=20), nullable=True),
        sa.Column('hospital_class', sa.String(length=10), nullable=True),
        sa.Column('hospital_type', sa.String(length=100), nullable=True),
        sa.Column('ownership', sa.String(length=100), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('letterhead_url', sa.String(length=500), nullable=True),
        sa.Column('total_departments', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_beds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_doctors', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_staff', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('license_number')
    )
    op.create_index(op.f('ix_hospital_profiles_id'), 'hospital_profiles', ['id'], unique=False)

    # Create departments table
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('department_type', sa.Enum('ward', 'poli', 'unit', 'icu', 'er', 'or', name='departmenttype'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_department_id', sa.Integer(), nullable=True),
        sa.Column('head_of_department_id', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('current_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('phone_extension', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospital_profiles.id'], ),
        sa.ForeignKeyConstraint(['parent_department_id'], ['departments.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_departments_id'), 'departments', ['id'], unique=False)
    op.create_index(op.f('ix_departments_code'), 'departments', ['code'], unique=False)
    op.create_index(op.f('ix_departments_hospital_id'), 'departments', ['hospital_id'], unique=False)
    op.create_index(op.f('ix_departments_department_type'), 'departments', ['department_type'], unique=False)
    op.create_index(op.f('ix_departments_parent_department_id'), 'departments', ['parent_department_id'], unique=False)

    # Create staff_profiles table
    op.create_table(
        'staff_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.String(length=50), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.Enum('doctor', 'nurse', 'midwife', 'pharmacist', 'lab_technician', 'radiologist', 'administrator', 'receptionist', 'security', 'cleaning', 'other', name='staffrole'), nullable=False),
        sa.Column('specialization', sa.Enum('general_practitioner', 'internist', 'pediatrician', 'surgeon', 'obstetrician', 'cardiologist', 'neurologist', 'orthopedist', 'dermatologist', 'psychiatrist', 'ophthalmologist', 'ent_specialist', 'urologist', 'anesthesiologist', 'radiologist', 'pathologist', 'other', name='doctorspecialization'), nullable=True),
        sa.Column('sip_number', sa.String(length=100), nullable=True),
        sa.Column('str_number', sa.String(length=100), nullable=True),
        sa.Column('license_expiry_date', sa.Date(), nullable=True),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('primary_department_id', sa.Integer(), nullable=True),
        sa.Column('employment_type', sa.String(length=50), nullable=True),
        sa.Column('employment_status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospital_profiles.id'], ),
        sa.ForeignKeyConstraint(['primary_department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_staff_profiles_id'), 'staff_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_staff_profiles_user_id'), 'staff_profiles', ['user_id'], unique=True)
    op.create_index(op.f('ix_staff_profiles_hospital_id'), 'staff_profiles', ['hospital_id'], unique=False)
    op.create_index(op.f('ix_staff_profiles_role'), 'staff_profiles', ['role'], unique=False)
    op.create_index(op.f('ix_staff_profiles_department_id'), 'staff_profiles', ['department_id'], unique=False)

    # Create shifts table
    op.create_table(
        'shifts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('shift_type', sa.Enum('morning', 'afternoon', 'night', 'flexible', 'on_call', name='shifttype'), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('break_duration_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shifts_id'), 'shifts', ['id'], unique=False)

    # Create shift_assignments table
    op.create_table(
        'shift_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('staff_id', sa.Integer(), nullable=False),
        sa.Column('shift_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['shift_id'], ['shifts.id'], ),
        sa.ForeignKeyConstraint(['staff_id'], ['staff_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shift_assignments_id'), 'shift_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_shift_assignments_staff_id'), 'shift_assignments', ['staff_id'], unique=False)
    op.create_index(op.f('ix_shift_assignments_shift_id'), 'shift_assignments', ['shift_id'], unique=False)

    # Create working_hours table
    op.create_table(
        'working_hours',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('is_working_day', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('opening_time', sa.Time(), nullable=True),
        sa.Column('closing_time', sa.Time(), nullable=True),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_working_hours_id'), 'working_hours', ['id'], unique=False)

    # Create branding_configs table
    op.create_table(
        'branding_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False),
        sa.Column('primary_color', sa.String(length=7), nullable=False, server_default='#0ea5e9'),
        sa.Column('secondary_color', sa.String(length=7), nullable=False, server_default='#06b6d4'),
        sa.Column('accent_color', sa.String(length=7), nullable=False, server_default='#f97316'),
        sa.Column('text_color', sa.String(length=7), nullable=False, server_default='#1f2937'),
        sa.Column('background_color', sa.String(length=7), nullable=False, server_default='#ffffff'),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('letterhead_url', sa.String(length=500), nullable=True),
        sa.Column('favicon_url', sa.String(length=500), nullable=True),
        sa.Column('custom_css', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospital_profiles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hospital_id')
    )
    op.create_index(op.f('ix_branding_configs_id'), 'branding_configs', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_branding_configs_id'), table_name='branding_configs')
    op.drop_table('branding_configs')

    op.drop_index(op.f('ix_working_hours_id'), table_name='working_hours')
    op.drop_table('working_hours')

    op.drop_index(op.f('ix_shift_assignments_shift_id'), table_name='shift_assignments')
    op.drop_index(op.f('ix_shift_assignments_staff_id'), table_name='shift_assignments')
    op.drop_index(op.f('ix_shift_assignments_id'), table_name='shift_assignments')
    op.drop_table('shift_assignments')

    op.drop_index(op.f('ix_shifts_id'), table_name='shifts')
    op.drop_table('shifts')

    op.drop_index(op.f('ix_staff_profiles_department_id'), table_name='staff_profiles')
    op.drop_index(op.f('ix_staff_profiles_role'), table_name='staff_profiles')
    op.drop_index(op.f('ix_staff_profiles_hospital_id'), table_name='staff_profiles')
    op.drop_index(op.f('ix_staff_profiles_user_id'), table_name='staff_profiles')
    op.drop_index(op.f('ix_staff_profiles_id'), table_name='staff_profiles')
    op.drop_table('staff_profiles')

    op.drop_index(op.f('ix_departments_parent_department_id'), table_name='departments')
    op.drop_index(op.f('ix_departments_department_type'), table_name='departments')
    op.drop_index(op.f('ix_departments_hospital_id'), table_name='departments')
    op.drop_index(op.f('ix_departments_code'), table_name='departments')
    op.drop_index(op.f('ix_departments_id'), table_name='departments')
    op.drop_table('departments')

    op.drop_index(op.f('ix_hospital_profiles_id'), table_name='hospital_profiles')
    op.drop_table('hospital_profiles')

    # Drop enums
    sa.Enum(name='shifttype').drop(op.get_bind())
    sa.Enum(name='doctorspecialization').drop(op.get_bind())
    sa.Enum(name='staffrole').drop(op.get_bind())
    sa.Enum(name='departmenttype').drop(op.get_bind())
