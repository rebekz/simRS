"""User Management Schemas for STORY-037

This module provides Pydantic schemas for user management operations including:
- User CRUD operations
- Role assignment
- Department-based access
- Bulk user import
- Password reset
- User activity logs
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from app.models.user import UserRole


# =============================================================================
# User Management Schemas
# =============================================================================

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=12)
    role: UserRole
    department_id: Optional[int] = None
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    license_number: Optional[str] = None  # For doctors, nurses, pharmacists
    is_active: bool = True

    @validator('password')
    def validate_password(cls, v):
        """Validate password complexity"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        # Password complexity check can be enhanced
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    department_id: Optional[int] = None
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    license_number: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    license_number: Optional[str] = None
    is_active: bool
    is_superuser: bool
    mfa_enabled: bool
    last_login: Optional[datetime] = None
    failed_login_attempts: int
    locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for user list response"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int


class UserSearchQuery(BaseModel):
    """Schema for user search query"""
    search: Optional[str] = None
    role: Optional[UserRole] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# =============================================================================
# Role Management Schemas
# =============================================================================

class RoleAssignment(BaseModel):
    """Schema for assigning roles to users"""
    user_id: int
    role: UserRole
    assigned_by: int  # Admin user ID


class RoleResponse(BaseModel):
    """Schema for role response"""
    role: UserRole
    display_name: str
    description: str
    permissions: List[str]


# =============================================================================
# Department Management Schemas
# =============================================================================

class DepartmentCreate(BaseModel):
    """Schema for creating a department"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None
    parent_department_id: Optional[int] = None


class DepartmentUpdate(BaseModel):
    """Schema for updating a department"""
    name: Optional[str] = None
    description: Optional[str] = None
    parent_department_id: Optional[int] = None


class DepartmentResponse(BaseModel):
    """Schema for department response"""
    id: int
    name: str
    code: str
    description: Optional[str] = None
    parent_department_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Bulk Import Schemas
# =============================================================================

class BulkUserImportItem(BaseModel):
    """Schema for single user in bulk import"""
    username: str
    email: EmailStr
    full_name: str
    password: str
    role: UserRole
    department_code: Optional[str] = None
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    license_number: Optional[str] = None


class BulkUserImportRequest(BaseModel):
    """Schema for bulk user import request"""
    users: List[BulkUserImportItem]
    send_welcome_email: bool = False


class BulkUserImportResponse(BaseModel):
    """Schema for bulk user import response"""
    total: int
    succeeded: int
    failed: int
    errors: List[dict]  # List of {row, username, error}


# =============================================================================
# Password Reset Schemas
# =============================================================================

class AdminPasswordReset(BaseModel):
    """Schema for admin password reset"""
    user_id: int
    new_password: str = Field(..., min_length=12)
    force_change_on_next_login: bool = True


class PasswordResetResponse(BaseModel):
    """Schema for password reset response"""
    user_id: int
    username: str
    reset_at: datetime
    force_change_on_next_login: bool


# =============================================================================
# User Activity Log Schemas
# =============================================================================

class UserActivityLogResponse(BaseModel):
    """Schema for user activity log response"""
    id: int
    user_id: int
    username: str
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    details: Optional[dict] = None


class UserActivityLogsResponse(BaseModel):
    """Schema for user activity logs list response"""
    logs: List[UserActivityLogResponse]
    total: int
    page: int
    page_size: int


# =============================================================================
# User Access Request Schemas
# =============================================================================

class UserAccessRequestCreate(BaseModel):
    """Schema for creating user access request"""
    requested_role: UserRole
    requested_department_id: Optional[int] = None
    reason: str = Field(..., min_length=10, max_length=500)


class UserAccessRequestResponse(BaseModel):
    """Schema for user access request response"""
    id: int
    user_id: int
    username: str
    full_name: str
    requested_role: UserRole
    requested_department_id: Optional[int] = None
    reason: str
    status: str  # pending, approved, rejected
    requested_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None
    review_notes: Optional[str] = None


class AccessRequestDecision(BaseModel):
    """Schema for access request decision"""
    decision: str  # approved, rejected
    review_notes: Optional[str] = None
    assign_role: Optional[UserRole] = None
    assign_department_id: Optional[int] = None


# =============================================================================
# User Profile Schemas
# =============================================================================

class UserProfileUpdate(BaseModel):
    """Schema for user to update their own profile"""
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserPasswordChange(BaseModel):
    """Schema for user to change their own password"""
    current_password: str
    new_password: str = Field(..., min_length=12)

    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password complexity"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
