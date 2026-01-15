"""Patient Portal Account Settings Endpoints

API endpoints for managing patient portal account settings including profile,
notifications, appearance, privacy, and security settings.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.models.patient_portal import PatientPortalUser
from app.api.v1.endpoints.patient_portal_auth import get_current_portal_user
from app.schemas.patient_portal.account import (
    AccountSettingsResponse,
    ProfileUpdateRequest,
    ProfileUpdateResponse,
    PasswordChangeRequest,
    NotificationPreferences,
    AppearancePreferences,
    PrivacySettings,
    SecuritySettingsResponse,
    SessionInfo,
    EmailVerificationRequest,
    PhoneVerificationRequest,
    VerificationSendRequest,
    VerificationSendResponse,
    DeleteAccountRequest,
    DeleteAccountResponse,
    RevokeSessionRequest,
    RevokeAllSessionsResponse,
)
from app.services.patient_portal.account_service import AccountSettingsService

router = APIRouter()


@router.get("/account/settings", response_model=AccountSettingsResponse, operation_id="get_account_settings")
async def get_account_settings(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all account settings

    Returns complete account settings including profile, notifications,
    appearance, privacy, and security information.

    Requires authentication.
    """
    service = AccountSettingsService(db)
    settings = await service.get_account_settings(current_user)
    return settings


