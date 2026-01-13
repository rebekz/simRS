from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime


class LoginRequest(BaseModel):
    """Schema for user login request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str
    mfa_code: Optional[str] = Field(None, min_length=6, max_length=6, description="6-digit TOTP code if MFA enabled")


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    mfa_required: bool = False
    mfa_setup_required: bool = False


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class MFASetupRequest(BaseModel):
    """Schema for MFA setup initiation"""
    password: str  # Verify password before enabling MFA


class MFASetupResponse(BaseModel):
    """Schema for MFA setup response"""
    secret: str
    qr_code_url: str
    backup_codes: List[str]


class MFAVerifyRequest(BaseModel):
    """Schema for MFA verification during setup"""
    secret: str
    code: str = Field(..., min_length=6, max_length=6)


class PasswordChangeRequest(BaseModel):
    """Schema for password change"""
    old_password: str
    new_password: str = Field(..., min_length=12, max_length=100)

    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password meets security requirements"""
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in v):
            raise ValueError('Password must contain at least one special character')
        return v


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=12, max_length=100)

    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password meets security requirements"""
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in v):
            raise ValueError('Password must contain at least one special character')
        return v


class SessionResponse(BaseModel):
    """Schema for session information"""
    id: int
    device_type: Optional[str] = None
    device_name: Optional[str] = None
    browser: Optional[str] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    last_used_at: datetime
    is_current: bool = False

    class Config:
        from_attributes = True


class LoginHistoryResponse(BaseModel):
    """Schema for login history"""
    id: int
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    failure_reason: Optional[str] = None

    class Config:
        from_attributes = True
