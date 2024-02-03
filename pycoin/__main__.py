from pycoin.protocol import ConnectionInterface
import socket
import asyncio


NODE_SERVER_BIND = '0.0.0.0'
NODE_SERVER_PORT = 4000

node_server: socket.socket


async def handler(conn: ConnectionInterface):
    msg = conn.recv()
    print('msg received: ', msg)
    conn.send('ok', b'hello')
    print('response sent')


def init():
    global node_server
    node_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    node_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    node_server.bind((NODE_SERVER_BIND, NODE_SERVER_PORT))
    node_server.listen()
    node_server.setblocking(False)


async def run():
    init()
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


if __name__ == '__main__':
    asyncio.run(run())
