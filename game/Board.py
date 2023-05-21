import json
import random
import threading
from threading import Thread, Lock, Condition


class Board:
    users = []
    json = None
    status = {}
    callbacks = {}
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
    chance_card_types = []
    jail_free_cards = {}
    curr_chance_card = None
    is_started = False

    def __init__(self, file_path):
        self.is_started = False
        self.users = []
        self.callbacks = {}
        self.json = json.loads(open(file_path, "r").read())
        self.cells = self.json["cells"]
        for cell in self.cells:
            if cell["type"] == "property":
                cell["level"] = 1
                cell["owner"] = None
        self.chances = self.json["chances"]
        for chance_card in self.json["chances"]:
            self.chance_card_types.append(chance_card["type"])
        self.upgrade_cost = self.json["upgrade"]
        self.teleport_cost = self.json["teleport"]
        self.jailbail_cost = self.json["jailbail"]
        self.lottery_amount = self.json["lottery"]
        self.tax_cost = self.json["tax"]
        self.startup_money = self.json["startup"]
        self.user_positions = {}

    def attach(self, user, callback, turncb):
        if not self.is_started:
            print(self.users)
            for a in self.users:
                print(a.username)
            self.users.append(user)
            self.callbacks[user.username] = callback
            self.turncbs[user.username] = turncb
            self.status[user.username] = False
            print("Now attaching: ",threading.current_thread().ident)
            self.log(user.username + " is attached to the board.")
            print(self.users)
            for a in self.users:
                print(a.username)
        else:
            callback("The game is started, you can not join as player.")

    def watch(self, user, callback):
        self.callbacks[user.username] = callback

    def unwatch(self, user):
        self.callbacks.pop(user.username)

    def detach(self, user):
        if self.is_user_present(user.username):
            self.users.remove(user)
            self.status.pop(user.username)
            self.turncbs.pop(user.username)
            self.callbacks.pop(user.username)
            self.log(user.username + " is detached from the board.")

    def ready(self, user):
        if self.is_user_present(user.username):
            self.status[user.username] = True
            self.user_positions[user.username] = 0
            self.user_amounts[user.username] = self.startup_money
            self.jail_free_cards[user.username] = 0
            self.log(user.username + " is ready.")

    def turn(self, user, command, *args):
        cell = self.cells[self.user_positions[user.username]]
        if command == "dice":
            self.dice(user)
        elif command == "roll":
            self.jail_roll(user)
        elif command == "jail-free":
            self.jail_free(user, args[0])
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
        # TODO: Generate a report for each user, money and properties with their levels
        return self.status[user.username]

    def get_board_state(self):
        # TODO: Generates a report for the board, properties, their level and owner
        return json.dumps([self.users, self.user_positions, self.user_amounts, self.cells])

    def dice(self, user):
        # implements rolling two dice and sends user to the corresponding cell.
        # if cell type is not jail or start, then to have the same user continue the function calls run_available(False) is called
        dice_one = random.randint(1, 6)
        dice_two = random.randint(1, 6)
        self.user_positions[user.username] = (self.user_positions[user.username] + dice_one + dice_two) % len(
            self.cells)
        self.print_dice(user, dice_one + dice_two)
        cell = self.cells[self.user_positions[user.username]]
        if cell["type"] == "jail" and self.jail_free_cards[user.username] != 0:
            self.run_available(False)
            return
        if cell["type"] != "jail" and cell["type"] != "start":
            self.run_available(False)

    def teleport(self, user, arg):
        # implements teleporting the user to the position he/she wants. Uses arg parameter as position index.
        # if cell type is not jail, then to have the same user continue the function calls run_available(False)
        if self.user_amounts[user.username] > self.teleport_cost:
            self.user_amounts[user.username] -= self.teleport_cost
            self.user_positions[user.username] = int(arg) % len(self.cells)

            self.log(f"{user.username} is teleported to {self.user_positions[user.username]}\n")
            
            log_string = f"[{user.username}] [cell: {self.cells[self.user_positions[user.username]]['type']}"
            if self.cells[self.user_positions[user.username]]['type'] == "property":
                log_string += f", name={self.cells[self.user_positions[user.username]]['name']}, owner={self.cells[self.user_positions[user.username]]['owner']}]\n"
            else:
                log_string += "]\n"
            self.log(log_string)

            cell = self.cells[self.user_positions[self.users[self.curr_user].username]]
            if cell["type"] != "jail":
                self.run_available(False)
        else:
            self.log(f"{user.username} does not have required amount of money to teleport.\n")

    def bail(self, user):
        # implements bailing user out of jail if s/he has enough money.
        if self.user_amounts[user.username] > self.jailbail_cost:
            self.user_amounts[user.username] -= self.jailbail_cost
            self.jail_free(user, "y")
        else:
            self.log(f"{user.username} does not have required money to bail jail.\n")

    def jail_roll(self, user):
        # implements rolling dices for the user to come out of jail.
        # if two dices' values are the same user gots out of jail, otherwise does not.
        # if cell type is not jail, then to have the same user continue the function calls run_available(False)
        dice_one = random.randint(1, 6)
        dice_two = random.randint(1, 6)
        if dice_one == dice_two:
            self.log(f"{user.username} get out of jail.\n")
            self.user_positions[user.username] = (self.user_positions[user.username] + dice_one + dice_two) % len(
                self.cells)
            self.print_dice(user, dice_one + dice_two)
        if self.cells[self.user_positions[self.users[self.curr_user].username]]["type"] != "jail":
            self.run_available(False)
        else:
            self.log(f"{user.username} still stays in jail.\n")
        if self.cells[self.user_positions[user.username]]["type"] == "goto_jail":
            self.go_to_jail(user)

    def buy_property(self, user, cell):
        # implements buying a property. 
        # if the user has enough money, s/he gets the property.
        if self.user_amounts[user.username] >= cell["price"]:
            cell["owner"] = user.username
            self.user_amounts[user.username] -= cell["price"]
            self.log(f"{user.username} bought the property.\n")
        else:
            self.log(f"{user.username} does not have required amount of money to buy.\n")

    def upgrade_property(self, user, cell):
        # implements upgrading a property. 
        # if the user has enough money and the property is upgradable, s/he upgrades the property. 
        if self.user_amounts[user.username] > self.upgrade_cost:
            if len(cell["rents"]) - 1 == cell["level"]:
                self.log(f"The property is already upgraded to the highest level.\n")
                return
            cell["level"] += 1
            self.user_amounts[user.username] -= self.upgrade_cost
            self.log(f"{user.username} upgraded the property.\n")
        else:
            self.log(f"{user.username} does not have required amount of money to upgrade.\n")

    def go_to_jail(self, user):
        # implements sending user to the closest jail cell.
        while True:
            self.user_positions[user.username] = (self.user_positions[user.username] + 1) % len(self.cells)
            if self.cells[self.user_positions[user.username]]["type"] == "jail":
                self.log(f"{user.username} is gone to the jail.\n")
                break

    def jail_free(self, user, answer):
        # implements the actions after the user uses the jail_free card
        if answer == "n":
            return
        if self.jail_free_cards[user.username] > 0:
            self.jail_free_cards[user.username] -= 1

        dice_one = random.randint(1, 6)
        dice_two = random.randint(1, 6)
        self.user_positions[user.username] = (self.user_positions[user.username] + dice_one + dice_two) % len(
            self.cells)
        self.print_dice(user, dice_one + dice_two)
        if self.cells[self.user_positions[self.users[self.curr_user].username]]["type"] != "jail":
            self.run_available(False)

    def pay_tax(self, user):
        # calculates the tax amount and makes user pay it if they have any money.
        # TODO: Should 0 property equals to 0 tax?
        dynamic_tax_cost = self.tax_cost
        for cell in self.cells:
            if cell["type"] == "property" and cell["owner"] == user.username:
                dynamic_tax_cost += self.tax_cost
        if self.user_amounts[user.username] > dynamic_tax_cost:
            prev_amount = self.user_amounts[user.username]
            self.user_amounts[user.username] -= dynamic_tax_cost
            self.log(
                f"{user.username} paid ${dynamic_tax_cost} the tax. good citizen. [prev: {prev_amount}, curr: {self.user_amounts[user.username]}]\n")
        else:
            self.log(f"{user.username} is eliminated from the game. cannot pay the tax.\n")
            self.users.remove(user)

    def pay_rent(self, user):
        # implements the pay rent actions.
        # prints out the before and after balances of the owner and the tenant
        cell = self.cells[self.user_positions[user.username]]
        if self.user_amounts[user.username] >= cell["rents"][cell["level"] - 1]:
            prev_amount = self.user_amounts[user.username]
            prev_owner = self.user_amounts[cell["owner"]]
            self.user_amounts[user.username] -= cell["rents"][cell["level"] - 1]
            self.user_amounts[cell["owner"]] += cell["rents"][cell["level"] - 1]
            self.log(
                f"{user.username} paid the rent ${cell['rents'][cell['level'] - 1]} tenant=[prev: {prev_amount}, curr: {self.user_amounts[user.username]}] owner=[prev: {prev_owner}, curr: {self.user_amounts[cell['owner']]}]\n")
        else:
            self.users.remove(user)
            self.log(f"{user.username} is eliminated from the game. cannot pay the rent.\n")

    def won_lottery(self, user):
        prev_amount = self.user_amounts[user.username]
        self.user_amounts[user.username] += self.lottery_amount
        self.log(f"{user.username} won the lottery! [prev: {prev_amount}, curr: {self.user_amounts[user.username]}]\n")

    def pick_chance_card(self, user, arg):
        # implements actions for "pick" command for different chance cards.
        if self.curr_chance_card == "upgrade":
            if self.cells[int(arg)]["type"] == "property":
                if self.user_amounts[user.username] > self.upgrade_cost:
                    self.cells[int(arg)]["level"] += 1
                    self.user_amounts[user.username] -= self.upgrade_cost
                else:
                    self.log(f"{user.username} does not have required amount of money to upgrade.\n")
            else:
                self.log(f"{user.username} did not choose a property.\n")
        elif self.curr_chance_card == "downgrade":
            if self.cells[int(arg)]["type"] == "property" and self.cells[int(arg)]["level"] > 1:
                self.cells[int(arg)]["level"] -= 1
            else:
                self.log(f"{user.username} did not choose a property or the property is already in the lowest level.\n")
        elif self.curr_chance_card == "color_upgrade":
            for cell_item in self.cells:
                if cell_item["type"] == "property" and cell_item["color"] == arg:
                    cell_item["level"] += 1
        elif self.curr_chance_card == "color_downgrade":
            for cell_item in self.cells:
                if cell_item["type"] == "property" and cell_item["color"] == arg and cell_item["level"] > 1:
                    cell_item[int(arg)]["level"] -= 1

    def handle_chance_card(self, chance_card):
        # calls related methods according to the given chance_card parameter.
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
            self.won_lottery(user)
        elif chance_card == "tax":
            self.pay_tax(user)
        return commands

    def run_available(self, first_time):
        # fills the commands array that is sent to the turncb function.
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
            self.log(f"[chance card: {chance_card}]\n")
            commands = self.handle_chance_card(chance_card)
            if len(commands) == 0:
                return
        else:
            commands.append("dice")
        # self.log(str(commands))
        self.turncbs[self.users[self.curr_user].username](self, commands)

    def game_loop(self):
        while True:
            user = self.users[self.curr_user]
            log_string = f"[{user.username}] [cell: {self.cells[self.user_positions[user.username]]['type']}"
            if self.cells[self.user_positions[user.username]]['type'] == "property":
                log_string += f", [name={self.cells[self.user_positions[user.username]]['name']}]\n"
            else:
                log_string += "]\n"
            self.log(log_string)
            self.run_available(True)
            self.curr_user += 1
            if len(self.users) == 1:
                self.log("GAME OVER! \n")
                self.log(f"{self.users[0].username} WON THE GAME\n")
                break
            elif self.curr_user == len(self.users):
                self.curr_user = 0

    def start_game(self):
        # check if every user ready.

        for user in self.users:
            if self.status[user.username] is False:
                self.log("All users should marked as ready.")
                return
        self.log("Game is started!")
        self.is_started = True
        # main game loop
        # Make this thread
        t = Thread(target=self.game_loop)
        t.start()

    def is_user_present(self, username):
        # checks if the given user whose username is given from the command line is present.
        for user in self.users:
            if user.username == username:
                return True
        return False

    def print_dice(self, user, dice):
        log_string = f"[{user.username}] [dice: {dice}] [cell: {self.cells[self.user_positions[user.username]]['type']}"
        if self.cells[self.user_positions[user.username]]['type'] == "property":
            log_string += f", name={self.cells[self.user_positions[user.username]]['name']}, owner={self.cells[self.user_positions[user.username]]['owner']}]\n"
        else:
            log_string += "]\n"
        self.log(log_string)

    def find_users_on_cell(self, index):
        users = []
        for user in self.users:
            if self.user_positions[user.username] == index:
                users.append(user.username[0])
        return users

    def log(self, message):
        for un in self.callbacks:
            self.callbacks[un](message)
