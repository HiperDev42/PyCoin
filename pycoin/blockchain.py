from hashlib import sha256
import json


class Block:
    previous_hash: bytes
    nonce: int

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    def get_hash(self) -> bytes:
        return sha256(self.toJSON().encode()).digest()


class Blockchain:
    def __init__(self) -> None:
        self.blocks = []

    def add_block(self, block: Block) -> None:
        self.blocks.append(block)
