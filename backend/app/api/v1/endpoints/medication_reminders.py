"""Medication Reminder API Endpoints

STORY-022-03: Medication Reminders
API endpoints for medication reminder management and adherence tracking.

Python 3.5+ compatible
"""

import logging
from datetime import datetime, date
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from pydantic import BaseModel

from app.db.session import get_db
from app.models.notifications import Notification, NotificationStatus, NotificationType
from app.services.medication_reminders import get_medication_reminder_service


logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class PrescriptionData(BaseModel):
    """Prescription data for medication reminders"""
    patient_id: int
    patient_name: str
    prescription_id: int
    medication_name: str
    dosage: str
    frequency: str  # daily, bid, tid, qid, prn
    duration_days: int = 30
    start_date: date = None
    instructions: Optional[str] = "Take as prescribed"
    supply_days_remaining: Optional[int] = None
    pharmacy_name: Optional[str] = "Hospital Pharmacy"
    pharmacy_phone: Optional[str] = "123-456-7890"
    prescription_number: Optional[str] = None


class InteractionWarningData(BaseModel):
    """Data for interaction warning"""
    patient_id: int
    patient_name: str
    doctor_id: Optional[int] = None
    doctor_name: Optional[str] = "Your Doctor"
    doctor_phone: Optional[str] = "Contact your doctor"
    new_medication: Dict
    existing_medication: Dict
    interaction: Dict


class AllergyAlertData(BaseModel):
    """Data for allergy alert"""
    patient_id: int
    patient_name: str
    doctor_id: Optional[int] = None
    doctor_name: Optional[str] = "Your Doctor"
    doctor_phone: Optional[str] = "Contact your doctor"
    medication: Dict
    allergy: Dict


class AdherenceAlertData(BaseModel):
    """Data for adherence alert"""
    patient_id: int
    patient_name: str
    doctor_id: int
    adherence_rate: float


class ReminderResponse(BaseModel):
    """Response for reminder operations"""
    success: bool
    message: str
    notification_id: Optional[int] = None
    scheduled_count: Optional[int] = None


class ScheduleRemindersResponse(BaseModel):
    """Response for scheduling reminders"""
    success: bool
    message: str
    scheduled_reminders: Dict[str, int]


@router.post("/schedule-reminders", response_model=ScheduleRemindersResponse)
async def schedule_medication_reminders(
    prescription: PrescriptionData,
    db: AsyncSession = Depends(get_db)
):
    """Schedule all medication reminders for a prescription

    Schedules daily reminders based on medication frequency and duration.
    Also schedules refill reminder when supply is low.
    """
    try:
        service = get_medication_reminder_service(db)

        # Set default start date to today
        data = prescription.dict()
        if data.get("start_date") is None:
            data["start_date"] = datetime.utcnow().date()

        # Set supply days to duration if not specified
        if data.get("supply_days_remaining") is None:
            data["supply_days_remaining"] = data.get("duration_days", 30)

        scheduled = await service.schedule_medication_reminders(data)

        return ScheduleRemindersResponse(
            success=True,
            message="Scheduled {} medication reminders".format(len(scheduled)),
            scheduled_reminders=scheduled
        )

    except Exception as e:
        logger.error("Error scheduling medication reminders: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule medication reminders"
        )


@router.post("/interaction-warning", response_model=ReminderResponse)
async def send_interaction_warning(
    data: InteractionWarningData,
    db: AsyncSession = Depends(get_db)
):
    """Send warning about potential drug interaction

    Warns patient about interaction between new and existing medications.
    """
    try:
        service = get_medication_reminder_service(db)

        notification_id = await service.send_interaction_warning(
            data.dict(),
            data.new_medication,
            data.existing_medication,
            data.interaction
        )

        if notification_id:
            return ReminderResponse(
                success=True,
                message="Interaction warning sent successfully",
                notification_id=notification_id
            )
        else:
            return ReminderResponse(
                success=False,
                message="Failed to send interaction warning or patient has opted out"
            )

    except Exception as e:
        logger.error("Error sending interaction warning: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send interaction warning"
        )


