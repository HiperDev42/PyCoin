from Crypto.PublicKey import RSA
from pycoin.tx import Tx
from time import time
import os


class Wallet:
    key_filename: str

    def __init__(self, key_filename: str):
        if not os.path.isfile(key_filename):
            raise FileNotFoundError(f"Key file not found: {key_filename}")

        self.key_filename = key_filename

    def __read_key(self) -> RSA.RsaKey:
        key_bytes = None
        with open(self.key_filename, 'r') as f:
            key_bytes = f.read()
        key = RSA.import_key(key_bytes)
        return key

    @property
    def public_key(self) -> RSA.RsaKey:
        return self.__read_key().public_key()

    def create_tx(self, receiver: RSA.RsaKey, amount: int) -> Tx:
        private_key = self.__read_key()
        public_key = private_key.public_key()
        tx = Tx(public_key, receiver, amount, timestamp=int(time()))
        tx.sign(private_key)
        return tx


def create_wallet(key_filename: str) -> Wallet:
    key = RSA.generate(2048)
    with open(key_filename, 'wb') as f:
        f.write(key.export_key('PEM'))
    return Wallet(key_filename)
