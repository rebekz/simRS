"""Queue Management CRUD Operations for STORY-010

This module provides CRUD operations for:
- Queue ticket generation and management
- Queue recall functionality
- Queue statistics
- SMS notification support
- Digital display data
- Queue transfer and cancellation
"""
from typing import List, Optional, Tuple, Dict
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_, or_, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import json

from app.models.queue import (
    QueueTicket, QueueRecall, QueueNotification,
    QueueStatisticsCache, QueueSettings, QueueTransfer
)
from app.models.patient import Patient
from app.models.user import User
from app.schemas.queue import (
    QueueDepartment, QueueStatus, QueuePriority,
    QueueTicketCreate, QueueTicketResponse,
    QueueRecallRequest, QueueRecallResponse,
    QueueStatistics, DepartmentQueueStatistics,
    DigitalDisplayData, DigitalDisplayResponse,
    MobileQueueStatus,
    QueueNotificationRequest, QueueNotificationResponse,
    QueueTransferRequest, QueueCancelRequest,
)


# =============================================================================
# Queue Ticket CRUD
# =============================================================================

async def create_queue_ticket(
    db: AsyncSession,
    ticket: QueueTicketCreate,
) -> QueueTicket:
    """Create a new queue ticket"""
    # Generate ticket number
    ticket_number = await _generate_ticket_number(
        db=db,
        department=ticket.department,
        date=date.today(),
        priority=ticket.priority
    )

    # Create ticket
    db_ticket = QueueTicket(
        ticket_number=ticket_number,
        department=ticket.department,
        date=date.today(),
        patient_id=ticket.patient_id,
        priority=ticket.priority,
        poli_id=ticket.poli_id,
        doctor_id=ticket.doctor_id,
        appointment_id=ticket.appointment_id,
    )

    db.add(db_ticket)
    await db.flush()  # Get ID before calculating position

    # Calculate queue position
    await _update_queue_positions(db, ticket.department, db_ticket.id)

    await db.commit()
    await db.refresh(db_ticket)

    return db_ticket


async def get_queue_tickets(
    db: AsyncSession,
    department: QueueDepartment,
    status: Optional[QueueStatus] = None,
    poli_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    date_filter: Optional[date] = None,
    page: int = 1,
    page_size: int = 50,
) -> Tuple[List[QueueTicket], int]:
    """Get queue tickets with filtering"""
    conditions = [
        QueueTicket.department == department,
        QueueTicket.date == (date_filter or date.today()),
    ]

    if status:
        conditions.append(QueueTicket.status == status)
    if poli_id:
        conditions.append(QueueTicket.poli_id == poli_id)
    if doctor_id:
        conditions.append(QueueTicket.doctor_id == doctor_id)

    # Build query
    stmt = select(QueueTicket).options(
        selectinload(QueueTicket.patient),
        selectinload(QueueTicket.poli),
        selectinload(QueueTicket.doctor),
    ).where(and_(*conditions))

    # Get total count
    count_stmt = select(sql_func.count(QueueTicket.id)).where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Apply pagination and ordering
    stmt = stmt.order_by(
        sql_func.case(
            (QueueTicket.priority == QueuePriority.EMERGENCY, 1),
            (QueueTicket.priority == QueuePriority.PRIORITY, 2),
            (QueueTicket.priority == QueuePriority.NORMAL, 3),
        ),
        QueueTicket.issued_at.asc(),
    )
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    tickets = result.scalars().all()

    return list(tickets), total


