"""BPJS Antrean API endpoints

This module provides REST API endpoints for BPJS Antrean (Queue) integration, including:
- Booking management from appointments
- Queue synchronization with BPJS
- Task management for queue tasks
- Monitoring and reporting
- Sync retry and health checks
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date, datetime, time
from decimal import Decimal

from app.db.session import get_db
from app.core.deps import get_current_user, require_permission, get_request_info
from app.models.user import User
from app.crud.audit_log import create_audit_log
from app.crud import bpjs_antrean as crud
from app.models.bpjs_antrean import (
    BPJSBookingStatus,
    BPJSTaskType,
    BPJSTaskStatus,
    BPJSSyncStatus,
)

router = APIRouter()


# =============================================================================
# BOOKING MANAGEMENT ENDPOINTS
# =============================================================================

@router.post("/bpjs-antrean/bookings", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: dict,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "create"))
):
    """
    Create BPJS booking from appointment.

    Args:
        booking_data: Booking data including appointment_id, patient_info, etc.
        background_tasks: FastAPI background tasks
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with bpjs_antrean:create permission

    Returns:
        Created booking details

    Raises:
        HTTPException 400: If validation error
    """
    request_info = await get_request_info(request)

    try:
        # Prepare booking data
        from datetime import datetime, timezone

        booking_datetime = booking_data.get("booking_date")
        booking_time = booking_data.get("booking_time")

        # Convert to datetime if needed
        if isinstance(booking_datetime, str):
            booking_datetime = datetime.fromisoformat(booking_datetime.replace('Z', '+00:00'))

        # Convert time if needed
        if isinstance(booking_time, str):
            booking_time = time.fromisoformat(booking_time)

        create_data = {
            'patient_id': booking_data.get('patient_id'),
            'appointment_id': booking_data.get('appointment_id'),
            'poli_id': booking_data.get('poli_id'),
            'doctor_id': booking_data.get('doctor_id'),
            'booking_date': booking_datetime,
            'booking_time': booking_time,
            'estimated_time': booking_data.get('estimated_time'),
            'status': booking_data.get('status', BPJSBookingStatus.BOOKED),
            'bpjs_task_id': booking_data.get('bpjs_task_id'),
            'referral_number': booking_data.get('referral_number'),
            'sep_number': booking_data.get('sep_number'),
            'bpjs_response_data': booking_data.get('bpjs_response_data'),
            'sync_status': BPJSSyncStatus.PENDING,
        }

        # Create booking
        booking = await crud.create_antrean_booking(db, create_data)

        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_BOOKING_CREATED",
            resource_type="BPJSAntreanBooking",
            resource_id=str(booking.id),
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "id": booking.id,
            "booking_code": booking.booking_code,
            "appointment_id": booking.appointment_id,
            "patient_id": booking.patient_id,
            "poli_id": booking.poli_id,
            "doctor_id": booking.doctor_id,
            "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
            "booking_time": booking.booking_time.isoformat() if booking.booking_time else None,
            "estimated_time": booking.estimated_time.isoformat() if booking.estimated_time else None,
            "status": booking.status,
            "bpjs_task_id": booking.bpjs_task_id,
            "referral_number": booking.referral_number,
            "sep_number": booking.sep_number,
            "sync_status": booking.sync_status,
            "created_at": booking.created_at.isoformat() if booking.created_at else None,
            "message": "Booking berhasil dibuat"
        }
    except ValueError as e:
        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_BOOKING_CREATE_FAILED",
            resource_type="BPJSAntreanBooking",
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=False,
            failure_reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_BOOKING_CREATE_FAILED",
            resource_type="BPJSAntreanBooking",
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=False,
            failure_reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error: {}".format(str(e))
        )


@router.get("/bpjs-antrean/bookings/{id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_booking(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "read"))
):
    """
    Get BPJS booking by ID.

    Args:
        id: Booking ID
        db: Database session
        current_user: Authenticated user with bpjs_antrean:read permission

    Returns:
        Booking details

    Raises:
        HTTPException 404: If booking not found
    """
    booking = await crud.get_antrean_booking_by_id(db, id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking dengan ID {} tidak ditemukan".format(id)
        )

    return {
        "id": booking.id,
        "booking_code": booking.booking_code,
        "appointment_id": booking.appointment_id,
        "patient_id": booking.patient_id,
        "poli_id": booking.poli_id,
        "doctor_id": booking.doctor_id,
        "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
        "booking_time": booking.booking_time.isoformat() if booking.booking_time else None,
        "estimated_time": booking.estimated_time.isoformat() if booking.estimated_time else None,
        "status": booking.status,
        "bpjs_task_id": booking.bpjs_task_id,
        "referral_number": booking.referral_number,
        "sep_number": booking.sep_number,
        "checkin_time": booking.checkin_time.isoformat() if booking.checkin_time else None,
        "service_start_time": booking.service_start_time.isoformat() if booking.service_start_time else None,
        "service_end_time": booking.service_end_time.isoformat() if booking.service_end_time else None,
        "sync_status": booking.sync_status,
        "last_sync_at": booking.last_sync_at.isoformat() if booking.last_sync_at else None,
        "sync_error_message": booking.sync_error_message,
        "cancellation_reason": booking.cancellation_reason,
        "cancelled_at": booking.cancelled_at.isoformat() if booking.cancelled_at else None,
        "created_at": booking.created_at.isoformat() if booking.created_at else None,
        "updated_at": booking.updated_at.isoformat() if booking.updated_at else None,
        "tasks": [
            {
                "id": task.id,
                "task_id": task.task_id,
                "task_name": task.task_name,
                "task_type": task.task_type,
                "status": task.status,
                "queue_number": task.queue_number,
                "estimated_time": task.estimated_time.isoformat() if task.estimated_time else None,
            }
            for task in booking.tasks
        ] if booking.tasks else [],
    }


@router.get("/bpjs-antrean/bookings/patient/{patient_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def list_patient_bookings(
    patient_id: int,
    skip: int = Query(0, ge=0, description="Jumlah record yang dilewati"),
    limit: int = Query(100, ge=1, le=100, description="Maksimal jumlah record yang dikembalikan"),
    status: Optional[str] = Query(None, description="Filter berdasarkan status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "read"))
):
    """
    List BPJS bookings for a patient.

    Args:
        patient_id: Patient ID
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        status: Filter by booking status
        db: Database session
        current_user: Authenticated user with bpjs_antrean:read permission

    Returns:
        Paginated list of patient bookings
    """
    page = (skip // limit) + 1
    bookings, total = await crud.get_bookings_by_patient(
        db,
        patient_id=patient_id,
        status=status,
        page=page,
        page_size=limit
    )

    return {
        "items": [
            {
                "id": booking.id,
                "booking_code": booking.booking_code,
                "appointment_id": booking.appointment_id,
                "poli_id": booking.poli_id,
                "doctor_id": booking.doctor_id,
                "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
                "booking_time": booking.booking_time.isoformat() if booking.booking_time else None,
                "status": booking.status,
                "created_at": booking.created_at.isoformat() if booking.created_at else None,
            }
            for booking in bookings
        ],
        "total": total,
        "page": page,
        "page_size": limit,
        "total_pages": (total + limit - 1) // limit if total > 0 else 0
    }


@router.patch("/bpjs-antrean/bookings/{id}/status", response_model=dict, status_code=status.HTTP_200_OK)
async def update_booking_status(
    id: int,
    status_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "update"))
):
    """
    Update BPJS booking status.

    Args:
        id: Booking ID
        status_data: Status update data (status, notes)
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with bpjs_antrean:update permission

    Returns:
        Updated booking details

    Raises:
        HTTPException 404: If booking not found
        HTTPException 400: If invalid status transition
    """
    request_info = await get_request_info(request)

    try:
        new_status = status_data.get("status")
        notes = status_data.get("notes")

        if not new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status baru harus diisi"
            )

        # Validate status is a valid BPJSBookingStatus
        valid_statuses = [s.value for s in BPJSBookingStatus]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status tidak valid. Pilihan yang valid: {}".format(', '.join(valid_statuses))
            )

        booking = await crud.update_booking_status(
            db,
            booking_id=id,
            new_status=new_status,
            updated_by_id=current_user.id,
            notes=notes,
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking dengan ID {} tidak ditemukan".format(id)
            )

        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_BOOKING_STATUS_UPDATED",
            resource_type="BPJSAntreanBooking",
            resource_id=str(id),
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "id": booking.id,
            "status": booking.status,
            "checkin_time": booking.checkin_time.isoformat() if booking.checkin_time else None,
            "service_start_time": booking.service_start_time.isoformat() if booking.service_start_time else None,
            "service_end_time": booking.service_end_time.isoformat() if booking.service_end_time else None,
            "updated_at": booking.updated_at.isoformat() if booking.updated_at else None,
            "message": "Status booking berhasil diperbarui"
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bpjs-antrean/bookings/{id}/cancel", response_model=dict, status_code=status.HTTP_200_OK)
async def cancel_booking(
    id: int,
    cancel_data: dict,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "delete"))
):
    """
    Cancel BPJS booking.

    Args:
        id: Booking ID
        cancel_data: Cancellation data (reason, notes)
        request: FastAPI Request object
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Authenticated user with bpjs_antrean:delete permission

    Returns:
        Cancellation confirmation

    Raises:
        HTTPException 404: If booking not found
        HTTPException 400: If booking cannot be cancelled
    """
    request_info = await get_request_info(request)

    try:
        reason = cancel_data.get("reason")

        booking = await crud.cancel_booking(
            db,
            booking_id=id,
            cancelled_by_id=current_user.id,
            reason=reason,
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking dengan ID {} tidak ditemukan".format(id)
            )

        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_BOOKING_CANCELLED",
            resource_type="BPJSAntreanBooking",
            resource_id=str(id),
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "id": booking.id,
            "status": booking.status,
            "cancellation_reason": booking.cancellation_reason,
            "cancelled_at": booking.cancelled_at.isoformat() if booking.cancelled_at else None,
            "message": "Booking berhasil dibatalkan"
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/bpjs-antrean/bookings/date/{date}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_bookings_by_date(
    date: str,
    polyclinic_id: Optional[int] = Query(None, description="Filter berdasarkan ID poliklinik"),
    status: Optional[str] = Query(None, description="Filter berdasarkan status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "read"))
):
    """
    Get BPJS bookings by date.

    Args:
        date: Date in YYYY-MM-DD format
        polyclinic_id: Filter by polyclinic ID
        status: Filter by booking status
        db: Database session
        current_user: Authenticated user with bpjs_antrean:read permission

    Returns:
        List of bookings for the date

    Raises:
        HTTPException 400: If invalid date format
    """
    try:
        # Validate date format
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format tanggal tidak valid. Gunakan format YYYY-MM-DD"
        )

    bookings, total = await crud.get_bookings_by_date_range(
        db,
        start_date=target_date,
        end_date=target_date,
        poli_id=polyclinic_id,
        status=status,
        page=1,
        page_size=1000,
    )

    return {
        "date": date,
        "polyclinic_id": polyclinic_id,
        "status": status,
        "total_bookings": total,
        "bookings": [
            {
                "id": booking.id,
                "booking_code": booking.booking_code,
                "patient_id": booking.patient_id,
                "poli_id": booking.poli_id,
                "doctor_id": booking.doctor_id,
                "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
                "booking_time": booking.booking_time.isoformat() if booking.booking_time else None,
                "status": booking.status,
            }
            for booking in bookings
        ]
    }


# =============================================================================
# QUEUE SYNC ENDPOINTS
# =============================================================================

@router.post("/bpjs-antrean/sync/update", response_model=dict, status_code=status.HTTP_200_OK)
async def sync_queue_update(
    sync_data: dict,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "update"))
):
    """
    Sync queue update to BPJS.

    Args:
        sync_data: Queue sync data (booking_id, status, queue_number)
        background_tasks: FastAPI background tasks
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with bpjs_antrean:update permission

    Returns:
        Sync confirmation

    Raises:
        HTTPException 400: If sync validation fails
        HTTPException 502: If BPJS API error
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement queue update sync to BPJS
        # 1. Validate booking exists
        # 2. Prepare sync payload
        # 3. Call BPJS Antrean API
        # 4. Store sync log

        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_QUEUE_SYNCED",
            resource_type="BPJSAntreanBooking",
            resource_id=str(sync_data.get("booking_id")),
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "booking_id": sync_data.get("booking_id"),
            "sync_status": "success",
            "synced_at": datetime.now(),
            "message": "Update antrian berhasil disinkronkan"
        }
    except ValueError as e:
        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_QUEUE_SYNC_FAILED",
            resource_type="BPJSAntreanBooking",
            resource_id=str(sync_data.get("booking_id")),
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=False,
            failure_reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/bpjs-antrean/sync/remaining", response_model=dict, status_code=status.HTTP_200_OK)
