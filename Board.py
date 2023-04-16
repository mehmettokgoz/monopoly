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
    jail_free_cards = {}
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
            self.turncbs.pop(user.username)
            # TODO: Remove callback too

    def ready(self, user):
        if self.is_user_present(user.username):
            self.status[user.username] = True
            self.user_positions[user.username] = 0
            self.user_amounts[user.username] = self.startup_money
            self.jail_free_cards[user.username] = 0

    def turn(self, user, command, *args):
        cell = self.cells[self.user_positions[user.username]]
        if command == "dice":
            self.dice(user)
        elif command == "roll":
            self.jail_roll(user)
        elif command == "jail-free":
            self.jail_free(user)
        elif command == "buy":
            self.buy_property(user, cell)
        elif command == "upgrade":
            self.upgrade_property(user, cell)
        elif command == "bail":
            self.bail(user)
        elif command == "teleport":
            self.teleport(user, args[0])
        elif command == "pick":
            self.pick_chance_card(user, args[0])

    def get_user_state(self, user):
        return self.status[user.username]

    def get_board_state(self):
        return self.users, self.user_positions, self.user_amounts, self.cells

    def dice(self, user):
        dice_one = random.randint(1, 6)
        dice_two = random.randint(1, 6)
        self.user_positions[user.username] = (self.user_positions[user.username] + dice_one + dice_two) % len(self.cells)
        self.print_dice(user, dice_one + dice_two)
        cell = self.cells[self.user_positions[user.username]]
        if cell["type"] != "jail" and cell["type"] != "start":
            self.run_available(False)

    def teleport(self, user, arg):
        if self.user_amounts[user.username] > self.teleport_cost:
            self.user_amounts[user.username] -= self.teleport_cost
            self.user_positions[user.username] = int(arg) % len(self.cells)
            print(f"{user.username} is teleported to {self.user_positions[user.username]}")
            # TODO: Prevent recursive selection of teleport
            cell = self.cells[self.user_positions[self.users[self.curr_user].username]]
            if cell["type"] != "jail":
                self.run_available(False)
        else:
            print(f"{user.username} does not have required amount of money to teleport.")

    def bail(self, user):
        if self.user_amounts[user.username] > self.jailbail_cost:
            self.user_amounts[user.username] -= self.jailbail_cost
            self.jail_free(user)
        else:
            print(f"{user.username} does not have required money to bail jail.")

    def jail_roll(self, user):
        dice_one = random.randint(1, 6)
        dice_two = random.randint(1, 6)
        if dice_one == dice_two:
            print(f"{user.username} get out of jail.")
            self.user_positions[user.username] = (self.user_positions[user.username] + dice_one + dice_two) % len(
                self.cells)
            self.print_dice(user, dice_one+dice_two)
        if self.cells[self.user_positions[self.users[self.curr_user].username]]["type"] != "jail":
            self.run_available(False)
        else:
            print(f"{user.username} still stays in jail.")
        if self.cells[self.user_positions[user.username]]["type"] == "goto_jail":
            self.go_to_jail(user)

    def pay_tax(self, user):
        # TODO: Should 0 property equals to 0 tax?
        dynamic_tax_cost = self.tax_cost
        for cell in self.cells:
            if cell["type"] == "property" and cell["owner"] == user.username:
                dynamic_tax_cost += self.tax_cost
        if self.user_amounts[user.username] > dynamic_tax_cost:
            self.user_amounts[user.username] -= dynamic_tax_cost
            print(f"{user.username} paid ${dynamic_tax_cost} the tax. good citizen.")
        else:
            print(f"{user.username} is eliminated from the game. cannot pay the tax.")
            self.users.remove(user)

    def buy_property(self, user, cell):
        if self.user_amounts[user.username] >= cell["price"]:
            cell["owner"] = user.username
            self.user_amounts[user.username] -= cell["price"]
        else:
            print(f"{user.username} does not have required amount of money to buy.")

    def upgrade_property(self, user, cell):
        if self.user_amounts[user.username] > self.upgrade_cost:
            cell["level"] += 1
            self.user_amounts[user.username] -= self.upgrade_cost
            print(f"{user.username} upgraded the property.")
        else:
            print(f"{user.username} does not have required amount of money to upgrade.")

    def go_to_jail(self, user):
        while True:
            self.user_positions[user.username] = (self.user_positions[user.username] + 1) % len(self.cells)
            if self.cells[self.user_positions[user.username]]["type"] == "jail":
                print(f"{user.username} is gone to the jail.")
                break

    def jail_free(self, user):
        dice_one = random.randint(1, 6)
        dice_two = random.randint(1, 6)
        self.user_positions[user.username] = (self.user_positions[user.username] + dice_one + dice_two) % len(
            self.cells)
        self.print_dice(user, dice_one+dice_two)
        if self.cells[self.user_positions[self.users[self.curr_user].username]]["type"] != "jail":
            self.run_available(False)

    def pay_rent(self, user):
        cell = self.cells[self.user_positions[user.username]]
        if self.user_amounts[user.username] >= cell["rents"][cell["level"] - 1]:
            self.user_amounts[user.username] -= cell["rents"][cell["level"] - 1]
            self.user_amounts[cell["owner"]] += cell["rents"][cell["level"] - 1]
            print(f"{user.username} paid the rent ${cell['rents'][cell['level'] - 1]}")
        else:
            self.users.remove(user)
            print(f"{user.username} is eliminated from the game. cannot pay the rent.")

    def pick_chance_card(self, user, arg):
        if self.curr_chance_card == "upgrade":
            if self.cells[int(arg)]["type"] == "property":
                if self.user_amounts[user.username] > self.upgrade_cost:
                    self.cells[int(arg)]["level"] += 1
                    self.user_amounts[user.username] -= self.upgrade_cost
                else:
                    print(f"{user.username} does not have required amount of money to upgrade.")
            else:
                print(f"{user.username} did not choose a property.")
        elif self.curr_chance_card == "downgrade":
            if self.cells[int(arg)]["type"] == "property" and self.cells[int(arg)]["level"] > 1:
                self.cells[int(arg)]["level"] -= 1
            else:
                print(f"{user.username} did not choose a property or the property is already in the lowest level.")
        elif self.curr_chance_card == "color_upgrade":
            for cell_item in self.cells:
                if cell_item["type"] == "property" and cell_item["color"] == arg:
                    cell_item["level"] += 1
        elif self.curr_chance_card == "color_downgrade":
            for cell_item in self.cells:
                if cell_item["type"] == "property" and cell_item["color"] == arg and cell_item["level"] > 1:
                    cell_item[int(arg)]["level"] -= 1

    def handle_chance_card(self, chance_card):
        user = self.users[self.curr_user]
        commands = []
        if chance_card == "upgrade" or chance_card == "downgrade" or chance_card == "color_upgrade" or chance_card == "color_downgrade":
            commands.append("pick")
        elif chance_card == "goto_jail":
            self.go_to_jail(user)
        elif chance_card == "jail_free":
            self.jail_free_cards[user.username] += 1
        elif chance_card == "teleport":
            commands.append("teleport")
        elif chance_card == "lottery":
            self.user_amounts[user.username] += self.lottery_amount
            print(f"{user.username} won the lottery!")
        elif chance_card == "tax":
            self.pay_tax(user)
        return commands

    def run_available(self, first_time):
        user = self.users[self.curr_user]
        # If the turn is on the user and s/he is not at the jail, offer the dice
        if first_time and self.cells[self.user_positions[user.username]]["type"] != "jail":
            self.turncbs[self.users[self.curr_user].username](self, ['dice'])
            return
        commands = []
        if self.cells[self.user_positions[user.username]]["type"] == "jail":
            # Offer to user jail-free card if user has one
            if self.jail_free_cards[user.username] != 0:
                commands.append("jail-free")
            # Try to dice double
            commands.append("roll")
            # Offer pay the penalty and get out of jail
            commands.append("bail")
        elif self.cells[self.user_positions[user.username]]["type"] == "property":
            # If owner is the current user, offer to upgrade
            if self.cells[self.user_positions[user.username]]["owner"] == user.username:
                commands.append("upgrade")
            # If the owner is None, offer to buy
            elif self.cells[self.user_positions[user.username]]["owner"] is None:
                commands.append("buy")
            # If already has an owner, pay the rent
            else:
                self.pay_rent(user)
                return
        elif self.cells[self.user_positions[user.username]]["type"] == "teleport":
            commands.append("teleport")
        elif self.cells[self.user_positions[user.username]]["type"] == "tax":
            self.pay_tax(user)
            return
        elif self.cells[self.user_positions[user.username]]["type"] == "start":
            return
        elif self.cells[self.user_positions[user.username]]["type"] == "goto_jail":
            self.go_to_jail(user)
            return
        elif self.cells[self.user_positions[user.username]]["type"] == "chance_card":
            chance_card = random.choice(self.chance_card_types)
            self.curr_chance_card = chance_card
            print(f"[chance card: {chance_card}]")
            commands = self.handle_chance_card(chance_card)
            if len(commands) == 0:
                return
        else:
            commands.append("dice")
        self.turncbs[self.users[self.curr_user].username](self, commands)

    def start_game(self):
        for user in self.users:
            if self.status[user.username] is False:
                print("All users should marked as ready.")
                return
        while True:
            user = self.users[self.curr_user]
            print(f"[{user.username}] [cell: {self.cells[self.user_positions[user.username]]['type']}]", end="")
            if self.cells[self.user_positions[user.username]]['type']=="property":
                print(f", name={self.cells[self.user_positions[user.username]]['name']}]")
            else:
                print("]")
            self.run_available(True)
            self.curr_user += 1
            if len(self.users) == 1:
                print("GAME OVER! ")
                print(f"{self.users[0].username} WON THE GAME")
                break
            elif self.curr_user == len(self.users):
                self.curr_user = 0

    def is_user_present(self, username):
        for user in self.users:
            if user.username == username:
                return True
        return False

    def print_dice(self, user, dice):
        print(f"[{user.username}] [dice: {dice}] [cell: {self.cells[self.user_positions[user.username]]['type']}", end="")
        if self.cells[self.user_positions[user.username]]['type'] == "property":
            print(f", name={self.cells[self.user_positions[user.username]]['name']}, owner={self.cells[self.user_positions[user.username]]['owner']}]")
        else:
            print("]")

    def print_board(self):
        print("---" * 55)
        for i in range(len(self.cells)):
            users = self.find_users_on_cell(i)
            if self.cells[i]['type'] == "property":
                print(f"{self.cells[i]['name']}", end="")
                if self.cells[i]["owner"] is not None:
                    print(f" [O:{self.cells[i]['owner'][0]}]", end="")
            else:
                print(f"{self.cells[i]['type']}", end="")
            if len(users) != 0:
                print(": ", end="")
                for user in users:
                    print(user, end=" ")
            print(" | ", end="\t")
        print("")
        print("---" * 55)

    def find_users_on_cell(self, index):
        users = []
        for user in self.users:
            if self.user_positions[user.username] == index:
                users.append(user.username[0])
        return users

    def log(self, message):
        for cb in self.callbacks:
            cb(message)
