#!/usr/bin/env python3
"""CLI utility to rotate CREDENTIALS_ENCRYPTION_KEY by re-encrypting all user credentials."""

import argparse
import asyncio
import sys
from sqlalchemy import select

from app.core.security.encryption import EncryptionService
from app.db.session import AsyncSessionLocal
from app.models.user_gemini_credential import UserGeminiCredential
from app.schemas.gemini_credential import ApiKeyStatus


async def rotate_keys(old_key: str, new_key: str) -> None:
    """Re-encrypt all stored credentials from old_key to new_key."""
    old_service = EncryptionService(master_key=old_key)
    new_service = EncryptionService(master_key=new_key)

    async with AsyncSessionLocal() as db:
        stmt = select(UserGeminiCredential).where(
            UserGeminiCredential.status == ApiKeyStatus.VALID.value
        )
        result = await db.execute(stmt)
        credentials = result.scalars().all()

        print(f"Encontradas {len(credentials)} credenciais válidas para rotação.")
        count = 0
        for cred in credentials:
            try:
                decrypted_secret = old_service.decrypt(cred.encrypted_api_key)
                cred.encrypted_api_key = new_service.encrypt(decrypted_secret)
                count += 1
            except Exception as exc:
                print(f"[ERRO] Falha ao rotacionar credencial {cred.id} do usuário {cred.user_id}: {exc}")

        await db.commit()
        print(f"[SUCESSO] Rotação concluída! {count}/{len(credentials)} credenciais recriptografadas.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rotaciona a chave mestra de criptografia do Atlas AI.")
    parser.add_argument("--old-key", required=True, help="Chave mestra de criptografia anterior (Fernet base64)")
    parser.add_argument("--new-key", required=True, help="Nova chave mestra de criptografia (Fernet base64)")

    args = parser.parse_args()

    try:
        asyncio.run(rotate_keys(args.old_key, args.new_key))
    except Exception as exc:
        print(f"[FALHA] Erro durante o processo de rotação: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
