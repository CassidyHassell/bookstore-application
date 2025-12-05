import FreeSimpleGUI as sg

from frontend.pagination import PaginationControls
from frontend.screens.new_book import new_book_window

current_page = 1
PAGE_SIZE = 100

def manager_orders_window(state, api):

    pagination_controls = PaginationControls(current_page=1, total_pages=1, base_key='Page')

    def fetch_orders(state, api, window=None, status_filter="All", page=1, page_size=PAGE_SIZE):
        try:
            status = status_filter if status_filter in ["All", "Pending", "Completed", "Cancelled"] else "All"
            status = status.lower()
            if status == "all":
                status = None
            
            resp = api.get_orders(state.jwt, status=status, page_number=page, page_size=page_size)
            orders = resp.get("orders", [])
            total_pages = resp.get("page", None).get("total_pages", 1)
            pagination_controls.update_total_pages(total_pages)

        except Exception as e:
            print(f"Error fetching orders: {e}")
            orders = []
        if window:
            # Update the orders list in the window
            window["orders_list"].update(values=[f"Order ID: {o['id']} | Date: {o['order_date']} | Status: {o['payment_status']}" for o in orders])
    
    def fetch_order_details(state, api, order_id, window=None):
        try:
            resp = api.get_order_details(state.jwt, order_id)
        except Exception as e:
            print(f"Error fetching order details: {e}")
            resp = {}
        if window:
            window["order_id"].update(resp.get("id", ""))
            window["order_user_id"].update(resp.get("user_id", ""))
            window["order_date"].update(resp.get("order_date", ""))
            window["payment_status"].update(resp.get("payment_status", ""))
            window["total_price"].update(resp.get("total_price", ""))
            window["email_sent"].update(str(resp.get("email_sent", "")))
            order_lines = resp.get("order_lines", [])
            window["order_lines_list"].update(values=[f"Book ID: {line['book_id']} | Type: {line['type']} | Price: {line['price']}" for line in order_lines])

    options = [sg.DropDown(values=["All", "Pending", "Completed", "Cancelled"], default_value="All", key="order_status_filter"), sg.Button("Filter")]
    order_details = sg.Frame("Order Details", [
        [sg.Text("Order ID:"), sg.Text("", key="order_id")],
        [sg.Text("User ID:"), sg.Text("", key="order_user_id")],
        [sg.Text("Order Date:"), sg.Text("", key="order_date")],
        [sg.Text("Payment Status:"), sg.Text("", key="payment_status"), sg.Button("Mark Paid")],
        [sg.Text("Total Price:"), sg.Text("", key="total_price")],
        [sg.Text("Email Sent:"), sg.Text("", key="email_sent")],
        [sg.Text("Order Lines:")],
        [sg.Listbox(values=[], size=(40, 10), key="order_lines_list")],
    ])
    orders_layout = sg.Frame("Orders", [
        [sg.Listbox(values=[], size=(50, 15), key="orders_list", select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, enable_events=True)],
        pagination_controls.get_layout()
    ])
    layout = [
        [options],
        [orders_layout, order_details],
        [sg.Button("Back")]
    ]

    window = sg.Window("Manager Orders Dashboard", layout, finalize=True)
    pagination_controls.attach_window(window)

    fetch_orders(state, api, window=window)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Back":
            break

        current_page = pagination_controls.handle_event(event, values)
        if current_page is not None:
            fetch_orders(state, api, window=window, status_filter=values["order_status_filter"], page=current_page, page_size=PAGE_SIZE)

        elif event == "orders_list":
            fetch_order_details(state, api, int(values["orders_list"][0].split("|")[0].split(":")[1].strip()), window=window)
        
        elif event == "Filter":
            current_page = 1
            pagination_controls.set_current_page(1)
            fetch_orders(state, api, window=window, status_filter=values["order_status_filter"], page=current_page, page_size=PAGE_SIZE)
            
        elif event == "Mark Paid":
            if not window["order_id"].get():
                sg.popup_error("Please select an order to mark as paid.")
                continue
            order_id = int(window["order_id"].get())
            if window["payment_status"].get().lower() != "pending":
                sg.popup_error("Order must be pending to mark as paid.")
                continue
            resp_json = api.update_order_status(state.jwt, order_id, "completed")
            if resp_json.get("error"):
                sg.popup_error(f"Error updating order status: {resp_json.get('error')}")
            else:
                sg.popup("Order marked as paid successfully.")
                fetch_orders(state, api, window=window, status_filter=values["order_status_filter"])
                fetch_order_details(state, api, order_id, window=window)

    window.close()