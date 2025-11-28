# Extract token from Authorization header
from functools import wraps

from flask import jsonify, request
import jwt
from db import SessionLocal
from config import Config
from models import User


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        session = SessionLocal()
        token = request.headers.get('Authorization')
        print("Token received:", token)

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            print("Decoded token data:", data)
            current_user = session.query(User).filter_by(id=data['id']).first()
            if (not current_user):
                return jsonify({'message': 'User not found!'}), 401
        except jwt.InvalidSignatureError:
            print("Error: Invalid token signature.")
            return jsonify({'message': 'Token is invalid!'}), 401
        except jwt.ExpiredSignatureError:
            print("Error: Token has expired.")
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError as e:
            print(f"Error: Invalid token - {e}")
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return jsonify({'message': 'Token is invalid!'}), 401
        return func(data, *args, **kwargs)

    return decorated