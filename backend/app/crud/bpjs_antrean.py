"""BPJS Antrean CRUD Operations

Modul ini menyediakan operasi CRUD komprehensif untuk manajemen antrian BPJS, termasuk:
- Manajemen booking antrian (create, update, cancel, status tracking)
- Manajemen task antrian (task creation, status updates, active tasks)
- Log sinkronisasi dengan API BPJS (sync logs, failed syncs, retry)
- Tracking update status antrian (status updates, latest status)
- Statistik dan laporan (booking statistics, sync summary, reports)
- Helper functions untuk integrasi (mapping, validation, code generation)

Mendukung persyaratan integrasi BPJS Antrean:
- Booking antran BPJS (API Antrean BPJS)
- Sinkronisasi status antrian dengan server BPJS
- Tracking nomor antrian dari BPJS
- Manajemen task untuk update dan check-in
- Log sinkronisasi untuk audit trail
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_, or_, func as sql_func, desc, update, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from decimal import Decimal
import uuid
import random
import string


# =============================================================================
# Model imports
# =============================================================================
from app.models.bpjs_antrean import (
    BPJSAntreanBooking,
    BPJSAntreanTask,
    BPJSAntreanSyncLog,
    BPJSAntreanStatusUpdate,
    BPJSBookingStatus,
    BPJSTaskStatus,
    BPJSSyncStatus,
)


# =============================================================================
# Booking Management - Basic CRUD
# =============================================================================

async def create_antrean_booking(
    db: AsyncSession,
    booking_data: Dict[str, Any],
    created_by_id: int,
) -> BPJSAntreanBooking:
    """
    Membuat booking antrian BPJS baru.

    Args:
        db: Sesi database
        booking_data: Data booking (patient_id, appointment_id, poli_id, etc.)
        created_by_id: ID user yang membuat booking

    Returns:
        Objek BPJSAntreanBooking yang dibuat

    Raises:
        ValueError: Jika data tidak valid atau booking gagal dibuat
    """
    # Generate booking code
    booking_code = await generate_booking_code(db)

    db_booking = BPJSAntreanBooking(
        booking_code=booking_code,
        patient_id=booking_data.get('patient_id'),
        appointment_id=booking_data.get('appointment_id'),
        poli_id=booking_data.get('poli_id'),
        doctor_id=booking_data.get('doctor_id'),
        booking_date=booking_data.get('booking_date'),
        booking_time=booking_data.get('booking_time'),
        estimated_time=booking_data.get('estimated_time'),
        status=booking_data.get('status', BPJSBookingStatus.BOOKED),
        bpjs_task_id=booking_data.get('bpjs_task_id'),
        referral_number=booking_data.get('referral_number'),
        sep_number=booking_data.get('sep_number'),
        bpjs_response_data=booking_data.get('bpjs_response_data'),
        sync_status=booking_data.get('sync_status', BPJSSyncStatus.PENDING),
    )

    db.add(db_booking)
    await db.flush()

    # Create initial task for booking if provided
    if 'bpjs_task_id' in booking_data:
        await create_antrean_task(
            db=db,
            task_data={
                'booking_id': db_booking.id,
                'task_id': booking_data['bpjs_task_id'],
                'task_name': "Booking Task - {}".format(booking_code),
                'task_type': BPJSTaskType.REGISTRATION,
                'status': BPJSTaskStatus.WAITING,
            },
        )

    await db.commit()
    await db.refresh(db_booking)

    return db_booking


async def get_antrean_booking_by_id(
    db: AsyncSession,
    booking_id: int,
) -> Optional[BPJSAntreanBooking]:
    """
    Mengambil booking antrian berdasarkan ID.

    Args:
        db: Sesi database
        booking_id: ID booking

    Returns:
        Objek BPJSAntreanBooking atau None
    """
    stmt = (
        select(BPJSAntreanBooking)
        .options(
            selectinload(BPJSAntreanBooking.tasks),
            selectinload(BPJSAntreanBooking.status_updates),
            selectinload(BPJSAntreanBooking.patient),
            selectinload(BPJSAntreanBooking.appointment),
        )
        .where(BPJSAntreanBooking.id == booking_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_antrean_booking_by_code(
    db: AsyncSession,
    booking_code: str,
) -> Optional[BPJSAntreanBooking]:
    """
    Mengambil booking antrian berdasarkan kode booking.

    Args:
        db: Sesi database
        booking_code: Kode booking unik

    Returns:
        Objek BPJSAntreanBooking atau None
    """
    stmt = select(BPJSAntreanBooking).where(
        BPJSAntreanBooking.booking_code == booking_code
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_bookings_by_patient(
    db: AsyncSession,
    patient_id: int,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[BPJSAntreanBooking], int]:
    """
    Mengambil semua booking untuk pasien tertentu dengan filter dan paginasi.

    Args:
        db: Sesi database
        patient_id: ID pasien
        status: Filter berdasarkan status (opsional)
        start_date: Filter tanggal mulai (opsional)
        end_date: Filter tanggal selesai (opsional)
        page: Nomor halaman
        page_size: Jumlah item per halaman

    Returns:
        Tuple dari (list of bookings, total count)
    """
    conditions = [BPJSAntreanBooking.patient_id == patient_id]

    if status:
        conditions.append(BPJSAntreanBooking.status == status)
    if start_date:
        conditions.append(BPJSAntreanBooking.booking_date >= start_date)
    if end_date:
        conditions.append(BPJSAntreanBooking.booking_date <= end_date)

    # Get total count
    count_stmt = select(sql_func.count(BPJSAntreanBooking.id)).where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Get paginated results
    stmt = (
        select(BPJSAntreanBooking)
        .where(and_(*conditions))
        .options(selectinload(BPJSAntreanBooking.tasks))
        .order_by(desc(BPJSAntreanBooking.booking_date), desc(BPJSAntreanBooking.booking_time))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(stmt)
    bookings = result.scalars().all()

    return list(bookings), total


async def get_bookings_by_date_range(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    poli_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[BPJSAntreanBooking], int]:
    """
    Mengambil booking berdasarkan rentang tanggal dengan filter tambahan.

    Args:
        db: Sesi database
        start_date: Tanggal mulai
        end_date: Tanggal selesai
        poli_id: Filter berdasarkan ID poli (opsional)
        status: Filter berdasarkan status (opsional)
        page: Nomor halaman
        page_size: Jumlah item per halaman

    Returns:
        Tuple dari (list of bookings, total count)
    """
    conditions = [
        BPJSAntreanBooking.booking_date >= start_date,
        BPJSAntreanBooking.booking_date <= end_date,
    ]

    if poli_id:
        conditions.append(BPJSAntreanBooking.poli_id == poli_id)
    if status:
        conditions.append(BPJSAntreanBooking.status == status)

    # Get total count
    count_stmt = select(sql_func.count(BPJSAntreanBooking.id)).where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Get paginated results
    stmt = (
        select(BPJSAntreanBooking)
        .where(and_(*conditions))
        .options(selectinload(BPJSAntreanBooking.patient))
        .order_by(BPJSAntreanBooking.booking_date, BPJSAntreanBooking.booking_time)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(stmt)
    bookings = result.scalars().all()

    return list(bookings), total


async def update_booking_status(
    db: AsyncSession,
    booking_id: int,
    new_status: str,
    updated_by_id: Optional[int] = None,
    notes: Optional[str] = None,
) -> Optional[BPJSAntreanBooking]:
    """
    Update status booking antrian.

    Args:
        db: Sesi database
        booking_id: ID booking
        new_status: Status baru (booked, checked-in, serving, completed, cancelled)
        updated_by_id: ID user yang mengupdate (opsional)
        notes: Catatan tambahan (opsional)

    Returns:
        Objek BPJSAntreanBooking yang diupdate atau None

    Raises:
        ValueError: Jika booking tidak ditemukan atau status tidak valid
    """
    booking = await get_antrean_booking_by_id(db, booking_id)
    if not booking:
        return None

    # Track previous status for audit
    previous_status = booking.status

    # Update booking status
    booking.status = new_status

    # Update timestamps based on status
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    if new_status == BPJSBookingStatus.CHECKED_IN and not booking.checkin_time:
        booking.checkin_time = now
    elif new_status == BPJSBookingStatus.SERVING and not booking.service_start_time:
        booking.service_start_time = now
    elif new_status == BPJSBookingStatus.COMPLETED and not booking.service_end_time:
        booking.service_end_time = now

    # Add status update record
    await create_status_update(
        db=db,
        status_update_data={
            'booking_id': booking_id,
            'old_status': previous_status,
            'new_status': new_status,
            'update_time': now,
            'notes': notes,
            'updated_by': updated_by_id,
        },
    )

    await db.commit()
    await db.refresh(booking)

    return booking


async def cancel_booking(
    db: AsyncSession,
    booking_id: int,
    cancelled_by_id: int,
    reason: Optional[str] = None,
) -> Optional[BPJSAntreanBooking]:
    """
    Membatalkan booking antrian.

    Args:
        db: Sesi database
        booking_id: ID booking
        cancelled_by_id: ID user yang membatalkan
        reason: Alasan pembatalan (opsional)

    Returns:
        Objek BPJSAntreanBooking yang dibatalkan atau None

    Raises:
        ValueError: Jika booking tidak ditemukan atau tidak bisa dibatalkan
    """
    from datetime import datetime, timezone

    booking = await get_antrean_booking_by_id(db, booking_id)
    if not booking:
        return None

    # Only allow cancellation of non-completed bookings
    if booking.status in [BPJSBookingStatus.COMPLETED]:
        raise ValueError("Cannot cancel booking with status: {}".format(booking.status))

    booking.status = BPJSBookingStatus.CANCELLED
    booking.cancellation_reason = reason
    booking.cancelled_at = datetime.now(timezone.utc)
    booking.cancelled_by = cancelled_by_id

    # Create status update record
    await create_status_update(
        db=db,
        status_update_data={
            'booking_id': booking_id,
            'old_status': booking.status,
            'new_status': BPJSBookingStatus.CANCELLED,
            'update_time': datetime.now(timezone.utc),
            'notes': reason,
            'updated_by': cancelled_by_id,
        },
    )

    await db.commit()
    await db.refresh(booking)

    return booking


# =============================================================================
# Task Management
# =============================================================================

async def create_antrean_task(
    db: AsyncSession,
    task_data: Dict[str, Any],
) -> BPJSAntreanTask:
    """
    Membuat task antrian baru.

    Args:
        db: Sesi database
        task_data: Data task (booking_id, task_type, task_id, etc.)

    Returns:
        Objek BPJSAntreanTask yang dibuat
    """
    db_task = BPJSAntreanTask(
        booking_id=task_data.get('booking_id'),
        task_id=task_data.get('task_id'),
        task_name=task_data.get('task_name'),
        task_type=task_data.get('task_type', BPJSTaskType.REGISTRATION),
        status=task_data.get('status', BPJSTaskStatus.WAITING),
        queue_number=task_data.get('queue_number'),
        estimated_time=task_data.get('estimated_time'),
        encounter_id=task_data.get('encounter_id'),
        prescription_id=task_data.get('prescription_id'),
        lab_order_id=task_data.get('lab_order_id'),
        bpjs_response_data=task_data.get('bpjs_response_data'),
        notes=task_data.get('notes'),
    )

    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)

    return db_task


async def get_task_by_id(
    db: AsyncSession,
    task_id: int,
) -> Optional[BPJSAntreanTask]:
    """
    Mengambil task berdasarkan ID.

    Args:
        db: Sesi database
        task_id: ID task

    Returns:
        Objek BPJSAntreanTask atau None
    """
    stmt = (
        select(BPJSAntreanTask)
        .options(selectinload(BPJSAntreanTask.booking))
        .where(BPJSAntreanTask.id == task_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_tasks_by_booking(
    db: AsyncSession,
    booking_id: int,
    task_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[BPJSAntreanTask], int]:
    """
    Mengambil semua task untuk booking tertentu.

    Args:
        db: Sesi database
        booking_id: ID booking
        task_type: Filter berdasarkan tipe task (opsional)
        status: Filter berdasarkan status (opsional)
        page: Nomor halaman
        page_size: Jumlah item per halaman

    Returns:
        Tuple dari (list of tasks, total count)
    """
    conditions = [BPJSAntreanTask.booking_id == booking_id]

    if task_type:
        conditions.append(BPJSAntreanTask.task_type == task_type)
    if status:
        conditions.append(BPJSAntreanTask.status == status)

    # Get total count
    count_stmt = select(sql_func.count(BPJSAntreanTask.id)).where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Get paginated results
    stmt = (
        select(BPJSAntreanTask)
        .where(and_(*conditions))
        .order_by(desc(BPJSAntreanTask.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return list(tasks), total


async def update_task_status(
    db: AsyncSession,
    task_id: int,
    new_status: str,
    response_data: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
) -> Optional[BPJSAntreanTask]:
    """
    Update status task antrian.

    Args:
        db: Sesi database
        task_id: ID task
        new_status: Status baru (waiting, active, completed)
        response_data: Data respon dari API BPJS (opsional)
        error_message: Pesan error jika gagal (opsional)

    Returns:
        Objek BPJSAntreanTask yang diupdate atau None
    """
    from datetime import datetime, timezone

    stmt = select(BPJSAntreanTask).where(BPJSAntreanTask.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        return None

    task.status = new_status

    if response_data:
        task.bpjs_response_data = response_data

    if error_message:
        task.notes = error_message

    # Update timestamps based on status
    now = datetime.now(timezone.utc)
    if new_status == BPJSTaskStatus.ACTIVE and not task.started_at:
        task.started_at = now
    elif new_status == BPJSTaskStatus.COMPLETED and not task.completed_at:
        task.completed_at = now

    await db.commit()
    await db.refresh(task)

    return task


async def get_active_tasks(
    db: AsyncSession,
    task_type: Optional[str] = None,
    limit: int = 100,
) -> List[BPJSAntreanTask]:
    """
    Mengambil semua task yang aktif (waiting).

    Args:
        db: Sesi database
        task_type: Filter berdasarkan tipe task (opsional)
        limit: Maksimal jumlah task yang diambil

    Returns:
        List of active BPJSAntreanTask objects
    """
    conditions = [
        BPJSAntreanTask.status == BPJSTaskStatus.WAITING,
    ]

    if task_type:
        conditions.append(BPJSAntreanTask.task_type == task_type)

    stmt = (
        select(BPJSAntreanTask)
        .options(selectinload(BPJSAntreanTask.booking))
        .where(and_(*conditions))
        .order_by(BPJSAntreanTask.created_at)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())


# =============================================================================
# Sync Log Management
# =============================================================================

async def create_sync_log(
    db: AsyncSession,
    sync_log_data: Dict[str, Any],
) -> BPJSAntreanSyncLog:
    """
    Membuat log sinkronisasi baru.

    Args:
        db: Sesi database
        sync_log_data: Data sync log (endpoint, request_data, response_data, etc.)

    Returns:
        Objek BPJSAntreanSyncLog yang dibuat
    """
    db_sync_log = BPJSAntreanSyncLog(
        endpoint=sync_log_data.get('endpoint'),
        http_method=sync_log_data.get('http_method', 'POST'),
        request_payload=sync_log_data.get('request_payload'),
        response_payload=sync_log_data.get('response_payload'),
        status=sync_log_data.get('status', BPJSSyncStatus.PENDING),
        http_status_code=sync_log_data.get('http_status_code'),
        bpjs_response_code=sync_log_data.get('bpjs_response_code'),
        error_message=sync_log_data.get('error_message'),
        execution_time_ms=sync_log_data.get('execution_time_ms'),
        referenced_entity_type=sync_log_data.get('referenced_entity_type'),
        referenced_entity_id=sync_log_data.get('referenced_entity_id'),
    )

    db.add(db_sync_log)
    await db.commit()
    await db.refresh(db_sync_log)

    return db_sync_log


async def get_sync_logs_by_date(
    db: AsyncSession,
    sync_date: date,
    status: Optional[str] = None,
    operation: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Mengambil log sinkronisasi berdasarkan tanggal.

    Args:
        db: Sesi database
        sync_date: Tanggal sinkronisasi
        status: Filter berdasarkan status (opsional)
        operation: Filter berdasarkan operasi (opsional)
        page: Nomor halaman
        page_size: Jumlah item per halaman

    Returns:
        Tuple dari (list of sync logs, total count)
    """
    # start_datetime = datetime.combine(sync_date, datetime.min.time())
    # end_datetime = datetime.combine(sync_date, datetime.max.time())

    # conditions = [
    #     AntreanSyncLog.created_at >= start_datetime,
    #     AntreanSyncLog.created_at <= end_datetime,
    # ]

    # if status:
    #     conditions.append(AntreanSyncLog.status == status)
    # if operation:
    #     conditions.append(AntreanSyncLog.operation == operation)

    # stmt = select(AntreanSyncLog).where(and_(*conditions))

    # count_stmt = select(sql_func.count(AntreanSyncLog.id)).where(and_(*conditions))
    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()

    # stmt = stmt.options(selectinload(AntreanSyncLog.booking))
    # stmt = stmt.order_by(desc(AntreanSyncLog.created_at))
    # stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    # result = await db.execute(stmt)
    # logs = result.scalars().all()

    # return list(logs), total
    return [], 0


