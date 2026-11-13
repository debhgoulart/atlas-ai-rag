"""Main FastAPI application initialization and entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup tasks (e.g. verify db connection or AI client)
    yield
    # Shutdown tasks (e.g. cleanup connections)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Full Stack RAG Knowledge Base and Chatbot API",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS Middleware for Frontend SPA
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom exception handlers
register_exception_handlers(app)

# Mount API v1 router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["System"])
async def root() -> dict:
    """Root redirect / information endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api_v1": "/api/v1",
    }
