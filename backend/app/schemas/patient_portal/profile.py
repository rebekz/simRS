"""Patient Portal Profile Schemas

Pydantic schemas for patient portal profile and settings.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class PatientPortalProfile(BaseModel):
    """Schema for patient portal user profile"""
    id: int
    email: str
    phone: Optional[str] = None
    patient_id: int

    # Verification status
    is_active: bool
    is_email_verified: bool
    is_phone_verified: bool
    is_identity_verified: bool

    # Patient information
    patient_name: Optional[str] = None
    medical_record_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None

    # Security info
    mfa_enabled: bool = False
    has_security_questions: bool = False

    # Timestamps
    last_login: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatientPortalProfileUpdate(BaseModel):
    """Schema for updating portal profile"""
    phone: Optional[str] = Field(None, pattern=r'^\+?62[0-9]{9,13}$|^08[0-9]{8,11}$')
    email: Optional[EmailStr] = None


class SecuritySettings(BaseModel):
    """Schema for security settings"""
    mfa_enabled: bool
    has_security_questions: bool
    security_question_1: Optional[str] = None
    last_password_change: Optional[datetime] = None
    failed_login_attempts: int
    is_locked: bool
    locked_until: Optional[datetime] = None


class NotificationPreferences(BaseModel):
    """Schema for notification preferences"""
    email_appointments: bool = True
    email_lab_results: bool = True
    email_bills: bool = True
    email_prescriptions: bool = True
    sms_appointments: bool = True
    sms_lab_results: bool = False
    sms_bills: bool = True
    push_notifications: bool = True


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

    model_config = ConfigDict(from_attributes=True)


class SessionsListResponse(BaseModel):
    """Schema for sessions list response"""
    sessions: list[SessionInfo]
    current_session_id: int
    total: int


class AccountDeactivateRequest(BaseModel):
    """Schema for account deactivation request"""
    reason: Optional[str] = Field(None, max_length=1000, description="Reason for deactivation")
    confirm: bool = Field(..., description="Confirm deactivation")


class AccountDeactivateResponse(BaseModel):
    """Schema for account deactivation response"""
    success: bool
    message: str
    deactivated_at: Optional[datetime] = None
