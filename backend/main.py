import functools
import logging
import os
import uuid
from collections.abc import Callable
from typing import ParamSpec
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask.typing import ResponseReturnValue
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydantic import BaseModel, Field, ValidationError, field_validator
from pydantic_core import ErrorDetails

from db.repository import CafeRepository, CoffeeBeanRepository, RoasterRepository


def _validation_errors(e: ValidationError) -> list[ErrorDetails]:
    """Return Pydantic v2 errors as a JSON-serializable list.

    field_validator errors embed the raw exception in ctx['error'], which is
    not JSON-serializable. We stringify it so Flask can serialize the response.
    """
    errors = e.errors(include_url=False)
    for err in errors:
        ctx = err.get("ctx")
        if ctx:
            error = ctx.get("error")
            if isinstance(error, Exception):
                ctx["error"] = str(error)
    return errors


# Load variables from .env file
_ = load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS — restrict to configured origins; default wildcard is only safe for local dev
_cors_origins = os.getenv("CORS_ORIGINS", "*")
if _cors_origins == "*":
    logger.warning(
        "CORS_ORIGINS not set — allowing all origins. Set CORS_ORIGINS in production."
    )
_ = CORS(app, resources={r"/api/*": {"origins": _cors_origins}})

# Rate limiting — in-memory storage, configurable via RATELIMIT_STORAGE_URI
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "60 per hour"],
    storage_uri=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
)

cafe_repo = CafeRepository()
bean_repo = CoffeeBeanRepository()
roaster_repo = RoasterRepository()


_P = ParamSpec("_P")


# ============== AUTH ==============


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


# ============== PYDANTIC MODELS ==============


class RoasterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    website: str | None = Field(default=None, max_length=500)
    location: str | None = Field(default=None, max_length=200)

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: str | None) -> str | None:
        if v is not None and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("website must start with http:// or https://")
        return v


class RoasterSearchParams(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=100)


class CafeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    website: str | None = Field(default=None, max_length=500)

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: str | None) -> str | None:
        if v is not None and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("website must start with http:// or https://")
        return v


class CafeSearchParams(BaseModel):
    roast: str | None = Field(default=None, max_length=50)
    origin: str | None = Field(default=None, max_length=100)
    roaster_id: uuid.UUID | None = None
    name: str | None = Field(default=None, max_length=200)
    q: str | None = Field(default=None, max_length=200)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=100)


class CafeInventoryAdd(BaseModel):
    bean_id: uuid.UUID


class BeanSearchParams(BaseModel):
    roast: str | None = Field(default=None, max_length=50)
    origin: str | None = Field(default=None, max_length=100)
    roaster_id: uuid.UUID | None = None
    variety: str | None = Field(default=None, max_length=100)
    processing: str | None = Field(default=None, max_length=50)
    region: str | None = Field(default=None, max_length=200)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=100)


class BeanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    roaster_id: uuid.UUID | None = None
    roast_level: str | None = Field(default=None, max_length=50)
    origin: str | None = Field(default=None, max_length=100)
    variety: str | None = Field(default=None, max_length=100)
    processing: str | None = Field(default=None, max_length=50)
    altitude: int | None = Field(default=None, ge=0, le=12000)
    producer: str | None = Field(default=None, max_length=200)
    farm: str | None = Field(default=None, max_length=200)
    region: str | None = Field(default=None, max_length=200)
    tasting_notes: list[str] | None = None
    acidity: int | None = Field(default=None, ge=1, le=5)
    sweetness: int | None = Field(default=None, ge=1, le=5)
    body: int | None = Field(default=None, ge=1, le=5)


