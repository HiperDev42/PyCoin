from pycoin.tx import TxV2, TxIn, TxOut
from pycoin.logs import logger
from pycoin.utils import Encoder
from pycoin.script import Pay2PubHash
from Crypto.Hash import SHA256
from typing import Dict
from .block import Block
from .blockchain_decoder import BlockchainDecoder
import json
import time


class Blockchain:
    blocks: list[Block]
    pendingTxs: list[TxV2]
    difficulty: int = 1
    reward: int
    db_filename: str
    __sync: bool
    data: Dict[str, Block]

    _json = []

    def __init__(self, db_filename: str = 'blockchain.db.json', sync=False) -> None:
        self.blocks = []
        self.pendingTxs = []
        self.reward = 50
        self.db_filename = db_filename
        self.__sync = sync
        self.load()

    def load(self):
        self.data = self.__read_data()

    def getBlockByHash(self, blockHash: bytes | str) -> Block | None:
        if isinstance(blockHash, bytes):
            blockHash = blockHash.hex()
        return self.data.get(blockHash, None)

    def addBlock(self, block: Block):
        blockHash = block.hash.hex()
        self.data[blockHash] = block
        if self.__sync:
            self.save()

    def minePendingTxs(self, pubHash: SHA256.SHA256Hash) -> bytes:
        logger.debug('Transactions to mine {}'.format(len(self.pendingTxs)))
        logger.info('Mining block...')

        last_block = self.last_block
        last_height = last_block.index if last_block else -1

        coinbase = TxV2(tx_ins=[
            TxIn(b'\x00' * 32, 0, ['OP_PUSHDATA', last_height + 1])
        ], tx_outs=[
            TxOut(50, Pay2PubHash(pubHash)),
        ])
        assert coinbase.isCoinbase()

        txs = [coinbase] + self.pendingTxs
        self.pendingTxs = []

        index = 0
        if last_block:
            index = last_block.index + 1

        newBlock = Block(txs, time.time(), index)
        newBlock.prev = self.last_hash

        newBlock.mineBlock(difficulty=self.difficulty)

        self.addBlock(newBlock)
        logger.debug('New block added to chain ({})'.format(
            newBlock.hash.hex()))

        return newBlock.hash

    def submitTx(self, tx: TxV2) -> None:
        """
        Submits a transaction to the pending transactions list.

        Args:
            tx (TxV2): The transaction to be submitted.

        Raises:
            ValueError: If the transaction is not of type Tx.
        """
        if not isinstance(tx, TxV2):
            raise ValueError("Invalid transaction type. Expected Tx object.")
        if tx.isCoinbase():
            raise ValueError("Cannot submit coinbase transaction.")

        self.pendingTxs.append(tx)
        logger.info('Transaction submitted: {}'.format(tx.hash.hex()))
        return True

    def save(self):
        with open(self.db_filename, 'w') as f:
            json.dump(self.data, f, cls=Encoder, indent=4)

    def __read_data(self):
        try:
            with open(self.db_filename, 'r') as f:
                return json.load(f, cls=BlockchainDecoder)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f'Error occurred while reading blockchain data: {e}')
            return {}

    def blockIndex(self, sorted=True) -> Dict[int, Block]:
        index = {}
        for block in self.data.values():
            index[block.index] = block

        if sorted:
            return dict(sorted(index.items(), key=lambda item: item[0]))
        return index

    def getSnapshot(self):
        pass

    @property
    def last_block(self) -> Block:
        idx = -1
        latest_block = None
        for _, block in self.data.items():
            if block.index > idx:
                latest_block = block
                idx = block.index
        return latest_block

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
