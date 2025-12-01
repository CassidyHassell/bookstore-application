import FreeSimpleGUI as sg

from frontend.screens.customer_rents import customer_rents_window

orderlines = []

def catalog_window(state, api):

    def fetch_books(state, api, window=None, status="Available", title_filter="", author_id_filter="", keywords_filter=""):
        try:
            status = status if status in ["Available", "New", "Used", "Rented"] else "Available"
            status = status.lower()
            if status == "used":
                status = "returned"
            if status == "all":
                status = None
            
            resp = api.get_books(state.jwt, status=status, author_id=author_id_filter or None, keyword=keywords_filter.split(",") if keywords_filter else None)
            print (resp)
            books = resp.get("books", [])

        except Exception as e:
            print(f"Error fetching books: {e}")
            books = []
        if window:
            # Update the book list in the window
            print(books)
            print("Should update book list on display")
            window["book_list"].update(disabled=False)
            window["book_list"].update(values=[f"{b['id']}: {b['title']} by {b['author']['name']}" for b in filter(lambda b: title_filter.lower() in b['title'].lower(), books)])

            if status == "rented":
                window["book_list"].update(disabled=True)
            else:
                window["book_list"].update(disabled=False)

        return books
    
    books = []

    searches = sg.Frame("Search Books", [
        [sg.Text("Title:"), sg.Input(key="title_search")],
        [sg.Text("Author ID:"), sg.Input(key="author_id_search")],
        [sg.Text("Keywords:"), sg.Input(key="keywords_search")],
        [sg.Text("Status:"), sg.Combo(["Available", "New", "Used", "Rented"], default_value="Available", key="status_search")],
        [sg.Button("Search")]
    ])
    layout = [
        [searches],
        [sg.Text("Catalog")],
        [sg.Listbox(values=[f"{b['id']}: {b['title']}" for b in books], size=(40, 10), key="book_list", select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],
        [sg.Button("Buy Books"), sg.Button("Rent Books"), sg.Button("View Order"), sg.Button("Checkout"), sg.Button("Logout"), sg.Button("Clear Order"), sg.Button("View Rented Books")]
    ]

    window = sg.Window("Catalog", layout, finalize=True)
    books = fetch_books(state, api, window=window)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Logout":
            # Clear state on logout
            state.jwt = None
            state.user_id = None
            state.role = None
            break

        if event == "Buy Books":
            selected = values["book_list"]
            if not selected:
                sg.popup_error("Please select a book to add to the order.")
                continue
            for item in selected:
                # Grab book ID from selected item
                book_id = int(item.split(":")[0]) 
                if any(line["book_id"] == book_id for line in orderlines):
                    sg.popup_error("Book already in order.")
                    continue
                orderlines.append({"book_id": book_id, "type": "buy"})
            values["book_list"].clear()
            sg.popup("Books added to order.")
        
        if event == "Rent Books":
            selected = values["book_list"]
            if not selected:
                sg.popup_error("Please select a book to add to the order.")
                continue
            for item in selected:
                # Grab book ID from selected item
                book_id = int(item.split(":")[0]) 
                if any(line["book_id"] == book_id for line in orderlines):
                    sg.popup_error("Book already in order.")
                    continue
                orderlines.append({"book_id": book_id, "type": "rent"})
            values["book_list"].clear()
            sg.popup("Books added to order.")
        
        if event == "View Order":
            sg.popup("Current Order", "\n".join([f"{line['type'].capitalize()} - Book ID: {line['book_id']}" for line in orderlines]) or "No items in order.")
        
        if event == "Checkout":
            if not orderlines:
                sg.popup_error("No items in order to checkout.")
                continue
            try:
                resp = api.create_order(state.jwt, orderlines=orderlines)
                sg.popup("Order Successful", f"Order ID: {resp.get('order_id')}")
                sg.popup(resp.get('bill'))
                orderlines.clear()
                # Refresh the book list after checkout
                fetch_books(state, api, window=window, status=values["status_search"], title_filter=values["title_search"], author_id_filter=values["author_id_search"], keywords_filter=values["keywords_search"])
            except Exception as e:
                print(f"Error during checkout: {e}")
                sg.popup_error(f"Error during checkout: {e}")

        if event == "Search":
            title = values["title_search"].lower()
            fetch_books(state, api, window=window, status=values["status_search"], title_filter=values["title_search"], author_id_filter=values["author_id_search"], keywords_filter=values["keywords_search"])

        if event == "View Rented Books":
            customer_rents_window(state, api)
            # Refresh the available books list after returning books
            fetch_books(state, api, window=window)

        if event == "Clear Order":
            orderlines.clear()
            sg.popup("Order cleared.")
            
    window.close()

    return 