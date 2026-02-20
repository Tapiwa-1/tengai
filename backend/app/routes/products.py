from flask import Blueprint, jsonify, request

from ..models import Product, ProductOffer

bp = Blueprint("products", __name__, url_prefix="/api/v1/products")


@bp.get("")
def list_products():
    query = request.args.get("query", "")
    page = int(request.args.get("page", 1))
    pagination = Product.query.filter(Product.title.ilike(f"%{query}%")).paginate(page=page, per_page=20)
    rows = [
        {
            "id": p.id,
            "asin": p.asin,
            "title": p.title,
            "brand": p.brand,
            "images": p.images or [],
            "currency": p.currency,
            "last_synced_at": p.last_synced_at.isoformat() if p.last_synced_at else None,
            "manual_price": float(p.manual_price) if p.manual_price is not None else None,
            "source": p.source,
        }
        for p in pagination.items
    ]
    return jsonify({"items": rows, "page": page, "total": pagination.total})


@bp.get("/<int:product_id>")
def get_product(product_id: int):
    p = Product.query.get_or_404(product_id)
    offers = ProductOffer.query.filter_by(product_id=product_id, status="approved").all()
    return jsonify(
        {
            "id": p.id,
            "asin": p.asin,
            "title": p.title,
            "brand": p.brand,
            "description": p.description,
            "images": p.images,
            "specs": p.specs,
            "amazon_url": p.amazon_url,
            "currency": p.currency,
            "rating": p.rating,
            "reviews_count": p.reviews_count,
            "last_synced_at": p.last_synced_at.isoformat() if p.last_synced_at else None,
            "manual_price": float(p.manual_price) if p.manual_price is not None else None,
            "source": p.source,
            "offers": [
                {
                    "id": o.id,
                    "agent_id": o.agent_id,
                    "selling_price": float(o.selling_price),
                    "delivery_days": o.delivery_days,
                    "notes": o.notes,
                    "status": o.status,
                }
                for o in offers
            ],
        }
    )
