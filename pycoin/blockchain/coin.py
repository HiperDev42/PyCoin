from pycoin.tx import TxV2, TxOut
from dataclasses import dataclass


@dataclass
class Coin:
    height: int
    tx: TxV2
    outIndex: int

    @property
    def tx_out(self) -> TxOut:
        return self.tx.tx_outs[self.outIndex]

    @property
    def amount(self) -> int:
        return self.tx_out.amount
