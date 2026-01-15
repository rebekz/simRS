"""Patient Portal Verification Service

Service for managing email and SMS verification codes and tokens.
"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.patient_portal import (
    PatientPortalUser,
    PatientPortalVerification,
    VerificationType,
    VerificationStatus,
)


def generate_verification_code(length: int = 6) -> str:
    """Generate a numeric verification code"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_verification_token() -> str:
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)


class VerificationService:
    """Service for managing patient portal verifications"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_email_verification(
        self,
        portal_user_id: int,
        email_address: str,
        expires_in_minutes: int = 15,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> PatientPortalVerification:
        """Create an email verification record"""
        code = generate_verification_code()

        verification = PatientPortalVerification(
            portal_user_id=portal_user_id,
            verification_type=VerificationType.EMAIL,
            verification_code=code,
            email_address=email_address,
            status=VerificationStatus.PENDING,
            attempts=0,
            max_attempts=3,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.add(verification)
        await self.db.flush()

        return verification

    async def create_phone_verification(
        self,
        portal_user_id: int,
        phone_number: str,
        expires_in_minutes: int = 10,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> PatientPortalVerification:
        """Create a phone/SMS verification record"""
        code = generate_verification_code()

        verification = PatientPortalVerification(
            portal_user_id=portal_user_id,
            verification_type=VerificationType.MOBILE,
            verification_code=code,
            phone_number=phone_number,
            status=VerificationStatus.PENDING,
            attempts=0,
            max_attempts=3,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.add(verification)
        await self.db.flush()

        return verification

    async def create_identity_verification(
        self,
        portal_user_id: int,
        verification_token: str,
        verification_data: Optional[str] = None,
        expires_in_hours: int = 24,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> PatientPortalVerification:
        """Create an identity verification record"""
        verification = PatientPortalVerification(
            portal_user_id=portal_user_id,
            verification_type=VerificationType.IDENTITY,
            verification_token=verification_token,
            verification_data=verification_data,
            status=VerificationStatus.PENDING,
            attempts=0,
            max_attempts=1,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.add(verification)
        await self.db.flush()

        return verification

    async def verify_code(
        self,
        portal_user_id: int,
        verification_type: VerificationType,
        code: str,
    ) -> Tuple[bool, str, Optional[PatientPortalVerification]]:
        """Verify a code (email or SMS)"""
        now = datetime.utcnow()

        # Get pending verification
        result = await self.db.execute(
            select(PatientPortalVerification).where(
                and_(
                    PatientPortalVerification.portal_user_id == portal_user_id,
                    PatientPortalVerification.verification_type == verification_type,
                    PatientPortalVerification.status == VerificationStatus.PENDING,
                    PatientPortalVerification.expires_at > now,
                )
            ).order_by(PatientPortalVerification.created_at.desc())
        )
        verification = result.scalar_one_or_none()

        if not verification:
            return False, "No valid verification code found. Please request a new code.", None

        if verification.verification_code != code:
            verification.attempts += 1
            if verification.attempts >= verification.max_attempts:
                verification.status = VerificationStatus.FAILED
                await self.db.commit()
                return False, "Too many failed attempts. Please request a new code.", verification
            await self.db.commit()
            return False, f"Invalid code. {verification.max_attempts - verification.attempts} attempts remaining.", verification

        # Mark as verified
        verification.status = VerificationStatus.VERIFIED
        verification.verified_at = now
        await self.db.commit()

        return True, "Verification successful!", verification

    async def verify_token(
        self,
        verification_token: str,
    ) -> Tuple[bool, str, Optional[PatientPortalVerification]]:
        """Verify an identity verification token"""
        now = datetime.utcnow()

        result = await self.db.execute(
            select(PatientPortalVerification).where(
                and_(
                    PatientPortalVerification.verification_token == verification_token,
                    PatientPortalVerification.verification_type == VerificationType.IDENTITY,
                    PatientPortalVerification.status == VerificationStatus.PENDING,
                    PatientPortalVerification.expires_at > now,
                )
            )
        )
        verification = result.scalar_one_or_none()

        if not verification:
            return False, "Invalid or expired verification link.", None

        verification.status = VerificationStatus.VERIFIED
        verification.verified_at = now
        await self.db.commit()

        return True, "Identity verification successful!", verification

    async def get_latest_verification(
        self,
        portal_user_id: int,
        verification_type: VerificationType,
    ) -> Optional[PatientPortalVerification]:
        """Get the latest verification record for a user"""
        result = await self.db.execute(
            select(PatientPortalVerification).where(
                and_(
                    PatientPortalVerification.portal_user_id == portal_user_id,
                    PatientPortalVerification.verification_type == verification_type,
                )
            ).order_by(PatientPortalVerification.created_at.desc())
        )
        return result.scalar_one_or_none()

    async def mark_expired_verifications(self) -> int:
        """Mark expired verifications as expired (cleanup job)"""
        now = datetime.utcnow()

        result = await self.db.execute(
            select(PatientPortalVerification).where(
                and_(
                    PatientPortalVerification.status == VerificationStatus.PENDING,
                    PatientPortalVerification.expires_at < now,
                )
            )
        )
        verifications = result.scalars().all()

        count = 0
        for verification in verifications:
            verification.status = VerificationStatus.EXPIRED
            count += 1

        await self.db.commit()
        return count

    async def can_request_new_verification(
        self,
        portal_user_id: int,
        verification_type: VerificationType,
        cooldown_seconds: int = 60,
    ) -> Tuple[bool, Optional[str]]:
        """Check if user can request a new verification code (rate limiting)"""
        latest = await self.get_latest_verification(portal_user_id, verification_type)

        if not latest:
            return True, None

        if latest.status == VerificationStatus.VERIFIED:
            return False, "Already verified"

        if latest.status == VerificationStatus.PENDING:
            elapsed = (datetime.utcnow() - latest.created_at).total_seconds()
            if elapsed < cooldown_seconds:
                remaining = int(cooldown_seconds - elapsed)
                return False, f"Please wait {remaining} seconds before requesting a new code"

        return True, None

    async def cleanup_old_verifications(self, days: int = 7) -> int:
        """Delete old verification records (cleanup job)"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        # This would typically use a delete query
        # For now, return count
        return 0
