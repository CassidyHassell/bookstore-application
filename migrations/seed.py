from sqlalchemy import create_engine, text, MetaData
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()  # Loads the .env file

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Password contains a special character, so safety is needed
DB_PASSWORD_SAFE = quote_plus(DB_PASSWORD)

SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD_SAFE}@{DB_HOST}/{DB_NAME}"

# Connect to the actual database
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    print("Connected to the database.")
except Exception as e:
    print("Error connecting to the database:", e)

# Function to seed initial user data
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
def seed_initial_users():
    # Pre-hashed passwords for "mypass" for testing purposes
    raw_password = "mypass"
    password = raw_password.encode()
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))
    
    users = [
        {
            "email": "cassidy.hassell@tamu.edu",
            "password_hash": hashed.decode(),
            "first_name": "Cassidy",
            "last_name": "Hassell",
            "username": "cassidy.hassell",
            "role": "manager"
        },
        {
            "email": "john.doe@example.com",
            "password_hash": "hashed_password_2",
            "first_name": "John",
            "last_name": "Doe",
            "username": "john.doe",
            "role": "customer"
        }
    ]
    try:
        statement = text("INSERT INTO users (email, password_hash, first_name, last_name, username, role) VALUES (:email, :password_hash, :first_name, :last_name, :username, :role)")
        with engine.connect() as conn:
            for user in users:
                conn.execute(statement, user)
            conn.commit()
        print("Initial users seeded successfully.")
    except Exception as e:
        print("Error seeding initial users:", e)

# CREATE TABLE authors (
#     id int PRIMARY KEY AUTO_INCREMENT,
#     name varchar(100) NOT NULL,
#     bio text
# );
def seed_initial_authors():
    authors = [
        {
            "name": "Author One",
            "bio": "Bio of Author One"
        },
        {
            "name": "Author Two",
            "bio": "Bio of Author Two"
        }
    ]
    try:
        statement = text("INSERT INTO authors (name, bio) VALUES (:name, :bio)")
        with engine.connect() as conn:
            for author in authors:
                conn.execute(statement, author)
            conn.commit()
        print("Initial authors seeded successfully.")
    except Exception as e:
        print("Error seeding initial authors:", e)

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
def seed_initial_books():
    books = [
        {
            "author_id": 1,
            "title": "Book One",
            "description": "Description of Book One",
            "price_buy": 19.99,
            "price_rent": 4.99,
            "status": "new"
        },
        {
            "author_id": 2,
            "title": "Book Two",
            "description": "Description of Book Two",
            "price_buy": 29.99,
            "price_rent": 6.99,
            "status": "new"
        }
    ]
    try:
        statement = text("INSERT INTO books (author_id, title, description, price_buy, price_rent, status) VALUES (:author_id, :title, :description, :price_buy, :price_rent, :status)")
        with engine.connect() as conn:
            for book in books:
                conn.execute(statement, book)
            conn.commit()
        print("Initial books seeded successfully.")
    except Exception as e:
        print("Error seeding initial books:", e)

# CREATE TABLE keywords (
#     id int PRIMARY KEY AUTO_INCREMENT,
#     word varchar(50) UNIQUE NOT NULL
# );
def seed_initial_keywords():
    keywords = [
        {"word": "Fiction"},
        {"word": "Science"},
        {"word": "History"}
    ]
    try:
        statement = text("INSERT INTO keywords (word) VALUES (:word)")
        with engine.connect() as conn:
            for keyword in keywords:
                conn.execute(statement, keyword)
            conn.commit()
        print("Initial keywords seeded successfully.")
    except Exception as e:
        print("Error seeding initial keywords:", e)

# CREATE TABLE book_keywords (
#     book_id int NOT NULL,
#     keyword_id int NOT NULL,
#     PRIMARY KEY (book_id, keyword_id)
# );
def seed_initial_book_keywords():
    book_keywords = [
        {"book_id": 1, "keyword_id": 1},
        {"book_id": 1, "keyword_id": 2},
        {"book_id": 2, "keyword_id": 3}
    ]
    try:
        statement = text("INSERT INTO book_keywords (book_id, keyword_id) VALUES (:book_id, :keyword_id)")
        with engine.connect() as conn:
            for bk in book_keywords:
                conn.execute(statement, **bk)
            conn.commit()
        print("Initial book_keywords seeded successfully.")
    except Exception as e:
        print("Error seeding initial book_keywords:", e)

# CREATE TABLE orders (
#     id int PRIMARY KEY AUTO_INCREMENT,
#     user_id int,
#     order_date timestamp NOT NULL DEFAULT (now()),
#     payment_status varchar(20) NOT NULL DEFAULT 'pending',
#     total_price decimal(10,2) NOT NULL,
#     email_sent boolean DEFAULT false
# );
# CREATE TABLE order_lines (
#     id int PRIMARY KEY AUTO_INCREMENT,
#     order_id int NOT NULL,
#     book_id int NOT NULL,
#     type varchar(10) NOT NULL COMMENT 'buy or rent',
#     price decimal(7,2) NOT NULL
# );
def seed_initial_orders_with_lines():

    orders = [
        {
            "user_id": 1,
            "total_price": 24.98,
            "payment_status": "completed",
            "email_sent": True
        }
    ]
    order_lines = [
        {
            "order_id": 1,
            "book_id": 1,
            "type": "buy",
            "price": 19.99
        },
        {
            "order_id": 1,
            "book_id": 2,
            "type": "rent",
            "price": 4.99
        }
    ]
    try:
        order_statement = text("INSERT INTO orders (user_id, total_price, payment_status, email_sent) VALUES (:user_id, :total_price, :payment_status, :email_sent)")
        order_line_statement = text("INSERT INTO order_lines (order_id, book_id, type, price) VALUES (:order_id, :book_id, :type, :price)")
        with engine.connect() as conn:
            for order in orders:
                result = conn.execute(order_statement, order)
                order_id = result.lastrowid
                for line in order_lines:
                    if line["order_id"] == order_id:
                        conn.execute(order_line_statement, line)
            conn.commit()
        print("Initial orders and order lines seeded successfully.")
    except Exception as e:
        print("Error seeding initial orders and order lines:", e)
    
def empty_all_tables():
    metadata = MetaData()
    print("Emptying all tables...")
    try:
        metadata.reflect(bind=engine)
        with engine.connect() as conn:
            for table in reversed(metadata.sorted_tables):
                conn.execute(table.delete())
            conn.commit()
        print("All tables emptied")
        # Reset auto-increment counters
        with engine.connect() as conn:
            for table in metadata.sorted_tables:
                conn.execute(text(f"ALTER TABLE {table.name} AUTO_INCREMENT = 1"))
            conn.commit()
    except Exception as e:
        print("Error emptying tables from database:", e)

def seed_all():
    empty_all_tables()
    seed_initial_users()
    seed_initial_authors()
    seed_initial_books()
    seed_initial_keywords()
    seed_initial_book_keywords()
    seed_initial_orders_with_lines()

if __name__ == "__main__":
    seed_all()