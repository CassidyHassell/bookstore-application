class AppState:
    def __init__(self):
        self.jwt: str | None = None
        self.user_id: str | None = None
        self.role: str | None = None
