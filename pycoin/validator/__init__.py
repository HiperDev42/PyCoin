from pycoin.blockchain import Blockchain
from pycoin.tx import TxV2
from pycoin.script import StackScript


class Validator:
    blockchain: Blockchain

    def __init__(self, blockchain: Blockchain) -> None:
        self.blockchain = blockchain

    def validate_tx(self, tx: TxV2):
        # Check if tx has inputs and outputs
        assert len(tx.tx_ins) > 0 and len(tx.tx_outs) > 0

        txid = tx.hash

        if tx.isCoinbase():
            return

        # Validate inputs
        for tx_in in tx.tx_ins:
            unlock_script = tx_in.scriptSig
            utxo = self.blockchain.findUTXO(tx_in.txid, tx_in.outIndex)
            lock_script = utxo.script

            script = StackScript(txid, lock_script, unlock_script)
            script.run()
