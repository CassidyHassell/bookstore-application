import FreeSimpleGUI as sg

def registration_window(state, api, role="customer"):
    layout = [
        [sg.Text("Register New Account")],
        [sg.Text("Email"), sg.Input(key="email")],
        [sg.Text("First Name"), sg.Input(key="first_name")],
        [sg.Text("Last Name"), sg.Input(key="last_name")],
        [sg.Text("Username"), sg.Input(key="username")],
        [sg.Text("Password"), sg.Input(password_char="*", key="password")],
        [sg.Text("", key="error", text_color="red")],
        [sg.Button("Register"), sg.Button("Cancel")],
    ]

    window = sg.Window("Register", layout)

    result = None
    success = False

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Cancel":
            break
        if event == "Register":
            username = values["username"]
            password = values["password"]
            email = values["email"]
            first_name = values["first_name"]
            last_name = values["last_name"]

            if not username or not password or not email or not first_name or not last_name:
                window["error"].update("Please fill in all fields.")
                continue

            if "@" not in email or "." not in email:
                window["error"].update("Please enter a valid email address.")
                continue

            try:
                resp = api.register(username, password, email, first_name, last_name, role=role)
            except Exception as e:
                window["error"].update(f"Registration error: {e}")
                print(f"Registration error: {e}")
                continue

            state.jwt = resp.get("token")
            state.user_id = resp.get("user_id")
            state.role = resp.get("role")
            success = True
            break
            
    window.close()

    return success