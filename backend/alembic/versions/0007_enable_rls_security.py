"""Enable Row Level Security (RLS) on all public tables for Supabase PostgREST hardening

Revision ID: 0007_enable_rls_security
Revises: 0006_multi_tenant_isolation
Create Date: 2026-11-18 13:41:00.000000

Context:
Atlas AI accesses PostgreSQL exclusively through the FastAPI backend using
SQLAlchemy (direct database connection as the table owner / postgres role),
and does NOT expose tables directly to clients via Supabase PostgREST.

Enabling RLS without permissive policies enforces a default-deny posture for
Supabase's PostgREST roles (anon, authenticated), resolving the Supabase
Security Advisor `rls_disabled_in_public` error while keeping backend access
(table owner / BYPASSRLS role) unaffected. Note that FORCE ROW LEVEL SECURITY
is intentionally NOT enabled so the backend connection continues operating
normally.
"""

from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0007_enable_rls_security"
down_revision: Union[str, None] = "0006_multi_tenant_isolation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PUBLIC_TABLES: tuple[str, ...] = (
    "alembic_version",
    "users",
    "user_gemini_credentials",
    "knowledge_bases",
    "documents",
    "document_chunks",
    "chat_sessions",
    "chat_messages",
)


def upgrade() -> None:
    for table in PUBLIC_TABLES:
        op.execute(f"ALTER TABLE IF EXISTS public.{table} ENABLE ROW LEVEL SECURITY")

    # Defense-in-depth: revoke direct PostgREST role privileges if running on Supabase
    op.execute(
        """
        DO $$
        DECLARE
            tbl text;
            target_tables text[] := ARRAY[
                'alembic_version',
                'users',
                'user_gemini_credentials',
                'knowledge_bases',
                'documents',
                'document_chunks',
                'chat_sessions',
                'chat_messages'
            ];
        BEGIN
            FOREACH tbl IN ARRAY target_tables LOOP
                IF to_regclass(format('public.%I', tbl)) IS NOT NULL THEN
                    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                        EXECUTE format('REVOKE ALL ON TABLE public.%I FROM anon', tbl);
                    END IF;
                    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                        EXECUTE format('REVOKE ALL ON TABLE public.%I FROM authenticated', tbl);
                    END IF;
                END IF;
            END LOOP;
        END $$
        """
    )


def downgrade() -> None:
    for table in reversed(PUBLIC_TABLES):
        op.execute(f"ALTER TABLE IF EXISTS public.{table} DISABLE ROW LEVEL SECURITY")
