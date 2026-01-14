"""BPJS Eligibility Verification API endpoints for STORY-008

This module provides REST API endpoints for BPJS eligibility verification with caching,
history tracking, and manual override capabilities.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from datetime import datetime

from app.db.session import get_db
from app.core.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.bpjs import BPJSEligibilityRequest, BPJSEligibilityResponse
from app.services.bpjs_vclaim import BPJSVClaimClient, BPJSVClaimError
from app.services.bpjs_cache import BPJSCacheManager
from app.crud.bpjs_eligibility import (
    create_eligibility_check,
    get_eligibility_checks_by_patient,
    get_eligibility_stats,
    create_manual_override,
)
from app.crud.patient import get_patient_by_id
from app.db.redis import get_redis_client

router = APIRouter()


async def get_redis():
    """Dependency to get Redis client."""
    return get_redis_client()


@router.post("/verify", response_model=Dict[str, Any])
async def verify_bpjs_eligibility(
    request: BPJSEligibilityRequest,
    patient_id: int = Query(..., description="Patient ID"),
    use_cache: bool = Query(True, description="Use cached results if available"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs", "read")),
    redis = Depends(get_redis_client),
):
    """
    Verify BPJS eligibility with caching and history tracking.

    Args:
        request: Eligibility check request
        patient_id: Patient ID to associate with check
        use_cache: Whether to use cached results
        db: Database session
        current_user: Authenticated user
        redis: Redis client

    Returns:
        Eligibility result with metadata

    Raises:
        HTTPException 400: If validation error
        HTTPException 404: If patient not found
        HTTPException 502: If BPJS API error
    """
    # Verify patient exists
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    # Initialize services
    bpjs_client = BPJSVClaimClient()
    cache_manager = BPJSCacheManager(redis)

    # Determine search key
    search_key = request.card_number or request.nik
    search_type = "card" if request.card_number else "nik"

    # Check cache first
    cached_result = None
    is_cached = False
    if use_cache and search_key:
        cached_result = await cache_manager.get_cached_eligibility(search_key)
        if cached_result:
            is_cached = True

    # If no cached result, call BPJS API
    api_result = None
    if not is_cached:
        try:
            if request.card_number:
                api_result = await bpjs_client.check_eligibility_by_card(
                    card_number=request.card_number,
                    sep_date=request.sep_date
                )
            elif request.nik:
                api_result = await bpjs_client.check_eligibility_by_nik(
                    nik=request.nik,
                    sep_date=request.sep_date
                )

            # Cache the result
            if api_result and search_key:
                await cache_manager.set_cached_eligibility(search_key, api_result.dict())

        except BPJSVClaimError as e:
            # Create failed check record
            await create_eligibility_check(
                db=db,
                patient_id=patient_id,
                search_type=search_type,
                search_value=search_key,
                is_eligible=False,
                response_message=e.message,
                verified_by=current_user.id,
                verification_method="api",
                api_error=e.message,
            )

            # Check if this is a "not eligible" error vs actual API error
            if " tidak aktif" in e.message.lower() or " tidak ditemukan" in e.message.lower():
                return {
                    "is_eligible": False,
                    "message": e.message,
                    "search_key": search_key,
                    "search_type": search_type,
                    "is_cached": False,
                    "verified_at": datetime.now(timezone.utc).isoformat(),
                }

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"BPJS API error: {e.message}"
            )

    # Use cached or API result
    result = cached_result if is_cached else (api_result.dict() if api_result else None)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get eligibility result"
        )

    # Create history record
    await create_eligibility_check(
        db=db,
        patient_id=patient_id,
        search_type=search_type,
        search_value=search_key,
        is_eligible=result.get("is_eligible", False),
        response_code=result.get("metaData", {}).get("code"),
        response_message=result.get("message"),
        participant_info=result.get("peserta"),
        verified_by=current_user.id,
        verification_method="api",
        is_cached=is_cached,
        cache_hit=is_cached,
    )

    return {
        **result,
        "search_key": search_key,
        "search_type": search_type,
        "is_cached": is_cached,
        "verified_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/history/{patient_id}", response_model=Dict[str, Any])
async def get_eligibility_history(
    patient_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs", "read")),
):
    """
    Get BPJS eligibility verification history for a patient.

    Args:
        patient_id: Patient ID
        skip: Number of records to skip
        limit: Maximum number of records
        db: Database session
        current_user: Authenticated user

    Returns:
        Paginated eligibility check history

    Raises:
        HTTPException 404: If patient not found
    """
    # Verify patient exists
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    checks, total = await get_eligibility_checks_by_patient(
        db=db,
        patient_id=patient_id,
        skip=skip,
        limit=limit,
    )

    return {
        "patient_id": patient_id,
        "medical_record_number": patient.medical_record_number,
        "full_name": patient.full_name,
        "checks": checks,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit,
    }


@router.post("/override/{check_id}", response_model=Dict[str, Any])
async def create_manual_eligibility_override(
    check_id: int,
    override_reason: str = Query(..., min_length=10, max_length=500, description="Reason for override"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs", "override")),
):
    """
    Create a manual override for an eligibility check.

    This allows supervisors to override eligibility status when BPJS API is down
    or in emergency situations.

    Args:
        check_id: Eligibility check ID to override
        override_reason: Detailed reason for the override
        db: Database session
        current_user: Authenticated user with override permission

    Returns:
        Updated eligibility check

    Raises:
        HTTPException 404: If check not found
        HTTPException 403: If user lacks override permission
    """
    check = await create_manual_override(
        db=db,
        check_id=check_id,
        override_reason=override_reason,
        override_approved_by=current_user.id,
    )

    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Eligibility check with ID {check_id} not found"
        )

    return {
        "id": check.id,
        "is_eligible": check.is_eligible,
        "is_manual_override": True,
        "override_reason": check.override_reason,
        "override_approved_by": current_user.full_name,
        "override_approved_at": check.override_approved_at.isoformat() if check.override_approved_at else None,
        "message": "Manual override created successfully",
    }


@router.get("/stats", response_model=Dict[str, Any])
async def get_verification_statistics(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bpjs", "read")),
):
    """
    Get BPJS eligibility verification statistics.

    Args:
        patient_id: Optional patient ID to filter
        days: Number of days to look back
        db: Database session
        current_user: Authenticated user

    Returns:
        Verification statistics
    """
    stats = await get_eligibility_stats(
        db=db,
        patient_id=patient_id,
        days=days,
    )

    return stats


@router.delete("/cache/{search_key}", response_model=Dict[str, Any])
async def invalidate_eligibility_cache(
    search_key: str,
    redis = Depends(get_redis_client),
    current_user: User = Depends(require_permission("bpjs", "admin")),
):
    """
    Invalidate cached eligibility result for a specific key.

    Args:
        search_key: Card number or NIK to invalidate cache for
        redis: Redis client
        current_user: Authenticated user with admin permission

    Returns:
        Confirmation message
    """
    cache_manager = BPJSCacheManager(redis)
    await cache_manager.invalidate_cache(search_key)

    return {
        "message": f"Cache invalidated for key: {search_key}",
        "search_key": search_key,
    }


@router.get("/cache/stats", response_model=Dict[str, Any])
async def get_cache_statistics(
    redis = Depends(get_redis_client),
    current_user: User = Depends(require_permission("bpjs", "read")),
):
    """
    Get BPJS eligibility cache statistics.

    Args:
        redis: Redis client
        current_user: Authenticated user

    Returns:
        Cache statistics
    """
    cache_manager = BPJSCacheManager(redis)
    stats = await cache_manager.get_cache_stats()

    return stats
