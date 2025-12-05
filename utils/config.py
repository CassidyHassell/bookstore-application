import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
import jwt

load_dotenv()  # Loads the .env file

class Config:
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_PASSWORD_SAFE = quote_plus(DB_PASSWORD)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET')
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD_SAFE}@{DB_HOST}/{DB_NAME}"
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

def decode_token(token):
    return jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])

