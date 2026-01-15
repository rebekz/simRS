"""PACS (Picture Archiving and Communication System) Integration API Endpoints for STORY-024-04

This module provides API endpoints for:
- PACS worklist management
- Study tracking and status
- DICOM image retrieval
- PACS configuration and mapping

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user, get_current_admin_user
from app.services.pacs_integration import get_pacs_integration_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class PACSWorklistCreateRequest(BaseModel):
    """Request to create worklist entry"""
    radiology_order_id: int = Field(..., description="Radiology order ID")


class PACSWorklistEntry(BaseModel):
    """Worklist entry response"""
    worklist_id: str
    accession_number: str
    study_instance_uid: str
    modality: str
    scheduled_date_time: str
    patient_id_dicom: str
    patient_name_dicom: str
    requested_procedure_description: str
    status: str
    performed: bool


class PACSStudyCreateRequest(BaseModel):
    """Request to create PACS study"""
    radiology_order_id: int = Field(..., description="Radiology order ID")
    study_instance_uid: str = Field(..., description="DICOM Study Instance UID")
    study_description: Optional[str] = Field(None, description="Study description")
    study_date: Optional[str] = Field(None, description="Study date (ISO format)")
    modality: str = Field(..., description="DICOM modality")
    body_part_examined: Optional[str] = Field(None, description="Body part examined")
    performing_physician: Optional[str] = Field(None, description="Performing physician")
    series_count: int = Field(0, description="Number of series")


class PACSSeriesInfo(BaseModel):
    """Series information"""
    series_id: str
    series_instance_uid: str
    modality: str
    series_description: Optional[str]
    instance_count: int


class PACSStudyResponse(BaseModel):
    """Study response"""
    study_id: str
    accession_number: str
    study_instance_uid: str
    status: str
    modality: str
    study_description: Optional[str]
    study_date: Optional[str]
    series_count: int
    instance_count: int
    has_images: bool
    series: List[PACSSeriesInfo]


class PACSMappingCreateRequest(BaseModel):
    """Request to create PACS mapping"""
    mapping_type: str = Field(..., description="Mapping type (modality, station, physician)")
    simrs_code: str = Field(..., description="SIMRS code")
    simrs_name: str = Field(..., description="SIMRS name")
    pacs_code: str = Field(..., description="PACS/AE title")
    pacs_name: str = Field(..., description="PACS name")


# =============================================================================
# Worklist Management Endpoints
# =============================================================================

@router.post("/worklist", status_code=status.HTTP_201_CREATED)
async def create_worklist_entry(
    request: PACSWorklistCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create PACS worklist entry for radiology order"""
    try:
        service = get_pacs_integration_service(db)

        result = await service.create_worklist_entry(
            radiology_order_id=request.radiology_order_id
        )

        return result

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error creating worklist entry: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create worklist entry"
        )


