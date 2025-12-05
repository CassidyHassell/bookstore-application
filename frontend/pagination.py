import FreeSimpleGUI as sg


class PaginationControls:
    """Pagination helper class.

    Usage:
      pc = PaginationControls(current_page=1, total_pages=50, base_key='Page')
      layout = pc.get_layout()
      window = sg.Window('...', layout)
      # in event loop:
      new_page = pc.handle_event(event, values)
      if new_page is not None:
          # load that page from API

    The class creates controls with keys prefixed by `base_key` (default 'Page').
    """

    def __init__(self, current_page, total_pages, base_key='Page'):
        self.current_page = int(max(1, current_page))
        self.total_pages = int(max(1, total_pages)) if total_pages else None
        self.base_key = base_key.rstrip("_")

        # keys used in window events/values
        p = self.base_key
        self.keys = {
            'first': f"{p}_First",
            'prev': f"{p}_Previous",
            'page': f"{p}_PageNumber",
            'next': f"{p}_Next",
            'last': f"{p}_Last",
        }

        # window reference (if attached)
        self.window = None

    def _make_page_selector(self):
        # Use Spin when pages count is reasonable; else Input with events
        if self.total_pages and self.total_pages <= 10000:
            return sg.Spin(list(range(1, self.total_pages + 1)), initial_value=self.current_page,
                           key=self.keys['page'], size=(6, 1), enable_events=True, bind_return_key=True)
        else:
            return sg.Input(default_text=str(self.current_page), key=self.keys['page'], size=(6, 1),
                            enable_events=True, tooltip="Enter page number")

    def get_layout(self):
        page_selector = self._make_page_selector()
        layout = [
            sg.Button("First", key=self.keys['first']),
            sg.Button("Previous", key=self.keys['prev']),
            sg.Text("Page"),
            page_selector,
            sg.Button("Next", key=self.keys['next']),
            sg.Button("Last", key=self.keys['last']),
        ]
        return layout

    def attach_window(self, window):
        """Attach a window to allow direct updates to controls."""
        self.window = window
        self._update_buttons()

    def _update_buttons(self):
        if not self.window:
            return
        try:
            self.window[self.keys['first']].update(disabled=(self.current_page <= 1))
            self.window[self.keys['prev']].update(disabled=(self.current_page <= 1))
            if self.total_pages:
                self.window[self.keys['next']].update(disabled=(self.current_page >= self.total_pages))
                self.window[self.keys['last']].update(disabled=(self.current_page >= self.total_pages))
        except Exception:
            pass

    def _update_page_selector(self):
        if not self.window:
            return
        try:
            if self.total_pages and self.total_pages <= 10000:
                self.window[self.keys['page']].update(values=list(range(1, self.total_pages + 1)), value=self.current_page)
            else:
                self.window[self.keys['page']].update(value=str(self.current_page))
        except Exception:
            pass

    def set_total_pages(self, total_pages):
        self.total_pages = int(total_pages)
        # If window attached, recreate/replace page selector isn't simple; caller can recreate layout

    def set_current_page(self, page):
        page = int(page)
        if page < 1:
            page = 1
        if self.total_pages:
            page = min(page, self.total_pages)
        self.current_page = page
        # update control value if attached
        if self.window:
            try:
                self.window[self.keys['page']].update(str(self.current_page))
            except Exception:
                pass
            self._update_buttons()

    def handle_event(self, event, values):
        """Process an event and return the new current page (int) when changed, else None.

        `event` is the key string, `values` is the event-values dict from the window.read loop.
        """
        # Map events
        if event == self.keys['first']:
            if self.current_page != 1:
                self.set_current_page(1)
                return self.current_page
            return None

        if event == self.keys['prev']:
            if self.current_page > 1:
                self.set_current_page(self.current_page - 1)
                return self.current_page
            return None

        if event == self.keys['next']:
            if self.total_pages is None or self.current_page < self.total_pages:
                self.set_current_page(self.current_page + 1)
                return self.current_page
            return None

        if event == self.keys['last']:
            if self.total_pages and self.current_page != self.total_pages:
                self.set_current_page(self.total_pages)
                return self.current_page
            return None

        # Page number typed/changed
        if event == self.keys['page']:
            raw = values.get(self.keys['page'])
            print(f"Raw page input: {raw}")
            if raw is None:
                return None
            try:
                new_page = int(str(raw).strip())
            except Exception:
                # Reset displayed value to current_page
                if self.window:
                    try:
                        self.window[self.keys['page']].update(str(self.current_page))
                    except Exception:
                        pass
                return None

            # clamp
            if new_page < 1:
                new_page = 1
            if self.total_pages:
                new_page = min(new_page, self.total_pages)

            if new_page != self.current_page:
                self.set_current_page(new_page)
                return self.current_page
            return None

        return None
    
    def update_total_pages(self, total_pages):
        self.total_pages = int(total_pages)
        self._update_buttons()
        self._update_page_selector()