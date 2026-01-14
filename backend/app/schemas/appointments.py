"""Appointment schemas for appointment booking system

This module defines Pydantic schemas for appointment booking, slots, and reminders.
All schemas match the appointment models with proper validation and serialization.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date, time
from enum import Enum


class AppointmentStatus(str, Enum):
    """Appointment status options"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentType(str, Enum):
    """Appointment type options"""
    INITIAL = "initial"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    CONSULTATION = "consultation"
    PROCEDURE = "procedure"
    THERAPY = "therapy"
    TELEMEDICINE = "telemedicine"


class SlotStatus(str, Enum):
    """Slot status options"""
    AVAILABLE = "available"
    BOOKED = "booked"
    BLOCKED = "blocked"
    PAST = "past"


class ReminderType(str, Enum):
    """Reminder type options"""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    SYSTEM = "system"


class ReminderStatus(str, Enum):
    """Reminder status options"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ==================== Appointment Schemas ====================

class AppointmentBase(BaseModel):
    """Base appointment schema with common fields"""
    patient_id: int = Field(..., description="Patient ID")
    doctor_id: int = Field(..., description="Doctor ID")
    department: str = Field(..., min_length=1, max_length=100, description="Department/clinic name")
    appointment_type: AppointmentType = Field(default=AppointmentType.CONSULTATION)
    appointment_date: date = Field(..., description="Appointment date")
    start_time: time = Field(..., description="Appointment start time")
    end_time: time = Field(..., description="Appointment end time")
    status: AppointmentStatus = Field(default=AppointmentStatus.SCHEDULED)
    is_urgent: bool = Field(default=False, description="Urgent appointment flag")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    reason_for_visit: Optional[str] = Field(None, max_length=500, description="Reason for visit")
    appointment_number: Optional[str] = Field(None, max_length=50, description="Unique appointment number")


class AppointmentCreate(AppointmentBase):
    """Schema for creating an appointment"""
    slot_id: Optional[int] = Field(None, description="Associated time slot ID")

    @validator('end_time')
    def validate_end_time(cls, v, info):
        """Validate end time is after start time"""
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

    @validator('appointment_date')
    def validate_appointment_date(cls, v):
        """Validate appointment date is not in the past"""
        today = date.today()
        if v < today:
            raise ValueError('appointment_date cannot be in the past')
        return v


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment (all fields optional)"""
    doctor_id: Optional[int] = None
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    appointment_type: Optional[AppointmentType] = None
    appointment_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    status: Optional[AppointmentStatus] = None
    is_urgent: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)
    reason_for_visit: Optional[str] = Field(None, max_length=500)
    cancellation_reason: Optional[str] = Field(None, max_length=500, description="Reason for cancellation")

    @validator('appointment_date')
    def validate_appointment_date(cls, v):
        """Validate appointment date is not in the past if provided"""
        if v is None:
            return v
        today = date.today()
        if v < today:
            raise ValueError('appointment_date cannot be in the past')
        return v


