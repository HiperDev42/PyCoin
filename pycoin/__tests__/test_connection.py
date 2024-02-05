import pycoin
import pytest
import asyncio
from random import randbytes, randint

pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_ping(data: bytes = randbytes(32)):
    conn = pycoin.Connection('127.0.0.1', 4000)

    async with conn:
        response = await conn.request('ping', data)
        assert response.payload == data


@pytest.mark.asyncio
async def test_multiple_pings():
    n = 100

    async def ping():
        conn = pycoin.Connection('127.0.0.1', 4000)
        data = randbytes(32)
        async with conn:
            response = await conn.request('ping', data)
            return response.payload == data

    result = await asyncio.gather(*[ping() for _ in range(n)])
    assert all(result)
