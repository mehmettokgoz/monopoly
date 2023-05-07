import socket
import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock, Condition
import os

from game.Board import Board
from game.User import User

from protocol.client_message import decode_opcode, StartGameCodec, NewBoardCodec, OpenBoardCodec, AuthCodec, CloseBoardCodec, CommandCodec, ReadyBoardCodec, ListBoardCodec


# TODO: This variable should be thread-safe
boards = {}
users = {}
users_database = {
    "mehmet": "tokgoz",
    "fazli": "balkan"
}

class Agent:
    sock: socket = None
    peer: str
    m = Lock()
    c = Condition(m)
    listener: Thread
    sender: Thread
    curr_move = None
    curr_args = []
    is_auth = False
    user = None

    def __init__(self, sock, peer):
        self.sock = sock
        self.peer = peer

    def authenticate(self, s):
        # Use this function and validate the user
        if users_database[s.name] == s.password:
            self.is_auth = True
            self.user = User(s.name, s.name, s.name, s.password)
            self.log("authentication is successful!")
        else:
            self.log("authentication failed!")

    def listen_reqs(self):
        print(f"[{self.peer}] listener thread has started.")
        req = self.sock.recv(1024)
        while req and req != b'':
            print(req)
            print(type(req))
            opcode = decode_opcode(req)
            if opcode == "authenticate":
                s = AuthCodec().auth_decode(req)
                self.authenticate(s)
            elif not self.is_auth:
                self.sock.send("Please authenticate using your password.".encode())
            elif opcode == "command":
                # A new game command is recieved
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
                boards[s.name].start_game()
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
                boards[s.name].detach(self.user)
            elif opcode == "open":
                s = OpenBoardCodec().open_board_decode(req)
                boards[s.name].attach(self.user, self.log, self.turncb)
            elif opcode == "ready":
                s = ReadyBoardCodec().ready_board_decode(req)
                boards[s.name].ready(self.user)

            req = self.sock.recv(1024)

    def send_logs(self):
        print(f"[{self.peer}] sender thread has started.")
        while True:
            # TODO: Wait for monitor (logs) and send to client
            log = "This is a log message."
            time.sleep(1)
            self.sock.send(log.encode())

    def turncb(self, board: Board, options):
        # Send options to client
        # Wait for condition variable to notify
        # Response is saved globally for Agent
        # Decode the response
        # Call board
        self.log("your command options: " + str(options))
        self.c.acquire()
        self.c.wait()

        # TODO: release when it is recursive
        if self.curr_move == "teleport" or self.curr_move == "pick":
            # TODO : index?
            self.c.release()
            board.turn(self.user, self.curr_move, self.curr_args[0])
        elif self.curr_move == "jail-free":
            self.c.release()
            board.turn(self.user, self.curr_move, "y")
        else:
            self.c.release()
            board.turn(self.user, self.curr_move)        

    def log(self, log):
        # Send log to client
        self.sock.send(log.encode())

    def call_new(self):
        board = Board(os.path.abspath("assets/input.json"))
        print("new board instance is created.")
        boards.append(board)

    def call_list(self):
        pass

    def call_open(self, req):
        # Register self.turncb function for user board
        # Register self.log function for user board
        pass

    def call_close(self):
        pass

    def call_others(self):
        pass

    def start_agent(self):
        self.listener = Thread(target=self.listen_reqs)
        # self.sender = Thread(target=self.send_logs)
        self.listener.start()
        # self.sender.start()

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