@router.put("/account/profile", response_model=ProfileUpdateResponse, operation_id="update_account_profile")
async def update_profile(
    update_data: ProfileUpdateRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile information

    Updates email and/or phone number. Changes require verification before
    taking effect. A verification email/SMS will be sent for any changed values.

    - Email: Must be unique across all portal accounts
    - Phone: Must match Indonesian phone format (+62... or 08...)

    Requires authentication.
    """
    service = AccountSettingsService(db)

    try:
        updated_profile = await service.update_profile(current_user, update_data)
        return updated_profile
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/account/change-password", operation_id="change_account_password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Change password

    Changes the user's password after verifying the current password.
    The new password must meet strength requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    A confirmation email will be sent after successful password change.

    Requires authentication.
    """
    service = AccountSettingsService(db)

    try:
        message = await service.change_password(
            current_user,
            password_data.current_password,
            password_data.new_password
        )
        return {"message": message}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.put("/account/notifications", response_model=NotificationPreferences, operation_id="update_notification_preferences")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Update notification preferences

    Updates notification preferences for email, SMS, and push notifications.
    Controls which types of notifications are sent and through which channels.

    Requires authentication.
    """
    service = AccountSettingsService(db)
    updated = await service.update_notification_preferences(current_user, preferences)
    return updated


@router.put("/account/appearance", response_model=AppearancePreferences, operation_id="update_appearance_preferences")
async def update_appearance_preferences(
    preferences: AppearancePreferences,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Update appearance preferences

    Updates appearance settings including theme, language, timezone,
    date format, time format, font size, and accessibility options.

    Requires authentication.
    """
    service = AccountSettingsService(db)
    updated = await service.update_appearance_preferences(current_user, preferences)
    return updated


@router.put("/account/privacy", response_model=PrivacySettings, operation_id="update_privacy_settings")
async def update_privacy_settings(
    settings: PrivacySettings,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Update privacy settings

    Updates privacy settings controlling data sharing, caregiver access,
    communication preferences, and data retention consent.

    Requires authentication.
    """
    service = AccountSettingsService(db)
    updated = await service.update_privacy_settings(current_user, settings)
    return updated


@router.get("/account/security", response_model=SecuritySettingsResponse, operation_id="get_security_settings")
async def get_security_settings(
    request: Request,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get security information

    Returns detailed security settings including:
    - MFA status
    - Security questions
    - Password information (last change, age)
    - Failed login attempts
    - Lock status
    - Active and recent sessions

    Requires authentication.
    """
    service = AccountSettingsService(db)

    # Get current session ID from token for marking
    from app.core.security import hash_token
    from app.models.patient_portal import PatientPortalSession
    from sqlalchemy import select, and_

    token = request.headers.get("authorization", "").replace("Bearer ", "")
    current_session_id = None

    if token:
        token_hash = hash_token(token)
        result = await db.execute(
            select(PatientPortalSession).where(
                and_(
                    PatientPortalSession.portal_user_id == current_user.id,
                    PatientPortalSession.token_hash == token_hash
                )
            )
        )
        session = result.scalar_one_or_none()
        if session:
            current_session_id = session.id

    return await service.get_security_settings(current_user, current_session_id)


@router.post("/account/send-verification", response_model=VerificationSendResponse, operation_id="send_verification_code")
async def send_verification_code(
    request_data: VerificationSendRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Send verification code

    Sends a verification code for email or phone verification.
    The code/token is valid for 1 hour.

    - Email: Sends a verification link
    - Phone: Sends a 6-digit SMS code

    Requires authentication.
    """
    service = AccountSettingsService(db)

    try:
        response = await service.send_verification(current_user, request_data.type)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/account/verify-email", operation_id="verify_email_address")
async def verify_email(
    verification_data: EmailVerificationRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify email address

    Verifies the email address using the token sent to the user's email.
    Email must be verified before certain account features can be used.

    Requires authentication.
    """
    service = AccountSettingsService(db)

    try:
        message = await service.verify_email(current_user, verification_data.token)
        return {"message": message}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/account/verify-phone", operation_id="verify_phone_number")
async def verify_phone(
    verification_data: PhoneVerificationRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify phone number

    Verifies the phone number using the 6-digit SMS code.
    Phone must be verified before SMS notifications can be sent.

    Maximum 3 attempts allowed per code.

    Requires authentication.
    """
    service = AccountSettingsService(db)

    try:
        message = await service.verify_phone(current_user, verification_data.code)
        return {"message": message}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/account", response_model=DeleteAccountResponse, operation_id="delete_account")
async def delete_account(
    deletion_request: DeleteAccountRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Request account deletion

    Performs a soft delete of the account, deactivating it immediately.
    Data will be permanently deleted after 30 days. Contact support during
    this period to restore the account.

    All active sessions will be revoked.

    Requires:
    - Current password verification
    - Explicit confirmation
    - Acknowledgment of permanent data loss

    Requires authentication.
    """
    service = AccountSettingsService(db)

    try:
        response = await service.request_account_deletion(current_user, deletion_request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/account/sessions/revoke", operation_id="revoke_session")
async def revoke_session(
    session_data: RevokeSessionRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke a specific session

    Revokes a specific active session. The session will no longer be valid.
    Useful for removing unrecognized devices or locations.

    Requires authentication.
    """
    service = AccountSettingsService(db)

    try:
        await service.revoke_session(current_user, session_data.session_id)
        return {"message": "Session revoked successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/account/sessions/revoke-all", response_model=RevokeAllSessionsResponse, operation_id="revoke_all_sessions")
async def revoke_all_sessions(
    request: Request,
    revoke_all: bool = True,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke all sessions

    Revokes all active sessions for the user, optionally excluding the current session.
    Use this after a security incident or when you suspect unauthorized access.

    - Set revoke_all=true to revoke all sessions including current (requires re-login)
    - Set revoke_all=false to revoke all except current session

    Requires authentication.
    """
    service = AccountSettingsService(db)

    # Get current session ID
    from app.core.security import decode_token, hash_token
    from app.models.patient_portal import PatientPortalSession
    from sqlalchemy import select, and_

    current_session_id = None
    if not revoke_all:
        token = request.headers.get("authorization", "").replace("Bearer ", "")
        if token:
            token_hash = hash_token(token)
            result = await db.execute(
                select(PatientPortalSession).where(
                    and_(
                        PatientPortalSession.portal_user_id == current_user.id,
                        PatientPortalSession.token_hash == token_hash
                    )
                )
            )
            session = result.scalar_one_or_none()
            if session:
                current_session_id = session.id

    revoked_count = await service.revoke_all_sessions(
        current_user,
        except_session_id=None if revoke_all else current_session_id
    )

    return RevokeAllSessionsResponse(
        revoked_count=revoked_count,
        message=f"Revoked {revoked_count} session(s)" + (
            ". You have been logged out from all devices." if revoke_all
            else ". You remain logged in on this device."
        )
    )
