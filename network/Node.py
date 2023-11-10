import asyncio
import select
import socket
import struct
from . import utils
import logging
from typing import Callable, List
import threading


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

    def handler(self, conn, addr):
        print('New task started')
        while not self._stop.is_set():
            try:
                command, payload = utils.recv_message(conn)
                if not command:
                    break

                action = self._commands.get(command)
                ctx = {
                    'data': payload,
                    'address': addr
                }
                response_command, response_payload = action(ctx)

                response_bytes = utils.encode_message(
                    response_command, response_payload)

                conn.send(response_bytes)
            except Exception as e:
                conn.close()
                print('Error')
                raise e
                break

        conn.close()
        print(f'End of connection {addr}')

    def _accept(self):
        while not self._stop.is_set():
            try:
                readable, _, _ = select.select([self.socket], [], [], 0.25)
                if self.socket in readable:
                    conn, addr = self.socket.accept()
                    thread = threading.Thread(
                        target=self.handler, args=(conn, addr))
                    self._threads.append(thread)
                    thread.start()
            except Exception as e:
                print(e)

    def start(self, max_connections=10) -> None:
        self.socket = self._init_sock(max_connections)
        print(f'Running node on port {self.port}')

        thread = threading.Thread(target=self._accept)
        self._threads.append(thread)
        thread.start()
        return thread

    def stop(self):
        self._stop.set()
        self.socket.close()
        print('threads', self._threads)
        for thread in self._threads:
            print('Joining thread', thread)
            thread.join()
