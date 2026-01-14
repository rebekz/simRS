"""Clinical Notes CRUD operations for STORY-015: Clinical Notes (SOAP)

This module provides CRUD operations for clinical documentation with
versioning, auto-save, and audit trail support.
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import hashlib
import uuid

from app.models.clinical_note import (
    ClinicalNote,
    ClinicalNoteSignature,
    ClinicalNoteAttachment,
)
from app.models.patient import Patient
from app.models.encounter import Encounter


async def get_note_by_id(
    db: AsyncSession,
    note_id: int,
    include_deleted: bool = False,
) -> Optional[ClinicalNote]:
    """Get clinical note by ID."""
    stmt = select(ClinicalNote).where(ClinicalNote.id == note_id)

    if not include_deleted:
        stmt = stmt.where(ClinicalNote.deleted_at.is_(None))

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_patient_notes(
    db: AsyncSession,
    patient_id: int,
    note_type_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[List[ClinicalNote], int]:
    """
    Get clinical notes for a patient with optional filters.

    Returns tuple of (notes, total_count).
    """
    # Build base query
    stmt = select(ClinicalNote).where(
        and_(
            ClinicalNote.patient_id == patient_id,
            ClinicalNote.deleted_at.is_(None),
        )
    )

    # Apply filters
    if note_type_filter:
        stmt = stmt.where(ClinicalNote.note_type == note_type_filter)

    if status_filter:
        stmt = stmt.where(ClinicalNote.status == status_filter)

    if date_from:
        stmt = stmt.where(ClinicalNote.note_date >= date_from)

    if date_to:
        stmt = stmt.where(ClinicalNote.note_date <= date_to)

    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Get paginated results
    stmt = stmt.order_by(desc(ClinicalNote.note_date), desc(ClinicalNote.created_at))
    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    notes = result.scalars().all()

    return list(notes), total


async def create_note(
    db: AsyncSession,
    patient_id: int,
    note_type: str,
    title: str,
    note_date: datetime,
    author_id: int,
    encounter_id: Optional[int] = None,
    subjective: Optional[str] = None,
    objective: Optional[str] = None,
    assessment: Optional[str] = None,
    plan: Optional[str] = None,
    content: Optional[str] = None,
    structured_data: Optional[Dict[str, Any]] = None,
) -> ClinicalNote:
    """Create a new clinical note."""
    # Verify patient exists
    patient_stmt = select(Patient).where(Patient.id == patient_id)
    patient_result = await db.execute(patient_stmt)
    if not patient_result.scalar_one_or_none():
        raise ValueError(f"Patient with ID {patient_id} not found")

    # Verify encounter exists if provided
    if encounter_id:
        encounter_stmt = select(Encounter).where(Encounter.id == encounter_id)
        encounter_result = await db.execute(encounter_stmt)
        if not encounter_result.scalar_one_or_none():
            raise ValueError(f"Encounter with ID {encounter_id} not found")

    note = ClinicalNote(
        patient_id=patient_id,
        encounter_id=encounter_id,
        note_type=note_type,
        title=title,
        note_date=note_date,
        author_id=author_id,
        subjective=subjective,
        objective=objective,
        assessment=assessment,
        plan=plan,
        content=content,
        structured_data=structured_data,
        status="draft",
        version=1,
    )

    db.add(note)
    await db.commit()
    await db.refresh(note)

    return note


async def update_note(
    db: AsyncSession,
    note_id: int,
    title: Optional[str] = None,
    note_date: Optional[datetime] = None,
    subjective: Optional[str] = None,
    objective: Optional[str] = None,
    assessment: Optional[str] = None,
    plan: Optional[str] = None,
    content: Optional[str] = None,
    structured_data: Optional[Dict[str, Any]] = None,
    status: Optional[str] = None,
) -> Optional[ClinicalNote]:
    """
    Update a clinical note.

    Note: Signed notes cannot be updated directly. Must create an amendment.
    """
    note = await get_note_by_id(db, note_id)
    if not note:
        return None

    # Prevent modification of signed notes
    if note.status == "signed":
        raise ValueError("Cannot update signed note. Create an amendment instead.")

    if title is not None:
        note.title = title
    if note_date is not None:
        note.note_date = note_date
    if subjective is not None:
        note.subjective = subjective
    if objective is not None:
        note.objective = objective
    if assessment is not None:
        note.assessment = assessment
    if plan is not None:
        note.plan = plan
    if content is not None:
        note.content = content
    if structured_data is not None:
        note.structured_data = structured_data
    if status is not None:
        note.status = status

    note.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(note)

    return note


async def auto_save_note(
    db: AsyncSession,
    patient_id: int,
    note_type: str,
    title: str,
    note_date: datetime,
    author_id: int,
    encounter_id: Optional[int] = None,
    subjective: Optional[str] = None,
    objective: Optional[str] = None,
    assessment: Optional[str] = None,
    plan: Optional[str] = None,
    content: Optional[str] = None,
    structured_data: Optional[Dict[str, Any]] = None,
    note_id: Optional[int] = None,
) -> tuple[ClinicalNote, bool]:
    """
    Auto-save a clinical note (create or update).

    Returns tuple of (note, is_new).
    """
    if note_id:
        # Try to update existing note
        note = await get_note_by_id(db, note_id)
        if note and note.status == "draft" and note.author_id == author_id:
            # Update existing draft
            if subjective is not None:
                note.subjective = subjective
            if objective is not None:
                note.objective = objective
            if assessment is not None:
                note.assessment = assessment
            if plan is not None:
                note.plan = plan
            if content is not None:
                note.content = content
            if structured_data is not None:
                note.structured_data = structured_data

            note.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(note)
            return note, False

    # Create new note
    note = await create_note(
        db=db,
        patient_id=patient_id,
        note_type=note_type,
        title=title,
        note_date=note_date,
        author_id=author_id,
        encounter_id=encounter_id,
        subjective=subjective,
        objective=objective,
        assessment=assessment,
        plan=plan,
        content=content,
        structured_data=structured_data,
    )
    return note, True


async def sign_note(
    db: AsyncSession,
    note_id: int,
    signer_id: int,
    signer_name: str,
    signer_role: str,
    signature_ip: str,
    signature_user_agent: Optional[str] = None,
) -> ClinicalNote:
    """
    Sign a clinical note with digital signature.

    Creates signature record and updates note status.
    """
    note = await get_note_by_id(db, note_id)
    if not note:
        raise ValueError(f"Note with ID {note_id} not found")

    if note.status == "signed":
        raise ValueError("Note is already signed")

    # Create signature hash (cryptographic hash of note content)
    note_content = f"{note.subjective}|{note.objective}|{note.assessment}|{note.plan}|{note.content}"
    signature_hash = hashlib.sha256(note_content.encode()).hexdigest()

    # Create signature record
    signature = ClinicalNoteSignature(
        note_id=note_id,
        signer_id=signer_id,
        signer_name=signer_name,
        signer_role=signer_role,
        signature_hash=signature_hash,
        signature_ip=signature_ip,
        signature_user_agent=signature_user_agent,
    )
    db.add(signature)

    # Update note status
    note.status = "signed"
    note.signed_by_id = signer_id
    note.signed_at = datetime.now(timezone.utc)
    note.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(note)

    return note


async def create_amendment(
    db: AsyncSession,
    parent_note_id: int,
    author_id: int,
    amend_reason: str,
    subjective: Optional[str] = None,
    objective: Optional[str] = None,
    assessment: Optional[str] = None,
    plan: Optional[str] = None,
    content: Optional[str] = None,
) -> ClinicalNote:
    """
    Create an amendment to a signed note.

    Original note remains unchanged. Amendment references parent.
    """
    parent_note = await get_note_by_id(db, parent_note_id)
    if not parent_note:
        raise ValueError(f"Parent note with ID {parent_note_id} not found")

    if parent_note.status != "signed":
        raise ValueError("Can only amend signed notes")

    # Create amendment
    amendment = ClinicalNote(
        patient_id=parent_note.patient_id,
        encounter_id=parent_note.encounter_id,
        note_type=parent_note.note_type,
        title=f"{parent_note.title} (AMENDEMEN)",
        note_date=datetime.now(timezone.utc),
        author_id=author_id,
        subjective=subjective or parent_note.subjective,
        objective=objective or parent_note.objective,
        assessment=assessment or parent_note.assessment,
        plan=plan or parent_note.plan,
        content=content or parent_note.content,
        structured_data=parent_note.structured_data,
        status="draft",
        version=parent_note.version + 1,
        parent_note_id=parent_note_id,
        is_amendment=True,
    )

    # Add amendment reason to structured_data
    if not amendment.structured_data:
        amendment.structured_data = {}
    amendment.structured_data["amendment_reason"] = amend_reason

    db.add(amendment)
    await db.commit()
    await db.refresh(amendment)

    # Update parent note status
    parent_note.status = "amended"
    await db.commit()

    return amendment


async def delete_note(
    db: AsyncSession,
    note_id: int,
    deleted_by: int,
) -> bool:
    """
    Soft delete a clinical note.

    Sets deleted_at timestamp. Note remains in database for audit.
    """
    note = await get_note_by_id(db, note_id)
    if not note:
        return False

    # Cannot delete signed notes
    if note.status == "signed":
        raise ValueError("Cannot delete signed note")

    note.deleted_at = datetime.now(timezone.utc)
    await db.commit()

    return True


async def get_note_versions(
    db: AsyncSession,
    note_id: int,
) -> List[ClinicalNote]:
    """
    Get all versions of a note (including amendments).

    Returns list ordered by version (newest first).
    """
    # First get the original note
    original_note = await get_note_by_id(db, note_id)
    if not original_note:
        return []

    # If this is an amendment, get the parent instead
    if original_note.is_amendment and original_note.parent_note_id:
        note_id = original_note.parent_note_id
        original_note = await get_note_by_id(db, note_id)

    versions = [original_note]

    # Get all amendments
    stmt = select(ClinicalNote).where(
        and_(
            ClinicalNote.parent_note_id == note_id,
            ClinicalNote.deleted_at.is_(None),
        )
    ).order_by(desc(ClinicalNote.version))

    result = await db.execute(stmt)
    amendments = result.scalars().all()
    versions.extend(amendments)

    return versions
