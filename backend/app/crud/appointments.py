"""Appointment Booking CRUD Operations

This module provides comprehensive CRUD operations for appointment booking including:
- Appointment Management
- Slot Management
- Queue Management for appointments
- Booking Logic
- Reminders

All functions follow SQLAlchemy 2.0+ async patterns.
"""
from datetime import datetime, date, time, timedelta, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import (
    select,
    and_,
    or_,
    func,
    desc,
    asc,
    update,
    delete,
    exists
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Import models (these would be defined in models/appointment.py)
# For now, we'll use placeholders that match typical appointment system models


# =============================================================================
# APPOINTMENT MANAGEMENT
# =============================================================================

async def get_appointment(
    db: AsyncSession,
    appointment_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get a specific appointment by ID.

    Args:
        db: Database session
        appointment_id: Appointment ID

    Returns:
        Appointment data or None
    """
    # This would query the appointments table
    # For now, returning a placeholder structure
    query = select(Appointment).where(Appointment.id == appointment_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_appointments(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Get appointments with filtering and pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        patient_id: Filter by patient ID
        doctor_id: Filter by doctor ID
        department: Filter by department
        status: Filter by status (scheduled, confirmed, completed, cancelled, no_show)
        start_date: Filter by start date
        end_date: Filter by end date

    Returns:
        Tuple of (list of appointments, total count)
    """
    # Build base query
    query = select(Appointment)
    count_query = select(func.count(Appointment.id))

    # Apply filters
    conditions = []
    if patient_id:
        conditions.append(Appointment.patient_id == patient_id)
    if doctor_id:
        conditions.append(Appointment.doctor_id == doctor_id)
    if department:
        conditions.append(Appointment.department == department)
    if status:
        conditions.append(Appointment.status == status)
    if start_date:
        conditions.append(Appointment.appointment_date >= start_date)
    if end_date:
        conditions.append(Appointment.appointment_date <= end_date)

    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination and ordering
    query = query.order_by(Appointment.appointment_date, Appointment.appointment_time)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    appointments = result.scalars().all()

    return list(appointments), total


async def create_appointment(
    db: AsyncSession,
    patient_id: int,
    doctor_id: int,
    appointment_date: date,
    appointment_time: time,
    department: str,
    appointment_type: str = "regular",
    duration_minutes: int = 30,
    notes: Optional[str] = None,
    slot_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create a new appointment.

    Args:
        db: Database session
        patient_id: Patient ID
        doctor_id: Doctor ID
        appointment_date: Appointment date
        appointment_time: Appointment time
        department: Department name
        appointment_type: Type of appointment (regular, follow_up, emergency)
        duration_minutes: Expected duration in minutes
        notes: Additional notes
        slot_id: Optional appointment slot ID

    Returns:
        Created appointment
    """
    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        department=department,
        appointment_type=appointment_type,
        duration_minutes=duration_minutes,
        notes=notes,
        slot_id=slot_id,
        status="scheduled",
        created_at=datetime.now(timezone.utc)
    )

    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)

    return appointment


async def update_appointment(
    db: AsyncSession,
    appointment_id: int,
    appointment_date: Optional[date] = None,
    appointment_time: Optional[time] = None,
    department: Optional[str] = None,
    appointment_type: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    notes: Optional[str] = None,
    status: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Update an existing appointment.

    Args:
        db: Database session
        appointment_id: Appointment ID
        appointment_date: New appointment date
        appointment_time: New appointment time
        department: New department
        appointment_type: New appointment type
        duration_minutes: New duration
        notes: New notes
        status: New status

    Returns:
        Updated appointment or None
    """
    appointment = await get_appointment(db, appointment_id)
    if not appointment:
        return None

    update_data = {}
    if appointment_date is not None:
        update_data['appointment_date'] = appointment_date
    if appointment_time is not None:
        update_data['appointment_time'] = appointment_time
    if department is not None:
        update_data['department'] = department
    if appointment_type is not None:
        update_data['appointment_type'] = appointment_type
    if duration_minutes is not None:
        update_data['duration_minutes'] = duration_minutes
    if notes is not None:
        update_data['notes'] = notes
    if status is not None:
        update_data['status'] = status

    if update_data:
        update_data['updated_at'] = datetime.now(timezone.utc)
        await db.execute(
            update(Appointment)
            .where(Appointment.id == appointment_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(appointment)

    return appointment


async def cancel_appointment(
    db: AsyncSession,
    appointment_id: int,
    cancellation_reason: Optional[str] = None,
    cancelled_by: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Cancel an appointment.

    Args:
        db: Database session
        appointment_id: Appointment ID
        cancellation_reason: Reason for cancellation
        cancelled_by: User ID who cancelled

    Returns:
        Cancelled appointment or None
    """
    appointment = await get_appointment(db, appointment_id)
    if not appointment:
        return None

    await db.execute(
        update(Appointment)
        .where(Appointment.id == appointment_id)
        .values(
            status="cancelled",
            cancellation_reason=cancellation_reason,
            cancelled_at=datetime.now(timezone.utc),
            cancelled_by=cancelled_by
        )
    )
    await db.commit()
    await db.refresh(appointment)

    return appointment


async def get_patient_appointments(
    db: AsyncSession,
    patient_id: int,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    include_past: bool = True
) -> List[Dict[str, Any]]:
    """
    Get all appointments for a specific patient.

    Args:
        db: Database session
        patient_id: Patient ID
        status: Filter by status
        from_date: Start date filter
        to_date: End date filter
        include_past: Include past appointments

    Returns:
        List of patient appointments
    """
    query = select(Appointment).where(Appointment.patient_id == patient_id)

    conditions = []
    if status:
        conditions.append(Appointment.status == status)
    if from_date:
        conditions.append(Appointment.appointment_date >= from_date)
    if to_date:
        conditions.append(Appointment.appointment_date <= to_date)
    if not include_past:
        conditions.append(
            or_(
                Appointment.appointment_date > date.today(),
                and_(
                    Appointment.appointment_date == date.today(),
                    Appointment.appointment_time >= datetime.now().time()
                )
            )
        )

    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(desc(Appointment.appointment_date), desc(Appointment.appointment_time))

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_doctor_appointments(
    db: AsyncSession,
    doctor_id: int,
    appointment_date: Optional[date] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all appointments for a specific doctor.

    Args:
        db: Database session
        doctor_id: Doctor ID
        appointment_date: Filter by specific date
        status: Filter by status

    Returns:
        List of doctor appointments
    """
    query = select(Appointment).where(Appointment.doctor_id == doctor_id)

    conditions = []
    if appointment_date:
        conditions.append(Appointment.appointment_date == appointment_date)
    if status:
        conditions.append(Appointment.status == status)

    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(Appointment.appointment_date, Appointment.appointment_time)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_department_appointments(
    db: AsyncSession,
    department: str,
    appointment_date: Optional[date] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all appointments for a specific department.

    Args:
        db: Database session
        department: Department name
        appointment_date: Filter by specific date
        status: Filter by status

    Returns:
        List of department appointments
    """
    query = select(Appointment).where(Appointment.department == department)

    conditions = []
    if appointment_date:
        conditions.append(Appointment.appointment_date == appointment_date)
    if status:
        conditions.append(Appointment.status == status)

    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(Appointment.appointment_date, Appointment.appointment_time)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_upcoming_appointments(
    db: AsyncSession,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    days_ahead: int = 30
) -> List[Dict[str, Any]]:
    """
    Get upcoming appointments within specified days.

    Args:
        db: Database session
        patient_id: Filter by patient ID
        doctor_id: Filter by doctor ID
        days_ahead: Number of days to look ahead

    Returns:
        List of upcoming appointments
    """
    start_date = date.today()
    end_date = start_date + timedelta(days=days_ahead)

    query = select(Appointment).where(
        and_(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date,
            Appointment.status.in_(['scheduled', 'confirmed'])
        )
    )

    conditions = []
    if patient_id:
        conditions.append(Appointment.patient_id == patient_id)
    if doctor_id:
        conditions.append(Appointment.doctor_id == doctor_id)

    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(Appointment.appointment_date, Appointment.appointment_time)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_today_appointments(
    db: AsyncSession,
    doctor_id: Optional[int] = None,
    department: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all appointments for today.

    Args:
        db: Database session
        doctor_id: Filter by doctor ID
        department: Filter by department
        status: Filter by status

    Returns:
        List of today's appointments
    """
    today = date.today()

    query = select(Appointment).where(Appointment.appointment_date == today)

    conditions = []
    if doctor_id:
        conditions.append(Appointment.doctor_id == doctor_id)
    if department:
        conditions.append(Appointment.department == department)
    if status:
        conditions.append(Appointment.status == status)

    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(Appointment.appointment_time)

    result = await db.execute(query)
    return list(result.scalars().all())


# =============================================================================
# SLOT MANAGEMENT
# =============================================================================

async def get_appointment_slot(
    db: AsyncSession,
    slot_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get a specific appointment slot by ID.

    Args:
        db: Database session
        slot_id: Slot ID

    Returns:
        Slot data or None
    """
    query = select(AppointmentSlot).where(AppointmentSlot.id == slot_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_available_slots(
    db: AsyncSession,
    doctor_id: int,
    slot_date: date,
    department: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all available appointment slots for a doctor on a specific date.

    Args:
        db: Database session
        doctor_id: Doctor ID
        slot_date: Date to check
        department: Filter by department

    Returns:
        List of available slots
    """
    query = select(AppointmentSlot).where(
        and_(
            AppointmentSlot.doctor_id == doctor_id,
            AppointmentSlot.slot_date == slot_date,
            AppointmentSlot.is_available == True
        )
    )

    if department:
        query = query.where(AppointmentSlot.department == department)

    query = query.order_by(AppointmentSlot.start_time)

    result = await db.execute(query)
    return list(result.scalars().all())


async def create_slot(
    db: AsyncSession,
    doctor_id: int,
    slot_date: date,
    start_time: time,
    end_time: time,
    department: str,
    max_bookings: int = 1,
    slot_type: str = "regular"
) -> Dict[str, Any]:
    """
    Create a new appointment slot.

    Args:
        db: Database session
        doctor_id: Doctor ID
        slot_date: Slot date
        start_time: Slot start time
        end_time: Slot end time
        department: Department name
        max_bookings: Maximum number of bookings for this slot
        slot_type: Type of slot (regular, priority, emergency)

    Returns:
        Created slot
    """
    slot = AppointmentSlot(
        doctor_id=doctor_id,
        slot_date=slot_date,
        start_time=start_time,
        end_time=end_time,
        department=department,
        max_bookings=max_bookings,
        current_bookings=0,
        slot_type=slot_type,
        is_available=True
    )

    db.add(slot)
    await db.commit()
    await db.refresh(slot)

    return slot


async def update_slot(
    db: AsyncSession,
    slot_id: int,
    max_bookings: Optional[int] = None,
    is_available: Optional[bool] = None,
    slot_type: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Update an appointment slot.

    Args:
        db: Database session
        slot_id: Slot ID
        max_bookings: New maximum bookings
        is_available: New availability status
        slot_type: New slot type

    Returns:
        Updated slot or None
    """
    slot = await get_appointment_slot(db, slot_id)
    if not slot:
        return None

    update_data = {}
    if max_bookings is not None:
        update_data['max_bookings'] = max_bookings
    if is_available is not None:
        update_data['is_available'] = is_available
    if slot_type is not None:
        update_data['slot_type'] = slot_type

    if update_data:
        update_data['updated_at'] = datetime.now(timezone.utc)
        await db.execute(
            update(AppointmentSlot)
            .where(AppointmentSlot.id == slot_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(slot)

    return slot


async def delete_slot(
    db: AsyncSession,
    slot_id: int
) -> bool:
    """
    Delete an appointment slot.

    Args:
        db: Database session
        slot_id: Slot ID

    Returns:
        True if deleted, False otherwise
    """
    slot = await get_appointment_slot(db, slot_id)
    if not slot:
        return False

    await db.execute(
        delete(AppointmentSlot).where(AppointmentSlot.id == slot_id)
    )
    await db.commit()

    return True


async def get_doctor_availability(
    db: AsyncSession,
    doctor_id: int,
    start_date: date,
    end_date: date,
    department: Optional[str] = None
) -> Dict[date, List[Dict[str, Any]]]:
    """
    Get doctor's availability across a date range.

    Args:
        db: Database session
        doctor_id: Doctor ID
        start_date: Start date
        end_date: End date
        department: Filter by department

    Returns:
        Dictionary mapping dates to available slots
    """
    query = select(AppointmentSlot).where(
        and_(
            AppointmentSlot.doctor_id == doctor_id,
            AppointmentSlot.slot_date >= start_date,
            AppointmentSlot.slot_date <= end_date,
            AppointmentSlot.is_available == True
        )
    )

    if department:
        query = query.where(AppointmentSlot.department == department)

    query = query.order_by(AppointmentSlot.slot_date, AppointmentSlot.start_time)

    result = await db.execute(query)
    slots = result.scalars().all()

    # Group by date
    availability = {}
    for slot in slots:
        if slot.slot_date not in availability:
            availability[slot.slot_date] = []
        availability[slot.slot_date].append(slot)

    return availability


async def get_department_availability(
    db: AsyncSession,
    department: str,
    appointment_date: date
) -> Dict[int, List[Dict[str, Any]]]:
    """
    Get availability for all doctors in a department on a specific date.

    Args:
        db: Database session
        department: Department name
        appointment_date: Date to check

    Returns:
        Dictionary mapping doctor IDs to available slots
    """
    query = select(AppointmentSlot).where(
        and_(
            AppointmentSlot.department == department,
            AppointmentSlot.slot_date == appointment_date,
            AppointmentSlot.is_available == True
        )
    ).order_by(AppointmentSlot.doctor_id, AppointmentSlot.start_time)

    result = await db.execute(query)
    slots = result.scalars().all()

    # Group by doctor
    availability = {}
    for slot in slots:
        if slot.doctor_id not in availability:
            availability[slot.doctor_id] = []
        availability[slot.doctor_id].append(slot)

    return availability


async def check_slot_availability(
    db: AsyncSession,
    slot_id: int
) -> bool:
    """
    Check if a slot has available capacity.

    Args:
        db: Database session
        slot_id: Slot ID

    Returns:
        True if slot is available, False otherwise
    """
    slot = await get_appointment_slot(db, slot_id)
    if not slot or not slot.is_available:
        return False

    return slot.current_bookings < slot.max_bookings


async def book_slot(
    db: AsyncSession,
    slot_id: int
) -> Optional[Dict[str, Any]]:
    """
    Book a slot (increment current bookings).

    Args:
        db: Database session
        slot_id: Slot ID

    Returns:
        Updated slot or None if slot is full
    """
    slot = await get_appointment_slot(db, slot_id)
    if not slot:
        return None

    if slot.current_bookings >= slot.max_bookings:
        return None

    await db.execute(
        update(AppointmentSlot)
        .where(AppointmentSlot.id == slot_id)
        .values(current_bookings=AppointmentSlot.current_bookings + 1)
    )
    await db.commit()
    await db.refresh(slot)

    return slot


async def release_slot(
    db: AsyncSession,
    slot_id: int
) -> Optional[Dict[str, Any]]:
    """
    Release a slot (decrement current bookings).

    Args:
        db: Database session
        slot_id: Slot ID

    Returns:
        Updated slot or None
    """
    slot = await get_appointment_slot(db, slot_id)
    if not slot:
        return None

    if slot.current_bookings > 0:
        await db.execute(
            update(AppointmentSlot)
            .where(AppointmentSlot.id == slot_id)
            .values(current_bookings=AppointmentSlot.current_bookings - 1)
        )
        await db.commit()
        await db.refresh(slot)

    return slot


async def generate_daily_slots(
    db: AsyncSession,
    doctor_id: int,
    slot_date: date,
    department: str,
    start_hour: int = 8,
    end_hour: int = 17,
    slot_duration_minutes: int = 30,
    break_start: Optional[time] = None,
    break_end: Optional[time] = None
) -> List[Dict[str, Any]]:
    """
    Generate appointment slots for a specific day.

    Args:
        db: Database session
        doctor_id: Doctor ID
        slot_date: Date to generate slots for
        department: Department name
        start_hour: Start hour (default 8 AM)
        end_hour: End hour (default 5 PM)
        slot_duration_minutes: Duration of each slot
        break_start: Break start time (optional)
        break_end: Break end time (optional)

    Returns:
        List of created slots
    """
    slots = []
    current_time = datetime.combine(slot_date, time(start_hour, 0))
    end_time = datetime.combine(slot_date, time(end_hour, 0))

    # Handle break times
    break_start_dt = datetime.combine(slot_date, break_start) if break_start else None
    break_end_dt = datetime.combine(slot_date, break_end) if break_end else None

    while current_time < end_time:
        # Skip break time
        if break_start_dt and break_end_dt:
            if break_start_dt <= current_time < break_end_dt:
                current_time = break_end_dt
                continue

        slot_end_time = current_time + timedelta(minutes=slot_duration_minutes)

        if slot_end_time > end_time:
            break

        slot = await create_slot(
            db=db,
            doctor_id=doctor_id,
            slot_date=slot_date,
            start_time=current_time.time(),
            end_time=slot_end_time.time(),
            department=department
        )
        slots.append(slot)

        current_time = slot_end_time

    return slots


async def generate_recurring_slots(
    db: AsyncSession,
    doctor_id: int,
    start_date: date,
    end_date: date,
    department: str,
    weekdays: Optional[List[int]] = None,
    start_hour: int = 8,
    end_hour: int = 17,
    slot_duration_minutes: int = 30
) -> List[Dict[str, Any]]:
    """
    Generate recurring appointment slots for a date range.

    Args:
        db: Database session
        doctor_id: Doctor ID
        start_date: Start date
        end_date: End date
        department: Department name
        weekdays: List of weekdays (0=Monday, 6=Sunday), None for all days
        start_hour: Start hour
        end_hour: End hour
        slot_duration_minutes: Duration of each slot

    Returns:
        List of all created slots
    """
    if weekdays is None:
        weekdays = [0, 1, 2, 3, 4]  # Monday to Friday

    all_slots = []
    current_date = start_date

    while current_date <= end_date:
        # Check if current date is in specified weekdays
        if current_date.weekday() in weekdays:
            daily_slots = await generate_daily_slots(
                db=db,
                doctor_id=doctor_id,
                slot_date=current_date,
                department=department,
                start_hour=start_hour,
                end_hour=end_hour,
                slot_duration_minutes=slot_duration_minutes
            )
            all_slots.extend(daily_slots)

        current_date += timedelta(days=1)

    return all_slots


# =============================================================================
# QUEUE MANAGEMENT
# =============================================================================

async def get_queue_position(
    db: AsyncSession,
    appointment_id: int
) -> Optional[int]:
    """
    Get the queue position for an appointment.

    Args:
        db: Database session
        appointment_id: Appointment ID

    Returns:
        Queue position or None
    """
    appointment = await get_appointment(db, appointment_id)
    if not appointment:
        return None

    # Count appointments before this one for the same doctor and date
    query = select(func.count(Appointment.id)).where(
        and_(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.appointment_date == appointment.appointment_date,
            Appointment.appointment_time < appointment.appointment_time,
            Appointment.status.in_(['scheduled', 'confirmed'])
        )
    )

    result = await db.execute(query)
    position = result.scalar()

    return position + 1 if position is not None else None


async def update_queue_position(
    db: AsyncSession,
    appointment_id: int,
    new_position: int
) -> bool:
    """
    Update the queue position for an appointment.

    Args:
        db: Database session
        appointment_id: Appointment ID
        new_position: New queue position

    Returns:
        True if updated, False otherwise
    """
    await db.execute(
        update(Appointment)
        .where(Appointment.id == appointment_id)
        .values(queue_position=new_position)
    )
    await db.commit()

    return True


async def assign_queue_number(
    db: AsyncSession,
    appointment_id: int
) -> Optional[int]:
    """
    Assign a queue number to an appointment.

    Args:
        db: Database session
        appointment_id: Appointment ID

    Returns:
        Assigned queue number or None
    """
    appointment = await get_appointment(db, appointment_id)
    if not appointment:
        return None

    # Get the next queue number for this doctor and date
    query = select(func.max(Appointment.queue_number)).where(
        and_(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.appointment_date == appointment.appointment_date
        )
    )

    result = await db.execute(query)
    max_queue_number = result.scalar()

    next_queue_number = (max_queue_number or 0) + 1

    await db.execute(
        update(Appointment)
        .where(Appointment.id == appointment_id)
        .values(queue_number=next_queue_number)
    )
    await db.commit()

    return next_queue_number


async def calculate_wait_time(
    db: AsyncSession,
    appointment_id: int,
    avg_consultation_minutes: int = 15
) -> Optional[int]:
    """
    Calculate estimated wait time for an appointment.

    Args:
        db: Database session
        appointment_id: Appointment ID
        avg_consultation_minutes: Average consultation time

    Returns:
        Estimated wait time in minutes or None
    """
    appointment = await get_appointment(db, appointment_id)
    if not appointment:
        return None

    # Count patients ahead
    query = select(func.count(Appointment.id)).where(
        and_(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.appointment_date == appointment.appointment_date,
            Appointment.appointment_time < appointment.appointment_time,
            Appointment.status.in_(['scheduled', 'confirmed'])
        )
    )

    result = await db.execute(query)
    patients_ahead = result.scalar() or 0

    return patients_ahead * avg_consultation_minutes


async def update_wait_times(
    db: AsyncSession,
    doctor_id: int,
    appointment_date: date
) -> Dict[int, int]:
    """
    Update wait times for all appointments of a doctor on a specific date.

    Args:
        db: Database session
        doctor_id: Doctor ID
        appointment_date: Appointment date

    Returns:
        Dictionary mapping appointment IDs to estimated wait times
    """
    # Get all appointments for the doctor on this date
    appointments = await get_doctor_appointments(db, doctor_id, appointment_date)

    wait_times = {}
    for appointment in appointments:
        if appointment.status in ['scheduled', 'confirmed']:
            wait_time = await calculate_wait_time(db, appointment.id)
            if wait_time is not None:
                wait_times[appointment.id] = wait_time

                await db.execute(
                    update(Appointment)
                    .where(Appointment.id == appointment.id)
                    .values(estimated_wait_minutes=wait_time)
                )

    await db.commit()
    return wait_times


async def get_waiting_patients(
    db: AsyncSession,
    doctor_id: int,
    appointment_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """
    Get all patients waiting for a specific doctor.

    Args:
        db: Database session
        doctor_id: Doctor ID
        appointment_date: Filter by date (default today)

    Returns:
        List of waiting patients
    """
    if appointment_date is None:
        appointment_date = date.today()

    query = select(Appointment).where(
        and_(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status.in_(['scheduled', 'confirmed'])
        )
    ).order_by(Appointment.appointment_time)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_next_patient(
    db: AsyncSession,
    doctor_id: int,
    current_time: Optional[datetime] = None
) -> Optional[Dict[str, Any]]:
    """
    Get the next patient to be seen.

    Args:
        db: Database session
        doctor_id: Doctor ID
        current_time: Current time (default now)

    Returns:
        Next appointment or None
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    query = select(Appointment).where(
        and_(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == current_time.date(),
            Appointment.status.in_(['scheduled', 'confirmed']),
            Appointment.appointment_time <= current_time.time()
        )
    ).order_by(Appointment.appointment_time)

    result = await db.execute(query)
    return result.scalar_one_or_none()


# =============================================================================
# BOOKING LOGIC
# =============================================================================

async def book_appointment_with_slot(
    db: AsyncSession,
    patient_id: int,
    doctor_id: int,
    slot_id: int,
    department: str,
    appointment_type: str = "regular",
    notes: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Book an appointment with a specific slot (prevents double-booking).

    Args:
        db: Database session
        patient_id: Patient ID
        doctor_id: Doctor ID
        slot_id: Slot ID
        department: Department name
        appointment_type: Type of appointment
        notes: Additional notes

    Returns:
        Created appointment or None if slot is unavailable
    """
    # Check slot availability
    slot = await get_appointment_slot(db, slot_id)
    if not slot or not slot.is_available:
        return None

    if slot.current_bookings >= slot.max_bookings:
        return None

    # Check for conflicting appointments
    has_conflict = await check_conflicts(
        db=db,
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=slot.slot_date,
        appointment_time=slot.start_time
    )

    if has_conflict:
        return None

    # Create appointment
    appointment = await create_appointment(
        db=db,
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=slot.slot_date,
        appointment_time=slot.start_time,
        department=department,
        appointment_type=appointment_type,
        duration_minutes=int(
            (datetime.combine(date.today(), slot.end_time) -
             datetime.combine(date.today(), slot.start_time)).total_seconds() / 60
        ),
        notes=notes,
        slot_id=slot_id
    )

    # Book the slot
    await book_slot(db, slot_id)

    return appointment


async def reschedule_appointment(
    db: AsyncSession,
    appointment_id: int,
    new_date: date,
    new_time: time,
    new_slot_id: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Reschedule an appointment to a new date/time.

    Args:
        db: Database session
        appointment_id: Appointment ID
        new_date: New appointment date
        new_time: New appointment time
        new_slot_id: New slot ID (optional)

    Returns:
        Updated appointment or None
    """
    appointment = await get_appointment(db, appointment_id)
    if not appointment:
        return None

    # Release old slot if exists
    if appointment.slot_id:
        await release_slot(db, appointment.slot_id)

    # Book new slot if provided
    if new_slot_id:
        slot_available = await check_slot_availability(db, new_slot_id)
        if not slot_available:
            return None
        await book_slot(db, new_slot_id)

    # Update appointment
    updated_appointment = await update_appointment(
        db=db,
        appointment_id=appointment_id,
        appointment_date=new_date,
        appointment_time=new_time,
        slot_id=new_slot_id
    )

    return updated_appointment


async def check_conflicts(
    db: AsyncSession,
    patient_id: int,
    doctor_id: int,
    appointment_date: date,
    appointment_time: time,
    exclude_appointment_id: Optional[int] = None,
    duration_minutes: int = 30
) -> bool:
    """
    Check for conflicting appointments.

    Args:
        db: Database session
        patient_id: Patient ID
        doctor_id: Doctor ID
        appointment_date: Appointment date
        appointment_time: Appointment time
        exclude_appointment_id: Exclude this appointment from check
        duration_minutes: Duration to check for conflicts

    Returns:
        True if conflict exists, False otherwise
    """
    # Calculate time window
    start_window = datetime.combine(appointment_date, appointment_time)
    end_window = start_window + timedelta(minutes=duration_minutes)

    # Check for patient conflicts (patient shouldn't have overlapping appointments)
    patient_query = select(exists().where(
        and_(
            Appointment.patient_id == patient_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status.in_(['scheduled', 'confirmed']),
            Appointment.id != exclude_appointment_id if exclude_appointment_id else True
        )
    ))

    patient_result = await db.execute(patient_query)
    has_patient_conflict = patient_result.scalar()

    # Check for doctor conflicts (doctor shouldn't be double-booked)
    doctor_query = select(exists().where(
        and_(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status.in_(['scheduled', 'confirmed']),
            Appointment.id != exclude_appointment_id if exclude_appointment_id else True
        )
    ))

    doctor_result = await db.execute(doctor_query)
    has_doctor_conflict = doctor_result.scalar()

    return has_patient_conflict or has_doctor_conflict


async def validate_booking_time(
    db: AsyncSession,
    doctor_id: int,
    appointment_date: date,
    appointment_time: time,
    department: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate if booking time is within doctor's availability.

    Args:
        db: Database session
        doctor_id: Doctor ID
        appointment_date: Appointment date
        appointment_time: Appointment time
        department: Department name

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if date is in the past
    if appointment_date < date.today():
        return False, "Cannot book appointments in the past"

    # Check if date is too far in the future (more than 3 months)
    if appointment_date > date.today() + timedelta(days=90):
        return False, "Cannot book appointments more than 3 months in advance"

    # Check if there's a slot available for this time
    slot_query = select(AppointmentSlot).where(
        and_(
            AppointmentSlot.doctor_id == doctor_id,
            AppointmentSlot.slot_date == appointment_date,
            AppointmentSlot.start_time <= appointment_time,
            AppointmentSlot.end_time > appointment_time,
            AppointmentSlot.department == department,
            AppointmentSlot.is_available == True
        )
    )

    slot_result = await db.execute(slot_query)
    slot = slot_result.scalar_one_or_none()

    if not slot:
        return False, "No available slot at this time"

    return True, None


# =============================================================================
# REMINDERS
# =============================================================================

async def create_reminder(
    db: AsyncSession,
    appointment_id: int,
    reminder_type: str,
    reminder_time: datetime,
    message: Optional[str] = None,
    method: str = "sms"
) -> Dict[str, Any]:
    """
    Create a reminder for an appointment.

    Args:
        db: Database session
        appointment_id: Appointment ID
        reminder_type: Type of reminder (day_before, hour_before, custom)
        reminder_time: When to send the reminder
        message: Custom message
        method: Reminder method (sms, email, whatsapp)

    Returns:
        Created reminder
    """
    reminder = AppointmentReminder(
        appointment_id=appointment_id,
        reminder_type=reminder_type,
        reminder_time=reminder_time,
        message=message,
        method=method,
        status="pending"
    )

    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)

    return reminder


async def send_reminder(
    db: AsyncSession,
    reminder_id: int
) -> Optional[Dict[str, Any]]:
    """
    Send a reminder (mark as sent).

    Args:
        db: Database session
        reminder_id: Reminder ID

    Returns:
        Updated reminder or None
    """
    reminder = await get_reminder(db, reminder_id)
    if not reminder:
        return None

    await db.execute(
        update(AppointmentReminder)
        .where(AppointmentReminder.id == reminder_id)
        .values(
            status="sent",
            sent_at=datetime.now(timezone.utc)
        )
    )
    await db.commit()
    await db.refresh(reminder)

    return reminder


async def update_reminder_status(
    db: AsyncSession,
    reminder_id: int,
    status: str,
    error_message: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Update reminder status.

    Args:
        db: Database session
        reminder_id: Reminder ID
        status: New status (pending, sent, failed, cancelled)
        error_message: Error message if failed

    Returns:
        Updated reminder or None
    """
    update_data = {"status": status}

    if status == "sent":
        update_data["sent_at"] = datetime.now(timezone.utc)
    elif status == "failed" and error_message:
        update_data["error_message"] = error_message

    await db.execute(
        update(AppointmentReminder)
        .where(AppointmentReminder.id == reminder_id)
        .values(**update_data)
    )
    await db.commit()

    reminder = await get_reminder(db, reminder_id)
    return reminder


async def get_pending_reminders(
    db: AsyncSession,
    current_time: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Get all reminders that are pending and due to be sent.

    Args:
        db: Database session
        current_time: Current time (default now)

    Returns:
        List of pending reminders
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    query = select(AppointmentReminder).where(
        and_(
            AppointmentReminder.status == "pending",
            AppointmentReminder.reminder_time <= current_time
        )
    ).order_by(AppointmentReminder.reminder_time)

    result = await db.execute(query)
    return list(result.scalars().all())


async def process_reminders(
    db: AsyncSession,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Process pending reminders (mark as sent).

    Args:
        db: Database session
        limit: Maximum number of reminders to process

    Returns:
        List of processed reminders
    """
    pending_reminders = await get_pending_reminders(db)
    pending_reminders = pending_reminders[:limit]

    processed = []
    for reminder in pending_reminders:
        updated = await send_reminder(db, reminder.id)
        if updated:
            processed.append(updated)

    return processed


async def get_reminder(
    db: AsyncSession,
    reminder_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get a specific reminder by ID.

    Args:
        db: Database session
        reminder_id: Reminder ID

    Returns:
        Reminder data or None
    """
    query = select(AppointmentReminder).where(AppointmentReminder.id == reminder_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# =============================================================================
# MODEL DEFINITIONS (These would be in models/appointment.py)
# =============================================================================

# Placeholder classes - in production, these would be imported from models
class Appointment:
    """Appointment model placeholder"""
    pass


class AppointmentSlot:
    """Appointment slot model placeholder"""
    pass


class AppointmentReminder:
    """Appointment reminder model placeholder"""
    pass
