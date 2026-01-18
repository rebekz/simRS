from __future__ import annotations

"""Patient Portal Authentication Schemas

Pydantic schemas for patient portal authentication, login, and password management.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, Literal

# Forward reference - imported here for Pydantic validation
from app.schemas.patient_portal.profile import PatientPortalProfile  # noqa: E402


class PatientPortalLogin(BaseModel):
    """Schema for patient portal login"""
    email: EmailStr = Field(..., description="Portal account email")
    password: str = Field(..., min_length=1, description="Account password")
    remember_me: bool = Field(default=False, description="Extend session duration")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "patient@example.com",
            "password": "SecurePass123!",
            "remember_me": False
        }
    })


class PatientPortalToken(BaseModel):
    """Schema for patient portal token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration in seconds")
    portal_user: PatientPortalProfile
    requires_verification: Optional[bool] = False
    pending_verification_step: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PatientPortalPasswordChange(BaseModel):
    """Schema for password change (authenticated user)"""
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(
        ...,
        min_length=12,
        max_length=100,
        description="New password (min 12 characters with complexity requirements)"
    )

    @field_validator('new_password')
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


class PatientPortalPasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr = Field(..., description="Email associated with portal account")

    model_config = ConfigDict(json_schema_extra={
        "example": {"email": "patient@example.com"}
    })


class PatientPortalPasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str = Field(..., description="Password reset token from email")
    new_password: str = Field(
        ...,
        min_length=12,
        max_length=100,
        description="New password"
    )

    @field_validator('new_password')
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


class SecurityQuestionsSetup(BaseModel):
    """Schema for setting up security questions"""
    security_question_1: str = Field(..., min_length=10, max_length=255, description="First security question")
    security_answer_1: str = Field(..., min_length=3, max_length=100, description="Answer to first question")
    security_question_2: str = Field(..., min_length=10, max_length=255, description="Second security question")
    security_answer_2: str = Field(..., min_length=3, max_length=100, description="Answer to second question")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "security_question_1": "What was the name of your first pet?",
            "security_answer_1": "Fluffy",
            "security_question_2": "In what city were you born?",
            "security_answer_2": "Jakarta"
        }
    })


class SecurityQuestionsVerify(BaseModel):
    """Schema for verifying security answers"""
    answer_1: str = Field(..., description="Answer to security question 1")
    answer_2: str = Field(..., description="Answer to security question 2")


class MFADisabledResponse(BaseModel):
    """Schema for MFA disabled response"""
    mfa_enabled: bool
    message: str


class MFASetupResponse(BaseModel):
    """Schema for MFA setup response"""
    mfa_enabled: bool
    secret: Optional[str] = None
    qr_code_url: Optional[str] = None
    backup_codes: Optional[list[str]] = None
    message: str


class MFAVerifyRequest(BaseModel):
    """Schema for MFA verification during login"""
    code: str = Field(..., min_length=6, max_length=6, pattern=r'^[0-9]{6}$', description="6-digit TOTP code")


class MFAVerifyResponse(BaseModel):
    """Schema for MFA verification response"""
    success: bool
    message: str


class MFAToggleRequest(BaseModel):
    """Schema for enabling/disabling MFA"""
    enable: bool = Field(..., description="True to enable MFA, False to disable")
    verification_code: Optional[str] = Field(None, min_length=6, max_length=6, description="Current TOTP code for disabling MFA")


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh"""
    refresh_token: str = Field(..., description="Refresh token")


class LogoutRequest(BaseModel):
    """Schema for logout"""
    revoke_all_sessions: bool = Field(default=False, description="Revoke all active sessions")


