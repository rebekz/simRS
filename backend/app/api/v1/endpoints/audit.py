"""Audit log API endpoints - admin only access.

STORY-003: Audit Logging System

Provides endpoints for:
- Querying and filtering audit logs
- Exporting audit logs to CSV
- Audit log statistics
- Sensitive operation alerting
- Retention policy management

Python 3.5+ compatible
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional, Dict, Any
from datetime import datetime
import csv
import io

from app.db.session import get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.audit import (
    AuditLogResponse,
    AuditLogListResponse,
    AuditLogQueryParams,
    AuditLogStatsResponse,
)
from app.core.deps import get_current_user, get_current_admin_user
from app.services.audit import (
    get_query_service,
    get_stats_service,
    get_export_service,
    get_alert_service,
    get_retention_service,
)

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class ManualAuditLogRequest(BaseModel):
    """Request model for manual audit log creation"""
    action: str = Field(..., description="Action performed (CREATE, READ, UPDATE, DELETE)")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(None, description="ID of specific resource")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    success: bool = Field(True, description="Whether operation succeeded")
    failure_reason: Optional[str] = Field(None, description="Reason for failure")


class RetentionCleanupResponse(BaseModel):
    """Response model for retention cleanup operation"""
    cutoff_date: str
    retention_years: int
    logs_to_delete: int
    logs_deleted: int
    dry_run: bool


@router.get("/logs", response_model=AuditLogListResponse, status_code=status.HTTP_200_OK)
async def get_audit_logs(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    user_id: Optional[int] = Query(None),
    username: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    success: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    Get audit logs with filters (admin only).

    Requires audit:read permission.
    """
    # Check permission
    from app.core.deps import require_permission
    await require_permission(db, current_user, "audit:read")

    # Build query
    query = select(AuditLog)

    conditions = []
    if user_id is not None:
        conditions.append(AuditLog.user_id == user_id)
    if username is not None:
        conditions.append(AuditLog.username.ilike(f"%{username}%"))
    if action is not None:
        conditions.append(AuditLog.action == action)
    if resource_type is not None:
        conditions.append(AuditLog.resource_type == resource_type)
    if resource_id is not None:
        conditions.append(AuditLog.resource_id == resource_id)
    if start_date is not None:
        conditions.append(AuditLog.timestamp >= start_date)
    if end_date is not None:
        conditions.append(AuditLog.timestamp <= end_date)
    if success is not None:
        conditions.append(AuditLog.success == success)

    if conditions:
        query = query.where(and_(*conditions))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(AuditLog.timestamp.desc())
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    logs = result.scalars().all()

    return AuditLogListResponse(
        total=total,
        items=[AuditLogResponse.model_validate(log) for log in logs],
        limit=limit,
        offset=offset,
        has_more=offset + limit < total,
    )


