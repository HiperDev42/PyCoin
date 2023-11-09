from blockchain import *
from network.Node import Node
from typing import Tuple
from random import randint
import asyncio
import time
import logging
import json
import time
import threading

logger = logging.getLogger(__name__)

node = Node()

reward_account = Account(1)
mempool = {}
blockchain = Blockchain()
running = threading.Event()


def submit_tx(tx: Tx):
    tx_hash = tx.get_hash().hex()
    mempool[tx_hash] = tx


@node.command('ping')
def ping(payload):
    return 'pong', b''


@node.command('tx')
def tx(payload: bytes) -> Tuple[str, bytes]:
    tx_json = json.loads(payload.decode())
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
    while not running.is_set():
        time.sleep(10)
        print('Mining')
        block = asyncio.run(mine_block())

        logger.info(f'Added new block')
        blockchain.append(block)
        blockchain.flush()

        for block_hash in blockchain.chain:
            block = blockchain.get_block(block_hash)
            block.show()

        balance1 = blockchain.get_balance(Account(1))
        print(f'Balance 1: {balance1}')

        balance2 = blockchain.get_balance(Account(2))
        print(f'Balance 2: {balance2}')


mining_thread = threading.Thread(target=miner)

if __name__ == '__main__':
    node.run()
    try:
        miner()
    except KeyboardInterrupt:
        pass
    finally:
        print('Stoping node...')
        node.stop()
