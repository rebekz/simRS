from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timedelta

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, is_password_expired
from app.core.security import validate_password_strength


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username"""
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user"""
    # Validate password strength
    is_valid, errors = validate_password_strength(user_in.password)
    if not is_valid:
        raise ValueError(f"Password validation failed: {', '.join(errors)}")

    db_user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        is_active=user_in.is_active,
        password_changed_at=datetime.utcnow(),  # Track password change
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, user_id: int, user_in: UserUpdate) -> Optional[User]:
    """Update a user"""
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        # Validate password strength
        is_valid, errors = validate_password_strength(update_data["password"])
        if not is_valid:
            raise ValueError(f"Password validation failed: {', '.join(errors)}")

        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        update_data["password_changed_at"] = datetime.utcnow()

    for field, value in update_data.items():
        setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Authenticate user by username and password"""
    user = await get_user_by_username(db, username)
    if not user:
        return None

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        return None

    if not verify_password(password, user.hashed_password):
        # Increment failed login attempts
        user.failed_login_attempts += 1

        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)

        await db.commit()
        return None

    if not user.is_active:
        return None

    # Check if password is expired
    if is_password_expired(user.password_changed_at):
        # User can still login but should be prompted to change password
        pass

    # Reset failed login attempts on successful authentication
    user.failed_login_attempts = 0
    user.locked_until = None

    await db.commit()
    return user


async def update_last_login(db: AsyncSession, user: User) -> User:
    """Update user's last login timestamp"""
    user.last_login = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user


async def enable_mfa(db: AsyncSession, user: User, secret: str) -> User:
    """Enable MFA for a user"""
    user.mfa_enabled = True
    user.mfa_secret = secret
    await db.commit()
    await db.refresh(user)
    return user


async def disable_mfa(db: AsyncSession, user: User) -> User:
    """Disable MFA for a user"""
    user.mfa_enabled = False
    user.mfa_secret = None
    await db.commit()
    await db.refresh(user)
    return user


async def change_password(
    db: AsyncSession,
    user: User,
    old_password: str,
    new_password: str,
) -> User:
    """Change user password"""
    # Verify old password
    if not verify_password(old_password, user.hashed_password):
        raise ValueError("Incorrect password")

    # Validate new password strength
    is_valid, errors = validate_password_strength(new_password)
    if not is_valid:
        raise ValueError(f"Password validation failed: {', '.join(errors)}")

    # Update password
    user.hashed_password = get_password_hash(new_password)
    user.password_changed_at = datetime.utcnow()
    user.failed_login_attempts = 0  # Reset failed attempts
    user.locked_until = None  # Unlock account

    await db.commit()
    await db.refresh(user)
    return user


async def reset_password(db: AsyncSession, user: User, new_password: str) -> User:
    """Reset user password (admin function or password reset flow)"""
    # Validate new password strength
    is_valid, errors = validate_password_strength(new_password)
    if not is_valid:
        raise ValueError(f"Password validation failed: {', '.join(errors)}")

    user.hashed_password = get_password_hash(new_password)
    user.password_changed_at = datetime.utcnow()
    user.failed_login_attempts = 0
    user.locked_until = None

    await db.commit()
    await db.refresh(user)
    return user


async def count_users(db: AsyncSession) -> int:
    """Count total number of users"""
    from sqlalchemy import func
    result = await db.execute(select(func.count(User.id)))
    return result.scalar()
