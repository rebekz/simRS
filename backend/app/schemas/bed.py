"""Bed Management System Schemas for STORY-020

This module provides Pydantic schemas for:
- Bed and room management
- Bed availability tracking
- Bed assignment and transfer
- Room status management
- Bed request workflow
- Real-time bed dashboard
"""
from typing import List, Optional, Dict
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# Bed and Room Enums
# =============================================================================

class RoomClass(str, Enum):
    """Hospital room classes"""
    VVIP = "vvip"
    VIP = "vip"
    CLASS_1 = "1"
    CLASS_2 = "2"
    CLASS_3 = "3"


class BedStatus(str, Enum):
    """Bed availability status"""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"


class RoomStatus(str, Enum):
    """Room status"""
    CLEAN = "clean"
    SOILED = "soiled"
    MAINTENANCE = "maintenance"
    ISOLATION = "isolation"


class GenderType(str, Enum):
    """Gender type for room assignment"""
    MALE = "male"
    FEMALE = "female"
    MIXED = "mixed"


class BedRequestStatus(str, Enum):
    """Bed request workflow status"""
    PENDING = "pending"
    APPROVED = "approved"
    ASSIGNED = "assigned"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


# =============================================================================
# Room and Bed Schemas
# =============================================================================

class RoomBase(BaseModel):
    """Base room schema"""
    ward_id: int
    room_number: str
    room_class: RoomClass
    gender_type: GenderType
    total_beds: int
    floor: int


class RoomCreate(RoomBase):
    """Schema for creating a new room"""
    description: Optional[str] = None


class RoomResponse(RoomBase):
    """Schema for room response"""
    id: int
    description: Optional[str] = None
    status: RoomStatus

    # Bed statistics
    available_beds: int
    occupied_beds: int
    maintenance_beds: int

    # Relationships
    beds: List['BedResponse'] = []

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BedBase(BaseModel):
    """Base bed schema"""
    room_id: int
    bed_number: str
    bed_type: str = Field(..., description="e.g., standard, icu, pediatric, isolation")


class BedCreate(BedBase):
    """Schema for creating a new bed"""
    pass


class BedResponse(BedBase):
    """Schema for bed response"""
    id: int
    room_id: int
    room_number: str  # Denormalized from room
    ward_id: int  # Denormalized from room
    bed_number: str
    bed_type: str
    status: BedStatus

    # Patient assignment (if occupied)
    current_patient_id: Optional[int] = None
    current_patient_name: Optional[str] = None
    admission_date: Optional[datetime] = None
    expected_discharge_date: Optional[date] = None

    # Room details
    room_class: RoomClass
    gender_type: GenderType
    floor: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Bed Assignment Schemas
# =============================================================================

class BedAssignmentRequest(BaseModel):
    """Schema for assigning patient to bed"""
    patient_id: int
    bed_id: int
    admission_id: Optional[int] = None
    expected_discharge_date: Optional[date] = None
    notes: Optional[str] = None
    assign_for_isolation: bool = False


class BedAssignmentResponse(BaseModel):
    """Schema for bed assignment response"""
    assignment_id: int
    patient_id: int
    patient_name: str
    bed_id: int
    bed_number: str
    room_number: str
    room_class: RoomClass
    ward_id: int
    assigned_at: datetime
    assigned_by: str
    expected_discharge_date: Optional[date] = None
    notes: Optional[str] = None


class BedTransferRequest(BaseModel):
    """Schema for transferring patient between beds"""
    patient_id: int
    from_bed_id: int
    to_bed_id: int
    reason: str = Field(..., description="Reason for transfer")
    transfer_notes: Optional[str] = None


class BedTransferResponse(BaseModel):
    """Schema for bed transfer response"""
    transfer_id: int
    patient_id: int
    patient_name: str
    from_bed: dict
    to_bed: dict
    transferred_at: datetime
    transferred_by: str
    reason: str
    transfer_notes: Optional[str] = None


class BedDischargeRequest(BaseModel):
    """Schema for discharging patient from bed"""
    patient_id: int
    bed_id: int
    discharge_notes: Optional[str] = None
    clean_required: bool = True


# =============================================================================
# Bed Availability Schemas
# =============================================================================

class BedAvailabilitySummary(BaseModel):
    """Schema for bed availability summary"""
    ward_id: int
    ward_name: str
    room_class: Optional[RoomClass] = None

    # Bed counts
    total_beds: int
    available_beds: int
    occupied_beds: int
    maintenance_beds: int
    reserved_beds: int

    # Percentage
    occupancy_rate: float

    # By gender
    male_available: int
    female_available: int
    mixed_available: int


