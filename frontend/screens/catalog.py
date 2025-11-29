import FreeSimpleGUI as sg

orderlines = []

def catalog_window(state, api):
    try:
        resp = api.get_available_books(state.jwt)
        books = resp.get("books", [])
    except Exception as e:
        sg.popup_error(f"Error fetching books: {e}")
        books = []
    layout = [
        [sg.Text("Title"), sg.Input(key="search", enable_events=True, size=(30,1)), sg.Button("Search"), sg.DropDown(values=["Available", "New", "Used", "Rented Out", "All"], default_value="Available", key="status_filter"), sg.Button("Filter by Status")],
        [sg.Text("Catalog")],
        [sg.Listbox(values=[f"{b['id']}: {b['title']}" for b in books], size=(40, 10), key="book_list", select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],
        [sg.Button("Buy Books"), sg.Button("Rent Books"), sg.Button("View Order"), sg.Button("Checkout"), sg.Button("Logout")]
    ]

    window = sg.Window("Catalog", layout)

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
                resp = api.create_order(state.jwt, {"order_lines": orderlines})
                sg.popup("Order Successful", f"Order ID: {resp.get('order_id')}\nBill:\n{resp.get('bill')}")
                orderlines.clear()
                sg.popup(resp.get('bill'))
            except Exception as e:
                sg.popup_error(f"Error during checkout: {e}")

        if event == "Filter by Status":
            status = values["status_filter"]
            try:
                if status == "Available":
                    resp = api.get_available_books(state.jwt)
                elif status == "All":
                    resp = api.get_all_books(state.jwt)
                elif status == "New":
                    resp = api.get_books_by_status(state.jwt, "new")
                elif status == "Used":
                    resp = api.get_books_by_status(state.jwt, "returned")
                elif status == "Rented Out":
                    resp = api.get_books_by_status(state.jwt, "rented")
                books = resp.get("books", [])
                window["book_list"].update(values=[f"{b['id']}: {b['title']}" for b in books])
            except Exception as e:
                sg.popup_error(f"Error filtering books: {e}")

        if event == "Search":
            title = values["search"].lower()
            filtered_books = [b for b in books if title in b['title'].lower()]
            window["book_list"].update(values=[f"{b['id']}: {b['title']}" for b in filtered_books])
            
    window.close()

    return 