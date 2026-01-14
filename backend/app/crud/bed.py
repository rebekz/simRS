"""Bed Management System CRUD Operations for STORY-020

This module provides CRUD operations for:
- Room and bed management
- Bed availability tracking
- Bed assignment and transfer
- Room status management
- Bed request workflow
- Real-time bed dashboard
"""
from typing import List, Optional, Dict, Tuple
from datetime import datetime, date
from sqlalchemy import select, update, delete, func, and_, or_, case
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bed import Room, Bed, BedAssignment, BedTransfer, BedRequest, RoomStatusHistory
from app.models.patient import Patient
from app.models.user import User
from app.schemas.bed import (
    RoomCreate, RoomUpdate, RoomStatusUpdate,
    BedCreate, BedAssignmentRequest, BedTransferRequest,
    BedDischargeRequest, BedRequestCreate, BedRequestApproval,
    BedAvailabilityFilter, BedStatus
)


# =============================================================================
# Room CRUD Operations
# =============================================================================

def get_room(db: Session, room_id: int) -> Optional[Room]:
    """Get a room by ID"""
    return db.query(Room).filter(Room.id == room_id).first()


def get_room_by_number(db: Session, ward_id: int, room_number: str) -> Optional[Room]:
    """Get a room by ward and room number"""
    return db.query(Room).filter(
        and_(Room.ward_id == ward_id, Room.room_number == room_number)
    ).first()


def get_rooms(db: Session, ward_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Room]:
    """Get list of rooms, optionally filtered by ward"""
    query = db.query(Room)
    if ward_id:
        query = query.filter(Room.ward_id == ward_id)
    return query.offset(skip).limit(limit).all()


