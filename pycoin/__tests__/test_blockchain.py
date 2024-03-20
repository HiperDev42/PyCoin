from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import pycoin
import pycoin.tx


def create_if_not_exists(filename: str):
    try:
        with open(filename) as f:
            return RSA.import_key(f.read())
    except FileNotFoundError:
        key = RSA.generate(2048)
        with open(filename, 'wb') as f:
            f.write(key.export_key('PEM'))
        return key


def getPubKeyHash(key: RSA.RsaKey):
    return SHA256.new(key.public_key().export_key('DER'))


def test_should_mine_empty_block():
    key = create_if_not_exists('alice.pem')
    pubHash = getPubKeyHash(key)

    blockchain = pycoin.Blockchain()

    blockchain.minePendingTxs(pubHash)

    blockchain.save()


def test_should_mine_a_block_with_txs():
    aliceKey = create_if_not_exists('alice.pem')
    # bobKey = create_if_not_exists('bob.pem')
    # minerPubHash = getPubKeyHash(aliceKey)

    # blockchain = pycoin.Blockchain()
    # block_hash = blockchain.minePendingTxs(minerPubHash)

    # tx = pycoin.tx.TxV2(
    #     tx_ins=[],
    #     tx_outs=[
    #         pycoin.tx.TxOut(10, pycoin.script.Pay2PubHash(
    #             getPubKeyHash(bobKey)))
    #     ]
    # )

    # blockchain.minePendingTxs(minerPubHash)

    # blockchain.save()
