"""User Management Models for STORY-037

This module provides database models for:
- User access requests
- Role assignment tracking

Note: Department model is defined in app.models.hospital
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.user import UserRole


class UserAccessRequest(Base):
    """User access request model for role and permission requests"""
    __tablename__ = "user_access_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    requested_role = Column(SQLEnum(UserRole), nullable=False)
    requested_department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    reason = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending", index=True)  # pending, approved, rejected
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="access_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    requested_department = relationship("Department")
