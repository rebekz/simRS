"""Clinical Notes schemas for STORY-015: Clinical Notes (SOAP)

This module defines Pydantic schemas for clinical documentation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Clinical Note Schemas
class ClinicalNoteBase(BaseModel):
    """Base clinical note schema."""
    note_type: str = Field(..., description="Type of note (soap, admission, progress, etc.)")
    title: str = Field(..., min_length=1, max_length=500, description="Note title")
    note_date: datetime = Field(..., description="When the care occurred")
    subjective: Optional[str] = Field(None, description="Subjective - patient's complaint")
    objective: Optional[str] = Field(None, description="Objective - findings, vitals, exam")
    assessment: Optional[str] = Field(None, description="Assessment - diagnosis, impression")
    plan: Optional[str] = Field(None, description="Plan - treatment, follow-up")
    content: Optional[str] = Field(None, description="Full content for non-SOAP notes")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Structured data (vitals, labs, etc.)")


class ClinicalNoteCreate(ClinicalNoteBase):
    """Schema for creating a clinical note."""
    patient_id: int
    encounter_id: Optional[int] = None


class ClinicalNoteUpdate(BaseModel):
    """Schema for updating a clinical note."""
    title: Optional[str] = None
    note_date: Optional[datetime] = None
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    content: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ClinicalNoteResponse(ClinicalNoteBase):
    """Schema for clinical note response."""
    id: int
    uuid: str
    patient_id: int
    encounter_id: Optional[int] = None
    status: str
    version: int
    is_amendment: bool
    parent_note_id: Optional[int] = None

    # Attribution
    author_id: int
    signed_by_id: Optional[int] = None
    signed_at: Optional[datetime] = None
    cosigned_by_id: Optional[int] = None
    cosigned_at: Optional[datetime] = None

    # System fields
    created_at: datetime
    updated_at: datetime

    # Expanded
    author_name: Optional[str] = None
    signer_name: Optional[str] = None

    class Config:
        from_attributes = True


# SOAP Note Specific Schema
class SOAPNoteCreate(BaseModel):
    """Schema for creating a SOAP note."""
    patient_id: int
    encounter_id: Optional[int] = None
    note_date: datetime
    title: str = Field(default="Catatan SOAP", description="SOAP note title")
    subjective: Optional[str] = Field(None, description="Keluhan pasien (Subjektif)")
    objective: Optional[str] = Field(None, description="Pemeriksaan fisik, vital signs (Objektif)")
    assessment: Optional[str] = Field(None, description="Diagnosis, kesan klinis (Asesmen)")
    plan: Optional[str] = Field(None, description="Rencana penatalaksanaan (Rencana)")
    structured_data: Optional[Dict[str, Any]] = None


# Note Signing
class NoteSignRequest(BaseModel):
    """Schema for signing a clinical note."""
    note_id: int
    signer_id: int


class NoteSignResponse(BaseModel):
    """Schema for note signing response."""
    note_id: int
    signed: bool
    signed_at: datetime
    signer_name: str
    signature_hash: str


# Note Versioning
class NoteVersionResponse(BaseModel):
    """Schema for note version history."""
    note_id: int
    version: int
    title: str
    note_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    author_name: str
    is_amendment: bool


# Patient Notes List
class PatientNotesListResponse(BaseModel):
    """Schema for patient clinical notes list."""
    patient_id: int
    notes: List[ClinicalNoteResponse]
    total: int

    # Filters applied
    note_type_filter: Optional[str] = None
    status_filter: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# Note Templates
class NoteTemplateResponse(BaseModel):
    """Schema for note template."""
    id: str
    name: str
    note_type: str
    description: Optional[str] = None
    template: Dict[str, Any]


# Auto-save Response
class AutoSaveResponse(BaseModel):
    """Schema for auto-save response."""
    note_id: Optional[int] = None  # None for new notes
    saved: bool
    saved_at: datetime
    status: str  # draft, pending, signed


# Attachment Schemas
class AttachmentCreate(BaseModel):
    """Schema for creating an attachment."""
    note_id: int
    filename: str
    file_type: str
    file_size: int
    file_path: str
    description: Optional[str] = None


class AttachmentResponse(BaseModel):
    """Schema for attachment response."""
    id: int
    note_id: int
    filename: str
    file_type: str
    file_size: int
    file_path: str
    description: Optional[str] = None
    uploaded_by: int
    created_at: datetime

    class Config:
        from_attributes = True
