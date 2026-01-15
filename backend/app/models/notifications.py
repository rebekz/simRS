from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Index, Time
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid


class Notification(Base):
    """
    Notification model for the notification system.
    Represents a notification to be sent to recipients via various channels.
    """
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    recipient_id = Column(Integer, nullable=False, index=True)
    recipient_type = Column(
        SQLEnum("patient", "staff", "system", name="notification_recipient_type"),
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
    subject = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    metadata = Column(JSONB, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failed_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=datetime.utcnow,
        onupdate=datetime.utcnow,
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


class NotificationTemplate(Base):
    """
    NotificationTemplate model for managing notification templates.
    Provides reusable templates for different types of notifications.
    """
    __tablename__ = "notification_templates"

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
    content_template = Column(Text, nullable=False)
    variables = Column(JSONB, nullable=True)  # List of available variables for template
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
        server_default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=datetime.utcnow,
        onupdate=datetime.utcnow,
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
    event_type = Column(
        SQLEnum("created", "queued", "sent", "delivered", "failed", "opened", "clicked",
                name="log_event_type"),
        nullable=False,
        index=True
    )
    channel = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    details = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=datetime.utcnow,
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
        Index("ix_notification_logs_notification_event", "notification_id", "event_type"),
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
    notification_type = Column(String(100), nullable=False)
    channel_enabled = Column(
        JSONB,
        nullable=False,
        default={"sms": True, "email": False, "whatsapp": True, "push": True, "in_app": True}
    )
    frequency = Column(
        SQLEnum("immediate", "hourly", "daily", "weekly", name="preference_frequency"),
        nullable=False,
        default="immediate"
    )
    quiet_hours_start = Column(Time, nullable=True)
    quiet_hours_end = Column(Time, nullable=True)
    language = Column(String(10), default="id", nullable=False)
    consent_given = Column(Boolean, default=True, nullable=False)
    consent_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_notification_preferences_user_type", "user_id", "user_type", "notification_type",
              unique=True),
        Index("ix_notification_preferences_user_id", "user_id"),
    )
