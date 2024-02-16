import pycoin.utils as utils
import json
from hashlib import sha256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


class Tx:
    sender: str
    receiver: str
    amount: int
    timestamp: int

    def __init__(self, sender: str, receiver: str, amount: int, timestamp: int) -> None:
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp

    def sign(self, key: RSA.RsaKey):
        sig_scheme = pkcs1_15.new(key)
        self.signature = sig_scheme.sign(self.hash)
        return self.signature

    def toJSON(self):
        return json.dumps(self, cls=utils.Encoder, sort_keys=True)

    @property
    def hash(self) -> bytes:
        return sha256(self.toJSON().encode()).digest()
