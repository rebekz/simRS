"""Patient Portal Authentication Endpoints

API endpoints for patient portal login, token management, and password reset.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from typing import Optional

from app.db.session import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
    get_password_hash,
)
from app.models.patient import Patient
from app.models.patient_portal import (
    PatientPortalUser,
    PatientPortalSession,
    PatientPortalPasswordReset,
)
from app.services.patient_portal import (
    generate_verification_token,
    PatientPortalEmailService,
)
from app.schemas.patient_portal.auth import (
    PatientPortalLogin,
    PatientPortalToken,
    PatientPortalPasswordChange,
    PatientPortalPasswordResetRequest,
    PatientPortalPasswordResetConfirm,
    SecurityQuestionsSetup,
    MFASetupResponse,
    MFAVerifyRequest,
    MFAVerifyResponse,
    RefreshTokenRequest,
)
from app.schemas.patient_portal.profile import PatientPortalProfile

router = APIRouter()
security = HTTPBearer()

# Constants
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30


async def get_current_portal_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> PatientPortalUser:
    """Get current authenticated patient portal user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_type = payload.get("type")
    if token_type != "portal_access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    portal_user_id = payload.get("sub")
    if not portal_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    result = await db.execute(
        select(PatientPortalUser).where(PatientPortalUser.id == int(portal_user_id))
    )
    portal_user = result.scalar_one_or_none()

    if not portal_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not portal_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Check if token is revoked
    token_hash = hash_token(token)
    result = await db.execute(
        select(PatientPortalSession).where(
            PatientPortalSession.portal_user_id == portal_user.id,
            PatientPortalSession.token_hash == token_hash,
            PatientPortalSession.is_revoked == True
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    return portal_user


@router.post("/auth/login", response_model=PatientPortalToken)
async def login(
    request: Request,
    login_data: PatientPortalLogin,
    db: AsyncSession = Depends(get_db),
):
    """Patient portal login

    Authenticates user and returns JWT tokens.
    """
    # Get portal user
    result = await db.execute(
        select(PatientPortalUser).where(PatientPortalUser.email == login_data.email)
    )
    portal_user = result.scalar_one_or_none()

    if not portal_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check if account is locked
    if portal_user.locked_until and portal_user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account is locked. Try again after {portal_user.locked_until.strftime('%Y-%m-%d %H:%M:%S')}",
        )

    # Verify password
    if not verify_password(login_data.password, portal_user.hashed_password):
        portal_user.failed_login_attempts += 1

        # Lock account after max attempts
        if portal_user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
            portal_user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            await db.commit()

            # Send locked account email
            email_service = PatientPortalEmailService()
            await email_service.send_account_locked_email(
                to_email=portal_user.email,
                patient_name=portal_user.patient.full_name if portal_user.patient else "Patient",
                locked_until=portal_user.locked_until,
            )

            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked due to too many failed attempts. Try again in {LOCKOUT_DURATION_MINUTES} minutes.",
            )
        else:
            await db.commit()
            remaining = MAX_LOGIN_ATTEMPTS - portal_user.failed_login_attempts
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid email or password. {remaining} attempts remaining.",
            )

    # Check if MFA is enabled
    if portal_user.mfa_enabled:
        # Return temp token indicating MFA required
        temp_token = create_access_token(
            portal_user.id,
            claims={"type": "portal_mfa_pending", "mfa_required": True}
        )

        return PatientPortalToken(
            access_token=temp_token,
            token_type="bearer",
            expires_in_minutes=15,  # Short expiry for MFA pending
            portal_user=None,  # Don't return user until MFA verified
            requires_verification=True,
            pending_verification_step="mfa",
        )

    # Reset failed attempts on successful login
    portal_user.failed_login_attempts = 0
    portal_user.locked_until = None
    portal_user.last_login = datetime.utcnow()

    # Create tokens
    token_expiry = timedelta(days=7) if login_data.remember_me else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        portal_user.id,
        claims={
            "type": "portal_access",
            "remember_me": login_data.remember_me,
        }
    )
    refresh_token = create_refresh_token(portal_user.id)

    # Create session
    session = PatientPortalSession(
        portal_user_id=portal_user.id,
        token_hash=hash_token(access_token),
        device_type=_detect_device_type(request.headers.get("user-agent", "")),
        browser=_extract_browser(request.headers.get("user-agent", "")),
        os=_extract_os(request.headers.get("user-agent", "")),
        ip_address=request.client.host if request.client else None,
        expires_at=datetime.utcnow() + token_expiry,
    )
    db.add(session)

    await db.commit()

    # Build profile
    profile = _build_profile(portal_user)

    return PatientPortalToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in_minutes=(7 * 24 * 60) if login_data.remember_me else ACCESS_TOKEN_EXPIRE_MINUTES,
        portal_user=profile,
    )


