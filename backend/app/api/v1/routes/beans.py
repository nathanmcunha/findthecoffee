"""Coffee Bean API routes."""
import logging
import uuid
from typing import Any
from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app.core.dependencies import container
from app.core.errors import NotFoundError
from app.api.v1.schemas.bean import BeanCreate, BeanSearchParams
from app.auth import require_api_key

logger = logging.getLogger(__name__)

# Blueprint configuration
beans_bp = Blueprint("beans", __name__, url_prefix="/beans")


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


@beans_bp.route("", methods=["GET"])
def list_beans():
    """List all beans with optional filters and pagination."""
    try:
        params = BeanSearchParams.model_validate(request.args.to_dict())
        offset = (params.page - 1) * params.per_page

        beans = container.bean_service.search(
            roast_level=params.roast,
            origin=params.origin,
            roaster_id=params.roaster_id,
            variety=params.variety,
            processing=params.processing,
            region=params.region,
            limit=params.per_page,
            offset=offset,
        )

        return jsonify({
            "data": beans,
            "page": params.page,
            "per_page": params.per_page,
        }), 200

    except ValidationError as e:
        return jsonify({
            "error": "Invalid filter parameters",
            "details": _validation_errors(e),
        }), 400
    except Exception as e:
        logger.exception("Error in list_beans")
        return jsonify({"error": "An internal error occurred"}), 500


@beans_bp.route("/<uuid:bean_id>", methods=["GET"])
def get_bean(bean_id: uuid.UUID):
    """Get a single coffee bean by ID."""
    try:
        bean = container.bean_service.get_by_id(bean_id)
        return jsonify(bean), 200

    except NotFoundError as e:
        return jsonify({"error": e.message}), 404
    except Exception as e:
        logger.exception("Error in get_bean id=%s", bean_id)
        return jsonify({"error": "An internal error occurred"}), 500


@beans_bp.route("", methods=["POST"])
@require_api_key
def create_bean():
    """Create a new coffee bean."""
    try:
        data: dict[str, Any] = request.get_json(silent=True) or {}
        bean_data = BeanCreate.model_validate(data)

        bean_id = container.bean_service.create(
            name=bean_data.name,
            roaster_id=bean_data.roaster_id,
            roast_level=bean_data.roast_level,
            origin=bean_data.origin,
            variety=bean_data.variety,
            processing=bean_data.processing,
            altitude=bean_data.altitude,
            producer=bean_data.producer,
            farm=bean_data.farm,
            region=bean_data.region,
            tasting_notes=bean_data.tasting_notes,
            acidity=bean_data.acidity,
            sweetness=bean_data.sweetness,
            body=bean_data.body,
        )

        return jsonify({
            "id": str(bean_id),
            "status": "created",
        }), 201

    except ValidationError as e:
        return jsonify({
            "error": "Validation Error",
            "details": _validation_errors(e),
        }), 400
    except Exception as e:
        logger.exception("Error in create_bean")
        return jsonify({"error": "An internal error occurred"}), 500
