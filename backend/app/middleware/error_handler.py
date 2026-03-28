"""
Error handling middleware and custom exceptions.
"""

import uuid
import traceback
from datetime import datetime
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================


class APIError(Exception):
    """Base API error."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type: str = "api_error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.details = details or {}


class ValidationError(APIError):
    """Validation error."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type="validation_error",
            details=details,
        )


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_type="not_found",
            details=details,
        )


class FileUploadError(APIError):
    """File upload error."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type="file_upload_error",
            details=details,
        )


class ModelError(APIError):
    """ML model error."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_type="model_error",
            details=details,
        )


# ============================================================================
# Error Handler Middleware
# ============================================================================


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling all exceptions and returning consistent error responses."""

    async def dispatch(self, request: Request, call_next):
        """Process request and handle any exceptions."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            return response

        except APIError as exc:
            logger.warning(
                "API error",
                error_type=exc.error_type,
                message=exc.message,
                status_code=exc.status_code,
                request_id=request_id,
                path=request.url.path,
            )
            return self._create_error_response(
                error_type=exc.error_type,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
                request_id=request_id,
            )

        except Exception as exc:
            logger.error(
                "Unhandled exception",
                error=str(exc),
                traceback=traceback.format_exc(),
                request_id=request_id,
                path=request.url.path,
            )
            return self._create_error_response(
                error_type="internal_server_error",
                message="An unexpected error occurred",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"exception": str(exc)} if logger.isEnabledFor(10) else None,
                request_id=request_id,
            )

    def _create_error_response(
        self,
        error_type: str,
        message: str,
        status_code: int,
        details: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> JSONResponse:
        """Create a standardized error response."""
        return JSONResponse(
            status_code=status_code,
            content={
                "error": error_type,
                "message": message,
                "details": details,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
            },
        )