@router.post("/allergy-alert", response_model=ReminderResponse)
async def send_allergy_alert(
    data: AllergyAlertData,
    db: AsyncSession = Depends(get_db)
):
    """Send alert about medication allergy

    Critical alert - always sent regardless of preferences.
    Alerts both patient and doctor.
    """
    try:
        service = get_medication_reminder_service(db)

        notification_id = await service.send_allergy_alert(
            data.dict(),
            data.medication,
            data.allergy
        )

        if notification_id:
            return ReminderResponse(
                success=True,
                message="Allergy alert sent successfully",
                notification_id=notification_id
            )
        else:
            return ReminderResponse(
                success=False,
                message="Failed to send allergy alert"
            )

    except Exception as e:
        logger.error("Error sending allergy alert: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send allergy alert"
        )


@router.post("/adherence-alert", response_model=ReminderResponse)
async def send_adherence_alert(
    data: AdherenceAlertData,
    db: AsyncSession = Depends(get_db)
):
    """Send alert to doctor about low medication adherence

    Automatically triggered when patient adherence drops below 80%.
    """
    try:
        service = get_medication_reminder_service(db)

        notification_id = await service.send_adherence_alert(
            data.patient_id,
            data.patient_name,
            data.doctor_id,
            data.adherence_rate
        )

        if notification_id:
            return ReminderResponse(
                success=True,
                message="Adherence alert sent successfully",
                notification_id=notification_id
            )
        else:
            return ReminderResponse(
                success=False,
                message="Adherence rate is acceptable or failed to send alert"
            )

    except Exception as e:
        logger.error("Error sending adherence alert: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send adherence alert"
        )


@router.delete("/cancel-reminders/{prescription_id}")
async def cancel_medication_reminders(
    prescription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Cancel all pending reminders for a prescription

    Use when prescription is discontinued or completed.
    """
    try:
        service = get_medication_reminder_service(db)

        cancelled = await service.cancel_medication_reminders(prescription_id)

        return {
            "success": True,
            "message": "Cancelled {} medication reminders".format(cancelled),
            "cancelled_count": cancelled
        }

    except Exception as e:
        logger.error("Error cancelling reminders: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel medication reminders"
        )


@router.get("/prescription/{prescription_id}/reminders")
async def get_prescription_reminders(
    prescription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all reminders for a specific prescription

    Returns scheduled and sent reminders.
    """
    try:
        query = select(Notification).where(
            and_(
                Notification.notification_type == NotificationType.MEDICATION_REMINDER,
                Notification.metadata["prescription_id"].astext == str(prescription_id)
            )
        ).order_by(Notification.scheduled_at.asc())

        result = await db.execute(query)
        notifications = result.scalars().all()

        return [
            {
                "id": str(notification.id),
                "reminder_type": notification.metadata.get("reminder_type") if notification.metadata else None,
                "medication_name": notification.metadata.get("medication_name") if notification.metadata else None,
                "status": notification.status,
                "channel": notification.channel,
                "scheduled_at": notification.scheduled_at.isoformat() if notification.scheduled_at else None,
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                "created_at": notification.created_at.isoformat(),
            }
            for notification in notifications
        ]

    except Exception as e:
        logger.error("Error getting reminders: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medication reminders"
        )


@router.get("/patient/{patient_id}/reminders")
async def get_patient_medication_reminders(
    patient_id: int,
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db)
):
    """Get all medication reminders for a patient

    Optionally filter by status (pending, sent, delivered, etc.)
    """
    try:
        filters = [
            Notification.notification_type == NotificationType.MEDICATION_REMINDER,
            Notification.recipient_id == patient_id
        ]

        if status:
            filters.append(Notification.status == status)

        query = select(Notification).where(
            and_(*filters)
        ).order_by(Notification.scheduled_at.asc())

        result = await db.execute(query)
        notifications = result.scalars().all()

        return [
            {
                "id": str(notification.id),
                "reminder_type": notification.metadata.get("reminder_type") if notification.metadata else None,
                "medication_name": notification.metadata.get("medication_name") if notification.metadata else None,
                "title": notification.title,
                "status": notification.status,
                "scheduled_at": notification.scheduled_at.isoformat() if notification.scheduled_at else None,
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
            }
            for notification in notifications
        ]

    except Exception as e:
        logger.error("Error getting patient reminders: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patient medication reminders"
        )
