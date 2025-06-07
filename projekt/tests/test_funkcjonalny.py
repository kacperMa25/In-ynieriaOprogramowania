import os
import tempfile
import pytest
from flask import session
from werkzeug.security import generate_password_hash
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(
    os.path.join(os.path.dirname(__file__), "../flaskr/bazaDanych.sql"), "rb"
) as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    """Tworzenie i konfiguracja aplikacji Flask do testów."""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
        }
    )

    with app.app_context():
        init_db()
        db = get_db()
        db.execute(
            "INSERT INTO employees (login, password, firstName, lastName) VALUES (?, ?, ?, ?)",
            (
                "testadmin",
                generate_password_hash("password123"),
                "Test",
                "Admin",
            ),
        )
        db.commit()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Klient testowy dla aplikacji."""
    return app.test_client()


@pytest.fixture
def auth(client):
    """Pomocnicza funkcja do uwierzytelniania użytkowników w testach."""

    class AuthActions:
        def login(self, username="testadmin", password="password123"):
            return client.post(
                "/auth/login", data={"login": username, "password": password}
            )

        def logout(self):
            return client.get("/auth/logout")

    return AuthActions()


def test_logowanie(client, auth):
    """Test funkcjonalności logowania użytkownika."""
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Login" in response.data

    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get("/")
        assert session["userID"] == 1

    response = client.post(
        "/auth/login", data={"login": "wronguser", "password": "password123"}
    )
    assert b"Incorrect username" in response.data

    response = client.post(
        "/auth/login", data={"login": "testadmin", "password": "wrongpassword"}
    )
    assert b"Incorrect password" in response.data


def test_dodawanie_uzytkownika(client, auth):
    """Test dodawania nowego użytkownika."""
    auth.login()

    response = client.get("/users/add")
    assert response.status_code == 200
    assert b"Dodaj uzytkownika" in response.data

    response = client.post(
        "/users/add",
        data={
            "firstName": "Jan",
            "lastName": "Kowalski",
            "login": "jkowalski",
            "password": "testowe_haslo",
        },
    )
    assert response.headers["Location"] == "/"
    with client.application.app_context():
        db = get_db()
        user = db.execute(
            "SELECT * FROM employees WHERE login = 'jkowalski'"
        ).fetchone()
        assert user is not None
        assert user["firstName"] == "Jan"
        assert user["lastName"] == "Kowalski"


def test_dodawanie_produktu(client, auth):
    """Test dodawania nowego produktu."""
    auth.login()

    response = client.get("/products/add")
    assert response.status_code == 200
    assert b"Dodaj przedmiot" in response.data

    response = client.post(
        "/products/add",
        data={
            "itemName": "Testowy Produkt",
            "sku": "TEST123",
            "description": "Opis testowego produktu",
            "category": "Elektronika",
            "unit": "szt",
            "location": "Magazyn A",
            "minStock": "5",
            "quantity": "10",
            "price": "99.99",
        },
    )
    assert response.headers["Location"] == "/"

    with client.application.app_context():
        db = get_db()
        product = db.execute(
            "SELECT * FROM products WHERE productCode = 'TEST123'"
        ).fetchone()
        assert product is not None
        assert product["productName"] == "Testowy Produkt"
        assert product["quantityInStock"] == 10
        assert float(product["price"]) == 99.99


def test_przyjecie_towaru(client, auth):
    """Test przyjęcia towaru (modyfikacji ilości produktu)."""
    auth.login()
    client.post(
        "/products/add",
        data={
            "itemName": "Produkt do modyfikacji",
            "sku": "MOD456",
            "description": "Opis produktu do modyfikacji",
            "category": "Elektronika",
            "unit": "szt",
            "location": "Magazyn B",
            "minStock": "5",
            "quantity": "10",
            "price": "49.99",
        },
    )

    response = client.get("/products/modifyQuantity")
    assert response.status_code == 200
    assert b"Modyfikacja stanu" in response.data

    response = client.post(
        "/products/modifyQuantity",
        data={
            "sku": "MOD456",
            "quantity": "5",
        },
    )
    assert response.headers["Location"] == "/products"

    with client.application.app_context():
        db = get_db()
        product = db.execute(
            "SELECT * FROM products WHERE productCode = 'MOD456'"
        ).fetchone()
        assert product is not None
        assert product["quantityInStock"] == 15  # 10 + 5
