import os

from flask import Flask, render_template
from flask.helpers import url_for
from werkzeug.utils import redirect


def create_app(test_config=None):
    """
    Funkcja odpalana jest automatycznie przy komendzie run,
    określa w którym miejscu powstanie plik binarny bazy danych,
    gdzie znajdują się testy do przeprowadzenia,
    oraz rejestruje wszystkie blueprinty
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "warehouse.sqlite"),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db

    db.init_app(app)

    from . import api

    app.register_blueprint(api.bp)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import dashboard

    app.register_blueprint(dashboard.bp)
    app.add_url_rule("/", endpoint="index")

    return app
