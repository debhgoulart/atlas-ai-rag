"""Database reset and zero-state sanitization script.

Truncates all application tables (knowledge_bases, documents, document_chunks,
chat_sessions, chat_messages) with CASCADE, leaving the database completely clean
while preserving the PostgreSQL schema, Alembic migration history, and pgvector extension.
"""

import asyncio
import sys
from sqlalchemy import text
from app.db.session import engine


async def reset_database() -> None:
    """Safely truncate all data tables to zero-state."""
    print("=" * 60)
    print("  Atlas AI — Sanitização de Base de Dados (Zero-State)")
    print("=" * 60)
    print("Conectando ao banco de dados...")

    tables = [
        "chat_messages",
        "chat_sessions",
        "document_chunks",
        "documents",
        "knowledge_bases",
    ]

    try:
        async with engine.begin() as conn:
            # Check existing tables and truncate
            for table in tables:
                print(f"-> Truncando tabela: {table} (CASCADE)...")
                await conn.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))

            print("\n[OK] Todas as tabelas de dados foram limpas com sucesso!")
            print("Extensão pgvector e migrações do Alembic preservadas.")
            print("A base de dados está em estado zero (limpa e pronta para uso).")
    except Exception as exc:
        print(f"\n[AVISO] Não foi possível conectar ou truncar as tabelas: {exc}")
        print("Certifique-se de que o container PostgreSQL está em execução (docker compose up -d db).")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_database())
