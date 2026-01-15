"""Patient Portal Radiology Results Endpoints

API endpoints for patients to view their radiology/imaging results.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.deps import get_db, get_current_portal_patient
from app.models.patient_portal import PatientPortalUser
from app.schemas.patient_portal.radiology_results import (
    RadiologyResultsListResponse,
    RadiologyResultDetail,
    CriticalFindingAlert,
    RadiologyExamExplanation,
)

router = APIRouter()


@router.get("/radiology-results", response_model=RadiologyResultsListResponse)
async def get_radiology_results(
    include_historical: bool = True,
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get patient's radiology/imaging results

    Returns radiology results grouped into recent (90 days) and historical.
    Includes counts for pending exams and critical findings.
    """
    from app.services.patient_portal.radiology_service import RadiologyResultsService

    service = RadiologyResultsService(db)
    results = await service.get_radiology_results(current_user.patient_id, include_historical)
    return results


@router.get("/radiology-results/{radiology_order_id}", response_model=RadiologyResultDetail)
async def get_radiology_result_detail(
    radiology_order_id: int,
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed radiology result with reports

    Returns detailed radiology result including:
    - Exam details (modality, body part, contrast)
    - Preliminary and final reports
    - Findings and impression
    - Critical finding alerts
    - Imaging study information
    """
    from app.services.patient_portal.radiology_service import RadiologyResultsService

    service = RadiologyResultsService(db)
    result = await service.get_radiology_result_detail(current_user.patient_id, radiology_order_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Radiology result not found",
        )

    return result


@router.get("/radiology-results/alerts/critical", response_model=list[CriticalFindingAlert])
async def get_critical_alerts(
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get critical finding alerts

    Returns all radiology exams with critical findings that require attention.
    These should be prominently displayed in the patient portal.
    """
    from app.services.patient_portal.radiology_service import RadiologyResultsService

    service = RadiologyResultsService(db)
    alerts = await service.get_critical_alerts(current_user.patient_id)
    return alerts


@router.get("/radiology-modalities/{modality}/explanation", response_model=RadiologyExamExplanation)
async def get_modality_explanation(
    modality: str,
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
):
    """Get patient-friendly explanation for an imaging modality

    Returns educational information about the imaging procedure:
    - What the exam is
    - Why it's done
    - How to prepare
    - What to expect
    - Risks and timing
    """
    from app.services.patient_portal.radiology_service import RadiologyResultsService

    # Access class-level method
    explanation = RadiologyResultsService.get_modality_explanation(None, modality)

    if not explanation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No explanation found for modality: {modality}",
        )

    return explanation
