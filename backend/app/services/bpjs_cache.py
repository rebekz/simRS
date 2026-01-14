"""BPJS Eligibility Verification Service for STORY-008

This module provides caching and history tracking for BPJS eligibility verification.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from redis.asyncio import Redis

from app.core.config import settings
from app.schemas.bpjs import BPJSEligibilityResponse

logger = logging.getLogger(__name__)


class BPJSCacheManager:
    """Manages caching of BPJS eligibility results in Redis."""

    def __init__(self, redis_client: Optional[Redis] = None):
        """
        Initialize cache manager.

        Args:
            redis_client: Optional Redis client (for testing)
        """
        self.redis = redis_client
        self.cache_ttl = 86400  # 24 hours in seconds

    async def get_cached_eligibility(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached eligibility result.

        Args:
            key: Cache key (card number or NIK)

        Returns:
            Cached eligibility data or None if not found/expired
        """
        if not self.redis:
            return None

        try:
            cached = await self.redis.get(f"bpjs:eligibility:{key}")
            if cached:
                data = json.loads(cached)
                logger.info(f"Cache hit for BPJS eligibility: {key}")
                return data
            return None
        except Exception as e:
            logger.error(f"Error getting cached eligibility: {e}")
            return None

    async def set_cached_eligibility(self, key: str, data: Dict[str, Any]) -> None:
        """
        Cache eligibility result.

        Args:
            key: Cache key (card number or NIK)
            data: Eligibility data to cache
        """
        if not self.redis:
            return

        try:
            # Add cache timestamp
            data["cached_at"] = datetime.now(timezone.utc).isoformat()
            await self.redis.setex(
                f"bpjs:eligibility:{key}",
                self.cache_ttl,
                json.dumps(data)
            )
            logger.info(f"Cached BPJS eligibility for: {key}")
        except Exception as e:
            logger.error(f"Error caching eligibility: {e}")

    async def invalidate_cache(self, key: str) -> None:
        """
        Invalidate cached eligibility for a specific key.

        Args:
            key: Cache key to invalidate
        """
        if not self.redis:
            return

        try:
            await self.redis.delete(f"bpjs:eligibility:{key}")
            logger.info(f"Invalidated cache for: {key}")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")

    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        if not self.redis:
            return {"error": "Redis not available"}

        try:
            info = await self.redis.info("stats")
            keyspace = await self.redis.info("keyspace")

            # Count BPJS eligibility keys
            bpjs_keys = 0
            async for key in self.redis.scan_iter(match="bpjs:eligibility:*"):
                bpjs_keys += 1

            return {
                "total_keys": bpjs_keys,
                "cache_hits": info.get("keyspace_hits", 0),
                "cache_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info),
                "db_keys": keyspace.get("db0", "")
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}

    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate."""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)
