"""Critical Value Alert API Endpoints

STORY-022-05: Critical Value Alerts to Physicians
Provides endpoints for processing lab results, acknowledging alerts,
and managing critical value alerts.

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel

from app.db.session import get_db
from app.models.notifications import (
    Notification,
    CriticalAlert,
    AlertAcknowledgment,
    NotificationStatus,
    NotificationType,
)
from app.services.critical_value_alerts import CriticalValueAlertService


logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class LabResultRequest(BaseModel):
    """Request model for processing lab result"""
    patient_id: int
    patient_name: str
    mrn: str
    test_name: str
    value: float
    unit: str
    ordering_physician: int
    patient_location: Optional[str] = None
    result_timestamp: Optional[datetime] = None


class CriticalAlertResponse(BaseModel):
    """Response model for critical alert"""
    id: str
    patient_id: int
    patient_name: str
    mrn: str
    test_name: str
    test_value: str
    test_unit: str
    critical_range: str
    ordering_physician_id: Optional[int]
    patient_location: Optional[str]
    result_timestamp: datetime
    acknowledged: bool
    acknowledged_at: Optional[datetime]
    escalation_level: int
    notification_id: Optional[str]

    class Config:
        orm_mode = True  # For Pydantic v1 compatibility


class AcknowledgeRequest(BaseModel):
    """Request model for acknowledging alert"""
    physician_id: int
    action_taken: str


class AcknowledgeResponse(BaseModel):
    """Response model for acknowledgment"""
    alert_id: str
    acknowledged: bool
    acknowledged_at: datetime
    message: str


class AlertStatsResponse(BaseModel):
    """Response model for alert statistics"""
    total_alerts: int
    unacknowledged_alerts: int
    acknowledged_alerts: int
    escalated_alerts: int
    avg_response_time_minutes: Optional[float]


@router.post("/process", response_model=Optional[CriticalAlertResponse], status_code=status.HTTP_200_OK)
async def process_lab_result(
    lab_result: LabResultRequest,
    db: AsyncSession = Depends(get_db)
):
    """Process lab result and check for critical values

    Args:
        lab_result: Lab result data to check
        db: Database session

    Returns:
        CriticalAlertResponse if critical value detected, None otherwise
    """
    try:
        service = CriticalValueAlertService(db)

        # Convert to dict for service
        lab_data = lab_result.dict()
        if lab_result.result_timestamp:
            lab_data["result_timestamp"] = lab_result.result_timestamp

        # Process lab result
        notification_id = await service.process_lab_result(lab_data)

        if notification_id:
            # Get the created critical alert
            query = select(CriticalAlert).where(
                CriticalAlert.notification_id == notification_id
            )
            result = await db.execute(query)
            alert = result.scalar_one_or_none()

            if alert:
                return CriticalAlertResponse(
                    id=str(alert.id),
                    patient_id=alert.patient_id,
                    patient_name=alert.patient_name,
                    mrn=alert.mrn,
                    test_name=alert.test_name,
                    test_value=alert.test_value,
                    test_unit=alert.test_unit,
                    critical_range=alert.critical_range,
                    ordering_physician_id=alert.ordering_physician_id,
                    patient_location=alert.patient_location,
                    result_timestamp=alert.result_timestamp,
                    acknowledged=alert.acknowledged,
                    acknowledged_at=alert.acknowledged_at,
                    escalation_level=alert.escalation_level,
                    notification_id=str(alert.notification_id) if alert.notification_id else None
                )

        return None

    except Exception as e:
        logger.error("Error processing lab result: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process lab result"
        )


@router.post("/{alert_id}/acknowledge", response_model=AcknowledgeResponse)
async def acknowledge_alert(
    alert_id: str,
    request: AcknowledgeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge a critical value alert

    Args:
        alert_id: Critical alert ID (UUID)
        request: Acknowledgment request
        db: Database session

    Returns:
        Acknowledgment response
    """
    try:
        import uuid
        from app.services.critical_value_alerts import CriticalValueAlertService

        service = CriticalValueAlertService(db)

        # Acknowledge via notification system
        # Get the notification ID for this alert
        query = select(CriticalAlert).where(
            CriticalAlert.id == uuid.UUID(alert_id)
        )
        result = await db.execute(query)
        alert = result.scalar_one_or_none()

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Critical alert not found"
            )

        if alert.notification_id:
            await service.acknowledge_alert(
                alert.notification_id,
                request.physician_id,
                request.action_taken
            )

        # Update the critical alert record
        alert.acknowledged = True
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = request.physician_id
        alert.action_taken = request.action_taken
        alert.updated_at = datetime.utcnow()

        # Create acknowledgment record
        response_time = None
        if alert.created_at:
            delta = datetime.utcnow() - alert.created_at
            response_time = int(delta.total_seconds())

        acknowledgment = AlertAcknowledgment(
            critical_alert_id=alert.id,
            physician_id=request.physician_id,
            acknowledgment_type="acknowledged",
            action_taken=request.action_taken,
            response_time_seconds=response_time
        )
        db.add(acknowledgment)

        await db.commit()

        logger.info(
            "Alert {} acknowledged by physician {}".format(
                alert_id, request.physician_id
            )
        )

        return AcknowledgeResponse(
            alert_id=alert_id,
            acknowledged=True,
            acknowledged_at=alert.acknowledged_at,
            message="Alert acknowledged successfully"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error acknowledging alert: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge alert"
        )


