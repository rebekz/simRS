from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base


class MessageThread(Base):
    """
    MessageThread model for patient portal messaging system.
    Represents a conversation thread between a patient and a healthcare provider.
    """
    __tablename__ = "message_threads"

    id = Column(Integer, primary_key=True, index=True)
    patient_portal_user_id = Column(
        Integer,
        ForeignKey("patient_portal_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    subject = Column(String(255), nullable=False)
    category = Column(
        SQLEnum("medical_question", "appointment_question", "billing_question",
                "prescription_question", "other", name="message_thread_category"),
        nullable=False,
        default="other",
        index=True
    )
    recipient_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    recipient_name = Column(String(255), nullable=False)
    recipient_role = Column(
        SQLEnum("doctor", "nurse", "staff", "admin", "pharmacist", "other",
                name="recipient_role"),
        nullable=False,
        default="staff"
    )
    is_starred = Column(Boolean, default=False, nullable=False, index=True)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    last_message_at = Column(DateTime(timezone=True), nullable=True, index=True)
    status = Column(
        SQLEnum("active", "resolved", "closed", name="message_thread_status"),
        nullable=False,
        default="active",
        index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    messages = relationship(
        "Message",
        back_populates="thread",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="Message.created_at.desc()"
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_message_threads_patient_status", "patient_portal_user_id", "status"),
        Index("ix_message_threads_recipient_status", "recipient_id", "status"),
        Index("ix_message_threads_last_message", "last_message_at"),
    )


class Message(Base):
    """
    Message model for patient portal messaging system.
    Represents individual messages within a thread.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(
        Integer,
        ForeignKey("message_threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sender_type = Column(
        SQLEnum("patient", "provider", name="message_sender_type"),
        nullable=False,
        index=True
    )
    sender_id = Column(Integer, nullable=False, index=True)
    sender_name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    attachments = Column(JSONB, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    is_delivered = Column(Boolean, default=False, nullable=False)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationships
    thread = relationship(
        "MessageThread",
        back_populates="messages"
    )
    read_receipts = relationship(
        "MessageReadReceipt",
        back_populates="message",
        cascade="all, delete-orphan"
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_messages_thread_created", "thread_id", "created_at"),
        Index("ix_messages_sender", "sender_type", "sender_id"),
    )


class MessageReadReceipt(Base):
    """
    MessageReadReceipt model for tracking when messages are read.
    Provides audit trail for message read status.
    """
    __tablename__ = "message_read_receipts"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(
        Integer,
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    read_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    read_at = Column(
        DateTime(timezone=True),
        server_default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    message = relationship(
        "Message",
        back_populates="read_receipts"
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_message_read_receipts_message_read_by", "message_id", "read_by"),
    )
