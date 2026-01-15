"""Notification Endpoints

API endpoints for notification system.
STORY-058: Notification System
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user
from app.schemas.notifications import (
    SendNotificationRequest,
    SendNotificationResponse,
    BulkSendRequest,
    BulkSendResponse,
    NotificationStatusResponse,
    NotificationHistoryResponse,
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplateResponse,
    TemplateListResponse,
    NotificationPreferenceRequest,
    NotificationPreferenceResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter()


@router.post("/notifications/send", response_model=SendNotificationResponse, operation_id="send_notification")
async def send_notification(
    request: SendNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a single notification

    Mengirim notifikasi tunggal kepada penerima melalui saluran yang ditentukan.
    Notifikasi dapat dikirim melalui email, SMS, WhatsApp, push notification, atau in-app.

    Field yang diperlukan:
    - **recipient_id**: ID user penerima notifikasi
    - **recipient_type**: Tipe penerima (patient, staff, dll.)
    - **channel**: Saluran notifikasi (email, sms, whatsapp, push, in_app)
    - **type**: Tipe notifikasi (appointment_reminder, prescription_ready, dll.)
    - **message**: Isi pesan notifikasi (mendukung placeholder variabel)

    Field opsional:
    - **subject**: Subjek notifikasi (untuk email/push)
    - **priority**: Prioritas notifikasi (low, normal, high, urgent)
    - **data**: Data tambahan untuk rendering template
    - **scheduled_for**: Jadwalkan pengiriman di masa depan

    Returns notification_id dari notifikasi yang dibuat.

    Raises:
    - 400: Jika validasi gagal atau penerima tidak ditemukan
    - 401: Jika tidak terautentikasi
    """
    service = NotificationService(db)
    try:
        result = await service.send_notification(current_user.id, request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/notifications/bulk", response_model=BulkSendResponse, operation_id="send_bulk_notifications")
async def send_bulk_notifications(
    request: BulkSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send bulk notifications to multiple recipients

    Mengirim notifikasi massal kepada banyak penerima sekaligus.
    Memerlukan role admin atau staff untuk mengirim bulk notifications.

    Field yang diperlukan:
    - **recipient_ids**: List ID user penerima (maksimal 1000 penerima)
    - **recipient_type**: Tipe penerima (patient, staff, dll.)
    - **channel**: Saluran notifikasi
    - **type**: Tipe notifikasi
    - **message**: Isi pesan notifikasi

    Field opsional:
    - **subject**: Subjek notifikasi
    - **priority**: Prioritas notifikasi
    - **data**: Data tambahan untuk template (sama untuk semua penerima)
    - **scheduled_for**: Jadwalkan pengiriman

    Returns daftar notification_ids dan jumlah sukses/gagal.

    Raises:
    - 400: Jika validasi gagal atau penerima tidak ditemukan
    - 401: Jika tidak terautentikasi
    - 403: Jika tidak memiliki izin (bukan admin/staff)
    """
    # Check role - admin or staff only
    if current_user.role.value not in ["admin", "doctor", "nurse", "receptionist", "support_staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin or staff role required.",
        )

    service = NotificationService(db)
    try:
        result = await service.send_bulk_notifications(current_user.id, request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/notifications/status/{notification_id}", response_model=NotificationStatusResponse, operation_id="get_notification_status")
async def get_notification_status(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get notification delivery status

    Mendapatkan status pengiriman notifikasi berdasarkan notification_id.
    Hanya user yang berhak dapat melihat status notifikasi.

    Returns detail status notifikasi:
    - **status**: Status saat ini (pending, sent, delivered, failed, cancelled)
    - **sent_at**: Waktu pengiriman
    - **delivered_at**: Waktu diterima
    - **failed_at**: Waktu gagal (jika applicable)
    - **failure_reason**: Alasan kegagalan (jika applicable)
    - **retry_count**: Jumlah percobaan ulang

    Raises:
    - 401: Jika tidak terautentikasi
    - 403: Jika tidak berhak melihat notifikasi
    - 404: Jika notifikasi tidak ditemukan
    """
    service = NotificationService(db)
    try:
        result = await service.get_notification_status(notification_id, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/notifications/history", response_model=NotificationHistoryResponse, operation_id="get_notification_history")
async def get_notification_history(
    page: int = Query(1, ge=1, description="Nomor halaman"),
    per_page: int = Query(20, ge=1, le=100, description="Jumlah item per halaman"),
    status_filter: Optional[str] = Query(None, description="Filter berdasarkan status"),
    type_filter: Optional[str] = Query(None, description="Filter berdasarkan tipe notifikasi"),
    start_date: Optional[datetime] = Query(None, description="Filter tanggal mulai"),
    end_date: Optional[datetime] = Query(None, description="Filter tanggal akhir"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get notification history

    Mendapatkan riwayat notifikasi untuk user yang sedang login.
    Mendukung pagination dan filtering.

    Query Parameters:
    - **page**: Nomor halaman (default: 1)
    - **per_page**: Jumlah item per halaman (default: 20, max: 100)
    - **status_filter**: Filter berdasarkan status (pending, sent, delivered, failed)
    - **type_filter**: Filter berdasarkan tipe notifikasi
    - **start_date**: Filter tanggal mulai (ISO 8601 format)
    - **end_date**: Filter tanggal akhir (ISO 8601 format)

    Returns:
    - **notifications**: List notifikasi dengan preview pesan
    - **total_count**: Total jumlah notifikasi
    - **page**: Nomor halaman saat ini
    - **per_page**: Jumlah per halaman
    - **statistics**: Statistik pengiriman (total_sent, total_delivered, total_failed, delivery_rate)

    Raises:
    - 401: Jika tidak terautentikasi
    """
    service = NotificationService(db)
    result = await service.get_notification_history(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        status=status_filter,
        notification_type=type_filter,
        start_date=start_date,
        end_date=end_date,
    )
    return result


@router.post("/notifications/templates", response_model=TemplateResponse, operation_id="create_template", status_code=status.HTTP_201_CREATED)
async def create_template(
    request: TemplateCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a notification template

    Membuat template notifikasi baru. Memerlukan role admin.
    Template digunakan untuk mengirim notifikasi dengan format yang konsisten.

    Field yang diperlukan:
    - **name**: Nama template (unik)
    - **category**: Kategori template (appointment, prescription, medical, billing, system, marketing)
    - **channel**: Saluran notifikasi
    - **type**: Tipe notifikasi
    - **message_template**: Template pesan dengan placeholder variabel
    - **variables**: List nama variabel yang digunakan dalam template

    Field opsional:
    - **language**: Bahasa template (default: id/Indonesian)
    - **subject_template**: Template subjek (untuk email/push)
    - **description**: Deskripsi template
    - **is_active**: Status aktif template (default: true)

    Contoh penggunaan placeholder:
    - "Halo {patient_name}, janji temu Anda pada {appointment_date} pukul {appointment_time}"

    Returns detail template yang dibuat.

    Raises:
    - 400: Jika validasi template gagal atau nama sudah ada
    - 401: Jika tidak terautentikasi
    - 403: Jika tidak memiliki izin (bukan admin)
    """
    # Check role - admin only
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required.",
        )

    service = NotificationService(db)
    try:
        result = await service.create_template(request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/notifications/templates", response_model=TemplateListResponse, operation_id="list_templates")
async def list_templates(
    category: Optional[str] = Query(None, description="Filter berdasarkan kategori"),
    status_filter: Optional[str] = Query(None, description="Filter berdasarkan status (active/inactive)"),
    language: Optional[str] = Query(None, description="Filter berdasarkan bahasa (id/en)"),
    page: int = Query(1, ge=1, description="Nomor halaman"),
    per_page: int = Query(20, ge=1, le=100, description="Jumlah item per halaman"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List notification templates

    Mendapatkan daftar template notifikasi dengan pagination dan filter.
    Memerlukan role admin atau staff.

    Query Parameters:
    - **category**: Filter kategori template (appointment, prescription, dll.)
    - **status_filter**: Filter status aktif (active/inactive)
    - **language**: Filter bahasa (id/en)
    - **page**: Nomor halaman (default: 1)
    - **per_page**: Jumlah per halaman (default: 20, max: 100)

    Returns:
    - **templates**: List template
    - **total_count**: Total jumlah template
    - **page**: Nomor halaman saat ini
    - **per_page**: Jumlah per halaman

    Raises:
    - 401: Jika tidak terautentikasi
    - 403: Jika tidak memiliki izin (bukan admin/staff)
    """
    # Check role - admin or staff only
    if current_user.role.value not in ["admin", "doctor", "nurse", "receptionist", "support_staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin or staff role required.",
        )

    service = NotificationService(db)
    result = await service.list_templates(
        category=category,
        template_status=status_filter,
        language=language,
        page=page,
        per_page=per_page,
    )
    return result


@router.get("/notifications/templates/{template_id}", response_model=TemplateResponse, operation_id="get_template")
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get template details

    Mendapatkan detail template berdasarkan template_id.
    Memerlukan role admin atau staff.

    Returns detail template lengkap termasuk:
    - Informasi template dasar (nama, kategori, bahasa)
    - Template pesan dan subjek
    - List variabel yang digunakan
    - Status aktif dan timestamps

    Raises:
    - 401: Jika tidak terautentikasi
    - 403: Jika tidak memiliki izin (bukan admin/staff)
    - 404: Jika template tidak ditemukan
    """
    # Check role - admin or staff only
    if current_user.role.value not in ["admin", "doctor", "nurse", "receptionist", "support_staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin or staff role required.",
        )

    service = NotificationService(db)
    try:
        result = await service.get_template(template_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/notifications/templates/{template_id}", response_model=TemplateResponse, operation_id="update_template")
async def update_template(
    template_id: int,
    request: TemplateUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a notification template

    Memperbarui template notifikasi yang sudah ada. Memerlukan role admin.
    Hanya field yang diberikan yang akan diperbarui (partial update).

    Field yang dapat diperbarui:
    - **name**: Nama template
    - **subject_template**: Template subjek
    - **message_template**: Template pesan
    - **variables**: List variabel
    - **description**: Deskripsi template
    - **is_active**: Status aktif

    Returns detail template yang diperbarui.

    Raises:
    - 400: Jika validasi template gagal
    - 401: Jika tidak terautentikasi
    - 403: Jika tidak memiliki izin (bukan admin)
    - 404: Jika template tidak ditemukan
    """
    # Check role - admin only
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required.",
        )

    service = NotificationService(db)
    try:
        result = await service.update_template(template_id, request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/notifications/preferences", response_model=NotificationPreferenceResponse, operation_id="get_notification_preferences")
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user notification preferences

    Mendapatkan preferensi notifikasi untuk user yang sedang login.
    Preferensi mencakup pengaturan channel, tipe notifikasi, dan jam tenang (quiet hours).

    Returns:
    - **preferences**: List preferensi notifikasi user
      - channel_preferences: Pengaturan per channel (email, sms, whatsapp, push, in_app)
      - type_preferences: Pengaturan per tipe notifikasi
      - quiet_hours_start: Jam mulai quiet hours
      - quiet_hours_end: Jam selesai quiet hours
      - timezone: Timezone user

    Raises:
    - 401: Jika tidak terautentikasi
    """
    service = NotificationService(db)
    # Placeholder - would fetch from database
    return {
        "preferences": [
            {
                "user_id": current_user.id,
                "setting_key": "channel_preferences",
                "setting_value": '{"email": true, "sms": false, "whatsapp": true, "push": true, "in_app": true}',
                "updated_at": datetime.utcnow(),
            }
        ]
    }


@router.put("/notifications/preferences", response_model=NotificationPreferenceResponse, operation_id="update_notification_preferences")
async def update_notification_preferences(
    request: NotificationPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update notification preferences

    Memperbarui preferensi notifikasi untuk user yang sedang login.
    User dapat mengatur channel notifikasi yang diinginkan dan jam tenang.

    Field yang diperlukan:
    - **channel_preferences**: Pengaturan per channel (dict dengan bool atau nested settings)
      Contoh: {"email": true, "sms": false, "whatsapp": true, "push": true, "in_app": true}

    Field opsional:
    - **type_preferences**: Pengaturan per tipe notifikasi
      Contoh: {"appointment_reminder": {"email": true, "whatsapp": true}, "marketing": false}
    - **quiet_hours_start**: Jam mulai quiet hours (HH:MM format)
    - **quiet_hours_end**: Jam selesai quiet hours (HH:MM format)
    - **timezone**: Timezone user (default: Asia/Jakarta)

    Returns preferensi yang diperbarui.

    Raises:
    - 400: Jika validasi gagal (format waktu salah, dll.)
    - 401: Jika tidak terautentikasi
    """
    service = NotificationService(db)
    result = await service.update_user_preferences(current_user.id, request)
    return {"preferences": result}


@router.post("/notifications/test", response_model=SendNotificationResponse, operation_id="test_notification")
async def test_notification(
    request: SendNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a test notification

    Mengirim notifikasi tes untuk memverifikasi konfigurasi dan format pesan.
    Notifikasi tes akan ditambahkan prefix [TEST] pada pesan.
    Memerlukan role admin.

    Ini berguna untuk:
    - Menguji template notifikasi baru
    - Memverifikasi format pesan
    - Mengecek konfigurasi channel notifikasi
    - Preview tampilan notifikasi

    Field sama dengan send_notification, tetapi pesan akan ditambahkan prefix [TEST].

    Returns notification_id dari notifikasi tes.

    Raises:
    - 400: Jika validasi gagal atau penerima tidak ditemukan
    - 401: Jika tidak terautentikasi
    - 403: Jika tidak memiliki izin (bukan admin)
    """
    # Check role - admin only
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required.",
        )

    service = NotificationService(db)
    try:
        result = await service.send_notification(current_user.id, request, is_test=True)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
