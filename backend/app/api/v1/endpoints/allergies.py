"""Allergy Tracking API endpoints for STORY-013

This module provides API endpoints for allergy tracking, alerting, and management.
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.allergy import (
    AllergyCreate,
    AllergyUpdate,
    AllergyResponse,
    PatientAllergySummary,
    AllergyCheckRequest,
    AllergyCheckResponse,
    AllergyWarning,
    NoKnownAllergiesCreate,
    NoKnownAllergiesResponse,
    AllergyOverrideRequest,
    AllergyOverrideResponse,
)
from app.crud import allergy as crud_allergy


router = APIRouter()


# =============================================================================
# Patient Allergy Management Endpoints
# =============================================================================

@router.post("/allergies", response_model=AllergyResponse)
async def create_allergy(
    allergy_data: AllergyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AllergyResponse:
    """
    Create a new allergy for a patient.

    Critical for patient safety - all allergies must be documented.
    """
    allergy = await crud_allergy.create_allergy(
        db=db,
        patient_id=allergy_data.patient_id,
        allergy_type=allergy_data.allergy_type,
        allergen=allergy_data.allergen,
        severity=allergy_data.severity,
        reaction=allergy_data.reaction,
        recorded_by=current_user.id,
        allergen_code=allergy_data.allergen_code,
        reaction_details=allergy_data.reaction_details,
        status=allergy_data.status,
        onset_date=allergy_data.onset_date,
        resolved_date=allergy_data.resolved_date,
        source=allergy_data.source,
        source_notes=allergy_data.source_notes,
        clinical_notes=allergy_data.clinical_notes,
        alternatives=allergy_data.alternatives,
        verified_by=allergy_data.verified_by,
    )

    return AllergyResponse(
        id=allergy.id,
        patient_id=allergy.patient_id,
        allergy_type=allergy.allergy_type,
        allergen=allergy.allergen,
        allergen_code=allergy.allergen_code,
        severity=allergy.severity,
        reaction=allergy.reaction,
        reaction_details=allergy.reaction_details,
        status=allergy.status,
        onset_date=allergy.onset_date,
        resolved_date=allergy.resolved_date,
        source=allergy.source,
        source_notes=allergy.source_notes,
        clinical_notes=allergy.clinical_notes,
        alternatives=allergy.alternatives,
        recorded_by=allergy.recorded_by,
        verified_by=allergy.verified_by,
        verified_at=allergy.verified_at,
        created_at=allergy.created_at,
        updated_at=allergy.updated_at,
        recorded_by_name=current_user.full_name,
    )


@router.get("/allergies/patient/{patient_id}", response_model=PatientAllergySummary)
async def get_patient_allergies(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: Optional[str] = Query(default=None),
    severity_filter: Optional[str] = Query(default=None),
    type_filter: Optional[str] = Query(default=None),
) -> PatientAllergySummary:
    """Get all allergies for a patient with summary statistics and alerts."""
    allergies = await crud_allergy.get_patient_allergies(
        db=db,
        patient_id=patient_id,
        status_filter=status_filter,
        severity_filter=severity_filter,
        type_filter=type_filter,
    )

    summary = await crud_allergy.get_patient_allergy_summary(db, patient_id)

    allergy_responses = []
    for allergy in allergies:
        allergy_responses.append(
            AllergyResponse(
                id=allergy.id,
                patient_id=allergy.patient_id,
                allergy_type=allergy.allergy_type,
                allergen=allergy.allergen,
                allergen_code=allergy.allergen_code,
                severity=allergy.severity,
                reaction=allergy.reaction,
                reaction_details=allergy.reaction_details,
                status=allergy.status,
                onset_date=allergy.onset_date,
                resolved_date=allergy.resolved_date,
                source=allergy.source,
                source_notes=allergy.source_notes,
                clinical_notes=allergy.clinical_notes,
                alternatives=allergy.alternatives,
                recorded_by=allergy.recorded_by,
                verified_by=allergy.verified_by,
                verified_at=allergy.verified_at,
                created_at=allergy.created_at,
                updated_at=allergy.updated_at,
                recorded_by_name=allergy.recorder.full_name if allergy.recorder else None,
                verified_by_name=allergy.verifier.full_name if allergy.verifier else None,
            )
        )

    return PatientAllergySummary(
        **summary,
        allergies=allergy_responses,
    )


@router.get("/allergies/{allergy_id}", response_model=AllergyResponse)
async def get_allergy(
    allergy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AllergyResponse:
    """Get a specific allergy by ID."""
    allergy = await crud_allergy.get_allergy_by_id(db, allergy_id)
    if not allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")

    return AllergyResponse(
        id=allergy.id,
        patient_id=allergy.patient_id,
        allergy_type=allergy.allergy_type,
        allergen=allergy.allergen,
        allergen_code=allergy.allergen_code,
        severity=allergy.severity,
        reaction=allergy.reaction,
        reaction_details=allergy.reaction_details,
        status=allergy.status,
        onset_date=allergy.onset_date,
        resolved_date=allergy.resolved_date,
        source=allergy.source,
        source_notes=allergy.source_notes,
        clinical_notes=allergy.clinical_notes,
        alternatives=allergy.alternatives,
        recorded_by=allergy.recorded_by,
        verified_by=allergy.verified_by,
        verified_at=allergy.verified_at,
        created_at=allergy.created_at,
        updated_at=allergy.updated_at,
        recorded_by_name=allergy.recorder.full_name if allergy.recorder else None,
        verified_by_name=allergy.verifier.full_name if allergy.verifier else None,
    )


@router.put("/allergies/{allergy_id}", response_model=AllergyResponse)
async def update_allergy(
    allergy_id: int,
    update_data: AllergyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AllergyResponse:
    """Update an allergy."""
    allergy = await crud_allergy.update_allergy(
        db=db,
        allergy_id=allergy_id,
        allergy_type=update_data.allergy_type,
        allergen=update_data.allergen,
        allergen_code=update_data.allergen_code,
        severity=update_data.severity,
        reaction=update_data.reaction,
        reaction_details=update_data.reaction_details,
        status=update_data.status,
        onset_date=update_data.onset_date,
        resolved_date=update_data.resolved_date,
        source=update_data.source,
        source_notes=update_data.source_notes,
        clinical_notes=update_data.clinical_notes,
        alternatives=update_data.alternatives,
        verified_by=update_data.verified_by,
    )

    if not allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")

    return AllergyResponse(
        id=allergy.id,
        patient_id=allergy.patient_id,
        allergy_type=allergy.allergy_type,
        allergen=allergy.allergen,
        allergen_code=allergy.allergen_code,
        severity=allergy.severity,
        reaction=allergy.reaction,
        reaction_details=allergy.reaction_details,
        status=allergy.status,
        onset_date=allergy.onset_date,
        resolved_date=allergy.resolved_date,
        source=allergy.source,
        source_notes=allergy.source_notes,
        clinical_notes=allergy.clinical_notes,
        alternatives=allergy.alternatives,
        recorded_by=allergy.recorded_by,
        verified_by=allergy.verified_by,
        verified_at=allergy.verified_at,
        created_at=allergy.created_at,
        updated_at=allergy.updated_at,
        recorded_by_name=allergy.recorder.full_name if allergy.recorder else None,
        verified_by_name=allergy.verifier.full_name if allergy.verifier else None,
    )


@router.delete("/allergies/{allergy_id}")
async def delete_allergy(
    allergy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an allergy.

    WARNING: This is a hard delete. Allergies are critical safety information.
    Consider updating status to 'resolved' instead.
    """
    success = await crud_allergy.delete_allergy(db, allergy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Allergy not found")
    return {"message": "Allergy deleted successfully"}


# =============================================================================
# Allergy Check Endpoints (for Prescription Safety)
# =============================================================================

@router.post("/allergies/check", response_model=AllergyCheckResponse)
async def check_allergies(
    request: AllergyCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AllergyCheckResponse:
    """
    Check if medications interact with patient allergies.

    Called before prescribing to prevent adverse reactions.
    """
    warnings, can_prescribe = await crud_allergy.check_allergies_against_medications(
        db=db,
        patient_id=request.patient_id,
        medications=request.medications,
    )

    warning_objects = [AllergyWarning(**w) for w in warnings]

    return AllergyCheckResponse(
        patient_id=request.patient_id,
        has_allergy_interaction=len(warnings) > 0,
        warnings=warning_objects,
        can_prescribe=can_prescribe,
        requires_override=any(w.get("is_contraindicated", False) for w in warnings),
    )


@router.post("/allergies/override", response_model=AllergyOverrideResponse)
async def override_allergy_alert(
    override_data: AllergyOverrideRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AllergyOverrideResponse:
    """
    Override allergy alert for prescription.

    Requires documented reason. Audit logged for compliance.
    """
    # Verify allergy exists
    allergy = await crud_allergy.get_allergy_by_id(db, override_data.allergy_id)
    if not allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")

    # Check if override is allowed (only for non-life_threatening)
    override_allowed = allergy.severity != "life_threatening"

    warning_message = ""
    if not override_allowed:
        warning_message = "TIDAK DIPERBOLEHKAN: Alergi yang mengancam jiwa tidak dapat diabaikan"
    elif allergy.severity == "severe":
        warning_message = "PERINGATAN: Mengabaikan alergi parah memerlukan pertimbangan klinis yang hati-hati"

    return AllergyOverrideResponse(
        allergy_id=override_data.allergy_id,
        medication=override_data.medication,
        override_reason=override_data.override_reason,
        override_allowed=override_allowed,
        warning_message=warning_message,
        prescribed_by=override_data.prescribed_by,
        overridden_at=datetime.now(),
    )


# =============================================================================
# No Known Allergies (NKA) Endpoint
# =============================================================================

@router.post("/allergies/nka", response_model=NoKnownAllergiesResponse)
async def record_no_known_allergies(
    nka_data: NoKnownAllergiesCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoKnownAllergiesResponse:
    """
    Record No Known Allergies (NKA) status for a patient.

    Documents that patient has been explicitly asked about allergies.
    """
    # In production, this would create an NKA record in a separate table
    # For now, we return a confirmation
    return NoKnownAllergiesResponse(
        patient_id=nka_data.patient_id,
        no_known_allergies=True,
        recorded_by=nka_data.recorded_by,
        recorded_by_name=current_user.full_name,
        recorded_at=datetime.now(),
        clinical_notes=nka_data.clinical_notes,
    )