@router.post("/auth/verify-mfa", response_model=PatientPortalToken)
async def verify_mfa(
    mfa_data: MFAVerifyRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Verify MFA code during login

    Completes login process when MFA is enabled.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "portal_mfa_pending":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA session",
        )

    portal_user_id = payload.get("sub")
    result = await db.execute(
        select(PatientPortalUser).where(PatientPortalUser.id == int(portal_user_id))
    )
    portal_user = result.scalar_one_or_none()

    if not portal_user or not portal_user.mfa_enabled or not portal_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not enabled for this account",
        )

    # Verify TOTP code
    from app.core.security import verify_mfa_code
    if not verify_mfa_code(portal_user.mfa_secret, mfa_data.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code",
        )

    # MFA verified, issue real tokens
    access_token = create_access_token(
        portal_user.id,
        claims={"type": "portal_access"}
    )
    refresh_token = create_refresh_token(portal_user.id)

    # Create session
    session = PatientPortalSession(
        portal_user_id=portal_user.id,
        token_hash=hash_token(access_token),
        expires_at=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    db.add(session)

    portal_user.last_login = datetime.utcnow()
    await db.commit()

    profile = _build_profile(portal_user)

    return PatientPortalToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        portal_user=profile,
    )


@router.post("/auth/refresh", response_model=PatientPortalToken)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token

    Issues a new access token using a valid refresh token.
    """
    payload = decode_token(refresh_data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    portal_user_id = payload.get("sub")
    result = await db.execute(
        select(PatientPortalUser).where(PatientPortalUser.id == int(portal_user_id))
    )
    portal_user = result.scalar_one_or_none()

    if not portal_user or not portal_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Create new access token
    access_token = create_access_token(
        portal_user.id,
        claims={"type": "portal_access"}
    )

    profile = _build_profile(portal_user)

    return PatientPortalToken(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        portal_user=profile,
    )


@router.post("/auth/logout")
async def logout(
    request: Request,
    revoke_all: bool = False,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Logout from patient portal

    Revokes the current session or all sessions.
    """
    if revoke_all:
        # Revoke all sessions for this user
        result = await db.execute(
            select(PatientPortalSession).where(
                and_(
                    PatientPortalSession.portal_user_id == current_user.id,
                    PatientPortalSession.is_active == True,
                )
            )
        )
        sessions = result.scalars().all()
        for session in sessions:
            session.is_revoked = True
            session.is_active = False
            session.revoked_at = datetime.utcnow()
    else:
        # Revoke only current session
        token = request.headers.get("authorization", "").replace("Bearer ", "")
        token_hash = hash_token(token)
        result = await db.execute(
            select(PatientPortalSession).where(
                and_(
                    PatientPortalSession.portal_user_id == current_user.id,
                    PatientPortalSession.token_hash == token_hash,
                )
            )
        )
        session = result.scalar_one_or_none()
        if session:
            session.is_revoked = True
            session.is_active = False
            session.revoked_at = datetime.utcnow()

    await db.commit()

    return {"message": "Logged out successfully"}


@router.get("/auth/me", response_model=PatientPortalProfile)
async def get_current_profile(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
):
    """Get current user profile

    Returns the profile of the authenticated user.
    """
    return _build_profile(current_user)


