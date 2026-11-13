"""Service for validating, encrypting, and managing user-specific Gemini API Keys."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException, status
from google import genai
from google.genai import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security.encryption import EncryptionService
from app.models.user_gemini_credential import UserGeminiCredential
from app.schemas.gemini_credential import ApiKeyStatus, GeminiKeyStatusResponse


class GeminiCredentialService:
    """Service handling lifecycle, validation, and encryption of Gemini API Keys."""

    def __init__(self, encryption_service: Optional[EncryptionService] = None) -> None:
        if encryption_service is not None:
            self.encryption_service = encryption_service
        else:
            # If not configured in environment, use or create a deterministic dev key
            try:
                self.encryption_service = EncryptionService()
            except Exception:
                # Fallback master key for local development when CREDENTIALS_ENCRYPTION_KEY is unset
                dev_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
                self.encryption_service = EncryptionService(master_key=dev_key)

    def validate_key_with_gemini(self, api_key: str) -> bool:
        """Validate candidate key against Google Gemini API metadata endpoint without token cost."""
        if not api_key or len(api_key) < 15:
            return False
        try:
            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(api_version=settings.GEMINI_API_VERSION),
            )
            # Query model metadata - lightweight GET that consumes zero generation tokens
            client.models.get(model=settings.GEMINI_CHAT_MODEL)
            return True
        except Exception:
            return False

    async def save_and_validate_key(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        raw_api_key: str,
    ) -> GeminiKeyStatusResponse:
        """Validate key with Google, encrypt, and persist to database for user."""
        clean_key = raw_api_key.strip()
        is_valid = self.validate_key_with_gemini(clean_key)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A Gemini API Key informada é inválida ou não tem permissão para acessar os modelos do Gemini.",
            )

        encrypted_key = self.encryption_service.encrypt(clean_key)
        hint = f"...{clean_key[-4:]}"
        now = datetime.now(timezone.utc)

        stmt = select(UserGeminiCredential).where(UserGeminiCredential.user_id == user_id)
        result = await db.execute(stmt)
        credential = result.scalar_one_or_none()

        if credential:
            credential.encrypted_api_key = encrypted_key
            credential.key_hint = hint
            credential.status = ApiKeyStatus.VALID.value
            credential.last_validated_at = now
        else:
            credential = UserGeminiCredential(
                user_id=user_id,
                encrypted_api_key=encrypted_key,
                key_hint=hint,
                status=ApiKeyStatus.VALID.value,
                last_validated_at=now,
            )
            db.add(credential)

        await db.commit()
        await db.refresh(credential)

        return GeminiKeyStatusResponse(
            status=ApiKeyStatus.VALID,
            key_hint=credential.key_hint,
            last_validated_at=credential.last_validated_at,
            updated_at=credential.updated_at,
        )

    async def get_status(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> GeminiKeyStatusResponse:
        """Return safe status payload for user without exposing decrypted secret."""
        stmt = select(UserGeminiCredential).where(UserGeminiCredential.user_id == user_id)
        result = await db.execute(stmt)
        credential = result.scalar_one_or_none()

        if not credential or credential.status == ApiKeyStatus.NOT_CONFIGURED.value:
            return GeminiKeyStatusResponse(status=ApiKeyStatus.NOT_CONFIGURED)

        return GeminiKeyStatusResponse(
            status=ApiKeyStatus(credential.status),
            key_hint=credential.key_hint,
            last_validated_at=credential.last_validated_at,
            updated_at=credential.updated_at,
        )

    async def get_decrypted_key(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> Optional[str]:
        """Retrieve and decrypt key in memory for RAG pipeline usage."""
        stmt = select(UserGeminiCredential).where(UserGeminiCredential.user_id == user_id)
        result = await db.execute(stmt)
        credential = result.scalar_one_or_none()

        if not credential or credential.status != ApiKeyStatus.VALID.value or not credential.encrypted_api_key:
            return None

        try:
            return self.encryption_service.decrypt(credential.encrypted_api_key)
        except Exception:
            # Mark credential as invalid if decryption fails (e.g. key rotation mismatch)
            credential.status = ApiKeyStatus.INVALID.value
            await db.commit()
            return None

    async def mark_key_invalid(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> None:
        """Mark stored key as INVALID upon Google API authentication failure in runtime."""
        stmt = select(UserGeminiCredential).where(UserGeminiCredential.user_id == user_id)
        result = await db.execute(stmt)
        credential = result.scalar_one_or_none()
        if credential:
            credential.status = ApiKeyStatus.INVALID.value
            await db.commit()

    async def delete_key(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> GeminiKeyStatusResponse:
        """Remove user's stored key and reset status to NOT_CONFIGURED."""
        stmt = select(UserGeminiCredential).where(UserGeminiCredential.user_id == user_id)
        result = await db.execute(stmt)
        credential = result.scalar_one_or_none()

        if credential:
            await db.delete(credential)
            await db.commit()

        return GeminiKeyStatusResponse(status=ApiKeyStatus.NOT_CONFIGURED)
