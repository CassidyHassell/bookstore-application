import FreeSimpleGUI as sg

def manager_books_window(state, api):

    def fetch_books(state, api, window=None, status="All"):
        try:
            if status == "All":
                resp = api.get_all_books(state.jwt)
            elif status == "Available":
                resp = api.get_available_books(state.jwt)
            elif status == "New":
                resp = api.get_books_by_status(state.jwt, "new")
            elif status == "Used":
                resp = api.get_books_by_status(state.jwt, "returned")
            elif status == "Rented Out":
                resp = api.get_books_by_status(state.jwt, "rented")
            elif status == "Sold":
                resp = api.get_books_by_status(state.jwt, "sold")
            else:
                # Default to available books if unknown status
                resp = api.get_all_books(state.jwt)
            books = resp.get("books", [])
        except Exception as e:
            print(f"Error fetching books: {e}")
            books = []
        if window:
            # Update the book list in the window
            window["books_list"].update(values=[f"{b['id']}: {b['title']} by {b['author']['name']}" for b in books])

        return books
    
    def load_book_details(state, api, book_id, window=None):
        # Placeholder for loading book details into the form
        try:
            resp = api.get_book_details(state.jwt, book_id)
        except Exception as e:
            print(f"Error fetching book details: {e}")
            resp = {}
        if window:
            window["book_id"].update(resp.get("id", ""))
            window["book_title"].update(resp.get("title", ""))
            window["book_author_name"].update(resp.get("author", {}).get("name", ""))
            window["book_author_id"].update(resp.get("author", {}).get("id", ""))
            window["book_keywords"].update(", ".join([kw.get("word", "") for kw in resp.get("keywords", [])]))
            window["book_price"].update(resp.get("price_buy", ""))
            window["book_rent_price"].update(resp.get("price_rent", ""))
            window["book_status"].update(resp.get("status", ""))
            window["book_description"].update(resp.get("description", ""))
        
    def update_book(state, api, details, window=None):
        # Placeholder for updating book details via the API
        pass

    searches = sg.Frame("Search Books", [
        [sg.Text("Title:"), sg.Input(key="title_search")],
        [sg.Text("Author:"), sg.Input(key="author_search")],
        [sg.Text("Keywords:"), sg.Input(key="keywords_search")],
        [sg.Text("Status:"), sg.Combo(["All", "Available", "New", "Used", "Sold", "Rented Out"], default_value="All", key="status_search")],
        [sg.Button("Search")]
    ])
    buttons = [
        sg.Button("Back")
    ]
    book_details = sg.Frame("Book Details", [
        [sg.Text("ID:"), sg.Text("", key="book_id")],
        [sg.Text("Title:"), sg.Input(key="book_title", default_text="")],
        [sg.Text("Author:"), sg.Text("ID:"), sg.Input(key="book_author_id", default_text="", size=(5,1)), sg.Text("Name:"), sg.Text("", key="book_author_name")],
        [sg.Text("Keywords:"), sg.Input(key="book_keywords", default_text="")],
        [sg.Text("Buy Price:"), sg.Input(key="book_price", default_text="")],
        [sg.Text("Rent Price:"), sg.Input(key="book_rent_price", default_text="")],
        [sg.Text("Description:")],
        [sg.Multiline(size=(60, 5), key="book_description", default_text="")],
        [sg.Text("Status:"), sg.Text("", key="book_status")],
        [sg.Button("Update Book"), sg.Button("Delete Book")]
    ])
    books_layout = [
        [sg.Listbox(values=[], size=(80, 20), key="books_list", enable_events=True), book_details]
    ]
    layout = [
        [sg.Text("Manager Books Dashboard")],
        [searches],
        books_layout,
        buttons
    ]

    window = sg.Window("Manager Books Dashboard", layout, finalize=True)

    # Initial fetch of books
    fetch_books(state, api, window=window)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Back":
            break
        elif event == "books_list":
            selected = values["books_list"]
            if selected:
                book_id = int(selected[0].split(":")[0])
                if book_id:
                    load_book_details(state, api, book_id, window=window)
        elif event == "Search":
            print("Searching books...")
            fetch_books(state, api, window=window, status=values["status_search"])
        elif event == "Update Book":
            print("Updating book...")
        elif event == "Delete Book":
            print("Deleting book...")


    window.close()