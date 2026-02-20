from pathlib import Path

from flask import Flask, request, send_from_directory
from sqlalchemy import create_engine

from .config import Config
from .extensions import db, migrate
from . import models  # noqa: F401
from .routes.admin import bp as admin_bp
from .routes.agent import bp as agent_bp
from .routes.auth import bp as auth_bp
from .routes.orders import bp as orders_bp
from .routes.products import bp as products_bp


def _ensure_database_uri(app: Flask):
    current_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if not current_uri.startswith("mysql"):
        return

    try:
        engine = create_engine(current_uri)
        with engine.connect():
            pass
    except Exception:
        fallback_uri = "sqlite:///tengai.db"
        app.logger.warning("MySQL is unreachable, falling back to SQLite at %s", fallback_uri)
        app.config["SQLALCHEMY_DATABASE_URI"] = fallback_uri


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    _ensure_database_uri(app)

    upload_dir = Path(app.root_path).parent / app.config["UPLOAD_FOLDER"]
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = str(upload_dir)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)

    @app.before_request
    def cors_preflight():
        if request.method == "OPTIONS" and request.path.startswith("/api/"):
            response = app.make_default_options_response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, PUT, DELETE, OPTIONS"
            return response
        return None

    @app.after_request
    def add_cors_headers(response):
        if response and request.path.startswith("/api/"):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, PUT, DELETE, OPTIONS"
        return response

    with app.app_context():
        db.create_all()

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename: str):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.get("/health")
    def health():
        return {"ok": True}

    return app
