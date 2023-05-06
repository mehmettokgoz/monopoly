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
    sock: socket.socket

    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("127.0.0.1", port))
        lt = Thread(target=self.listen)
        lt.start()

    def send_command(self, c, *args):
        s = None
        if c == "call":
            s = NewBoardCodec("yeni_board", "../assets&/input.json").new_board_encode()
            print("new board coded is created")
            print(s)
        if c == "auth":
            s = "authenticate,12345".encode("utf-8")
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
            self.c.acquire()
            print(req)
            self.logs.append(req)
            self.c.notify_all()
            self.c.release()
            req = self.sock.recv(1024)


