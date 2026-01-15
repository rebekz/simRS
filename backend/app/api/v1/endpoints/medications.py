"""Medication List API endpoints for STORY-014

This module provides API endpoints for:
- Patient medication tracking
- Drug interaction checking
- Medication reconciliation
- Duplicate therapy warnings
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.medication import (
    MedicationCreate, MedicationUpdate, MedicationResponse,
    MedicationListResponse, MedicationStatus,
    DrugInteractionCheckRequest, DrugInteractionCheckResponse,
    MedicationReconciliationRequest, MedicationReconciliationResponse,
    MedicationHistoryResponse,
    DuplicateTherapyWarning,
)
from app.crud import medication as crud_medication


router = APIRouter()


# =============================================================================
# Patient Medication Endpoints
# =============================================================================

@router.get("/patients/{patient_id}/medications", response_model=MedicationListResponse)
async def get_patient_medications(
    patient_id: int,
    include_past: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MedicationListResponse:
    """Get all medications for a patient (current and past)"""
    # Get current medications
    current_meds, current_count = await crud_medication.get_patient_medications(
        db=db,
        patient_id=patient_id,
        status=MedicationStatus.ACTIVE,
        include_past=False,
    )

    # Get past medications if requested
    past_meds = []
    past_count = 0
    if include_past:
        past_meds, past_count = await crud_medication.get_patient_medications(
            db=db,
            patient_id=patient_id,
            status=None,
            include_past=True,
        )
        # Filter out current medications from past list
        past_meds = [m for m in past_meds if m.status != MedicationStatus.ACTIVE]
        past_count = len(past_meds)

    # Build response
    current_responses = []
    for med in current_meds:
        current_responses.append(MedicationResponse(
            id=med.id,
            patient_id=med.patient_id,
            encounter_id=med.encounter_id,
            drug_id=med.drug_id,
            drug_name=med.drug_name,
            generic_name=med.generic_name,
            dosage=med.dosage,
            dose_unit=med.dose_unit,
            frequency=med.frequency,
            route=med.route,
            indication=med.indication,
            prescriber_id=med.prescriber_id,
            prescriber_name=med.prescriber.full_name if med.prescriber else None,
            prescription_date=med.prescription_date,
            start_date=med.start_date,
            end_date=med.end_date,
            status=med.status,
            notes=med.notes,
            batch_number=med.batch_number,
            manufacturer=med.manufacturer,
            discontinuation_reason=med.discontinuation_reason,
            bpjs_code=med.drug.bpjs_code if med.drug else None,
            is_narcotic=med.drug.is_narcotic if med.drug else False,
            is_antibiotic=med.drug.is_antibiotic if med.drug else False,
            requires_prescription=med.drug.requires_prescription if med.drug else True,
            created_at=med.created_at,
            updated_at=med.updated_at,
        ))

    past_responses = []
    for med in past_meds:
        past_responses.append(MedicationResponse(
            id=med.id,
            patient_id=med.patient_id,
            encounter_id=med.encounter_id,
            drug_id=med.drug_id,
            drug_name=med.drug_name,
            generic_name=med.generic_name,
            dosage=med.dosage,
            dose_unit=med.dose_unit,
            frequency=med.frequency,
            route=med.route,
            indication=med.indication,
            prescriber_id=med.prescriber_id,
            prescriber_name=med.prescriber.full_name if med.prescriber else None,
            prescription_date=med.prescription_date,
            start_date=med.start_date,
            end_date=med.end_date,
            status=med.status,
            notes=med.notes,
            batch_number=med.batch_number,
            manufacturer=med.manufacturer,
            discontinuation_reason=med.discontinuation_reason,
            bpjs_code=med.drug.bpjs_code if med.drug else None,
            is_narcotic=med.drug.is_narcotic if med.drug else False,
            is_antibiotic=med.drug.is_antibiotic if med.drug else False,
            requires_prescription=med.drug.requires_prescription if med.drug else True,
            created_at=med.created_at,
            updated_at=med.updated_at,
        ))

    return MedicationListResponse(
        patient_id=patient_id,
        current_medications=current_responses,
        past_medications=past_responses,
        total_current=current_count,
        total_past=past_count,
    )


@router.post("/patients/{patient_id}/medications", response_model=MedicationResponse)
async def create_patient_medication(
    patient_id: int,
    medication_data: MedicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MedicationResponse:
    """Create a new medication record for a patient"""
    medication = await crud_medication.create_patient_medication(
        db=db,
        medication_data=medication_data,
        patient_id=patient_id,
        created_by=current_user.id,
    )

    return MedicationResponse(
        id=medication.id,
        patient_id=medication.patient_id,
        encounter_id=medication.encounter_id,
        drug_id=medication.drug_id,
        drug_name=medication.drug_name,
        generic_name=medication.generic_name,
        dosage=medication.dosage,
        dose_unit=medication.dose_unit,
        frequency=medication.frequency,
        route=medication.route,
        indication=medication.indication,
        prescriber_id=medication.prescriber_id,
        prescriber_name=medication.prescriber.full_name if medication.prescriber else None,
        prescription_date=medication.prescription_date,
        start_date=medication.start_date,
        end_date=medication.end_date,
        status=medication.status,
        notes=medication.notes,
        batch_number=medication.batch_number,
        manufacturer=medication.manufacturer,
        discontinuation_reason=None,
        bpjs_code=medication.drug.bpjs_code if medication.drug else None,
        is_narcotic=medication.drug.is_narcotic if medication.drug else False,
        is_antibiotic=medication.drug.is_antibiotic if medication.drug else False,
        requires_prescription=medication.drug.requires_prescription if medication.drug else True,
        created_at=medication.created_at,
        updated_at=medication.updated_at,
    )


@router.get("/patients/{patient_id}/medications/history", response_model=MedicationHistoryResponse)
async def get_medication_history(
    patient_id: int,
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MedicationHistoryResponse:
    """Get complete medication history for a patient"""
    from datetime import datetime

    dt_from = datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None
    dt_to = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None

    medications, total_count = await crud_medication.get_medication_history(
        db=db,
        patient_id=patient_id,
        date_from=dt_from,
        date_to=dt_to,
    )

    medication_responses = []
    for med in medications:
        medication_responses.append(MedicationResponse(
            id=med.id,
            patient_id=med.patient_id,
            encounter_id=med.encounter_id,
            drug_id=med.drug_id,
            drug_name=med.drug_name,
            generic_name=med.generic_name,
            dosage=med.dosage,
            dose_unit=med.dose_unit,
            frequency=med.frequency,
            route=med.route,
            indication=med.indication,
            prescriber_id=med.prescriber_id,
            prescriber_name=med.prescriber.full_name if med.prescriber else None,
            prescription_date=med.prescription_date,
            start_date=med.start_date,
            end_date=med.end_date,
            status=med.status,
            notes=med.notes,
            batch_number=med.batch_number,
            manufacturer=med.manufacturer,
            discontinuation_reason=med.discontinuation_reason,
            bpjs_code=med.drug.bpjs_code if med.drug else None,
            is_narcotic=med.drug.is_narcotic if med.drug else False,
            is_antibiotic=med.drug.is_antibiotic if med.drug else False,
            requires_prescription=med.drug.requires_prescription if med.drug else True,
            created_at=med.created_at,
            updated_at=med.updated_at,
        ))

    return MedicationHistoryResponse(
        patient_id=patient_id,
        medications=medication_responses,
        total_count=total_count,
        date_range={"from": dt_from, "to": dt_to} if dt_from or dt_to else None,
    )


@router.put("/medications/{medication_id}", response_model=MedicationResponse)
async def update_medication(
    medication_id: int,
    medication_data: MedicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MedicationResponse:
    """Update medication information"""
    medication = await crud_medication.update_patient_medication(
        db=db,
        medication_id=medication_id,
        medication_data=medication_data,
    )
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    return MedicationResponse(
        id=medication.id,
        patient_id=medication.patient_id,
        encounter_id=medication.encounter_id,
        drug_id=medication.drug_id,
        drug_name=medication.drug_name,
        generic_name=medication.generic_name,
        dosage=medication.dosage,
        dose_unit=medication.dose_unit,
        frequency=medication.frequency,
        route=medication.route,
        indication=medication.indication,
        prescriber_id=medication.prescriber_id,
        prescriber_name=medication.prescriber.full_name if medication.prescriber else None,
        prescription_date=medication.prescription_date,
        start_date=medication.start_date,
        end_date=medication.end_date,
        status=medication.status,
        notes=medication.notes,
        batch_number=medication.batch_number,
        manufacturer=medication.manufacturer,
        discontinuation_reason=medication.discontinuation_reason,
        bpjs_code=medication.drug.bpjs_code if medication.drug else None,
        is_narcotic=medication.drug.is_narcotic if medication.drug else False,
        is_antibiotic=medication.drug.is_antibiotic if medication.drug else False,
        requires_prescription=medication.drug.requires_prescription if medication.drug else True,
        created_at=medication.created_at,
        updated_at=medication.updated_at,
    )


@router.post("/medications/{medication_id}/stop", response_model=MedicationResponse)
async def stop_medication(
    medication_id: int,
    reason: str = Query(..., min_length=5),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MedicationResponse:
    """Stop a patient medication"""
    medication = await crud_medication.stop_patient_medication(
        db=db,
        medication_id=medication_id,
        reason=reason,
    )
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    return MedicationResponse(
        id=medication.id,
        patient_id=medication.patient_id,
        encounter_id=medication.encounter_id,
        drug_id=medication.drug_id,
        drug_name=medication.drug_name,
        generic_name=medication.generic_name,
        dosage=medication.dosage,
        dose_unit=medication.dose_unit,
        frequency=medication.frequency,
        route=medication.route,
        indication=medication.indication,
        prescriber_id=medication.prescriber_id,
        prescriber_name=medication.prescriber.full_name if medication.prescriber else None,
        prescription_date=medication.prescription_date,
        start_date=medication.start_date,
        end_date=medication.end_date,
        status=medication.status,
        notes=medication.notes,
        batch_number=medication.batch_number,
        manufacturer=medication.manufacturer,
        discontinuation_reason=medication.discontinuation_reason,
        bpjs_code=medication.drug.bpjs_code if medication.drug else None,
        is_narcotic=medication.drug.is_narcotic if medication.drug else False,
        is_antibiotic=medication.drug.is_antibiotic if medication.drug else False,
        requires_prescription=medication.drug.requires_prescription if medication.drug else True,
        created_at=medication.created_at,
        updated_at=medication.updated_at,
    )


# =============================================================================
# Drug Interaction Checking Endpoints
# =============================================================================

@router.post("/medications/check-interactions", response_model=DrugInteractionCheckResponse)
async def check_interactions(
    check_request: DrugInteractionCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DrugInteractionCheckResponse:
    """Check for drug interactions"""
    result = await crud_medication.check_drug_interactions(
        db=db,
        patient_id=check_request.patient_id,
        drug_ids=check_request.drug_ids,
    )
    return result


@router.post("/medications/check-duplicates", response_model=List[DuplicateTherapyWarning])
async def check_duplicate_therapy(
    drug_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[DuplicateTherapyWarning]:
    """Check for duplicate therapies"""
    duplicates = await crud_medication.check_duplicate_therapy(
        db=db,
        drug_ids=drug_ids,
    )

    return [
        DuplicateTherapyWarning(
            drug_1_id=d["drug_1_id"],
            drug_1_name=d["drug_1_name"],
            drug_2_id=d["drug_2_id"],
            drug_2_name=d["drug_2_name"],
            therapeutic_class=d["therapeutic_class"],
            severity=d["severity"],
            recommendation=d["recommendation"],
        )
        for d in duplicates
    ]


# =============================================================================
# Medication Reconciliation Endpoints
# =============================================================================

@router.post("/patients/{patient_id}/medications/reconcile", response_model=MedicationReconciliationResponse)
async def reconcile_medications(
    patient_id: int,
    reconciliation_data: MedicationReconciliationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MedicationReconciliationResponse:
    """Create a medication reconciliation record"""
    # Convert medications to dict format
    medications_dict = [med.model_dump() for med in reconciliation_data.medications]

    reconciliation = await crud_medication.create_medication_reconciliation(
        db=db,
        patient_id=patient_id,
        encounter_id=reconciliation_data.encounter_id,
        source=reconciliation_data.source,
        medications=medications_dict,
        reconciled_by=current_user.id,
        notes=reconciliation_data.notes,
    )

    return MedicationReconciliationResponse(
        id=reconciliation.id,
        patient_id=reconciliation.patient_id,
        encounter_id=reconciliation.encounter_id,
        reconciliation_date=reconciliation.reconciliation_date,
        source=reconciliation.source,
        total_medications=reconciliation.total_medications,
        discrepancies_found=reconciliation.discrepancies_found,
        medications_continued=reconciliation.medications_continued,
        medications_modified=reconciliation.medications_modified,
        medications_stopped=reconciliation.medications_stopped,
        medications_added=reconciliation.medications_added,
        reconciled_by=reconciliation.reconciled_by,
        reconciled_by_name=reconciliation.reconciler.full_name if reconciliation.reconciler else None,
        notes=reconciliation.notes,
        created_at=reconciliation.created_at,
    )


@router.get("/patients/{patient_id}/medications/reconciliations", response_model=List[MedicationReconciliationResponse])
async def get_reconciliation_history(
    patient_id: int,
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[MedicationReconciliationResponse]:
    """Get medication reconciliation history for a patient"""
    reconciliations = await crud_medication.get_medication_reconciliations(
        db=db,
        patient_id=patient_id,
        limit=limit,
    )

    return [
        MedicationReconciliationResponse(
            id=r.id,
            patient_id=r.patient_id,
            encounter_id=r.encounter_id,
            reconciliation_date=r.reconciliation_date,
            source=r.source,
            total_medications=r.total_medications,
            discrepancies_found=r.discrepancies_found,
            medications_continued=r.medications_continued,
            medications_modified=r.medications_modified,
            medications_stopped=r.medications_stopped,
            medications_added=r.medications_added,
            reconciled_by=r.reconciled_by,
            reconciled_by_name=r.reconciler.full_name if r.reconciler else None,
            notes=r.notes,
            created_at=r.created_at,
        )
        for r in reconciliations
    ]
