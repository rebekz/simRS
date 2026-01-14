"""Clinical Notes model for STORY-015: Clinical Notes (SOAP)

This module defines the database model for clinical documentation with
versioning, audit trail, and digital signature support.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.session import Base


# Note type enum
note_type_enum = SQLEnum(
    'soap',          # Subjective, Objective, Assessment, Plan
    'admission',     # Admission note
    'progress',      # Progress note
    'discharge',     # Discharge summary
    'consultation',  # Consultation note
    'procedure',     # Procedure note
    'operating',     # Operating room note
    'emergency',     # Emergency department note
    'telephone',     # Telephone encounter note
    'email',         # Email communication note
    'other',         # Other type
    name='note_type',
    create_type=True,
)


# Note status enum
note_status_enum = SQLEnum(
    'draft',         # Being edited
    'pending',       # Awaiting signature
    'signed',        # Digitally signed
    'amended',       # Amended after signing
    name='note_status',
    create_type=True,
)


class ClinicalNote(Base):
    """Clinical documentation with SOAP structure and version control."""
    __tablename__ = "clinical_notes"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    # Patient and encounter
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id", ondelete="SET NULL"), nullable=True, index=True)

    # Note classification
    note_type = Column(note_type_enum, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    status = Column(note_status_enum, nullable=False, index=True, default='draft')

    # SOAP structure (stored as JSONB for flexibility)
    subjective = Column(Text, nullable=True)  # Subjective - patient's complaint
    objective = Column(Text, nullable=True)   # Objective - findings, vitals, exam
    assessment = Column(Text, nullable=True)  # Assessment - diagnosis, clinical impression
    plan = Column(Text, nullable=True)        # Plan - treatment, follow-up

    # Alternative: Full note content for non-SOAP notes
    content = Column(Text, nullable=True)

    # Additional structured data
    structured_data = Column(JSONB, nullable=True)  # Vitals, labs, etc.

    # Attribution
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    signed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)

    # Co-signature (for trainees, residents)
    cosigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    cosigned_at = Column(DateTime(timezone=True), nullable=True)

    # Version control
    version = Column(Integer, nullable=False, default=1, index=True)
    parent_note_id = Column(Integer, ForeignKey("clinical_notes.id"), nullable=True)  # For amendments
    is_amendment = Column(Boolean, server_default="false", nullable=False)

    # Timing
    note_date = Column(DateTime(timezone=True), nullable=False, index=True)  # When the care occurred
    # Note: note_date != created_at - created_at is when documented, note_date is when care occurred

    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id], backref="clinical_notes")
    encounter = relationship("Encounter", foreign_keys=[encounter_id])
    author = relationship("User", foreign_keys=[author_id])
    signer = relationship("User", foreign_keys=[signed_by_id])
    cosigner = relationship("User", foreign_keys=[cosigned_by_id])
    parent_note = relationship("ClinicalNote", remote_side=[id], backref="amendments")


class ClinicalNoteAttachment(Base):
    """Attachments for clinical notes (images, documents, etc.)."""
    __tablename__ = "clinical_note_attachments"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("clinical_notes.id", ondelete="CASCADE"), nullable=False, index=True)

    # File information
    filename = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False)  # MIME type
    file_size = Column(Integer, nullable=False)  # in bytes
    file_path = Column(String(1000), nullable=False)  # Storage path

    # Metadata
    description = Column(Text, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    note = relationship("ClinicalNote", foreign_keys=[note_id], backref="attachments")
    uploader = relationship("User", foreign_keys=[uploaded_by])


class ClinicalNoteSignature(Base):
    """Digital signatures for clinical notes (audit trail)."""
    __tablename__ = "clinical_note_signatures"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("clinical_notes.id", ondelete="CASCADE"), nullable=False, index=True)

    # Signer information
    signer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    signer_name = Column(String(500), nullable=False)  # Denormalized for audit
    signer_role = Column(String(100), nullable=False)

    # Signature data
    signature_hash = Column(String(500), nullable=False)  # Cryptographic hash
    signature_ip = Column(String(50), nullable=False)  # IP address
    signature_user_agent = Column(Text, nullable=True)  # Browser/device

    # Timing
    signed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    note = relationship("ClinicalNote", foreign_keys=[note_id], backref="signatures")
    signer = relationship("User", foreign_keys=[signer_id])


class ClinicalNoteShare(Base):
    """Shared notes (with patient consent or internal sharing)."""
    __tablename__ = "clinical_note_shares"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("clinical_notes.id", ondelete="CASCADE"), nullable=False, index=True)

    # Share details
    shared_with = Column(Integer, ForeignKey("users.id"), nullable=False)  # User ID
    share_type = Column(String(50), nullable=False)  # 'patient', 'colleague', 'external'
    access_level = Column(String(50), nullable=False)  # 'read', 'comment'

    # Consent and expiration
    consent_obtained = Column(Boolean, server_default="false", nullable=False)
    consent_date = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    note = relationship("ClinicalNote", foreign_keys=[note_id], backref="shares")
    shared_with_user = relationship("User", foreign_keys=[shared_with])
    creator = relationship("User", foreign_keys=[created_by])
