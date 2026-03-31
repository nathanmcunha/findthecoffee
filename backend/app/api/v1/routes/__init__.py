"""API v1 routes package."""
from app.api.v1.routes.cafes import cafes_bp
from app.api.v1.routes.roasters import roasters_bp
from app.api.v1.routes.beans import beans_bp

__all__ = ["cafes_bp", "roasters_bp", "beans_bp"]
