"""Create daily care documentation tables for STORY-022

Revision ID: 20250114000017
Revises: 20250114000016
Create Date: 2025-01-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = '20250114000017'
down_revision: Union[str, None] = '20250114000016'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '20250114000016'


def upgrade() -> None:
    # Create shift type enum if not exists
    try:
        shift_type_enum = ENUM(
            'morning', 'afternoon', 'night',
            name='shifttype', create_type=True
        )
        shift_type_enum.create(op.get_bind())
    except Exception:
        # Enum might already exist from admission tables
        pass

    # Create nursing_flow_sheets table
    op.create_table(
        'nursing_flow_sheets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('nurse_id', sa.Integer(), nullable=False),
        sa.Column('shift_date', sa.Date(), nullable=False),
        sa.Column('shift_type', sa.Enum('morning', 'afternoon', 'night', name='shifttype'), nullable=False),
        sa.Column('vital_signs', sa.JSON(), nullable=True),
        sa.Column('oral_intake_ml', sa.Integer(), nullable=True),
        sa.Column('iv_intake_ml', sa.Integer(), nullable=True),
        sa.Column('urine_output_ml', sa.Integer(), nullable=True),
        sa.Column('stool_output', sa.String(length=50), nullable=True),
        sa.Column('emesis', sa.Boolean(), nullable=True),
        sa.Column('drainage_output', sa.Integer(), nullable=True),
        sa.Column('skin_intact', sa.Boolean(), nullable=True),
        sa.Column('skin_issues', sa.JSON(), nullable=True),
        sa.Column('wound_care_performed', sa.Boolean(), nullable=True),
        sa.Column('wound_description', sa.Text(), nullable=True),
        sa.Column('activity_level', sa.String(length=50), nullable=True),
        sa.Column('mobility_assistance', sa.String(length=50), nullable=True),
        sa.Column('fall_risk', sa.String(length=50), nullable=True),
        sa.Column('diet_tolerance', sa.String(length=50), nullable=True),
        sa.Column('eating_assistance', sa.Boolean(), nullable=True),
        sa.Column('swallowing_difficulty', sa.Boolean(), nullable=True),
        sa.Column('bowel_pattern', sa.String(length=50), nullable=True),
        sa.Column('bladder_pattern', sa.String(length=50), nullable=True),
        sa.Column('incontinence_care', sa.String(length=50), nullable=True),
        sa.Column('consciousness_level', sa.String(length=50), nullable=True),
        sa.Column('orientation', sa.String(length=50), nullable=True),
        sa.Column('behavior', sa.Text(), nullable=True),
        sa.Column('restlessness', sa.Boolean(), nullable=True),
        sa.Column('pain_present', sa.Boolean(), nullable=True),
        sa.Column('pain_location', sa.String(length=200), nullable=True),
        sa.Column('pain_score', sa.Integer(), nullable=True),
        sa.Column('pain_intervention', sa.Text(), nullable=True),
        sa.Column('auto_saved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['nurse_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_nursing_flow_sheets_id'), 'nursing_flow_sheets', ['id'], unique=False)
    op.create_index(op.f('ix_nursing_flow_sheets_admission_id'), 'nursing_flow_sheets', ['admission_id'], unique=False)
    op.create_index(op.f('ix_nursing_flow_sheets_shift_date'), 'nursing_flow_sheets', ['shift_date'], unique=False)

    # Create nursing_narratives table
    op.create_table(
        'nursing_narratives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('nurse_id', sa.Integer(), nullable=False),
        sa.Column('note_type', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_confidential', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('interventions_performed', sa.JSON(), nullable=True),
        sa.Column('patient_response', sa.Text(), nullable=True),
        sa.Column('complications', sa.JSON(), nullable=True),
        sa.Column('signed_by_id', sa.Integer(), nullable=False),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['nurse_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['signed_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_nursing_narratives_id'), 'nursing_narratives', ['id'], unique=False)
    op.create_index(op.f('ix_nursing_narratives_admission_id'), 'nursing_narratives', ['admission_id'], unique=False)

    # Create nursing_care_plans table
    op.create_table(
        'nursing_care_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('nurse_id', sa.Integer(), nullable=False),
        sa.Column('nursing_diagnosis', sa.JSON(), nullable=False),
        sa.Column('goals', sa.JSON(), nullable=False),
        sa.Column('interventions', sa.JSON(), nullable=False),
        sa.Column('rationale', sa.JSON(), nullable=False),
        sa.Column('evaluation', sa.Text(), nullable=True),
        sa.Column('outcome_achieved', sa.Boolean(), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('review_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['nurse_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create patient_education_records table
    op.create_table(
        'patient_education_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('educator_id', sa.Integer(), nullable=False),
        sa.Column('education_topic', sa.String(length=200), nullable=False),
        sa.Column('education_content', sa.Text(), nullable=False),
        sa.Column('teaching_method', sa.JSON(), nullable=False),
        sa.Column('barriers_to_learning', sa.JSON(), nullable=True),
        sa.Column('patient_understanding', sa.String(length=50), nullable=False),
        sa.Column('return_demonstration', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('teach_back_method', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('follow_up_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('follow_up_instructions', sa.Text(), nullable=True),
        sa.Column('signed_by_id', sa.Integer(), nullable=False),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['educator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create physician_daily_notes table
    op.create_table(
        'physician_daily_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('physician_id', sa.Integer(), nullable=False),
        sa.Column('note_date', sa.Date(), nullable=False),
        sa.Column('subjective', sa.Text(), nullable=True),
        sa.Column('objective', sa.Text(), nullable=True),
        sa.Column('assessment', sa.Text(), nullable=False),
        sa.Column('plan', sa.Text(), nullable=False),
        sa.Column('primary_diagnosis', sa.String(length=500), nullable=False),
        sa.Column('secondary_diagnoses', sa.JSON(), nullable=True),
        sa.Column('new_orders', sa.JSON(), nullable=True),
        sa.Column('continued_orders', sa.JSON(), nullable=True),
        sa.Column('discontinued_orders', sa.JSON(), nullable=True),
        sa.Column('prognosis', sa.String(length=200), nullable=True),
        sa.Column('signed_by_id', sa.Integer(), nullable=False),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['physician_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_physician_daily_notes_id'), 'physician_daily_notes', ['id'], unique=False)
    op.create_index(op.f('ix_physician_daily_notes_admission_id'), 'physician_daily_notes', ['admission_id'], unique=False)
    op.create_index(op.f('ix_physician_daily_notes_note_date'), 'physician_daily_notes', ['note_date'], unique=False)

    # Create respiratory_therapy_notes table
    op.create_table(
        'respiratory_therapy_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('therapist_id', sa.Integer(), nullable=False),
        sa.Column('note_date', sa.Date(), nullable=False),
        sa.Column('therapy_type', sa.String(length=100), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('frequency', sa.String(length=50), nullable=True),
        sa.Column('pre_therapy_assessment', sa.Text(), nullable=True),
        sa.Column('intervention_provided', sa.Text(), nullable=False),
        sa.Column('patient_response', sa.Text(), nullable=True),
        sa.Column('post_therapy_assessment', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('signed_by_id', sa.Integer(), nullable=False),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['therapist_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create physical_therapy_notes table
    op.create_table(
        'physical_therapy_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('therapist_id', sa.Integer(), nullable=False),
        sa.Column('note_date', sa.Date(), nullable=False),
        sa.Column('therapy_type', sa.String(length=100), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('frequency', sa.String(length=50), nullable=True),
        sa.Column('functional_status', sa.Text(), nullable=True),
        sa.Column('treatment_provided', sa.Text(), nullable=False),
        sa.Column('patient_response', sa.Text(), nullable=True),
        sa.Column('progress_made', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('signed_by_id', sa.Integer(), nullable=False),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['therapist_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create nutrition_notes table
    op.create_table(
        'nutrition_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('dietitian_id', sa.Integer(), nullable=False),
        sa.Column('note_date', sa.Date(), nullable=False),
        sa.Column('diet_type', sa.String(length=100), nullable=False),
        sa.Column('calorie_target', sa.Integer(), nullable=True),
        sa.Column('protein_target', sa.Integer(), nullable=True),
        sa.Column('nutritional_assessment', sa.Text(), nullable=True),
        sa.Column('intake_assessment', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('follow_up_date', sa.Date(), nullable=True),
        sa.Column('signed_by_id', sa.Integer(), nullable=False),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['dietitian_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create social_work_notes table
    op.create_table(
        'social_work_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('social_worker_id', sa.Integer(), nullable=False),
        sa.Column('note_date', sa.Date(), nullable=False),
        sa.Column('psychosocial_assessment', sa.Text(), nullable=True),
        sa.Column('support_system', sa.Text(), nullable=True),
        sa.Column('barriers_to_discharge', sa.JSON(), nullable=True),
        sa.Column('discharge_planning', sa.Text(), nullable=True),
        sa.Column('interventions_provided', sa.JSON(), nullable=True),
        sa.Column('referrals_made', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('signed_by_id', sa.Integer(), nullable=False),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['social_worker_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create shift_handoffs table
    op.create_table(
        'shift_handoffs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('from_shift', sa.Enum('morning', 'afternoon', 'night', name='shifttype'), nullable=False),
        sa.Column('to_shift', sa.Enum('morning', 'afternoon', 'night', name='shifttype'), nullable=False),
        sa.Column('handoff_date', sa.Date(), nullable=False),
        sa.Column('handoff_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('handing_over_nurse_id', sa.Integer(), nullable=False),
        sa.Column('receiving_nurse_id', sa.Integer(), nullable=False),
        sa.Column('patient_status_summary', sa.Text(), nullable=False),
        sa.Column('critical_events', sa.JSON(), nullable=True),
        sa.Column('pending_tasks', sa.JSON(), nullable=True),
        sa.Column('follow_up_required', sa.JSON(), nullable=True),
        sa.Column('total_patients', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('stable_patients', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('critical_patients', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('new_admissions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('verified_by_receiving_nurse', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['handing_over_nurse_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['receiving_nurse_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create change_of_shift_reports table
    op.create_table(
        'change_of_shift_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ward_id', sa.Integer(), nullable=False),
        sa.Column('shift_date', sa.Date(), nullable=False),
        sa.Column('shift_type', sa.Enum('morning', 'afternoon', 'night', name='shifttype'), nullable=False),
        sa.Column('report_by_nurse_id', sa.Integer(), nullable=False),
        sa.Column('total_patients', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_admissions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_discharges', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_transfers', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('critical_patient_list', sa.JSON(), nullable=True),
        sa.Column('incidents_reported', sa.JSON(), nullable=True),
        sa.Column('equipment_issues', sa.JSON(), nullable=True),
        sa.Column('supply_needs', sa.JSON(), nullable=True),
        sa.Column('nursing_staff_present', sa.JSON(), nullable=True),
        sa.Column('staffing_concerns', sa.Text(), nullable=True),
        sa.Column('verified_by_supervisor', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['report_by_nurse_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['ward_id'], ['departments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create digital_signatures table
    op.create_table(
        'digital_signatures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.String(length=100), nullable=False),
        sa.Column('signer_id', sa.Integer(), nullable=False),
        sa.Column('signature_data', sa.Text(), nullable=False),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['signer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create auto_save_drafts table
    op.create_table(
        'auto_save_drafts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.String(length=100), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('draft_content', sa.JSON(), nullable=False),
        sa.Column('last_saved', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auto_save_drafts_id'), 'auto_save_drafts', ['id'], unique=False)
    op.create_index(op.f('ix_auto_save_drafts_admission_id'), 'auto_save_drafts', ['admission_id'], unique=False)

    # Create discharge_summary_exports table
    op.create_table(
        'discharge_summary_exports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('summary_data', sa.JSON(), nullable=False),
        sa.Column('export_format', sa.String(length=10), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.Column('generated_by_id', sa.Integer(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['admission_id'], ['admission_orders.id'], ),
        sa.ForeignKeyConstraint(['generated_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('admission_id')
    )


def downgrade() -> None:
    # Drop tables
    op.drop_table('discharge_summary_exports')

    op.drop_index(op.f('ix_auto_save_drafts_admission_id'), table_name='auto_save_drafts')
    op.drop_index(op.f('ix_auto_save_drafts_id'), table_name='auto_save_drafts')
    op.drop_table('auto_save_drafts')

    op.drop_table('digital_signatures')
    op.drop_table('change_of_shift_reports')
    op.drop_table('shift_handoffs')
    op.drop_table('social_work_notes')
    op.drop_table('nutrition_notes')
    op.drop_table('physical_therapy_notes')
    op.drop_table('respiratory_therapy_notes')

    op.drop_index(op.f('ix_physician_daily_notes_note_date'), table_name='physician_daily_notes')
    op.drop_index(op.f('ix_physician_daily_notes_admission_id'), table_name='physician_daily_notes')
    op.drop_index(op.f('ix_physician_daily_notes_id'), table_name='physician_daily_notes')
    op.drop_table('physician_daily_notes')

    op.drop_table('patient_education_records')
    op.drop_table('nursing_care_plans')

    op.drop_index(op.f('ix_nursing_narratives_admission_id'), table_name='nursing_narratives')
    op.drop_index(op.f('ix_nursing_narratives_id'), table_name='nursing_narratives')
    op.drop_table('nursing_narratives')

    op.drop_index(op.f('ix_nursing_flow_sheets_shift_date'), table_name='nursing_flow_sheets')
    op.drop_index(op.f('ix_nursing_flow_sheets_admission_id'), table_name='nursing_flow_sheets')
    op.drop_index(op.f('ix_nursing_flow_sheets_id'), table_name='nursing_flow_sheets')
    op.drop_table('nursing_flow_sheets')

    # Drop enum (only if not used by other tables)
    try:
        sa.Enum(name='shifttype').drop(op.get_bind())
    except Exception:
        pass
