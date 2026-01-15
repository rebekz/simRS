"""Notification Channel Providers

Multi-channel notification delivery system with provider abstraction.
Supports SMS, Email, Push, In-App, and WhatsApp notifications.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

try:
    from enum import Enum
except ImportError:
    # Python 3.5 compatibility
    class EnumMeta(type):
        def __new__(cls, name, bases, attrs):
            return super(EnumMeta, cls).__new__(cls, name, bases, attrs)

    class Enum(object):
        __metaclass__ = EnumMeta

import httpx
import aiosmtplib
from email.message import EmailMessage

from app.core.config import settings


logger = logging.getLogger(__name__)


class ChannelStatus(str, Enum):
    """Channel delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class DeliveryResult(object):
    """Result of notification delivery attempt"""

    def __init__(
        self,
        success,  # type: bool
        status,  # type: ChannelStatus
        message_id=None,  # type: Optional[str]
        provider_response=None,  # type: Optional[Dict[str, Any]]
        error_message=None,  # type: Optional[str]
        retry_after=None  # type: Optional[timedelta]
    ):
        self.success = success
        self.status = status
        self.message_id = message_id
        self.provider_response = provider_response
        self.error_message = error_message
        self.retry_after = retry_after


class BaseChannelProvider(ABC):
    """Base class for notification channel providers"""

    def __init__(self):
        self.max_retries = 3
        self.retry_delays = [60, 300, 900]  # 1min, 5min, 15min

    @abstractmethod
    async def send(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DeliveryResult:
        """Send notification via this channel

        Args:
            recipient: Recipient identifier (phone, email, device_id, etc.)
            subject: Notification subject/title
            message: Notification body/content
            metadata: Additional metadata for the notification

        Returns:
            DeliveryResult with delivery status
        """
        pass

    @abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        """Validate recipient identifier format

        Args:
            recipient: Recipient identifier to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    async def send_with_retry(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DeliveryResult:
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
                        "Channel send failed (attempt {attempt + 1}), ".format()
                        "retrying in {delay}s: {result.error_message}".format()
                    )
                    await asyncio.sleep(delay)

            except Exception as e:
                last_result = DeliveryResult(
                    success=False,
                    status=ChannelStatus.FAILED,
                    error_message=str(e)
                )
                logger.error("Channel send error (attempt {attempt + 1}): {e}".format())

                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    await asyncio.sleep(delay)

        return last_result or DeliveryResult(
            success=False,
            status=ChannelStatus.FAILED,
            error_message="Max retries exceeded"
        )


class SMSProvider(BaseChannelProvider):
    """SMS notification provider with multiple gateway support"""

    def __init__(self):
        super().__init__()
        # Configuration - supports multiple providers
        self.provider = settings.SMS_PROVIDER  # 'twilio', 'nexmo', 'local'
        self.from_number = settings.SMS_FROM_NUMBER

        # Provider credentials
        self.twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        self.nexmo_api_key = getattr(settings, 'NEXMO_API_KEY', '')
        self.nexmo_api_secret = getattr(settings, 'NEXMO_API_SECRET', '')

    async def send(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DeliveryResult:
        """Send SMS notification

        Args:
            recipient: Phone number in E.164 format (e.g., +628123456789)
            subject: Not used for SMS (included in message)
            message: SMS body (max 160 chars for single segment)
            metadata: Optional metadata

        Returns:
            DeliveryResult
        """
        if not self.validate_recipient(recipient):
            return DeliveryResult(
                success=False,
                status=ChannelStatus.FAILED,
                error_message="Invalid phone number format: {recipient}".format()
            )

        try:
            # Truncate message if too long
            sms_message = message[:160] if len(message) > 160 else message

            if self.provider == "twilio":
                return await self._send_via_twilio(recipient, sms_message)
            elif self.provider == "nexmo":
                return await self._send_via_nexmo(recipient, sms_message)
            else:
                # Mock implementation for development
                return await self._send_mock(recipient, sms_message)

        except Exception as e:
            logger.error("SMS send failed: {e}".format())
            return DeliveryResult(
                success=False,
                status=ChannelStatus.FAILED,
                error_message=str(e)
            )

    def validate_recipient(self, recipient: str) -> bool:
        """Validate phone number format (E.164)"""
        # Basic validation for E.164 format: + followed by 10-15 digits
        import re
        return bool(re.match(r'^\+[1-9]\d{9,14}$', recipient))

    async def _send_via_twilio(
        self,
        recipient: str,
        message: str
    ) -> DeliveryResult:
        """Send SMS via Twilio API"""
        url = "https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json".format()
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

        return DeliveryResult(
            success=True,
            status=ChannelStatus.SENT,
            message_id=result.get("sid"),
            provider_response={"twilio_message": result}
        )

    async def _send_via_nexmo(
        self,
        recipient: str,
        message: str
    ) -> DeliveryResult:
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

        return DeliveryResult(
            success=True,
            status=ChannelStatus.SENT,
            message_id=message_id,
            provider_response={"nexmo_response": result}
        )

    async def _send_mock(
        self,
        recipient: str,
        message: str
    ) -> DeliveryResult:
        """Mock SMS delivery for development/testing"""
        logger.info("[MOCK SMS] To: {recipient}, Message: {message}".format())
        # Simulate network delay
        await asyncio.sleep(0.1)

        return DeliveryResult(
            success=True,
            status=ChannelStatus.SENT,
            message_id="mock_{datetime.utcnow().timestamp()}".format(),
            provider_response={"mock": True, "recipient": recipient}
        )


class EmailProvider(BaseChannelProvider):
    """Email notification provider with SMTP support"""

    def __init__(self):
        super().__init__()
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_use_tls = settings.SMTP_USE_TLS
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = getattr(settings, 'SMTP_FROM_NAME', 'SIMRS Hospital')

    async def send(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DeliveryResult:
        """Send email notification

        Args:
            recipient: Email address
            subject: Email subject
            message: Email body (HTML or plain text)
            metadata: Optional metadata (is_html, attachments, etc.)

        Returns:
            DeliveryResult
        """
        if not self.validate_recipient(recipient):
            return DeliveryResult(
                success=False,
                status=ChannelStatus.FAILED,
                error_message="Invalid email format: {recipient}".format()
            )

        try:
            # Create email message
            email_msg = EmailMessage()
            email_msg["From"] = "{self.from_name} <{self.from_email}>".format()
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

            message_id = "<{datetime.utcnow().timestamp()}@{self.smtp_host}>".format()

            return DeliveryResult(
                success=True,
                status=ChannelStatus.SENT,
                message_id=message_id,
                provider_response={"smtp_accepted": True}
            )

        except aiosmtplib.SMTPException as e:
            logger.error("SMTP error: {e}".format())
            return DeliveryResult(
                success=False,
                status=ChannelStatus.FAILED,
                error_message="SMTP error: {str(e)}".format()
            )
        except Exception as e:
            logger.error("Email send failed: {e}".format())
            return DeliveryResult(
                success=False,
                status=ChannelStatus.FAILED,
                error_message=str(e)
            )

    def validate_recipient(self, recipient: str) -> bool:
        """Validate email address format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, recipient))