class AppointmentResponse(AppointmentBase):
    """Schema for full appointment data response"""
    id: int
    slot_id: Optional[int] = None
    cancellation_reason: Optional[str] = None
    check_in_time: Optional[datetime] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppointmentListResponse(BaseModel):
    """Schema for paginated appointment list response"""
    items: List[AppointmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AppointmentBookingRequest(BaseModel):
    """Schema for appointment booking request"""
    patient_id: int = Field(..., description="Patient ID")
    doctor_id: int = Field(..., description="Doctor ID")
    department: str = Field(..., min_length=1, max_length=100)
    appointment_type: AppointmentType = Field(default=AppointmentType.CONSULTATION)
    slot_id: int = Field(..., description="Time slot ID to book")
    reason_for_visit: Optional[str] = Field(None, max_length=500)
    is_urgent: bool = Field(default=False)
    notes: Optional[str] = Field(None, max_length=1000)


class AppointmentBookingResponse(BaseModel):
    """Schema for appointment booking response"""
    appointment: AppointmentResponse
    message: str = Field(default="Appointment booked successfully")
    confirmation_number: str = Field(..., description="Unique confirmation number")
    qr_code: Optional[str] = Field(None, description="QR code data for check-in")
    reminder_scheduled: bool = Field(default=False, description="Whether reminder was scheduled")


# ==================== Appointment Slot Schemas ====================

class AppointmentSlotBase(BaseModel):
    """Base appointment slot schema"""
    doctor_id: int = Field(..., description="Doctor ID")
    department: str = Field(..., min_length=1, max_length=100, description="Department/clinic")
    slot_date: date = Field(..., description="Date of the slot")
    start_time: time = Field(..., description="Slot start time")
    end_time: time = Field(..., description="Slot end time")
    status: SlotStatus = Field(default=SlotStatus.AVAILABLE)
    max_patients: int = Field(default=1, ge=1, le=10, description="Maximum patients per slot")


class AppointmentSlotCreate(AppointmentSlotBase):
    """Schema for creating an appointment slot"""
    @validator('end_time')
    def validate_end_time(cls, v, info):
        """Validate end time is after start time"""
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class AppointmentSlotUpdate(BaseModel):
    """Schema for updating an appointment slot (all fields optional)"""
    status: Optional[SlotStatus] = None
    max_patients: Optional[int] = Field(None, ge=1, le=10)


class AppointmentSlotResponse(AppointmentSlotBase):
    """Schema for appointment slot response"""
    id: int
    current_bookings: int = Field(default=0, description="Current number of bookings")
    available_spots: int = Field(default=1, description="Available spots remaining")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SlotAvailabilityResponse(BaseModel):
    """Schema for slot availability check"""
    slot_id: int
    is_available: bool
    available_spots: int
    slot_date: date
    start_time: time
    end_time: time
    doctor_id: int
    department: str


class AvailableSlotsResponse(BaseModel):
    """Schema for available slots response"""
    doctor_id: int
    doctor_name: str = Field(..., description="Doctor's name")
    department: str
    date: date
    available_slots: List[AppointmentSlotResponse] = Field(default_factory=list)
    total_available: int = Field(default=0, description="Total available slots")


# ==================== Appointment Reminder Schemas ====================

class AppointmentReminderBase(BaseModel):
    """Base appointment reminder schema"""
    appointment_id: int = Field(..., description="Appointment ID")
    reminder_type: ReminderType = Field(..., description="Type of reminder")
    reminder_time: datetime = Field(..., description="When to send reminder")
    status: ReminderStatus = Field(default=ReminderStatus.PENDING)
    message: Optional[str] = Field(None, max_length=1000, description="Reminder message content")
    recipient_contact: str = Field(..., max_length=255, description="Recipient contact (email/phone)")


class AppointmentReminderCreate(AppointmentReminderBase):
    """Schema for creating an appointment reminder"""
    @validator('reminder_time')
    def validate_reminder_time(cls, v):
        """Validate reminder time is in the future"""
        if v < datetime.now():
            raise ValueError('reminder_time must be in the future')
        return v

    @validator('recipient_contact')
    def validate_recipient_contact(cls, v, info):
        """Validate recipient contact based on reminder type"""
        reminder_type = info.data.get('reminder_type')
        if reminder_type == ReminderType.EMAIL:
            if '@' not in v:
                raise ValueError('recipient_contact must be valid email for EMAIL reminders')
        elif reminder_type in [ReminderType.SMS, ReminderType.WHATSAPP]:
            if not v.replace('+', '').replace(' ', '').replace('-', '').isdigit():
                raise ValueError('recipient_contact must be valid phone number for SMS/WHATSAPP reminders')
        return v


class AppointmentReminderResponse(AppointmentReminderBase):
    """Schema for appointment reminder response"""
    id: int
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Additional Schemas ====================

class TimeSlot(BaseModel):
    """Schema for a time slot"""
    start_time: time = Field(..., description="Slot start time")
    end_time: time = Field(..., description="Slot end time")
    available: bool = Field(default=True, description="Whether slot is available")
    slot_id: Optional[int] = None
    available_spots: int = Field(default=1, description="Number of available spots")


class DoctorAvailability(BaseModel):
    """Schema for doctor availability on a specific date"""
    date: date = Field(..., description="Date of availability")
    doctor_id: int
    doctor_name: str
    department: str
    slots: List[TimeSlot] = Field(default_factory=list, description="Available time slots")
    total_slots: int = Field(default=0, description="Total available slots")


class AppointmentSummary(BaseModel):
    """Schema for appointment summary statistics"""
    total: int = Field(default=0, description="Total appointments")
    scheduled: int = Field(default=0, description="Scheduled appointments")
    confirmed: int = Field(default=0, description="Confirmed appointments")
    checked_in: int = Field(default=0, description="Checked-in appointments")
    in_progress: int = Field(default=0, description="Appointments in progress")
    completed: int = Field(default=0, description="Completed appointments")
    cancelled: int = Field(default=0, description="Cancelled appointments")
    no_show: int = Field(default=0, description="No-show appointments")


class AppointmentCalendar(BaseModel):
    """Schema for appointment calendar view"""
    date: date = Field(..., description="Calendar date")
    appointments: List[AppointmentResponse] = Field(default_factory=list)
    total_count: int = Field(default=0)
    summary: AppointmentSummary = Field(default_factory=AppointmentSummary)


class BookingConfirmation(BaseModel):
    """Schema for booking confirmation"""
    appointment_number: str = Field(..., description="Unique appointment number")
    appointment_id: int = Field(..., description="Appointment ID")
    qr_code: str = Field(..., description="QR code data for check-in")
    qr_code_url: Optional[str] = Field(None, description="URL to QR code image")
    confirmation_message: str = Field(..., description="Confirmation message")
    appointment_details: AppointmentResponse = Field(..., description="Full appointment details")
    check_in_instructions: List[str] = Field(
        default_factory=list,
        description="Instructions for check-in"
    )
    reminder_info: Optional[dict] = Field(None, description="Reminder scheduling information")
