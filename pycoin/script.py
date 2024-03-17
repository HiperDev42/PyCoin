from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


def calc_hash(data: bytes):
    return SHA256.new(data).digest()


class StackScript:
    txid: SHA256
    stack: list[bytes] = []
    script: list[str | bytes] = []
    pointer: int = 0

    def __init__(self, txid: SHA256, script: list[str], stack: list[bytes]) -> None:
        self.txid = txid
        self.stack = stack
        self.script = script
        self.pointer = 0

    def seek(self, position: int):
        if position > len(self.script):
            raise IndexError("Position out of range")
        self.pointer = position

    def eat(self):
        if self.pointer >= len(self.script):
            raise IndexError("Script ended unexpectedly")
        op = self.script[self.pointer]
        self.pointer += 1
        return op

    def run(self):
        while self.pointer < len(self.script):
            op = self.eat()
            if not isinstance(op, str) or op not in self.OP_CODES:
                raise ValueError("Invalid opcode")
            self.OP_CODES[op](self)

        self.op_verify()

    def op_dup(self):
        self.stack.append(self.stack[-1])

    def op_hash160(self):
        data = self.stack.pop()
        self.stack.append(calc_hash(data))

    def op_equal(self):
        d1 = self.stack.pop()
        d2 = self.stack.pop()
        result = b'\x01' if d1 == d2 else b'\x00'
        self.stack.append(result)

    def op_verify(self):
        d = self.stack.pop()
        assert d == b'\x01'

    def op_equalverify(self):
        self.op_equal()
        self.op_verify()

    def op_pushdata(self):
        data = self.eat()
        self.stack.append(data)

    def op_checksig(self):
        pub = RSA.import_key(self.stack.pop())
        sig = self.stack.pop()
        try:
            pkcs1_15.new(pub).verify(self.txid, sig)
        except ValueError:
            self.stack.append(b'\x00')
        else:
            self.stack.append(b'\x01')

    OP_CODES = {
        'OP_DUP': op_dup,
        'OP_HASH160': op_hash160,
        'OP_EQUALVERIFY': op_equalverify,
        'OP_PUSHDATA': op_pushdata,
        'OP_CHECKSIG': op_checksig
    }
