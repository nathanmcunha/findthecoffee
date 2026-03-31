"""Centralized error handling and HTTP exceptions."""
from dataclasses import dataclass
from typing import Any
from flask import jsonify
from flask.typing import ResponseReturnValue


@dataclass
class ErrorResponse:
    """Standard error response format."""
    error: str
    message: str | None = None
    details: list[dict[str, Any]] | None = None


class AppException(Exception):
    """Base exception for application-specific errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str | None = None,
        details: Any | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppException):
    """Resource not found."""
    def __init__(self, resource: str, identifier: str | None = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class ValidationError(AppException):
    """Request validation failed."""
    def __init__(self, details: list[dict[str, Any]] | None = None):
        super().__init__(
            "Validation Error",
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class UnauthorizedError(AppException):
    """Authentication required."""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED")


class ForbiddenError(AppException):
    """Access denied."""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403, error_code="FORBIDDEN")


class ConflictError(AppException):
    """Resource conflict (e.g., duplicate)."""
    def __init__(self, message: str = "Conflict"):
        super().__init__(message, status_code=409, error_code="CONFLICT")


class ServiceUnavailableError(AppException):
    """Service temporarily unavailable."""
    def __init__(self, message: str = "Service unavailable"):
        super().__init__(
            message,
            status_code=503,
            error_code="SERVICE_UNAVAILABLE"
        )


def create_error_response(
    error: str,
    message: str | None = None,
    details: Any | None = None,
) -> tuple[ResponseReturnValue, int]:
    """Create a standardized JSON error response."""
    response = {"error": error}
    if message:
        response["message"] = message
    if details:
        response["details"] = details
    return jsonify(response), get_status_code(error)


def get_status_code(error_code: str) -> int:
    """Map error code to HTTP status code."""
    mapping = {
        "VALIDATION_ERROR": 400,
        "UNAUTHORIZED": 401,
        "FORBIDDEN": 403,
        "NOT_FOUND": 404,
        "CONFLICT": 409,
        "SERVICE_UNAVAILABLE": 503,
    }
    return mapping.get(error_code, 500)