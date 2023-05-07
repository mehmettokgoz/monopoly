import socket
import threading
import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock, Condition, RLock
import os

from game.Board import Board
from game.User import User

from protocol.client_message import decode_opcode, StartGameCodec, NewBoardCodec, OpenBoardCodec, AuthCodec, \
    CloseBoardCodec, CommandCodec, ReadyBoardCodec, ListBoardCodec, WatchBoardCodec, UnwatchBoardCodec

# TODO: This variable should be thread-safe
boards = {}
users_db = {
    "mehmet": "tokgoz",
    "fazli": "balkan"
}


class Agent:
    sock: socket = None
    peer: str
    m = None
    c = None
    listener: Thread
    sender: Thread
    curr_move = None
    curr_args = []
    is_auth = False
    user = None

    def __init__(self, sock, peer):
        self.sock = sock
        self.peer = peer
        self.m = Lock()
        self.c = Condition(self.m)

    def authenticate(self, s):
        # Use this function and validate the user
        if users_db[s.name] == s.password:
            self.is_auth = True
            self.user = User(s.name, s.name, s.name, s.password)
            self.log(f"Login successful, welcome {s.name}!")
        else:
            self.log("Login failed, please check your username or password!")

    def listen_reqs(self):
        print(f"[{self.peer}] listener thread has started.")
        req = self.sock.recv(1024)
        while req and req != b'':
            opcode = decode_opcode(req)
            if opcode == "authenticate":
                s = AuthCodec().auth_decode(req)
                self.authenticate(s)
            elif not self.is_auth:
                self.sock.send("Please authenticate using your password.".encode())
            elif opcode == "command":
                # A new game command is received
                # Save choice to curr_move
                # Call notify on c
                s = CommandCodec().command_decode(req)
                self.curr_move = s.command
                self.curr_args = s.args
                self.c.acquire()
                self.c.notify_all()
                self.c.release()
            elif opcode == "start":
                s = StartGameCodec().start_game_decode(req)
                if s.name in boards.keys():
                    boards[s.name].start_game()
                else:
                    self.log(f"Board {s.name} is not present.")
            elif opcode == "new":
                s = NewBoardCodec().new_board_decode(req)
                board = Board(os.path.abspath(s.path))
                boards[s.name] = board
                self.log(f"New board with name {s.name} is created!")
            elif opcode == "list":
                s = ListBoardCodec().list_board_decode(req)
                self.log(",".join(boards.keys()))
            elif opcode == "close":
                s = CloseBoardCodec().close_board_decode(req)
                if s.name in boards.keys():
                    boards[s.name].detach(self.user)
                else:
                    self.log(f"Board {s.name} is not present.")
            elif opcode == "open":
                print("Inside open() server: ", self.user.username, threading.current_thread().ident)
                s = OpenBoardCodec().open_board_decode(req)
                print("open codec: ", s.name)
                if s.name in boards.keys():
                    boards[s.name].attach(self.user, self.log, self.turncb)
                else:
                    self.log(f"Board {s.name} is not present.")
            elif opcode == "ready":
                s = ReadyBoardCodec().ready_board_decode(req)
                if s.name in boards.keys():
                    boards[s.name].ready(self.user)
                else:
                    self.log(f"Board {s.name} is not present.")
            elif opcode == "watch":
                s = WatchBoardCodec().watch_board_decode(req)
                if s.name in boards.keys():
                    boards[s.name].watch(self.user, self.log)
                else:
                    self.log(f"Board {s.name} is not present.")
            elif opcode == "unwatch":
                s = UnwatchBoardCodec().unwatch_board_decode(req)
                if s.name in boards.keys():
                    boards[s.name].unwatch(self.user)
                else:
                    self.log(f"Board {s.name} is not present.")
            elif opcode == "debug":
                print("debug request, ", req)
                req = req.decode().split(",")
                self.board_status(req[1])
            req = self.sock.recv(1024)


    def board_status(self, name):
        self.sock.send(("callbacks: "+", ".join(boards[name].callbacks.keys())).encode())
        usersdas = []
        for i in boards[name].users:
            usersdas.append(i.username)
        self.sock.send(("users: "+", ".join(usersdas)).encode())

    def turncb(self, board: Board, options):
        # Send options to client
        # Wait for condition variable to notify
        # Response is saved globally for Agent
        # Decode the response
        # Call board
        self.log("Your command options: " + str(",".join(options)))
        while self.curr_move is None:
            self.c.acquire()
            self.c.wait()
            self.c.release()
        move = self.curr_move
        self.curr_move = None
        # TODO: release when it is recursive
        if move == "teleport" or move == "pick":
            # TODO : index?
            board.turn(self.user, move, self.curr_args[0])
        elif self.curr_move == "jail-free":
            board.turn(self.user, move, "y")
        else:
            board.turn(self.user, move)

    def log(self, log):
        # Send log to client
        # TODO: Should we protect socket.send()
        print("Sending log message to ", self.user.username, threading.current_thread().ident)
        self.sock.send(log.encode())

    def start_agent(self):
        self.listener = Thread(target=self.listen_reqs)
        self.listener.start()

    def stop_agent(self):
        self.listener.join(1)
        self.sender.join(1)


class MonopolyServer:
    sock: socket
    t: Thread
    agents = []
    port = 0

    def __init__(self, port):
        self.port = port

    def accept(self):
        try:
            while True:
                ns, peer = self.sock.accept()
                agent = Agent(ns, peer)
                self.agents.append(agent)
                agent.start_agent()
                print(f"[{peer}] new client is connected: ")
        finally:
            self.sock.close()

    def start(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind(('localhost', self.port))
        self.sock.listen(10)
        self.t = Thread(target=self.accept)
        self.t.start()

    def stop(self):
        for a in self.agents:
            a.stop_agent()
        self.t.join(1)
