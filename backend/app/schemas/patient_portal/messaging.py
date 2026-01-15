"""Patient Portal Messaging Schemas

Pydantic schemas for secure messaging between patients and healthcare providers.
STORY-049: Communication Center
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum


class MessageCategory(str, Enum):
    """Categories for message threads"""
    MEDICAL_QUESTION = "medical_question"
    APPOINTMENT_QUESTION = "appointment_question"
    BILLING_QUESTION = "billing_question"
    PRESCRIPTION_QUESTION = "prescription_question"
    OTHER = "other"


class MessageThreadStatus(str, Enum):
    """Status of a message thread"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    CLOSED = "closed"


class RecipientRole(str, Enum):
    """Role of the message recipient"""
    DOCTOR = "doctor"
    NURSE = "nurse"
    STAFF = "staff"
    ADMIN = "admin"
    PHARMACIST = "pharmacist"
    OTHER = "other"


class SenderType(str, Enum):
    """Type of message sender"""
    PATIENT = "patient"
    PROVIDER = "provider"


class MessageAttachment(BaseModel):
    """Attachment in a message"""
    file_name: str
    file_url: str
    file_size_bytes: Optional[int] = None
    content_type: Optional[str] = None


class MessageThreadSummary(BaseModel):
    """Summary of a message thread for list views"""
    id: int
    subject: str
    category: MessageCategory
    recipient_name: str
    recipient_role: RecipientRole

    # Last message info
    last_message_preview: str
    last_message_at: Optional[datetime] = None
    last_message_sender_type: Optional[SenderType] = None

    # Thread status
    status: MessageThreadStatus
    is_starred: bool
    is_archived: bool

    # Unread count
    unread_count: int = 0

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageThreadList(BaseModel):
    """Response for listing message threads"""
    threads: List[MessageThreadSummary]
    total_count: int
    unread_count: int


class MessageDetail(BaseModel):
    """Detailed message information"""
    id: int
    sender_type: SenderType
    sender_id: int
    sender_name: str
    content: str
    attachments: Optional[List[MessageAttachment]] = None

    # Read status
    is_read: bool
    read_at: Optional[datetime] = None

    # Delivery status
    is_delivered: bool
    delivered_at: Optional[datetime] = None

    # Timestamp
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageThreadResponse(BaseModel):
    """Complete message thread with all messages"""
    id: int
    subject: str
    category: MessageCategory
    recipient_id: Optional[int] = None
    recipient_name: str
    recipient_role: RecipientRole
    status: MessageThreadStatus
    is_starred: bool
    is_archived: bool

    # Messages
    messages: List[MessageDetail]

    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SendMessageRequest(BaseModel):
    """Request to send a new message"""
    thread_id: Optional[int] = Field(None, description="Existing thread ID. If None, creates new thread.")
    subject: Optional[str] = Field(None, min_length=3, max_length=255, description="Required for new threads.")
    category: MessageCategory = Field(MessageCategory.OTHER, description="Required for new threads.")
    recipient_id: Optional[int] = Field(None, description="Required for new threads. User ID of recipient.")
    recipient_name: str = Field(..., min_length=2, max_length=255, description="Required for new threads.")
    recipient_role: RecipientRole = Field(RecipientRole.STAFF, description="Required for new threads.")
    content: str = Field(..., min_length=1, max_length=5000, description="Message content.")
    attachments: Optional[List[MessageAttachment]] = Field(None, max_length=5, description="Optional attachments.")

    @field_validator('content')
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        """Sanitize message content"""
        # Basic sanitization - strip excessive whitespace
        return ' '.join(v.split())

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "thread_id": None,
            "subject": "Question about prescription",
            "category": "prescription_question",
            "recipient_id": 5,
            "recipient_name": "Dr. Smith",
            "recipient_role": "doctor",
            "content": "I have a question about my new medication dosage.",
            "attachments": None
        }
    })


class SendMessageResponse(BaseModel):
    """Response after sending a message"""
    thread_id: int
    message_id: int
    is_new_thread: bool
    message: str


class MarkAsReadRequest(BaseModel):
    """Request to mark messages as read"""
    message_ids: List[int] = Field(..., min_length=1, description="List of message IDs to mark as read.")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "message_ids": [123, 124, 125]
        }
    })


class MarkAsReadResponse(BaseModel):
    """Response after marking messages as read"""
    marked_count: int
    message: str


class StarThreadRequest(BaseModel):
    """Request to star or unstar a thread"""
    is_starred: bool = Field(..., description="True to star, False to unstar.")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "is_starred": True
        }
    })


class StarThreadResponse(BaseModel):
    """Response after starring/unstarring a thread"""
    thread_id: int
    is_starred: bool
    message: str


class ArchiveThreadRequest(BaseModel):
    """Request to archive or unarchive a thread"""
    is_archived: bool = Field(..., description="True to archive, False to unarchive.")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "is_archived": True
        }
    })


class ArchiveThreadResponse(BaseModel):
    """Response after archiving/unarchiving a thread"""
    thread_id: int
    is_archived: bool
    message: str


class UnreadCountResponse(BaseModel):
    """Response for unread message count"""
    total_unread: int
    threads_with_unread: int


class ThreadUpdateRequest(BaseModel):
    """Request to update thread metadata"""
    subject: Optional[str] = Field(None, min_length=3, max_length=255)
    category: Optional[MessageCategory] = None
    status: Optional[MessageThreadStatus] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "subject": "Updated subject",
            "category": "medical_question",
            "status": "resolved"
        }
    })


class ThreadUpdateResponse(BaseModel):
    """Response after updating thread metadata"""
    thread_id: int
    message: str
