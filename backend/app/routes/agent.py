import re

import redis
from flask import Blueprint, current_app, g, jsonify, request
from rq import Queue

from ..auth import jwt_required
from ..extensions import db
from ..jobs.tasks import sync_product
from ..models import ProductImportHistory, ProductOffer

bp = Blueprint("agent", __name__, url_prefix="/api/v1/agent")

ASIN_PATTERN = re.compile(r"([A-Z0-9]{10})")


def extract_asin(value: str):
    match = ASIN_PATTERN.search((value or "").upper())
    return match.group(1) if match else None


@bp.post("/import")
@jwt_required(["agent", "admin"])
def import_product():
    redis_client = redis.from_url(current_app.config["REDIS_URL"])
    key = f"ratelimit:import:{g.current_user.id}"
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, 60)
    if count > 20:
        return jsonify({"error": "Rate limit exceeded"}), 429

    asin = extract_asin((request.get_json() or {}).get("url_or_asin", ""))
    if not asin:
        return jsonify({"error": "Invalid ASIN or URL"}), 400

    q = Queue(connection=redis_client)
    job = q.enqueue(sync_product, asin)

    db.session.merge(ProductImportHistory(asin=asin, agent_id=g.current_user.id))
    db.session.commit()
    return jsonify({"job_id": job.id, "asin": asin})


@bp.get("/imports")
@jwt_required(["agent", "admin"])
def import_history():
    rows = ProductImportHistory.query.filter_by(agent_id=g.current_user.id).order_by(ProductImportHistory.created_at.desc()).limit(50)
    return jsonify({"items": [{"asin": r.asin, "created_at": r.created_at.isoformat()} for r in rows]})


@bp.post("/offers")
@jwt_required(["agent", "admin"])
def create_offer():
    data = request.get_json() or {}
    offer = ProductOffer(
        product_id=data["product_id"],
        agent_id=g.current_user.id,
        selling_price=data["selling_price"],
        delivery_days=data["delivery_days"],
        notes=data.get("notes"),
        status="pending",
    )
    db.session.add(offer)
    db.session.commit()
    return jsonify({"id": offer.id, "status": offer.status}), 201


@bp.get("/orders")
@jwt_required(["agent", "admin"])
def agent_orders():
    from ..models import Order

    orders = Order.query.filter_by(agent_id=g.current_user.id).all()
    return jsonify({"items": [{"id": o.id, "status": o.status, "selling_total": float(o.selling_total)} for o in orders]})
