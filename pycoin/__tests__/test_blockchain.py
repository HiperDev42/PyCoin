import pycoin
import pycoin.wallet


def createIfNotExists(key_filename: str) -> pycoin.wallet.Wallet:
    try:
        return pycoin.wallet.Wallet(key_filename)
    except FileNotFoundError:
        return pycoin.wallet.create_wallet(key_filename)


def test_blockchain():
    alice = createIfNotExists('alice.pem')
    bob = createIfNotExists('bob.pem')

    blockchain = pycoin.Blockchain()

    tx = alice.create_tx(receiver=bob.public_key, amount=10)

    assert tx.validateSignature()
    assert blockchain.submitTx(tx)
    blockchain.minePendingTxs(alice.public_key)

    blockchain.save()
