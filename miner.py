from blockchain import *
import hashlib
import asyncio

mempool = []
genesis = Block(
    hashlib.sha256(b'').digest(),
    0,
)
asyncio.run(genesis.mine())
blockchain = Blockchain()

def submit_tx(tx: Tx):
    mempool.append(tx)


if __name__ == '__main__':
    account1 = Account(1)
    account2 = Account(2)
    account3 = Account(3)

    if len(blockchain.chain) < 2:
        new_block = Block(
            blockchain.last_hash(),
        )
        asyncio.run(new_block.mine())

        blockchain.append(new_block)
        blockchain.dump()
    
    for block_hash in blockchain.chain:
        block = blockchain.get_block(block_hash)
        block.show()
