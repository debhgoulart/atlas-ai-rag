"""Standardized error exceptions and handlers for Atlas AI Backend."""

from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AtlasException(Exception):
    """Base exception class for all Atlas AI domain exceptions."""

    def __init__(
        self,
        detail: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.code = code
        self.status_code = status_code
        self.context = context or {}


class EntityNotFoundException(AtlasException):
    """Exception raised when a requested resource does not exist."""

    def __init__(self, entity_name: str, identifier: Any) -> None:
        super().__init__(
            detail=f"{entity_name} with identifier '{identifier}' was not found.",
            code="ENTITY_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            context={"entity": entity_name, "identifier": str(identifier)},
        )


class DuplicateEntityException(AtlasException):
    """Exception raised when attempting to create an entity with conflicting unique fields."""

    def __init__(self, entity_name: str, field: str, value: Any) -> None:
        super().__init__(
            detail=f"{entity_name} with {field} '{value}' already exists.",
            code="DUPLICATE_ENTITY",
            status_code=status.HTTP_400_BAD_REQUEST,
            context={"entity": entity_name, "field": field, "value": str(value)},
        )


class DocumentValidationException(AtlasException):
    """Exception raised when an uploaded document fails validation."""

    def __init__(self, message: str, code: str = "DOCUMENT_VALIDATION_ERROR") -> None:
        super().__init__(
            detail=message,
            code=code,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class AIServiceException(AtlasException):
    """Exception raised when external AI services (e.g. Gemini API) fail or rate-limit."""

    def __init__(self, message: str, code: str = "AI_SERVICE_ERROR") -> None:
        super().__init__(
            detail=message,
            code=code,
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI application."""

    @app.exception_handler(AtlasException)
    async def atlas_exception_handler(_: Request, exc: AtlasException) -> JSONResponse:
        content = {
            "detail": exc.detail,
            "code": exc.code,
        }
        if exc.context:
            content["context"] = exc.context
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        message = errors[0].get("msg") if errors else "Validation error"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": f"Payload validation error: {message}",
                "code": "VALIDATION_ERROR",
                "errors": errors,
            },
        )
