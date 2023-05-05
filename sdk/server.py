import cmd
from sdk.tcp.monopoly_server import MonopolyServer


class MonopolyTcpServerCli(cmd.Cmd):
    intro = 'Welcome to the Monopoly Server shell. Type help or ? to list commands.\n'
    prompt = 'server> '

    server: MonopolyServer = None

    def __init__(self):
        super().__init__()

    def do_create(self, args):
        # TODO: Get port from args
        port = 1543
        self.server = MonopolyServer(port)

    def do_start(self, args):
        self.server.start()

    def do_stop(self, args):
        self.server.stop()


if __name__ == '__main__':
    MonopolyTcpServerCli().cmdloop()
