# books.py

import bcrypt
from flask import Blueprint, jsonify, request
from sqlalchemy import select
from auth import role_required, token_required
from db import SessionLocal
from models import User
from config import Config
# from auth import current_user
import jwt

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")


# TODO: require admin role
@users_bp.route("/", methods=["GET"])
@token_required
@role_required("Manager")
def get_users(context):
    session = SessionLocal()
    try:
        users = session.query(User).all()
        if not users:
            return jsonify({"error": "No users found"}), 404

        users_list = [{"id": u.id, "username": u.username, "email": u.email, "role": u.role} for u in users]
        return jsonify({"users": users_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# Testing route TODO: Remove later or require admin role
@users_bp.route("/<int:id>", methods=["GET"])
@token_required
@role_required("Manager")
def get_user(id):
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
            token = jwt.encode({"id": user.id, "role": user.role}, Config.JWT_SECRET_KEY, algorithm="HS256")
            # Return user token in response
            return jsonify({"message": "Login successful", "token": token})
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    finally:
        session.close()


@users_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Logged out"})


@users_bp.route("/register", methods=["POST"])
def register():
    pass  # Implement registration logic here