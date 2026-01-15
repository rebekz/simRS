"""Notification Preference Management API Endpoints

STORY-022-09: Notification Preference Management
Provides endpoints for patients and staff to manage their notification preferences.

Python 3.5+ compatible
"""

import logging
from datetime import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from pydantic import BaseModel

from app.db.session import get_db
from app.models.notifications import NotificationPreference
from app.models.user import User
from app.core.deps import get_current_user


logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class NotificationPreferenceRequest(BaseModel):
    """Request model for upserting notification preferences"""
    notification_type: str
    email_enabled: Optional[bool] = True
    sms_enabled: Optional[bool] = False
    push_enabled: Optional[bool] = True
    in_app_enabled: Optional[bool] = True
    whatsapp_enabled: Optional[bool] = False
    quiet_hours_start: Optional[str] = None  # Format: "HH:MM"
    quiet_hours_end: Optional[str] = None  # Format: "HH:MM"
    timezone: Optional[str] = "Asia/Jakarta"


class NotificationPreferenceResponse(BaseModel):
    """Response model for notification preferences"""
    id: int
    user_id: int
    user_type: str
    notification_type: str
    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool
    in_app_enabled: bool
    whatsapp_enabled: bool
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    timezone: str

    class Config:
        orm_mode = True


class BulkPreferenceRequest(BaseModel):
    """Request model for bulk preference update"""
    preferences: List[NotificationPreferenceRequest]


class ConsentRequest(BaseModel):
    """Request model for consent management"""
    notification_type: str
    consent_given: bool
    consent_expiration: Optional[str] = None  # ISO date string


@router.get("/my-preferences", response_model=List[NotificationPreferenceResponse])
async def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's notification preferences

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of user's notification preferences
    """
    try:
        # Determine user type
        user_type = "staff" if current_user.role != "patient" else "patient"

        query = select(NotificationPreference).where(
            and_(
                NotificationPreference.user_id == current_user.id,
                NotificationPreference.user_type == user_type
            )
        )
        result = await db.execute(query)
        preferences = result.scalars().all()

        return [
            NotificationPreferenceResponse(
                id=pref.id,
                user_id=pref.user_id,
                user_type=pref.user_type,
                notification_type=pref.notification_type,
                email_enabled=pref.email_enabled,
                sms_enabled=pref.sms_enabled,
                push_enabled=pref.push_enabled,
                in_app_enabled=pref.in_app_enabled,
                whatsapp_enabled=pref.whatsapp_enabled,
                quiet_hours_start=pref.quiet_hours_start.strftime("%H:%M") if pref.quiet_hours_start else None,
                quiet_hours_end=pref.quiet_hours_end.strftime("%H:%M") if pref.quiet_hours_end else None,
                timezone=pref.timezone
            )
            for pref in preferences
        ]

    except Exception as e:
        logger.error("Error getting preferences: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve preferences"
        )


@router.get("/my-preferences/{notification_type}", response_model=NotificationPreferenceResponse)
async def get_my_preference_by_type(
    notification_type: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get preference for specific notification type

    Args:
        notification_type: Type of notification
        current_user: Authenticated user
        db: Database session

    Returns:
        Notification preference for specified type
    """
    try:
        # Determine user type
        user_type = "staff" if current_user.role != "patient" else "patient"

        query = select(NotificationPreference).where(
            and_(
                NotificationPreference.user_id == current_user.id,
                NotificationPreference.user_type == user_type,
                NotificationPreference.notification_type == notification_type
            )
        )
        result = await db.execute(query)
        preference = result.scalar_one_or_none()

        if not preference:
            # Return default preferences
            return NotificationPreferenceResponse(
                id=0,
                user_id=current_user.id,
                user_type=user_type,
                notification_type=notification_type,
                email_enabled=True,
                sms_enabled=False,
                push_enabled=True,
                in_app_enabled=True,
                whatsapp_enabled=False,
                quiet_hours_start=None,
                quiet_hours_end=None,
                timezone="Asia/Jakarta"
            )

        return NotificationPreferenceResponse(
            id=preference.id,
            user_id=preference.user_id,
            user_type=preference.user_type,
            notification_type=preference.notification_type,
            email_enabled=preference.email_enabled,
            sms_enabled=preference.sms_enabled,
            push_enabled=preference.push_enabled,
            in_app_enabled=preference.in_app_enabled,
            whatsapp_enabled=preference.whatsapp_enabled,
            quiet_hours_start=preference.quiet_hours_start.strftime("%H:%M") if preference.quiet_hours_start else None,
            quiet_hours_end=preference.quiet_hours_end.strftime("%H:%M") if preference.quiet_hours_end else None,
            timezone=preference.timezone
        )

    except Exception as e:
        logger.error("Error getting preference: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve preference"
        )


