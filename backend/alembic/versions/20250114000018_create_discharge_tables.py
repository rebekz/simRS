"""Create discharge planning tables for STORY-023

Revision ID: 20250114000018
Revises: 20250114000017
Create Date: 2025-01-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = '20250114000018'
down_revision: Union[str, None] = '20250114000017'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '20250114000017'


def upgrade() -> None:
    # Create enums
    discharge_status_enum = ENUM(
        'planned', 'ready', 'pending', 'discharged',
        name='dischargestatus', create_type=True
    )
    discharge_status_enum.create(op.get_bind())

    discharge_destination_enum = ENUM(
        'home', 'transfer', 'facility', 'left_against_advice', 'deceased',
        name='dischargedestination', create_type=True
    )
    discharge_destination_enum.create(op.get_bind())

    discharge_condition_enum = ENUM(
        'improved', 'stable', 'unchanged', 'worsened',
        name='dischargecondition', create_type=True
    )
    discharge_condition_enum.create(op.get_bind())

    follow_up_type_enum = ENUM(
        'outpatient', 'telephone', 'video', 'home_visit',
        name='followuptype', create_type=True
    )
    follow_up_type_enum.create(op.get_bind())

    # Create discharge_readiness table
    op.create_table(
        'discharge_readiness',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('assessed_by_id', sa.Integer(), nullable=False),
        sa.Column('criteria', sa.JSON(), nullable=False),
        sa.Column('is_ready', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('readiness_score', sa.Float(), nullable=False),
        sa.Column('barriers_to_discharge', sa.JSON(), nullable=True),
        sa.Column('required_actions', sa.JSON(), nullable=True),
        sa.Column('estimated_discharge_date', sa.Date(), nullable=True),
        sa.Column('assessed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['assessed_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discharge_readiness_id'), 'discharge_readiness', ['id'], unique=False)
    op.create_index(op.f('ix_discharge_readiness_admission_id'), 'discharge_readiness', ['admission_id'], unique=False)

    # Create discharge_orders table
    op.create_table(
        'discharge_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('physician_id', sa.Integer(), nullable=False),
        sa.Column('discharge_status', sa.Enum('planned', 'ready', 'pending', 'discharged', name='dischargestatus'), nullable=False),
        sa.Column('discharge_destination', sa.Enum('home', 'transfer', 'facility', 'left_against_advice', 'deceased', name='dischargedestination'), nullable=False),
        sa.Column('discharge_condition', sa.Enum('improved', 'stable', 'unchanged', 'worsened', name='dischargecondition'), nullable=False),
        sa.Column('discharge_medications', sa.JSON(), nullable=False),
        sa.Column('discharge_instructions', sa.JSON(), nullable=False),
        sa.Column('activity_restrictions', sa.JSON(), nullable=True),
        sa.Column('diet_instructions', sa.Text(), nullable=True),
        sa.Column('wound_care_instructions', sa.Text(), nullable=True),
        sa.Column('follow_up_appointments', sa.JSON(), nullable=True),
        sa.Column('medical_equipment', sa.JSON(), nullable=True),
        sa.Column('transportation_arranged', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('transportation_type', sa.String(length=50), nullable=True),
        sa.Column('responsible_adult_name', sa.String(length=200), nullable=True),
        sa.Column('responsible_adult_relationship', sa.String(length=100), nullable=True),
        sa.Column('responsible_adult_contact', sa.String(length=50), nullable=True),
        sa.Column('special_needs', sa.JSON(), nullable=True),
        sa.Column('ordered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('estimated_discharge_date', sa.Date(), nullable=True),
        sa.Column('actual_discharge_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('physician_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['physician_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discharge_orders_id'), 'discharge_orders', ['id'], unique=False)
    op.create_index(op.f('ix_discharge_orders_admission_id'), 'discharge_orders', ['admission_id'], unique=False)

    # Create discharge_summaries table
    op.create_table(
        'discharge_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('patient_name', sa.String(length=200), nullable=False),
        sa.Column('mrn', sa.String(length=50), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('gender', sa.String(length=20), nullable=False),
        sa.Column('admission_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('discharge_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('length_of_stay_days', sa.Integer(), nullable=False),
        sa.Column('admission_diagnosis', sa.Text(), nullable=False),
        sa.Column('discharge_diagnosis', sa.Text(), nullable=False),
        sa.Column('secondary_diagnoses', sa.JSON(), nullable=True),
        sa.Column('procedures_performed', sa.JSON(), nullable=True),
        sa.Column('course_of_illness', sa.Text(), nullable=True),
        sa.Column('treatments_given', sa.JSON(), nullable=False),
        sa.Column('medications_administered', sa.JSON(), nullable=False),
        sa.Column('complications', sa.JSON(), nullable=True),
        sa.Column('discharge_condition', sa.Enum('improved', 'stable', 'unchanged', 'worsened', name='dischargecondition'), nullable=False),
        sa.Column('discharge_medications', sa.JSON(), nullable=False),
        sa.Column('discharge_instructions', sa.JSON(), nullable=False),
        sa.Column('follow_up_appointments', sa.JSON(), nullable=True),
        sa.Column('attending_physician', sa.String(length=200), nullable=False),
        sa.Column('generated_by_id', sa.Integer(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('export_format', sa.String(length=10), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['generated_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('admission_id')
    )

    # Create medication_reconciliations table
    op.create_table(
        'medication_reconciliations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('pharmacist_id', sa.Integer(), nullable=False),
        sa.Column('physician_id', sa.Integer(), nullable=False),
        sa.Column('reconciliation_date', sa.Date(), nullable=False),
        sa.Column('medications_to_continue', sa.JSON(), nullable=False),
        sa.Column('medications_to_discontinue', sa.JSON(), nullable=False),
        sa.Column('medications_to_change', sa.JSON(), nullable=False),
        sa.Column('new_medications', sa.JSON(), nullable=False),
        sa.Column('reconciliation_notes', sa.Text(), nullable=True),
        sa.Column('pharmacist_notes', sa.Text(), nullable=True),
        sa.Column('verified_by_physician', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['pharmacist_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['physician_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create follow_up_appointments table
    op.create_table(
        'follow_up_appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_by_id', sa.Integer(), nullable=False),
        sa.Column('appointment_type', sa.Enum('outpatient', 'telephone', 'video', 'home_visit', name='followuptype'), nullable=False),
        sa.Column('specialty', sa.String(length=100), nullable=False),
        sa.Column('physician_name', sa.String(length=200), nullable=True),
        sa.Column('appointment_date', sa.Date(), nullable=False),
        sa.Column('appointment_time', sa.String(length=10), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('contact_number', sa.String(length=50), nullable=True),
        sa.Column('video_link', sa.String(length=500), nullable=True),
        sa.Column('purpose', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='routine'),
        sa.Column('send_reminder', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('reminder_method', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('confirmed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['scheduled_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_follow_up_appointments_id'), 'follow_up_appointments', ['id'], unique=False)
    op.create_index(op.f('ix_follow_up_appointments_admission_id'), 'follow_up_appointments', ['admission_id'], unique=False)
    op.create_index(op.f('ix_follow_up_appointments_appointment_date'), 'follow_up_appointments', ['appointment_date'], unique=False)

    # Create bpjs_claim_finalizations table
    op.create_table(
        'bpjs_claim_finalizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('sep_number', sa.String(length=50), nullable=False),
        sa.Column('final_diagnosis', sa.Text(), nullable=False),
        sa.Column('procedure_codes', sa.JSON(), nullable=True),
        sa.Column('icd_10_codes', sa.JSON(), nullable=False),
        sa.Column('admission_type', sa.String(length=50), nullable=False),
        sa.Column('class_type', sa.String(length=20), nullable=False),
        sa.Column('bed_type', sa.String(length=50), nullable=False),
        sa.Column('room_number', sa.String(length=50), nullable=False),
        sa.Column('admission_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('discharge_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('length_of_stay_days', sa.Integer(), nullable=False),
        sa.Column('doctor_visit_count', sa.Integer(), nullable=False),
        sa.Column('doctor_visit_fees', sa.Float(), nullable=True),
        sa.Column('consultation_fees', sa.Float(), nullable=True),
        sa.Column('procedure_fees', sa.Float(), nullable=True),
        sa.Column('room_charges', sa.Float(), nullable=True),
        sa.Column('medication_charges', sa.Float(), nullable=True),
        sa.Column('laboratory_charges', sa.Float(), nullable=True),
        sa.Column('radiology_charges', sa.Float(), nullable=True),
        sa.Column('other_charges', sa.Float(), nullable=True),
        sa.Column('total_claim_amount', sa.Float(), nullable=False),
        sa.Column('validated_by', sa.Integer(), nullable=False),
        sa.Column('validated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('validation_notes', sa.Text(), nullable=True),
        sa.Column('submitted_to_bpjs', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('claim_submission_number', sa.String(length=100), nullable=True),
        sa.Column('claim_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['validated_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('admission_id'),
        sa.UniqueConstraint('sep_number')
    )

    # Create sep_closures table
    op.create_table(
        'sep_closures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('sep_number', sa.String(length=50), nullable=False),
        sa.Column('closure_reason', sa.String(length=50), nullable=False),
        sa.Column('discharge_status', sa.Enum('planned', 'ready', 'pending', 'discharged', name='dischargestatus'), nullable=False),
        sa.Column('discharge_condition', sa.Enum('improved', 'stable', 'unchanged', 'worsened', name='dischargecondition'), nullable=False),
        sa.Column('final_diagnosis', sa.Text(), nullable=False),
        sa.Column('icd_10_code', sa.String(length=20), nullable=False),
        sa.Column('discharge_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('length_of_stay_days', sa.Integer(), nullable=False),
        sa.Column('patient_outcome', sa.String(length=50), nullable=False),
        sa.Column('follow_up_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('follow_up_instructions', sa.Text(), nullable=True),
        sa.Column('closed_by_id', sa.Integer(), nullable=False),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sep_updated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sep_update_response', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['closed_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('admission_id'),
        sa.UniqueConstraint('sep_number')
    )

    # Create patient_discharge_instructions table
    op.create_table(
        'patient_discharge_instructions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('diagnoses', sa.JSON(), nullable=False),
        sa.Column('treatments_received', sa.JSON(), nullable=False),
        sa.Column('medications', sa.JSON(), nullable=False),
        sa.Column('activity_instructions', sa.JSON(), nullable=False),
        sa.Column('diet_instructions', sa.JSON(), nullable=False),
        sa.Column('wound_care_instructions', sa.JSON(), nullable=True),
        sa.Column('warning_signs', sa.JSON(), nullable=False),
        sa.Column('emergency_care_instructions', sa.JSON(), nullable=False),
        sa.Column('follow_up_appointments', sa.JSON(), nullable=False),
        sa.Column('emergency_contact', sa.String(length=200), nullable=False),
        sa.Column('hospital_contact', sa.String(length=200), nullable=False),
        sa.Column('generated_by_id', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='id'),
        sa.Column('delivery_method', sa.String(length=20), nullable=False, server_default='printed'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['generated_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('admission_id')
    )

    # Create discharge_checklists table
    op.create_table(
        'discharge_checklists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('clinical_criteria', sa.JSON(), nullable=False),
        sa.Column('medication_criteria', sa.JSON(), nullable=False),
        sa.Column('documentation_criteria', sa.JSON(), nullable=False),
        sa.Column('logistics_criteria', sa.JSON(), nullable=False),
        sa.Column('education_criteria', sa.JSON(), nullable=False),
        sa.Column('follow_up_criteria', sa.JSON(), nullable=False),
        sa.Column('all_criteria_met', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verified_by_id', sa.Integer(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['verified_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('admission_id')
    )


def downgrade() -> None:
    # Drop tables
    op.drop_table('discharge_checklists')
    op.drop_table('patient_discharge_instructions')
    op.drop_table('sep_closures')
    op.drop_table('bpjs_claim_finalizations')

    op.drop_index(op.f('ix_follow_up_appointments_appointment_date'), table_name='follow_up_appointments')
    op.drop_index(op.f('ix_follow_up_appointments_admission_id'), table_name='follow_up_appointments')
    op.drop_index(op.f('ix_follow_up_appointments_id'), table_name='follow_up_appointments')
    op.drop_table('follow_up_appointments')

    op.drop_table('medication_reconciliations')
    op.drop_table('discharge_summaries')

    op.drop_index(op.f('ix_discharge_orders_admission_id'), table_name='discharge_orders')
    op.drop_index(op.f('ix_discharge_orders_id'), table_name='discharge_orders')
    op.drop_table('discharge_orders')

    op.drop_index(op.f('ix_discharge_readiness_admission_id'), table_name='discharge_readiness')
    op.drop_index(op.f('ix_discharge_readiness_id'), table_name='discharge_readiness')
    op.drop_table('discharge_readiness')

    # Drop enums
    sa.Enum(name='followuptype').drop(op.get_bind())
    sa.Enum(name='dischargecondition').drop(op.get_bind())
    sa.Enum(name='dischargedestination').drop(op.get_bind())
    sa.Enum(name='dischargestatus').drop(op.get_bind())
