import FreeSimpleGUI as sg
from frontend.async_wrapper import run_in_background

def customer_rents_window(state, api):
    
    def fetch_rented_books(state, api):
        try:
            resp = api.get_user_rented_books(state.jwt)
            rented = resp.get("books", [])
            for book in rented:
                resp = api.get_book_details(state.jwt, book['id'])
            return rented
        except Exception as e:
            print(f"Error fetching rented books: {e}")
            return []
    
    rented = []
    layout = [
        [sg.Text("Your Rented Books")],
        [sg.Listbox(values=[f"{b['id']}: {b['title']}" for b in rented], size=(40, 10), key="rent_list", select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],
        [sg.Button("Return Selected Books"), sg.Button("Close")]
    ]
    window = sg.Window("Customer Rentals", layout, finalize=True)
    rented = run_in_background(window, "-RENTED_BOOKS_LOADED-", fetch_rented_books, state, api)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Close":
            break
        
        if event == "Return Selected Books":
            selected_books = values["rent_list"]
            if not selected_books:
                sg.popup_error("Please select books to return.")
                continue
            for item in selected_books:
                # Grab book ID from selected item
                success = True
                book_id = int(item.split(":")[0]) 
                resp_json = api.return_book(state.jwt, book_id)
                if resp_json.get("error"):
                    sg.popup_error(f"Error returning book ID {book_id}: {resp_json.get('error')}")
                    success = False
            if success:
                sg.popup("Selected books returned successfully.")
            # Refresh the rented books list
            run_in_background(window, "-RENTED_BOOKS_LOADED-", fetch_rented_books, state, api)
        
        if event == "-RENTED_BOOKS_LOADED-":
            payload = values[event]
            if payload["ok"]:
                rented = payload["result"]
            else:
                rented = []
            print(f"Rented books updated: {rented}")
            if rented == []:
                window["rent_list"].update(['No rented books found.'])
            else:
                window["rent_list"].update([f"{b['id']}: {b['title']}" for b in rented])
            
                
    window.close()