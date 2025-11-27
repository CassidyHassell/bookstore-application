CREATE TABLE users (
    id int PRIMARY KEY AUTO_INCREMENT,
    email varchar(100) UNIQUE NOT NULL,
    password_hash varchar(255) NOT NULL,
    first_name varchar(50),
    last_name varchar(50),
    username varchar(255) UNIQUE NOT NULL,
    created_at timestamp NOT NULL DEFAULT now(),
    role enum('customer', 'manager') NOT NULL COMMENT 'User type'
);

CREATE TABLE authors (
    id int PRIMARY KEY AUTO_INCREMENT,
    name varchar(100) NOT NULL,
    bio text
);

CREATE TABLE books (
    id int PRIMARY KEY AUTO_INCREMENT,
    author_id int NOT NULL,
    title varchar(255) NOT NULL,
    description text,
    price_buy decimal(7,2) NOT NULL,
    price_rent decimal(7,2) NOT NULL,
    status enum('new', 'rented', 'sold', 'returned') NOT NULL DEFAULT 'new',
    created_at timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE keywords (
    id int PRIMARY KEY AUTO_INCREMENT,
    word varchar(50) UNIQUE NOT NULL
);

CREATE TABLE book_keywords (
    book_id int NOT NULL,
    keyword_id int NOT NULL,
    PRIMARY KEY (book_id, keyword_id)
);

CREATE TABLE orders (
    id int PRIMARY KEY AUTO_INCREMENT,
    user_id int,
    order_date timestamp NOT NULL DEFAULT (now()),
    payment_status enum('pending', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
    total_price decimal(10,2) NOT NULL,
    email_sent boolean DEFAULT false
);

CREATE TABLE order_lines (
    id int PRIMARY KEY AUTO_INCREMENT,
    order_id int NOT NULL,
    book_id int NOT NULL,
    type enum('buy', 'rent') NOT NULL,
    price decimal(7,2) NOT NULL
);

ALTER TABLE books ADD FOREIGN KEY (author_id) REFERENCES authors (id);

ALTER TABLE book_keywords ADD FOREIGN KEY (book_id) REFERENCES books (id);

ALTER TABLE book_keywords ADD FOREIGN KEY (keyword_id) REFERENCES keywords (id);

ALTER TABLE orders ADD FOREIGN KEY (user_id) REFERENCES users (id);

ALTER TABLE order_lines ADD FOREIGN KEY (order_id) REFERENCES orders (id);

ALTER TABLE order_lines ADD FOREIGN KEY (book_id) REFERENCES books (id);
