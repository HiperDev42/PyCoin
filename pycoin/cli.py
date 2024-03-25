import pycoin
import pycoin.script
import pycoin.wallet
import click
import colorama
from typing import BinaryIO
from Crypto.PublicKey import RSA
from pycoin.logs import logger


blockchain = pycoin.Blockchain('blockchain.db.json')


def colored(s: str, color: str) -> str:
    return color+s+colorama.Fore.RESET


@click.group()
def app():
    pass


@app.command()
@click.argument('key_file', type=click.File('wb'))
def create_wallet(key_file: BinaryIO):
    key_file.write(RSA.generate(2048).export_key('PEM'))
    click.echo('Wallet created')


@app.group()
@click.option('--key', '-k', default='wallet.pem', help='Key filename')
@click.pass_context
def wallet(ctx, key: str):
    wallet = pycoin.wallet.Wallet(key, blockchain)
    ctx.obj = wallet


@wallet.command()
@click.pass_obj
def balance(wallet: pycoin.wallet.Wallet):
    balance = wallet.getBalance()
    click.echo(f'Wallet: {balance}')


@wallet.command()
@click.pass_obj
def get_address(wallet: pycoin.wallet.Wallet):
    addr = wallet.get_p2pkh_address()
    click.echo(addr.hex())


@wallet.command()
@click.argument('receiver')
@click.argument('amount')
@click.pass_obj
def create_tx(wallet: pycoin.wallet.Wallet, receiver: str, amount: int):
    receiver_address = pycoin.script.Script(bytes.fromhex(receiver))
    try:
        tx = wallet.createTx(receiver=receiver_address, amount=amount)
    except pycoin.wallet.InsuffitientFunds:
        click.echo(colored('Insufficient funds', colorama.Fore.RED))
        return

    blockchain.submitTx(tx)


if __name__ == '__main__':
    app()
