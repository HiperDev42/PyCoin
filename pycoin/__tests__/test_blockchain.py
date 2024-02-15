from pycoin import Blockchain, Block
from time import time


def test_blockchain():
    blockchain = Blockchain()
    txs = []

    block = Block(txs, time(), 0)
    blockchain.add_block(block)

    block = Block(txs, time(), 1)
    blockchain.add_block(block)

    block = Block(txs, time(), 2)
    blockchain.add_block(block)

    assert len(blockchain.blocks) == 3
