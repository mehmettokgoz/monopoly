import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import sys


def listen_reqs(sock, peer):
    print(f"[{peer}] listener thread has started.")
    req = sock.recv(1024)
    while req and req != '':
        print(req)
        # TODO: Do useful operations in here
        req = sock.recv(1024)


def send_logs(sock, peer):
    print(f"[{peer}] sender thread has started.")
    while True:
        # TODO: Wait for monitor (logs) and send to client
        log = "This is a log message."
        time.sleep(10)
        sock.send(log.encode())


def server(port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(('localhost', port))
    sock.listen(10)
    try:
        while True:
            ns, peer = sock.accept()
            print(f"[{peer}] new client is connected: ")
            listener_thread = Thread(target=listen_reqs, args=(ns, peer))
            sender_thread = Thread(target=send_logs, args=(ns, peer))
            listener_thread.start()
            sender_thread.start()
    finally:
        sock.close()


if __name__ == "__main__":
    p = int(sys.argv[1])
    st = Thread(target=server, args=(p,))
    st.start()
