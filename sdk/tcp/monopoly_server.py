import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from game.Board import Board

# TODO: This variable should be thread-safe
boards = []


class Agent:
    sock: socket = None
    peer: str
    listener: Thread
    sender: Thread

    def __init__(self, sock, peer):
        self.sock = sock
        self.peer = peer

    def listen_reqs(self):
        print(f"[{self.peer}] listener thread has started.")
        req = self.sock.recv(1024)
        while req and req != '':
            print(req)
            # TODO: Do useful operations in here
            req = self.sock.recv(1024)

    def send_logs(self):
        print(f"[{self.peer}] sender thread has started.")
        while True:
            # TODO: Wait for monitor (logs) and send to client
            log = "This is a log message."
            time.sleep(10)
            self.sock.send(log.encode())

    """
    Important note:
    
    There should be two function: turncb and log for communicating with client.
    """
    def authenticate(self):
        pass

    def turncb(self):
        pass

    def log(self):
        pass

    def call_new(self):
        board = Board("../assets/input.json")
        print("new board instance is created.")
        boards.append(board)

    def call_list(self):
        pass

    def call_open(self):
        pass

    def call_close(self):
        pass

    def call_others(self):
        pass

    def start_agent(self):
        self.listener = Thread(target=self.listen_reqs)
        self.sender = Thread(target=self.send_logs)
        self.listener.start()
        self.sender.start()

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
