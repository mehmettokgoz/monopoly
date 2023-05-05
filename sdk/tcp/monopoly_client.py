# Client class for Monopoly
import socket
from threading import Thread, Lock, Condition

from protocol.client_message import NewBoardCodec, Command, ListBoardCodec, OpenBoardCodec, CloseBoardCodec


class MonopolyClient:
    sock: socket.socket = None

    logs = []
    m = Lock()
    c = Condition(m)

    def __init__(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", port))
        self.sock = sock
        lt = Thread(target=self.listen)
        pl = Thread(target=self.print_logs)
        lt.start()
        pl.start()

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
        while req and req != '':
            self.logs.append(req)
            self.c.notifyAll()
            req = self.sock.recv(1024)

    def print_logs(self):
        self.m.acquire()
        while True:
            self.c.wait()
            print(self.logs.pop())