class NearbySearchParams(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    radius: int = Field(default=5000, ge=100, le=50000)


@app.route("/ping", methods=["GET"])
def ping():
    """Basic health check route."""
    return jsonify({"status": "online", "message": "Coffee Finder API is running"}), 200


# ============== ROASTER ENDPOINTS ==============


@app.route("/api/roasters", methods=["GET"])
def list_roasters():
    """Return a list of all roasters."""
    try:
        params = RoasterSearchParams.model_validate(request.args.to_dict())
        offset = (params.page - 1) * params.per_page

        roasters = roaster_repo.get_all(limit=params.per_page, offset=offset)
        return jsonify({
            "data": roasters,
            "page": params.page,
            "per_page": params.per_page
        }), 200
    except Exception:
        logger.exception("Error in list_roasters")
        return jsonify({"error": "An internal error occurred"}), 500


@app.route("/api/roasters/<uuid:roaster_id>", methods=["GET"])
def get_roaster(roaster_id: uuid.UUID):
    """Return a single roaster by ID."""
    try:
        roaster = roaster_repo.get_by_id(roaster_id)
        if roaster is None:
            return jsonify({"error": "Roaster not found"}), 404
        return jsonify(roaster), 200
    except Exception:
        logger.exception("Error in get_roaster id=%s", roaster_id)
        return jsonify({"error": "An internal error occurred"}), 500


@app.route("/api/roasters", methods=["POST"])
@require_api_key
@limiter.limit("30 per minute")
def add_roaster():
    """Creates a new roaster from a JSON body."""
    try:
        data: dict[str, object] = request.get_json(silent=True) or {}
        roaster_data = RoasterCreate.model_validate(data)

        roaster_id = roaster_repo.create(
            roaster_data.name, roaster_data.website, roaster_data.location
        )
        return jsonify({"id": roaster_id, "status": "created"}), 201
    except ValidationError as e:
        return jsonify(
            {"error": "Validation Error", "details": _validation_errors(e)}
        ), 400
    except Exception:
        logger.exception("Error in add_roaster")
        return jsonify({"error": "An internal error occurred"}), 500


# ============== CAFE ENDPOINTS ==============


@app.route("/api/cafes", methods=["POST"])
@require_api_key
@limiter.limit("30 per minute")
def add_cafe():
    """Creates a new cafe from a JSON body."""
    try:
        data: dict[str, object] = request.get_json(silent=True) or {}
        cafe_data = CafeCreate.model_validate(data)

        cafe_id = cafe_repo.create(
            cafe_data.name, cafe_data.location, cafe_data.website
        )
        return jsonify({"id": cafe_id, "status": "created"}), 201
    except ValidationError as e:
        return jsonify(
            {"error": "Validation Error", "details": _validation_errors(e)}
        ), 400
    except Exception:
        logger.exception("Error in add_cafe")
        return jsonify({"error": "An internal error occurred"}), 500


@app.route("/api/cafes", methods=["GET"])
@limiter.limit("60 per minute")
def list_cafes():
    """Return a list of cafes. Supports discovery filters and global search: ?q=query"""
    try:
        params = CafeSearchParams.model_validate(request.args.to_dict())
        offset = (params.page - 1) * params.per_page

        cafes = cafe_repo.search(
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
            "per_page": params.per_page
        }), 200
    except ValidationError as e:
        return jsonify(
            {"error": "Invalid filter parameters", "details": _validation_errors(e)}
        ), 400
    except Exception:
        logger.exception("Error in list_cafes")
        return jsonify({"error": "An internal error occurred"}), 500


@app.route("/api/cafes/nearby", methods=["GET"])
@limiter.limit("60 per minute")
def search_nearby():
    """Return cafes near a given latitude/longitude within a radius."""
    try:
        params = NearbySearchParams.model_validate(request.args.to_dict())

        cafes = cafe_repo.search_nearby(lat=params.lat, lng=params.lng, radius_m=params.radius)
        return jsonify(cafes), 200
    except ValidationError as e:
        return jsonify(
            {"error": "Invalid filter parameters", "details": _validation_errors(e)}
        ), 400
    except Exception:
        logger.exception("Error in search_nearby")
        return jsonify({"error": "An internal error occurred"}), 500


@app.route("/api/cafes/<uuid:cafe_id>", methods=["GET"])
def get_cafe(cafe_id: uuid.UUID):
    """Return a single cafe by ID."""
    try:
        cafe = cafe_repo.get_by_id(cafe_id)
        if cafe is None:
            return jsonify({"error": "Cafe not found"}), 404
        return jsonify(cafe), 200
    except Exception:
        logger.exception("Error in get_cafe id=%s", cafe_id)
        return jsonify({"error": "An internal error occurred"}), 500


