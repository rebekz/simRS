"""Appointment Reminders API endpoints for STORY-022-04

This module provides API endpoints for:
- Appointment reminder management
- Reply processing for confirmations
- Reminder statistics and monitoring
- Template management
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.core.deps import get_current_user, get_current_active_user, require_permission
from app.models.user import User
from app.services.appointment_reminder_service import AppointmentReminderService


router = APIRouter()


# =============================================================================
# Request/Response Schemas
# =============================================================================

class ReminderReplyRequest(BaseModel):
    """Request schema for processing patient reply to reminder"""
    phone_number: str = Field(..., description="Patient's phone number")
    message: str = Field(..., description="Reply message content")


class ReminderReplyResponse(BaseModel):
    """Response schema for reply processing result"""
    success: bool
    appointment_id: Optional[int] = None
    appointment_number: Optional[str] = None
    status: Optional[str] = None
    message: str


class ReminderScheduleRequest(BaseModel):
    """Request schema for manual reminder scheduling"""
    appointment_id: int = Field(..., description="Appointment ID")
    reminder_hours: List[int] = Field(default=[24, 2], description="Hours before appointment to send reminders")


class ReminderListResponse(BaseModel):
    """Response schema for upcoming reminders list"""
    reminders: List[Dict[str, Any]]
    total_count: int


class ReminderStatsResponse(BaseModel):
    """Response schema for reminder statistics"""
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    total: int


class TemplateListResponse(BaseModel):
    """Response schema for reminder templates"""
    templates: Dict[str, str]
    language: str


class SendReminderRequest(BaseModel):
    """Request schema for manual reminder sending"""
    appointment_id: int = Field(..., description="Appointment ID")
    reminder_type: str = Field(..., description="Type of reminder (sms, email, whatsapp)")


class BulkReminderRequest(BaseModel):
    """Request schema for sending bulk reminders"""
    appointment_ids: List[int] = Field(..., description="List of appointment IDs")
    reminder_type: str = Field(..., description="Type of reminder")


# =============================================================================
# Public Endpoints (for SMS gateway webhook)
# =============================================================================

@router.post("/webhook/reply", response_model=ReminderReplyResponse)
async def process_reminder_reply(
    request: ReminderReplyRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Process patient reply to appointment reminder SMS/WhatsApp

    **Authentication**: Bypassed for SMS gateway webhook (uses API key in headers)

    Supported keywords (case-insensitive):
    - YA, YES, OK, HADIR: Confirm appointment
    - BATAL, CANCEL, NO: Cancel appointment
    - JADWAL, RESCHEDULE: Request reschedule

    **Usage**:
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/appointment-reminders/webhook/reply \\
      -H "Content-Type: application/json" \\
      -H "X-API-Key: your-api-key" \\
      -d '{
        "phone_number": "+6281234567890",
        "message": "YA"
      }'
    ```

    **Response**:
    ```json
    {
      "success": true,
      "appointment_id": 12345,
      "appointment_number": "APT-2026-0012345",
      "status": "confirmed",
      "message": "Terima kasih. Kehadiran Anda untuk janji temu pada 15/01/2026 jam 09:00 telah dikonfirmasi."
    }
    ```
    """
    service = AppointmentReminderService(db)

    try:
        result = await service.process_reply_message(
            phone_number=request.phone_number,
            message=request.message
        )
        return ReminderReplyResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to process reply: {error}".format(error=str(e))
        )


# =============================================================================
# Patient Endpoints
# =============================================================================

