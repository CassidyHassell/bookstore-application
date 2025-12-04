from datetime import datetime
from decimal import Decimal
import random
from sqlalchemy import func, text, MetaData
import bcrypt
from faker import Faker
from utils.db import SessionLocal
from utils.faker_providers import BookTitleProvider, KeywordsProvider
from utils.models import Author, Book, BookKeyword, Keyword, Order, OrderLine, User

fake = Faker('en_US')  # For English data

# register the provider on our Faker instance
fake.add_provider(BookTitleProvider)
fake.add_provider(KeywordsProvider)

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
def seed_initial_users(count=10000):
    # Pre-hashed passwords for "pass" for testing purposes
    raw_password = "pass"
    password = raw_password.encode()
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))
    password_hash=hashed.decode()
    
    test_manager = User(
        email="cassidy.hassell@tamu.edu",
        password_hash=password_hash,
        first_name="Cassidy",
        last_name="Hassell",
        username="manager",
        role="manager"
    )
    test_customer = User(
        email="cassidy.n.hassell@gmail.com",
        password_hash=password_hash,
        first_name="Cassidy",
        last_name="Hassell",
        username="customer",
        role="customer"
    )
    try:
        session = SessionLocal()
        # Add predefined users
        session.add(test_manager)
        session.add(test_customer)

        # Use same password for all seeded users for seeding efficiency
        for _ in range(count):
            print (f"Seeding user {_+1}/{count}")
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}{fake.random_int(1, 99)}"
            email = fake.email()
            session.add(User(
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                username=username,
                role=random.choice(["customer", "manager"])
            ))
        session.commit()
        print("Initial users seeded successfully.")
    except Exception as e:
        session.rollback()
        print("Error seeding initial users:", e)
    finally:
        session.close()


# CREATE TABLE authors (
#     id int PRIMARY KEY AUTO_INCREMENT,
#     name varchar(100) NOT NULL,
#     bio text
# );
def seed_initial_authors(count=1000):
    authors = []
    try:
        session = SessionLocal()
        for _ in range(count):
            print(f"Seeding author {_+1}/{count}")
            name = fake.name()
            bio = fake.text(max_nb_chars=200)
            session.add(
                Author(
                    name=name,
                    bio=bio
                )
            )
        session.commit()
        print("Initial authors seeded successfully.")
    except Exception as e:
        session.rollback()
        print("Error seeding initial authors:", e)
    finally:
        authors.extend(session.query(Author).all())
        session.close()
    return authors

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
def seed_initial_books(authors, count=1000000):
    try:
        session = SessionLocal()
        for _ in range(count):
            print(f"Seeding book {_+1}/{count}")
            author = random.choice(authors)
            # Use realistic book titles from our provider for more variety
            try:
                title = fake.book_title()
            except Exception:
                # Fallback to a short sentence if provider isn't available
                title = fake.sentence(nb_words=4).rstrip(".")
            description = fake.paragraph(nb_sentences=4)

            price_buy = Decimal(str(round(random.uniform(5, 50), 2)))
            price_rent = Decimal(str(round(random.uniform(1, 10), 2)))

            book = Book(
                author_id=author.id,
                title=title,
                description=description,
                price_buy=price_buy,
                price_rent=price_rent,
            )
            session.add(book)
        session.commit()
        print("Initial books seeded successfully.")
    except Exception as e:
        session.rollback()
        print("Error seeding initial books:", e)
    finally:
        books = session.query(Book).all()
        session.close()
    return books

# CREATE TABLE keywords (
#     id int PRIMARY KEY AUTO_INCREMENT,
#     word varchar(50) UNIQUE NOT NULL
# );
def seed_initial_keywords():
    try:
        session = SessionLocal()
        words = fake.all_keywords()

        for word in words:
            print(f"Seeding keyword {word}")
            session.add(
                Keyword(
                    word=word
                )
            )
        session.commit()
        print("Initial keywords seeded successfully.")
    except Exception as e:
        session.rollback()
        print("Error seeding initial keywords:", e)
    finally:
        keywords = session.query(Keyword).all()
        session.close()
    return keywords

