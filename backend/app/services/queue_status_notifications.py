"""Queue Status Notification Service

STORY-022-07: Queue Status Notifications
Service for queue position updates and real-time queue notifications.

Python 3.5+ compatible
"""

import logging
from datetime import datetime, timedelta, time
from typing import Optional, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.notifications import (
    Notification,
    NotificationLog,
    NotificationStatus,
    NotificationChannel,
    NotificationPriority,
    NotificationType,
)
from app.models.queue import QueueTicket, QueueNotification, QueueSettings
from app.services.notification_preferences import get_preference_manager


logger = logging.getLogger(__name__)


class QueueStatusNotificationService(object):
    """Service for queue status notifications"""

    # Notification thresholds
    POSITION_CHANGE_THRESHOLD = 1  # Notify every position change
    APPROACHING_TURN_THRESHOLD = 5  # Notify when 5 patients away
    NEXT_IN_QUEUE_THRESHOLD = 1  # Notify when next
    LONG_WAIT_MINUTES = 30  # Long wait threshold
    LONG_WAIT_UPDATE_MINUTES = 15  # Update frequency for long waits
    DEPARTURE_WARNING_MINUTES = 30  # Send departure warning 30 min before

    # Message templates
    POSITION_UPDATE_TEMPLATE = (
        "QUEUE UPDATE - {hospital_name}\n\n"
        "Dear {patient_name},\n\n"
        "Your queue position:\n"
        "Ticket: {ticket_number}\n"
        "Current Position: {position}\n"
        "Patients Ahead: {people_ahead}\n"
        "Estimated Wait: {wait_minutes} minutes\n"
        "{location_info}\n\n"
        "Please check for updates."
    )

    APPROACHING_TURN_TEMPLATE = (
        "QUEUE ALERT - Approaching Soon!\n\n"
        "Dear {patient_name},\n\n"
        "Your turn is approaching:\n"
        "Ticket: {ticket_number}\n"
        "Position: {position} ({people_ahead} patients ahead)\n"
        "Estimated Wait: ~{wait_minutes} minutes\n\n"
        "Please be ready to proceed to:\n"
        "{location_info}\n\n"
        "Thank you!"
    )

    NEXT_IN_QUEUE_TEMPLATE = (
        "QUEUE ALERT - You're Next!\n\n"
        "Dear {patient_name},\n\n"
        "You are next in line:\n"
        "Ticket: {ticket_number}\n"
        "Counter/Room: {counter}\n\n"
        "Please proceed to the service area now.\n\n"
        "Thank you!"
    )

    LONG_WAIT_TEMPLATE = (
        "QUEUE UPDATE - Extended Wait\n\n"
        "Dear {patient_name},\n\n"
        "Your queue status:\n"
        "Ticket: {ticket_number}\n"
        "Current Position: {position}\n"
        "Estimated Wait: {wait_minutes} minutes\n\n"
        "We apologize for the extended wait time.\n"
        "You will be notified when your turn approaches.\n\n"
        "Thank you for your patience!"
    )

    DOCTOR_ARRIVED_TEMPLATE = (
        "QUEUE UPDATE - Doctor Arrived\n\n"
        "Dear {patient_name},\n\n"
        "Good news! Your doctor has arrived:\n"
        "Ticket: {ticket_number}\n"
        "Doctor: {doctor_name}\n"
        "Queue will resume shortly.\n\n"
        "Current Position: {position}\n"
        "Estimated Wait: {wait_minutes} minutes\n\n"
        "Thank you!"
    )

    DOCTOR_ON_BREAK_TEMPLATE = (
        "QUEUE UPDATE - Doctor on Break\n\n"
        "Dear {patient_name},\n\n"
        "Your doctor is currently on break:\n"
        "Ticket: {ticket_number}\n"
        "Doctor: {doctor_name}\n\n"
        "Expected resume: {resume_time}\n"
        "Current Position: {position}\n\n"
        "You will be notified when service resumes.\n\n"
        "Thank you for your patience!"
    )

    DELAY_NOTIFICATION_TEMPLATE = (
        "QUEUE ALERT - Service Delay\n\n"
        "Dear {patient_name},\n\n"
        "There is a delay in service:\n"
        "Ticket: {ticket_number}\n"
        "Current Position: {position}\n"
        "Additional Wait: {additional_minutes} minutes\n"
        "New Estimated Wait: {total_wait_minutes} minutes\n\n"
        "We apologize for the inconvenience.\n"
        "You will be notified when your turn approaches.\n\n"
        "Thank you!"
    )

    DEPARTURE_TEMPLATE = (
        "QUEUE ALERT - Time to Leave\n\n"
        "Dear {patient_name},\n\n"
        "It's time to head to the hospital:\n"
        "Ticket: {ticket_number}\n"
        "Department: {department}\n"
        "{location_info}\n\n"
        "Please arrive within the next 30 minutes.\n"
        "Current wait time: {wait_minutes} minutes\n\n"
        "See you soon!"
    )

    SERVICE_STARTED_TEMPLATE = (
        "QUEUE UPDATE - Being Served\n\n"
        "Dear {patient_name},\n\n"
        "You are now being served:\n"
        "Ticket: {ticket_number}\n"
        "Counter/Room: {counter}\n\n"
        "Next steps will be provided after service.\n\n"
        "Thank you!"
    )

    SERVICE_COMPLETED_TEMPLATE = (
        "QUEUE UPDATE - Service Completed\n\n"
        "Dear {patient_name},\n\n"
        "Your service has been completed:\n"
        "Ticket: {ticket_number}\n"
        "Department: {department}\n\n"
        "Next Steps:\n"
        "{next_steps}\n\n"
        "Thank you for visiting {hospital_name}!"
    )

    def __init__(self, db):
        self.db = db
        self.preference_manager = get_preference_manager(db)

    async def notify_position_change(self, ticket_id):
        """Send notification when queue position changes

        Args:
            ticket_id: Queue ticket ID

        Returns:
            Notification ID or None
        """
        try:
            # Get ticket with related data
            ticket = await self._get_ticket_with_details(ticket_id)
            if not ticket:
                logger.warning("Queue ticket {} not found".format(ticket_id))
                return None

            # Check if notifications are enabled
            enabled_channels = await self.preference_manager.get_enabled_channels(
                ticket.patient_id,
                "patient",
                "queue_notification"
            )

            if not enabled_channels:
                logger.info("Patient {} has opted out of queue notifications".format(ticket.patient_id))
                return None

            # Build message
            location_info = self._get_location_info(ticket)
            message = self.POSITION_UPDATE_TEMPLATE.format(
                patient_name=self._get_patient_name(ticket),
                hospital_name="SIMRS Hospital",
                ticket_number=ticket.ticket_number,
                position=ticket.queue_position or 0,
                people_ahead=ticket.people_ahead or 0,
                wait_minutes=ticket.estimated_wait_minutes or 0,
                location_info=location_info
            )

            # Send notification
            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=ticket.patient_id,
                    user_type="patient",
                    notification_type=NotificationType.QUEUE_UPDATE,
                    channel=channel,
                    priority=NotificationPriority.NORMAL,
                    status=NotificationStatus.PENDING,
                    title="Queue Position Update - " + ticket.ticket_number,
                    message=message,
                    metadata={
                        "ticket_id": ticket.id,
                        "ticket_number": ticket.ticket_number,
                        "department": ticket.department.value if ticket.department else None,
                        "queue_position": ticket.queue_position,
                        "notification_type": "position_change"
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent position change notification for ticket {}".format(
                    ticket.ticket_number
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending position change notification: {}".format(e))
            await self.db.rollback()
            return None

    async def notify_approaching_turn(self, ticket_id):
        """Send notification when patient is approaching their turn (5 away)

        Args:
            ticket_id: Queue ticket ID

        Returns:
            Notification ID or None
        """
        try:
            ticket = await self._get_ticket_with_details(ticket_id)
            if not ticket:
                return None

            enabled_channels = await self.preference_manager.get_enabled_channels(
                ticket.patient_id,
                "patient",
                "queue_notification"
            )

            if not enabled_channels:
                return None

            location_info = self._get_location_info(ticket)
            message = self.APPROACHING_TURN_TEMPLATE.format(
                patient_name=self._get_patient_name(ticket),
                ticket_number=ticket.ticket_number,
                position=ticket.queue_position or 0,
                people_ahead=ticket.people_ahead or 0,
                wait_minutes=ticket.estimated_wait_minutes or 0,
                location_info=location_info
            )

            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=ticket.patient_id,
                    user_type="patient",
                    notification_type=NotificationType.QUEUE_UPDATE,
                    channel=channel,
                    priority=NotificationPriority.HIGH,
                    status=NotificationStatus.PENDING,
                    title="Queue Alert - Approaching Soon - " + ticket.ticket_number,
                    message=message,
                    metadata={
                        "ticket_id": ticket.id,
                        "ticket_number": ticket.ticket_number,
                        "queue_position": ticket.queue_position,
                        "notification_type": "approaching_turn"
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent approaching turn notification for ticket {}".format(
                    ticket.ticket_number
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending approaching turn notification: {}".format(e))
            await self.db.rollback()
            return None

    async def notify_next_in_queue(self, ticket_id, counter=None):
        """Send notification when patient is next in queue

        Args:
            ticket_id: Queue ticket ID
            counter: Counter/room number

        Returns:
            Notification ID or None
        """
        try:
            ticket = await self._get_ticket_with_details(ticket_id)
            if not ticket:
                return None

            # High priority - use multiple channels
            enabled_channels = await self.preference_manager.get_enabled_channels(
                ticket.patient_id,
                "patient",
                "queue_notification"
            )

            # Ensure SMS/Push for next-in-queue
            if "sms" not in enabled_channels:
                enabled_channels.insert(0, "sms")

            message = self.NEXT_IN_QUEUE_TEMPLATE.format(
                patient_name=self._get_patient_name(ticket),
                ticket_number=ticket.ticket_number,
                counter=counter or ticket.serving_counter or "Service Counter"
            )

            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=ticket.patient_id,
                    user_type="patient",
                    notification_type=NotificationType.QUEUE_UPDATE,
                    channel=channel,
                    priority=NotificationPriority.HIGH,
                    status=NotificationStatus.PENDING,
                    title="You're Next! - " + ticket.ticket_number,
                    message=message,
                    metadata={
                        "ticket_id": ticket.id,
                        "ticket_number": ticket.ticket_number,
                        "counter": counter or ticket.serving_counter,
                        "notification_type": "next_in_queue"
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent next in queue notification for ticket {}".format(
                    ticket.ticket_number
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending next in queue notification: {}".format(e))
            await self.db.rollback()
            return None

    async def notify_long_wait_update(self, ticket_id):
        """Send update for long wait times (>30 min)

        Args:
            ticket_id: Queue ticket ID

        Returns:
            Notification ID or None
        """
        try:
            ticket = await self._get_ticket_with_details(ticket_id)
            if not ticket:
                return None

            enabled_channels = await self.preference_manager.get_enabled_channels(
                ticket.patient_id,
                "patient",
                "queue_notification"
            )

            if not enabled_channels:
                return None

            message = self.LONG_WAIT_TEMPLATE.format(
                patient_name=self._get_patient_name(ticket),
                ticket_number=ticket.ticket_number,
                position=ticket.queue_position or 0,
                wait_minutes=ticket.estimated_wait_minutes or 0
            )

            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=ticket.patient_id,
                    user_type="patient",
                    notification_type=NotificationType.QUEUE_UPDATE,
                    channel=channel,
                    priority=NotificationPriority.NORMAL,
                    status=NotificationStatus.PENDING,
                    title="Queue Update - Extended Wait - " + ticket.ticket_number,
                    message=message,
                    metadata={
                        "ticket_id": ticket.id,
                        "ticket_number": ticket.ticket_number,
                        "queue_position": ticket.queue_position,
                        "notification_type": "long_wait"
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent long wait update for ticket {}".format(
                    ticket.ticket_number
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending long wait update: {}".format(e))
            await self.db.rollback()
            return None

    async def notify_doctor_arrived(self, ticket_id):
        """Send notification when doctor arrives (if running late)

        Args:
            ticket_id: Queue ticket ID

        Returns:
            Notification ID or None
        """
        try:
            ticket = await self._get_ticket_with_details(ticket_id)
            if not ticket:
                return None

            enabled_channels = await self.preference_manager.get_enabled_channels(
                ticket.patient_id,
                "patient",
                "queue_notification"
            )

            if not enabled_channels:
                return None

            doctor_name = ticket.doctor.full_name if ticket.doctor else "Your Doctor"

            message = self.DOCTOR_ARRIVED_TEMPLATE.format(
                patient_name=self._get_patient_name(ticket),
                ticket_number=ticket.ticket_number,
                doctor_name=doctor_name,
                position=ticket.queue_position or 0,
                wait_minutes=ticket.estimated_wait_minutes or 0
            )

            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=ticket.patient_id,
                    user_type="patient",
                    notification_type=NotificationType.QUEUE_UPDATE,
                    channel=channel,
                    priority=NotificationPriority.NORMAL,
                    status=NotificationStatus.PENDING,
                    title="Doctor Arrived - " + ticket.ticket_number,
                    message=message,
                    metadata={
                        "ticket_id": ticket.id,
                        "ticket_number": ticket.ticket_number,
                        "doctor_id": ticket.doctor_id,
                        "notification_type": "doctor_arrived"
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent doctor arrived notification for ticket {}".format(
                    ticket.ticket_number
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending doctor arrived notification: {}".format(e))
            await self.db.rollback()
            return None

    async def notify_doctor_on_break(self, ticket_id, resume_time_str):
        """Send notification when doctor goes on break

        Args:
            ticket_id: Queue ticket ID
            resume_time_str: Expected resume time (HH:MM format)

        Returns:
            Notification ID or None
        """
        try:
            ticket = await self._get_ticket_with_details(ticket_id)
            if not ticket:
                return None

            enabled_channels = await self.preference_manager.get_enabled_channels(
                ticket.patient_id,
                "patient",
                "queue_notification"
            )

            if not enabled_channels:
                return None

            doctor_name = ticket.doctor.full_name if ticket.doctor else "Your Doctor"

            message = self.DOCTOR_ON_BREAK_TEMPLATE.format(
                patient_name=self._get_patient_name(ticket),
                ticket_number=ticket.ticket_number,
                doctor_name=doctor_name,
                resume_time=resume_time_str,
                position=ticket.queue_position or 0
            )

            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=ticket.patient_id,
                    user_type="patient",
                    notification_type=NotificationType.QUEUE_UPDATE,
                    channel=channel,
                    priority=NotificationPriority.NORMAL,
                    status=NotificationStatus.PENDING,
                    title="Doctor on Break - " + ticket.ticket_number,
                    message=message,
                    metadata={
                        "ticket_id": ticket.id,
                        "ticket_number": ticket.ticket_number,
                        "doctor_id": ticket.doctor_id,
                        "notification_type": "doctor_break"
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent doctor on break notification for ticket {}".format(
                    ticket.ticket_number
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending doctor on break notification: {}".format(e))
            await self.db.rollback()
            return None

    async def notify_delay(self, ticket_id, additional_minutes):
        """Send notification when significant delay occurs (>30 min)

        Args:
            ticket_id: Queue ticket ID
            additional_minutes: Additional wait time in minutes

        Returns:
            Notification ID or None
        """
        try:
            ticket = await self._get_ticket_with_details(ticket_id)
            if not ticket:
                return None

            enabled_channels = await self.preference_manager.get_enabled_channels(
                ticket.patient_id,
                "patient",
                "queue_notification"
            )

            if not enabled_channels:
                return None

            total_wait = (ticket.estimated_wait_minutes or 0) + additional_minutes

            message = self.DELAY_NOTIFICATION_TEMPLATE.format(
                patient_name=self._get_patient_name(ticket),
                ticket_number=ticket.ticket_number,
                position=ticket.queue_position or 0,
                additional_minutes=additional_minutes,
                total_wait_minutes=total_wait
            )

            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=ticket.patient_id,
                    user_type="patient",
                    notification_type=NotificationType.QUEUE_UPDATE,
                    channel=channel,
                    priority=NotificationPriority.HIGH,
                    status=NotificationStatus.PENDING,
                    title="Service Delay - " + ticket.ticket_number,
                    message=message,
                    metadata={
                        "ticket_id": ticket.id,
                        "ticket_number": ticket.ticket_number,
                        "additional_minutes": additional_minutes,
                        "notification_type": "delay"
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent delay notification for ticket {}".format(
                    ticket.ticket_number
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending delay notification: {}".format(e))
            await self.db.rollback()
            return None

    async def notify_departure_time(self, ticket_id):
        """Send notification when it's time to leave for hospital

        Args:
            ticket_id: Queue ticket ID

        Returns:
            Notification ID or None
        """
        try:
            ticket = await self._get_ticket_with_details(ticket_id)
            if not ticket:
                return None

            enabled_channels = await self.preference_manager.get_enabled_channels(
                ticket.patient_id,
                "patient",
                "queue_notification"
            )

            if not enabled_channels:
                return None

            location_info = self._get_location_info(ticket)
            department_name = ticket.department.value if ticket.department else "Service"

            message = self.DEPARTURE_TEMPLATE.format(
                patient_name=self._get_patient_name(ticket),
                ticket_number=ticket.ticket_number,
                department=department_name,
                location_info=location_info,
                wait_minutes=ticket.estimated_wait_minutes or 0
            )

            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=ticket.patient_id,
                    user_type="patient",
                    notification_type=NotificationType.QUEUE_UPDATE,
                    channel=channel,
                    priority=NotificationPriority.HIGH,
                    status=NotificationStatus.PENDING,
                    title="Time to Leave - " + ticket.ticket_number,
                    message=message,
                    metadata={
                        "ticket_id": ticket.id,
                        "ticket_number": ticket.ticket_number,
                        "department": department_name,
                        "notification_type": "departure_time"
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent departure time notification for ticket {}".format(
                    ticket.ticket_number
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending departure time notification: {}".format(e))
            await self.db.rollback()
            return None

    async def notify_service_started(self, ticket_id, counter=None):
        """Send notification when patient is being served

        Args:
            ticket_id: Queue ticket ID
            counter: Counter/room number

        Returns:
            Notification ID or None
        """
        try:
            ticket = await self._get_ticket_with_details(ticket_id)
            if not ticket:
                return None

            enabled_channels = await self.preference_manager.get_enabled_channels(
                ticket.patient_id,
                "patient",
                "queue_notification"
            )

            if not enabled_channels:
                return None

            message = self.SERVICE_STARTED_TEMPLATE.format(
                patient_name=self._get_patient_name(ticket),
                ticket_number=ticket.ticket_number,
                counter=counter or ticket.serving_counter or "Service Counter"
            )

            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=ticket.patient_id,
                    user_type="patient",
                    notification_type=NotificationType.QUEUE_UPDATE,
                    channel=channel,
                    priority=NotificationPriority.NORMAL,
                    status=NotificationStatus.PENDING,
                    title="Being Served - " + ticket.ticket_number,
                    message=message,
                    metadata={
                        "ticket_id": ticket.id,
                        "ticket_number": ticket.ticket_number,
                        "counter": counter or ticket.serving_counter,
                        "notification_type": "service_started"
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent service started notification for ticket {}".format(
                    ticket.ticket_number
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending service started notification: {}".format(e))
            await self.db.rollback()
            return None

    async def notify_service_completed(self, ticket_id, next_steps=None):
        """Send notification when service is completed

        Args:
            ticket_id: Queue ticket ID
            next_steps: List of next steps (e.g., ["Go to pharmacy", "Go to cashier"])

        Returns:
            Notification ID or None
        """
        try:
            ticket = await self._get_ticket_with_details(ticket_id)
            if not ticket:
                return None

            enabled_channels = await self.preference_manager.get_enabled_channels(
                ticket.patient_id,
                "patient",
                "queue_notification"
            )

            if not enabled_channels:
                return None

            # Format next steps
            if next_steps:
                steps_text = "\n".join(["{}. {}".format(i+1, step) for i, step in enumerate(next_steps)])
            else:
                steps_text = "Please proceed to the next service area."

            department_name = ticket.department.value if ticket.department else "Service"

            message = self.SERVICE_COMPLETED_TEMPLATE.format(
                patient_name=self._get_patient_name(ticket),
                ticket_number=ticket.ticket_number,
                department=department_name,
                next_steps=steps_text,
                hospital_name="SIMRS Hospital"
            )

            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=ticket.patient_id,
                    user_type="patient",
                    notification_type=NotificationType.QUEUE_UPDATE,
                    channel=channel,
                    priority=NotificationPriority.NORMAL,
                    status=NotificationStatus.PENDING,
                    title="Service Completed - " + ticket.ticket_number,
                    message=message,
                    metadata={
                        "ticket_id": ticket.id,
                        "ticket_number": ticket.ticket_number,
                        "department": department_name,
                        "notification_type": "service_completed"
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent service completed notification for ticket {}".format(
                    ticket.ticket_number
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending service completed notification: {}".format(e))
            await self.db.rollback()
            return None

    async def check_and_notify_queue_updates(self, department=None):
        """Check all active tickets and send appropriate notifications

        Args:
            department: Optional department filter

        Returns:
            Dictionary with notification counts
        """
        try:
            # Get active waiting tickets
            filters = [
                QueueTicket.status == "waiting"
            ]

            if department:
                filters.append(QueueTicket.department == department)

            query = select(QueueTicket).where(
                and_(*filters)
            ).options(
                selectinload(QueueTicket.patient),
                selectinload(QueueTicket.doctor),
                selectinload(QueueTicket.poli)
            )

            result = await self.db.execute(query)
            tickets = result.scalars().all()

            notifications_sent = {
                "position_change": 0,
                "approaching_turn": 0,
                "next_in_queue": 0,
                "long_wait": 0
            }

            for ticket in tickets:
                # Check if position changed recently (would need tracking)
                # This is a placeholder - actual implementation would track changes

                # Check if approaching turn (5 away)
                if ticket.people_ahead == self.APPROACHING_TURN_THRESHOLD:
                    await self.notify_approaching_turn(ticket.id)
                    notifications_sent["approaching_turn"] += 1

                # Check if next in queue
                if ticket.people_ahead == self.NEXT_IN_QUEUE_THRESHOLD:
                    await self.notify_next_in_queue(ticket.id)
                    notifications_sent["next_in_queue"] += 1

                # Check for long wait
                if ticket.estimated_wait_minutes and ticket.estimated_wait_minutes > self.LONG_WAIT_MINUTES:
                    # Check if we haven't sent long wait notification recently
                    # This would require tracking last notification time
                    pass

            logger.info(
                "Queue update check completed: {}".format(notifications_sent)
            )

            return notifications_sent

        except Exception as e:
            logger.error("Error checking queue updates: {}".format(e))
            return {}

    async def _get_ticket_with_details(self, ticket_id):
        """Get ticket with all related data"""
        query = select(QueueTicket).where(
            QueueTicket.id == ticket_id
        ).options(
            selectinload(QueueTicket.patient),
            selectinload(QueueTicket.doctor),
            selectinload(QueueTicket.poli)
        )

        result = await self.db.execute(query)
        return result.scalars().first()

    def _get_patient_name(self, ticket):
        """Get patient name from ticket"""
        if ticket.patient:
            return ticket.patient.name
        return "Pasien"

    def _get_location_info(self, ticket):
        """Get location information for ticket"""
        parts = []

        if ticket.department:
            parts.append("Department: " + ticket.department.value)

        if ticket.poli:
            parts.append("Poli: " + ticket.poli.name)

        if ticket.doctor:
            parts.append("Doctor: " + ticket.doctor.full_name)

        if ticket.serving_counter:
            parts.append("Counter: " + str(ticket.serving_counter))

        return "\n".join(parts) if parts else "Please proceed to the service area."

    def _get_channel_objects(self, channel_names):
        """Convert channel names to NotificationChannel enums"""
        channel_map = {
            "email": NotificationChannel.EMAIL,
            "sms": NotificationChannel.SMS,
            "push": NotificationChannel.PUSH,
            "in_app": NotificationChannel.IN_APP,
            "whatsapp": NotificationChannel.WHATSAPP
        }
        return [channel_map.get(ch) for ch in channel_names if ch in channel_map]


def get_queue_status_notification_service(db):
    """Get or create queue status notification service instance

    Args:
        db: Database session

    Returns:
        QueueStatusNotificationService instance
    """
    return QueueStatusNotificationService(db)
