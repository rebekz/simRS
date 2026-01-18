"""Patient Portal SMS Service

Service for sending SMS messages for patient portal verification.
"""
from typing import Optional
from datetime import datetime

from app.core.config import settings


class PatientPortalSMSService:
    """Service for sending patient portal SMS messages

    Note: This is a template service. In production, integrate with
    an SMS gateway like Twilio, Nexmo, or local Indonesian providers
    like Tapera, Verihape, or Bulk SMS Indonesia.
    """

    def __init__(self):
        self.from_number = getattr(settings, 'SMS_FROM_NUMBER', 'SIMRS')
        self.provider = getattr(settings, 'SMS_PROVIDER', 'mock')  # mock, twilio, tapera, etc.

    async def send_verification_sms(
        self,
        phone_number: str,
        patient_name: str,
        verification_code: str,
        expires_in_minutes: int = 10,
    ) -> bool:
        """Send SMS verification code

        Args:
            phone_number: Indonesian mobile number (+62... or 08...)
            patient_name: Patient's name
            verification_code: 6-digit verification code
            expires_in_minutes: Code expiration time

        Returns:
            True if SMS sent successfully
        """
        # Normalize phone number
        normalized_phone = self._normalize_phone_number(phone_number)
        message = self._get_verification_message(patient_name, verification_code, expires_in_minutes)

        # TODO: Integrate with actual SMS service
        # For now, log the SMS content
        print(f"[SMS] To: {normalized_phone}")
        print(f"[SMS] Message: {message}")

        # Example integration with Twilio:
        # from twilio.rest import Client
        # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        # message = client.messages.create(
        #     body=message,
        #     from_=self.from_number,
        #     to=normalized_phone
        # )
        # return message.status == 'queued'

        # Example integration with Indonesian provider (Tapera/Verihape):
        # import requests
        # response = requests.post(
        #     'https://api.sms-provider.id/send',
        #     json={
        #         'apikey': settings.SMS_API_KEY,
        #         'sender': self.from_number,
        #         'number': normalized_phone,
        #         'message': message
        #     }
        # )
        # return response.status_code == 200

        return True

    async def send_appointment_reminder(
        self,
        phone_number: str,
        patient_name: str,
        appointment_date: datetime,
        doctor_name: str,
        clinic: str,
    ) -> bool:
        """Send appointment reminder SMS"""
        normalized_phone = self._normalize_phone_number(phone_number)
        message = self._get_appointment_reminder_message(
            patient_name, appointment_date, doctor_name, clinic
        )

        print(f"[SMS] To: {normalized_phone}")
        print(f"[SMS] Message: {message}")

        return True

    async def send_password_reset_sms(
        self,
        phone_number: str,
        patient_name: str,
        reset_token: str,
    ) -> bool:
        """Send password reset SMS"""
        normalized_phone = self._normalize_phone_number(phone_number)
        reset_link = f"{getattr(settings, 'PORTAL_BASE_URL', 'https://portal.simrs.hospital.id')}/auth/reset-password?token={reset_token}"
        message = f"SIMRS: Reset password anda: {reset_link}. Link berlaku 1 jam."

        print(f"[SMS] To: {normalized_phone}")
        print(f"[SMS] Message: {message}")

        return True

    def _normalize_phone_number(self, phone_number: str) -> str:
        """Normalize Indonesian phone number to E.164 format

        Args:
            phone_number: Phone in various formats (08..., 628..., +628...)

        Returns:
            Normalized phone number (+628...)
        """
        # Remove all non-digits
        digits_only = ''.join(c for c in phone_number if c.isdigit())

        # If starts with 0, replace with +62
        if digits_only.startswith('0'):
            digits_only = '62' + digits_only[1:]

        # Add + if not present
        if not digits_only.startswith('+'):
            digits_only = '+' + digits_only

        return digits_only

    def _get_verification_message(
        self,
        patient_name: str,
        verification_code: str,
        expires_in_minutes: int,
    ) -> str:
        """Generate SMS verification message

        Indonesian SMS messages should be concise and clear
        """
        return f"SIMRS: Kode verifikasi untuk {patient_name}: {verification_code}. Berlaku {expires_in_minutes} menit. JANGAN BERIKAN kode ini kepada siapapun."

    def _get_appointment_reminder_message(
        self,
        patient_name: str,
        appointment_date: datetime,
        doctor_name: str,
        clinic: str,
    ) -> str:
        """Generate appointment reminder SMS message"""
        date_str = appointment_date.strftime('%d/%m %H:%M')
        return f"SIMRS: Pengingat janji temu {patient_name} tgl {date_str} dg {doctor_name} di {clinic}. Datang 15 menit sebelum jadwal."

    def _get_lab_result_notification_message(
        self,
        patient_name: str,
        test_name: str,
    ) -> str:
        """Generate lab result notification SMS"""
        return f"SIMRS: Hasil lab {test_name} untuk {patient_name} sudah tersedia. Silakan login ke portal pasien."

    def _get_prescription_ready_notification_message(
        self,
        patient_name: str,
        pharmacy_name: str,
    ) -> str:
        """Generate prescription ready notification SMS"""
        return f"SIMRS: Resep untuk {patient_name} siap diambil di {pharmacy_name}. Buka jam 08:00-20:00."

    async def send_batch_sms(
        self,
        phone_numbers: list[str],
        message: str,
    ) -> dict:
        """Send batch SMS to multiple recipients

        Args:
            phone_numbers: List of phone numbers
            message: Common message to send

        Returns:
            Dict with success/failure counts
        """
        results = {"success": 0, "failed": 0}

        for phone_number in phone_numbers:
            normalized_phone = self._normalize_phone_number(phone_number)
            # TODO: Implement actual batch sending
            print(f"[SMS] To: {normalized_phone}")
            print(f"[SMS] Message: {message}")
            results["success"] += 1

        return results
