from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.core.encryption import encrypt_field, decrypt_field


class AuditLog(Base):
    """Audit log model for tracking all user actions for compliance with UU 27/2022"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # User information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(100), nullable=True)

    # Action details
    action = Column(String(50), nullable=False, index=True)  # CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT, etc.
    resource_type = Column(String(50), nullable=False, index=True)  # Patient, User, Prescription, etc.
    resource_id = Column(String(100), nullable=True, index=True)

    # Request metadata
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    request_path = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)

    # Encrypted sensitive data fields
    _request_body = Column("request_body", Text, nullable=True)  # Encrypted
    _response_body = Column("response_body", Text, nullable=True)  # Encrypted
    _changes = Column("changes", Text, nullable=True)  # Encrypted

    # Result
    success = Column(Boolean, default=True, index=True)
    failure_reason = Column(Text, nullable=True)

    # Additional context
    additional_data = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    # Property getters/setters for automatic encryption/decryption
    @property
    def request_body(self) -> str:
        """Get decrypted request body."""
        if self._request_body is None:
            return None
        return decrypt_field(self._request_body)

    @request_body.setter
    def request_body(self, value: str) -> None:
        """Set and encrypt request body."""
        self._request_body = encrypt_field(value)

    @property
    def response_body(self) -> str:
        """Get decrypted response body."""
        if self._response_body is None:
            return None
        return decrypt_field(self._response_body)

    @response_body.setter
    def response_body(self, value: str) -> None:
        """Set and encrypt response body."""
        self._response_body = encrypt_field(value)

    @property
    def changes(self) -> str:
        """Get decrypted changes."""
        if self._changes is None:
            return None
        return decrypt_field(self._changes)

    @changes.setter
    def changes(self, value: str) -> None:
        """Set and encrypt changes."""
        self._changes = encrypt_field(value)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user={self.username}, action={self.action}, resource={self.resource_type})>"
