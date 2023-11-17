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
logger.setLevel(logging.DEBUG)


class Node:
    ip: str
    port: int
    _msg_header = struct.Struct('4s12sI4s')

    _commands = {}
    _threads: List[threading.Thread] = []
    _stop: threading.Event

    def __init__(self, ip='0.0.0.0', port=5500) -> None:
        self.ip = ip
        self.port = port
        self._stop = threading.Event()

    def _init_sock(self, max_connections):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(max_connections)

        return self.socket

    def command(self, name: str):
        def assign(action: Callable):
            self._commands[name] = action
            return action
        return assign

    def handler(self, conn: Connection):
        while not self._stop.is_set():
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
        while not self._stop.is_set():
            try:
                readable, _, _ = select.select([self.socket], [], [], 0.25)
                if self.socket in readable:
                    conn, addr = self.socket.accept()
                    connection = Connection(addr, socket=conn)
                    thread = threading.Thread(
                        target=self.handler, args=(connection,))
                    self._threads.append(thread)
                    thread.start()
            except Exception as e:
                print(e)

    def start(self, max_connections=10) -> None:
        self.socket = self._init_sock(max_connections)
        logger.info(f'Running node on port {self.port}')

        thread = threading.Thread(target=self._accept)
        self._threads.append(thread)
        thread.start()
        return thread

    def stop(self):
        self._stop.set()
        for thread in self._threads:
            thread.join()
        if self.socket:
            self.socket.close()
