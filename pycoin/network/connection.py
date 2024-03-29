import asyncore
import socket
import logging
from pycoin.protocol import Message
from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from .node import BaseNode


BLOCK_SIZE = 4

logger = logging.getLogger('pycoin')


class Connection(asyncore.dispatcher):
    def __init__(self, address: Tuple[str, int], sock: socket.socket, node: 'BaseNode') -> None:
        self.node = node
        self._address = address

        self._rx_buffer = bytearray()

        if sock:
            asyncore.dispatcher.__init__(self, sock, map=node._peers)

            self._incoming = True
        else:
            asyncore.dispatcher.__init__(self, map=node._peers)

            try:
                self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connect(self._address)
            except Exception as e:
                self.handle_close()
                raise e

            self._incoming = False

    def handle_read(self) -> None:
        try:
            chunk = self.recv(BLOCK_SIZE)
        except Exception as e:
            chunk = ''

        if not chunk:
            self.handle_close()
            return

        logger.debug('Received {} bytes'.format(chunk))

        self._rx_buffer += chunk

        header = Message.decode_header(self._rx_buffer)
        if not header or header.length + 24 > len(self._rx_buffer):
            return

        payload = self._rx_buffer[:header.length + 24]
        del self._rx_buffer[:header.length + 24]

        try:
            message = Message.parse(payload)
            logger.info(message)
        except Exception as e:
            logger.exception(e)
