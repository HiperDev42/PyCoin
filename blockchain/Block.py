from .Tx import Tx
from .utils import get_merkle_root
import hashlib
import struct


class BlockHeader:
    VERSION = 1
    prev_block: bytes
    merkle_root: bytes
    time: int
    bits: int
    nonce: int

    def __init__(self, prev_block, merkle_root, time, bits, nonce) -> None:
        self.prev_block = prev_block
        self.merkle_root = merkle_root
        self.time = time
        self.bits = bits
        self.nonce = nonce

    def hash(self) -> bytes:
        data_bytes = struct.pack(
            '32s32sIII', self.prev_block, self.merkle_root, self.time, self.bits, self.nonce)
        return hashlib.sha256(data_bytes).digest()


class Block(BlockHeader):
    bits: int = 8
    txs: list[Tx]

    def __init__(self, prev_block, time = 0, bits: int = 8, nonce: int = 0, txs=[]) -> None:
        self.prev_block = prev_block
        self.time = time
        self.bits = bits
        self.nonce = nonce
        self.txs = txs
    
    def to_json(self):
        return {
            'prev_block': self.prev_block.hex(),
            'time': self.time,
            'bits': self.bits,
            'nonce': self.nonce,
            'txs': [tx.to_json() for tx in self.txs]
        }

    @staticmethod
    def from_json(serial):
        prev_block = bytes.fromhex(serial.get('prev_block'))
        time = serial.get('time')
        bits = serial.get('bits')
        nonce = serial.get('nonce')
        txs = [Tx.from_json(tx_json) for tx_json in serial.get('txs')]
        block = Block(prev_block, time=time, nonce=nonce, bits=bits, txs=txs)
        return block

    def __repr__(self) -> str:
        return self.hash().hex()

    def show(self):
        print(f'Block ({self.hash().hex()})')
        print(f'\t- Prev block: {self.prev_block.hex()}')
        print(f'\t- Nonce: {self.nonce}')
        print(f'\t- Bits: {self.bits}')
        print(f'\t- Time: {self.time}')

    def validate(self):
        block_hash = self.hash()
        mask = (1 << (self.bits))-1

        if block_hash[-1] & mask == 0:
            return True
        return False
    
    def checksum(self, in_hash):
        return in_hash == self.hash()

    @property
    def merkle_root(self):
        hashes = [tx.get_hash() for tx in self.txs]
        return get_merkle_root(hashes)

    @property
    def header(self):
        return BlockHeader(
            self.prev_block,
            self.merkle_root,
            self.time,
            self.bits,
            self.nonce
        )
