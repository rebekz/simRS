"""Enhanced Queue Management API Endpoints for STORY-010

This module provides API endpoints for queue management operations
including ticket creation, calling, serving, and digital display support.

Python 3.5+ compatible
"""

import logging
from typing import Optional, List
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.queue_management import (
    get_queue_management_service,
    QueueNotFoundError,
    QueueOperationError,
)
from app.schemas.queue import QueueDepartment, QueueStatus, QueuePriority
from app.core.deps import get_current_user, get_current_admin_user


logger = logging.getLogger(__name__)


router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class QueueTicketCreateRequest(BaseModel):
    """Request model for creating queue ticket"""
    patient_id: int = Field(..., description="Patient ID")
    department: QueueDepartment = Field(..., description="Department")
    priority: QueuePriority = Field(QueuePriority.NORMAL, description="Queue priority")
    poli_id: Optional[int] = Field(None, description="Polyclinic ID (for POLI)")
    doctor_id: Optional[int] = Field(None, description="Doctor ID")
    appointment_id: Optional[int] = Field(None, description="Appointment ID")


class CallNextPatientRequest(BaseModel):
    """Request model for calling next patient"""
    department: QueueDepartment = Field(..., description="Department")
    counter: int = Field(..., description="Counter number", ge=1)
    poli_id: Optional[int] = Field(None, description="Polyclinic ID (for POLI)")
    doctor_id: Optional[int] = Field(None, description="Doctor ID")


class ServePatientRequest(BaseModel):
    """Request model for marking patient as served"""
    service_outcome: str = Field("completed", description="Service outcome")
    served_by: Optional[int] = Field(None, description="User ID")


class NoShowRequest(BaseModel):
    """Request model for marking patient as no-show"""
    reason: str = Field("Patient not present", description="Reason for no-show")


class CancelQueueRequest(BaseModel):
    """Request model for cancelling queue ticket"""
    reason: str = Field(..., description="Cancellation reason")


class TransferQueueRequest(BaseModel):
    """Request model for transferring queue ticket"""
    to_department: QueueDepartment = Field(..., description="Target department")
    to_poli_id: Optional[int] = Field(None, description="Target polyclinic ID")
    to_doctor_id: Optional[int] = Field(None, description="Target doctor ID")
    reason: Optional[str] = Field("Patient transfer", description="Transfer reason")


# =============================================================================
# Queue Ticket Management Endpoints
# =============================================================================

