import redis.asyncio as redis
from typing import Optional
from app.core.config import settings

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """
    Get or create Redis client instance.
    """
    global _redis_client

    if _redis_client is None:
        # Parse REDIS_URL (format: redis://:password@host:port/db)
        # We need to extract password, host, port, db from URL
        import re

        url = settings.REDIS_URL
        # Match redis://:password@host:port/db
        match = re.match(r'redis://:(?P<password>[^@]+)@(?P<host>[^:]+):(?P<port>\d+)/(?P<db>\d+)', url)

        if match:
            password = match.group('password')
            host = match.group('host')
            port = int(match.group('port'))
            db = int(match.group('db'))
        else:
            # Fallback to direct connection
            password = None
            host = 'localhost'
            port = 6379
            db = 0

        _redis_client = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )

    return _redis_client


async def close_redis() -> None:
    """
    Close Redis connection.
    """
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
