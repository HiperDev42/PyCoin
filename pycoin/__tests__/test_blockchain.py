from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import pycoin
import pycoin.tx
from pycoin.logs import logger


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
    alicePubKey = aliceKey.public_key().export_key('DER')
    bobKey = create_if_not_exists('bob.pem')
    minerPubHash = getPubKeyHash(aliceKey)

    blockchain = pycoin.Blockchain()
    block_hash = blockchain.minePendingTxs(minerPubHash)
    block = blockchain.data[block_hash.hex()]

    prev_tx = block.txs[0]
    prev_hash = SHA256.new(prev_tx.hash.digest())
    signature = pkcs1_15.new(aliceKey).sign(prev_hash)

    pkcs1_15.new(RSA.import_key(alicePubKey)).verify(
        prev_hash, signature)

    tx = pycoin.tx.TxV2(
        tx_ins=[
            pycoin.tx.TxIn(prev_tx.hash.digest(), 0, [
                           signature, alicePubKey])
        ],
        tx_outs=[
            pycoin.tx.TxOut(10, pycoin.script.Pay2PubHash(
                getPubKeyHash(bobKey)))
        ]
    )
    blockchain.submitTx(tx)

    blockchain.minePendingTxs(minerPubHash)

    blockchain.save()
