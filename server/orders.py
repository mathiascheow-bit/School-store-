from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from .db import get_db_session
from .models import Order, OrderItem, Product, generate_unique_order_code


orders_bp = Blueprint("orders", __name__)


@orders_bp.post("")
def create_order():
    payload = request.get_json(force=True)
    customer_name = (payload.get("customer_name") or "").strip()
    location = (payload.get("location") or "").strip()
    items = payload.get("items") or []

    if not customer_name or not location or not items:
        return jsonify({"error": "customer_name, location, and items are required"}), 400

    session = get_db_session()
    order_code = generate_unique_order_code()

    order = Order(order_code=order_code, customer_name=customer_name, location=location)

    try:
        user_id = get_jwt_identity()
        if user_id:
            order.user_id = int(user_id)
    except Exception:
        pass

    order_items: list[OrderItem] = []
    for item in items:
        product_id = int(item.get("product_id"))
        quantity = int(item.get("quantity", 1))
        if quantity <= 0:
            return jsonify({"error": "quantity must be positive"}), 400
        product = session.get(Product, product_id)
        if not product:
            return jsonify({"error": f"product {product_id} not found"}), 404
        if product.stock is not None and product.stock < quantity:
            return jsonify({"error": f"insufficient stock for {product.name}"}), 400
        order_items.append(
            OrderItem(
                product_id=product.id,
                quantity=quantity,
                unit_price_cents=product.price_cents,
                product_name=product.name,
            )
        )

    session.add(order)
    session.flush()

    for item in order_items:
        item.order_id = order.id
        session.add(item)

    for item in order_items:
        product = session.get(Product, item.product_id)
        if product and product.stock is not None:
            product.stock = max(0, product.stock - item.quantity)

    session.commit()

    return jsonify({
        "order_id": order.id,
        "order_code": order.order_code,
        "created_at": order.created_at.isoformat(),
    })


@orders_bp.get("/me")
@jwt_required()
def list_my_orders():
    session = get_db_session()
    user_id = int(get_jwt_identity())
    orders = session.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()
    return jsonify([
        {
            "order_id": o.id,
            "order_code": o.order_code,
            "created_at": o.created_at.isoformat(),
            "items": [
                {
                    "product_id": it.product_id,
                    "product_name": it.product_name,
                    "quantity": it.quantity,
                    "unit_price_cents": it.unit_price_cents,
                }
                for it in o.items
            ],
        }
        for o in orders
    ])


@orders_bp.get("")
@jwt_required()
def list_orders_admin():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin required"}), 403

    session = get_db_session()
    orders = session.query(Order).order_by(Order.created_at.desc()).all()
    return jsonify([
        {
            "order_id": o.id,
            "order_code": o.order_code,
            "customer_name": o.customer_name,
            "location": o.location,
            "created_at": o.created_at.isoformat(),
            "items": [
                {
                    "product_id": it.product_id,
                    "product_name": it.product_name,
                    "quantity": it.quantity,
                    "unit_price_cents": it.unit_price_cents,
                }
                for it in o.items
            ],
        }
        for o in orders
    ])


@orders_bp.get("/stats")
@jwt_required()
def stats():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin required"}), 403

    session = get_db_session()

    now = datetime.utcnow()
    start = now - timedelta(days=29)
    orders = (
        session.query(Order)
        .filter(Order.created_at >= start)
        .order_by(Order.created_at)
        .all()
    )

    daily_counts: dict[str, int] = defaultdict(int)
    for o in orders:
        day = o.created_at.strftime("%Y-%m-%d")
        daily_counts[day] += 1

    days = [
        (start + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(30)
    ]
    line = [{"date": d, "count": daily_counts.get(d, 0)} for d in days]

    from sqlalchemy import func

    rows = (
        session.query(OrderItem.product_name, func.sum(OrderItem.quantity))
        .group_by(OrderItem.product_name)
        .all()
    )
    bar = [{"product": r[0], "count": int(r[1] or 0)} for r in rows]

    return jsonify({"line": line, "bar": bar})
