from Crypto.PublicKey import RSA
from typing import Generator, Iterable, Tuple, Type, Optional, Union
from .opcodes import *


ScriptElement_Type = Union[ScriptOp, int, bytes, bytearray]


class ScriptInvalidError(Exception):
    ...


class Script(bytes):
    @classmethod
    def __coerce_instance(cls, other: ScriptElement_Type) -> bytes:
        if isinstance(other, ScriptOp):
            other = bytes([other])
        elif isinstance(other, int):
            if 0 <= other <= 16:
                other = ScriptOp.encode_op_n(other)
            elif other == -1:
                other = bytes([OP_1NEGATE])
            else:
                raise NotImplementedError()
        elif isinstance(other, (bytes, bytearray)):
            other = ScriptOp.encode_op_pushdata(other)
        else:
            raise TypeError(
                "Unsupported type for script element: %s" % type(other))
        return other

    def __new__(cls, value: Type[ScriptElement_Type] = b'', *, name: Optional[str] = None) -> 'Script':
        if isinstance(value, (bytes, bytearray)):
            instance = super().__new__(cls, value)
        else:
            def coerce_iterable(iterable: Iterable[ScriptElement_Type]) -> Generator[bytes, None, None]:
                for instance in iterable:
                    yield cls.__coerce_instance(instance)

            # Annoyingly bytes.join() always
            # returns a bytes instance even when subclassed.
            instance = super().__new__(
                cls, b''.join(coerce_iterable(value)))
        if name is not None:
            if not isinstance(name, str):
                raise ValueError("name must be a string")
            instance._script_name = name
        return instance

    def raw_iter(self) -> Generator[Tuple[ScriptOp, Optional[bytes], int], None, None]:
        i = 0
        while i < len(self):
            sop_idx = i
            opcode = self[i]
            i += 1

            if opcode > OP_PUSHDATA4:
                yield (ScriptOp(opcode), None, sop_idx)
            else:
                datasize = None
                pushdata_type = None
                if opcode < OP_PUSHDATA1:
                    pushdata_type = 'PUSHDATA(%d)' % opcode
                    datasize = opcode
                elif opcode == OP_PUSHDATA1:
                    pushdata_type = 'PUSHDATA1'
                    if i >= len(self):
                        raise ScriptInvalidError(
                            'PUSHDATA1: missing data length')
                    datasize = self[i]
                    i += 1
                elif opcode == OP_PUSHDATA2:
                    pushdata_type = 'PUSHDATA2'
                    if i + 1 >= len(self):
                        raise ScriptInvalidError(
                            'PUSHDATA2: missing data length')
                    datasize = int.from_bytes(self[i:i+2], 'big')
                    i += 2
                elif opcode == OP_PUSHDATA4:
                    pushdata_type = 'PUSHDATA4'
                    if i + 3 >= len(self):
                        raise ScriptInvalidError(
                            'PUSHDATA4: missing data length')
                    datasize = int.from_bytes(self[i:i+4], 'big')
                    i += 4
                else:
                    assert False  # should never happen

                data = bytes(self[i:i+datasize])

                # check for truncation
                if len(data) < datasize:
                    raise ScriptInvalidError(
                        'Script truncated: %s' % pushdata_type, data)

                i += datasize

                yield (ScriptOp(opcode), data, sop_idx)

    def __iter__(self) -> Iterable[int]:
        for (opcode, data, sop_idx) in self.raw_iter():
            if opcode == OP_0:
                yield 0
            elif data is not None:
                yield data
            else:
                if opcode.is_small_int():
                    yield opcode.decode_op_n()
                else:
                    yield opcode

    def is_p2pkh(self) -> bool:
        """Checks if the script is a pay-to-pubkey-hash script."""
        return (len(self)) == 25 \
            and self[0] == OP_DUP \
            and self[1] == OP_HASH160 \
            and self[2] == 0x14 \
            and self[23] == OP_EQUALVERIFY \
            and self[24] == OP_CHECKSIG


def p2pkh_script(pubkey_hash: bytes) -> Script:
    assert len(pubkey_hash) == 0x14
    return Script([OP_DUP, OP_HASH160, pubkey_hash, OP_EQUALVERIFY, OP_CHECKSIG])
