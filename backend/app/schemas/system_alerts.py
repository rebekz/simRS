"""System Alerts Schemas

Pydantic schemas for system alert management.
STORY-022-06: System Alerts
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum


class AlertSeverity(str, Enum):
    """Severity levels for system alerts"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, Enum):
    """Status of system alerts"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AlertCategory(str, Enum):
    """Categories of system alerts"""
    SYSTEM = "system"
    DATABASE = "database"
    API = "api"
    SECURITY = "security"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"
    RESOURCE = "resource"
    BACKUP = "backup"


class SystemAlertCreate(BaseModel):
    """Request schema for creating a system alert"""
    title: str = Field(..., min_length=3, max_length=255, description="Alert title")
    description: str = Field(..., min_length=10, max_length=5000, description="Detailed description of the alert")
    severity: AlertSeverity = Field(..., description="Severity level of the alert")
    category: AlertCategory = Field(..., description="Category of the alert")
    source: str = Field(..., max_length=100, description="Source system or component that generated the alert")
    affected_service: Optional[str] = Field(None, max_length=100, description="Service or component affected by the alert")
    metadata: Optional[dict] = Field(None, description="Additional metadata related to the alert")
    assigned_to: Optional[int] = Field(None, description="User ID of the person assigned to handle the alert")
    tags: Optional[List[str]] = Field(None, description="List of tags for categorization")
    escalation_level: int = Field(0, ge=0, le=5, description="Escalation level (0-5)")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "Database Connection Pool Exhausted",
            "description": "The database connection pool has reached 95% capacity. Immediate investigation required.",
            "severity": "critical",
            "category": "database",
            "source": "postgres_primary",
            "affected_service": "patient_registration",
            "metadata": {
                "connection_usage": "95%",
                "total_connections": 100,
                "active_connections": 95
            },
            "assigned_to": 1,
            "tags": ["database", "performance", "urgent"],
            "escalation_level": 0
        }
    })


class SystemAlertUpdate(BaseModel):
    """Request schema for updating a system alert"""
    title: Optional[str] = Field(None, min_length=3, max_length=255, description="Alert title")
    description: Optional[str] = Field(None, min_length=10, max_length=5000, description="Detailed description of the alert")
    severity: Optional[AlertSeverity] = Field(None, description="Severity level of the alert")
    status: Optional[AlertStatus] = Field(None, description="Status of the alert")
    category: Optional[AlertCategory] = Field(None, description="Category of the alert")
    assigned_to: Optional[int] = Field(None, description="User ID of the person assigned to handle the alert")
    resolution_notes: Optional[str] = Field(None, max_length=5000, description="Notes about how the alert was resolved")
    metadata: Optional[dict] = Field(None, description="Additional metadata related to the alert")
    tags: Optional[List[str]] = Field(None, description="List of tags for categorization")
    escalation_level: Optional[int] = Field(None, ge=0, le=5, description="Escalation level (0-5)")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "status": "acknowledged",
            "assigned_to": 5,
            "escalation_level": 1
        }
    })


class SystemAlertResponse(BaseModel):
    """Response schema for system alert details"""
    id: int
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    category: AlertCategory
    source: str
    affected_service: Optional[str] = None
    metadata: Optional[dict] = None
    assigned_to: Optional[int] = None
    assigned_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolution_notes: Optional[str] = None
    closed_at: Optional[datetime] = None
    closed_by: Optional[int] = None
    tags: Optional[List[str]] = None
    escalation_level: int = 0
    escalation_history: Optional[List[dict]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SystemAlertListResponse(BaseModel):
    """Response schema for paginated system alert list"""
    alerts: List[SystemAlertResponse]
    total_count: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_previous: bool
    filters_applied: Optional[dict] = None


class AlertRuleCreate(BaseModel):
    """Request schema for creating an alert rule"""
    name: str = Field(..., min_length=3, max_length=100, description="Rule name")
    description: Optional[str] = Field(None, max_length=500, description="Rule description")
    category: AlertCategory = Field(..., description="Category this rule applies to")
    severity: AlertSeverity = Field(..., description="Severity level for alerts generated by this rule")
    condition: dict = Field(..., description="Condition logic for triggering the alert")
    threshold_value: Optional[float] = Field(None, description="Threshold value for triggering the alert")
    comparison_operator: Optional[str] = Field(None, max_length=10, description="Comparison operator (gt, lt, eq, gte, lte)")
    time_window_minutes: Optional[int] = Field(None, ge=1, description="Time window in minutes to check the condition")
    notification_channels: List[str] = Field(..., min_length=1, description="Channels to send alert notifications")
    is_active: bool = Field(True, description="Whether the rule is active")
    cooldown_minutes: int = Field(5, ge=0, description="Cooldown period before triggering the same alert again")
    escalation_enabled: bool = Field(False, description="Whether auto-escalation is enabled")
    escalation_minutes: Optional[int] = Field(None, ge=1, description="Minutes before auto-escalation")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "High CPU Usage Alert",
            "description": "Alert when CPU usage exceeds 90% for 5 minutes",
            "category": "system",
            "severity": "high",
            "condition": {
                "metric": "cpu_usage_percent",
                "operator": "gt",
                "threshold": 90
            },
            "threshold_value": 90.0,
            "comparison_operator": "gt",
            "time_window_minutes": 5,
            "notification_channels": ["email", "slack"],
            "is_active": True,
            "cooldown_minutes": 10,
            "escalation_enabled": True,
            "escalation_minutes": 30
        }
    })


class AlertRuleUpdate(BaseModel):
    """Request schema for updating an alert rule"""
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Rule name")
    description: Optional[str] = Field(None, max_length=500, description="Rule description")
    category: Optional[AlertCategory] = Field(None, description="Category this rule applies to")
    severity: Optional[AlertSeverity] = Field(None, description="Severity level for alerts generated by this rule")
    condition: Optional[dict] = Field(None, description="Condition logic for triggering the alert")
    threshold_value: Optional[float] = Field(None, description="Threshold value for triggering the alert")
    comparison_operator: Optional[str] = Field(None, max_length=10, description="Comparison operator (gt, lt, eq, gte, lte)")
    time_window_minutes: Optional[int] = Field(None, ge=1, description="Time window in minutes to check the condition")
    notification_channels: Optional[List[str]] = Field(None, min_length=1, description="Channels to send alert notifications")
    is_active: Optional[bool] = Field(None, description="Whether the rule is active")
    cooldown_minutes: Optional[int] = Field(None, ge=0, description="Cooldown period before triggering the same alert again")
    escalation_enabled: Optional[bool] = Field(None, description="Whether auto-escalation is enabled")
    escalation_minutes: Optional[int] = Field(None, ge=1, description="Minutes before auto-escalation")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "is_active": False,
            "threshold_value": 95.0
        }
    })


class AlertRuleResponse(BaseModel):
    """Response schema for alert rule details"""
    id: int
    name: str
    description: Optional[str] = None
    category: AlertCategory
    severity: AlertSeverity
    condition: dict
    threshold_value: Optional[float] = None
    comparison_operator: Optional[str] = None
    time_window_minutes: Optional[int] = None
    notification_channels: List[str]
    is_active: bool
    cooldown_minutes: int
    escalation_enabled: bool
    escalation_minutes: Optional[int] = None
    trigger_count: int = 0
    last_triggered_at: Optional[datetime] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AlertRuleListResponse(BaseModel):
    """Response schema for paginated alert rule list"""
    rules: List[AlertRuleResponse]
    total_count: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class AlertStatistics(BaseModel):
    """Response schema for alert statistics"""
    total_alerts: int
    open_alerts: int
    acknowledged_alerts: int
    resolved_alerts: int
    closed_alerts: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    average_resolution_time_minutes: Optional[float] = None
    alerts_by_category: dict
    alerts_by_source: dict
    recent_escalations: int
    active_rules: int


class AlertAcknowledgeRequest(BaseModel):
    """Request schema for acknowledging an alert"""
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes when acknowledging the alert")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "notes": "Investigating the issue. Assigned to database team."
        }
    })


class AlertResolveRequest(BaseModel):
    """Request schema for resolving an alert"""
    resolution_notes: str = Field(..., min_length=10, max_length=5000, description="Detailed notes about the resolution")
    root_cause: Optional[str] = Field(None, max_length=1000, description="Root cause analysis")
    preventive_action: Optional[str] = Field(None, max_length=1000, description="Preventive actions taken")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "resolution_notes": "Increased connection pool size from 100 to 150. Updated application configuration.",
            "root_cause": "Sudden spike in patient registrations exceeded connection pool capacity",
            "preventive_action": "Implemented connection pool monitoring and auto-scaling"
        }
    })


class AlertEscalateRequest(BaseModel):
    """Request schema for escalating an alert"""
    escalation_level: int = Field(..., ge=1, le=5, description="New escalation level")
    reason: str = Field(..., min_length=10, max_length=1000, description="Reason for escalation")
    assign_to: Optional[int] = Field(None, description="User ID to assign the escalated alert to")
    notify_channels: List[str] = Field(..., min_length=1, description="Channels to notify about escalation")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "escalation_level": 2,
            "reason": "Issue not resolved within SLA. Requires senior DBA intervention.",
            "assign_to": 10,
            "notify_channels": ["email", "slack", "sms"]
        }
    })
