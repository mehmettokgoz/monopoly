import socket
import threading
import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock, Condition, RLock
import os

from game.Board import Board
from game.User import User

from protocol.client_message import decode_opcode, StartGameCodec, NewBoardCodec, OpenBoardCodec, AuthCodec, \
    CloseBoardCodec, CommandCodec, ReadyBoardCodec, ListBoardCodec, WatchBoardCodec, UnwatchBoardCodec, BoardStateCodec

boards = {}
user_agents = []
users = {}
users_db = {
    "mehmet": "tokgoz",
    "fazli": "balkan",
    "onur": "yuce",
    "mirza": "altay",
    "tunahan": "dundar"
}

block = Lock()


class AgentBoard:
    m = None
    c = None
    curr_move = None
    curr_args = []
    user: User
    options = []
    logs = []
    token: str

    def __init__(self, name, password):
        self.m = Lock()
        self.logs = ["This is sample log."]
        self.c = Condition(self.m)
        self.user = User(name, name, name, password)
        self.token = self.user.get_token()

    def listen_reqs(self, req):
        token, opcode = decode_opcode(req)
        if opcode == "command":
            # A new game command is received
            # Save choice to curr_move
            # Call notify on c
            s = CommandCodec().decode(req)
            self.curr_move = s.command
            self.curr_args = s.args
            self.c.acquire()
            self.c.notify_all()
            self.c.release()
            return self.logs[-1]
        elif opcode == "start":
            with block:
                s = StartGameCodec().decode(req)
                if s.name in boards.keys():
                    boards[s.name].start_game()
                else:
                    return f"Board {s.name} is not present."
                return f"start!"
        elif opcode == "new":
            with block:
                s = NewBoardCodec().decode(req)
                board = Board(os.path.abspath(s.path))
                boards[s.name] = board
                return f"New board with name {s.name} is created!"
        elif opcode == "list":
            with block:
                s = ListBoardCodec().decode(req)
                if len(boards) > 0:
                    return ",".join(boards.keys())
                else:
                    return "No board is available."
        elif opcode == "close":
            with block:
                s = CloseBoardCodec().decode(req)
                if s.name in boards.keys():
                    boards[s.name].detach(self.user)
                else:
                    return f"Board {s.name} is not present."
                return f"{self.user} is detached from board."
        elif opcode == "open":
            print("Inside open() server: ", self.user.username, threading.current_thread().ident)
            with block:
                s = OpenBoardCodec().decode(req)
                print("open codec: ", s.name)
                if s.name in boards.keys():
                    boards[s.name].attach(self.user, self.log, self.turncb)
                else:
                    return f"Board {s.name} is not present."
                return f"{self.user} is attached to board."
        elif opcode == "ready":
            with block:
                s = ReadyBoardCodec().decode(req)
                if s.name in boards.keys():
                    boards[s.name].ready(self.user)
                else:
                    return f"Board {s.name} is not present."
                return f"ready!"
        elif opcode == "watch":
            with block:
                s = WatchBoardCodec().decode(req)
                if s.name in boards.keys():
                    boards[s.name].watch(self.user, self.log)
                else:
                    return f"Board {s.name} is not present."
                return f"watch!"
        elif opcode == "unwatch":
            with block:
                s = UnwatchBoardCodec().decode(req)
                if s.name in boards.keys():
                    boards[s.name].unwatch(self.user)
                else:
                    return f"Board {s.name} is not present."
                return f"unwatch!"
        elif opcode == "state":
            with block:
                s = BoardStateCodec().decode(req)
                print(s)
                if s.name in boards.keys():
                    state = boards[s.name].get_board_state()
                    return state

    def turncb(self, board: Board, options):
        if "buy" in options or "upgrade" in options:
            options.append("not")
        self.options = options
        # Wait for client to request the options and send an answer, when an answer is recieved this will released.
        while self.curr_move is None:
            self.c.acquire()
            self.c.wait()
            self.c.release()
        move = self.curr_move
        self.curr_move = None
        if move == "teleport" or move == "pick":
            board.turn(self.user, move, self.curr_args)
        elif move == "jail-free":
            board.turn(self.user, move, "y")
        elif move == "not":
            return
        else:
            board.turn(self.user, move)

    def log(self, log):
        # Send log to client
        print(log)
        self.logs.append(log)


class Agent:
    sock: socket = None
    peer: str

    def __init__(self, sock, peer):
        self.sock = sock
        self.peer = peer
        self.listener = Thread(target=self.listen_reqs)
        self.listener.start()
        self.listener.join(1)

    def authenticate(self, s):
        if s.name in users_db.keys() and users_db[s.name] == s.password:
            user = AgentBoard(s.name, s.password)
            users[user.token] = user
            self.log(f"{user.token}")
        else:
            self.log("Login failed, please check your username or password!")

    def listen_reqs(self):
        req = self.sock.recv(1024)
        while req and req != b'':
            # TODO: Extract token here and auth accordingly!
            token, opcode = decode_opcode(req)
            if opcode == "authenticate":
                s = AuthCodec().decode(req)
                print(s)
                self.authenticate(s)
            elif token == "NO_TOKEN":
                self.sock.send("Please authenticate using your password.".encode())
            else:
                # TODO: Call the related AgenBoard here!
                response = users[token].listen_reqs(req)
                if response is not None:
                    self.sock.send(response.encode())
            req = self.sock.recv(1024)

    def log(self, log):
        # Send log to client
        self.sock.send(log.encode())


class MonopolyServer:
    sock: socket
    t: Thread
    port = 0

    def __init__(self, port):
        self.port = port

    def accept(self):
        try:
            while True:
                ns, peer = self.sock.accept()
                Agent(ns, peer)
                print(f"[{peer}] new client is connected: ")
        finally:
            self.sock.close()

    def start(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind(('localhost', self.port))
        self.sock.listen(10)
        self.t = Thread(target=self.accept)
        self.t.start()
