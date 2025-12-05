# authors.py

from flask import Blueprint, jsonify, request
from sqlalchemy import or_, select
from api.auth import role_required, token_required
from utils.db import SessionLocal
from utils.models import Author, Book

authors_bp = Blueprint("authors", __name__, url_prefix="/api/v1/authors")


@authors_bp.route("/", methods=["GET"])
@token_required
def get_authors(context):
    session = SessionLocal()
    page_number = request.args.get("page_number", 1, type=int)
    page_size = request.args.get("page_size", 100, type=int)
    include_total = request.args.get("include_total", "false").lower() == "true"
    try:
        authors = session.query(Author).order_by(Author.id).offset((page_number - 1) * page_size).limit(page_size).all()

        authors_list = [{"id": a.id, "name": a.name, "bio": a.bio} for a in authors]
        if include_total:
            total_count = session.query(Author).count()
            return jsonify({"authors": authors_list, "page": {
                "current_page": page_number,
                "total_pages": (total_count + page_size - 1) // page_size,
            }})
        else:
            return jsonify({"authors": authors_list, "page": {
                "current_page": page_number
            }})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@authors_bp.route("/<int:id>", methods=["GET"])
@token_required
def get_author(context, id):
    session = SessionLocal()
    try:
        author = session.get(Author, id)
        if not author:
            return jsonify({"error": "Author not found"}), 404
        return jsonify({"id": author.id, "name": author.name, "bio": author.bio})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@authors_bp.route("/new_author", methods=["POST"])
@token_required
@role_required("Manager")
def create_author(context):
    data = request.json
    name = data.get("name")
    bio = data.get("bio", "No bio available")

    session = SessionLocal()
    try:
        new_author = Author(name=name, bio=bio)
        session.add(new_author)
        session.commit()
        return jsonify({"message": "Author created successfully", "author_id": new_author.id}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# Update author bio
@authors_bp.route("/<int:id>/update", methods=["PUT"])
@token_required
@role_required("Manager")
def update_author_bio(context, id):
    data = request.json
    new_bio = data.get("bio")
    new_name = data.get("name")
    if not new_bio and not new_name:
        return jsonify({"error": "Bio or name are required"}), 400

    session = SessionLocal()
    try:
        author = session.get(Author, id)
        if not author:
            return jsonify({"error": "Author not found"}), 404
        if new_bio:
            author.bio = new_bio
        if new_name:
            author.name = new_name
        session.commit()
        return jsonify({"message": "Author updated successfully"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
