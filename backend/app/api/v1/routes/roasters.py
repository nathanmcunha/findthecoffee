"""Roaster API routes."""
import logging
import uuid
from typing import Any
from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app.core.dependencies import container
from app.core.errors import NotFoundError
from app.api.v1.schemas.roaster import RoasterCreate, RoasterSearchParams
from app.auth import require_api_key

logger = logging.getLogger(__name__)

# Blueprint configuration
roasters_bp = Blueprint("roasters", __name__, url_prefix="/roasters")


def _validation_errors(e: ValidationError) -> list[Any]:
    """Convert Pydantic validation errors to JSON-serializable format."""
    errors = e.errors(include_url=False)
    for err in errors:
        ctx = err.get("ctx")
        if ctx:
            error = ctx.get("error")
            if isinstance(error, Exception):
                ctx["error"] = str(error)
    return errors


@roasters_bp.route("", methods=["GET"])
def list_roasters():
    """List all roasters with optional pagination."""
    try:
        params = RoasterSearchParams.model_validate(request.args.to_dict())
        offset = (params.page - 1) * params.per_page

        roasters = container.roaster_service.get_all(
            limit=params.per_page,
            offset=offset,
        )

        return jsonify({
            "data": roasters,
            "page": params.page,
            "per_page": params.per_page,
        }), 200

    except ValidationError as e:
        return jsonify({
            "error": "Invalid filter parameters",
            "details": _validation_errors(e),
        }), 400
    except Exception as e:
        logger.exception("Error in list_roasters")
        return jsonify({"error": "An internal error occurred"}), 500


@roasters_bp.route("/<uuid:roaster_id>", methods=["GET"])
def get_roaster(roaster_id: uuid.UUID):
    """Get a single roaster by ID."""
    try:
        roaster = container.roaster_service.get_by_id(roaster_id)
        return jsonify(roaster), 200

    except NotFoundError as e:
        return jsonify({"error": e.message}), 404
    except Exception as e:
        logger.exception("Error in get_roaster id=%s", roaster_id)
        return jsonify({"error": "An internal error occurred"}), 500


@roasters_bp.route("", methods=["POST"])
@require_api_key
def create_roaster():
    """Create a new roaster."""
    try:
        data: dict[str, Any] = request.get_json(silent=True) or {}
        roaster_data = RoasterCreate.model_validate(data)

        roaster_id = container.roaster_service.create(
            name=roaster_data.name,
            website=roaster_data.website,
            location=roaster_data.location,
        )

        return jsonify({
            "id": str(roaster_id),
            "status": "created",
        }), 201

    except ValidationError as e:
        return jsonify({
            "error": "Validation Error",
            "details": _validation_errors(e),
        }), 400
    except Exception as e:
        logger.exception("Error in create_roaster")
        return jsonify({"error": "An internal error occurred"}), 500