def create_room(db: Session, room: RoomCreate) -> Room:
    """Create a new room"""
    db_room = Room(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


def update_room(db: Session, room_id: int, room_update: dict) -> Optional[Room]:
    """Update room details"""
    db_room = get_room(db, room_id)
    if not db_room:
        return None
    for field, value in room_update.items():
        setattr(db_room, field, value)
    db.commit()
    db.refresh(db_room)
    return db_room


def update_room_status(db: Session, room_id: int, status_update: RoomStatusUpdate, user_id: int) -> Optional[Room]:
    """Update room status with history tracking"""
    db_room = get_room(db, room_id)
    if not db_room:
        return None

    # Create status history entry
    history = RoomStatusHistory(
        room_id=room_id,
        status=status_update.status,
        previous_status=db_room.status,
        notes=status_update.notes,
        clean_required=status_update.clean_required,
        maintenance_reason=status_update.maintenance_reason,
        updated_by_id=user_id
    )
    db.add(history)

    # Update room status
    db_room.status = status_update.status
    db.commit()
    db.refresh(db_room)
    return db_room


def delete_room(db: Session, room_id: int) -> bool:
    """Delete a room"""
    db_room = get_room(db, room_id)
    if not db_room:
        return False
    db.delete(db_room)
    db.commit()
    return True


# =============================================================================
# Bed CRUD Operations
# =============================================================================

def get_bed(db: Session, bed_id: int) -> Optional[Bed]:
    """Get a bed by ID"""
    return db.query(Bed).filter(Bed.id == bed_id).first()


def get_beds(db: Session, room_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Bed]:
    """Get list of beds, optionally filtered by room"""
    query = db.query(Bed)
    if room_id:
        query = query.filter(Bed.room_id == room_id)
    return query.offset(skip).limit(limit).all()


def get_bed_by_number(db: Session, room_id: int, bed_number: str) -> Optional[Bed]:
    """Get a bed by room and bed number"""
    return db.query(Bed).filter(
        and_(Bed.room_id == room_id, Bed.bed_number == bed_number)
    ).first()


def create_bed(db: Session, bed: BedCreate, room: Room) -> Bed:
    """Create a new bed"""
    # Create bed with denormalized fields from room
    db_bed = Bed(
        **bed.model_dump(),
        room_number=room.room_number,
        ward_id=room.ward_id,
        room_class=room.room_class,
        gender_type=room.gender_type,
        floor=room.floor
    )
    db.add(db_bed)
    db.commit()
    db.refresh(db_bed)
    return db_bed


def update_bed_status(db: Session, bed_id: int, status: BedStatus) -> Optional[Bed]:
    """Update bed status"""
    db_bed = get_bed(db, bed_id)
    if not db_bed:
        return None
    db_bed.status = status
    db.commit()
    db.refresh(db_bed)
    return db_bed


# =============================================================================
# Bed Assignment Operations
# =============================================================================

def assign_patient_to_bed(
    db: Session,
    assignment: BedAssignmentRequest,
    assigned_by_id: int
) -> Optional[BedAssignment]:
    """Assign a patient to a bed"""
    # Verify bed is available
    bed = get_bed(db, assignment.bed_id)
    if not bed or bed.status != BedStatus.AVAILABLE:
        return None

    # Create assignment
    db_assignment = BedAssignment(
        patient_id=assignment.patient_id,
        bed_id=assignment.bed_id,
        admission_id=assignment.admission_id,
        assigned_by_id=assigned_by_id,
        expected_discharge_date=assignment.expected_discharge_date,
        notes=assignment.notes,
        assign_for_isolation=assignment.assign_for_isolation
    )
    db.add(db_assignment)

    # Update bed status and patient info
    bed.status = BedStatus.OCCUPIED
    bed.current_patient_id = assignment.patient_id
    bed.admission_date = datetime.now()
    bed.expected_discharge_date = assignment.expected_discharge_date

    db.commit()
    db.refresh(db_assignment)
    return db_assignment


def discharge_patient_from_bed(
    db: Session,
    discharge: BedDischargeRequest,
    discharged_by_id: int
) -> Optional[BedAssignment]:
    """Discharge a patient from bed"""
    # Get active assignment
    assignment = db.query(BedAssignment).filter(
        and_(
            BedAssignment.bed_id == discharge.bed_id,
            BedAssignment.patient_id == discharge.patient_id,
            BedAssignment.discharged_at.is_(None)
        )
    ).first()

    if not assignment:
        return None

    # Update assignment
    assignment.discharged_at = datetime.now()
    assignment.discharged_by_id = discharged_by_id
    assignment.discharge_notes = discharge.discharge_notes

    # Update bed status
    bed = get_bed(db, discharge.bed_id)
    if bed:
        bed.status = BedStatus.AVAILABLE
        bed.current_patient_id = None
        bed.admission_date = None
        bed.expected_discharge_date = None

        # Mark room as soiled if clean required
        if discharge.clean_required:
            room = get_room(db, bed.room_id)
            if room:
                room.status = "soiled"

    db.commit()
    db.refresh(assignment)
    return assignment


def transfer_patient(
    db: Session,
    transfer: BedTransferRequest,
    transferred_by_id: int
) -> Optional[BedTransfer]:
    """Transfer patient between beds"""
    # Verify from_bed has the patient
    from_bed = get_bed(db, transfer.from_bed_id)
    if not from_bed or from_bed.current_patient_id != transfer.patient_id:
        return None

    # Verify to_bed is available
    to_bed = get_bed(db, transfer.to_bed_id)
    if not to_bed or to_bed.status != BedStatus.AVAILABLE:
        return None

    # Close old assignment
    old_assignment = db.query(BedAssignment).filter(
        and_(
            BedAssignment.bed_id == transfer.from_bed_id,
            BedAssignment.patient_id == transfer.patient_id,
            BedAssignment.discharged_at.is_(None)
        )
    ).first()
    if old_assignment:
        old_assignment.discharged_at = datetime.now()

    # Create new assignment
    new_assignment = BedAssignment(
        patient_id=transfer.patient_id,
        bed_id=transfer.to_bed_id,
        assigned_by_id=transferred_by_id
    )
    db.add(new_assignment)

    # Create transfer record
    db_transfer = BedTransfer(
        patient_id=transfer.patient_id,
        from_bed_id=transfer.from_bed_id,
        to_bed_id=transfer.to_bed_id,
        reason=transfer.reason,
        transfer_notes=transfer.transfer_notes,
        transferred_by_id=transferred_by_id
    )
    db.add(db_transfer)

    # Update bed statuses
    from_bed.status = BedStatus.AVAILABLE
    from_bed.current_patient_id = None
    from_bed.admission_date = None

    to_bed.status = BedStatus.OCCUPIED
    to_bed.current_patient_id = transfer.patient_id
    to_bed.admission_date = datetime.now()

    db.commit()
    db.refresh(db_transfer)
    return db_transfer


def get_active_assignments(db: Session, patient_id: Optional[int] = None) -> List[BedAssignment]:
    """Get active bed assignments"""
    query = db.query(BedAssignment).filter(BedAssignment.discharged_at.is_(None))
    if patient_id:
        query = query.filter(BedAssignment.patient_id == patient_id)
    return query.all()


def get_patient_assignment_history(db: Session, patient_id: int, limit: int = 50) -> List[BedAssignment]:
    """Get patient's bed assignment history"""
    return db.query(BedAssignment).filter(
        BedAssignment.patient_id == patient_id
    ).order_by(BedAssignment.assigned_at.desc()).limit(limit).all()


# =============================================================================
# Bed Availability Operations
# =============================================================================

def get_available_beds(
    db: Session,
    filters: BedAvailabilityFilter,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[Bed], int]:
    """Get available beds with filtering"""
    query = db.query(Bed).filter(Bed.status == BedStatus.AVAILABLE)

    # Apply filters
    if filters.ward_id:
        query = query.filter(Bed.ward_id == filters.ward_id)
    if filters.room_class:
        query = query.filter(Bed.room_class == filters.room_class.value)
    if filters.gender_type:
        query = query.filter(Bed.gender_type == filters.gender_type.value)
    if filters.bed_type:
        query = query.filter(Bed.bed_type == filters.bed_type)
    if filters.floor is not None:
        query = query.filter(Bed.floor == filters.floor)

    total = query.count()
    beds = query.offset(skip).limit(limit).all()

    return beds, total


def get_bed_availability_summary(db: Session, ward_id: Optional[int] = None) -> List[Dict]:
    """Get bed availability summary grouped by ward and class"""
    query = db.query(
        Bed.ward_id,
        Bed.room_class,
        func.count(Bed.id).label('total_beds'),
        func.sum(case((Bed.status == 'available', 1), else_=0)).label('available_beds'),
        func.sum(case((Bed.status == 'occupied', 1), else_=0)).label('occupied_beds'),
        func.sum(case((Bed.status == 'maintenance', 1), else_=0)).label('maintenance_beds'),
        func.sum(case((Bed.status == 'reserved', 1), else_=0)).label('reserved_beds')
    ).group_by(Bed.ward_id, Bed.room_class)

    if ward_id:
        query = query.filter(Bed.ward_id == ward_id)

    results = query.all()

    summaries = []
    for row in results:
        occupancy_rate = (row.occupied_beds / row.total_beds * 100) if row.total_beds > 0 else 0

        # Get gender breakdown
        gender_query = db.query(
            Bed.gender_type,
            func.sum(case((Bed.status == 'available', 1), else_=0)).label('available')
        ).filter(
            and_(Bed.ward_id == row.ward_id, Bed.room_class == row.room_class)
        ).group_by(Bed.gender_type)

        gender_counts = {g.gender_type: int(g.available) for g in gender_query.all()}

        summaries.append({
            'ward_id': row.ward_id,
            'room_class': row.room_class,
            'total_beds': row.total_beds,
            'available_beds': int(row.available_beds or 0),
            'occupied_beds': int(row.occupied_beds or 0),
            'maintenance_beds': int(row.maintenance_beds or 0),
            'reserved_beds': int(row.reserved_beds or 0),
            'occupancy_rate': round(occupancy_rate, 2),
            'male_available': gender_counts.get('male', 0),
            'female_available': gender_counts.get('female', 0),
            'mixed_available': gender_counts.get('mixed', 0)
        })

    return summaries


# =============================================================================
# Bed Request Operations
# =============================================================================

def create_bed_request(db: Session, request: BedRequestCreate, requested_by_id: int) -> BedRequest:
    """Create a new bed request"""
    db_request = BedRequest(
        **request.model_dump(exclude={'requested_by_id'}),
        requested_by_id=requested_by_id
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def approve_bed_request(
    db: Session,
    request_id: int,
    approval: BedRequestApproval
) -> Optional[BedRequest]:
    """Approve a bed request"""
    db_request = db.query(BedRequest).filter(BedRequest.id == request_id).first()
    if not db_request or db_request.status != "pending":
        return None

    db_request.status = "approved"
    db_request.approved_by_id = approval.approved_by_id
    db_request.approved_at = datetime.now()
    db_request.approval_notes = approval.notes

    db.commit()
    db.refresh(db_request)
    return db_request


def assign_bed_request(
    db: Session,
    request_id: int,
    bed_id: int,
    assigned_by_id: int
) -> Optional[BedRequest]:
    """Assign a bed to an approved request"""
    db_request = db.query(BedRequest).filter(BedRequest.id == request_id).first()
    if not db_request or db_request.status != "approved":
        return None

    bed = get_bed(db, bed_id)
    if not bed or bed.status != BedStatus.AVAILABLE:
        return None

    # Assign the bed
    assignment = assign_patient_to_bed(
        db,
        BedAssignmentRequest(
            patient_id=db_request.patient_id,
            bed_id=bed_id,
            expected_discharge_date=db_request.expected_admission_date
        ),
        assigned_by_id
    )

    if assignment:
        db_request.status = "assigned"
        db_request.assigned_bed_id = bed_id
        db_request.assigned_at = datetime.now()
        db_request.assigned_by_id = assigned_by_id

        db.commit()
        db.refresh(db_request)
        return db_request

    return None


def cancel_bed_request(db: Session, request_id: int, cancelled_by_id: int, reason: str) -> Optional[BedRequest]:
    """Cancel a bed request"""
    db_request = db.query(BedRequest).filter(BedRequest.id == request_id).first()
    if not db_request or db_request.status in ["completed", "cancelled"]:
        return None

    db_request.status = "cancelled"
    db_request.cancelled_by_id = cancelled_by_id
    db_request.cancelled_at = datetime.now()
    db_request.cancellation_reason = reason

    db.commit()
    db.refresh(db_request)
    return db_request


def get_bed_requests(db: Session, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[BedRequest]:
    """Get bed requests, optionally filtered by status"""
    query = db.query(BedRequest)
    if status:
        query = query.filter(BedRequest.status == status)
    return query.order_by(BedRequest.created_at.desc()).offset(skip).limit(limit).all()


def get_pending_bed_requests(db: Session) -> List[BedRequest]:
    """Get all pending bed requests ordered by priority"""
    priority_order = case(
        (BedRequest.priority == 'emergency', 1),
        (BedRequest.priority == 'urgent', 2),
        (BedRequest.priority == 'routine', 3),
    )
    return db.query(BedRequest).filter(
        BedRequest.status == "pending"
    ).order_by(priority_order, BedRequest.created_at).all()


# =============================================================================
# Bed Dashboard Operations
# =============================================================================

def get_bed_dashboard_data(db: Session) -> Dict:
    """Get comprehensive bed dashboard data"""
    # Overall statistics
    total_beds = db.query(func.count(Bed.id)).scalar()
    total_available = db.query(func.count(Bed.id)).filter(Bed.status == 'available').scalar()
    total_occupied = db.query(func.count(Bed.id)).filter(Bed.status == 'occupied').scalar()
    total_maintenance = db.query(func.count(Bed.id)).filter(Bed.status == 'maintenance').scalar()

    occupancy_rate = (total_occupied / total_beds * 100) if total_beds > 0 else 0

    # By class
    by_class = {}
    for room_class in ['vvip', 'vip', '1', '2', '3']:
        class_beds = db.query(
            func.count(Bed.id).label('total'),
            func.sum(case((Bed.status == 'available', 1), else_=0)).label('available'),
            func.sum(case((Bed.status == 'occupied', 1), else_=0)).label('occupied'),
            func.sum(case((Bed.status == 'maintenance', 1), else_=0)).label('maintenance')
        ).filter(Bed.room_class == room_class).first()

        by_class[room_class] = {
            'total': int(class_beds.total or 0),
            'available': int(class_beds.available or 0),
            'occupied': int(class_beds.occupied or 0),
            'maintenance': int(class_beds.maintenance or 0)
        }

    # By ward
    by_ward = {}
    wards = db.query(Bed.ward_id).distinct().all()
    for (ward_id,) in wards:
        ward_beds = db.query(
            func.count(Bed.id).label('total'),
            func.sum(case((Bed.status == 'available', 1), else_=0)).label('available'),
            func.sum(case((Bed.status == 'occupied', 1), else_=0)).label('occupied')
        ).filter(Bed.ward_id == ward_id).first()

        by_ward[str(ward_id)] = {
            'total': int(ward_beds.total or 0),
            'available': int(ward_beds.available or 0),
            'occupied': int(ward_beds.occupied or 0)
        }

    # ICU statistics
    icu_beds = db.query(
        func.count(Bed.id).label('total'),
        func.sum(case((Bed.status == 'available', 1), else_=0)).label('available')
    ).filter(Bed.bed_type == 'icu').first()

    icu_total = int(icu_beds.total or 0)
    icu_available = int(icu_beds.available or 0)
    icu_occupancy_rate = ((icu_total - icu_available) / icu_total * 100) if icu_total > 0 else 0

    # Available beds by class
    available_by_class = {
        'vvip': by_class['vvip']['available'],
        'vip': by_class['vip']['available'],
        'class_1': by_class['1']['available'],
        'class_2': by_class['2']['available'],
        'class_3': by_class['3']['available']
    }

    return {
        'total_beds': total_beds,
        'total_available': total_available,
        'total_occupied': total_occupied,
        'total_maintenance': total_maintenance,
        'occupancy_rate': round(occupancy_rate, 2),
        'by_class': by_class,
        'by_ward': by_ward,
        'icu_total': icu_total,
        'icu_available': icu_available,
        'icu_occupancy_rate': round(icu_occupancy_rate, 2),
        'available_vvip': available_by_class['vvip'],
        'available_vip': available_by_class['vip'],
        'available_class_1': available_by_class['class_1'],
        'available_class_2': available_by_class['class_2'],
        'available_class_3': available_by_class['class_3']
    }


def get_recent_assignments(db: Session, limit: int = 10) -> List[BedAssignment]:
    """Get recent bed assignments"""
    return db.query(BedAssignment).order_by(
        BedAssignment.assigned_at.desc()
    ).limit(limit).all()
