"""Authentication utilities."""
import functools
import logging
import os
from collections.abc import Callable
from typing import ParamSpec

from flask import jsonify, request
from flask.typing import ResponseReturnValue

logger = logging.getLogger(__name__)

_P = ParamSpec("_P")


def require_api_key(
    f: Callable[_P, ResponseReturnValue],
) -> Callable[_P, ResponseReturnValue]:
    """Decorator that enforces X-API-Key header on mutating endpoints."""

    @functools.wraps(f)
    def decorated(*args: _P.args, **kwargs: _P.kwargs) -> ResponseReturnValue:
        api_key = os.getenv("API_KEY")
        if not api_key:
            logger.error("API_KEY environment variable is not configured")
            return jsonify({"error": "Service misconfigured"}), 503
        if request.headers.get("X-API-Key") != api_key:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated
