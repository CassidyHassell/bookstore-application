import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()  # Loads the .env file

class Config:
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_PASSWORD_SAFE = quote_plus(DB_PASSWORD)
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD_SAFE}@{DB_HOST}/{DB_NAME}"