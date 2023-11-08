from blockchain import *
import asyncio
import time

reward_account = Account(1)
mempool = []
blockchain = Blockchain()

def submit_tx(tx: Tx):
    mempool.append(tx)

async def mine_block():
    reward = Tx(Account(0), reward_account, 50)

    txs = mempool.copy()
    mempool.clear()
    txs.append(reward)

    block = Block(
        prev_block=blockchain.last_hash(),
        time=int(time.time()),
        txs=txs
    )

    while not block.validate():
        block.nonce += 1
    
    return block

if __name__ == '__main__':
    account1 = Account(1)
    account2 = Account(2)
    account3 = Account(3)

    submit_tx(Tx(account1, account2, 30))

    block = asyncio.run(mine_block())
    print('New block')

    blockchain.append(block)
    blockchain.flush()

    for block_hash in blockchain.chain:
        block = blockchain.get_block(block_hash)
        block.show()

    balance1 = blockchain.get_balance(account1)
    print(f'Balance 1: {balance1}')

    balance2 = blockchain.get_balance(account2)
    print(f'Balance 2: {balance2}')