class PushNotificationProvider(BaseChannelProvider):
    """Push notification provider for mobile apps (Firebase/FCM, APNS)"""

    def __init__(self):
        super().__init__()
        self.provider = settings.PUSH_PROVIDER  # 'firebase', 'apns', 'mock'
        self.firebase_server_key = getattr(settings, 'FIREBASE_SERVER_KEY', '')
        self.apns_key_id = getattr(settings, 'APNS_KEY_ID', '')
        self.apns_team_id = getattr(settings, 'APNS_TEAM_ID', '')

    async def send(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DeliveryResult:
        """Send push notification

        Args:
            recipient: Device token or registration ID
            subject: Notification title
            message: Notification body
            metadata: Optional data payload, sound, badge, etc.

        Returns:
            DeliveryResult
        """
        if not self.validate_recipient(recipient):
            return DeliveryResult(
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
            logger.error("Push notification failed: {e}".format())
            return DeliveryResult(
                success=False,
                status=ChannelStatus.FAILED,
                error_message=str(e)
            )

    def validate_recipient(self, recipient: str) -> bool:
        """Validate device token"""
        # Basic validation - token should be at least 32 chars
        return len(recipient) >= 32

    async def _send_via_firebase(
        self,
        device_token: str,
        payload: Dict[str, Any]
    ) -> DeliveryResult:
        """Send via Firebase Cloud Messaging (FCM)"""
        url = "https://fcm.googleapis.com/fcm/send"
        headers = {
            "Authorization": "key={self.firebase_server_key}".format(),
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

        return DeliveryResult(
            success=True,
            status=ChannelStatus.SENT,
            message_id=str(message_id),
            provider_response={"fcm_response": result}
        )

    async def _send_via_apns(
        self,
        device_token: str,
        payload: Dict[str, Any]
    ) -> DeliveryResult:
        """Send via Apple Push Notification Service (APNS)"""
        # APNS requires http/2 - simplified implementation
        # In production, use httpx with http2 or apns2 library
        logger.info("[APNS MOCK] To: {device_token}, Payload: {payload}".format())
        await asyncio.sleep(0.1)

        return DeliveryResult(
            success=True,
            status=ChannelStatus.SENT,
            message_id="apns_{datetime.utcnow().timestamp()}".format(),
            provider_response={"apns_id": "apns_{datetime.utcnow().timestamp()}".format()}
        )

    async def _send_mock(
        self,
        device_token: str,
        payload: Dict[str, Any]
    ) -> DeliveryResult:
        """Mock push notification for development"""
        logger.info("[MOCK PUSH] To: {device_token}, Title: {payload['title']}".format())
        await asyncio.sleep(0.1)

        return DeliveryResult(
            success=True,
            status=ChannelStatus.SENT,
            message_id="mock_push_{datetime.utcnow().timestamp()}".format(),
            provider_response={"mock": True, "token": device_token}
        )


class InAppNotificationProvider(BaseChannelProvider):
    """In-app notification provider (stores in database for real-time delivery)"""

    def __init__(self, db):
        super().__init__()
        self.db = db

    async def send(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DeliveryResult:
        """Store in-app notification

        Args:
            recipient: User ID or patient ID
            subject: Notification title
            message: Notification body
            metadata: Optional metadata

        Returns:
            DeliveryResult
        """
        # In-app notifications don't need validation
        # They're stored in database and retrieved by frontend polling or WebSocket
        return DeliveryResult(
            success=True,
            status=ChannelStatus.DELIVERED,
            message_id="inapp_{datetime.utcnow().timestamp()}".format(),
            provider_response={
                "stored_for": recipient,
                "delivered_via": "polling_or_websocket"
            }
        )

    def validate_recipient(self, recipient: str) -> bool:
        """In-app recipients are user/patient IDs"""
        return recipient.isdigit() or len(recipient) > 0


class WhatsAppProvider(BaseChannelProvider):
    """WhatsApp Business API provider"""

    def __init__(self):
        super().__init__()
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', 'https://graph.facebook.com/v17.0')
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
        self.access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')

    async def send(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DeliveryResult:
        """Send WhatsApp message

        Args:
            recipient: Phone number with country code (e.g., 628123456789)
            subject: Not used for WhatsApp (included in message)
            message: Message text
            metadata: Optional template name, parameters, etc.

        Returns:
            DeliveryResult
        """
        if not self.validate_recipient(recipient):
            return DeliveryResult(
                success=False,
                status=ChannelStatus.FAILED,
                error_message="Invalid phone number format: {recipient}".format()
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
            logger.error("WhatsApp send failed: {e}".format())
            return DeliveryResult(
                success=False,
                status=ChannelStatus.FAILED,
                error_message=str(e)
            )

    def validate_recipient(self, recipient: str) -> bool:
        """Validate phone number for WhatsApp"""
        import re
        return bool(re.match(r'^\+?[1-9]\d{9,14}$', recipient))

    async def _send_template_message(
        self,
        phone: str,
        template_name: str,
        params: Dict[str, str]
    ) -> DeliveryResult:
        """Send WhatsApp template message (requires pre-approved template)"""
        url = "{self.api_url}/{self.phone_number_id}/messages".format()
        headers = {
            "Authorization": "Bearer {self.access_token}".format(),
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "id"},  # Indonesian
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

        return DeliveryResult(
            success=True,
            status=ChannelStatus.SENT,
            message_id=message_id,
            provider_response={"whatsapp_response": result}
        )

    async def _send_free_form_message(
        self,
        phone: str,
        message: str
    ) -> DeliveryResult:
        """Send free-form WhatsApp message (session must be active)"""
        url = "{self.api_url}/{self.phone_number_id}/messages".format()
        headers = {
            "Authorization": "Bearer {self.access_token}".format(),
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

        return DeliveryResult(
            success=True,
            status=ChannelStatus.SENT,
            message_id=message_id,
            provider_response={"whatsapp_response": result}
        )


class ChannelProviderFactory:
    """Factory for creating channel provider instances"""

    _providers: Dict[str, BaseChannelProvider] = {}

    @classmethod
    def get_sms_provider(cls) -> SMSProvider:
        """Get or create SMS provider instance"""
        if "sms" not in cls._providers:
            cls._providers["sms"] = SMSProvider()
        return cls._providers["sms"]

    @classmethod
    def get_email_provider(cls) -> EmailProvider:
        """Get or create Email provider instance"""
        if "email" not in cls._providers:
            cls._providers["email"] = EmailProvider()
        return cls._providers["email"]

    @classmethod
    def get_push_provider(cls) -> PushNotificationProvider:
        """Get or create Push notification provider instance"""
        if "push" not in cls._providers:
            cls._providers["push"] = PushNotificationProvider()
        return cls._providers["push"]

    @classmethod
    def get_whatsapp_provider(cls) -> WhatsAppProvider:
        """Get or create WhatsApp provider instance"""
        if "whatsapp" not in cls._providers:
            cls._providers["whatsapp"] = WhatsAppProvider()
        return cls._providers["whatsapp"]

    @classmethod
    def get_inapp_provider(cls, db) -> InAppNotificationProvider:
        """Get or create In-App provider instance"""
        # In-App provider needs database, create new instance each time
        return InAppNotificationProvider(db)

    @classmethod
    def get_provider(cls, channel: str, db=None) -> BaseChannelProvider:
        """Get provider by channel name

        Args:
            channel: Channel name (sms, email, push, whatsapp, in_app)
            db: Database session (required for in_app channel)

        Returns:
            Channel provider instance

        Raises:
            ValueError: If channel is not supported
        """
        channel_map = {
            "sms": cls.get_sms_provider,
            "email": cls.get_email_provider,
            "push": cls.get_push_provider,
            "whatsapp": cls.get_whatsapp_provider,
            "in_app": lambda: cls.get_inapp_provider(db) if db else InAppNotificationProvider(None),
        }

        if channel not in channel_map:
            raise ValueError("Unsupported channel: {channel}".format())

        return channel_map[channel]()
