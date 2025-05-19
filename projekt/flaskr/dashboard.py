from flask import Blueprint
from flask.templating import render_template

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@bp.route("/usersPane")
def usersPane():
    return render_template("dashboard/usersPane.html")

@bp.route("/productsPane")
def productsPane():
    return render_template("dashboard/productsPane.html")
