from flask import Blueprint
from flask.templating import render_template

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@bp.route("/users")
def users():
    return render_template("dashboard/users.html")

@bp.route("/products")
def products():
    return render_template("dashboard/products.html")

@bp.route("/index")
def index():
    return render_template("dashboard/index.html")
