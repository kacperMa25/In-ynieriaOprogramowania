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
    productCode TEXT PRIMARY KEY,
    productName TEXT NOT NULL,
    productDescription TEXT NOT NULL,
    quantityInStock INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);
