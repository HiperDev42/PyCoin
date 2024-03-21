from pycoin.script import StackScript
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from random import randbytes


def test_should_verify_signature():
    txid = SHA256.new(randbytes(32)).digest()
    keys = RSA.generate(2048)
    pub_bytes = keys.public_key().export_key('DER')
    pub_hash = SHA256.new(pub_bytes).hexdigest()
    signature = pkcs1_15.new(keys).sign(SHA256.new(txid))

    stack = [signature, pub_bytes]
    script = ['OP_DUP', 'OP_HASH160', 'OP_PUSHDATA', pub_hash, 'OP_EQUALVERIFY',
              'OP_CHECKSIG']
    stackScript = StackScript(txid, script, stack)
    stackScript.run()
