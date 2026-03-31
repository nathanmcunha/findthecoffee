"""Cafe API routes."""
import logging
import uuid
from typing import Any
from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app.core.dependencies import container
from app.core.errors import NotFoundError
from app.api.v1.schemas.cafe import (
    CafeCreate,
    CafeSearchParams,
    CafeInventoryAdd,
    NearbySearchParams,
)
from app.auth import require_api_key

logger = logging.getLogger(__name__)

# Blueprint configuration
cafes_bp = Blueprint("cafes", __name__, url_prefix="/cafes")


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


@cafes_bp.route("", methods=["GET"])
def list_cafes():
    """List all cafes with optional filters and pagination."""
    try:
        params = CafeSearchParams.model_validate(request.args.to_dict())
        offset = (params.page - 1) * params.per_page

        cafes = container.cafe_service.search(
            roast_level=params.roast,
            origin=params.origin,
            roaster_id=params.roaster_id,
            cafe_name=params.name,
            query_text=params.q,
            limit=params.per_page,
            offset=offset,
        )

        return jsonify({
            "data": cafes,
            "page": params.page,
            "per_page": params.per_page,
        }), 200

    except ValidationError as e:
        return jsonify({
            "error": "Invalid filter parameters",
            "details": _validation_errors(e),
        }), 400
    except Exception as e:
        logger.exception("Error in list_cafes")
        return jsonify({"error": "An internal error occurred"}), 500


@cafes_bp.route("", methods=["POST"])
@require_api_key
def create_cafe():
    """Create a new cafe."""
    try:
        data: dict[str, Any] = request.get_json(silent=True) or {}
        cafe_data = CafeCreate.model_validate(data)

        cafe_id = container.cafe_service.create(
            name=cafe_data.name,
            location=cafe_data.location,
            website=cafe_data.website,
        )

        return jsonify({
            "status": "created",
            "id": str(cafe_id),
        }), 201

    except ValidationError as e:
        return jsonify({
            "error": "Validation Error",
            "details": _validation_errors(e),
        }), 400
    except Exception as e:
        logger.exception("Error in create_cafe")
        return jsonify({"error": "An internal error occurred"}), 500


@cafes_bp.route("/nearby", methods=["GET"])
def search_nearby():
    """Search cafes near a location."""
    try:
        params = NearbySearchParams.model_validate(request.args.to_dict())

        cafes = container.cafe_service.search_nearby(
            lat=params.lat,
            lng=params.lng,
            radius_m=params.radius,
        )

        return jsonify(cafes), 200

    except ValidationError as e:
        return jsonify({
            "error": "Invalid filter parameters",
            "details": _validation_errors(e),
        }), 400
    except Exception as e:
        logger.exception("Error in search_nearby")
        return jsonify({"error": "An internal error occurred"}), 500


@cafes_bp.route("/<uuid:cafe_id>", methods=["GET"])
def get_cafe(cafe_id: uuid.UUID):
    """Get a single cafe by ID."""
    try:
        cafe = container.cafe_service.get_by_id(cafe_id)
        return jsonify(cafe), 200

    except NotFoundError as e:
        return jsonify({"error": e.message}), 404
    except Exception as e:
        logger.exception("Error in get_cafe id=%s", cafe_id)
        return jsonify({"error": "An internal error occurred"}), 500


@cafes_bp.route("/<uuid:cafe_id>/inventory", methods=["GET"])
def get_cafe_inventory(cafe_id: uuid.UUID):
    """Get cafe's coffee bean inventory."""
    try:
        inventory = container.cafe_service.get_inventory(cafe_id)
        return jsonify(inventory), 200

    except NotFoundError as e:
        return jsonify({"error": e.message}), 404
    except Exception as e:
        logger.exception("Error in get_cafe_inventory id=%s", cafe_id)
        return jsonify({"error": "An internal error occurred"}), 500


@cafes_bp.route("/<uuid:cafe_id>/inventory", methods=["POST"])
@require_api_key
def add_to_inventory(cafe_id: uuid.UUID):
    """Add a coffee bean to cafe inventory."""
    try:
        data: dict[str, Any] = request.get_json(silent=True) or {}
        inventory_data = CafeInventoryAdd.model_validate(data)

        container.cafe_service.add_to_inventory(cafe_id, inventory_data.bean_id)

        return jsonify({
            "status": "success",
            "message": "Added to inventory",
        }), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation Error",
            "details": _validation_errors(e),
        }), 400
    except NotFoundError as e:
        return jsonify({"error": e.message}), 404
    except Exception as e:
        logger.exception("Error in add_to_inventory cafe_id=%s", cafe_id)
        return jsonify({"error": "An internal error occurred"}), 500