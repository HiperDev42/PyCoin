from hashlib import sha256
import struct
import socket

MAGIC = b'PYC1'
_msg_header = struct.Struct('4s12sI4s')


def get_checksum(payload: bytes):
    return sha256(payload).digest()[:4]


def check_sum(payload: bytes, sum: bytes):
    payload_hash = sha256(payload).digest()
    return payload_hash[:4] == sum


def encode_message(command: str, payload: bytes = b''):
    command_encoded = command.encode().ljust(12, b'\x00')
    checksum = get_checksum(payload)
    length = len(payload)
    header_bytes = _msg_header.pack(
        MAGIC, command_encoded, length, checksum)
    return header_bytes + payload


def recv_message(connection: socket.socket):
    header_bytes = connection.recv(_msg_header.size)
    if len(header_bytes) != _msg_header.size:
        return (False, header_bytes)
    header = _msg_header.unpack(header_bytes)
    magic, command_raw, length, checksum = header
    command = command_raw.rstrip(b'\x00').decode()

    if magic != MAGIC:
        raise Exception('Invalid Magic')

    payload = connection.recv(length)
    if not check_sum(payload, checksum):
        raise Exception('Invalid Checksum')

    return (command, payload)
