import math
import re
from collections import Counter

from flask import Blueprint, jsonify, request

from ..models import Product, ProductOffer

bp = Blueprint("products", __name__, url_prefix="/api/v1/products")

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")


def _tokenize(value: str) -> list[str]:
    return TOKEN_PATTERN.findall((value or "").lower())


def _cosine_similarity(left: Counter, right: Counter) -> float:
    if not left or not right:
        return 0.0
    numerator = sum(left[token] * right[token] for token in left.keys() & right.keys())
    left_norm = math.sqrt(sum(v * v for v in left.values()))
    right_norm = math.sqrt(sum(v * v for v in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def _semantic_score(query_tokens: list[str], product: Product) -> float:
    searchable_text = " ".join(
        [
            product.title or "",
            product.brand or "",
            product.category or "",
            product.description or "",
            " ".join(map(str, (product.specs or {}).values())),
        ]
    )
    product_tokens = _tokenize(searchable_text)
    if not product_tokens:
        return 0.0

    query_counter = Counter(query_tokens)
    product_counter = Counter(product_tokens)
    cosine = _cosine_similarity(query_counter, product_counter)

    overlap = len(set(query_tokens) & set(product_tokens)) / max(len(set(query_tokens)), 1)
    return (0.7 * cosine) + (0.3 * overlap)


def _serialize_product(product: Product) -> dict:
    return {
        "id": product.id,
        "asin": product.asin,
        "title": product.title,
        "brand": product.brand,
        "images": product.images or [],
        "currency": product.currency,
        "last_synced_at": product.last_synced_at.isoformat() if product.last_synced_at else None,
        "manual_price": float(product.manual_price) if product.manual_price is not None else None,
        "source": product.source,
    }


@bp.get("")
def list_products():
    query = (request.args.get("query", "") or "").strip()
    page = max(1, int(request.args.get("page", 1)))
    per_page = 20

    if not query:
        pagination = Product.query.order_by(Product.last_synced_at.desc().nullslast(), Product.id.desc()).paginate(page=page, per_page=per_page)
        rows = [_serialize_product(p) for p in pagination.items]
        return jsonify({"items": rows, "page": page, "total": pagination.total})

    query_tokens = _tokenize(query)
    products = Product.query.all()

    scored = []
    for product in products:
        score = _semantic_score(query_tokens, product)
        if score > 0:
            scored.append((score, product))

    scored.sort(
        key=lambda item: (
            item[0],
            item[1].last_synced_at.timestamp() if item[1].last_synced_at else 0,
        ),
        reverse=True,
    )
    total = len(scored)
    start = (page - 1) * per_page
    end = start + per_page
    rows = [_serialize_product(product) for _, product in scored[start:end]]

    return jsonify({"items": rows, "page": page, "total": total})


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
