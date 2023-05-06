import socket
import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock, Condition

from game.Board import Board

from protocol.client_message import decode_opcode, NewBoardCodec


# TODO: This variable should be thread-safe
boards = {}


class Agent:
    sock: socket = None
    peer: str
    m = Lock()
    c = Condition(m)
    listener: Thread
    sender: Thread
    curr_move = None
    is_auth = False

    def __init__(self, sock, peer):
        self.sock = sock
        self.peer = peer

    def authenticate(self):
        # Use this function and validate the user
        pass

    def listen_reqs(self):
        print(f"[{self.peer}] listener thread has started.")
        req = self.sock.recv(1024)
        while req and req != b'':
            print(req)
            print(type(req))
            opcode = decode_opcode(req)
            if opcode == "authenticate":
                self.is_auth = True
            elif not self.is_auth:
                self.sock.send("Please authenticate using your password.".encode())
            elif opcode == "command":
                # A new game command is recieved
                # Save choice to curr_move
                # Call notify on c
                pass
            elif opcode == "new":
                print("new operation should be executed on server-side.")
                board = Board("assets/input.json")
                boards["new_board"] = board
                self.sock.send("New board is created!".encode())
            elif opcode == "list":
                pass
            elif opcode == "close":
                pass
            elif opcode == "open":
                # boards["new_board"].attach(user, self.log, self.turncb)
                pass
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
        self.c.wait()
        board.turn(self, [])

    def log(self, log):
        # Send log to client
        self.sock.send(log.encode())

    def call_new(self):
        board = Board("../assets/input.json")
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

    users = {
        "mehmet": "tokgoz",
        "fazli": "balkan"
    }

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
