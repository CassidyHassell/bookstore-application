import FreeSimpleGUI as sg

from frontend.screens.manager_books import manager_books_window
from frontend.screens.manager_orders import manager_orders_window

def manager_window(state, api):
    layout = [
        [sg.Text("Manager Dashboard")],
        [sg.Button("Manage Books"), sg.Button("View Orders"), sg.Button("Logout")]
    ]

    window = sg.Window("Manager Dashboard", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Logout":
            # Clear state on logout
            state.jwt = None
            state.user_id = None
            state.role = None
            break
        elif event == "Manage Books":
            manager_books_window(state, api)
        elif event == "View Orders":
            manager_orders_window(state, api)

    window.close()