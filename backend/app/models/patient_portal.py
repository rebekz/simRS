"""Patient Portal models for STORY-041: Patient Registration & Account Creation

This module defines the PatientPortalUser, PatientPortalVerification, and related models
for managing patient portal access and authentication.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.session import Base


class ProxyAccessLevel(str, Enum):
    """Access levels for caregiver/proxy accounts"""
    FULL_ACCESS = "full_access"
    LIMITED_ACCESS = "limited_access"
    BILLING_ONLY = "billing_only"


class VerificationType(str, Enum):
    """Types of verification for patient portal registration"""
    EMAIL = "email"
    MOBILE = "mobile"
    IDENTITY = "identity"


class VerificationStatus(str, Enum):
    """Status of verification process"""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"


class PatientPortalUser(Base):
    """Patient Portal User model for patient portal authentication

    This model stores authentication and account information for patients accessing
    the patient portal. It links to the existing Patient model for medical data.
    """
    __tablename__ = "patient_portal_users"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to patient record")

    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False, comment="Portal login email")
    phone = Column(String(20), index=True, nullable=True, comment="Verified mobile number")
    hashed_password = Column(String(255), nullable=False, comment="Bcrypt hashed password")

    # Account status
    is_active = Column(Boolean, default=False, nullable=False, comment="Account active status (requires verification)")
    is_email_verified = Column(Boolean, default=False, nullable=False, comment="Email verification status")
    is_phone_verified = Column(Boolean, default=False, nullable=False, comment="Phone verification status")
    is_identity_verified = Column(Boolean, default=False, nullable=False, comment="Identity verification status (KTP/selfie)")

    # Security fields
    mfa_enabled = Column(Boolean, default=False, nullable=False, comment="Multi-factor authentication enabled")
    mfa_secret = Column(String(32), nullable=True, comment="TOTP secret for MFA")
    failed_login_attempts = Column(Integer, default=0, nullable=False, comment="Failed login attempt count")
    locked_until = Column(DateTime(timezone=True), nullable=True, comment="Account locked until this timestamp")
    password_changed_at = Column(DateTime(timezone=True), nullable=True, comment="Last password change timestamp")
    last_login = Column(DateTime(timezone=True), nullable=True, comment="Last successful login timestamp")
    security_question_1 = Column(String(255), nullable=True, comment="Security question 1")
    security_answer_1_hash = Column(String(255), nullable=True, comment="Hashed answer for security question 1")
    security_question_2 = Column(String(255), nullable=True, comment="Security question 2")
    security_answer_2_hash = Column(String(255), nullable=True, comment="Hashed answer for security question 2")

    # Registration tracking
    accepted_terms_at = Column(DateTime(timezone=True), nullable=True, comment="Terms of service acceptance timestamp")
    accepted_privacy_at = Column(DateTime(timezone=True), nullable=True, comment="Privacy policy acceptance timestamp")
    registration_ip = Column(String(45), nullable=True, comment="IP address at registration")
    registration_user_agent = Column(String(500), nullable=True, comment="User agent at registration")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Account creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Last update timestamp")
    deactivated_at = Column(DateTime(timezone=True), nullable=True, comment="Account deactivation timestamp")
    deactivated_reason = Column(Text, nullable=True, comment="Reason for deactivation")

    # Relationships
    patient = relationship("Patient", back_populates="portal_user")
    verifications = relationship("PatientPortalVerification", back_populates="portal_user", cascade="all, delete-orphan")
    sessions = relationship("PatientPortalSession", back_populates="portal_user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PatientPortalPasswordReset", back_populates="portal_user", cascade="all, delete-orphan")
    caregiver_links = relationship("CaregiverLink", foreign_keys="CaregiverLink.patient_portal_user_id", back_populates="caregiver", cascade="all, delete-orphan")


class PatientPortalVerification(Base):
    """Patient Portal Verification model for tracking verification attempts

    This model stores verification codes/tokens for email, SMS, and identity verification
    during patient registration and account recovery.
    """
    __tablename__ = "patient_portal_verifications"

    id = Column(Integer, primary_key=True, index=True)
    portal_user_id = Column(Integer, ForeignKey("patient_portal_users.id", ondelete="CASCADE"), nullable=False, index=True)
    verification_type = Column(SQLEnum(VerificationType), nullable=False, comment="Type of verification")
    verification_code = Column(String(10), nullable=True, comment="OTP code (email/SMS)")
    verification_token = Column(String(255), nullable=True, index=True, comment="Verification token for identity")
    verification_data = Column(Text, nullable=True, comment="Additional verification data (JSON)")

    # Contact information for verification
    email_address = Column(String(255), nullable=True, comment="Email being verified")
    phone_number = Column(String(20), nullable=True, comment="Phone being verified")

    # Status tracking
    status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    attempts = Column(Integer, default=0, nullable=False, comment="Verification attempts")
    max_attempts = Column(Integer, default=3, nullable=False, comment="Maximum allowed attempts")

    # Expiration
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="Code/token expiration timestamp")
    verified_at = Column(DateTime(timezone=True), nullable=True, comment="Successful verification timestamp")

    # Request tracking
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Relationships
    portal_user = relationship("PatientPortalUser", back_populates="verifications")


class PatientPortalSession(Base):
    """Patient Portal Session model for managing active sessions

    This model stores active sessions for patient portal users, enabling
    session management and revocation.
    """
    __tablename__ = "patient_portal_sessions"

    id = Column(Integer, primary_key=True, index=True)
    portal_user_id = Column(Integer, ForeignKey("patient_portal_users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True, comment="Hashed JWT token")

    # Session metadata
    device_type = Column(String(50), nullable=True, comment="Device type (mobile, desktop, tablet)")
    browser = Column(String(100), nullable=True, comment="Browser name")
    os = Column(String(100), nullable=True, comment="Operating system")
    ip_address = Column(String(45), nullable=True, comment="IP address of session")

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="Session expiration timestamp")
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Last activity timestamp")

    # Relationships
    portal_user = relationship("PatientPortalUser", back_populates="sessions")


class PatientPortalPasswordReset(Base):
    """Patient Portal Password Reset model for secure password reset

    This model stores password reset tokens for patient portal users.
    """
    __tablename__ = "patient_portal_password_resets"

    id = Column(Integer, primary_key=True, index=True)
    portal_user_id = Column(Integer, ForeignKey("patient_portal_users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)

    # Token metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="Token expiration timestamp")
    used_at = Column(DateTime(timezone=True), nullable=True, comment="Token usage timestamp")

    # Status
    is_used = Column(Boolean, default=False, nullable=False)

    # Request tracking
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Relationships
    portal_user = relationship("PatientPortalUser", back_populates="password_reset_tokens")


class CaregiverLink(Base):
    """Caregiver Link model for proxy/caregiver access

    This model manages caregiver/proxy relationships allowing family members
    to access patient records (for children, elderly, dependents).
    """
    __tablename__ = "caregiver_links"

    id = Column(Integer, primary_key=True, index=True)

    # The caregiver (who has the portal account)
    patient_portal_user_id = Column(Integer, ForeignKey("patient_portal_users.id", ondelete="CASCADE"), nullable=False, index=True)

    # The patient being linked (the care recipient)
    linked_patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)

    # Access configuration
    access_level = Column(SQLEnum(ProxyAccessLevel), nullable=False, default=ProxyAccessLevel.FULL_ACCESS, comment="Level of access granted")
    relationship_type = Column(String(100), nullable=False, comment="Relationship to patient (parent, spouse, child, guardian, etc.)")

    # Verification
    is_verified = Column(Boolean, default=False, nullable=False, comment="Caregiver relationship verified")
    verification_document_path = Column(String(500), nullable=True, comment="Path to verification document (birth certificate, power of attorney, etc.)")

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True, comment="Optional expiration for temporary access")
    deactivated_at = Column(DateTime(timezone=True), nullable=True)
    deactivated_reason = Column(Text, nullable=True)

    # Relationships
    caregiver = relationship("PatientPortalUser", foreign_keys=[patient_portal_user_id], back_populates="caregiver_links")
    linked_patient = relationship("Patient", foreign_keys=[linked_patient_id], back_populates="caregiver_links")
