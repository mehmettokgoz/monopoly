# Client class for Monopoly
import socket

from protocol import NewBoardCodec, StartGameCodec, ListBoardCodec, OpenBoardCodec, \
    CloseBoardCodec, AuthCodec, CommandCodec, ReadyBoardCodec, UnwatchBoardCodec, WatchBoardCodec, BoardStateCodec, RegisterCodec


class MonopolyClient:
    sock: socket.socket = None

    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("127.0.0.1", port))

    def send_command(self, token, command, *args):
        print("now sending...")
        s = None
        if command == "new":
            s = NewBoardCodec(token=token, name=args[0], path=args[1]).encode()
        elif command == "auth":
            s = AuthCodec(token=token, name=args[0], password=args[1]).encode()
        elif command == "register":
            s = RegisterCodec(token=token, username=args[0], email=args[1], full_name=args[2], password=args[3]).encode()
        elif command == "list":
            s = ListBoardCodec(token).encode()
        elif command == "open":
            s = OpenBoardCodec(token=token, name=args[0]).encode()
        elif command == "close":
            s = CloseBoardCodec(token=token, name=args[0]).encode()
        elif command == "start":
            s = StartGameCodec(token=token, name=args[0]).encode()
        elif command == "command":
            s = CommandCodec(token=token, command=args[0], args=args[1:]).encode()
        elif command == "ready":
            s = ReadyBoardCodec(token=token, name=args[0]).encode()
        elif command == "watch":
            s = WatchBoardCodec(token=token, name=args[0]).encode()
        elif command == "unwatch":
            s = UnwatchBoardCodec(token=token, name=args[0]).encode()
        elif command == "state":
            s = BoardStateCodec(token=token, name=args[0]).encode()
        else:
            return
        self.sock.send(s)

        return self.sock.recv(4096)

    def close(self):
        self.sock.close()
