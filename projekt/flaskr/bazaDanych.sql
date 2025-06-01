DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS products;

CREATE TABLE employees (
    employeeCode INTEGER PRIMARY KEY AUTOINCREMENT,
    lastName VARCHAR(50) NOT NULL,
    firstName VARCHAR(50) NOT NULL,
    login VARCHAR(30) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    reportsTo INTEGER,
    jobTitle VARCHAR(50),
    FOREIGN KEY (reportsTo) REFERENCES employees (employeeCode)
);

CREATE TABLE products (
    productCode VARCHAR(20) PRIMARY KEY,
    productName TEXT NOT NULL,
    productDescription TEXT NOT NULL,
    category VARCHAR(30),
    unit VARCHAR(20),
    location VARCHAR(50),
    quantityInStock INTEGER NOT NULL,
    minimalQuantity INTEGER,
    price DECIMAL(10, 2) NOT NULL
);
