import sys
from sdk.monopoly_client import MonopolyClient
import cmd
from sdk.protocol.client_message import Command


class MonopolyTcpCli(cmd.Cmd):
    intro = 'Welcome to the Monopoly shell. Type help or ? to list commands.\n'
    prompt = 'monopoly> '

    client: MonopolyClient = None

    def __init__(self, client):
        self.client = client
        super().__init__()

    def do_new(self, args):
        """Creates new board instance with given input file:  CREATE file_path"""
        self.client.send_command(Command.NEW)


if __name__ == '__main__':
    c = MonopolyClient(int(sys.argv[1]))
    MonopolyTcpCli(c).cmdloop()
