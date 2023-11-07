from blockchain import *
import hashlib
import asyncio
import pickledb

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

    for i in range(len(blockchain.chain)):
        block = blockchain.get_block(i)
        print(block, block.nonce)

    if len(blockchain.chain) < 2:
        new_block = Block(
            blockchain.last_hash(),
        )
        asyncio.run(new_block.mine())

        blockchain.append(new_block)
        blockchain.dump()