@router.post("/tickets", status_code=status.HTTP_201_CREATED)
async def create_queue_ticket(
    request: QueueTicketCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new queue ticket

    Requires queue:create permission.
    """
    try:
        service = get_queue_management_service(db)

        ticket = await service.create_queue_ticket(
            patient_id=request.patient_id,
            department=request.department,
            priority=request.priority,
            poli_id=request.poli_id,
            doctor_id=request.doctor_id,
            appointment_id=request.appointment_id,
            created_by=current_user.id,
        )

        await db.commit()

        return {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "department": ticket.department.value,
            "queue_position": ticket.queue_position,
            "people_ahead": ticket.people_ahead,
            "estimated_wait_minutes": ticket.estimated_wait_minutes,
            "status": ticket.status.value,
            "issued_at": ticket.issued_at.isoformat() if ticket.issued_at else None,
            "message": "Queue ticket created successfully",
        }

    except Exception as e:
        await db.rollback()
        logger.error("Error creating queue ticket: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create queue ticket"
        )


@router.post("/call-next")
async def call_next_patient(
    request: CallNextPatientRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Call next patient in queue

    Requires queue:manage permission.
    """
    try:
        service = get_queue_management_service(db)

        result = await service.call_next_patient(
            department=request.department,
            counter=request.counter,
            poli_id=request.poli_id,
            doctor_id=request.doctor_id,
            called_by=current_user.id,
        )

        await db.commit()

        if not result:
            return {
                "message": "No patients waiting in queue",
                "ticket": None,
            }

        return {
            "message": "Patient called successfully",
            "ticket": result,
        }

    except Exception as e:
        await db.rollback()
        logger.error("Error calling patient: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to call patient"
        )


@router.put("/tickets/{ticket_id}/serve")
async def mark_patient_served(
    ticket_id: int,
    request: ServePatientRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark patient as served

    Requires queue:manage permission.
    """
    try:
        service = get_queue_management_service(db)

        result = await service.mark_patient_served(
            ticket_id=ticket_id,
            service_outcome=request.service_outcome,
            served_by=current_user.id,
        )

        await db.commit()

        return result

    except QueueNotFoundError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error marking patient served: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark patient as served"
        )


@router.put("/tickets/{ticket_id}/no-show")
async def mark_patient_no_show(
    ticket_id: int,
    request: NoShowRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark patient as no-show

    Requires queue:manage permission.
    """
    try:
        service = get_queue_management_service(db)

        result = await service.mark_patient_no_show(
            ticket_id=ticket_id,
            reason=request.reason,
            marked_by=current_user.id,
        )

        await db.commit()

        return result

    except QueueNotFoundError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error marking no-show: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark patient as no-show"
        )


@router.put("/tickets/{ticket_id}/cancel")
async def cancel_queue_ticket(
    ticket_id: int,
    request: CancelQueueRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a queue ticket

    Requires queue:manage permission.
    """
    try:
        service = get_queue_management_service(db)

        result = await service.cancel_queue_ticket(
            ticket_id=ticket_id,
            reason=request.reason,
            cancelled_by=current_user.id,
        )

        await db.commit()

        return result

    except QueueNotFoundError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except QueueOperationError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error cancelling ticket: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel ticket"
        )


@router.post("/tickets/{ticket_id}/transfer")
async def transfer_queue_ticket(
    ticket_id: int,
    request: TransferQueueRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Transfer queue ticket to another department/poli/doctor

    Requires queue:manage permission.
    """
    try:
        service = get_queue_management_service(db)

        result = await service.transfer_queue_ticket(
            ticket_id=ticket_id,
            to_department=request.to_department,
            to_poli_id=request.to_poli_id,
            to_doctor_id=request.to_doctor_id,
            reason=request.reason,
            transferred_by=current_user.id,
        )

        await db.commit()

        return result

    except QueueNotFoundError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except QueueOperationError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error transferring ticket: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transfer ticket"
        )


# =============================================================================
# Queue Status and Display Endpoints
# =============================================================================

@router.get("/status/{department}")
async def get_department_queue_status(
    department: QueueDepartment,
    poli_id: Optional[int] = Query(None, description="Filter by polyclinic"),
    doctor_id: Optional[int] = Query(None, description="Filter by doctor"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current queue status for department

    Requires queue:read permission.
    """
    try:
        service = get_queue_management_service(db)

        status = await service.get_department_queue_status(
            department=department,
            poli_id=poli_id,
            doctor_id=doctor_id,
        )

        return status

    except Exception as e:
        logger.error("Error getting queue status: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get queue status"
        )


@router.get("/display/{department}")
async def get_digital_display_data(
    department: QueueDepartment,
    poli_id: Optional[int] = Query(None, description="Filter by polyclinic"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get data for digital queue display

    Includes current serving, waiting, and recently served.

    Requires queue:read permission.
    """
    try:
        service = get_queue_management_service(db)

        display_data = await service.get_digital_display_data(
            department=department,
            poli_id=poli_id,
        )

        return display_data

    except Exception as e:
        logger.error("Error getting display data: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get display data"
        )


@router.get("/tickets/{ticket_id}/status")
async def get_patient_queue_status(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get queue status for patient's ticket

    Requires queue:read permission.
    """
    try:
        service = get_queue_management_service(db)

        status = await service.get_patient_queue_status(ticket_id)

        return status

    except QueueNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        logger.error("Error getting patient queue status: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get patient queue status"
        )


# =============================================================================
# Queue Statistics Endpoints
# =============================================================================

@router.get("/statistics")
async def get_queue_statistics(
    department: Optional[QueueDepartment] = Query(None, description="Filter by department"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get queue statistics

    Requires queue:read permission.
    """
    try:
        service = get_queue_management_service(db)

        stats = await service.get_queue_statistics(
            department=department,
            start_date=start_date,
            end_date=end_date,
        )

        return stats

    except Exception as e:
        logger.error("Error getting queue statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get queue statistics"
        )
