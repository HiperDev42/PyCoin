import pycoin
import asyncio
from random import randbytes, randint


def test_ping():
    conn = pycoin.connect(('127.0.0.1', 4000))
    data = randbytes(32)
    response = conn.request('ping', data)
    assert response.payload == data


def test_multiple_pings():
    async def ping():
        conn = pycoin.connect(('127.0.0.1', 4000))
        data = randbytes(32)
        response = conn.request('ping', data)
        return response.payload == data

    async def ping_multiple(n=100):
        return await asyncio.gather(*[ping() for _ in range(n)])

    result = asyncio.run(ping_multiple())
    assert all(result)
