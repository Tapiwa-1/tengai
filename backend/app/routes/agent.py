import os
import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.utils import secure_filename

from ..auth import jwt_required
from ..extensions import db
from ..models import Product, ProductImportHistory, ProductOffer

bp = Blueprint("agent", __name__, url_prefix="/api/v1/agent")

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


@bp.post("/import")
@jwt_required(["agent", "admin"])
def manual_upload_product():
    form = request.form
    title = (form.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    price_raw = (form.get("manual_price") or "0").strip()
    try:
        manual_price = Decimal(price_raw)
    except InvalidOperation:
        return jsonify({"error": "manual_price must be a valid number"}), 400

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    image_urls = []
    for file in request.files.getlist("images"):
        if not file or not file.filename:
            continue
        filename = secure_filename(file.filename)
        if not _allowed_file(filename):
            return jsonify({"error": f"Unsupported image format: {filename}"}), 400
        extension = filename.rsplit(".", 1)[1].lower()
        generated_name = f"{uuid.uuid4().hex}.{extension}"
        path = os.path.join(upload_dir, generated_name)
        file.save(path)
        image_urls.append(f"/uploads/{generated_name}")

    product = Product(
        asin=f"MANUAL-{uuid.uuid4().hex[:10].upper()}",
        title=title,
        brand=(form.get("brand") or None),
        category=(form.get("category") or None),
        description=(form.get("description") or None),
        images=image_urls,
        specs={},
        amazon_url=(form.get("amazon_url") or None),
        currency=(form.get("currency") or "AED"),
        manual_price=manual_price,
        source="manual",
        last_synced_at=datetime.utcnow(),
    )

    db.session.add(product)
    db.session.flush()
    db.session.add(ProductImportHistory(asin=product.asin, agent_id=g.current_user.id))
    db.session.commit()

    return jsonify({"id": product.id, "asin": product.asin, "source": product.source}), 201


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
