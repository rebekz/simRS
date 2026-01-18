"""ICD-10 and Problem List API endpoints for STORY-012

This module provides API endpoints for ICD-10 code search and problem list management.
"""
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.icd10 import (
    ICD10SearchRequest,
    ICD10SearchResponse,
    ICD10CodeResponse,
    ICD10FavoritesListResponse,
    ICD10FavoriteCreate,
    ICD10FavoriteResponse,
    ProblemListCreate,
    ProblemListUpdate,
    ProblemListResponse,
    PatientProblemListResponse,
)
from app.crud import icd10 as crud_icd10


router = APIRouter()


# =============================================================================
# ICD-10 Code Search Endpoints
# =============================================================================

@router.post("/icd10/search", response_model=ICD10SearchResponse)
async def search_icd10_codes(
    request: ICD10SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ICD10SearchResponse:
    """
    Search ICD-10 codes by code or description.

    Supports:
    - Full-text search on Indonesian and English descriptions
    - Filtering by chapter and severity
    - Common codes filter
    - Usage-based ranking
    """
    start_time = time.time()

    codes, total = await crud_icd10.search_icd10_codes(
        db=db,
        query=request.query,
        limit=request.limit,
        chapter_filter=request.chapter_filter,
        severity_filter=request.severity_filter,
        common_only=request.common_only,
    )

    search_time_ms = (time.time() - start_time) * 1000

    return ICD10SearchResponse(
        query=request.query,
        results=[ICD10CodeResponse.model_validate(code) for code in codes],
        total=total,
        search_time_ms=round(search_time_ms, 2),
    )


@router.get("/icd10/chapters")
async def get_icd10_chapters(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ICD10CodeResponse]:
    """Get all ICD-10 chapters for filtering."""
    chapters = await crud_icd10.get_icd10_chapters(db)
    return [ICD10CodeResponse.model_validate(ch) for ch in chapters]


@router.get("/icd10/code/{code_id}", response_model=ICD10CodeResponse)
async def get_icd10_code(
    code_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ICD10CodeResponse:
    """Get a specific ICD-10 code by ID."""
    code = await crud_icd10.get_icd10_code_by_id(db, code_id)
    if not code:
        raise HTTPException(status_code=404, detail="ICD-10 code not found")
    return ICD10CodeResponse.model_validate(code)


# =============================================================================
# ICD-10 User Favorites Endpoints
# =============================================================================

@router.get("/icd10/favorites", response_model=ICD10FavoritesListResponse)
async def get_user_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=100, ge=1, le=500),
) -> ICD10FavoritesListResponse:
    """Get current user's favorite ICD-10 codes."""
    favorites = await crud_icd10.get_user_favorites(db, current_user.id, limit)

    return ICD10FavoritesListResponse(
        user_id=current_user.id,
        favorites=[
            ICD10FavoriteResponse(
                id=fav.id,
                icd10_code_id=fav.icd10_code_id,
                notes=fav.notes,
                created_at=fav.created_at,
                code=fav.icd10_reference.code,
                description_indonesian=fav.icd10_reference.description_indonesian,
            )
            for fav in favorites
        ],
        total=len(favorites),
    )


@router.post("/icd10/favorites", response_model=ICD10FavoriteResponse)
async def add_user_favorite(
    favorite_data: ICD10FavoriteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ICD10FavoriteResponse:
    """Add ICD-10 code to user favorites."""
    # Verify code exists
    code = await crud_icd10.get_icd10_code_by_id(db, favorite_data.icd10_code_id)
    if not code:
        raise HTTPException(status_code=404, detail="ICD-10 code not found")

    try:
        favorite = await crud_icd10.add_user_favorite(
            db=db,
            user_id=current_user.id,
            icd10_code_id=favorite_data.icd10_code_id,
            notes=favorite_data.notes,
        )

        return ICD10FavoriteResponse(
            id=favorite.id,
            icd10_code_id=favorite.icd10_code_id,
            notes=favorite.notes,
            created_at=favorite.created_at,
            code=code.code,
            description_indonesian=code.description_indonesian,
        )
    except Exception as e:
        # Likely a unique constraint violation (duplicate favorite)
        if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="This code is already in your favorites"
            )
        raise


