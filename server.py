import cmd
import sys
from tcp.monopoly_server import MonopolyServer

if __name__ == '__main__':
    port = int(sys.argv[-1])
    server = MonopolyServer(port)
    server.start()

