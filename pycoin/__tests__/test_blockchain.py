from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import pycoin
import pycoin.tx
import pycoin.script
from pycoin.utils import hash160
from pycoin.logs import logger
from pycoin.script import Script, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG


def create_if_not_exists(filename: str):
    try:
        with open(filename) as f:
            return RSA.import_key(f.read())
    except FileNotFoundError:
        key = RSA.generate(2048)
        with open(filename, 'wb') as f:
            f.write(key.export_key('PEM'))
        return key


def get_p2pkh_address(key: RSA.RsaKey):
    return Script([OP_DUP, OP_HASH160, hash160(
        key.public_key().export_key('DER')), OP_EQUALVERIFY, OP_CHECKSIG])


def test_should_mine_empty_block():
    key = create_if_not_exists('alice.pem')

    payScript = get_p2pkh_address(key)

    blockchain = pycoin.Blockchain()
    blockchain.minePendingTxs(payScript)

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

    tx = pycoin.tx.Tx(
        tx_ins=[
            pycoin.tx.TxIn(prev_tx.hash.digest(), 0, [
                           signature, alicePubKey])
        ],
        tx_outs=[
            pycoin.tx.TxOut(10, pycoin.script.Pay2PubHash(
                getPubKeyHash(bobKey))),
            pycoin.tx.TxOut(40, pycoin.script.Pay2PubHash(
                getPubKeyHash(aliceKey)))
        ]
    )
    blockchain.submitTx(tx)

    blockchain.minePendingTxs(minerPubHash)

    blockchain.save()
