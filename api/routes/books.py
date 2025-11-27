# books.py

from flask import Blueprint, jsonify
from sqlalchemy import select
from db import SessionLocal
from models import Book

books_bp = Blueprint("books", __name__, url_prefix="/api/v1/books")

@books_bp.route("/", methods=["GET"])
def get_books():
    session = SessionLocal()
    try:
        books = session.query(Book).all()
        if not books:
            return jsonify({"error": "No books found"}), 404

        books_list = [{"id": b.id, "title": b.title, "status": b.status, "author": b.author, "price_buy": b.price_buy, "price_rent": b.price_rent} for b in books]
        return jsonify({"books": books_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@books_bp.route("/<int:id>", methods=["GET"])
def get_book(id):
    session = SessionLocal()
    try:
        book = session.get(Book, id)
        if not book:
            return jsonify({"error": "Book not found"}), 404
        return jsonify({"id": book.id, "title": book.title, "status": book.status, "author": book.author, "price_buy": book.price_buy, "price_rent": book.price_rent, "description": book.description})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()