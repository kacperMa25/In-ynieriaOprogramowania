from flask import Blueprint, jsonify, request
from flaskr.db import get_db

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/check-product", methods=["POST"])
def check_product():
    productName = request.json.get("product_name", "")
    productSku = request.json.get("sku", "")
    db = get_db()

    if productName:
        product = db.execute(
            "SELECT * FROM products WHERE productName = ?", (productName,)
        ).fetchone()
    elif productSku:
        product = db.execute(
            "SELECT * FROM products WHERE productCode = ?", (productSku,)
        ).fetchone()
    else:
        return jsonify({"error": "No search parameters provided"}), 400

    if product:
        productDict = dict(product)
        return jsonify({"exists": True, "product": productDict})
    else:
        return jsonify({"exists": False})
