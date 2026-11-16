CREATE   DATABASE ecommerce;
USE ecommerce;

DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100),
    city VARCHAR(100),
    category VARCHAR(100),
    order_status VARCHAR(100),
    price INT,
    quantity INT,
    order_date DATE,
    delivery_date DATE,
    seller_id INT
);

INSERT INTO orders
(order_id, customer_name, city, category, order_status, price, quantity, order_date, delivery_date, seller_id)
VALUES
(1, 'AA', 'Hyderabad', 'Electronics', 'Delivered', 15000, 1, '2026-09-01', '2026-09-04', 101),
(2, 'BB', 'Mumbai', 'Clothing', 'Shipped', 2500, 2, '2026-09-02', '2026-09-06', 102),
(3, 'CC', 'Delhi', 'Groceries', 'Cancelled', 1200, 3, '2026-09-03', NULL, 103),
(4, 'DD', 'Chennai', 'Furniture', 'Pending', 8500, 1, '2026-09-04', NULL, 104),
(5, 'EE', 'Bangalore', 'Electronics', 'Delivered', 22000, 1, '2026-09-05', '2026-09-08', 105);

SELECT * FROM orders;
ALTER TABLE orders
ADD CONSTRAINT fk_seller
FOREIGN KEY (seller_id)
REFERENCES sellers(seller_id);
SELECT * FROM orders WHERE order_status='Delivered';
SELECT * FROM orders WHERE price>5000;
SELECT *
FROM orders
WHERE order_status = 'Pending'
  AND delivery_date IS NULL;
UPDATE orders
SET order_status ='cancelled' WHERE order_id=1;
SELECT * FROM orders;
SELECT city ,
 SUM(price*quantity) AS total_sales
FROM orders
GROUP BY city;

SELECT price
FROM orders
ORDER BY price DESC;
SELECT 
    customer_name,
    order_date,
    delivery_date,
    DATEDIFF(delivery_date, order_date) AS delivery_days
FROM orders;
SELECT 
    category,
    SUM(price * quantity) AS total_sales
FROM orders
GROUP BY category
HAVING total_sales > 100000;
CREATE TABLE sellers (
    seller_id INT PRIMARY KEY,
    seller_name VARCHAR(100),
    seller_city VARCHAR(100)
);
INSERT INTO sellers (seller_id, seller_name, seller_city)
VALUES
(101, 'Ravi', 'Hyderabad'),
(102, 'Priya', 'Mumbai'),
(103, 'Arjun', 'Delhi'),
(104, 'Sneha', 'Chennai'),
(105, 'Kiran', 'Bangalore');
SELECT * 
FROM orders o
 JOIN sellers s
ON o.seller_id=s.seller_id;
SELECT * 
FROM orders o
  LEFT JOIN sellers s
ON o.seller_id=s.seller_id;
CREATE INDEX idx_orders
ON orders(city);
CREATE VIEW QUERY AS 
SELECT * FROM orders WHERE order_status='Delivered';
SELECT * FROM orders WHERE price>(SELECT  AVG(price) FROM orders);
CREATE TABLE orders_2025
(customer_id INT,
customer_name VARCHAR(100));
INSERT INTO orders_2025
(customer_id,customer_name)
VALUES (1,'AKSHITHA'),(2,'ANUSHKA'),(3,'SUDHA');
SELECT * FROM orders_2025;
CREATE TABLE orders_2026
(customer_id INT,
customer_name VARCHAR(100));
INSERT INTO orders_2026
(customer_id,customer_name)
VALUES (1,'AKSHITHA'),(2,'ANUSHKA'),(3,'SRINIVAS');
SELECT * FROM orders_2026;
SELECT customer_name FROM orders_2025
UNION 
SELECT customer_name FROM orders_2026;
SELECT category,city,
    SUM(price * quantity) AS total_sales
FROM orders
GROUP BY category ,city WITH ROLLUP; 
DELIMITER //
CREATE PROCEDURE get_Delivered_orders()
BEGIN 
SELECT * FROM orders
WHERE order_status='DElivered';
END //
DELIMITER ;
call get_Delivered_orders();

DELIMITER //

CREATE PROCEDURE city_orders(IN city_name VARCHAR(100))
BEGIN
    SELECT *
    FROM orders
    WHERE city = city_name;
END //

DELIMITER ;
CALL city_orders('Hyderabad');
CREATE TABLE order_cancellations (
    cancellation_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    cancelled_at DATETIME,
    reason VARCHAR(255)
);
SELECT * FROM order_cancellations;
INSERT INTO order_cancellations
(order_id, cancelled_at, reason)
VALUES
(3, '2026-09-08 10:30:00', 'Order cancelled by user'),
(7, '2026-09-08 11:15:00', 'Payment failed'),
(9, '2026-09-08 12:00:00', 'Customer requested cancellation');
DELIMITER //
CREATE TRIGGER trg_log_order_cancel
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    IF NEW.order_status = 'Cancelled' THEN
        INSERT INTO order_cancellations
        (order_id, cancelled_at, reason)
        VALUES
        (NEW.order_id, NOW(), 'Order cancelled by user');
    END IF;
END //
DELIMITER ;

ALTER USER 'ola_user'@'localhost'
IDENTIFIED BY 'OlaPowerBI2026!';

GRANT ALL PRIVILEGES ON ola_ride_project.* TO 'ola_user'@'localhost';

FLUSH PRIVILEGES;


