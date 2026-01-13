from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from datetime import datetime, timedelta

from app.models.session import Session as UserSession
from app.models.user import User
from app.core.security import hash_token, verify_token_hash


async def create_session(
    db: AsyncSession,
    user: User,
    access_token: str,
    refresh_token: str,
    ip_address: str,
    user_agent: str,
    device_info: dict = None,
) -> UserSession:
    """Create a new user session"""
    # Determine device type and info
    device_type = "desktop"
    device_name = None
    browser = None

    if user_agent:
        ua_lower = user_agent.lower()
        if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
            device_type = "mobile"
        elif "tablet" in ua_lower or "ipad" in ua_lower:
            device_type = "tablet"

        # Extract browser info
        if "chrome" in ua_lower:
            browser = "Chrome"
        elif "firefox" in ua_lower:
            browser = "Firefox"
        elif "safari" in ua_lower:
            browser = "Safari"
        elif "edge" in ua_lower:
            browser = "Edge"

    if device_info:
        device_name = device_info.get("device_name")

    # Calculate expiration time
    expires_at = datetime.utcnow() + timedelta(minutes=30)  # 30-minute session timeout

    db_session = UserSession(
        user_id=user.id,
        token_hash=hash_token(access_token),
        refresh_token_hash=hash_token(refresh_token),
        ip_address=ip_address,
        user_agent=user_agent,
        device_type=device_type,
        device_name=device_name,
        browser=browser,
        expires_at=expires_at,
    )

    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)

    return db_session


async def get_session_by_token_hash(
    db: AsyncSession,
    token_hash: str,
) -> Optional[UserSession]:
    """Get session by token hash"""
    result = await db.execute(
        select(UserSession).filter(UserSession.token_hash == token_hash)
    )
    return result.scalar_one_or_none()


async def refresh_session(
    db: AsyncSession,
    old_refresh_token: str,
    new_access_token: str,
    new_refresh_token: str,
) -> Optional[UserSession]:
    """Rotate refresh token and create new session"""
    old_refresh_hash = hash_token(old_refresh_token)

    result = await db.execute(
        select(UserSession).filter(
            UserSession.refresh_token_hash == old_refresh_hash,
            UserSession.is_revoked == False
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        return None

    # Revoke old session
    session.is_revoked = True
    session.revoked_at = datetime.utcnow()

    # Create new session
    new_session = UserSession(
        user_id=session.user_id,
        token_hash=hash_token(new_access_token),
        refresh_token_hash=hash_token(new_refresh_token),
        ip_address=session.ip_address,
        user_agent=session.user_agent,
        device_type=session.device_type,
        device_name=session.device_name,
        browser=session.browser,
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    )

    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return new_session


async def revoke_session(
    db: AsyncSession,
    session_id: int,
    user_id: int,
) -> bool:
    """Revoke a specific session"""
    result = await db.execute(
        select(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == user_id
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        return False

    session.is_revoked = True
    session.revoked_at = datetime.utcnow()
    await db.commit()

    return True


async def revoke_all_sessions(
    db: AsyncSession,
    user_id: int,
    exclude_session_id: int = None,
) -> int:
    """Revoke all sessions for a user (logout from all devices)"""
    query = select(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_revoked == False
    )

    if exclude_session_id:
        query = query.filter(UserSession.id != exclude_session_id)

    result = await db.execute(query)
    sessions = result.scalars().all()

    count = 0
    for session in sessions:
        session.is_revoked = True
        session.revoked_at = datetime.utcnow()
        count += 1

    await db.commit()
    return count


async def get_user_sessions(
    db: AsyncSession,
    user_id: int,
) -> List[UserSession]:
    """Get all active sessions for a user"""
    result = await db.execute(
        select(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_revoked == False
        ).order_by(UserSession.last_used_at.desc())
    )
    return result.scalars().all()


async def cleanup_expired_sessions(
    db: AsyncSession,
) -> int:
    """Clean up expired sessions (should be run as a scheduled task)"""
    result = await db.execute(
        select(UserSession).filter(
            UserSession.expires_at < datetime.utcnow(),
            UserSession.is_revoked == False
        )
    )
    sessions = result.scalars().all()

    count = 0
    for session in sessions:
        session.is_revoked = True
        session.revoked_at = datetime.utcnow()
        count += 1

    await db.commit()
    return count
