from datetime import datetime
from decimal import Decimal
import json

import redis
from flask import current_app

from ..extensions import db
from ..models import Product
from ..services.oxylabs_client import get_amazon_product


def _cache_key(asin: str) -> str:
    return f"oxylabs:raw:{asin}"


def _extract_content(payload: dict) -> dict:
    results = payload.get("results") or []
    first = results[0] if results else {}
    content = first.get("content") or {}
    if isinstance(content, list):
        return content[0] if content else {}
    return content


def _normalize_price(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    digits = "".join(ch for ch in str(value) if ch.isdigit() or ch == ".")
    return Decimal(digits or "0")


def sync_product(asin: str):
    redis_client = redis.from_url(current_app.config["REDIS_URL"])
    cached = redis_client.get(_cache_key(asin))
    if cached:
        payload = json.loads(cached.decode())
    else:
        payload = get_amazon_product(asin)
        redis_client.setex(_cache_key(asin), 600, json.dumps(payload))

    content = _extract_content(payload)

    raw_price = (
        content.get("price")
        or content.get("price_upper")
        or (content.get("buybox_winner") or {}).get("price")
    )
    price = _normalize_price(raw_price)

    images = content.get("images") or []
    if isinstance(images, dict):
        images = [v for v in images.values() if isinstance(v, str)]

    bullets = content.get("bullet_points") or content.get("feature_bullets") or []
    if isinstance(bullets, dict):
        bullets = list(bullets.values())

    rating = content.get("rating")
    reviews_count = content.get("reviews_count") or content.get("reviews")

    product = Product.query.filter_by(asin=asin).first() or Product(asin=asin, title=asin)
    product.title = content.get("title") or asin
    product.brand = content.get("brand")
    product.category = (content.get("category") or {}).get("name") if isinstance(content.get("category"), dict) else content.get("category")
    product.description = "\n".join([str(x) for x in bullets if x])
    product.images = images
    product.specs = content.get("specifications") or {}
    product.amazon_url = content.get("url") or f"https://www.amazon.ae/dp/{asin}"
    product.currency = content.get("currency") or "AED"
    product.rating = float(rating) if rating is not None else None
    product.reviews_count = int(reviews_count) if reviews_count is not None else None
    product.last_synced_at = datetime.utcnow()

    db.session.add(product)
    db.session.commit()
    return {"asin": asin, "price": float(price)}


def nightly_refresh():
    products = Product.query.order_by(Product.last_synced_at.asc().nullsfirst()).limit(100).all()
    for product in products:
        sync_product(product.asin)
    return {"refreshed": len(products)}
