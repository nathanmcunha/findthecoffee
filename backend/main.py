"""Flask application entry point."""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # We use host='0.0.0.0' so it's accessible from outside the container
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
