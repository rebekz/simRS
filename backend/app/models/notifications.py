from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Index, Time, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid


class NotificationStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationType(str, Enum):
    """Notification types"""
    APPOINTMENT_REMINDER = "appointment_reminder"
    MEDICATION_REMINDER = "medication_reminder"
    LAB_RESULT = "lab_result"
    PAYMENT_REMINDER = "payment_reminder"
    CRITICAL_ALERT = "critical_alert"
    SYSTEM_ALERT = "system_alert"
    QUEUE_UPDATE = "queue_update"


class Notification(Base):
    """
    Notification model for the notification system.
    Represents a notification to be sent to recipients via various channels.
    """
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    recipient_id = Column(Integer, nullable=False, index=True)
    user_type = Column(
        SQLEnum("patient", "doctor", "nurse", "staff", "admin", name="notification_user_type"),
        nullable=False,
        default="staff",
        index=True
    )
    notification_type = Column(
        SQLEnum("appointment_reminder", "medication_reminder", "lab_result",
                "payment_reminder", "critical_alert", "system_alert", "queue_update",
                name="notification_type"),
        nullable=False,
        index=True
    )
    channel = Column(
        SQLEnum("sms", "email", "whatsapp", "push", "in_app", name="notification_channel"),
        nullable=False,
        index=True
    )
    status = Column(
        SQLEnum("pending", "processing", "sent", "delivered", "failed", "cancelled",
                name="notification_status"),
        nullable=False,
        default="pending",
        index=True
    )
    priority = Column(
        SQLEnum("low", "normal", "high", "urgent", name="notification_priority"),
        nullable=False,
        default="normal",
        index=True
    )
    template_id = Column(
        Integer,
        ForeignKey("notification_templates.id", ondelete="SET NULL"),
        nullable=True
    )
    title = Column(String(500), nullable=True)  # Subject line for notifications
    message = Column(Text, nullable=False)  # Main message content
    message_id = Column(String(255), nullable=True)  # External provider message ID
    notification_metadata = Column(JSONB, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failed_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    template = relationship(
        "NotificationTemplate",
        back_populates="notifications"
    )
    logs = relationship(
        "NotificationLog",
        back_populates="notification",
        cascade="all, delete-orphan"
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_notifications_recipient_status", "recipient_id", "status"),
        Index("ix_notifications_type_status", "notification_type", "status"),
        Index("ix_notifications_scheduled_pending", "scheduled_at", "status"),
        Index("ix_notifications_channel_status", "channel", "status"),
    )


class OldNotificationTemplate(Base):
    """
    Deprecated: Use NotificationTemplate from notification_templates.py instead.
    This model is kept for backwards compatibility.
    """
    __tablename__ = "old_notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(
        SQLEnum("appointment", "medication", "lab_result", "payment", "system", "marketing",
                name="template_category"),
        nullable=False,
        index=True
    )
    language = Column(String(10), default="id", nullable=False, index=True)
    subject_template = Column(String(500), nullable=True)
    body_template = Column(Text, nullable=False)  # Changed from content_template to body_template
    variables = Column(JSONB, nullable=True)  # List of available variables for template
    description = Column(Text, nullable=True)  # Added description field
    tags = Column(JSONB, nullable=True)  # Added tags field
    is_active = Column(Boolean, default=True, nullable=False)  # Added is_active field
    status = Column(
        SQLEnum("draft", "active", "archived", name="template_status"),
        nullable=False,
        default="draft",
        index=True
    )
    version = Column(Integer, default=1, nullable=False)
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False
    )
    approved_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    notifications = relationship(
        "Notification",
        back_populates="template"
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_templates_category_status", "category", "status"),
        Index("ix_templates_language_status", "language", "status"),
        Index("ix_templates_name_status", "name", "status"),
    )


