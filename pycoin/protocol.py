from dataclasses import dataclass
from hashlib import sha256
import struct
import socket

_msg_header = struct.Struct('4s12sI4s')


@dataclass
class MessageHeader:
    magic: bytes
    command: str
    size: int
    checksum: bytes

    def pack(self):
        return _msg_header.pack(
            self.magic,
            self.command.encode('ascii').rjust(12, b'\x00'),
            self.size,
            self.checksum
        )


@dataclass
class Message:
    header: MessageHeader
    payload: bytes


def read_header(conn: socket.socket) -> MessageHeader:
    header_bytes = conn.recv(_msg_header.size)
    magic, command_encoded, size, checksum = _msg_header.unpack(header_bytes)

    command = command_encoded.strip(b'\x00').decode('ascii')
    header = MessageHeader(magic, command, size, checksum)

    return header


def get_checksum(payload: bytes) -> bytes:
    return sha256(payload).digest()[:4]


def read_msg(conn: socket.socket) -> Message:
    header = read_header(conn)
    payload = conn.recv(header.size)

    if len(payload) != header.size:
        raise Exception("Invalid payload size")
    checksum = get_checksum(payload)
    if checksum != header.checksum:
        raise Exception("Invalid checksum")

    msg = Message(header, payload)

    return msg


def pack_message(payload: bytes) -> Message:
    header = MessageHeader(
        magic=b"\x00\x00\x00\x00",
        command="",
        size=len(payload),
        checksum=b"\x00\x00\x00\x00",
    )
    return Message(header, payload)


class ConnectionInterface:
    def __init__(self, connection: socket.socket | None = None, address: tuple | None = None) -> None:
        self.socket = connection
        self.address = address

    def connect(self, address: tuple) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        self.socket = sock

    def recv(self) -> Message:
        return read_msg(self.socket)

    def send(self, command: str, payload: bytes) -> bool:
        header = MessageHeader(
            b'\x00\x00\x00\x00',
            command,
            len(payload),
            get_checksum(payload),
        )

        header_bytes = header.pack()
        self.socket.sendall(header_bytes + payload)
        return True
