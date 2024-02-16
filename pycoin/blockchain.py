from hashlib import sha256
from pycoin.tx import Tx
from pycoin.logs import logger
from pycoin.utils import Encoder
import json
import time


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

    def mineBlock(self, difficulty=4) -> bool:
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


class Blockchain:
    blocks: list[Block]
    pendingTxs: list[Tx]
    difficulty: int = 2
    reward: int

    def __init__(self) -> None:
        self.blocks = []
        self.pendingTxs = []
        self.reward = 50

    def minePendingTxs(self, miner) -> None:
        logger.debug('Transactions to mine {}'.format(len(self.pendingTxs)))
        logger.info('Mining block...')
        txs = self.pendingTxs
        self.pendingTxs = []

        last_block = self.last_block

        index = 0
        if last_block:
            index = last_block.index + 1

        newBlock = Block(txs, time.time(), index)
        newBlock.prev = self.last_hash

        newBlock.mineBlock(self.difficulty)

        self.blocks.append(newBlock)
        logger.debug('New block added to chain ({})'.format(
            newBlock.hash.hex()))

    def submitTx(self, tx: Tx) -> None:
        self.pendingTxs.append(tx)

    @property
    def last_block(self) -> Block:
        return self.blocks[-1] if len(self.blocks) > 0 else None

    @property
    def last_hash(self) -> bytes:
        last_block = self.last_block
        return last_block.hash if last_block else b'\x00' * 32

    def add_block(self, block: Block) -> None:
        if len(self.blocks) > 0:
            block.prev = self.last_block.hash
        else:
            block.prev = b'\x00' * 32
        logger.debug('Adding new block to chain ({}: {})'.format(
            block.index, block.hash.hex()))
        self.blocks.append(block)
