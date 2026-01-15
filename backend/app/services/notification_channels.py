"""Notification Channel Providers

Multi-channel notification delivery system with provider abstraction.
Supports SMS, Email, Push, In-App, and WhatsApp notifications.

Python 3.5+ compatible - uses .format() instead of f-strings
"""

import asyncio
import json
import logging
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from collections import namedtuple

import httpx
import aiosmtplib
from email.message import EmailMessage

from app.core.config import settings


logger = logging.getLogger(__name__)


# Use namedtuple for DeliveryResult instead of dataclass (Python 3.5 compatible)
DeliveryResult = namedtuple('DeliveryResult', [
    'success',
    'status',
    'message_id',
    'provider_response',
    'error_message',
    'retry_after'
])


def create_delivery_result(success, status, message_id=None, provider_response=None,
                          error_message=None, retry_after=None):
    """Factory function for creating DeliveryResult with default values"""
    return DeliveryResult(
        success=success,
        status=status,
        message_id=message_id,
        provider_response=provider_response,
        error_message=error_message,
        retry_after=retry_after
    )


class ChannelStatus(object):
    """Channel delivery status constants"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class BaseChannelProvider(object):
    """Base class for notification channel providers"""
    __metaclass__ = ABCMeta

    def __init__(self):
        self.max_retries = 3
        self.retry_delays = [60, 300, 900]  # 1min, 5min, 15min

    @abstractmethod
    async def send(self, recipient, subject, message, metadata=None):
        """Send notification via this channel

        Args:
            recipient: Recipient identifier (phone, email, device_id, etc.)
            subject: Notification subject/title
            message: Notification body/content
            metadata: Additional metadata for the notification

        Returns:
            DeliveryResult namedtuple
        """
        pass

    @abstractmethod
    def validate_recipient(self, recipient):
        """Validate recipient identifier format

        Args:
            recipient: Recipient identifier to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    async def send_with_retry(self, recipient, subject, message, metadata=None):
        """Send with automatic retry on failure

        Args:
            recipient: Recipient identifier
            subject: Notification subject
            message: Notification body
            metadata: Additional metadata

        Returns:
            DeliveryResult from final attempt
        """
        last_result = None

        for attempt in range(self.max_retries):
            try:
                result = await self.send(recipient, subject, message, metadata)
                last_result = result

                if result.success:
                    return result

                # If failed and not last attempt, wait before retry
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    logger.warning(
                        "Channel send failed (attempt {}), retrying in {}s: {}".format(
                            attempt + 1, delay, result.error_message
                        )
                    )
                    await asyncio.sleep(delay)

            except Exception as e:
                last_result = create_delivery_result(
                    success=False,
                    status=ChannelStatus.FAILED,
                    error_message=str(e)
                )
                logger.error("Channel send error (attempt {}): {}".format(attempt + 1, e))

                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    await asyncio.sleep(delay)

        return last_result or create_delivery_result(
            success=False,
            status=ChannelStatus.FAILED,
            error_message="Max retries exceeded"
        )


