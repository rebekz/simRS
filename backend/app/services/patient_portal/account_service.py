"""Patient Portal Account Settings Service

Service layer for patient portal account settings management.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import Optional, Literal
import secrets

from app.models.patient_portal import (
    PatientPortalUser,
    PatientPortalSession,
    PatientPortalVerification,
    VerificationType,
    VerificationStatus,
)
from app.models.patient import Patient
from app.core.security import verify_password, get_password_hash
from app.schemas.patient_portal.account import (
    ProfileSettings,
    ProfileUpdateRequest,
    ProfileUpdateResponse,
    NotificationPreferences,
    AppearancePreferences,
    PrivacySettings,
    SecuritySettingsOverview,
    SecuritySettingsResponse,
    SessionInfo,
    EmailVerificationRequest,
    PhoneVerificationRequest,
    VerificationSendRequest,
    VerificationSendResponse,
    DeleteAccountRequest,
    DeleteAccountResponse,
)
from app.services.patient_portal.email_service import PatientPortalEmailService
from app.services.patient_portal.sms_service import PatientPortalSMSService


class AccountSettingsService:
    """Service for managing patient portal account settings"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_account_settings(self, portal_user: PatientPortalUser) -> dict:
        """Get complete account settings for a portal user

        Args:
            portal_user: The authenticated portal user

        Returns:
            Dictionary containing profile, notifications, appearance, privacy, and security settings
        """
        # Get active sessions count
        result = await self.db.execute(
            select(PatientPortalSession).where(
                and_(
                    PatientPortalSession.portal_user_id == portal_user.id,
                    PatientPortalSession.is_active == True,
                    PatientPortalSession.is_revoked == False
                )
            )
        )
        active_sessions = len(result.scalars().all())

        # Build profile settings
        profile = ProfileSettings(
            id=portal_user.id,
            email=portal_user.email,
            phone=portal_user.phone,
            patient_id=portal_user.patient_id,
            patient_name=portal_user.patient.full_name if portal_user.patient else None,
            medical_record_number=portal_user.patient.medical_record_number if portal_user.patient else None,
            is_active=portal_user.is_active,
            is_email_verified=portal_user.is_email_verified,
            is_phone_verified=portal_user.is_phone_verified,
            is_identity_verified=portal_user.is_identity_verified,
            created_at=portal_user.created_at,
            updated_at=portal_user.updated_at,
            last_login=portal_user.last_login,
        )

        # Default notification preferences (would be stored in DB in production)
        notifications = NotificationPreferences()

        # Default appearance preferences (would be stored in DB in production)
        appearance = AppearancePreferences()

        # Default privacy settings (would be stored in DB in production)
        privacy = PrivacySettings()

        # Build security overview
        password_age_days = None
        if portal_user.password_changed_at:
            password_age_days = (datetime.utcnow() - portal_user.password_changed_at).days

        security = SecuritySettingsOverview(
            mfa_enabled=portal_user.mfa_enabled,
            has_security_questions=bool(portal_user.security_question_1),
            last_password_change=portal_user.password_changed_at,
            password_age_days=password_age_days,
            failed_login_attempts=portal_user.failed_login_attempts,
            is_locked=bool(portal_user.locked_until and portal_user.locked_until > datetime.utcnow()),
            locked_until=portal_user.locked_until,
            active_sessions=active_sessions,
        )

        return {
            "profile": profile,
            "notifications": notifications,
            "appearance": appearance,
            "privacy": privacy,
            "security": security,
        }

    async def update_profile(
        self,
        portal_user: PatientPortalUser,
        update_data: ProfileUpdateRequest
    ) -> ProfileUpdateResponse:
        """Update user profile information

        Args:
            portal_user: The authenticated portal user
            update_data: Profile update request data

        Returns:
            Updated profile response with verification requirements

        Raises:
            ValueError: If update fails or validation fails
        """
        verification_type = None
        requires_verification = False

        # Check if email is being changed
        if update_data.email and update_data.email != portal_user.email:
            # Check if email already exists
            result = await self.db.execute(
                select(PatientPortalUser).where(PatientPortalUser.email == update_data.email)
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise ValueError("Email address already registered")

            # Update email and mark as unverified
            portal_user.email = update_data.email
            portal_user.is_email_verified = False
            requires_verification = True
            if verification_type is None:
                verification_type = "email"
            else:
                verification_type = "both"

        # Check if phone is being changed
        if update_data.phone and update_data.phone != portal_user.phone:
            # Update phone and mark as unverified
            portal_user.phone = update_data.phone
            portal_user.is_phone_verified = False
            requires_verification = True
            if verification_type is None:
                verification_type = "phone"
            else:
                verification_type = "both"

        # Update timestamp
        portal_user.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(portal_user)

        return ProfileUpdateResponse(
            id=portal_user.id,
            email=portal_user.email,
            phone=portal_user.phone,
            is_email_verified=portal_user.is_email_verified,
            is_phone_verified=portal_user.is_phone_verified,
            message="Profile updated successfully" + (
                ". Please verify your new contact information." if requires_verification else ""
            ),
            requires_verification=requires_verification,
            verification_type=verification_type,
        )

    async def change_password(
        self,
        portal_user: PatientPortalUser,
        current_password: str,
        new_password: str
    ) -> str:
        """Change user password

        Args:
            portal_user: The authenticated portal user
            current_password: Current password for verification
            new_password: New password to set

        Returns:
            Success message

        Raises:
            ValueError: If current password is invalid or update fails
        """
        # Verify current password
        if not verify_password(current_password, portal_user.hashed_password):
            raise ValueError("Current password is incorrect")

        # Update password
        portal_user.hashed_password = get_password_hash(new_password)
        portal_user.password_changed_at = datetime.utcnow()
        portal_user.updated_at = datetime.utcnow()

        await self.db.commit()

        # Send confirmation email
        email_service = PatientPortalEmailService()
        await email_service.send_password_changed_email(
            to_email=portal_user.email,
            patient_name=portal_user.patient.full_name if portal_user.patient else "Patient",
            changed_at=datetime.utcnow(),
        )

        return "Password changed successfully"

    async def update_notification_preferences(
        self,
        portal_user: PatientPortalUser,
        preferences: NotificationPreferences
    ) -> NotificationPreferences:
        """Update notification preferences

        Args:
            portal_user: The authenticated portal user
            preferences: New notification preferences

        Returns:
            Updated notification preferences

        Note:
            In production, this would store preferences in a separate table.
            Currently returns the input preferences as confirmation.
        """
        # In production, would store in database
        # For now, just return the preferences to confirm update
        return preferences

    async def update_appearance_preferences(
        self,
        portal_user: PatientPortalUser,
        preferences: AppearancePreferences
    ) -> AppearancePreferences:
        """Update appearance preferences

        Args:
            portal_user: The authenticated portal user
            preferences: New appearance preferences

        Returns:
            Updated appearance preferences

        Note:
            In production, this would store preferences in a separate table.
            Currently returns the input preferences as confirmation.
        """
        # In production, would store in database
        # For now, just return the preferences to confirm update
        return preferences

    async def update_privacy_settings(
        self,
        portal_user: PatientPortalUser,
        settings: PrivacySettings
    ) -> PrivacySettings:
        """Update privacy settings

        Args:
            portal_user: The authenticated portal user
            settings: New privacy settings

        Returns:
            Updated privacy settings

        Note:
            In production, this would store settings in a separate table.
            Currently returns the input settings as confirmation.
        """
        # In production, would store in database
        # For now, just return the settings to confirm update
        return settings

    async def get_security_settings(
        self,
        portal_user: PatientPortalUser,
        current_session_id: Optional[int] = None
    ) -> SecuritySettingsResponse:
        """Get detailed security settings

        Args:
            portal_user: The authenticated portal user
            current_session_id: Current session ID for marking

        Returns:
            Detailed security settings including session information
        """
        # Get recent sessions
        result = await self.db.execute(
            select(PatientPortalSession)
            .where(PatientPortalSession.portal_user_id == portal_user.id)
            .order_by(PatientPortalSession.created_at.desc())
            .limit(10)
        )
        sessions = result.scalars().all()

        recent_sessions = [
            SessionInfo(
                id=session.id,
                device_type=session.device_type,
                browser=session.browser,
                os=session.os,
                ip_address=session.ip_address,
                is_active=session.is_active and not session.is_revoked,
                created_at=session.created_at,
                expires_at=session.expires_at,
                last_activity=session.last_activity,
                is_current_session=(session.id == current_session_id) if current_session_id else False,
            )
            for session in sessions
        ]

        # Calculate password age
        password_age_days = None
        if portal_user.password_changed_at:
            password_age_days = (datetime.utcnow() - portal_user.password_changed_at).days

        # Get active sessions count
        active_count = sum(1 for s in recent_sessions if s.is_active)

        return SecuritySettingsResponse(
            mfa_enabled=portal_user.mfa_enabled,
            has_security_questions=bool(portal_user.security_question_1),
            security_question_1=portal_user.security_question_1,
            security_question_2=portal_user.security_question_2,
            last_password_change=portal_user.password_changed_at,
            password_age_days=password_age_days,
            failed_login_attempts=portal_user.failed_login_attempts,
            is_locked=bool(portal_user.locked_until and portal_user.locked_until > datetime.utcnow()),
            locked_until=portal_user.locked_until,
            active_sessions=active_count,
            recent_sessions=recent_sessions,
            last_login=portal_user.last_login,
            created_at=portal_user.created_at,
        )

    async def verify_email(
        self,
        portal_user: PatientPortalUser,
        token: str
    ) -> str:
        """Verify email address with token

        Args:
            portal_user: The authenticated portal user
            token: Email verification token

        Returns:
            Success message

        Raises:
            ValueError: If token is invalid or expired
        """
        from app.core.security import hash_token

        token_hash = hash_token(token)

        # Find valid verification token
        result = await self.db.execute(
            select(PatientPortalVerification).where(
                and_(
                    PatientPortalVerification.portal_user_id == portal_user.id,
                    PatientPortalVerification.verification_type == VerificationType.EMAIL,
                    PatientPortalVerification.verification_token == token_hash,
                    PatientPortalVerification.status == VerificationStatus.PENDING,
                    PatientPortalVerification.expires_at > datetime.utcnow()
                )
            )
        )
        verification = result.scalar_one_or_none()

        if not verification:
            raise ValueError("Invalid or expired verification token")

        # Mark as verified
        verification.status = VerificationStatus.VERIFIED
        verification.verified_at = datetime.utcnow()

        # Update user
        portal_user.is_email_verified = True
        portal_user.is_active = True  # Activate account if not already active
        portal_user.updated_at = datetime.utcnow()

        await self.db.commit()

        return "Email verified successfully"

    async def verify_phone(
        self,
        portal_user: PatientPortalUser,
        code: str
    ) -> str:
        """Verify phone number with SMS code

        Args:
            portal_user: The authenticated portal user
            code: 6-digit SMS verification code

        Returns:
            Success message

        Raises:
            ValueError: If code is invalid or expired
        """
        # Find valid verification code
        result = await self.db.execute(
            select(PatientPortalVerification).where(
                and_(
                    PatientPortalVerification.portal_user_id == portal_user.id,
                    PatientPortalVerification.verification_type == VerificationType.MOBILE,
                    PatientPortalVerification.verification_code == code,
                    PatientPortalVerification.status == VerificationStatus.PENDING,
                    PatientPortalVerification.expires_at > datetime.utcnow()
                )
            )
        )
        verification = result.scalar_one_or_none()

        if not verification:
            raise ValueError("Invalid or expired verification code")

        # Check attempts
        if verification.attempts >= verification.max_attempts:
            verification.status = VerificationStatus.FAILED
            await self.db.commit()
            raise ValueError("Maximum verification attempts exceeded")

        # Increment attempts
        verification.attempts += 1

        # Mark as verified
        verification.status = VerificationStatus.VERIFIED
        verification.verified_at = datetime.utcnow()

        # Update user
        portal_user.is_phone_verified = True
        portal_user.is_active = True  # Activate account if not already active
        portal_user.updated_at = datetime.utcnow()

        await self.db.commit()

        return "Phone number verified successfully"

    async def send_verification(
        self,
        portal_user: PatientPortalUser,
        verification_type: Literal["email", "phone"]
    ) -> VerificationSendResponse:
        """Send verification code for email or phone

        Args:
            portal_user: The authenticated portal user
            verification_type: Type of verification to send ("email" or "phone")

        Returns:
            Verification send response

        Raises:
            ValueError: If verification type is invalid
        """
        # Generate code/token
        code = ''.join(secrets.choice('0123456789') for _ in range(6))
        token = secrets.token_urlsafe(32)

        expires_at = datetime.utcnow() + timedelta(hours=1)

        # Create verification record
        from app.core.security import hash_token

        verification = PatientPortalVerification(
            portal_user_id=portal_user.id,
            verification_type=VerificationType.EMAIL if verification_type == "email" else VerificationType.MOBILE,
            verification_code=code if verification_type == "phone" else None,
            verification_token=hash_token(token) if verification_type == "email" else None,
            email_address=portal_user.email if verification_type == "email" else None,
            phone_number=portal_user.phone if verification_type == "phone" else None,
            status=VerificationStatus.PENDING,
            expires_at=expires_at,
        )
        self.db.add(verification)
        await self.db.commit()

        # Send verification
        if verification_type == "email":
            email_service = PatientPortalEmailService()
            # Use the existing send_verification_email method with a code
            # Note: The token is stored in verification_token for later verification
            await email_service.send_verification_email(
                to_email=portal_user.email,
                patient_name=portal_user.patient.full_name if portal_user.patient else "Patient",
                verification_code=token,  # Using token as code for email verification
                expires_in_minutes=60,
            )
            return VerificationSendResponse(
                message="Verification email sent",
                expires_at=expires_at,
                sent_to=portal_user.email,
            )
        else:  # phone
            if not portal_user.phone:
                raise ValueError("No phone number associated with account")

            sms_service = PatientPortalSMSService()
            await sms_service.send_phone_verification(
                phone_number=portal_user.phone,
                verification_code=code,
            )
            return VerificationSendResponse(
                message="Verification SMS sent",
                expires_at=expires_at,
                sent_to=portal_user.phone,
            )

    async def request_account_deletion(
        self,
        portal_user: PatientPortalUser,
        deletion_request: DeleteAccountRequest
    ) -> DeleteAccountResponse:
        """Request account deletion (soft delete)

        Args:
            portal_user: The authenticated portal user
            deletion_request: Account deletion request data

        Returns:
            Account deletion response

        Raises:
            ValueError: If password is invalid or confirmation is missing
        """
        # Verify password
        if not verify_password(deletion_request.password, portal_user.hashed_password):
            raise ValueError("Current password is incorrect")

        # Perform soft delete
        portal_user.is_active = False
        portal_user.deactivated_at = datetime.utcnow()
        portal_user.deactivated_reason = deletion_request.reason or "User requested deletion"

        # Revoke all sessions
        result = await self.db.execute(
            select(PatientPortalSession).where(
                and_(
                    PatientPortalSession.portal_user_id == portal_user.id,
                    PatientPortalSession.is_active == True
                )
            )
        )
        sessions = result.scalars().all()
        for session in sessions:
            session.is_revoked = True
            session.is_active = False
            session.revoked_at = datetime.utcnow()

        await self.db.commit()

        # Schedule permanent deletion (30 days)
        scheduled_deletion_date = datetime.utcnow() + timedelta(days=30)

        return DeleteAccountResponse(
            success=True,
            message="Account deactivated successfully. Your data will be permanently deleted in 30 days. Contact support if you wish to restore your account.",
            scheduled_deletion_date=scheduled_deletion_date,
            can_cancel=True,
        )

    async def revoke_session(
        self,
        portal_user: PatientPortalUser,
        session_id: int
    ) -> bool:
        """Revoke a specific session

        Args:
            portal_user: The authenticated portal user
            session_id: Session ID to revoke

        Returns:
            True if session was revoked

        Raises:
            ValueError: If session not found or already revoked
        """
        result = await self.db.execute(
            select(PatientPortalSession).where(
                and_(
                    PatientPortalSession.id == session_id,
                    PatientPortalSession.portal_user_id == portal_user.id
                )
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise ValueError("Session not found")

        if session.is_revoked:
            raise ValueError("Session already revoked")

        session.is_revoked = True
        session.is_active = False
        session.revoked_at = datetime.utcnow()

        await self.db.commit()

        return True

    async def revoke_all_sessions(
        self,
        portal_user: PatientPortalUser,
        except_session_id: Optional[int] = None
    ) -> int:
        """Revoke all sessions except optionally the current one

        Args:
            portal_user: The authenticated portal user
            except_session_id: Session ID to exclude from revocation

        Returns:
            Number of sessions revoked
        """
        result = await self.db.execute(
            select(PatientPortalSession).where(
                and_(
                    PatientPortalSession.portal_user_id == portal_user.id,
                    PatientPortalSession.is_active == True,
                    PatientPortalSession.is_revoked == False
                )
            )
        )
        sessions = result.scalars().all()

        revoked_count = 0
        for session in sessions:
            if except_session_id and session.id == except_session_id:
                continue
            session.is_revoked = True
            session.is_active = False
            session.revoked_at = datetime.utcnow()
            revoked_count += 1

        await self.db.commit()

        return revoked_count