async def get_queue_ticket(
    db: AsyncSession,
    ticket_id: int,
) -> Optional[QueueTicket]:
    """Get queue ticket by ID"""
    stmt = select(QueueTicket).options(
        selectinload(QueueTicket.patient),
        selectinload(QueueTicket.poli),
        selectinload(QueueTicket.doctor),
    ).where(QueueTicket.id == ticket_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_queue_ticket_by_number(
    db: AsyncSession,
    ticket_number: str,
) -> Optional[QueueTicket]:
    """Get queue ticket by ticket number"""
    stmt = select(QueueTicket).options(
        selectinload(QueueTicket.patient),
        selectinload(QueueTicket.poli),
        selectinload(QueueTicket.doctor),
    ).where(QueueTicket.ticket_number == ticket_number)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# =============================================================================
# Queue Recall
# =============================================================================

async def recall_queue_ticket(
    db: AsyncSession,
    ticket_id: int,
    counter: int,
    called_by_id: int,
    announce: bool = True,
) -> QueueRecallResponse:
    """Call/recall a queue ticket"""
    # Get ticket
    ticket = await get_queue_ticket(db, ticket_id)
    if not ticket:
        raise ValueError("Queue ticket not found")

    # Update ticket status
    ticket.status = QueueStatus.CALLED
    ticket.called_at = datetime.utcnow()
    ticket.serving_counter = counter
    ticket.service_started_at = datetime.utcnow()

    # Create recall record
    recall = QueueRecall(
        ticket_id=ticket_id,
        counter=counter,
        announced=announce,
        called_by_id=called_by_id,
    )
    db.add(recall)

    await db.commit()
    await db.refresh(ticket)

    # Generate announcement message
    message = f"Nomor antrian {ticket.ticket_number}, silakan ke loket {counter}"

    return QueueRecallResponse(
        ticket_id=ticket_id,
        ticket_number=ticket.ticket_number,
        patient_name=ticket.patient.name if ticket.patient else "",
        counter=counter,
        recalled_at=recall.recall_time,
        announced=announce,
        message=message,
    )


async def mark_ticket_served(
    db: AsyncSession,
    ticket_id: int,
) -> QueueTicket:
    """Mark queue ticket as served"""
    ticket = await get_queue_ticket(db, ticket_id)
    if not ticket:
        raise ValueError("Queue ticket not found")

    ticket.status = QueueStatus.SERVED
    ticket.served_at = datetime.utcnow()
    ticket.service_completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(ticket)

    # Update statistics cache
    await _update_statistics_cache(db, ticket.department, date.today())

    return ticket


async def mark_ticket_skipped(
    db: AsyncSession,
    ticket_id: int,
) -> QueueTicket:
    """Mark queue ticket as skipped (patient not present)"""
    ticket = await get_queue_ticket(db, ticket_id)
    if not ticket:
        raise ValueError("Queue ticket not found")

    ticket.status = QueueStatus.SKIPPED

    # Update recall record
    latest_recall = select(QueueRecall).where(
        QueueRecall.ticket_id == ticket_id
    ).order_by(QueueRecall.recall_time.desc()).first()

    if latest_recall:
        latest_recall.patient_present = False
        latest_recall.no_show_time = datetime.utcnow()

    await db.commit()
    await db.refresh(ticket)

    return ticket


# =============================================================================
# Queue Statistics
# =============================================================================

async def get_queue_statistics(
    db: AsyncSession,
    department: QueueDepartment,
    date_filter: Optional[date] = None,
) -> QueueStatistics:
    """Get queue statistics for a department"""
    target_date = date_filter or date.today()

    # Try cache first
    cache_stmt = select(QueueStatisticsCache).where(
        and_(
            QueueStatisticsCache.department == department,
            QueueStatisticsCache.date == target_date,
            QueueStatisticsCache.expires_at > datetime.utcnow()
        )
    )
    cache_result = await db.execute(cache_stmt)
    cache = cache_result.scalar_one_or_none()

    if cache:
        return QueueStatistics(
            department=department,
            date=target_date,
            total_issued=cache.total_issued,
            total_served=cache.total_served,
            total_waiting=cache.total_waiting,
            total_skipped=cache.total_skipped,
            total_cancelled=cache.total_cancelled,
            average_wait_time_minutes=cache.average_wait_time_minutes or 0,
            average_service_time_minutes=cache.average_service_time_minutes or 0,
            longest_wait_time_minutes=0,
            normal_served=cache.normal_served,
            priority_served=cache.priority_served,
            emergency_served=cache.emergency_served,
            hourly_distribution=json.loads(cache.hourly_distribution) if cache.hourly_distribution else {},
        )

    # Calculate from scratch if no cache
    return await _calculate_queue_statistics(db, department, target_date)


async def get_all_department_statistics(
    db: AsyncSession,
    date_filter: Optional[date] = None,
) -> DepartmentQueueStatistics:
    """Get statistics for all departments"""
    departments = list(QueueDepartment)
    target_date = date_filter or date.today()

    stats_dict = {}
    total_waiting = 0
    total_served = 0

    for dept in departments:
        stats = await get_queue_statistics(db, dept, target_date)
        stats_dict[dept] = stats
        total_waiting += stats.total_waiting
        total_served += stats.total_served

    return DepartmentQueueStatistics(
        statistics=stats_dict,
        total_patients_waiting=total_waiting,
        total_patients_served_today=total_served,
    )


# =============================================================================
# Digital Display Data
# =============================================================================

async def get_digital_display_data(
    db: AsyncSession,
) -> DigitalDisplayResponse:
    """Get data for digital queue displays"""
    departments = list(QueueDepartment)
    displays = {}

    for dept in departments:
        # Get currently serving ticket
        current_stmt = select(QueueTicket).options(
            selectinload(QueueTicket.patient),
            selectinload(QueueTicket.doctor),
        ).where(
            and_(
                QueueTicket.department == dept,
                QueueTicket.date == date.today(),
                QueueTicket.status == QueueStatus.CALLED,
            )
        ).order_by(QueueTicket.called_at.desc())

        current_result = await db.execute(current_stmt)
        current_ticket = current_result.scalar_one_or_none()

        # Get recently served tickets (last 5)
        recent_stmt = select(QueueTicket).where(
            and_(
                QueueTicket.department == dept,
                QueueTicket.date == date.today(),
                QueueTicket.status == QueueStatus.SERVED,
            )
        ).order_by(QueueTicket.served_at.desc()).limit(5)

        recent_result = await db.execute(recent_stmt)
        recent_tickets = recent_result.scalars().all()

        # Get waiting count
        waiting_stmt = select(sql_func.count(QueueTicket.id)).where(
            and_(
                QueueTicket.department == dept,
                QueueTicket.date == date.today(),
                QueueTicket.status == QueueStatus.WAITING,
            )
        )
        waiting_result = await db.execute(waiting_stmt)
        waiting_count = waiting_result.scalar_one() or 0

        # Build display data
        current_data = None
        if current_ticket:
            current_data = {
                "ticket_number": current_ticket.ticket_number,
                "counter": current_ticket.serving_counter,
                "patient_name": current_ticket.patient.name if current_ticket.patient else "",
                "doctor_name": current_ticket.doctor.full_name if current_ticket.doctor else None,
            }

        recent_data = []
        for ticket in recent_tickets:
            recent_data.append({
                "ticket_number": ticket.ticket_number,
                "counter": ticket.serving_counter,
            })

        displays[dept] = DigitalDisplayData(
            department=dept,
            department_name=_get_department_name(dept),
            current_ticket=current_data,
            recent_tickets=recent_data,
            waiting_count=waiting_count,
            estimated_wait_time=waiting_count * 15,  # 15 min per person
            last_updated=datetime.utcnow(),
        )

    return DigitalDisplayResponse(
        displays=displays,
        hospital_info={"name": "SIMRS Hospital"},  # Would load from settings
        last_updated=datetime.utcnow(),
        refresh_interval_seconds=10,
    )


# =============================================================================
# Mobile Queue Status
# =============================================================================

async def get_mobile_queue_status(
    db: AsyncSession,
    ticket_id: int,
) -> MobileQueueStatus:
    """Get queue status for mobile view"""
    ticket = await get_queue_ticket(db, ticket_id)
    if not ticket:
        raise ValueError("Queue ticket not found")

    # Get currently serving ticket in this department
    current_stmt = select(QueueTicket).where(
        and_(
            QueueTicket.department == ticket.department,
            QueueTicket.date == date.today(),
            QueueTicket.status == QueueStatus.CALLED,
        )
    ).order_by(QueueTicket.called_at.desc())

    current_result = await db.execute(current_stmt)
    current_ticket = current_result.scalar_one_or_none()

    # Get latest notification
    notif_stmt = select(QueueNotification).where(
        QueueNotification.ticket_id == ticket_id
    ).order_by(QueueNotification.created_at.desc()).first()

    has_sms = False
    has_whatsapp = False
    last_notif_at = None

    if notif_stmt:
        has_sms = 'sms' in notif_stmt.notification_type
        has_whatsapp = 'whatsapp' in notif_stmt.notification_type
        last_notif_at = notif_stmt.created_at

    return MobileQueueStatus(
        ticket_id=ticket.id,
        ticket_number=ticket.ticket_number,
        department=ticket.department,
        department_name=_get_department_name(ticket.department),
        status=ticket.status,
        queue_position=ticket.queue_position,
        people_ahead=ticket.people_ahead or 0,
        estimated_wait_minutes=ticket.estimated_wait_minutes,
        current_ticket_number=current_ticket.ticket_number if current_ticket else None,
        current_counter=current_ticket.serving_counter if current_ticket else None,
        patient_name=ticket.patient.name if ticket.patient else "",
        poli_name=ticket.poli.name if ticket.poli else None,
        doctor_name=ticket.doctor.full_name if ticket.doctor else None,
        issued_at=ticket.issued_at,
        called_at=ticket.called_at,
        sms_sent=has_sms,
        whatsapp_sent=has_whatsapp,
        last_notification_at=last_notif_at,
    )


# =============================================================================
# Queue Notifications
# =============================================================================

async def send_queue_notification(
    db: AsyncSession,
    notification: QueueNotificationRequest,
) -> QueueNotificationResponse:
    """Send SMS/WhatsApp notification for queue"""
    ticket = await get_queue_ticket(db, notification.ticket_id)
    if not ticket:
        raise ValueError("Queue ticket not found")

    # Get patient phone number
    patient_stmt = select(Patient).where(Patient.id == ticket.patient_id)
    patient_result = await db.execute(patient_stmt)
    patient = patient_result.scalar_one_or_none()

    if not patient or not patient.phone:
        return QueueNotificationResponse(
            ticket_id=notification.ticket_id,
            notification_type=notification.notification_type,
            sent=False,
            sent_at=datetime.utcnow(),
            message="",
            error="No phone number available",
        )

    # Build message
    message = notification.message or f"Nomor antrian Anda: {ticket.ticket_number}. Dept: {_get_department_name(ticket.department)}. Mohon menunggu panggilan."

    # Create notification record
    notif = QueueNotification(
        ticket_id=notification.ticket_id,
        notification_type=notification.notification_type,
        message=message,
        phone_number=patient.phone,
        sent=True,  # Would integrate with SMS/WhatsApp API
        sent_at=datetime.utcnow(),
        delivery_status="sent",
    )

    db.add(notif)
    await db.commit()

    return QueueNotificationResponse(
        ticket_id=notification.ticket_id,
        notification_type=notification.notification_type,
        sent=True,
        sent_at=notif.sent_at,
        message=message,
        error=None,
    )


# =============================================================================
# Queue Transfer and Cancellation
# =============================================================================

async def transfer_queue_ticket(
    db: AsyncSession,
    transfer: QueueTransferRequest,
    transferred_by_id: int,
) -> QueueTicket:
    """Transfer queue ticket to different department/poli/doctor"""
    ticket = await get_queue_ticket(db, transfer.ticket_id)
    if not ticket:
        raise ValueError("Queue ticket not found")

    # Create transfer record
    transfer_record = QueueTransfer(
        ticket_id=transfer.ticket_id,
        from_department=ticket.department,
        to_department=transfer.new_department or ticket.department,
        from_poli_id=ticket.poli_id,
        to_poli_id=transfer.new_poli_id,
        from_doctor_id=ticket.doctor_id,
        to_doctor_id=transfer.new_doctor_id,
        reason=transfer.reason,
        transferred_by_id=transferred_by_id,
    )
    db.add(transfer_record)

    # Update ticket
    if transfer.new_department:
        ticket.department = transfer.new_department
        ticket.ticket_number = await _generate_ticket_number(
            db, transfer.new_department, date.today(), ticket.priority
        )
    if transfer.new_poli_id:
        ticket.poli_id = transfer.new_poli_id
    if transfer.new_doctor_id:
        ticket.doctor_id = transfer.new_doctor_id

    await db.commit()
    await db.refresh(ticket)

    return ticket


async def cancel_queue_ticket(
    db: AsyncSession,
    cancellation: QueueCancelRequest,
) -> QueueTicket:
    """Cancel a queue ticket"""
    ticket = await get_queue_ticket(db, cancellation.ticket_id)
    if not ticket:
        raise ValueError("Queue ticket not found")

    ticket.status = QueueStatus.CANCELLED
    ticket.cancelled_at = datetime.utcnow()
    ticket.cancellation_reason = cancellation.reason

    await db.commit()
    await db.refresh(ticket)

    # Update statistics
    await _update_statistics_cache(db, ticket.department, date.today())

    return ticket


# =============================================================================
# Helper Functions
# =============================================================================

async def _generate_ticket_number(
    db: AsyncSession,
    department: QueueDepartment,
    target_date: date,
    priority: QueuePriority,
) -> str:
    """Generate queue ticket number"""
    # Get prefix for department
    prefix = _get_department_prefix(department)

    # Priority prefix
    priority_prefix = ""
    if priority == QueuePriority.PRIORITY:
        priority_prefix = "P-"
    elif priority == QueuePriority.EMERGENCY:
        priority_prefix = "E-"

    # Count tickets today for this department
    stmt = select(sql_func.count(QueueTicket.id)).where(
        and_(
            QueueTicket.department == department,
            QueueTicket.date == target_date,
        )
    )
    result = await db.execute(stmt)
    count = result.scalar_one() or 0

    # Generate number
    number = count + 1

    # Format: PREFIX-NNN or P-PREFIX-NNN for priority
    if priority_prefix:
        return f"{priority_prefix}{prefix}-{number:03d}"
    return f"{prefix}-{number:03d}"


async def _update_queue_positions(
    db: AsyncSession,
    department: QueueDepartment,
    new_ticket_id: int,
) -> None:
    """Update queue positions for all waiting tickets"""
    # Get all waiting tickets ordered by priority and issue time
    stmt = select(QueueTicket).where(
        and_(
            QueueTicket.department == department,
            QueueTicket.date == date.today(),
            QueueTicket.status == QueueStatus.WAITING,
        )
    ).order_by(
        sql_func.case(
            (QueueTicket.priority == QueuePriority.EMERGENCY, 1),
            (QueueTicket.priority == QueuePriority.PRIORITY, 2),
            (QueueTicket.priority == QueuePriority.NORMAL, 3),
        ),
        QueueTicket.issued_at.asc(),
    )

    result = await db.execute(stmt)
    tickets = result.scalars().all()

    # Update positions
    for position, ticket in enumerate(tickets, start=1):
        ticket.queue_position = position
        ticket.people_ahead = max(0, position - 1)
        ticket.estimated_wait_minutes = (position - 1) * 15  # 15 min per person

    await db.commit()


async def _calculate_queue_statistics(
    db: AsyncSession,
    department: QueueDepartment,
    target_date: date,
) -> QueueStatistics:
    """Calculate queue statistics from scratch"""
    # Count by status
    status_counts = {}
    for status in QueueStatus:
        stmt = select(sql_func.count(QueueTicket.id)).where(
            and_(
                QueueTicket.department == department,
                QueueTicket.date == target_date,
                QueueTicket.status == status,
            )
        )
        result = await db.execute(stmt)
        status_counts[status] = result.scalar_one() or 0

    # Count by priority for served
    priority_counts = {}
    for priority in QueuePriority:
        stmt = select(sql_func.count(QueueTicket.id)).where(
            and_(
                QueueTicket.department == department,
                QueueTicket.date == target_date,
                QueueTicket.priority == priority,
                QueueTicket.status == QueueStatus.SERVED,
            )
        )
        result = await db.execute(stmt)
        priority_counts[priority] = result.scalar_one() or 0

    # Calculate average wait time
    wait_stmt = select(
        sql_func.avg(
            sql_func.extract('epoch', QueueTicket.called_at - QueueTicket.issued_at) / 60
        )
    ).where(
        and_(
            QueueTicket.department == department,
            QueueTicket.date == target_date,
            QueueTicket.called_at.isnot(None),
        )
    )
    wait_result = await db.execute(wait_stmt)
    avg_wait = wait_result.scalar_one() or 0

    # Calculate average service time
    service_stmt = select(
        sql_func.avg(
            sql_func.extract('epoch', QueueTicket.service_completed_at - QueueTicket.service_started_at) / 60
        )
    ).where(
        and_(
            QueueTicket.department == department,
            QueueTicket.date == target_date,
            QueueTicket.service_completed_at.isnot(None),
            QueueTicket.service_started_at.isnot(None),
        )
    )
    service_result = await db.execute(service_stmt)
    avg_service = service_result.scalar_one() or 0

    return QueueStatistics(
        department=department,
        date=target_date,
        total_issued=status_counts.get(QueueStatus.WAITING, 0) +
                      status_counts.get(QueueStatus.CALLED, 0) +
                      status_counts.get(QueueStatus.SERVED, 0) +
                      status_counts.get(QueueStatus.SKIPPED, 0) +
                      status_counts.get(QueueStatus.CANCELLED, 0),
        total_served=status_counts.get(QueueStatus.SERVED, 0),
        total_waiting=status_counts.get(QueueStatus.WAITING, 0),
        total_skipped=status_counts.get(QueueStatus.SKIPPED, 0),
        total_cancelled=status_counts.get(QueueStatus.CANCELLED, 0),
        average_wait_time_minutes=round(avg_wait, 2),
        average_service_time_minutes=round(avg_service, 2),
        longest_wait_time_minutes=0,
        normal_served=priority_counts.get(QueuePriority.NORMAL, 0),
        priority_served=priority_counts.get(QueuePriority.PRIORITY, 0),
        emergency_served=priority_counts.get(QueuePriority.EMERGENCY, 0),
        hourly_distribution={},  # Would calculate hourly distribution
    )


async def _update_statistics_cache(
    db: AsyncSession,
    department: QueueDepartment,
    target_date: date,
) -> None:
    """Update statistics cache"""
    stats = await _calculate_queue_statistics(db, department, target_date)

    # Try to get existing cache
    cache_stmt = select(QueueStatisticsCache).where(
        and_(
            QueueStatisticsCache.department == department,
            QueueStatisticsCache.date == target_date,
        )
    )
    cache_result = await db.execute(cache_stmt)
    cache = cache_result.scalar_one_or_none()

    if cache:
        # Update existing
        cache.total_issued = stats.total_issued
        cache.total_served = stats.total_served
        cache.total_waiting = stats.total_waiting
        cache.total_skipped = stats.total_skipped
        cache.total_cancelled = stats.total_cancelled
        cache.average_wait_time_minutes = stats.average_wait_time_minutes
        cache.average_service_time_minutes = stats.average_service_time_minutes
        cache.normal_served = stats.normal_served
        cache.priority_served = stats.priority_served
        cache.emergency_served = stats.emergency_served
        cache.hourly_distribution = json.dumps(stats.hourly_distribution)
        cache.calculated_at = datetime.utcnow()
        cache.expires_at = datetime.utcnow() + timedelta(minutes=5)  # Cache for 5 minutes
    else:
        # Create new cache entry
        cache = QueueStatisticsCache(
            department=department,
            date=target_date,
            total_issued=stats.total_issued,
            total_served=stats.total_served,
            total_waiting=stats.total_waiting,
            total_skipped=stats.total_skipped,
            total_cancelled=stats.total_cancelled,
            average_wait_time_minutes=stats.average_wait_time_minutes,
            average_service_time_minutes=stats.average_service_time_minutes,
            normal_served=stats.normal_served,
            priority_served=stats.priority_served,
            emergency_served=stats.emergency_served,
            hourly_distribution=json.dumps(stats.hourly_distribution),
            calculated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=5),
        )
        db.add(cache)

    await db.commit()


def _get_department_prefix(department: QueueDepartment) -> str:
    """Get prefix for ticket number"""
    prefixes = {
        QueueDepartment.POLI: "A",
        QueueDepartment.FARMASI: "F",
        QueueDepartment.LAB: "L",
        QueueDepartment.RADIOLOGI: "R",
        QueueDepartment.KASIR: "K",
    }
    return prefixes.get(department, "X")


def _get_department_name(department: QueueDepartment) -> str:
    """Get Indonesian department name"""
    names = {
        QueueDepartment.POLI: "Poli Rawat Jalan",
        QueueDepartment.FARMASI: "Farmasi",
        QueueDepartment.LAB: "Laboratorium",
        QueueDepartment.RADIOLOGI: "Radiologi",
        QueueDepartment.KASIR: "Kasir",
    }
    return names.get(department, department.value)
