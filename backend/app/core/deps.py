from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import decode_token, hash_token
from app.db.session import get_db
from app.models.user import User as UserModel
from app.models.session import Session as UserSession
from app.models.permission import Permission

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    result = await db.execute(select(User).filter(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Check if token is revoked
    token_hash = hash_token(token)
    result = await db.execute(
        select(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.token_hash == token_hash,
            UserSession.is_revoked == True
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    return user


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return current_user


async def get_current_superuser(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """Get current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


class PermissionChecker:
    """Dependency class for checking user permissions"""

    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    def __call__(self, current_user: UserModel = Depends(get_current_user)) -> UserModel:
        """Check if user has required permission"""
        if current_user.is_superuser:
            return current_user

        user_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role

        # Check if permission exists for this role
        # This will be loaded from database in a real implementation
        # For now, we'll do a basic check based on role definitions
        # TODO: Implement actual permission checking

        # For now, allow all authenticated users
        return current_user

        # Uncomment below when permission checking is fully implemented
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail=f"Not enough permissions to {self.action} {self.resource}",
        # )


def require_permission(resource: str, action: str) -> PermissionChecker:
    """Factory function to create a PermissionChecker instance"""
    return PermissionChecker(resource, action)


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers (proxy/load balancer)
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    x_real_ip = request.headers.get("X-Real-IP")
    if x_real_ip:
        return x_real_ip

    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Extract user agent from request"""
    return request.headers.get("User-Agent", "unknown")


async def get_request_info(request: Request) -> dict:
    """Get request metadata for logging"""
    return {
        "ip_address": get_client_ip(request),
        "user_agent": get_user_agent(request),
        "request_path": request.url.path,
        "request_method": request.method,
    }
