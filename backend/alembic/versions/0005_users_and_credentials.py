"""Create users and user_gemini_credentials tables

Revision ID: 0005_users_and_credentials
Revises: 0004_create_chat_tables
Create Date: 2026-11-13 03:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0005_users_and_credentials'
down_revision: Union[str, None] = '0004_create_chat_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. Create user_gemini_credentials table
    op.create_table(
        'user_gemini_credentials',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            'user_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('encrypted_api_key', sa.Text(), nullable=False),
        sa.Column('key_hint', sa.String(length=10), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='NOT_CONFIGURED'),
        sa.Column('last_validated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_user_gemini_credentials_id', 'user_gemini_credentials', ['id'])
    op.create_index('ix_user_gemini_credentials_user_id', 'user_gemini_credentials', ['user_id'], unique=True)
    op.create_index('ix_user_gemini_credentials_status', 'user_gemini_credentials', ['status'])


def downgrade() -> None:
    op.drop_index('ix_user_gemini_credentials_status', table_name='user_gemini_credentials')
    op.drop_index('ix_user_gemini_credentials_user_id', table_name='user_gemini_credentials')
    op.drop_index('ix_user_gemini_credentials_id', table_name='user_gemini_credentials')
    op.drop_table('user_gemini_credentials')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
