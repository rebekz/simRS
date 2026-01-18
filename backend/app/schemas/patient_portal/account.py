"""Patient Portal Account Settings Schemas

Pydantic schemas for patient portal account settings management.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List, Literal


# ============ Profile Settings ============

class ProfileSettings(BaseModel):
    """Schema for profile settings"""
    id: int
    email: str
    phone: Optional[str] = None
    patient_id: int
    patient_name: Optional[str] = None
    medical_record_number: Optional[str] = None

    # Verification status
    is_active: bool
    is_email_verified: bool
    is_phone_verified: bool
    is_identity_verified: bool

    # Account info
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdateRequest(BaseModel):
    """Schema for updating profile information"""
    email: Optional[EmailStr] = Field(None, description="New email address (requires verification)")
    phone: Optional[str] = Field(None, pattern=r'^\+?62[0-9]{9,13}$|^08[0-9]{8,11}$', description="New phone number (requires verification)")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "newemail@example.com",
            "phone": "081234567890"
        }
    })


class ProfileUpdateResponse(BaseModel):
    """Schema for profile update response"""
    id: int
    email: str
    phone: Optional[str] = None
    is_email_verified: bool
    is_phone_verified: bool
    message: str
    requires_verification: bool
    verification_type: Optional[Literal["email", "phone", "both"]] = None

    model_config = ConfigDict(from_attributes=True)


# ============ Password Change ============

class PasswordChangeRequest(BaseModel):
    """Schema for changing password"""
    current_password: str = Field(..., min_length=1, description="Current password for verification")
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


# ============ Notification Preferences ============

class NotificationPreferences(BaseModel):
    """Schema for notification preferences"""
    # Email notifications
    email_appointments: bool = True
    email_lab_results: bool = True
    email_radiology_results: bool = True
    email_prescriptions: bool = True
    email_bills: bool = True
    email_payment_reminders: bool = True
    email_health_tips: bool = False
    email_newsletter: bool = False

    # SMS notifications
    sms_appointments: bool = True
    sms_lab_results: bool = False
    sms_radiology_results: bool = False
    sms_prescriptions: bool = False
    sms_bills: bool = True
    sms_payment_reminders: bool = True
    sms_emergency_alerts: bool = True

    # Push notifications
    push_notifications: bool = True
    push_appointments: bool = True
    push_results: bool = True
    push_medications: bool = True
    push_bills: bool = True

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email_appointments": True,
            "email_lab_results": True,
            "sms_appointments": True,
            "push_notifications": True
        }
    })


# ============ Appearance Preferences ============

class AppearancePreferences(BaseModel):
    """Schema for appearance preferences"""
    theme: Literal["light", "dark", "auto"] = "light"
    language: str = "id"  # ISO 639-1 language code
    timezone: str = "Asia/Jakarta"  # IANA timezone database
    date_format: Literal["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"] = "DD/MM/YYYY"
    time_format: Literal["24h", "12h"] = "24h"
    font_size: Literal["small", "medium", "large", "extra_large"] = "medium"
    high_contrast: bool = False
    reduce_motion: bool = False

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "theme": "light",
            "language": "id",
            "timezone": "Asia/Jakarta",
            "date_format": "DD/MM/YYYY"
        }
    })


# ============ Privacy Settings ============

class PrivacySettings(BaseModel):
    """Schema for privacy settings"""
    # Data sharing preferences
    share_data_with_research: bool = False
    share_data_with_pharmacies: bool = True
    share_data_with_labs: bool = True
    share_data_with_bpjs: bool = True

    # Caregiver access
    allow_caregiver_access: bool = False
    caregiver_access_level: Optional[Literal["full", "limited", "billing_only"]] = None

    # Communication preferences
    allow_promotional_communications: bool = False
    allow_third_party_communications: bool = False

    # Data retention
    data_retention_consent: bool = True

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "share_data_with_bpjs": True,
            "share_data_with_pharmacies": True,
            "allow_caregiver_access": False
        }
    })


# ============ Security Settings ============

class SecuritySettingsOverview(BaseModel):
    """Schema for security settings overview"""
    mfa_enabled: bool
    has_security_questions: bool
    last_password_change: Optional[datetime] = None
    password_age_days: Optional[int] = None
    failed_login_attempts: int
    is_locked: bool
    locked_until: Optional[datetime] = None
    active_sessions: int

    model_config = ConfigDict(from_attributes=True)


class SessionInfo(BaseModel):
    """Schema for active session info"""
    id: int
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    ip_address: Optional[str] = None
    is_active: bool
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    is_current_session: bool = False

    model_config = ConfigDict(from_attributes=True)


# ============ Verification ============

class EmailVerificationRequest(BaseModel):
    """Schema for email verification"""
    token: str = Field(..., min_length=1, description="Email verification token")


class PhoneVerificationRequest(BaseModel):
    """Schema for phone verification"""
    code: str = Field(..., min_length=6, max_length=6, pattern=r'^[0-9]{6}$', description="6-digit SMS verification code")


class VerificationSendRequest(BaseModel):
    """Schema for requesting verification code"""
    type: Literal["email", "phone"] = Field(..., description="Type of verification to send")


class VerificationSendResponse(BaseModel):
    """Schema for verification send response"""
    message: str
    expires_at: datetime
    sent_to: str


# ============ Account Deletion ============

class DeleteAccountRequest(BaseModel):
    """Schema for account deletion request"""
    password: str = Field(..., min_length=1, description="Current password for verification")
    reason: Optional[str] = Field(None, max_length=1000, description="Reason for account deletion")
    confirm: bool = Field(..., description="Confirm account deletion")
    understand_data_loss: bool = Field(..., description="Understand that all data will be permanently deleted")

    @field_validator('confirm')
    @classmethod
    def validate_confirmation(cls, v: bool) -> bool:
        """Validate that user has confirmed deletion"""
        if not v:
            raise ValueError('You must confirm account deletion')
        return v

    @field_validator('understand_data_loss')
    @classmethod
    def validate_understanding(cls, v: bool) -> bool:
        """Validate that user understands data loss"""
        if not v:
            raise ValueError('You must acknowledge that all data will be permanently deleted')
        return v


class DeleteAccountResponse(BaseModel):
    """Schema for account deletion response"""
    success: bool
    message: str
    scheduled_deletion_date: Optional[datetime] = None
    can_cancel: bool = True


# ============ Sessions Management ============

class RevokeSessionRequest(BaseModel):
    """Schema for revoking a specific session"""
    session_id: int = Field(..., description="Session ID to revoke")


class RevokeAllSessionsResponse(BaseModel):
    """Schema for revoking all sessions response"""
    revoked_count: int
    message: str


# ============ Account Settings Response ============

class AccountSettingsResponse(BaseModel):
    """Schema for complete account settings response"""
    profile: ProfileSettings
    notifications: NotificationPreferences
    appearance: AppearancePreferences
    privacy: PrivacySettings
    security: SecuritySettingsOverview

    model_config = ConfigDict(from_attributes=True)


# ============ Security Settings Response ============

class SecuritySettingsResponse(BaseModel):
    """Schema for detailed security settings response"""
    mfa_enabled: bool
    has_security_questions: bool
    security_question_1: Optional[str] = None
    security_question_2: Optional[str] = None
    last_password_change: Optional[datetime] = None
    password_age_days: Optional[int] = None
    failed_login_attempts: int
    is_locked: bool
    locked_until: Optional[datetime] = None
    active_sessions: int
    recent_sessions: List[SessionInfo]
    last_login: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
