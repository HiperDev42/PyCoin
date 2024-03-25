from Crypto.Hash import RIPEMD160, SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from pycoin.script.script import Script
from pycoin.script.scripteval import Eval
from pycoin.script.opcodes import *
from pycoin.tx import Tx, TxIn, TxOut


def HASH160(data: bytes):
    return RIPEMD160.new(SHA256.new(data).digest()).digest()


def get_txid_hash(tx: Tx):
    txid = tx.hash.digest()
    return SHA256.new(txid)


def test_p2pkh_eval():
    tx = Tx(tx_ins=[], tx_outs=[])

    keyPair = RSA.generate(2048)
    pubkey_bytes = keyPair.public_key().export_key('DER')
    pubkey_hash = HASH160(pubkey_bytes)
    assert len(pubkey_hash) == 0x14

    txid_hash = get_txid_hash(tx)
    signature = pkcs1_15.new(keyPair).sign(txid_hash)
    script = Script()

    stack = [signature, pubkey_bytes]

    result = Eval(stack, script, tx)
