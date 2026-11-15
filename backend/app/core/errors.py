"""Application error hierarchy and FastAPI exception handlers."""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    """Base class for all application errors."""

    http_status: int = 500

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        *,
        code: str = "internal_error",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details: dict[str, Any] = details or {}
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class NotFoundError(AppError):
    http_status = 404

    def __init__(self, message: str = "Resource not found.", **kwargs: Any) -> None:
        super().__init__(message, code="not_found", **kwargs)


class ForbiddenError(AppError):
    http_status = 403

    def __init__(self, message: str = "Access forbidden.", **kwargs: Any) -> None:
        super().__init__(message, code="forbidden", **kwargs)


class UnauthorizedError(AppError):
    http_status = 401

    def __init__(self, message: str = "Authentication required.", **kwargs: Any) -> None:
        super().__init__(message, code="unauthorized", **kwargs)


class ConflictError(AppError):
    http_status = 409

    def __init__(self, message: str = "Resource conflict.", **kwargs: Any) -> None:
        super().__init__(message, code="conflict", **kwargs)


class ValidationError(AppError):
    http_status = 422

    def __init__(self, message: str = "Validation failed.", **kwargs: Any) -> None:
        super().__init__(message, code="validation_error", **kwargs)


class RateLimitError(AppError):
    http_status = 429

    def __init__(self, message: str = "Rate limit exceeded. Please try again later.", **kwargs: Any) -> None:
        super().__init__(message, code="rate_limited", **kwargs)


# ── FastAPI exception handler ────────────────────────────────────────────────

from fastapi import Request
from fastapi.responses import JSONResponse


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status,
        content=exc.to_dict(),
    )
