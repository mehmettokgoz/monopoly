# Client class for Monopoly
import socket

from monopoly.protocol import NewBoardCodec, Command, StartGameCodec, ListBoardCodec, OpenBoardCodec, \
    CloseBoardCodec, AuthCodec, CommandCodec, ReadyBoardCodec, UnwatchBoardCodec, WatchBoardCodec


class MonopolyClient:
    sock: socket.socket = None

    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("127.0.0.1", port))

    def send_command(self, c, *args):
        command_and_args = c.split(",")
        command = command_and_args[0]
        args = command_and_args[1:]
        s = None
        if command == "new":
            s = NewBoardCodec(args[0], args[1]).new_board_encode()
        elif command == "auth":
            s = AuthCodec(args[0], args[1]).auth_encode()
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
        elif command == "ready":
            s = ReadyBoardCodec(args[0]).ready_board_encode()
        elif command == "watch":
            s = WatchBoardCodec(args[0]).watch_board_encode()
        elif command == "unwatch":
            s = UnwatchBoardCodec(args[0]).unwatch_board_encode()
        elif command == "debug":
            self.sock.send(("debug," + args[0]).encode())
            return
        else:
            return
        self.sock.send(s)

        return self.sock.recv(1024)


    def close(self):
        self.sock.close()