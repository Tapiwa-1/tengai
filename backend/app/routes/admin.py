from flask import Blueprint, g, jsonify

from ..auth import jwt_required
from ..extensions import db
from ..models import AuditLog, ProductOffer

bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


@bp.patch("/offers/<int:offer_id>/approve")
@jwt_required(["admin"])
def approve_offer(offer_id: int):
    offer = ProductOffer.query.get_or_404(offer_id)
    offer.status = "approved"
    db.session.add(AuditLog(actor_user_id=g.current_user.id, action="approve_offer", entity_type="product_offer", entity_id=offer.id, meta_json={"status": "approved"}))
    db.session.commit()
    return jsonify({"id": offer.id, "status": offer.status})


@bp.patch("/offers/<int:offer_id>/block")
@jwt_required(["admin"])
def block_offer(offer_id: int):
    offer = ProductOffer.query.get_or_404(offer_id)
    offer.status = "blocked"
    db.session.add(AuditLog(actor_user_id=g.current_user.id, action="block_offer", entity_type="product_offer", entity_id=offer.id, meta_json={"status": "blocked"}))
    db.session.commit()
    return jsonify({"id": offer.id, "status": offer.status})
