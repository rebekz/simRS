"""Payment Reminder API Endpoints

STORY-022-08: Payment Due Reminders
API endpoints for payment reminder management and invoice notifications.

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
from app.services.payment_reminders import get_payment_reminder_service


logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class InvoiceData(BaseModel):
    """Invoice data for payment reminders"""
    patient_id: int
    patient_name: str
    invoice_id: int
    invoice_number: str
    amount: str
    due_date: str  # YYYY-MM-DD format
    description: Optional[str] = "Hospital services"
    services: Optional[List[str]] = []
    hospital_name: Optional[str] = "SIMRS Hospital"
    payment_link: Optional[str] = "https://portal.simrs.hospital/pay"
    invoice_link: Optional[str] = "https://portal.simrs.hospital/invoices"
    bank_details: Optional[str] = None
    hospital_phone: Optional[str] = "123-456-7890"
    invoice_date: Optional[str] = None


class PaymentConfirmationData(BaseModel):
    """Payment confirmation data"""
    patient_id: int
    patient_name: str
    invoice_id: int
    invoice_number: str
    amount: str
    payment_date: Optional[str] = None
    transaction_id: str
    remaining_balance: Optional[str] = "0"
    hospital_name: Optional[str] = "SIMRS Hospital"


class InsuranceClaimData(BaseModel):
    """Insurance claim notification data"""
    patient_id: int
    patient_name: str
    invoice_id: int
    invoice_number: str
    claim_id: str
    amount: str
    claim_date: Optional[str] = None
    status: str  # submitted, approved, rejected
    reason: Optional[str] = None
    patient_responsibility: Optional[str] = None
    appeal_days: Optional[int] = 30
    hospital_phone: Optional[str] = "123-456-7890"


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
async def schedule_payment_reminders(
    invoice: InvoiceData,
    db: AsyncSession = Depends(get_db)
):
    """Schedule all payment reminders for an invoice

    Schedules reminders at:
    - 7 days before due
    - 3 days before due
    - On due date
    - 1 day overdue (if not paid)
    """
    try:
        service = get_payment_reminder_service(db)

        scheduled = await service.schedule_payment_reminders(invoice.dict())

        return ScheduleRemindersResponse(
            success=True,
            message="Scheduled {} payment reminders".format(len(scheduled)),
            scheduled_reminders=scheduled
        )

    except Exception as e:
        logger.error("Error scheduling payment reminders: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule payment reminders"
        )


@router.post("/send-invoice", response_model=ReminderResponse)
async def send_invoice_delivery(
    invoice: InvoiceData,
    db: AsyncSession = Depends(get_db)
):
    """Send invoice to patient immediately

    Delivers invoice via email and in-app notification.
    Includes payment link and invoice details.
    """
    try:
        service = get_payment_reminder_service(db)

        # Set invoice date if not provided
        data = invoice.dict()
        if not data.get("invoice_date"):
            data["invoice_date"] = datetime.utcnow().strftime("%Y-%m-%d")

        notification_id = await service.send_invoice_delivery(data)

        if notification_id:
            return ReminderResponse(
                success=True,
                message="Invoice sent successfully",
                notification_id=notification_id
            )
        else:
            return ReminderResponse(
                success=False,
                message="Failed to send invoice"
            )

    except Exception as e:
        logger.error("Error sending invoice delivery: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send invoice"
        )


@router.post("/payment-confirmation", response_model=ReminderResponse)
async def send_payment_confirmation(
    payment: PaymentConfirmationData,
    db: AsyncSession = Depends(get_db)
):
    """Send payment confirmation to patient

    Sent immediately after payment is received.
    Stops reminder series for this invoice.
    """
    try:
        service = get_payment_reminder_service(db)

        # Set payment date if not provided
        data = payment.dict()
        if not data.get("payment_date"):
            data["payment_date"] = datetime.utcnow().strftime("%Y-%m-%d")

        notification_id = await service.send_payment_confirmation(data)

        # Cancel pending reminders for this invoice
        await service.cancel_payment_reminders(data.get("invoice_id"))

        if notification_id:
            return ReminderResponse(
                success=True,
                message="Payment confirmation sent, reminders cancelled",
                notification_id=notification_id
            )
        else:
            return ReminderResponse(
                success=False,
                message="Failed to send payment confirmation"
            )

    except Exception as e:
        logger.error("Error sending payment confirmation: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send payment confirmation"
        )


@router.post("/insurance-claim", response_model=ReminderResponse)
async def send_insurance_claim_notification(
    claim: InsuranceClaimData,
    db: AsyncSession = Depends(get_db)
):
    """Send insurance claim status notification

    Notifies patient about:
    - Claim submission
    - Claim approval
    - Claim rejection with appeal information
    """
    try:
        service = get_payment_reminder_service(db)

        # Set claim date if not provided
        data = claim.dict()
        if not data.get("claim_date"):
            data["claim_date"] = datetime.utcnow().strftime("%Y-%m-%d")

        notification_id = await service.send_insurance_claim_notification(data)

        if notification_id:
            return ReminderResponse(
                success=True,
                message="Insurance claim notification sent successfully",
                notification_id=notification_id
            )
        else:
            return ReminderResponse(
                success=False,
                message="Failed to send insurance claim notification"
            )

    except Exception as e:
        logger.error("Error sending insurance claim notification: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send insurance claim notification"
        )


@router.delete("/cancel-reminders/{invoice_id}")
async def cancel_payment_reminders(
    invoice_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Cancel all pending reminders for an invoice

    Use when invoice is paid or written off.
    """
    try:
        service = get_payment_reminder_service(db)

        cancelled = await service.cancel_payment_reminders(invoice_id)

        return {
            "success": True,
            "message": "Cancelled {} payment reminders".format(cancelled),
            "cancelled_count": cancelled
        }

    except Exception as e:
        logger.error("Error cancelling reminders: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel payment reminders"
        )


