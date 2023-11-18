from blockchain import *
from random import randint
from typing import List, Tuple, Set

import json
import logging
import miner
import network
import traceback


MINE_INTERVAL = 10

logger = logging.getLogger(__name__)

miner.reward_account = Account(1)
known_peers: Set[network.Peer] = set()

node = network.Node()


def submit_addrs(addrs):
    for addr in addrs:
        peer = network.Peer(addr)
        known_peers.add(peer)
    logger.debug(known_peers)


@node.command('ping')
def ping(ctx) -> Tuple[str, bytes]:
    return 'pong', ctx['data']


@node.command('addr')
def addr(ctx):
    addrs = []
    for addr_json in json.loads(ctx['data']):
        addr = network.Address.from_json(addr_json)
        addrs.append(addr)
    submit_addrs(addrs)
    return 'ack', b''


@node.command('tx')
def tx(ctx) -> Tuple[str, bytes]:
    tx_json = json.loads(ctx['data'].decode())
    logger.debug(tx_json)
    tx = Tx.from_json(tx_json)

    miner.submit_tx(tx)

    return 'ack', b''


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        miner.start()
        node.start()
        node.wait()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.fatal('Fatal error')
        logger.fatal(traceback.format_exc())
        logger.fatal(e)
    finally:
        logger.info('Stopping...')
        miner.stop()
        node.stop()
