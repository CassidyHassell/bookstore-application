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
    
    
    def create_order(self, jwt: str, orderlines: list):
        headers = {"Authorization": f"{jwt}"}
        print(f"{orderlines}")
        data = {
            "order_lines": orderlines
        }
        response = requests.post(f"{self.base_url}/orders/create_order", json=data, headers=headers)
        if response.status_code != 200 and response.status_code != 201:
            try:
                print(response.json())
                raise Exception("Failed to create order: " + response.json().get("error", "Unknown error"))
            except Exception as e:
                raise Exception(str(response.status_code) + " " + str(e))
            
        print(response.json())
        return response.json()
    
    def get_user_rented_books(self, jwt: str):
        headers = {"Authorization": f"{jwt}"}
        response = requests.get(f"{self.base_url}/books/rented", headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to fetch rented books: " + response.json().get("error", "Unknown error"))
        return response.json()
    
    def return_book(self, jwt: str, book_id: int):
        headers = {"Authorization": f"{jwt}"}
        response = requests.patch(f"{self.base_url}/books/{book_id}/return", headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to return book: " + response.json().get("error", "Unknown error"))
        return response.json()
    
    def get_book_details(self, jwt: str, book_id: int):
        headers = {"Authorization": f"{jwt}"}
        response = requests.get(f"{self.base_url}/books/{book_id}", headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to fetch book details: " + response.json().get("error", "Unknown error"))
        return response.json()