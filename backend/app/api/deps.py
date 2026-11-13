"""FastAPI dependencies for authentication and database sessions."""

import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.auth import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.services.gemini_credential_service import GeminiCredentialService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate Bearer JWT token and return the authenticated User entity."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária. Token de acesso ausente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise ValueError("Token missing subject claim")
        user_id = uuid.UUID(user_id_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário associado ao token não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta de usuário desativada.",
        )

    return user


async def get_user_gemini_api_key(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> str:
    """Retrieve and decrypt the authenticated user's Gemini API Key.
    
    Raises HTTP 403 Forbidden if user has no valid key configured.
    """
    credential_service = GeminiCredentialService()
    decrypted_key = await credential_service.get_decrypted_key(db=db, user_id=current_user.id)
    if not decrypted_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação de IA bloqueada. Você precisa cadastrar uma Gemini API Key válida para continuar.",
        )
    return decrypted_key

