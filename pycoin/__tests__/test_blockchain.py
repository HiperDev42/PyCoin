import pycoin
import pycoin.tx


# def createIfNotExists(key_filename: str) -> pycoin.wallet.Wallet:
#     try:
#         return pycoin.wallet.Wallet(key_filename)
#     except FileNotFoundError:
#         return pycoin.wallet.create_wallet(key_filename)


def test_blockchain():
    # alice = createIfNotExists('alice.pem')
    # bob = createIfNotExists('bob.pem')

    blockchain = pycoin.Blockchain()

    tx = pycoin.tx.TxV2(
        tx_ins=[],
        tx_outs=[]
    )

    blockchain.submitTx(tx)
    blockchain.minePendingTxs(None)

    blockchain.save()
