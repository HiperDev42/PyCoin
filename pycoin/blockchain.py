from hashlib import sha256
from pycoin.tx import Tx
from pycoin.logs import logger
import json


class Block:
    index: int  # the index of the block in the chain
    timestamp: int  # timestamp of the block
    prev: bytes  # 32 bytes hash to the previous block on chain
    nonce: int  # nonce to solve the proof of work
    txs: list[Tx]  # list of transactions in the block

    def __init__(self, txs, timestamp, index) -> None:
        self.index = index
        self.timestamp = timestamp
        self.prev = b'\x00' * 32
        self.nonce = 0
        self.txs = txs

    def toJSON(self):
        jsonDict = self.__dict__.copy()
        for key, value in jsonDict.items():
            if isinstance(value, bytes):
                jsonDict[key] = value.hex()
        return json.dumps(jsonDict, sort_keys=True)

    @property
    def hash(self) -> bytes:
        return sha256(self.toJSON().encode()).digest()


class Blockchain:
    blocks: list[Block]

    def __init__(self) -> None:
        self.blocks = []

    @property
    def last_block(self) -> Block:
        return self.blocks[-1] if len(self.blocks) > 0 else None

    def add_block(self, block: Block) -> None:
        if len(self.blocks) > 0:
            block.prev = self.last_block.hash
        else:
            block.prev = b'\x00' * 32
        logger.debug('Adding new block to chain ({}: {})'.format(
            block.index, block.hash.hex()))
        self.blocks.append(block)
