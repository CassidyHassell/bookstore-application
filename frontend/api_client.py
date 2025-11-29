import requests
from .utils import decode_token

class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def login(self, username: str, password: str) -> dict:
        response = requests.post(f"{self.base_url}/users/login", json={"username": username, "password": password})
        if (response.status_code != 200):
            raise Exception("Login failed: " + response.json().get("error", "Unknown error"))
        token = response.json().get("token")
        user_id = decode_token(token).get("id")
        role = decode_token(token).get("role")
        return {
            "token": token,
            "user_id": user_id,
            "role": role
        }
