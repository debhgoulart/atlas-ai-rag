"""Create knowledge_bases table

Revision ID: 0002_create_knowledge_bases
Revises: 0001_enable_pgvector
Create Date: 2026-11-13 00:01:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0002_create_knowledge_bases'
down_revision: Union[str, None] = '0001_enable_pgvector'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'knowledge_bases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_knowledge_bases_id', 'knowledge_bases', ['id'])
    op.create_index('ix_knowledge_bases_name', 'knowledge_bases', ['name'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_knowledge_bases_name', table_name='knowledge_bases')
    op.drop_index('ix_knowledge_bases_id', table_name='knowledge_bases')
    op.drop_table('knowledge_bases')
