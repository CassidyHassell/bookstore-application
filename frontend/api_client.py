import requests
from utils.config import decode_token

class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url


    # SIGN IN / REGISTERATION
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
    
    def register(self, username: str, password: str, email: str, first_name: str, last_name: str, role: str) -> dict:
        response = requests.post(f"{self.base_url}/users/register", json={
            "username": username,
            "password": password,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": role
        })
        if response.status_code != 200 and response.status_code != 201:
            raise Exception("Registration failed: " + response.json().get("error", "Unknown error"))
        return response.json()
    
    
    # USERS
    def get_users(self, jwt: str, role=None, include_total=False, page_number=1, page_size=100):
        headers = {"Authorization": f"{jwt}"}
        params = {
            "page_number": page_number,
            "page_size": page_size,
            "include_total": str(include_total).lower()
        }
        if role is not None:
            params["role"] = role
        response = requests.get(f"{self.base_url}/users/", headers=headers, params=params)
        if response.status_code != 200:
            raise Exception("Failed to fetch users: " + response.json().get("error", "Unknown error"))
        return response.json()
    
    def get_user_details(self, jwt: str, user_id: int):
        headers = {"Authorization": f"{jwt}"}
        response = requests.get(f"{self.base_url}/users/{user_id}", headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to fetch user details: " + response.json().get("error", "Unknown error"))
        return response.json()
    

    # BOOKS
    def get_books(self, jwt: str, author_id=None, status=None, keyword=None, title_contains=None, include_total=False, page_number=1, page_size=100):
        headers = {"Authorization": f"{jwt}"}
        params = {}
        if author_id is not None:
            params["author_id"] = author_id
        if status is not None:
            params["status"] = status
        if keyword is not None:
            params["keyword"] = keyword 
        if title_contains is not None:
            params["title_contains"] = title_contains
        params["include_total"] = str(include_total).lower()
        params["page_number"] = page_number
        params["page_size"] = page_size
        response = requests.get(f"{self.base_url}/books/", headers=headers, params=params)
        if response.status_code != 200:
            raise Exception("Failed to fetch books: " + response.json().get("error", "Unknown error"))
        return response.json()
    
    def get_book_details(self, jwt: str, book_id: int):
        headers = {"Authorization": f"{jwt}"}
        response = requests.get(f"{self.base_url}/books/{book_id}", headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to fetch book details: " + response.json().get("error", "Unknown error"))
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
    
    def add_book(self, jwt: str, data):
        headers = {"Authorization": f"{jwt}"}
        response = requests.post(f"{self.base_url}/books/new_book", json=data, headers=headers)
        if response.status_code != 200 and response.status_code != 201:
            raise Exception("Failed to add book: " + response.json().get("error", "Unknown error"))
        return response.json()
    
    def update_book(self, jwt: str, book_id: int, data):
        headers = {"Authorization": f"{jwt}"}
        response = requests.put(f"{self.base_url}/books/{book_id}/update", json=data, headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to update book: " + response.json().get("error", "Unknown error"))
        return response.json()
    

    # ORDERS
    def get_orders(self, jwt: str, status=None, include_total=True, page_number=1, page_size=100):
        headers = {"Authorization": f"{jwt}"}
        params = {}
        if status is not None:
            params["status"] = status
        params["include_total"] = str(include_total).lower()
        params["page_number"] = page_number
        params["page_size"] = page_size
        response = requests.get(f"{self.base_url}/orders/", headers=headers, params=params)
        if response.status_code != 200:
            raise Exception("Failed to fetch orders: " + response.json().get("error", "Unknown error"))
        return response.json()
    
    def get_order_details(self, jwt: str, order_id: int):
        headers = {"Authorization": f"{jwt}"}
        response = requests.get(f"{self.base_url}/orders/{order_id}", headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to fetch order details: " + response.json().get("error", "Unknown error"))
        return response.json()
    
    def create_order(self, jwt: str, orderlines: list):
        headers = {"Authorization": f"{jwt}"}
        data = {
            "order_lines": orderlines
        }
        response = requests.post(f"{self.base_url}/orders/create_order", json=data, headers=headers)
        if response.status_code != 200 and response.status_code != 201:
            try:
                raise Exception("Failed to create order: " + response.json().get("error", "Unknown error"))
            except Exception as e:
                raise Exception(str(response.status_code) + " " + str(e))
            
        return response.json()
    
    def update_order_status(self, jwt: str, order_id: int, new_status: str):
        headers = {"Authorization": f"{jwt}"}
        data = {"status": new_status}
        response = requests.patch(f"{self.base_url}/orders/{order_id}/status", json=data, headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to update order status: " + response.json().get("error", "Unknown error"))
        return response.json()
    

    # AUTHORS
    def get_authors(self, jwt: str, include_total=True, page_number=1, page_size=100):
        headers = {"Authorization": f"{jwt}"}
        params = {
            "include_total": str(include_total).lower(),
            "page_number": page_number,
            "page_size": page_size
        }
        response = requests.get(f"{self.base_url}/authors/", headers=headers, params=params)
        if response.status_code != 200:
            raise Exception("Failed to fetch authors: " + response.json().get("error", "Unknown error"))
        return response.json()
    
    def get_author_details(self, jwt: str, author_id: int):
        headers = {"Authorization": f"{jwt}"}
        response = requests.get(f"{self.base_url}/authors/{author_id}", headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to fetch author details: " + response.json().get("error", "Unknown error"))
        return response.json()