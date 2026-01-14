"""Appointment Booking Models for STORY-009

This module provides SQLAlchemy models for:
- Appointment scheduling and management
- Appointment slot configuration
- Appointment reminders (SMS, WhatsApp, email, push)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Time, ForeignKey, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.session import Base


class AppointmentType(str, Enum):
    """Types of appointments"""
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    PROCEDURE = "procedure"
    VACCINATION = "vaccination"


class AppointmentStatus(str, Enum):
    """Status options for appointments"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class BookingChannel(str, Enum):
    """Channels through which appointments can be booked"""
    WEB = "web"
    MOBILE = "mobile"
    KIOSK = "kiosk"
    PHONE = "phone"
    WALK_IN = "walk_in"


class AppointmentPriority(str, Enum):
    """Priority levels for appointments"""
    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class ReminderType(str, Enum):
    """Types of reminder notifications"""
    SMS = "sms"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    PUSH = "push"


class ReminderStatus(str, Enum):
    """Status for reminder notifications"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


# =============================================================================
# Appointment Model
# =============================================================================

class Appointment(Base):
    """Appointment model for managing patient appointments

    This model stores comprehensive appointment data including scheduling details,
    patient information, status tracking, and queue management integration.
    """
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    # Appointment identification
    appointment_number = Column(String(50), unique=True, nullable=False, index=True, comment="Unique appointment booking number")

    # References
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Reference to patient")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True, comment="Reference to department")
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True, comment="Reference to doctor")

    # Scheduling details
    appointment_date = Column(Date, nullable=False, index=True, comment="Date of appointment")
    appointment_time = Column(Time, nullable=False, comment="Scheduled start time")
    end_time = Column(Time, nullable=True, comment="Scheduled end time")
    duration_minutes = Column(Integer, nullable=False, default=30, comment="Expected duration in minutes")

    # Appointment classification
    appointment_type = Column(SQLEnum(AppointmentType), nullable=False, index=True, comment="Type of appointment")
    status = Column(SQLEnum(AppointmentStatus), nullable=False, default=AppointmentStatus.SCHEDULED, index=True, comment="Current appointment status")
    booking_channel = Column(SQLEnum(BookingChannel), nullable=False, default=BookingChannel.WEB, comment="How appointment was booked")
    priority = Column(SQLEnum(AppointmentPriority), nullable=False, default=AppointmentPriority.ROUTINE, index=True, comment="Priority level")

    # Clinical information
    reason_for_visit = Column(Text, nullable=True, comment="Patient's reason for visit")
    symptoms = Column(Text, nullable=True, comment="Patient's symptoms description")

    # Queue management
    queue_number = Column(String(20), nullable=True, index=True, comment="Queue number assigned")
    queue_position = Column(Integer, nullable=True, comment="Current position in queue")
    estimated_wait_time_minutes = Column(Integer, nullable=True, comment="Estimated wait time in minutes")

    # Reminders
    reminder_sent = Column(Boolean, nullable=False, default=False, comment="Whether reminder was sent")
    reminder_sent_at = Column(DateTime(timezone=True), nullable=True, comment="When reminder was sent")

    # Timestamp tracking
    check_in_time = Column(DateTime(timezone=True), nullable=True, comment="When patient checked in")
    start_time = Column(DateTime(timezone=True), nullable=True, comment="When appointment actually started")
    completion_time = Column(DateTime(timezone=True), nullable=True, comment="When appointment was completed")

    # Cancellation details
    cancellation_reason = Column(Text, nullable=True, comment="Reason for cancellation")
    cancelled_at = Column(DateTime(timezone=True), nullable=True, comment="When appointment was cancelled")
    cancelled_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User who cancelled the appointment")

    # Additional information
    notes = Column(Text, nullable=True, comment="Additional notes")
    metadata = Column(JSON, nullable=True, comment="Additional metadata in JSON format")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    patient = relationship("Patient", backref="appointments")
    department = relationship("Department", backref="appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], backref="doctor_appointments")
    cancelled_by_user = relationship("User", foreign_keys=[cancelled_by], backref="cancelled_appointments")
    reminders = relationship("AppointmentReminder", back_populates="appointment", cascade="all, delete-orphan")


# =============================================================================
# Appointment Slot Model
# =============================================================================

class AppointmentSlot(Base):
    """Appointment slot model for managing available appointment slots

    This model stores time slots available for booking, including capacity limits
    and blocking information for doctors/departments.
    """
    __tablename__ = "appointment_slots"

    id = Column(Integer, primary_key=True, index=True)

    # References
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True, comment="Reference to department")
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True, comment="Reference to doctor (null for general slots)")

    # Slot details
    date = Column(Date, nullable=False, index=True, comment="Date of the slot")
    start_time = Column(Time, nullable=False, comment="Slot start time")
    end_time = Column(Time, nullable=False, comment="Slot end time")
    slot_duration_minutes = Column(Integer, nullable=False, default=30, comment="Duration of each appointment in minutes")

    # Capacity management
    max_patients = Column(Integer, nullable=False, default=1, comment="Maximum number of patients for this slot")
    booked_count = Column(Integer, nullable=False, default=0, comment="Number of bookings for this slot")

    # Availability status
    is_available = Column(Boolean, nullable=False, default=True, index=True, comment="Whether slot is available for booking")
    is_blocked = Column(Boolean, nullable=False, default=False, comment="Whether slot is blocked")
    block_reason = Column(Text, nullable=True, comment="Reason for blocking the slot")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    department = relationship("Department", backref="appointment_slots")
    doctor = relationship("User", backref="appointment_slots")


# =============================================================================
# Appointment Reminder Model
# =============================================================================

class AppointmentReminder(Base):
    """Appointment reminder model for tracking reminder notifications

    This model stores information about reminder notifications sent to patients
    via various channels (SMS, WhatsApp, email, push notifications).
    """
    __tablename__ = "appointment_reminders"

    id = Column(Integer, primary_key=True, index=True)

    # Reference
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to appointment")

    # Reminder details
    reminder_type = Column(SQLEnum(ReminderType), nullable=False, comment="Type of reminder notification")
    scheduled_at = Column(DateTime(timezone=True), nullable=False, comment="When reminder is scheduled to be sent")
    sent_at = Column(DateTime(timezone=True), nullable=True, comment="When reminder was actually sent")
    status = Column(SQLEnum(ReminderStatus), nullable=False, default=ReminderStatus.PENDING, index=True, comment="Current status of reminder")

    # Message details
    message_content = Column(Text, nullable=True, comment="Content of the reminder message")
    error_message = Column(Text, nullable=True, comment="Error message if sending failed")

    # Retry mechanism
    retry_count = Column(Integer, nullable=False, default=0, comment="Number of retry attempts")
    max_retries = Column(Integer, nullable=False, default=3, comment="Maximum number of retry attempts")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    appointment = relationship("Appointment", back_populates="reminders")
