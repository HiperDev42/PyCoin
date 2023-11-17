from blockchain import Tx
from . import utils
from .Address import Address
from .Connection import Connection

from secrets import token_bytes
from typing import List
import json
import socket
import logging


logger = logging.getLogger(__name__)


class Commands:
    PING = 'ping'
    PONG = 'pong'
    GET_ADDRESS = 'getaddr'
    VERSION = 'version'


class Peer:
    def __init__(self, ip='127.0.0.1', port=5500, version=1) -> None:
        self._address = Address(ip, port)
        self.version = version

    @property
    def address(self) -> Address:
        return self._address

    def _connect(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self._address.addr)
        return sock

    def _send(self, sock: socket.socket, command: str, payload) -> int:
        if type(payload) is str:
            payload = payload.encode()
        message = utils.encode_message(command, payload)
        sent = sock.send(message)
        return sent

    def _send_version(self) -> bool:
        with self._connect() as sock:
            version_json = {
                'version': self.version,
            }

            self._send(sock, Commands.VERSION, json.dumps(version_json))
            response_cmd, data = utils.recv_message(sock)
            if response_cmd == 'verack':
                return True
            return False

    def test_connection(self) -> bool:
        logger.info('Testing connection...')
        try:
            x = self.ping()
            return x
        except Exception as e:
            logger.error('Got exception when trying to connect')
            logger.error(e)
            return False

    def ping(self):
        try:
            with Connection(self.address) as conn:
                rand_bytes = token_bytes(64)
                conn.send_command(Commands.PING, rand_bytes)

                response = conn.recv_command()
                if response[0] == Commands.PONG and response[1] == rand_bytes:
                    return True
                logger.debug('Recieved unexpected response')
                logger.debug(response)
        except Exception as e:
            logger.error('Got error')
            logger.error(e)
            return False
        finally:
            logger.debug('FINALLY')
        return False

    def get_address(self) -> List[Address]:
        try:
            peer_socket = self._connect()
            self._send(peer_socket, Commands.GET_ADDRESS, b'')
            response_cmd, data = utils.recv_message(peer_socket)
            raw_json = json.loads(data.decode())
            addrs = [Address.from_json(addr_json) for addr_json in raw_json]
            return addrs
        except:
            return []

    def tx(self, tx: Tx):
        sock = self._connect()
        tx_bytes = json.dumps(tx.to_json()).encode()
        msg = utils.encode_message('tx', tx_bytes)
        sock.send(msg)

        response = utils.recv_message(sock)
        return response[0] == 'ack'

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Peer):
            raise ValueError(f'Expected Peer, got {type(__value)}')
        return self.address == __value.address
