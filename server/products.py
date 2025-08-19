from __future__ import annotations

import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt

from .db import get_db_session
from .models import Product


products_bp = Blueprint("products", __name__)


@products_bp.get("")
def list_products():
    session = get_db_session()
    products = session.query(Product).order_by(Product.created_at.desc()).all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price_cents": p.price_cents,
            "image_url": p.image_url,
            "stock": p.stock,
        }
        for p in products
    ])


@products_bp.post("")
@jwt_required()
def create_product():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin required"}), 403

    data = request.form if request.form else request.get_json(silent=True) or {}
    name = (data.get("name") or request.form.get("name") or "").strip()
    price_cents = int(data.get("price_cents") or request.form.get("price_cents") or 0)
    description = (data.get("description") or request.form.get("description") or "").strip() or None
    stock = int(data.get("stock") or request.form.get("stock") or 0)

    if not name or price_cents <= 0:
        return jsonify({"error": "Name and positive price_cents are required"}), 400

    image_url = None
    if "image" in request.files:
        image = request.files["image"]
        if image.filename:
            filename = secure_filename(image.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
            image.save(upload_path)
            image_url = f"/uploads/{unique_name}"

    session = get_db_session()
    product = Product(name=name, price_cents=price_cents, description=description, stock=stock, image_url=image_url)
    session.add(product)
    session.commit()

    return jsonify({"id": product.id, "name": product.name, "price_cents": product.price_cents, "image_url": product.image_url, "stock": product.stock})


@products_bp.get("/<int:product_id>")
def get_product(product_id: int):
    session = get_db_session()
    product = session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price_cents": product.price_cents,
        "image_url": product.image_url,
        "stock": product.stock,
    })


@products_bp.delete("/<int:product_id>")
@jwt_required()
def delete_product(product_id: int):
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin required"}), 403
    session = get_db_session()
    product = session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Not found"}), 404
    session.delete(product)
    session.commit()
    return jsonify({"message": "Deleted"})