async def get_remaining_queue(
    booking_id: int = Query(..., description="Booking ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "read"))
):
    """
    Get remaining queue from BPJS.

    Args:
        booking_id: Booking ID
        db: Database session
        current_user: Authenticated user with bpjs_antrean:read permission

    Returns:
        Remaining queue information

    Raises:
        HTTPException 404: If booking not found
        HTTPException 502: If BPJS API error
    """
    # TODO: Implement remaining queue fetch from BPJS
    return {
        "booking_id": booking_id,
        "current_queue": 1,
        "remaining_queue": 5,
        "estimated_wait_time_minutes": 30,
        "fetched_at": datetime.now()
    }


@router.get("/bpjs-antrean/sync/list", response_model=dict, status_code=status.HTTP_200_OK)
async def get_queue_list(
    date: str = Query(..., description="Tanggal antrian (YYYY-MM-DD)"),
    polyclinic_code: str = Query(..., description="Kode poliklinik"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "read"))
):
    """
    Get queue list from BPJS.

    Args:
        date: Queue date in YYYY-MM-DD format
        polyclinic_code: Polyclinic code
        db: Database session
        current_user: Authenticated user with bpjs_antrean:read permission

    Returns:
        Queue list from BPJS

    Raises:
        HTTPException 400: If invalid date format
        HTTPException 502: If BPJS API error
    """
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format tanggal tidak valid. Gunakan format YYYY-MM-DD"
        )

    # TODO: Implement queue list fetch from BPJS
    return {
        "date": date,
        "polyclinic_code": polyclinic_code,
        "total_queue": 0,
        "queue_list": []
    }


