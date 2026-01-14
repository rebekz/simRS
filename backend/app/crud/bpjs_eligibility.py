"""BPJS Eligibility CRUD operations for STORY-008

This module provides CRUD operations for BPJS eligibility verification history.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bpjs_eligibility import BPJSEligibilityCheck
from app.models.patient import Patient
from app.models.user import User


async def create_eligibility_check(
    db: AsyncSession,
    patient_id: int,
    search_type: str,
    search_value: str,
    is_eligible: bool,
    response_code: Optional[str] = None,
    response_message: Optional[str] = None,
    participant_info: Optional[Dict[str, Any]] = None,
    verified_by: Optional[int] = None,
    verification_method: str = "api",
    is_cached: bool = False,
    cache_hit: bool = False,
    api_error: Optional[str] = None,
    api_error_code: Optional[str] = None,
) -> BPJSEligibilityCheck:
    """
    Create a new eligibility check record.

    Args:
        db: Database session
        patient_id: Patient ID
        search_type: Type of search ('card' or 'nik')
        search_value: Card number or NIK
        is_eligible: Eligibility status
        response_code: BPJS API response code
        response_message: BPJS API response message
        participant_info: Participant information from BPJS
        verified_by: User ID who performed verification
        verification_method: Method used ('api', 'manual', 'override')
        is_cached: Whether result was from cache
        cache_hit: Whether cache was hit
        api_error: API error message if any
        api_error_code: API error code if any

    Returns:
        Created eligibility check record
    """
    check = BPJSEligibilityCheck(
        patient_id=patient_id,
        search_type=search_type,
        search_value=search_value,
        is_eligible=is_eligible,
        response_code=response_code,
        response_message=response_message,
        participant_info=participant_info,
        verified_by=verified_by,
        verification_method=verification_method,
        is_cached=is_cached,
        cache_hit=cache_hit,
        api_error=api_error,
        api_error_code=api_error_code,
    )
    db.add(check)
    await db.commit()
    await db.refresh(check)
    return check


async def get_eligibility_checks_by_patient(
    db: AsyncSession,
    patient_id: int,
    skip: int = 0,
    limit: int = 100,
) -> tuple[List[BPJSEligibilityCheck], int]:
    """
    Get eligibility checks for a patient.

    Args:
        db: Database session
        patient_id: Patient ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of eligibility checks, total count)
    """
    # Get total count
    count_query = select(BPJSEligibilityCheck).where(
        BPJSEligibilityCheck.patient_id == patient_id
    )
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    # Get paginated results
    query = (
        select(BPJSEligibilityCheck)
        .where(BPJSEligibilityCheck.patient_id == patient_id)
        .order_by(desc(BPJSEligibilityCheck.verified_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    checks = result.scalars().all()

    return list(checks), total


async def get_latest_eligibility_check(
    db: AsyncSession,
    patient_id: int,
) -> Optional[BPJSEligibilityCheck]:
    """
    Get the latest eligibility check for a patient.

    Args:
        db: Database session
        patient_id: Patient ID

    Returns:
        Latest eligibility check or None
    """
    query = (
        select(BPJSEligibilityCheck)
        .where(BPJSEligibilityCheck.patient_id == patient_id)
        .order_by(desc(BPJSEligibilityCheck.verified_at))
        .limit(1)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_eligibility_check_by_id(
    db: AsyncSession,
    check_id: int,
) -> Optional[BPJSEligibilityCheck]:
    """
    Get eligibility check by ID.

    Args:
        db: Database session
        check_id: Eligibility check ID

    Returns:
        Eligibility check or None
    """
    query = select(BPJSEligibilityCheck).where(
        BPJSEligibilityCheck.id == check_id
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_manual_override(
    db: AsyncSession,
    check_id: int,
    override_reason: str,
    override_approved_by: int,
) -> Optional[BPJSEligibilityCheck]:
    """
    Create a manual override for an eligibility check.

    Args:
        db: Database session
        check_id: Eligibility check ID to override
        override_reason: Reason for override
        override_approved_by: User ID approving override

    Returns:
        Updated eligibility check or None
    """
    check = await get_eligibility_check_by_id(db, check_id)
    if not check:
        return None

    check.is_manual_override = True
    check.override_reason = override_reason
    check.override_approved_by = override_approved_by
    check.override_approved_at = datetime.now(timezone.utc)
    check.verification_method = "override"

    await db.commit()
    await db.refresh(check)
    return check


async def increment_retry_count(
    db: AsyncSession,
    check_id: int,
) -> Optional[BPJSEligibilityCheck]:
    """
    Increment retry count for an eligibility check.

    Args:
        db: Database session
        check_id: Eligibility check ID

    Returns:
        Updated eligibility check or None
    """
    check = await get_eligibility_check_by_id(db, check_id)
    if not check:
        return None

    check.retry_count += 1
    check.last_retry_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(check)
    return check


async def get_eligibility_stats(
    db: AsyncSession,
    patient_id: Optional[int] = None,
    days: int = 30,
) -> Dict[str, Any]:
    """
    Get eligibility verification statistics.

    Args:
        db: Database session
        patient_id: Optional patient ID to filter
        days: Number of days to look back

    Returns:
        Dictionary with statistics
    """
    since_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Build query
    query = select(BPJSEligibilityCheck).where(
        BPJSEligibilityCheck.verified_at >= since_date
    )
    if patient_id:
        query = query.where(BPJSEligibilityCheck.patient_id == patient_id)

    result = await db.execute(query)
    checks = result.scalars().all()

    # Calculate statistics
    total = len(checks)
    eligible = sum(1 for c in checks if c.is_eligible)
    ineligible = total - eligible
    manual_overrides = sum(1 for c in checks if c.is_manual_override)
    cache_hits = sum(1 for c in checks if c.cache_hit)
    api_errors = sum(1 for c in checks if c.api_error is not None)

    return {
        "total_checks": total,
        "eligible": eligible,
        "ineligible": ineligible,
        "eligibility_rate": round((eligible / total * 100) if total > 0 else 0, 2),
        "manual_overrides": manual_overrides,
        "cache_hits": cache_hits,
        "cache_hit_rate": round((cache_hits / total * 100) if total > 0 else 0, 2),
        "api_errors": api_errors,
        "error_rate": round((api_errors / total * 100) if total > 0 else 0, 2),
        "period_days": days,
    }
