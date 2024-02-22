from hashlib import sha256
from pycoin.tx import TxV2
from pycoin.logs import logger
from pycoin.utils import Encoder
import json
import time


class Block:
    index: int  # the index of the block in the chain
    timestamp: int  # timestamp of the block
    prev: bytes  # 32 bytes hash to the previous block on chain
    nonce: int  # nonce to solve the proof of work
    txs: list[TxV2]  # list of transactions in the block

    _json = ['index', 'timestamp', 'prev', 'nonce', 'txs']

    def __init__(self, txs, timestamp, index, prev=b'\x00' * 32, nonce=0) -> None:
        self.index = index
        self.timestamp = timestamp
        self.prev = prev
        self.nonce = nonce
        self.txs = txs

    def mineBlock(self, difficulty=1) -> bool:
        start = time.time()
        while not self.validateHash(difficulty):
            self.nonce += 1
        end = time.time()
        ellapsed = end - start

        logger.debug("Block mined in {:.2f} seconds".format(ellapsed))
        return True

    def toJSON(self):
        return json.dumps(self, cls=Encoder, sort_keys=True)

    def validateHash(self, difficulty=4) -> bool:
        return self.hash.startswith(b'\x00' * difficulty)

    @property
    def hash(self) -> bytes:
        return sha256(self.toJSON().encode()).digest()
