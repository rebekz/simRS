"""Enhanced Patient Registration API Endpoints for STORY-006

This module provides enhanced API endpoints for patient registration
using the new service layer for better business logic encapsulation.

Python 3.5+ compatible
"""

import logging
from typing import Optional, List
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.patient_registration import (
    get_patient_registration_service,
    PatientValidationError,
    DuplicatePatientError,
)
from app.services.patient_deduplication import (
    get_deduplication_service,
    get_merge_request_service,
)
from app.core.deps import get_current_user, get_current_admin_user


logger = logging.getLogger(__name__)


router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class PatientRegistrationRequest(BaseModel):
    """Request model for patient registration"""
    nik: Optional[str] = Field(None, description="16-digit Indonesian ID number")
    full_name: str = Field(..., description="Patient full name")
    date_of_birth: date = Field(..., description="Date of birth (YYYY-MM-DD)")
    gender: str = Field(..., description="Gender (male, female)")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    address: Optional[str] = Field(None, description="Residential address")
    city: Optional[str] = Field(None, description="City of residence")
    province: Optional[str] = Field(None, description="Province of residence")
    postal_code: Optional[str] = Field(None, description="Postal code")
    blood_type: Optional[str] = Field(None, description="Blood type")
    marital_status: Optional[str] = Field(None, description="Marital status")
    religion: Optional[str] = Field(None, description="Religion")
    occupation: Optional[str] = Field(None, description="Occupation")
    photo_url: Optional[str] = Field(None, description="URL to patient photo")
    bpjs_card_number: Optional[str] = Field(None, description="BPJS card number")
    satusehat_patient_id: Optional[str] = Field(None, description="SATUSEHAT patient ID")
    emergency_contacts: Optional[List[dict]] = Field(None, description="Emergency contacts")
    insurance_policies: Optional[List[dict]] = Field(None, description="Insurance policies")


class PatientUpdateRequest(BaseModel):
    """Request model for patient update"""
    full_name: Optional[str] = Field(None, description="Patient full name")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    address: Optional[str] = Field(None, description="Residential address")
    city: Optional[str] = Field(None, description="City")
    province: Optional[str] = Field(None, description="Province")
    postal_code: Optional[str] = Field(None, description="Postal code")
    blood_type: Optional[str] = Field(None, description="Blood type")
    marital_status: Optional[str] = Field(None, description="Marital status")
    religion: Optional[str] = Field(None, description="Religion")
    occupation: Optional[str] = Field(None, description="Occupation")
    photo_url: Optional[str] = Field(None, description="Photo URL")
    bpjs_card_number: Optional[str] = Field(None, description="BPJS card number")


class PatientSearchRequest(BaseModel):
    """Request model for patient search"""
    search_term: Optional[str] = Field(None, description="General search term")
    nik: Optional[str] = Field(None, description="NIK")
    mrn: Optional[str] = Field(None, description="Medical record number")
    phone: Optional[str] = Field(None, description="Phone number")
    name: Optional[str] = Field(None, description="Patient name")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")


class DuplicateCheckRequest(BaseModel):
    """Request model for duplicate patient check"""
    nik: Optional[str] = Field(None, description="NIK to check")
    full_name: Optional[str] = Field(None, description="Patient full name")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")


class PatientMergeRequest(BaseModel):
    """Request model for patient merge"""
    primary_mrn: str = Field(..., description="Primary patient MRN")
    duplicate_mrns: List[str] = Field(..., description="Duplicate MRNs to merge")
    reason: str = Field(..., description="Reason for merge")


# =============================================================================
# Patient Registration Endpoints
# =============================================================================

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_new_patient(
    request: PatientRegistrationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register a new patient with auto-generated MRN

    Requires patient:create permission.
    """
    try:
        service = get_patient_registration_service(db)

        # Convert request to dict
        patient_data = request.model_dump(exclude_none=True)

        # Register patient
        patient = await service.register_patient(
            patient_data=patient_data,
            emergency_contacts=request.emergency_contacts,
            insurance_policies=request.insurance_policies,
            created_by=current_user.id,
            check_duplicates=True,
        )

        await db.commit()

        return {
            "id": patient.id,
            "mrn": patient.medical_record_number,
            "full_name": patient.full_name,
            "message": "Patient registered successfully",
            "created_at": patient.created_at.isoformat() if patient.created_at else None,
        }

    except DuplicatePatientError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": e.message,
                "existing_patient": e.existing_patient,
            }
        )

    except PatientValidationError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error registering patient: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register patient"
        )


@router.post("/check-duplicate")
async def check_duplicate_patients(
    request: DuplicateCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check for duplicate patients before registration

    Helps prevent duplicate patient registration.
    """
    try:
        service = get_deduplication_service(db)

        # Convert request to dict
        patient_data = request.model_dump(exclude_none=True)

        # Find potential duplicates
        duplicates = await service.find_potential_duplicates(
            patient_data=patient_data,
            threshold=0.7,
        )

        return {
            "has_duplicates": len(duplicates) > 0,
            "duplicates": duplicates,
            "count": len(duplicates),
        }

    except Exception as e:
        logger.error("Error checking duplicates: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check duplicates"
        )


@router.get("/search")
async def search_patients(
    search_term: Optional[str] = Query(None, description="General search term"),
    nik: Optional[str] = Query(None, description="NIK"),
    mrn: Optional[str] = Query(None, description="Medical record number"),
    phone: Optional[str] = Query(None, description="Phone number"),
    name: Optional[str] = Query(None, description="Patient name"),
    date_of_birth: Optional[date] = Query(None, description="Date of birth"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search for patients by various criteria

    Requires patient:read permission.
    """
    try:
        service = get_patient_registration_service(db)

        patients = await service.search_patients(
            search_term=search_term,
            nik=nik,
            mrn=mrn,
            phone=phone,
            name=name,
            date_of_birth=date_of_birth,
            limit=limit,
        )

        return {
            "patients": patients,
            "count": len(patients),
        }

    except Exception as e:
        logger.error("Error searching patients: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search patients"
        )


@router.get("/statistics")
async def get_patient_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get patient registration statistics

    Requires patient:read permission.
    """
    try:
        service = get_patient_registration_service(db)

        stats = await service.get_patient_statistics()

        return stats

    except Exception as e:
        logger.error("Error getting patient statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )


@router.get("/{mrn}")
async def get_patient_by_mrn(
    mrn: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get patient by medical record number

    Requires patient:read permission.
    """
    try:
        service = get_patient_registration_service(db)

        patient = await service.get_patient_by_mrn(mrn)

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        return {
            "id": patient.id,
            "mrn": patient.medical_record_number,
            "nik": patient.nik,
            "full_name": patient.full_name,
            "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            "gender": patient.gender.value if patient.gender else None,
            "phone": patient.phone,
            "email": patient.email,
            "address": patient.address,
            "city": patient.city,
            "province": patient.province,
            "postal_code": patient.postal_code,
            "blood_type": patient.blood_type.value if patient.blood_type else None,
            "marital_status": patient.marital_status.value if patient.marital_status else None,
            "religion": patient.religion,
            "occupation": patient.occupation,
            "photo_url": patient.photo_url,
            "bpjs_card_number": patient.bpjs_card_number,
            "is_active": patient.is_active,
            "created_at": patient.created_at.isoformat() if patient.created_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting patient: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get patient"
        )


@router.put("/{mrn}")
async def update_patient(
    mrn: str,
    request: PatientUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update patient information (admin only)

    Requires patient:update permission.
    """
    try:
        service = get_patient_registration_service(db)

        patient_data = request.model_dump(exclude_none=True)

        patient = await service.update_patient(
            mrn=mrn,
            patient_data=patient_data,
            updated_by=current_user.id,
        )

        await db.commit()

        return {
            "mrn": patient.medical_record_number,
            "full_name": patient.full_name,
            "message": "Patient updated successfully",
            "updated_at": patient.updated_at.isoformat() if patient.updated_at else None,
        }

    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error updating patient: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update patient"
        )


@router.post("/{mrn}/deactivate")
async def deactivate_patient(
    mrn: str,
    reason: str = Body(..., embed=True, description="Reason for deactivation"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a patient record (admin only)

    Requires patient:delete permission.
    """
    try:
        service = get_patient_registration_service(db)

        await service.deactivate_patient(
            mrn=mrn,
            reason=reason,
            deactivated_by=current_user.id,
        )

        await db.commit()

        return {
            "mrn": mrn,
            "message": "Patient deactivated successfully",
        }

    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error deactivating patient: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate patient"
        )


@router.post("/merge")
async def merge_patient_records(
    request: PatientMergeRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Merge duplicate patient records (admin only)

    Requires patient:delete permission.
    """
    try:
        service = get_deduplication_service(db)

        result = await service.merge_patient_records(
            primary_mrn=request.primary_mrn,
            duplicate_mrns=request.duplicate_mrns,
            merge_reason=request.reason,
            merged_by=current_user.id,
        )

        await db.commit()

        return {
            "primary_mrn": request.primary_mrn,
            "message": "Patient records merged successfully",
            "merged_count": result["merged_count"],
            "failed_count": result["failed_count"],
            "errors": result.get("errors", []),
        }

    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error merging patients: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to merge patient records"
        )