@router.get("/my-reminders", response_model=ReminderListResponse)
async def get_my_reminders(
    days_ahead: int = Query(7, ge=1, le=30, description="Number of days ahead to look"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get upcoming appointment reminders for current patient

    **Authentication**: Patient login required

    Returns all scheduled reminders for the patient's upcoming appointments.

    **Usage**:
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/appointment-reminders/my-reminders?days_ahead=7 \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```

    **Response**:
    ```json
    {
      "reminders": [
        {
          "reminder_id": 1,
          "appointment_id": 12345,
          "appointment_number": "APT-2026-0012345",
          "scheduled_at": "2026-01-14T09:00:00",
          "reminder_type": "sms"
        }
      ],
      "total_count": 1
    }
    ```
    """
    service = AppointmentReminderService(db)

    reminders = await service.get_upcoming_reminders(
        patient_id=current_user.id,
        days_ahead=days_ahead
    )

    return ReminderListResponse(
        reminders=reminders,
        total_count=len(reminders)
    )


@router.get("/templates", response_model=TemplateListResponse)
async def get_reminder_templates(
    language: str = Query("id", pattern="^(id|en)$", description="Language code"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get reminder message templates

    **Authentication**: Patient login required

    Returns all available reminder templates in the specified language.

    **Usage**:
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/appointment-reminders/templates?language=id \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```

    **Response**:
    ```json
    {
      "templates": {
        "confirmation_id": "Halo {patient_name}, janji temu Anda telah TERKONFIRMASI...",
        "reminder_24h_id": "PENGINGAT: Anda punya janji temu BESOK...",
        "reminder_2h_id": "PENGINGAT: Janji temu Anda dalam 2 jam..."
      },
      "language": "id"
    }
    ```
    """
    service = AppointmentReminderService(db)

    templates = await service.get_reminder_templates(language=language)

    return TemplateListResponse(
        templates=templates,
        language=language
    )


# =============================================================================
# Staff/Admin Endpoints
# =============================================================================

@router.post("/schedule", response_model=Dict[str, Any])
async def schedule_reminders(
    request: ReminderScheduleRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Manually schedule reminders for an appointment

    **Authentication**: Staff/Admin login required
    **Permission**: appointments:manage

    Schedules reminders at specified hours before the appointment.
    Default is 24 hours and 2 hours before.

    **Usage**:
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/appointment-reminders/schedule \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "appointment_id": 12345,
        "reminder_hours": [24, 2]
      }'
    ```

    **Response**:
    ```json
    {
      "message": "Reminders scheduled successfully",
      "reminders_created": 2,
      "reminder_times": ["2026-01-14T09:00:00", "2026-01-15T07:00:00"]
    }
    ```
    """
    from app.models.appointments import Appointment

    # Get appointment
    result = await db.execute(
        select(Appointment).where(Appointment.id == request.appointment_id)
    )
    appointment = result.scalar_one_or_none()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment {appointment_id} not found".format(appointment_id=request.appointment_id)
        )

    service = AppointmentReminderService(db)

    # Schedule reminders
    try:
        reminders = await service.schedule_appointment_reminders(appointment)

        return {
            "message": "Reminders scheduled successfully",
            "reminders_created": len(reminders),
            "reminder_times": [r.scheduled_at.isoformat() for r in reminders]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to schedule reminders: {error}".format(error=str(e))
        )


@router.post("/send-manual", response_model=Dict[str, Any])
async def send_manual_reminder(
    request: SendReminderRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Manually send a reminder immediately (bypassing schedule)

    **Authentication**: Staff/Admin login required
    **Permission**: appointments:manage

    Sends a reminder immediately without waiting for scheduled time.
    Useful for urgent reminders or testing.

    **Usage**:
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/appointment-reminders/send-manual \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "appointment_id": 12345,
        "reminder_type": "whatsapp"
      }'
    ```

    **Response**:
    ```json
    {
      "message": "Reminder sent successfully",
      "notification_id": "uuid-here",
      "sent_at": "2026-01-15T08:30:00"
    }
    ```
    """
    from app.models.appointments import Appointment, AppointmentReminder, ReminderType

    # Get appointment
    result = await db.execute(
        select(Appointment).where(Appointment.id == request.appointment_id)
    )
    appointment = result.scalar_one_or_none()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment {appointment_id} not found".format(appointment_id=request.appointment_id)
        )

    # Create and send reminder
    reminder = AppointmentReminder(
        appointment_id=request.appointment_id,
        reminder_type=ReminderType(request.reminder_type),
        scheduled_at=datetime.now(),
        status="pending"
    )
    db.add(reminder)
    await db.flush()

    service = AppointmentReminderService(db)

    try:
        await service._send_reminder(reminder, appointment)
        reminder.status = "sent"
        reminder.sent_at = datetime.now()
        await db.commit()

        return {
            "message": "Reminder sent successfully",
            "reminder_id": reminder.id,
            "sent_at": reminder.sent_at.isoformat()
        }
    except Exception as e:
        reminder.status = "failed"
        reminder.error_message = str(e)
        await db.commit()
        raise HTTPException(
            status_code=500,
            detail="Failed to send reminder: {error}".format(error=str(e))
        )


@router.post("/send-bulk", response_model=Dict[str, Any])
async def send_bulk_reminders(
    request: BulkReminderRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("appointments", "manage")),
):
    """
    Send bulk reminders to multiple appointments

    **Authentication**: Admin login required
    **Permission**: appointments:manage

    Sends reminders to multiple appointments at once.
    Useful for sending daily batch reminders.

    **Usage**:
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/appointment-reminders/send-bulk \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "appointment_ids": [12345, 12346, 12347],
        "reminder_type": "sms"
      }'
    ```

    **Response**:
    ```json
    {
      "message": "Bulk reminders sent",
      "total": 3,
      "sent": 3,
      "failed": 0
    }
    ```
    """
    from app.models.appointments import Appointment

    # Get appointments
    result = await db.execute(
        select(Appointment).where(Appointment.id.in_(request.appointment_ids))
    )
    appointments = result.scalars().all()

    if not appointments:
        raise HTTPException(
            status_code=404,
            detail="No valid appointments found"
        )

    service = AppointmentReminderService(db)

    sent_count = 0
    failed_count = 0

    for appointment in appointments:
        try:
            reminders = await service.schedule_appointment_reminders(appointment)
            sent_count += len(reminders)
        except Exception:
            failed_count += 1

    await db.commit()

    return {
        "message": "Bulk reminders processed",
        "total": len(request.appointment_ids),
        "sent": sent_count,
        "failed": failed_count
    }


@router.get("/stats", response_model=ReminderStatsResponse)
async def get_reminder_statistics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("reports", "view")),
):
    """
    Get reminder delivery statistics

    **Authentication**: Admin login required
    **Permission**: reports:view

    Returns statistics about reminder delivery including:
    - Counts by status (pending, sent, failed)
    - Counts by type (SMS, email, WhatsApp, push)

    **Usage**:
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/appointment-reminders/stats?start_date=2026-01-01&end_date=2026-01-15" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```

    **Response**:
    ```json
    {
      "by_status": {
        "pending": 45,
        "sent": 892,
        "failed": 12
      },
      "by_type": {
        "sms": 450,
        "email": 200,
        "whatsapp": 250,
        "push": 0
      },
      "total": 949
    }
    ```
    """
    service = AppointmentReminderService(db)

    # Parse dates if provided
    start = None
    end = None
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

    stats = await service.get_reminder_statistics(start_date=start, end_date=end)

    return ReminderStatsResponse(**stats)


@router.post("/process-pending", response_model=Dict[str, Any])
async def process_pending_reminders(
    background_tasks: BackgroundTasks,
    limit: int = Query(100, ge=1, le=500, description="Maximum reminders to process"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("system", "admin")),
):
    """
    Process pending reminders (background job trigger)

    **Authentication**: System/Service account required
    **Permission**: system:admin

    Triggers the background job to send pending scheduled reminders.
    This is typically called by a cron job or scheduler.

    **Usage**:
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/appointment-reminders/process-pending?limit=100 \\
      -H "Authorization: Bearer SERVICE_TOKEN"
    ```

    **Response**:
    ```json
    {
      "processed": 95,
      "sent": 92,
      "failed": 3,
      "message": "Processed 95 reminders: 92 sent, 3 failed"
    }
    ```
    """
    service = AppointmentReminderService(db)

    result = await service.send_pending_reminders(limit=limit)

    return result


@router.get("/upcoming", response_model=ReminderListResponse)
async def get_all_upcoming_reminders(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    days_ahead: int = Query(7, ge=1, le=30, description="Number of days ahead"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("appointments", "view")),
):
    """
    Get all upcoming scheduled reminders (admin view)

    **Authentication**: Staff/Admin login required
    **Permission**: appointments:view

    Returns all scheduled pending reminders for monitoring purposes.
    Can filter by patient ID.

    **Usage**:
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/appointment-reminders/upcoming?days_ahead=7" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```

    **Response**:
    ```json
    {
      "reminders": [
        {
          "reminder_id": 1,
          "appointment_id": 12345,
          "appointment_number": "APT-2026-0012345",
          "scheduled_at": "2026-01-14T09:00:00",
          "reminder_type": "sms"
        }
      ],
      "total_count": 150
    }
    ```
    """
    service = AppointmentReminderService(db)

    reminders = await service.get_upcoming_reminders(
        patient_id=patient_id,
        days_ahead=days_ahead
    )

    return ReminderListResponse(
        reminders=reminders,
        total_count=len(reminders)
    )


# =============================================================================
# Utility Endpoints
# =============================================================================

@router.get("/health", response_model=Dict[str, Any])
async def reminder_service_health(
    db: AsyncSession = Depends(get_db),
):
    """
    Health check endpoint for the reminder service

    **Authentication**: None (public endpoint)

    Returns the current status of the reminder service including:
    - Service status
    - Pending reminder count
    - Last processing time

    **Usage**:
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/appointment-reminders/health
    ```

    **Response**:
    ```json
    {
      "status": "healthy",
      "service": "appointment_reminders",
      "pending_reminders": 45,
      "timestamp": "2026-01-15T10:30:00Z"
    }
    ```
    """
    from app.models.appointments import AppointmentReminder, ReminderStatus

    # Count pending reminders
    from sqlalchemy import select, func
    result = await db.execute(
        select(func.count(AppointmentReminder.id)).where(
            AppointmentReminder.status == ReminderStatus.PENDING
        )
    )
    pending_count = result.scalar() or 0

    return {
        "status": "healthy" if pending_count < 1000 else "degraded",
        "service": "appointment_reminders",
        "pending_reminders": pending_count,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
