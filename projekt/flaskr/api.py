from flask import Blueprint, jsonify, request
from flaskr.db import get_db
from flaskr.auth import loginRequired

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/check-product", methods=["POST"])
def check_product():
    """
    Funkcja sprawdza czy nazwa z pola product_name lub sku
    pasuje do jakiegokolwiek wiersza w tabeli products
    """
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


@bp.route("/check-employee", methods=["POST"])
@loginRequired
def check_employee():
    """
    Funkcja API sprawdza czy istnieje pracownik o podanym kodzie
    i zwraca jego dane jeśli istnieje
    """
    data = request.get_json()
    employeeCode = data.get("employee_code")

    if not employeeCode:
        return jsonify({"error": "No employee code provided"}), 400

    db = get_db()

    employee = db.execute(
        "SELECT * FROM employees WHERE employeeCode = ?", (employeeCode,)
    ).fetchone()

    if employee:
        employeeDict = dict(employee)

        managers = db.execute(
            "SELECT employeeCode, firstName, lastName FROM employees"
        ).fetchall()
        managersList = [dict(manager) for manager in managers]

        return jsonify(
            {
                "exists": True,
                "employee": employeeDict,
                "managers": managersList,
            }
        )
    else:
        return jsonify({"exists": False})
