from flask import Flask
from flask_cors import CORS

from app.config import get_config
from app.routes.health import health_blueprint
from app.utils.responses import register_error_handlers


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)

    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    app.register_blueprint(health_blueprint, url_prefix="/api/v1")
    register_error_handlers(app)

    return app

