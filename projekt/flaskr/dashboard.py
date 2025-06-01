from flaskr.auth import loginRequired
from flaskr.db import get_db
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from werkzeug.security import generate_password_hash

bp = Blueprint("dashboard", __name__, url_prefix="/")


@bp.route("/")
@loginRequired
def index():
    db = get_db()
    wDetails = db.execute(
        "SELECT COUNT(productCode) as howMany, SUM(quantityInStock * price) as howMuch, SUM(quantityInStock < minimalQuantity) as lowStock FROM products"
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


@bp.route("/users/add", methods=("GET", "POST"))
@loginRequired
def add_user():
    if request.method == "POST":
        db = get_db()
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        login = request.form["login"]
        password = request.form["password"]
        error = None

        if not firstName or firstName.strip() == "":
            error = "Imie jest wymagane"
        elif not lastName or lastName.strip() == "":
            error = "Nazwisko jest wymagane"
        elif not login or login.strip() == "":
            error = "Login jest wymagany"
        elif not password or password.strip() == "":
            error = "Hasło jest wymagane"

        if error is None:
            try:
                db.execute(
                    "INSERT INTO employees (firstName, lastName, login, password) VALUES (?, ?, ?, ?)",
                    (firstName, lastName, login, generate_password_hash(password)),
                )
                db.commit()

            except db.IntegrityError as e:
                error = f"{e}"
            else:
                return redirect(url_for("index"))

        flash(error)
    return render_template("dashboard/add-user.html")


@bp.route("/products")
@loginRequired
def products():
    db = get_db()
    wDetails = db.execute(
        "SELECT SUM(quantityInStock) as howMany, COUNT(productCode) as howManyD FROM products"
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
        itemCategory = request.form.get("category", "")
        itemUnit = request.form.get("unit", "")
        itemLocation = request.form["location"]
        itemMinQuant = request.form["minStock"]
        itemQuantity = request.form["quantity"]
        itemPrice = request.form["price"]

        if not itemName or itemName.strip() == "":
            error = "Nazwa wymagana"
        elif not itemCode or itemCode.strip() == "":
            error = "Kod wymagany"
        elif not itemDesc or itemDesc.strip() == "":
            error = "Opis wymagany"
        elif not itemQuantity:
            error = "Ilość wymagana"
        elif not itemPrice:
            error = "Cena wymagana"
        elif not itemCategory:
            error = "Kategoria wymagana"
        elif not itemUnit:
            error = "Jednostka wymagana"
        elif not itemLocation:
            error = "Lokalizacja wymagana"
        elif not itemMinQuant:
            error = "Minimala ilość wymagana"
        else:
            try:
                quantity = int(itemQuantity)
                price = float(itemPrice)
                minStock = int(itemMinQuant)
                if quantity or minStock <= 0:
                    error = "Ilość musi być większa niż 0"
                elif price <= 0:
                    error = "Cena musi być większa niż 0"
            except ValueError:
                error = "Ilość i cena muszą być liczbami"

            try:
                db.execute(
                    "INSERT INTO products (productCode, productName, productDescription, category, unit, location, quantityInStock, minimalQuantity, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        itemCode,
                        itemName,
                        itemDesc,
                        itemCategory,
                        itemUnit,
                        itemLocation,
                        itemQuantity,
                        itemMinQuant,
                        itemPrice,
                    ),
                )
                db.commit()
            except db.IntegrityError as e:
                error = f"Błąd integralności: {str(e)} - Produkt o kodzie {itemCode}"
            else:
                return redirect(url_for("index"))

        flash(error)

    return render_template("dashboard/add-item.html")


@bp.route("/products/edit", methods=("GET", "POST"))
@loginRequired
def editItem():
    return render_template("dashboard/edit-item.html")
