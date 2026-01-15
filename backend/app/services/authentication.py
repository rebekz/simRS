"""Authentication Service for STORY-002: User Authentication Service Layer

This module provides comprehensive authentication services including:
- Token-based authentication with JWT
- Password validation and hashing
- Session management
- Password reset functionality
- Rate limiting for auth attempts
- Multi-factor authentication support

Python 3.5+ compatible
"""

import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.user import User
from app.models.session import UserSession
from app.models.password_reset import PasswordResetToken
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.models.system_alerts import SystemAlert, AlertSeverity, AlertStatus


logger = logging.getLogger(__name__)


# Authentication configuration
MIN_PASSWORD_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_MINUTES = 30
SESSION_EXPIRY_HOURS = 24
REFRESH_TOKEN_DAYS = 30
PASSWORD_RESET_HOURS = 24


class AuthenticationError(Exception):
    """Authentication error with severity level"""
    def __init__(self, message: str, severity: str = "error"):
        self.message = message
        self.severity = severity
        super(AuthenticationError, self).__init__(message)


class PasswordValidationError(AuthenticationError):
    """Password validation error"""
    pass


class AuthenticationService(object):
    """Service for user authentication and session management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Authenticate a user with username and password

        Args:
            username: Username or email
            password: User password
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Dict with user info, access token, and refresh token

        Raises:
            AuthenticationError: If authentication fails
        """
        # Find user by username or email
        user = await self._get_user_by_identifier(username)

        if not user:
            # Still check password to prevent timing attacks
            verify_password(password, "dummy_hash")
            await self._track_failed_login(None, ip_address, "user_not_found")
            raise AuthenticationError("Invalid credentials", "warning")

        # Check if user is active
        if not user.is_active:
            await self._track_failed_login(user.id, ip_address, "user_inactive")
            raise AuthenticationError("Account is inactive", "error")

        # Check if account is locked
        if await self._is_account_locked(user.id):
            await self._track_failed_login(user.id, ip_address, "account_locked")
            raise AuthenticationError(
                "Account is temporarily locked due to too many failed login attempts. "
                "Please try again later.",
                "warning"
            )

        # Verify password
        if not verify_password(password, user.hashed_password):
            await self._track_failed_login(user.id, ip_address, "invalid_password")
            raise AuthenticationError("Invalid credentials", "warning")

        # Check if password needs to be changed
        if user.force_password_change:
            raise AuthenticationError(
                "Password must be changed before continuing",
                "info"
            )

        # Successful authentication - create tokens
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})

        # Create session
        session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(hours=SESSION_EXPIRY_HOURS),
        )
        self.db.add(session)
        await self.db.flush()

        # Clear failed login attempts
        await self._clear_failed_login_attempts(user.id)

        # Update last login
        user.last_login = datetime.utcnow()

        logger.info("User authenticated successfully: {}".format(username))

        return {
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,  # 1 hour
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            Dict with new access token

        Raises:
            AuthenticationError: If refresh token is invalid
        """
        # Verify refresh token
        token_data = verify_token(refresh_token)
        if not token_data:
            raise AuthenticationError("Invalid refresh token", "warning")

        user_id = token_data.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid refresh token", "warning")

        # Find session
        session = await self._get_valid_session(user_id, refresh_token)
        if not session:
            raise AuthenticationError("Session expired or invalid", "warning")

        # Get user
        user = await self._get_user_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive", "error")

        # Create new access token
        access_token = create_access_token(data={"sub": user.id})

        logger.info("Token refreshed for user: {}".format(user.username))

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600,
        }

    async def logout_user(
        self,
        user_id: int,
        refresh_token: str,
        revoke_all: bool = False,
    ) -> bool:
        """Logout user by invalidating session(s)

        Args:
            user_id: User ID
            refresh_token: Refresh token to invalidate
            revoke_all: Whether to revoke all sessions

        Returns:
            True if successful
        """
        try:
            if revoke_all:
                # Revoke all sessions for user
                query = select(UserSession).where(
                    and_(
                        UserSession.user_id == user_id,
                        UserSession.is_active == True,
                    )
                )
                result = await self.db.execute(query)
                sessions = result.scalars().all()

                for session in sessions:
                    session.is_active = False
                    session.revoked_at = datetime.utcnow()

                logger.info("All sessions revoked for user: {}".format(user_id))

            else:
                # Revoke specific session
                session = await self._get_valid_session(user_id, refresh_token)
                if session:
                    session.is_active = False
                    session.revoked_at = datetime.utcnow()

                logger.info("Session revoked for user: {}".format(user_id))

            return True

        except Exception as e:
            logger.error("Error during logout: {}".format(e))
            return False

    async def validate_password(self, password: str) -> None:
        """Validate password strength

        Args:
            password: Password to validate

        Raises:
            PasswordValidationError: If password doesn't meet requirements
        """
        errors = []

        # Check length
        if len(password) < MIN_PASSWORD_LENGTH:
            errors.append("Password must be at least {} characters long".format(
                MIN_PASSWORD_LENGTH
            ))

        # Check for uppercase
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")

        # Check for lowercase
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")

        # Check for digit
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")

        # Check for special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            errors.append("Password must contain at least one special character")

        if errors:
            raise PasswordValidationError("; ".join(errors))

    async def hash_password(self, password: str) -> str:
        """Hash a password

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return get_password_hash(password)

    async def verify_password_reset_token(self, token: str) -> Optional[User]:
        """Verify password reset token and return user

        Args:
            token: Password reset token

        Returns:
            User if token is valid, None otherwise
        """
        query = select(PasswordResetToken).where(
            and_(
                PasswordResetToken.token == token,
                PasswordResetToken.is_active == True,
                PasswordResetToken.expires_at > datetime.utcnow(),
            )
        )

        result = await self.db.execute(query)
        reset_token = result.scalar_one_or_none()

        if not reset_token:
            return None

        # Get user
        user = await self._get_user_by_id(reset_token.user_id)
        return user

    async def invalidate_reset_token(self, token: str) -> bool:
        """Invalidate a password reset token

        Args:
            token: Reset token to invalidate

        Returns:
            True if successful
        """
        query = select(PasswordResetToken).where(
            PasswordResetToken.token == token
        )

        result = await self.db.execute(query)
        reset_token = result.scalar_one_or_none()

        if reset_token:
            reset_token.is_active = False
            reset_token.used_at = datetime.utcnow()
            return True

        return False

    async def get_user_sessions(self, user_id: int) -> list:
        """Get all active sessions for user

        Args:
            user_id: User ID

        Returns:
            List of active sessions
        """
        query = select(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow(),
            )
        ).order_by(UserSession.created_at.desc())

        result = await self.db.execute(query)
        sessions = result.scalars().all()

        return [
            {
                "session_id": s.id,
                "ip_address": s.ip_address,
                "user_agent": s.user_agent,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "expires_at": s.expires_at.isoformat() if s.expires_at else None,
                "last_activity": s.last_activity.isoformat() if s.last_activity else None,
            }
            for s in sessions
        ]

    # ==========================================================================
    # Private Helper Methods
    # ==========================================================================

    async def _get_user_by_identifier(self, identifier: str) -> Optional[User]:
        """Get user by username or email"""
        query = select(User).where(
            or_(
                User.username == identifier,
                User.email == identifier,
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_valid_session(
        self,
        user_id: int,
        refresh_token: str,
    ) -> Optional[UserSession]:
        """Get valid session for user"""
        query = select(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.refresh_token == refresh_token,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow(),
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _is_account_locked(self, user_id: int) -> bool:
        """Check if account is locked due to failed login attempts"""
        from app.core.redis import redis_client

        if not redis_client:
            return False

        key = "login_attempts:{}".format(user_id)
        attempts = redis_client.get(key)

        if attempts and int(attempts) >= MAX_LOGIN_ATTEMPTS:
            return True

        return False

    async def _track_failed_login(
        self,
        user_id: Optional[int],
        ip_address: Optional[str],
        reason: str,
    ):
        """Track failed login attempts and create alerts if needed"""
        from app.core.redis import redis_client

        if not redis_client:
            return

        if user_id:
            key = "login_attempts:{}".format(user_id)
            attempts = redis_client.incr(key)
            redis_client.expire(key, ACCOUNT_LOCKOUT_MINUTES * 60)

            # Create alert if max attempts reached
            if attempts >= MAX_LOGIN_ATTEMPTS:
                await self._create_security_alert(
                    user_id=user_id,
                    ip_address=ip_address,
                    reason="max_login_attempts",
                    details={
                        "attempts": attempts,
                        "reason": reason,
                    }
                )

    async def _clear_failed_login_attempts(self, user_id: int):
        """Clear failed login attempts for user"""
        from app.core.redis import redis_client

        if not redis_client:
            return

        key = "login_attempts:{}".format(user_id)
        redis_client.delete(key)

    async def _create_security_alert(
        self,
        user_id: int,
        ip_address: Optional[str],
        reason: str,
        details: Dict[str, Any] = None,
    ):
        """Create security alert for suspicious activity"""
        try:
            alert = SystemAlert(
                severity=AlertSeverity.HIGH,
                component="authentication",
                alert_type="security_alert",
                message="Security alert: {}".format(reason),
                details={
                    "user_id": user_id,
                    "ip_address": ip_address,
                    "reason": reason,
                }
            )
            alert.details.update(details or {})

            self.db.add(alert)
            await self.db.flush()

        except Exception as e:
            logger.error("Failed to create security alert: {}".format(e))


class PasswordResetService(object):
    """Service for password reset functionality"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_reset_token(self, email: str) -> Optional[str]:
        """Create a password reset token for user

        Args:
            email: User email address

        Returns:
            Reset token if user found, None otherwise
        """
        import uuid

        # Find user by email
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            # Don't reveal if user exists
            return None

        # Generate secure token
        token = secrets.token_urlsafe(32)

        # Create reset token record
        reset_token = PasswordResetToken(
            token=token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=PASSWORD_RESET_HOURS),
        )

        self.db.add(reset_token)
        await self.db.flush()

        logger.info("Password reset token created for user: {}".format(user.id))

        return token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password using token

        Args:
            token: Valid reset token
            new_password: New password

        Returns:
            True if successful

        Raises:
            AuthenticationError: If token is invalid
            PasswordValidationError: If password doesn't meet requirements
        """
        # Verify token
        auth_service = AuthenticationService(self.db)
        user = await auth_service.verify_password_reset_token(token)

        if not user:
            raise AuthenticationError("Invalid or expired reset token", "warning")

        # Validate new password
        await auth_service.validate_password(new_password)

        # Hash new password
        hashed_password = await auth_service.hash_password(new_password)

        # Update user password
        user.hashed_password = hashed_password
        user.force_password_change = False
        user.password_changed_at = datetime.utcnow()

        # Invalidate reset token
        await auth_service.invalidate_reset_token(token)

        logger.info("Password reset completed for user: {}".format(user.id))

        return True


class SessionCleanupService(object):
    """Service for cleaning up expired sessions"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions

        Returns:
            Number of sessions cleaned up
        """
        query = select(UserSession).where(
            or_(
                UserSession.expires_at < datetime.utcnow(),
                and_(
                    UserSession.is_active == False,
                    UserSession.revoked_at < datetime.utcnow() - timedelta(days=7),
                ),
            )
        )

        result = await self.db.execute(query)
        sessions = result.scalars().all()

        count = len(sessions)
        for session in sessions:
            await self.db.delete(session)

        await db.flush()

        if count > 0:
            logger.info("Cleaned up {} expired sessions".format(count))

        return count

    async def cleanup_expired_reset_tokens(self) -> int:
        """Clean up expired password reset tokens

        Returns:
            Number of tokens cleaned up
        """
        query = select(PasswordResetToken).where(
            or_(
                PasswordResetToken.expires_at < datetime.utcnow(),
                and_(
                    PasswordResetToken.is_active == False,
                    PasswordResetToken.used_at < datetime.utcnow() - timedelta(days=7),
                ),
            )
        )

        result = await self.db.execute(query)
        tokens = result.scalars().all()

        count = len(tokens)
        for token in tokens:
            await self.db.delete(token)

        await db.flush()

        if count > 0:
            logger.info("Cleaned up {} expired reset tokens".format(count))

        return count


# Factory functions
def get_auth_service(db: AsyncSession) -> AuthenticationService:
    """Get authentication service"""
    return AuthenticationService(db)


def get_password_reset_service(db: AsyncSession) -> PasswordResetService:
    """Get password reset service"""
    return PasswordResetService(db)


def get_session_cleanup_service(db: AsyncSession) -> SessionCleanupService:
    """Get session cleanup service"""
    return SessionCleanupService(db)