@router.get("/unacknowledged", response_model=List[CriticalAlertResponse])
async def get_unacknowledged_alerts(
    physician_id: Optional[int] = Query(None, description="Filter by physician"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    db: AsyncSession = Depends(get_db)
):
    """Get unacknowledged critical value alerts

    Args:
        physician_id: Optional filter by ordering physician
        limit: Maximum number of results
        db: Database session

    Returns:
        List of unacknowledged alerts
    """
    try:
        filters = [CriticalAlert.acknowledged == False]

        if physician_id:
            filters.append(CriticalAlert.ordering_physician_id == physician_id)

        query = select(CriticalAlert).where(
            and_(*filters)
        ).order_by(
            CriticalAlert.result_timestamp.desc()
        ).limit(limit)

        result = await db.execute(query)
        alerts = result.scalars().all()

        return [
            CriticalAlertResponse(
                id=str(alert.id),
                patient_id=alert.patient_id,
                patient_name=alert.patient_name,
                mrn=alert.mrn,
                test_name=alert.test_name,
                test_value=alert.test_value,
                test_unit=alert.test_unit,
                critical_range=alert.critical_range,
                ordering_physician_id=alert.ordering_physician_id,
                patient_location=alert.patient_location,
                result_timestamp=alert.result_timestamp,
                acknowledged=alert.acknowledged,
                acknowledged_at=alert.acknowledged_at,
                escalation_level=alert.escalation_level,
                notification_id=str(alert.notification_id) if alert.notification_id else None
            )
            for alert in alerts
        ]

    except Exception as e:
        logger.error("Error getting unacknowledged alerts: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts"
        )


@router.get("/stats", response_model=AlertStatsResponse)
async def get_alert_stats(
    physician_id: Optional[int] = Query(None, description="Filter by physician"),
    db: AsyncSession = Depends(get_db)
):
    """Get critical value alert statistics

    Args:
        physician_id: Optional filter by physician
        db: Database session

    Returns:
        Alert statistics
    """
    try:
        filters = []

        if physician_id:
            filters.append(CriticalAlert.ordering_physician_id == physician_id)

        # Total alerts
        total_query = select(func.count(CriticalAlert.id))
        if filters:
            total_query = total_query.where(and_(*filters))
        total_result = await db.execute(total_query)
        total_alerts = total_result.scalar() or 0

        # Unacknowledged alerts
        unack_filters = filters + [CriticalAlert.acknowledged == False]
        unack_query = select(func.count(CriticalAlert.id)).where(and_(*unack_filters))
        unack_result = await db.execute(unack_query)
        unacknowledged_alerts = unack_result.scalar() or 0

        # Acknowledged alerts
        ack_filters = filters + [CriticalAlert.acknowledged == True]
        ack_query = select(func.count(CriticalAlert.id)).where(and_(*ack_filters))
        ack_result = await db.execute(ack_query)
        acknowledged_alerts = ack_result.scalar() or 0

        # Escalated alerts (level > 0)
        esc_filters = filters + [CriticalAlert.escalation_level > 0]
        esc_query = select(func.count(CriticalAlert.id)).where(and_(*esc_filters))
        esc_result = await db.execute(esc_query)
        escalated_alerts = esc_result.scalar() or 0

        # Average response time
        avg_query = select(
            func.avg(AlertAcknowledgment.response_time_seconds)
        ).join(
            CriticalAlert,
            AlertAcknowledgment.critical_alert_id == CriticalAlert.id
        )
        if filters:
            avg_query = avg_query.where(and_(*filters))
        avg_result = await db.execute(avg_query)
        avg_seconds = avg_result.scalar()

        avg_response_time_minutes = None
        if avg_seconds:
            avg_response_time_minutes = round(avg_seconds / 60.0, 2)

        return AlertStatsResponse(
            total_alerts=total_alerts,
            unacknowledged_alerts=unacknowledged_alerts,
            acknowledged_alerts=acknowledged_alerts,
            escalated_alerts=escalated_alerts,
            avg_response_time_minutes=avg_response_time_minutes
        )

    except Exception as e:
        logger.error("Error getting alert stats: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )


@router.get("/{alert_id}", response_model=CriticalAlertResponse)
async def get_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific critical value alert

    Args:
        alert_id: Critical alert ID (UUID)
        db: Database session

    Returns:
        Critical alert details
    """
    try:
        import uuid

        query = select(CriticalAlert).where(
            CriticalAlert.id == uuid.UUID(alert_id)
        )
        result = await db.execute(query)
        alert = result.scalar_one_or_none()

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Critical alert not found"
            )

        return CriticalAlertResponse(
            id=str(alert.id),
            patient_id=alert.patient_id,
            patient_name=alert.patient_name,
            mrn=alert.mrn,
            test_name=alert.test_name,
            test_value=alert.test_value,
            test_unit=alert.test_unit,
            critical_range=alert.critical_range,
            ordering_physician_id=alert.ordering_physician_id,
            patient_location=alert.patient_location,
            result_timestamp=alert.result_timestamp,
            acknowledged=alert.acknowledged,
            acknowledged_at=alert.acknowledged_at,
            escalation_level=alert.escalation_level,
            notification_id=str(alert.notification_id) if alert.notification_id else None
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid alert ID format"
        )
    except Exception as e:
        logger.error("Error getting alert: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alert"
        )
