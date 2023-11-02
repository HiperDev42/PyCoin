from . import Tx
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

    def __init__(self, prev_block, time, bits: int = 4, nonce: int = 0, txs=[]) -> None:
        self.prev_block = prev_block
        self.time = time
        self.bits = bits
        self.nonce = nonce
        self.txs = txs

    def __repr__(self) -> str:
        return self.hash().hex()

    def validate(self):
        block_hash = self.hash()
        mask = (1 << (self.bits))-1

        if block_hash[-1] & mask == 0:
            return True
        return False

    async def mine(self):
        self.nonce = 0
        while not self.validate():
            self.nonce += 1
        return self

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
