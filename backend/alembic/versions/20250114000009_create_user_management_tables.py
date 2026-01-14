"""create user management tables for STORY-037

Revision ID: 20250114000009
Create Date: 2026-01-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250114000009'
down_revision: Union[str, None] = '20250114000008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '20250114000008'


def upgrade() -> None:
    # Add columns to users table for extended user management
    op.add_column('users', sa.Column('department_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('phone', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('employee_id', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('license_number', sa.String(length=100), nullable=True))

    # Create foreign key for department_id
    op.create_foreign_key(
        'fk_users_department_id', 'users', 'departments',
        ['department_id'], ['id']
    )

    # Create departments table
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_department_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['parent_department_id'], ['departments.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_departments_id'), 'departments', ['id'], unique=False)
    op.create_index(op.f('ix_departments_code'), 'departments', ['code'], unique=True)

    # Create user_access_requests table
    op.create_table(
        'user_access_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('requested_role', sa.String(length=50), nullable=False),
        sa.Column('requested_department_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['requested_department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_access_requests_id'), 'user_access_requests', ['id'], unique=False)
    op.create_index(op.f('ix_user_access_requests_user_id'), 'user_access_requests', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_access_requests_status'), 'user_access_requests', ['status'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('user_access_requests')
    op.drop_table('departments')

    # Drop columns from users table
    op.drop_constraint('fk_users_department_id', 'users', type_='foreignkey')
    op.drop_column('users', 'license_number')
    op.drop_column('users', 'employee_id')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'department_id')
