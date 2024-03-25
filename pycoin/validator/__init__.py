from pycoin.tx import Tx
from pycoin.script import Script, Eval
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pycoin import Blockchain


class Validator:
    blockchain: 'Blockchain'

    def __init__(self, blockchain: 'Blockchain') -> None:
        self.blockchain = blockchain

    def validate_tx(self, tx: Tx):
        # Check if tx has inputs and outputs
        assert len(tx.tx_ins) > 0 and len(tx.tx_outs) > 0

        if tx.isCoinbase():
            return

        balance = 0
        # Validate inputs
        for tx_in in tx.tx_ins:
            unlock_script = tx_in.scriptSig
            utxo = self.blockchain.findUTXO(tx_in.txid, tx_in.outIndex)
            prev_tx = self.blockchain.getTxById(tx_in.txid)
            lock_script = utxo.script

            result = Eval(unlock_script.copy(), lock_script, prev_tx)
            assert len(result.stack) == 1
            assert result.stack[0] == b'\x01'

            balance += utxo.amount

        # Validate outputs
        for tx_out in tx.tx_outs:
            assert tx_out.amount > 0
            assert balance >= tx_out.amount
            balance -= tx_out.amount