@app.route("/api/cafes/<uuid:cafe_id>/inventory", methods=["GET"])
def get_cafe_inventory(cafe_id: uuid.UUID):
    """Return all coffee beans currently available at a cafe."""
    try:
        cafe = cafe_repo.get_by_id(cafe_id)
        if cafe is None:
            return jsonify({"error": "Cafe not found"}), 404

        inventory = cafe_repo.get_inventory(cafe_id)
        return jsonify(inventory), 200
    except Exception:
        logger.exception("Error in get_cafe_inventory id=%s", cafe_id)
        return jsonify({"error": "An internal error occurred"}), 500


@app.route("/api/cafes/<uuid:cafe_id>/inventory", methods=["POST"])
@require_api_key
@limiter.limit("30 per minute")
def add_to_inventory(cafe_id: uuid.UUID):
    """Links an existing bean to a cafe's inventory."""
    try:
        cafe = cafe_repo.get_by_id(cafe_id)
        if cafe is None:
            return jsonify({"error": "Cafe not found"}), 404

        data: dict[str, object] = request.get_json(silent=True) or {}
        inventory_data = CafeInventoryAdd.model_validate(data)

        if not bean_repo.get_by_id(inventory_data.bean_id):
            return jsonify({"error": "Coffee bean not found"}), 404

        cafe_repo.add_to_inventory(cafe_id, inventory_data.bean_id)
        return jsonify({"status": "success", "message": "Added to inventory"}), 200
    except ValidationError as e:
        return jsonify(
            {"error": "Validation Error", "details": _validation_errors(e)}
        ), 400
    except Exception:
        logger.exception("Error in add_to_inventory cafe_id=%s", cafe_id)
        return jsonify({"error": "An internal error occurred"}), 500


# ============== COFFEE BEAN ENDPOINTS ==============


@app.route("/api/beans", methods=["GET"])
def list_beans():
    """Return a list of all coffee beans. Supports filters: ?roast=medium&origin=ethiopia&roaster_id=1&variety=bourbon&processing=natural&region=minas"""
    try:
        params = BeanSearchParams.model_validate(request.args.to_dict())
        offset = (params.page - 1) * params.per_page

        beans = bean_repo.search(
            roast_level=params.roast,
            origin=params.origin,
            roaster_id=params.roaster_id,
            variety=params.variety,
            processing=params.processing,
            region=params.region,
            limit=params.per_page,
            offset=offset
        )
        return jsonify({
            "data": beans,
            "page": params.page,
            "per_page": params.per_page
        }), 200
    except ValidationError as e:
        return jsonify(
            {"error": "Invalid filter parameters", "details": _validation_errors(e)}
        ), 400
    except Exception:
        logger.exception("Error in list_beans")
        return jsonify({"error": "An internal error occurred"}), 500


@app.route("/api/beans/<uuid:bean_id>", methods=["GET"])
def get_bean(bean_id: uuid.UUID):
    """Return a single coffee bean by ID."""
    try:
        bean = bean_repo.get_by_id(bean_id)
        if bean is None:
            return jsonify({"error": "Coffee bean not found"}), 404
        return jsonify(bean), 200
    except Exception:
        logger.exception("Error in get_bean id=%s", bean_id)
        return jsonify({"error": "An internal error occurred"}), 500


@app.route("/api/beans", methods=["POST"])
@require_api_key
@limiter.limit("30 per minute")
def add_bean():
    """Creates a new coffee bean."""
    try:
        data: dict[str, object] = request.get_json(silent=True) or {}
        bean_data = BeanCreate.model_validate(data)

        bean_id = bean_repo.create(
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
        return jsonify({"id": bean_id, "status": "created"}), 201
    except ValidationError as e:
        return jsonify(
            {"error": "Validation Error", "details": _validation_errors(e)}
        ), 400
    except Exception:
        logger.exception("Error in add_bean")
        return jsonify({"error": "An internal error occurred"}), 500


if __name__ == "__main__":
    # We use host='0.0.0.0' so it's accessible from outside the container
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
