import FreeSimpleGUI as sg
from frontend.api_client import ApiClient
from frontend.app_state import AppState
from .screens.login import login_window
from .screens.catalog import catalog_window

state = AppState()
api = ApiClient(base_url="http://127.0.0.1:5000/api/v1")

def main():
    sg.theme("LightBlue2")
    login_data = login_window(state=state, api=api)

    if login_data is None:
        print("User cancelled login")
        return

    print("User submitted credentials:", login_data)

    if state.role.lower() == "customer":
        print("Launching Customer Dashboard...")
        catalog_window(state=state, api=api)
    elif state.role.lower() == "manager":
        print("Launching Manager Dashboard...")
    else:
        print("Unknown role. Access denied.")

if __name__ == "__main__":
    main()