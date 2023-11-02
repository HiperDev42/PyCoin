from . import Account
import struct
import hashlib


class Tx:
    VERSION = 1
    src: Account
    dst: Account
    amount: int

    def __init__(self, src: Account, dst: Account, amount: int) -> None:
        self.src = src
        self.dst = dst
        self.amount = amount

    def __repr__(self) -> str:
        return f'Tx[{self.src} -{self.amount}-> {self.dst}]'

    def get_hash(self):
        data_bytes = struct.pack('III', self.src.id, self.dst.id, self.amount)
        return hashlib.sha256(data_bytes).digest()
