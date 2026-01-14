"""Encounter API endpoints for STORY-011: Patient History View

This module provides REST API endpoints for managing patient encounters,
including creating, updating, and retrieving patient history.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.core.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.encounter import (
    EncounterCreate,
    EncounterUpdate,
    EncounterResponse,
    EncounterListResponse,
    PatientHistoryResponse,
    PatientEncountersListResponse
)
from app.crud import encounter as encounter_crud
from app.crud.patient import get_patient_by_id

router = APIRouter()


@router.get("/patients/{patient_id}/history", response_model=PatientHistoryResponse)
async def get_patient_history(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("patient", "read"))
):
    """
    Get comprehensive patient history including all encounters, diagnoses, and treatments.

    Args:
        patient_id: Patient ID
        db: Database session
        current_user: Authenticated user with patient:read permission

    Returns:
        Comprehensive patient history with statistics

    Raises:
        HTTPException 404: If patient not found
    """
    try:
        history = await encounter_crud.get_patient_history(db, patient_id)
        return PatientHistoryResponse(**history)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/patients/{patient_id}/encounters", response_model=PatientEncountersListResponse)
async def get_patient_encounters(
    patient_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("patient", "read"))
):
    """
    Get paginated list of patient encounters.

    Args:
        patient_id: Patient ID
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        status: Optional status filter (active, completed, cancelled, scheduled)
        db: Database session
        current_user: Authenticated user with patient:read permission

    Returns:
        Paginated list of encounters
    """
    # Verify patient exists
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    encounters, total = await encounter_crud.get_encounters_by_patient(
        db=db,
        patient_id=patient_id,
        skip=skip,
        limit=limit,
        status=status
    )

    return PatientEncountersListResponse(
        patient_id=patient.id,
        medical_record_number=patient.medical_record_number,
        full_name=patient.full_name,
        encounters=encounters,
        total=total
    )


@router.get("/{encounter_id}", response_model=EncounterResponse)
async def get_encounter(
    encounter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("encounter", "read"))
):
    """
    Get encounter by ID.

    Args:
        encounter_id: Encounter ID
        db: Database session
        current_user: Authenticated user with encounter:read permission

    Returns:
        Encounter with diagnoses and treatments

    Raises:
        HTTPException 404: If encounter not found
    """
    encounter = await encounter_crud.get_encounter_by_id(db, encounter_id)
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Encounter with ID {encounter_id} not found"
        )
    return encounter


@router.post("/", response_model=EncounterResponse, status_code=status.HTTP_201_CREATED)
async def create_encounter(
    encounter_in: EncounterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("encounter", "create"))
):
    """
    Create a new encounter with diagnoses and treatments.

    Args:
        encounter_in: Encounter creation data
        db: Database session
        current_user: Authenticated user with encounter:create permission

    Returns:
        Created encounter with diagnoses and treatments

    Raises:
        HTTPException 400: If validation error
        HTTPException 404: If patient not found
    """
    try:
        encounter = await encounter_crud.create_encounter(db, encounter_in)
        return encounter
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{encounter_id}", response_model=EncounterResponse)
async def update_encounter(
    encounter_id: int,
    encounter_in: EncounterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("encounter", "update"))
):
    """
    Update an existing encounter.

    Args:
        encounter_id: Encounter ID
        encounter_in: Encounter update data
        db: Database session
        current_user: Authenticated user with encounter:update permission

    Returns:
        Updated encounter with diagnoses and treatments

    Raises:
        HTTPException 404: If encounter not found
        HTTPException 400: If validation error
    """
    try:
        encounter = await encounter_crud.update_encounter(db, encounter_id, encounter_in)
        if not encounter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Encounter with ID {encounter_id} not found"
            )
        return encounter
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
