"""System Alert Endpoints

API endpoints for system alert management.
STORY-022-06: System Alerts (Downtime, Failures)

Python 3.5+ compatible
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user
from app.services.system_alert_service import SystemAlertService
from app.models.system_alerts import AlertSeverity, AlertStatus


router = APIRouter()


class AlertSeverityEnum(str, Enum):
    """Severity levels for system alerts"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class AlertStatusEnum(str, Enum):
    """Status of system alerts"""
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class AlertCategory(str, Enum):
    """Categories for system alerts"""
    SYSTEM_HEALTH = "system_health"
    DATABASE = "database"
    API = "api"
    EXTERNAL_INTEGRATION = "external_integration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BACKUP = "backup"
    NETWORK = "network"
    MAINTENANCE = "maintenance"


class SystemAlertCreateRequest(BaseModel):
    """Request to create a new system alert"""
    severity: AlertSeverityEnum
    category: AlertCategory
    title: str = Field(..., min_length=1, max_length=255, description="Alert title")
    message: str = Field(..., min_length=1, max_length=5000, description="Alert message")
    source: str = Field(..., max_length=100, description="Alert source (system, component name)")
    affected_service: Optional[str] = Field(None, max_length=100, description="Affected service name")
    metadata: Optional[dict] = Field(None, description="Additional alert metadata")
    related_alert_id: Optional[int] = Field(None, description="Related alert ID for grouping")
    estimated_resolution: Optional[datetime] = Field(None, description="Estimated resolution time")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "severity": "HIGH",
            "category": "external_integration",
            "title": "BPJS API Connection Failed",
            "message": "Failed to connect to BPJS API after 3 attempts.",
            "source": "bpjs_vclaim_service",
            "affected_service": "BPJS Integration",
            "metadata": {"error_code": "CONNECTION_TIMEOUT", "attempts": 3},
            "related_alert_id": None,
            "estimated_resolution": None
        }
    })


class SystemAlertResponse(BaseModel):
    """Response for system alert details"""
    alert_id: int
    severity: str
    component: str
    alert_type: str
    message: str
    details: Optional[dict] = None
    status: str
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class AlertAcknowledgeRequest(BaseModel):
    """Request to acknowledge an alert"""
    note: Optional[str] = Field(None, max_length=1000, description="Acknowledgment note")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "note": "Investigating the issue. Assigned to network team."
        }
    })


class AlertResolveRequest(BaseModel):
    """Request to resolve an alert"""
    resolution_note: str = Field(..., min_length=1, max_length=2000, description="Resolution details")
    status: AlertStatusEnum = Field(AlertStatusEnum.RESOLVED, description="Final status (resolved or closed)")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "resolution_note": "Fixed network connectivity issue. BPJS API responding normally.",
            "status": "RESOLVED"
        }
    })


class AlertListResponse(BaseModel):
    """Response for alert list"""
    alerts: List[SystemAlertResponse]
    total_count: int
    page: int
    per_page: int
    total_pages: int


class AlertRuleCreateRequest(BaseModel):
    """Request to create an alert rule"""
    name: str = Field(..., min_length=3, max_length=100, description="Rule name")
    component: str = Field(..., max_length=100, description="System component")
    alert_type: str = Field(..., max_length=100, description="Alert type")
    severity: AlertSeverityEnum
    condition: dict = Field(..., description="Alert condition configuration")
    enabled: bool = Field(True, description="Whether rule is active")
    description: Optional[str] = Field(None, max_length=500, description="Rule description")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "High CPU Usage Alert",
            "component": "server",
            "alert_type": "high_cpu",
            "severity": "HIGH",
            "condition": {"metric": "cpu_usage_percent", "threshold": 80},
            "enabled": True,
            "description": "Alert when CPU usage exceeds 80% for more than 5 minutes"
        }
    })


class AlertRuleResponse(BaseModel):
    """Response for alert rule details"""
    rule_id: int
    name: str
    component: str
    alert_type: str
    severity: str
    condition: dict
    enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class AlertRuleListResponse(BaseModel):
    """Response for alert rules list"""
    rules: List[AlertRuleResponse]
    total_count: int


