"""Notification Preference Service

STORY-022-09: Notification Preference Management
Service layer for managing user notification preferences.

Python 3.5+ compatible
"""

import logging
from datetime import time, datetime
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.notifications import NotificationPreference


logger = logging.getLogger(__name__)


class PreferenceManager(object):
    """Manages notification preferences for users"""

    # Default notification types by user type
    DEFAULT_PATIENT_TYPES = [
        "appointment_reminder",
        "medication_reminder",
        "lab_result",
        "payment_reminder",
        "queue_update"
    ]

    DEFAULT_STAFF_TYPES = [
        "appointment_reminder",
        "critical_alert",
        "system_alert",
        "queue_update"
    ]

    # Default channel settings
    DEFAULT_CHANNEL_SETTINGS = {
        "email_enabled": True,
        "sms_enabled": False,
        "push_enabled": True,
        "in_app_enabled": True,
        "whatsapp_enabled": False
    }

    def __init__(self, db):
        self.db = db

    async def get_user_preferences(self, user_id, user_type):
        """Get all preferences for a user

        Args:
            user_id: User ID
            user_type: Type of user (patient/staff)

        Returns:
            List of NotificationPreference objects
        """
        query = select(NotificationPreference).where(
            and_(
                NotificationPreference.user_id == user_id,
                NotificationPreference.user_type == user_type
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_preference(self, user_id, user_type, notification_type):
        """Get specific preference for user

        Args:
            user_id: User ID
            user_type: Type of user (patient/staff)
            notification_type: Type of notification

        Returns:
            NotificationPreference object or None
        """
        query = select(NotificationPreference).where(
            and_(
                NotificationPreference.user_id == user_id,
                NotificationPreference.user_type == user_type,
                NotificationPreference.notification_type == notification_type
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def upsert_preference(self, user_id, user_type, notification_type,
                                email_enabled=None, sms_enabled=None,
                                push_enabled=None, in_app_enabled=None,
                                whatsapp_enabled=None,
                                quiet_hours_start=None, quiet_hours_end=None,
                                timezone="Asia/Jakarta"):
        """Update or create notification preference

        Args:
            user_id: User ID
            user_type: Type of user (patient/staff)
            notification_type: Type of notification
            email_enabled: Enable email notifications
            sms_enabled: Enable SMS notifications
            push_enabled: Enable push notifications
            in_app_enabled: Enable in-app notifications
            whatsapp_enabled: Enable WhatsApp notifications
            quiet_hours_start: Start of quiet hours (time object or "HH:MM" string)
            quiet_hours_end: End of quiet hours (time object or "HH:MM" string)
            timezone: User timezone

        Returns:
            NotificationPreference object
        """
        # Check if preference exists
        preference = await self.get_preference(user_id, user_type, notification_type)

        # Parse time strings if provided
        if isinstance(quiet_hours_start, str):
            hours, minutes = quiet_hours_start.split(":")
            quiet_hours_start = time(int(hours), int(minutes))

        if isinstance(quiet_hours_end, str):
            hours, minutes = quiet_hours_end.split(":")
            quiet_hours_end = time(int(hours), int(minutes))

        if preference:
            # Update existing
            if email_enabled is not None:
                preference.email_enabled = email_enabled
            if sms_enabled is not None:
                preference.sms_enabled = sms_enabled
            if push_enabled is not None:
                preference.push_enabled = push_enabled
            if in_app_enabled is not None:
                preference.in_app_enabled = in_app_enabled
            if whatsapp_enabled is not None:
                preference.whatsapp_enabled = whatsapp_enabled

            preference.quiet_hours_start = quiet_hours_start
            preference.quiet_hours_end = quiet_hours_end
            preference.timezone = timezone
            preference.updated_at = datetime.utcnow()
        else:
            # Create new with defaults for unspecified channels
            preference = NotificationPreference(
                user_id=user_id,
                user_type=user_type,
                notification_type=notification_type,
                email_enabled=email_enabled if email_enabled is not None else self.DEFAULT_CHANNEL_SETTINGS["email_enabled"],
                sms_enabled=sms_enabled if sms_enabled is not None else self.DEFAULT_CHANNEL_SETTINGS["sms_enabled"],
                push_enabled=push_enabled if push_enabled is not None else self.DEFAULT_CHANNEL_SETTINGS["push_enabled"],
                in_app_enabled=in_app_enabled if in_app_enabled is not None else self.DEFAULT_CHANNEL_SETTINGS["in_app_enabled"],
                whatsapp_enabled=whatsapp_enabled if whatsapp_enabled is not None else self.DEFAULT_CHANNEL_SETTINGS["whatsapp_enabled"],
                quiet_hours_start=quiet_hours_start,
                quiet_hours_end=quiet_hours_end,
                timezone=timezone
            )
            self.db.add(preference)

        await self.db.flush()
        return preference

    async def delete_preference(self, user_id, user_type, notification_type):
        """Delete notification preference (revert to defaults)

        Args:
            user_id: User ID
            user_type: Type of user (patient/staff)
            notification_type: Type of notification

        Returns:
            True if deleted, False if not found
        """
        preference = await self.get_preference(user_id, user_type, notification_type)

        if preference:
            await self.db.delete(preference)
            return True

        return False

    async def is_channel_enabled(self, user_id, user_type, notification_type, channel):
        """Check if specific channel is enabled for notification type

        Args:
            user_id: User ID
            user_type: Type of user (patient/staff)
            notification_type: Type of notification
            channel: Channel name (email, sms, push, in_app, whatsapp)

        Returns:
            True if channel is enabled, False otherwise
        """
        preference = await self.get_preference(user_id, user_type, notification_type)

        if not preference:
            # Return default for channel
            return self.DEFAULT_CHANNEL_SETTINGS.get("{}_enabled".format(channel), False)

        # Check specific channel
        channel_map = {
            "email": preference.email_enabled,
            "sms": preference.sms_enabled,
            "push": preference.push_enabled,
            "in_app": preference.in_app_enabled,
            "whatsapp": preference.whatsapp_enabled
        }

        return channel_map.get(channel, False)

    async def is_quiet_hours(self, user_id, user_type, notification_type, check_time=None):
        """Check if current time is within user's quiet hours

        Args:
            user_id: User ID
            user_type: Type of user (patient/staff)
            notification_type: Type of notification
            check_time: Time to check (defaults to current time)

        Returns:
            True if in quiet hours, False otherwise
        """
        preference = await self.get_preference(user_id, user_type, notification_type)

        if not preference or not preference.quiet_hours_start or not preference.quiet_hours_end:
            return False

        if check_time is None:
            check_time = datetime.utcnow().time()

        # Check if current time is within quiet hours range
        start = preference.quiet_hours_start
        end = preference.quiet_hours_end

        # Handle case where quiet hours span midnight (e.g., 22:00 - 06:00)
        if start <= end:
            return start <= check_time <= end
        else:
            return check_time >= start or check_time <= end

    async def get_enabled_channels(self, user_id, user_type, notification_type):
        """Get list of enabled channels for notification type

        Args:
            user_id: User ID
            user_type: Type of user (patient/staff)
            notification_type: Type of notification

        Returns:
            List of enabled channel names
        """
        preference = await self.get_preference(user_id, user_type, notification_type)

        if not preference:
            # Return default enabled channels
            return [ch for ch, enabled in self.DEFAULT_CHANNEL_SETTINGS.items() if enabled]

        channels = []
        if preference.email_enabled:
            channels.append("email")
        if preference.sms_enabled:
            channels.append("sms")
        if preference.push_enabled:
            channels.append("push")
        if preference.in_app_enabled:
            channels.append("in_app")
        if preference.whatsapp_enabled:
            channels.append("whatsapp")

        return channels

    async def initialize_default_preferences(self, user_id, user_type):
        """Initialize default preferences for new user

        Args:
            user_id: User ID
            user_type: Type of user (patient/staff)

        Returns:
            List of created NotificationPreference objects
        """
        notification_types = (
            self.DEFAULT_PATIENT_TYPES if user_type == "patient"
            else self.DEFAULT_STAFF_TYPES
        )

        preferences = []
        for notif_type in notification_types:
            pref = await self.upsert_preference(
                user_id=user_id,
                user_type=user_type,
                notification_type=notif_type,
                **self.DEFAULT_CHANNEL_SETTINGS
            )
            preferences.append(pref)

        await self.db.commit()
        logger.info(
            "Initialized default preferences for user {} ({})".format(
                user_id, user_type
            )
        )

        return preferences

    async def bulk_update_preferences(self, user_id, user_type, preferences_data):
        """Bulk update multiple preferences

        Args:
            user_id: User ID
            user_type: Type of user (patient/staff)
            preferences_data: List of preference dictionaries

        Returns:
            Dictionary with update counts
        """
        updated = 0
        created = 0

        for pref_data in preferences_data:
            notification_type = pref_data.get("notification_type")
            if not notification_type:
                continue

            existing = await self.get_preference(user_id, user_type, notification_type)

            if existing:
                updated += 1
            else:
                created += 1

            await self.upsert_preference(
                user_id=user_id,
                user_type=user_type,
                notification_type=notification_type,
                email_enabled=pref_data.get("email_enabled"),
                sms_enabled=pref_data.get("sms_enabled"),
                push_enabled=pref_data.get("push_enabled"),
                in_app_enabled=pref_data.get("in_app_enabled"),
                whatsapp_enabled=pref_data.get("whatsapp_enabled"),
                quiet_hours_start=pref_data.get("quiet_hours_start"),
                quiet_hours_end=pref_data.get("quiet_hours_end"),
                timezone=pref_data.get("timezone", "Asia/Jakarta")
            )

        await self.db.commit()

        logger.info(
            "Bulk update for user {}: {} updated, {} created".format(
                user_id, updated, created
            )
        )

        return {"updated": updated, "created": created}


def get_preference_manager(db):
    """Get or create preference manager instance

    Args:
        db: Database session

    Returns:
        PreferenceManager instance
    """
    return PreferenceManager(db)
