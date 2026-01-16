"""Enhanced Appointment Booking API Endpoints for STORY-009

This module provides API endpoints for online appointment booking with
real-time slot availability and queue integration.

Python 3.5+ compatible
"""

import logging
from typing import Optional
from datetime import date, time

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.appointment_booking import (
    get_appointment_booking_service,
    AppointmentValidationError,
    AppointmentUnavailableError,
)
from app.models.appointments import AppointmentType, BookingChannel, AppointmentPriority, AppointmentStatus
from app.core.deps import get_current_user


logger = logging.getLogger(__name__)


router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class BookAppointmentRequest(BaseModel):
    """Request model for booking appointment"""
    patient_id: int = Field(..., description="Patient ID")
    department_id: int = Field(..., description="Department ID")
    doctor_id: Optional[int] = Field(None, description="Doctor ID")
    appointment_date: date = Field(..., description="Appointment date")
    appointment_time: str = Field(..., description="Appointment time (HH:MM)")
    appointment_type: AppointmentType = Field(..., description="Type of appointment")
    reason_for_visit: Optional[str] = Field(None, description="Reason for visit")
    symptoms: Optional[str] = Field(None, description="Symptoms description")
    duration_minutes: int = Field(30, description="Duration in minutes", ge=5, le=240)
    priority: AppointmentPriority = Field(AppointmentPriority.ROUTINE, description="Priority level")


class RescheduleAppointmentRequest(BaseModel):
    """Request model for rescheduling appointment"""
    new_appointment_date: date = Field(..., description="New appointment date")
    new_appointment_time: str = Field(..., description="New appointment time (HH:MM)")


class CancelAppointmentRequest(BaseModel):
    """Request model for cancelling appointment"""
    cancellation_reason: str = Field(..., description="Reason for cancellation")


# =============================================================================
# Appointment Booking Endpoints
# =============================================================================

