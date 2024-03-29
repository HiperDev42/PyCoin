import struct
from typing import Tuple
from dataclasses import dataclass


class MessageFormatError(Exception):
    ...


class UnknownMessageError(Exception):
    ...


@dataclass
class MessageHeader:
    magic: bytes
    command: str
    length: int
    checksum: bytes


class Message:
    HEADER_STRUCT = struct.Struct('4s12sI4s')

    @staticmethod
    def decode_header(header: bytes) -> MessageHeader:
        header_struct = Message.HEADER_STRUCT
        header: Tuple[bytes, bytes, int, bytes]
        if len(header) < header_struct.size:
            return None

        header = header_struct.unpack_from(header)

        return MessageHeader(
            magic=header[0],
            command=header[1].strip(b'\x00').decode(),
            length=header[2],
            checksum=header[3]
        )

    @classmethod
    def parse(cls, data: bytes) -> 'Message':
        pass
