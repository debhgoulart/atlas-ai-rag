"""API v1 master router aggregating all sub-routers."""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.documents import router as doc_router
from app.api.v1.gemini_credentials import router as gemini_router
from app.api.v1.knowledge_bases import router as kb_router

api_router = APIRouter()

# System endpoints
@api_router.get("/health", tags=["System"])
async def health_check() -> dict:
    """Health check endpoint to verify backend operational status."""
    return {"status": "ok", "service": "Atlas AI Backend", "version": "0.1.0"}

# Feature endpoints
api_router.include_router(auth_router)
api_router.include_router(gemini_router)
api_router.include_router(kb_router)
api_router.include_router(doc_router)
api_router.include_router(chat_router)
