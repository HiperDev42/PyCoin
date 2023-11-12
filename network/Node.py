import select
import socket
import struct
from . import utils
import logging
from typing import Callable, List
import threading
from .Connection import Connection


MAGIC = b'PYC1'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Node:
    ip: str
    port: int
    _msg_header = struct.Struct('4s12sI4s')

    _commands = {}
    _accept_thread: threading.Thread
    _threads: List[threading.Thread] = []
    _kill_event: threading.Event()

    def __init__(self, ip='0.0.0.0', port=5500) -> None:
        self.ip = ip
        self.port = port
        self._kill_event: threading.Event = threading.Event()

    def _init_sock(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip, self.port))
        self.socket.listen()

        return self.socket

    def command(self, name: str):
        def assign(action: Callable):
            self._commands[name] = action
            return action
        return assign

    def handler(self, conn: Connection):
        print('New task started')
        while not self._kill_event.is_set():
            try:
                command, payload = conn.recv_command()
                if not command:
                    break

                action = self._commands.get(command)
                ctx = {
                    'data': payload,
                    'address': conn.address
                }
                response_command, response_payload = action(ctx)

                conn.send_command(response_command, response_payload)
            except Exception as e:
                conn.close()
                logger.fatal('Error')
                raise e

        conn.close()
        print(f'End of connection {conn.address}')

    def _accept(self):
        while not self._kill_event.is_set():
            try:
                readable, _, _ = select.select([self.socket], [], [], 0.25)
                if self.socket in readable:
                    conn, addr = self.socket.accept()
                    connection = Connection(addr, socket=conn)
                    thread = threading.Thread(
                        target=self.handler, args=connection)
                    self._threads.append(thread)
                    thread.start()
            except Exception as e:
                print(e)

    def start(self) -> None:
        self._kill_event.clear()
        self.socket = self._init_sock()

        self._accept_thread = threading.Thread(target=self._accept)
        self._accept_thread.start()

        logger.info(f'Running node on address ({(self.ip, self.port)})')

    def stop(self):
        self._kill_event.set()
        for thread in self._threads:
            thread.join()
        self._accept_thread.join()
        self.socket.close()
        logger.debug('Node stopped')
