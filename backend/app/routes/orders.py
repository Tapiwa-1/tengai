from decimal import Decimal

from flask import Blueprint, g, jsonify, request

from ..auth import jwt_required
from ..extensions import db
from ..models import Order, OrderItem, ProductOffer

bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")


def _commission(selling_price: Decimal, landed_cost: Decimal):
    profit = selling_price - landed_cost
    tengai_fee = max(Decimal("0"), profit * Decimal("0.30"))
    agent_earnings = selling_price - landed_cost - tengai_fee
    return tengai_fee, agent_earnings


@bp.post("")
@jwt_required(["customer", "admin"])
def create_order():
    data = request.get_json() or {}
    offer = ProductOffer.query.get_or_404(data["offer_id"])

    shipping = Decimal(str(data.get("cost_estimate", {}).get("shipping", 0)))
    duty = Decimal(str(data.get("cost_estimate", {}).get("duty", 0)))
    handling = Decimal(str(data.get("cost_estimate", {}).get("handling", 0)))

    selling_total = Decimal("0")
    landed_total = Decimal("0")
    fee_total = Decimal("0")
    earnings_total = Decimal("0")

    order = Order(customer_id=g.current_user.id, agent_id=offer.agent_id, status="created", currency="AED", selling_total=0, landed_cost_total=0, tengai_fee_total=0, agent_earnings_total=0)
    db.session.add(order)
    db.session.flush()

    for item in data.get("items", []):
        qty = int(item["qty"])
        selling_each = Decimal(str(offer.selling_price))
        amazon_price = Decimal(str(item.get("amazon_price_snapshot", 0)))
        landed_cost = amazon_price + shipping + duty + handling
        tengai_fee, earnings = _commission(selling_each, landed_cost)

        selling_total += selling_each * qty
        landed_total += landed_cost * qty
        fee_total += tengai_fee * qty
        earnings_total += earnings * qty

        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            qty=qty,
            selling_price_each=selling_each,
            amazon_price_snapshot=amazon_price,
            cost_snapshot_json={"shipping": float(shipping), "duty": float(duty), "handling": float(handling)},
        )
        db.session.add(order_item)

    order.selling_total = selling_total
    order.landed_cost_total = landed_total
    order.tengai_fee_total = fee_total
    order.agent_earnings_total = earnings_total

    db.session.commit()
    return jsonify({"id": order.id, "status": order.status, "tengai_fee_total": float(order.tengai_fee_total)}), 201


@bp.get("")
@jwt_required(["customer", "admin"])
def customer_orders():
    orders = Order.query.filter_by(customer_id=g.current_user.id).all()
    return jsonify({"items": [{"id": o.id, "status": o.status, "selling_total": float(o.selling_total)} for o in orders]})
