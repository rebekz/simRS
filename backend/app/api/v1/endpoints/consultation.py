"""Consultation Workflow API endpoints for STORY-016

This module provides API endpoints for the doctor consultation workflow.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.consultation import (
    ConsultationSessionCreate,
    ConsultationSessionResponse,
    ConsultationPatientSummary,
    ConsultationDocumentationUpdate,
    QuickDiagnosisCreate,
    TreatmentPlanCreate,
    ConsultationCompletion,
    ConsultationCompletionResponse,
    ConsultationTemplateResponse,
    EducationMaterialResponse,
)
from app.crud import consultation as crud_consultation
from app.crud import encounter as crud_encounter


router = APIRouter()


# =============================================================================
# Consultation Session Management
# =============================================================================

@router.post("/consultation/start", response_model=ConsultationSessionResponse)
async def start_consultation(
    consultation_data: ConsultationSessionCreate,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConsultationSessionResponse:
    """Start a new consultation session."""
    encounter = await crud_consultation.start_consultation(
        db=db,
        patient_id=consultation_data.patient_id,
        encounter_type=consultation_data.encounter_type,
        doctor_id=current_user.id,
        department=consultation_data.department,
        chief_complaint=consultation_data.chief_complaint,
    )

    # Trigger SATUSEHAT sync in background (STORY-035)
    if background_tasks and encounter:
        from app.services.encounter_sync import trigger_encounter_sync_on_create
        background_tasks.add_task(trigger_encounter_sync_on_create, db, encounter.id)

    return ConsultationSessionResponse(
        encounter_id=encounter.id,
        patient_id=encounter.patient_id,
        status=encounter.status,
        start_time=encounter.start_time,
        encounter_type=encounter.encounter_type,
        department=encounter.department,
    )


@router.get("/consultation/patient-summary/{patient_id}", response_model=ConsultationPatientSummary)
async def get_patient_summary(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConsultationPatientSummary:
    """Get patient summary for consultation display."""
    try:
        summary = await crud_consultation.get_patient_summary_for_consultation(db, patient_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return ConsultationPatientSummary(**summary)


@router.get("/consultation/session/{encounter_id}", response_model=ConsultationSessionResponse)
async def get_consultation_session(
    encounter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConsultationSessionResponse:
    """Get consultation session by ID."""
    encounter = await crud_consultation.get_consultation_session(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Consultation session not found")

    return ConsultationSessionResponse(
        encounter_id=encounter.id,
        patient_id=encounter.patient_id,
        status=encounter.status,
        start_time=encounter.start_time,
        encounter_type=encounter.encounter_type,
        department=encounter.department,
    )


@router.get("/consultation/active", response_model=List[ConsultationSessionResponse])
async def get_active_consultations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=100),
) -> List[ConsultationSessionResponse]:
    """Get active consultations for current doctor."""
    encounters = await crud_consultation.get_active_consultations(
        db=db,
        doctor_id=current_user.id,
        limit=limit,
    )

    return [
        ConsultationSessionResponse(
            encounter_id=e.id,
            patient_id=e.patient_id,
            status=e.status,
            start_time=e.start_time,
            encounter_type=e.encounter_type,
            department=e.department,
        )
        for e in encounters
    ]


# =============================================================================
# Consultation Documentation
# =============================================================================

@router.put("/consultation/documentation", response_model=ConsultationSessionResponse)
async def update_documentation(
    doc_data: ConsultationDocumentationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConsultationSessionResponse:
    """Update consultation documentation (auto-save)."""
    encounter = await crud_consultation.update_consultation_documentation(
        db=db,
        encounter_id=doc_data.encounter_id,
        chief_complaint=doc_data.chief_complaint,
        present_illness=doc_data.present_illness,
        physical_examination=doc_data.physical_examination,
        vital_signs=doc_data.vital_signs,
        clinical_note_id=doc_data.clinical_note_id,
    )

    if not encounter:
        raise HTTPException(status_code=404, detail="Consultation session not found")

    return ConsultationSessionResponse(
        encounter_id=encounter.id,
        patient_id=encounter.patient_id,
        status=encounter.status,
        start_time=encounter.start_time,
        encounter_type=encounter.encounter_type,
        department=encounter.department,
    )


# =============================================================================
# Quick Diagnosis Entry
# =============================================================================

@router.post("/consultation/diagnosis", response_model=dict)
async def add_diagnosis(
    diagnosis_data: QuickDiagnosisCreate,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add diagnosis to consultation."""
    try:
        diagnosis = await crud_consultation.add_diagnosis_to_consultation(
            db=db,
            encounter_id=diagnosis_data.encounter_id,
            icd10_code_id=diagnosis_data.icd10_code_id,
            diagnosis_name=diagnosis_data.diagnosis_name,
            diagnosis_type=diagnosis_data.diagnosis_type,
            is_chronic=diagnosis_data.is_chronic,
        )

        # Trigger SATUSEHAT sync in background (STORY-036)
        if background_tasks and diagnosis:
            from app.services.condition_sync import trigger_condition_sync_on_create
            background_tasks.add_task(trigger_condition_sync_on_create, db, diagnosis.id)

        return {
            "diagnosis_id": diagnosis.id,
            "encounter_id": diagnosis.encounter_id,
            "icd_10_code": diagnosis.icd_10_code,
            "diagnosis_name": diagnosis.diagnosis_name,
            "added": True,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# Treatment Plan
# =============================================================================

@router.post("/consultation/treatment", response_model=dict)
async def add_treatment(
    treatment_data: TreatmentPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add treatment to consultation."""
    try:
        treatment = await crud_consultation.add_treatment_to_consultation(
            db=db,
            encounter_id=treatment_data.encounter_id,
            treatment_type=treatment_data.treatment_type,
            treatment_name=treatment_data.treatment_name,
            description=treatment_data.description,
            dosage=treatment_data.dosage,
            frequency=treatment_data.frequency,
            duration=treatment_data.duration,
            route=treatment_data.route,
            is_active=treatment_data.is_active,
        )
        return {
            "treatment_id": treatment.id,
            "encounter_id": treatment.encounter_id,
            "treatment_name": treatment.treatment_name,
            "added": True,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# Consultation Completion
# =============================================================================

@router.post("/consultation/complete", response_model=ConsultationCompletionResponse)
async def complete_consultation(
    completion_data: ConsultationCompletion,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConsultationCompletionResponse:
    """Complete a consultation encounter."""
    try:
        encounter = await crud_consultation.complete_consultation(
            db=db,
            encounter_id=completion_data.encounter_id,
            end_time=completion_data.end_time,
            notes=completion_data.notes,
            follow_up_required=completion_data.follow_up_required,
            follow_up_date=completion_data.follow_up_date,
            next_appointment_date=completion_data.next_appointment_date,
            next_appointment_department=completion_data.next_appointment_department,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not encounter:
        raise HTTPException(status_code=404, detail="Consultation session not found")

    # Trigger SATUSEHAT sync in background (STORY-035)
    if background_tasks and encounter:
        from app.services.encounter_sync import trigger_encounter_sync_on_completion
        background_tasks.add_task(trigger_encounter_sync_on_completion, db, encounter.id)

    # Calculate duration
    duration_minutes = None
    if encounter.end_time and encounter.start_time:
        duration = encounter.end_time - encounter.start_time
        duration_minutes = int(duration.total_seconds() / 60)

    return ConsultationCompletionResponse(
        encounter_id=encounter.id,
        status=encounter.status,
        end_time=encounter.end_time,
        duration_minutes=duration_minutes,
        diagnoses_count=len(encounter.diagnoses),
        treatments_count=len(encounter.treatments),
        clinical_note_signed=False,  # TODO: check if linked clinical note is signed
    )


# =============================================================================
# Consultation Templates
# =============================================================================

@router.get("/consultation/templates", response_model=List[ConsultationTemplateResponse])
async def get_consultation_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    specialty: Optional[str] = Query(default=None),
) -> List[ConsultationTemplateResponse]:
    """Get consultation templates for auto-population."""
    templates = await crud_consultation.get_consultation_templates(db, specialty)

    return [
        ConsultationTemplateResponse(
            id=t["id"],
            name=t["name"],
            specialty=t["specialty"],
            template=t["template"],
            description=t.get("description"),
        )
        for t in templates
    ]


# =============================================================================
# Patient Education Materials
# =============================================================================

@router.get("/consultation/education-materials", response_model=List[EducationMaterialResponse])
async def get_education_materials(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    icd10_codes: Optional[str] = Query(default=None, description="Comma-separated ICD-10 codes"),
    limit: int = Query(default=20, ge=1, le=100),
) -> List[EducationMaterialResponse]:
    """Get patient education materials based on diagnoses."""
    codes = [c.strip() for c in icd10_codes.split(",")] if icd10_codes else None

    materials = await crud_consultation.get_patient_education_materials(
        db=db,
        icd10_codes=codes,
        limit=limit,
    )

    return [
        EducationMaterialResponse(
            id=m["id"],
            title=m["title"],
            description=m.get("description"),
            icd10_codes=m["icd10_codes"],
            content_type=m["content_type"],
            content_url=m.get("content_url"),
            content=m.get("content"),
            language=m["language"],
        )
        for m in materials
    ]
