import pycoin
import pycoin.wallet
from time import time


def test_blockchain():
    blockchain = pycoin.Blockchain()
    alice_key = pycoin.wallet.generate_keys()
    bob_key = pycoin.wallet.generate_keys()

    tx = pycoin.Tx(alice_key.public_key(),
                   bob_key.public_key(), 10, int(time()))
    signature = tx.sign(alice_key)

    assert tx.verifySignature(signature)
