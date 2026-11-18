"""Move pgvector extension from public to extensions schema

Revision ID: 0008_move_vector_extension_schema
Revises: 0007_enable_rls_security
Create Date: 2026-11-18 14:05:00.000000

Context:
Resolves Supabase Security Advisor warning `extension_in_public` (0014) by
relocating the `vector` (pgvector) extension out of the `public` schema into
the dedicated `extensions` schema, while ensuring `extensions` is present in
`search_path` so unqualified `vector` types and operators (`<=>`) continue to
resolve seamlessly in SQLAlchemy/pgvector queries.
"""

from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0008_move_vector_extension_schema"
down_revision: Union[str, None] = "0007_enable_rls_security"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS extensions")

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_extension e
                JOIN pg_namespace n ON n.oid = e.extnamespace
                WHERE e.extname = 'vector' AND n.nspname = 'public'
            ) THEN
                ALTER EXTENSION vector SET SCHEMA extensions;
            END IF;

            IF position('extensions' in current_setting('search_path')) = 0 THEN
                EXECUTE format(
                    'ALTER ROLE %I SET search_path TO "$user", public, extensions',
                    current_user
                );
                PERFORM set_config('search_path', '"$user", public, extensions', false);
            END IF;
        END $$
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_extension e
                JOIN pg_namespace n ON n.oid = e.extnamespace
                WHERE e.extname = 'vector' AND n.nspname = 'extensions'
            ) THEN
                ALTER EXTENSION vector SET SCHEMA public;
            END IF;
        END $$
        """
    )
