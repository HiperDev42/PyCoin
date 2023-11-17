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

node = Node()

reward_account = Account(1)
mempool = {}
blockchain = Blockchain()
_stop_event: threading.Event = threading.Event()
_mining_thread: threading.Thread = None


def submit_tx(tx: Tx):
    tx_hash = tx.get_hash().hex()
    mempool[tx_hash] = tx


@node.command('ping')
def ping(ctx):
    return 'pong', ctx['data']


@node.command('tx')
def tx(ctx) -> Tuple[str, bytes]:
    tx_json = json.loads(ctx['data'].decode())
    tx = Tx.from_json(tx_json)

    result = submit_tx(tx)

    return 'ack', b''


async def mine_block():
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
    _stop_event.clear()
    logger.info('Miner starting...')
    while not _stop_event.is_set():
        if _stop_event.wait(MINE_INTERVAL):
            break

        # logger.debug('Mining')
        block = asyncio.run(mine_block())

        logger.debug(f'Added new block')
        blockchain.append(block)
        blockchain.flush()

        for block_hash in blockchain.chain[-4:]:
            block = blockchain.get_block(block_hash)
            # block.show()

        balance1 = blockchain.get_balance(Account(1))
        # print(f'Balance 1: {balance1}')

        balance2 = blockchain.get_balance(Account(2))
        # print(f'Balance 2: {balance2}')


def start():
    global _mining_thread
    _mining_thread = threading.Thread(target=miner)
    _mining_thread.start()
    node.start()


def stop():
    global _mining_thread
    node.stop()
    _stop_event.set()
    if _mining_thread:
        _mining_thread.join()
        _mining_thread = None
        logger.info('Miner stopped')


def is_alive():
    return _mining_thread.is_alive()


if __name__ == '__main__':
    miner()