# CREATE TABLE book_keywords (
#     book_id int NOT NULL,
#     keyword_id int NOT NULL,
#     PRIMARY KEY (book_id, keyword_id)
# );
def seed_initial_book_keywords(books, keywords):
    try:
        session = SessionLocal()
        for book in books:
            print(f"Seeding keywords for book id {book.id}")
            num_keywords = fake.random_int(min=1, max=5)
            available = len(keywords) if keywords else 0
            if available == 0:
                continue
            take = min(num_keywords, available)
            
            # Use random.sample to pick unique keywords safely
            try:
                selected_keywords = random.sample(keywords, k=take)
            except ValueError:
                selected_keywords = [random.choice(keywords) for _ in range(take)]
            for keyword in selected_keywords:
                session.add(
                    BookKeyword(
                        book_id=book.id,
                        keyword_id=keyword.id
                    )
                )
        session.commit()
        print("Initial book_keywords seeded successfully.")
    except Exception as e:
        session.rollback()
        print("Error seeding initial book_keywords:", e)
    finally:
        session.close()

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
def seed_initial_orders_with_lines(count=500000):
    try:
        session = SessionLocal()
        for _ in range(count):
            print(f"Seeding order {_+1}/{count}")
            user = session.query(User).filter(User.role == 'customer').order_by(func.random()).first()
            if not user:
                continue

            num_order_lines = fake.random_int(min=1, max=5)
            order_lines_data = []
            total_price = Decimal('0.00')

            for _ in range(num_order_lines):
                book = session.query(Book).filter(Book.status == 'new').order_by(func.random()).first()
                if not book:
                    continue

                order_type = random.choice(['buy', 'rent'])
                if order_type == 'buy':
                    price = book.price_buy
                    book.status = 'sold'
                else:
                    price = book.price_rent
                    book.status = 'rented'

                order_lines_data.append({
                    'book_id': book.id,
                    'type': order_type,
                    'price': price
                })
                total_price += price

            if not order_lines_data:
                continue

            # Create order with random date time in the past 6 months
            new_order = Order(
                user_id=user.id,
                total_price=total_price,
                payment_status='completed',
                email_sent=True,
                order_date=fake.date_time_between(start_date='-6M', end_date='now')
            )
            session.add(new_order)
            session.flush()  # Ensure new_order.id is available

            for ol_data in order_lines_data:
                new_order_line = OrderLine(
                    order_id=new_order.id,
                    book_id=ol_data['book_id'],
                    type=ol_data['type'],
                    price=ol_data['price']
                )
                session.add(new_order_line)
        session.commit()
        print("Initial orders and order lines seeded successfully.")
    except Exception as e:
        session.rollback()
        print("Error seeding initial orders and order lines:", e)
    finally:
        session.close()
    
def empty_all_tables():
    print("Emptying all tables...")
    try:
        with SessionLocal() as session:
            engine = session.get_bind()
            metadata = MetaData()
            metadata.reflect(bind=engine)

            # Delete rows from all tables
            for table in reversed(metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()
            print("All tables emptied")

            # Reset auto-increment counters
            for table in reversed(metadata.sorted_tables):
                session.execute(text(f"ALTER TABLE {table.name} AUTO_INCREMENT = 1"))
            session.commit()
            print("Auto-increment counters reset")

    except Exception as e:
        session.rollback()
        print("Error emptying tables from database:", e)
    finally:
        session.close()


def seed_all():
    empty_all_tables()
    seed_initial_users(count=100)
    authors = seed_initial_authors(count=100)
    books = seed_initial_books(authors=authors, count=1000)
    keywords = seed_initial_keywords()
    seed_initial_book_keywords(books, keywords)
    seed_initial_orders_with_lines(count=500)

if __name__ == "__main__":
    seed_all()