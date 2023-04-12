import cmd

from Board import Board
from User import User


class MonopolyShell(cmd.Cmd):
    intro = 'Welcome to the Monopoly shell. Type help or ? to list commands.\n'
    prompt = 'monopoly> '

    board = None
    users = []

    def find_user_by_username(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return None

    def do_create_board(self, args):
        """Creates new board instance with given input file:  CREATE file_path"""
        args = parse(args, 1)
        if args is not None:
            self.board = Board(args[0])

    def do_create_user(self, args):
        """Creates new user and adds it to the board: CREATE_USER username email fullname password"""
        args = parse(args, 4)
        if args is not None:
            user = User(username=args[0], email=args[1], fullname=args[2], passwd=args[3])
            self.users.append(user)

    def do_attach(self, args):
        """Attaches the given user to the board: ATTACH username"""
        args = parse(args, 1)
        if args is not None:
            user = self.find_user_by_username(args[0])
            if user is not None:
                self.board.attach(user, None, None)  # TODO: Send callback functions here!
            else:
                print("Invalid username: User couldn't found.")

    def do_detach(self, args):
        """Detaches the given user to the board: ATTACH username"""
        args = parse(args, 1)
        if args is not None:
            user = self.find_user_by_username(args[0])
            self.board.detach(user)

    def do_ready(self, args):
        """Mark the given user as ready: READY username"""
        args = parse(args, 1)
        if args is not None:
            user = self.find_user_by_username(args[0])
            self.board.ready(user)  # TODO: Check if all users are ready after this operation.

    def do_get_board_users(self, args):
        """Get board users: GET_BOARD_USERS"""
        for user in self.board.users:
            print(user.username, self.board.get_user_state(user))

    def do_get_users(self, args):
        """Get users: GET_USERS"""
        for user in self.users:
            print(user.username)


def parse(args, length):
    args = tuple(map(str, args.split()))
    if len(args) != length:
        print("Wrong number of arguments. Use help <command> to see all required arguments.")
        return None
    return args


if __name__ == '__main__':
    MonopolyShell().cmdloop()
