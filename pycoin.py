import click
from click_shell import make_click_shell
import logging
import network
import blockchain
import miner


peer: network.Peer = network.Peer()
logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def app(ctx, verbose):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    shell = make_click_shell(ctx)
    shell.cmdloop()
    miner.stop()
    exit(0)


@app.command()
@click.argument('ip')
@click.argument('port', type=int)
def connect(ip: str, port: int):
    peer = network.Peer(ip, port)
    if peer.test_connection():
        print('Connected')
    else:
        print('Not connected')


@app.command()
@click.argument('source')
@click.argument('destination')
@click.argument('amount')
def tx(source: int, destination: int, amount: int):
    src_acc = blockchain.Account(source)
    dst_acc = blockchain.Account(destination)
    tx = blockchain.Tx(src_acc, dst_acc, amount)
    if peer.tx(tx):
        print('Sent')
    else:
        print('Error')


@app.command()
def ping():
    pass


@app.group('miner')
def miner_group():
    pass


@miner_group.command('start')
def start_miner():
    miner.start()


@miner_group.command('stop')
def stop_miner():
    miner.stop()


if __name__ == '__main__':
    app()