@router.get("/invoice/{invoice_id}/reminders")
async def get_invoice_reminders(
    invoice_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all reminders for a specific invoice

    Returns scheduled, sent, and cancelled reminders.
    """
    try:
        query = select(Notification).where(
            and_(
                Notification.notification_type == NotificationType.PAYMENT_REMINDER,
                Notification.metadata["invoice_id"].astext == str(invoice_id)
            )
        ).order_by(Notification.scheduled_at.asc())

        result = await db.execute(query)
        notifications = result.scalars().all()

        return [
            {
                "id": str(notification.id),
                "reminder_type": notification.metadata.get("reminder_type") if notification.metadata else None,
                "invoice_number": notification.metadata.get("invoice_number") if notification.metadata else None,
                "status": notification.status,
                "priority": notification.priority,
                "channel": notification.channel,
                "scheduled_at": notification.scheduled_at.isoformat() if notification.scheduled_at else None,
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                "created_at": notification.created_at.isoformat(),
            }
            for notification in notifications
        ]

    except Exception as e:
        logger.error("Error getting invoice reminders: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoice reminders"
        )


@router.get("/patient/{patient_id}/reminders")
async def get_patient_payment_reminders(
    patient_id: int,
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    db: AsyncSession = Depends(get_db)
):
    """Get all payment reminders for a patient

    Optionally filter by status (pending, sent, delivered, etc.)
    """
    try:
        filters = [
            Notification.notification_type == NotificationType.PAYMENT_REMINDER,
            Notification.recipient_id == patient_id
        ]

        if status:
            filters.append(Notification.status == status)

        query = select(Notification).where(
            and_(*filters)
        ).order_by(Notification.scheduled_at.asc()).limit(limit)

        result = await db.execute(query)
        notifications = result.scalars().all()

        return [
            {
                "id": str(notification.id),
                "title": notification.title,
                "reminder_type": notification.metadata.get("reminder_type") if notification.metadata else None,
                "invoice_number": notification.metadata.get("invoice_number") if notification.metadata else None,
                "amount": notification.metadata.get("amount") if notification.metadata else None,
                "status": notification.status,
                "scheduled_at": notification.scheduled_at.isoformat() if notification.scheduled_at else None,
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
            }
            for notification in notifications
        ]

    except Exception as e:
        logger.error("Error getting patient payment reminders: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patient payment reminders"
        )


@router.get("/stats/patient/{patient_id}")
async def get_patient_payment_stats(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for patient's payment reminders

    Returns counts by status and outstanding balance.
    """
    try:
        # Get all payment notifications for patient
        query = select(Notification).where(
            and_(
                Notification.notification_type == NotificationType.PAYMENT_REMINDER,
                Notification.recipient_id == patient_id
            )
        )
        result = await db.execute(query)
        notifications = result.scalars().all()

        # Count by status
        status_counts = {}
        reminder_type_counts = {}
        total = len(notifications)

        for notification in notifications:
            # Count by status
            status_str = notification.status
            status_counts[status_str] = status_counts.get(status_str, 0) + 1

            # Count by reminder type
            reminder_type = notification.metadata.get("reminder_type") if notification.metadata else None
            if reminder_type:
                reminder_type_counts[reminder_type] = reminder_type_counts.get(reminder_type, 0) + 1

        # Calculate outstanding amount from pending notifications
        outstanding_invoices = set()
        for notification in notifications:
            if notification.status == NotificationStatus.PENDING:
                invoice_number = notification.metadata.get("invoice_number") if notification.metadata else None
                if invoice_number:
                    outstanding_invoices.add(invoice_number)

        return {
            "patient_id": patient_id,
            "total": total,
            "by_status": status_counts,
            "by_reminder_type": reminder_type_counts,
            "outstanding_invoices": len(outstanding_invoices),
        }

    except Exception as e:
        logger.error("Error getting patient payment stats: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment statistics"
        )
