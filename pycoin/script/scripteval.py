from Crypto.Hash import RIPEMD160, SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from typing import Callable, Dict, List, TYPE_CHECKING
from dataclasses import dataclass
from .script import Script
from .opcodes import *
from pycoin.utils import hash160
if TYPE_CHECKING:
    from pycoin.tx import Tx

_opcode_evals: Dict[ScriptOp, Callable] = {}


class EvalScriptError(Exception):
    pass


@dataclass
class EvalState:
    stack: List[bytes]
    tx: 'Tx'


def register(opcode: ScriptOp):
    def wrapper(func: Callable):
        _opcode_evals[opcode] = func
        return func
    return wrapper


@register(OP_DUP)
def eval_OP_DUP(state: EvalState):
    val = state.stack[-1]
    state.stack.append(val)


@register(OP_HASH160)
def eval_OP_HASH160(state: EvalState):
    value = state.stack.pop()
    hashed = RIPEMD160.new(SHA256.new(value).digest()).digest()
    state.stack.append(hashed)


@register(OP_EQUAL)
def eval_OP_EQUAL(state: EvalState):
    d1 = state.stack.pop()
    d2 = state.stack.pop()
    result = b'\x01' if d1 == d2 else b'\x00'
    state.stack.append(result)


@register(OP_VERIFY)
def eval_OP_VERIFY(state: EvalState):
    d = state.stack.pop()
    assert d == b'\x01'


@register(OP_EQUALVERIFY)
def eval_OP_EQUALVERIFY(state: EvalState):
    eval_OP_EQUAL(state)
    eval_OP_VERIFY(state)


@register(OP_CHECKSIG)
def eval_OP_CHECKSIG(state: EvalState):
    pubkey = RSA.import_key(state.stack.pop())
    sig = state.stack.pop()
    txid_hash = SHA256.new(state.tx.hash.digest())
    try:
        pkcs1_15.new(pubkey).verify(txid_hash, sig)
    except ValueError:
        state.stack.append(b'\x00')
    else:
        state.stack.append(b'\x01')


def Eval(stack: List[bytes], scriptIn: Script, tx: 'Tx'):
    state = EvalState(stack=stack, tx=tx)
    for (opcode, data, sop_idx) in scriptIn.raw_iter():
        if opcode in DISABLED_OPCODES:
            raise EvalScriptError("trying to execute a disabled opcode")

        if opcode <= OP_PUSHDATA4:
            assert data is not None
            stack.append(data)
            continue

        action = _opcode_evals[opcode]

        if not action:
            raise EvalScriptError("unsupported opcode 0x%x" % opcode)

        action(state)

    return state
