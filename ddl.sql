CREATE DATABASE IF NOT EXISTS ecommerce CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecommerce;

CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    amount DECIMAL(10,2),
    method VARCHAR(255) NOT NULL,
    status BOOLEAN,
    reference VARCHAR(100) UNIQUE,
    created_at TIMESTAMP,
    refunded BOOLEAN NOT NULL DEFAULT 0
);