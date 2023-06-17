# Binary Protocol Implementation for Monopoly Game
import base64


def decode_opcode(b):
    # print(type(b))
    # print(b)
    req = b.decode().split(",")

    if req[0].split(":")[0] == "token":
        return req[0].split(":")[1], req[1]
    else:
        return "NO_TOKEN", req[0]


class NewBoardCodec:

    def __init__(self, token="", name="", path=""):
        self.name = name
        self.path = path
        self.token = token

    def encode(self):
        return ("token:" + self.token + ",new," + self.name + "," + self.path).encode("utf-8")

    def decode(self, b):
        req = b.decode().split(',')
        self.token = req[0].split(":")[1]
        # print(req)
        self.name = req[2]
        self.path = req[3]
        return self


class ListBoardCodec:
    token: str

    def __init__(self, token: str = ""):
        self.token = token

    def encode(self):
        return ("token:" + self.token + ",list").encode("utf-8")

    def decode(self, b):
        req = b.decode().split(',')
        self.token = req[0].split(":")[1]
        return self


class OpenBoardCodec:

    def __init__(self, token="", name=""):
        self.token = token
        self.name = name

    def encode(self):
        return ("token:" + self.token + ",open," + self.name).encode("utf-8")

    def decode(self, req):
        req = req.decode().split(',')
        self.token = req[0].split(":")[1]
        self.name = req[2]
        return self


class CloseBoardCodec:

    def __init__(self, token="", name=""):
        self.token = token
        self.name = name

    def encode(self):
        return ("token:" + self.token + ",close," + self.name).encode("utf-8")

    def decode(self, req):
        req = req.decode().split(',')
        self.token = req[0].split(":")[1]
        self.name = req[2]
        return self


class ReadyBoardCodec:

    def __init__(self, token="", name=""):
        self.token = token
        self.name = name

    def encode(self):
        return ("token:" + self.token + ",ready," + self.name).encode("utf-8")

    def decode(self, req):
        req = req.decode().split(',')
        self.token = req[0].split(":")[1]
        self.name = req[2]
        return self


class AuthCodec:
    name: str
    password: str

    def __init__(self, token="", name="", password=""):
        self.token = token
        self.name = name
        self.password = password

    def encode(self):
        return ("token:" + self.token + ",authenticate," + self.name + "," + self.password).encode("utf-8")

    def decode(self, req):
        req = req.decode().split(",")
        self.token = req[0].split(":")[1]
        self.name = req[2]
        self.password = req[3]
        return self


class StartGameCodec:

    def __init__(self, token="", name=""):
        self.token = token
        self.name = name

    def encode(self):
        return ("token:" + self.token + ",start," + self.name).encode("utf-8")

    def decode(self, req):
        req = req.decode().split(",")
        self.token = req[0].split(":")[1]
        self.name = req[2]
        return self


class CommandCodec:

    def __init__(self, token="", command="", args=[]):
        self.token = token
        self.command = command
        self.args = args

    def encode(self):
        return ("token:" + self.token + ",command," + self.command + "," + ",".join(
            [str(i) for i in self.args])).encode("utf-8")

    def decode(self, req):
        req = req.decode().split(',')
        self.token = req[0].split(":")[1]
        self.command = req[2]
        if len(req) > 3:
            self.args = req[3]
        return self


class WatchBoardCodec:

    def __init__(self, token="", name=""):
        self.token = token
        self.name = name

    def encode(self):
        return ("token:" + self.token + ",watch," + self.name).encode("utf-8")

    def decode(self, req):
        req = req.decode().split(',')
        self.token = req[0].split(":")[1]
        self.name = req[2]
        return self


class UnwatchBoardCodec:

    def __init__(self, token="", name=""):
        self.token = token
        self.name = name

    def encode(self):
        return ("token:" + self.token + ",unwatch," + self.name).encode("utf-8")

    def decode(self, req):
        req = req.decode().split(',')
        self.token = req[0].split(":")[1]
        self.name = req[2]
        return self


class BoardStateCodec:

    def __init__(self, token="", name=""):
        self.token = token
        self.name = name

    def encode(self):
        return ("token:" + self.token + ",state," + self.name).encode("utf-8")

    def decode(self, req):
        req = req.decode().split(',')
        self.token = req[0].split(":")[1]
        self.name = req[2]
        return self


class RegisterCodec:

    def __init__(self, token="", username="", email="", full_name="", password=""):
        self.token = token
        self.username = username
        self.email = email
        self.full_name = full_name
        self.password = password

    def encode(self):
        return ("token:" + self.token + ",register," + self.username+","+self.email+","+self.full_name+","+self.password).encode("utf-8")

    def decode(self, req):
        req = req.decode().split(',')

        self.token = req[0].split(":")[1]
        self.username = req[2]
        self.email = req[3]
        self.full_name = req[4]
        self.password = req[5]
        return self