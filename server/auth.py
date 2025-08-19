from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required

from .db import get_db_session
from .models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/signin")
def signin():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    name = (data.get("name") or "").strip()
    if not email:
        return jsonify({"error": "Email is required"}), 400

    session = get_db_session()
    user = session.query(User).filter(User.email == email).first()
    if user is None:
        user = User(email=email, name=name or email.split("@")[0])
        session.add(user)
        session.commit()

    token = create_access_token(identity=user.id, additional_claims={"is_admin": user.is_admin})
    return jsonify({"token": token, "user": {"id": user.id, "email": user.email, "name": user.name, "is_admin": user.is_admin}})


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    session = get_db_session()
    user = session.get(User, user_id)
    return jsonify({"id": user.id, "email": user.email, "name": user.name, "is_admin": user.is_admin})


@auth_bp.post("/grant-admin")
@jwt_required()
def grant_admin():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin required"}), 403
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"error": "Email is required"}), 400
    session = get_db_session()
    user = session.query(User).filter(User.email == email).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    user.is_admin = True
    session.commit()
    return jsonify({"message": "Granted", "user": {"id": user.id, "email": user.email, "is_admin": user.is_admin}})
