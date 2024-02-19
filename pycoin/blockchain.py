from hashlib import sha256
from pycoin.tx import Tx
from pycoin.logs import logger
from pycoin.utils import Encoder
from Crypto.PublicKey import RSA
from typing import Dict, get_type_hints, get_args, get_origin
import json
import time


class Block:
    index: int  # the index of the block in the chain
    timestamp: int  # timestamp of the block
    prev: bytes  # 32 bytes hash to the previous block on chain
    nonce: int  # nonce to solve the proof of work
    txs: list[Tx]  # list of transactions in the block

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


class Blockchain:
    blocks: list[Block]
    pendingTxs: list[Tx]
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

    def minePendingTxs(self, miner: RSA.RsaKey) -> bytes:
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

        newBlock.mineBlock(difficulty=self.difficulty)

        self.addBlock(newBlock)
        logger.debug('New block added to chain ({})'.format(
            newBlock.hash.hex()))

        return newBlock.hash

    def submitTx(self, tx: Tx) -> None:
        """
        Submits a transaction to the pending transactions list.

        Args:
            tx (Tx): The transaction to be submitted.

        Raises:
            ValueError: If the transaction is not of type Tx.
        """
        if not isinstance(tx, Tx):
            raise ValueError("Invalid transaction type. Expected Tx object.")

        try:
            if tx.validateSignature():
                self.pendingTxs.append(tx)
                logger.info('Transaction submitted: {}'.format(tx.hash.hex()))
                return True
        except Exception as e:
            logger.error(
                f'Error occurred while adding transaction to pending transactions: {e}')
            return False

    def save(self):
        with open(self.db_filename, 'w') as f:
            json.dump(self.data, f, cls=Encoder)

    def __read_data(self):
        try:
            with open(self.db_filename, 'r') as f:
                return json.load(f, cls=BlockchainDecoder)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f'Error occurred while reading blockchain data: {e}')
            return {}

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


class BlockchainDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, *args, **kwargs)

    def decode_class(self, value: any, cls) -> any:
        cls_origin = get_origin(cls) or cls
        if cls is bytes:
            if not type(value) == str:
                raise json.JSONDecodeError('Expected bytes')
            return bytes.fromhex(value)

        if cls is RSA.RsaKey:
            return RSA.import_key(bytes.fromhex(value))

        if cls_origin in {list, tuple}:
            if not isinstance(value, list):
                raise json.JSONDecodeError('Expected list')
            sub_hint = get_args(cls)[0]
            result = []
            for item in value:
                result.append(self.decode_class(item, cls=sub_hint))
            return result

        if isinstance(value, dict):
            class_hints = get_type_hints(cls)
            kwargs = {}
            for key, val in value.items():
                hint = class_hints[key]
                kwargs[key] = self.decode_class(val, cls=hint)
            obj = cls(**kwargs)
            return obj

        return value

    def decode(self, s):
        dct = super(BlockchainDecoder, self).decode(s)
        result = {}

        for key, value in dct.items():
            result[key] = self.decode_class(value, cls=Block)

        return result
