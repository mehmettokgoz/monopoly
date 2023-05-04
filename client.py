import sys
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


def listen(s):
    req = s.recv(1024)
    while req and req != '':
        print(req)
        req = s.recv(1024)


def send(s):
    while True:
        msg = input("[client]: ")
        if msg == "q":
            s.close()
            exit(0)
        else:
            s.send(msg.encode())


if __name__ == "__main__":
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(("127.0.0.1", int(sys.argv[1])))

    lt = Thread(target=listen, args=(sock,))
    st = Thread(target=send, args=(sock,))

    lt.start()
    st.start()

