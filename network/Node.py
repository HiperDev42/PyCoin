from . import utils
from .Connection import Connection
from typing import Callable, List

import logging
import select
import socket
import struct
import threading
import traceback


MAGIC = b'PYC1'
logger = logging.getLogger(__name__)


class Node:
    ip: str
    port: int
    _msg_header = struct.Struct('4s12sI4s')

    _commands = {}
    _accept_thread: threading.Thread = None
    _threads: List[threading.Thread] = []
    _kill_event: threading.Event()
    _socket: socket.socket = None

    def __init__(self, ip='0.0.0.0', port=5500) -> None:
        self.ip = ip
        self.port = port
        self._kill_event: threading.Event = threading.Event()

    def _init_sock(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.ip, self.port))
        self._socket.listen()

        return self._socket

    def command(self, name: str):
        def assign(action: Callable):
            self._commands[name] = action
            return action
        return assign

    def handler(self, conn: Connection):
        while not self._kill_event.is_set():
            try:
                command, payload = conn.recv_command()
                if not command:
                    break

                logger.debug(f'Recieved command ({command}): {payload}')

                action = self._commands.get(command)
                ctx = {
                    'data': payload,
                    'address': conn.address
                }

                try:
                    response_command, response_payload = action(ctx)
                    conn.send_command(response_command, response_payload)
                except Exception:
                    logger.critical('Got unexpected error')
                    logger.error(traceback.format_exc())

                    conn.send_command('reject', b'Internal server error')

            except Exception as e:
                conn.close()
                logger.fatal('Error')
                raise e

        conn.close()

    def _accept(self):
        while not self._kill_event.is_set():
            readable, _, _ = select.select([self._socket], [], [], 0.25)
            if self._socket in readable:
                conn, addr = self._socket.accept()
                connection = Connection(addr, socket=conn)
                thread = threading.Thread(
                    target=self.handler, args=(connection,))
                self._threads.append(thread)
                thread.start()

    def start(self) -> None:
        self._kill_event.clear()
        self._socket = self._init_sock()

        self._accept_thread = threading.Thread(target=self._accept)
        self._accept_thread.start()

        logger.info(f'Running node on address ({(self.ip, self.port)})')

    def stop(self):
        self._kill_event.set()
        for thread in self._threads:
            thread.join()

        if self._accept_thread:
            self._accept_thread.join()

        if self._socket:
            self._socket.close()
        logger.debug('Node stopped')
