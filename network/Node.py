import asyncio
import socket
import struct
from . import utils
import logging
from typing import Callable
import threading


MAGIC = b'PYC1'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Node:
    ip: str
    port: int
    _msg_header = struct.Struct('4s12sI4s')

    _commands = {}
    _threads = []
    _stop: threading.Event

    def __init__(self, ip='0.0.0.0', port=5500) -> None:
        self.ip = ip
        self.port = port
        self._stop = threading.Event()

    def _init_sock(self, max_connections):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, self.port))
        sock.listen(max_connections)

        return sock

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
                response_command, response_payload = action(payload)

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

    def run(self, max_connections=10) -> None:
        try:
            node_socket = self._init_sock(max_connections)
            print(f'Running node on port {self.port}')

            while True:
                conn, addr = node_socket.accept()
                thread = threading.Thread(
                    target=self.handler, args=(conn, addr))
                self._threads.append(thread)
                thread.start()
        except KeyboardInterrupt:
            print('Interrupting')
            self._stop.set()
