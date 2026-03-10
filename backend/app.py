import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from db.repository import CafeRepository, CoffeeBeanRepository

# Load variables from .env file
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes (important for decoupled architecture)
CORS(app)

cafe_repo = CafeRepository()
bean_repo = CoffeeBeanRepository()


@app.route("/ping", methods=["GET"])
def ping():
    """Basic health check route."""
    return jsonify({"status": "online", "message": "Coffee Finder API is running"}), 200


# ============== CAFE ENDPOINTS ==============

@app.route("/api/cafes", methods=["GET"])
def list_cafes():
    """Return a list of all cafes. Use ?include=beans for nested beans."""
    try:
        include_beans = request.args.get("include") == "beans"
        if include_beans:
            cafes = cafe_repo.get_all_with_beans()
        else:
            cafes = cafe_repo.get_all()
        return jsonify(cafes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cafes/<int:cafe_id>", methods=["GET"])
def get_cafe(cafe_id: int):
    """Return a single cafe by ID. Use ?include=beans for nested beans."""
    try:
        include_beans = request.args.get("include") == "beans"
        if include_beans:
            cafe = cafe_repo.get_with_beans(cafe_id)
        else:
            cafe = cafe_repo.get_by_id(cafe_id)
        
        if cafe is None:
            return jsonify({"error": "Cafe not found"}), 404
        return jsonify(cafe), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cafes", methods=["POST"])
def add_cafe():
    """Creates a new cafe from a JSON body."""
    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    try:
        cafe_id = cafe_repo.create(
            data["name"], 
            data.get("location"),
            data.get("website")
        )
        return jsonify({"id": cafe_id, "status": "created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============== COFFEE BEAN ENDPOINTS ==============

@app.route("/api/beans", methods=["GET"])
def list_beans():
    """Return a list of all coffee beans. Supports filters: ?roast=medium&origin=ethiopia"""
    try:
        roast = request.args.get("roast")
        origin = request.args.get("origin")
        
        beans = bean_repo.search(roast_level=roast, origin=origin)
        return jsonify(beans), 200
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


@app.route("/api/cafes/<int:cafe_id>/beans", methods=["GET"])
def list_cafe_beans(cafe_id: int):
    """Return all coffee beans for a specific cafe."""
    try:
        cafe = cafe_repo.get_by_id(cafe_id)
        if cafe is None:
            return jsonify({"error": "Cafe not found"}), 404
        
        beans = bean_repo.get_by_cafe(cafe_id)
        return jsonify(beans), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cafes/<int:cafe_id>/beans", methods=["POST"])
def add_bean_to_cafe(cafe_id: int):
    """Creates a new coffee bean linked to a cafe."""
    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    try:
        cafe = cafe_repo.get_by_id(cafe_id)
        if cafe is None:
            return jsonify({"error": "Cafe not found"}), 404
        
        bean_id = bean_repo.create(
            name=data["name"],
            cafe_id=cafe_id,
            roast_level=data.get("roast_level"),
            origin=data.get("origin"),
        )
        return jsonify({"id": bean_id, "status": "created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # We use host='0.0.0.0' so it's accessible from outside the container later
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
