import threading

def run_in_background(window, event_key, func, *args, **kwargs):
    def worker():
        try:
            result = func(*args, **kwargs)
            payload = {"ok": True, "result": result}
        except Exception as e:
            payload = {"ok": False, "error": e}
        if window:
            window.write_event_value(event_key, payload)
    threading.Thread(target=worker, daemon=True).start()
