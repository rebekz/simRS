"""Enhanced BPJS Eligibility Verification API Endpoints for STORY-008

This module provides API endpoints for BPJS eligibility verification with caching,
history tracking, and manual override capabilities.

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
from app.services.bpjs_eligibility_verification import (
    get_bpjs_eligibility_service,
    EligibilityCheckError,
)
from app.core.deps import get_current_user, get_current_admin_user


logger = logging.getLogger(__name__)


router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class VerifyByCardRequest(BaseModel):
    """Request model for verifying eligibility by card number"""
    card_number: str = Field(..., description="BPJS card number (13 digits)", min_length=13, max_length=13)
    sep_date: date = Field(..., description="SEP date (YYYY-MM-DD)")
    patient_id: Optional[int] = Field(None, description="Patient ID (for history tracking)")
    use_cache: bool = Field(True, description="Use cached results if available")


class VerifyByNIKRequest(BaseModel):
    """Request model for verifying eligibility by NIK"""
    nik: str = Field(..., description="NIK (16 digits)", min_length=16, max_length=16)
    sep_date: date = Field(..., description="SEP date (YYYY-MM-DD)")
    patient_id: Optional[int] = Field(None, description="Patient ID (for history tracking)")
    use_cache: bool = Field(True, description="Use cached results if available")


class ManualOverrideRequest(BaseModel):
    """Request model for manual eligibility override"""
    patient_id: int = Field(..., description="Patient ID")
    card_number: Optional[str] = Field(None, description="BPJS card number")
    nik: Optional[str] = Field(None, description="NIK")
    is_eligible: bool = Field(True, description="Eligibility status")
    reason: str = Field(..., description="Override reason")
    approved_by: Optional[int] = Field(None, description="User ID approving override (admin)")


# =============================================================================
# BPJS Eligibility Verification Endpoints
# =============================================================================

@router.post("/verify/by-card", status_code=status.HTTP_200_OK)
async def verify_eligibility_by_card(
    request: VerifyByCardRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify BPJS eligibility by card number

    Target: Verification completes in <5 seconds

    Requires bpjs:read permission.
    """
    try:
        service = get_bpjs_eligibility_service(db)

        result = await service.verify_eligibility_by_card(
            card_number=request.card_number,
            sep_date=request.sep_date,
            patient_id=request.patient_id,
            use_cache=request.use_cache,
            verified_by=current_user.id,
        )

        await db.commit()

        return result

    except EligibilityCheckError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error verifying eligibility by card: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memverifikasi eligibility BPJS"
        )


@router.post("/verify/by-nik", status_code=status.HTTP_200_OK)
async def verify_eligibility_by_nik(
    request: VerifyByNIKRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify BPJS eligibility by NIK

    Target: Verification completes in <5 seconds

    Requires bpjs:read permission.
    """
    try:
        service = get_bpjs_eligibility_service(db)

        result = await service.verify_eligibility_by_nik(
            nik=request.nik,
            sep_date=request.sep_date,
            patient_id=request.patient_id,
            use_cache=request.use_cache,
            verified_by=current_user.id,
        )

        await db.commit()

        return result

    except EligibilityCheckError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error verifying eligibility by NIK: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memverifikasi eligibility BPJS"
        )


@router.get("/verify/by-card")
async def verify_eligibility_by_card_get(
    card_number: str = Query(..., description="BPJS card number (13 digits)", min_length=13, max_length=13),
    sep_date: date = Query(..., description="SEP date (YYYY-MM-DD)"),
    patient_id: Optional[int] = Query(None, description="Patient ID"),
    use_cache: bool = Query(True, description="Use cached results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify BPJS eligibility by card number (GET method)

    Target: Verification completes in <5 seconds

    Requires bpjs:read permission.
    """
    try:
        service = get_bpjs_eligibility_service(db)

        result = await service.verify_eligibility_by_card(
            card_number=card_number,
            sep_date=sep_date,
            patient_id=patient_id,
            use_cache=use_cache,
            verified_by=current_user.id,
        )

        await db.commit()

        return result

    except EligibilityCheckError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error verifying eligibility by card: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memverifikasi eligibility BPJS"
        )


@router.get("/verify/by-nik")
async def verify_eligibility_by_nik_get(
    nik: str = Query(..., description="NIK (16 digits)", min_length=16, max_length=16),
    sep_date: date = Query(..., description="SEP date (YYYY-MM-DD)"),
    patient_id: Optional[int] = Query(None, description="Patient ID"),
    use_cache: bool = Query(True, description="Use cached results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify BPJS eligibility by NIK (GET method)

    Target: Verification completes in <5 seconds

    Requires bpjs:read permission.
    """
    try:
        service = get_bpjs_eligibility_service(db)

        result = await service.verify_eligibility_by_nik(
            nik=nik,
            sep_date=sep_date,
            patient_id=patient_id,
            use_cache=use_cache,
            verified_by=current_user.id,
        )

        await db.commit()

        return result

    except EligibilityCheckError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error verifying eligibility by NIK: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memverifikasi eligibility BPJS"
        )


@router.post("/verify/override")
async def create_manual_override(
    request: ManualOverrideRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create manual eligibility verification override

    For use when BPJS API is down or manual verification is needed.
    Requires admin approval.

    Requires bpjs:write permission.
    """
    try:
        service = get_bpjs_eligibility_service(db)

        # For manual override, use admin user as approver
        approved_by = request.approved_by or current_user.id

        result = await service.create_manual_override(
            patient_id=request.patient_id,
            card_number=request.card_number,
            nik=request.nik,
            is_eligible=request.is_eligible,
            reason=request.reason,
            override_by=current_user.id,
            approved_by=approved_by,
        )

        await db.commit()

        return result

    except EligibilityCheckError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        logger.error("Error creating manual override: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal membuat manual override"
        )


@router.get("/history/{patient_id}")
async def get_eligibility_history(
    patient_id: int,
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get eligibility verification history for patient

    Requires bpjs:read permission.
    """
    try:
        service = get_bpjs_eligibility_service(db)

        history = await service.get_eligibility_history(
            patient_id=patient_id,
            limit=limit,
        )

        return {
            "patient_id": patient_id,
            "history": history,
            "count": len(history),
        }

    except Exception as e:
        logger.error("Error getting eligibility history: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil riwayat eligibility"
        )


@router.get("/status")
async def get_eligibility_status(
    card_number: Optional[str] = Query(None, description="BPJS card number"),
    nik: Optional[str] = Query(None, description="NIK"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current eligibility status from recent checks

    Requires bpjs:read permission.
    """
    try:
        service = get_bpjs_eligibility_service(db)

        status_result = await service.get_eligibility_status(
            card_number=card_number,
            nik=nik,
        )

        return status_result

    except EligibilityCheckError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        logger.error("Error getting eligibility status: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil status eligibility"
        )


@router.get("/statistics")
async def get_eligibility_statistics(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get eligibility verification statistics

    Requires bpjs:read permission.
    """
    try:
        service = get_bpjs_eligibility_service(db)

        stats = await service.get_eligibility_statistics(
            start_date=start_date,
            end_date=end_date,
        )

        return stats

    except Exception as e:
        logger.error("Error getting eligibility statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil statistik eligibility"
        )
