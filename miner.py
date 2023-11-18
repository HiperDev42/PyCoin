from blockchain import *
from network import Node, Peer
from typing import Tuple, Set
from random import randint
import asyncio
import logging
import json
import time
import threading


MINE_INTERVAL: int = 10


logger = logging.getLogger(__name__)

reward_account = Account(1)
mempool = {}
blockchain = Blockchain()
_stop_event: threading.Event = threading.Event()
_miner_thread: threading.Thread = None


def submit_tx(tx: Tx):
    tx_hash = tx.get_hash().hex()
    mempool[tx_hash] = tx


async def mine_block():
    logger.debug('Mining new block...')
    reward = Tx(Account(0), reward_account, 50)

    txs = list(mempool.values())
    mempool.clear()
    txs.append(reward)

    block = Block(
        prev_block=blockchain.last_hash(),
        time=int(time.time()),
        txs=txs
    )

    while not block.validate():
        block.nonce = randint(0, (1 << 32)-1)

    return block


def miner():
    logger.info('Miner start')
    while not _stop_event.is_set():
        if _stop_event.wait(MINE_INTERVAL):
            break

        block = asyncio.run(mine_block())

        logger.debug(f'Added new block')
        blockchain.append(block)
        blockchain.flush()
    logger.info('Miner stopped')


def start():
    global _miner_thread
    _stop_event.clear()
    _miner_thread = threading.Thread(target=miner)
    _miner_thread.start()


def stop():
    global _miner_thread
    _stop_event.set()
    if _miner_thread:
        _miner_thread.join()
        _miner_thread = None


def is_alive():
    return _miner_thread.is_alive()


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    miner()
