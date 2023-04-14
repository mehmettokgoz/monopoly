import json
import random


class Board:
    users = []
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
    lottery_amount = 0
    startup_money = 0
    curr_cell = 0
    curr_user = 0
    user_positions = {}
    user_amounts = {}
    chance_card_types = ["upgrade", "downgrade", "color_upgrade", "color_downgrade", "goto_jail", "jail_free", "teleport", "lottery", "tax"]
    curr_chance_card = None

    def __init__(self, file_path):
        self.users = []
        self.json = json.loads(open(file_path, "r").read())
        self.cells = self.json["cells"]
        for cell in self.cells:
            if cell["type"] == "property":
                cell["level"] = 1
                cell["owner"] = None
        self.chances = self.json["chances"]
        self.upgrade_cost = self.json["upgrade"]
        self.teleport_cost = self.json["teleport"]
        self.jailbail_cost = self.json["jailbail"]
        self.lottery_amount = self.json["lottery"]
        self.tax_cost = self.json["tax"]
        self.startup_money = self.json["startup"]
        self.user_positions = {}

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
            self.user_positions[user.username] = 0
            self.user_amounts[user.username] = self.startup_money

    def turn(self, user, command, *args):
        # TODO: Take necessary action here depending on the command
        cell = self.cells[self.user_positions[user.username]]
        if command == "turn-roll":
            dice_one = random.randint(1, 6)
            dice_two = random.randint(1, 6)
            self.user_positions[self.users[self.curr_user].username] = (self.user_positions[self.users[self.curr_user].username]+dice_one+dice_two) % len(self.cells)
            print(f'[{self.users[self.curr_user].username}] rolled {dice_one+dice_two} and now at position {self.user_positions[self.users[self.curr_user].username]}')
            if self.cells[self.user_positions[self.users[self.curr_user].username]]["type"] != "jail" and self.cells[self.user_positions[self.users[self.curr_user].username]]["type"] != "start":
                self.run_available(False)

        elif command == "roll":
            dice_one = random.randint(1, 6)
            dice_two = random.randint(1, 6)
            if dice_one == dice_two:
                print(f"{user.username} get out of jail.")
                self.user_positions[user.username] = (self.user_positions[user.username]+dice_one+dice_two) % len(self.cells)
                print(f"[{user.username}] rolled {dice_one+dice_two} is now on cell {self.user_positions[user.username]}")
            if self.cells[self.user_positions[self.users[self.curr_user].username]]["type"] != "jail":
                self.run_available(False)
            else:
                print(f"{user.username} still stays in jail.")

            if self.cells[self.user_positions[user.username]]["type"] == "goto_jail":
                while True:
                    self.user_positions[user.username]
                    if self.cells[self.user_positions[user.username]]["type"] == "jail":
                        break
        elif command == "buy":
            if self.user_amounts[user.username] >= cell["price"]:
                cell["owner"] = user.username
                self.user_amounts[user.username] -= cell["price"]
            else:
                print(f"{user.username} does not have required amount of money to buy.")
        elif command == "upgrade":
            if self.user_amounts[user.username] > self.upgrade_cost:
                cell["level"] += 1
                self.user_amounts[user.username] -= self.upgrade_cost
            else:
                print(f"{user.username} does not have required amount of money to upgrade.")
        elif command == "bail":
            if self.user_amounts[user.username] > self.jailbail_cost:
                self.user_amounts[user.username] -= self.jailbail_cost
                dice_one = random.randint(1, 6)
                dice_two = random.randint(1, 6)
                self.user_positions[user.username] = (self.user_positions[user.username]+dice_one + dice_two) % len(self.cells)
                print(f"[{user.username}] is now on cell {self.user_positions[user.username]}")
                self.run_available(False)
        elif command == "teleport":
            if self.user_amounts[user.username] > self.teleport_cost:
                self.user_amounts[user.username] -= self.teleport_cost
                self.user_positions[user.username] = int(args[0]) % len(self.cells)
                print(f"{user.username} is teleported to {self.user_positions[user.username]}")
                # TODO: Prevent recursive selection of teleport
                if self.cells[self.user_positions[self.users[self.curr_user].username]]["type"] != "jail":
                    self.run_available(False)
            else:
                print(f"{user.username} does not have required amount of money to teleport.")
        elif command == "pick":
            if self.curr_chance_card == "upgrade":
                if self.cells[int(args[0])]["type"] == "property":
                    if self.user_amounts[user.username] > self.upgrade_cost:
                        self.cells[int(args[0])]["level"] += 1
                        self.user_amounts[user.username] -= self.upgrade_cost
                    else:
                        print(f"{user.username} does not have required amount of money to upgrade.")
                else:
                        print(f"{user.username} did not choose a property.")
            elif self.curr_chance_card == "downgrade":
                if self.cells[int(args[0])]["type"] == "property" and self.cells[int(args[0])]["level"] > 1:
                    self.cells[int(args[0])]["level"] -= 1
                else:
                    print(f"{user.username} did not choose a property or the property is already in the lowest level.")
            elif self.curr_chance_card == "color_upgrade":
                for cell_item in self.cells:
                    if cell_item["type"] == "property" and cell_item["color"] == args[0]:
                        cell_item["level"] += 1
            elif self.curr_chance_card == "color_downgrade":
                for cell_item in self.cells:
                    if cell_item["type"] == "property" and cell_item["color"] == args[0] and cell_item["level"] > 1:
                        cell_item[int(args[0])]["level"] -= 1

    def get_user_state(self, user):
        return self.status[user.username]

    def get_board_state(self):
        pass

    def handle_chance_card(self, chance_card):
        user = self.users[self.curr_user]
        commands = []

        if chance_card == "upgrade" or chance_card == "downgrade" or chance_card == "color_upgrade" or chance_card == "color_downgrade":
            commands.append("pick")
        elif chance_card == "goto_jail":
            while True:
                self.user_positions[user.username] = (self.user_positions[user.username] + 1) % len(self.cells)
                if self.cells[self.user_positions[user.username]]["type"] == "jail":
                    print(f"{user.username} is gone to the jail.")
                    break
        elif chance_card == "jail_free":
            # TODO: handle jail free card
            pass
        elif chance_card == "teleport":
            commands.append("teleport")
        elif chance_card == "lottery":
            self.user_amounts[user.username] += self.lottery_amount
        elif chance_card == "tax":
            # TODO: tax should be calculated according to the # of properties the user have.
            if self.user_amounts[user.username] > self.tax_cost:
                self.user_amounts[user.username] -= self.tax_cost
                print(f"{user.username} paid the tax. good citizen.")
            else:
                print(f"{user.username} should be eliminated from the game. cannot pay the tax.")

        return commands

    def run_available(self, first_time):
        user = self.users[self.curr_user]
        if first_time and self.cells[self.user_positions[user.username]]["type"] != "jail":
            self.turncbs[self.users[self.curr_user].username](self, ['turn-roll'])
            return
        commands = []
        if self.cells[self.user_positions[user.username]]["type"] == "jail":
            commands.append("roll")
            commands.append("bail")
        elif self.cells[self.user_positions[user.username]]["type"] == "property":
            if self.cells[self.user_positions[user.username]]["owner"] == user.username:
                commands.append("upgrade")
            elif self.cells[self.user_positions[user.username]]["owner"] is None:
                commands.append("buy")
            else:
                cell = self.cells[self.user_positions[user.username]]
                if self.user_amounts[user.username] >= cell["rents"][cell["level"]-1]:
                    self.user_amounts[user.username] -= cell["rents"][cell["level"]-1]
                    print(f"{user.username} paid the rent ${cell['rents'][cell['level']-1]}")
                else:
                    print(f"{user.username} should be eliminated from the game. cannot pay the rent.")
                return
        elif self.cells[self.user_positions[user.username]]["type"] == "teleport":
            commands.append("teleport")
        elif self.cells[self.user_positions[user.username]]["type"] == "tax":
            if self.user_amounts[user.username] > self.tax_cost:
                self.user_amounts[user.username] -= self.tax_cost
                print(f"{user.username} paid the tax. good citizen.")
            else:
                print(f"{user.username} should be eliminated from the game. cannot pay the tax.")
            return
        elif self.cells[self.user_positions[user.username]]["type"] == "start":
            return
        elif self.cells[self.user_positions[user.username]]["type"] == "goto_jail":
            while True:
                self.user_positions[user.username] = (self.user_positions[user.username] + 1) % len(self.cells)
                if self.cells[self.user_positions[user.username]]["type"] == "jail":
                    print(f"{user.username} is gone to the jail.")
                    break
        elif self.cells[self.user_positions[user.username]]["type"] == "chance_card":
            chance_card = random.choice(self.chance_card_types)
            self.curr_chance_card = chance_card
            commands = self.handle_chance_card(chance_card)
            print(chance_card)
            if len(commands) == 0:
                return
        else:
            commands.append("turn-roll")
        self.turncbs[self.users[self.curr_user].username](self, commands)

    def start_game(self):
        for user in self.users:
            if self.status[user.username] is False:
                print("All users should marked as ready.")
                return
        while True:
            print(f"turn of {self.users[self.curr_user].username} current location: {self.cells[self.user_positions[self.users[self.curr_user].username]]}")
            # self.turncbs[self.users[self.curr_user].username](self, ["turn-roll"])
            self.run_available(True)
            self.curr_user += 1
            if self.curr_user == len(self.users):
                self.curr_user = 0

    def is_user_present(self, username):
        for user in self.users:
            if user.username == username:
                return True
        return False

    def log(self, message):
        for cb in self.callbacks:
            cb(message)
