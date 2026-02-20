from datetime import datetime
from decimal import Decimal
import json

import redis
from flask import current_app

from ..extensions import db
from ..models import Product
from ..services.amazon_paapi import get_items


def _cache_key(asin: str) -> str:
    return f"paapi:raw:{asin}"


def sync_product(asin: str):
    redis_client = redis.from_url(current_app.config["REDIS_URL"])
    cached = redis_client.get(_cache_key(asin))
    if cached:
        raw = cached.decode()
    else:
        payload = get_items([asin])
        raw = json.dumps(payload)
        redis_client.setex(_cache_key(asin), 600, raw)

    payload = json.loads(raw)
    item = (payload.get("ItemsResult", {}).get("Items") or [{}])[0]

    price = (
        item.get("Offers", {})
        .get("Listings", [{}])[0]
        .get("Price", {})
        .get("Amount", 0)
    )

    product = Product.query.filter_by(asin=asin).first() or Product(asin=asin, title=asin)
    product.title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", asin)
    product.brand = item.get("ItemInfo", {}).get("ByLineInfo", {}).get("Brand", {}).get("DisplayValue")
    product.description = "\n".join(item.get("ItemInfo", {}).get("Features", {}).get("DisplayValues", []))
    product.images = [item.get("Images", {}).get("Primary", {}).get("Large", {}).get("URL")]
    product.specs = {"raw": item.get("ItemInfo", {}).get("ProductInfo", {})}
    product.amazon_url = item.get("DetailPageURL")
    product.currency = (
        item.get("Offers", {}).get("Listings", [{}])[0].get("Price", {}).get("Currency", "AED")
    )
    product.rating = item.get("CustomerReviews", {}).get("StarRating", {}).get("Value")
    product.reviews_count = item.get("CustomerReviews", {}).get("Count")
    product.category = item.get("BrowseNodeInfo", {}).get("BrowseNodes", [{}])[0].get("DisplayName")
    product.last_synced_at = datetime.utcnow()

    db.session.add(product)
    db.session.commit()
    return {"asin": asin, "price": float(Decimal(str(price)))}


def nightly_refresh():
    products = Product.query.order_by(Product.last_synced_at.asc().nullsfirst()).limit(100).all()
    for product in products:
        sync_product(product.asin)
    return {"refreshed": len(products)}
