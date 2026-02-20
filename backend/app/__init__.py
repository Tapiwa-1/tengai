from flask import Flask

from .config import Config
from .extensions import db, migrate
from . import models  # noqa: F401
from .routes.admin import bp as admin_bp
from .routes.agent import bp as agent_bp
from .routes.auth import bp as auth_bp
from .routes.orders import bp as orders_bp
from .routes.products import bp as products_bp


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)

    @app.get("/health")
    def health():
        return {"ok": True}

    return app