@router.get("/worklist", response_model=List[PACSWorklistEntry])
async def get_worklist_entries(
    modality: Optional[str] = Query(None, description="Filter by modality (CT, MR, US, etc.)"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    performed: Optional[bool] = Query(None, description="Filter by performed status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get PACS worklist entries with filtering"""
    try:
        service = get_pacs_integration_service(db)

        entries = await service.get_worklist_entries(
            modality=modality,
            date=date,
            performed=performed
        )

        return entries

    except Exception as e:
        logger.error("Error getting worklist entries: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get worklist entries"
        )


# =============================================================================
# Study Management Endpoints
# =============================================================================

@router.post("/studies", status_code=status.HTTP_201_CREATED)
async def create_pacs_study(
    request: PACSStudyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create PACS study tracking record"""
    try:
        service = get_pacs_integration_service(db)

        # Build study metadata
        study_metadata = {
            "study_instance_uid": request.study_instance_uid,
            "study_description": request.study_description,
            "study_date": request.study_date,
            "modality": request.modality,
            "body_part_examined": request.body_part_examined,
            "performing_physician": request.performing_physician,
            "series_count": request.series_count
        }

        result = await service.create_study(
            radiology_order_id=request.radiology_order_id,
            study_metadata=study_metadata
        )

        return result

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error creating PACS study: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create PACS study"
        )


@router.get("/studies/{study_id}", response_model=PACSStudyResponse)
async def get_pacs_study_status(
    study_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get PACS study status by study ID"""
    try:
        service = get_pacs_integration_service(db)

        result = await service.get_study_status(study_id)

        return result

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error getting PACS study status: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get study status"
        )


@router.get("/studies")
async def list_pacs_studies(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    modality: Optional[str] = Query(None, description="Filter by modality"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List PACS studies with filtering"""
    try:
        from app.models.pacs_integration import PACSStudy
        from sqlalchemy import select, func, and_

        # Build filters
        filters = []

        if patient_id:
            filters.append(PACSStudy.patient_id == patient_id)
        if modality:
            filters.append(PACSStudy.modality == modality.upper())
        if status:
            filters.append(PACSStudy.status == status)
        if start_date:
            filters.append(PACSStudy.created_at >= start_date)
        if end_date:
            filters.append(PACSStudy.created_at <= end_date)

        # Get total count
        count_query = select(func.count(PACSStudy.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Get studies with pagination
        offset = (page - 1) * per_page
        query = select(PACSStudy)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(PACSStudy.created_at.desc()).limit(per_page).offset(offset)

        result = await db.execute(query)
        studies = result.scalars().all()

        # Build response
        study_list = [
            {
                "study_id": s.study_id,
                "accession_number": s.accession_number,
                "study_instance_uid": s.study_instance_uid,
                "patient_id": s.patient_id,
                "modality": s.modality,
                "study_description": s.study_description,
                "status": s.status,
                "study_date": s.study_date.isoformat() if s.study_date else None,
                "series_count": s.series_count,
                "instance_count": s.instance_count,
                "has_images": s.has_images
            }
            for s in studies
        ]

        return {
            "studies": study_list,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 0
        }

    except Exception as e:
        logger.error("Error listing PACS studies: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list studies"
        )


# =============================================================================
# Configuration Endpoints (Admin)
# =============================================================================

@router.post("/mappings", status_code=status.HTTP_201_CREATED)
async def create_pacs_mapping(
    request: PACSMappingCreateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create PACS code mapping (admin only)"""
    try:
        service = get_pacs_integration_service(db)

        result = await service.create_mapping(
            mapping_type=request.mapping_type,
            simrs_code=request.simrs_code,
            simrs_name=request.simrs_name,
            pacs_code=request.pacs_code,
            pacs_name=request.pacs_name
        )

        return result

    except Exception as e:
        logger.error("Error creating PACS mapping: {}".format(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create PACS mapping"
        )


# =============================================================================
# Statistics Endpoints
# =============================================================================

@router.get("/statistics")
async def get_pacs_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get PACS integration statistics"""
    try:
        from app.models.pacs_integration import PACSStudy, PACSStudyStatus
        from sqlalchemy import select, func

        # Get study counts by status
        status_query = select(
            PACSStudy.status,
            func.count(PACSStudy.id).label("count")
        ).group_by(PACSStudy.status)

        status_result = await db.execute(status_query)
        status_counts = {row[0]: row[1] for row in status_result.all()}

        # Get total studies
        total_query = select(func.count(PACSStudy.id))
        total_result = await db.execute(total_query)
        total_studies = total_result.scalar() or 0

        # Get total series
        from app.models.pacs_integration import DICOMSeries
        series_query = select(func.count(DICOMSeries.id))
        series_result = await db.execute(series_query)
        total_series = series_result.scalar() or 0

        # Get total instances
        from app.models.pacs_integration import DICOMInstance
        instance_query = select(func.count(DICOMInstance.id))
        instance_result = await db.execute(instance_query)
        total_instances = instance_result.scalar() or 0

        # Get modality breakdown
        modality_query = select(
            PACSStudy.modality,
            func.count(PACSStudy.id).label("count")
        ).group_by(PACSStudy.modality)

        modality_result = await db.execute(modality_query)
        modality_counts = {row[0]: row[1] for row in modality_result.all()}

        return {
            "total_studies": total_studies,
            "total_series": total_series,
            "total_instances": total_instances,
            "status_counts": status_counts,
            "modality_counts": modality_counts,
            "summary": {
                "scheduled": status_counts.get(PACSStudyStatus.SCHEDULED, 0),
                "in_progress": status_counts.get(PACSStudyStatus.IN_PROGRESS, 0),
                "completed": status_counts.get(PACSStudyStatus.COMPLETED, 0),
                "cancelled": status_counts.get(PACSStudyStatus.CANCELLED, 0),
                "error": status_counts.get(PACSStudyStatus.ERROR, 0),
            }
        }

    except Exception as e:
        logger.error("Error getting PACS statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
