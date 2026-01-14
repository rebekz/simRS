"""Queue Management API endpoints for STORY-010

This module provides API endpoints for:
- Queue ticket generation and management
- Queue recall functionality
- Queue statistics
- Digital display data
- Mobile queue status
- SMS notifications
- Queue transfer and cancellation
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_active_user, get_db
from app.models.user import User
from app.schemas.queue import (
    QueueTicketCreate, QueueTicketResponse, QueueListResponse,
    QueueRecallRequest, QueueRecallResponse,
    QueueStatistics, DepartmentQueueStatistics,
    DigitalDisplayResponse,
    MobileQueueStatus,
    QueueNotificationRequest, QueueNotificationResponse,
    QueueTransferRequest,
    QueueCancelRequest,
    QueueDepartment, QueueStatus,
)
from app.crud import queue as crud


router = APIRouter()


# =============================================================================
# Queue Ticket Management Endpoints
# =============================================================================

@router.post("/queue/tickets", response_model=QueueTicketResponse)
async def create_queue_ticket(
    ticket: QueueTicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new queue ticket"""
    db_ticket = await crud.create_queue_ticket(db=db, ticket=ticket)

    return _build_ticket_response(db_ticket)


@router.get("/queue/tickets/{ticket_id}", response_model=QueueTicketResponse)
async def get_queue_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get queue ticket by ID"""
    ticket = await crud.get_queue_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Queue ticket not found")

    return _build_ticket_response(ticket)


@router.get("/queue/tickets/number/{ticket_number}", response_model=QueueTicketResponse)
async def get_queue_ticket_by_number(
    ticket_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get queue ticket by ticket number"""
    ticket = await crud.get_queue_ticket_by_number(db=db, ticket_number=ticket_number)
    if not ticket:
        raise HTTPException(status_code=404, detail="Queue ticket not found")

    return _build_ticket_response(ticket)


