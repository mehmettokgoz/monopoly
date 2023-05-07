# Binary Protocol Implementation for Monopoly Game

"""
OPCODE | ARGS_START | [TYPE | LEN |VALUE] | ARGS_END
"""
from enum import Enum


def decode_opcode(b):
    print(type(b))
    print(b)
    return b.decode().split(",")[0]


def create_initial_buffer():
    pass


class Command(Enum):
    NEW = 1
    LIST = 2
    OPEN = 3
    CLOSE = 4


class Codec:

    def __init__(self):
        pass

    def encode_string(self, s):
        pass

    def encode_opcode(self, s):
        pass


class NewBoardCodec(Codec):

    def __init__(self, name = "", path = ""):
        self.name = name
        self.path = path
        super().__init__()

    def new_board_encode(self):
        return ("new," + self.name + "," + self.path).encode("utf-8")

    def new_board_decode(self, b):
        req = b.decode()
        req = req.split(',')
        self.name = req[1]
        self.path = req[2]
        return self


class ListBoardCodec(Codec):

    boards = []
    def __init__(self):
        super().__init__()

    def list_board_encode(self):
        return "list".encode("utf-8")

    def list_board_decode(self, req):
        return self


class OpenBoardCodec(Codec):

    name: str

    def __init__(self, name = ""):
        self.name = name
        super().__init__()

    def open_board_encode(self):
        return ("open," + self.name).encode("utf-8")

    def open_board_decode(self, req):
        req = req.decode()
        req = req.split(',')
        self.name = req[1]
        return self


class CloseBoardCodec(Codec):

    def __init__(self, name = ""):
        self.name = name
        super().__init__()

    def close_board_encode(self):
        return ("close," + self.name).encode("utf-8")

    def close_board_decode(self, req):
        req = req.decode()
        req = req.split(',')
        self.name = req[1]
        return self

class ReadyBoardCodec(Codec):

    def __init__(self, name = ""):
        self.name = name
        super().__init__()

    def ready_board_encode(self):
        return ("ready," + self.name).encode("utf-8")

    def ready_board_decode(self, req):
        req = req.decode()
        req = req.split(',')
        self.name = req[1]
        return self

class AuthCodec(Codec):
    name: str
    password: str

    def __init__(self, name = "", password = ""):
        self.name = name
        self.password = password
        super().__init__()

    def auth_encode(self):
        return ("authenticate," + self.name + "," + self.password).encode("utf-8")

    def auth_decode(self, req):
        req = req.decode()
        req = req.split(',')
        self.name = req[1]
        self.password = req[2]
        return self
    
class StartGameCodec(Codec):
    name: str

    def __init__(self, name = ""):
        self.name = name
        super().__init__()

    def start_game_encode(self):
        return ("start," + self.name).encode("utf-8")

    def start_game_decode(self, req):
        req = req.decode()
        req = req.split(',')
        self.name = req[1]
        return self

class CommandCodec(Codec):
    command: str
    args: list

    def __init__(self, command = "", args = []):
        self.command = command
        self.args = args
        super().__init__()

    def command_encode(self):
        return ("command," + self.command + "," + ",".join([str(i) for i in self.args])).encode("utf-8")

    def command_decode(self, req):
        req = req.decode()
        req = req.split(',')
        self.command = req[1]
        if len(req) > 2:
            self.args = req[2]
        return self