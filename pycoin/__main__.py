import pycoin
from pycoin.protocol import Message
import pycoin.node as node
import asyncio


@node.command()
def ping(payload: bytes) -> Message:
    return Message(command='pong', payload=payload)


@node.command()
@node.response('block')
def getblocks(data: bytes):
    return b''


if __name__ == '__main__':
    asyncio.run(node.run())
