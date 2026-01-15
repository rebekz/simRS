"""Clinical Notes API endpoints for STORY-015

This module provides API endpoints for clinical documentation with SOAP notes,
auto-save, digital signatures, and version control.
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.clinical_note import (
    ClinicalNoteCreate,
    ClinicalNoteUpdate,
    ClinicalNoteResponse,
    SOAPNoteCreate,
    PatientNotesListResponse,
    NoteSignRequest,
    NoteSignResponse,
    NoteVersionResponse,
    AutoSaveResponse,
)
from app.crud import clinical_note as crud


router = APIRouter()


# =============================================================================
# Clinical Note Management Endpoints
# =============================================================================

@router.post("/clinical-notes", response_model=ClinicalNoteResponse)
async def create_clinical_note(
    note_data: ClinicalNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClinicalNoteResponse:
    """Create a new clinical note."""
    note = await crud.create_note(
        db=db,
        patient_id=note_data.patient_id,
        note_type=note_data.note_type,
        title=note_data.title,
        note_date=note_data.note_date,
        author_id=current_user.id,
        encounter_id=note_data.encounter_id,
        subjective=note_data.subjective,
        objective=note_data.objective,
        assessment=note_data.assessment,
        plan=note_data.plan,
        content=note_data.content,
        structured_data=note_data.structured_data,
    )

    return ClinicalNoteResponse(
        id=note.id,
        uuid=str(note.uuid),
        patient_id=note.patient_id,
        encounter_id=note.encounter_id,
        note_type=note.note_type,
        title=note.title,
        note_date=note.note_date,
        subjective=note.subjective,
        objective=note.objective,
        assessment=note.assessment,
        plan=note.plan,
        content=note.content,
        structured_data=note.structured_data,
        status=note.status,
        version=note.version,
        is_amendment=note.is_amendment,
        parent_note_id=note.parent_note_id,
        author_id=note.author_id,
        signed_by_id=note.signed_by_id,
        signed_at=note.signed_at,
        cosigned_by_id=note.cosigned_by_id,
        cosigned_at=note.cosigned_at,
        created_at=note.created_at,
        updated_at=note.updated_at,
        author_name=current_user.full_name,
    )


@router.post("/clinical-notes/soap", response_model=ClinicalNoteResponse)
async def create_soap_note(
    note_data: SOAPNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClinicalNoteResponse:
    """Create a new SOAP note."""
    note = await crud.create_note(
        db=db,
        patient_id=note_data.patient_id,
        note_type="soap",
        title=note_data.title,
        note_date=note_data.note_date,
        author_id=current_user.id,
        encounter_id=note_data.encounter_id,
        subjective=note_data.subjective,
        objective=note_data.objective,
        assessment=note_data.assessment,
        plan=note_data.plan,
        structured_data=note_data.structured_data,
    )

    return ClinicalNoteResponse(
        id=note.id,
        uuid=str(note.uuid),
        patient_id=note.patient_id,
        encounter_id=note.encounter_id,
        note_type=note.note_type,
        title=note.title,
        note_date=note.note_date,
        subjective=note.subjective,
        objective=note.objective,
        assessment=note.assessment,
        plan=note.plan,
        structured_data=note.structured_data,
        status=note.status,
        version=note.version,
        is_amendment=note.is_amendment,
        parent_note_id=note.parent_note_id,
        author_id=note.author_id,
        signed_by_id=note.signed_by_id,
        signed_at=note.signed_at,
        cosigned_by_id=note.cosigned_by_id,
        cosigned_at=note.cosigned_at,
        created_at=note.created_at,
        updated_at=note.updated_at,
        author_name=current_user.full_name,
    )


@router.get("/clinical-notes/patient/{patient_id}", response_model=PatientNotesListResponse)
async def get_patient_notes(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    note_type_filter: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> PatientNotesListResponse:
    """Get clinical notes for a patient with filters and pagination."""
    notes, total = await crud.get_patient_notes(
        db=db,
        patient_id=patient_id,
        note_type_filter=note_type_filter,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )

    note_responses = []
    for note in notes:
        note_responses.append(
            ClinicalNoteResponse(
                id=note.id,
                uuid=str(note.uuid),
                patient_id=note.patient_id,
                encounter_id=note.encounter_id,
                note_type=note.note_type,
                title=note.title,
                note_date=note.note_date,
                subjective=note.subjective,
                objective=note.objective,
                assessment=note.assessment,
                plan=note.plan,
                content=note.content,
                structured_data=note.structured_data,
                status=note.status,
                version=note.version,
                is_amendment=note.is_amendment,
                parent_note_id=note.parent_note_id,
                author_id=note.author_id,
                signed_by_id=note.signed_by_id,
                signed_at=note.signed_at,
                cosigned_by_id=note.cosigned_by_id,
                cosigned_at=note.cosigned_at,
                created_at=note.created_at,
                updated_at=note.updated_at,
                author_name=note.author.full_name if note.author else None,
                signer_name=note.signer.full_name if note.signer else None,
            )
        )

    return PatientNotesListResponse(
        patient_id=patient_id,
        notes=note_responses,
        total=total,
        note_type_filter=note_type_filter,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/clinical-notes/{note_id}", response_model=ClinicalNoteResponse)
async def get_clinical_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClinicalNoteResponse:
    """Get a specific clinical note by ID."""
    note = await crud.get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Clinical note not found")

    return ClinicalNoteResponse(
        id=note.id,
        uuid=str(note.uuid),
        patient_id=note.patient_id,
        encounter_id=note.encounter_id,
        note_type=note.note_type,
        title=note.title,
        note_date=note.note_date,
        subjective=note.subjective,
        objective=note.objective,
        assessment=note.assessment,
        plan=note.plan,
        content=note.content,
        structured_data=note.structured_data,
        status=note.status,
        version=note.version,
        is_amendment=note.is_amendment,
        parent_note_id=note.parent_note_id,
        author_id=note.author_id,
        signed_by_id=note.signed_by_id,
        signed_at=note.signed_at,
        cosigned_by_id=note.cosigned_by_id,
        cosigned_at=note.cosigned_at,
        created_at=note.created_at,
        updated_at=note.updated_at,
        author_name=note.author.full_name if note.author else None,
        signer_name=note.signer.full_name if note.signer else None,
    )


@router.put("/clinical-notes/{note_id}", response_model=ClinicalNoteResponse)
async def update_clinical_note(
    note_id: int,
    update_data: ClinicalNoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClinicalNoteResponse:
    """Update a clinical note (draft status only)."""
    try:
        note = await crud.update_note(
            db=db,
            note_id=note_id,
            title=update_data.title,
            note_date=update_data.note_date,
            subjective=update_data.subjective,
            objective=update_data.objective,
            assessment=update_data.assessment,
            plan=update_data.plan,
            content=update_data.content,
            structured_data=update_data.structured_data,
            status=update_data.status,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not note:
        raise HTTPException(status_code=404, detail="Clinical note not found")

    return ClinicalNoteResponse(
        id=note.id,
        uuid=str(note.uuid),
        patient_id=note.patient_id,
        encounter_id=note.encounter_id,
        note_type=note.note_type,
        title=note.title,
        note_date=note.note_date,
        subjective=note.subjective,
        objective=note.objective,
        assessment=note.assessment,
        plan=note.plan,
        content=note.content,
        structured_data=note.structured_data,
        status=note.status,
        version=note.version,
        is_amendment=note.is_amendment,
        parent_note_id=note.parent_note_id,
        author_id=note.author_id,
        signed_by_id=note.signed_by_id,
        signed_at=note.signed_at,
        cosigned_by_id=note.cosigned_by_id,
        cosigned_at=note.cosigned_at,
        created_at=note.created_at,
        updated_at=note.updated_at,
        author_name=note.author.full_name if note.author else None,
        signer_name=note.signer.full_name if note.signer else None,
    )


@router.delete("/clinical-notes/{note_id}")
async def delete_clinical_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete a clinical note (draft status only)."""
    try:
        success = await crud.delete_note(db, note_id, deleted_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not success:
        raise HTTPException(status_code=404, detail="Clinical note not found")

    return {"message": "Clinical note deleted successfully"}


# =============================================================================
# Auto-save Endpoint
# =============================================================================

@router.post("/clinical-notes/autosave", response_model=AutoSaveResponse)
async def autosave_note(
    note_data: ClinicalNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    note_id: Optional[int] = Query(default=None),
) -> AutoSaveResponse:
    """
    Auto-save a clinical note.

    Creates new note or updates existing draft note.
    """
    note, is_new = await crud.auto_save_note(
        db=db,
        patient_id=note_data.patient_id,
        note_type=note_data.note_type,
        title=note_data.title,
        note_date=note_data.note_date,
        author_id=current_user.id,
        encounter_id=note_data.encounter_id,
        subjective=note_data.subjective,
        objective=note_data.objective,
        assessment=note_data.assessment,
        plan=note_data.plan,
        content=note_data.content,
        structured_data=note_data.structured_data,
        note_id=note_id,
    )

    return AutoSaveResponse(
        note_id=note.id,
        saved=True,
        saved_at=note.updated_at,
        status=note.status,
    )


# =============================================================================
# Digital Signature Endpoints
# =============================================================================

@router.post("/clinical-notes/{note_id}/sign", response_model=NoteSignResponse)
async def sign_clinical_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None,
) -> NoteSignResponse:
    """
    Sign a clinical note with digital signature.

    Creates audit trail and marks note as signed.
    """
    # Get client IP and user agent
    client_ip = request.client.host if request else "unknown"
    user_agent = request.headers.get("user-agent")

    try:
        note = await crud.sign_note(
            db=db,
            note_id=note_id,
            signer_id=current_user.id,
            signer_name=current_user.full_name,
            signer_role=current_user.role.value if hasattr(current_user, 'role') else "doctor",
            signature_ip=client_ip,
            signature_user_agent=user_agent,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return NoteSignResponse(
        note_id=note.id,
        signed=True,
        signed_at=note.signed_at or datetime.now(),
        signer_name=current_user.full_name,
        signature_hash=f"sha256:{note.signed_at.isoformat()}",
    )


# =============================================================================
# Version Control Endpoints
# =============================================================================

@router.get("/clinical-notes/{note_id}/versions", response_model=List[NoteVersionResponse])
async def get_note_versions(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[NoteVersionResponse]:
    """Get all versions of a note (including amendments)."""
    versions = await crud.get_note_versions(db, note_id)

    return [
        NoteVersionResponse(
            note_id=v.id,
            version=v.version,
            title=v.title,
            note_type=v.note_type,
            status=v.status,
            created_at=v.created_at,
            updated_at=v.updated_at,
            author_name=v.author.full_name if v.author else "Unknown",
            is_amendment=v.is_amendment,
        )
        for v in versions
    ]


@router.post("/clinical-notes/{note_id}/amend", response_model=ClinicalNoteResponse)
async def amend_note(
    note_id: int,
    amend_reason: str = Query(..., min_length=10, description="Reason for amendment"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    subjective: Optional[str] = None,
    objective: Optional[str] = None,
    assessment: Optional[str] = None,
    plan: Optional[str] = None,
    content: Optional[str] = None,
) -> ClinicalNoteResponse:
    """
    Create an amendment to a signed note.

    Original note remains unchanged. Amendment references parent.
    """
    try:
        amendment = await crud.create_amendment(
            db=db,
            parent_note_id=note_id,
            author_id=current_user.id,
            amend_reason=amend_reason,
            subjective=subjective,
            objective=objective,
            assessment=assessment,
            plan=plan,
            content=content,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ClinicalNoteResponse(
        id=amendment.id,
        uuid=str(amendment.uuid),
        patient_id=amendment.patient_id,
        encounter_id=amendment.encounter_id,
        note_type=amendment.note_type,
        title=amendment.title,
        note_date=amendment.note_date,
        subjective=amendment.subjective,
        objective=amendment.objective,
        assessment=amendment.assessment,
        plan=amendment.plan,
        content=amendment.content,
        structured_data=amendment.structured_data,
        status=amendment.status,
        version=amendment.version,
        is_amendment=amendment.is_amendment,
        parent_note_id=amendment.parent_note_id,
        author_id=amendment.author_id,
        signed_by_id=amendment.signed_by_id,
        signed_at=amendment.signed_at,
        cosigned_by_id=amendment.cosigned_by_id,
        cosigned_at=amendment.cosigned_at,
        created_at=amendment.created_at,
        updated_at=amendment.updated_at,
        author_name=current_user.full_name,
    )