@router.get("/logs/{log_id}", response_model=AuditLogResponse, status_code=status.HTTP_200_OK)
async def get_audit_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single audit log entry by ID (admin only).

    Requires audit:read permission.
    """
    await require_permission(db, current_user, "audit:read")

    result = await db.execute(select(AuditLog).where(AuditLog.id == log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )

    return AuditLogResponse.model_validate(log)


@router.get("/logs/stats", response_model=AuditLogStatsResponse)
async def get_audit_log_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """
    Get audit log statistics (admin only).

    Requires audit:read permission.
    """
    await require_permission(db, current_user, "audit:read")

    # Build base query with date filters
    base_query = select(AuditLog)
    conditions = []
    if start_date:
        conditions.append(AuditLog.timestamp >= start_date)
    if end_date:
        conditions.append(AuditLog.timestamp <= end_date)
    if conditions:
        base_query = base_query.where(and_(*conditions))

    # Total logs
    total_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0

    # By action
    action_query = select(
        AuditLog.action,
        func.count().label('count')
    ).select_from(base_query.subquery()).group_by(AuditLog.action)
    action_result = await db.execute(action_query)
    by_action = {row.action: row.count for row in action_result}

    # By resource type
    resource_query = select(
        AuditLog.resource_type,
        func.count().label('count')
    ).select_from(base_query.subquery()).group_by(AuditLog.resource_type)
    resource_result = await db.execute(resource_query)
    by_resource_type = {row.resource_type: row.count for row in resource_result}

    # By user
    user_query = select(
        AuditLog.username,
        func.count().label('count')
    ).select_from(base_query.subquery()).group_by(AuditLog.username).limit(10)
    user_result = await db.execute(user_query)
    by_user = {row.username: row.count for row in user_result if row.username}

    # Failed operations
    failed_query = select(func.count()).select_from(
        base_query.where(AuditLog.success == False).subquery()
    )
    failed_result = await db.execute(failed_query)
    failed_operations = failed_result.scalar() or 0

    return AuditLogStatsResponse(
        total_logs=total,
        by_action=by_action,
        by_resource_type=by_resource_type,
        by_user=by_user,
        failed_operations=failed_operations,
        date_range_start=start_date,
        date_range_end=end_date,
    )


@router.get("/logs/export")
async def export_audit_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    format: str = Query("csv", pattern="^(csv|excel)$"),
):
    """
    Export audit logs to CSV/Excel (admin only).

    Requires audit:read permission.
    Streams the response for large datasets.
    """
    await require_permission(db, current_user, "audit:read")

    # Build query (same as get_audit_logs)
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
        query = query.where(and_(*conditions))

    query = query.order_by(AuditLog.timestamp.desc())

    result = await db.execute(query)
    logs = result.scalars().all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "ID", "Timestamp", "User ID", "Username", "Action",
        "Resource Type", "Resource ID", "IP Address",
        "Request Path", "Request Method", "Success",
        "Failure Reason"
    ])

    # Data rows
    for log in logs:
        writer.writerow([
            log.id,
            log.timestamp.isoformat(),
            log.user_id,
            log.username,
            log.action,
            log.resource_type,
            log.resource_id,
            log.ip_address,
            log.request_path,
            log.request_method,
            log.success,
            log.failure_reason,
        ])

    # Reset pointer to beginning
    output.seek(0)

    # Generate filename with timestamp
    filename = f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    # Return streaming response
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
        },
    )


@router.post("/logs/manual", status_code=status.HTTP_201_CREATED)
async def create_manual_audit_log(
    request: ManualAuditLogRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a manual audit log entry (admin only).

    Use this for operations that aren't automatically logged by the middleware.
    Requires audit:write permission.
    """
    from app.core.deps import require_permission
    from app.core.audit_middleware import get_audit_logger

    await require_permission(db, current_user, "audit:write")

    try:
        audit_logger = get_audit_logger(db)

        audit_log = await audit_logger.create_audit_log(
            user_id=current_user.id,
            username=current_user.username,
            action=request.action,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            ip_address=None,  # Manual logs don't have request context
            user_agent="Manual Entry",
            request_path=None,
            request_method=None,
            request_body=str(request.details) if request.details else None,
            response_status=200 if request.success else 400,
            success=request.success,
            failure_reason=request.failure_reason,
            additional_data=request.details,
        )

        if not audit_log:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create audit log"
            )

        # Commit the transaction
        await db.commit()

        # Check for sensitive operation alerting
        alert_service = get_alert_service(db)
        await alert_service.check_and_alert_sensitive_operation(audit_log)
        await db.commit()

        return {
            "id": audit_log.id,
            "message": "Audit log created successfully",
            "timestamp": audit_log.timestamp.isoformat() if audit_log.timestamp else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create audit log: {}".format(str(e))
        )


@router.post("/logs/cleanup", response_model=RetentionCleanupResponse)
async def cleanup_old_audit_logs(
    dry_run: bool = Query(True, description="If true, only report what would be deleted"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Clean up audit logs older than retention period (admin only).

    Default retention is 6 years per UU 27/2022 requirements.
    Requires admin privileges.
    """
    try:
        retention_service = get_retention_service(db)
        result = await retention_service.cleanup_old_logs(dry_run=dry_run)

        # Commit if not dry run
        if not dry_run:
            await db.commit()

        return RetentionCleanupResponse(**result)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup audit logs: {}".format(str(e))
        )


@router.get("/logs/retention-info")
async def get_retention_info(
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get audit log retention policy information (admin only).

    Returns retention periods for different types of audit logs.
    """
    from app.services.audit import AuditRetentionService

    return {
        "retention_policies": AuditRetentionService.RETENTION_POLICIES,
        "description": "Audit log retention periods in years per UU 27/2022 compliance",
        "default_retention_years": AuditRetentionService.RETENTION_POLICIES["default"],
        "patient_data_retention_years": AuditRetentionService.RETENTION_POLICIES["patient_data"],
        "financial_retention_years": AuditRetentionService.RETENTION_POLICIES["financial"],
        "system_retention_years": AuditRetentionService.RETENTION_POLICIES["system"],
    }


from fastapi import Request  # Add at top of file if not already imported
