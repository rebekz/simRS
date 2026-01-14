"""ICD-10 and Problem List CRUD operations for STORY-012

This module provides CRUD operations for ICD-10 codes and patient problem list.
"""
from datetime import datetime, timezone, date
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.models.icd10 import ICD10Code, ICD10UserFavorite
from app.models.problem_list import ProblemList
from app.models.patient import Patient
from app.models.user import User
from app.models.encounter import Encounter


async def search_icd10_codes(
    db: AsyncSession,
    query: str,
    limit: int = 50,
    chapter_filter: Optional[str] = None,
    severity_filter: Optional[str] = None,
    common_only: bool = False,
) -> tuple[List[ICD10Code], int]:
    """
    Search ICD-10 codes by code or description.

    Args:
        db: Database session
        query: Search query
        limit: Maximum results
        chapter_filter: Filter by chapter
        severity_filter: Filter by severity
        common_only: Show only common codes

    Returns:
        Tuple of (list of codes, total count)
    """
    # Build search query with full-text search
    search_query = f"%{query}%"

    # Start building the query
    stmt = select(ICD10Code).where(
        or_(
            ICD10Code.code.ilike(search_query),
            ICD10Code.code_full.ilike(search_query),
            ICD10Code.description_indonesian.ilike(search_query),
            ICD10Code.description_english.ilike(search_query),
        )
    )

    # Apply filters
    if chapter_filter:
        stmt = stmt.where(ICD10Code.chapter == chapter_filter)

    if severity_filter:
        stmt = stmt.where(ICD10Code.severity == severity_filter)

    if common_only:
        stmt = stmt.where(ICD10Code.is_common == True)

    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Get paginated results
    stmt = stmt.order_by(
        desc(ICD10Code.is_common),
        desc(ICD10Code.usage_count),
        ICD10Code.code
    ).limit(limit)

    result = await db.execute(stmt)
    codes = result.scalars().all()

    return list(codes), total


