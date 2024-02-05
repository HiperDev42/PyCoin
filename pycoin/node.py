from pycoin.protocol import Message
from pycoin.logs import logger
from typing import Callable
import asyncio
import socket

NODE_SERVER_BIND = '0.0.0.0'
NODE_SERVER_PORT = 4000

actions = dict()


def command(name: str | None = None):
    def decorator(func: Callable):
        key = name or func.__name__
        actions[key] = func
        return func
    return decorator


def response(name: str):
    def decorator(func: Callable):
        def execute(*args, **kwargs) -> Message:
            data = func(*args, **kwargs)
            return Message(command=name, payload=data)
        execute.__name__ = func.__name__
        return execute
    return decorator


def get_action(name: str) -> Callable:
    return actions[name]


class Handler(asyncio.Protocol):
    transport: asyncio.Transport

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.transport = transport
        return super().connection_made(transport)

    def data_received(self, data: bytes) -> None:
        try:
            request = Message.unpack(data)
            logger.info(f'Request - {request.command}')
            action = get_action(request.command)
            if not action:
                raise Exception("Unknown command")
            response = action(request.payload)
            self.transport.write(response.pack())
        except Exception as e:
            logger.exception(e)
            sep = ' '
            error_message = sep.join(e.args)
            response = Message(command='error', payload=error_message.encode())
            self.transport.write(response.pack())


async def run():
    loop = asyncio.get_event_loop()

    node_server = await loop.create_server(lambda: Handler(), NODE_SERVER_BIND, NODE_SERVER_PORT)
    logger.info(f"PyCoin node server started on port {NODE_SERVER_PORT}")

    async with node_server:
        await node_server.serve_forever()
