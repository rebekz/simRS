"""create medication list tables for STORY-014

Revision ID: 20250114000010
Create Date: 2026-01-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '20250114000010'
down_revision: Union[str, None] = '20250114000009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '20250114000009'


def upgrade() -> None:
    # Create patient_medications table
    op.create_table(
        'patient_medications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('encounter_id', sa.Integer(), nullable=True),
        sa.Column('drug_id', sa.Integer(), nullable=False),
        sa.Column('drug_name', sa.String(length=255), nullable=False),
        sa.Column('generic_name', sa.String(length=255), nullable=False),
        sa.Column('dosage', sa.String(length=100), nullable=True),
        sa.Column('dose_unit', sa.String(length=50), nullable=True),
        sa.Column('frequency', sa.String(length=100), nullable=True),
        sa.Column('route', sa.String(length=50), nullable=True),
        sa.Column('indication', sa.Text(), nullable=True),
        sa.Column('prescriber_id', sa.Integer(), nullable=True),
        sa.Column('prescription_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('discontinuation_reason', sa.Text(), nullable=True),
        sa.Column('batch_number', sa.String(length=100), nullable=True),
        sa.Column('manufacturer', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['drug_id'], ['drugs.id'], ),
        sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['prescriber_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patient_medications_id'), 'patient_medications', ['id'], unique=False)
    op.create_index(op.f('ix_patient_medications_patient_id'), 'patient_medications', ['patient_id'], unique=False)
    op.create_index(op.f('ix_patient_medications_drug_id'), 'patient_medications', ['drug_id'], unique=False)
    op.create_index(op.f('ix_patient_medications_status'), 'patient_medications', ['status'], unique=False)

    # Create drug_interactions table
    op.create_table(
        'drug_interactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('interaction_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('drug_1_id', sa.Integer(), nullable=False),
        sa.Column('drug_1_name', sa.String(length=255), nullable=False),
        sa.Column('drug_2_id', sa.Integer(), nullable=True),
        sa.Column('drug_2_name', sa.String(length=255), nullable=True),
        sa.Column('disease_code', sa.String(length=20), nullable=True),
        sa.Column('disease_name', sa.String(length=255), nullable=True),
        sa.Column('allergy_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('recommendation', sa.Text(), nullable=False),
        sa.Column('references', sa.Text(), nullable=True),
        sa.Column('requires_override', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('evidence_level', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['drug_1_id'], ['drugs.id'], ),
        sa.ForeignKeyConstraint(['drug_2_id'], ['drugs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_drug_interactions_id'), 'drug_interactions', ['id'], unique=False)
    op.create_index(op.f('ix_drug_interactions_interaction_type'), 'drug_interactions', ['interaction_type'], unique=False)
    op.create_index(op.f('ix_drug_interactions_severity'), 'drug_interactions', ['severity'], unique=False)
    op.create_index(op.f('ix_drug_interactions_disease_code'), 'drug_interactions', ['disease_code'], unique=False)

    # Create custom_interaction_rules table
    op.create_table(
        'custom_interaction_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('drug_ids', sa.Text(), nullable=False),
        sa.Column('drug_names', sa.Text(), nullable=True),
        sa.Column('age_min', sa.Integer(), nullable=True),
        sa.Column('age_max', sa.Integer(), nullable=True),
        sa.Column('renal_dose_adjustment', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('hepatic_dose_adjustment', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('pregnancy_contraindication', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('breastfeeding_contraindication', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('action_required', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_custom_interaction_rules_id'), 'custom_interaction_rules', ['id'], unique=False)

    # Create medication_reconciliations table
    op.create_table(
        'medication_reconciliations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('encounter_id', sa.Integer(), nullable=False),
        sa.Column('reconciliation_date', sa.Date(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('total_medications', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('discrepancies_found', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('medications_continued', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('medications_modified', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('medications_stopped', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('medications_added', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reconciled_by', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['reconciled_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medication_reconciliations_id'), 'medication_reconciliations', ['id'], unique=False)
    op.create_index(op.f('ix_medication_reconciliations_patient_id'), 'medication_reconciliations', ['patient_id'], unique=False)

    # Create medication_reconciliation_items table
    op.create_table(
        'medication_reconciliation_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reconciliation_id', sa.Integer(), nullable=False),
        sa.Column('patient_medication_id', sa.Integer(), nullable=True),
        sa.Column('drug_name', sa.String(length=255), nullable=False),
        sa.Column('current_status', sa.String(length=50), nullable=False),
        sa.Column('new_dosage', sa.String(length=100), nullable=True),
        sa.Column('new_frequency', sa.String(length=100), nullable=True),
        sa.Column('discrepancies', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['patient_medication_id'], ['patient_medications.id'], ),
        sa.ForeignKeyConstraint(['reconciliation_id'], ['medication_reconciliations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medication_reconciliation_items_id'), 'medication_reconciliation_items', ['id'], unique=False)

    # Create medication_administrations table
    op.create_table(
        'medication_administrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_medication_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('administered_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('administered_by', sa.Integer(), nullable=True),
        sa.Column('dosage_given', sa.String(length=100), nullable=True),
        sa.Column('route', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='scheduled'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['administered_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_medication_id'], ['patient_medications.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medication_administrations_id'), 'medication_administrations', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('medication_administrations')
    op.drop_table('medication_reconciliation_items')
    op.drop_table('medication_reconciliations')
    op.drop_table('custom_interaction_rules')
    op.drop_table('drug_interactions')
    op.drop_table('patient_medications')