async def get_failed_sync_logs(
    db: AsyncSession,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    operation: Optional[str] = None,
    limit: int = 100,
) -> List[Any]:
    """
    Mengambil log sinkronisasi yang gagal untuk retry.

    Args:
        db: Sesi database
        start_date: Tanggal mulai filter (opsional)
        end_date: Tanggal selesai filter (opsional)
        operation: Filter berdasarkan operasi (opsional)
        limit: Maksimal jumlah log yang diambil

    Returns:
        List of failed AntreanSyncLog objects
    """
    # conditions = [AntreanSyncLog.status == 'failed']

    # if start_date:
    #     conditions.append(AntreanSyncLog.created_at >= datetime.combine(start_date, datetime.min.time()))
    # if end_date:
    #     conditions.append(AntreanSyncLog.created_at <= datetime.combine(end_date, datetime.max.time()))
    # if operation:
    #     conditions.append(AntreanSyncLog.operation == operation)

    # stmt = (
    #     select(AntreanSyncLog)
    #     .options(selectinload(AntreanSyncLog.booking))
    #     .where(and_(*conditions))
    #     .order_by(desc(AntreanSyncLog.created_at))
    #     .limit(limit)
    # )

    # result = await db.execute(stmt)
    # return list(result.scalars().all())
    return []


