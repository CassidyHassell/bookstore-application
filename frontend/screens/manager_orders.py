import FreeSimpleGUI as sg

def manager_orders_window(state, api):
    layout = [
        [sg.Text("Manager Orders Dashboard")],
        [sg.Button("View All Orders"), sg.Button("Back")]
    ]

    window = sg.Window("Manager Orders Dashboard", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Back":
            break
        elif event == "View All Orders":
            sg.popup("Orders management feature is under development.")

    window.close()