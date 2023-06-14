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
from web.monopoly.protocol import RegisterCodec

boards = []
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


def get_board_obj(name):
    for b in boards:
        if b["name"] == name:
            return b["obj"]
    return None


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
        self.n = Lock()
        self.logs = []
        self.c = Condition(self.m)
        self.cond = Condition(self.n)
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
            self.logs = []
            while self.logs.__len__() == 0:
                # print("waiting for logs")
                self.cond.acquire()
                self.cond.wait()
                self.cond.release()
            log = "*".join(self.logs)

            # print("all logs: ", self.logs)
            # print("log returning: ", log)
            self.logs = []
            return log
        elif opcode == "start":
            with block:
                s = StartGameCodec().decode(req)
                b = get_board_obj(s.name)
                if b is not None:
                    b.start_game()
                    return f"Game is started at board {s.name}!"
                return f"Board {s.name} is not present."
        elif opcode == "new":
            with block:
                s = NewBoardCodec().decode(req)
                board = Board(os.path.abspath(s.path))
                boards.append({"name": s.name, "obj": board})
                return f"New board with name {s.name} is created!"
        elif opcode == "list":
            with block:
                s = ListBoardCodec().decode(req)
                res = ""
                for i in range(len(boards)):
                    obj: Board = boards[i]["obj"]
                    res += boards[i]["name"] + ":" + str(len(obj.ready_users())) + ":" + str(
                        len(obj.users)) + ":" + str(obj.is_started)
                    if i != len(boards) - 1:
                        res += ","
                if res == "":
                    return "No board is available."
                return res
        elif opcode == "close":
            with block:
                s = CloseBoardCodec().decode(req)
                b = get_board_obj(s.name)
                if b is not None:
                    b.detach(self.user)
                    return f"{self.user.username} is detached from board."
                return f"Board {s.name} is not present."
        elif opcode == "open":
            # print("Inside open() server: ", self.user.username, threading.current_thread().ident)
            with block:
                s = OpenBoardCodec().decode(req)
                b = get_board_obj(s.name)
                if b is not None:
                    b.attach(self.user, self.log, self.turncb)
                    return f"{self.user.username} is attached to board."
                return f"Board {s.name} is not present."
        elif opcode == "ready":
            with block:
                s = ReadyBoardCodec().decode(req)
                b = get_board_obj(s.name)
                if b is not None:
                    b.ready(self.user)
                    return f"ready!"
                return f"Board {s.name} is not present."
        elif opcode == "watch":
            with block:
                s = WatchBoardCodec().decode(req)
                s = ReadyBoardCodec().decode(req)
                b = get_board_obj(s.name)
                if b is not None:
                    b.watch(self.user, self.log)
                    return f"watch!"
                return f"Board {s.name} is not present."
        elif opcode == "unwatch":
            with block:
                s = UnwatchBoardCodec().decode(req)
                b = get_board_obj(s.name)
                if b is not None:
                    b.unwatch(self.user)
                    return f"unwatch!"
                return f"Board {s.name} is not present."
        elif opcode == "state":
            with block:
                s = BoardStateCodec().decode(req)
                # print(s)
                b = get_board_obj(s.name)
                if b is not None:
                    return b.get_board_state()
                return f"Board {s.name} is not present."

    def turncb(self, board: Board, options):
        self.options = options
        # Wait for client to request the options and send an answer, when an answer is recieved this will released.
        while self.curr_move is None:
            self.c.acquire()
            self.c.wait()
            self.c.release()
        move = self.curr_move
        self.curr_move = None
        if move == "teleport" or move == "pick":
            board.turn(self.user, move, self.cond, self.curr_args)
        elif move == "jail-free":
            board.turn(self.user, move, self.cond, "y")
        elif move == "not":
            return
        else:
            board.turn(self.user, move, self.cond)

    def log(self, log):
        # Send log to client
        # print("logging: ",log)
        self.logs.append(log)
        self.cond.acquire()
        self.cond.notify_all()
        self.cond.release()
        # print("releasing condition")


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

    def register(self, s: RegisterCodec):
        # TODO: Protect users_db from multiple access
        users_db[s.username] = s.password
        self.log(f"User {s.username} is successfully registered.")

    def listen_reqs(self):
        req = self.sock.recv(1024)
        while req and req != b'':
            # TODO: Extract token here and auth accordingly!
            token, opcode = decode_opcode(req)
            if opcode == "authenticate":
                s = AuthCodec().decode(req)
                # print(s)
                self.authenticate(s)
            elif opcode == "register":
                s = RegisterCodec().decode(req)
                # print(s)
                self.register(s)
            elif token == "NO_TOKEN":
                self.sock.send("Please authenticate using your password.".encode())
            else:
                # TODO: Call the related AgenBoard here!
                try:
                    response = users[token].listen_reqs(req)
                    if response is not None:
                        self.sock.send(response.encode())
                except Exception as e:
                    self.sock.send("Wrong token. Please authenticate using your password.".encode())
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
                # print(f"[{peer}] new client is connected: ")
        finally:
            self.sock.close()

    def start(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind(('localhost', self.port))
        self.sock.listen(10)
        self.t = Thread(target=self.accept)
        print("socket server is started.")
        self.t.start()

