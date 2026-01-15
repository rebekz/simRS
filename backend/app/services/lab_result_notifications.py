"""Lab Result Notification Service

STORY-022-04: Lab Result Notifications
Service for notifying patients when lab results are ready and available.

Python 3.5+ compatible
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.notifications import (
    Notification,
    NotificationLog,
    NotificationStatus,
    NotificationChannel,
    NotificationPriority,
    NotificationType,
)
from app.services.notification_preferences import get_preference_manager


logger = logging.getLogger(__name__)


class LabResultNotificationService(object):
    """Service for lab result notifications"""

    # Notification priorities by result type
    CRITICAL_VALUE_PRIORITY = NotificationPriority.URGENT
    ABNORMAL_VALUE_PRIORITY = NotificationPriority.HIGH
    NORMAL_VALUE_PRIORITY = NotificationPriority.NORMAL

    # Message templates
    RESULT_READY_TEMPLATE = (
        "LAB RESULT READY\n\n"
        "Dear {patient_name},\n\n"
        "Your lab test results are ready for viewing:\n"
        "{test_names}\n"
        "Completed: {completion_date}\n\n"
        "Please log in to the patient portal to view your results:\n"
        "{portal_link}\n\n"
        "If you have questions, contact your doctor."
    )

    CRITICAL_VALUE_TEMPLATE = (
        "CRITICAL LAB VALUE ALERT\n\n"
        "Dear {patient_name},\n\n"
        "URGENT: A critical value was detected in your recent lab results.\n\n"
        "Test: {test_name}\n"
        "Value: {value} {unit}\n"
        "Critical Range: {critical_range}\n\n"
        "Please contact your doctor IMMEDIATELY:\n"
        "Dr. {doctor_name}\n"
        "Phone: {doctor_phone}\n\n"
        "This may require urgent medical attention."
    )

    ABNORMAL_RESULT_TEMPLATE = (
        "LAB RESULT - ABNORMAL VALUE\n\n"
        "Dear {patient_name},\n\n"
        "Your lab results show an abnormal value:\n"
        "Test: {test_name}\n"
        "Value: {value} {unit} (Abnormal)\n"
        "{explanation}\n\n"
        "Please log in to the patient portal for details:\n"
        "{portal_link}\n\n"
        "Recommendation: {recommendation}"
    )

    NORMAL_RESULT_TEMPLATE = (
        "LAB RESULT - NORMAL\n\n"
        "Dear {patient_name},\n\n"
        "Your lab results are ready and all values are within normal range.\n\n"
        "Tests: {test_names}\n"
        "Completed: {completion_date}\n\n"
        "Please log in to the patient portal to view:\n"
        "{portal_link}"
    )

    def __init__(self, db):
        self.db = db
        self.preference_manager = get_preference_manager(db)

    async def notify_results_ready(self, result_data):
        """Notify patient that lab results are ready

        Args:
            result_data: Dictionary with result details
                - patient_id, patient_name
                - result_id, test_names (list)
                - completion_date
                - doctor_name, doctor_phone
                - has_critical_values (bool)
                - has_abnormal_values (bool)

        Returns:
            Notification ID or None
        """
        try:
            # Check patient preferences
            enabled_channels = await self.preference_manager.get_enabled_channels(
                result_data.get("patient_id"),
                "patient",
                "lab_result"
            )

            if not enabled_channels:
                logger.info("Patient {} has opted out of lab result notifications".format(
                    result_data.get("patient_id")
                ))
                return None

            # Determine message type based on results
            has_critical = result_data.get("has_critical_values", False)
            has_abnormal = result_data.get("has_abnormal_values", False)

            if has_critical:
                # Send critical value alert (separate notification)
                await self._send_critical_value_alert(result_data)

            # Send result ready notification
            test_names = result_data.get("test_names", [])
            if isinstance(test_names, list):
                if len(test_names) > 3:
                    test_list = ", ".join(test_names[:3]) + " + {} more".format(len(test_names) - 3)
                else:
                    test_list = ", ".join(test_names)
            else:
                test_list = str(test_names)

            message = self.RESULT_READY_TEMPLATE.format(
                patient_name=result_data.get("patient_name"),
                test_names=test_list,
                completion_date=result_data.get("completion_date", datetime.utcnow().strftime("%Y-%m-%d")),
                portal_link=result_data.get("portal_link", "https://portal.simrs.hospital/lab-results")
            )

            # Determine priority
            if has_critical:
                priority = self.CRITICAL_VALUE_PRIORITY
                title = "CRITICAL: Lab Results Ready"
            elif has_abnormal:
                priority = self.ABNORMAL_VALUE_PRIORITY
                title = "Lab Results Ready (Abnormal)"
            else:
                priority = self.NORMAL_VALUE_PRIORITY
                title = "Lab Results Ready"

            # Send to enabled channels
            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=result_data.get("patient_id"),
                    user_type="patient",
                    notification_type=NotificationType.LAB_RESULT,
                    channel=channel,
                    priority=priority,
                    status=NotificationStatus.PENDING,
                    title=title,
                    message=message,
                    metadata={
                        "result_id": result_data.get("result_id"),
                        "patient_id": result_data.get("patient_id"),
                        "patient_name": result_data.get("patient_name"),
                        "test_names": test_names,
                        "has_critical_values": has_critical,
                        "has_abnormal_values": has_abnormal,
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent lab result notification to patient {} for result {}".format(
                    result_data.get("patient_id"), result_data.get("result_id")
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending lab result notification: {}".format(e))
            await self.db.rollback()
            return None

    async def _send_critical_value_alert(self, result_data):
        """Send critical value alert to patient

        Critical values are sent via all available channels immediately.
        """
        try:
            # Send to all channels regardless of preferences
            channels = [
                NotificationChannel.SMS,
                NotificationChannel.PUSH,
                NotificationChannel.IN_APP,
                NotificationChannel.EMAIL
            ]

            # Use first critical value if available
            critical_values = result_data.get("critical_values", [])
            if critical_values:
                cv = critical_values[0]
                message = self.CRITICAL_VALUE_TEMPLATE.format(
                    patient_name=result_data.get("patient_name"),
                    test_name=cv.get("test_name", "Lab Test"),
                    value=cv.get("value", ""),
                    unit=cv.get("unit", ""),
                    critical_range=cv.get("critical_range", ""),
                    doctor_name=result_data.get("doctor_name", "Your Doctor"),
                    doctor_phone=result_data.get("doctor_phone", "Contact hospital")
                )
            else:
                message = self.CRITICAL_VALUE_TEMPLATE.format(
                    patient_name=result_data.get("patient_name"),
                    test_name="Lab Test",
                    value="",
                    unit="",
                    critical_range="Critical value detected",
                    doctor_name=result_data.get("doctor_name", "Your Doctor"),
                    doctor_phone=result_data.get("doctor_phone", "Contact hospital")
                )

            # Send to all channels
            for channel in channels:
                notification = Notification(
                    recipient_id=result_data.get("patient_id"),
                    user_type="patient",
                    notification_type=NotificationType.LAB_RESULT,
                    channel=channel,
                    priority=self.CRITICAL_VALUE_PRIORITY,
                    status=NotificationStatus.PENDING,
                    title="CRITICAL: Lab Value Alert",
                    message=message,
                    metadata={
                        "result_id": result_data.get("result_id"),
                        "patient_id": result_data.get("patient_id"),
                        "alert_type": "critical_value",
                        "critical_values": critical_values,
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()

            logger.warning(
                "Sent critical value alert to patient {} for result {}".format(
                    result_data.get("patient_id"), result_data.get("result_id")
                )
            )

        except Exception as e:
            logger.error("Error sending critical value alert: {}".format(e))

    async def send_abnormal_result_alert(self, result_data, abnormal_value):
        """Send alert for specific abnormal result

        Args:
            result_data: Result information
            abnormal_value: Details of abnormal value
                - test_name, value, unit, explanation, recommendation

        Returns:
            Notification ID or None
        """
        try:
            # Check preferences
            enabled_channels = await self.preference_manager.get_enabled_channels(
                result_data.get("patient_id"),
                "patient",
                "lab_result"
            )

            if not enabled_channels:
                return None

            message = self.ABNORMAL_RESULT_TEMPLATE.format(
                patient_name=result_data.get("patient_name"),
                test_name=abnormal_value.get("test_name", "Lab Test"),
                value=abnormal_value.get("value", ""),
                unit=abnormal_value.get("unit", ""),
                explanation=abnormal_value.get("explanation", "Value outside normal range"),
                recommendation=abnormal_value.get("recommendation", "Please consult your doctor"),
                portal_link=result_data.get("portal_link", "https://portal.simrs.hospital/lab-results")
            )

            # Send to enabled channels
            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=result_data.get("patient_id"),
                    user_type="patient",
                    notification_type=NotificationType.LAB_RESULT,
                    channel=channel,
                    priority=self.ABNORMAL_VALUE_PRIORITY,
                    status=NotificationStatus.PENDING,
                    title="Abnormal Lab Result Alert",
                    message=message,
                    metadata={
                        "result_id": result_data.get("result_id"),
                        "test_name": abnormal_value.get("test_name"),
                        "value": abnormal_value.get("value"),
                        "abnormal_type": "abnormal_value",
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent abnormal result alert to patient {} for test {}".format(
                    result_data.get("patient_id"), abnormal_value.get("test_name")
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending abnormal result alert: {}".format(e))
            await self.db.rollback()
            return None

    async def send_normal_result_summary(self, result_data):
        """Send summary for all normal results

        Args:
            result_data: Result information

        Returns:
            Notification ID or None
        """
        try:
            # Check preferences
            enabled_channels = await self.preference_manager.get_enabled_channels(
                result_data.get("patient_id"),
                "patient",
                "lab_result"
            )

            if not enabled_channels:
                return None

            test_names = result_data.get("test_names", [])
            if isinstance(test_names, list):
                test_list = ", ".join(test_names[:5])  # Limit to 5 tests
            else:
                test_list = str(test_names)

            message = self.NORMAL_RESULT_TEMPLATE.format(
                patient_name=result_data.get("patient_name"),
                test_names=test_list,
                completion_date=result_data.get("completion_date", datetime.utcnow().strftime("%Y-%m-%d")),
                portal_link=result_data.get("portal_link", "https://portal.simrs.hospital/lab-results")
            )

            # Send to enabled channels (typically lower priority)
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=result_data.get("patient_id"),
                    user_type="patient",
                    notification_type=NotificationType.LAB_RESULT,
                    channel=channel,
                    priority=self.NORMAL_VALUE_PRIORITY,
                    status=NotificationStatus.PENDING,
                    title="Lab Results Ready (Normal)",
                    message=message,
                    metadata={
                        "result_id": result_data.get("result_id"),
                        "test_names": test_names,
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()

            await self.db.commit()

            return notification.id

        except Exception as e:
            logger.error("Error sending normal result summary: {}".format(e))
            await self.db.rollback()
            return None

    async def notify_doctor_of_critical_value(self, result_data, critical_value):
        """Notify ordering doctor about critical value

        Args:
            result_data: Result information
            critical_value: Critical value details

        Returns:
            Notification ID or None
        """
        try:
            message = (
                "PATIENT CRITICAL VALUE NOTIFICATION\n\n"
                "Patient: {patient_name} (ID: {patient_id})\n"
                "MRN: {mrn}\n\n"
                "CRITICAL VALUE DETECTED:\n"
                "Test: {test_name}\n"
                "Value: {value} {unit}\n"
                "Critical Range: {critical_range}\n\n"
                "Patient has been notified.\n"
                "Please follow up with the patient.\n\n"
                "Result Date: {result_date}"
            ).format(
                patient_name=result_data.get("patient_name"),
                patient_id=result_data.get("patient_id"),
                mrn=result_data.get("mrn", "N/A"),
                test_name=critical_value.get("test_name", "Lab Test"),
                value=critical_value.get("value", ""),
                unit=critical_value.get("unit", ""),
                critical_range=critical_value.get("critical_range", ""),
                result_date=result_data.get("completion_date", datetime.utcnow().strftime("%Y-%m-%d"))
            )

            notification = Notification(
                recipient_id=result_data.get("doctor_id"),
                user_type="doctor",
                notification_type=NotificationType.LAB_RESULT,
                channel=NotificationChannel.IN_APP,
                priority=NotificationPriority.URGENT,
                status=NotificationStatus.PENDING,
                title="Patient Critical Value - " + critical_value.get("test_name", "Lab Test"),
                message=message,
                metadata={
                    "patient_id": result_data.get("patient_id"),
                    "result_id": result_data.get("result_id"),
                    "critical_value": critical_value,
                    "alert_type": "critical_value_doctor_notification"
                },
                scheduled_at=datetime.utcnow()
            )
            self.db.add(notification)
            await self.db.flush()

            logger.info(
                "Notified doctor {} of critical value for patient {}".format(
                    result_data.get("doctor_id"), result_data.get("patient_id")
                )
            )

            return notification.id

        except Exception as e:
            logger.error("Error notifying doctor of critical value: {}".format(e))
            return None

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


def get_lab_result_notification_service(db):
    """Get or create lab result notification service instance

    Args:
        db: Database session

    Returns:
        LabResultNotificationService instance
    """
    return LabResultNotificationService(db)