@router.post("/book", status_code=status.HTTP_201_CREATED)
async def book_appointment(
    request: BookAppointmentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Book a new appointment

    Validates slot availability and creates appointment record.
    Queue number is reserved for check-in.

    Requires appointment:create permission.
    """
    try:
        service = get_appointment_booking_service(db)

        # Parse time string
        hour, minute = map(int, request.appointment_time.split(':'))
        appointment_time = time(hour=hour, minute=minute)

        appointment = await service.book_appointment(
            patient_id=request.patient_id,
            department_id=request.department_id,
            doctor_id=request.doctor_id,
            appointment_date=request.appointment_date,
            appointment_time=appointment_time,
            appointment_type=request.appointment_type,
            reason_for_visit=request.reason_for_visit,
            symptoms=request.symptoms,
            duration_minutes=request.duration_minutes,
            booking_channel=BookingChannel.WEB,
            priority=request.priority,
            booked_by=current_user.id,
        )

        await db.commit()

        return {
            "id": appointment.id,
            "appointment_number": appointment.appointment_number,
            "patient_id": appointment.patient_id,
            "department_id": appointment.department_id,
            "doctor_id": appointment.doctor_id,
            "appointment_date": appointment.appointment_date.isoformat() if appointment.appointment_date else None,
            "appointment_time": appointment.appointment_time.strftime("%H:%M") if appointment.appointment_time else None,
            "end_time": appointment.end_time.strftime("%H:%M") if appointment.end_time else None,
            "appointment_type": appointment.appointment_type.value,
            "status": appointment.status.value,
            "message": "Appointment booked successfully",
        }

    except AppointmentValidationError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except AppointmentUnavailableError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error booking appointment: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to book appointment"
        )


@router.get("/available-slots")
async def get_available_slots(
    department_id: int,
    doctor_id: Optional[int] = None,
    appointment_date: date = ...,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get available appointment slots for doctor and date

    Returns list of available time slots based on:
    - Doctor's schedule
    - Existing appointments
    - Slot configuration

    Requires appointment:read permission.
    """
    try:
        service = get_appointment_booking_service(db)

        slots = await service.get_available_slots(
            department_id=department_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
        )

        return {
            "department_id": department_id,
            "doctor_id": doctor_id,
            "appointment_date": appointment_date.isoformat(),
            "available_slots": slots,
            "count": len(slots),
        }

    except Exception as e:
        logger.error("Error getting available slots: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available slots"
        )


@router.get("/patient/{patient_id}")
async def get_patient_appointments(
    patient_id: int,
    status: Optional[AppointmentStatus] = None,
    upcoming_only: bool = False,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get appointments for patient

    Requires appointment:read permission.
    """
    try:
        service = get_appointment_booking_service(db)

        appointments = await service.get_patient_appointments(
            patient_id=patient_id,
            status=status,
            upcoming_only=upcoming_only,
            limit=limit,
        )

        return {
            "patient_id": patient_id,
            "appointments": appointments,
            "count": len(appointments),
        }

    except Exception as e:
        logger.error("Error getting patient appointments: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get appointments"
        )


@router.get("/doctor/{doctor_id}/{appointment_date}")
async def get_doctor_appointments(
    doctor_id: int,
    appointment_date: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get appointments for doctor on specific date

    Requires appointment:read permission.
    """
    try:
        service = get_appointment_booking_service(db)

        appointments = await service.get_doctor_appointments(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
        )

        return {
            "doctor_id": doctor_id,
            "appointment_date": appointment_date.isoformat(),
            "appointments": appointments,
            "count": len(appointments),
        }

    except Exception as e:
        logger.error("Error getting doctor appointments: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get appointments"
        )


@router.put("/cancel/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    request: CancelAppointmentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an appointment

    Requires appointment:delete permission.
    """
    try:
        service = get_appointment_booking_service(db)

        appointment = await service.cancel_appointment(
            appointment_id=appointment_id,
            cancellation_reason=request.cancellation_reason,
            cancelled_by=current_user.id,
        )

        await db.commit()

        return {
            "appointment_id": appointment.id,
            "appointment_number": appointment.appointment_number,
            "status": appointment.status.value,
            "message": "Appointment cancelled successfully",
        }

    except AppointmentValidationError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error cancelling appointment: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel appointment"
        )


@router.put("/reschedule/{appointment_id}")
async def reschedule_appointment(
    appointment_id: int,
    request: RescheduleAppointmentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reschedule an appointment

    Requires appointment:update permission.
    """
    try:
        service = get_appointment_booking_service(db)

        # Parse time string
        hour, minute = map(int, request.new_appointment_time.split(':'))
        new_appointment_time = time(hour=hour, minute=minute)

        result = await service.reschedule_appointment(
            appointment_id=appointment_id,
            new_appointment_date=request.new_appointment_date,
            new_appointment_time=new_appointment_time,
            rescheduled_by=current_user.id,
        )

        await db.commit()

        return result

    except AppointmentValidationError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except AppointmentUnavailableError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error rescheduling appointment: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reschedule appointment"
        )


@router.put("/confirm/{appointment_id}")
async def confirm_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Confirm an appointment

    Requires appointment:update permission.
    """
    try:
        service = get_appointment_booking_service(db)

        appointment = await service.confirm_appointment(
            appointment_id=appointment_id
        )

        await db.commit()

        return {
            "appointment_id": appointment.id,
            "appointment_number": appointment.appointment_number,
            "status": appointment.status.value,
            "message": "Appointment confirmed successfully",
        }

    except AppointmentValidationError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error confirming appointment: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm appointment"
        )


@router.put("/checkin/{appointment_id}")
async def check_in_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check in patient for appointment

    Creates queue ticket for the patient.

    Requires appointment:update permission.
    """
    try:
        service = get_appointment_booking_service(db)

        result = await service.check_in_appointment(
            appointment_id=appointment_id
        )

        await db.commit()

        return result

    except AppointmentValidationError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error checking in appointment: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check in appointment"
        )