@router.put("/my-preferences/{notification_type}", response_model=NotificationPreferenceResponse)
async def update_my_preference(
    notification_type: str,
    request: NotificationPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update or create notification preference for specific type

    Args:
        notification_type: Type of notification
        request: Preference data
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated notification preference
    """
    try:
        # Determine user type
        user_type = "staff" if current_user.role != "patient" else "patient"

        # Check if preference exists
        query = select(NotificationPreference).where(
            and_(
                NotificationPreference.user_id == current_user.id,
                NotificationPreference.user_type == user_type,
                NotificationPreference.notification_type == notification_type
            )
        )
        result = await db.execute(query)
        preference = result.scalar_one_or_none()

        # Parse time strings
        quiet_start = None
        quiet_end = None

        if request.quiet_hours_start:
            hours, minutes = request.quiet_hours_start.split(":")
            quiet_start = time(int(hours), int(minutes))

        if request.quiet_hours_end:
            hours, minutes = request.quiet_hours_end.split(":")
            quiet_end = time(int(hours), int(minutes))

        if preference:
            # Update existing
            preference.email_enabled = request.email_enabled
            preference.sms_enabled = request.sms_enabled
            preference.push_enabled = request.push_enabled
            preference.in_app_enabled = request.in_app_enabled
            preference.whatsapp_enabled = request.whatsapp_enabled
            preference.quiet_hours_start = quiet_start
            preference.quiet_hours_end = quiet_end
            preference.timezone = request.timezone
        else:
            # Create new
            preference = NotificationPreference(
                user_id=current_user.id,
                user_type=user_type,
                notification_type=request.notification_type,
                email_enabled=request.email_enabled,
                sms_enabled=request.sms_enabled,
                push_enabled=request.push_enabled,
                in_app_enabled=request.in_app_enabled,
                whatsapp_enabled=request.whatsapp_enabled,
                quiet_hours_start=quiet_start,
                quiet_hours_end=quiet_end,
                timezone=request.timezone
            )
            db.add(preference)

        await db.commit()
        await db.refresh(preference)

        logger.info(
            "Updated preference for user {} type {}".format(
                current_user.id, notification_type
            )
        )

        return NotificationPreferenceResponse(
            id=preference.id,
            user_id=preference.user_id,
            user_type=preference.user_type,
            notification_type=preference.notification_type,
            email_enabled=preference.email_enabled,
            sms_enabled=preference.sms_enabled,
            push_enabled=preference.push_enabled,
            in_app_enabled=preference.in_app_enabled,
            whatsapp_enabled=preference.whatsapp_enabled,
            quiet_hours_start=preference.quiet_hours_start.strftime("%H:%M") if preference.quiet_hours_start else None,
            quiet_hours_end=preference.quiet_hours_end.strftime("%H:%M") if preference.quiet_hours_end else None,
            timezone=preference.timezone
        )

    except Exception as e:
        logger.error("Error updating preference: {}".format(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preference"
        )


@router.put("/my-preferences")
async def update_my_preferences_bulk(
    request: BulkPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk update notification preferences

    Args:
        request: List of preferences to update
        current_user: Authenticated user
        db: Database session

    Returns:
        Summary of updated preferences
    """
    try:
        # Determine user type
        user_type = "staff" if current_user.role != "patient" else "patient"

        updated_count = 0
        created_count = 0

        for pref_request in request.preferences:
            # Check if preference exists
            query = select(NotificationPreference).where(
                and_(
                    NotificationPreference.user_id == current_user.id,
                    NotificationPreference.user_type == user_type,
                    NotificationPreference.notification_type == pref_request.notification_type
                )
            )
            result = await db.execute(query)
            preference = result.scalar_one_or_none()

            # Parse time strings
            quiet_start = None
            quiet_end = None

            if pref_request.quiet_hours_start:
                hours, minutes = pref_request.quiet_hours_start.split(":")
                quiet_start = time(int(hours), int(minutes))

            if pref_request.quiet_hours_end:
                hours, minutes = pref_request.quiet_hours_end.split(":")
                quiet_end = time(int(hours), int(minutes))

            if preference:
                # Update existing
                preference.email_enabled = pref_request.email_enabled
                preference.sms_enabled = pref_request.sms_enabled
                preference.push_enabled = pref_request.push_enabled
                preference.in_app_enabled = pref_request.in_app_enabled
                preference.whatsapp_enabled = pref_request.whatsapp_enabled
                preference.quiet_hours_start = quiet_start
                preference.quiet_hours_end = quiet_end
                preference.timezone = pref_request.timezone
                updated_count += 1
            else:
                # Create new
                preference = NotificationPreference(
                    user_id=current_user.id,
                    user_type=user_type,
                    notification_type=pref_request.notification_type,
                    email_enabled=pref_request.email_enabled,
                    sms_enabled=pref_request.sms_enabled,
                    push_enabled=pref_request.push_enabled,
                    in_app_enabled=pref_request.in_app_enabled,
                    whatsapp_enabled=pref_request.whatsapp_enabled,
                    quiet_hours_start=quiet_start,
                    quiet_hours_end=quiet_end,
                    timezone=pref_request.timezone
                )
                db.add(preference)
                created_count += 1

        await db.commit()

        logger.info(
            "Bulk update for user {}: {} updated, {} created".format(
                current_user.id, updated_count, created_count
            )
        )

        return {
            "message": "Preferences updated successfully",
            "updated": updated_count,
            "created": created_count
        }

    except Exception as e:
        logger.error("Error in bulk update: {}".format(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )


@router.delete("/my-preferences/{notification_type}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_preference(
    notification_type: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete notification preference (revert to defaults)

    Args:
        notification_type: Type of notification
        current_user: Authenticated user
        db: Database session
    """
    try:
        # Determine user type
        user_type = "staff" if current_user.role != "patient" else "patient"

        query = select(NotificationPreference).where(
            and_(
                NotificationPreference.user_id == current_user.id,
                NotificationPreference.user_type == user_type,
                NotificationPreference.notification_type == notification_type
            )
        )
        result = await db.execute(query)
        preference = result.scalar_one_or_none()

        if preference:
            await db.delete(preference)
            await db.commit()

            logger.info(
                "Deleted preference for user {} type {}".format(
                    current_user.id, notification_type
                )
            )

    except Exception as e:
        logger.error("Error deleting preference: {}".format(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete preference"
        )


@router.get("/defaults", response_model=List[NotificationPreferenceResponse])
async def get_default_preferences(
    user_type: str = Query("patient", description="User type (patient/staff)"),
    db: AsyncSession = Depends(get_db)
):
    """Get default notification preferences for new users

    Args:
        user_type: Type of user
        db: Database session

    Returns:
        List of default preferences
    """
    try:
        # Define default notification types
        if user_type == "patient":
            notification_types = [
                "appointment_reminder",
                "medication_reminder",
                "lab_result",
                "payment_reminder",
                "queue_update"
            ]
        else:
            notification_types = [
                "appointment_reminder",
                "critical_alert",
                "system_alert",
                "queue_update"
            ]

        # Return defaults (no DB query needed)
        defaults = []
        for notif_type in notification_types:
            defaults.append({
                "id": 0,
                "user_id": 0,
                "user_type": user_type,
                "notification_type": notif_type,
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True,
                "in_app_enabled": True,
                "whatsapp_enabled": False,
                "quiet_hours_start": None,
                "quiet_hours_end": None,
                "timezone": "Asia/Jakarta"
            })

        return defaults

    except Exception as e:
        logger.error("Error getting defaults: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve default preferences"
        )


@router.get("/check-preference/{user_id}/{notification_type}")
async def check_user_preference(
    user_id: int,
    notification_type: str,
    channel: Optional[str] = Query(None, description="Channel to check (email, sms, push, etc.)"),
    db: AsyncSession = Depends(get_db)
):
    """Check if user has opted in for specific notification type and channel
    Internal endpoint used by notification system.

    Args:
        user_id: User ID to check
        notification_type: Type of notification
        channel: Specific channel to check
        db: Database session

    Returns:
        Preference status
    """
    try:
        # Check both patient and staff user types
        query = select(NotificationPreference).where(
            and_(
                NotificationPreference.user_id == user_id,
                NotificationPreference.notification_type == notification_type
            )
        )
        result = await db.execute(query)
        preference = result.scalar_one_or_none()

        if not preference:
            # Return default enabled
            return {
                "user_id": user_id,
                "notification_type": notification_type,
                "enabled": True,
                "channels": {
                    "email": True,
                    "sms": False,
                    "push": True,
                    "in_app": True,
                    "whatsapp": False
                }
            }

        channels = {
            "email": preference.email_enabled,
            "sms": preference.sms_enabled,
            "push": preference.push_enabled,
            "in_app": preference.in_app_enabled,
            "whatsapp": preference.whatsapp_enabled
        }

        # Check specific channel if requested
        if channel:
            channel_enabled = channels.get(channel, False)
            return {
                "user_id": user_id,
                "notification_type": notification_type,
                "channel": channel,
                "enabled": channel_enabled
            }

        return {
            "user_id": user_id,
            "notification_type": notification_type,
            "enabled": any(channels.values()),
            "channels": channels
        }

    except Exception as e:
        logger.error("Error checking preference: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check preference"
        )
