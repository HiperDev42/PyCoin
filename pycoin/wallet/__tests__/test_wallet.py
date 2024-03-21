from pycoin.wallet import Wallet, create_wallet
from pycoin.blockchain import Blockchain
from pycoin.logs import logger


def create_if_not_exists(filename: str, blockchain: Blockchain):
    try:
        return Wallet(filename, blockchain)
    except FileNotFoundError:
        return create_wallet(filename, blockchain)


def test_send_funds():
    blockchain = Blockchain()
    alice = create_if_not_exists('alice.pem', blockchain)
    bob = create_if_not_exists('bob.pem', blockchain)
    miner = create_if_not_exists('miner.pem', blockchain)

    if alice.getBalance() == 0:
        blockchain.minePendingTxs(alice.pubKeyHash())

    aliceBalance = alice.getBalance()
    bobBalance = bob.getBalance()
    assert aliceBalance > 0

    amount = aliceBalance // 2
    tx = alice.createTx(bob.get_p2pkh_address(), amount)
    blockchain.submitTx(tx)
    blockchain.minePendingTxs(miner.pubKeyHash())

    assert bob.getBalance() == bobBalance + amount
    assert alice.getBalance() == aliceBalance - amount
    logger.info(f'Alice: {alice.getBalance()}')
    logger.info(f'Bob: {bob.getBalance()}')
