# books.py

from flask import Blueprint, jsonify, request
from sqlalchemy import or_, select
from auth import role_required, token_required
from db import SessionLocal
from models import Author, Book, Order, OrderLine

books_bp = Blueprint("books", __name__, url_prefix="/api/v1/books")


@books_bp.route("/", methods=["GET"])
@token_required
def get_books(context):
    session = SessionLocal()
    try:
        books = session.query(Book).all()

        books_list = [{"id": b.id, "title": b.title, "status": b.status, "author": {"id": b.author.id, "name": b.author.name}, "price_buy": b.price_buy, "price_rent": b.price_rent} for b in books]
        return jsonify({"books": books_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@books_bp.route("/<int:id>", methods=["GET"])
@token_required
def get_book(context, id):
    session = SessionLocal()
    try:
        book = session.get(Book, id)
        if not book:
            return jsonify({"error": "Book not found"}), 404
        return jsonify({"id": book.id, "title": book.title, "status": book.status, "author": {"id": book.author.id, "name": book.author.name}, "price_buy": book.price_buy, "price_rent": book.price_rent, "description": book.description})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@books_bp.route("/status/<string:status>", methods=["GET"])
@token_required
def get_books_by_status(context, status):
    session = SessionLocal()
    try:
        books = session.query(Book).filter(Book.status == status).all()
        if not books:
            return jsonify({"error": f"No books found with status '{status}'"}), 404
        books_list = [{"id": b.id, "title": b.title, "status": b.status, "author": {"id": b.author.id, "name": b.author.name}, "price_buy": b.price_buy, "price_rent": b.price_rent} for b in books]
        return jsonify({"books": books_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@books_bp.route("/author/<int:author_id>", methods=["GET"])
@token_required
def get_books_by_author(context, author_id):
    session = SessionLocal()
    try:
        books = session.query(Book).filter(Book.author_id == author_id).all()
        if not books:
            return jsonify({"error": f"No books found for author ID '{author_id}'"}), 404
        books_list = [{"id": b.id, "title": b.title, "status": b.status, "author": {"id": b.author.id, "name": b.author.name}, "price_buy": b.price_buy, "price_rent": b.price_rent} for b in books]
        return jsonify({"books": books_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@books_bp.route("/available", methods=["GET"])
@token_required
def get_available_books(context):
    session = SessionLocal()
    try:
        books = session.query(Book).filter(or_(Book.status == "new", Book.status == "returned")).all()
        
        books_list = [{"id": b.id, "title": b.title, "status": b.status, "author": {"id": b.author.id, "name": b.author.name}, "price_buy": b.price_buy, "price_rent": b.price_rent} for b in books]
        return jsonify({"books": books_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@books_bp.route("/unavailable", methods=["GET"])
@token_required
def get_unavailable_books(context):
    session = SessionLocal()
    try:
        books = session.query(Book).filter(or_(Book.status == "rented", Book.status == "sold")).all()
        
        books_list = [{"id": b.id, "title": b.title, "status": b.status, "author": {"id": b.author.id, "name": b.author.name}, "price_buy": b.price_buy, "price_rent": b.price_rent} for b in books]
        return jsonify({"books": books_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# Get current user's rented books
@books_bp.route("/rented", methods=["GET"])
@token_required
@role_required("Customer")
def get_user_rented_books(context):
    user_id = context['id']
    session = SessionLocal()
    try:
        # Fetch rented books for the user from orders with user_id, order_line with type 'rent', and books with status 'rented'
        books = session.query(Book).join(OrderLine).join(Order).filter(Order.user_id == user_id, OrderLine.type == 'rent', Book.status == 'rented').all()
        
        books_list = [{"id": b.id} for b in books]
        return jsonify({"books": books_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@books_bp.route("/new_book", methods=["POST"])
@token_required
@role_required("Manager")
def create_book(context):
    data = request.json
    title = data.get("title")
    author_id = data.get("author_id", None)
    author_name = data.get("author_name", "Unknown Author")
    author_bio = data.get("author_bio", "No bio available")
    price_buy = data.get("price_buy")
    price_rent = data.get("price_rent")
    description = data.get("description", None)

    session = SessionLocal()
    try:
        if (author_id is None):
            new_author = Author(name=author_name, bio=author_bio)
            session.add(new_author)
            # Ensure new_author.id is available
            session.flush()
            author_id = new_author.id
        new_book = Book(title=title, author_id=author_id, price_buy=price_buy, price_rent=price_rent, description=description)
        session.add(new_book)
        session.commit()
        return jsonify({"message": "Book created successfully", "book_id": new_book.id}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# Update book status manually
@books_bp.route("/<int:id>/status", methods=["PATCH"])
@token_required
@role_required("Manager")
def update_book_status(context, id):
    data = request.json
    new_status = data.get("status")

    session = SessionLocal()
    try:
        book = session.get(Book, id)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        book.status = new_status
        session.commit()
        return jsonify({"message": "Book status updated successfully"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# Returned rented book
@books_bp.route("/<int:id>/return", methods=["PATCH"])
@token_required
@role_required("Customer")
def return_rented_book(context, id):
    user_id = context['id']
    session = SessionLocal()
    try:
        book = session.get(Book, id)
        if not book:
            return jsonify({"error": "Book not found"}), 404
        if book.status != 'rented':
            return jsonify({"error": "Book is not currently rented"}), 400

        # Verify that the book is rented by the current user
        order_line = session.query(OrderLine).join(Order).filter(Order.user_id == user_id, OrderLine.book_id == id, OrderLine.type == 'rent').first()
        if not order_line:
            return jsonify({"error": "You have not rented this book"}), 403

        book.status = 'returned'
        session.commit()
        return jsonify({"message": "Book returned successfully"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()