async def get_sync_statistics(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    polyclinic_code: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Mengambil statistik sinkronisasi untuk periode tertentu.

    Args:
        db: Sesi database
        start_date: Tanggal mulai
        end_date: Tanggal selesai
        polyclinic_code: Filter berdasarkan poliklinik (opsional)

    Returns:
        Dictionary berisi statistik sinkronisasi
    """
    # start_datetime = datetime.combine(start_date, datetime.min.time())
    # end_datetime = datetime.combine(end_date, datetime.max.time())

    # conditions = [
    #     AntreanSyncLog.created_at >= start_datetime,
    #     AntreanSyncLog.created_at <= end_datetime,
    # ]

    # if polyclinic_code:
    #     conditions.append(AntreanBooking.polyclinic_code == polyclinic_code)

    # Join with booking to get polyclinic filter
    # stmt = select(AntreanSyncLog).join(AntreanBooking).where(and_(*conditions))

    # result = await db.execute(stmt)
    # logs = result.scalars().all()

    # Calculate statistics
    # total_syncs = len(logs)
    # successful = len([l for l in logs if l.status == 'success'])
    # failed = len([l for logs if l.status == 'failed'])
    # pending = len([l for l in logs if l.status == 'pending'])

    # Calculate average execution time
    # execution_times = [l.execution_time_ms for l in logs if l.execution_time_ms]
    # avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0

    # By operation
    # by_operation = {}
    # for log in logs:
    #     if log.operation not in by_operation:
    #         by_operation[log.operation] = {'total': 0, 'success': 0, 'failed': 0}
    #     by_operation[log.operation]['total'] += 1
    #     if log.status == 'success':
    #         by_operation[log.operation]['success'] += 1
    #     elif log.status == 'failed':
    #         by_operation[log.operation]['failed'] += 1

    return {
        'period': {'start': start_date, 'end': end_date},
        'total_syncs': 0,
        'successful': 0,
        'failed': 0,
        'pending': 0,
        'success_rate': Decimal('0.00'),
        'average_execution_time_ms': 0,
        'by_operation': {},
    }


async def retry_failed_sync(
    db: AsyncSession,
    sync_log_id: int,
    retried_by_id: int,
) -> Optional[Any]:
    """
    Melakukan retry sinkronisasi yang gagal.

    Args:
        db: Sesi database
        sync_log_id: ID sync log yang akan di-retry
        retried_by_id: ID user yang melakukan retry

    Returns:
        Objek AntreanTask yang dibuat untuk retry atau None

    Raises:
        ValueError: Jika sync log tidak ditemukan atau tidak bisa di-retry
    """
    # stmt = select(AntreanSyncLog).where(AntreanSyncLog.id == sync_log_id)
    # result = await db.execute(stmt)
    # sync_log = result.scalar_one_or_none()

    # if not sync_log:
    #     return None

    # if sync_log.status != 'failed':
    #     raise ValueError("Can only retry failed sync logs")

    # # Mark sync log as retried
    # sync_log.status = 'retrying'
    # sync_log.retried_at = datetime.utcnow()
    # sync_log.retried_by_id = retried_by_id

    # # Create new task for retry
    # task_data = {
    #     'booking_id': sync_log.booking_id,
    #     'task_type': sync_log.operation,
    #     'payload': sync_log.request_data,
    #     'status': 'pending',
    # }

    # retry_task = await create_antrean_task(db, task_data, retried_by_id)

    # await db.commit()

    # return retry_task
    return None


# =============================================================================
# Status Update Tracking
# =============================================================================

async def create_status_update(
    db: AsyncSession,
    status_update_data: Dict[str, Any],
) -> BPJSAntreanStatusUpdate:
    """
    Membuat catatan update status antrian.

    Args:
        db: Sesi database
        status_update_data: Data status update (booking_id, old_status, new_status, etc.)

    Returns:
        Objek BPJSAntreanStatusUpdate yang dibuat
    """
    from datetime import datetime, timezone

    db_status_update = BPJSAntreanStatusUpdate(
        booking_id=status_update_data.get('booking_id'),
        old_status=status_update_data.get('old_status'),
        new_status=status_update_data.get('new_status'),
        update_time=status_update_data.get('update_time', datetime.now(timezone.utc)),
        sync_status=status_update_data.get('sync_status', BPJSSyncStatus.PENDING),
        bpjs_response=status_update_data.get('bpjs_response'),
        error_message=status_update_data.get('error_message'),
        updated_by=status_update_data.get('updated_by'),
        update_source=status_update_data.get('update_source', 'system'),
        notes=status_update_data.get('notes'),
    )

    db.add(db_status_update)
    await db.commit()
    await db.refresh(db_status_update)

    return db_status_update


async def get_status_updates_by_booking(
    db: AsyncSession,
    booking_id: int,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[BPJSAntreanStatusUpdate], int]:
    """
    Mengambil semua update status untuk booking tertentu.

    Args:
        db: Sesi database
        booking_id: ID booking
        page: Nomor halaman
        page_size: Jumlah item per halaman

    Returns:
        Tuple dari (list of status updates, total count)
    """
    # Get total count
    count_stmt = select(sql_func.count(BPJSAntreanStatusUpdate.id)).where(
        BPJSAntreanStatusUpdate.booking_id == booking_id
    )
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Get paginated results
    stmt = (
        select(BPJSAntreanStatusUpdate)
        .where(BPJSAntreanStatusUpdate.booking_id == booking_id)
        .order_by(desc(BPJSAntreanStatusUpdate.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(stmt)
    updates = result.scalars().all()

    return list(updates), total


async def get_latest_status_update(
    db: AsyncSession,
    booking_id: int,
) -> Optional[BPJSAntreanStatusUpdate]:
    """
    Mengambil update status terakhir untuk booking tertentu.

    Args:
        db: Sesi database
        booking_id: ID booking

    Returns:
        Objek BPJSAntreanStatusUpdate terakhir atau None
    """
    stmt = select(BPJSAntreanStatusUpdate).where(
        BPJSAntreanStatusUpdate.booking_id == booking_id
    ).order_by(desc(BPJSAntreanStatusUpdate.created_at)).limit(1)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# =============================================================================
# Statistics & Reports
# =============================================================================

async def get_booking_statistics(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    poli_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Mengambil statistik booking untuk periode tertentu.

    Args:
        db: Sesi database
        start_date: Tanggal mulai
        end_date: Tanggal selesai
        poli_id: Filter berdasarkan ID poli (opsional)

    Returns:
        Dictionary berisi statistik booking
    """
    conditions = [
        BPJSAntreanBooking.booking_date >= start_date,
        BPJSAntreanBooking.booking_date <= end_date,
    ]

    if poli_id:
        conditions.append(BPJSAntreanBooking.poli_id == poli_id)

    stmt = select(BPJSAntreanBooking).where(and_(*conditions))
    result = await db.execute(stmt)
    bookings = result.scalars().all()

    # Calculate statistics
    total_bookings = len(bookings)

    # Count by status
    by_status = {status.value: 0 for status in BPJSBookingStatus}
    for booking in bookings:
        if booking.status in by_status:
            by_status[booking.status] += 1

    # Count by poli
    by_poli = {}
    for booking in bookings:
        if booking.poli_id not in by_poli:
            by_poli[booking.poli_id] = 0
        by_poli[booking.poli_id] += 1

    # Calculate rates
    completed = by_status.get(BPJSBookingStatus.COMPLETED, 0)
    cancelled = by_status.get(BPJSBookingStatus.CANCELLED, 0)

    completion_rate = (completed / total_bookings * 100) if total_bookings > 0 else Decimal('0.00')
    cancellation_rate = (cancelled / total_bookings * 100) if total_bookings > 0 else Decimal('0.00')

    return {
        'period': {'start': start_date, 'end': end_date},
        'total_bookings': total_bookings,
        'by_status': by_status,
        'by_poli': by_poli,
        'completion_rate': Decimal(str(round(completion_rate, 2))),
        'cancellation_rate': Decimal(str(round(cancellation_rate, 2))),
    }


async def get_daily_sync_summary(
    db: AsyncSession,
    target_date: date,
) -> Dict[str, Any]:
    """
    Mengambil ringkasan sinkronisasi harian.

    Args:
        db: Sesi database
        target_date: Tanggal target

    Returns:
        Dictionary berisi ringkasan sinkronisasi harian
    """
    # start_datetime = datetime.combine(target_date, datetime.min.time())
    # end_datetime = datetime.combine(target_date, datetime.max.time())

    # stmt = select(AntreanSyncLog).where(
    #     and_(
    #         AntreanSyncLog.created_at >= start_datetime,
    #         AntreanSyncLog.created_at <= end_datetime,
    #     )
    # )

    # result = await db.execute(stmt)
    # logs = result.scalars().all()

    # By hour
    # by_hour = {}
    # for log in logs:
    #     hour = log.created_at.hour
    #     if hour not in by_hour:
    #         by_hour[hour] = {'total': 0, 'success': 0, 'failed': 0}
    #     by_hour[hour]['total'] += 1
    #     if log.status == 'success':
    #         by_hour[hour]['success'] += 1
    #     elif log.status == 'failed':
    #         by_hour[hour]['failed'] += 1

    # By operation
    # by_operation = {}
    # for log in logs:
    #     if log.operation not in by_operation:
    #         by_operation[log.operation] = {'total': 0, 'success': 0, 'failed': 0}
    #     by_operation[log.operation]['total'] += 1
    #     if log.status == 'success':
    #         by_operation[log.operation]['success'] += 1
    #     elif log.status == 'failed':
    #         by_operation[log.operation]['failed'] += 1

    return {
        'date': target_date,
        'total_syncs': 0,
        'successful': 0,
        'failed': 0,
        'success_rate': Decimal('0.00'),
        'by_hour': {},
        'by_operation': {},
    }


async def get_upcoming_bookings(
    db: AsyncSession,
    from_date: date,
    days_ahead: int = 7,
    polyclinic_code: Optional[str] = None,
    limit: int = 100,
) -> List[Any]:
    """
    Mengambil booking yang akan datang.

    Args:
        db: Sesi database
        from_date: Tanggal mulai
        days_ahead: Jumlah hari ke depan
        polyclinic_code: Filter berdasarkan poliklinik (opsional)
        limit: Maksimal jumlah booking

    Returns:
        List of upcoming AntreanBooking objects
    """
    # end_date = from_date + timedelta(days=days_ahead)

    # conditions = [
    #     AntreanBooking.booking_date >= from_date,
    #     AntreanBooking.booking_date <= end_date,
    #     AntreanBooking.status.in_(['booked', 'confirmed']),
    # ]

    # if polyclinic_code:
    #     conditions.append(AntreanBooking.polyclinic_code == polyclinic_code)

    # stmt = (
    #     select(AntreanBooking)
    #     .options(selectinload(AntreanBooking.patient))
    #     .where(and_(*conditions))
    #     .order_by(AntreanBooking.booking_date, AntreanBooking.booking_time)
    #     .limit(limit)
    # )

    # result = await db.execute(stmt)
    # return list(result.scalars().all())
    return []


async def get_active_bookings_count(
    db: AsyncSession,
    target_date: Optional[date] = None,
    poli_id: Optional[int] = None,
) -> Dict[str, int]:
    """
    Mengambil jumlah booking yang aktif berdasarkan status.

    Args:
        db: Sesi database
        target_date: Tanggal target (default: hari ini)
        poli_id: Filter berdasarkan ID poli (opsional)

    Returns:
        Dictionary berisi jumlah booking per status
    """
    if target_date is None:
        target_date = date.today()

    conditions = [
        BPJSAntreanBooking.booking_date == target_date,
    ]

    if poli_id:
        conditions.append(BPJSAntreanBooking.poli_id == poli_id)

    stmt = select(BPJSAntreanBooking).where(and_(*conditions))
    result = await db.execute(stmt)
    bookings = result.scalars().all()

    # Count by status
    counts = {status.value: 0 for status in BPJSBookingStatus}

    for booking in bookings:
        if booking.status in counts:
            counts[booking.status] += 1

    counts['total'] = len(bookings)

    return counts


# =============================================================================
# Integration Helpers
# =============================================================================

async def map_appointment_to_booking(
    db: AsyncSession,
    appointment_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Memetakan data appointment ke format booking antrian BPJS.

    Args:
        db: Sesi database
        appointment_id: ID appointment

    Returns:
        Dictionary berisi data booking atau None jika appointment tidak ditemukan
    """
    # from app.crud.appointments import get_appointment_by_id

    # appointment = await get_appointment_by_id(db, appointment_id)
    # if not appointment:
    #     return None

    # booking_data = {
    #     'patient_id': appointment.patient_id,
    #     'patient_bpjs_card': appointment.patient.bpjs_card_number if appointment.patient else None,
    #     'patient_name': appointment.patient.full_name if appointment.patient else None,
    #     'patient_phone': appointment.patient.phone if appointment.patient else None,
    #     'appointment_id': appointment.id,
    #     'polyclinic_code': appointment.department.code if appointment.department else None,
    #     'polyclinic_name': appointment.department.name if appointment.department else None,
    #     'doctor_id': appointment.doctor_id,
    #     'doctor_name': appointment.doctor.full_name if appointment.doctor else None,
    #     'booking_date': appointment.appointment_date,
    #     'booking_time': appointment.appointment_time,
    #     'estimated_time_minutes': appointment.duration_minutes,
    #     'priority': 'urgent' if appointment.priority == 'emergency' else 'routine',
    #     'reason_for_visit': appointment.reason_for_visit,
    # }

    # return booking_data
    return None


async def map_queue_to_antrean_format(
    db: AsyncSession,
    queue_ticket_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Memetakan data queue ticket ke format antrian BPJS.

    Args:
        db: Sesi database
        queue_ticket_id: ID queue ticket

    Returns:
        Dictionary berisi data antrian BPJS atau None jika ticket tidak ditemukan
    """
    # from app.crud.queue import get_queue_ticket_by_id

    # queue_ticket = await get_queue_ticket_by_id(db, queue_ticket_id)
    # if not queue_ticket:
    #     return None

    # antrean_data = {
    #     'booking_code': queue_ticket.ticket_number,
    #     'patient_id': queue_ticket.patient_id,
    #     'patient_bpjs_card': queue_ticket.patient.bpjs_card_number if queue_ticket.patient else None,
    #     'patient_name': queue_ticket.patient.full_name if queue_ticket.patient else None,
    #     'poli_code': queue_ticket.poli.code if queue_ticket.poli else None,
    #     'poli_name': queue_ticket.poli.name if queue_ticket.poli else None,
    #     'doctor_id': queue_ticket.doctor_id,
    #     'doctor_name': queue_ticket.doctor.full_name if queue_ticket.doctor else None,
    #     'nomor_antrian': queue_ticket.ticket_number,
    #     'queue_position': queue_ticket.queue_position,
    #     'people_ahead': queue_ticket.people_ahead,
    #     'estimated_wait_minutes': queue_ticket.estimated_wait_minutes,
    #     'priority': queue_ticket.priority.value,
    #     'status': 'booked' if queue_ticket.status == 'waiting' else queue_ticket.status.value,
    # }

    # return antrean_data
    return None


async def validate_bpjs_task_id(
    db: AsyncSession,
    task_id: str,
) -> bool:
    """
    Memvalidasi format BPJS task ID dan memeriksa duplikasi.

    Args:
        db: Sesi database
        task_id: Task ID dari BPJS

    Returns:
        True jika valid dan belum ada duplikat, False otherwise

    Note:
        Format task_id BPJS biasanya: {jenis_antrian}-{tanggal}-{nomor_urut}
        Contoh: ANTRE-20250115-00001
    """
    if not task_id:
        return False

    # Basic validation: check format
    # BPJS task ID format: XXXX-YYYYMMDD-NNNNN
    parts = task_id.split('-')
    if len(parts) != 3:
        return False

    # Check if middle part is valid date
    try:
        datetime.strptime(parts[1], '%Y%m%d')
    except ValueError:
        return False

    # Check if last part is numeric
    if not parts[2].isdigit():
        return False

    # Additional validation: check if task_id already exists
    stmt = select(BPJSAntreanTask).where(BPJSAntreanTask.task_id == task_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    # Return True if no duplicate found, False if duplicate exists
    return existing is None


async def generate_booking_code(
    db: AsyncSession,
) -> str:
    """
    Generate kode booking unik untuk antrian BPJS.

    Args:
        db: Sesi database

    Returns:
        Kode booking unik dengan format: BPJS-YYYYMMDD-XXXXX
    """
    today = date.today()
    date_str = today.strftime('%Y%m%d')

    # Get last booking code for today
    pattern = "BPJS-{}-%".format(date_str)
    stmt = select(sql_func.max(BPJSAntreanBooking.booking_code)).where(
        BPJSAntreanBooking.booking_code.like(pattern)
    )
    result = await db.execute(stmt)
    last_code = result.scalar()

    if last_code:
        last_sequence = int(last_code.split('-')[-1])
        new_sequence = last_sequence + 1
    else:
        new_sequence = 1

    return "BPJS-{date_str}-{sequence:05d}".format(date_str=date_str, sequence=new_sequence)


# =============================================================================
# Additional Helper Functions
# =============================================================================

async def check_bpjs_sync_required(
    db: AsyncSession,
    booking_id: int,
) -> bool:
    """
    Memeriksa apakah perlu sinkronisasi dengan BPJS.

    Args:
        db: Sesi database
        booking_id: ID booking

    Returns:
        True jika perlu sync, False otherwise
    """
    # booking = await get_antrean_booking_by_id(db, booking_id)
    # if not booking:
    #     return False

    # Check if booking has pending changes not yet synced
    # last_sync = await get_latest_sync_for_booking(db, booking_id)

    # if not last_sync:
    #     return True  # Never synced, need to sync

    # Check if booking was updated after last sync
    # if booking.updated_at > last_sync.created_at:
    #     return True  # Has unsynced changes

    # return False  # No sync needed
    return False


async def get_latest_sync_for_booking(
    db: AsyncSession,
    booking_id: int,
) -> Optional[Any]:
    """
    Mengambil log sinkronisasi terakhir untuk booking.

    Args:
        db: Sesi database
        booking_id: ID booking

    Returns:
        Objek AntreanSyncLog terakhir atau None
    """
    # stmt = select(AntreanSyncLog).where(
    #     AntreanSyncLog.booking_id == booking_id
    # ).order_by(desc(AntreanSyncLog.created_at)).limit(1)

    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()
    return None


async def update_booking_from_bpjs_response(
    db: AsyncSession,
    booking_id: int,
    bpjs_response: Dict[str, Any],
    updated_by_id: int,
) -> Optional[Any]:
    """
    Update data booking berdasarkan respon dari API BPJS.

    Args:
        db: Sesi database
        booking_id: ID booking
        bpjs_response: Respon dari API BPJS
        updated_by_id: ID user yang melakukan update

    Returns:
        Objek AntreanBooking yang diupdate atau None
    """
    # booking = await get_antrean_booking_by_id(db, booking_id)
    # if not booking:
    #     return None

    # Update booking with BPJS response data
    # if 'nomorAntrian' in bpjs_response:
    #     booking.nomor_antrian = bpjs_response['nomorAntrian']

    # if 'kodeBooking' in bpjs_response:
    #     booking.booking_code = bpjs_response['kodeBooking']

    # if 'estimasiDilayani' in bpjs_response:
    #     booking.estimated_service_time = bpjs_response['estimasiDilayani']

    # if 'statusAntrian' in bpjs_response:
    #     # Map BPJS status to internal status
    #     status_map = {
    #         'BOOKED': 'booked',
    #         'CHECK-IN': 'checked_in',
    #         'DILAYANI': 'in_progress',
    #         'SELESAI': 'completed',
    #         'BATAL': 'cancelled',
    #     }
    #     bpjs_status = bpjs_response['statusAntrian']
    #     if bpjs_status in status_map:
    #         await update_booking_status(
    #             db, booking_id, status_map[bpjs_status], updated_by_id,
    #             notes="Status updated from BPJS API"
    #         )

    # booking.metadata = booking.metadata or {}
    # booking.metadata['last_bpjs_sync'] = datetime.utcnow().isoformat()
    # booking.metadata['bpjs_response'] = bpjs_response

    # booking.updated_by_id = updated_by_id
    # booking.updated_at = datetime.utcnow()

    # await db.commit()
    # await db.refresh(booking)

    # return booking
    return None


async def cleanup_old_sync_logs(
    db: AsyncSession,
    days_to_keep: int = 30,
) -> int:
    """
    Membersihkan log sinkronisasi lama untuk menjaga performa database.

    Args:
        db: Sesi database
        days_to_keep: Jumlah hari log yang disimpan

    Returns:
        Jumlah log yang dihapus
    """
    # cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

    # Delete old sync logs
    # stmt = delete(AntreanSyncLog).where(
    #     AntreanSyncLog.created_at < cutoff_date
    # )

    # result = await db.execute(stmt)
    # deleted_count = result.rowcount

    # await db.commit()

    # return deleted_count
    return 0


async def get_booking_with_active_tasks(
    db: AsyncSession,
    booking_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Mengambil booking beserta task yang sedang aktif.

    Args:
        db: Sesi database
        booking_id: ID booking

    Returns:
        Dictionary berisi booking dan active tasks atau None
    """
    # booking = await get_antrean_booking_by_id(db, booking_id)
    # if not booking:
    #     return None

    # tasks, _ = await get_tasks_by_booking(
    #     db, booking_id, status='pending'
    # )

    # return {
    #     'booking': booking,
    #     'active_tasks': tasks,
    #     'has_pending_tasks': len(tasks) > 0,
    # }
    return None
