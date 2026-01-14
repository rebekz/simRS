"""Bed Management API Endpoints for STORY-020

This module provides API endpoints for:
- Room and bed management
- Bed availability tracking
- Bed assignment and transfer
- Room status management
- Bed request workflow
- Real-time bed dashboard
"""
from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.bed import (
    # Room schemas
    RoomCreate, RoomResponse, RoomStatusUpdate, RoomStatusResponse,
    # Bed schemas
    BedCreate, BedResponse,
    # Assignment schemas
    BedAssignmentRequest, BedAssignmentResponse,
    BedTransferRequest, BedTransferResponse,
    BedDischargeRequest,
    # Availability schemas
    BedAvailabilitySummary, BedAvailabilityFilter, BedAvailabilityResponse,
    # Request schemas
    BedRequestCreate, BedRequestResponse, BedRequestApproval,
    # Dashboard schemas
    BedDashboardSummary, BedDashboardData,
    # History schemas
    BedTransferHistory, BedAssignmentHistory
)
from app.crud.bed import (
    # Room operations
    get_room, get_rooms, create_room, update_room, update_room_status, delete_room,
    # Bed operations
    get_bed, get_beds, create_bed, update_bed_status,
    # Assignment operations
    assign_patient_to_bed, discharge_patient_from_bed, transfer_patient,
    get_active_assignments, get_patient_assignment_history,
    # Availability operations
    get_available_beds, get_bed_availability_summary,
    # Request operations
    create_bed_request, approve_bed_request, assign_bed_request, cancel_bed_request,
    get_bed_requests, get_pending_bed_requests,
    # Dashboard operations
    get_bed_dashboard_data, get_recent_assignments
)


router = APIRouter()


# =============================================================================
# Room Management Endpoints
# =============================================================================

