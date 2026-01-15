"""Queue Status Notification API Endpoints

STORY-022-07: Queue Status Notifications
API endpoints for queue status notification management.

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
from app.services.queue_status_notifications import get_queue_status_notification_service


logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class QueuePositionRequest(BaseModel):
    """Request for position change notification"""
    ticket_id: int


class ApproachingTurnRequest(BaseModel):
    """Request for approaching turn notification"""
    ticket_id: int


class NextInQueueRequest(BaseModel):
    """Request for next in queue notification"""
    ticket_id: int
    counter: Optional[str] = None


class DoctorArrivedRequest(BaseModel):
    """Request for doctor arrived notification"""
    ticket_id: int


class DoctorBreakRequest(BaseModel):
    """Request for doctor on break notification"""
    ticket_id: int
    resume_time: str  # HH:MM format


class DelayRequest(BaseModel):
    """Request for delay notification"""
    ticket_id: int
    additional_minutes: int


class DepartureTimeRequest(BaseModel):
    """Request for departure time notification"""
    ticket_id: int


class ServiceStartedRequest(BaseModel):
    """Request for service started notification"""
    ticket_id: int
    counter: Optional[str] = None


class ServiceCompletedRequest(BaseModel):
    """Request for service completed notification"""
    ticket_id: int
    next_steps: Optional[List[str]] = None


class NotificationResponse(BaseModel):
    """Response for notification operations"""
    success: bool
    message: str
    notification_id: Optional[int] = None


class QueueCheckResponse(BaseModel):
    """Response for queue update check"""
    success: bool
    message: str
    notifications_sent: Dict[str, int]


@router.post("/position-change", response_model=NotificationResponse)
async def notify_position_change(
    request: QueuePositionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send notification when queue position changes

    Notifies patient of their current queue position and estimated wait time.
    """
    try:
        service = get_queue_status_notification_service(db)

        notification_id = await service.notify_position_change(request.ticket_id)

        if notification_id:
            return NotificationResponse(
                success=True,
                message="Position change notification sent successfully",
                notification_id=notification_id
            )
        else:
            return NotificationResponse(
                success=False,
                message="Failed to send notification or patient has opted out"
            )

    except Exception as e:
        logger.error("Error sending position change notification: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send position change notification"
        )


