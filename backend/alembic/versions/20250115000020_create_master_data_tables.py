"""create master data tables

Revision ID: 20250115000020
Revises: 20250115000019
Create Date: 2026-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250115000020'
down_revision = '20250115000019'
branch_labels = None
depends_on = None


def upgrade():
    # Create icd10_codes table
    op.create_table(
        'icd10_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False, comment='ICD-10 code (e.g., A00, J01)'),
        sa.Column('code_full', sa.String(length=20), nullable=False, comment='Full code with decimal (e.g., A00.0)'),
        sa.Column('chapter', sa.String(length=20), nullable=False, comment='Chapter (I-XXII)'),
        sa.Column('block', sa.String(length=20), nullable=True, comment='Block code range'),
        sa.Column('description_indonesian', sa.Text(), nullable=False, comment='Description in Indonesian'),
        sa.Column('description_english', sa.Text(), nullable=True, comment='Description in English'),
        sa.Column('severity', sa.String(length=20), nullable=True, comment='Severity level if applicable'),
        sa.Column('inclusion_terms', postgresql.JSONB(), nullable=True, comment='Inclusion terms'),
        sa.Column('exclusion_terms', postgresql.JSONB(), nullable=True, comment='Exclusion terms'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes'),
        sa.Column('is_common', sa.Boolean(), nullable=False, server_default='false', comment='Mark as commonly used'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0', comment='Usage tracking'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Active status'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_icd10_codes_id', 'icd10_codes', ['id'])
    op.create_index('ix_icd10_codes_code', 'icd10_codes', ['code'])
    op.create_index('ix_icd10_codes_chapter', 'icd10_codes', ['chapter'])

    # Create loinc_codes table
    op.create_table(
        'loinc_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('loinc_num', sa.String(length=50), nullable=False, comment='LOINC number'),
        sa.Column('component', sa.Text(), nullable=False, comment='Analyte/component name'),
        sa.Column('property_attr', sa.String(length=50), nullable=True, comment='Property (e.g., MassConc, NCln)'),
        sa.Column('time_aspect', sa.String(length=50), nullable=True, comment='Time aspect (e.g., Pt, 24h)'),
        sa.Column('system', sa.String(length=50), nullable=True, comment='System (e.g., Serum, Urine)'),
        sa.Column('scale_type', sa.String(length=50), nullable=True, comment='Scale type (e.g., Qn, Ord)'),
        sa.Column('method_type', sa.String(length=50), nullable=True, comment='Method type'),
        sa.Column('class_name', sa.String(length=20), nullable=True, comment='LOINC class'),
        sa.Column('status', sa.String(length=20), nullable=True, comment='Status (ACTIVE, TRIAL, DISCOURAGED)'),
        sa.Column('short_name', sa.String(length=255), nullable=True, comment='Short name'),
        sa.Column('long_common_name', sa.Text(), nullable=True, comment='Long common name'),
        sa.Column('example_units', sa.String(length=100), nullable=True, comment='Example units'),
        sa.Column('units_and_range', sa.Text(), nullable=True, comment='Reference range'),
        sa.Column('is_common', sa.Boolean(), nullable=False, server_default='false', comment='Mark as commonly used'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0', comment='Usage tracking'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Active status'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('loinc_num')
    )
    op.create_index('ix_loinc_codes_id', 'loinc_codes', ['id'])
    op.create_index('ix_loinc_codes_loinc_num', 'loinc_codes', ['loinc_num'])
    op.create_index('ix_loinc_codes_class_name', 'loinc_codes', ['class_name'])

    # Create drug_formulary table
    op.create_table(
        'drug_formulary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('generic_name', sa.String(length=255), nullable=False, comment='Generic (scientific) name'),
        sa.Column('brand_names', postgresql.JSONB(), nullable=True, comment='List of brand names'),
        sa.Column('dosage_form', sa.String(length=50), nullable=True, comment='Tablet, capsule, injection, etc.'),
        sa.Column('strength', sa.String(length=100), nullable=True, comment='Strength (e.g., 500mg, 5mg/mL)'),
        sa.Column('bpjs_code', sa.String(length=50), nullable=True, comment='BPJS formularium code'),
        sa.Column('bpjs_covered', sa.Boolean(), nullable=False, server_default='true', comment='Covered by BPJS'),
        sa.Column('atc_code', sa.String(length=20), nullable=True, comment='Anatomical Therapeutic Chemical code'),
        sa.Column('atc_level', sa.Integer(), nullable=True, comment='ATC classification level (1-5)'),
        sa.Column('ekatalog_code', sa.String(length=50), nullable=True, comment='e-Katalog LKPP code'),
        sa.Column('manufacturer', sa.String(length=255), nullable=True, comment='Manufacturer name'),
        sa.Column('is_narcotic', sa.Boolean(), nullable=False, server_default='false', comment='Narcotic drug'),
        sa.Column('is_antibiotic', sa.Boolean(), nullable=False, server_default='false', comment='Antibiotic'),
        sa.Column('requires_prescription', sa.Boolean(), nullable=False, server_default='true', comment='Requires prescription'),
        sa.Column('cold_chain_required', sa.Boolean(), nullable=False, server_default='false', comment='Requires cold storage'),
        sa.Column('storage_conditions', sa.Text(), nullable=True, comment='Storage requirements'),
        sa.Column('default_dosage', sa.String(length=100), nullable=True, comment='Default dosage guideline'),
        sa.Column('default_frequency', sa.String(length=50), nullable=True, comment='Default frequency'),
        sa.Column('default_route', sa.String(length=50), nullable=True, comment='Default route (oral, IV, IM, etc.)'),
        sa.Column('contraindications', postgresql.JSONB(), nullable=True, comment='Contraindications'),
        sa.Column('interactions', postgresql.JSONB(), nullable=True, comment='Drug interactions'),
        sa.Column('side_effects', postgresql.JSONB(), nullable=True, comment='Common side effects'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Active status'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_drug_formulary_id', 'drug_formulary', ['id'])
    op.create_index('ix_drug_formulary_generic_name', 'drug_formulary', ['generic_name'])
    op.create_index('ix_drug_formulary_dosage_form', 'drug_formulary', ['dosage_form'])
    op.create_index('ix_drug_formulary_bpjs_code', 'drug_formulary', ['bpjs_code'])
    op.create_index('ix_drug_formulary_atc_code', 'drug_formulary', ['atc_code'])

    # Create procedure_codes table
    op.create_table(
        'procedure_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False, comment='Procedure code'),
        sa.Column('code_system', sa.String(length=50), nullable=False, comment='ICD-9-CM, LOINC, or LOCAL'),
        sa.Column('code_type', sa.String(length=50), nullable=True, comment='LAB, RADIOLOGY, SURGERY, THERAPY'),
        sa.Column('description_indonesian', sa.Text(), nullable=False, comment='Description in Indonesian'),
        sa.Column('description_english', sa.Text(), nullable=True, comment='Description in English'),
        sa.Column('category', sa.String(length=100), nullable=True, comment='Procedure category'),
        sa.Column('department', sa.String(length=100), nullable=True, comment='Performing department'),
        sa.Column('bpjs_tariff_code', sa.String(length=50), nullable=True, comment='BPJS tariff code'),
        sa.Column('bpjs_covered', sa.Boolean(), nullable=False, server_default='true', comment='Covered by BPJS'),
        sa.Column('default_price', sa.Numeric(precision=15, scale=2), nullable=True, comment='Default procedure price'),
        sa.Column('is_surgical', sa.Boolean(), nullable=False, server_default='false', comment='Surgical procedure'),
        sa.Column('requires_authorization', sa.Boolean(), nullable=False, server_default='false', comment='Requires pre-authorization'),
        sa.Column('preparation_instructions', sa.Text(), nullable=True, comment='Patient preparation instructions'),
        sa.Column('contraindications', postgresql.JSONB(), nullable=True, comment='Contraindications'),
        sa.Column('risks', postgresql.JSONB(), nullable=True, comment='Associated risks'),
        sa.Column('is_common', sa.Boolean(), nullable=False, server_default='false', comment='Mark as commonly used'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0', comment='Usage tracking'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Active status'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_procedure_codes_id', 'procedure_codes', ['id'])
    op.create_index('ix_procedure_codes_code', 'procedure_codes', ['code'])
    op.create_index('ix_procedure_codes_code_system', 'procedure_codes', ['code_system'])
    op.create_index('ix_procedure_codes_code_type', 'procedure_codes', ['code_type'])
    op.create_index('ix_procedure_codes_category', 'procedure_codes', ['category'])
    op.create_index('ix_procedure_codes_department', 'procedure_codes', ['department'])

    # Create room_classes table
    op.create_table(
        'room_classes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False, comment='Room class code (VVIP, VIP, 1, 2, 3)'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='Room class name'),
        sa.Column('name_indonesian', sa.String(length=100), nullable=False, comment='Name in Indonesian'),
        sa.Column('description', sa.Text(), nullable=True, comment='Description'),
        sa.Column('daily_rate', sa.Numeric(precision=15, scale=2), nullable=False, comment='Daily room rate'),
        sa.Column('bpjs_package_rate', sa.Numeric(precision=15, scale=2), nullable=True, comment='BPJS INA-CBG package rate'),
        sa.Column('capacity', sa.Integer(), nullable=False, server_default='1', comment='Bed capacity per room'),
        sa.Column('has_ac', sa.Boolean(), nullable=False, server_default='false', comment='Air conditioning'),
        sa.Column('has_tv', sa.Boolean(), nullable=False, server_default='false', comment='Television'),
        sa.Column('has_bathroom', sa.Boolean(), nullable=False, server_default='true', comment='Private bathroom'),
        sa.Column('has_refrigerator', sa.Boolean(), nullable=False, server_default='false', comment='Refrigerator'),
        sa.Column('amenities', postgresql.JSONB(), nullable=True, comment='Additional amenities'),
        sa.Column('nurses_station_distance', sa.String(length=50), nullable=True, comment='Proximity to nurses station'),
        sa.Column('visitation_hours', sa.String(length=100), nullable=True, comment='Visitation hours'),
        sa.Column('max_visitors', sa.Integer(), nullable=False, server_default='2', comment='Maximum visitors'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Active status'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_room_classes_id', 'room_classes', ['id'])

    # Create insurance_companies table
    op.create_table(
        'insurance_companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False, comment='Insurance company code'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Insurance company name'),
        sa.Column('insurance_type', sa.String(length=50), nullable=False, comment='BPJS, ASURANSI, UMUM, CORPORATE'),
        sa.Column('address', sa.Text(), nullable=True, comment='Company address'),
        sa.Column('phone', sa.String(length=50), nullable=True, comment='Contact phone'),
        sa.Column('email', sa.String(length=255), nullable=True, comment='Contact email'),
        sa.Column('website', sa.String(length=255), nullable=True, comment='Website'),
        sa.Column('contact_person', sa.String(length=255), nullable=True, comment='Contact person name'),
        sa.Column('contact_phone', sa.String(length=50), nullable=True, comment='Contact person phone'),
        sa.Column('claims_address', sa.Text(), nullable=True, comment='Claims submission address'),
        sa.Column('claims_email', sa.String(length=255), nullable=True, comment='Claims email'),
        sa.Column('claims_phone', sa.String(length=50), nullable=True, comment='Claims phone'),
        sa.Column('payment_terms', sa.Integer(), nullable=True, comment='Payment terms in days'),
        sa.Column('credit_limit', sa.Numeric(precision=15, scale=2), nullable=True, comment='Credit limit'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Active status'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_insurance_companies_id', 'insurance_companies', ['id'])
    op.create_index('ix_insurance_companies_code', 'insurance_companies', ['code'])
    op.create_index('ix_insurance_companies_insurance_type', 'insurance_companies', ['insurance_type'])

    # Create insurance_plans table
    op.create_table(
        'insurance_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('plan_code', sa.String(length=50), nullable=False, comment='Plan code'),
        sa.Column('plan_name', sa.String(length=255), nullable=False, comment='Plan name'),
        sa.Column('plan_type', sa.String(length=50), nullable=True, comment='INDIVIDUAL, FAMILY, CORPORATE'),
        sa.Column('coverage_type', sa.String(length=50), nullable=True, comment='INPATIENT, OUTPATIENT, COMPREHENSIVE'),
        sa.Column('deductible_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('co_insurance_percentage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('co_pay_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('out_of_pocket_max', sa.Numeric(precision=15, scale=2), nullable=True, comment='Annual out-of-pocket maximum'),
        sa.Column('coverage_limit', sa.Numeric(precision=15, scale=2), nullable=True, comment='Annual coverage limit'),
        sa.Column('pre_authorization_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('network_type', sa.String(length=50), nullable=True, comment='Network type (PPO, HMO, EPO)'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Active status'),
        sa.Column('effective_date', sa.DateTime(timezone=True), nullable=True, comment='Plan effective date'),
        sa.Column('expiration_date', sa.DateTime(timezone=True), nullable=True, comment='Plan expiration date'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['insurance_companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_insurance_plans_id', 'insurance_plans', ['id'])
    op.create_index('ix_insurance_plans_company_id', 'insurance_plans', ['company_id'])

    # Create reference_data table
    op.create_table(
        'reference_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False, comment='Data category'),
        sa.Column('code', sa.String(length=100), nullable=False, comment='Reference code'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Reference name'),
        sa.Column('name_indonesian', sa.String(length=255), nullable=True, comment='Name in Indonesian'),
        sa.Column('description', sa.Text(), nullable=True, comment='Description'),
        sa.Column('parent_id', sa.Integer(), nullable=True, comment='Parent reference for hierarchy'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0', comment='Display order'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Active status'),
        sa.Column('attributes', postgresql.JSONB(), nullable=True, comment='Additional attributes'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['reference_data.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reference_data_id', 'reference_data', ['id'])
    op.create_index('ix_reference_data_category', 'reference_data', ['category'])
    op.create_index('ix_reference_data_code', 'reference_data', ['code'])
    op.create_index('ix_reference_data_parent_id', 'reference_data', ['parent_id'])


def downgrade():
    # Drop tables in reverse order of creation
    op.drop_index('ix_reference_data_parent_id', table_name='reference_data')
    op.drop_index('ix_reference_data_code', table_name='reference_data')
    op.drop_index('ix_reference_data_category', table_name='reference_data')
    op.drop_index('ix_reference_data_id', table_name='reference_data')
    op.drop_table('reference_data')

    op.drop_index('ix_insurance_plans_company_id', table_name='insurance_plans')
    op.drop_index('ix_insurance_plans_id', table_name='insurance_plans')
    op.drop_table('insurance_plans')

    op.drop_index('ix_insurance_companies_insurance_type', table_name='insurance_companies')
    op.drop_index('ix_insurance_companies_code', table_name='insurance_companies')
    op.drop_index('ix_insurance_companies_id', table_name='insurance_companies')
    op.drop_table('insurance_companies')

    op.drop_index('ix_room_classes_id', table_name='room_classes')
    op.drop_table('room_classes')

    op.drop_index('ix_procedure_codes_department', table_name='procedure_codes')
    op.drop_index('ix_procedure_codes_category', table_name='procedure_codes')
    op.drop_index('ix_procedure_codes_code_type', table_name='procedure_codes')
    op.drop_index('ix_procedure_codes_code_system', table_name='procedure_codes')
    op.drop_index('ix_procedure_codes_code', table_name='procedure_codes')
    op.drop_index('ix_procedure_codes_id', table_name='procedure_codes')
    op.drop_table('procedure_codes')

    op.drop_index('ix_drug_formulary_atc_code', table_name='drug_formulary')
    op.drop_index('ix_drug_formulary_bpjs_code', table_name='drug_formulary')
    op.drop_index('ix_drug_formulary_dosage_form', table_name='drug_formulary')
    op.drop_index('ix_drug_formulary_generic_name', table_name='drug_formulary')
    op.drop_index('ix_drug_formulary_id', table_name='drug_formulary')
    op.drop_table('drug_formulary')

    op.drop_index('ix_loinc_codes_class_name', table_name='loinc_codes')
    op.drop_index('ix_loinc_codes_loinc_num', table_name='loinc_codes')
    op.drop_index('ix_loinc_codes_id', table_name='loinc_codes')
    op.drop_table('loinc_codes')

    op.drop_index('ix_icd10_codes_chapter', table_name='icd10_codes')
    op.drop_index('ix_icd10_codes_code', table_name='icd10_codes')
    op.drop_index('ix_icd10_codes_id', table_name='icd10_codes')
    op.drop_table('icd10_codes')
