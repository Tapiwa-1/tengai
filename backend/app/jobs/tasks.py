from datetime import datetime
from decimal import Decimal
import json

import redis
from flask import current_app

from ..extensions import db
from ..models import Product
from ..services.serpapi_client import get_amazon_product


def _cache_key(asin: str) -> str:
    return f"serpapi:raw:{asin}"


def sync_product(asin: str):
    redis_client = redis.from_url(current_app.config["REDIS_URL"])
    cached = redis_client.get(_cache_key(asin))
    if cached:
        payload = json.loads(cached.decode())
    else:
        payload = get_amazon_product(asin)
        redis_client.setex(_cache_key(asin), 600, json.dumps(payload))

    product_data = payload.get("product", {})
    buybox = payload.get("buybox_winner", {})
    rating = product_data.get("rating")
    reviews = product_data.get("reviews")

    raw_price = buybox.get("price") or product_data.get("buybox_price") or 0
    if isinstance(raw_price, str):
        digits = "".join(ch for ch in raw_price if ch.isdigit() or ch == ".")
        raw_price = digits or 0

    product = Product.query.filter_by(asin=asin).first() or Product(asin=asin, title=asin)
    product.title = product_data.get("title", asin)
    product.brand = product_data.get("brand")
    product.category = product_data.get("categories", [{}])[0].get("name") if product_data.get("categories") else None
    product.description = "\n".join(product_data.get("feature_bullets", []))
    product.images = product_data.get("images", [])
    product.specs = product_data.get("specifications", {})
    product.amazon_url = product_data.get("link")
    product.currency = buybox.get("currency", "AED")
    product.rating = float(rating) if rating is not None else None
    product.reviews_count = int(reviews) if reviews is not None else None
    product.last_synced_at = datetime.utcnow()

    db.session.add(product)
    db.session.commit()
    return {"asin": asin, "price": float(Decimal(str(raw_price or 0)))}


def nightly_refresh():
    products = Product.query.order_by(Product.last_synced_at.asc().nullsfirst()).limit(100).all()
    for product in products:
        sync_product(product.asin)
    return {"refreshed": len(products)}
