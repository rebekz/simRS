"""Medication Reminder Service

STORY-022-03: Medication Reminders
Service for scheduling and managing medication reminders with adherence tracking.

Python 3.5+ compatible
"""

import logging
from datetime import datetime, timedelta, time
from typing import Optional, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

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


class MedicationReminderService(object):
    """Service for medication reminders and adherence tracking"""

    # Reminder times
    MORNING_TIME = time(8, 0)    # 8:00 AM
    AFTERNOON_TIME = time(13, 0)  # 1:00 PM
    EVENING_TIME = time(20, 0)    # 8:00 PM

    # Adherence tracking thresholds
    ADHERENCE_WARNING_THRESHOLD = 80  # Alert if below 80%
    LOW_SUPPLY_THRESHOLD = 3          # Days

    # Message templates
    MEDICATION_REMINDER_TEMPLATE = (
        "MEDICATION REMINDER\n\n"
        "Dear {patient_name},\n\n"
        "It's time to take your medication:\n"
        "{medication_name} - {dosage}\n"
        "{instructions}\n\n"
        "Remaining supply: {days_remaining} days\n\n"
        "Please confirm by replying TAKEN."
    )

    REFILL_REMINDER_TEMPLATE = (
        "MEDICATION REFILL REMINDER\n\n"
        "Dear {patient_name},\n\n"
        "Your medication supply is running low:\n"
        "{medication_name} - {dosage}\n\n"
        "Remaining: {days_remaining} days\n"
        "Please contact your pharmacy to refill.\n"
        "Pharmacy: {pharmacy_name}\n"
        "Phone: {pharmacy_phone}\n\n"
        "Prescription #: {prescription_number}"
    )

    ANTIBIOTIC_COMPLETION_TEMPLATE = (
        "ANTIBIOTIC COURSE REMINDER\n\n"
        "Dear {patient_name},\n\n"
        "Please complete your full antibiotic course:\n"
        "{medication_name}\n\n"
        "{days_remaining} days remaining.\n\n"
        "Even if you feel better, complete the full course\n"
        "to prevent antibiotic resistance.\n\n"
        "Contact your doctor if you have questions."
    )

    INTERACTION_WARNING_TEMPLATE = (
        "MEDICATION INTERACTION WARNING\n\n"
        "Dear {patient_name},\n\n"
        "A new medication ({new_medication}) may interact\n"
        "with your current medication ({existing_medication}).\n\n"
        "Interaction: {interaction_type}\n"
        "Severity: {severity}\n\n"
        "Please contact your doctor before taking both medications.\n"
        "Doctor: {doctor_name}\n"
        "Phone: {doctor_phone}"
    )

    ALLERGY_ALERT_TEMPLATE = (
        "ALLERGY ALERT - MEDICATION\n\n"
        "Dear {patient_name},\n\n"
        "ALERT: A prescribed medication may trigger your allergy.\n\n"
        "Medication: {medication_name}\n"
        "Your Allergy: {allergen}\n"
        "Severity: {severity}\n\n"
        "Please inform your doctor immediately.\n"
        "Doctor: {doctor_name}\n"
        "Phone: {doctor_phone}\n\n"
        "DO NOT take this medication until cleared by your doctor."
    )

    def __init__(self, db):
        self.db = db
        self.preference_manager = get_preference_manager(db)

    async def schedule_medication_reminders(self, prescription_data):
        """Schedule reminders for a medication prescription

        Args:
            prescription_data: Dictionary with prescription details
                - patient_id, patient_name
                - prescription_id, medication_name, dosage
                - frequency (daily, bid, tid, qid, prn)
                - duration_days
                - instructions
                - supply_days_remaining

        Returns:
            Dictionary with scheduled reminder IDs
        """
        try:
            frequency = prescription_data.get("frequency", "daily")
            duration = prescription_data.get("duration_days", 30)
            start_date = prescription_data.get("start_date", datetime.utcnow().date())

            # Determine reminder times based on frequency
            reminder_times = self._get_reminder_times(frequency)

            scheduled = {}

            # Schedule reminders for each day of duration
            for day_offset in range(duration):
                reminder_date = start_date + timedelta(days=day_offset)

                # Skip past dates
                if reminder_date < datetime.utcnow().date():
                    continue

                for reminder_time in reminder_times:
                    scheduled_at = datetime.combine(reminder_date, reminder_time)

                    # Skip if time has passed today
                    if scheduled_at < datetime.utcnow():
                        continue

                    notification_id = await self._schedule_reminder(
                        prescription_data,
                        scheduled_at,
                        "medication_reminder"
                    )

                    key = "{date}_{time}".format(
                        date=reminder_date.isoformat(),
                        time=reminder_time.strftime("%H%M")
                    )
                    scheduled[key] = notification_id

            # Schedule refill reminder
            supply_days = prescription_data.get("supply_days_remaining", duration)
            if supply_days > self.LOW_SUPPLY_THRESHOLD:
                refill_date = start_date + timedelta(days=supply_days - self.LOW_SUPPLY_THRESHOLD)
                refill_at = datetime.combine(refill_date, self.MORNING_TIME)

                if refill_at > datetime.utcnow():
                    notification_id = await self._schedule_reminder(
                        prescription_data,
                        refill_at,
                        "refill_reminder"
                    )
                    scheduled["refill"] = notification_id

            logger.info(
                "Scheduled {} medication reminders for prescription {}".format(
                    len(scheduled), prescription_data.get("prescription_id")
                )
            )

            return scheduled

        except Exception as e:
            logger.error("Error scheduling medication reminders: {}".format(e))
            return {}

    async def send_adherence_alert(self, patient_id, patient_name, doctor_id, adherence_rate):
        """Send alert to doctor if patient adherence is low

        Args:
            patient_id: Patient ID
            patient_name: Patient name
            doctor_id: Doctor ID
            adherence_rate: Adherence percentage

        Returns:
            Notification ID or None
        """
        try:
            if adherence_rate >= self.ADHERENCE_WARNING_THRESHOLD:
                return None

            message = (
                "MEDICATION ADHERENCE ALERT\n\n"
                "Patient: {patient_name} (ID: {patient_id})\n"
                "Adherence Rate: {adherence_rate}%\n\n"
                "Patient's medication adherence is below threshold.\n"
                "Please follow up with the patient.\n\n"
                "Threshold: {threshold}%"
            ).format(
                patient_name=patient_name,
                patient_id=patient_id,
                adherence_rate=int(adherence_rate),
                threshold=self.ADHERENCE_WARNING_THRESHOLD
            )

            notification = Notification(
                recipient_id=doctor_id,
                user_type="doctor",
                notification_type=NotificationType.MEDICATION_REMINDER,
                channel=NotificationChannel.IN_APP,
                priority=NotificationPriority.HIGH,
                status=NotificationStatus.PENDING,
                title="Low Medication Adherence Alert",
                message=message,
                metadata={
                    "patient_id": patient_id,
                    "patient_name": patient_name,
                    "adherence_rate": adherence_rate,
                    "alert_type": "low_adherence"
                },
                scheduled_at=datetime.utcnow()
            )
            self.db.add(notification)
            await self.db.flush()

            logger.info(
                "Sent adherence alert for patient {} to doctor {}".format(
                    patient_id, doctor_id
                )
            )

            return notification.id

        except Exception as e:
            logger.error("Error sending adherence alert: {}".format(e))
            return None

    async def send_interaction_warning(self, patient_data, new_medication, existing_medication, interaction):
        """Send warning about potential drug interaction

        Args:
            patient_data: Patient information
            new_medication: New medication details
            existing_medication: Existing medication details
            interaction: Interaction details

        Returns:
            Notification ID or None
        """
        try:
            # Check if patient wants medication reminders
            enabled_channels = await self.preference_manager.get_enabled_channels(
                patient_data.get("patient_id"),
                "patient",
                "medication_reminder"
            )

            if not enabled_channels:
                return None

            message = self.INTERACTION_WARNING_TEMPLATE.format(
                patient_name=patient_data.get("patient_name"),
                new_medication=new_medication.get("name"),
                existing_medication=existing_medication.get("name"),
                interaction_type=interaction.get("type", "Unknown"),
                severity=interaction.get("severity", "Unknown"),
                doctor_name=patient_data.get("doctor_name", "Your Doctor"),
                doctor_phone=patient_data.get("doctor_phone", "Contact your doctor")
            )

            # Send to all enabled channels
            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=patient_data.get("patient_id"),
                    user_type="patient",
                    notification_type=NotificationType.MEDICATION_REMINDER,
                    channel=channel,
                    priority=NotificationPriority.URGENT,
                    status=NotificationStatus.PENDING,
                    title="Drug Interaction Warning",
                    message=message,
                    metadata={
                        "patient_id": patient_data.get("patient_id"),
                        "new_medication": new_medication,
                        "existing_medication": existing_medication,
                        "interaction": interaction,
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            logger.info(
                "Sent interaction warning to patient {}".format(
                    patient_data.get("patient_id")
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending interaction warning: {}".format(e))
            return None

    async def send_allergy_alert(self, patient_data, medication, allergy):
        """Send alert about medication allergy

        Args:
            patient_data: Patient information
            medication: Medication details
            allergy: Allergy details

        Returns:
            Notification ID or None
        """
        try:
            # Allergy alerts should always be sent regardless of preferences
            message = self.ALLERGY_ALERT_TEMPLATE.format(
                patient_name=patient_data.get("patient_name"),
                medication_name=medication.get("name"),
                allergen=allergy.get("allergen"),
                severity=allergy.get("severity", "Unknown"),
                doctor_name=patient_data.get("doctor_name", "Your Doctor"),
                doctor_phone=patient_data.get("doctor_phone", "Contact your doctor")
            )

            # Send via all critical channels
            channels = [NotificationChannel.SMS, NotificationChannel.PUSH, NotificationChannel.IN_APP]

            notification_ids = []
            for channel in channels:
                notification = Notification(
                    recipient_id=patient_data.get("patient_id"),
                    user_type="patient",
                    notification_type=NotificationType.MEDICATION_REMINDER,
                    channel=channel,
                    priority=NotificationPriority.URGENT,
                    status=NotificationStatus.PENDING,
                    title="ALLERGY ALERT - Do Not Take",
                    message=message,
                    metadata={
                        "patient_id": patient_data.get("patient_id"),
                        "medication": medication,
                        "allergy": allergy,
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            # Also alert doctor
            doctor_notification = Notification(
                recipient_id=patient_data.get("doctor_id"),
                user_type="doctor",
                notification_type=NotificationType.MEDICATION_REMINDER,
                channel=NotificationChannel.IN_APP,
                priority=NotificationPriority.URGENT,
                status=NotificationStatus.PENDING,
                title="Patient Allergy Alert",
                message=(
                    "ALLERGY ALERT\n\n"
                    "Patient: {patient_name}\n"
                    "Prescribed medication: {medication}\n"
                    "Patient allergy: {allergen}\n\n"
                    "Please review and prescribe alternative."
                ).format(
                    patient_name=patient_data.get("patient_name"),
                    medication=medication.get("name"),
                    allergen=allergy.get("allergen")
                ),
                metadata={
                    "patient_id": patient_data.get("patient_id"),
                    "medication": medication,
                    "allergy": allergy,
                },
                scheduled_at=datetime.utcnow()
            )
            self.db.add(doctor_notification)
            await self.db.flush()

            logger.warning(
                "Sent allergy alert for patient {} medication {}".format(
                    patient_data.get("patient_id"), medication.get("name")
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending allergy alert: {}".format(e))
            return None

    async def cancel_medication_reminders(self, prescription_id):
        """Cancel all pending reminders for a prescription

        Args:
            prescription_id: Prescription ID

        Returns:
            Number of reminders cancelled
        """
        try:
            # Find all pending reminders for this prescription
            query = select(Notification).where(
                and_(
                    Notification.notification_type == NotificationType.MEDICATION_REMINDER,
                    Notification.status == NotificationStatus.PENDING,
                    Notification.metadata["prescription_id"].astext == str(prescription_id)
                )
            )
            result = await self.db.execute(query)
            notifications = result.scalars().all()

            # Cancel each reminder
            cancelled = 0
            for notification in notifications:
                notification.status = NotificationStatus.CANCELLED
                notification.updated_at = datetime.utcnow()
                cancelled += 1

            await self.db.commit()

            logger.info(
                "Cancelled {} medication reminders for prescription {}".format(
                    cancelled, prescription_id
                )
            )

            return cancelled

        except Exception as e:
            logger.error("Error cancelling reminders: {}".format(e))
            await self.db.rollback()
            return 0

    def _get_reminder_times(self, frequency):
        """Get reminder times based on medication frequency

        Args:
            frequency: Medication frequency (daily, bid, tid, qid, prn)

        Returns:
            List of time objects
        """
        if frequency == "daily" or frequency == "qd":
            return [self.MORNING_TIME]
        elif frequency == "bid" or frequency == "b.i.d.":
            return [self.MORNING_TIME, self.EVENING_TIME]
        elif frequency == "tid" or frequency == "t.i.d.":
            return [self.MORNING_TIME, self.AFTERNOON_TIME, self.EVENING_TIME]
        elif frequency == "qid" or frequency == "q.i.d.":
            return [self.MORNING_TIME, self.AFTERNOON_TIME, self.EVENING_TIME, time(23, 59)]
        else:
            return [self.MORNING_TIME]

    async def _schedule_reminder(self, prescription_data, scheduled_at, reminder_type):
        """Schedule a medication reminder

        Args:
            prescription_data: Prescription details
            scheduled_at: When to send
            reminder_type: Type of reminder

        Returns:
            Notification ID or None
        """
        try:
            # Format message based on type
            if reminder_type == "refill_reminder":
                message = self.REFILL_REMINDER_TEMPLATE.format(
                    patient_name=prescription_data.get("patient_name"),
                    medication_name=prescription_data.get("medication_name"),
                    dosage=prescription_data.get("dosage"),
                    days_remaining=prescription_data.get("supply_days_remaining", 3),
                    pharmacy_name=prescription_data.get("pharmacy_name", "Hospital Pharmacy"),
                    pharmacy_phone=prescription_data.get("pharmacy_phone", "123-456-7890"),
                    prescription_number=prescription_data.get("prescription_number", "N/A")
                )
            else:
                message = self.MEDICATION_REMINDER_TEMPLATE.format(
                    patient_name=prescription_data.get("patient_name"),
                    medication_name=prescription_data.get("medication_name"),
                    dosage=prescription_data.get("dosage"),
                    instructions=prescription_data.get("instructions", "Take as prescribed"),
                    days_remaining=prescription_data.get("supply_days_remaining", 30)
                )

            notification = Notification(
                recipient_id=prescription_data.get("patient_id"),
                user_type="patient",
                notification_type=NotificationType.MEDICATION_REMINDER,
                channel=NotificationChannel.SMS,
                priority=NotificationPriority.NORMAL,
                status=NotificationStatus.PENDING,
                title="Medication Reminder" if reminder_type == "medication_reminder" else "Refill Reminder",
                message=message,
                scheduled_at=scheduled_at,
                metadata={
                    "prescription_id": prescription_data.get("prescription_id"),
                    "medication_name": prescription_data.get("medication_name"),
                    "reminder_type": reminder_type,
                    "patient_name": prescription_data.get("patient_name"),
                }
            )
            self.db.add(notification)
            await self.db.flush()

            return notification.id

        except Exception as e:
            logger.error("Error scheduling reminder: {}".format(e))
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


def get_medication_reminder_service(db):
    """Get or create medication reminder service instance

    Args:
        db: Database session

    Returns:
        MedicationReminderService instance
    """
    return MedicationReminderService(db)
