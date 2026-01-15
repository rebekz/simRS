"""Patient Portal Appointment Schemas

Pydantic schemas for appointment booking and management via patient portal.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date, time
from typing import Optional, List
from enum import Enum


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


class AppointmentPriority(str, Enum):
    """Priority levels for appointments"""
    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"


# Booking Schemas
class AvailableSlot(BaseModel):
    """Available time slot for booking"""
    slot_id: Optional[int] = None
    start_time: str
    end_time: str
    is_available: bool
    doctors_available: Optional[int] = None


class AvailableSlotsResponse(BaseModel):
    """Response for available slots query"""
    date: date
    department_id: int
    department_name: str
    slots: List[AvailableSlot]
    total_available: int


class DoctorAvailabilityItem(BaseModel):
    """Doctor availability info"""
    doctor_id: int
    doctor_name: str
    specialization: Optional[str] = None
    available_slots: int
    next_available_slot: Optional[str] = None


class DepartmentAvailabilityItem(BaseModel):
    """Department availability info"""
    department_id: int
    department_name: str
    doctors: List[DoctorAvailabilityItem]


class AppointmentBookRequest(BaseModel):
    """Request to book an appointment"""
    department_id: int
    doctor_id: Optional[int] = None
    appointment_date: date
    appointment_time: str
    appointment_type: AppointmentType
    reason_for_visit: str = Field(..., min_length=5, max_length=1000)
    symptoms: Optional[str] = Field(None, max_length=2000)
    priority: AppointmentPriority = AppointmentPriority.ROUTINE

    @field_validator('appointment_time')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate time format HH:MM"""
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError("Time must be in HH:MM format")

    @field_validator('appointment_date')
    @classmethod
    def validate_date_not_past(cls, v: date) -> date:
        """Validate appointment date is not in the past"""
        if v < date.today():
            raise ValueError("Appointment date cannot be in the past")
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "department_id": 1,
            "doctor_id": 10,
            "appointment_date": "2026-01-20",
            "appointment_time": "09:00",
            "appointment_type": "consultation",
            "reason_for_visit": "Annual checkup",
            "symptoms": "No specific symptoms, just routine checkup",
            "priority": "routine"
        }
    })


class AppointmentResponse(BaseModel):
    """Response after booking an appointment"""
    id: int
    appointment_number: str
    appointment_date: date
    appointment_time: time
    end_time: Optional[time] = None
    department_name: str
    doctor_name: Optional[str] = None
    appointment_type: str
    status: str
    queue_number: Optional[str] = None
    estimated_wait_time_minutes: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class AppointmentDetail(BaseModel):
    """Detailed appointment information"""
    id: int
    appointment_number: str
    appointment_date: date
    appointment_time: time
    end_time: Optional[time] = None
    duration_minutes: int

    # Related entities
    department_id: int
    department_name: str
    doctor_id: Optional[int] = None
    doctor_name: Optional[str] = None

    # Classification
    appointment_type: str
    status: str
    priority: str

    # Clinical info
    reason_for_visit: Optional[str] = None
    symptoms: Optional[str] = None

    # Queue info
    queue_number: Optional[str] = None
    queue_position: Optional[int] = None
    estimated_wait_time_minutes: Optional[int] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    check_in_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None

    # Cancellation info
    cancellation_reason: Optional[str] = None
    cancelled_at: Optional[datetime] = None

    # Reminders
    reminder_sent: bool = False
    reminder_sent_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MyAppointmentsResponse(BaseModel):
    """Response for my appointments query"""
    upcoming: List[AppointmentDetail]
    past: List[AppointmentDetail]
    cancelled: List[AppointmentDetail]
    total_upcoming: int
    total_past: int
    total_cancelled: int


# Reschedule/Cancel Schemas
class AppointmentRescheduleRequest(BaseModel):
    """Request to reschedule an appointment"""
    new_date: date
    new_time: str
    reason: Optional[str] = Field(None, max_length=500)

    @field_validator('new_date')
    @classmethod
    def validate_date_not_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("New appointment date cannot be in the past")
        return v


class AppointmentCancelRequest(BaseModel):
    """Request to cancel an appointment"""
    reason: Optional[str] = Field(None, max_length=500, description="Reason for cancellation")


class AppointmentCancelResponse(BaseModel):
    """Response after cancellation"""
    success: bool
    message: str
    cancellation_policy_info: Optional[str] = None


# Waitlist Schemas
class WaitlistJoinRequest(BaseModel):
    """Request to join waitlist for fully booked slot"""
    department_id: int
    doctor_id: Optional[int] = None
    preferred_date: date
    preferred_time_range: Optional[str] = Field(None, description="e.g., 'morning', 'afternoon'")
    appointment_type: AppointmentType
    reason_for_visit: str = Field(..., min_length=5, max_length=1000)


class WaitlistResponse(BaseModel):
    """Response for waitlist join"""
    success: bool
    message: str
    waitlist_position: Optional[int] = None
    estimated_wait_days: Optional[int] = None


# Calendar Integration Schemas
class CalendarEvent(BaseModel):
    """Event for calendar integration"""
    title: str
    start: datetime
    end: datetime
    description: Optional[str] = None
    location: Optional[str] = None


class CalendarIntegrationResponse(BaseModel):
    """Response for calendar integration"""
    google_calendar_url: Optional[str] = None
    outlook_calendar_url: Optional[str] = None
    ics_download_url: Optional[str] = None


# Pre-appointment Checklist Schemas
class PreAppointmentChecklist(BaseModel):
    """Pre-appointment instructions"""
    fasting_required: bool = False
    fasting_hours: Optional[int] = None
    bring_documents: List[str] = []
    arrive_early_minutes: int = 15
    preparation_instructions: List[str] = []


class AppointmentInfoResponse(BaseModel):
    """Combined response for appointment details"""
    appointment: AppointmentDetail
    pre_appointment_checklist: PreAppointmentChecklist
    department_info: Optional[dict] = None
    doctor_info: Optional[dict] = None


# Queue Status Schemas
class QueueStatusResponse(BaseModel):
    """Real-time queue status for appointment"""
    queue_number: Optional[str] = None
    queue_position: Optional[int] = None
    estimated_wait_time_minutes: Optional[int] = None
    patients_ahead: Optional[int] = None
    currently_serving: Optional[str] = None
    status_message: Optional[str] = None


# Search/Filter Schemas
class AppointmentSearchRequest(BaseModel):
    """Search/filter appointments"""
    status: Optional[AppointmentStatus] = None
    department_id: Optional[int] = None
    doctor_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    appointment_type: Optional[AppointmentType] = None
