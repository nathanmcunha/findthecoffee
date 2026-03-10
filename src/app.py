import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from src.db.repository import CafeRepository

# Load variables from .env file
load_dotenv()

app = Flask(__name__)
repo = CafeRepository()


@app.route("/ping", methods=["GET"])
def ping():
    """Basic health check route."""
    return jsonify({"status": "online", "message": "Coffee Finder API is running"}), 200


@app.route("/api/cafes", methods=["GET"])
def list_cafes():
    """Return a list of all cafes"""
    try:
        cafes = repo.get_all()
        return jsonify(cafes), 200
    except Exception as e:
        return jsonify({"error: srt(e)"})


@app.route("/api/cafes", methods=["POST"])
def add_cafe():
    """Creates a new cafe from a JSON body."""
    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    try:
        cafe_id = repo.create(data["name"], data.get("location"))
        return jsonify({"id": cafe_id, "status": "created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # We use host='0.0.0.0' so it's accessible from outside the container later
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
