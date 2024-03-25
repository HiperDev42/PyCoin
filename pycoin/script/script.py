from collections.abc import Iterator
from typing import Generator, Tuple, Optional


class ScriptInvalidError(Exception):
    ...


class ScriptOp(int):
    def decode_op_n(self) -> int:
        if self == 0:
            return 0
        if not (0x51 <= self <= 0x60):
            raise ValueError("Opcode %r os not an OP_N" % self)

        return int(self - 0x50)

    def is_small_int(self) -> bool:
        if 0x51 <= self <= 0x60 or self == 0:
            return True
        else:
            return False


class Script(bytes):
    ...

    def __raw_iter(self) -> Generator[Tuple[ScriptOp, Optional[bytes], int], None, None]:
        i = 0
        while i < len(self):
            sop_idx = i
            opcode = self[i]
            i += 1

            if opcode > 0x4E:
                yield (ScriptOp(opcode), None, sop_idx)
            else:
                datasize = None
                pushdata_type = None
                if opcode < 0x4C:
                    pushdata_type = 'PUSHDATA(%d)' % opcode
                    datasize = opcode
                elif opcode == 0x4C:
                    pushdata_type = 'PUSHDATA1'
                    if i >= len(self):
                        raise ScriptInvalidError(
                            'PUSHDATA1: missing data length')
                    datasize = self[i]
                    i += 1
                elif opcode == 0x4D:
                    pushdata_type = 'PUSHDATA2'
                    if i + 1 >= len(self):
                        raise ScriptInvalidError(
                            'PUSHDATA2: missing data length')
                    datasize = int.from_bytes(self[i:i+2], 'big')
                    i += 2
                elif opcode == 0x4E:
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
        for (opcode, data, sop_idx) in self.__raw_iter():
            if opcode == 0:
                yield 0
            elif data is not None:
                yield data
            else:
                if opcode.is_small_int():
                    yield opcode.decode_op_n()
                else:
                    yield opcode
