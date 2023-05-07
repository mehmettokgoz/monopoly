import cmd

from tcp.monopoly_client import MonopolyClient
from protocol.client_message import Command


class MonopolyTcpCli(cmd.Cmd):
    intro = 'Welcome to the Monopoly Client shell. Type help or ? to list commands.\n'
    prompt = 'client> '

    client: MonopolyClient = None

    def __init__(self):
        super().__init__()

    def do_create(self, args):
        # TODO: Get port from args
        port = 1543
        self.client = MonopolyClient(port)

    def do_new(self, args):
        self.client.send_command(Command.NEW)


if __name__ == '__main__':
    MonopolyTcpCli().cmdloop()
