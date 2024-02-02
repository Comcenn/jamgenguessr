import redis.asyncio as aioredis


class RedisClient:
    def __init__(self, host: str = "localhost", port: int = 6379, ) -> None:
        self.host = host
        self.port = port
        self.pubsub = None
    
    async def _get_redis_connection(self) -> aioredis.Redis:
        return aioredis.Redis.from_url(f"redis://{self.host}:{self.port}")

    async def is_connected(self) -> bool:
        return bool(await self.connection.ping() if hasattr(self, "connection") else None)
    
    async def connect(self) -> None:
        self.connection = await self._get_redis_connection()
        self.pubsub = self.connection.pubsub()
    
    async def subscribe(self, channel_id: str) -> aioredis.Redis:
        await self.pubsub.subscribe(channel_id)
        return self.pubsub
    
    async def publish(self, channel_id: str, message: str) -> None:
        await self.connection.publish(channel_id, message)

    async def unsubscribe(self, channel_id: str) -> None:
        await self.pubsub.unsubscribe(channel_id)
