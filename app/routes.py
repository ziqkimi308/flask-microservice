import os
from flask import Blueprint, jsonify, request
from app.database import db
from app.models import Item

"""
- Routes need to be on same file as Flask instance which means it cannot be modular.
- To break this, we use Blueprint to allow modularization.
- Routes now attached to bp instance.
- And bp instance attached to flask's app instance in __init__.py
"""

bp = Blueprint("main", __name__)

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

@bp.route("/health")
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify({
        "status":  "ok" if db_status == "ok" else "degraded",
        "version": APP_VERSION,
        "db":      db_status,
    }), 200 if db_status == "ok" else 503

@bp.route("/items", methods=["GET"])
def get_items():
    items = Item.query.all()
    return jsonify({"items": [i.to_dict() for i in items], "count": len(items)}), 200

@bp.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name is required"}), 400

    if len(data["name"]) > 100:
        return jsonify({"error": "name must be 100 characters or less"}), 400

    item = Item(
        name        = data["name"],
        description = data.get("description", ""),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@bp.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict()), 200

@bp.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"Item {item_id} deleted"}), 200

@bp.route("/")
def index():
    return jsonify({
        "service": "flask-microservice",
        "version": APP_VERSION,
        "endpoints": [
            "GET  /health",
            "GET  /items",
            "POST /items",
            "GET  /items/<id>",
            "DELETE /items/<id>",
        ],
    }), 200
