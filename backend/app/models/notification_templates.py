"""Notification Template Models

STORY-071: Notification Template Management System
Database models for managing notification templates with versioning.

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum as SQLEnum, JSON, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class NotificationTemplate(Base):
    """Notification template model for managing notification message templates

    Allows system administrators to customize notification messages
    without code changes.
    """
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True, comment="Template name")
    category = Column(String(100), nullable=False, index=True, comment="Template category (appointment, queue, payment, etc.)")
    channel = Column(String(50), nullable=False, comment="Notification channel (sms, email, push, whatsapp)")
    language = Column(String(10), nullable=False, default="id", comment="Language code (id, en)")
    subject = Column(Text, nullable=True, comment="Message subject (for email/push)")
    body = Column(Text, nullable=False, comment="Message body with variable placeholders")
    variables = Column(JSON, nullable=True, comment="List of variables used in template")
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether template is active")
    is_default = Column(Boolean, default=False, nullable=False, comment="Whether this is the default template")
    version = Column(Integer, nullable=False, default=1, comment="Current version number")
    description = Column(Text, nullable=True, comment="Template description")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User who created template")
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User who last updated template")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    versions = relationship("NotificationTemplateVersion", back_populates="template", cascade="all, delete-orphan")
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])

    __table_args__ = (
        {"comment": "Notification templates for dynamic message management", "extend_existing": True},
    )


class NotificationTemplateVersion(Base):
    """Notification template version history

    Tracks all changes to notification templates for audit trail
    and rollback capability.
    """
    __tablename__ = "notification_template_versions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("notification_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, comment="Version number")
    subject = Column(Text, nullable=True, comment="Message subject at this version")
    body = Column(Text, nullable=False, comment="Message body at this version")
    variables = Column(JSON, nullable=True, comment="Variables at this version")
    change_reason = Column(Text, nullable=True, comment="Reason for change")
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User who made change")
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    template = relationship("NotificationTemplate", back_populates="versions")
    changed_by_user = relationship("User", foreign_keys=[changed_by])

    __table_args__ = (
        {"comment": "Notification template version history", "extend_existing": True},
    )


class NotificationTemplateVariable(Base):
    """Notification template variable definitions

    Defines available variables that can be used in notification templates.
    """
    __tablename__ = "notification_template_variables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True, comment="Variable name (e.g., patient_name)")
    description = Column(Text, nullable=True, comment="Variable description")
    data_type = Column(String(50), nullable=False, comment="Data type (string, date, number, boolean)")
    example_value = Column(String(255), nullable=True, comment="Example value for preview")
    category = Column(String(100), nullable=True, index=True, comment="Variable category (patient, appointment, etc.)")
    is_required = Column(Boolean, default=False, nullable=False, comment="Whether variable is required")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "Notification template variable definitions", "extend_existing": True},
    )
