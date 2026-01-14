"""Queue Management System Models for STORY-010

This module provides database models for:
- Queue ticket management
- Queue recall tracking
- Queue statistics
- Digital display support
- SMS notification logging
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Boolean, Enum as SQLEnum, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.schemas.queue import QueueDepartment, QueueStatus, QueuePriority


# =============================================================================
# Queue Ticket Models
# =============================================================================

class QueueTicket(Base):
    """Queue ticket model for managing patient queues"""
    __tablename__ = "queue_tickets"

    id = Column(Integer, primary_key=True, index=True)

    # Ticket identification
    ticket_number = Column(String(20), unique=True, nullable=False, index=True)  # e.g., "A-001", "F-045"
    department = Column(SQLEnum(QueueDepartment), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)  # Ticket date (for daily numbering)

    # Patient reference
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)

    # Priority and status
    priority = Column(SQLEnum(QueuePriority), nullable=False, default=QueuePriority.NORMAL, index=True)
    status = Column(SQLEnum(QueueStatus), nullable=False, default=QueueStatus.WAITING, index=True)

    # Specific assignments (for POLI department)
    poli_id = Column(Integer, ForeignKey("polis.id"), nullable=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Appointment reference (if pre-booked)
    appointment_id = Column(Integer, nullable=True)

    # Queue position (calculated)
    queue_position = Column(Integer, nullable=True)  # Current position in queue
    people_ahead = Column(Integer, nullable=False, default=0)  # Number of people ahead

    # Service information
    serving_counter = Column(Integer, nullable=True)  # Counter number being served
    service_started_at = Column(DateTime(timezone=True), nullable=True)
    service_completed_at = Column(DateTime(timezone=True), nullable=True)

    # Estimated wait time (calculated)
    estimated_wait_minutes = Column(Integer, nullable=True)

    # Timestamps
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    called_at = Column(DateTime(timezone=True), nullable=True)
    served_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Relationships
    patient = relationship("Patient", backref="queue_tickets")
    poli = relationship("Poli", backref="queue_tickets")
    doctor = relationship("User", foreign_keys=[doctor_id], backref="assigned_queue_tickets")
    recalls = relationship("QueueRecall", back_populates="ticket", cascade="all, delete-orphan")
    notifications = relationship("QueueNotification", back_populates="ticket", cascade="all, delete-orphan")


# =============================================================================
# Queue Recall Models
# =============================================================================

class QueueRecall(Base):
    """Queue recall tracking - when a ticket is called"""
    __tablename__ = "queue_recalls"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("queue_tickets.id"), nullable=False, index=True)

    # Recall details
    counter = Column(Integer, nullable=False)  # Counter number
    announced = Column(Boolean, nullable=False, default=False)  # Whether announced via PA
    recall_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Staff who called
    called_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Result
    patient_present = Column(Boolean, nullable=True)  # Null if not checked yet
    no_show_time = Column(DateTime(timezone=True), nullable=True)  # When marked as no-show

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticket = relationship("QueueTicket", back_populates="recalls")
    called_by = relationship("User", foreign_keys=[called_by_id], backref="queue_recalls_made")


# =============================================================================
# Queue Notification Models
# =============================================================================

class QueueNotification(Base):
    """Queue notification logging (SMS/WhatsApp)"""
    __tablename__ = "queue_notifications"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("queue_tickets.id"), nullable=False, index=True)

    # Notification details
    notification_type = Column(String(20), nullable=False)  # "sms", "whatsapp", "both"
    message = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=False)  # Recipient phone number

    # Status
    sent = Column(Boolean, nullable=False, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    # Delivery tracking
    delivery_status = Column(String(50), nullable=True)  # "sent", "delivered", "failed"
    delivery_receipt_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticket = relationship("QueueTicket", back_populates="notifications")


# =============================================================================
# Queue Statistics Cache Models
# =============================================================================

class QueueStatisticsCache(Base):
    """Cached queue statistics for performance"""
    __tablename__ = "queue_statistics_cache"

    id = Column(Integer, primary_key=True, index=True)
    department = Column(SQLEnum(QueueDepartment), nullable=False, unique=True)
    date = Column(Date, nullable=False, unique=True)

    # Cached statistics
    total_issued = Column(Integer, nullable=False, default=0)
    total_served = Column(Integer, nullable=False, default=0)
    total_waiting = Column(Integer, nullable=False, default=0)
    total_skipped = Column(Integer, nullable=False, default=0)
    total_cancelled = Column(Integer, nullable=False, default=0)

    # Performance metrics
    average_wait_time_minutes = Column(Float, nullable=True)
    average_service_time_minutes = Column(Float, nullable=True)

    # By priority
    normal_served = Column(Integer, nullable=False, default=0)
    priority_served = Column(Integer, nullable=False, default=0)
    emergency_served = Column(Integer, nullable=False, default=0)

    # Hourly distribution (JSON)
    hourly_distribution = Column(JSON, nullable=True)

    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Cache expiry


# =============================================================================
# Queue Settings Models
# =============================================================================

class QueueSettings(Base):
    """Per-department queue settings"""
    __tablename__ = "queue_settings"

    id = Column(Integer, primary_key=True, index=True)
    department = Column(SQLEnum(QueueDepartment), unique=True, nullable=False)

    # Capacity settings
    max_concurrent = Column(Integer, nullable=False, default=5)  # Max concurrent patients
    counters = Column(Integer, nullable=False, default=3)  # Number of service counters

    # Time estimates
    average_service_time_minutes = Column(Integer, nullable=False, default=15)

    # Notification settings
    enable_sms = Column(Boolean, nullable=False, default=True)
    enable_whatsapp = Column(Boolean, nullable=False, default=False)
    sms_on_issue = Column(Boolean, nullable=False, default=True)
    sms_on_call = Column(Boolean, nullable=False, default=True)
    sms_on_reminder = Column(Boolean, nullable=False, default=False)

    # Display settings
    enable_display = Column(Boolean, nullable=False, default=True)
    display_refresh_interval_seconds = Column(Integer, nullable=False, default=10)
    show_bpjs = Column(Boolean, nullable=False, default=True)
    show_doctor_name = Column(Boolean, nullable=False, default=True)
    show_counter = Column(Boolean, nullable=False, default=True)

    # Priority queue settings
    priority_enabled = Column(Boolean, nullable=False, default=True)
    priority_categories = Column(JSON, nullable=True)  # ["lansia", "ibu_hamil", "difabel"]

    # Offline support
    enable_offline = Column(Boolean, nullable=False, default=True)
    offline_sync_interval_minutes = Column(Integer, nullable=False, default=5)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# =============================================================================
# Queue Transfer History Models
# =============================================================================

class QueueTransfer(Base):
    """Queue transfer history - when patients are moved between queues"""
    __tablename__ = "queue_transfers"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("queue_tickets.id"), nullable=False)

    # Transfer details
    from_department = Column(SQLEnum(QueueDepartment), nullable=False)
    to_department = Column(SQLEnum(QueueDepartment), nullable=False)

    # Optional specific transfers
    from_poli_id = Column(Integer, nullable=True)
    to_poli_id = Column(Integer, nullable=True)
    from_doctor_id = Column(Integer, nullable=True)
    to_doctor_id = Column(Integer, nullable=True)

    # Reason
    reason = Column(Text, nullable=False)

    # Staff who initiated transfer
    transferred_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticket = relationship("QueueTicket", backref="transfers")
    transferred_by = relationship("User", foreign_keys=[transferred_by_id], backref="queue_transfers_made")
