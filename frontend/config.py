import os
from dotenv import load_dotenv

load_dotenv()  # Loads the .env file

class Config:
    JWT_SECRET_KEY = os.getenv('JWT_SECRET')
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:5000/api/v1')