from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timedelta
import secrets

from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.core.security import hash_token


async def create_password_reset_token(
    db: AsyncSession,
    user: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    expiry_hours: int = 24,
) -> PasswordResetToken:
    """Create a password reset token"""
    # Generate secure random token
    token = secrets.token_urlsafe(32)

    # Calculate expiration
    expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(reset_token)
    await db.commit()
    await db.refresh(reset_token)

    # Return the token (not hashed) so it can be sent to user
    reset_token.plain_token = token
    return reset_token


async def verify_password_reset_token(
    db: AsyncSession,
    token: str,
) -> Optional[User]:
    """Verify a password reset token and return the associated user"""
    token_hash = hash_token(token)

    result = await db.execute(
        select(PasswordResetToken).filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.is_used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        )
    )
    reset_token = result.scalar_one_or_none()

    if not reset_token:
        return None

    # Get the user
    result = await db.execute(
        select(User).filter(User.id == reset_token.user_id)
    )
    return result.scalar_one_or_none()


async def mark_password_reset_token_used(
    db: AsyncSession,
    token: str,
) -> bool:
    """Mark a password reset token as used"""
    token_hash = hash_token(token)

    result = await db.execute(
        select(PasswordResetToken).filter(
            PasswordResetToken.token_hash == token_hash
        )
    )
    reset_token = result.scalar_one_or_none()

    if not reset_token:
        return False

    reset_token.is_used = True
    reset_token.used_at = datetime.utcnow()

    await db.commit()
    return True


async def cleanup_old_reset_tokens(
    db: AsyncSession,
) -> int:
    """Clean up expired or used password reset tokens"""
    result = await db.execute(
        select(PasswordResetToken).filter(
            (PasswordResetToken.expires_at < datetime.utcnow()) |
            (PasswordResetToken.is_used == True)
        )
    )
    tokens = result.scalars().all()

    count = len(tokens)
    for token in tokens:
        await db.delete(token)

    await db.commit()
    return count