class BedAvailabilityFilter(BaseModel):
    """Schema for bed availability filtering"""
    ward_id: Optional[int] = None
    room_class: Optional[RoomClass] = None
    gender_type: Optional[GenderType] = None
    bed_type: Optional[str] = None
    floor: Optional[int] = None
    availability_status: Optional[BedStatus] = None


class BedAvailabilityResponse(BaseModel):
    """Schema for bed availability response"""
    filters: BedAvailabilityFilter
    beds: List[BedResponse]
    total: int
    summary: Dict[str, int]  # {"available": 15, "occupied": 45, ...}


# =============================================================================
# Room Status Management Schemas
# =============================================================================

class RoomStatusUpdate(BaseModel):
    """Schema for updating room status"""
    status: RoomStatus
    notes: Optional[str] = None
    clean_required: bool = False
    maintenance_reason: Optional[str] = None


class RoomStatusResponse(BaseModel):
    """Schema for room status response"""
    room_id: int
    room_number: str
    ward_id: int
    status: RoomStatus
    previous_status: Optional[RoomStatus] = None
    updated_at: datetime
    updated_by: str
    notes: Optional[str] = None


# =============================================================================
# Bed Request Workflow Schemas
# =============================================================================

class BedRequestCreate(BaseModel):
    """Schema for creating bed request"""
    patient_id: int
    requested_by_id: int
    priority: str = Field("routine", description="routine, urgent, emergency")
    requested_room_class: Optional[RoomClass] = None
    requested_ward_id: Optional[int] = None
    gender_preference: Optional[GenderType] = None
    medical_requirements: Optional[str] = None
    expected_admission_date: Optional[date] = None
    notes: Optional[str] = None


class BedRequestResponse(BaseModel):
    """Schema for bed request response"""
    request_id: int
    patient_id: int
    patient_name: str
    requested_by: str
    priority: str
    requested_room_class: Optional[RoomClass] = None
    requested_ward_id: Optional[int] = None
    gender_preference: Optional[GenderType] = None
    medical_requirements: Optional[str] = None
    expected_admission_date: Optional[date] = None
    status: BedRequestStatus

    # Assignment details
    assigned_bed_id: Optional[int] = None
    assigned_bed_number: Optional[str] = None
    assigned_room_number: Optional[str] = None
    assigned_room_class: Optional[RoomClass] = None
    assigned_ward_id: Optional[int] = None
    assigned_at: Optional[datetime] = None
    assigned_by: Optional[str] = None

    # Approval
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime


class BedRequestApproval(BaseModel):
    """Schema for approving bed request"""
    notes: Optional[str] = None
    approved_by_id: int


# =============================================================================
# Bed Dashboard Schemas
# =============================================================================

class BedDashboardSummary(BaseModel):
    """Schema for bed dashboard summary"""
    hospital_name: str
    last_updated: datetime

    # Overall statistics
    total_beds: int
    total_available: int
    total_occupied: int
    total_maintenance: int
    occupancy_rate: float

    # By class
    by_class: Dict[str, Dict[str, int]]  # {"vvip": {"total": 10, "available": 5, ...}}

    # By ward
    by_ward: Dict[str, Dict[str, int]]  # {"ward_1": {"total": 50, "available": 20, ...}}

    # Critical beds
    icu_available: int
    icu_total: int
    icu_occupancy_rate: float

    # Available beds by class
    available_vvip: int
    available_vip: int
    available_class_1: int
    available_class_2: int
    available_class_3: int


class BedDashboardData(BaseModel):
    """Schema for bed dashboard data"""
    summary: BedDashboardSummary
    wards: List[BedAvailabilitySummary]
    recently_assigned: List[BedAssignmentResponse]  # Last 10 assignments
    bed_requests_pending: List[BedRequestResponse]  # Pending requests
    available_beds: List[BedResponse]  # All available beds with details


# =============================================================================
# Bed Transfer History Schemas
# =============================================================================

class BedTransferHistory(BaseModel):
    """Schema for bed transfer history"""
    transfer_id: int
    patient_id: int
    patient_name: str
    from_bed_number: str
    from_room_number: str
    from_ward_id: int
    to_bed_number: str
    to_room_number: str
    to_ward_id: int
    reason: str
    transferred_at: datetime
    transferred_by: str
    transfer_notes: Optional[str] = None


class BedAssignmentHistory(BaseModel):
    """Schema for bed assignment history"""
    assignment_id: int
    patient_id: int
    patient_name: str
    bed_number: str
    room_number: str
    room_class: RoomClass
    ward_id: int
    assigned_at: datetime
    assigned_by: str
    discharged_at: Optional[datetime] = None
    length_of_stay_days: Optional[int] = None