async def get_icd10_code_by_id(
    db: AsyncSession,
    code_id: int,
) -> Optional[ICD10Code]:
    """Get ICD-10 code by ID."""
    stmt = select(ICD10Code).where(ICD10Code.id == code_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_icd10_chapters(db: AsyncSession) -> List[Dict[str, Any]]:
    """Get all ICD-10 chapters."""
    stmt = select(ICD10Code).where(ICD10Code.is_chapter == True).order_by(ICD10Code.code)
    result = await db.execute(stmt)
    chapters = result.scalars().all()

    return [
        {
            "code": ch.code,
            "chapter": ch.chapter,
            "description": ch.description_indonesian,
        }
        for ch in chapters
    ]


async def get_user_favorites(
    db: AsyncSession,
    user_id: int,
    limit: int = 100,
) -> List[ICD10UserFavorite]:
    """Get user's favorite ICD-10 codes."""
    stmt = (
        select(ICD10UserFavorite)
        .where(ICD10UserFavorite.user_id == user_id)
        .order_by(ICD10UserFavorite.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def add_user_favorite(
    db: AsyncSession,
    user_id: int,
    icd10_code_id: int,
    notes: Optional[str] = None,
) -> ICD10UserFavorite:
    """Add ICD-10 code to user favorites."""
    favorite = ICD10UserFavorite(
        user_id=user_id,
        icd10_code_id=icd10_code_id,
        notes=notes,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


async def remove_user_favorite(
    db: AsyncSession,
    user_id: int,
    favorite_id: int,
) -> bool:
    """Remove ICD-10 code from user favorites."""
    stmt = select(ICD10UserFavorite).where(
        and_(
            ICD10UserFavorite.id == favorite_id,
            ICD10UserFavorite.user_id == user_id,
        )
    )
    result = await db.execute(stmt)
    favorite = result.scalar_one_or_none()

    if favorite:
        await db.delete(favorite)
        await db.commit()
        return True
    return False


# Problem List CRUD Operations
async def create_problem(
    db: AsyncSession,
    patient_id: int,
    icd10_code_id: int,
    problem_name: str,
    recorded_by: int,
    encounter_id: Optional[int] = None,
    diagnosed_by: Optional[int] = None,
    status: str = "active",
    onset_date: Optional[date] = None,
    is_chronic: bool = False,
    severity: Optional[str] = None,
    description: Optional[str] = None,
    clinical_notes: Optional[str] = None,
    treatment_plan: Optional[str] = None,
    follow_up_required: bool = False,
    follow_up_date: Optional[date] = None,
    certainty: Optional[str] = None,
) -> ProblemList:
    """Create a new problem for a patient."""
    # Get ICD-10 code details
    icd10_code = await get_icd10_code_by_id(db, icd10_code_id)
    if not icd10_code:
        raise ValueError(f"ICD-10 code with ID {icd10_code_id} not found")

    problem = ProblemList(
        patient_id=patient_id,
        encounter_id=encounter_id,
        icd10_code_id=icd10_code_id,
        icd10_code=icd10_code.code,
        problem_name=problem_name,
        description=description,
        status=status,
        onset_date=onset_date,
        is_chronic=is_chronic,
        severity=severity,
        diagnosed_by=diagnosed_by,
        recorded_by=recorded_by,
        clinical_notes=clinical_notes,
        treatment_plan=treatment_plan,
        follow_up_required=follow_up_required,
        follow_up_date=follow_up_date,
        certainty=certainty,
    )

    db.add(problem)
    await db.commit()
    await db.refresh(problem)
    return problem


async def update_problem(
    db: AsyncSession,
    problem_id: int,
    status: Optional[str] = None,
    resolved_date: Optional[date] = None,
    description: Optional[str] = None,
    severity: Optional[str] = None,
    clinical_notes: Optional[str] = None,
    treatment_plan: Optional[str] = None,
    follow_up_required: Optional[bool] = None,
    follow_up_date: Optional[date] = None,
    certainty: Optional[str] = None,
) -> Optional[ProblemList]:
    """Update a problem."""
    stmt = select(ProblemList).where(ProblemList.id == problem_id)
    result = await db.execute(stmt)
    problem = result.scalar_one_or_none()

    if not problem:
        return None

    if status is not None:
        problem.status = status
        if status == "resolved" and not resolved_date:
            problem.resolved_date = date.today()

    if resolved_date is not None:
        problem.resolved_date = resolved_date

    if description is not None:
        problem.description = description

    if severity is not None:
        problem.severity = severity

    if clinical_notes is not None:
        problem.clinical_notes = clinical_notes

    if treatment_plan is not None:
        problem.treatment_plan = treatment_plan

    if follow_up_required is not None:
        problem.follow_up_required = follow_up_required

    if follow_up_date is not None:
        problem.follow_up_date = follow_up_date

    if certainty is not None:
        problem.certainty = certainty

    await db.commit()
    await db.refresh(problem)
    return problem


async def get_patient_problems(
    db: AsyncSession,
    patient_id: int,
    status_filter: Optional[str] = None,
    limit: int = 100,
) -> List[ProblemList]:
    """Get all problems for a patient."""
    stmt = select(ProblemList).where(ProblemList.patient_id == patient_id)

    if status_filter:
        stmt = stmt.where(ProblemList.status == status_filter)

    stmt = stmt.order_by(
        desc(ProblemList.is_chronic),
        desc(ProblemList.created_at)
    ).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_problem_by_id(
    db: AsyncSession,
    problem_id: int,
) -> Optional[ProblemList]:
    """Get problem by ID."""
    stmt = select(ProblemList).where(ProblemList.id == problem_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def delete_problem(
    db: AsyncSession,
    problem_id: int,
) -> bool:
    """Delete a problem (soft delete by setting status to resolved)."""
    stmt = select(ProblemList).where(ProblemList.id == problem_id)
    result = await db.execute(stmt)
    problem = result.scalar_one_or_none()

    if problem:
        problem.status = "resolved"
        problem.resolved_date = date.today()
        await db.commit()
        return True
    return False