@router.post("/auth/request-password-reset")
async def request_password_reset(
    request_data: PatientPortalPasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request password reset

    Sends a password reset link to the user's email.
    """
    result = await db.execute(
        select(PatientPortalUser).where(PatientPortalUser.email == request_data.email)
    )
    portal_user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    if not portal_user:
        return {"message": "If an account exists with this email, a password reset link has been sent."}

    # Check if there's a recent unused token
    recent_time = datetime.utcnow() - timedelta(hours=1)
    result = await db.execute(
        select(PatientPortalPasswordReset).where(
            and_(
                PatientPortalPasswordReset.portal_user_id == portal_user.id,
                PatientPortalPasswordReset.is_used == False,
                PatientPortalPasswordReset.created_at > recent_time,
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        return {"message": "If an account exists with this email, a password reset link has been sent."}

    # Create reset token
    reset_token = generate_verification_token()

    reset = PatientPortalPasswordReset(
        portal_user_id=portal_user.id,
        token_hash=hash_token(reset_token),
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    db.add(reset)
    await db.commit()

    # Send email
    email_service = PatientPortalEmailService()
    await email_service.send_password_reset_email(
        to_email=portal_user.email,
        patient_name=portal_user.patient.full_name if portal_user.patient else "Patient",
        reset_token=reset_token,
    )

    return {"message": "If an account exists with this email, a password reset link has been sent."}


@router.post("/auth/reset-password")
async def reset_password(
    reset_data: PatientPortalPasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    """Reset password with token

    Completes password reset using the token from email.
    """
    # Find valid reset token
    token_hash = hash_token(reset_data.token)
    result = await db.execute(
        select(PatientPortalPasswordReset).where(
            and_(
                PatientPortalPasswordReset.token_hash == token_hash,
                PatientPortalPasswordReset.is_used == False,
                PatientPortalPasswordReset.expires_at > datetime.utcnow(),
            )
        )
    )
    reset = result.scalar_one_or_none()

    if not reset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Get portal user
    result = await db.execute(
        select(PatientPortalUser).where(PatientPortalUser.id == reset.portal_user_id)
    )
    portal_user = result.scalar_one_or_none()

    if not portal_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update password
    portal_user.hashed_password = get_password_hash(reset_data.new_password)
    portal_user.password_changed_at = datetime.utcnow()
    portal_user.failed_login_attempts = 0
    portal_user.locked_until = None

    # Mark token as used
    reset.is_used = True
    reset.used_at = datetime.utcnow()

    await db.commit()

    # Send confirmation email
    email_service = PatientPortalEmailService()
    await email_service.send_password_changed_email(
        to_email=portal_user.email,
        patient_name=portal_user.patient.full_name if portal_user.patient else "Patient",
        changed_at=datetime.utcnow(),
    )

    return {"message": "Password reset successfully. You can now log in with your new password."}


@router.post("/auth/change-password")
async def change_password(
    password_data: PatientPortalPasswordChange,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Change password (authenticated)

    Changes password for authenticated user.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.password_changed_at = datetime.utcnow()

    await db.commit()

    # Send confirmation email
    email_service = PatientPortalEmailService()
    await email_service.send_password_changed_email(
        to_email=current_user.email,
        patient_name=current_user.patient.full_name if current_user.patient else "Patient",
        changed_at=datetime.utcnow(),
    )

    return {"message": "Password changed successfully"}


# Helper functions
def _build_profile(portal_user: PatientPortalUser) -> PatientPortalProfile:
    """Build profile from portal user"""
    return PatientPortalProfile(
        id=portal_user.id,
        email=portal_user.email,
        phone=portal_user.phone,
        patient_id=portal_user.patient_id,
        is_active=portal_user.is_active,
        is_email_verified=portal_user.is_email_verified,
        is_phone_verified=portal_user.is_phone_verified,
        is_identity_verified=portal_user.is_identity_verified,
        patient_name=portal_user.patient.full_name if portal_user.patient else None,
        medical_record_number=portal_user.patient.medical_record_number if portal_user.patient else None,
        date_of_birth=portal_user.patient.date_of_birth if portal_user.patient else None,
        mfa_enabled=portal_user.mfa_enabled,
        has_security_questions=bool(portal_user.security_question_1),
        last_login=portal_user.last_login,
        created_at=portal_user.created_at,
    )


def _detect_device_type(user_agent: str) -> Optional[str]:
    """Detect device type from user agent"""
    user_agent_lower = user_agent.lower()
    if "mobile" in user_agent_lower or "android" in user_agent_lower or "iphone" in user_agent_lower:
        return "mobile"
    elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
        return "tablet"
    else:
        return "desktop"


def _extract_browser(user_agent: str) -> Optional[str]:
    """Extract browser name from user agent"""
    user_agent_lower = user_agent.lower()
    if "chrome" in user_agent_lower:
        return "Chrome"
    elif "safari" in user_agent_lower:
        return "Safari"
    elif "firefox" in user_agent_lower:
        return "Firefox"
    elif "edge" in user_agent_lower:
        return "Edge"
    else:
        return "Unknown"


def _extract_os(user_agent: str) -> Optional[str]:
    """Extract OS from user agent"""
    user_agent_lower = user_agent.lower()
    if "windows" in user_agent_lower:
        return "Windows"
    elif "mac" in user_agent_lower and "iphone" not in user_agent_lower:
        return "macOS"
    elif "linux" in user_agent_lower:
        return "Linux"
    elif "android" in user_agent_lower:
        return "Android"
    elif "iphone" in user_agent_lower or "ipad" in user_agent_lower:
        return "iOS"
    else:
        return "Unknown"
