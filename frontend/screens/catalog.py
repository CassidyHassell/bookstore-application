import FreeSimpleGUI as sg

from frontend.screens.customer_rents import customer_rents_window
from frontend.pagination import PaginationControls

orderlines = []
current_page = 1
PAGE_SIZE = 100

def catalog_window(state, api):

    pagination_controls = PaginationControls(current_page=1, total_pages=1, base_key='Page')

    def fetch_books(state, api, window=None, status="Available", title_filter="", author_id_filter="", keywords_filter="", page=1, page_size=PAGE_SIZE):
        try:
            status = status if status in ["Available", "New", "Used", "Rented"] else "Available"
            status = status.lower()
            if status == "used":
                status = "returned"
            if status == "all":
                status = None
            
            resp = api.get_books(state.jwt, status=status, author_id=author_id_filter or None, title_contains=title_filter or None, keyword=keywords_filter.split(",") if keywords_filter else None, page_number=page, page_size=page_size)
            books = resp.get("books", [])
            total_pages = resp.get("page", None).get("total_pages", 1)
            pagination_controls.update_total_pages(total_pages)

        except Exception as e:
            print(f"Error fetching books: {e}")
            books = []
        if window:
            # Update the book list in the window
            window["book_list"].update(values=[f"{b['id']}: {b['title']} by {b['author']['name']}" for b in books])

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
    
    books = []

    searches = sg.Frame("Search Books", [
        [sg.Text("Title:"), sg.Input(key="title_search")],
        [sg.Text("Author ID:"), sg.Input(key="author_id_search")],
        [sg.Text("Keywords:"), sg.Input(key="keywords_search")],
        [sg.Text("Status:"), sg.Combo(["Available", "New", "Used", "Rented"], default_value="Available", key="status_search")],
        [sg.Button("Search")]
    ])
    pagination_layout = pagination_controls.get_layout()
    books_layout = sg.Frame("Books", [
        [sg.Listbox(values=[], size=(40, 10), key="book_list", enable_events=True)],
        pagination_layout
    ])
    book_details = sg.Frame("Book Details", [
        [sg.Text("ID:"), sg.Text("", key="book_id")],
        [sg.Text("Title:"), sg.Text("", key="book_title")],
        [sg.Text("Author:"), sg.Text("ID:"), sg.Text("", key="book_author_id", size=(5,1)), sg.Text("Name:"), sg.Text("", key="book_author_name")],
        [sg.Text("Keywords:"), sg.Text("", key="book_keywords")],
        [sg.Text("Buy Price:"), sg.Text("", key="book_price")],
        [sg.Text("Rent Price:"), sg.Text("", key="book_rent_price")],
        [sg.Text("Description:")],
        [sg.Multiline(size=(60, 5), key="book_description", default_text="", disabled=True), ],
        [sg.Text("Status:"), sg.Text("", key="book_status")],
    ])
    layout = [
        [searches],
        [books_layout, book_details],
        [sg.Button("Buy Books"), sg.Button("Rent Books"), sg.Button("View Order"), sg.Button("Checkout"), sg.Button("Logout"), sg.Button("Clear Order"), sg.Button("View Rented Books")]
    ]

    window = sg.Window("Catalog", layout, finalize=True)
    pagination_controls.attach_window(window)
    # Fetch initial book list
    books = fetch_books(state, api, window=window)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Logout":
            # Clear state on logout
            state.jwt = None
            state.user_id = None
            state.role = None
            break

        current_page = pagination_controls.handle_event(event, values)
        if current_page is not None:
            # Fetch books for the new page with current filters
            books = fetch_books(state, api, window=window, status=values["status_search"], title_filter=values["title_search"], author_id_filter=values["author_id_search"], keywords_filter=values["keywords_search"], page=current_page, page_size=PAGE_SIZE)

        if event == "Buy Books" or event == "Rent Books":
            selected = values["book_list"]
            if not selected:
                sg.popup_error("Please select a book to add to the order.")
                continue
            success = True
            for item in selected:
                # Grab book ID from selected item
                book_id = int(item.split(":")[0]) 
                if any(line["book_id"] == book_id for line in orderlines):
                    sg.popup_error("Book already in order.")
                    success = False
                    continue
                if event == "Buy Books":
                    orderlines.append({"book_id": book_id, "type": "buy"})
                else:
                    orderlines.append({"book_id": book_id, "type": "rent"})
            values["book_list"].clear()
            if success:
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
            current_page = 1
            pagination_controls.set_current_page(1)
            if values["status_search"] == "Rented":
                window["Buy Books"].update(disabled=True)
                window["Rent Books"].update(disabled=True)
            else:
                window["Buy Books"].update(disabled=False)
                window["Rent Books"].update(disabled=False)
            fetch_books(state, api, window=window, status=values["status_search"], title_filter=values["title_search"], author_id_filter=values["author_id_search"], keywords_filter=values["keywords_search"])

        if event == "View Rented Books":
            customer_rents_window(state, api)
            # Refresh the available books list after returning books
            fetch_books(state, api, window=window)

        if event == "Clear Order":
            orderlines.clear()
            sg.popup("Order cleared.")

        if event == "book_list":
            selected = values["book_list"]
            print(f"Selected books: {selected}")
            if selected:
                book_id = int(selected[0].split(":")[0])
                if book_id:
                    load_book_details(state, api, book_id, window=window)
            
    window.close()

    return 