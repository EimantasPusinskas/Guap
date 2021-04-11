DROP TABLE IF EXISTS products;
CREATE TABLE products
(
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    gender TEXT NOT NULL, 
    image_url TEXT NOT NULL
);
INSERT INTO products(name, price, description, category, gender, image_url) 
VALUES ('Grey Cardigan', 39.99, 'A grey cardigan perfect for any occasion ','Cardigan', 'Male', '1.jpg'),
        ('White Jumper', 29.99, 'A stylish white jumper suitable for any occasion','Jumper', 'Female', '2.jpg'),
        ('Maroon T-Shirt', 19.99, 'A Maroon T-Shirt ideal for any occasion','T-Shirt', 'Male', '3.jpg'),   
        ('Black Hoodie', 24.99, 'A black hoodie perfect for any occasion','Hoodie', 'Male', '4.jpg'),
        ('Black T-Shirt', 19.99, 'A black T-shirt suitable for any occasion', 'T-Shirt','Female', '5.jpg'),
        ('Beige T-Shirt', 19.99, 'A beige T-Shirt suitable for any occasion','T-Shirt', 'Male', '7.jpg'),
        ('White Shirt', 29.99, 'A stylish white shirt perfect for any occasion', 'Shirt','Male', '8.jpg'),
        ('White T-Shirt', 19.99, 'A fashionable white T-shirt suitable for any occasion', 'T-Shirt','Female', '9.jpg'),
        ('Red Jumper', 24.99, 'A red jumper suitable for any occasion', 'Jumper', 'Female', '11.jpg'),
        ('Denim Jacket', 49.99, 'A stylish denim jacket perfect for any occasion','Jacket', 'Male', '10.jpg');
      

DROP TABLE IF EXISTS stock;
CREATE TABLE stock
(
    product_id INTEGER,
    size TEXT NOT NULL, 
    quantity INT NOT NULL
);
INSERT INTO stock(product_id, size, quantity)
VALUES (1, 'Small', 10),
        (1, 'Medium', 20), 
        (1, 'Large', 30),
        (2, 'Small', 10),
        (2, 'Medium', 20), 
        (2, 'Large', 30),
        (3, 'Small', 10),
        (3, 'Medium', 20), 
        (3, 'Large', 30),
        (4, 'Small', 10),
        (4, 'Medium', 20), 
        (4, 'Large', 30),
        (5, 'Small', 10),
        (5, 'Medium', 20), 
        (5, 'Large', 30),
        (6, 'Small', 10),
        (6, 'Medium', 20), 
        (6, 'Large', 30),
        (7, 'Small', 10),
        (7, 'Medium', 20), 
        (7, 'Large', 30),
        (8, 'Small', 10),
        (8, 'Medium', 20), 
        (8, 'Large', 30),
        (9, 'Small', 10),
        (9, 'Medium', 20), 
        (9, 'Large', 30),
        (10, 'Small', 10),
        (10, 'Medium', 20), 
        (10, 'Large', 30);



DROP TABLE IF EXISTS customers;
CREATE TABLE customers
(
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);


DROP TABLE IF EXISTS orders;
CREATE TABLE orders
(
    username TEXT NOT NULL, 
    product_id INT NOT NULL, 
    product_size TEXT NOT NULL, 
    product_quantity INT NOT NULL,  
    date_of_order INT NOT NULL, 
    order_cost INT NOT NULL 
);


DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews
(
    username TEXT NOT NULL, 
    product_id INT NOT NULL, 
    review TEXT NOT NULL,
    date_of_review INT NOT NULL,
    rating INT NOT NULL
);



DROP TABLE IF EXISTS messages;
CREATE TABLE messages
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL, 
    recipient TEXT NOT NULL, 
    message TEXT NOT NULL, 
    date_sent INT NOT NULL
);


