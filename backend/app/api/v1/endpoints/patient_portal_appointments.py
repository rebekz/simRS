"""Patient Portal Appointment Booking Endpoints

API endpoints for appointment booking and management via patient portal.
STORY-043: Appointment Scheduling & Management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date, datetime, timedelta

from app.db.session import get_db
from app.models.patient_portal import PatientPortalUser
from app.api.v1.endpoints.patient_portal_auth import get_current_portal_user
from app.schemas.patient_portal.appointments import (
    AppointmentBookRequest,
    AppointmentResponse,
    AppointmentDetail,
    MyAppointmentsResponse,
    AvailableSlotsResponse,
    DepartmentAvailabilityItem,
    AppointmentRescheduleRequest,
    AppointmentCancelRequest,
    AppointmentCancelResponse,
    WaitlistJoinRequest,
    WaitlistResponse,
    CalendarIntegrationResponse,
    AppointmentInfoResponse,
    QueueStatusResponse,
)
from app.services.patient_portal.appointment_service import AppointmentBookingService
from app.services.patient_portal import PatientPortalEmailService, PatientPortalSMSService

router = APIRouter()


@router.get("/appointments/available-slots", response_model=AvailableSlotsResponse)
async def get_available_slots(
    department_id: int = Query(..., description="Department ID"),
    date_str: str = Query(..., description="Date in YYYY-MM-DD format"),
    doctor_id: Optional[int] = Query(None, description="Filter by specific doctor"),
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get available appointment slots for a department and date"""
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD",
        )

    service = AppointmentBookingService(db)
    try:
        return await service.get_available_slots(department_id, target_date, doctor_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/appointments/departments/{department_id}/availability", response_model=DepartmentAvailabilityItem)
async def get_department_availability(
    department_id: int,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get availability overview for a department"""
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = None
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD",
        )

    service = AppointmentBookingService(db)
    try:
        return await service.get_department_availability(department_id, start, end)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/appointments/book", response_model=AppointmentResponse)
async def book_appointment(
    request: AppointmentBookRequest,
    background_tasks: BackgroundTasks,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Book a new appointment"""
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = AppointmentBookingService(db)

    try:
        appointment = await service.book_appointment(current_user.patient_id, request)

        # Send confirmation notification
        background_tasks.add_task(send_appointment_confirmation, appointment, current_user)

        return AppointmentResponse(
            id=appointment.id,
            appointment_number=appointment.appointment_number,
            appointment_date=appointment.appointment_date,
            appointment_time=appointment.appointment_time,
            end_time=appointment.end_time,
            department_name=appointment.department.name if appointment.department else None,
            doctor_name=appointment.doctor.full_name if appointment.doctor else None,
            appointment_type=appointment.appointment_type.value,
            status=appointment.status.value,
            queue_number=appointment.queue_number,
            estimated_wait_time_minutes=appointment.estimated_wait_time_minutes,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/appointments/my-appointments", response_model=MyAppointmentsResponse)
async def get_my_appointments(
    include_past: bool = Query(True, description="Include past appointments"),
    include_cancelled: bool = Query(True, description="Include cancelled appointments"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of appointments to return"),
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all appointments for the current patient"""
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = AppointmentBookingService(db)
    return await service.get_my_appointments(
        current_user.patient_id,
        include_past=include_past,
        include_cancelled=include_cancelled,
        limit=limit,
    )


@router.get("/appointments/{appointment_id}", response_model=AppointmentDetail)
async def get_appointment_detail(
    appointment_id: int,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific appointment"""
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = AppointmentBookingService(db)
    try:
        return await service.get_appointment_detail(appointment_id, current_user.patient_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/appointments/{appointment_id}/cancel", response_model=AppointmentCancelResponse)
async def cancel_appointment(
    appointment_id: int,
    request: AppointmentCancelRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an appointment"""
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = AppointmentBookingService(db)
    success, message, appointment = await service.cancel_appointment(
        appointment_id,
        current_user.patient_id,
        request.reason,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    return AppointmentCancelResponse(
        success=True,
        message=message,
        cancellation_policy_info="Cancellations must be made at least 24 hours in advance.",
    )


@router.post("/appointments/{appointment_id}/reschedule", response_model=AppointmentDetail)
async def reschedule_appointment(
    appointment_id: int,
    request: AppointmentRescheduleRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Reschedule an appointment to a new date/time"""
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = AppointmentBookingService(db)
    success, message, appointment = await service.reschedule_appointment(
        appointment_id,
        current_user.patient_id,
        request.new_date,
        request.new_time,
        request.reason,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    return service._to_detail(appointment)


@router.get("/appointments/{appointment_id}/queue-status", response_model=QueueStatusResponse)
async def get_queue_status(
    appointment_id: int,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get real-time queue status for an appointment"""
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = AppointmentBookingService(db)
    try:
        status = await service.get_queue_status(appointment_id, current_user.patient_id)
        return QueueStatusResponse(**status)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/appointments/{appointment_id}/info", response_model=AppointmentInfoResponse)
async def get_appointment_info(
    appointment_id: int,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get comprehensive appointment information including pre-appointment checklist"""
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = AppointmentBookingService(db)

    try:
        appointment_detail = await service.get_appointment_detail(appointment_id, current_user.patient_id)
        checklist = await service.get_pre_appointment_checklist(appointment_id, current_user.patient_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return AppointmentInfoResponse(
        appointment=appointment_detail,
        pre_appointment_checklist=checklist,
        department_info=None,  # Could add department info
        doctor_info=None,    # Could add doctor info
    )


@router.post("/appointments/{appointment_id}/waitlist", response_model=WaitlistResponse)
async def join_waitlist(
    appointment_id: int,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Join waitlist for a fully booked slot

    This is a placeholder - in production would integrate with a waitlist system.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    # Placeholder response
    return WaitlistResponse(
        success=False,
        message="Waitlist feature coming soon. Please try booking a different time slot.",
        waitlist_position=None,
        estimated_wait_days=None,
    )


@router.get("/appointments/{appointment_id}/calendar", response_model=CalendarIntegrationResponse)
async def get_calendar_integration(
    appointment_id: int,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get calendar integration links for an appointment"""
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = AppointmentBookingService(db)

    try:
        appointment = await service.get_appointment_detail(appointment_id, current_user.patient_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    # Generate calendar URLs
    start_dt = datetime.combine(appointment.appointment_date, appointment.appointment_time)
    end_dt = start_dt + timedelta(minutes=appointment.duration_minutes or 30)

    # Google Calendar URL
    google_url = (
        f"https://calendar.google.com/calendar/render"
        f"?action=TEMPLATE"
        f"&text={appointment.department_name or 'Appointment'} - {appointment.appointment_type}"
        f"&dates={start_dt.strftime('%Y%m%dT%H%M%S')}/{end_dt.strftime('%Y%m%dT%H%M%S')}"
        f"&details=Appointment Number: {appointment.appointment_number}"
        f"&location={appointment.department_name or 'Hospital'}"
    )

    # Outlook/Office 365 URL
    outlook_url = (
        f"https://outlook.live.com/calendar/0/deeplink/compose"
        f"?path=/calendar/action/compose"
        f"&rru=addevent"
        f"&startdt={start_dt.strftime('%Y-%m-%dT%H:%M:%S')}"
        f"&enddt={end_dt.strftime('%Y-%m-%dT%H:%M:%S')}"
        f"&subject={appointment.department_name or 'Appointment'} - {appointment.appointment_type}"
        f"&location={appointment.department_name or 'Hospital'}"
        f"&body=Appointment Number: {appointment.appointment_number}"
    )

    # ICS file would be generated in production
    ics_url = f"/api/v1/portal/appointments/{appointment_id}/ics"

    return CalendarIntegrationResponse(
        google_calendar_url=google_url,
        outlook_calendar_url=outlook_url,
        ics_download_url=ics_url,
    )


# Helper function for background tasks
async def send_appointment_confirmation(appointment, user):
    """Send appointment confirmation via email and SMS"""
    email_service = PatientPortalEmailService()
    sms_service = PatientPortalSMSService()

    # Send email
    # await email_service.send_appointment_confirmation(
    #     to_email=user.email,
    #     patient_name=user.patient.full_name if user.patient else "Patient",
    #     appointment_number=appointment.appointment_number,
    #     appointment_date=appointment.appointment_date,
    #     appointment_time=appointment.appointment_time,
    #     department_name=appointment.department.name if appointment.department else None,
    # )

    # Send SMS
    # if user.phone:
    #     await sms_service.send_appointment_reminder(
    #         phone_number=user.phone,
    #         patient_name=user.patient.full_name if user.patient else "Patient",
    #         appointment_date=appointment.appointment_date,
    #         appointment_time=appointment.appointment_time,
    #         department_name=appointment.department.name if appointment.department else None,
    #     )
    pass
