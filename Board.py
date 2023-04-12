import json


class Board:
    users: []
    json = None
    status = {}
    callbacks = []
    turncbs = {}
    cells = None
    chances = None
    upgrade_cost = 0
    teleport_cost = 0
    jailbail_cost = 0
    tax_cost = 0
    startup_money = 0
    curr_cell = 0
    curr_user = 0

    def __init__(self, file_path):
        self.users = []
        self.json = json.loads(open(file_path, "r").read())
        self.cells = self.json["cells"]
        for cell in self.cells:
            if cell["type"] == "property":
                cell["level"] = 1
        self.chances = self.json["chances"]
        self.upgrade_cost = self.json["upgrade"]
        self.teleport_cost = self.json["teleport"]
        self.jailbail_cost = self.json["jailbail"]
        self.tax_cost = self.json["tax"]
        self.startup_money = self.json["startup"]

    def attach(self, user, callback, turncb):
        self.users.append(user)
        self.callbacks.append(callback)
        self.turncbs[user.username] = turncb
        self.status[user.username] = False

    def detach(self, user):
        if self.is_user_present(user.username):
            self.users.remove(user)
            self.status.pop(user.username)

    def ready(self, user):
        if self.is_user_present(user.username):
            self.status[user.username] = True

    def turn(self, user, command):
        # TODO: Take necessary action here depending on the command
        """
        self.curr_cell += 1
        if self.curr_cell == len(self.cells):
            self.curr_cell = 0
        """
        print(f"[{user.username}]: {command}")

    def get_user_state(self, user):
        return self.status[user.username]

    def get_board_state(self):
        pass

    def start_game(self):
        while True:
            self.turncbs[self.users[self.curr_user].username](self)
            self.curr_user += 1
            if self.curr_user == len(self.users):
                self.curr_user = 0

    def is_user_present(self, username):
        for user in self.users:
            if user.username == username:
                return True
        return False

    def log(self, message):
        print(self.cells)
        for cb in self.callbacks:
            cb(message)
