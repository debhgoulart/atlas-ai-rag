"""API endpoints for managing user's encrypted Gemini API Key and status."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.gemini_credential import (
    GeminiKeyCreateRequest,
    GeminiKeyStatusResponse,
)
from app.services.gemini_credential_service import GeminiCredentialService

router = APIRouter(prefix="/settings/gemini-key", tags=["Gemini Credentials"])

_credential_service = GeminiCredentialService()


@router.get(
    "/status",
    response_model=GeminiKeyStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's Gemini API Key status",
)
async def get_key_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GeminiKeyStatusResponse:
    """Return status (NOT_CONFIGURED, VALID, INVALID) and masked hint without exposing secret."""
    return await _credential_service.get_status(db=db, user_id=current_user.id)


@router.post(
    "",
    response_model=GeminiKeyStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Register or replace Gemini API Key",
)
async def register_gemini_key(
    payload: GeminiKeyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GeminiKeyStatusResponse:
    """Validate candidate key with Google Gemini, encrypt symmetrically, and save for user."""
    return await _credential_service.save_and_validate_key(
        db=db,
        user_id=current_user.id,
        raw_api_key=payload.api_key,
    )


@router.delete(
    "",
    response_model=GeminiKeyStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete stored Gemini API Key",
)
async def delete_gemini_key(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GeminiKeyStatusResponse:
    """Remove stored Gemini key and reset credential status to NOT_CONFIGURED."""
    return await _credential_service.delete_key(db=db, user_id=current_user.id)
