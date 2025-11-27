# books.py

import bcrypt
from flask import Blueprint, jsonify, request
from sqlalchemy import select
from db import SessionLocal
from models import User
from auth import current_user

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")

@users_bp.route("/", methods=["GET"])
def get_users():
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


@users_bp.route("/<int:id>", methods=["GET"])
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


@users_bp.route("/current", methods=["GET"])
def get_current_user():
    if current_user.get():
        return jsonify(current_user.get())
    else:
        return jsonify({"error": "No user logged in"}), 401


@users_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            current_user.set({"id": user.id, "username": user.username, "role": user.role})
            return jsonify({"message": "Login successful", "role": user.role})
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    finally:
        session.close()


@users_bp.route("/logout", methods=["POST"])
def logout():
    current_user.clear()
    return jsonify({"message": "Logged out"})


@users_bp.route("/register", methods=["POST"])
def register():
    pass  # Implement registration logic here