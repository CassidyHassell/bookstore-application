import FreeSimpleGUI as sg
from frontend.api_client import ApiClient
from frontend.app_state import AppState
from frontend.screens.manager import manager_window
from .screens.login import login_window
from .screens.catalog import catalog_window

state = AppState()
api = ApiClient(base_url="http://127.0.0.1:5000/api/v1")

def main():
    sg.theme("LightGreen3")
    login_window(state=state, api=api)

if __name__ == "__main__":
    main()