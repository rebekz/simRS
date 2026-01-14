"""Queue Management System Schemas for STORY-010

This module provides Pydantic schemas for:
- Queue number generation
- Queue status tracking
- Priority queue management
- Queue recall functionality
- Queue statistics
- Digital display integration
- SMS notification support
"""
from typing import List, Optional, Dict
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# Queue Enums
# =============================================================================

class QueueDepartment(str, Enum):
    """Hospital departments with queue management"""
    POLI = "poli"  # Outpatient polyclinic
    FARMASI = "farmasi"  # Pharmacy
    LAB = "lab"  # Laboratory
    RADIOLOGI = "radiologi"  # Radiology
    KASIR = "kasir"  # Cashier/payment


class QueueStatus(str, Enum):
    """Queue ticket status"""
    WAITING = "waiting"  # Waiting to be called
    CALLED = "called"  # Currently being served
    SERVED = "served"  # Service completed
    SKIPPED = "skipped"  # Patient not present when called
    CANCELLED = "cancelled"  # Cancelled by patient


class QueuePriority(str, Enum):
    """Queue priority levels"""
    NORMAL = "normal"  # Regular queue
    PRIORITY = "priority"  # Priority patients (lansia, ibu hamil, difabel)
    EMERGENCY = "emergency"  # Emergency cases


# =============================================================================
# Queue Ticket Schemas
# =============================================================================

class QueueTicketCreate(BaseModel):
    """Schema for creating a new queue ticket"""
    patient_id: int
    department: QueueDepartment
    priority: QueuePriority = QueuePriority.NORMAL
    poli_id: Optional[int] = Field(None, description="Polyclinic ID (required if department is POLI)")
    doctor_id: Optional[int] = Field(None, description="Doctor ID (optional)")
    appointment_id: Optional[int] = Field(None, description="Appointment ID if booking")


class QueueTicketResponse(BaseModel):
    """Schema for queue ticket response"""
    id: int
    ticket_number: str  # Human-readable queue number (e.g., "A-001")
    patient_id: int
    patient_name: str
    patient_bpjs_number: Optional[str] = None
    department: QueueDepartment
    department_name: str
    priority: QueuePriority
    status: QueueStatus

    # Optional specific assignments
    poli_id: Optional[int] = None
    poli_name: Optional[str] = None
    doctor_id: Optional[int] = None
    doctor_name: Optional[str] = None

    # Queue position
    queue_position: Optional[int] = None
    people_ahead: int = 0
    estimated_wait_minutes: Optional[int] = None

    # Timestamps
    issued_at: datetime
    called_at: Optional[datetime] = None
    served_at: Optional[datetime] = None

    # Service information
    serving_counter: Optional[int] = None  # Counter number being served
    service_started_at: Optional[datetime] = None
    service_completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QueueListResponse(BaseModel):
    """Schema for queue list response"""
    department: QueueDepartment
    current_ticket: Optional[QueueTicketResponse] = None  # Currently being served
    waiting: List[QueueTicketResponse] = []  # Waiting patients
    served_today: int = 0
    total_waiting: int = 0
    average_wait_time_minutes: Optional[float] = None


# =============================================================================
# Queue Recall Schemas
# =============================================================================

class QueueRecallRequest(BaseModel):
    """Schema for recalling a queue ticket"""
    ticket_id: int
    counter: int = Field(1, ge=1, le=10, description="Counter number")
    announce: bool = True  # Whether to announce via PA system


class QueueRecallResponse(BaseModel):
    """Schema for queue recall response"""
    ticket_id: int
    ticket_number: str
    patient_name: str
    counter: int
    recalled_at: datetime
    announced: bool
    message: str  # Announcement message


# =============================================================================
# Queue Statistics Schemas
# =============================================================================

