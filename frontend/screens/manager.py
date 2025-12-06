import FreeSimpleGUI as sg

from frontend.screens.login import login_window
from frontend.screens.manager_books import manager_books_window
from frontend.screens.manager_orders import manager_orders_window
from frontend.screens.registration import registration_window

def manager_window(state, api):
    actions = sg.Frame("Actions", [
        [sg.Button("Manage Books"), sg.Button("View Orders"), sg.Button("Add New Manager")]
    ])  # Placeholder for future action buttons
    layout = [
        [sg.Text("Manager Dashboard")],
        [actions, sg.Button("Logout")],
    ]

    window = sg.Window("Manager Dashboard", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            # Clear state on logout
            state.jwt = None
            state.user_id = None
            state.role = None
            break
        if event == "Logout":
            # Clear state on logout
            state.jwt = None
            state.user_id = None
            state.role = None
            window.close()
            login_window(state, api)
            return
        elif event == "Manage Books":
            window.disappear()
            manager_books_window(state, api)
            window.reappear()
        elif event == "View Orders":
            window.disappear()
            manager_orders_window(state, api)
            window.reappear()
        elif event == "Add New Manager":
            window.disappear()
            registration_window(state, api, role="manager")
            window.reappear()

    window.close()