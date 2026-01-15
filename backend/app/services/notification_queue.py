"""Notification Queue Processor

Asynchronous queue-based notification processing system with Redis backend.
Handles priority queues, retry logic, and delivery tracking.

Python 3.5+ compatible - uses .format() instead of f-strings
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta

import redis
import aioredis
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


class QueuePriority(object):
    """Notification queue priority levels"""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class NotificationQueueProcessor(object):
    """Process notification queue with priority and retry logic"""

    QUEUE_PATTERN = "notification_queue:{priority}"
    PROCESSING_QUEUE = "notification_processing"
    FAILED_QUEUE = "notification_failed"

    BATCH_SIZE = 50
    POLL_INTERVAL = 5
    MAX_PROCESSING_TIME = 300
    RETRY_DELAYS = {
        1: 60,
        2: 300,
        3: 900,
    }

    def __init__(self, db):
        self.db = db
        self.redis_client = None
        self.running = False
        self.worker_tasks = []

    async def start(self, num_workers=3):
        """Start queue processor with multiple workers"""
        if self.running:
            logger.warning("Queue processor already running")
            return

        try:
            # Connect to Redis
            self.redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis at {}".format(settings.REDIS_URL))

            self.running = True

            # Start worker tasks
            for i in range(num_workers):
                task = asyncio.create_task(self._worker("worker-{}".format(i)))
                self.worker_tasks.append(task)

            logger.info("Started {} queue processor workers".format(num_workers))

        except Exception as e:
            logger.error("Failed to start queue processor: {}".format(e))
            raise

    async def stop(self):
        """Stop queue processor gracefully"""
        self.running = False

        for task in self.worker_tasks:
            task.cancel()

        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()

        if self.redis_client:
            await self.redis_client.close()
            logger.info("Queue processor stopped")

    async def enqueue(self, notification_id, priority=NotificationPriority.NORMAL):
        """Add notification to queue"""
        if not self.redis_client:
            logger.warning("Redis not connected, skipping queue")
            return

        queue_priority = self._map_priority(priority)
        queue_name = self.QUEUE_PATTERN.format(priority=queue_priority)

        score = datetime.utcnow().timestamp()
        await self.redis_client.zadd(queue_name, {str(notification_id): score})

        logger.info("Enqueued notification {} to {}".format(notification_id, queue_name))

    async def _worker(self, worker_name):
        """Worker task that processes notifications from queue"""
        logger.info("Worker {} started".format(worker_name))

        while self.running:
            try:
                processed = await self._process_batch(worker_name)

                if processed == 0:
                    await asyncio.sleep(self.POLL_INTERVAL)

            except Exception as e:
                logger.error("Worker {} error: {}".format(worker_name, e))
                await asyncio.sleep(self.POLL_INTERVAL)

        logger.info("Worker {} stopped".format(worker_name))

    async def _process_batch(self, worker_name):
        """Process a batch of notifications from priority queues"""
        processed = 0

        priorities = [QueuePriority.URGENT, QueuePriority.HIGH, QueuePriority.NORMAL, QueuePriority.LOW]

        for priority in priorities:
            if processed >= self.BATCH_SIZE:
                break

            queue_name = self.QUEUE_PATTERN.format(priority=priority)
            notifications = await self._dequeue_batch(queue_name, self.BATCH_SIZE - processed)

            for notification_id_str in notifications:
                try:
                    notification_id = int(notification_id_str)
                    await self._process_notification(notification_id, worker_name)
                    processed += 1

                except Exception as e:
                    logger.error("Error processing notification {}: {}".format(notification_id_str, e))
                    await self._move_to_failed(notification_id_str, str(e))

        return processed

    async def _dequeue_batch(self, queue_name, count):
        """Dequeue multiple notifications from queue"""
        if not self.redis_client:
            return []

        results = await self.redis_client.zpopmin(queue_name, count)
        return [item[0] for item in results] if results else []

    async def _process_notification(self, notification_id, worker_name):
        """Process a single notification"""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if not notification:
            logger.warning("Notification {} not found".format(notification_id))
            return

        if notification.status != NotificationStatus.PENDING:
            logger.info("Notification {} already processed (status: {})".format(
                notification_id, notification.status
            ))
            return

        logger.info("{}: Processing notification {}".format(worker_name, notification_id))

        try:
            provider = ChannelProviderFactory.get_provider(
                notification.channel,
                self.db
            )

            recipient = await self._get_recipient_contact(
                notification.recipient_id,
                notification.user_type,
                notification.channel
            )

            delivery_result = await provider.send_with_retry(
                recipient=recipient,
                subject=notification.title or "",
                message=notification.message,
                metadata=notification.metadata
            )

            await self._update_notification_status(notification, delivery_result)
            await self._log_delivery(notification, delivery_result, worker_name)

        except Exception as e:
            logger.error("Failed to process notification {}: {}".format(notification_id, e))
            await self._handle_processing_error(notification, str(e), worker_name)

    async def _get_recipient_contact(self, recipient_id, user_type, channel):
        """Get recipient contact information for channel"""
        if channel == NotificationChannel.EMAIL:
            return "user{}@example.com".format(recipient_id)
        elif channel in [NotificationChannel.SMS, NotificationChannel.WHATSAPP]:
            return "+62812345678{:02d}".format(recipient_id % 100)
        elif channel == NotificationChannel.PUSH:
            return "device_token_{}".format(recipient_id)
        else:
            return str(recipient_id)

    async def _update_notification_status(self, notification, delivery_result):
        """Update notification status in database"""
        if delivery_result.success:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            notification.message_id = delivery_result.message_id

            if delivery_result.status == ChannelStatus.DELIVERED:
                notification.status = NotificationStatus.DELIVERED
                notification.delivered_at = datetime.utcnow()
        else:
            notification.status = NotificationStatus.FAILED
            notification.failed_at = datetime.utcnow()
            notification.failed_reason = delivery_result.error_message
            notification.retry_count += 1

            if notification.retry_count < notification.max_retries:
                notification.status = NotificationStatus.PENDING
                delay = self.RETRY_DELAYS.get(
                    notification.retry_count,
                    self.RETRY_DELAYS[3]
                )
                await self._schedule_retry(notification, delay)

        notification.updated_at = datetime.utcnow()

    async def _schedule_retry(self, notification, delay_seconds):
        """Schedule notification for retry"""
        if not self.redis_client:
            return

        retry_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
        notification.scheduled_at = retry_time

        queue_priority = self._map_priority(NotificationPriority(notification.priority))
        queue_name = self.QUEUE_PATTERN.format(priority=queue_priority)
        score = retry_time.timestamp()

        await self.redis_client.zadd(queue_name, {str(notification.id): score})

        logger.info(
            "Scheduled notification {} for retry in {}s (attempt {})".format(
                notification.id, delay_seconds, notification.retry_count
            )
        )

    async def _log_delivery(self, notification, delivery_result, worker_name):
        """Log notification delivery attempt"""
        log = NotificationLog(
            notification_id=notification.id,
            status=delivery_result.status,
            message="Processed by {}: {}".format(
                worker_name,
                delivery_result.error_message or "Sent successfully"
            ),
            error_details=delivery_result.provider_response
        )
        self.db.add(log)

    async def _handle_processing_error(self, notification, error_message, worker_name):
        """Handle processing error"""
        notification.status = NotificationStatus.FAILED
        notification.failed_at = datetime.utcnow()
        notification.failed_reason = error_message
        notification.retry_count += 1
        notification.updated_at = datetime.utcnow()

        log = NotificationLog(
            notification_id=notification.id,
            status="processing_error",
            message="{}: {}".format(worker_name, error_message),
        )
        self.db.add(log)

        await self.db.commit()

    async def _move_to_failed(self, notification_id_str, error_message):
        """Move notification to failed queue"""
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
        logger.error("Moved notification {} to failed queue: {}".format(
            notification_id_str, error_message
        ))

    def _map_priority(self, priority):
        """Map notification priority to queue priority"""
        mapping = {
            NotificationPriority.URGENT: QueuePriority.URGENT,
            NotificationPriority.HIGH: QueuePriority.HIGH,
            NotificationPriority.NORMAL: QueuePriority.NORMAL,
            NotificationPriority.LOW: QueuePriority.LOW,
        }
        return mapping.get(priority, QueuePriority.NORMAL)

    async def get_queue_stats(self):
        """Get queue statistics"""
        if not self.redis_client:
            return {"error": "Redis not connected"}

        stats = {
            "queues": {},
            "processing": 0,
            "failed": 0
        }

        for priority in [QueuePriority.URGENT, QueuePriority.HIGH, QueuePriority.NORMAL, QueuePriority.LOW]:
            queue_name = self.QUEUE_PATTERN.format(priority=priority)
            count = await self.redis_client.zcard(queue_name)
            stats["queues"][priority] = count

        stats["processing"] = await self.redis_client.zcard(self.PROCESSING_QUEUE)
        stats["failed"] = await self.redis_client.hlen(self.FAILED_QUEUE)

        return stats


_processor_instance = None


def get_queue_processor(db):
    """Get or create queue processor instance"""
    global _processor_instance

    if _processor_instance is None:
        _processor_instance = NotificationQueueProcessor(db)

    return _processor_instance
