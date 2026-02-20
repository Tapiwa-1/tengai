from datetime import datetime
from enum import Enum

from sqlalchemy import UniqueConstraint

from .extensions import db


class Role(str, Enum):
    CUSTOMER = "customer"
    AGENT = "agent"
    ADMIN = "admin"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(64))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=Role.CUSTOMER.value)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String(20), nullable=False, unique=True)
    title = db.Column(db.String(500), nullable=False)
    brand = db.Column(db.String(255))
    category = db.Column(db.String(255))
    description = db.Column(db.Text)
    images = db.Column(db.JSON, default=list)
    specs = db.Column(db.JSON, default=dict)
    amazon_url = db.Column(db.String(1024))
    currency = db.Column(db.String(8), default="AED")
    rating = db.Column(db.Float)
    reviews_count = db.Column(db.Integer)
    last_synced_at = db.Column(db.DateTime)


class ProductOffer(db.Model):
    __tablename__ = "product_offers"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    selling_price = db.Column(db.Numeric(12, 2), nullable=False)
    delivery_days = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending", nullable=False)

    product = db.relationship("Product")
    agent = db.relationship("User")


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="created")
    currency = db.Column(db.String(8), nullable=False, default="AED")
    selling_total = db.Column(db.Numeric(12, 2), nullable=False)
    landed_cost_total = db.Column(db.Numeric(12, 2), nullable=False)
    tengai_fee_total = db.Column(db.Numeric(12, 2), nullable=False)
    agent_earnings_total = db.Column(db.Numeric(12, 2), nullable=False)


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    selling_price_each = db.Column(db.Numeric(12, 2), nullable=False)
    amazon_price_snapshot = db.Column(db.Numeric(12, 2), nullable=False)
    cost_snapshot_json = db.Column(db.JSON, nullable=False)


class Payout(db.Model):
    __tablename__ = "payouts"
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    meta_json = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class ProductImportHistory(db.Model):
    __tablename__ = "product_import_history"
    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String(20), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (UniqueConstraint("asin", "agent_id", name="uniq_import_asin_agent"),)
