"""Schemas for audit log API responses."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class AuditLogResponse(BaseModel):
    """Response model for a single audit log entry."""

    id: int
    timestamp: datetime
    user_id: Optional[int]
    username: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_path: Optional[str]
    request_method: Optional[str]
    success: bool
    failure_reason: Optional[str]

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Response model for a list of audit logs."""

    total: int
    items: list[AuditLogResponse]
    limit: int
    offset: int
    has_more: bool


class AuditLogQueryParams(BaseModel):
    """Query parameters for filtering audit logs."""

    user_id: Optional[int] = None
    username: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    success: Optional[bool] = None
    limit: int = 100
    offset: int = 0

    class Config:
        extra = "allow"


class AuditLogStatsResponse(BaseModel):
    """Response model for audit log statistics."""

    total_logs: int
    by_action: dict[str, int]
    by_resource_type: dict[str, int]
    by_user: dict[str, int]
    failed_operations: int
    date_range_start: Optional[datetime]
    date_range_end: Optional[datetime]
