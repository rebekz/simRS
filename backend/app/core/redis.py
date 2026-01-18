"""Redis client configuration and initialization.

This module provides a global Redis client instance for caching,
rate limiting, and other Redis-based functionality.
"""
import logging
from typing import Optional

from redis.asyncio import Redis as AsyncRedis
from redis.exceptions import RedisError

from app.core.config import settings


logger = logging.getLogger(__name__)


# Global Redis client instance
redis_client: Optional[AsyncRedis] = None


async def init_redis() -> Optional[AsyncRedis]:
    """Initialize Redis client connection.

    Returns:
        Redis client instance or None if connection fails
    """
    global redis_client

    try:
        redis_client = await AsyncRedis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await redis_client.ping()
        logger.info(f"Connected to Redis at {settings.REDIS_URL}")
        return redis_client
    except RedisError as e:
        logger.warning(f"Failed to connect to Redis: {e}")
        redis_client = None
        return None
    except Exception as e:
        logger.error(f"Unexpected error connecting to Redis: {e}")
        redis_client = None
        return None


async def close_redis() -> None:
    """Close Redis client connection."""
    global redis_client

    if redis_client:
        try:
            await redis_client.close()
            logger.info("Redis connection closed")
        except RedisError as e:
            logger.warning(f"Error closing Redis connection: {e}")
        finally:
            redis_client = None


def get_redis() -> Optional[AsyncRedis]:
    """Get the current Redis client instance.

    Returns:
        Redis client instance or None if not initialized
    """
    return redis_client
