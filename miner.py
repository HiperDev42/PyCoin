from blockchain import Account, Tx

mempool = []


def submit_tx(tx: Tx):
    mempool.append(tx)


if __name__ == '__main__':
    account1 = Account(1)
    account2 = Account(2)
    account3 = Account(3)

    print(account1, account2, account3)

    submit_tx(Tx(account1, account2, 100))
    submit_tx(Tx(account2, account3, 50))
    submit_tx(Tx(account3, account1, 10))
    submit_tx(Tx(account3, account2, 10))

    print(mempool)
