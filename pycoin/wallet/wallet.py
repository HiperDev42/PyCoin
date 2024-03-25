from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from pycoin.tx import Tx, TxIn, TxOut
from pycoin.blockchain.coin import Coin
from typing import TYPE_CHECKING
import os

if TYPE_CHECKING:
    from pycoin import Blockchain


class InsuffitientFunds(Exception):
    ...


def Pay2PubHash(pub_hash: SHA256.SHA256Hash) -> list[str]:
    return ['OP_DUP', 'OP_HASH160', 'OP_PUSHDATA', pub_hash.hexdigest(), 'OP_EQUALVERIFY',
            'OP_CHECKSIG']


class Wallet:
    key_filename: str

    def __init__(self, key_filename: str, blockchain: 'Blockchain') -> None:
        if not os.path.isfile(key_filename):
            raise FileNotFoundError(f"Key file not found: {key_filename}")

        self.blockchain = blockchain
        self.key_filename = key_filename
        self.public_key = self.__read_key().public_key()

    def __read_key(self) -> RSA.RsaKey:
        key_bytes = None
        with open(self.key_filename, 'r') as f:
            key_bytes = f.read()
        key = RSA.import_key(key_bytes)
        return key

    def pubKeyHash(self):
        return SHA256.new(self.public_key.export_key('DER'))

    def spendSig(self, coin: Coin) -> bytes:
        prev_hash = SHA256.new(coin.tx.hash.digest())
        key = self.__read_key()
        signature = pkcs1_15.new(key).sign(prev_hash)
        return [signature, self.public_key.export_key('DER')]

    def get_p2pkh_address(self) -> list[str]:
        return Pay2PubHash(self.pubKeyHash())

    def getUTXOs(self) -> list[Coin]:
        p2pkh_address = self.get_p2pkh_address()
        snapshot = self.blockchain.getSnapshot()
        coins: list[Coin] = []

        for utxo in snapshot.values():
            if utxo.tx_out.script == p2pkh_address:
                coins.append(utxo)

        return sorted(coins, key=lambda utxo: utxo.amount)

    def getBalance(self) -> int:
        coins = self.getUTXOs()
        balance = 0

        for coin in coins:
            balance += coin.amount

        return balance

    def createTx(self, receiver: list[str], amount: int) -> Tx:
        coins = self.getUTXOs()

        tx_ins: list[TxIn] = []
        tx_outs: list[TxOut] = []
        balance = 0
        for coin in coins:
            tx_ins.append(TxIn(coin.tx.hash.digest(),
                          coin.outIndex, scriptSig=self.spendSig(coin)))
            balance += coin.amount
            if balance >= amount:
                break
        else:
            raise InsuffitientFunds()

        tx_outs.append(TxOut(amount, receiver))
        balance -= amount

        if balance > 0:
            tx_outs.append(TxOut(balance, self.get_p2pkh_address()))

        tx = Tx(tx_ins, tx_outs)

        return tx


def create_wallet(key_filename: str, blockchain: 'Blockchain') -> Wallet:
    key = RSA.generate(2048)
    with open(key_filename, 'wb') as f:
        f.write(key.export_key('PEM'))
    return Wallet(key_filename, blockchain)
