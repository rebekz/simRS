"""Appointment Reminder Service for STORY-022-04

This service provides:
- Automatic reminder scheduling when appointments are booked
- Multi-channel reminder delivery (SMS, WhatsApp, Email, Push)
- Patient reply processing for confirmations
- Appointment confirmation notifications
"""
from datetime import datetime, timedelta, date, time as dt_time
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
import json

from app.models.appointments import (
    Appointment,
    AppointmentReminder,
    ReminderType,
    ReminderStatus,
    AppointmentStatus,
)
from app.models.patient import Patient
from app.models.notification_templates import NotificationTemplate
from app.models.notifications import (
    Notification,
    NotificationPreference,
    NotificationLog,
)
from app.models.user import User
from app.models.hospital import Department


class AppointmentReminderService:
    """Service for managing appointment reminders and confirmations

    Features:
    - Schedule reminders automatically when appointments are created
    - Send reminders at configured intervals (24 hours, 2 hours before)
    - Send immediate confirmation on booking
    - Process patient replies (confirm, cancel, reschedule)
    - Support multiple channels (SMS, WhatsApp, Email, Push)
    """

    # Default reminder times before appointment
    DEFAULT_REMINDER_HOURS = [24, 2]  # 24 hours and 2 hours before

    # Reminder message templates (Indonesian)
    TEMPLATES = {
        "confirmation_id": "Halo {patient_name}, janji temu Anda telah TERKONFIRMASI.\n\nDetail:\n- Tanggal: {appointment_date}\n- Jam: {appointment_time}\n- Dokter: {doctor_name}\n- Poli: {department}\n- No. Antrian: {queue_number}\n\nSilakan datang 15 menit sebelum jadwal.",
        "confirmation_id_short": "JANJI TEMU TERKONFIRMASI: {appointment_date} jam {appointment_time} dg {doctor_name} di {department}. No. Antrian: {queue_number}",
        "reminder_24h_id": "PENGINGAT: Anda punya janji temu BESOK jam {appointment_time} dengan {doctor_name} di {department}. No. Antrian: {queue_number}. Reply: YA untuk hadir, BATAL untuk batalkan.",
        "reminder_2h_id": "PENGINGAT: Janji temu Anda dalam 2 jam ({appointment_time}) dengan {doctor_name} di {department}. No. Antrian: {queue_number}. Silakan menuju {department}.",
        "reminder_24h_en": "REMINDER: You have an appointment TOMORROW at {appointment_time} with Dr. {doctor_name} at {department}. Queue No: {queue_number}. Reply: YES to confirm, CANCEL to reschedule.",
        "reminder_2h_en": "REMINDER: Your appointment is in 2 hours ({appointment_time}) with Dr. {doctor_name} at {department}. Queue No: {queue_number}. Please proceed to {department}.",
        "cancelled_id": "Janji temu Anda pada {appointment_date} jam {appointment_time} dengan {doctor_name} telah DIBATALKAN. Untuk jadwal baru, silakan hubungi rumah sakit.",
        "rescheduled_id": "Janji temu Anda telah DIJADWALKAN ULANG.\n\nBaru:\n- Tanggal: {appointment_date}\n- Jam: {appointment_time}\n- Dokter: {doctor_name}\n- Poli: {department}\n\nNo. Antrian: {queue_number}",
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def schedule_appointment_reminders(
        self,
        appointment: Appointment
    ) -> List[AppointmentReminder]:
        """Schedule reminders for a newly created appointment

        Args:
            appointment: The appointment object

        Returns:
            List of created reminder records
        """
        # Combine date and time to get full appointment datetime
        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.appointment_time
        )

        # Schedule reminders at configured intervals
        reminders = []
        for hours_before in self.DEFAULT_REMINDER_HOURS:
            reminder_time = appointment_datetime - timedelta(hours=hours_before)

            # Only schedule if reminder time is in the future
            if reminder_time > datetime.now():
                # Create reminder for each enabled channel
                for reminder_type in [ReminderType.SMS, ReminderType.WHATSAPP, ReminderType.EMAIL]:
                    # Check if patient has this channel enabled
                    if await self._is_channel_enabled(appointment.patient_id, reminder_type.value):
                        reminder = AppointmentReminder(
                            appointment_id=appointment.id,
                            reminder_type=reminder_type,
                            scheduled_at=reminder_time,
                            status=ReminderStatus.PENDING,
                        )
                        self.db.add(reminder)
                        reminders.append(reminder)

        await self.db.flush()

        # Also send immediate confirmation
        await self._send_confirmation_notification(appointment)

        return reminders

    async def send_pending_reminders(
        self,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Background job to send pending reminders

        Args:
            limit: Maximum number of reminders to process

        Returns:
            Dict with processing statistics
        """
        # Query pending reminders that are due
        query = (
            select(AppointmentReminder)
            .options(selectinload(AppointmentReminder.appointment))
            .where(
                and_(
                    AppointmentReminder.status == ReminderStatus.PENDING,
                    AppointmentReminder.scheduled_at <= datetime.now(),
                )
            )
            .limit(limit)
        )

        result = await self.db.execute(query)
        reminders = result.scalars().all()

        sent_count = 0
        failed_count = 0

        for reminder in reminders:
            try:
                # Get appointment with patient data
                appointment = reminder.appointment

                # Skip if appointment is cancelled
                if appointment.status == AppointmentStatus.CANCELLED:
                    reminder.status = ReminderStatus.FAILED
                    reminder.error_message = "Appointment cancelled"
                    continue

                # Send the reminder
                await self._send_reminder(reminder, appointment)
                reminder.status = ReminderStatus.SENT
                reminder.sent_at = datetime.now()
                sent_count += 1

            except Exception as e:
                reminder.status = ReminderStatus.FAILED
                reminder.error_message = str(e)
                reminder.retry_count += 1
                failed_count += 1

        await self.db.commit()

        return {
            "processed": len(reminders),
            "sent": sent_count,
            "failed": failed_count,
            "message": "Processed {count} reminders: {sent} sent, {failed} failed".format(
                count=len(reminders),
                sent=sent_count,
                failed=failed_count
            )
        }

    async def process_reply_message(
        self,
        phone_number: str,
        message: str
    ) -> Dict[str, Any]:
        """Process patient reply to appointment reminder

        Supported keywords (case-insensitive):
        - YA, YES, OK, HADIR: Confirm appointment
        - BATAL, CANCEL, NO: Cancel appointment
        - JADWAL, RESCHEDULE: Request reschedule

        Args:
            phone_number: Patient's phone number
            message: Reply message content

        Returns:
            Dict with processing result
        """
        # Normalize message
        msg_lower = message.strip().lower()

        # Find patient by phone number
        patient_result = await self.db.execute(
            select(Patient).where(Patient.phone == phone_number)
        )
        patient = patient_result.scalar_one_or_none()

        if not patient:
            return {
                "success": False,
                "message": "Nomor telepon tidak terdaftar dalam sistem kami."
            }

        # Find upcoming appointment for this patient
        appointment_result = await self.db.execute(
            select(Appointment)
            .where(
                and_(
                    Appointment.patient_id == patient.id,
                    Appointment.appointment_date >= date.today(),
                    Appointment.status.in_([
                        AppointmentStatus.SCHEDULED,
                        AppointmentStatus.CONFIRMED
                    ])
                )
            )
            .order_by(Appointment.appointment_date.asc())
            .limit(1)
        )
        appointment = appointment_result.scalar_one_or_none()

        if not appointment:
            return {
                "success": False,
                "message": "Tidak ada janji temu yang akan datang untuk nomor ini."
            }

        # Process the reply
        if msg_lower in ["ya", "yes", "ok", "hadir", "confirm", "confirmed"]:
            # Confirm appointment
            appointment.status = AppointmentStatus.CONFIRMED
            response_message = "Terima kasih. Kehadiran Anda untuk janji temu pada {date} jam {time} telah dikonfirmasi.".format(
                date=appointment.appointment_date,
                time=appointment.appointment_time
            )

        elif msg_lower in ["batal", "cancel", "no", "tidak"]:
            # Cancel appointment
            appointment.status = AppointmentStatus.CANCELLED
            appointment.cancellation_reason = "Dibatalkan melalui SMS"
            appointment.cancelled_at = datetime.now()
            response_message = "Janji temu Anda pada {date} jam {time} telah dibatalkan. Untuk jadwal baru, silakan hubungi rumah sakit.".format(
                date=appointment.appointment_date,
                time=appointment.appointment_time
            )

            # Cancel remaining reminders
            await self._cancel_appointment_reminders(appointment.id)

        elif msg_lower in ["jadwal", "reschedule", "ubah"]:
            # Request reschedule
            response_message = "Untuk mengubah jadwal janji temu Anda, silakan hubungi rumah sakit atau login ke portal pasien. Janji temu saat ini: {date} jam {time}.".format(
                date=appointment.appointment_date,
                time=appointment.appointment_time
            )

        else:
            # Unknown command
            response_message = "Pesan tidak dikenali. Reply: YA untuk hadir, BATAL untuk batalkan, JADWAL untuk mengubah jadwal."

        await self.db.commit()

        return {
            "success": True,
            "appointment_id": appointment.id,
            "appointment_number": appointment.appointment_number,
            "status": appointment.status.value,
            "message": response_message
        }

    async def get_reminder_templates(
        self,
        language: str = "id"
    ) -> Dict[str, str]:
        """Get all reminder templates for a language

        Args:
            language: Language code (id, en)

        Returns:
            Dict of template names to templates
        """
        templates = {}
        suffix = "_{language}".format(language=language)

        for key, template in self.TEMPLATES.items():
            if key.endswith(suffix):
                templates[key] = template

        return templates

    async def _send_confirmation_notification(
        self,
        appointment: Appointment
    ) -> None:
        """Send immediate confirmation notification for new appointment

        Args:
            appointment: The appointment object
        """
        # Get patient data
        patient_result = await self.db.execute(
            select(Patient).where(Patient.id == appointment.patient_id)
        )
        patient = patient_result.scalar_one_or_none()

        if not patient:
            return

        # Get doctor data
        doctor_name = "Dokter"
        if appointment.doctor_id:
            doctor_result = await self.db.execute(
                select(User).where(User.id == appointment.doctor_id)
            )
            doctor = doctor_result.scalar_one_or_none()
            if doctor:
                doctor_name = "dr. {name}".format(name=doctor.last_name or doctor.first_name)

        # Get department data
        department_result = await self.db.execute(
            select(Department).where(Department.id == appointment.department_id)
        )
        department = department_result.scalar_one_or_none()
        department_name = department.name if department else "Poli"

        # Prepare template variables
        variables = {
            "patient_name": patient.first_name or "",
            "appointment_date": appointment.appointment_date.strftime("%d/%m/%Y"),
            "appointment_time": appointment.appointment_time.strftime("%H:%M"),
            "doctor_name": doctor_name,
            "department": department_name,
            "queue_number": appointment.queue_number or "Akan diberikan saat check-in",
        }

        # Send to enabled channels
        channels_to_send = []

        # Check preferences and send to enabled channels
        if await self._is_channel_enabled(appointment.patient_id, "sms"):
            channels_to_send.append(("sms", patient.phone))

        if await self._is_channel_enabled(appointment.patient_id, "email"):
            channels_to_send.append(("email", patient.email))

        if await self._is_channel_enabled(appointment.patient_id, "whatsapp"):
            channels_to_send.append(("whatsapp", patient.phone))

        for channel, recipient in channels_to_send:
            # Create notification record
            notification = Notification(
                recipient_id=appointment.patient_id,
                recipient_type="patient",
                notification_type="appointment_reminder",
                channel=channel,
                status="pending",
                priority="normal",
                subject="Konfirmasi Janji Temu",
                content=self._format_confirmation_message(variables, is_short=channel == "sms"),
                metadata={
                    "appointment_id": appointment.id,
                    "appointment_number": appointment.appointment_number,
                    "type": "confirmation",
                },
                scheduled_at=datetime.now(),
            )
            self.db.add(notification)

    async def _send_reminder(
        self,
        reminder: AppointmentReminder,
        appointment: Appointment
    ) -> None:
        """Send a reminder notification

        Args:
            reminder: The reminder record
            appointment: The appointment object
        """
        # Get patient data
        patient_result = await self.db.execute(
            select(Patient).where(Patient.id == appointment.patient_id)
        )
        patient = patient_result.scalar_one_or_none()

        if not patient:
            raise ValueError("Patient {patient_id} not found".format(patient_id=appointment.patient_id))

        # Get doctor data
        doctor_name = "Dokter"
        if appointment.doctor_id:
            doctor_result = await self.db.execute(
                select(User).where(User.id == appointment.doctor_id)
            )
            doctor = doctor_result.scalar_one_or_none()
            if doctor:
                doctor_name = "dr. {name}".format(name=doctor.last_name or doctor.first_name)

        # Get department data
        department_result = await self.db.execute(
            select(Department).where(Department.id == appointment.department_id)
        )
        department = department_result.scalar_one_or_none()
        department_name = department.name if department else "Poli"

        # Calculate hours until appointment
        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.appointment_time
        )
        hours_until = (appointment_datetime - datetime.now()).total_seconds() / 3600

        # Select appropriate template
        if hours_until <= 3:
            template_key = "reminder_2h_id"
        else:
            template_key = "reminder_24h_id"

        # Get patient language preference (default to Indonesian)
        language = await self._get_patient_language(appointment.patient_id)

        # Prepare template variables
        variables = {
            "patient_name": patient.first_name or "",
            "appointment_date": appointment.appointment_date.strftime("%d/%m/%Y"),
            "appointment_time": appointment.appointment_time.strftime("%H:%M"),
            "doctor_name": doctor_name,
            "department": department_name,
            "queue_number": appointment.queue_number or "-",
        }

        # Format message
        template = self.TEMPLATES.get("{key}_{lang}".format(key=template_key[:10], lang=language), self.TEMPLATES[template_key])
        message = template.format(**variables)

        # Store message content
        reminder.message_content = message

        # Create notification record
        notification = Notification(
            recipient_id=appointment.patient_id,
            recipient_type="patient",
            notification_type="appointment_reminder",
            channel=reminder.reminder_type.value,
            status="pending",
            priority="normal",
            subject="Pengingat Janji Temu",
            content=message,
            metadata={
                "appointment_id": appointment.id,
                "appointment_number": appointment.appointment_number,
                "reminder_id": reminder.id,
                "type": "reminder",
                "hours_before": int(hours_until),
            },
            scheduled_at=datetime.now(),
        )
        self.db.add(notification)

    async def _is_channel_enabled(
        self,
        patient_id: int,
        channel: str
    ) -> bool:
        """Check if a notification channel is enabled for a patient

        Args:
            patient_id: The patient ID
            channel: The channel to check (sms, email, whatsapp, push)

        Returns:
            True if channel is enabled
        """
        # Check user preferences
        pref_result = await self.db.execute(
            select(NotificationPreference).where(
                and_(
                    NotificationPreference.user_id == patient_id,
                    NotificationPreference.user_type == "patient",
                    NotificationPreference.notification_type == "appointment_reminder"
                )
            )
        )
        preference = pref_result.scalar_one_or_none()

        if preference:
            # Check channel_enabled JSONB field
            channel_map = {
                "sms": "sms",
                "email": "email",
                "whatsapp": "whatsapp",
                "push": "push",
                "in_app": "in_app",
            }
            enabled_channels = preference.channel_enabled or {}
            return enabled_channels.get(channel_map.get(channel, channel), False)

        # Default: SMS and WhatsApp enabled, email disabled
        return channel in ["sms", "whatsapp"]

    async def _get_patient_language(
        self,
        patient_id: int
    ) -> str:
        """Get patient's preferred language

        Args:
            patient_id: The patient ID

        Returns:
            Language code (id, en)
        """
        # Check preferences
        pref_result = await self.db.execute(
            select(NotificationPreference).where(
                and_(
                    NotificationPreference.user_id == patient_id,
                    NotificationPreference.user_type == "patient"
                )
            )
        )
        preference = pref_result.first()

        if preference:
            return preference.language

        # Default to Indonesian
        return "id"

    def _format_confirmation_message(
        self,
        variables: Dict[str, str],
        is_short: bool = False
    ) -> str:
        """Format confirmation message with variables

        Args:
            variables: Template variables
            is_short: Use short format for SMS

        Returns:
            Formatted message
        """
        if is_short:
            return self.TEMPLATES["confirmation_id_short"].format(**variables)
        return self.TEMPLATES["confirmation_id"].format(**variables)

    async def _cancel_appointment_reminders(
        self,
        appointment_id: int
    ) -> None:
        """Cancel all pending reminders for an appointment

        Args:
            appointment_id: The appointment ID
        """
        await self.db.execute(
            select(AppointmentReminder)
            .where(
                and_(
                    AppointmentReminder.appointment_id == appointment_id,
                    AppointmentReminder.status == ReminderStatus.PENDING
                )
            )
        ).update(
            {
                "status": ReminderStatus.FAILED,
                "error_message": "Appointment cancelled"
            }
        )

    async def get_upcoming_reminders(
        self,
        patient_id: Optional[int] = None,
        days_ahead: int = 7
    ) -> List[Dict[str, Any]]:
        """Get upcoming scheduled reminders

        Args:
            patient_id: Optional patient ID filter
            days_ahead: Number of days ahead to look

        Returns:
            List of reminder details
        """
        cutoff_date = datetime.now() + timedelta(days=days_ahead)

        query = (
            select(AppointmentReminder)
            .options(selectinload(AppointmentReminder.appointment))
            .where(
                and_(
                    AppointmentReminder.status == ReminderStatus.PENDING,
                    AppointmentReminder.scheduled_at <= cutoff_date,
                )
            )
        )

        if patient_id:
            # Join with appointments to filter by patient
            query = query.join(Appointment).where(Appointment.patient_id == patient_id)

        query = query.order_by(AppointmentReminder.scheduled_at.asc())

        result = await self.db.execute(query)
        reminders = result.scalars().all()

        return [
            {
                "reminder_id": r.id,
                "appointment_id": r.appointment_id,
                "appointment_number": r.appointment.appointment_number if r.appointment else None,
                "scheduled_at": r.scheduled_at,
                "reminder_type": r.reminder_type.value,
            }
            for r in reminders
        ]

    async def get_reminder_statistics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get statistics about reminder delivery

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Statistics dict
        """
        # Base query
        base_filters = []
        if start_date:
            base_filters.append(AppointmentReminder.created_at >= datetime.combine(start_date, dt_time(0, 0)))
        if end_date:
            base_filters.append(AppointmentReminder.created_at <= datetime.combine(end_date, dt_time(23, 59)))

        # Get counts by status
        status_query = (
            select(AppointmentReminder.status, func.count(AppointmentReminder.id))
            .where(and_(*base_filters)) if base_filters else select(AppointmentReminder.status, func.count(AppointmentReminder.id))
        ).group_by(AppointmentReminder.status)

        status_result = await self.db.execute(status_query)
        status_counts = {status.value: count for status, count in status_result.all()}

        # Get counts by type
        type_query = (
            select(AppointmentReminder.reminder_type, func.count(AppointmentReminder.id))
            .where(and_(*base_filters)) if base_filters else select(AppointmentReminder.reminder_type, func.count(AppointmentReminder.id))
        ).group_by(AppointmentReminder.reminder_type)

        type_result = await self.db.execute(type_query)
        type_counts = {r_type.value: count for r_type, count in type_result.all()}

        return {
            "by_status": {
                "pending": status_counts.get("pending", 0),
                "sent": status_counts.get("sent", 0),
                "failed": status_counts.get("failed", 0),
            },
            "by_type": {
                "sms": type_counts.get("sms", 0),
                "email": type_counts.get("email", 0),
                "whatsapp": type_counts.get("whatsapp", 0),
                "push": type_counts.get("push", 0),
            },
            "total": sum(status_counts.values()),
        }