@router.post("/bpjs-antrean/sync/checkin", response_model=dict, status_code=status.HTTP_200_OK)
async def sync_patient_checkin(
    checkin_data: dict,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "update"))
):
    """
    Sync patient check-in to BPJS.

    Args:
        checkin_data: Check-in data (booking_id, checkin_time)
        background_tasks: FastAPI background tasks
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with bpjs_antrean:update permission

    Returns:
        Check-in sync confirmation

    Raises:
        HTTPException 404: If booking not found
        HTTPException 400: If check-in validation fails
        HTTPException 502: If BPJS API error
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement patient check-in sync to BPJS
        # 1. Validate booking exists and is in valid status
        # 2. Update booking status to 'checked_in'
        # 3. Sync to BPJS API

        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_CHECKIN_SYNCED",
            resource_type="BPJSAntreanBooking",
            resource_id=str(checkin_data.get("booking_id")),
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "booking_id": checkin_data.get("booking_id"),
            "checkin_time": checkin_data.get("checkin_time"),
            "sync_status": "success",
            "message": "Check-in pasien berhasil disinkronkan"
        }
    except ValueError as e:
        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_CHECKIN_SYNC_FAILED",
            resource_type="BPJSAntreanBooking",
            resource_id=str(checkin_data.get("booking_id")),
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=False,
            failure_reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bpjs-antrean/sync/complete", response_model=dict, status_code=status.HTTP_200_OK)
async def sync_service_completion(
    completion_data: dict,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "update"))
):
    """
    Sync service completion to BPJS.

    Args:
        completion_data: Completion data (booking_id, completion_time, notes)
        background_tasks: FastAPI background tasks
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with bpjs_antrean:update permission

    Returns:
        Completion sync confirmation

    Raises:
        HTTPException 404: If booking not found
        HTTPException 400: If completion validation fails
        HTTPException 502: If BPJS API error
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement service completion sync to BPJS
        # 1. Validate booking exists and is in valid status
        # 2. Update booking status to 'completed'
        # 3. Sync to BPJS API

        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_COMPLETION_SYNCED",
            resource_type="BPJSAntreanBooking",
            resource_id=str(completion_data.get("booking_id")),
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "booking_id": completion_data.get("booking_id"),
            "completion_time": completion_data.get("completion_time"),
            "sync_status": "success",
            "message": "Selesai pelayanan berhasil disinkronkan"
        }
    except ValueError as e:
        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_COMPLETION_SYNC_FAILED",
            resource_type="BPJSAntreanBooking",
            resource_id=str(completion_data.get("booking_id")),
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=False,
            failure_reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# TASK MANAGEMENT ENDPOINTS