@router.delete("/icd10/favorites/{favorite_id}")
async def remove_user_favorite(
    favorite_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove ICD-10 code from user favorites."""
    success = await crud_icd10.remove_user_favorite(db, current_user.id, favorite_id)
    if not success:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Favorite removed successfully"}


# =============================================================================
# Problem List Management Endpoints
# =============================================================================

@router.post("/problems", response_model=ProblemListResponse)
async def create_problem(
    problem_data: ProblemListCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProblemListResponse:
    """
    Create a new problem for a patient.

    Automatically:
    - Sets recorded_by to current user
    - Fetches ICD-10 code details
    - Records creation timestamp
    """
    problem = await crud_icd10.create_problem(
        db=db,
        patient_id=problem_data.patient_id,
        encounter_id=problem_data.encounter_id,
        icd10_code_id=problem_data.icd10_code_id,
        problem_name=problem_data.problem_name,
        diagnosed_by=problem_data.diagnosed_by,
        recorded_by=current_user.id,
        status=problem_data.status,
        onset_date=problem_data.onset_date,
        is_chronic=problem_data.is_chronic,
        severity=problem_data.severity,
        description=problem_data.description,
        clinical_notes=problem_data.clinical_notes,
        treatment_plan=problem_data.treatment_plan,
        follow_up_required=problem_data.follow_up_required,
        follow_up_date=problem_data.follow_up_date,
        certainty=problem_data.certainty,
    )

    # Fetch related data for response
    icd10_ref = problem.icd10_reference

    return ProblemListResponse(
        id=problem.id,
        patient_id=problem.patient_id,
        encounter_id=problem.encounter_id,
        icd10_code_id=problem.icd10_code_id,
        icd10_code=problem.icd10_code,
        problem_name=problem.problem_name,
        description=problem.description,
        status=problem.status,
        onset_date=problem.onset_date,
        resolved_date=problem.resolved_date,
        is_chronic=problem.is_chronic,
        severity=problem.severity,
        diagnosed_by=problem.diagnosed_by,
        recorded_by=problem.recorded_by,
        facility=problem.facility,
        clinical_notes=problem.clinical_notes,
        treatment_plan=problem.treatment_plan,
        follow_up_required=problem.follow_up_required,
        follow_up_date=problem.follow_up_date,
        certainty=problem.certainty,
        chronicity_indicators=problem.chronicity_indicators,
        created_at=problem.created_at,
        updated_at=problem.updated_at,
        icd10_description=icd10_ref.description_indonesian if icd10_ref else None,
        icd10_chapter=icd10_ref.chapter if icd10_ref else None,
    )


@router.get("/problems/patient/{patient_id}", response_model=PatientProblemListResponse)
async def get_patient_problems(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
) -> PatientProblemListResponse:
    """Get all problems for a patient with summary statistics."""
    problems = await crud_icd10.get_patient_problems(
        db=db,
        patient_id=patient_id,
        status_filter=status_filter,
        limit=limit,
    )

    # Get patient details
    from app.crud import patient as crud_patient
    patient = await crud_patient.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Calculate statistics
    total_problems = len(problems)
    active_problems = sum(1 for p in problems if p.status == "active")
    chronic_problems = sum(1 for p in problems if p.is_chronic)
    resolved_problems = sum(1 for p in problems if p.status == "resolved")

    # Build problem responses with related data
    problem_responses = []
    for problem in problems:
        icd10_ref = problem.icd10_reference

        problem_responses.append(
            ProblemListResponse(
                id=problem.id,
                patient_id=problem.patient_id,
                encounter_id=problem.encounter_id,
                icd10_code_id=problem.icd10_code_id,
                icd10_code=problem.icd10_code,
                problem_name=problem.problem_name,
                description=problem.description,
                status=problem.status,
                onset_date=problem.onset_date,
                resolved_date=problem.resolved_date,
                is_chronic=problem.is_chronic,
                severity=problem.severity,
                diagnosed_by=problem.diagnosed_by,
                recorded_by=problem.recorded_by,
                facility=problem.facility,
                clinical_notes=problem.clinical_notes,
                treatment_plan=problem.treatment_plan,
                follow_up_required=problem.follow_up_required,
                follow_up_date=problem.follow_up_date,
                certainty=problem.certainty,
                chronicity_indicators=problem.chronicity_indicators,
                created_at=problem.created_at,
                updated_at=problem.updated_at,
                icd10_description=icd10_ref.description_indonesian if icd10_ref else None,
                icd10_chapter=icd10_ref.chapter if icd10_ref else None,
                diagnosed_by_name=problem.diagnoser.full_name if problem.diagnoser else None,
                recorded_by_name=problem.recorder.full_name if problem.recorder else None,
            )
        )

    return PatientProblemListResponse(
        patient_id=patient.id,
        medical_record_number=patient.medical_record_number,
        full_name=patient.full_name,
        problems=problem_responses,
        total_problems=total_problems,
        active_problems=active_problems,
        chronic_problems=chronic_problems,
        resolved_problems=resolved_problems,
    )


@router.get("/problems/{problem_id}", response_model=ProblemListResponse)
async def get_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProblemListResponse:
    """Get a specific problem by ID."""
    problem = await crud_icd10.get_problem_by_id(db, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    icd10_ref = problem.icd10_reference

    return ProblemListResponse(
        id=problem.id,
        patient_id=problem.patient_id,
        encounter_id=problem.encounter_id,
        icd10_code_id=problem.icd10_code_id,
        icd10_code=problem.icd10_code,
        problem_name=problem.problem_name,
        description=problem.description,
        status=problem.status,
        onset_date=problem.onset_date,
        resolved_date=problem.resolved_date,
        is_chronic=problem.is_chronic,
        severity=problem.severity,
        diagnosed_by=problem.diagnosed_by,
        recorded_by=problem.recorded_by,
        facility=problem.facility,
        clinical_notes=problem.clinical_notes,
        treatment_plan=problem.treatment_plan,
        follow_up_required=problem.follow_up_required,
        follow_up_date=problem.follow_up_date,
        certainty=problem.certainty,
        chronicity_indicators=problem.chronicity_indicators,
        created_at=problem.created_at,
        updated_at=problem.updated_at,
        icd10_description=icd10_ref.description_indonesian if icd10_ref else None,
        icd10_chapter=icd10_ref.chapter if icd10_ref else None,
        diagnosed_by_name=problem.diagnoser.full_name if problem.diagnoser else None,
        recorded_by_name=problem.recorder.full_name if problem.recorder else None,
    )


@router.put("/problems/{problem_id}", response_model=ProblemListResponse)
async def update_problem(
    problem_id: int,
    update_data: ProblemListUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProblemListResponse:
    """Update a problem."""
    problem = await crud_icd10.update_problem(
        db=db,
        problem_id=problem_id,
        status=update_data.status,
        resolved_date=update_data.resolved_date,
        description=update_data.description,
        severity=update_data.severity,
        clinical_notes=update_data.clinical_notes,
        treatment_plan=update_data.treatment_plan,
        follow_up_required=update_data.follow_up_required,
        follow_up_date=update_data.follow_up_date,
        certainty=update_data.certainty,
    )

    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    icd10_ref = problem.icd10_reference

    return ProblemListResponse(
        id=problem.id,
        patient_id=problem.patient_id,
        encounter_id=problem.encounter_id,
        icd10_code_id=problem.icd10_code_id,
        icd10_code=problem.icd10_code,
        problem_name=problem.problem_name,
        description=problem.description,
        status=problem.status,
        onset_date=problem.onset_date,
        resolved_date=problem.resolved_date,
        is_chronic=problem.is_chronic,
        severity=problem.severity,
        diagnosed_by=problem.diagnosed_by,
        recorded_by=problem.recorded_by,
        facility=problem.facility,
        clinical_notes=problem.clinical_notes,
        treatment_plan=problem.treatment_plan,
        follow_up_required=problem.follow_up_required,
        follow_up_date=problem.follow_up_date,
        certainty=problem.certainty,
        chronicity_indicators=problem.chronicity_indicators,
        created_at=problem.created_at,
        updated_at=problem.updated_at,
        icd10_description=icd10_ref.description_indonesian if icd10_ref else None,
        icd10_chapter=icd10_ref.chapter if icd10_ref else None,
    )


@router.delete("/problems/{problem_id}")
async def delete_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a problem (soft delete by setting status to resolved).

    This maintains audit trail while removing from active problems.
    """
    success = await crud_icd10.delete_problem(db, problem_id)
    if not success:
        raise HTTPException(status_code=404, detail="Problem not found")
    return {"message": "Problem resolved successfully"}
