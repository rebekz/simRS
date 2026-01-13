from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from datetime import datetime, timedelta

from app.models.audit_log import AuditLog
from app.models.user import User


async def create_audit_log(
    db: AsyncSession,
    action: str,
    resource_type: str,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_path: Optional[str] = None,
    request_method: Optional[str] = None,
    success: bool = True,
    failure_reason: Optional[str] = None,
    additional_data: Optional[dict] = None,
) -> AuditLog:
    """Create an audit log entry"""
    audit_log = AuditLog(
        user_id=user_id,
        username=username,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        request_path=request_path,
        request_method=request_method,
        success=success,
        failure_reason=failure_reason,
        additional_data=additional_data,
    )

    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)

    return audit_log


async def get_user_audit_logs(
    db: AsyncSession,
    user_id: int,
    limit: int = 100,
    offset: int = 0,
) -> List[AuditLog]:
    """Get audit logs for a specific user"""
    result = await db.execute(
        select(AuditLog)
        .filter(AuditLog.user_id == user_id)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def get_audit_logs(
    db: AsyncSession,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[AuditLog]:
    """Get audit logs with optional filters"""
    query = select(AuditLog)

    conditions = []
    if user_id is not None:
        conditions.append(AuditLog.user_id == user_id)
    if action is not None:
        conditions.append(AuditLog.action == action)
    if resource_type is not None:
        conditions.append(AuditLog.resource_type == resource_type)
    if start_date is not None:
        conditions.append(AuditLog.timestamp >= start_date)
    if end_date is not None:
        conditions.append(AuditLog.timestamp <= end_date)

    if conditions:
        query = query.filter(and_(*conditions))

    query = query.order_by(AuditLog.timestamp.desc())
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return result.scalars().all()


async def get_failed_login_attempts(
    db: AsyncSession,
    username: str,
    since: Optional[datetime] = None,
) -> List[AuditLog]:
    """Get failed login attempts for a username"""
    if since is None:
        since = datetime.utcnow() - timedelta(minutes=15)

    result = await db.execute(
        select(AuditLog).filter(
            AuditLog.username == username,
            AuditLog.action == "LOGIN",
            AuditLog.success == False,
            AuditLog.timestamp >= since
        ).order_by(AuditLog.timestamp.desc())
    )
    return result.scalars().all()


async def cleanup_old_audit_logs(
    db: AsyncSession,
    retention_years: int = 6,
) -> int:
    """Clean up old audit logs based on retention policy"""
    cutoff_date = datetime.utcnow() - timedelta(days=retention_years * 365)

    # In PostgreSQL, we'd use DELETE with RETURNING to get count
    # For now, we'll select then delete
    result = await db.execute(
        select(AuditLog).filter(AuditLog.timestamp < cutoff_date)
    )
    logs = result.scalars().all()

    count = len(logs)
    for log in logs:
        await db.delete(log)

    await db.commit()
    return count


async def count_audit_logs(db: AsyncSession) -> int:
    """Count total number of audit logs"""
    from sqlalchemy import func
    result = await db.execute(select(func.count(AuditLog.id)))
    return result.scalar()
