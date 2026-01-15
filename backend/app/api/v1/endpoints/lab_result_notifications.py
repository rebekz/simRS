"""Lab Result Notification API Endpoints

STORY-022-04: Lab Result Notifications
API endpoints for lab result notification management.

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
from app.services.lab_result_notifications import get_lab_result_notification_service


logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class LabResultData(BaseModel):
    """Lab result data for notifications"""
    patient_id: int
    patient_name: str
    mrn: Optional[str] = None
    result_id: int
    test_names: List[str]
    completion_date: Optional[str] = None
    doctor_id: Optional[int] = None
    doctor_name: Optional[str] = "Your Doctor"
    doctor_phone: Optional[str] = "Contact hospital"
    portal_link: Optional[str] = "https://portal.simrs.hospital/lab-results"
    has_critical_values: Optional[bool] = False
    has_abnormal_values: Optional[bool] = False
    critical_values: Optional[List[Dict]] = None


class AbnormalValueData(BaseModel):
    """Data for abnormal value alert"""
    patient_id: int
    patient_name: str
    result_id: int
    test_name: str
    value: str
    unit: Optional[str] = ""
    explanation: Optional[str] = "Value outside normal range"
    recommendation: Optional[str] = "Please consult your doctor"
    portal_link: Optional[str] = "https://portal.simrs.hospital/lab-results"


class DoctorNotificationData(BaseModel):
    """Data for doctor critical value notification"""
    patient_id: int
    patient_name: str
    mrn: Optional[str] = None
    result_id: int
    doctor_id: int
    completion_date: Optional[str] = None
    critical_value: Dict


class NotificationResponse(BaseModel):
    """Response for notification operations"""
    success: bool
    message: str
    notification_id: Optional[int] = None


@router.post("/notify-ready", response_model=NotificationResponse)
async def notify_results_ready(
    result: LabResultData,
    db: AsyncSession = Depends(get_db)
):
    """Notify patient that lab results are ready

    Sends notification with appropriate priority based on results:
    - URGENT: If critical values present
    - HIGH: If abnormal values present
    - NORMAL: If all values normal
    """
    try:
        service = get_lab_result_notification_service(db)

        notification_id = await service.notify_results_ready(result.dict())

        if notification_id:
            return NotificationResponse(
                success=True,
                message="Lab result notification sent successfully",
                notification_id=notification_id
            )
        else:
            return NotificationResponse(
                success=False,
                message="Failed to send notification or patient has opted out"
            )

    except Exception as e:
        logger.error("Error sending lab result notification: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send lab result notification"
        )


@router.post("/abnormal-alert", response_model=NotificationResponse)
async def send_abnormal_result_alert(
    data: AbnormalValueData,
    db: AsyncSession = Depends(get_db)
):
    """Send alert for specific abnormal lab result

    Provides detailed explanation of abnormal value and recommendations.
    """
    try:
        service = get_lab_result_notification_service(db)

        notification_id = await service.send_abnormal_result_alert(
            data.dict(),
            data.dict()
        )

        if notification_id:
            return NotificationResponse(
                success=True,
                message="Abnormal result alert sent successfully",
                notification_id=notification_id
            )
        else:
            return NotificationResponse(
                success=False,
                message="Failed to send abnormal alert or patient has opted out"
            )

    except Exception as e:
        logger.error("Error sending abnormal result alert: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send abnormal result alert"
        )


@router.post("/doctor-critical-alert", response_model=NotificationResponse)
async def notify_doctor_critical_value(
    data: DoctorNotificationData,
    db: AsyncSession = Depends(get_db)
):
    """Notify ordering doctor about critical patient value

    Doctor notification when critical value is detected.
    """
    try:
        service = get_lab_result_notification_service(db)

        notification_id = await service.notify_doctor_of_critical_value(
            data.dict(),
            data.critical_value
        )

        if notification_id:
            return NotificationResponse(
                success=True,
                message="Doctor critical value notification sent successfully",
                notification_id=notification_id
            )
        else:
            return NotificationResponse(
                success=False,
                message="Failed to send doctor notification"
            )

    except Exception as e:
        logger.error("Error sending doctor critical value notification: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send doctor notification"
        )


@router.get("/patient/{patient_id}/notifications")
async def get_patient_lab_notifications(
    patient_id: int,
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    db: AsyncSession = Depends(get_db)
):
    """Get all lab result notifications for a patient

    Returns lab result notifications with optional status filter.
    """
    try:
        filters = [
            Notification.notification_type == NotificationType.LAB_RESULT,
            Notification.recipient_id == patient_id
        ]

        if status:
            filters.append(Notification.status == status)

        query = select(Notification).where(
            and_(*filters)
        ).order_by(Notification.created_at.desc()).limit(limit)

        result = await db.execute(query)
        notifications = result.scalars().all()

        return [
            {
                "id": str(notification.id),
                "title": notification.title,
                "status": notification.status,
                "priority": notification.priority,
                "channel": notification.channel,
                "created_at": notification.created_at.isoformat(),
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                "metadata": notification.metadata,
            }
            for notification in notifications
        ]

    except Exception as e:
        logger.error("Error getting patient lab notifications: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patient lab notifications"
        )


@router.get("/result/{result_id}/notifications")
async def get_result_notifications(
    result_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all notifications for a specific lab result

    Includes both patient and doctor notifications.
    """
    try:
        query = select(Notification).where(
            and_(
                Notification.notification_type == NotificationType.LAB_RESULT,
                Notification.metadata["result_id"].astext == str(result_id)
            )
        ).order_by(Notification.created_at.desc())

        result = await db.execute(query)
        notifications = result.scalars().all()

        return [
            {
                "id": str(notification.id),
                "recipient_id": notification.recipient_id,
                "user_type": notification.user_type,
                "title": notification.title,
                "status": notification.status,
                "priority": notification.priority,
                "channel": notification.channel,
                "created_at": notification.created_at.isoformat(),
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
            }
            for notification in notifications
        ]

    except Exception as e:
        logger.error("Error getting result notifications: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve result notifications"
        )


@router.get("/stats/patient/{patient_id}")
async def get_patient_lab_notification_stats(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for patient's lab result notifications

    Returns counts by status and priority.
    """
    try:
        # Get all lab result notifications for patient
        query = select(Notification).where(
            and_(
                Notification.notification_type == NotificationType.LAB_RESULT,
                Notification.recipient_id == patient_id
            )
        )
        result = await db.execute(query)
        notifications = result.scalars().all()

        # Count by status
        status_counts = {}
        priority_counts = {}
        total = len(notifications)

        for notification in notifications:
            # Count by status
            status_str = notification.status
            status_counts[status_str] = status_counts.get(status_str, 0) + 1

            # Count by priority
            priority_str = notification.priority
            priority_counts[priority_str] = priority_counts.get(priority_str, 0) + 1

        return {
            "patient_id": patient_id,
            "total": total,
            "by_status": status_counts,
            "by_priority": priority_counts,
        }

    except Exception as e:
        logger.error("Error getting patient notification stats: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notification statistics"
        )
