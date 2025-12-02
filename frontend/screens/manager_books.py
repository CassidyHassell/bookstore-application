import FreeSimpleGUI as sg

from frontend.screens.new_book import new_book_window

def manager_books_window(state, api):

    def fetch_books(state, api, window=None, status="All", title_filter="", author_id_filter="", keywords_filter=""):
        try:
            status = status if status in ["All", "Available", "New", "Used", "Sold", "Rented"] else "All"
            status = status.lower()
            if status == "used":
                status = "returned"
            if status == "all":
                status = None
            
            resp = api.get_books(state.jwt, status=status, author_id=author_id_filter or None, keyword=keywords_filter.split(",") if keywords_filter else None)
            books = resp.get("books", [])

        except Exception as e:
            print(f"Error fetching books: {e}")
            books = []
        if window:
            # Update the book list in the window
            window["books_list"].update(values=[f"{b['id']}: {b['title']} by {b['author']['name']}" for b in filter(lambda b: title_filter.lower() in b['title'].lower(), books)])

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
            window["book_author_name"].update(resp.get("author", {}).get("name", ""), text_color="black")
            window["book_author_id"].update(resp.get("author", {}).get("id", ""))
            window["book_keywords"].update(", ".join([kw.get("word", "") for kw in resp.get("keywords", [])]))
            window["book_price"].update(resp.get("price_buy", ""))
            window["book_rent_price"].update(resp.get("price_rent", ""))
            window["book_status"].update(resp.get("status", ""))
            window["book_description"].update(resp.get("description", ""))
        
    def update_book(state, api, book_id, details, window=None):
        try:
            resp = api.update_book(
                state.jwt,
                book_id,
                details
            )
            if details.get("author_id") is None:
                sg.popup_warning("Warning: Book has no associated author.")
            if resp.get("error"):
                print(f"Error updating book: {resp.get('error')}")
                sg.popup_error(f"Error updating book")
        except Exception as e:
            print(f"Error updating book: {e}")
            sg.popup_error(f"Error updating book")

    searches = sg.Frame("Search Books", [
        [sg.Text("Title:"), sg.Input(key="title_search")],
        [sg.Text("Author ID:"), sg.Input(key="author_id_search")],
        [sg.Text("Keywords:"), sg.Input(key="keywords_search")],
        [sg.Text("Status:"), sg.Combo(["All", "Available", "New", "Used", "Sold", "Rented"], default_value="All", key="status_search")],
        [sg.Button("Search")]
    ])
    buttons = [
        sg.Button("Back"), sg.Button("Add New Book")
    ]
    book_details = sg.Frame("Book Details", [
        [sg.Text("ID:"), sg.Text("", key="book_id")],
        [sg.Text("Title:"), sg.Input(key="book_title", default_text="")],
        [sg.Text("Author:"), sg.Text("ID:"), sg.Input(key="book_author_id", default_text="", size=(5,1), enable_events=True), sg.Text("Name:"), sg.Text("", key="book_author_name")],
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
            fetch_books(state, api, window=window, status=values["status_search"], title_filter=values["title_search"], author_id_filter=values["author_id_search"], keywords_filter=values["keywords_search"])
        elif event == "Update Book":
            print("Updating book...")

            # Validate fields
            if not window["book_id"].get():
                sg.popup_error("Please select a book to update.")
                continue
            author_name = window["book_author_name"].get()
            if author_name == "Invalid Author ID" or author_name == "Error fetching author":
                sg.popup_error("Cannot update book: Invalid Author ID.")
                continue

            details = {
                "title": values["book_title"],
                "keywords": values["book_keywords"].strip().split(",") if values["book_keywords"].strip() else [],
                "price_buy": float(values["book_price"].strip()),
                "price_rent": float(values["book_rent_price"].strip()) if values["book_rent_price"].strip() else None,
                "description": values["book_description"].strip(),
                "author_id": int(values["book_author_id"].strip()) if values["book_author_id"].strip() else None,
            }
            update_book(state, api, int(window["book_id"].get()), details, window=window)
            # Refresh book list after update
            fetch_books(state, api, window=window, status=values["status_search"], title_filter=values["title_search"], author_id_filter=values["author_id_search"], keywords_filter=values["keywords_search"])

        elif event == "Delete Book":
            print("Deleting book...")
        elif event == "Add New Book":
            new_book_window(state=state, api=api)
            # Refresh book list after adding new book
            fetch_books(state, api, window=window, status=values["status_search"], title_filter=values["title_search"], author_id_filter=values["author_id_search"], keywords_filter=values["keywords_search"])
        elif event == "book_author_id":
            author_id_input = values["book_author_id"].strip()
            if author_id_input:
                try:
                    author_id = int(author_id_input)
                    # Fetch author details
                    resp = api.get_author_details(state.jwt, author_id)
                    author_name = resp.get("name")
                    window["book_author_name"].update(author_name, text_color="black")
                except ValueError:
                    window["book_author_name"].update("Enter a valid integer ID", text_color="red")
                except Exception as e:
                    print(f"Error fetching author details: {e}")
                    window["book_author_name"].update("No author found", text_color="red")

    window.close()