from pycoin.protocol import ConnectionInterface, Message
from typing import Callable
import asyncio
import socket

NODE_SERVER_BIND = '0.0.0.0'
NODE_SERVER_PORT = 4000

node_server: socket.socket
actions = dict()


def __init():
    global node_server
    node_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    node_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    node_server.bind((NODE_SERVER_BIND, NODE_SERVER_PORT))
    node_server.listen()
    node_server.setblocking(False)


def command(name: str | None = None):
    def decorator(func: Callable):
        key = name or func.__name__
        actions[key] = func
        return func
    return decorator


def __get_action(name: str):
    return actions[name]


async def handler(conn: ConnectionInterface):
    request = conn.recv()
    action = __get_action(request.command)
    try:
        response = action(request.payload)
        conn.send(response)
    except:
        response = Message(command='error', payload=b'unknown command')
        conn.send(response)


async def run():
    __init()
    _, port = node_server.getsockname()
    print(f"PyCoin node server started on port {port}")

    loop = asyncio.get_event_loop()

    while True:
        try:
            conn, addr = await loop.sock_accept(node_server)
            interface = ConnectionInterface(conn, addr)
            loop.create_task(handler(interface))
        except KeyboardInterrupt:
            break

    print('Closing node server...')
    node_server.close()
