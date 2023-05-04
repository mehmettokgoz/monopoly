# Client class for Monopoly
import socket
from threading import Thread

from sdk.protocol.client_message import Command, NewBoardCodec, ListBoardCodec, OpenBoardCodec, CloseBoardCodec


class MonopolyClient:
    sock: socket.socket = None

    def __init__(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", port))
        self.sock = sock

    def send_command(self, c, *args):
        s = None
        if c == Command.NEW:
            s = NewBoardCodec().new_board_encode()
        elif c == Command.LIST:
            s = ListBoardCodec().list_board_encode()
        elif c == Command.OPEN:
            s = OpenBoardCodec().open_board_encode()
        elif c == Command.CLOSE:
            s = CloseBoardCodec().close_board_encode()
        self.sock.send(s)

    def start_listen(self):
        def listen():
            req = self.sock.recv(1024)
            while req and req != '':
                print(req)
                req = self.sock.recv(1024)

        lt = Thread(target=listen)
        lt.start()