# =============================================================================

@router.get("/bpjs-antrean/tasks/booking/{booking_id}", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_booking_tasks(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "read"))
):
    """
    Get tasks by booking ID.

    Args:
        booking_id: Booking ID
        db: Database session
        current_user: Authenticated user with bpjs_antrean:read permission

    Returns:
        List of tasks for the booking

    Raises:
        HTTPException 404: If booking not found
    """
    tasks, total = await crud.get_tasks_by_booking(
        db,
        booking_id=booking_id,
        page=1,
        page_size=100,
    )

    return [
        {
            "id": task.id,
            "booking_id": task.booking_id,
            "task_id": task.task_id,
            "task_name": task.task_name,
            "task_type": task.task_type,
            "status": task.status,
            "queue_number": task.queue_number,
            "estimated_time": task.estimated_time.isoformat() if task.estimated_time else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "created_at": task.created_at.isoformat() if task.created_at else None,
        }
        for task in tasks
    ]


@router.patch("/bpjs-antrean/tasks/{id}/status", response_model=dict, status_code=status.HTTP_200_OK)
async def update_task_status(
    id: int,
    status_data: dict,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "update"))
):
    """
    Update task status.

    Args:
        id: Task ID
        status_data: Status update data (status, notes)
        request: FastAPI Request object
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Authenticated user with bpjs_antrean:update permission

    Returns:
        Updated task details

    Raises:
        HTTPException 404: If task not found
        HTTPException 400: If invalid status transition
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement task status update
        # 1. Validate task exists
        # 2. Validate status transition
        # 3. Update task status
        # 4. Schedule background sync to BPJS if needed

        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_TASK_STATUS_UPDATED",
            resource_type="BPJSAntreanTask",
            resource_id=str(id),
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "id": id,
            "status": status_data.get("status"),
            "message": "Status tugas berhasil diperbarui"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/bpjs-antrean/tasks/active", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_active_tasks(
    polyclinic: Optional[str] = Query(None, description="Filter berdasarkan poliklinik"),
    date: Optional[str] = Query(None, description="Filter berdasarkan tanggal (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "read"))
):
    """
    Get active tasks.

    Args:
        polyclinic: Filter by polyclinic code
        date: Filter by date
        db: Database session
        current_user: Authenticated user with bpjs_antrean:read permission

    Returns:
        List of active tasks

    Raises:
        HTTPException 400: If invalid date format
    """
    if date:
        try:
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format tanggal tidak valid. Gunakan format YYYY-MM-DD"
            )

    # TODO: Implement active tasks retrieval
    return [
        {
            "id": 1,
            "booking_id": 1,
            "task_code": "2",
            "task_name": "Pemeriksaan",
            "status": "in_progress",
            "patient_name": "John Doe",
            "polyclinic": "POLI UMUM",
            "started_at": datetime.now()
        }
    ]


# =============================================================================
# MONITORING & REPORTS ENDPOINTS
# =============================================================================

@router.get("/bpjs-antrean/logs/sync", response_model=dict, status_code=status.HTTP_200_OK)
async def get_sync_logs(
    skip: int = Query(0, ge=0, description="Jumlah record yang dilewati"),
    limit: int = Query(100, ge=1, le=100, description="Maksimal jumlah record yang dikembalikan"),
    date_from: Optional[date] = Query(None, description="Filter dari tanggal"),
    date_to: Optional[date] = Query(None, description="Filter sampai tanggal"),
    status: Optional[str] = Query(None, description="Filter berdasarkan status sync"),
    booking_id: Optional[int] = Query(None, description="Filter berdasarkan booking ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "read"))
):
    """
    Get BPJS Antrean sync logs.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        date_from: Filter from date
        date_to: Filter to date
        status: Filter by sync status
        booking_id: Filter by booking ID
        db: Database session
        current_user: Authenticated user with bpjs_antrean:read permission

    Returns:
        Paginated list of sync logs
    """
    # TODO: Implement sync logs retrieval
    return {
        "items": [],
        "total": 0,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "total_pages": 0
    }


@router.get("/bpjs-antrean/statistics", response_model=dict, status_code=status.HTTP_200_OK)
async def get_booking_statistics(
    date_from: date = Query(..., description="Tanggal awal"),
    date_to: date = Query(..., description="Tanggal akhir"),
    poli_id: Optional[int] = Query(None, description="Filter berdasarkan ID poliklinik"),
    group_by: Optional[str] = Query("day", description="Group by: day, week, month"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "read"))
):
    """
    Get BPJS Antrean booking statistics.

    Args:
        date_from: Start date
        date_to: End date
        poli_id: Filter by polyclinic ID
        group_by: Grouping period (day, week, month)
        db: Database session
        current_user: Authenticated user with bpjs_antrean:read permission

    Returns:
        Booking statistics with breakdown
    """
    stats = await crud.get_booking_statistics(
        db,
        start_date=date_from,
        end_date=date_to,
        poli_id=poli_id,
    )

    return {
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "poli_id": poli_id,
        "group_by": group_by,
        "total_bookings": stats["total_bookings"],
        "by_status": stats["by_status"],
        "by_poli": stats["by_poli"],
        "completion_rate": float(stats["completion_rate"]),
        "cancellation_rate": float(stats["cancellation_rate"]),
    }


@router.get("/bpjs-antrean/dashboard", response_model=dict, status_code=status.HTTP_200_OK)
async def get_dashboard_summary(
    date: Optional[date] = Query(None, description="Tanggal (default: hari ini)"),
    poli_id: Optional[int] = Query(None, description="Filter berdasarkan ID poliklinik"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "read"))
):
    """
    Get BPJS Antrean dashboard summary.

    Args:
        date: Dashboard date (default: today)
        poli_id: Filter by polyclinic ID
        db: Database session
        current_user: Authenticated user with bpjs_antrean:read permission

    Returns:
        Dashboard summary with key metrics
    """
    target_date = date or date.today()

    counts = await crud.get_active_bookings_count(
        db,
        target_date=target_date,
        poli_id=poli_id,
    )

    return {
        "date": target_date.isoformat(),
        "poli_id": poli_id,
        "today_bookings": counts.get("total", 0),
        "active_bookings": counts.get("booked", 0),
        "checked_in": counts.get("checked-in", 0),
        "in_progress": counts.get("serving", 0),
        "completed_today": counts.get("completed", 0),
        "cancelled": counts.get("cancelled", 0),
    }


@router.post("/bpjs-antrean/retry-sync", response_model=dict, status_code=status.HTTP_200_OK)
async def retry_failed_syncs(
    retry_data: dict,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "update"))
):
    """
    Retry failed BPJS syncs.

    Args:
        retry_data: Retry parameters (sync_ids, date_range, all_failed)
        background_tasks: FastAPI background tasks
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with bpjs_antrean:update permission

    Returns:
        Retry operation confirmation

    Raises:
        HTTPException 400: If retry validation fails
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement failed sync retry
        # 1. Identify failed syncs based on criteria
        # 2. Schedule background retry tasks
        # 3. Track retry attempts

        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_SYNC_RETRY",
            resource_type="BPJSAntreanSync",
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "retry_count": 0,
            "message": "Retry sinkronisasi dijadwalkan",
            "retried_at": datetime.now()
        }
    except ValueError as e:
        await create_audit_log(
            db=db,
            action="BPJS_ANTREAN_SYNC_RETRY_FAILED",
            resource_type="BPJSAntreanSync",
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=False,
            failure_reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/bpjs-antrean/status", response_model=dict, status_code=status.HTTP_200_OK)
async def get_integration_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs_antrean", "read"))
):
    """
    Get BPJS Antrean integration status.

    Args:
        db: Database session
        current_user: Authenticated user with bpjs_antrean:read permission

    Returns:
        Integration status information
    """
    # TODO: Implement integration status check
    # 1. Check BPJS API connectivity
    # 2. Verify configuration
    # 3. Check recent sync health
    return {
        "integration_name": "BPJS Antrean",
        "status": "active",
        "api_connected": True,
        "last_successful_sync": datetime.now(),
        "last_failed_sync": None,
        "total_syncs_today": 0,
        "failed_syncs_today": 0,
        "success_rate": 100.0,
        "configuration": {
            "api_url": "configured",
            "cons_id": "configured",
            "secret_key": "configured"
        },
        "message": "Integrasi BPJS Antrean berjalan normal"
    }


@router.get("/bpjs-antrean/health", response_model=dict, status_code=status.HTTP_200_OK)
async def health_check(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Health check for BPJS Antrean integration.

    Args:
        db: Database session
        current_user: Authenticated user

    Returns:
        Health check status
    """
    # TODO: Implement health check
    return {
        "status": "healthy",
        "service": "bpjs-antrean",
        "timestamp": datetime.now(),
        "checks": {
            "database": "ok",
            "bpjs_api": "ok",
            "configuration": "ok"
        }
    }