class AlertStatisticsResponse(BaseModel):
    """Response for alert statistics"""
    total: int
    by_severity: dict
    by_status: dict
    by_component: dict


@router.post("/system-alerts", response_model=SystemAlertResponse, operation_id="create_system_alert", status_code=status.HTTP_201_CREATED)
async def create_system_alert(
    request: SystemAlertCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new system alert

    Membuat sistem alert baru untuk notifikasi masalah atau kejadian penting dalam sistem.
    Semua user yang terautentikasi dapat membuat alert, biasanya dibuat oleh sistem monitoring otomatis.

    Field yang diperlukan:
    - **severity**: Tingkat severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)
    - **source**: Sumber alert (nama service, komponen, atau subsistem)
    - **message**: Deskripsi lengkap masalah atau kejadian

    Field opsional:
    - **metadata**: Data tambahan terkait alert (error codes, metrics, dll.)
    - **related_alert_id**: ID alert terkait untuk pengelompokan

    Severity levels:
    - **CRITICAL**: Sistem down, risiko kehilangan data, memerlukan respons segera
    - **HIGH**: Performa degraded, partial outage
    - **MEDIUM**: Kegagalan non-kritikal
    - **LOW**: Degrade performa
    - **INFO**: Notifikasi informasional

    Returns detail alert yang dibuat dengan alert_id.

    Raises:
    - 400: Jika validasi gagal
    - 401: Jika tidak terautentikasi
    """
    try:
        service = SystemAlertService(db)

        # Map category to component
        component_mapping = {
            "system_health": "system",
            "database": "database",
            "api": "api",
            "external_integration": "external_service",
            "performance": "application",
            "security": "security",
            "backup": "backup",
            "network": "network",
            "maintenance": "system"
        }
        component = component_mapping.get(request.category.value, request.source)

        # Build details from request
        details = request.metadata or {}
        if request.affected_service:
            details["affected_service"] = request.affected_service
        if request.estimated_resolution:
            details["estimated_resolution"] = request.estimated_resolution.isoformat()
        if request.related_alert_id:
            details["related_alert_id"] = request.related_alert_id

        # Create alert
        result = await service.create_alert(
            severity=request.severity.value,
            component=component,
            alert_type=request.category.value,
            message=request.message,
            details=details
        )

        return SystemAlertResponse(
            alert_id=result["alert_id"],
            severity=result["severity"],
            component=result["component"],
            alert_type=result["alert_type"],
            message=request.message,
            details=details,
            status=result["status"],
            acknowledged_by=None,
            acknowledged_at=None,
            resolved_at=None,
            created_at=result["created_at"],
            updated_at=result["created_at"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create system alert"
        )


@router.get("/system-alerts/{alert_id}", response_model=SystemAlertResponse, operation_id="get_system_alert")
async def get_system_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get system alert details"""
    try:
        service = SystemAlertService(db)
        result = await service.get_alert(alert_id)

        return SystemAlertResponse(**result)

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system alert"
        )


@router.put("/system-alerts/{alert_id}/acknowledge", response_model=SystemAlertResponse, operation_id="acknowledge_alert")
async def acknowledge_alert(
    alert_id: int,
    request: AlertAcknowledgeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Acknowledge a system alert"""
    try:
        service = SystemAlertService(db)
        result = await service.acknowledge_alert(alert_id, current_user.id)

        # Get full alert details
        alert_details = await service.get_alert(alert_id)

        # Add acknowledgment note to details if provided
        if request.note:
            if not alert_details["details"]:
                alert_details["details"] = {}
            alert_details["details"]["acknowledgment_note"] = request.note

        return SystemAlertResponse(**alert_details)

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge alert"
        )


@router.put("/system-alerts/{alert_id}/resolve", response_model=SystemAlertResponse, operation_id="resolve_alert")
async def resolve_alert(
    alert_id: int,
    request: AlertResolveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Resolve a system alert"""
    try:
        service = SystemAlertService(db)
        result = await service.resolve_alert(alert_id)

        # Get full alert details
        alert_details = await service.get_alert(alert_id)

        # Add resolution note to details
        if not alert_details["details"]:
            alert_details["details"] = {}
        alert_details["details"]["resolution_note"] = request.resolution_note
        alert_details["details"]["resolved_by"] = current_user.id
        alert_details["details"]["resolved_at"] = result["resolved_at"].isoformat() if result["resolved_at"] else None

        return SystemAlertResponse(**alert_details)

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve alert"
        )


