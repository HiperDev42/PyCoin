from collections.abc import Iterator
from typing import Generator, Tuple, Optional
from .opcodes import *


class ScriptInvalidError(Exception):
    ...


class Script(bytes):
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

    def __iter__(self) -> Iterator[int]:
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
