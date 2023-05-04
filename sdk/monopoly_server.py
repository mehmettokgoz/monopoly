import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


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

    def __init__(self, port):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind(('localhost', port))
        self.sock.listen(10)

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
        self.t = Thread(target=self.accept)
        self.t.start()

    def stop(self):
        for a in self.agents:
            a.stop_agent()
        self.t.join(1)