@router.get("/system-alerts", response_model=AlertListResponse, operation_id="list_system_alerts")
async def list_system_alerts(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    severity: Optional[AlertSeverityEnum] = Query(None, description="Filter by severity"),
    status_filter: Optional[AlertStatusEnum] = Query(None, description="Filter by status", alias="status"),
    component: Optional[str] = Query(None, description="Filter by component"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List system alerts with filters"""
    try:
        service = SystemAlertService(db)

        # Convert severity enum to value if provided
        severity_value = severity.value if severity else None
        status_value = status_filter.value if status_filter else None

        result = await service.list_alerts(
            severity=severity_value,
            status=status_value,
            component=component,
            page=page,
            per_page=per_page
        )

        return AlertListResponse(
            alerts=[SystemAlertResponse(**alert) for alert in result["alerts"]],
            total_count=result["total_count"],
            page=page,
            per_page=per_page,
            total_pages=result["total_pages"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list system alerts"
        )


@router.get("/system-alerts/statistics", response_model=AlertStatisticsResponse, operation_id="get_alert_statistics")
async def get_alert_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get alert statistics"""
    try:
        service = SystemAlertService(db)

        # Get all alerts (no pagination)
        result = await service.list_alerts(page=1, per_page=10000)

        # Calculate statistics
        by_severity = {}
        by_status = {}
        by_component = {}

        for alert in result["alerts"]:
            # Count by severity
            severity = alert["severity"]
            by_severity[severity] = by_severity.get(severity, 0) + 1

            # Count by status
            status_val = alert["status"]
            by_status[status_val] = by_status.get(status_val, 0) + 1

            # Count by component
            component = alert["component"]
            by_component[component] = by_component.get(component, 0) + 1

        return AlertStatisticsResponse(
            total=result["total_count"],
            by_severity=by_severity,
            by_status=by_status,
            by_component=by_component
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alert statistics"
        )


@router.post("/system-alerts/rules", response_model=AlertRuleResponse, operation_id="create_alert_rule", status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    request: AlertRuleCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new alert rule (admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required."
        )

    try:
        service = SystemAlertService(db)

        result = await service.create_rule(
            name=request.name,
            component=request.component,
            alert_type=request.alert_type,
            severity=request.severity.value,
            condition=request.condition
        )

        return AlertRuleResponse(
            rule_id=result["rule_id"],
            name=result["name"],
            component=result["component"],
            alert_type=result["alert_type"],
            severity=result["severity"],
            enabled=result["enabled"],
            condition=request.condition,
            created_at=result["created_at"],
            updated_at=result["created_at"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create alert rule"
        )


@router.get("/system-alerts/rules", response_model=AlertRuleListResponse, operation_id="list_alert_rules")
async def list_alert_rules(
    enabled_only: bool = Query(True, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List alert rules"""
    try:
        service = SystemAlertService(db)
        rules = await service.list_rules(enabled_only=enabled_only)

        return AlertRuleListResponse(
            rules=[
                AlertRuleResponse(
                    rule_id=rule["rule_id"],
                    name=rule["name"],
                    component=rule["component"],
                    alert_type=rule["alert_type"],
                    severity=rule["severity"],
                    enabled=rule["enabled"],
                    condition=rule["condition"],
                    created_at=rule["created_at"],
                    updated_at=rule["updated_at"]
                )
                for rule in rules
            ],
            total_count=len(rules)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list alert rules"
        )
