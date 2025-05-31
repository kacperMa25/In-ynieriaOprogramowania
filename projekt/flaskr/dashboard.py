from flaskr.auth import loginRequired
from flaskr.db import get_db
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

bp = Blueprint("dashboard", __name__, url_prefix="/")


@bp.route("/")
@loginRequired
def index():
    db = get_db()
    wDetails = db.execute(
        "SELECT COUNT(productCode) as howMany, SUM(quantityInStock * price) as howMuch FROM products"
    ).fetchone()
    return render_template("dashboard/index.html", wDetails=wDetails)


@bp.route("/users")
@loginRequired
def users():
    db = get_db()
    wDetails = db.execute(
        "SELECT COUNT(employeeCode) as howMany FROM employees"
    ).fetchone()
    return render_template("dashboard/users.html", wDetails=wDetails)


@bp.route("/users/add")
@loginRequired
def add_user():
    return render_template("dashboard/add-user.html")


@bp.route("/products")
@loginRequired
def products():
    db = get_db()
    wDetails = db.execute(
        "SELECT SUM(quantityInStock) as howMany, COUNT(DISTINCT productCode) as howManyD FROM products"
    ).fetchone()
    return render_template("dashboard/products.html", wDetails=wDetails)


@bp.route("/products/add", methods=("GET", "POST"))
@loginRequired
def add_item():
    if request.method == "POST":
        db = get_db()
        error = None
        itemName = request.form["itemName"]
        itemCode = request.form["sku"]
        itemDesc = request.form["description"]
        itemQuantity = request.form["quantity"]
        itemPrice = request.form["price"]

        if not itemName or itemName.strip() == "":
            error = "Nazwa wymagana"
        elif not itemCode or itemCode.strip() == "":
            error = "Kod wymagany"
        elif not itemDesc or itemDesc.strip() == "":
            error = "Opis wymagany"
        elif not itemQuantity or itemQuantity.strip() == "":
            error = "Ilość wymagana"
        elif not itemPrice or itemPrice.strip() == "":
            error = "Cena wymagana"
        else:
            try:
                quantity = int(itemQuantity)
                price = float(itemPrice)
                if quantity <= 0:
                    error = "Ilość musi być większa niż 0"
                elif price <= 0:
                    error = "Cena musi być większa niż 0"
            except ValueError:
                error = "Ilość i cena muszą być liczbami"

            try:
                db.execute(
                    "INSERT INTO products (productCode, productName, productDescription, quantityInStock, price) VALUES (?, ?, ?, ?, ?)",
                    (itemCode, itemName, itemDesc, itemQuantity, itemPrice),
                )
                db.commit()
            except db.IntegrityError as e:
                error = f"Błąd integralności: {str(e)} - Produkt o kodzie {itemCode}"
            else:
                return redirect(url_for("index"))

        flash(error)

    return render_template("dashboard/add-item.html")
