#!/usr/bin/python


import logging
from threading import Thread, Lock, Condition
import socket

import websockets
from websockets.sync.server import serve
import sys

from client import MonopolyClient


port = 1576
class Chat:
    def __init__(self):
        self.buf = []
        self.state = ""
        self.lock = Lock()
        self.state_lock = Lock()
        self.newmess = Condition(self.lock)
        self.state_cond = Condition(self.state_lock)

    def newmessage(self, mess):
        self.lock.acquire()
        self.buf.append(mess)
        self.newmess.notifyAll()
        self.lock.release()

    def save_state(self, mess):
        self.state_lock.acquire()
        self.state = mess
        self.state_cond.notifyAll()
        self.state_lock.release()

    def getmessages(self, after=0):
        self.lock.acquire()
        if len(self.buf) < after:
            a = []
        else:
            a = self.buf[after:]
        self.lock.release()
        return a

    def get_state(self):
        self.state_lock.acquire()
        a = self.state
        self.state_lock.release()
        return a


class WRAgent(Thread):
    def __init__(self, conn, chat):
        self.conn = conn
        self.chat = chat
        self.current = 0
        Thread.__init__(self)

    def run(self):
        print("started new agent")
        oldmess = self.chat.getmessages()
        self.current += len(oldmess)
        self.conn.send('*'.join([i for i in oldmess]))
        notexit = True
        while notexit:
            self.chat.lock.acquire()
            self.chat.newmess.wait()
            self.chat.lock.release()
            oldmess = self.chat.getmessages(self.current)
            self.current += len(oldmess)
            try:
                resp  ='*'.join([i for i in oldmess])
                print("sending respo: ", resp)
                self.conn.send(resp)
            except:
                notexit = False


class WRStateAgent(Thread):
    def __init__(self, conn, chat):
        self.conn = conn
        self.chat = chat
        Thread.__init__(self)

    def run(self):
        old_state = self.chat.get_state()
        if old_state != "":
            self.conn.send(old_state)
        notexit = True
        while notexit:
            self.chat.state_lock.acquire()
            self.chat.state_cond.wait()
            self.chat.state_lock.release()
            state = self.chat.get_state()
            try:
                self.conn.send(state)
            except:
                notexit = False


chat_rooms = {}

if len(sys.argv) != 2:
    print('usage: ', sys.argv[0], 'port')
    sys.exit(-1)


def serveconnection(sc):
    print("started")
    board_name = sc.recv(1024)
    print("board_name", board_name)
    if not chat_rooms.keys().__contains__(board_name):
        chat_rooms[board_name] = Chat()
    cr = chat_rooms[board_name]
    wrtr = WRAgent(sc, cr)
    wrtr_state = WRStateAgent(sc, cr)
    wrtr.start()
    wrtr_state.start()
    try:
        inp = sc.recv(1024)
        while inp:

            print(inp)
            ty = inp.split(",")[0]
            if ty == "n":
                cr.newmessage(" ".join(inp.split(",")[1:]))
            else:
                client = MonopolyClient(port)
                command_details = inp.split(",")
                response = b''
                log = True
                if command_details[0] == "open":
                    response = client.send_command(command_details[2], "open", command_details[1])
                elif command_details[0] == "ready":
                    response = client.send_command(command_details[2], "ready", command_details[1])
                elif command_details[0] == "start":
                    response = client.send_command(command_details[2], "start", command_details[1])
                elif command_details[0] == "close":
                    response = client.send_command(command_details[2], "close", command_details[1])
                elif command_details[0] == "start":
                    response = client.send_command(command_details[2], "start", command_details[1])
                elif command_details[0] == "command":
                    response = client.send_command(command_details[2], "command", command_details[1], command_details[3])
                elif command_details[0] == "state":
                    response = client.send_command(command_details[2], "state", command_details[1])
                    log = False
                if log:
                    token_response = response.decode()
                    print("sending: " + "l&" + token_response)
                    cr.newmessage("l&" + token_response)
                    response = client.send_command(command_details[2], "state", command_details[1])
                    cr.save_state("s&" + response.decode())
                else:
                    print("sending: " + "s&" + response.decode())
                    cr.save_state("s&" + response.decode())
                client.close()

            print('waiting next')
            inp = sc.recv(1024)
        print('client is terminating')
        sc.close()
    except websockets.exceptions.ConnectionClosed:
        sc.close()


HOST = ''
PORT = int(sys.argv[1])
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((HOST, PORT))

chatroom = Chat()

with serve(lambda nc: serveconnection(nc), host=HOST, port=PORT, logger=logging.getLogger("chatsrv")) as server:
    print("serving")
    server.serve_forever()
