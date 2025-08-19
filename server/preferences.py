from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from .db import get_db_session
from .models import Preference


preferences_bp = Blueprint("preferences", __name__)


@preferences_bp.get("/me")
@jwt_required()
def get_my_preferences():
    user_id = int(get_jwt_identity())
    session = get_db_session()
    prefs = session.query(Preference).filter(Preference.user_id == user_id, Preference.liked == True).all()  # noqa: E712
    return jsonify({"likes": [p.product_id for p in prefs]})


@preferences_bp.post("/like")
@jwt_required()
def like_product():
    user_id = int(get_jwt_identity())
    payload = request.get_json(force=True)
    product_id = int(payload.get("product_id"))
    liked = bool(payload.get("liked", True))

    session = get_db_session()
    pref = (
        session.query(Preference)
        .filter(Preference.user_id == user_id, Preference.product_id == product_id)
        .first()
    )
    if pref is None:
        pref = Preference(user_id=user_id, product_id=product_id, liked=liked)
        session.add(pref)
    else:
        pref.liked = liked
    session.commit()

    return jsonify({"product_id": product_id, "liked": liked})
