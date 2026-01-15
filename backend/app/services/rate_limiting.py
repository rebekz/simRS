"""Rate Limiting Service for STORY-002: User Authentication

This module provides rate limiting functionality for authentication attempts
and other sensitive operations to prevent brute force attacks.

Python 3.5+ compatible
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.system_alerts import SystemAlert, AlertSeverity, AlertStatus


logger = logging.getLogger(__name__)


# Rate limit configuration
LOGIN_RATE_LIMIT = 5  # attempts per window
LOGIN_RATE_WINDOW_MINUTES = 15
PASSWORD_RESET_RATE_LIMIT = 3  # attempts per window
PASSWORD_RESET_WINDOW_HOURS = 24


class RateLimitExceeded(Exception):
    """Rate limit exceeded exception"""
    def __init__(self, message: str, retry_after: int = 0):
        self.message = message
        self.retry_after = retry_after
        super(RateLimitExceeded, self).__init__(message)


class RateLimitingService(object):
    """Service for rate limiting authentication and other sensitive operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_login_rate_limit(
        self,
        identifier: str,
        ip_address: Optional[str] = None,
    ) -> None:
        """Check if login rate limit is exceeded

        Args:
            identifier: Username or email
            ip_address: Client IP address

        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        from app.core.redis import redis_client

        if not redis_client:
            return

        # Check rate limit by identifier
        key = "rate_limit:login:{}".format(identifier.lower())
        attempts = redis_client.get(key)

        if attempts and int(attempts) >= LOGIN_RATE_LIMIT:
            # Calculate retry after time
            ttl = redis_client.ttl(key)
            raise RateLimitExceeded(
                "Too many login attempts. Please try again later.",
                retry_after=ttl
            )

        # Check rate limit by IP
        if ip_address:
            ip_key = "rate_limit:login:ip:{}".format(ip_address)
            ip_attempts = redis_client.get(ip_key)

            if ip_attempts and int(ip_attempts) >= LOGIN_RATE_LIMIT * 2:
                # IP has higher limit (to account for multiple users)
                ttl = redis_client.ttl(ip_key)
                raise RateLimitExceeded(
                    "Too many login attempts from this IP. Please try again later.",
                    retry_after=ttl
                )

    async def record_login_attempt(
        self,
        identifier: str,
        success: bool,
        ip_address: Optional[str] = None,
    ):
        """Record a login attempt for rate limiting

        Args:
            identifier: Username or email
            success: Whether login was successful
            ip_address: Client IP address
        """
        from app.core.redis import redis_client

        if not redis_client:
            return

        if not success:
            # Increment counter for identifier
            key = "rate_limit:login:{}".format(identifier.lower())
            attempts = redis_client.incr(key)
            redis_client.expire(key, LOGIN_RATE_WINDOW_MINUTES * 60)

            # Increment counter for IP
            if ip_address:
                ip_key = "rate_limit:login:ip:{}".format(ip_address)
                redis_client.incr(ip_key)
                redis_client.expire(ip_key, LOGIN_RATE_WINDOW_MINUTES * 60)

            # Create alert if limit exceeded
            if attempts >= LOGIN_RATE_LIMIT:
                await self._create_rate_limit_alert(
                    identifier=identifier,
                    ip_address=ip_address,
                    attempts=attempts,
                )
        else:
            # Clear rate limit on successful login
            key = "rate_limit:login:{}".format(identifier.lower())
            redis_client.delete(key)

    async def check_password_reset_rate_limit(self, email: str) -> None:
        """Check if password reset rate limit is exceeded

        Args:
            email: Email address

        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        from app.core.redis import redis_client

        if not redis_client:
            return

        key = "rate_limit:password_reset:{}".format(email.lower())
        attempts = redis_client.get(key)

        if attempts and int(attempts) >= PASSWORD_RESET_RATE_LIMIT:
            ttl = redis_client.ttl(key)
            raise RateLimitExceeded(
                "Too many password reset attempts. Please try again later.",
                retry_after=ttl
            )

    async def record_password_reset_request(self, email: str):
        """Record a password reset request

        Args:
            email: Email address
        """
        from app.core.redis import redis_client

        if not redis_client:
            return

        key = "rate_limit:password_reset:{}".format(email.lower())
        redis_client.incr(key)
        redis_client.expire(key, PASSWORD_RESET_WINDOW_HOURS * 3600)

    async def get_rate_limit_status(
        self,
        identifier: str,
    ) -> Dict[str, Any]:
        """Get current rate limit status for identifier

        Args:
            identifier: Username or email

        Returns:
            Dict with rate limit status
        """
        from app.core.redis import redis_client

        if not redis_client:
            return {
                "limited": False,
                "attempts": 0,
                "max_attempts": LOGIN_RATE_LIMIT,
                "window_seconds": LOGIN_RATE_WINDOW_MINUTES * 60,
            }

        key = "rate_limit:login:{}".format(identifier.lower())
        attempts = redis_client.get(key)
        ttl = redis_client.ttl(key) if attempts else 0

        return {
            "limited": int(attempts or 0) >= LOGIN_RATE_LIMIT,
            "attempts": int(attempts or 0),
            "max_attempts": LOGIN_RATE_LIMIT,
            "window_seconds": LOGIN_RATE_WINDOW_MINUTES * 60,
            "retry_after": ttl,
        }

    async def _create_rate_limit_alert(
        self,
        identifier: str,
        ip_address: Optional[str],
        attempts: int,
    ):
        """Create security alert for rate limit violation"""
        try:
            alert = SystemAlert(
                severity=AlertSeverity.MEDIUM,
                component="authentication",
                alert_type="rate_limit_exceeded",
                message="Rate limit exceeded for login attempts",
                details={
                    "identifier": identifier,
                    "ip_address": ip_address,
                    "attempts": attempts,
                    "max_attempts": LOGIN_RATE_LIMIT,
                },
                status=AlertStatus.OPEN,
            )

            self.db.add(alert)
            await self.db.flush()

            logger.warning("Rate limit alert created for: {}".format(identifier))

        except Exception as e:
            logger.error("Failed to create rate limit alert: {}".format(e))


# Factory function
def get_rate_limiting_service(db: AsyncSession) -> RateLimitingService:
    """Get rate limiting service"""
    return RateLimitingService(db)
