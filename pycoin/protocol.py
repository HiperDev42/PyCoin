from dataclasses import dataclass
from hashlib import sha256
import struct
import socket

_msg_header = struct.Struct('4s12sI4s')


def get_checksum(payload: bytes) -> bytes:
    return sha256(payload).digest()[:4]


@dataclass
class MessageHeader:
    magic: bytes
    command: str
    size: int
    checksum: bytes

    @staticmethod
    def unpack(data: bytes):
        magic, command_encoded, size, checksum = _msg_header.unpack_from(data)
        command = bytes(command_encoded).strip(b'\x00').decode('ascii')
        return MessageHeader(magic, command, size, checksum)

    def pack(self):
        return _msg_header.pack(
            self.magic,
            self.command.encode('ascii').rjust(12, b'\x00'),
            self.size,
            self.checksum
        )


@dataclass
class Message:
    command: MessageHeader
    payload: bytes
    magic: bytes = b"\x00\x00\x00\x00"

    @property
    def size(self):
        return len(self.payload)

    @property
    def checksum(self):
        return get_checksum(self.payload)

    @property
    def header(self):
        return MessageHeader(self.magic, self.command, self.size, self.checksum)

    @staticmethod
    def unpack(data: bytes):
        header = MessageHeader.unpack(data)
        offset = _msg_header.size
        payload = data[offset:offset+header.size]
        if len(payload) != header.size:
            raise Exception("Invalid payload size")
        checksum = get_checksum(payload)
        if checksum != header.checksum:
            raise Exception("Invalid checksum")
        return Message(magic=header.magic, command=header.command, payload=payload)

    def pack(self):
        return self.header.pack() + self.payload


def _read_header(conn: socket.socket) -> MessageHeader:
    header_bytes = conn.recv(_msg_header.size)
    magic, command_encoded, size, checksum = _msg_header.unpack(header_bytes)

    command = command_encoded.strip(b'\x00').decode('ascii')
    header = MessageHeader(magic, command, size, checksum)

    return header


def _read_msg(conn: socket.socket) -> Message:
    header = _read_header(conn)
    payload = conn.recv(header.size)

    if len(payload) != header.size:
        raise Exception("Invalid payload size")
    checksum = get_checksum(payload)
    if checksum != header.checksum:
        raise Exception("Invalid checksum")

    msg = Message(header.command, payload, magic=header.magic)

    return msg


def _send_message(conn: socket.socket, msg: Message) -> None:
    conn.sendall(msg.pack())


class ConnectionInterface:
    def __init__(self, connection: socket.socket | None = None, address: tuple | None = None) -> None:
        self.socket = connection
        self.address = address

    def recv(self) -> Message:
        return _read_msg(self.socket)

    def send(self, msg: Message) -> bool:
        try:
            _send_message(self.socket, msg)
            return True
        except:
            return False

    def request(self, command: str, data: bytes = b'') -> Message:
        request = Message(command=command, payload=data)
        success = self.send(request)
        if not success:
            raise Exception("Failed to send request")
        response = self.recv()
        return response


def connect(address: tuple) -> ConnectionInterface:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    return ConnectionInterface(sock, address)
