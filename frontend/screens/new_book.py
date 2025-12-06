import FreeSimpleGUI as sg

def new_book_window(state, api):

    def create_book(state, api, details, window=None):
        try:
            resp = api.create_book(
                state.jwt,
                details
            )
            if resp.get("error"):
                sg.popup_error(f"Error adding book: {resp.get('error')}")
            else:
                sg.popup("Book added successfully.")
                if window:
                    window.close()
        except Exception as e:
            print(f"Error adding book: {e}")
            sg.popup_error(f"Error adding book")

    author_layout = sg.Frame("Author", [
            [sg.Text("For existing authors, please use Author ID.")],
            [sg.Text("Author ID:"), sg.Input(key="book_author_id", default_text="", enable_events=True)],
            [sg.Text("For new authors, please provide the name and bio below.")],
            [sg.Text("Name:"), sg.Input(key="book_author_name", default_text="")],
            [sg.Text("Bio:"), sg.Multiline(size=(40, 5), key="book_author_bio", default_text="")]
        ])
    layout = [
        [sg.Text("Add New Book")],
        [sg.Text("Title:"), sg.Input(key="book_title", default_text="")],
        [author_layout],
        [sg.Text("Keywords (comma separated):"), sg.Input(key="book_keywords", default_text="")],
        [sg.Text("Price (Buy):"), sg.Input(key="book_price", default_text="")],
        [sg.Text("Price (Rent):"), sg.Input(key="book_rent_price", default_text="")],
        [sg.Text("Description:")],
        [sg.Multiline(size=(60, 5), key="book_description", default_text="")],
        [sg.Button("Add Book"), sg.Button("Cancel")]
    ]

    window = sg.Window("Add New Book", layout, finalize=True)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Cancel":
            break

        elif event == "Add Book":
            # Check all required fields
            # Title, Author (either ID or Name), Prices
            if not values["book_title"].strip():
                sg.popup_error("Title is required.")
                continue
            if not values["book_author_id"].strip() and not values["book_author_name"].strip():
                sg.popup_error("Either Author ID or Author Name is required.")
                continue
            if not values["book_price"].strip() or not values["book_rent_price"].strip():
                sg.popup_error("Both Buy and Rent prices are required.")
                continue
            # If Author ID is provided, validate it's an integer
            if values["book_author_id"].strip():
                try:
                    int(values["book_author_id"].strip())
                except ValueError:
                    sg.popup_error("Author ID must be an integer.")
                    continue
            # If author id is provided, ignore name and bio
            details = {
                "title": values["book_title"],
                "author_id": int(values["book_author_id"].strip()) if values["book_author_id"].strip() else None,
                "author_name": values["book_author_name"].strip() if not values["book_author_id"].strip() else None,
                "author_bio": values["book_author_bio"].strip() if not values["book_author_id"].strip() else None,
                "keywords": values["book_keywords"].strip().split(",") if values["book_keywords"].strip() else [],
                "price_buy": float(values["book_price"].strip()),
                "price_rent": float(values["book_rent_price"].strip()),
                "description": values["book_description"]
            }
            create_book(state, api, details, window=window)
        
        elif event == "book_author_id":
            # Disable name and bio inputs if author ID is provided
            if values["book_author_id"].strip():
                window["book_author_name"].update(disabled=True)
                window["book_author_bio"].update(disabled=True)
            else:
                window["book_author_name"].update(disabled=False)
                window["book_author_bio"].update(disabled=False)


    window.close()