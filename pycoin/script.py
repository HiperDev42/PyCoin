from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


def calc_hash(data: bytes):
    return SHA256.new(data).digest()


class StackScript:
    stack: list[bytes] = []

    def __init__(self, txid: bytes) -> None:
        self.txid = txid

    def pop(self):
        return self.stack.pop()

    def push(self, data: bytes):
        return self.stack.append(data)

    def op_dup(self):
        self.push(self.stack[-1])

    def op_hash160(self):
        data = self.pop()
        self.push(calc_hash(data))

    def op_equalverify(self):
        d1 = self.pop()
        d2 = self.pop()
        assert d1 == d2

    def op_checksig(self):
        pub = RSA.import_key(self.pop())
        sig = self.pop()
        pkcs1_15.new(pub).verify(self.txid, sig)
