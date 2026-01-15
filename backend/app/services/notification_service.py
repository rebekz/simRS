"""Notification Service

Service layer for notification management across multiple channels.
Supports templates, user preferences, and delivery tracking.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, time
from typing import Optional, List, Dict, Any

from app.models.notifications import (
    Notification,
    NotificationTemplate,
    NotificationLog,
    NotificationPreference,
)
from app.models.user import User
from app.models.patient import Patient
from app.models.patient_portal import PatientPortalUser
from app.schemas.notifications import (
    SendNotificationRequest,
    SendNotificationResponse,
    BulkSendRequest,
    BulkSendResponse,
    NotificationDetail,
    NotificationStatusResponse,
    NotificationHistoryResponse,
    NotificationHistoryItem,
    NotificationStatus,
    NotificationChannel,
    NotificationType,
    NotificationPriority,
    TemplateCategory,
    TemplateLanguage,
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplateResponse,
    TemplateListResponse,
)


class NotificationService:
    """Service for managing notifications across multiple channels"""

    # Default channel preferences by notification type
    DEFAULT_PREFERENCES = {
        "appointment_reminder": {
            "email_enabled": True,
            "sms_enabled": True,
            "push_enabled": True,
            "in_app_enabled": True,
            "whatsapp_enabled": False,
        },
        "prescription_ready": {
            "email_enabled": True,
            "sms_enabled": True,
            "push_enabled": True,
            "in_app_enabled": True,
            "whatsapp_enabled": False,
        },
        "test_result": {
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": True,
            "in_app_enabled": True,
            "whatsapp_enabled": False,
        },
        "billing": {
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": True,
            "in_app_enabled": True,
            "whatsapp_enabled": False,
        },
        "system": {
            "email_enabled": False,
            "sms_enabled": False,
            "push_enabled": True,
            "in_app_enabled": True,
            "whatsapp_enabled": False,
        },
        "security": {
            "email_enabled": True,
            "sms_enabled": True,
            "push_enabled": True,
            "in_app_enabled": True,
            "whatsapp_enabled": False,
        },
        "message": {
            "email_enabled": False,
            "sms_enabled": False,
            "push_enabled": True,
            "in_app_enabled": True,
            "whatsapp_enabled": False,
        },
        "alert": {
            "email_enabled": True,
            "sms_enabled": True,
            "push_enabled": True,
            "in_app_enabled": True,
            "whatsapp_enabled": False,
        },
        "all": {
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": True,
            "in_app_enabled": True,
            "whatsapp_enabled": False,
        },
    }

    # Maximum retry attempts
    MAX_RETRIES = 3

    # Batch size for bulk operations
    BULK_BATCH_SIZE = 100

    def __init__(self, db: AsyncSession):
        self.db = db

    async def send_notification(
        self,
        request: SendNotificationRequest
    ) -> SendNotificationResponse:
        """Send a single notification

        Args:
            request: Send notification request with recipient, content, and delivery details

        Returns:
            SendNotificationResponse with notification_id

        Raises:
            ValueError: If validation fails
        """
        # Validate recipient exists
        await self._validate_recipient(request.recipient_id, request.recipient_type)

        # Create notification record
        notification = Notification(
            recipient_id=request.recipient_id,
            user_type=request.recipient_type,
            notification_type=request.type.value,
            channel=request.channel.value,
            priority=request.priority.value,
            status=NotificationStatus.PENDING.value,
            title=request.subject or "Notification",
            message=request.message,
            metadata=request.data,
            scheduled_at=request.scheduled_for or datetime.utcnow(),
        )

        self.db.add(notification)
        await self.db.flush()  # Get the notification ID

        # Queue for delivery (mock implementation)
        await self._queue_notification(notification)

        # Create log entry
        log = NotificationLog(
            notification_id=notification.id,
            status="queued",
            message="Notification queued for delivery"
        )
        self.db.add(log)

        await self.db.commit()

        return SendNotificationResponse(
            notification_id=notification.id,
            status=NotificationStatus.PENDING,
            message="Notification created and queued for delivery"
        )

    async def send_bulk_notifications(
        self,
        request: BulkSendRequest
    ) -> BulkSendResponse:
        """Send bulk notifications to multiple recipients

        Args:
            request: Bulk notification request with recipient list and content

        Returns:
            BulkSendResponse with notification_ids and failed count
        """
        notification_ids = []
        failed_count = 0

        # Process in batches
        for i in range(0, len(request.recipient_ids), self.BULK_BATCH_SIZE):
            batch = request.recipient_ids[i:i + self.BULK_BATCH_SIZE]

            for recipient_id in batch:
                try:
                    # Validate recipient
                    await self._validate_recipient(recipient_id, request.recipient_type)

                    # Create notification
                    notification = Notification(
                        recipient_id=recipient_id,
                        user_type=request.recipient_type,
                        notification_type=request.type.value,
                        channel=request.channel.value,
                        priority=request.priority.value,
                        status=NotificationStatus.PENDING.value,
                        title=request.subject or "Notification",
                        message=request.message,
                        metadata=request.data,
                        scheduled_at=request.scheduled_for or datetime.utcnow(),
                    )

                    self.db.add(notification)
                    await self.db.flush()

                    notification_ids.append(notification.id)

                    # Log
                    log = NotificationLog(
                        notification_id=notification.id,
                        status="queued",
                        message="Bulk notification queued for delivery"
                    )
                    self.db.add(log)

                except Exception:
                    failed_count += 1
                    # Log failure but continue processing
                    continue

            # Commit batch
            await self.db.commit()

        return BulkSendResponse(
            notification_ids=notification_ids,
            total_recipients=len(request.recipient_ids),
            successful_count=len(notification_ids),
            failed_count=failed_count,
            message="Bulk notifications queued"
        )

    async def get_notification_status(
        self,
        notification_id: int
    ) -> NotificationStatusResponse:
        """Get delivery status of a notification

        Args:
            notification_id: The notification ID

        Returns:
            NotificationStatusResponse with status and timestamps

        Raises:
            ValueError: If notification not found
        """
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if not notification:
            raise ValueError("Notification {notification_id} not found".format(notification_id=notification_id))

        return NotificationStatusResponse(
            notification_id=notification.id,
            status=NotificationStatus(notification.status),
            channel=NotificationChannel(notification.channel),
            type=NotificationType(notification.notification_type),
            recipient_id=notification.recipient_id,
            sent_at=notification.sent_at,
            delivered_at=notification.delivered_at,
            failed_at=notification.failed_at,
            failure_reason=notification.failed_reason,
            retry_count=notification.retry_count,
            created_at=notification.created_at,
        )

    async def get_notification_history(
        self,
        recipient_id: int,
        page: int = 1,
        per_page: int = 20,
        status: Optional[NotificationStatus] = None,
        notification_type: Optional[NotificationType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> NotificationHistoryResponse:
        """Get user's notification history

        Args:
            recipient_id: The recipient ID
            page: Page number (1-indexed)
            per_page: Items per page
            status: Optional filter by status
            notification_type: Optional filter by type
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            NotificationHistoryResponse with notifications and statistics
        """
        # Build query filters
        filters = [Notification.recipient_id == recipient_id]

        if status:
            filters.append(Notification.status == status.value)
        if notification_type:
            filters.append(Notification.notification_type == notification_type.value)
        if start_date:
            filters.append(Notification.created_at >= start_date)
        if end_date:
            filters.append(Notification.created_at <= end_date)

        # Get total count
        count_query = select(func.count(Notification.id)).where(and_(*filters))
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Get notifications with pagination
        offset = (page - 1) * per_page
        query = (
            select(Notification)
            .where(and_(*filters))
            .order_by(Notification.created_at.desc())
            .limit(per_page)
            .offset(offset)
        )
        result = await self.db.execute(query)
        notifications = result.scalars().all()

        # Build notification history items
        notification_items = [
            NotificationHistoryItem(
                notification_id=n.id,
                channel=NotificationChannel(n.channel),
                type=NotificationType(n.notification_type),
                status=NotificationStatus(n.status),
                priority=NotificationPriority(n.priority),
                subject=n.title,
                message_preview=n.message[:100] + "..." if len(n.message) > 100 else n.message,
                sent_at=n.sent_at,
                delivered_at=n.delivered_at,
                created_at=n.created_at,
            )
            for n in notifications
        ]

        # Calculate statistics
        stats_query = select(
            Notification.status,
            func.count(Notification.id)
        ).where(
            Notification.recipient_id == recipient_id
        ).group_by(Notification.status)

        stats_result = await self.db.execute(stats_query)
        statistics = {status: count for status, count in stats_result.all()}

        return NotificationHistoryResponse(
            notifications=notification_items,
            total_count=total_count,
            page=page,
            per_page=per_page,
            statistics=statistics,
        )

    async def mark_as_delivered(
        self,
        notification_id: int
    ) -> Dict[str, Any]:
        """Mark notification as delivered

        Args:
            notification_id: The notification ID

        Returns:
            Dict with status

        Raises:
            ValueError: If notification not found
        """
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if not notification:
            raise ValueError("Notification {notification_id} not found".format(notification_id=notification_id))

        # Update status
        notification.status = NotificationStatus.DELIVERED.value
        notification.delivered_at = datetime.utcnow()
        notification.updated_at = datetime.utcnow()

        # Create log entry
        log = NotificationLog(
            notification_id=notification.id,
            status="delivered",
            message="Notification successfully delivered"
        )
        self.db.add(log)

        await self.db.commit()

        return {
            "notification_id": notification.id,
            "status": notification.status,
            "delivered_at": notification.delivered_at,
            "message": "Notification marked as delivered"
        }

    async def mark_as_failed(
        self,
        notification_id: int,
        failed_reason: str
    ) -> Dict[str, Any]:
        """Mark notification as failed

        Args:
            notification_id: The notification ID
            failed_reason: Reason for failure

        Returns:
            Dict with status and retry info

        Raises:
            ValueError: If notification not found
        """
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if not notification:
            raise ValueError("Notification {notification_id} not found".format(notification_id=notification_id))

        # Update status and increment retry count
        notification.status = NotificationStatus.FAILED.value
        notification.failed_at = datetime.utcnow()
        notification.failed_reason = failed_reason
        notification.retry_count += 1
        notification.updated_at = datetime.utcnow()

        # Determine if should retry
        will_retry = notification.retry_count < notification.max_retries
        if will_retry:
            # Re-queue for retry
            notification.status = NotificationStatus.PENDING.value

        # Create log entry
        log = NotificationLog(
            notification_id=notification.id,
            status="failed",
            message=failed_reason,
            error_details={"retry_count": notification.retry_count, "will_retry": will_retry}
        )
        self.db.add(log)

        await self.db.commit()

        return {
            "notification_id": notification.id,
            "status": notification.status,
            "failed_at": notification.failed_at,
            "failed_reason": failed_reason,
            "retry_count": notification.retry_count,
            "will_retry": will_retry,
            "message": "Notification marked as failed. Will retry: {will_retry}".format(will_retry=will_retry)
        }

    async def process_pending_notifications(
        self,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Background job to process pending notifications

        Args:
            limit: Maximum number of notifications to process

        Returns:
            Dict with counts
        """
        # Query pending notifications scheduled for now or earlier
        query = (
            select(Notification)
            .where(
                and_(
                    Notification.status == NotificationStatus.PENDING.value,
                    Notification.scheduled_at <= datetime.utcnow()
                )
            )
            .order_by(
                # Priority order: urgent first
                func.case(
                    (Notification.priority == NotificationPriority.URGENT.value, 1),
                    (Notification.priority == NotificationPriority.HIGH.value, 2),
                    (Notification.priority == NotificationPriority.NORMAL.value, 3),
                    else_=4
                ),
                Notification.created_at.asc()
            )
            .limit(limit)
        )

        result = await self.db.execute(query)
        notifications = result.scalars().all()

        sent_count = 0
        failed_count = 0

        # Process notifications using channel providers
        for notification in notifications:
            try:
                # Import channel provider factory
                from app.services.notification_channels import ChannelProviderFactory

                # Get appropriate channel provider
                provider = ChannelProviderFactory.get_provider(
                    notification.channel,
                    self.db
                )

                # Get recipient contact info
                recipient = await self._get_recipient_contact(
                    notification.recipient_id,
                    notification.user_type,
                    notification.channel
                )

                # Send notification
                delivery_result = await provider.send(
                    recipient=recipient,
                    subject=notification.title or "",
                    message=notification.message,
                    metadata=notification.metadata
                )

                # Update based on result
                if delivery_result.success:
                    notification.status = NotificationStatus.SENT.value
                    notification.sent_at = datetime.utcnow()
                    notification.message_id = delivery_result.message_id
                    sent_count += 1

                    # Create success log
                    log = NotificationLog(
                        notification_id=notification.id,
                        status="sent",
                        message=f"Sent via {notification.channel}: {delivery_result.message_id}",
                    )
                    self.db.add(log)
                else:
                    notification.status = NotificationStatus.FAILED.value
                    notification.failed_at = datetime.utcnow()
                    notification.failed_reason = delivery_result.error_message
                    notification.retry_count += 1
                    failed_count += 1

                    # Create failure log
                    log = NotificationLog(
                        notification_id=notification.id,
                        status="failed",
                        message=f"Failed via {notification.channel}: {delivery_result.error_message}",
                    )
                    self.db.add(log)

                notification.updated_at = datetime.utcnow()

            except Exception as e:
                notification.status = NotificationStatus.FAILED.value
                notification.failed_at = datetime.utcnow()
                notification.failed_reason = str(e)
                notification.retry_count += 1
                notification.updated_at = datetime.utcnow()
                failed_count += 1

                # Create error log
                log = NotificationLog(
                    notification_id=notification.id,
                    status="error",
                    message=f"Processing error: {str(e)}",
                )
                self.db.add(log)

        await self.db.commit()

        return {
            "processed_count": len(notifications),
            "sent_count": sent_count,
            "failed_count": failed_count,
            "message": "Processed {count} pending notifications: {sent} sent, {failed} failed".format(
                count=len(notifications),
                sent=sent_count,
                failed=failed_count
            )
        }

    async def _get_recipient_contact(
        self,
        recipient_id: int,
        user_type: str,
        channel: str
    ) -> str:
        """Get recipient contact information for notification channel

        Args:
            recipient_id: Recipient ID
            user_type: User type (patient, doctor, staff, etc.)
            channel: Notification channel

        Returns:
            Contact info (phone, email, device token, etc.)

        Raises:
            ValueError: If recipient not found or no contact info available
        """
        from app.models.notifications import NotificationChannel

        # Query based on user type
        if user_type in ["doctor", "nurse", "staff", "admin"]:
            result = await self.db.execute(
                select(User).where(User.id == recipient_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                raise ValueError(f"User {recipient_id} not found")

            # Return appropriate contact based on channel
            if channel == NotificationChannel.EMAIL.value:
                return user.email
            elif channel == NotificationChannel.SMS.value:
                return user.phone_number or ""
            elif channel == NotificationChannel.PUSH.value:
                return user.push_token or ""
            else:
                return str(recipient_id)

        elif user_type == "patient":
            # Check Patient table first
            result = await self.db.execute(
                select(Patient).where(Patient.id == recipient_id)
            )
            patient = result.scalar_one_or_none()

            if patient:
                if channel == NotificationChannel.EMAIL.value:
                    return patient.email or ""
                elif channel == NotificationChannel.SMS.value or channel == NotificationChannel.WHATSAPP.value:
                    return patient.phone_number or ""
                elif channel == NotificationChannel.PUSH.value:
                    return patient.push_token or ""
                else:
                    return str(recipient_id)

            # Fallback to PatientPortalUser
            result = await self.db.execute(
                select(PatientPortalUser).where(PatientPortalUser.id == recipient_id)
            )
            portal_user = result.scalar_one_or_none()

            if not portal_user:
                raise ValueError(f"Patient {recipient_id} not found")

            if channel == NotificationChannel.EMAIL.value:
                return portal_user.email
            elif channel == NotificationChannel.SMS.value or channel == NotificationChannel.WHATSAPP.value:
                return portal_user.phone_number or ""
            elif channel == NotificationChannel.PUSH.value:
                return portal_user.push_token or ""
            else:
                return str(recipient_id)

        else:
            # Default to returning ID for unknown user types
            return str(recipient_id)

    # Template methods

    async def create_template(
        self,
        request: TemplateCreateRequest
    ) -> TemplateResponse:
        """Create a new notification template

        Args:
            request: Template creation request

        Returns:
            TemplateResponse with template_id

        Raises:
            ValueError: If validation fails
        """
        # Check if template name already exists
        existing = await self.db.execute(
            select(NotificationTemplate).where(NotificationTemplate.name == request.name)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Template with name '{name}' already exists".format(name=request.name))

        # Create template
        template = NotificationTemplate(
            name=request.name,
            category=request.category.value,
            language=request.language.value,
            version=1,
            subject_template=request.subject_template or "",
            body_template=request.message_template,
            variables=request.variables or [],
            description=request.description,
            tags=[request.category.value, request.type.value],
            is_active=True,
        )

        self.db.add(template)
        await self.db.flush()

        # Create initial version record
        version = NotificationTemplateVersion(
            template_id=template.id,
            version=1,
            subject_template=request.subject_template or "",
            body_template=request.message_template,
            variables=request.variables,
            change_description="Initial version"
        )
        self.db.add(version)

        await self.db.commit()

        return TemplateResponse(
            template_id=template.id,
            name=template.name,
            category=TemplateCategory(template.category),
            language=TemplateLanguage(template.language),
            channel=NotificationChannel(request.channel.value),
            type=NotificationType(request.type.value),
            subject_template=template.subject_template,
            message_template=template.body_template,
            variables=template.variables,
            description=template.description,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )

    async def update_template(
        self,
        template_id: int,
        request: TemplateUpdateRequest
    ) -> TemplateResponse:
        """Update an existing template

        Args:
            template_id: The template ID
            request: Update request

        Returns:
            Updated TemplateResponse

        Raises:
            ValueError: If template not found
        """
        result = await self.db.execute(
            select(NotificationTemplate).where(NotificationTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            raise ValueError("Template {template_id} not found".format(template_id=template_id))

        # Archive old version
        old_version = NotificationTemplateVersion(
            template_id=template.id,
            version=template.version,
            subject_template=template.subject_template,
            body_template=template.body_template,
            variables=template.variables,
            change_description="Archived before update"
        )
        self.db.add(old_version)

        # Update template
        if request.subject_template is not None:
            template.subject_template = request.subject_template
        if request.message_template is not None:
            template.body_template = request.message_template
        if request.variables is not None:
            template.variables = request.variables
        if request.description is not None:
            template.description = request.description
        if request.is_active is not None:
            template.is_active = request.is_active

        # Increment version
        template.version += 1
        template.updated_at = datetime.utcnow()

        await self.db.commit()

        # Return response - need to get channel and type from tags or defaults
        return TemplateResponse(
            template_id=template.id,
            name=template.name,
            category=TemplateCategory(template.category),
            language=TemplateLanguage(template.language),
            channel=NotificationChannel.EMAIL,  # Default, would be stored in template
            type=NotificationType.SYSTEM_ALERT,  # Default, would be stored in template
            subject_template=template.subject_template,
            message_template=template.body_template,
            variables=template.variables,
            description=template.description,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )

    async def get_template(
        self,
        template_id: int
    ) -> TemplateResponse:
        """Get template by ID

        Args:
            template_id: The template ID

        Returns:
            TemplateResponse

        Raises:
            ValueError: If template not found
        """
        result = await self.db.execute(
            select(NotificationTemplate).where(NotificationTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            raise ValueError("Template {template_id} not found".format(template_id=template_id))

        return TemplateResponse(
            template_id=template.id,
            name=template.name,
            category=TemplateCategory(template.category),
            language=TemplateLanguage(template.language),
            channel=NotificationChannel.EMAIL,  # Default, would be stored in template
            type=NotificationType.SYSTEM_ALERT,  # Default, would be stored in template
            subject_template=template.subject_template,
            message_template=template.body_template,
            variables=template.variables,
            description=template.description,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )

    async def list_templates(
        self,
        category: Optional[str] = None,
        template_status: Optional[bool] = None,
        language: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> TemplateListResponse:
        """List all templates with filtering

        Args:
            category: Optional category filter
            template_status: Optional active status filter
            language: Optional language filter
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            TemplateListResponse
        """
        # Build filters
        filters = []
        if category:
            filters.append(NotificationTemplate.category == category)
        if template_status is not None:
            filters.append(NotificationTemplate.is_active == template_status)
        if language:
            filters.append(NotificationTemplate.language == language)

        # Get total count
        count_query = select(func.count(NotificationTemplate.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Get templates with pagination
        offset = (page - 1) * per_page
        query = select(NotificationTemplate)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(NotificationTemplate.name.asc()).limit(per_page).offset(offset)

        result = await self.db.execute(query)
        templates = result.scalars().all()

        # Build response
        template_responses = [
            TemplateResponse(
                template_id=t.id,
                name=t.name,
                category=TemplateCategory(t.category),
                language=TemplateLanguage(t.language),
                channel=NotificationChannel.EMAIL,  # Default
                type=NotificationType.SYSTEM_ALERT,  # Default
                subject_template=t.subject_template,
                message_template=t.body_template,
                variables=t.variables,
                description=t.description,
                is_active=t.is_active,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in templates
        ]

        return TemplateListResponse(
            templates=template_responses,
            total_count=total_count,
            page=page,
            per_page=per_page,
        )

    # Preference methods

    async def get_user_preferences(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Get all notification preferences for a user

        Args:
            user_id: The user ID

        Returns:
            List of preference dicts
        """
        result = await self.db.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            ).order_by(NotificationPreference.notification_type)
        )
        preferences = result.scalars().all()

        return [
            {
                "id": p.id,
                "user_id": p.user_id,
                "user_type": p.user_type,
                "notification_type": p.notification_type,
                "email_enabled": p.email_enabled,
                "sms_enabled": p.sms_enabled,
                "push_enabled": p.push_enabled,
                "in_app_enabled": p.in_app_enabled,
                "whatsapp_enabled": p.whatsapp_enabled,
                "quiet_hours_start": p.quiet_hours_start,
                "quiet_hours_end": p.quiet_hours_end,
                "timezone": p.timezone,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
            }
            for p in preferences
        ]

    async def update_user_preferences(
        self,
        user_id: int,
        notification_type: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user notification preferences

        Args:
            user_id: The user ID
            notification_type: The notification type
            preferences: Preference settings

        Returns:
            Updated preferences dict
        """
        # Check if preference exists
        result = await self.db.execute(
            select(NotificationPreference).where(
                and_(
                    NotificationPreference.user_id == user_id,
                    NotificationPreference.notification_type == notification_type
                )
            )
        )
        preference = result.scalar_one_or_none()

        if preference:
            # Update existing
            if "email_enabled" in preferences:
                preference.email_enabled = preferences["email_enabled"]
            if "sms_enabled" in preferences:
                preference.sms_enabled = preferences["sms_enabled"]
            if "push_enabled" in preferences:
                preference.push_enabled = preferences["push_enabled"]
            if "in_app_enabled" in preferences:
                preference.in_app_enabled = preferences["in_app_enabled"]
            if "whatsapp_enabled" in preferences:
                preference.whatsapp_enabled = preferences["whatsapp_enabled"]
            if "quiet_hours_start" in preferences:
                preference.quiet_hours_start = preferences["quiet_hours_start"]
            if "quiet_hours_end" in preferences:
                preference.quiet_hours_end = preferences["quiet_hours_end"]
            if "timezone" in preferences:
                preference.timezone = preferences["timezone"]
            preference.updated_at = datetime.utcnow()
        else:
            # Create new
            preference = NotificationPreference(
                user_id=user_id,
                user_type="patient",  # Default, would be determined by user lookup
                notification_type=notification_type,
                email_enabled=preferences.get("email_enabled", True),
                sms_enabled=preferences.get("sms_enabled", False),
                push_enabled=preferences.get("push_enabled", True),
                in_app_enabled=preferences.get("in_app_enabled", True),
                whatsapp_enabled=preferences.get("whatsapp_enabled", False),
                quiet_hours_start=preferences.get("quiet_hours_start"),
                quiet_hours_end=preferences.get("quiet_hours_end"),
                timezone=preferences.get("timezone", "Asia/Jakarta"),
            )
            self.db.add(preference)

        await self.db.commit()

        return {
            "id": preference.id,
            "user_id": preference.user_id,
            "user_type": preference.user_type,
            "notification_type": preference.notification_type,
            "email_enabled": preference.email_enabled,
            "sms_enabled": preference.sms_enabled,
            "push_enabled": preference.push_enabled,
            "in_app_enabled": preference.in_app_enabled,
            "whatsapp_enabled": preference.whatsapp_enabled,
            "quiet_hours_start": preference.quiet_hours_start,
            "quiet_hours_end": preference.quiet_hours_end,
            "timezone": preference.timezone,
            "created_at": preference.created_at,
            "updated_at": preference.updated_at,
        }

    async def get_effective_preferences(
        self,
        user_id: int,
        notification_type: str
    ) -> Dict[str, Any]:
        """Get effective preferences (user preferences merged with defaults)

        Args:
            user_id: The user ID
            notification_type: The notification type

        Returns:
            Effective preferences dict
        """
        # Get user preferences
        result = await self.db.execute(
            select(NotificationPreference).where(
                and_(
                    NotificationPreference.user_id == user_id,
                    NotificationPreference.notification_type == notification_type
                )
            )
        )
        preference = result.scalar_one_or_none()

        # Get defaults for notification type
        defaults = self.DEFAULT_PREFERENCES.get(
            notification_type,
            self.DEFAULT_PREFERENCES["all"]
        )

        if preference:
            # Use user preferences
            return {
                "user_id": user_id,
                "notification_type": notification_type,
                "preferences": {
                    "email_enabled": preference.email_enabled,
                    "sms_enabled": preference.sms_enabled,
                    "push_enabled": preference.push_enabled,
                    "in_app_enabled": preference.in_app_enabled,
                    "whatsapp_enabled": preference.whatsapp_enabled,
                },
                "channels_enabled": [
                    channel for channel, enabled in [
                        ("email", preference.email_enabled),
                        ("sms", preference.sms_enabled),
                        ("push", preference.push_enabled),
                        ("in_app", preference.in_app_enabled),
                        ("whatsapp", preference.whatsapp_enabled),
                    ] if enabled
                ],
                "quiet_hours": {
                    "start": preference.quiet_hours_start,
                    "end": preference.quiet_hours_end,
                } if preference.quiet_hours_start and preference.quiet_hours_end else None,
                "timezone": preference.timezone,
                "is_default": False
            }
        else:
            # Use defaults
            return {
                "user_id": user_id,
                "notification_type": notification_type,
                "preferences": defaults,
                "channels_enabled": [
                    channel for channel, enabled in [
                        ("email", defaults["email_enabled"]),
                        ("sms", defaults["sms_enabled"]),
                        ("push", defaults["push_enabled"]),
                        ("in_app", defaults["in_app_enabled"]),
                        ("whatsapp", defaults["whatsapp_enabled"]),
                    ] if enabled
                ],
                "quiet_hours": None,
                "timezone": "Asia/Jakarta",
                "is_default": True
            }

    # Helper methods

    async def _validate_recipient(
        self,
        recipient_id: int,
        recipient_type: str
    ) -> None:
        """Validate that recipient exists

        Args:
            recipient_id: The recipient ID
            recipient_type: The recipient type

        Raises:
            ValueError: If recipient not found
        """
        if recipient_type in ["doctor", "nurse", "staff", "admin"]:
            result = await self.db.execute(
                select(User).where(User.id == recipient_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise ValueError("User {recipient_id} not found".format(recipient_id=recipient_id))
        elif recipient_type == "patient":
            # Check both Patient and PatientPortalUser tables
            result = await self.db.execute(
                select(Patient).where(Patient.id == recipient_id)
            )
            patient = result.scalar_one_or_none()
            if not patient:
                result = await self.db.execute(
                    select(PatientPortalUser).where(PatientPortalUser.id == recipient_id)
                )
                portal_user = result.scalar_one_or_none()
                if not portal_user:
                    raise ValueError("Patient {recipient_id} not found".format(recipient_id=recipient_id))

    async def _process_template(
        self,
        template_id: int,
        variables: Dict[str, Any]
    ) -> tuple:
        """Process template with variable substitution

        Args:
            template_id: The template ID
            variables: Dictionary of variable values

        Returns:
            Tuple of (subject, body) with variables substituted

        Raises:
            ValueError: If template not found or variables missing
        """
        result = await self.db.execute(
            select(NotificationTemplate).where(NotificationTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            raise ValueError("Template {template_id} not found".format(template_id=template_id))

        # Check for missing required variables
        if template.variables:
            missing = [var for var in template.variables if var not in variables]
            if missing:
                raise ValueError("Missing required template variables: {vars}".format(
                    vars=", ".join(missing)
                ))

        # Substitute variables
        subject = self._substitute_variables(template.subject_template, variables)
        body = self._substitute_variables(template.body_template, variables)

        return subject, body

    def _substitute_variables(
        self,
        template: str,
        variables: Dict[str, Any]
    ) -> str:
        """Substitute variables in template string

        Args:
            template: Template string with {variable} placeholders
            variables: Dictionary of variable values

        Returns:
            String with variables substituted
        """
        result = template
        for key, value in variables.items():
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, str(value))
        return result

    async def _queue_notification(
        self,
        notification: Notification
    ) -> None:
        """Queue notification for delivery

        Integrates with Redis-based queue processor for async delivery.

        Args:
            notification: The notification to queue
        """
        try:
            # Import here to avoid circular dependency
            from app.services.notification_queue import get_queue_processor

            # Get queue processor and enqueue notification
            processor = get_queue_processor(self.db)
            await processor.enqueue(
                notification.id,
                NotificationPriority(notification.priority)
            )

        except Exception as e:
            # If queue is unavailable, fall back to immediate processing
            logger.warning(f"Queue unavailable, processing immediately: {e}")
            # Notification will remain in PENDING status for background job
