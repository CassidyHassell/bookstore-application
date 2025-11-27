# Define data models for SQLAlchemy here
from sqlalchemy import Column, ForeignKey, Integer, String, Text
import sqlalchemy, sqlalchemy.orm
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# CREATE TABLE users (
#     id int PRIMARY KEY AUTO_INCREMENT,
#     email varchar(100) UNIQUE NOT NULL,
#     password_hash varchar(255) NOT NULL,
#     first_name varchar(50),
#     last_name varchar(50),
#     username varchar(255) UNIQUE NOT NULL,
#     created_at timestamp NOT NULL DEFAULT now(),
#     role enum('customer', 'manager') NOT NULL COMMENT 'User type'
# );
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(255), unique=True, nullable=False)
    created_at = Column(sqlalchemy.TIMESTAMP, nullable=False, server_default=sqlalchemy.func.now())
    role = Column(sqlalchemy.Enum('customer', 'manager', name='user_roles'), nullable=False)

    orders = sqlalchemy.orm.relationship("Order", back_populates="user")


# CREATE TABLE authors (
#     id int PRIMARY KEY AUTO_INCREMENT,
#     name varchar(100) NOT NULL,
#     bio text
# );
class Author(Base):
    __tablename__ = 'authors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    bio = Column(Text)

    books = sqlalchemy.orm.relationship("Book", back_populates="author")


# CREATE TABLE books (
#     id int PRIMARY KEY AUTO_INCREMENT,
#     author_id int NOT NULL,
#     title varchar(255) NOT NULL,
#     description text,
#     price_buy decimal(7,2) NOT NULL,
#     price_rent decimal(7,2) NOT NULL,
#     status enum('new', 'rented', 'sold', 'returned') NOT NULL DEFAULT 'new',
#     created_at timestamp NOT NULL DEFAULT (now())
# );
# ALTER TABLE books ADD FOREIGN KEY (author_id) REFERENCES authors (id);
class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    price_buy = Column(sqlalchemy.DECIMAL(7, 2), nullable=False)
    price_rent = Column(sqlalchemy.DECIMAL(7, 2), nullable=False)
    status = Column(sqlalchemy.Enum('new', 'rented', 'sold', 'returned', name='book_status'), nullable=False, server_default='new')
    created_at = Column(sqlalchemy.TIMESTAMP, nullable=False, server_default=sqlalchemy.func.now())

    author = sqlalchemy.orm.relationship("Author", back_populates="books")
    keywords = sqlalchemy.orm.relationship("BookKeyword", back_populates="book")
    order_lines = sqlalchemy.orm.relationship("OrderLine", back_populates="book")

# CREATE TABLE keywords (
#     id int PRIMARY KEY AUTO_INCREMENT,
#     word varchar(50) UNIQUE NOT NULL
# );
class Keyword(Base):
    __tablename__ = 'keywords'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(50), unique=True, nullable=False)

    books = sqlalchemy.orm.relationship("BookKeyword", back_populates="keyword")


# CREATE TABLE book_keywords (
#     book_id int NOT NULL,
#     keyword_id int NOT NULL,
#     PRIMARY KEY (book_id, keyword_id)
# );
# ALTER TABLE book_keywords ADD FOREIGN KEY (book_id) REFERENCES books (id);
# ALTER TABLE book_keywords ADD FOREIGN KEY (keyword_id) REFERENCES keywords (id);
class BookKeyword(Base):
    __tablename__ = 'book_keywords'
    
    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True, nullable=False)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), primary_key=True, nullable=False)

    book = sqlalchemy.orm.relationship("Book", back_populates="keywords")
    keyword = sqlalchemy.orm.relationship("Keyword", back_populates="books")


# CREATE TABLE orders (
#     id int PRIMARY KEY AUTO_INCREMENT,
#     user_id int,
#     order_date timestamp NOT NULL DEFAULT (now()),
#     payment_status enum('pending', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
#     total_price decimal(10,2) NOT NULL,
#     email_sent boolean DEFAULT false
# );
# ALTER TABLE orders ADD FOREIGN KEY (user_id) REFERENCES users (id);
class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    order_date = Column(sqlalchemy.TIMESTAMP, nullable=False, server_default=sqlalchemy.func.now())
    payment_status = Column(sqlalchemy.Enum('pending', 'completed', 'cancelled', name='payment_status'), nullable=False, server_default='pending')
    total_price = Column(sqlalchemy.DECIMAL(10, 2), nullable=False)
    email_sent = Column(sqlalchemy.Boolean, default=False)

    user = sqlalchemy.orm.relationship("User", back_populates="orders")
    order_lines = sqlalchemy.orm.relationship("OrderLine", back_populates="order")


# CREATE TABLE order_lines (
#     id int PRIMARY KEY AUTO_INCREMENT,
#     order_id int NOT NULL,
#     book_id int NOT NULL,
#     type enum('buy', 'rent') NOT NULL,
#     price decimal(7,2) NOT NULL
# );
# ALTER TABLE order_lines ADD FOREIGN KEY (order_id) REFERENCES orders (id);
# ALTER TABLE order_lines ADD FOREIGN KEY (book_id) REFERENCES books (id);
class OrderLine(Base):
    __tablename__ = 'order_lines'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    type = Column(sqlalchemy.Enum('buy', 'rent', name='order_line_type'), nullable=False)
    price = Column(sqlalchemy.DECIMAL(7, 2), nullable=False)

    order = sqlalchemy.orm.relationship("Order", back_populates="order_lines")
    book = sqlalchemy.orm.relationship("Book", back_populates="order_lines")
    