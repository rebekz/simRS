"""create allergies table for STORY-013: Allergy Tracking

Revision ID: 008
Revises: 007
Create Date: 2025-01-14 19:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    allergy_type_enum = postgresql.ENUM(
        'drug',
        'food',
        'environmental',
        'other',
        name='allergy_type',
        create_type=True,
    )
    allergy_type_enum.create(op.get_bind())

    allergy_severity_enum = postgresql.ENUM(
        'mild',
        'moderate',
        'severe',
        'life_threatening',
        name='allergy_severity',
        create_type=True,
    )
    allergy_severity_enum.create(op.get_bind())

    allergy_source_enum = postgresql.ENUM(
        'patient_reported',
        'tested',
        'observed',
        'inferred',
        name='allergy_source',
        create_type=True,
    )
    allergy_source_enum.create(op.get_bind())

    allergy_status_enum = postgresql.ENUM(
        'active',
        'resolved',
        'unconfirmed',
        name='allergy_status',
        create_type=True,
    )
    allergy_status_enum.create(op.get_bind())

    # Create allergies table
    op.create_table(
        'allergies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('allergy_type', allergy_type_enum, nullable=False),
        sa.Column('allergen', sa.String(length=500), nullable=False),
        sa.Column('allergen_code', sa.String(length=100), nullable=True),
        sa.Column('severity', allergy_severity_enum, nullable=False),
        sa.Column('reaction', sa.Text(), nullable=False),
        sa.Column('reaction_details', postgresql.JSONB(), nullable=True),
        sa.Column('status', allergy_status_enum, nullable=False, server_default='active'),
        sa.Column('onset_date', sa.Date(), nullable=True),
        sa.Column('resolved_date', sa.Date(), nullable=True),
        sa.Column('source', allergy_source_enum, nullable=False, server_default='patient_reported'),
        sa.Column('source_notes', sa.Text(), nullable=True),
        sa.Column('clinical_notes', sa.Text(), nullable=True),
        sa.Column('alternatives', postgresql.JSONB(), nullable=True),
        sa.Column('recorded_by', sa.Integer(), nullable=False),
        sa.Column('verified_by', sa.Integer(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recorded_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for allergies
    op.create_index(op.f('ix_allergies_patient_id'), 'allergies', ['patient_id'], unique=False)
    op.create_index(op.f('ix_allergies_allergy_type'), 'allergies', ['allergy_type'], unique=False)
    op.create_index(op.f('ix_allergies_allergen'), 'allergies', ['allergen'], unique=False)
    op.create_index(op.f('ix_allergies_severity'), 'allergies', ['severity'], unique=False)
    op.create_index(op.f('ix_allergies_status'), 'allergies', ['status'], unique=False)
    op.create_index(op.f('ix_allergies_allergen_code'), 'allergies', ['allergen_code'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_allergies_allergen_code'), table_name='allergies')
    op.drop_index(op.f('ix_allergies_status'), table_name='allergies')
    op.drop_index(op.f('ix_allergies_severity'), table_name='allergies')
    op.drop_index(op.f('ix_allergies_allergen'), table_name='allergies')
    op.drop_index(op.f('ix_allergies_allergy_type'), table_name='allergies')
    op.drop_index(op.f('ix_allergies_patient_id'), table_name='allergies')

    # Drop table
    op.drop_table('allergies')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS allergy_status')
    op.execute('DROP TYPE IF EXISTS allergy_source')
    op.execute('DROP TYPE IF EXISTS allergy_severity')
    op.execute('DROP TYPE IF EXISTS allergy_type')
