from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
import jwt
from flask import current_app, g, jsonify, request

from .models import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_token(user: User) -> str:
    payload = {
        "sub": user.id,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")


def jwt_required(roles=None):
    roles = roles or []

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({"error": "Unauthorized"}), 401

            token = auth.replace("Bearer ", "", 1)
            try:
                payload = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
                user = User.query.get(payload["sub"])
            except Exception:
                return jsonify({"error": "Unauthorized"}), 401

            if not user:
                return jsonify({"error": "Unauthorized"}), 401

            if roles and user.role not in roles:
                return jsonify({"error": "Forbidden"}), 403

            g.current_user = user
            return fn(*args, **kwargs)

        return wrapper

    return decorator
