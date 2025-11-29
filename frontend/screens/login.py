import FreeSimpleGUI as sg

def login_window(state, api):
    layout = [
        [sg.Text("Username"), sg.Input(key="username")],
        [sg.Text("Password"), sg.Input(password_char="*", key="password")],
        [sg.Text("", key="error", text_color="red")],
        [sg.Button("Login"), sg.Button("Cancel")],
    ]

    window = sg.Window("Login", layout)

    result = None
    success = False

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Cancel":
            break
        if event == "Login":
            username = values["username"]
            password = values["password"]

            if not username or not password:
                window["error"].update("Please enter both username and password.")
                continue

            try:
                resp = api.login(username, password)
            except Exception as e:
                window["error"].update(f"Login error: {e}")
                print(f"Login error: {e}")
                continue

            state.jwt = resp.get("token")
            state.user_id = resp.get("user_id")
            state.role = resp.get("role")
            success = True
            break
            
    window.close()

    return success