# books.py

import datetime
import bcrypt
from flask import Blueprint, jsonify, request
from sqlalchemy import select
from api.auth import role_required, token_required
from utils.db import SessionLocal
from utils.models import User
from utils.config import Config
# from auth import current_user
import jwt

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")


@users_bp.route("/", methods=["GET"])
@token_required
@role_required("Manager")
def get_users(context):
    session = SessionLocal()
    page_number = request.args.get("page_number", 1, type=int)
    page_size = request.args.get("page_size", 100, type=int)
    role = request.args.get("role", None)

    filters = []

    if role and role not in ["Customer", "Manager"]:
        return jsonify({"error": "Invalid role filter"}), 400
    
    if role is not None:
        filters.append(User.role == role)

    try:
        users = session.query(User).order_by(User.id).filter(*filters).offset((page_number - 1) * page_size).limit(page_size).all()

        users_list = [{"id": u.id, "username": u.username, "email": u.email, "role": u.role} for u in users]
        return jsonify({"users": users_list, "page": {
            "current_page": page_number,
            "total_pages": (session.query(User).filter(*filters).count() + page_size - 1) // page_size,
        }})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@users_bp.route("/<int:id>", methods=["GET"])
@token_required
@role_required("Manager")
def get_user(context, id):
    session = SessionLocal()
    try:
        user = session.get(User, id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"id": user.id, "username": user.username, "email": user.email, "role": user.role, "first_name": user.first_name, "last_name": user.last_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@users_bp.route("/me", methods=["GET"])
@token_required
def get_current_user(context):
    id = context['id']
    session = SessionLocal()
    try:
        user = session.get(User, id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"id": user.id, "username": user.username, "email": user.email, "role": user.role, "first_name": user.first_name, "last_name": user.last_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@users_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            # Create token
            token = jwt.encode({"id": user.id, "role": user.role, "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)}, Config.JWT_SECRET_KEY, algorithm="HS256")
            # Return user token in response
            return jsonify({"message": "Login successful", "token": token})
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    finally:
        session.close()


# Logout will be handled client-side by deleting the token
@users_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Logged out"})


@users_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    session = SessionLocal()

    try:
        # Check if username or email already exists
        existing_user = session.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return jsonify({"error": "Username or email already exists"}), 400

        # Hash the password
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

        # Create new user
        new_user = User(username=username, email=email, password_hash=password_hash, role=role, first_name=first_name, last_name=last_name)
        session.add(new_user)
        session.commit()

        return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()