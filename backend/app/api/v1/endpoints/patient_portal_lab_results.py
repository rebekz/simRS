"""Patient Portal Lab Results Endpoints

API endpoints for patients to view their laboratory results.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.deps import get_db, get_current_portal_patient
from app.models.patient_portal import PatientPortalUser
from app.schemas.patient_portal.lab_results import (
    LabResultsListResponse,
    LabResultDetail,
    TestHistoryResponse,
    CriticalValueAlert,
    LabTestExplanation,
)

router = APIRouter()


@router.get("/lab-results", response_model=LabResultsListResponse)
async def get_lab_results(
    include_historical: bool = True,
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get patient's lab results

    Returns lab results grouped into recent (90 days) and historical.
    Includes counts for pending results and critical alerts.
    """
    from app.services.patient_portal.lab_results_service import LabResultsService

    service = LabResultsService(db)
    results = await service.get_lab_results(current_user.patient_id, include_historical)
    return results


@router.get("/lab-results/{lab_order_id}", response_model=LabResultDetail)
async def get_lab_result_detail(
    lab_order_id: int,
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed lab result with explanations

    Returns detailed lab result including:
    - Test results with reference ranges
    - Abnormal flags
    - Patient-friendly explanations
    - Test descriptions
    """
    from app.services.patient_portal.lab_results_service import LabResultsService

    service = LabResultsService(db)
    result = await service.get_lab_result_detail(current_user.patient_id, lab_order_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab result not found",
        )

    return result


@router.get("/lab-results/{test_code}/history", response_model=TestHistoryResponse)
async def get_test_history(
    test_code: str,
    months: int = Query(12, ge=1, le=24, description="Number of months of history"),
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get test history for trending visualization

    Returns historical results for a specific test to show trends over time.
    Useful for monitoring chronic conditions like diabetes (HbA1c), cholesterol, etc.
    """
    from app.services.patient_portal.lab_results_service import LabResultsService

    service = LabResultsService(db)
    history = await service.get_test_history(current_user.patient_id, test_code, months)

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No history found for test code: {test_code}",
        )

    return history


@router.get("/lab-results/alerts/critical", response_model=list[CriticalValueAlert])
async def get_critical_alerts(
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get critical value alerts

    Returns all lab results with critical values that require attention.
    These should be prominently displayed in the patient portal.
    """
    from app.services.patient_portal.lab_results_service import LabResultsService

    service = LabResultsService(db)
    alerts = await service.get_critical_alerts(current_user.patient_id)
    return alerts


@router.get("/lab-tests/{test_code}/explanation", response_model=LabTestExplanation)
async def get_test_explanation(
    test_code: str,
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
):
    """Get patient-friendly explanation for a lab test

    Returns educational information about what the test measures,
    why it's done, how to prepare, and what results mean.
    """
    from app.services.patient_portal.lab_results_service import LabResultsService

    # Get explanation from service
    service = LabResultsService  # Access class-level dict
    explanation = service.TEST_EXPLANATIONS.get(test_code.upper())

    if not explanation:
        # Try partial match
        for code, exp in service.TEST_EXPLANATIONS.items():
            if code in test_code.upper() or test_code.upper() in code:
                explanation = exp
                break

    if not explanation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No explanation found for test code: {test_code}",
        )

    return LabTestExplanation(
        test_code=test_code,
        test_name=test_code,  # Would be looked up from test catalog
        loinc_code=None,
        description=explanation.get("description", ""),
        what_it_measures=explanation.get("what_it_measures", ""),
        why_its_done=explanation.get("why_its_done", ""),
        how_to_prepare=explanation.get("how_to_prepare"),
        what_results_mean=explanation.get("what_results_mean", ""),
        normal_range=explanation.get("normal_range", ""),
        abnormal_values_mean=explanation.get("abnormal_values_mean", ""),
        next_steps_if_abnormal=explanation.get("next_steps_if_abnormal", ""),
        educational_links=[],
    )
