"""Add user_id multi-tenant isolation and compound uniqueness

Revision ID: 0006_multi_tenant_isolation
Revises: 0005_users_and_credentials
Create Date: 2026-11-14 00:54:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0006_multi_tenant_isolation'
down_revision: Union[str, None] = '0005_users_and_credentials'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Purge legacy orphaned records without attributable owner
    op.execute("DELETE FROM chat_messages")
    op.execute("DELETE FROM chat_sessions")
    op.execute("DELETE FROM document_chunks")
    op.execute("DELETE FROM documents")
    op.execute("DELETE FROM knowledge_bases")

    # 2. Update knowledge_bases table
    op.add_column(
        'knowledge_bases',
        sa.Column(
            'user_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
    )
    op.drop_index('ix_knowledge_bases_name', table_name='knowledge_bases')
    op.create_index('ix_knowledge_bases_user_id', 'knowledge_bases', ['user_id'])
    op.create_unique_constraint(
        'uq_knowledge_bases_user_id_name',
        'knowledge_bases',
        ['user_id', 'name'],
    )

    # 3. Update documents table
    op.add_column(
        'documents',
        sa.Column(
            'user_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
    )
    op.create_index('ix_documents_user_id', 'documents', ['user_id'])

    # 4. Update document_chunks table
    op.add_column(
        'document_chunks',
        sa.Column(
            'user_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
    )
    op.create_index('ix_document_chunks_user_id', 'document_chunks', ['user_id'])
    op.create_index(
        'ix_document_chunks_user_kb',
        'document_chunks',
        ['user_id', 'knowledge_base_id'],
    )

    # 5. Update chat_sessions table
    op.add_column(
        'chat_sessions',
        sa.Column(
            'user_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
    )
    op.create_index('ix_chat_sessions_user_id', 'chat_sessions', ['user_id'])
    op.create_index(
        'ix_chat_sessions_user_kb',
        'chat_sessions',
        ['user_id', 'knowledge_base_id'],
    )


def downgrade() -> None:
    # 5. Revert chat_sessions
    op.drop_index('ix_chat_sessions_user_kb', table_name='chat_sessions')
    op.drop_index('ix_chat_sessions_user_id', table_name='chat_sessions')
    op.drop_column('chat_sessions', 'user_id')

    # 4. Revert document_chunks
    op.drop_index('ix_document_chunks_user_kb', table_name='document_chunks')
    op.drop_index('ix_document_chunks_user_id', table_name='document_chunks')
    op.drop_column('document_chunks', 'user_id')

    # 3. Revert documents
    op.drop_index('ix_documents_user_id', table_name='documents')
    op.drop_column('documents', 'user_id')

    # 2. Revert knowledge_bases
    op.drop_constraint('uq_knowledge_bases_user_id_name', 'knowledge_bases', type_='unique')
    op.drop_index('ix_knowledge_bases_user_id', table_name='knowledge_bases')
    op.create_index('ix_knowledge_bases_name', 'knowledge_bases', ['name'], unique=True)
    op.drop_column('knowledge_bases', 'user_id')
