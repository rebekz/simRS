"""Notification Schemas

Pydantic schemas for notification system.
STORY-058: Notification System
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum


class NotificationChannel(str, Enum):
    """Channels for sending notifications"""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationType(str, Enum):
    """Types of notifications"""
    APPOINTMENT_REMINDER = "appointment_reminder"
    APPOINTMENT_CONFIRMATION = "appointment_confirmation"
    APPOINTMENT_CANCELLATION = "appointment_cancellation"
    APPOINTMENT_RESCHEDULING = "appointment_rescheduling"
    PRESCRIPTION_READY = "prescription_ready"
    TEST_RESULTS = "test_results"
    BILLING_PAYMENT = "billing_payment"
    SYSTEM_ALERT = "system_alert"
    MARKETING = "marketing"


class NotificationStatus(str, Enum):
    """Status of notification delivery"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationPriority(str, Enum):
    """Priority levels for notifications"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TemplateCategory(str, Enum):
    """Categories for notification templates"""
    APPOINTMENT = "appointment"
    PRESCRIPTION = "prescription"
    MEDICAL = "medical"
    BILLING = "billing"
    SYSTEM = "system"
    MARKETING = "marketing"


class TemplateLanguage(str, Enum):
    """Supported languages for templates"""
    INDONESIAN = "id"
    ENGLISH = "en"


class SendNotificationRequest(BaseModel):
    """Request to send a single notification"""
    recipient_id: int = Field(..., description="User ID of the recipient")
    recipient_type: str = Field(..., description="Type of recipient (patient, staff, etc.)")
    channel: NotificationChannel = Field(..., description="Notification channel")
    type: NotificationType = Field(..., description="Notification type")
    priority: NotificationPriority = Field(NotificationPriority.NORMAL, description="Notification priority")
    subject: Optional[str] = Field(None, max_length=255, description="Notification subject (for email/push)")
    message: str = Field(..., min_length=1, max_length=5000, description="Notification message body")
    data: Optional[dict] = Field(None, description="Additional data for template rendering")
    scheduled_for: Optional[datetime] = Field(None, description="Schedule for future delivery")

    @field_validator('message')
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        """Sanitize notification message"""
        return ' '.join(v.split())

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "recipient_id": 123,
            "recipient_type": "patient",
            "channel": "whatsapp",
            "type": "appointment_reminder",
            "priority": "normal",
            "subject": "Pengingat Janji Temu",
            "message": "Halo {name}, ini adalah pengingat untuk janji temu Anda besok pukul {time}.",
            "data": {"name": "Budi", "time": "09:00"},
            "scheduled_for": None
        }
    })


class SendNotificationResponse(BaseModel):
    """Response after sending a notification"""
    notification_id: int
    status: NotificationStatus
    message: str
    estimated_delivery: Optional[datetime] = None


class BulkSendRequest(BaseModel):
    """Request to send bulk notifications"""
    recipient_ids: List[int] = Field(..., min_length=1, max_length=1000, description="List of recipient user IDs")
    recipient_type: str = Field(..., description="Type of recipients (patient, staff, etc.)")
    channel: NotificationChannel = Field(..., description="Notification channel")
    type: NotificationType = Field(..., description="Notification type")
    priority: NotificationPriority = Field(NotificationPriority.NORMAL, description="Notification priority")
    subject: Optional[str] = Field(None, max_length=255, description="Notification subject")
    message: str = Field(..., min_length=1, max_length=5000, description="Notification message body")
    data: Optional[dict] = Field(None, description="Additional data for template rendering (common to all)")
    scheduled_for: Optional[datetime] = Field(None, description="Schedule for future delivery")

    @field_validator('message')
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        """Sanitize notification message"""
        return ' '.join(v.split())

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "recipient_ids": [123, 124, 125],
            "recipient_type": "patient",
            "channel": "email",
            "type": "system_alert",
            "priority": "high",
            "subject": "Pemeliharaan Sistem",
            "message": "Sistem akan melakukan pemeliharaan pada tanggal {date}.",
            "data": {"date": "15 Januari 2026"},
            "scheduled_for": None
        }
    })


class BulkSendResponse(BaseModel):
    """Response after sending bulk notifications"""
    notification_ids: List[int]
    total_recipients: int
    successful_count: int
    failed_count: int
    message: str


class NotificationStatusResponse(BaseModel):
    """Response for notification status"""
    notification_id: int
    status: NotificationStatus
    channel: NotificationChannel
    type: NotificationType
    recipient_id: int
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    retry_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationHistoryItem(BaseModel):
    """Item in notification history"""
    notification_id: int
    channel: NotificationChannel
    type: NotificationType
    status: NotificationStatus
    priority: NotificationPriority
    subject: Optional[str] = None
    message_preview: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationHistoryResponse(BaseModel):
    """Response for notification history"""
    notifications: List[NotificationHistoryItem]
    total_count: int
    page: int
    per_page: int
    statistics: dict


class TemplateCreateRequest(BaseModel):
    """Request to create a notification template"""
    name: str = Field(..., min_length=3, max_length=100, description="Template name")
    category: TemplateCategory = Field(..., description="Template category")
    language: TemplateLanguage = Field(TemplateLanguage.INDONESIAN, description="Template language")
    channel: NotificationChannel = Field(..., description="Notification channel")
    type: NotificationType = Field(..., description="Notification type")
    subject_template: Optional[str] = Field(None, max_length=255, description="Subject template with placeholders")
    message_template: str = Field(..., min_length=1, max_length=5000, description="Message template with placeholders")
    variables: List[str] = Field(..., description="List of variable names used in templates")
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    is_active: bool = Field(True, description="Whether template is active")

    @field_validator('message_template')
    @classmethod
    def validate_message_template(cls, v: str) -> str:
        """Validate message template syntax"""
        # Check for balanced braces
        if v.count('{') != v.count('}'):
            raise ValueError('Unbalanced braces in message template')
        return ' '.join(v.split())

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Appointment Reminder WhatsApp",
            "category": "appointment",
            "language": "id",
            "channel": "whatsapp",
            "type": "appointment_reminder",
            "subject_template": "Pengingat Janji Temu - {clinic_name}",
            "message_template": "Halo {patient_name}, ini pengingat janji temu Anda pada {appointment_date} pukul {appointment_time} di {clinic_name}. Mohon datang 15 menit sebelumnya.",
            "variables": ["patient_name", "appointment_date", "appointment_time", "clinic_name"],
            "description": "Template pengingat janji temu via WhatsApp",
            "is_active": True
        }
    })


class TemplateUpdateRequest(BaseModel):
    """Request to update a notification template"""
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Template name")
    subject_template: Optional[str] = Field(None, max_length=255, description="Subject template with placeholders")
    message_template: Optional[str] = Field(None, min_length=1, max_length=5000, description="Message template with placeholders")
    variables: Optional[List[str]] = Field(None, description="List of variable names used in templates")
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    is_active: Optional[bool] = Field(None, description="Whether template is active")

    @field_validator('message_template')
    @classmethod
    def validate_message_template(cls, v: Optional[str]) -> Optional[str]:
        """Validate message template syntax"""
        if v is not None:
            if v.count('{') != v.count('}'):
                raise ValueError('Unbalanced braces in message template')
            return ' '.join(v.split())
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Updated Template Name",
            "message_template": "Updated message template with {placeholder}.",
            "is_active": True
        }
    })


class TemplateResponse(BaseModel):
    """Response for template details"""
    template_id: int
    name: str
    category: TemplateCategory
    language: TemplateLanguage
    channel: NotificationChannel
    type: NotificationType
    subject_template: Optional[str] = None
    message_template: str
    variables: List[str]
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TemplateListResponse(BaseModel):
    """Response for template list"""
    templates: List[TemplateResponse]
    total_count: int
    page: int
    per_page: int


class NotificationPreferenceRequest(BaseModel):
    """Request to update notification preferences"""
    channel_preferences: dict = Field(
        ...,
        description="Channel-specific preferences. Keys: email, sms, whatsapp, push, in_app. Values: bool or dict with type settings."
    )
    type_preferences: Optional[dict] = Field(
        None,
        description="Type-specific preferences. Keys: notification types. Values: bool or channel settings."
    )
    quiet_hours_start: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", description="Quiet hours start time (HH:MM)")
    quiet_hours_end: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", description="Quiet hours end time (HH:MM)")
    timezone: Optional[str] = Field(None, max_length=50, description="User timezone")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "channel_preferences": {
                "email": True,
                "sms": False,
                "whatsapp": True,
                "push": True,
                "in_app": True
            },
            "type_preferences": {
                "appointment_reminder": {"email": True, "whatsapp": True, "sms": False},
                "marketing": False
            },
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "timezone": "Asia/Jakarta"
        }
    })


class NotificationPreferenceItem(BaseModel):
    """Single notification preference item"""
    user_id: int
    setting_key: str
    setting_value: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationPreferenceResponse(BaseModel):
    """Response for notification preferences"""
    preferences: List[NotificationPreferenceItem]

    model_config = ConfigDict(from_attributes=True)


class NotificationDetail(BaseModel):
    """Detailed notification information"""
    id: int
    recipient_id: int
    channel: NotificationChannel
    type: NotificationType
    status: NotificationStatus
    priority: NotificationPriority
    subject: Optional[str] = None
    message: str
    data: Optional[dict] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
