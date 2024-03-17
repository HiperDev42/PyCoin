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


def test_blockchain():
    key = create_if_not_exists('alice.pem')
    pubHash = SHA256.new(key.publickey().export_key('DER'))

    blockchain = pycoin.Blockchain()

    blockchain.minePendingTxs(pubHash)

    blockchain.save()
