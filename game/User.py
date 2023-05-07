from game.Board import Board


class User:
    username: str
    email: str
    fullname: str
    passwd: str

    def __init__(self, username, email, fullname, passwd):
        self.username = username
        self.email = email
        self.fullname = fullname
        self.passwd = passwd  # TODO: Convert this string password to hashed version.

    def get(self):
        pass

    def update(self):
        pass

    def delete(self):
        """Not implemented for Phase 1"""
        pass

    def auth(self):
        """Not implemented for Phase 1"""
        pass

    def login(self):
        """Not implemented for Phase 1"""
        pass

    def check_session(self, token):
        """Not implemented for Phase 1"""
        pass

    def logout(self):
        """Not implemented for Phase 1"""
        pass

    def log(self, message):
        print(f"{[self.username]}: ", message)

    def turncb(self, board: Board, options):
        for option in options:
            if option == "teleport" or option == "pick":
                print(f"monopoly> [{self.username}] {option} [y INDEX/n]")
                c = input(f"monopoly> [{self.username}] {option} [y INDEX/n]")
            else:
                c = input(f"monopoly> [{self.username}] {option} [y/n]")
            c = c.split(" ")
            if c[0] == "y":
                if option == "teleport" or option == "pick":
                    board.turn(self, option, c[1])
                elif option == "jail-free":
                    board.turn(self, option, c[0])
                else:
                    board.turn(self, option)
                return
 