@router.get("/queue/{department}/tickets", response_model=QueueListResponse)
async def get_queue_tickets(
    department: QueueDepartment,
    status: Optional[QueueStatus] = Query(None),
    poli_id: Optional[int] = Query(None),
    doctor_id: Optional[int] = Query(None),
    date_filter: Optional[str] = Query(None),  # YYYY-MM-DD format
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get queue tickets for a department"""
    from datetime import datetime

    # Parse date
    target_date = None
    if date_filter:
        target_date = datetime.strptime(date_filter, "%Y-%m-%d").date()

    tickets, total = await crud.get_queue_tickets(
        db=db,
        department=department,
        status=status,
        poli_id=poli_id,
        doctor_id=doctor_id,
        date_filter=target_date,
        page=page,
        page_size=page_size,
    )

    response_tickets = [_build_ticket_response(t) for t in tickets]

    return QueueListResponse(
        department=department,
        current_ticket=None,  # Would load currently serving
        waiting=response_tickets,
        served_today=0,  # Would calculate
        total_waiting=total,
        average_wait_time_minutes=None,
    )


# =============================================================================
# Queue Recall Endpoints
# =============================================================================

@router.post("/queue/tickets/{ticket_id}/recall", response_model=QueueRecallResponse)
async def recall_queue_ticket(
    ticket_id: int,
    counter: int = Query(default=1, ge=1, le=10),
    announce: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Call/recall a queue ticket"""
    recall_response = await crud.recall_queue_ticket(
        db=db,
        ticket_id=ticket_id,
        counter=counter,
        called_by_id=current_user.id,
        announce=announce,
    )

    return recall_response


@router.post("/queue/tickets/{ticket_id}/serve", response_model=QueueTicketResponse)
async def mark_ticket_served(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark queue ticket as served"""
    ticket = await crud.mark_ticket_served(db=db, ticket_id=ticket_id)
    return _build_ticket_response(ticket)


@router.post("/queue/tickets/{ticket_id}/skip", response_model=QueueTicketResponse)
async def mark_ticket_skipped(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark queue ticket as skipped (patient not present)"""
    ticket = await crud.mark_ticket_skipped(db=db, ticket_id=ticket_id)
    return _build_ticket_response(ticket)


# =============================================================================
# Queue Statistics Endpoints
# =============================================================================

@router.get("/queue/{department}/statistics", response_model=QueueStatistics)
async def get_queue_statistics(
    department: QueueDepartment,
    date_filter: Optional[str] = Query(None),  # YYYY-MM-DD format
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get queue statistics for a department"""
    from datetime import datetime

    target_date = None
    if date_filter:
        target_date = datetime.strptime(date_filter, "%Y-%m-%d").date()

    stats = await crud.get_queue_statistics(
        db=db,
        department=department,
        date_filter=target_date,
    )

    return stats


@router.get("/queue/statistics", response_model=DepartmentQueueStatistics)
async def get_all_department_statistics(
    date_filter: Optional[str] = Query(None),  # YYYY-MM-DD format
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get statistics for all departments"""
    from datetime import datetime

    target_date = None
    if date_filter:
        target_date = datetime.strptime(date_filter, "%Y-%m-%d").date()

    stats = await crud.get_all_department_statistics(
        db=db,
        date_filter=target_date,
    )

    return stats


# =============================================================================
# Digital Display Endpoints
# =============================================================================

@router.get("/queue/displays", response_model=DigitalDisplayResponse)
async def get_digital_display_data(
    db: AsyncSession = Depends(get_db),
):
    """Get data for digital queue displays (public endpoint)"""
    display_data = await crud.get_digital_display_data(db=db)
    return display_data


# =============================================================================
# Mobile Queue Status Endpoints
# =============================================================================

@router.get("/queue/tickets/{ticket_id}/mobile", response_model=MobileQueueStatus)
async def get_mobile_queue_status(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get queue status for mobile view (public endpoint)"""
    status = await crud.get_mobile_queue_status(db=db, ticket_id=ticket_id)
    return status


# =============================================================================
# Queue Notification Endpoints
# =============================================================================

@router.post("/queue/tickets/{ticket_id}/notify", response_model=QueueNotificationResponse)
async def send_queue_notification(
    ticket_id: int,
    notification: QueueNotificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Send SMS/WhatsApp notification for queue"""
    # Override ticket_id from URL
    notification.ticket_id = ticket_id

    notif_response = await crud.send_queue_notification(
        db=db,
        notification=notification,
    )

    return notif_response


# =============================================================================
# Queue Transfer and Cancellation Endpoints
# =============================================================================

@router.post("/queue/tickets/{ticket_id}/transfer", response_model=QueueTicketResponse)
async def transfer_queue_ticket(
    ticket_id: int,
    transfer: QueueTransferRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Transfer queue ticket to different department/poli/doctor"""
    # Override ticket_id from URL
    transfer.ticket_id = ticket_id

    ticket = await crud.transfer_queue_ticket(
        db=db,
        transfer=transfer,
        transferred_by_id=current_user.id,
    )

    return _build_ticket_response(ticket)


@router.post("/queue/tickets/{ticket_id}/cancel", response_model=QueueTicketResponse)
async def cancel_queue_ticket(
    ticket_id: int,
    reason: str = Query(..., description="Reason for cancellation"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Cancel a queue ticket"""
    cancellation = QueueCancelRequest(
        ticket_id=ticket_id,
        reason=reason,
        cancelled_by=current_user.id,
    )

    ticket = await crud.cancel_queue_ticket(
        db=db,
        cancellation=cancellation,
    )

    return _build_ticket_response(ticket)


# =============================================================================
# Helper Functions
# =============================================================================

def _build_ticket_response(ticket) -> QueueTicketResponse:
    """Build queue ticket response"""
    from app.schemas.queue import QueueDepartment, QueuePriority, QueueStatus

    return QueueTicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        patient_id=ticket.patient_id,
        patient_name=ticket.patient.name if ticket.patient else "Unknown",
        patient_bpjs_number=ticket.patient.bpjs_number if ticket.patient else None,
        department=QueueDepartment(ticket.department),
        department_name=crud._get_department_name(ticket.department),
        priority=QueuePriority(ticket.priority),
        status=QueueStatus(ticket.status),
        poli_id=ticket.poli_id,
        poli_name=ticket.poli.name if ticket.poli else None,
        doctor_id=ticket.doctor_id,
        doctor_name=ticket.doctor.full_name if ticket.doctor else None,
        queue_position=ticket.queue_position,
        people_ahead=ticket.people_ahead or 0,
        estimated_wait_minutes=ticket.estimated_wait_minutes,
        issued_at=ticket.issued_at,
        called_at=ticket.called_at,
        served_at=ticket.served_at,
        serving_counter=ticket.serving_counter,
        service_started_at=ticket.service_started_at,
        service_completed_at=ticket.service_completed_at,
    )
