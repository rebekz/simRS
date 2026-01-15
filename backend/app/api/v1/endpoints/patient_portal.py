"""Patient Portal Registration and Authentication Endpoints

API endpoints for patient portal registration, verification, and authentication.
STORY-041: Patient Registration & Account Creation
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta
from typing import Optional

from app.db.session import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)
from app.models.patient import Patient
from app.models.patient_portal import (
    PatientPortalUser,
    PatientPortalVerification,
    PatientPortalSession,
    VerificationType,
    VerificationStatus,
)
from app.schemas.patient_portal import (
    PatientRegistrationCreate,
    PatientRegistrationResponse,
    RegistrationStep,
    EmailVerificationRequest,
    EmailVerificationResponse,
    PhoneVerificationRequest,
    PhoneVerificationVerifyRequest,
    PhoneVerificationResponse,
    RegistrationCheckRequest,
    RegistrationCheckResponse,
    AccountActivationRequest,
    AccountActivationResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    PatientPortalLogin,
    PatientPortalToken,
    PatientPortalProfile,
)
from app.services.patient_portal import (
    VerificationService,
    generate_verification_token,
    PatientPortalEmailService,
    PatientPortalSMSService,
)

router = APIRouter()
security = HTTPBearer()

# Constants
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


@router.post("/register/check", response_model=RegistrationCheckResponse)
async def check_registration_eligibility(
    request: RegistrationCheckRequest,
    db: AsyncSession = Depends(get_db),
):
    """Check if email/phone/NIK is available for registration

    Returns availability status for each field provided.
    """
    email_available = True
    phone_available = True
    nik_exists = False
    patient_exists = False

    if request.email:
        result = await db.execute(
            select(PatientPortalUser).where(PatientPortalUser.email == request.email)
        )
        if result.scalar_one_or_none():
            email_available = False

    if request.phone:
        normalized_phone = request.phone.replace(" ", "").replace("-", "")
        result = await db.execute(
            select(PatientPortalUser).where(PatientPortalUser.phone == normalized_phone)
        )
        if result.scalar_one_or_none():
            phone_available = False

    if request.nik:
        result = await db.execute(
            select(Patient).where(Patient.nik == request.nik)
        )
        patient = result.scalar_one_or_none()
        if patient:
            nik_exists = True
            patient_exists = True

    can_register = email_available and phone_available

    return RegistrationCheckResponse(
        email_available=email_available if request.email else None,
        phone_available=phone_available if request.phone else None,
        nik_exists=nik_exists if request.nik else None,
        patient_exists=patient_exists if request.nik else None,
        can_register=can_register,
        message="Registration check completed" if can_register else "Some fields are not available",
    )


@router.post("/register", response_model=PatientRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_patient_portal(
    request: Request,
    registration: PatientRegistrationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new patient portal account

    Creates a portal account and initiates email verification.
    """
    # Check for existing email
    result = await db.execute(
        select(PatientPortalUser).where(PatientPortalUser.email == registration.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password
    hashed_password = get_password_hash(registration.password)

    # Create portal user (not yet active)
    portal_user = PatientPortalUser(
        email=registration.email,
        phone=registration.phone,
        hashed_password=hashed_password,
        is_active=False,
        is_email_verified=False,
        is_phone_verified=False,
        is_identity_verified=False,
        accepted_terms_at=datetime.utcnow() if registration.accept_terms else None,
        accepted_privacy_at=datetime.utcnow() if registration.accept_privacy else None,
        registration_ip=request.client.host if request.client else None,
        registration_user_agent=request.headers.get("user-agent"),
    )

    # Add security questions if provided
    if registration.security_question_1 and registration.security_answer_1:
        portal_user.security_question_1 = registration.security_question_1
        portal_user.security_answer_1_hash = get_password_hash(registration.security_answer_1)
    if registration.security_question_2 and registration.security_answer_2:
        portal_user.security_question_2 = registration.security_question_2
        portal_user.security_answer_2_hash = get_password_hash(registration.security_answer_2)

    # Try to link to existing patient record
    patient_id = None
    if registration.nik:
        result = await db.execute(
            select(Patient).where(Patient.nik == registration.nik)
        )
        patient = result.scalar_one_or_none()
        if patient:
            portal_user.patient_id = patient.id
            patient_id = patient.id

    db.add(portal_user)
    await db.flush()

    # Create email verification
    verification_service = VerificationService(db)
    email_verification = await verification_service.create_email_verification(
        portal_user_id=portal_user.id,
        email_address=registration.email,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # Send verification email
    email_service = PatientPortalEmailService()
    patient_name = "Patient"  # Will be updated once patient is linked
    await email_service.send_verification_email(
        to_email=registration.email,
        patient_name=patient_name,
        verification_code=email_verification.verification_code,
    )

    await db.commit()

    return PatientRegistrationResponse(
        portal_user_id=portal_user.id,
        email=portal_user.email,
        is_email_verified=False,
        is_phone_verified=False,
        is_identity_verified=False,
        current_step=RegistrationStep.EMAIL_VERIFY,
        message="Registration successful. Please check your email for verification code.",
        created_at=portal_user.created_at,
    )


@router.post("/register/verify-email", response_model=EmailVerificationResponse)
async def verify_email(
    request: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verify email with verification code

    Verifies the email address using the 6-digit code sent via email.
    """
    # Get portal user by email
    result = await db.execute(
        select(PatientPortalUser).where(PatientPortalUser.email == request.email)
    )
    portal_user = result.scalar_one_or_none()

    if not portal_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portal user not found",
        )

    # Verify code
    verification_service = VerificationService(db)
    success, message, verification = await verification_service.verify_code(
        portal_user_id=portal_user.id,
        verification_type=VerificationType.EMAIL,
        code=request.verification_code,
    )

    if success:
        portal_user.is_email_verified = True
        await db.commit()

        # Determine next step
        next_step = RegistrationStep.PHONE_VERIFY
        if not portal_user.patient_id:
            next_step = RegistrationStep.PATIENT_LINK

        return EmailVerificationResponse(
            success=True,
            message="Email verified successfully!",
            is_verified=True,
            next_step=next_step,
        )
    else:
        return EmailVerificationResponse(
            success=False,
            message=message,
            is_verified=False,
        )


@router.post("/register/send-phone-verification", response_model=PhoneVerificationResponse)
async def send_phone_verification(
    request: PhoneVerificationRequest,
    current_user: PatientPortalUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Initiate phone verification by sending SMS code

    Sends a 6-digit verification code to the provided phone number.
    """
    # For now, require portal_user_id to be provided
    # In production, this would be authenticated
    portal_user_id = None  # Would come from auth token

    # Find user by phone
    result = await db.execute(
        select(PatientPortalUser).where(PatientPortalUser.phone == request.phone)
    )
    portal_user = result.scalar_one_or_none()

    if not portal_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check rate limiting
    verification_service = VerificationService(db)
    can_request, error_msg = await verification_service.can_request_new_verification(
        portal_user_id=portal_user.id,
        verification_type=VerificationType.MOBILE,
        cooldown_seconds=60,
    )

    if not can_request:
        return PhoneVerificationResponse(
            success=False,
            message=error_msg,
            is_verified=False,
        )

    # Create phone verification
    phone_verification = await verification_service.create_phone_verification(
        portal_user_id=portal_user.id,
        phone_number=request.phone,
    )

    # Send SMS
    sms_service = PatientPortalSMSService()
    await sms_service.send_verification_sms(
        phone_number=request.phone,
        patient_name=portal_user.patient.full_name if portal_user.patient else "Patient",
        verification_code=phone_verification.verification_code,
    )

    await db.commit()

    return PhoneVerificationResponse(
        success=True,
        message="Verification code sent to your phone",
        is_verified=False,
    )


@router.post("/register/verify-phone", response_model=PhoneVerificationResponse)
async def verify_phone(
    request: PhoneVerificationVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verify phone number with SMS code

    Verifies the phone number using the 6-digit code sent via SMS.
    """
    # Get portal user by phone
    result = await db.execute(
        select(PatientPortalUser).where(PatientPortalUser.phone == request.phone)
    )
    portal_user = result.scalar_one_or_none()

    if not portal_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Verify code
    verification_service = VerificationService(db)
    success, message, verification = await verification_service.verify_code(
        portal_user_id=portal_user.id,
        verification_type=VerificationType.MOBILE,
        code=request.verification_code,
    )

    if success:
        portal_user.is_phone_verified = True
        await db.commit()

        return PhoneVerificationResponse(
            success=True,
            message="Phone verified successfully!",
            is_verified=True,
            next_step=RegistrationStep.IDENTITY_VERIFY,
        )
    else:
        return PhoneVerificationResponse(
            success=False,
            message=message,
            is_verified=False,
        )


@router.post("/register/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification(
    request: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Resend verification code (email or SMS)

    Resends the verification code to the user's email or phone.
    """
    # Get portal user
    result = await db.execute(
        select(PatientPortalUser).where(PatientPortalUser.email == request.email)
    )
    portal_user = result.scalar_one_or_none()

    if not portal_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    verification_service = VerificationService(db)

    if request.verification_type == "email":
        # Check rate limiting
        can_request, error_msg = await verification_service.can_request_new_verification(
            portal_user_id=portal_user.id,
            verification_type=VerificationType.EMAIL,
            cooldown_seconds=60,
        )

        if not can_request:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_msg,
            )

        # Create new verification
        verification = await verification_service.create_email_verification(
            portal_user_id=portal_user.id,
            email_address=portal_user.email,
        )

        # Send email
        email_service = PatientPortalEmailService()
        await email_service.send_verification_email(
            to_email=portal_user.email,
            patient_name=portal_user.patient.full_name if portal_user.patient else "Patient",
            verification_code=verification.verification_code,
        )

        await db.commit()

        return ResendVerificationResponse(
            success=True,
            message="Verification code sent to your email",
            expires_in_minutes=15,
        )

    else:  # SMS
        if not portal_user.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No phone number associated with account",
            )

        # Check rate limiting
        can_request, error_msg = await verification_service.can_request_new_verification(
            portal_user_id=portal_user.id,
            verification_type=VerificationType.MOBILE,
            cooldown_seconds=60,
        )

        if not can_request:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_msg,
            )

        # Create new verification
        verification = await verification_service.create_phone_verification(
            portal_user_id=portal_user.id,
            phone_number=portal_user.phone,
        )

        # Send SMS
        sms_service = PatientPortalSMSService()
        await sms_service.send_verification_sms(
            phone_number=portal_user.phone,
            patient_name=portal_user.patient.full_name if portal_user.patient else "Patient",
            verification_code=verification.verification_code,
        )

        await db.commit()

        return ResendVerificationResponse(
            success=True,
            message="Verification code sent to your phone",
            expires_in_minutes=10,
        )


@router.post("/register/activate", response_model=AccountActivationResponse)
async def activate_account(
    request: AccountActivationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Activate account after all verifications complete

    Finalizes the registration and activates the portal account.
    """
    # Get portal user
    result = await db.execute(
        select(PatientPortalUser).where(PatientPortalUser.id == request.portal_user_id)
    )
    portal_user = result.scalar_one_or_none()

    if not portal_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portal user not found",
        )

    # Check all verifications
    if not portal_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification required",
        )

    # Phone verification is optional
    # Identity verification is optional for MVP

    # Activate account
    portal_user.is_active = True
    await db.commit()

    # Send welcome email
    email_service = PatientPortalEmailService()
    portal_url = "https://portal.simrs.hospital.id"
    await email_service.send_welcome_email(
        to_email=portal_user.email,
        patient_name=portal_user.patient.full_name if portal_user.patient else "Patient",
        portal_url=portal_url,
    )

    return AccountActivationResponse(
        success=True,
        message="Account activated successfully! You can now log in to the patient portal.",
        is_active=True,
        activation_date=datetime.utcnow(),
    )
