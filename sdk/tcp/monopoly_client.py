# Client class for Monopoly
import socket
from threading import Thread, Lock, Condition

from protocol.client_message import NewBoardCodec, Command, ListBoardCodec, OpenBoardCodec, CloseBoardCodec


class MonopolyClient:
    sock: socket.socket = None

    # TODO: Logs queue should be thread-safe
    logs = []
    m = Lock()
    c = Condition(m)

    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("127.0.0.1", port))
        lt = Thread(target=self.listen)
        lt.start()

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

    def listen(self):
        req = self.sock.recv(1024)
        self.c.acquire()
        while req and req != '':
            self.logs.append(req)
            self.c.notifyAll()
            req = self.sock.recv(1024)

