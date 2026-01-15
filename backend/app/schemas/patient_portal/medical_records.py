"""Patient Portal Medical Records & Documents Schemas

Pydantic schemas for medical records and document management through patient portal.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date
from typing import List, Optional, Literal
from enum import Enum


class DocumentCategory(str, Enum):
    """Category of medical document for organization and filtering"""
    CLINICAL_NOTES = "clinical_notes"
    LAB_RESULTS = "lab_results"
    RADIOLOGY_REPORTS = "radiology_reports"
    PRESCRIPTIONS = "prescriptions"
    REFERRAL_LETTERS = "referral_letters"
    MEDICAL_CERTIFICATES = "medical_certificates"
    INSURANCE_DOCUMENTS = "insurance_documents"
    ID_DOCUMENTS = "id_documents"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Processing status of uploaded document"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    AVAILABLE = "available"
    ARCHIVED = "archived"


class DocumentType(str, Enum):
    """File format type of the document"""
    PDF = "pdf"
    JPG = "jpg"
    PNG = "png"
    DICOM = "dicom"
    TXT = "txt"
    DOCX = "docx"


class MedicalDocument(BaseModel):
    """Complete medical document metadata.

    Contains all information about a medical document stored in the system.

    Attributes:
        id: Unique identifier for the document
        title: Document title or description
        category: Category classification of the document
        document_type: File format type
        status: Current processing status
        file_url: Secure URL to access the document file
        file_size: File size in bytes
        upload_date: Timestamp when document was uploaded
        encounter_id: Optional associated medical encounter ID
        uploaded_by: Name of user who uploaded the document
        description: Detailed description of document contents
        tags: List of searchable tags for the document
        access_count: Number of times document has been accessed
        last_accessed: Most recent access timestamp
        expires_at: Optional expiration date for document access
        is_confidential: Whether document is marked as confidential
    """

    id: int = Field(..., description="Unique document identifier")

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Document title or name"
    )

    category: DocumentCategory = Field(
        ...,
        description="Document category classification"
    )

    document_type: DocumentType = Field(
        ...,
        description="File format type"
    )

    status: DocumentStatus = Field(
        ...,
        description="Current document processing status"
    )

    file_url: str = Field(
        ...,
        description="Secure URL to access document file"
    )

    file_size: int = Field(
        ...,
        ge=0,
        description="File size in bytes"
    )

    upload_date: datetime = Field(
        ...,
        description="Document upload timestamp"
    )

    encounter_id: Optional[int] = Field(
        None,
        description="Associated medical encounter ID"
    )

    uploaded_by: str = Field(
        ...,
        max_length=255,
        description="Name of user who uploaded"
    )

    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Detailed document description"
    )

    tags: List[str] = Field(
        default_factory=list,
        description="Searchable tags"
    )

    access_count: int = Field(
        default=0,
        ge=0,
        description="Number of times accessed"
    )

    last_accessed: Optional[datetime] = Field(
        None,
        description="Most recent access timestamp"
    )

    expires_at: Optional[datetime] = Field(
        None,
        description="Document access expiration date"
    )

    is_confidential: bool = Field(
        default=False,
        description="Whether document is confidential"
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Ensure title is not empty or just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()

    @field_validator("file_url")
    @classmethod
    def validate_file_url(cls, v: str) -> str:
        """Ensure file URL uses HTTPS."""
        if not v.startswith("https://"):
            raise ValueError("File URL must use HTTPS for security")
        return v

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Ensure expiration date is in the future if set."""
        if v is not None and v <= datetime.now():
            raise ValueError("Expiration date must be in the future")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Ensure tags are not empty strings."""
        tags = [tag.strip() for tag in v]
        if any(not tag for tag in tags):
            raise ValueError("Tags cannot be empty strings")
        return tags

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadRequest(BaseModel):
    """Request schema for uploading a new medical document.

    Used when patients upload documents through the patient portal.

    Attributes:
        title: Document title
        category: Document category classification
        document_type: File format type
        encounter_id: Optional associated encounter ID
        description: Optional document description
        tags: Optional list of tags for categorization
        is_confidential: Whether to mark as confidential
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Document title"
    )

    category: DocumentCategory = Field(
        ...,
        description="Document category"
    )

    document_type: DocumentType = Field(
        ...,
        description="File format type"
    )

    encounter_id: Optional[int] = Field(
        None,
        description="Associated medical encounter ID"
    )

    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Document description"
    )

    tags: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Tags for categorization (max 10)"
    )

    is_confidential: bool = Field(
        default=False,
        description="Mark as confidential"
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Ensure title is not empty or just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Ensure tags are valid and not too many."""
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        tags = [tag.strip() for tag in v if tag.strip()]
        if len(tags) != len(v):
            raise ValueError("Tags cannot be empty strings")
        return tags

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    """Response after successful document upload.

    Provides confirmation and access details for uploaded document.

    Attributes:
        document_id: ID of the uploaded document
        message: Success message (in Indonesian)
        file_url: URL to access the uploaded document
        access_code: Optional access code for shared documents
        upload_date: Timestamp of upload
        expires_at: Optional expiration date
    """

    document_id: int = Field(
        ...,
        description="Uploaded document ID"
    )

    message: str = Field(
        ...,
        description="Success message in Indonesian"
    )

    file_url: str = Field(
        ...,
        description="URL to access document"
    )

    access_code: Optional[str] = Field(
        None,
        description="Access code if document is shared"
    )

    upload_date: datetime = Field(
        ...,
        description="Upload timestamp"
    )

    expires_at: Optional[datetime] = Field(
        None,
        description="Access expiration date"
    )

    @field_validator("file_url")
    @classmethod
    def validate_file_url(cls, v: str) -> str:
        """Ensure file URL uses HTTPS."""
        if not v.startswith("https://"):
            raise ValueError("File URL must use HTTPS")
        return v

    model_config = ConfigDict(from_attributes=True)


class MedicalDocumentsList(BaseModel):
    """Paginated list of medical documents.

    Returns filtered and paginated documents with metadata.

    Attributes:
        documents: List of medical documents
        total: Total number of documents matching filters
        page: Current page number
        page_size: Number of documents per page
        total_pages: Total number of pages
        has_next: Whether there is a next page
        has_previous: Whether there is a previous page
    """

    documents: List[MedicalDocument] = Field(
        default_factory=list,
        description="List of medical documents"
    )

    total: int = Field(
        ...,
        ge=0,
        description="Total matching documents"
    )

    page: int = Field(
        ...,
        ge=1,
        description="Current page number"
    )

    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Documents per page"
    )

    total_pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages"
    )

    has_next: bool = Field(
        ...,
        description="Whether next page exists"
    )

    has_previous: bool = Field(
        ...,
        description="Whether previous page exists"
    )

    @field_validator("page", "page_size")
    @classmethod
    def validate_pagination(cls, v: int, info) -> int:
        """Ensure pagination values are positive."""
        if v < 1:
            raise ValueError("Page and page_size must be positive")
        return v

    model_config = ConfigDict(from_attributes=True)


class DocumentAccessLog(BaseModel):
    """Access log entry for document access tracking.

    Records each time a document is accessed for audit purposes.

    Attributes:
        id: Unique access log identifier
        document_id: ID of the accessed document
        document_title: Title of the accessed document
        accessed_by: Name of user who accessed the document
        access_type: Type of access (view, download, share)
        access_date: Timestamp of access
        ip_address: IP address of the accessor
        user_agent: Browser/client user agent
        purpose: Purpose of access (if provided)
    """

    id: int = Field(
        ...,
        description="Access log entry ID"
    )

    document_id: int = Field(
        ...,
        description="Accessed document ID"
    )

    document_title: str = Field(
        ...,
        description="Title of accessed document"
    )

    accessed_by: str = Field(
        ...,
        max_length=255,
        description="Name of user who accessed"
    )

    access_type: Literal["view", "download", "share"] = Field(
        ...,
        description="Type of access performed"
    )

    access_date: datetime = Field(
        ...,
        description="Access timestamp"
    )

    ip_address: Optional[str] = Field(
        None,
        max_length=45,
        description="IP address (IPv4 or IPv6)"
    )

    user_agent: Optional[str] = Field(
        None,
        max_length=500,
        description="Client user agent string"
    )

    purpose: Optional[str] = Field(
        None,
        max_length=500,
        description="Purpose of access (Tujuan akses)"
    )

    @field_validator("document_title")
    @classmethod
    def validate_document_title(cls, v: str) -> str:
        """Ensure document title is not empty."""
        if not v.strip():
            raise ValueError("Document title cannot be empty")
        return v.strip()

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, v: Optional[str]) -> Optional[str]:
        """Basic validation for IP address format."""
        if v is not None and not v.strip():
            return None
        return v

    model_config = ConfigDict(from_attributes=True)


class DocumentShareRequest(BaseModel):
    """Request schema for sharing a medical document.

    Used when patients want to share documents with healthcare providers or family.

    Attributes:
        document_id: ID of the document to share
        recipient_name: Name of the recipient
        recipient_email: Email address of recipient
        recipient_type: Type of recipient (provider, family, other)
        access_duration: Duration of access in hours (optional)
        purpose: Purpose of sharing the document
        allow_download: Whether recipient can download the document
        message: Optional message to recipient
    """

    document_id: int = Field(
        ...,
        gt=0,
        description="Document ID to share"
    )

    recipient_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Recipient name (Nama penerima)"
    )

    recipient_email: str = Field(
        ...,
        max_length=255,
        description="Recipient email address"
    )

    recipient_type: Literal["provider", "family", "other"] = Field(
        ...,
        description="Type of recipient"
    )

    access_duration: Optional[int] = Field(
        None,
        ge=1,
        le=720,  # Max 30 days (720 hours)
        description="Access duration in hours"
    )

    purpose: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Purpose of sharing (Tujuan berbagi)"
    )

    allow_download: bool = Field(
        default=True,
        description="Allow recipient to download"
    )

    message: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional message to recipient"
    )

    @field_validator("recipient_name")
    @classmethod
    def validate_recipient_name(cls, v: str) -> str:
        """Ensure recipient name is not empty."""
        if not v.strip():
            raise ValueError("Recipient name cannot be empty")
        return v.strip()

    @field_validator("recipient_email")
    @classmethod
    def validate_recipient_email(cls, v: str) -> str:
        """Basic email validation."""
        email = v.strip().lower()
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Invalid email address format")
        return email

    @field_validator("purpose")
    @classmethod
    def validate_purpose(cls, v: str) -> str:
        """Ensure purpose is not empty."""
        if not v.strip():
            raise ValueError("Purpose cannot be empty")
        return v.strip()

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: Optional[str]) -> Optional[str]:
        """Clean up message if provided."""
        if v is not None:
            return v.strip() or None
        return v

    model_config = ConfigDict(from_attributes=True)


class DocumentShareResponse(BaseModel):
    """Response after successfully sharing a document.

    Provides sharing details and access information for the recipient.

    Attributes:
        share_id: Unique sharing session identifier
        document_id: ID of the shared document
        access_url: Secure URL for recipient to access document
        access_code: Optional access code for additional security
        expires_at: Timestamp when access expires
        message: Success message (in Indonesian)
        recipient_email: Email of the recipient
        share_created: Timestamp when share was created
    """

    share_id: str = Field(
        ...,
        description="Unique share session ID"
    )

    document_id: int = Field(
        ...,
        description="Shared document ID"
    )

    access_url: str = Field(
        ...,
        description="Secure access URL for recipient"
    )

    access_code: Optional[str] = Field(
        None,
        description="Access code if required"
    )

    expires_at: datetime = Field(
        ...,
        description="Access expiration timestamp"
    )

    message: str = Field(
        ...,
        description="Success message in Indonesian"
    )

    recipient_email: str = Field(
        ...,
        description="Recipient email address"
    )

    share_created: datetime = Field(
        ...,
        description="Share creation timestamp"
    )

    @field_validator("access_url")
    @classmethod
    def validate_access_url(cls, v: str) -> str:
        """Ensure access URL uses HTTPS."""
        if not v.startswith("https://"):
            raise ValueError("Access URL must use HTTPS")
        return v

    @field_validator("recipient_email")
    @classmethod
    def validate_recipient_email(cls, v: str) -> str:
        """Basic email validation."""
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid recipient email")
        return v

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, v: datetime, info) -> datetime:
        """Ensure expiration is in the future."""
        if v <= datetime.now():
            raise ValueError("Expiration must be in the future")
        return v

    model_config = ConfigDict(from_attributes=True)
