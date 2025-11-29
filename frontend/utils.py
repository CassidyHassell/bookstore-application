import tkinter as tk
from .config import Config
import jwt

SECRET_KEY = Config.JWT_SECRET_KEY

def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

