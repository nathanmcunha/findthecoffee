"""Flask application factory."""
import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.api.v1.routes import cafes_bp, roasters_bp, beans_bp

# Load variables from .env file
_ = load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # CORS — restrict to configured origins; default wildcard is only safe for local dev
    _cors_origins = os.getenv("CORS_ORIGINS", "*")
    if _cors_origins == "*":
        logger.warning(
            "CORS_ORIGINS not set — allowing all origins. Set CORS_ORIGINS in production."
        )
    CORS(app, resources={r"/api/*": {"origins": _cors_origins}})

    # Rate limiting — in-memory storage, configurable via RATELIMIT_STORAGE_URI
    Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "60 per hour"],
        storage_uri=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
    )

    # Health check
    @app.route("/ping", methods=["GET"])
    def ping():  # type: ignore[reportUnusedFunction]
        """Basic health check route."""
        return jsonify({"status": "online", "message": "Coffee Finder API is running"}), 200

    # Register API v1 blueprints
    app.register_blueprint(cafes_bp, url_prefix="/api/v1/cafes")
    app.register_blueprint(roasters_bp, url_prefix="/api/v1/roasters")
    app.register_blueprint(beans_bp, url_prefix="/api/v1/beans")

    return app
