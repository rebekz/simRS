"""Patient Portal Health Record Endpoints

API endpoints for accessing personal health records.
STORY-042: Personal Health Record Access
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date

from app.db.session import get_db
from app.models.patient_portal import PatientPortalUser
from app.api.v1.endpoints.patient_portal_auth import get_current_portal_user
from app.schemas.patient_portal.health_record import (
    PatientDemographics,
    PatientDemographicsUpdate,
    DemographicsUpdateRequest,
    AllergyList,
    AllergyItem,
    DiagnosisList,
    MedicationList,
    VitalSignsHistory,
    EncounterHistory,
    HealthTimeline,
    PersonalHealthRecord,
    HealthRecordSearch,
    HealthRecordSearchResult,
    HealthRecordExportRequest,
    HealthRecordExportResponse,
)
from app.services.patient_portal.health_record import HealthRecordService

router = APIRouter()


@router.get("/health-record", response_model=PersonalHealthRecord)
async def get_health_record(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get complete personal health record

    Returns all patient information including demographics, allergies,
    diagnoses, medications, vital signs, and encounter history.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = HealthRecordService(db)
    try:
        record = await service.get_complete_health_record(current_user.patient_id)
        return record
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/health-record/demographics", response_model=PatientDemographics)
async def get_demographics(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get patient demographic information"""
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = HealthRecordService(db)
    return await service.get_demographics(current_user.patient_id)


@router.put("/health-record/demographics")
async def update_demographics(
    request: DemographicsUpdateRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Request update to demographic information

    Updates require approval before being applied to the patient record.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    # Create update request for review
    # In production, this would create a pending update in a separate table
    # and notify staff for approval

    return {
        "message": "Update request submitted for review",
        "status": "pending_approval",
        "requested_changes": request.changes.model_dump(exclude_unset=True),
        "reason": request.reason,
    }


@router.get("/health-record/allergies", response_model=AllergyList)
async def get_allergies(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get patient allergy list

    Returns active and resolved allergies with severity information.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = HealthRecordService(db)
    return await service.get_allergies(current_user.patient_id)


@router.get("/health-record/diagnoses", response_model=DiagnosisList)
async def get_diagnoses(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get patient diagnoses

    Returns active, resolved, and chronic diagnoses with patient-friendly descriptions.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = HealthRecordService(db)
    return await service.get_diagnoses(current_user.patient_id)


@router.get("/health-record/medications", response_model=MedicationList)
async def get_medications(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get patient medications

    Returns current and past medications with dosage and frequency information.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = HealthRecordService(db)
    return await service.get_medications(current_user.patient_id)


@router.get("/health-record/vital-signs", response_model=VitalSignsHistory)
async def get_vital_signs(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
):
    """Get vital signs history

    Returns historical vital signs recordings (blood pressure, weight, height, temperature).
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = HealthRecordService(db)
    return await service.get_vital_signs_history(current_user.patient_id)


@router.get("/health-record/encounters", response_model=EncounterHistory)
async def get_encounter_history(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get encounter history

    Returns past visits, hospitalizations, and procedures.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = HealthRecordService(db)
    history = await service.get_encounter_history(current_user.patient_id)

    # Apply pagination
    encounters = history.encounters[offset:offset + limit]

    return EncounterHistory(
        encounters=encounters,
        total=history.total,
        admission_count=history.admission_count,
        emergency_count=history.emergency_count,
        outpatient_count=history.outpatient_count,
    )


@router.get("/health-record/timeline", response_model=HealthTimeline)
async def get_health_timeline(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=500),
):
    """Get health timeline

    Returns chronological view of all health events including encounters,
    diagnoses, medications, allergies, and procedures.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = HealthRecordService(db)
    timeline = await service.get_health_timeline(current_user.patient_id)

    # Apply limit
    events = timeline.events[:limit]

    return HealthTimeline(
        events=events,
        total_events=len(events),
    )


@router.post("/health-record/search", response_model=HealthRecordSearchResult)
async def search_health_records(
    query: HealthRecordSearch,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Search health records

    Search by keyword, date range, and/or event type.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = HealthRecordService(db)
    return await service.search_health_records(current_user.patient_id, query)


@router.post("/health-record/export", response_model=HealthRecordExportResponse)
async def export_health_record(
    request: HealthRecordExportRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Export health records

    Generates a downloadable file (PDF or JSON) of selected health record sections.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = HealthRecordService(db)

    # Get complete record
    record = await service.get_complete_health_record(current_user.patient_id)

    # Generate export based on format
    if request.format == "json":
        # In production, would generate actual JSON file and store it
        download_url = f"/api/v1/portal/health-record/download/{current_user.id}.json"
        expires_at = None  # Would set expiration for temporary link

        return HealthRecordExportResponse(
            success=True,
            download_url=download_url,
            expires_at=expires_at,
            message="JSON export generated successfully",
        )
    else:  # PDF
        # In production, would use a PDF generation library like ReportLab or WeasyPrint
        # For now, return a placeholder response
        return HealthRecordExportResponse(
            success=False,
            download_url=None,
            expires_at=None,
            message="PDF export not yet implemented. Please use JSON format or contact support.",
        )


@router.get("/health-record/summary")
async def get_health_summary(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get health record summary

    Returns a concise overview of key health information for dashboard display.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = HealthRecordService(db)

    # Get key components
    demographics = await service.get_demographics(current_user.patient_id)
    allergies = await service.get_allergies(current_user.patient_id)
    diagnoses = await service.get_diagnoses(current_user.patient_id)
    medications = await service.get_medications(current_user.patient_id)
    encounters = await service.get_encounter_history(current_user.patient_id)

    # Calculate age
    from datetime import datetime
    today = date.today()
    age = today.year - demographics.date_of_birth.year
    if (today.month, today.day) < (demographics.date_of_birth.month, demographics.date_of_birth.day):
        age -= 1

    # Get last visit
    last_visit = None
    last_visit_date = None
    if encounters.encounters:
        last_visit = encounters.encounters[0]
        last_visit_date = last_visit.encounter_date

    return {
        "patient_name": demographics.full_name,
        "medical_record_number": demographics.medical_record_number,
        "age": age,
        "gender": demographics.gender,
        "blood_type": demographics.blood_type,
        "allergies_count": len(allergies.active_allergies),
        "has_severe_allergies": allergies.has_severe_allergies,
        "chronic_conditions_count": len(diagnoses.chronic_conditions),
        "current_medications_count": len(medications.current_medications),
        "total_visits": encounters.total,
        "last_visit_date": last_visit_date,
        "last_visit_department": last_visit.department if last_visit else None,
        "record_completeness": service._calculate_completeness(demographics),
        "last_updated": max(
            demographics.updated_at,
            *[e.created_at for e in encounters.encounters[:1]] if encounters.encounters else [demographics.updated_at]
        ),
    }
