"""Enhanced Patient Check-in API Endpoints for STORY-007

This module provides API endpoints for patient check-in operations
including fast lookup, summary view, and quick check-in workflow.

Python 3.5+ compatible
"""

import logging
from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.patient_checkin import (
    get_patient_checkin_service,
    PatientNotFoundError,
    CheckinValidationError,
)
from app.schemas.queue import QueueDepartment, QueuePriority
from app.core.deps import get_current_user


logger = logging.getLogger(__name__)


router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class PatientLookupRequest(BaseModel):
    """Request model for patient lookup"""
    search_term: Optional[str] = Field(None, description="General search term")
    mrn: Optional[str] = Field(None, description="Medical record number")
    nik: Optional[str] = Field(None, description="NIK")
    bpjs_number: Optional[str] = Field(None, description="BPJS card number")
    phone: Optional[str] = Field(None, description="Phone number")
    name: Optional[str] = Field(None, description="Patient name")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")


class QuickCheckinRequest(BaseModel):
    """Request model for quick check-in"""
    patient_id: int = Field(..., description="Patient ID")
    department: QueueDepartment = Field(..., description="Department to check into")
    encounter_type: str = Field("outpatient", description="Type of encounter")
    chief_complaint: Optional[str] = Field(None, description="Patient's chief complaint")
    poli_id: Optional[int] = Field(None, description="Polyclinic ID (for POLI department)")
    doctor_id: Optional[int] = Field(None, description="Doctor ID")
    appointment_id: Optional[int] = Field(None, description="Appointment ID (if pre-booked)")
    priority: QueuePriority = Field(QueuePriority.NORMAL, description="Queue priority")


class PatientUpdateDuringCheckinRequest(BaseModel):
    """Request model for patient update during check-in"""
    patient_id: int = Field(..., description="Patient ID")
    phone: Optional[str] = Field(None, description="Updated phone number")
    email: Optional[str] = Field(None, description="Updated email")
    address: Optional[str] = Field(None, description="Updated address")
    city: Optional[str] = Field(None, description="Updated city")
    province: Optional[str] = Field(None, description="Updated province")
    postal_code: Optional[str] = Field(None, description="Updated postal code")
    bpjs_card_number: Optional[str] = Field(None, description="Updated BPJS card number")


# =============================================================================
# Patient Check-in Endpoints
# =============================================================================

@router.post("/lookup")
async def lookup_patients(
    request: PatientLookupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fast patient lookup with multiple search methods

    Target: Lookup time <10 seconds (typically <2 seconds)

    Requires patient:read permission.
    """
    try:
        service = get_patient_checkin_service(db)

        patients = await service.lookup_patient(
            search_term=request.search_term,
            mrn=request.mrn,
            nik=request.nik,
            bpjs_number=request.bpjs_number,
            phone=request.phone,
            name=request.name,
            date_of_birth=request.date_of_birth,
        )

        return {
            "patients": patients,
            "count": len(patients),
        }

    except Exception as e:
        logger.error("Error looking up patients: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to lookup patients"
        )


@router.get("/lookup")
async def lookup_patients_get(
    search_term: Optional[str] = Query(None, description="General search term"),
    mrn: Optional[str] = Query(None, description="Medical record number"),
    nik: Optional[str] = Query(None, description="NIK"),
    bpjs_number: Optional[str] = Query(None, description="BPJS card number"),
    phone: Optional[str] = Query(None, description="Phone number"),
    name: Optional[str] = Query(None, description="Patient name"),
    date_of_birth: Optional[date] = Query(None, description="Date of birth"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fast patient lookup via GET with multiple search methods

    Target: Lookup time <10 seconds (typically <2 seconds)

    Requires patient:read permission.
    """
    try:
        service = get_patient_checkin_service(db)

        patients = await service.lookup_patient(
            search_term=search_term,
            mrn=mrn,
            nik=nik,
            bpjs_number=bpjs_number,
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
        logger.error("Error looking up patients: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to lookup patients"
        )


@router.get("/summary/{patient_id}")
async def get_patient_summary(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get comprehensive patient summary for check-in

    Includes demographics, last visit, diagnoses, allergies, and insurance.

    Requires patient:read permission.
    """
    try:
        service = get_patient_checkin_service(db)

        summary = await service.get_patient_summary(patient_id)

        return summary

    except PatientNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        logger.error("Error getting patient summary: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get patient summary"
        )


@router.post("/checkin")
async def quick_checkin(
    request: QuickCheckinRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Quick check-in workflow (single click after patient lookup)

    Creates encounter and queue ticket automatically.

    Requires patient:create permission.
    """
    try:
        service = get_patient_checkin_service(db)

        result = await service.quick_checkin(
            patient_id=request.patient_id,
            department=request.department,
            encounter_type=request.encounter_type,
            chief_complaint=request.chief_complaint,
            poli_id=request.poli_id,
            doctor_id=request.doctor_id,
            appointment_id=request.appointment_id,
            priority=request.priority,
            checked_in_by=current_user.id,
        )

        await db.commit()

        return result

    except PatientNotFoundError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except CheckinValidationError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error during check-in: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check in patient"
        )


@router.put("/update-during-checkin")
async def update_patient_during_checkin(
    request: PatientUpdateDuringCheckinRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update patient information during check-in

    Allows quick updates to contact information and insurance.
    Returns highlighted changes for staff review.

    Requires patient:update permission.
    """
    try:
        service = get_patient_checkin_service(db)

        result = await service.update_patient_during_checkin(
            patient_id=request.patient_id,
            phone=request.phone,
            email=request.email,
            address=request.address,
            city=request.city,
            province=request.province,
            postal_code=request.postal_code,
            bpjs_card_number=request.bpjs_card_number,
            updated_by=current_user.id,
        )

        await db.commit()

        return result

    except PatientNotFoundError as e:
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


@router.get("/verify-insurance/{patient_id}")
async def verify_insurance_status(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify current insurance status for patient

    Checks BPJS or other insurance validity.

    Requires patient:read permission.
    """
    try:
        service = get_patient_checkin_service(db)

        status = await service.verify_insurance_status(patient_id)

        return status

    except PatientNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        logger.error("Error verifying insurance: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify insurance status"
        )