@router.post("/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_new_room(
    room_in: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> RoomResponse:
    """Create a new room (admin/staff only)"""
    if not current_user.is_superuser and current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Check if room number already exists in ward
    from app.crud.bed import get_room_by_number
    existing = get_room_by_number(db, room_in.ward_id, room_in.room_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room number already exists in this ward"
        )

    room = create_room(db, room_in)
    return room


@router.get("/rooms", response_model=List[RoomResponse])
def list_rooms(
    ward_id: Optional[int] = Query(None, description="Filter by ward ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[RoomResponse]:
    """List all rooms with optional filtering"""
    rooms = get_rooms(db, ward_id=ward_id, skip=skip, limit=limit)
    return rooms


@router.get("/rooms/{room_id}", response_model=RoomResponse)
def get_room_details(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> RoomResponse:
    """Get room details with bed statistics"""
    room = get_room(db, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    return room


@router.put("/rooms/{room_id}/status", response_model=RoomStatusResponse)
def update_room_status_endpoint(
    room_id: int,
    status_update: RoomStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> RoomStatusResponse:
    """Update room status (admin/staff only)"""
    if not current_user.is_superuser and current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    room = update_room_status(db, room_id, status_update, current_user.id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    return RoomStatusResponse(
        room_id=room.id,
        room_number=room.room_number,
        ward_id=room.ward_id,
        status=room.status,
        updated_at=datetime.now(),
        updated_by=current_user.full_name,
        notes=status_update.notes
    )


@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room_endpoint(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a room (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    if not delete_room(db, room_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )


# =============================================================================
# Bed Management Endpoints
# =============================================================================

@router.post("/beds", response_model=BedResponse, status_code=status.HTTP_201_CREATED)
def create_new_bed(
    bed_in: BedCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BedResponse:
    """Create a new bed in a room (admin/staff only)"""
    if not current_user.is_superuser and current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    room = get_room(db, bed_in.room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    bed = create_bed(db, bed_in, room)
    return bed


@router.get("/beds", response_model=List[BedResponse])
def list_beds(
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[BedResponse]:
    """List all beds with optional filtering"""
    beds = get_beds(db, room_id=room_id, skip=skip, limit=limit)
    return beds


@router.get("/beds/{bed_id}", response_model=BedResponse)
def get_bed_details(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BedResponse:
    """Get bed details"""
    bed = get_bed(db, bed_id)
    if not bed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bed not found"
        )
    return bed


# =============================================================================
# Bed Assignment Endpoints
# =============================================================================

@router.post("/assignments", response_model=BedAssignmentResponse, status_code=status.HTTP_201_CREATED)
def assign_bed(
    assignment: BedAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BedAssignmentResponse:
    """Assign a patient to a bed (staff/admin only)"""
    if not current_user.is_superuser and current_user.role not in ["admin", "staff", "doctor", "nurse"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    result = assign_patient_to_bed(db, assignment, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bed not available or not found"
        )

    # Get patient name
    from app.crud import patient as patient_crud
    patient = patient_crud.get_patient(db, assignment.patient_id)

    # Get bed details
    bed = get_bed(db, assignment.bed_id)

    return BedAssignmentResponse(
        assignment_id=result.id,
        patient_id=result.patient_id,
        patient_name=patient.full_name if patient else "Unknown",
        bed_id=result.bed_id,
        bed_number=bed.bed_number if bed else "",
        room_number=bed.room_number if bed else "",
        room_class=bed.room_class if bed else "",
        ward_id=bed.ward_id if bed else 0,
        assigned_at=result.assigned_at,
        assigned_by=current_user.full_name,
        expected_discharge_date=result.expected_discharge_date,
        notes=result.notes
    )


@router.post("/discharge", response_model=BedAssignmentResponse)
def discharge_from_bed(
    discharge: BedDischargeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BedAssignmentResponse:
    """Discharge a patient from bed (staff/admin only)"""
    if not current_user.is_superuser and current_user.role not in ["admin", "staff", "doctor", "nurse"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    result = discharge_patient_from_bed(db, discharge, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active assignment not found"
        )

    bed = get_bed(db, discharge.bed_id)
    from app.crud import patient as patient_crud
    patient = patient_crud.get_patient(db, discharge.patient_id)

    return BedAssignmentResponse(
        assignment_id=result.id,
        patient_id=result.patient_id,
        patient_name=patient.full_name if patient else "Unknown",
        bed_id=result.bed_id,
        bed_number=bed.bed_number if bed else "",
        room_number=bed.room_number if bed else "",
        room_class=bed.room_class if bed else "",
        ward_id=bed.ward_id if bed else 0,
        assigned_at=result.assigned_at,
        assigned_by=current_user.full_name,
        expected_discharge_date=result.expected_discharge_date,
        notes=result.notes
    )


@router.post("/transfers", response_model=BedTransferResponse, status_code=status.HTTP_201_CREATED)
def transfer_between_beds(
    transfer: BedTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BedTransferResponse:
    """Transfer patient between beds (staff/admin only)"""
    if not current_user.is_superuser and current_user.role not in ["admin", "staff", "doctor", "nurse"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    result = transfer_patient(db, transfer, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer failed - check bed availability and patient assignment"
        )

    from_bed = get_bed(db, transfer.from_bed_id)
    to_bed = get_bed(db, transfer.to_bed_id)
    from app.crud import patient as patient_crud
    patient = patient_crud.get_patient(db, transfer.patient_id)

    return BedTransferResponse(
        transfer_id=result.id,
        patient_id=result.patient_id,
        patient_name=patient.full_name if patient else "Unknown",
        from_bed={
            "bed_id": from_bed.id if from_bed else 0,
            "bed_number": from_bed.bed_number if from_bed else "",
            "room_number": from_bed.room_number if from_bed else "",
            "ward_id": from_bed.ward_id if from_bed else 0
        },
        to_bed={
            "bed_id": to_bed.id if to_bed else 0,
            "bed_number": to_bed.bed_number if to_bed else "",
            "room_number": to_bed.room_number if to_bed else "",
            "ward_id": to_bed.ward_id if to_bed else 0
        },
        transferred_at=result.transferred_at,
        transferred_by=current_user.full_name,
        reason=result.reason,
        transfer_notes=result.transfer_notes
    )


# =============================================================================
# Bed Availability Endpoints
# =============================================================================

@router.get("/availability", response_model=BedAvailabilityResponse)
def check_bed_availability(
    ward_id: Optional[int] = Query(None),
    room_class: Optional[str] = Query(None),
    gender_type: Optional[str] = Query(None),
    bed_type: Optional[str] = Query(None),
    floor: Optional[int] = Query(None),
    availability_status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BedAvailabilityResponse:
    """Check bed availability with filters"""
    from app.schemas.bed import BedStatus, RoomClass, GenderType

    filters = BedAvailabilityFilter(
        ward_id=ward_id,
        room_class=RoomClass(room_class) if room_class else None,
        gender_type=GenderType(gender_type) if gender_type else None,
        bed_type=bed_type,
        floor=floor,
        availability_status=BedStatus(availability_status) if availability_status else None
    )

    beds, total = get_available_beds(db, filters, skip=skip, limit=limit)

    # Calculate summary
    summary = {
        "available": sum(1 for b in beds if b.status == "available"),
        "occupied": sum(1 for b in beds if b.status == "occupied"),
        "maintenance": sum(1 for b in beds if b.status == "maintenance"),
        "reserved": sum(1 for b in beds if b.status == "reserved")
    }

    return BedAvailabilityResponse(
        filters=filters,
        beds=beds,
        total=total,
        summary=summary
    )


@router.get("/availability/summary", response_model=List[BedAvailabilitySummary])
def get_availability_summary(
    ward_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[BedAvailabilitySummary]:
    """Get bed availability summary by ward and class"""
    summaries = get_bed_availability_summary(db, ward_id=ward_id)

    # Get ward names
    from app.models.ward import Ward
    ward_names = {w.id: w.name for w in db.query(Ward).all()}

    result = []
    for s in summaries:
        ward_name = ward_names.get(s['ward_id'], f"Ward {s['ward_id']}")
        result.append(BedAvailabilitySummary(
            ward_id=s['ward_id'],
            ward_name=ward_name,
            room_class=s['room_class'],
            total_beds=s['total_beds'],
            available_beds=s['available_beds'],
            occupied_beds=s['occupied_beds'],
            maintenance_beds=s['maintenance_beds'],
            reserved_beds=s['reserved_beds'],
            occupancy_rate=s['occupancy_rate'],
            male_available=s['male_available'],
            female_available=s['female_available'],
            mixed_available=s['mixed_available']
        ))

    return result


# =============================================================================
# Bed Request Workflow Endpoints
# =============================================================================

@router.post("/requests", response_model=BedRequestResponse, status_code=status.HTTP_201_CREATED)
def create_bed_request_endpoint(
    request: BedRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BedRequestResponse:
    """Create a new bed request"""
    result = create_bed_request(db, request, current_user.id)

    from app.crud import patient as patient_crud
    patient = patient_crud.get_patient(db, request.patient_id)

    return BedRequestResponse(
        request_id=result.id,
        patient_id=result.patient_id,
        patient_name=patient.full_name if patient else "Unknown",
        requested_by=current_user.full_name,
        priority=result.priority,
        requested_room_class=result.requested_room_class,
        requested_ward_id=result.requested_ward_id,
        gender_preference=result.gender_preference,
        medical_requirements=result.medical_requirements,
        expected_admission_date=result.expected_admission_date,
        status=result.status,
        created_at=result.created_at,
        updated_at=result.updated_at
    )


@router.get("/requests", response_model=List[BedRequestResponse])
def list_bed_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[BedRequestResponse]:
    """List bed requests with optional status filter"""
    requests = get_bed_requests(db, status=status_filter, skip=skip, limit=limit)

    from app.crud import patient as patient_crud
    result = []
    for req in requests:
        patient = patient_crud.get_patient(db, req.patient_id)

        # Get assignment details if assigned
        assigned_bed = None
        if req.assigned_bed_id:
            bed = get_bed(db, req.assigned_bed_id)
            if bed:
                assigned_bed = {
                    "bed_id": bed.id,
                    "bed_number": bed.bed_number,
                    "room_number": bed.room_number,
                    "room_class": bed.room_class,
                    "ward_id": bed.ward_id
                }

        result.append(BedRequestResponse(
            request_id=req.id,
            patient_id=req.patient_id,
            patient_name=patient.full_name if patient else "Unknown",
            requested_by=current_user.full_name,
            priority=req.priority,
            requested_room_class=req.requested_room_class,
            requested_ward_id=req.requested_ward_id,
            gender_preference=req.gender_preference,
            medical_requirements=req.medical_requirements,
            expected_admission_date=req.expected_admission_date,
            status=req.status,
            assigned_bed_id=req.assigned_bed_id,
            assigned_at=req.assigned_at,
            approved_by=req.approved_by.full_name if req.approved_by else None,
            approved_at=req.approved_at,
            approval_notes=req.approval_notes,
            created_at=req.created_at,
            updated_at=req.updated_at
        ))

    return result


@router.post("/requests/{request_id}/approve", response_model=BedRequestResponse)
def approve_request(
    request_id: int,
    approval: BedRequestApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BedRequestResponse:
    """Approve a bed request (admin/staff only)"""
    if not current_user.is_superuser and current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    result = approve_bed_request(db, request_id, approval)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found or not in pending status"
        )

    from app.crud import patient as patient_crud
    patient = patient_crud.get_patient(db, result.patient_id)

    return BedRequestResponse(
        request_id=result.id,
        patient_id=result.patient_id,
        patient_name=patient.full_name if patient else "Unknown",
        requested_by=current_user.full_name,
        priority=result.priority,
        requested_room_class=result.requested_room_class,
        requested_ward_id=result.requested_ward_id,
        gender_preference=result.gender_preference,
        medical_requirements=result.medical_requirements,
        expected_admission_date=result.expected_admission_date,
        status=result.status,
        approved_by=result.approved_by.full_name if result.approved_by else None,
        approved_at=result.approved_at,
        approval_notes=result.approval_notes,
        created_at=result.created_at,
        updated_at=result.updated_at
    )


@router.post("/requests/{request_id}/assign", response_model=BedRequestResponse)
def assign_bed_to_request(
    request_id: int,
    bed_id: int = Query(..., description="Bed ID to assign"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BedRequestResponse:
    """Assign a bed to an approved request (admin/staff only)"""
    if not current_user.is_superuser and current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    result = assign_bed_request(db, request_id, bed_id, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request not found, not approved, or bed not available"
        )

    bed = get_bed(db, bed_id)
    from app.crud import patient as patient_crud
    patient = patient_crud.get_patient(db, result.patient_id)

    return BedRequestResponse(
        request_id=result.id,
        patient_id=result.patient_id,
        patient_name=patient.full_name if patient else "Unknown",
        requested_by=current_user.full_name,
        priority=result.priority,
        requested_room_class=result.requested_room_class,
        requested_ward_id=result.requested_ward_id,
        gender_preference=result.gender_preference,
        medical_requirements=result.medical_requirements,
        expected_admission_date=result.expected_admission_date,
        status=result.status,
        assigned_bed_id=result.assigned_bed_id,
        assigned_bed_number=bed.bed_number if bed else None,
        assigned_room_number=bed.room_number if bed else None,
        assigned_room_class=bed.room_class if bed else None,
        assigned_ward_id=bed.ward_id if bed else None,
        assigned_at=result.assigned_at,
        assigned_by=result.assigned_by_user.full_name if result.assigned_by_user else None,
        created_at=result.created_at,
        updated_at=result.updated_at
    )


# =============================================================================
# Dashboard Endpoints
# =============================================================================

@router.get("/dashboard", response_model=BedDashboardData)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BedDashboardData:
    """Get comprehensive bed dashboard data"""
    dashboard_data = get_bed_dashboard_data(db)

    summary = BedDashboardSummary(
        hospital_name=settings.PROJECT_NAME,
        last_updated=datetime.now(),
        **dashboard_data
    )

    # Get ward summaries
    ward_summaries = get_bed_availability_summary(db)
    from app.models.ward import Ward
    ward_names = {w.id: w.name for w in db.query(Ward).all()}

    wards = []
    for s in ward_summaries:
        ward_name = ward_names.get(s['ward_id'], f"Ward {s['ward_id']}")
        wards.append(BedAvailabilitySummary(
            ward_id=s['ward_id'],
            ward_name=ward_name,
            room_class=s['room_class'],
            total_beds=s['total_beds'],
            available_beds=s['available_beds'],
            occupied_beds=s['occupied_beds'],
            maintenance_beds=s['maintenance_beds'],
            reserved_beds=s['reserved_beds'],
            occupancy_rate=s['occupancy_rate'],
            male_available=s['male_available'],
            female_available=s['female_available'],
            mixed_available=s['mixed_available']
        ))

    # Get recent assignments
    recent_assignments = get_recent_assignments(db, limit=10)
    from app.crud import patient as patient_crud

    assignments = []
    for a in recent_assignments:
        patient = patient_crud.get_patient(db, a.patient_id)
        bed = get_bed(db, a.bed_id)
        assignments.append(BedAssignmentResponse(
            assignment_id=a.id,
            patient_id=a.patient_id,
            patient_name=patient.full_name if patient else "Unknown",
            bed_id=a.bed_id,
            bed_number=bed.bed_number if bed else "",
            room_number=bed.room_number if bed else "",
            room_class=bed.room_class if bed else "",
            ward_id=bed.ward_id if bed else 0,
            assigned_at=a.assigned_at,
            assigned_by=a.assigned_by.full_name if a.assigned_by else "",
            expected_discharge_date=a.expected_discharge_date,
            notes=a.notes
        ))

    # Get pending requests
    pending_requests = get_pending_bed_requests(db)
    requests = []
    for req in pending_requests:
        patient = patient_crud.get_patient(db, req.patient_id)
        requests.append(BedRequestResponse(
            request_id=req.id,
            patient_id=req.patient_id,
            patient_name=patient.full_name if patient else "Unknown",
            requested_by=req.requested_by.full_name if req.requested_by else "",
            priority=req.priority,
            requested_room_class=req.requested_room_class,
            requested_ward_id=req.requested_ward_id,
            gender_preference=req.gender_preference,
            medical_requirements=req.medical_requirements,
            expected_admission_date=req.expected_admission_date,
            status=req.status,
            created_at=req.created_at,
            updated_at=req.updated_at
        ))

    # Get all available beds
    filters = BedAvailabilityFilter()
    available_beds, _ = get_available_beds(db, filters, limit=1000)

    return BedDashboardData(
        summary=summary,
        wards=wards,
        recently_assigned=assignments,
        bed_requests_pending=requests,
        available_beds=available_beds
    )
