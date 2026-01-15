"""Patient Portal Vaccination Records Endpoints

API endpoints for accessing vaccination records and immunization history.
STORY-050: Vaccination Records & Immunization History
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.models.patient_portal import PatientPortalUser
from app.api.v1.endpoints.patient_portal_auth import get_current_portal_user
from app.schemas.patient_portal.vaccinations import (
    VaccinationSummary,
    VaccinationListResponse,
    VaccinationDetailResponse,
    VaccinationStatus,
    VaccinationCertificate,
)
from app.services.patient_portal.vaccination_service import VaccinationService

router = APIRouter()


@router.get(
    "/vaccinations",
    response_model=VaccinationSummary,
    operation_id="get_vaccination_summary",
    summary="Get vaccination summary",
    description="Get complete vaccination summary including status, recent, upcoming, and overdue vaccinations",
)
async def get_vaccination_summary(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get complete vaccination summary for patient

    Returns summary with status, recent, upcoming, overdue vaccinations.

    Raises:
        HTTPException 400: If no patient record is linked to the account
        HTTPException 404: If patient is not found
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = VaccinationService(db)
    try:
        summary = await service.get_vaccination_summary(current_user.patient_id)
        return summary
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/vaccinations/list",
    response_model=VaccinationListResponse,
    operation_id="list_vaccinations",
    summary="List vaccinations",
    description="List vaccinations with optional filtering by status and pagination support",
)
async def list_vaccinations(
    status: Optional[str] = Query(
        None,
        description="Filter by vaccination status (e.g., 'administered', 'scheduled', 'missed', 'overdue')"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=100,
        description="Maximum number of records to return"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of records to skip for pagination"
    ),
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """List vaccinations with optional filtering

    Returns paginated list of vaccination records.

    Query Parameters:
        status: Optional filter for vaccination status
        limit: Maximum number of records to return (1-100, default 100)
        offset: Number of records to skip for pagination (default 0)

    Raises:
        HTTPException 400: If no patient record is linked to the account
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = VaccinationService(db)
    return await service.list_vaccinations(
        patient_id=current_user.patient_id,
        status=status,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/vaccinations/{vaccination_id}",
    response_model=VaccinationDetailResponse,
    operation_id="get_vaccination_detail",
    summary="Get vaccination detail",
    description="Get detailed information about a specific vaccination record",
)
async def get_vaccination_detail(
    vaccination_id: int,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about specific vaccination

    Returns detailed vaccination record with certificate availability.

    Path Parameters:
        vaccination_id: Unique identifier of the vaccination record

    Raises:
        HTTPException 400: If no patient record is linked to the account
        HTTPException 404: If vaccination record is not found
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = VaccinationService(db)
    try:
        detail = await service.get_vaccination_detail(
            patient_id=current_user.patient_id,
            vaccination_id=vaccination_id,
        )
        return detail
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/vaccinations/status",
    response_model=VaccinationStatus,
    operation_id="get_vaccination_status",
    summary="Get vaccination status",
    description="Get vaccination status statistics including complete, incomplete, overdue, and upcoming counts",
)
async def get_vaccination_status(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get vaccination status statistics

    Returns counts and status information for all vaccinations.

    Raises:
        HTTPException 400: If no patient record is linked to the account
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = VaccinationService(db)
    status_info = await service.get_vaccination_status(current_user.patient_id)
    return status_info


@router.post(
    "/vaccinations/{vaccination_id}/certificate",
    response_model=VaccinationCertificate,
    operation_id="generate_vaccination_certificate",
    summary="Generate vaccination certificate",
    description="Generate an official vaccination certificate document for download",
)
async def generate_vaccination_certificate(
    vaccination_id: int,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate vaccination certificate (mock)

    Generates and returns certificate URLs for download.

    Path Parameters:
        vaccination_id: Unique identifier of the vaccination record

    Returns:
        VaccinationCertificate with download URLs for the certificate and QR code

    Raises:
        HTTPException 400: If no patient record is linked to the account
        HTTPException 400: If vaccination is incomplete and certificate cannot be generated
        HTTPException 404: If vaccination record is not found

    Notes:
        Certificate can only be generated for completed vaccination regimens.
        This is a mock implementation - in production, would generate actual PDF documents.
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    service = VaccinationService(db)
    try:
        certificate = await service.generate_vaccination_certificate(
            patient_id=current_user.patient_id,
            vaccination_id=vaccination_id,
        )
        return certificate
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
