"""Appointment Reminder Service for STORY-022-02

Service for managing appointment reminders and confirmations:
- 24-hour and 2-hour reminders before appointments
- Immediate confirmation on booking
- Rescheduling and cancellation confirmations
- Patient response processing (YES, CANCEL, RESCHEDULE)
- Channel preference management with fallback
- Effectiveness tracking and reporting

Python 3.5+ compatible - uses .format() instead of f-strings
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.appointments import (
    Appointment, AppointmentReminder, ReminderType,
    ReminderStatus, AppointmentStatus
)
from app.models.notifications import Notification, NotificationStatus, NotificationChannel
from app.models.patients import Patient
from app.services.notification_channels import get_channel_provider
from app.core.config import settings


logger = logging.getLogger(__name__)


# Reminder timing configurations (hours before appointment)
REMINDER_24H = 24
REMINDER_2H = 2

# Indonesian message templates
MESSAGE_TEMPLATES = {
    'confirmation': {
        'sms': (
            "SIMRS: Konfirmasi Booking {appointment_number}\n"
            "Tanggal: {appointment_date}\n"
            "Jam: {appointment_time}\n"
            "Dokter: {doctor_name}\n"
            "Poliklinik: {department_name}\n"
            "No. Antrian: {queue_number}\n"
            "Estimasi Tunggu: {wait_time} menit\n\n"
            "Persiapan: {preparation_instructions}\n\n"
            "Untuk reschedule/cancel: {hospital_phone}"
        ),
        'whatsapp': (
            "*SIMRS - Konfirmasi Booking*\n\n"
            "No. Booking: *{appointment_number}*\n\n"
            "📅 Tanggal: {appointment_date}\n"
            "⏰ Jam: {appointment_time}\n"
            "👨‍⚕️ Dokter: {doctor_name}\n"
            "🏥 Poliklinik: {department_name}\n"
            "🎫 No. Antrian: {queue_number}\n"
            "⏱️ Estimasi Tunggu: {wait_time} menit\n\n"
            "📋 *Persiapan:*\n{preparation_instructions}\n\n"
            "Untuk reschedule/cancel: {hospital_phone}"
        ),
        'email': {
            'subject': "Konfirmasi Booking Appointment - {appointment_number}",
            'body': (
                "<h2>Konfirmasi Booking Appointment</h2>"
                "<p>Dear {patient_name},</p>"
                "<p>Booking appointment Anda telah dikonfirmasi:</p>"
                "<table>"
                "<tr><td>No. Booking:</td><td><strong>{appointment_number}</strong></td></tr>"
                "<tr><td>Tanggal:</td><td>{appointment_date}</td></tr>"
                "<tr><td>Jam:</td><td>{appointment_time}</td></tr>"
                "<tr><td>Dokter:</td><td>{doctor_name}</td></tr>"
                "<tr><td>Poliklinik:</td><td>{department_name}</td></tr>"
                "<tr><td>No. Antrian:</td><td>{queue_number}</td></tr>"
                "<tr><td>Estimasi Tunggu:</td><td>{wait_time} menit</td></tr>"
                "</table>"
                "<h3>Persiapan:</h3>"
                "<p>{preparation_instructions}</p>"
                "<p>Untuk reschedule/cancel: {hospital_phone}</p>"
            )
        }
    },
    'reminder_24h': {
        'sms': (
            "SIMRS: Pengingat Appointment {appointment_number}\n"
            "Besok, {appointment_date} pukul {appointment_time}\n"
            "Dokter: {doctor_name}\n"
            "Poliklinik: {department_name}\n"
            "No. Antrian: {queue_number}\n\n"
            "Reply YES untuk konfirmasi, CANCEL untuk batalkan"
        ),
        'whatsapp': (
            "*SIMRS - Pengingat Appointment* ⏰\n\n"
            "Besok, {appointment_date} pukul {appointment_time}\n\n"
            "👨‍⚕️ Dokter: {doctor_name}\n"
            "🏥 Poliklinik: {department_name}\n"
            "🎫 No. Antrian: {queue_number}\n\n"
            "Reply *YES* untuk konfirmasi\n"
            "Reply *CANCEL* untuk batalkan"
        ),
        'email': {
            'subject': "Pengingat Appointment Besok - {appointment_number}",
            'body': (
                "<h2>Pengingat Appointment</h2>"
                "<p>Dear {patient_name},</p>"
                "<p>Ini adalah pengingat untuk appointment Anda:</p>"
                "<table>"
                "<tr><td>No. Booking:</td><td><strong>{appointment_number}</strong></td></tr>"
                "<tr><td>Tanggal:</td><td>{appointment_date}</td></tr>"
                "<tr><td>Jam:</td><td>{appointment_time}</td></tr>"
                "<tr><td>Dokter:</td><td>{doctor_name}</td></tr>"
                "<tr><td>Poliklinik:</td><td>{department_name}</td></tr>"
                "<tr><td>No. Antrian:</td><td>{queue_number}</td></tr>"
                "</table>"
                "<p>Reply YES untuk konfirmasi atau CANCEL untuk batalkan.</p>"
            )
        }
    },
    'reminder_2h': {
        'sms': (
            "SIMRS: Pengingat Appointment {appointment_number}\n"
            "Dalam 2 jam: {appointment_date} pukul {appointment_time}\n"
            "Dokter: {doctor_name}\n"
            "Poliklinik: {department_name}\n"
            "No. Antrian: {queue_number}\n\n"
            "Silakan check-in 30 menit sebelumnya"
        ),
        'whatsapp': (
            "*SIMRS - Pengingat* (2 jam)\n\n"
            "Dalam 2 jam: {appointment_date} pukul {appointment_time}\n\n"
            "👨‍⚕️ Dokter: {doctor_name}\n"
            "🏥 Poliklinik: {department_name}\n"
            "🎫 No. Antrian: {queue_number}\n\n"
            "Silakan check-in 30 menit sebelumnya"
        ),
        'email': {
            'subject': "Pengingat 2 Jam - {appointment_number}",
            'body': (
                "<h2>Pengingat Appointment (2 Jam)</h2>"
                "<p>Dear {patient_name},</p>"
                "<p>Appointment Anda akan dimulai dalam 2 jam:</p>"
                "<table>"
                "<tr><td>No. Booking:</td><td><strong>{appointment_number}</strong></td></tr>"
                "<tr><td>Tanggal:</td><td>{appointment_date}</td></tr>"
                "<tr><td>Jam:</td><td>{appointment_time}</td></tr>"
                "<tr><td>Dokter:</td><td>{doctor_name}</td></tr>"
                "<tr><td>Poliklinik:</td><td>{department_name}</td></tr>"
                "<tr><td>No. Antrian:</td><td>{queue_number}</td></tr>"
                "</table>"
                "<p>Silakan check-in 30 menit sebelum jadwal.</p>"
            )
        }
    },
    'rescheduled': {
        'sms': (
            "SIMRS: Appointment Rescheduled {appointment_number}\n"
            "Baru: {new_date} pukul {new_time}\n"
            "Dokter: {doctor_name}\n"
            "Poliklinik: {department_name}\n\n"
            "Reply YES untuk konfirmasi"
        ),
        'whatsapp': (
            "*SIMRS - Appointment Rescheduled* 🔄\n\n"
            "No. Booking: {appointment_number}\n\n"
            "Jadwal Baru:\n"
            "📅 {new_date}\n"
            "⏰ {new_time}\n"
            "👨‍⚕️ {doctor_name}\n"
            "🏥 {department_name}\n\n"
            "Reply *YES* untuk konfirmasi"
        ),
        'email': {
            'subject': "Appointment Rescheduled - {appointment_number}",
            'body': (
                "<h2>Appointment Rescheduled</h2>"
                "<p>Dear {patient_name},</p>"
                "<p>Appointment Anda telah direschedule:</p>"
                "<table>"
                "<tr><td>No. Booking:</td><td><strong>{appointment_number}</strong></td></tr>"
                "<tr><td>Tanggal Baru:</td><td>{new_date}</td></tr>"
                "<tr><td>Jam Baru:</td><td>{new_time}</td></tr>"
                "<tr><td>Dokter:</td><td>{doctor_name}</td></tr>"
                "<tr><td>Poliklinik:</td><td>{department_name}</td></tr>"
                "</table>"
                "<p>Reply YES untuk konfirmasi jadwal baru.</p>"
            )
        }
    },
    'cancelled': {
        'sms': (
            "SIMRS: Appointment Dibatalkan {appointment_number}\n"
            "Terima kasih telah menginformasikan pembatalan.\n\n"
            "Untuk booking baru: {hospital_phone}"
        ),
        'whatsapp': (
            "*SIMRS - Pembatalan Dikonfirmasi* ✅\n\n"
            "No. Booking: {appointment_number}\n\n"
            "Pembatalan appointment Anda telah dikonfirmasi.\n\n"
            "Untuk booking baru: {hospital_phone}"
        ),
        'email': {
            'subject': "Pembatalan Dikonfirmasi - {appointment_number}",
            'body': (
                "<h2>Pembatalan Dikonfirmasi</h2>"
                "<p>Dear {patient_name},</p>"
                "<p>Pembatalan appointment Anda telah dikonfirmasi:</p>"
                "<table>"
                "<tr><td>No. Booking:</td><td><strong>{appointment_number}</strong></td></tr>"
                "<tr><td>Tanggal:</td><td>{appointment_date}</td></tr>"
                "</table>"
                "<p>Terima kasih telah menginformasikan pembatalan.</p>"
                "<p>Untuk booking baru: {hospital_phone}</p>"
            )
        }
    }
}


class AppointmentReminderService(object):
    """Service for managing appointment reminders and confirmations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_message_template(self, template_type: str, channel: str) -> Optional[Dict]:
        """Get message template for specific type and channel"""
        templates = MESSAGE_TEMPLATES.get(template_type, {})
        return templates.get(channel)

    async def format_message(self, template_type: str, channel: str,
                            appointment: Appointment, patient: Patient,
                            doctor_name: str, department_name: str,
                            hospital_phone: str = None) -> Optional[str]:
        """Format message with appointment details"""
        template = await self.get_message_template(template_type, channel)

        if not template:
            return None

        if channel == 'email':
            # Email has subject and body
            subject = template['subject'].format(
                appointment_number=appointment.appointment_number,
                appointment_date=appointment.appointment_date.strftime('%d/%m/%Y'),
                appointment_time=appointment.appointment_time.strftime('%H:%M'),
                doctor_name=doctor_name,
                department_name=department_name,
                queue_number=appointment.queue_number or '-',
                patient_name=patient.full_name,
                wait_time=appointment.estimated_wait_time_minutes or '-',
                preparation_instructions=self._get_preparation_instructions(appointment),
                hospital_phone=hospital_phone or settings.HOSPITAL_PHONE,
                new_date=appointment.appointment_date.strftime('%d/%m/%Y'),
                new_time=appointment.appointment_time.strftime('%H:%M')
            )
            body = template['body'].format(
                appointment_number=appointment.appointment_number,
                appointment_date=appointment.appointment_date.strftime('%d/%m/%Y'),
                appointment_time=appointment.appointment_time.strftime('%H:%M'),
                doctor_name=doctor_name,
                department_name=department_name,
                queue_number=appointment.queue_number or '-',
                patient_name=patient.full_name,
                wait_time=appointment.estimated_wait_time_minutes or '-',
                preparation_instructions=self._get_preparation_instructions(appointment),
                hospital_phone=hospital_phone or settings.HOSPITAL_PHONE,
                new_date=appointment.appointment_date.strftime('%d/%m/%Y'),
                new_time=appointment.appointment_time.strftime('%H:%M')
            )
            return {'subject': subject, 'body': body}
        else:
            # SMS and WhatsApp are plain text
            return template.format(
                appointment_number=appointment.appointment_number,
                appointment_date=appointment.appointment_date.strftime('%d/%m/%Y'),
                appointment_time=appointment.appointment_time.strftime('%H:%M'),
                doctor_name=doctor_name,
                department_name=department_name,
                queue_number=appointment.queue_number or '-',
                patient_name=patient.full_name,
                wait_time=appointment.estimated_wait_time_minutes or '-',
                preparation_instructions=self._get_preparation_instructions(appointment),
                hospital_phone=hospital_phone or settings.HOSPITAL_PHONE,
                new_date=appointment.appointment_date.strftime('%d/%m/%Y'),
                new_time=appointment.appointment_time.strftime('%H:%M')
            )

    def _get_preparation_instructions(self, appointment: Appointment) -> str:
        """Get preparation instructions based on appointment type"""
        if appointment.appointment_type == 'consultation':
            return "Bawa kartu identitas dan kartu BPJS (jika ada)"
        elif appointment.appointment_type == 'procedure':
            return "Puasa 8 jam sebelum prosedur (jika diinstruksikan)"
        elif appointment.appointment_type == 'vaccination':
            return "Bawa kartu imunisasi sebelumnya"
        else:
            return "Bawa kartu identitas dan kartu BPJS"

    async def get_patient_channel_preference(self, patient: Patient) -> List[str]:
        """Get patient's preferred notification channels with fallback"""
        # Check if patient has notification preferences stored
        # For now, return default priority order
        return ['whatsapp', 'sms', 'email']

    async def get_patient_contact(self, patient: Patient, channel: str) -> Optional[str]:
        """Get patient's contact info for specific channel"""
        if channel == 'sms':
            return patient.phone_number
        elif channel == 'whatsapp':
            return patient.phone_number  # WhatsApp uses same number
        elif channel == 'email':
            return patient.email
        elif channel == 'push':
            return patient.push_device_token
        return None

    async def send_confirmation(self, appointment: Appointment) -> bool:
        """Send immediate confirmation on appointment booking"""
        try:
            # Load related data
            stmt = select(Appointment).where(
                Appointment.id == appointment.id
            ).options(
                selectinload(Appointment.patient),
                selectinload(Appointment.doctor),
                selectinload(Appointment.department)
            )
            result = await self.db.execute(stmt)
            appointment = result.scalar_one_or_none()

            if not appointment:
                logger.error("Appointment not found: {}".format(appointment.id))
                return False

            patient = appointment.patient
            doctor_name = appointment.doctor.full_name if appointment.doctor else "Dokter"
            department_name = appointment.department.name

            # Get preferred channels
            channels = await self.get_patient_channel_preference(patient)

            # Send to each channel
            success_count = 0
            for channel in channels:
                contact = await self.get_patient_contact(patient, channel)
                if not contact:
                    continue

                message = await self.format_message(
                    'confirmation', channel, appointment, patient,
                    doctor_name, department_name
                )

                if not message:
                    continue

                # Create notification record
                notification = Notification(
                    recipient_id=patient.id,
                    user_type='patient',
                    notification_type='appointment_reminder',
                    channel=channel,
                    status=NotificationStatus.PENDING,
                    priority='normal',
                    title=message.get('subject', 'Appointment Confirmation') if channel == 'email' else 'Konfirmasi Booking',
                    message=message.get('body', message) if channel == 'email' else message,
                    scheduled_at=datetime.utcnow(),
                    metadata={
                        'appointment_id': appointment.id,
                        'confirmation_type': 'booking'
                    }
                )
                self.db.add(notification)
                await self.db.flush()

                # Send notification (async)
                # In production, this would be queued
                success_count += 1

            await self.db.commit()
            return success_count > 0

        except Exception as e:
            logger.error("Error sending confirmation: {}".format(str(e)))
            await self.db.rollback()
            return False

    async def schedule_reminders(self, appointment: Appointment) -> bool:
        """Schedule 24h and 2h reminders for an appointment"""
        try:
            # Calculate reminder times
            appointment_datetime = datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time
            )

            reminder_24h_time = appointment_datetime - timedelta(hours=REMINDER_24H)
            reminder_2h_time = appointment_datetime - timedelta(hours=REMINDER_2H)

            # Create reminder records
            reminder_24h = AppointmentReminder(
                appointment_id=appointment.id,
                reminder_type=ReminderType.SMS,
                scheduled_at=reminder_24h_time,
                status=ReminderStatus.PENDING,
                retry_count=0,
                max_retries=3
            )
            self.db.add(reminder_24h)

            reminder_2h = AppointmentReminder(
                appointment_id=appointment.id,
                reminder_type=ReminderType.SMS,
                scheduled_at=reminder_2h_time,
                status=ReminderStatus.PENDING,
                retry_count=0,
                max_retries=3
            )
            self.db.add(reminder_2h)

            await self.db.commit()
            return True

        except Exception as e:
            logger.error("Error scheduling reminders: {}".format(str(e)))
            await self.db.rollback()
            return False

    async def send_reminder(self, reminder: AppointmentReminder) -> bool:
        """Send a scheduled reminder"""
        try:
            # Load appointment with related data
            stmt = select(Appointment).where(
                Appointment.id == reminder.appointment_id
            ).options(
                selectinload(Appointment.patient),
                selectinload(Appointment.doctor),
                selectinload(Appointment.department)
            )
            result = await self.db.execute(stmt)
            appointment = result.scalar_one_or_none()

            if not appointment:
                logger.error("Appointment not found: {}".format(reminder.appointment_id))
                return False

            # Check if appointment is still active
            if appointment.status in [AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]:
                reminder.status = ReminderStatus.FAILED
                reminder.error_message = "Appointment cancelled or completed"
                await self.db.commit()
                return False

            patient = appointment.patient
            doctor_name = appointment.doctor.full_name if appointment.doctor else "Dokter"
            department_name = appointment.department.name

            # Determine reminder type (24h or 2h)
            appointment_datetime = datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time
            )
            hours_until = (appointment_datetime - datetime.utcnow()).total_seconds() / 3600

            if hours_until > 12:
                template_type = 'reminder_24h'
            else:
                template_type = 'reminder_2h'

            # Get preferred channels
            channels = await self.get_patient_channel_preference(patient)

            # Send to each channel
            success_count = 0
            for channel in channels:
                contact = await self.get_patient_contact(patient, channel)
                if not contact:
                    continue

                message = await self.format_message(
                    template_type, channel, appointment, patient,
                    doctor_name, department_name
                )

                if not message:
                    continue

                # Create notification record
                notification = Notification(
                    recipient_id=patient.id,
                    user_type='patient',
                    notification_type='appointment_reminder',
                    channel=channel,
                    status=NotificationStatus.PENDING,
                    priority='normal',
                    title=message.get('subject', 'Appointment Reminder') if channel == 'email' else 'Pengingat Appointment',
                    message=message.get('body', message) if channel == 'email' else message,
                    scheduled_at=datetime.utcnow(),
                    metadata={
                        'appointment_id': appointment.id,
                        'reminder_type': template_type,
                        'reminder_id': reminder.id
                    }
                )
                self.db.add(notification)
                await self.db.flush()

                success_count += 1

            # Update reminder status
            if success_count > 0:
                reminder.status = ReminderStatus.SENT
                reminder.sent_at = datetime.utcnow()
            else:
                reminder.status = ReminderStatus.FAILED
                reminder.error_message = "No valid contact channels"

            appointment.reminder_sent = True
            appointment.reminder_sent_at = datetime.utcnow()

            await self.db.commit()
            return success_count > 0

        except Exception as e:
            logger.error("Error sending reminder: {}".format(str(e)))
            await self.db.rollback()
            return False

    async def process_patient_response(self, message: str, phone_number: str,
                                      appointment_number: str) -> Dict:
        """Process patient response to reminder (YES, CANCEL, RESCHEDULE)

        Args:
            message: Patient's reply message
            phone_number: Patient's phone number
            appointment_number: Appointment booking number

        Returns:
            Dict with status and message
        """
        try:
            # Find appointment
            stmt = select(Appointment).where(
                Appointment.appointment_number == appointment_number
            ).options(
                selectinload(Appointment.patient)
            )
            result = await self.db.execute(stmt)
            appointment = result.scalar_one_or_none()

            if not appointment:
                return {
                    'success': False,
                    'status': 'not_found',
                    'message': 'Appointment tidak ditemukan'
                }

            patient = appointment.patient

            # Verify phone number matches
            if patient.phone_number != phone_number:
                return {
                    'success': False,
                    'status': 'unauthorized',
                    'message': 'Nomor telepon tidak sesuai'
                }

            # Parse message
            msg_upper = message.strip().upper()

            if msg_upper in ['YES', 'YA', 'OK', 'CONFIRM', 'KONFIRMASI']:
                # Confirm appointment
                appointment.status = AppointmentStatus.CONFIRMED
                await self.db.commit()

                return {
                    'success': True,
                    'status': 'confirmed',
                    'message': 'Terima kasih. Appointment Anda telah dikonfirmasi.'
                }

            elif msg_upper in ['CANCEL', 'BATAL', 'UNCONFIRM']:
                # Cancel appointment
                appointment.status = AppointmentStatus.CANCELLED
                appointment.cancellation_reason = 'Cancelled via SMS/WhatsApp'
                appointment.cancelled_at = datetime.utcnow()

                # Send cancellation confirmation
                await self._send_cancellation_confirmation(appointment)

                await self.db.commit()

                return {
                    'success': True,
                    'status': 'cancelled',
                    'message': 'Appointment Anda telah dibatalkan.'
                }

            elif msg_upper in ['RESCHEDULE', 'RESCHEDULED', 'JADWAL BARU', 'GANTI JADWAL']:
                # Request reschedule
                return {
                    'success': True,
                    'status': 'reschedule_requested',
                    'message': 'Untuk reschedule, silakan hubungi: ' + settings.HOSPITAL_PHONE
                }

            else:
                return {
                    'success': False,
                    'status': 'unknown_command',
                    'message': 'Perintah tidak dikenali. Reply YES untuk konfirmasi atau CANCEL untuk batalkan.'
                }

        except Exception as e:
            logger.error("Error processing patient response: {}".format(str(e)))
            await self.db.rollback()
            return {
                'success': False,
                'status': 'error',
                'message': 'Terjadi kesalahan. Silakan coba lagi.'
            }

    async def _send_cancellation_confirmation(self, appointment: Appointment):
        """Send cancellation confirmation notification"""
        try:
            patient = appointment.patient
            doctor_name = appointment.doctor.full_name if appointment.doctor else "Dokter"
            department_name = appointment.department.name

            channels = await self.get_patient_channel_preference(patient)

            for channel in channels:
                contact = await self.get_patient_contact(patient, channel)
                if not contact:
                    continue

                message = await self.format_message(
                    'cancelled', channel, appointment, patient,
                    doctor_name, department_name
                )

                if not message:
                    continue

                notification = Notification(
                    recipient_id=patient.id,
                    user_type='patient',
                    notification_type='appointment_reminder',
                    channel=channel,
                    status=NotificationStatus.PENDING,
                    priority='normal',
                    title=message.get('subject', 'Pembatalan Dikonfirmasi') if channel == 'email' else 'Pembatalan Dikonfirmasi',
                    message=message.get('body', message) if channel == 'email' else message,
                    scheduled_at=datetime.utcnow(),
                    metadata={
                        'appointment_id': appointment.id,
                        'confirmation_type': 'cancellation'
                    }
                )
                self.db.add(notification)

        except Exception as e:
            logger.error("Error sending cancellation confirmation: {}".format(str(e)))

    async def get_pending_reminders(self, hours_before: int = 2) -> List[AppointmentReminder]:
        """Get reminders that need to be sent soon"""
        from_time = datetime.utcnow()
        to_time = from_time + timedelta(hours=hours_before)

        stmt = select(AppointmentReminder).where(
            and_(
                AppointmentReminder.status == ReminderStatus.PENDING,
                AppointmentReminder.scheduled_at <= to_time,
                AppointmentReminder.scheduled_at > from_time
            )
        ).options(
            selectinload(AppointmentReminder.appointment)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_reminder_statistics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get reminder effectiveness statistics"""
        try:
            # Count total reminders sent
            total_sent = await self.db.execute(
                select(func.count(AppointmentReminder.id)).where(
                    and_(
                        AppointmentReminder.sent_at >= start_date,
                        AppointmentReminder.sent_at <= end_date,
                        AppointmentReminder.status == ReminderStatus.SENT
                    )
                )
            )
            total_sent = total_sent.scalar() or 0

            # Count failed reminders
            total_failed = await self.db.execute(
                select(func.count(AppointmentReminder.id)).where(
                    and_(
                        AppointmentReminder.created_at >= start_date,
                        AppointmentReminder.created_at <= end_date,
                        AppointmentReminder.status == ReminderStatus.FAILED
                    )
                )
            )
            total_failed = total_failed.scalar() or 0

            # Calculate success rate
            total = total_sent + total_failed
            success_rate = (total_sent / total * 100) if total > 0 else 0

            return {
                'total_sent': total_sent,
                'total_failed': total_failed,
                'success_rate': round(success_rate, 2),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error("Error getting reminder statistics: {}".format(str(e)))
            return {}


# Factory function for service creation
def create_reminder_service(db: AsyncSession) -> AppointmentReminderService:
    """Factory function to create AppointmentReminderService"""
    return AppointmentReminderService(db)
