from blockchain import Tx
from . import utils

from secrets import token_bytes
import json
import socket
import logging


logger = logging.getLogger(__name__)


class Peer:
    def __init__(self, ip='127.0.0.1', port=5500) -> None:
        self.ip = ip
        self.port = port

    def _connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.port))
        return sock

    def test_connection(self):
        logger.info('Testing connection...')
        try:
            return self.ping()
        except Exception as e:
            logger.error('Got exception when trying to connect')
            logger.error(e)
            return False

    def ping(self):
        try:
            peer_socket = self._connect()
            rand_bytes = token_bytes(64)
            msg = utils.encode_message('ping', rand_bytes)
            peer_socket.send(msg)

            response = utils.recv_message(peer_socket)
            if response[0] == 'pong' and response[1] == rand_bytes:
                return True
        finally:
            return False

    def tx(self, tx: Tx):
        sock = self._connect()
        tx_bytes = json.dumps(tx.to_json()).encode()
        msg = utils.encode_message('tx', tx_bytes)
        sock.send(msg)

        response = utils.recv_message(sock)
        return response[0] == 'ack'
