"""Patient Portal Registration Schemas

Pydantic schemas for patient portal registration and verification.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, Literal
from enum import Enum


class RegistrationStep(str, Enum):
    """Steps in the registration process"""
    EMAIL_VERIFY = "email_verify"
    PHONE_VERIFY = "phone_verify"
    PATIENT_LINK = "patient_link"
    IDENTITY_VERIFY = "identity_verify"
    SECURITY_SETUP = "security_setup"
    COMPLETE = "complete"


class PatientRegistrationCreate(BaseModel):
    """Schema for creating a new patient portal registration"""
    email: EmailStr = Field(..., description="Email address for portal account")
    password: str = Field(
        ...,
        min_length=12,
        max_length=100,
        description="Password (min 12 characters, must include uppercase, lowercase, number, special char)"
    )
    phone: str = Field(..., pattern=r'^\+?62[0-9]{9,13}$|^08[0-9]{8,11}$', description="Indonesian mobile number")

    # Terms acceptance
    accept_terms: bool = Field(..., description="Acceptance of terms of service")
    accept_privacy: bool = Field(..., description="Acceptance of privacy policy")

    # Optional patient linking info
    nik: Optional[str] = Field(None, pattern=r'^[0-9]{16}$', description="16-digit NIK (Indonesian National ID)")
    mrn: Optional[str] = Field(None, min_length=1, max_length=20, description="Medical Record Number")
    bpjs_card_number: Optional[str] = Field(None, min_length=13, max_length=20, description="BPJS card number")

    # Security questions (optional during registration)
    security_question_1: Optional[str] = Field(None, max_length=255, description="First security question")
    security_answer_1: Optional[str] = Field(None, min_length=3, max_length=100, description="Answer to first security question")
    security_question_2: Optional[str] = Field(None, max_length=255, description="Second security question")
    security_answer_2: Optional[str] = Field(None, min_length=3, max_length=100, description="Answer to second security question")

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets strength requirements"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?`~' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('accept_terms', 'accept_privacy')
    @classmethod
    def validate_terms_acceptance(cls, v: bool) -> bool:
        """Validate terms are accepted"""
        if not v:
            raise ValueError('You must accept the terms to register')
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "patient@example.com",
            "password": "SecurePass123!",
            "phone": "+6281234567890",
            "nik": "3201010101010001",
            "mrn": "RM20240001",
            "bpjs_card_number": "1234567890123",
            "accept_terms": True,
            "accept_privacy": True,
        }
    })


class PatientRegistrationResponse(BaseModel):
    """Schema for registration response"""
    portal_user_id: int
    email: str
    is_email_verified: bool
    is_phone_verified: bool
    is_identity_verified: bool
    current_step: RegistrationStep
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request"""
    email: EmailStr = Field(..., description="Email to verify")
    verification_code: str = Field(..., min_length=6, max_length=6, pattern=r'^[0-9]{6}$', description="6-digit verification code")

    model_config = ConfigDict(json_schema_extra={
        "example": {"email": "patient@example.com", "verification_code": "123456"}
    })


class EmailVerificationResponse(BaseModel):
    """Schema for email verification response"""
    success: bool
    message: str
    is_verified: bool
    next_step: Optional[RegistrationStep] = None


class PhoneVerificationRequest(BaseModel):
    """Schema for phone verification request (initiate)"""
    phone: str = Field(..., pattern=r'^\+?62[0-9]{9,13}$|^08[0-9]{8,11}$', description="Indonesian mobile number")

    model_config = ConfigDict(json_schema_extra={
        "example": {"phone": "+6281234567890"}
    })


class PhoneVerificationVerifyRequest(BaseModel):
    """Schema for phone verification code submission"""
    phone: str = Field(..., pattern=r'^\+?62[0-9]{9,13}$|^08[0-9]{8,11}$')
    verification_code: str = Field(..., min_length=6, max_length=6, pattern=r'^[0-9]{6}$')


class PhoneVerificationResponse(BaseModel):
    """Schema for phone verification response"""
    success: bool
    message: str
    is_verified: bool
    next_step: Optional[RegistrationStep] = None


class IdentityVerificationRequest(BaseModel):
    """Schema for identity verification request"""
    id_type: Literal["KTP", "PASSPORT", "OTHER"] = Field(..., description="Type of ID document")
    id_number: str = Field(..., description="ID document number")

    # For selfie verification, include base64 or reference to uploaded image
    selfie_image_path: Optional[str] = Field(None, description="Path to uploaded selfie image")
    id_document_path: Optional[str] = Field(None, description="Path to uploaded ID document image")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id_type": "KTP",
            "id_number": "3201010101010001",
            "selfie_image_path": "/uploads/identity/selfie_123.jpg",
            "id_document_path": "/uploads/identity/ktp_123.jpg"
        }
    })


class IdentityVerificationResponse(BaseModel):
    """Schema for identity verification response"""
    success: bool
    message: str
    is_verified: bool
    verification_status: Literal["pending", "verified", "failed", "manual_review_required"]
    next_step: Optional[RegistrationStep] = None


class RegistrationCheckRequest(BaseModel):
    """Schema for checking if email/phone/NIK already registered"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nik: Optional[str] = Field(None, pattern=r'^[0-9]{16}$')

    @field_validator('email', 'phone', 'nik')
    @classmethod
    def validate_at_least_one(cls, v, info):
        """Ensure at least one field is provided"""
        if not v and not any(info.data.get(field) for field in ['email', 'phone', 'nik'] if field != info.field_name):
            raise ValueError('At least one of email, phone, or NIK must be provided')
        return v


class RegistrationCheckResponse(BaseModel):
    """Schema for registration check response"""
    email_available: Optional[bool] = None
    phone_available: Optional[bool] = None
    nik_exists: Optional[bool] = None
    patient_exists: Optional[bool] = None
    can_register: bool
    message: str


class AccountActivationRequest(BaseModel):
    """Schema for final account activation after all verifications complete"""
    portal_user_id: int = Field(..., description="Portal user ID to activate")

    model_config = ConfigDict(json_schema_extra={
        "example": {"portal_user_id": 1}
    })


class AccountActivationResponse(BaseModel):
    """Schema for account activation response"""
    success: bool
    message: str
    is_active: bool
    activation_date: Optional[datetime] = None


class ResendVerificationRequest(BaseModel):
    """Schema for resending verification code"""
    email: EmailStr = Field(..., description="Email to resend verification to")
    verification_type: Literal["email", "phone"] = Field(default="email", description="Type of verification to resend")


class ResendVerificationResponse(BaseModel):
    """Schema for resend verification response"""
    success: bool
    message: str
    expires_in_minutes: int
