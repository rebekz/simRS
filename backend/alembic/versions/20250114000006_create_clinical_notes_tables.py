"""create clinical notes tables for STORY-015: Clinical Notes (SOAP)

Revision ID: 009
Revises: 008
Create Date: 2025-01-14 20:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    note_type_enum = postgresql.ENUM(
        'soap',
        'admission',
        'progress',
        'discharge',
        'consultation',
        'procedure',
        'operating',
        'emergency',
        'telephone',
        'email',
        'other',
        name='note_type',
        create_type=True,
    )
    note_type_enum.create(op.get_bind())

    note_status_enum = postgresql.ENUM(
        'draft',
        'pending',
        'signed',
        'amended',
        name='note_status',
        create_type=True,
    )
    note_status_enum.create(op.get_bind())

    # Create clinical_notes table
    op.create_table(
        'clinical_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('encounter_id', sa.Integer(), nullable=True),
        sa.Column('note_type', note_type_enum, nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('status', note_status_enum, nullable=False, server_default='draft'),
        sa.Column('subjective', sa.Text(), nullable=True),
        sa.Column('objective', sa.Text(), nullable=True),
        sa.Column('assessment', sa.Text(), nullable=True),
        sa.Column('plan', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('structured_data', postgresql.JSONB(), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('signed_by_id', sa.Integer(), nullable=True),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cosigned_by_id', sa.Integer(), nullable=True),
        sa.Column('cosigned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('parent_note_id', sa.Integer(), nullable=True),
        sa.Column('is_amendment', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('note_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['cosigned_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_note_id'], ['clinical_notes.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['signed_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for clinical_notes
    op.create_index(op.f('ix_clinical_notes_patient_id'), 'clinical_notes', ['patient_id'], unique=False)
    op.create_index(op.f('ix_clinical_notes_encounter_id'), 'clinical_notes', ['encounter_id'], unique=False)
    op.create_index(op.f('ix_clinical_notes_note_type'), 'clinical_notes', ['note_type'], unique=False)
    op.create_index(op.f('ix_clinical_notes_status'), 'clinical_notes', ['status'], unique=False)
    op.create_index(op.f('ix_clinical_notes_note_date'), 'clinical_notes', ['note_date'], unique=False)
    op.create_index(op.f('ix_clinical_notes_version'), 'clinical_notes', ['version'], unique=False)
    op.create_index('ix_clinical_notes_uuid', 'clinical_notes', ['uuid'], unique=True)

    # Create clinical_note_attachments table
    op.create_table(
        'clinical_note_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=500), nullable=False),
        sa.Column('file_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=1000), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['note_id'], ['clinical_notes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for clinical_note_attachments
    op.create_index(op.f('ix_clinical_note_attachments_note_id'), 'clinical_note_attachments', ['note_id'], unique=False)

    # Create clinical_note_signatures table
    op.create_table(
        'clinical_note_signatures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.Integer(), nullable=False),
        sa.Column('signer_id', sa.Integer(), nullable=False),
        sa.Column('signer_name', sa.String(length=500), nullable=False),
        sa.Column('signer_role', sa.String(length=100), nullable=False),
        sa.Column('signature_hash', sa.String(length=500), nullable=False),
        sa.Column('signature_ip', sa.String(length=50), nullable=False),
        sa.Column('signature_user_agent', sa.Text(), nullable=True),
        sa.Column('signed_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['note_id'], ['clinical_notes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['signer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for clinical_note_signatures
    op.create_index(op.f('ix_clinical_note_signatures_note_id'), 'clinical_note_signatures', ['note_id'], unique=False)
    op.create_index(op.f('ix_clinical_note_signatures_signer_id'), 'clinical_note_signatures', ['signer_id'], unique=False)

    # Create clinical_note_shares table
    op.create_table(
        'clinical_note_shares',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.Integer(), nullable=False),
        sa.Column('shared_with', sa.Integer(), nullable=False),
        sa.Column('share_type', sa.String(length=50), nullable=False),
        sa.Column('access_level', sa.String(length=50), nullable=False),
        sa.Column('consent_obtained', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('consent_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['note_id'], ['clinical_notes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shared_with'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for clinical_note_shares
    op.create_index(op.f('ix_clinical_note_shares_note_id'), 'clinical_note_shares', ['note_id'], unique=False)
    op.create_index(op.f('ix_clinical_note_shares_shared_with'), 'clinical_note_shares', ['shared_with'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_clinical_note_shares_shared_with'), table_name='clinical_note_shares')
    op.drop_index(op.f('ix_clinical_note_shares_note_id'), table_name='clinical_note_shares')
    op.drop_table('clinical_note_shares')

    op.drop_index(op.f('ix_clinical_note_signatures_signer_id'), table_name='clinical_note_signatures')
    op.drop_index(op.f('ix_clinical_note_signatures_note_id'), table_name='clinical_note_signatures')
    op.drop_table('clinical_note_signatures')

    op.drop_index(op.f('ix_clinical_note_attachments_note_id'), table_name='clinical_note_attachments')
    op.drop_table('clinical_note_attachments')

    op.drop_index('ix_clinical_notes_uuid', table_name='clinical_notes')
    op.drop_index(op.f('ix_clinical_notes_version'), table_name='clinical_notes')
    op.drop_index(op.f('ix_clinical_notes_note_date'), table_name='clinical_notes')
    op.drop_index(op.f('ix_clinical_notes_status'), table_name='clinical_notes')
    op.drop_index(op.f('ix_clinical_notes_note_type'), table_name='clinical_notes')
    op.drop_index(op.f('ix_clinical_notes_encounter_id'), table_name='clinical_notes')
    op.drop_index(op.f('ix_clinical_notes_patient_id'), table_name='clinical_notes')
    op.drop_table('clinical_notes')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS note_status')
    op.execute('DROP TYPE IF EXISTS note_type')
