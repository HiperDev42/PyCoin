from blockchain import Tx
from . import utils

import json
import socket


class Peer:
    def __init__(self, ip='127.0.0.1', port=5500) -> None:
        self.ip = ip
        self.port = port

    def _connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.port))
        return sock

    def ping(self):
        peer_socket = self._connect()
        msg = utils.encode_message('ping')
        peer_socket.send(msg)

        response = utils.recv_message(peer_socket)
        print(response)

    def tx(self, tx: Tx):
        sock = self._connect()
        tx_bytes = json.dumps(tx.to_json()).encode()
        msg = utils.encode_message('tx', tx_bytes)
        sock.send(msg)

        response = utils.recv_message(sock)
        print(response)
