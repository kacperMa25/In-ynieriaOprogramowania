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
    """
    Główna strona dashboardu, wyświetla na ekranie pare informacji
    """
    db = get_db()
    wDetails = db.execute(
        "SELECT COUNT(productCode) as howMany, SUM(quantityInStock * price) as howMuch, SUM(quantityInStock < minimalQuantity) as lowStock FROM products"
    ).fetchone()
    return render_template("dashboard/index.html", wDetails=wDetails)


@bp.route("/users")
@loginRequired
def users():
    """
    Podstrona, panel zarządzania użytkownikami, wyświetla ile
    jest w bazie danych użytkowników
    """
    db = get_db()
    wDetails = db.execute(
        "SELECT COUNT(employeeCode) as howMany FROM employees"
    ).fetchone()
    return render_template("dashboard/users.html", wDetails=wDetails)


@bp.route("/users/add", methods=("GET", "POST"))
@loginRequired
def add_user():
    """
    Przetwarzanie formularza z danymi nowego użytkownika, którego mamy na celu dodać.
    """
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
                flash("Pomyślnie dodano użytkownika")
                return redirect(url_for("index"))

        flash(error)
    return render_template("dashboard/add-user.html")


@bp.route("/users/edit", methods=("POST", "GET"))
@loginRequired
def editUser():
    """
    Edycja informacji o użytkowniku
    """
    if request.method == "POST":
        action = request.form.get("action", "save")
        db = get_db()
        error = None
        employeeCode = request.form["employeeCode"]

        if action == "delete":
            try:
                db.execute(
                    "DELETE FROM employees WHERE employeeCode = ?", (employeeCode,)
                )
                db.commit()
                flash("Użytkownik został usunięty pomyślnie")
                return redirect(url_for("dashboard.users"))
            except db.IntegrityError as e:
                error = f"Wystąpił błąd podczas usuwania: {e}"
                flash(error)
                return redirect(url_for("dashboard.users"))

        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        login = request.form["login"]
        password = request.form.get("password", "")
        jobTitle = request.form.get("jobTitle", "")
        reportsTo = request.form.get("reportsTo", "")

        if not firstName or firstName.strip() == "":
            error = "Imię jest wymagane"
        elif not lastName or lastName.strip() == "":
            error = "Nazwisko jest wymagane"
        elif not login or login.strip() == "":
            error = "Login jest wymagany"

        if error is None:
            try:
                if password and password.strip() != "":
                    db.execute(
                        "UPDATE employees SET firstName = ?, lastName = ?, login = ?, password = ?, jobTitle = ?, reportsTo = ? WHERE employeeCode = ?",
                        (
                            firstName,
                            lastName,
                            login,
                            generate_password_hash(password),
                            jobTitle,
                            reportsTo or None,
                            employeeCode,
                        ),
                    )
                else:
                    db.execute(
                        "UPDATE employees SET firstName = ?, lastName = ?, login = ?, jobTitle = ?, reportsTo = ? WHERE employeeCode = ?",
                        (
                            firstName,
                            lastName,
                            login,
                            jobTitle,
                            reportsTo or None,
                            employeeCode,
                        ),
                    )
                db.commit()
                flash("Użytkownik został zaktualizowany pomyślnie")
                return redirect(url_for("dashboard.users"))
            except db.IntegrityError as e:
                error = f"Błąd integralności bazy danych: {e}"

        flash(error)

    return render_template("dashboard/edit-user.html")


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
    """
    Przetwarzanie danych wprowadzonych w formluarzu dodawania przedmiotu do bazy danych
    """
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
                flash("Dodano pomyślnie przedmiot")
                return redirect(url_for("index"))

        flash(error)

    return render_template("dashboard/add-item.html")


