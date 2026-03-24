import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from pydantic import BaseModel, ValidationError

from db.repository import CafeRepository, CoffeeBeanRepository, RoasterRepository

# Load variables from .env file
_ = load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes (important for decoupled architecture)
_ = CORS(app)

cafe_repo = CafeRepository()
bean_repo = CoffeeBeanRepository()
roaster_repo = RoasterRepository()


# ============== PYDANTIC MODELS ==============


class RoasterCreate(BaseModel):
    name: str
    website: str | None = None
    location: str | None = None


class CafeCreate(BaseModel):
    name: str
    location: str | None = None
    website: str | None = None


class CafeSearchParams(BaseModel):
    roast: str | None = None
    origin: str | None = None
    roaster_id: int | None = None
    name: str | None = None
    q: str | None = None


class CafeInventoryAdd(BaseModel):
    bean_id: int


class BeanSearchParams(BaseModel):
    roast: str | None = None
    origin: str | None = None
    roaster_id: int | None = None


class BeanCreate(BaseModel):
    name: str
    roaster_id: int | None = None
    roast_level: str | None = None
    origin: str | None = None


@app.route("/ping", methods=["GET"])
def ping():
    """Basic health check route."""
    return jsonify({"status": "online", "message": "Coffee Finder API is running"}), 200


# ============== ROASTER ENDPOINTS ==============


@app.route("/api/roasters", methods=["GET"])
def list_roasters():
    """Return a list of all roasters."""
    try:
        roasters = roaster_repo.get_all()
        return jsonify(roasters), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/roasters/<int:roaster_id>", methods=["GET"])
def get_roaster(roaster_id: int):
    """Return a single roaster by ID."""
    try:
        roaster = roaster_repo.get_by_id(roaster_id)
        if roaster is None:
            return jsonify({"error": "Roaster not found"}), 404
        return jsonify(roaster), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/roasters", methods=["POST"])
def add_roaster():
    """Creates a new roaster from a JSON body."""
    try:
        # Validate and parse the JSON payload using Pydantic
        data = request.get_json(silent=True) or {}
        roaster_data = RoasterCreate.model_validate(data)

        roaster_id = roaster_repo.create(
            roaster_data.name, roaster_data.website, roaster_data.location
        )
        return jsonify({"id": roaster_id, "status": "created"}), 201
    except ValidationError as e:
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============== CAFE ENDPOINTS ==============


@app.route("/api/cafes", methods=["POST"])
def add_cafe():
    """Creates a new cafe from a JSON body."""
    try:
        data = request.get_json(silent=True) or {}
        cafe_data = CafeCreate.model_validate(data)

        cafe_id = cafe_repo.create(
            cafe_data.name, cafe_data.location, cafe_data.website
        )
        return jsonify({"id": cafe_id, "status": "created"}), 201
    except ValidationError as e:
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cafes", methods=["GET"])
def list_cafes():
    """Return a list of cafes. Supports discovery filters and global search: ?q=query"""
    try:
        # Validate query parameters
        # request.args.to_dict() ensures we pass a plain dict to Pydantic
        params = CafeSearchParams.model_validate(request.args.to_dict())

        if (
            params.roast
            or params.origin
            or params.roaster_id
            or params.name
            or params.q
        ):
            cafes = cafe_repo.search(
                roast_level=params.roast,
                origin=params.origin,
                roaster_id=params.roaster_id,
                cafe_name=params.name,
                query_text=params.q,
            )
        else:
            # For "All Cafes", we still use the basic list
            cafes = cafe_repo.get_all()
        return jsonify(cafes), 200
    except ValidationError as e:
        return jsonify(
            {"error": "Invalid filter parameters", "details": e.errors()}
        ), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cafes/<int:cafe_id>", methods=["GET"])
def get_cafe(cafe_id: int):
    """Return a single cafe by ID."""
    try:
        cafe = cafe_repo.get_by_id(cafe_id)
        if cafe is None:
            return jsonify({"error": "Cafe not found"}), 404
        return jsonify(cafe), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cafes/<int:cafe_id>/inventory", methods=["GET"])
def get_cafe_inventory(cafe_id: int):
    """Return all coffee beans currently available at a cafe."""
    try:
        cafe = cafe_repo.get_by_id(cafe_id)
        if cafe is None:
            return jsonify({"error": "Cafe not found"}), 404

        inventory = cafe_repo.get_inventory(cafe_id)
        return jsonify(inventory), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cafes/<int:cafe_id>/inventory", methods=["POST"])
def add_to_inventory(cafe_id: int):
    """Links an existing bean to a cafe's inventory."""
    try:
        cafe = cafe_repo.get_by_id(cafe_id)
        if cafe is None:
            return jsonify({"error": "Cafe not found"}), 404

        data = request.get_json(silent=True) or {}
        inventory_data = CafeInventoryAdd.model_validate(data)

        if not bean_repo.get_by_id(inventory_data.bean_id):
            return jsonify({"error": "Coffee bean not found"}), 404

        cafe_repo.add_to_inventory(cafe_id, inventory_data.bean_id)
        return jsonify({"status": "success", "message": "Added to inventory"}), 200
    except ValidationError as e:
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============== COFFEE BEAN ENDPOINTS ==============


@app.route("/api/beans", methods=["GET"])
def list_beans():
    """Return a list of all coffee beans. Supports filters: ?roast=medium&origin=ethiopia&roaster_id=1"""
    try:
        params = BeanSearchParams.model_validate(request.args.to_dict())

        beans = bean_repo.search(
            roast_level=params.roast, origin=params.origin, roaster_id=params.roaster_id
        )
        return jsonify(beans), 200
    except ValidationError as e:
        return jsonify(
            {"error": "Invalid filter parameters", "details": e.errors()}
        ), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/beans/<int:bean_id>", methods=["GET"])
def get_bean(bean_id: int):
    """Return a single coffee bean by ID."""
    try:
        bean = bean_repo.get_by_id(bean_id)
        if bean is None:
            return jsonify({"error": "Coffee bean not found"}), 404
        return jsonify(bean), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/beans", methods=["POST"])
def add_bean():
    """Creates a new coffee bean."""
    try:
        data = request.get_json(silent=True) or {}
        bean_data = BeanCreate.model_validate(data)

        bean_id = bean_repo.create(
            name=bean_data.name,
            roaster_id=bean_data.roaster_id,
            roast_level=bean_data.roast_level,
            origin=bean_data.origin,
        )
        return jsonify({"id": bean_id, "status": "created"}), 201
    except ValidationError as e:
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # We use host='0.0.0.0' so it's accessible from outside the container later
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
