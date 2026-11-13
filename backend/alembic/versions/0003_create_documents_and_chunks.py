"""Create documents and document_chunks tables with HNSW vector index

Revision ID: 0003_create_documents_and_chunks
Revises: 0002_create_knowledge_bases
Create Date: 2026-11-13 00:02:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '0003_create_documents_and_chunks'
down_revision: Union[str, None] = '0002_create_knowledge_bases'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            'knowledge_base_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('knowledge_bases.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('chunk_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_documents_id', 'documents', ['id'])
    op.create_index('ix_documents_kb_id', 'documents', ['knowledge_base_id'])
    op.create_index('ix_documents_status', 'documents', ['status'])

    # 2. Create document_chunks table with 768-dim Vector column
    op.create_table(
        'document_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            'document_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('documents.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'knowledge_base_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('knowledge_bases.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(768), nullable=False),
        sa.Column('chunk_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_document_chunks_id', 'document_chunks', ['id'])
    op.create_index('ix_document_chunks_doc_id', 'document_chunks', ['document_id'])
    op.create_index('ix_document_chunks_kb_id', 'document_chunks', ['knowledge_base_id'])

    # 3. Create HNSW Cosine vector index on embedding column
    op.execute(
        """
        CREATE INDEX idx_chunks_embedding_hnsw ON document_chunks 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_chunks_embedding_hnsw;")
    op.drop_table('document_chunks')
    op.drop_table('documents')