@router.post("/approaching-turn", response_model=NotificationResponse)
async def notify_approaching_turn(
    request: ApproachingTurnRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send notification when patient is approaching their turn (5 away)

    High-priority notification sent when patient is 5 positions away.
    """
    try:
        service = get_queue_status_notification_service(db)

        notification_id = await service.notify_approaching_turn(request.ticket_id)

        if notification_id:
            return NotificationResponse(
                success=True,
                message="Approaching turn notification sent successfully",
                notification_id=notification_id
            )
        else:
            return NotificationResponse(
                success=False,
                message="Failed to send notification or patient has opted out"
            )

    except Exception as e:
        logger.error("Error sending approaching turn notification: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send approaching turn notification"
        )


@router.post("/next-in-queue", response_model=NotificationResponse)
async def notify_next_in_queue(
    request: NextInQueueRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send notification when patient is next in queue

    High-priority notification sent when patient is next to be served.
    Includes counter/room number.
    """
    try:
        service = get_queue_status_notification_service(db)

        notification_id = await service.notify_next_in_queue(
            request.ticket_id,
            request.counter
        )

        if notification_id:
            return NotificationResponse(
                success=True,
                message="Next in queue notification sent successfully",
                notification_id=notification_id
            )
        else:
            return NotificationResponse(
                success=False,
                message="Failed to send notification or patient has opted out"
            )

    except Exception as e:
        logger.error("Error sending next in queue notification: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send next in queue notification"
        )


@router.post("/long-wait", response_model=NotificationResponse)
async def notify_long_wait(
    request: QueuePositionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send update for long wait times (>30 min)

    Sent every 10-15 minutes for extended waits.
    """
    try:
        service = get_queue_status_notification_service(db)

        notification_id = await service.notify_long_wait_update(request.ticket_id)

        if notification_id:
            return NotificationResponse(
                success=True,
                message="Long wait update sent successfully",
                notification_id=notification_id
            )
        else:
            return NotificationResponse(
                success=False,
                message="Failed to send notification or patient has opted out"
            )

    except Exception as e:
        logger.error("Error sending long wait update: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send long wait update"
        )


@router.post("/doctor-arrived", response_model=NotificationResponse)
async def notify_doctor_arrived(
    request: DoctorArrivedRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send notification when doctor arrives (if running late)

    Notifies patient that their doctor has arrived and queue will resume.
    """
    try:
        service = get_queue_status_notification_service(db)

        notification_id = await service.notify_doctor_arrived(request.ticket_id)

        if notification_id:
            return NotificationResponse(
                success=True,
                message="Doctor arrived notification sent successfully",
                notification_id=notification_id
            )
        else:
            return NotificationResponse(
                success=False,
                message="Failed to send notification or patient has opted out"
            )

    except Exception as e:
        logger.error("Error sending doctor arrived notification: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send doctor arrived notification"
        )


@router.post("/doctor-break", response_model=NotificationResponse)
async def notify_doctor_break(
    request: DoctorBreakRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send notification when doctor goes on break

    Notifies patient of doctor break and expected resume time.
    """
    try:
        service = get_queue_status_notification_service(db)

        notification_id = await service.notify_doctor_on_break(
            request.ticket_id,
            request.resume_time
        )

        if notification_id:
            return NotificationResponse(
                success=True,
                message="Doctor on break notification sent successfully",
                notification_id=notification_id
            )
        else:
            return NotificationResponse(
                success=False,
                message="Failed to send notification or patient has opted out"
            )

    except Exception as e:
        logger.error("Error sending doctor on break notification: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send doctor on break notification"
        )


@router.post("/delay", response_model=NotificationResponse)
async def notify_delay(
    request: DelayRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send notification when significant delay occurs (>30 min)

    Notifies patient of service delays with updated wait time.
    """
    try:
        service = get_queue_status_notification_service(db)

        notification_id = await service.notify_delay(
            request.ticket_id,
            request.additional_minutes
        )

        if notification_id:
            return NotificationResponse(
                success=True,
                message="Delay notification sent successfully",
                notification_id=notification_id
            )
        else:
            return NotificationResponse(
                success=False,
                message="Failed to send notification or patient has opted out"
            )

    except Exception as e:
        logger.error("Error sending delay notification: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send delay notification"
        )


@router.post("/departure-time", response_model=NotificationResponse)
async def notify_departure_time(
    request: DepartureTimeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send notification when it's time to leave for hospital

    Sent 30 minutes before patient needs to arrive based on queue speed.
    """
    try:
        service = get_queue_status_notification_service(db)

        notification_id = await service.notify_departure_time(request.ticket_id)

        if notification_id:
            return NotificationResponse(
                success=True,
                message="Departure time notification sent successfully",
                notification_id=notification_id
            )
        else:
            return NotificationResponse(
                success=False,
                message="Failed to send notification or patient has opted out"
            )

    except Exception as e:
        logger.error("Error sending departure time notification: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send departure time notification"
        )


@router.post("/service-started", response_model=NotificationResponse)
async def notify_service_started(
    request: ServiceStartedRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send notification when patient is being served

    Notifies patient that their service has started.
    """
    try:
        service = get_queue_status_notification_service(db)

        notification_id = await service.notify_service_started(
            request.ticket_id,
            request.counter
        )

        if notification_id:
            return NotificationResponse(
                success=True,
                message="Service started notification sent successfully",
                notification_id=notification_id
            )
        else:
            return NotificationResponse(
                success=False,
                message="Failed to send notification or patient has opted out"
            )

    except Exception as e:
        logger.error("Error sending service started notification: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send service started notification"
        )


@router.post("/service-completed", response_model=NotificationResponse)
async def notify_service_completed(
    request: ServiceCompletedRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send notification when service is completed

    Notifies patient of service completion and next steps.
    """
    try:
        service = get_queue_status_notification_service(db)

        notification_id = await service.notify_service_completed(
            request.ticket_id,
            request.next_steps
        )

        if notification_id:
            return NotificationResponse(
                success=True,
                message="Service completed notification sent successfully",
                notification_id=notification_id
            )
        else:
            return NotificationResponse(
                success=False,
                message="Failed to send notification or patient has opted out"
            )

    except Exception as e:
        logger.error("Error sending service completed notification: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send service completed notification"
        )


@router.post("/check-updates", response_model=QueueCheckResponse)
async def check_queue_updates(
    department: Optional[str] = Query(None, description="Filter by department"),
    db: AsyncSession = Depends(get_db)
):
    """Check all active tickets and send appropriate notifications

    Automated endpoint to check queue status and send notifications.
    Should be called periodically (every 5-10 minutes).
    """
    try:
        service = get_queue_status_notification_service(db)

        notifications_sent = await service.check_and_notify_queue_updates(department)

        total_sent = sum(notifications_sent.values())

        return QueueCheckResponse(
            success=True,
            message="Queue update check completed",
            notifications_sent=notifications_sent
        )

    except Exception as e:
        logger.error("Error checking queue updates: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check queue updates"
        )


@router.get("/ticket/{ticket_id}/notifications")
async def get_ticket_queue_notifications(
    ticket_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all queue notifications for a specific ticket

    Returns all queue update notifications sent for this ticket.
    """
    try:
        query = select(Notification).where(
            and_(
                Notification.notification_type == NotificationType.QUEUE_UPDATE,
                Notification.metadata["ticket_id"].astext == str(ticket_id)
            )
        ).order_by(Notification.created_at.desc())

        result = await db.execute(query)
        notifications = result.scalars().all()

        return [
            {
                "id": str(notification.id),
                "title": notification.title,
                "notification_type": notification.metadata.get("notification_type") if notification.metadata else None,
                "status": notification.status,
                "priority": notification.priority,
                "channel": notification.channel,
                "created_at": notification.created_at.isoformat(),
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
            }
            for notification in notifications
        ]

    except Exception as e:
        logger.error("Error getting ticket queue notifications: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ticket queue notifications"
        )


@router.get("/patient/{patient_id}/notifications")
async def get_patient_queue_notifications(
    patient_id: int,
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    db: AsyncSession = Depends(get_db)
):
    """Get all queue notifications for a patient

    Returns queue update notifications with optional status filter.
    """
    try:
        filters = [
            Notification.notification_type == NotificationType.QUEUE_UPDATE,
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
                "notification_type": notification.metadata.get("notification_type") if notification.metadata else None,
                "ticket_number": notification.metadata.get("ticket_number") if notification.metadata else None,
                "status": notification.status,
                "created_at": notification.created_at.isoformat(),
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
            }
            for notification in notifications
        ]

    except Exception as e:
        logger.error("Error getting patient queue notifications: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patient queue notifications"
        )


@router.get("/stats/patient/{patient_id}")
async def get_patient_queue_notification_stats(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for patient's queue notifications

    Returns counts by status and notification type.
    """
    try:
        # Get all queue notifications for patient
        query = select(Notification).where(
            and_(
                Notification.notification_type == NotificationType.QUEUE_UPDATE,
                Notification.recipient_id == patient_id
            )
        )
        result = await db.execute(query)
        notifications = result.scalars().all()

        # Count by status
        status_counts = {}
        notification_type_counts = {}
        total = len(notifications)

        for notification in notifications:
            # Count by status
            status_str = notification.status
            status_counts[status_str] = status_counts.get(status_str, 0) + 1

            # Count by notification type
            notification_type = notification.metadata.get("notification_type") if notification.metadata else None
            if notification_type:
                notification_type_counts[notification_type] = notification_type_counts.get(notification_type, 0) + 1

        return {
            "patient_id": patient_id,
            "total": total,
            "by_status": status_counts,
            "by_notification_type": notification_type_counts,
        }

    except Exception as e:
        logger.error("Error getting patient queue notification stats: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve queue notification statistics"
        )
