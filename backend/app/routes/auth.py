from flask import Blueprint, jsonify, request

from ..auth import check_password, create_token, hash_password
from ..extensions import db
from ..models import User

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@bp.post("/register")
def register():
    data = request.get_json() or {}
    user = User(
        name=data.get("name", ""),
        email=data.get("email", "").lower(),
        phone=data.get("phone"),
        password_hash=hash_password(data.get("password", "")),
        role=data.get("role", "customer"),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"token": create_token(user), "user": {"id": user.id, "role": user.role}}), 201


@bp.post("/login")
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email", "").lower()).first()
    if not user or not check_password(data.get("password", ""), user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify({"token": create_token(user), "user": {"id": user.id, "role": user.role}})
