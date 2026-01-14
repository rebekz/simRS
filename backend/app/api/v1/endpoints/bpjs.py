"""BPJS VClaim API endpoints for STORY-022: BPJS VClaim API Integration

This module provides REST API endpoints for BPJS VClaim integration,
including eligibility checks and SEP management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from app.db.session import get_db
from app.core.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.bpjs import (
    BPJSEligibilityRequest,
    BPJSEligibilityResponse,
    BPJSSEPCreateRequest,
    BPJSSEPCreateResponse,
    BPJSSEPDeleteRequest,
    BPJSSEPDeleteResponse,
    BPJSErrorResponse,
)
from app.services.bpjs_vclaim import BPJSVClaimClient, BPJSVClaimError

router = APIRouter()


async def get_bpjs_client() -> BPJSVClaimClient:
    """Dependency to get BPJS VClaim client instance."""
    return BPJSVClaimClient()


@router.post("/eligibility", response_model=BPJSEligibilityResponse)
async def check_eligibility(
    request: BPJSEligibilityRequest,
    bpjs_client: BPJSVClaimClient = Depends(get_bpjs_client),
    current_user: User = Depends(require_permission("bpjs", "read"))
):
    """
    Check BPJS member eligibility.

    Args:
        request: Eligibility check request with card number or NIK
        bpjs_client: BPJS VClaim API client
        current_user: Authenticated user with bpjs:read permission

    Returns:
        BPJS eligibility information including participant details

    Raises:
        HTTPException 400: If validation error
        HTTPException 502: If BPJS API error
    """
    try:
        # Check eligibility by card number or NIK
        if request.card_number:
            result = await bpjs_client.check_eligibility_by_card(
                card_number=request.card_number,
                sep_date=request.sep_date
            )
        elif request.nik:
            result = await bpjs_client.check_eligibility_by_nik(
                nik=request.nik,
                sep_date=request.sep_date
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either card_number or nik must be provided"
            )

        return result

    except BPJSVClaimError as e:
        # Check if this is a BPJS API error (not eligible, etc)
        if " tidak aktif" in e.message.lower() or " tidak ditemukan" in e.message.lower():
            # Return eligibility response with is_eligible=False
            return BPJSEligibilityResponse(
                is_eligible=False,
                message=e.message,
                peserta=None
            )

        # For other BPJS errors
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"BPJS API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/sep", response_model=BPJSSEPCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_sep(
    request: BPJSSEPCreateRequest,
    bpjs_client: BPJSVClaimClient = Depends(get_bpjs_client),
    current_user: User = Depends(require_permission("bpjs", "create"))
):
    """
    Create SEP (Surat Eligibilitas Peserta) for BPJS claim.

    Args:
        request: SEP creation request with all required fields
        bpjs_client: BPJS VClaim API client
        current_user: Authenticated user with bpjs:create permission

    Returns:
        Created SEP information

    Raises:
        HTTPException 400: If validation error
        HTTPException 502: If BPJS API error
    """
    try:
        result = await bpjs_client.create_sep(request)
        return result

    except BPJSVClaimError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"BPJS API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.delete("/sep/{sep_number}", response_model=BPJSSEPDeleteResponse)
async def delete_sep(
    sep_number: str,
    user: str = Query(..., description="User requesting deletion"),
    bpjs_client: BPJSVClaimClient = Depends(get_bpjs_client),
    current_user: User = Depends(require_permission("bpjs", "delete"))
):
    """
    Delete SEP (Surat Eligibilitas Peserta).

    Args:
        sep_number: SEP number to delete
        user: User requesting the deletion
        bpjs_client: BPJS VClaim API client
        current_user: Authenticated user with bpjs:delete permission

    Returns:
        Deletion confirmation

    Raises:
        HTTPException 404: If SEP not found
        HTTPException 502: If BPJS API error
    """
    try:
        request = BPJSSEPDeleteRequest(sep_number=sep_number, user=user)
        result = await bpjs_client.delete_sep(request)
        return result

    except BPJSVClaimError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"BPJS API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/polyclinics")
async def get_polyclinics(
    bpjs_client: BPJSVClaimClient = Depends(get_bpjs_client),
    current_user: User = Depends(require_permission("bpjs", "read"))
):
    """
    Get list of BPJS polyclinics.

    Args:
        bpjs_client: BPJS VClaim API client
        current_user: Authenticated user with bpjs:read permission

    Returns:
        List of polyclinics

    Raises:
        HTTPException 502: If BPJS API error
    """
    try:
        result = await bpjs_client.get_polyclinics()
        return result

    except BPJSVClaimError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"BPJS API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/facilities")
async def get_facilities(
    bpjs_client: BPJSVClaimClient = Depends(get_bpjs_client),
    current_user: User = Depends(require_permission("bpjs", "read"))
):
    """
    Get list of BPJS healthcare facilities.

    Args:
        bpjs_client: BPJS VClaim API client
        current_user: Authenticated user with bpjs:read permission

    Returns:
        List of healthcare facilities

    Raises:
        HTTPException 502: If BPJS API error
    """
    try:
        result = await bpjs_client.get_facilities()
        return result

    except BPJSVClaimError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"BPJS API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/diagnoses")
async def get_diagnoses(
    search: Optional[str] = Query(None, description="Search term for diagnosis"),
    bpjs_client: BPJSVClaimClient = Depends(get_bpjs_client),
    current_user: User = Depends(require_permission("bpjs", "read"))
):
    """
    Get list of BPJS diagnoses (ICD-10).

    Args:
        search: Optional search term
        bpjs_client: BPJS VClaim API client
        current_user: Authenticated user with bpjs:read permission

    Returns:
        List of diagnoses

    Raises:
        HTTPException 502: If BPJS API error
    """
    try:
        result = await bpjs_client.get_diagnoses(search=search)
        return result

    except BPJSVClaimError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"BPJS API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/doctors")
async def get_doctors(
    ppk_pelayanan: Optional[str] = Query(None, description="Healthcare facility code"),
    polyclinic: Optional[str] = Query(None, description="Polyclinic code"),
    bpjs_client: BPJSVClaimClient = Depends(get_bpjs_client),
    current_user: User = Depends(require_permission("bpjs", "read"))
):
    """
    Get list of BPJS doctors.

    Args:
        ppk_pelayanan: Healthcare facility code
        polyclinic: Polyclinic code
        bpjs_client: BPJS VClaim API client
        current_user: Authenticated user with bpjs:read permission

    Returns:
        List of doctors

    Raises:
        HTTPException 502: If BPJS API error
    """
    try:
        result = await bpjs_client.get_doctors(
            ppk_pelayanan=ppk_pelayanan,
            polyclinic=polyclinic
        )
        return result

    except BPJSVClaimError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"BPJS API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
