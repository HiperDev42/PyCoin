from .connection import Connection
from typing import Dict, Tuple
import asyncore
import socket
import logging

logger = logging.getLogger('pycoin')


class BaseNode(asyncore.dispatcher):
    _peers: Dict[int, Connection] = {}

    def __init__(self, address: Tuple[str, int]) -> None:
        asyncore.dispatcher.__init__(self, map=self._peers)
        self._address = address

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(self._address)
        self.listen(5)

    def serve_forever(self) -> None:
        try:
            asyncore.loop(5, map=self._map)
        except KeyboardInterrupt:
            pass
        finally:
            self.handle_close()

    def handle_accept(self) -> None:
        pair = self.accept()
        if not pair:
            return

        (sock, address) = pair
        logger.info("Incoming connection from %s" % repr(address))
        Connection(address=address, sock=sock, node=self)
        logger.info(self._peers)
