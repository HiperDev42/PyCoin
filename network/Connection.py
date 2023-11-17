from . import Address, utils
import json
import socket


class Connection:
    _address: Address
    _socket: socket.socket

    def __init__(self, address: Address, socket: socket.socket = None) -> None:
        self._address = address
        self._socket = socket

    @property
    def address(self) -> Address:
        return self._address

    def connect(self) -> bool:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(self._address.addr)
        return True

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        self.close()

    def send_command(self, command: str, data: any) -> None:
        if isinstance(data, str):
            payload = data.encode()
        elif isinstance(data, bytes) or isinstance(data, bytearray):
            payload = bytes(data)
        elif isinstance(data, list) or isinstance(data, dict) or isinstance(data, set):
            payload = json.dumps(data).encode()
        else:
            try:
                payload_json = data.to_json()
                payload = json.dumps(payload_json).encode()
            except:
                raise ValueError(f'Cannot encode data type {type(data)}')

        message_bytes = utils.encode_message(command, payload)
        self._socket.send(message_bytes)

    def recv_command(self):
        command, data = utils.recv_message(self._socket)
        return command, data

    def close(self):
        return self._socket.close()
