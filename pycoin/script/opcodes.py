from typing import List

_opcode_instances: List['ScriptOp'] = []


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

    def __new__(cls, n: int) -> 'ScriptOp':
        try:
            return _opcode_instances[n]
        except IndexError:
            assert len(_opcode_instances) == n
            _opcode_instances.append(super().__new__(cls, n))
            return _opcode_instances[n]


# Populate opcode instance table
for n in range(0x100):
    ScriptOp(n)

# push value
OP_0 = ScriptOp(0x00)
OP_FALSE = OP_0
OP_PUSHDATA1 = ScriptOp(0x4c)
OP_PUSHDATA2 = ScriptOp(0x4d)
OP_PUSHDATA4 = ScriptOp(0x4e)
OP_1NEGATE = ScriptOp(0x4f)
OP_RESERVED = ScriptOp(0x50)
OP_1 = ScriptOp(0x51)
OP_TRUE = OP_1
OP_2 = ScriptOp(0x52)
OP_3 = ScriptOp(0x53)
OP_4 = ScriptOp(0x54)
OP_5 = ScriptOp(0x55)
OP_6 = ScriptOp(0x56)
OP_7 = ScriptOp(0x57)
OP_8 = ScriptOp(0x58)
OP_9 = ScriptOp(0x59)
OP_10 = ScriptOp(0x5a)
OP_11 = ScriptOp(0x5b)
OP_12 = ScriptOp(0x5c)
OP_13 = ScriptOp(0x5d)
OP_14 = ScriptOp(0x5e)
OP_15 = ScriptOp(0x5f)
OP_16 = ScriptOp(0x60)

# control
OP_NOP = ScriptOp(0x61)
OP_VER = ScriptOp(0x62)
OP_IF = ScriptOp(0x63)
OP_NOTIF = ScriptOp(0x64)
OP_VERIF = ScriptOp(0x65)
OP_VERNOTIF = ScriptOp(0x66)
OP_ELSE = ScriptOp(0x67)
OP_ENDIF = ScriptOp(0x68)
OP_VERIFY = ScriptOp(0x69)
OP_RETURN = ScriptOp(0x6a)

# stack ops
OP_TOALTSTACK = ScriptOp(0x6b)
OP_FROMALTSTACK = ScriptOp(0x6c)
OP_2DROP = ScriptOp(0x6d)
OP_2DUP = ScriptOp(0x6e)
OP_3DUP = ScriptOp(0x6f)
OP_2OVER = ScriptOp(0x70)
OP_2ROT = ScriptOp(0x71)
OP_2SWAP = ScriptOp(0x72)
OP_IFDUP = ScriptOp(0x73)
OP_DEPTH = ScriptOp(0x74)
OP_DROP = ScriptOp(0x75)
OP_DUP = ScriptOp(0x76)
OP_NIP = ScriptOp(0x77)
OP_OVER = ScriptOp(0x78)
OP_PICK = ScriptOp(0x79)
OP_ROLL = ScriptOp(0x7a)
OP_ROT = ScriptOp(0x7b)
OP_SWAP = ScriptOp(0x7c)
OP_TUCK = ScriptOp(0x7d)

# splice ops
OP_CAT = ScriptOp(0x7e)
OP_SUBSTR = ScriptOp(0x7f)
OP_LEFT = ScriptOp(0x80)
OP_RIGHT = ScriptOp(0x81)
OP_SIZE = ScriptOp(0x82)

# bit logic
OP_INVERT = ScriptOp(0x83)
OP_AND = ScriptOp(0x84)
OP_OR = ScriptOp(0x85)
OP_XOR = ScriptOp(0x86)
OP_EQUAL = ScriptOp(0x87)
OP_EQUALVERIFY = ScriptOp(0x88)
OP_RESERVED1 = ScriptOp(0x89)
OP_RESERVED2 = ScriptOp(0x8a)

# numeric
OP_1ADD = ScriptOp(0x8b)
OP_1SUB = ScriptOp(0x8c)
OP_2MUL = ScriptOp(0x8d)
OP_2DIV = ScriptOp(0x8e)
OP_NEGATE = ScriptOp(0x8f)
OP_ABS = ScriptOp(0x90)
OP_NOT = ScriptOp(0x91)
OP_0NOTEQUAL = ScriptOp(0x92)

OP_ADD = ScriptOp(0x93)
OP_SUB = ScriptOp(0x94)
OP_MUL = ScriptOp(0x95)
OP_DIV = ScriptOp(0x96)
OP_MOD = ScriptOp(0x97)
OP_LSHIFT = ScriptOp(0x98)
OP_RSHIFT = ScriptOp(0x99)

OP_BOOLAND = ScriptOp(0x9a)
OP_BOOLOR = ScriptOp(0x9b)
OP_NUMEQUAL = ScriptOp(0x9c)
OP_NUMEQUALVERIFY = ScriptOp(0x9d)
OP_NUMNOTEQUAL = ScriptOp(0x9e)
OP_LESSTHAN = ScriptOp(0x9f)
OP_GREATERTHAN = ScriptOp(0xa0)
OP_LESSTHANOREQUAL = ScriptOp(0xa1)
OP_GREATERTHANOREQUAL = ScriptOp(0xa2)
OP_MIN = ScriptOp(0xa3)
OP_MAX = ScriptOp(0xa4)

OP_WITHIN = ScriptOp(0xa5)

# crypto
OP_RIPEMD160 = ScriptOp(0xa6)
OP_SHA1 = ScriptOp(0xa7)
OP_SHA256 = ScriptOp(0xa8)
OP_HASH160 = ScriptOp(0xa9)
OP_HASH256 = ScriptOp(0xaa)
OP_CODESEPARATOR = ScriptOp(0xab)
OP_CHECKSIG = ScriptOp(0xac)
OP_CHECKSIGVERIFY = ScriptOp(0xad)
OP_CHECKMULTISIG = ScriptOp(0xae)
OP_CHECKMULTISIGVERIFY = ScriptOp(0xaf)

# expansion
OP_NOP1 = ScriptOp(0xb0)
OP_NOP2 = ScriptOp(0xb1)
OP_CHECKLOCKTIMEVERIFY = OP_NOP2
OP_NOP3 = ScriptOp(0xb2)
OP_CHECKSEQUENCEVERIFY = OP_NOP3
OP_NOP4 = ScriptOp(0xb3)
OP_NOP5 = ScriptOp(0xb4)
OP_NOP6 = ScriptOp(0xb5)
OP_NOP7 = ScriptOp(0xb6)
OP_NOP8 = ScriptOp(0xb7)
OP_NOP9 = ScriptOp(0xb8)
OP_NOP10 = ScriptOp(0xb9)

# Opcode added by BIP 342 (Tapscript)
OP_CHECKSIGADD = ScriptOp(0xba)

# template matching params
OP_SMALLINTEGER = ScriptOp(0xfa)
OP_PUBKEYS = ScriptOp(0xfb)
OP_PUBKEYHASH = ScriptOp(0xfd)
OP_PUBKEY = ScriptOp(0xfe)

OP_INVALIDOPCODE = ScriptOp(0xff)
