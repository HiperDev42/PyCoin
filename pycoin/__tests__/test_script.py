from pycoin.script import StackScript
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from random import randbytes


def test_should_verify_signature():
    txid = SHA256.new(randbytes(32))
    keys = RSA.generate(2048)
    pub_bytes = keys.public_key().export_key('DER')
    pub_hash = SHA256.new(pub_bytes).digest()
    signature = pkcs1_15.new(keys).sign(txid)

    script = StackScript(txid)

    script.push(signature)
    script.push(pub_bytes)

    script.op_dup()
    script.op_hash160()
    script.push(pub_hash)
    script.op_equalverify()
    script.op_checksig()
