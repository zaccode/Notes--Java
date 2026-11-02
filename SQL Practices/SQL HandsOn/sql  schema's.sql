-- Create employee management database
CREATE DATABASE IF NOT EXISTS company;
USE company;

-- Core Tables
CREATE TABLE employees (
    emp_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(10),
    salary DECIMAL(10,2),
    department VARCHAR(50),
    designation VARCHAR(50),
    manager_id INT,
    hire_date DATE,
    city VARCHAR(50),
    bonus DECIMAL(10,2),
    experience_years INT
);

CREATE TABLE departments (
    dept_id INT PRIMARY KEY AUTO_INCREMENT,
    dept_name VARCHAR(100) UNIQUE,
    location VARCHAR(100),
    budget DECIMAL(15,2)
);

CREATE TABLE projects (
    project_id INT PRIMARY KEY AUTO_INCREMENT,
    project_name VARCHAR(100),
    department VARCHAR(50),
    status VARCHAR(20),
    start_date DATE,
    end_date DATE,
    budget DECIMAL(15,2)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    order_date DATE,
    amount DECIMAL(10,2),
    status VARCHAR(20),
    product_category VARCHAR(50)
);

CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    city VARCHAR(50),
    registration_date DATE,
    email VARCHAR(100)
);

CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2),
    stock_quantity INT
);

CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2)
);
