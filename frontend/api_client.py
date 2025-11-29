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
    

    def get_all_books(self, jwt: str):
        headers = {"Authorization": f"{jwt}"}
        response = requests.get(f"{self.base_url}/books/", headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to fetch books: " + response.json().get("error", "Unknown error"))
        return response.json()
    

    def get_available_books(self, jwt: str):
        headers = {"Authorization": f"{jwt}"}
        response = requests.get(f"{self.base_url}/books/available", headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to fetch books: " + response.json().get("error", "Unknown error"))
        return response.json()
    

    def get_books_by_status(self, jwt: str, status: str):
        headers = {"Authorization": f"{jwt}"}
        response = requests.get(f"{self.base_url}/books/status/{status}", headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to fetch books by status: " + response.json().get("error", "Unknown error"))
        return response.json()
    
    
    def create_order(self, jwt: str, user_id: int, orderlines: list):
        headers = {"Authorization": f"{jwt}"}
        data = {
            "user_id": user_id,
            "order_lines": orderlines
        }
        response = requests.post(f"{self.base_url}/orders/", json=data, headers=headers)
        if response.status_code != 201:
            raise Exception("Failed to create order: " + response.json().get("error", "Unknown error"))
        return response.json()