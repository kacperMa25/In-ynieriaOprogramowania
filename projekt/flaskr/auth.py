import functools

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
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/init", methods=("GET", "POST"))
def init():
    """
    Endpoint dla strony init.html, sprawdza czy baza jest zainicjowana,
    jeśli nie możliwe jest dodanie jednego użytkownika.
    """
    db = get_db()
    count = db.execute(
        "SELECT COUNT(employeeCode) as howMany FROM employees"
    ).fetchone()
    if count["howMany"] != 0:
        return render_template("auth/message.html")
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        db = get_db()
        error = None

        if not login:
            error = "Login requierd."
        elif not password:
            error = "Password required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO employees (login, password, firstName, lastName) VALUES (?, ?, ?, ?)",
                    (login, generate_password_hash(password), firstName, lastName),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Użytkownik {login} jest już zarejestrowany"
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/init.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """
    Sprawdzanie czy login oraz hasło istnieje w bazie danych,
    jeśli tak jesteśmy przekierowani do dashboardu.
    """
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM employees WHERE login = ?", (login,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["userID"] = user["employeeCode"]
            return redirect(url_for("dashboard.index"))

        flash(error)

    return render_template("auth/login.html")


@bp.before_app_request
def loadLoggedInUser():
    """
    Sprawdza czy w sesji zapamiętane są dane użytkownika,
    jeśli tak automatycznie jesteśmy logowani.
    """
    userID = session.get("userID")

    if userID is None:
        g.user = None
    else:
        g.user = (
            get_db()
            .execute("SELECT * FROM employees WHERE employeeCode = ?", (userID,))
            .fetchone()
        )


@bp.route("/logout")
def logout():
    """
    Czyści sesje i przekireowuje nas do strony logowania
    """
    session.clear()
    return redirect(url_for("auth.login"))


def loginRequired(view):
    """
    Dekorator, który sprawdza czy użytkownik jest zalogowany,
    jeśli nie przekierowani jesteśmy do strony logowania.
    """

    @functools.wraps(view)
    def wrappedView(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrappedView
