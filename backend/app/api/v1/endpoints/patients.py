"""Patient registration API endpoints for STORY-006: New Patient Registration

This module provides REST API endpoints for patient registration and management.
All endpoints require authentication and appropriate permissions.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.core.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse,
    DuplicatePatientWarning,
    PatientCheckInResponse,
    PatientLookupResponse
)
from app.crud import patient as patient_crud

router = APIRouter()


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def register_patient(
    patient_in: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("patient", "create"))
):
    """
    Register a new patient with auto-generated medical record number.

    Args:
        patient_in: Patient registration data
        db: Database session
        current_user: Authenticated user with patient:create permission

    Returns:
        Created patient with auto-generated MRN

    Raises:
        HTTPException 400: If duplicate patient detected
    """
    try:
        patient = await patient_crud.create_patient(db, patient_in)
        return patient
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/duplicate-check", response_model=DuplicatePatientWarning)
async def check_duplicate_patient(
    nik: Optional[str] = Query(None, description="NIK to check for duplicates"),
    full_name: Optional[str] = Query(None, description="Patient full name"),
    date_of_birth: Optional[str] = Query(None, description="Date of birth (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check for duplicate patients by NIK or name+date of birth.

    Args:
        nik: 16-digit Indonesian ID number
        full_name: Patient's full name
        date_of_birth: Patient's date of birth (YYYY-MM-DD format)
        db: Database session
        current_user: Authenticated user

    Returns:
        Duplicate patient warning with existing patient info if found
    """
    from datetime import datetime

    # Check by NIK if provided
    if nik:
        existing = await patient_crud.get_patient_by_nik(db, nik)
        if existing:
            return DuplicatePatientWarning(
                is_duplicate=True,
                existing_patient=existing,
                message=f"Patient with NIK {nik} already exists (MRN: {existing.medical_record_number})"
            )

    # Check by name and date of birth if both provided
    if full_name and date_of_birth:
        try:
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="date_of_birth must be in YYYY-MM-DD format"
            )

        existing = await patient_crud.detect_duplicates(db, full_name, dob)
        if existing:
            return DuplicatePatientWarning(
                is_duplicate=True,
                existing_patient=existing,
                message=f"Patient with name '{full_name}' and DOB '{date_of_birth}' already exists (MRN: {existing.medical_record_number})"
            )

    return DuplicatePatientWarning(
        is_duplicate=False,
        message="No duplicate patient found"
    )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("patient", "read"))
):
    """
    Get patient by ID.

    Args:
        patient_id: Patient ID
        db: Database session
        current_user: Authenticated user with patient:read permission

    Returns:
        Patient data

    Raises:
        HTTPException 404: If patient not found
    """
    patient = await patient_crud.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    return patient


@router.get("/mrn/{medical_record_number}", response_model=PatientResponse)
async def get_patient_by_mrn(
    medical_record_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("patient", "read"))
):
    """
    Get patient by Medical Record Number (MRN).

    Args:
        medical_record_number: Medical Record Number
        db: Database session
        current_user: Authenticated user with patient:read permission

    Returns:
        Patient data

    Raises:
        HTTPException 404: If patient not found
    """
    patient = await patient_crud.get_patient_by_mrn(db, medical_record_number)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with MRN {medical_record_number} not found"
        )
    return patient


@router.get("/nik/{nik}", response_model=PatientResponse)
async def get_patient_by_nik_endpoint(
    nik: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("patient", "read"))
):
    """
    Get patient by NIK (Indonesian ID number).

    Args:
        nik: 16-digit Indonesian ID number
        db: Database session
        current_user: Authenticated user with patient:read permission

    Returns:
        Patient data

    Raises:
        HTTPException 404: If patient not found
    """
    patient = await patient_crud.get_patient_by_nik(db, nik)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with NIK {nik} not found"
        )
    return patient


@router.get("/", response_model=PatientListResponse)
async def search_patients(
    search: Optional[str] = Query(None, description="Search term (name, phone, MRN, or NIK)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    is_active: bool = Query(True, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("patient", "read"))
):
    """
    Search patients with pagination.

    Args:
        search: Search term (matches name, phone, MRN, or NIK)
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        is_active: Filter by active status
        db: Database session
        current_user: Authenticated user with patient:read permission

    Returns:
        Paginated list of patients
    """
    patients, total = await patient_crud.search_patients(
        db=db,
        search_term=search,
        skip=skip,
        limit=limit,
        is_active=is_active
    )

    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1

    return PatientListResponse(
        items=patients,
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages
    )


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_in: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("patient", "update"))
):
    """
    Update patient information.

    Args:
        patient_id: Patient ID
        patient_in: Patient update data
        db: Database session
        current_user: Authenticated user with patient:update permission

    Returns:
        Updated patient data

    Raises:
        HTTPException 404: If patient not found
        HTTPException 400: If validation error
    """
    try:
        patient = await patient_crud.update_patient(db, patient_id, patient_in)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        return patient
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("patient", "delete"))
):
    """
    Soft delete a patient by setting is_active to False.

    Args:
        patient_id: Patient ID
        db: Database session
        current_user: Authenticated user with patient:delete permission

    Raises:
        HTTPException 404: If patient not found
    """
    patient = await patient_crud.deactivate_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )


@router.post("/{patient_id}/checkin", response_model=PatientCheckInResponse)
async def check_in_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("patient", "update"))
):
    """
    Check-in a returning patient with queue number generation.

    Args:
        patient_id: Patient ID
        db: Database session
        current_user: Authenticated user with patient:update permission

    Returns:
        Check-in confirmation with queue number

    Raises:
        HTTPException 404: If patient not found
    """
    from datetime import datetime

    patient = await patient_crud.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    # TODO: Generate queue number (requires STORY-010: Queue Management System)
    # For now, return placeholder
    queue_number = None

    # Check insurance status
    insurance_status = "Unknown"
    if patient.insurance_policies:
        latest_insurance = patient.insurance_policies[0]
        if latest_insurance.expiry_date:
            if latest_insurance.expiry_date > datetime.now().date():
                insurance_status = f"Active ({latest_insurance.insurance_type.value.upper()})"
            else:
                insurance_status = f"Expired ({latest_insurance.insurance_type.value.upper()})"
        else:
            insurance_status = f"{latest_insurance.insurance_type.value.upper()}"

    return PatientCheckInResponse(
        patient=patient,
        queue_number=queue_number,
        check_in_time=datetime.now(),
        message=f"Patient {patient.full_name} checked in successfully",
        last_visit=None,  # TODO: Track visit history (requires encounter table)
        insurance_status=insurance_status
    )


@router.get("/lookup/advanced", response_model=PatientLookupResponse)
async def lookup_patient_advanced(
    search: str = Query(..., description="Search term (MRN, NIK, BPJS number, phone, or name)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("patient", "read"))
):
    """
    Advanced patient lookup for returning patient check-in (STORY-007).

    Searches patients by multiple methods and returns enhanced information
    including last visit, diagnoses, allergies, and insurance status.

    Args:
        search: Search term (MRN, NIK, BPJS number, phone, or name)
        db: Database session
        current_user: Authenticated user with patient:read permission

    Returns:
        Enhanced patient information for check-in

    Raises:
        HTTPException 404: If patient not found
    """
    # Try multiple search methods in order of specificity
    patient = None

    # 1. Try MRN (most specific)
    patient = await patient_crud.get_patient_by_mrn(db, search)

    # 2. Try NIK
    if not patient:
        patient = await patient_crud.get_patient_by_nik(db, search)

    # 3. Try phone number
    if not patient:
        patients, _ = await patient_crud.search_patients(
            db=db,
            search_term=search,
            skip=0,
            limit=1,
            is_active=True
        )
        if patients:
            patient = patients[0]

    # 4. Try by name (less specific, may return multiple)
    if not patient:
        patients, _ = await patient_crud.search_patients(
            db=db,
            search_term=search,
            skip=0,
            limit=10,
            is_active=True
        )
        if patients and len(patients) == 1:
            # Only auto-select if single match
            patient = patients[0]

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient not found with search term: {search}"
        )

    # Get insurance status
    insurance_status = "Unknown"
    if patient.insurance_policies:
        latest_insurance = patient.insurance_policies[0]
        if latest_insurance.expiry_date:
            from datetime import datetime
            if latest_insurance.expiry_date > datetime.now().date():
                insurance_status = f"Active ({latest_insurance.insurance_type.value.upper()})"
            else:
                insurance_status = f"Expired ({latest_insurance.insurance_type.value.upper()})"
        else:
            insurance_status = f"{latest_insurance.insurance_type.value.upper()}"

    # TODO: Get last visit, diagnoses, allergies (requires encounter table)
    return PatientLookupResponse(
        patient=patient,
        last_visit_date=None,
        last_diagnoses=[],
        allergies=[],
        insurance_status=insurance_status,
        has_unpaid_bills=False
    )