class OldNotificationTemplateVersion(Base):
    """
    Deprecated: Use NotificationTemplateVersion from notification_templates.py instead.
    This model is kept for backwards compatibility.
    """
    __tablename__ = "old_notification_template_versions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(
        Integer,
        ForeignKey("notification_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    version = Column(Integer, nullable=False)
    subject_template = Column(String(500), nullable=True)
    body_template = Column(Text, nullable=False)
    variables = Column(JSONB, nullable=True)
    change_description = Column(Text, nullable=True)
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    template = relationship("NotificationTemplate")

    # Indexes for common queries
    __table_args__ = (
        Index("ix_template_versions_template_version", "template_id", "version"),
    )


class NotificationLog(Base):
    """
    NotificationLog model for audit trail of notifications.
    Tracks all events and status changes for notifications.
    """
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status = Column(String(50), nullable=False)  # queued, sent, delivered, failed, etc.
    message = Column(Text, nullable=True)  # Human-readable log message
    error_details = Column(JSONB, nullable=True)  # Additional error/response details
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Relationships
    notification = relationship(
        "Notification",
        back_populates="logs"
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_notification_logs_notification_status", "notification_id", "status"),
        Index("ix_notification_logs_created_at", "created_at"),
    )


class NotificationPreference(Base):
    """
    NotificationPreference model for user notification preferences.
    Allows users to customize how they receive notifications.
    """
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_type = Column(
        SQLEnum("patient", "staff", name="preference_user_type"),
        nullable=False
    )
    notification_type = Column(String(100), nullable=False, index=True)
    email_enabled = Column(Boolean, default=True, nullable=False)
    sms_enabled = Column(Boolean, default=False, nullable=False)
    push_enabled = Column(Boolean, default=True, nullable=False)
    in_app_enabled = Column(Boolean, default=True, nullable=False)
    whatsapp_enabled = Column(Boolean, default=False, nullable=False)
    quiet_hours_start = Column(Time, nullable=True)
    quiet_hours_end = Column(Time, nullable=True)
    timezone = Column(String(50), default="Asia/Jakarta", nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_notification_preferences_user_type", "user_id", "user_type", "notification_type",
              unique=True),
        Index("ix_notification_preferences_user_id", "user_id"),
    )


class CriticalAlert(Base):
    """
    CriticalAlert model for tracking critical value alerts.
    Stores records of all critical values detected and their acknowledgment status.
    """
    __tablename__ = "critical_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    patient_name = Column(String(255), nullable=False)
    mrn = Column(String(50), nullable=False, index=True)

    # Test information
    test_name = Column(String(255), nullable=False)
    test_value = Column(String(100), nullable=False)
    test_unit = Column(String(50), nullable=False)
    critical_range = Column(String(100), nullable=False)

    # Ordering information
    ordering_physician_id = Column(Integer, nullable=True, index=True)
    patient_location = Column(String(255), nullable=True)

    # Result information
    result_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # Notification tracking
    notification_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notifications.id", ondelete="SET NULL"),
        nullable=True
    )

    # Acknowledgment tracking
    acknowledged = Column(Boolean, default=False, nullable=False, index=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(Integer, nullable=True)
    action_taken = Column(Text, nullable=True)

    # Escalation tracking
    escalation_level = Column(Integer, default=0, nullable=False)
    escalated_at = Column(DateTime(timezone=True), nullable=True)

    # Resolution tracking
    resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    notification = relationship("Notification", foreign_keys=[notification_id])

    # Indexes for common queries
    __table_args__ = (
        Index("ix_critical_alerts_patient_ack", "patient_id", "acknowledged"),
        Index("ix_critical_alerts_physician_unack", "ordering_physician_id", "acknowledged"),
        Index("ix_critical_alerts_result_time", "result_timestamp"),
        Index("ix_critical_alerts_escalation", "escalation_level", "acknowledged"),
    )


class AlertAcknowledgment(Base):
    """
    AlertAcknowledgment model for tracking detailed acknowledgment history.
    Stores all acknowledgment attempts and actions taken for critical alerts.
    """
    __tablename__ = "alert_acknowledgments"

    id = Column(Integer, primary_key=True, index=True)
    critical_alert_id = Column(
        UUID(as_uuid=True),
        ForeignKey("critical_alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    physician_id = Column(Integer, nullable=False, index=True)
    acknowledgment_type = Column(
        SQLEnum("acknowledged", "escalated", "resolved", name="acknowledgment_type"),
        nullable=False
    )
    action_taken = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)

    # Timestamp tracking
    acknowledged_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Response time tracking
    response_time_seconds = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    critical_alert = relationship("CriticalAlert", cascade="all, delete")

    # Indexes for common queries
    __table_args__ = (
        Index("ix_alert_acknowledgments_alert_time", "critical_alert_id", "acknowledged_at"),
        Index("ix_alert_acknowledgments_physician", "physician_id", "acknowledged_at"),
    )
