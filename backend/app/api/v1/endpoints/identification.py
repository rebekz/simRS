"""Identification System Integration API Endpoints for STORY-024-09

This module provides API endpoints for:
- KTP-el (Electronic ID) verification
- BPJS card validation
- Face recognition verification
- Biometric data management
- Verification history

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user, get_current_admin_user
from app.services.identification import get_identification_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class KTPVerificationRequest(BaseModel):
    """Request to verify KTP"""
    nik: str = Field(..., min_length=16, max_length=16, description="16-digit NIK")
    full_name: str = Field(..., description="Full name as on KTP")
    date_of_birth: datetime = Field(..., description="Date of birth")
    config: Optional[dict] = Field(None, description="Optional configuration override")


class BPJSValidationRequest(BaseModel):
    """Request to validate BPJS card"""
    bpjs_card_number: str = Field(..., min_length=13, max_length=13, description="13-digit BPJS card number")
    nik: str = Field(..., min_length=16, max_length=16, description="16-digit NIK from BPJS")
    full_name: str = Field(..., description="Full name as on BPJS card")
    config: Optional[dict] = Field(None, description="Optional configuration override")


class FaceVerificationRequest(BaseModel):
    """Request to verify face"""
    source_image_data: str = Field(..., description="Base64 source image (from ID)")
    captured_image_data: str = Field(..., description="Base64 captured image")
    patient_id: Optional[int] = Field(None, description="Optional patient ID")


# =============================================================================
# KTP Verification Endpoints
# =============================================================================

@router.post("/ktp/verify", status_code=status.HTTP_200_OK)
async def verify_ktp(
    request: KTPVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify KTP through Dukcapil API"""
    try:
        service = get_identification_service(db)

        result = await service.verify_ktp(
            nik=request.nik,
            full_name=request.full_name,
            date_of_birth=request.date_of_birth,
            config=request.config
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error verifying KTP: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify KTP"
        )


# =============================================================================
# BPJS Card Validation Endpoints
# =============================================================================

@router.post("/bpjs/validate", status_code=status.HTTP_200_OK)
async def validate_bpjs_card(
    request: BPJSValidationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Validate BPJS card through BPJS API"""
    try:
        service = get_identification_service(db)

        result = await service.verify_bpjs_card(
            bpjs_card_number=request.bpjs_card_number,
            nik=request.nik,
            full_name=request.full_name,
            config=request.config
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error validating BPJS card: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate BPJS card"
        )


# =============================================================================
# Face Recognition Endpoints
# =============================================================================

@router.post("/face/verify", status_code=status.HTTP_200_OK)
async def verify_face(
    request: FaceVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify face match between source and captured images"""
    try:
        service = get_identification_service(db)

        result = await service.verify_face(
            source_image_data=request.source_image_data,
            captured_image_data=request.captured_image_data,
            patient_id=request.patient_id
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error verifying face: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify face"
        )


# =============================================================================
# Verification History Endpoints
# =============================================================================

@router.get("/verifications/history")
async def get_verification_history(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    verification_type: Optional[str] = Query(None, description="Filter by verification type (ktp_el, bpjs, face)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get verification history"""
    try:
        service = get_identification_service(db)

        history = await service.get_verification_history(
            patient_id=patient_id,
            verification_type=verification_type,
            limit=limit
        )

        return {
            "verifications": history,
            "count": len(history)
        }

    except Exception as e:
        logger.error("Error getting verification history: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get verification history"
        )


# =============================================================================
# Statistics Endpoints
# =============================================================================

@router.get("/statistics")
async def get_identification_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get identification verification statistics"""
    try:
        from app.models.identification import IDVerification, BPJSCardValidation, FaceRecognition
        from sqlalchemy import select, func

        # Get total verification counts by type
        ktp_query = select(func.count(IDVerification.id)).where(
            IDVerification.verification_type == "ktp_el"
        )
        ktp_result = await db.execute(ktp_query)
        total_ktp_verifications = ktp_result.scalar() or 0

        bpjs_query = select(func.count(BPJSCardValidation.id))
        bpjs_result = await db.execute(bpjs_query)
        total_bpjs_validations = bpjs_result.scalar() or 0

        face_query = select(func.count(FaceRecognition.id))
        face_result = await db.execute(face_query)
        total_face_verifications = face_result.scalar() or 0

        # Get verification status breakdown
        status_query = select(
            IDVerification.status,
            func.count(IDVerification.id).label("count")
        ).group_by(IDVerification.status)

        status_result = await db.execute(status_query)
        status_counts = {row[0]: row[1] for row in status_result.all()}

        # Get BPJS membership status breakdown
        bpjs_status_query = select(
            BPJSCardValidation.membership_status,
            func.count(BPJSCardValidation.id).label("count")
        ).group_by(BPJSCardValidation.membership_status)

        bpjs_status_result = await db.execute(bpjs_status_query)
        bpjs_status_counts = {row[0]: row[1] for row in bpjs_status_result.all()}

        return {
            "total_ktp_verifications": total_ktp_verifications,
            "total_bpjs_validations": total_bpjs_validations,
            "total_face_verifications": total_face_verifications,
            "verification_status_counts": status_counts,
            "bpjs_membership_status_counts": bpjs_status_counts,
            "summary": {
                "verified": status_counts.get("verified", 0),
                "not_verified": status_counts.get("not_verified", 0),
                "failed": status_counts.get("failed", 0),
                "bpjs_active": bpjs_status_counts.get("AKTIF", 0)
            }
        }

    except Exception as e:
        logger.error("Error getting identification statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
