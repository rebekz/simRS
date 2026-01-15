"""Notification Queue Processor

Asynchronous queue-based notification processing system with Redis backend.
Handles priority queues, retry logic, and delivery tracking.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update

from app.models.notifications import (
    Notification,
    NotificationLog,
    NotificationStatus,
    NotificationChannel,
    NotificationPriority,
)
from app.services.notification_channels import (
    ChannelProviderFactory,
    DeliveryResult,
    ChannelStatus,
)
from app.core.config import settings


logger = logging.getLogger(__name__)


class QueuePriority(str, Enum):
    """Notification queue priority levels"""
    URGENT = "urgent"      # Critical alerts, process immediately
    HIGH = "high"          # Important notifications
    NORMAL = "normal"      # Standard notifications
    LOW = "low"            # Bulk notifications, lowest priority


class NotificationQueueProcessor:
    """Process notification queue with priority and retry logic"""

    # Queue name patterns
    QUEUE_PATTERN = "notification_queue:{priority}"
    PROCESSING_QUEUE = "notification_processing"
    FAILED_QUEUE = "notification_failed"

    # Processing configuration
    BATCH_SIZE = 50
    POLL_INTERVAL = 5  # seconds
    MAX_PROCESSING_TIME = 300  # 5 minutes max per notification
    RETRY_DELAYS = {
        1: 60,      # 1 minute
        2: 300,     # 5 minutes
        3: 900,     # 15 minutes
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis_client: Optional[redis.Redis] = None
        self.running = False
        self.worker_tasks: List[asyncio.Task] = []

    async def start(self, num_workers: int = 3):
        """Start queue processor with multiple workers

        Args:
            num_workers: Number of concurrent worker tasks
        """
        if self.running:
            logger.warning("Queue processor already running")
            return

        try:
            # Connect to Redis
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info(f"Connected to Redis at {settings.REDIS_URL}")

            self.running = True

            # Start worker tasks
            for i in range(num_workers):
                task = asyncio.create_task(self._worker(f"worker-{i}"))
                self.worker_tasks.append(task)

            logger.info(f"Started {num_workers} queue processor workers")

        except Exception as e:
            logger.error(f"Failed to start queue processor: {e}")
            raise

    async def stop(self):
        """Stop queue processor gracefully"""
        self.running = False

        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()

        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Queue processor stopped")

    async def enqueue(
        self,
        notification_id: int,
        priority: NotificationPriority = NotificationPriority.NORMAL
    ):
        """Add notification to queue

        Args:
            notification_id: Notification database ID
            priority: Notification priority level
        """
        if not self.redis_client:
            logger.warning("Redis not connected, skipping queue")
            return

        # Map priority to queue
        queue_priority = self._map_priority(priority)
        queue_name = self.QUEUE_PATTERN.format(priority=queue_priority)

        # Add to queue with score as timestamp for FIFO
        score = datetime.utcnow().timestamp()
        await self.redis_client.zadd(queue_name, {str(notification_id): score})

        logger.info(f"Enqueued notification {notification_id} to {queue_name}")

    async def _worker(self, worker_name: str):
        """Worker task that processes notifications from queue

        Args:
            worker_name: Worker identifier for logging
        """
        logger.info(f"Worker {worker_name} started")

        while self.running:
            try:
                # Process batch of notifications
                processed = await self._process_batch(worker_name)

                if processed == 0:
                    # No notifications processed, wait before polling again
                    await asyncio.sleep(self.POLL_INTERVAL)

            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(self.POLL_INTERVAL)

        logger.info(f"Worker {worker_name} stopped")

    async def _process_batch(self, worker_name: str) -> int:
        """Process a batch of notifications from priority queues

        Args:
            worker_name: Worker identifier

        Returns:
            Number of notifications processed
        """
        processed = 0

        # Check queues in priority order (urgent first)
        priorities = [QueuePriority.URGENT, QueuePriority.HIGH, QueuePriority.NORMAL, QueuePriority.LOW]

        for priority in priorities:
            if processed >= self.BATCH_SIZE:
                break

            queue_name = self.QUEUE_PATTERN.format(priority=priority)

            # Pop notifications from queue (blocking with timeout)
            notifications = await self._dequeue_batch(queue_name, self.BATCH_SIZE - processed)

            for notification_id_str in notifications:
                try:
                    notification_id = int(notification_id_str)
                    await self._process_notification(notification_id, worker_name)
                    processed += 1

                except Exception as e:
                    logger.error(f"Error processing notification {notification_id_str}: {e}")
                    # Move to failed queue
                    await self._move_to_failed(notification_id_str, str(e))

        return processed

    async def _dequeue_batch(self, queue_name: str, count: int) -> List[str]:
        """Dequeue multiple notifications from queue

        Args:
            queue_name: Queue name
            count: Maximum number to dequeue

        Returns:
            List of notification IDs as strings
        """
        if not self.redis_client:
            return []

        # Use ZPOPMIN for FIFO ordering (lowest score first)
        # ZPOPMIN returns sorted set members with lowest scores
        results = await self.redis_client.zpopmin(queue_name, count)

        # Extract notification IDs (results are list of [member, score] pairs)
        return [item[0] for item in results] if results else []

    async def _process_notification(self, notification_id: int, worker_name: str):
        """Process a single notification

        Args:
            notification_id: Notification database ID
            worker_name: Worker identifier for logging
        """
        # Get notification from database
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if not notification:
            logger.warning(f"Notification {notification_id} not found")
            return

        if notification.status != NotificationStatus.PENDING:
            logger.info(f"Notification {notification_id} already processed (status: {notification.status})")
            return

        logger.info(f"{worker_name}: Processing notification {notification_id}")

        try:
            # Get channel provider
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

            # Send notification via channel
            delivery_result = await provider.send_with_retry(
                recipient=recipient,
                subject=notification.title or "",
                message=notification.message,
                metadata=notification.metadata
            )

            # Update notification based on result
            await self._update_notification_status(notification, delivery_result)

            # Log delivery
            await self._log_delivery(notification, delivery_result, worker_name)

        except Exception as e:
            logger.error(f"Failed to process notification {notification_id}: {e}")
            await self._handle_processing_error(notification, str(e), worker_name)

    async def _get_recipient_contact(
        self,
        recipient_id: int,
        user_type: str,
        channel: NotificationChannel
    ) -> str:
        """Get recipient contact information for channel

        Args:
            recipient_id: Recipient ID
            user_type: User type (patient, doctor, staff, etc.)
            channel: Notification channel

        Returns:
            Contact info (phone, email, device token, etc.)
        """
        # In production, this would query the appropriate tables
        # For now, return mock contact info
        if channel == NotificationChannel.EMAIL:
            return f"user{recipient_id}@example.com"
        elif channel in [NotificationChannel.SMS, NotificationChannel.WHATSAPP]:
            return f"+62812345678{recipient_id % 100:02d}"
        elif channel == NotificationChannel.PUSH:
            return f"device_token_{recipient_id}"
        else:  # IN_APP
            return str(recipient_id)

    async def _update_notification_status(
        self,
        notification: Notification,
        delivery_result: DeliveryResult
    ):
        """Update notification status in database

        Args:
            notification: Notification model instance
            delivery_result: Delivery result from channel provider
        """
        if delivery_result.success:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            notification.message_id = delivery_result.message_id

            # Some channels confirm delivery immediately
            if delivery_result.status == ChannelStatus.DELIVERED:
                notification.status = NotificationStatus.DELIVERED
                notification.delivered_at = datetime.utcnow()
        else:
            notification.status = NotificationStatus.FAILED
            notification.failed_at = datetime.utcnow()
            notification.failed_reason = delivery_result.error_message
            notification.retry_count += 1

            # Check if should retry
            if notification.retry_count < notification.max_retries:
                notification.status = NotificationStatus.PENDING
                # Re-enqueue with delay
                delay = self.RETRY_DELAYS.get(
                    notification.retry_count,
                    self.RETRY_DELAYS[3]
                )
                await self._schedule_retry(notification, delay)

        notification.updated_at = datetime.utcnow()

    async def _schedule_retry(self, notification: Notification, delay_seconds: int):
        """Schedule notification for retry

        Args:
            notification: Notification to retry
            delay_seconds: Delay before retry
        """
        if not self.redis_client:
            return

        # Calculate retry time
        retry_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
        notification.scheduled_at = retry_time

        # Add back to queue with scheduled time as score
        queue_priority = self._map_priority(NotificationPriority(notification.priority))
        queue_name = self.QUEUE_PATTERN.format(priority=queue_priority)
        score = retry_time.timestamp()

        await self.redis_client.zadd(queue_name, {str(notification.id): score})

        logger.info(
            f"Scheduled notification {notification.id} for retry "
            f"in {delay_seconds}s (attempt {notification.retry_count})"
        )

    async def _log_delivery(
        self,
        notification: Notification,
        delivery_result: DeliveryResult,
        worker_name: str
    ):
        """Log notification delivery attempt

        Args:
            notification: Notification instance
            delivery_result: Delivery result
            worker_name: Worker that processed it
        """
        log = NotificationLog(
            notification_id=notification.id,
            status=delivery_result.status.value,
            message=f"Processed by {worker_name}: {delivery_result.error_message or 'Sent successfully'}",
            error_details=delivery_result.provider_response
        )
        self.db.add(log)

    async def _handle_processing_error(
        self,
        notification: Notification,
        error_message: str,
        worker_name: str
    ):
        """Handle processing error

        Args:
            notification: Notification that failed
            error_message: Error message
            worker_name: Worker identifier
        """
        notification.status = NotificationStatus.FAILED
        notification.failed_at = datetime.utcnow()
        notification.failed_reason = error_message
        notification.retry_count += 1
        notification.updated_at = datetime.utcnow()

        # Log error
        log = NotificationLog(
            notification_id=notification.id,
            status="processing_error",
            message=f"{worker_name}: {error_message}",
        )
        self.db.add(log)

        await self.db.commit()

    async def _move_to_failed(self, notification_id_str: str, error_message: str):
        """Move notification to failed queue

        Args:
            notification_id_str: Notification ID as string
            error_message: Error message
        """
        if not self.redis_client:
            return

        await self.redis_client.hset(
            self.FAILED_QUEUE,
            notification_id_str,
            json.dumps({
                "failed_at": datetime.utcnow().isoformat(),
                "error": error_message
            })
        )
        logger.error(f"Moved notification {notification_id_str} to failed queue: {error_message}")

    def _map_priority(self, priority: NotificationPriority) -> QueuePriority:
        """Map notification priority to queue priority

        Args:
            priority: Notification priority enum

        Returns:
            Queue priority enum
        """
        mapping = {
            NotificationPriority.URGENT: QueuePriority.URGENT,
            NotificationPriority.HIGH: QueuePriority.HIGH,
            NotificationPriority.NORMAL: QueuePriority.NORMAL,
            NotificationPriority.LOW: QueuePriority.LOW,
        }
        return mapping.get(priority, QueuePriority.NORMAL)

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics

        Returns:
            Dictionary with queue stats
        """
        if not self.redis_client:
            return {"error": "Redis not connected"}

        stats = {
            "queues": {},
            "processing": 0,
            "failed": 0
        }

        # Get counts for each priority queue
        for priority in QueuePriority:
            queue_name = self.QUEUE_PATTERN.format(priority=priority)
            count = await self.redis_client.zcard(queue_name)
            stats["queues"][priority] = count

        # Get processing and failed counts
        stats["processing"] = await self.redis_client.zcard(self.PROCESSING_QUEUE)
        stats["failed"] = await self.redis_client.hlen(self.FAILED_QUEUE)

        return stats


# Singleton instance management
_processor_instance: Optional[NotificationQueueProcessor] = None


def get_queue_processor(db: AsyncSession) -> NotificationQueueProcessor:
    """Get or create queue processor instance

    Args:
        db: Database session

    Returns:
        NotificationQueueProcessor instance
    """
    global _processor_instance

    if _processor_instance is None:
        _processor_instance = NotificationQueueProcessor(db)

    return _processor_instance
