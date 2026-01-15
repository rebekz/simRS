"""Patient Portal Messaging Service

Service layer for patient portal messaging functionality.
STORY-049: Communication Center
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import Optional, List, Tuple

from app.models.patient_portal import PatientPortalUser
from app.models.patient_portal_messaging import MessageThread, Message, MessageReadReceipt
from app.schemas.patient_portal.messaging import (
    MessageThreadSummary,
    MessageThreadList,
    MessageThreadResponse,
    MessageDetail,
    SendMessageRequest,
    SendMessageResponse,
    MarkAsReadResponse,
    StarThreadResponse,
    ArchiveThreadResponse,
    UnreadCountResponse,
    MessageCategory,
    RecipientRole,
    SenderType,
)


class MessagingService:
    """Service for managing patient portal messaging"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_message_threads(
        self,
        portal_user_id: int,
        is_archived: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> MessageThreadList:
        """List message threads for a patient

        Args:
            portal_user_id: The patient portal user ID
            is_archived: Filter by archived status
            limit: Maximum number of threads to return
            offset: Number of threads to skip

        Returns:
            MessageThreadList with threads and metadata
        """
        # Get total count
        count_query = select(func.count(MessageThread.id)).where(
            and_(
                MessageThread.patient_portal_user_id == portal_user_id,
                MessageThread.is_archived == is_archived
            )
        )
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar() or 0

        # Get threads with last message info
        query = (
            select(MessageThread)
            .where(
                and_(
                    MessageThread.patient_portal_user_id == portal_user_id,
                    MessageThread.is_archived == is_archived
                )
            )
            .order_by(MessageThread.last_message_at.desc().nullsfirst())
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(query)
        threads = result.scalars().all()

        # Get unread count
        unread_result = await self.db.execute(
            select(func.count(Message.id))
            .join(MessageThread)
            .where(
                and_(
                    MessageThread.patient_portal_user_id == portal_user_id,
                    Message.is_read == False,
                    Message.sender_type == "provider"
                )
            )
        )
        unread_count = unread_result.scalar() or 0

        # Build thread summaries
        thread_summaries = []
        for thread in threads:
            # Get last message for preview
            last_msg_query = (
                select(Message)
                .where(Message.thread_id == thread.id)
                .order_by(Message.created_at.desc())
                .limit(1)
            )
            last_msg_result = await self.db.execute(last_msg_query)
            last_message = last_msg_result.scalar_one_or_none()

            # Count unread messages in this thread
            thread_unread_result = await self.db.execute(
                select(func.count(Message.id))
                .where(
                    and_(
                        Message.thread_id == thread.id,
                        Message.is_read == False,
                        Message.sender_type == "provider"
                    )
                )
            )
            thread_unread = thread_unread_result.scalar() or 0

            summary = MessageThreadSummary(
                id=thread.id,
                subject=thread.subject,
                category=MessageCategory(thread.category),
                recipient_name=thread.recipient_name,
                recipient_role=RecipientRole(thread.recipient_role),
                last_message_preview=last_message.content[:100] + "..." if last_message and len(last_message.content) > 100 else (last_message.content if last_message else "No messages"),
                last_message_at=thread.last_message_at,
                last_message_sender_type=SenderType(last_message.sender_type) if last_message else None,
                status=thread.status,
                is_starred=thread.is_starred,
                is_archived=thread.is_archived,
                unread_count=thread_unread,
                created_at=thread.created_at,
                updated_at=thread.updated_at,
            )
            thread_summaries.append(summary)

        return MessageThreadList(
            threads=thread_summaries,
            total_count=total_count,
            unread_count=unread_count,
        )

    async def get_message_thread(
        self,
        thread_id: int,
        portal_user_id: int
    ) -> MessageThreadResponse:
        """Get a complete message thread with all messages

        Args:
            thread_id: The thread ID
            portal_user_id: The patient portal user ID

        Returns:
            MessageThreadResponse with thread details and all messages

        Raises:
            ValueError: If thread not found or doesn't belong to user
        """
        # Get thread with messages
        result = await self.db.execute(
            select(MessageThread)
            .where(
                and_(
                    MessageThread.id == thread_id,
                    MessageThread.patient_portal_user_id == portal_user_id
                )
            )
        )
        thread = result.scalar_one_or_none()

        if not thread:
            raise ValueError("Message thread not found")

        # Get all messages for the thread
        messages_result = await self.db.execute(
            select(Message)
            .where(Message.thread_id == thread_id)
            .order_by(Message.created_at.asc())
        )
        messages = messages_result.scalars().all()

        # Mark unread provider messages as read
        unread_provider_messages = [m for m in messages if not m.is_read and m.sender_type == "provider"]
        if unread_provider_messages:
            for msg in unread_provider_messages:
                msg.is_read = True
                msg.read_at = datetime.utcnow()
            await self.db.commit()

        # Build message details
        message_details = [
            MessageDetail(
                id=msg.id,
                sender_type=SenderType(msg.sender_type),
                sender_id=msg.sender_id,
                sender_name=msg.sender_name,
                content=msg.content,
                attachments=msg.attachments,
                is_read=msg.is_read,
                read_at=msg.read_at,
                is_delivered=msg.is_delivered,
                delivered_at=msg.delivered_at,
                created_at=msg.created_at,
            )
            for msg in messages
        ]

        return MessageThreadResponse(
            id=thread.id,
            subject=thread.subject,
            category=MessageCategory(thread.category),
            recipient_id=thread.recipient_id,
            recipient_name=thread.recipient_name,
            recipient_role=RecipientRole(thread.recipient_role),
            status=thread.status,
            is_starred=thread.is_starred,
            is_archived=thread.is_archived,
            messages=message_details,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
            last_message_at=thread.last_message_at,
        )

    async def send_message(
        self,
        portal_user_id: int,
        request: SendMessageRequest
    ) -> SendMessageResponse:
        """Send a new message or create a new thread

        Args:
            portal_user_id: The patient portal user ID
            request: The send message request

        Returns:
            SendMessageResponse with thread_id and message_id

        Raises:
            ValueError: If validation fails
        """
        portal_user = await self.db.get(PatientPortalUser, portal_user_id)
        if not portal_user or not portal_user.patient_id:
            raise ValueError("Invalid patient portal user")

        thread = None
        is_new_thread = False

        if request.thread_id:
            # Reply to existing thread
            result = await self.db.execute(
                select(MessageThread).where(
                    and_(
                        MessageThread.id == request.thread_id,
                        MessageThread.patient_portal_user_id == portal_user_id
                    )
                )
            )
            thread = result.scalar_one_or_none()

            if not thread:
                raise ValueError("Message thread not found")
        else:
            # Create new thread
            if not request.subject:
                raise ValueError("Subject is required for new message threads")

            thread = MessageThread(
                patient_portal_user_id=portal_user_id,
                subject=request.subject,
                category=request.category.value,
                recipient_id=request.recipient_id,
                recipient_name=request.recipient_name,
                recipient_role=request.recipient_role.value,
                status="active",
            )
            self.db.add(thread)
            await self.db.flush()  # Get the thread ID
            is_new_thread = True

        # Create the message
        message = Message(
            thread_id=thread.id,
            sender_type="patient",
            sender_id=portal_user_id,
            sender_name=portal_user.patient.full_name if portal_user.patient else "Patient",
            content=request.content,
            attachments=[a.model_dump() for a in request.attachments] if request.attachments else None,
            is_delivered=False,
        )
        self.db.add(message)

        # Update thread
        thread.last_message_at = datetime.utcnow()
        thread.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(message)

        return SendMessageResponse(
            thread_id=thread.id,
            message_id=message.id,
            is_new_thread=is_new_thread,
            message="Message sent successfully",
        )

    async def mark_messages_as_read(
        self,
        portal_user_id: int,
        message_ids: List[int]
    ) -> MarkAsReadResponse:
        """Mark specific messages as read

        Args:
            portal_user_id: The patient portal user ID
            message_ids: List of message IDs to mark as read

        Returns:
            MarkAsReadResponse with count of marked messages
        """
        # Get messages that belong to user's threads
        result = await self.db.execute(
            select(Message)
            .join(MessageThread)
            .where(
                and_(
                    Message.id.in_(message_ids),
                    MessageThread.patient_portal_user_id == portal_user_id,
                    Message.is_read == False
                )
            )
        )
        messages = result.scalars().all()

        marked_count = 0
        for message in messages:
            message.is_read = True
            message.read_at = datetime.utcnow()
            marked_count += 1

        await self.db.commit()

        return MarkAsReadResponse(
            marked_count=marked_count,
            message=f"Marked {marked_count} messages as read",
        )

    async def star_thread(
        self,
        thread_id: int,
        portal_user_id: int,
        is_starred: bool
    ) -> StarThreadResponse:
        """Star or unstar a message thread

        Args:
            thread_id: The thread ID
            portal_user_id: The patient portal user ID
            is_starred: True to star, False to unstar

        Returns:
            StarThreadResponse

        Raises:
            ValueError: If thread not found or doesn't belong to user
        """
        result = await self.db.execute(
            select(MessageThread).where(
                and_(
                    MessageThread.id == thread_id,
                    MessageThread.patient_portal_user_id == portal_user_id
                )
            )
        )
        thread = result.scalar_one_or_none()

        if not thread:
            raise ValueError("Message thread not found")

        thread.is_starred = is_starred
        await self.db.commit()

        action = "starred" if is_starred else "unstarred"

        return StarThreadResponse(
            thread_id=thread.id,
            is_starred=is_starred,
            message=f"Thread {action} successfully",
        )

    async def archive_thread(
        self,
        thread_id: int,
        portal_user_id: int,
        is_archived: bool
    ) -> ArchiveThreadResponse:
        """Archive or unarchive a message thread

        Args:
            thread_id: The thread ID
            portal_user_id: The patient portal user ID
            is_archived: True to archive, False to unarchive

        Returns:
            ArchiveThreadResponse

        Raises:
            ValueError: If thread not found or doesn't belong to user
        """
        result = await self.db.execute(
            select(MessageThread).where(
                and_(
                    MessageThread.id == thread_id,
                    MessageThread.patient_portal_user_id == portal_user_id
                )
            )
        )
        thread = result.scalar_one_or_none()

        if not thread:
            raise ValueError("Message thread not found")

        thread.is_archived = is_archived
        await self.db.commit()

        action = "archived" if is_archived else "unarchived"

        return ArchiveThreadResponse(
            thread_id=thread.id,
            is_archived=is_archived,
            message=f"Thread {action} successfully",
        )

    async def get_unread_count(
        self,
        portal_user_id: int
    ) -> UnreadCountResponse:
        """Get count of unread messages

        Args:
            portal_user_id: The patient portal user ID

        Returns:
            UnreadCountResponse with unread message counts
        """
        # Get total unread messages
        total_result = await self.db.execute(
            select(func.count(Message.id))
            .join(MessageThread)
            .where(
                and_(
                    MessageThread.patient_portal_user_id == portal_user_id,
                    Message.is_read == False,
                    Message.sender_type == "provider"
                )
            )
        )
        total_unread = total_result.scalar() or 0

        # Get threads with unread messages
        threads_result = await self.db.execute(
            select(func.count(func.distinct(Message.thread_id)))
            .join(MessageThread)
            .where(
                and_(
                    MessageThread.patient_portal_user_id == portal_user_id,
                    Message.is_read == False,
                    Message.sender_type == "provider"
                )
            )
        )
        threads_with_unread = threads_result.scalar() or 0

        return UnreadCountResponse(
            total_unread=total_unread,
            threads_with_unread=threads_with_unread,
        )
