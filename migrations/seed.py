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
            username = fake.unique.user_name()
            email = fake.unique.email()
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
    # Batch-insert books to improve performance and avoid huge transactions.
    # We use ORM `add_all` in moderate batches so inserted objects receive
    # primary keys (IDs) which later steps rely on.
    BATCH_SIZE = 200
    try:
        session = SessionLocal()
        books_batch = []
        created_books = []  # keep references to committed ORM Book objects (with IDs)
        for i in range(count):
            if i % 500 == 0 and i > 0:
                print(f"Seeding book {i}/{count}")

            author = random.choice(authors)
            # Use realistic book titles from our provider for more variety
            try:
                title = fake.book_title()
            except Exception:
                # Fallback to a short sentence if provider isn't available
                title = fake.sentence(nb_words=4).rstrip(".")
            description = fake.paragraph(nb_sentences=4)

            # Generate random prices and add 99 cents
            price_buy = Decimal(str(round(random.uniform(5, 50), 2))) + Decimal('0.99')
            price_rent = Decimal(str(round(random.uniform(1, 10), 2))) + Decimal('0.99')

            books_batch.append(Book(
                author_id=author.id,
                title=title,
                description=description,
                price_buy=price_buy,
                price_rent=price_rent,
            ))

            # Flush batch to DB so we don't accumulate too many objects in memory
            if len(books_batch) >= BATCH_SIZE:
                session.add_all(books_batch)
                session.commit()
                # After commit, ORM objects in books_batch have PKs assigned
                created_books.extend(books_batch)
                books_batch = []

        # commit any remaining books
        if books_batch:
            session.add_all(books_batch)
            session.commit()
            created_books.extend(books_batch)

        print("Initial books seeded successfully.")
    except Exception as e:
        session.rollback()
        print("Error seeding initial books:", e)
    finally:
        session.close()
    # Return the list of created ORM Book objects (with `.id` populated)
    return created_books

# CREATE TABLE keywords (
#     id int PRIMARY KEY AUTO_INCREMENT,
#     word varchar(50) UNIQUE NOT NULL
# );
def seed_initial_keywords():
    """Seed the provider keywords into the DB and return ORM Keyword objects.

    Adds diagnostic prints so we can see where the function may block.
    """
    print("seed_initial_keywords: entry", flush=True)
    keywords = []
    try:
        session = SessionLocal()
        print("seed_initial_keywords: Session acquired", flush=True)

        words = fake.all_keywords()
        print(f"seed_initial_keywords: got words count={len(words)}", flush=True)

        for word in words:
            print(f"Seeding keyword {word}", flush=True)
            session.add(Keyword(word=word))
        session.commit()
        print("Initial keywords seeded successfully.", flush=True)

        # Return keyword IDs (ints) so callers don't receive detached ORM objects
        keywords = [r[0] for r in session.query(Keyword.id).all()]
    except Exception as e:
        session.rollback()
        print("Error seeding initial keywords:", e, flush=True)
    finally:
        session.close()
    return keywords

# CREATE TABLE book_keywords (
#     book_id int NOT NULL,
#     keyword_id int NOT NULL,
#     PRIMARY KEY (book_id, keyword_id)
# );
def seed_initial_book_keywords():
    try:
        session = SessionLocal()
        books = session.query(Book).all()
        keywords = session.query(Keyword).all()
        for book in books:
            print(f"Seeding keywords for book id {book.id}")
            num_keywords = fake.random_int(min=1, max=4)
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
    # Batch-insert orders and order_lines to improve throughput.
    # Approach:
    # - Prefetch user IDs and 'new' book IDs once.
    # - For each order, pick user and book(s) from these in-memory lists.
    # - Accumulate Order objects into `orders_batch` and their corresponding
    #   order-line data into `pending_lines`.
    # - When batch is full, add_all(orders_batch) and flush so inserted Order
    #   objects receive primary keys, then create OrderLine objects using those
    #   PKs and add_all(order_lines_batch) before committing.
    BATCH_SIZE = 1000
    try:
        session = SessionLocal()

        # Prefetch candidate ids to avoid ORDER BY RANDOM in the loop
        user_ids = [r[0] for r in session.query(User.id).filter(User.role == 'customer').all()]
        new_book_ids = [r[0] for r in session.query(Book.id).filter(Book.status == 'new').all()]
        if not user_ids:
            print("No customers available to create orders; exiting seeder.")
            return

        orders_batch = []
        pending_lines = []  # list of tuples (Order_obj, [line_dicts])

        for i in range(count):
            print(f"Seeding order {i+1}/{count}")
            user_id = random.choice(user_ids)
            num_order_lines = fake.random_int(min=1, max=5)
            total_price = Decimal('0.00')
            line_items = []

            for _ in range(num_order_lines):
                if not new_book_ids:
                    break
                book_id = random.choice(new_book_ids)
                book = session.get(Book, book_id)
                if not book or book.status != 'new':
                    try:
                        new_book_ids.remove(book_id)
                    except ValueError:
                        pass
                    continue

                order_type = random.choice(['buy', 'rent'])
                price = book.price_buy if order_type == 'buy' else book.price_rent
                # mark book as used locally (will be persisted when we commit)
                book.status = 'sold' if order_type == 'buy' else 'rented'

                # remove id from pool so we don't reuse this book
                try:
                    new_book_ids.remove(book.id)
                except ValueError:
                    pass

                line_items.append({'book_id': book.id, 'type': order_type, 'price': price})
                total_price += price

            if not line_items:
                continue

            new_order = Order(
                user_id=user_id,
                total_price=total_price,
                payment_status='completed',
                email_sent=True,
                order_date=fake.date_time_between(start_date='-6M', end_date='now')
            )
            orders_batch.append(new_order)
            pending_lines.append((new_order, line_items))

            # flush a batch: insert orders, then create corresponding lines
            if len(orders_batch) >= BATCH_SIZE:
                session.add_all(orders_batch)
                session.flush()  # ensures new_order.id is available on each object

                order_lines_batch = []
                for ord_obj, lines in pending_lines:
                    for ld in lines:
                        order_lines_batch.append(OrderLine(
                            order_id=ord_obj.id,
                            book_id=ld['book_id'],
                            type=ld['type'],
                            price=ld['price']
                        ))

                session.add_all(order_lines_batch)
                session.commit()

                # clear batches
                orders_batch = []
                pending_lines = []

        # flush remaining batches
        if orders_batch:
            session.add_all(orders_batch)
            session.flush()
            order_lines_batch = []
            for ord_obj, lines in pending_lines:
                for ld in lines:
                    order_lines_batch.append(OrderLine(
                        order_id=ord_obj.id,
                        book_id=ld['book_id'],
                        type=ld['type'],
                        price=ld['price']
                    ))
            session.add_all(order_lines_batch)
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
    seed_initial_users(count=1000)
    authors = seed_initial_authors(count=5000)
    books = seed_initial_books(authors=authors, count=10000)
    keywords = seed_initial_keywords()
    seed_initial_book_keywords()
    seed_initial_orders_with_lines(count=7500)

if __name__ == "__main__":
    seed_all()