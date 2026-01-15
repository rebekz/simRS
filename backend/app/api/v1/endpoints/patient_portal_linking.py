"""Patient Portal Patient Linking Endpoints

API endpoints for linking portal accounts to existing patient records.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.models.patient import Patient
from app.models.patient_portal import PatientPortalUser
from app.schemas.patient_portal.patient_link import (
    PatientLinkRequest,
    PatientLinkResponse,
    ExistingPatientSearchRequest,
    ExistingPatientSearchResponse,
    PatientSummary,
    BPJSCardLinkRequest,
    MedicalRecordNumberSearchRequest,
    MedicalRecordNumberSearchResponse,
    NewPatientRecordRequest,
    NewPatientRecordResponse,
)
from app.schemas.patient_portal.profile import PatientPortalProfile
from app.services.patient_portal.patient_linking import PatientLinkingService
from app.api.v1.endpoints.patient_portal_auth import get_current_portal_user

router = APIRouter()


@router.post("/link/search", response_model=ExistingPatientSearchResponse)
async def search_existing_patient(
    request: ExistingPatientSearchRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Search for existing patient records by NIK or BPJS

    Allows users to find their existing patient record to link to their portal account.
    """
    # Check if already linked
    if current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already linked to a patient record",
        )

    service = PatientLinkingService(db)
    found, patients, message = await service.search_patients(
        search_type=request.search_type,
        nik=request.nik,
        bpjs_card_number=request.bpjs_card_number,
        include_inactive=request.include_inactive,
    )

    patient_summaries = [
        PatientSummary(
            patient_id=p.id,
            medical_record_number=p.medical_record_number,
            full_name=p.full_name,
            date_of_birth=p.date_of_birth,
            gender=p.gender.value,
            phone=p.phone,
            email=p.email,
            is_active=p.is_active,
            bpjs_card_number=p.bpjs_card_number,
        )
        for p in patients
    ]

    return ExistingPatientSearchResponse(
        found=found,
        patients=patient_summaries,
        message=message,
    )


@router.post("/link/by-nik", response_model=PatientLinkResponse)
async def link_by_nik(
    request: PatientLinkRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Link portal account to patient using NIK

    Links the portal user to an existing patient record using NIK verification.
    """
    if current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already linked to a patient record",
        )

    if request.link_method != "nik":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid link method for this endpoint",
        )

    service = PatientLinkingService(db)
    patient = await service.find_patient_by_nik(
        nik=request.nik,
        date_of_birth=request.date_of_birth,
    )

    if not patient:
        return PatientLinkResponse(
            success=False,
            message="No patient found with the provided NIK and date of birth",
            patient_id=None,
            is_verified=False,
        )

    # Verify eligibility
    eligible, msg = await service.verify_patient_link_eligibility(current_user.id, patient.id)
    if not eligible:
        return PatientLinkResponse(
            success=False,
            message=msg,
            patient_id=None,
            is_verified=False,
        )

    # Link
    success, message = await service.link_portal_user_to_patient(current_user.id, patient.id)

    await db.commit()

    return PatientLinkResponse(
        success=success,
        message=message,
        patient_id=patient.id,
        medical_record_number=patient.medical_record_number if success else None,
        patient_name=patient.full_name if success else None,
        date_of_birth=patient.date_of_birth if success else None,
        is_verified=True,
        requires_additional_verification=False,
    )


@router.post("/link/by-mrn", response_model=PatientLinkResponse)
async def link_by_mrn(
    mrn: str,
    date_of_birth: Optional[str] = None,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Link portal account to patient using MRN

    Links the portal user to an existing patient record using Medical Record Number.
    """
    if current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already linked to a patient record",
        )

    service = PatientLinkingService(db)

    # Parse date of birth if provided
    dob = None
    if date_of_birth:
        from datetime import datetime
        dob = datetime.fromisoformat(date_of_birth).date()

    patient = await service.find_patient_by_mrn(mrn=mrn, date_of_birth=dob)

    if not patient:
        return PatientLinkResponse(
            success=False,
            message="No patient found with the provided MRN",
            patient_id=None,
            is_verified=False,
        )

    # Verify eligibility
    eligible, msg = await service.verify_patient_link_eligibility(current_user.id, patient.id)
    if not eligible:
        return PatientLinkResponse(
            success=False,
            message=msg,
            patient_id=None,
            is_verified=False,
        )

    # Link
    success, message = await service.link_portal_user_to_patient(current_user.id, patient.id)

    await db.commit()

    return PatientLinkResponse(
        success=success,
        message=message,
        patient_id=patient.id,
        medical_record_number=patient.medical_record_number if success else None,
        patient_name=patient.full_name if success else None,
        date_of_birth=patient.date_of_birth if success else None,
        is_verified=True,
        requires_additional_verification=False,
    )