class QueueStatistics(BaseModel):
    """Schema for queue statistics"""
    department: QueueDepartment
    date: date

    # Basic counts
    total_issued: int
    total_served: int
    total_waiting: int
    total_skipped: int
    total_cancelled: int

    # Performance metrics
    average_wait_time_minutes: float
    average_service_time_minutes: float
    longest_wait_time_minutes: int

    # By priority
    normal_served: int
    priority_served: int
    emergency_served: int

    # By hour (for graphs)
    hourly_distribution: Dict[str, int]  # {"09:00": 15, "10:00": 23, ...}

    # Current status
    currently_serving: Optional[Dict[str, str]] = None  # {"ticket_number": "A-001", "counter": 1}


class DepartmentQueueStatistics(BaseModel):
    """Schema for multi-department queue statistics"""
    statistics: Dict[QueueDepartment, QueueStatistics]
    total_patients_waiting: int
    total_patients_served_today: int


# =============================================================================
# Digital Display Schemas
# =============================================================================

class DigitalDisplayData(BaseModel):
    """Schema for digital queue display data"""
    department: QueueDepartment
    department_name: str
    current_ticket: Optional[Dict] = None  # Currently serving
    recent_tickets: List[Dict] = []  # Recently served (last 5)
    waiting_count: int
    estimated_wait_time: Optional[int] = None
    last_updated: datetime

    # Display settings
    show_bpjs: bool = True
    show_doctor_name: bool = True
    show_counter: bool = True


class DigitalDisplayResponse(BaseModel):
    """Schema for digital display response (all departments)"""
    displays: Dict[QueueDepartment, DigitalDisplayData]
    hospital_info: Optional[Dict] = None  # Hospital name, logo, etc.
    last_updated: datetime
    refresh_interval_seconds: int = 10


# =============================================================================
# Mobile Queue Status Schemas
# =============================================================================

class MobileQueueStatus(BaseModel):
    """Schema for mobile queue status view"""
    ticket_id: int
    ticket_number: str
    department: QueueDepartment
    department_name: str
    status: QueueStatus
    queue_position: Optional[int] = None
    people_ahead: int
    estimated_wait_minutes: Optional[int] = None

    # Currently serving
    current_ticket_number: Optional[str] = None
    current_counter: Optional[int] = None

    # Patient info
    patient_name: str
    poli_name: Optional[str] = None
    doctor_name: Optional[str] = None

    # Timestamps
    issued_at: datetime
    called_at: Optional[datetime] = None

    # Notifications
    sms_sent: bool = False
    whatsapp_sent: bool = False
    last_notification_at: Optional[datetime] = None


# =============================================================================
# Queue Notification Schemas
# =============================================================================

class QueueNotificationRequest(BaseModel):
    """Schema for sending queue notifications"""
    ticket_id: int
    notification_type: str = Field(..., description="sms, whatsapp, or both")
    message: Optional[str] = Field(None, description="Custom message (optional)")


class QueueNotificationResponse(BaseModel):
    """Schema for queue notification response"""
    ticket_id: int
    notification_type: str
    sent: bool
    sent_at: datetime
    message: str
    error: Optional[str] = None


# =============================================================================
# Queue Management Schemas (Admin)
# =============================================================================

class QueueTransferRequest(BaseModel):
    """Schema for transferring queue to different department/poli"""
    ticket_id: int
    new_department: Optional[QueueDepartment] = None
    new_poli_id: Optional[int] = None
    new_doctor_id: Optional[int] = None
    reason: str = Field(..., description="Reason for transfer")


class QueueCancelRequest(BaseModel):
    """Schema for cancelling queue ticket"""
    ticket_id: int
    reason: str = Field(..., description="Reason for cancellation")
    cancelled_by: int = Field(..., description="User ID who cancelled")


class QueueSettings(BaseModel):
    """Schema for queue department settings"""
    department: QueueDepartment
    max_concurrent: int = Field(5, ge=1, le=20, description="Max patients served concurrently")
    average_service_time_minutes: int = Field(15, description="Expected service time per patient")
    counters: int = Field(3, ge=1, le=10, description="Number of service counters")
    enable_sms: bool = True
    enable_whatsapp: bool = False
    enable_display: bool = True
    display_refresh_interval_seconds: int = Field(10, ge=5, le=60)
