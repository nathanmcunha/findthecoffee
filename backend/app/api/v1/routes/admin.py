"""Admin API routes for curation and internal management."""
import logging
import uuid
from typing import Any
from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app.core.dependencies import container
from app.core.errors import NotFoundError
from app.api.v1.schemas.admin import CurationUpdate
from app.auth import require_api_key

logger = logging.getLogger(__name__)

# Blueprint configuration
admin_bp = Blueprint("admin", __name__, url_prefix="/admin/v1")


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


@admin_bp.route("/cafes/<uuid:cafe_id>/curation", methods=["PATCH"])
@require_api_key
def update_cafe_curation(cafe_id: uuid.UUID):
    """Update curation fields on a cafe.

    All fields optional — partial updates supported.
    """
    try:
        data: dict[str, Any] = request.get_json(silent=True) or {}
        curation = CurationUpdate.model_validate(data)

        result = container.cafe_service.update_curation(
            cafe_id=cafe_id,
            is_curator_pick=curation.is_curator_pick,
            source_attribution=curation.source_attribution,
        )

        return jsonify({
            "status": "updated",
            "id": str(result["id"]),
            "is_curator_pick": result["is_curator_pick"],
            "source_attribution": result["source_attribution"],
        }), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation Error",
            "details": _validation_errors(e),
        }), 400
    except NotFoundError as e:
        return jsonify({"error": e.message}), 404
    except Exception as e:
        logger.exception("Error in update_cafe_curation id=%s", cafe_id)
        return jsonify({"error": "An internal error occurred"}), 500


@admin_bp.route("/roasters/<uuid:roaster_id>/curation", methods=["PATCH"])
@require_api_key
def update_roaster_curation(roaster_id: uuid.UUID):
    """Update curation fields on a roaster.

    All fields optional — partial updates supported.
    """
    try:
        data: dict[str, Any] = request.get_json(silent=True) or {}
        curation = CurationUpdate.model_validate(data)

        result = container.roaster_service.update_curation(
            roaster_id=roaster_id,
            is_curator_pick=curation.is_curator_pick,
            source_attribution=curation.source_attribution,
        )

        return jsonify({
            "status": "updated",
            "id": str(result["id"]),
            "is_curator_pick": result["is_curator_pick"],
            "source_attribution": result["source_attribution"],
        }), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation Error",
            "details": _validation_errors(e),
        }), 400
    except NotFoundError as e:
        return jsonify({"error": e.message}), 404
    except Exception as e:
        logger.exception("Error in update_roaster_curation id=%s", roaster_id)
        return jsonify({"error": "An internal error occurred"}), 500