@router.post("/link/by-bpjs", response_model=PatientLinkResponse)
async def link_by_bpjs(
    request: BPJSCardLinkRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Link portal account to patient using BPJS card

    Links the portal user to an existing patient record using BPJS card number.
    Date of birth is required for verification.
    """
    if current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already linked to a patient record",
        )

    service = PatientLinkingService(db)
    patient = await service.find_patient_by_bpjs(
        bpjs_card_number=request.bpjs_card_number,
        date_of_birth=request.date_of_birth,
    )

    if not patient:
        return PatientLinkResponse(
            success=False,
            message="No patient found with the provided BPJS card number and date of birth",
            patient_id=None,
            is_verified=False,
        )

    # Verify eligibility
    eligible, msg = await service.verify_patient_link_eligibility(current_user.id, patient.id)
    if not eligible:
        return PatientLinkResponse(
            success=False,
            message=msg,
            patient_id=None,
            is_verified=False,
        )

    # Link
    success, message = await service.link_portal_user_to_patient(current_user.id, patient.id)

    await db.commit()

    return PatientLinkResponse(
        success=success,
        message=message,
        patient_id=patient.id,
        medical_record_number=patient.medical_record_number if success else None,
        patient_name=patient.full_name if success else None,
        date_of_birth=patient.date_of_birth if success else None,
        is_verified=True,
        requires_additional_verification=False,
    )


@router.post("/link/create-new", response_model=NewPatientRecordResponse)
async def create_new_patient_record(
    patient_data: NewPatientRecordRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Create new patient record and link to portal account

    Creates a new patient record for users who don't have an existing record.
    """
    if current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already linked to a patient record",
        )

    service = PatientLinkingService(db)
    success, message, patient = await service.create_new_patient_and_link(
        portal_user_id=current_user.id,
        patient_data=patient_data.model_dump(),
    )

    if success and patient:
        await db.commit()
        return NewPatientRecordResponse(
            success=True,
            message=message,
            patient_id=patient.id,
            medical_record_number=patient.medical_record_number,
        )
    else:
        return NewPatientRecordResponse(
            success=False,
            message=message,
            patient_id=None,
            medical_record_number=None,
        )


@router.get("/link/status", response_model=PatientPortalProfile)
async def get_link_status(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
):
    """Get current patient link status

    Returns information about the linked patient record.
    """
    return PatientPortalProfile(
        id=current_user.id,
        email=current_user.email,
        phone=current_user.phone,
        patient_id=current_user.patient_id,
        is_active=current_user.is_active,
        is_email_verified=current_user.is_email_verified,
        is_phone_verified=current_user.is_phone_verified,
        is_identity_verified=current_user.is_identity_verified,
        patient_name=current_user.patient.full_name if current_user.patient else None,
        medical_record_number=current_user.patient.medical_record_number if current_user.patient else None,
        date_of_birth=current_user.patient.date_of_birth if current_user.patient else None,
        mfa_enabled=current_user.mfa_enabled,
        has_security_questions=bool(current_user.security_question_1),
        last_login=current_user.last_login,
        created_at=current_user.created_at,
    )
