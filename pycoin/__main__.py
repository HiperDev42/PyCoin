from pycoin.protocol import ConnectionInterface, Message
import pycoin.node as node
import asyncio


@node.command()
def ping(payload: bytes) -> Message:
    return Message(command='pong', payload=payload)


if __name__ == '__main__':
    asyncio.run(node.run())
