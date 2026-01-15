"""Patient Portal Messaging Endpoints

API endpoints for secure messaging between patients and healthcare providers.
STORY-049: Communication Center
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.models.patient_portal import PatientPortalUser
from app.api.v1.endpoints.patient_portal_auth import get_current_portal_user
from app.schemas.patient_portal.messaging import (
    MessageThreadList,
    MessageThreadResponse,
    SendMessageRequest,
    SendMessageResponse,
    MarkAsReadRequest,
    MarkAsReadResponse,
    StarThreadRequest,
    StarThreadResponse,
    ArchiveThreadRequest,
    ArchiveThreadResponse,
    UnreadCountResponse,
)
from app.services.patient_portal.messaging_service import MessagingService

router = APIRouter()


@router.get("/messages/threads", response_model=MessageThreadList, operation_id="list_message_threads")
async def list_message_threads(
    is_archived: bool = Query(False, description="Filter by archived status"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of threads to return"),
    offset: int = Query(0, ge=0, description="Number of threads to skip"),
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's message threads with pagination

    Returns a paginated list of message threads for the authenticated patient.
    Threads are ordered by most recent message first.

    - **is_archived**: Filter to show only archived (True) or active (False) threads
    - **limit**: Maximum number of threads to return (1-100)
    - **offset**: Number of threads to skip for pagination

    Returns thread summaries including:
    - Thread subject and category
    - Recipient information
    - Last message preview
    - Unread message count
    - Starred and archived status
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = MessagingService(db)
    return await service.list_message_threads(
        portal_user_id=current_user.id,
        is_archived=is_archived,
        limit=limit,
        offset=offset,
    )


@router.get("/messages/threads/{thread_id}", response_model=MessageThreadResponse, operation_id="get_message_thread")
async def get_message_thread(
    thread_id: int,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get complete thread with all messages

    Retrieves a complete message thread with all messages in chronological order.
    Automatically marks unread provider messages as read when the patient views the thread.

    - **thread_id**: The unique identifier of the message thread

    Returns complete thread information including:
    - Thread metadata (subject, category, status)
    - All messages ordered by creation date
    - Message read/delivery status
    - Attachment information

    Raises:
    - 404: If thread not found or doesn't belong to the user
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = MessagingService(db)
    try:
        return await service.get_message_thread(thread_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/messages/send", response_model=SendMessageResponse, operation_id="send_message")
async def send_message(
    request: SendMessageRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a new message or create new thread

    Sends a new message. If thread_id is provided, adds a message to an existing thread.
    If thread_id is None, creates a new message thread.

    For new threads, the following fields are required:
    - **subject**: Thread subject line (3-255 characters)
    - **category**: Message category (medical_question, appointment_question, etc.)
    - **recipient_id**: User ID of the healthcare provider recipient
    - **recipient_name**: Name of the recipient
    - **recipient_role**: Role of the recipient (doctor, nurse, staff, etc.)

    For all messages:
    - **content**: Message content (1-5000 characters)
    - **attachments**: Optional list of file attachments (max 5)

    Returns the thread_id and message_id of the sent message.

    Raises:
    - 400: If validation fails or required fields are missing for new threads
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = MessagingService(db)
    try:
        return await service.send_message(current_user.id, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/messages/mark-read", operation_id="mark_messages_as_read")
async def mark_messages_as_read(
    request: MarkAsReadRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark specific messages as read

    Marks the specified messages as read. Only messages from providers
    can be marked as read by patients. Automatically updates the read_at timestamp.

    - **message_ids**: List of message IDs to mark as read

    Returns the count of messages that were successfully marked as read.

    Note: Messages are automatically marked as read when viewing a thread.
    This endpoint is useful for bulk marking messages as read without viewing.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = MessagingService(db)
    return await service.mark_messages_as_read(current_user.id, request.message_ids)


@router.post("/messages/threads/{thread_id}/star", operation_id="star_thread")
async def star_thread(
    thread_id: int,
    request: StarThreadRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Star or unstar a thread

    Stars or unstars a message thread for easy access to important conversations.
    Starred threads can be filtered and appear prominently in the thread list.

    - **thread_id**: The unique identifier of the message thread
    - **is_starred**: True to star the thread, False to unstar

    Returns the updated starred status of the thread.

    Raises:
    - 404: If thread not found or doesn't belong to the user
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = MessagingService(db)
    try:
        return await service.star_thread(thread_id, current_user.id, request.is_starred)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/messages/threads/{thread_id}/archive", operation_id="archive_thread")
async def archive_thread(
    thread_id: int,
    request: ArchiveThreadRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Archive or unarchive a thread

    Archives or unarchives a message thread. Archived threads are hidden from
    the default view but can still be accessed when filtering for archived threads.

    - **thread_id**: The unique identifier of the message thread
    - **is_archived**: True to archive the thread, False to unarchive

    Returns the updated archived status of the thread.

    Raises:
    - 404: If thread not found or doesn't belong to the user
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = MessagingService(db)
    try:
        return await service.archive_thread(thread_id, current_user.id, request.is_archived)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/messages/unread-count", operation_id="get_unread_count")
async def get_unread_count(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get count of unread messages

    Returns the total number of unread messages from healthcare providers
    and the number of threads that contain unread messages.

    Useful for displaying notification badges on messaging UI elements.

    Returns:
    - **total_unread**: Total count of unread messages across all threads
    - **threads_with_unread**: Number of threads that have at least one unread message

    Note: Only messages from providers (not from the patient) are counted as unread.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = MessagingService(db)
    return await service.get_unread_count(current_user.id)