@bp.route("/products/edit", methods=("GET", "POST"))
@loginRequired
def editItem():
    """
    Edytowanie, bądź usunięcie już istniejącego przedmiotu
    """
    if request.method == "POST":
        action = request.form.get("action", "save")
        db = get_db()
        error = None
        itemCode = request.form["sku"]

        if action == "delete":
            try:
                db.execute("DELETE FROM products WHERE productCode = ?", (itemCode,))
                db.commit()
                flash("Przedmiot został usunięty pomyślnie")
                return redirect(url_for("dashboard.products"))
            except db.IntegrityError as e:
                error = f"Wystąpił błąd podczas usuwania {e}"
                flash(error)
                return redirect(url_for("dashboard.products"))

        itemName = request.form["itemName"]
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
                    "UPDATE products SET productDescription = ?, category = ?, unit = ?, location = ?, quantityInStock = ?, minimalQuantity = ?, price = ? WHERE productCode = ? OR productName = ?",
                    (
                        itemDesc,
                        itemCategory,
                        itemUnit,
                        itemLocation,
                        itemQuantity,
                        itemMinQuant,
                        itemPrice,
                        itemCode,
                        itemName,
                    ),
                )
                db.commit()
            except db.IntegrityError as e:
                error = f"Błąd integralności: {str(e)} - Produkt o kodzie {itemCode}"
            else:
                flash("Edytowano pomyślnie przedmiot")
                return redirect(url_for("index"))

        flash(error)
    return render_template("dashboard/edit-item.html")


@bp.route("/raport", methods=["GET"])
@loginRequired
def raport():
    """Funkcja weryfikuje czy podane kryteria generowania raportu są prawidłowe,
    przepytuje baze danych, a następnie przesyła informacje do template'u gdzie są one
    wyświetlane."""
    db = get_db()
    category = request.args.get("category", "").lower()
    sortBy = request.args.get("sortBy", "").lower()
    error = None
    wDetails = None
    descAsc = "DESC"

    if category or sortBy:
        if sortBy:
            match sortBy:
                case "nazwa":
                    sortBy = "productName"
                    descAsc = "ASC"
                case "ilość":
                    sortBy = "quantityInStock"
                case "wartość":
                    sortBy = "price"
                case _:
                    sortBy = "productName"
                    descAsc = "ASC"
        else:
            sortBy = "productName"

        try:
            if not category or category == "wszystkie kategorie":
                wDetails = db.execute(
                    f"SELECT productCode, productName, category, quantityInStock, price, location, price * quantityInStock AS valueWhole FROM products ORDER BY {sortBy} {descAsc}"
                ).fetchall()
            else:
                wDetails = db.execute(
                    f"SELECT productCode, productName, category, quantityInStock, price, location, price * quantityInStock AS valueWhole FROM products WHERE category = ? ORDER BY {sortBy} {descAsc}",
                    (category,),
                ).fetchall()
        except db.IntegrityError as e:
            error = f"Naruszono integralność z bazą danych: {str(e)}"
            flash(error)

    categories = db.execute("SELECT DISTINCT category FROM products").fetchall()

    return render_template(
        "dashboard/raport.html", wDetails=wDetails, categories=categories
    )


@bp.route("/products/modifyQuantity", methods=("GET", "POST"))
@loginRequired
def modQuant():
    if request.method == "POST":
        db = get_db()
        productCode = request.form["sku"]
        quantity = request.form["quantity"]
        error = None

        if not productCode:
            error = "Wprowadź kod produktu"
        elif not quantity:
            error = "Wprowadź ilość"

        if error is None:
            try:
                quantDB = db.execute(
                    "SELECT quantityInStock FROM products WHERE productCode = ?",
                    (productCode,),
                ).fetchone()
                if int(quantDB["quantityInStock"]) + int(quantity) < 0:
                    flash(
                        "Przedmiot po aktualizacji byłby na stanie ujemnym, spróbuj ponownie"
                    )
                    return redirect(url_for("dashboard.products"))
                db.execute(
                    "UPDATE products SET quantityInStock = quantityInStock + ? WHERE productCode = ?",
                    (quantity, productCode),
                )
                db.commit()
            except db.IntegrityError as e:
                error = f"Naruszono integralność: {e}"
            else:
                flash("Zaktualizowano ilość")
                return redirect(url_for("dashboard.products"))

        flash(error)
    return render_template("dashboard/modQuant.html")
