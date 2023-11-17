import click
from click_shell import make_click_shell
import logging
import network
import blockchain
import miner
from colorama import Fore, Style


class LogFormatter(logging.Formatter):
    fmt: str = '%(asctime)s - %(name)s - {levelNameColor}%(levelname)s{reset} - %(message)s (%(filename)s:%(lineno)d)'
    FORMATS = {
        logging.DEBUG: fmt.format(levelNameColor=Fore.BLUE, reset=Style.RESET_ALL),
        logging.INFO: fmt.format(levelNameColor=Fore.CYAN, reset=Style.RESET_ALL),
        logging.WARNING: fmt.format(levelNameColor=Fore.LIGHTRED_EX, reset=Style.RESET_ALL),
        logging.ERROR: fmt.format(levelNameColor=Fore.RED, reset=Style.RESET_ALL),
        logging.CRITICAL: fmt.format(levelNameColor=Fore.MAGENTA, reset=Style.RESET_ALL),
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class strings:
    SUCCESS = f'{Fore.GREEN}Success{Style.RESET_ALL}'
    FAIL = f'{Fore.RED}Failed{Style.RESET_ALL}'


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(LogFormatter())
logger.addHandler(ch)


peer: network.Peer = network.Peer()


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
        print(strings.SUCCESS)
    else:
        print(strings.FAIL)


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
    if peer.ping():
        print(strings.SUCCESS)
    else:
        print(strings.FAIL)


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
