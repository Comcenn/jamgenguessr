import pytest

from redis.asyncio.client import PubSub

from api.lib.redis import RedisClient


CHANNEL_ID = "12345"


@pytest.mark.asyncio(scope="module")
async def test_can_connect_to_redis():
    client = RedisClient()
    await client.connect()
    assert await client.is_connected()
    assert isinstance(client.pubsub,  PubSub)


@pytest.mark.asyncio(scope="module")
async def test_can_subscribe_to_channel():
    client = RedisClient()
    await  client.connect()
    assert await client.is_connected()
    await client.subscribe(CHANNEL_ID)
    assert await client.connection.pubsub_numsub(CHANNEL_ID) == [(b"12345", 1)]


@pytest.mark.asyncio(scope="module")
async def test_can_unsubscribe_to_channel():
    client = RedisClient()
    await client.connect()
    assert await client.is_connected()
    assert await client.connection.pubsub_numsub(CHANNEL_ID) == [(b"12345", 0)]
    await client.subscribe(CHANNEL_ID)
    assert await client.connection.pubsub_numsub(CHANNEL_ID) == [(b"12345", 1)]
    await client.unsubscribe(CHANNEL_ID)
    assert await client.connection.pubsub_numsub(CHANNEL_ID) == [(b"12345", 1)]


