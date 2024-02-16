import pycoin
import pycoin.wallet
from time import time


def test_blockchain():
    blockchain = pycoin.Blockchain()
    keys = pycoin.wallet.generate_keys()

    tx = pycoin.Tx("alice", "bob", 10, int(time()))
    signature = tx.sign(keys)

    assert tx.verifySignature(signature, keys.public_key())
