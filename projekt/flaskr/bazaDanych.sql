DROP TABLE IF EXISTS employees;

DROP TABLE IF EXISTS products;

CREATE TABLE employees (
    employeeCode INTEGER PRIMARY KEY AUTOINCREMENT,
    lastName TEXT NOT NULL,
    firstName TEXT NOT NULL,
    login TEXT NOT NULL,
    password TEXT NOT NULL,
    reportsTo INTEGER,
    jobTitle TEXT,
    FOREIGN KEY (reportsTo) REFERENCES employees (employeeCode)
);

CREATE TABLE products (
    productCode INTEGER PRIMARY KEY AUTOINCREMENT,
    productName TEXT NOT NULL,
    productLine TEXT NOT NULL,
    productScale TEXT NOT NULL,
    productVendor TEXT NOT NULL,
    productDescription TEXT NOT NULL,
    quantityInStock INTEGER NOT NULL,
    buyPrice DECIMAL(10, 2) NOT NULL,
    MSRP DECIMAL(10, 2) NOT NULL
);

INSERT INTO
    employees (lastName, firstName, login, password, jobTitle)
VALUES
    ("admin", "admin", "admin", "admin", "admin");