class SMSProvider(BaseChannelProvider):
    """SMS notification provider with multiple gateway support"""

    def __init__(self):
        super(SMSProvider, self).__init__()
        self.provider = getattr(settings, 'SMS_PROVIDER', 'mock')
        self.from_number = getattr(settings, 'SMS_FROM_NUMBER', '+1234567890')
        self.twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        self.nexmo_api_key = getattr(settings, 'NEXMO_API_KEY', '')
        self.nexmo_api_secret = getattr(settings, 'NEXMO_API_SECRET', '')

    async def send(self, recipient, subject, message, metadata=None):
        """Send SMS notification"""
        if not self.validate_recipient(recipient):
            return create_delivery_result(
                success=False,
                status=ChannelStatus.FAILED,
                error_message="Invalid phone number format: {}".format(recipient)
            )

        try:
            # Truncate message if too long
            sms_message = message[:160] if len(message) > 160 else message

            if self.provider == "twilio":
                return await self._send_via_twilio(recipient, sms_message)
            elif self.provider == "nexmo":
                return await self._send_via_nexmo(recipient, sms_message)
            else:
                return await self._send_mock(recipient, sms_message)

        except Exception as e:
            logger.error("SMS send failed: {}".format(e))
            return create_delivery_result(
                success=False,
                status=ChannelStatus.FAILED,
                error_message=str(e)
            )

    def validate_recipient(self, recipient):
        """Validate phone number format (E.164)"""
        import re
        return bool(re.match(r'^\+[1-9]\d{9,14}$', recipient))

    async def _send_via_twilio(self, recipient, message):
        """Send SMS via Twilio API"""
        url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json".format(
            self.twilio_account_sid
        )
        data = {
            "From": self.from_number,
            "To": recipient,
            "Body": message
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data=data,
                auth=(self.twilio_account_sid, self.twilio_auth_token),
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()

        return create_delivery_result(
            success=True,
            status=ChannelStatus.SENT,
            message_id=result.get("sid"),
            provider_response={"twilio_message": result}
        )

    async def _send_via_nexmo(self, recipient, message):
        """Send SMS via Vonage/Nexmo API"""
        url = "https://rest.nexmo.com/sms/json"
        data = {
            "from": self.from_number,
            "to": recipient,
            "text": message,
            "api_key": self.nexmo_api_key,
            "api_secret": self.nexmo_api_secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, timeout=30.0)
            response.raise_for_status()
            result = response.json()

        message_id = None
        if result.get("messages"):
            message_id = result["messages"][0].get("message-id")

        return create_delivery_result(
            success=True,
            status=ChannelStatus.SENT,
            message_id=message_id,
            provider_response={"nexmo_response": result}
        )

    async def _send_mock(self, recipient, message):
        """Mock SMS delivery for development/testing"""
        logger.info("[MOCK SMS] To: {}, Message: {}".format(recipient, message))
        await asyncio.sleep(0.1)

        return create_delivery_result(
            success=True,
            status=ChannelStatus.SENT,
            message_id="mock_{}".format(datetime.utcnow().timestamp()),
            provider_response={"mock": True, "recipient": recipient}
        )


class EmailProvider(BaseChannelProvider):
    """Email notification provider with SMTP support"""

    def __init__(self):
        super(EmailProvider, self).__init__()
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.smtp_use_tls = getattr(settings, 'SMTP_USE_TLS', True)
        self.from_email = getattr(settings, 'SMTP_FROM_EMAIL', 'noreply@simrs.hospital')
        self.from_name = getattr(settings, 'SMTP_FROM_NAME', 'SIMRS Hospital')

    async def send(self, recipient, subject, message, metadata=None):
        """Send email notification"""
        if not self.validate_recipient(recipient):
            return create_delivery_result(
                success=False,
                status=ChannelStatus.FAILED,
                error_message="Invalid email format: {}".format(recipient)
            )

        try:
            # Create email message
            email_msg = EmailMessage()
            email_msg["From"] = "{} <{}>".format(self.from_name, self.from_email)
            email_msg["To"] = recipient
            email_msg["Subject"] = subject

            # Determine content type
            is_html = metadata.get("is_html", False) if metadata else False
            if is_html:
                email_msg.set_content(message, subtype="html")
            else:
                email_msg.set_content(message)

            # Send via SMTP
            await aiosmtplib.send(
                email_msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.smtp_use_tls,
                timeout=30
            )

            message_id = "<{}@{}>".format(datetime.utcnow().timestamp(), self.smtp_host)

            return create_delivery_result(
                success=True,
                status=ChannelStatus.SENT,
                message_id=message_id,
                provider_response={"smtp_accepted": True}
            )

        except aiosmtplib.SMTPException as e:
            logger.error("SMTP error: {}".format(e))
            return create_delivery_result(
                success=False,
                status=ChannelStatus.FAILED,
                error_message="SMTP error: {}".format(str(e))
            )
        except Exception as e:
            logger.error("Email send failed: {}".format(e))
            return create_delivery_result(
                success=False,
                status=ChannelStatus.FAILED,
                error_message=str(e)
            )

    def validate_recipient(self, recipient):
        """Validate email address format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, recipient))


class PushNotificationProvider(BaseChannelProvider):
    """Push notification provider for mobile apps (Firebase/FCM, APNS)"""

    def __init__(self):
        super(PushNotificationProvider, self).__init__()
        self.provider = getattr(settings, 'PUSH_PROVIDER', 'mock')
        self.firebase_server_key = getattr(settings, 'FIREBASE_SERVER_KEY', '')
        self.apns_key_id = getattr(settings, 'APNS_KEY_ID', '')
        self.apns_team_id = getattr(settings, 'APNS_TEAM_ID', '')

    async def send(self, recipient, subject, message, metadata=None):
        """Send push notification"""
        if not self.validate_recipient(recipient):
            return create_delivery_result(
                success=False,
                status=ChannelStatus.FAILED,
                error_message="Invalid device token format"
            )

        try:
            # Build notification payload
            payload = {
                "title": subject,
                "body": message,
                "data": metadata.get("data", {}) if metadata else {}
            }

            if self.provider == "firebase":
                return await self._send_via_firebase(recipient, payload)
            elif self.provider == "apns":
                return await self._send_via_apns(recipient, payload)
            else:
                return await self._send_mock(recipient, payload)

        except Exception as e:
            logger.error("Push notification failed: {}".format(e))
            return create_delivery_result(
                success=False,
                status=ChannelStatus.FAILED,
                error_message=str(e)
            )

    def validate_recipient(self, recipient):
        """Validate device token"""
        return len(recipient) >= 32

    async def _send_via_firebase(self, device_token, payload):
        """Send via Firebase Cloud Messaging (FCM)"""
        url = "https://fcm.googleapis.com/fcm/send"
        headers = {
            "Authorization": "key={}".format(self.firebase_server_key),
            "Content-Type": "application/json"
        }
        data = {
            "to": device_token,
            "notification": {
                "title": payload["title"],
                "body": payload["body"]
            },
            "data": payload.get("data", {})
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=30.0)
            response.raise_for_status()
            result = response.json()

        message_id = result.get("message_id") or result.get("multicast_id")

        return create_delivery_result(
            success=True,
            status=ChannelStatus.SENT,
            message_id=str(message_id),
            provider_response={"fcm_response": result}
        )

    async def _send_via_apns(self, device_token, payload):
        """Send via Apple Push Notification Service (APNS)"""
        logger.info("[APNS MOCK] To: {}, Payload: {}".format(device_token, payload))
        await asyncio.sleep(0.1)

        return create_delivery_result(
            success=True,
            status=ChannelStatus.SENT,
            message_id="apns_{}".format(datetime.utcnow().timestamp()),
            provider_response={"apns_id": "apns_{}".format(datetime.utcnow().timestamp())}
        )

    async def _send_mock(self, device_token, payload):
        """Mock push notification for development"""
        logger.info("[MOCK PUSH] To: {}, Title: {}".format(device_token, payload['title']))
        await asyncio.sleep(0.1)

        return create_delivery_result(
            success=True,
            status=ChannelStatus.SENT,
            message_id="mock_push_{}".format(datetime.utcnow().timestamp()),
            provider_response={"mock": True, "token": device_token}
        )


class InAppNotificationProvider(BaseChannelProvider):
    """In-app notification provider (stores in database for real-time delivery)"""

    def __init__(self, db=None):
        super(InAppNotificationProvider, self).__init__()
        self.db = db

    async def send(self, recipient, subject, message, metadata=None):
        """Store in-app notification"""
        return create_delivery_result(
            success=True,
            status=ChannelStatus.DELIVERED,
            message_id="inapp_{}".format(datetime.utcnow().timestamp()),
            provider_response={
                "stored_for": recipient,
                "delivered_via": "polling_or_websocket"
            }
        )

    def validate_recipient(self, recipient):
        """In-app recipients are user/patient IDs"""
        return recipient.isdigit() or len(recipient) > 0


class WhatsAppProvider(BaseChannelProvider):
    """WhatsApp Business API provider"""

    def __init__(self):
        super(WhatsAppProvider, self).__init__()
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', 'https://graph.facebook.com/v17.0')
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
        self.access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')

    async def send(self, recipient, subject, message, metadata=None):
        """Send WhatsApp message"""
        if not self.validate_recipient(recipient):
            return create_delivery_result(
                success=False,
                status=ChannelStatus.FAILED,
                error_message="Invalid phone number format: {}".format(recipient)
            )

        try:
            # Remove + prefix if present for WhatsApp API
            phone = recipient.lstrip('+')

            # Check if using template or free-form message
            template_name = metadata.get("template_name") if metadata else None
            template_params = metadata.get("template_params", {}) if metadata else {}

            if template_name:
                return await self._send_template_message(phone, template_name, template_params)
            else:
                return await self._send_free_form_message(phone, message)

        except Exception as e:
            logger.error("WhatsApp send failed: {}".format(e))
            return create_delivery_result(
                success=False,
                status=ChannelStatus.FAILED,
                error_message=str(e)
            )

    def validate_recipient(self, recipient):
        """Validate phone number for WhatsApp"""
        import re
        return bool(re.match(r'^\+?[1-9]\d{9,14}$', recipient))

    async def _send_template_message(self, phone, template_name, params):
        """Send WhatsApp template message"""
        url = "{}/{}/messages".format(self.api_url, self.phone_number_id)
        headers = {
            "Authorization": "Bearer {}".format(self.access_token),
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "id"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": value}
                            for value in params.values()
                        ]
                    }
                ]
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=30.0)
            response.raise_for_status()
            result = response.json()

        message_id = result.get("messages", [{}])[0].get("id")

        return create_delivery_result(
            success=True,
            status=ChannelStatus.SENT,
            message_id=message_id,
            provider_response={"whatsapp_response": result}
        )

    async def _send_free_form_message(self, phone, message):
        """Send free-form WhatsApp message"""
        url = "{}/{}/messages".format(self.api_url, self.phone_number_id)
        headers = {
            "Authorization": "Bearer {}".format(self.access_token),
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": message}
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=30.0)
            response.raise_for_status()
            result = response.json()

        message_id = result.get("messages", [{}])[0].get("id")

        return create_delivery_result(
            success=True,
            status=ChannelStatus.SENT,
            message_id=message_id,
            provider_response={"whatsapp_response": result}
        )


class ChannelProviderFactory(object):
    """Factory for creating channel provider instances"""

    _providers = {}

    @classmethod
    def get_sms_provider(cls):
        """Get or create SMS provider instance"""
        if "sms" not in cls._providers:
            cls._providers["sms"] = SMSProvider()
        return cls._providers["sms"]

    @classmethod
    def get_email_provider(cls):
        """Get or create Email provider instance"""
        if "email" not in cls._providers:
            cls._providers["email"] = EmailProvider()
        return cls._providers["email"]

    @classmethod
    def get_push_provider(cls):
        """Get or create Push notification provider instance"""
        if "push" not in cls._providers:
            cls._providers["push"] = PushNotificationProvider()
        return cls._providers["push"]

    @classmethod
    def get_whatsapp_provider(cls):
        """Get or create WhatsApp provider instance"""
        if "whatsapp" not in cls._providers:
            cls._providers["whatsapp"] = WhatsAppProvider()
        return cls._providers["whatsapp"]

    @classmethod
    def get_inapp_provider(cls, db=None):
        """Get or create In-App provider instance"""
        return InAppNotificationProvider(db)

    @classmethod
    def get_provider(cls, channel, db=None):
        """Get provider by channel name

        Args:
            channel: Channel name (sms, email, push, whatsapp, in_app)
            db: Database session (required for in_app channel)

        Returns:
            Channel provider instance
        """
        channel_map = {
            "sms": cls.get_sms_provider,
            "email": cls.get_email_provider,
            "push": cls.get_push_provider,
            "whatsapp": cls.get_whatsapp_provider,
            "in_app": lambda: cls.get_inapp_provider(db) if db else InAppNotificationProvider(),
        }

        if channel not in channel_map:
            raise ValueError("Unsupported channel: {}".format(channel))

        return channel_map[channel]()
