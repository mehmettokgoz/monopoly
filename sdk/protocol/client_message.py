# Binary Protocol Implementation for Monopoly Game

"""
OPCODE | ARGS_START | [TYPE | LEN |VALUE] | ARGS_END
"""
from enum import Enum


def decode_opcode(self, b):
    pass


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

    def __init__(self):
        super().__init__()

    def new_board_encode(self):
        pass

    def new_board_decode(self):
        pass


class ListBoardCodec(Codec):

    def __init__(self):
        super().__init__()

    def list_board_encode(self):
        pass

    def list_board_decode(self):
        pass


class OpenBoardCodec(Codec):
    
    def __init__(self):
        super().__init__()

    def open_board_encode(self):
        pass

    def open_board_decode(self):
        pass
        

class CloseBoardCodec(Codec):
    
    def __init__(self):
        super().__init__()

    def close_board_encode(self):
        pass

    def close_board_decode(self):
        pass

