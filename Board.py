class Board:
    file_path: str
    users: []
    status = {}
    callbacks = []

    def __init__(self, file_path):
        self.users = []
        self.file_path = file_path  # TODO: Load the JSON file using the given path and create cells

    def attach(self, user, callback, turncb):
        self.users.append(user)
        self.callbacks.append(callback)
        self.status[user.username] = False

    def detach(self, user):
        if self.is_user_present(user.username):
            self.users.remove(user)
            self.status.pop(user.username)

    def ready(self, user):
        if self.is_user_present(user.username):
            self.status[user.username] = True

    def turn(self, user, command):
        pass

    def get_user_state(self, user):
        return self.status[user.username]

    def get_board_state(self):
        pass

    def is_user_present(self, username):
        for user in self.users:
            if user.username == username:
                return True
        return False

    def log(self, message):
        for cb in self.callbacks:
            cb(message)
