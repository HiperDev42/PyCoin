import pycoin.utils as utils
import json
from Crypto.Hash import SHA256
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
        signature = sig_scheme.sign(self.__hash())
        return signature

    def verifySignature(self, signature: bytes, key: RSA.RsaKey) -> bool:
        sig_scheme = pkcs1_15.new(key)
        try:
            sig_scheme.verify(self.__hash(), signature)
            return True
        except ValueError:
            return False

    def toJSON(self):
        return json.dumps(self, cls=utils.Encoder, sort_keys=True)

    def __hash(self):
        return SHA256.new(self.toJSON().encode())

    @property
    def hash(self) -> bytes:
        return self.__hash().digest()
