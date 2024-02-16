import pycoin
import pycoin.wallet
from time import time


def test_blockchain():
    blockchain = pycoin.Blockchain()
    alice_key = pycoin.wallet.generate_keys()
    bob_key = pycoin.wallet.generate_keys()

    tx = pycoin.Tx(alice_key.public_key(),
                   bob_key.public_key(), 10, int(time()))
    tx.sign(alice_key)

    assert tx.validateSignature()
    assert blockchain.submitTx(tx)
    blockchain.minePendingTxs(alice_key.public_key())

    blockchain.save()
