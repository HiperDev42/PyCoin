import pycoin.utils as utils
from pycoin.logs import logger
import json
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class TxOut:
    amount: int
    script: list[str]


@dataclass
class TxIn:
    txid: bytes
    outIndex: int
    scriptSig: list[bytes]


@dataclass
class Tx:
    tx_ins: list[TxIn]
    tx_outs: list[TxOut]

    def toJSON(self):
        return json.dumps(self, cls=utils.Encoder, sort_keys=True)

    def __hash(self):
        return SHA256.new(self.toJSON().encode())

    @property
    def hash(self):
        return self.__hash()

    def isCoinbase(self):
        return len(self.tx_ins) == 1 and self.tx_ins[0].txid == b'\x00' * 32
