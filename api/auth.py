# A wrapper class for current_user to manage session state
class CurrentUser:
    def __init__(self):
        self.user = None

    def set(self, user_info):
        self.user = user_info
        print("Current user set to:", self.user)

    def clear(self):
        self.user = None
        print("Current user cleared")

    def get(self):
        return self.user
    
current_user = CurrentUser()
