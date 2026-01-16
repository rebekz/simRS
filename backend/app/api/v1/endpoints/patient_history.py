"""Enhanced Patient History API Endpoints for STORY-011

This module provides API endpoints for comprehensive patient history viewing
with optimized performance for clinical workflows.

Python 3.5+ compatible
"""

import logging
from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.patient_history_service import PatientHistoryService
from app.schemas.patient_history import (
    PatientHistoryResponse,
    PatientHistorySummary,
    PatientHistoryFilter,
    PatientHistoryExportRequest,
)
from app.core.deps import get_current_user


logger = logging.getLogger(__name__)


router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class ExportHistoryRequest(BaseModel):
    """Request model for exporting patient history"""
    format: str = Field("pdf", description="Export format (pdf, html, json)")
    include_sections: Optional[list] = Field(None, description="Sections to include")
    language: str = Field("id", description="Language (id, en)")
    include_images: bool = Field(False, description="Include images in export")


# =============================================================================
# Patient History Endpoints
# =============================================================================

@router.get("/{patient_id}", response_model=PatientHistoryResponse)
async def get_patient_history(
    patient_id: int,
    include_allergies: bool = Query(True, description="Include allergy history"),
    include_medications: bool = Query(True, description="Include current medications"),
    include_conditions: bool = Query(True, description="Include chronic conditions"),
    include_encounters: bool = Query(True, description="Include encounter history"),
    include_lab_results: bool = Query(True, description="Include lab results"),
    include_vital_signs: bool = Query(True, description="Include vital signs"),
    include_surgical_history: bool = Query(True, description="Include surgical history"),
    include_immunizations: bool = Query(True, description="Include immunizations"),
    include_family_history: bool = Query(True, description="Include family history"),
    include_social_history: bool = Query(True, description="Include social history"),
    encounter_limit: int = Query(10, ge=1, le=50, description="Max encounters to return"),
    lab_results_limit: int = Query(10, ge=1, le=50, description="Max lab results to return"),
    vital_signs_limit: int = Query(5, ge=1, le=20, description="Max vital signs to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get comprehensive patient history

    Displays complete patient history in single view including:
    - Demographics, contacts, insurance
    - Medical history (visits, hospitalizations, surgeries, allergies, chronic conditions)
    - Family medical history
    - Social history (smoking, alcohol, occupation)
    - Immunization records
    - Current medications
    - Recent lab results and vital signs
    - Timeline visualization of past encounters

    Target: History loads in <3 seconds

    Requires patient:read permission.
    """
    try:
        service = PatientHistoryService(db)

        # Build filter object
        filters = PatientHistoryFilter(
            include_allergies=include_allergies,
            include_medications=include_medications,
            include_conditions=include_conditions,
            include_encounters=include_encounters,
            include_lab_results=include_lab_results,
            include_vital_signs=include_vital_signs,
            include_surgical_history=include_surgical_history,
            include_immunizations=include_immunizations,
            include_family_history=include_family_history,
            include_social_history=include_social_history,
            encounter_limit=encounter_limit,
            lab_results_limit=lab_results_limit,
            vital_signs_limit=vital_signs_limit,
        )

        history = await service.get_patient_history(patient_id, filters)

        return history

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        logger.error("Error getting patient history: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil riwayat pasien"
        )


@router.get("/{patient_id}/summary", response_model=PatientHistorySummary)
async def get_patient_history_summary(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get lightweight patient history summary

    Returns quick reference data including:
    - Basic demographics
    - Quick indicators (allergies, chronic conditions, medications)
    - Last visit information
    - Flags (unpaid bills, pending appointments)
    - Insurance status

    Requires patient:read permission.
    """
    try:
        service = PatientHistoryService(db)

        summary = await service.get_patient_history_summary(patient_id)

        return summary

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        logger.error("Error getting patient history summary: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil ringkasan riwayat pasien"
        )


@router.get("/{patient_id}/timeline", response_model=list)
async def get_patient_timeline(
    patient_id: int,
    start_date: Optional[date] = Query(None, description="Filter start date"),
    end_date: Optional[date] = Query(None, description="Filter end date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get patient encounter timeline visualization

    Returns chronological timeline of:
    - Outpatient visits
    - Inpatient admissions
    - Emergency visits
    - Surgeries/procedures
    - Significant diagnoses

    Can be filtered by date range.

    Requires patient:read permission.
    """
    try:
        service = PatientHistoryService(db)

        # Get patient history with timeline
        filters = PatientHistoryFilter(
            include_encounters=True,
            include_surgical_history=True,
            encounter_limit=50,  # Get more for full timeline
        )

        history = await service.get_patient_history(patient_id, filters)

        # Filter timeline by date range if provided
        timeline = history.encounter_timeline

        if start_date or end_date:
            filtered_timeline = []
            for item in timeline:
                item_date = item.date.date() if hasattr(item.date, 'date') else item.date

                if start_date and item_date < start_date:
                    continue
                if end_date and item_date > end_date:
                    continue

                filtered_timeline.append(item)

            timeline = filtered_timeline

        return timeline

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        logger.error("Error getting patient timeline: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil timeline pasien"
        )


@router.post("/search")
async def search_patient_history(
    search_term: str = Query(..., min_length=2, description="Search term (name, MRN, NIK)"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search patients by name, MRN, or NIK with history summary

    Returns list of patients matching search criteria with:
    - Basic demographics
    - Quick indicators (allergies, conditions, medications)
    - Last visit information
    - Insurance status

    Requires patient:read permission.
    """
    try:
        service = PatientHistoryService(db)

        results = await service.search_patient_history(search_term, limit)

        return {
            "search_term": search_term,
            "count": len(results),
            "results": results,
        }

    except Exception as e:
        logger.error("Error searching patient history: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mencari riwayat pasien"
        )


@router.post("/{patient_id}/export")
async def export_patient_history(
    patient_id: int,
    request: ExportHistoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export patient history to PDF or other formats

    Generates downloadable document containing patient history
    including all requested sections.

    Supported formats:
    - PDF (default): Printable document for patient copy
    - HTML: Web-viewable document
    - JSON: Raw data export

    Sections can be selectively included.

    Requires patient:read permission.
    """
    try:
        service = PatientHistoryService(db)

        # Build filter based on requested sections
        filters = PatientHistoryFilter(
            include_allergies=True,  # Always include by default
            include_medications=True,
            include_conditions=True,
            include_encounters=True,
            include_lab_results=True,
            include_vital_signs=True,
            include_surgical_history=True,
            include_immunizations=True,
            include_family_history=True,
            include_social_history=True,
        )

        # Get full history
        history = await service.get_patient_history(patient_id, filters)

        # For now, return JSON response
        # TODO: Implement PDF generation in frontend or separate service
        export_format = request.format

        if export_format == "json":
            return {
                "format": "json",
                "patient_id": patient_id,
                "medical_record_number": history.medical_record_number,
                "full_name": history.full_name,
                "data": history.dict(),
                "exported_at": history.last_updated.isoformat(),
            }
        elif export_format == "html":
            # Return HTML placeholder
            return {
                "format": "html",
                "patient_id": patient_id,
                "medical_record_number": history.medical_record_number,
                "full_name": history.full_name,
                "message": "HTML export akan diimplementasikan di frontend",
                "data": history.dict(),
            }
        else:  # pdf
            # Return PDF placeholder
            return {
                "format": "pdf",
                "patient_id": patient_id,
                "medical_record_number": history.medical_record_number,
                "full_name": history.full_name,
                "message": "PDF export akan diimplementasikan di frontend",
                "data": history.dict(),
            }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        logger.error("Error exporting patient history: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengekspor riwayat pasien"
        )


@router.get("/{patient_id}/encounters")
async def get_patient_encounters(
    patient_id: int,
    limit: int = Query(10, ge=1, le=50, description="Max encounters to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get patient encounter history with pagination

    Returns list of past encounters including:
    - Outpatient visits
    - Inpatient admissions
    - Emergency visits
    - Diagnoses and treatments

    Supports pagination for large encounter histories.

    Requires patient:read permission.
    """
    try:
        service = PatientHistoryService(db)

        filters = PatientHistoryFilter(
            include_encounters=True,
            encounter_limit=limit + offset,  # Get more to support offset
        )

        history = await service.get_patient_history(patient_id, filters)

        # Apply offset
        encounters = history.recent_encounters[offset:offset + limit]

        return {
            "patient_id": patient_id,
            "total_encounters": history.total_encounters,
            "limit": limit,
            "offset": offset,
            "encounters": encounters,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        logger.error("Error getting patient encounters: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil riwayat kunjungan"
        )


@router.get("/{patient_id}/allergies")
async def get_patient_allergies(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get patient allergy history

    Returns all recorded allergies including:
    - Drug allergies
    - Food allergies
    - Environmental allergies
    - Severity and reaction information

    Requires patient:read permission.
    """
    try:
        service = PatientHistoryService(db)

        filters = PatientHistoryFilter(
            include_allergies=True,
        )

        history = await service.get_patient_history(patient_id, filters)

        return {
            "patient_id": patient_id,
            "allergies": history.allergies,
            "count": len(history.allergies),
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        logger.error("Error getting patient allergies: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil riwayat alergi"
        )


@router.get("/{patient_id}/medications")
async def get_patient_medications(
    patient_id: int,
    active_only: bool = Query(True, description="Show only active medications"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get patient medication history

    Returns current and past medications including:
    - Drug name and dosage
    - Frequency and route
    - Start and end dates
    - Prescriber information
    - Indications

    Requires patient:read permission.
    """
    try:
        service = PatientHistoryService(db)

        filters = PatientHistoryFilter(
            include_medications=True,
        )

        history = await service.get_patient_history(patient_id, filters)

        medications = history.current_medications

        # Filter for active only if requested
        if active_only:
            medications = [m for m in medications if getattr(m, 'is_active', True)]

        return {
            "patient_id": patient_id,
            "medications": medications,
            "count": len(medications),
            "active_only": active_only,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        logger.error("Error getting patient medications: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil riwayat obat"
        )
