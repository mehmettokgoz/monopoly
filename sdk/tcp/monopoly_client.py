# Client class for Monopoly
import socket
from threading import Thread, Lock, Condition

from protocol.client_message import NewBoardCodec, Command, StartGameCodec, ListBoardCodec, OpenBoardCodec, CloseBoardCodec, AuthCodec, CommandCodec


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
        command_and_args = c.split(",")
        command = command_and_args[0]
        args = command_and_args[1:]
        print(args)
        s = None
        if command == "call":
            s = NewBoardCodec("yeni_board", "../assets&/input.json").new_board_encode()
            print("new board coded is created")
            print(s)
        if command == "auth":
            s = AuthCodec(args[0], args[1]).auth_encode()
            # s = "authenticate,12345".encode("utf-8")
        elif command == "list":
            s = ListBoardCodec().list_board_encode()
        elif command == "open":
            s = OpenBoardCodec(args[0]).open_board_encode()
        elif command == "close":
            s = CloseBoardCodec(args[0]).close_board_encode()
        elif command == "start":
            s = StartGameCodec(args[0]).start_game_encode()
        elif command == "command":
            s = CommandCodec(args[0], args[1:]).command_encode()
        elif command == "y" or command == "n":
            s = command.encode()
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


