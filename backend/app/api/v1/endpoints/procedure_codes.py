"""Procedure Code API endpoints for Lab/Radiology Ordering

This module provides API endpoints for:
- Procedure code management (lab tests, radiology procedures)
- LOINC code lookup
- Code search and filtering
- Admin-only code management (create, update)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_current_active_user, get_current_superuser, get_db
from app.models.user import User, UserRole
from app.schemas.procedure_codes import (
    ProcedureCodeResponse,
    ProcedureCodeListResponse,
    ProcedureCodeCreate,
    ProcedureCodeUpdate,
    ProcedureCodeSearchResponse,
    LOINCCodeResponse,
    LOINCCodeListResponse,
    ProcedureCodeType,
)


router = APIRouter()


# =============================================================================
# Procedure Code Query Endpoints (Public/Authenticated)
# =============================================================================

@router.get("/procedure-codes", response_model=ProcedureCodeListResponse)
async def list_procedure_codes(
    code_type: Optional[ProcedureCodeType] = Query(None, description="Filter by code type: lab, radiology"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in code or name"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProcedureCodeListResponse:
    """List procedure codes with filtering and pagination.

    Args:
        code_type: Optional filter by procedure code type
        category: Optional filter by category
        search: Optional search query for code/name
        is_active: Filter by active status
        page: Page number (1-indexed)
        page_size: Results per page
        db: Database session
        current_user: Authenticated user

    Returns:
        ProcedureCodeListResponse: Paginated list of procedure codes
    """
    from app.crud import procedure_codes as crud_codes

    codes, total = await crud_codes.list_procedure_codes(
        db=db,
        code_type=code_type,
        category=category,
        search=search,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )

    response_data = []
    for code in codes:
        response_data.append(ProcedureCodeResponse(
            id=code.id,
            code=code.code,
            code_type=code.code_type,
            name=code.name,
            description=code.description,
            category=code.category,
            loinc_code=code.loinc_code,
            cpt_code=code.cpt_code,
            bpjs_code=code.bpjs_code,
            standard_cost=code.standard_cost,
            bpjs_tariff=code.bpjs_tariff,
            is_active=code.is_active,
            specimen_type=code.specimen_type,
            body_system=code.body_system,
            typical_turnaround_hours=code.typical_turnaround_hours,
            contrast_required=getattr(code, 'contrast_required', None),
            ionizing_radiation=getattr(code, 'ionizing_radiation', None),
            created_at=code.created_at,
            updated_at=code.updated_at,
        ))

    return ProcedureCodeListResponse(
        codes=response_data,
        total=total,
        page=page,
        page_size=page_size,
        filters_applied={
            "code_type": code_type.value if code_type else None,
            "category": category,
            "search": search,
            "is_active": is_active,
        },
    )


@router.get("/procedure-codes/{code_id}", response_model=ProcedureCodeResponse)
async def get_procedure_code(
    code_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProcedureCodeResponse:
    """Get a single procedure code by ID.

    Args:
        code_id: Procedure code ID
        db: Database session
        current_user: Authenticated user

    Returns:
        ProcedureCodeResponse: Procedure code details

    Raises:
        HTTPException 404: Procedure code not found
    """
    from app.crud import procedure_codes as crud_codes

    code = await crud_codes.get_procedure_code(db=db, code_id=code_id)

    if not code:
        raise HTTPException(status_code=404, detail="Procedure code not found")

    return ProcedureCodeResponse(
        id=code.id,
        code=code.code,
        code_type=code.code_type,
        name=code.name,
        description=code.description,
        category=code.category,
        loinc_code=code.loinc_code,
        cpt_code=code.cpt_code,
        bpjs_code=code.bpjs_code,
        standard_cost=code.standard_cost,
        bpjs_tariff=code.bpjs_tariff,
        is_active=code.is_active,
        specimen_type=code.specimen_type,
        body_system=code.body_system,
        typical_turnaround_hours=code.typical_turnaround_hours,
        contrast_required=getattr(code, 'contrast_required', None),
        ionizing_radiation=getattr(code, 'ionizing_radiation', None),
        created_at=code.created_at,
        updated_at=code.updated_at,
    )


@router.get("/procedure-codes/search", response_model=ProcedureCodeSearchResponse)
async def search_procedure_codes(
    query: str = Query(..., min_length=2, description="Search query"),
    code_type: Optional[ProcedureCodeType] = Query(None, description="Filter by code type"),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProcedureCodeSearchResponse:
    """Search procedure codes by name or code.

    Provides auto-complete style search for procedure selection UI.
    Searches in code, name, and description fields.

    Args:
        query: Search query string
        code_type: Optional filter by procedure code type
        limit: Maximum number of results
        db: Database session
        current_user: Authenticated user

    Returns:
        ProcedureCodeSearchResponse: Search results with relevance scoring
    """
    from app.crud import procedure_codes as crud_codes

    results = await crud_codes.search_procedure_codes(
        db=db,
        query=query,
        code_type=code_type,
        limit=limit,
    )

    response_data = []
    for code in results:
        response_data.append(ProcedureCodeResponse(
            id=code.id,
            code=code.code,
            code_type=code.code_type,
            name=code.name,
            description=code.description,
            category=code.category,
            loinc_code=code.loinc_code,
            cpt_code=code.cpt_code,
            bpjs_code=code.bpjs_code,
            standard_cost=code.standard_cost,
            bpjs_tariff=code.bpjs_tariff,
            is_active=code.is_active,
            specimen_type=code.specimen_type,
            body_system=code.body_system,
            typical_turnaround_hours=code.typical_turnaround_hours,
            contrast_required=getattr(code, 'contrast_required', None),
            ionizing_radiation=getattr(code, 'ionizing_radiation', None),
            created_at=code.created_at,
            updated_at=code.updated_at,
        ))

    return ProcedureCodeSearchResponse(
        query=query,
        results=response_data,
        total=len(response_data),
    )


@router.get("/procedure-codes/loinc", response_model=LOINCCodeListResponse)
async def get_loinc_codes(
    search: Optional[str] = Query(None, description="Search LOINC codes"),
    system: Optional[str] = Query(None, description="Filter by LOINC system"),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LOINCCodeListResponse:
    """Get LOINC codes for lab test mapping.

    LOINC (Logical Observation Identifiers Names and Codes) is the international
    standard for identifying laboratory and clinical observations.

    Args:
        search: Optional search query for LOINC code or name
        system: Optional filter by LOINC system (e.g., "Hematology", "Chemistry")
        limit: Maximum number of results
        db: Database session
        current_user: Authenticated user

    Returns:
        LOINCCodeListResponse: List of LOINC codes
    """
    from app.crud import procedure_codes as crud_codes

    loinc_codes = await crud_codes.get_loinc_codes(
        db=db,
        search=search,
        system=system,
        limit=limit,
    )

    response_data = []
    for loinc in loinc_codes:
        response_data.append(LOINCCodeResponse(
            id=loinc.id,
            loinc_num=loinc.loinc_num,
            loinc_display_name=loinc.loinc_display_name,
            loinc_short_name=loinc.loinc_short_name,
            system=loinc.system,
            units_required=loinc.units_required,
            example_units=loinc.example_units,
        ))

    return LOINCCodeListResponse(
        codes=response_data,
        total=len(response_data),
    )


# =============================================================================
# Procedure Code Management Endpoints (Admin Only)
# =============================================================================

@router.post("/procedure-codes", response_model=ProcedureCodeResponse)
async def create_procedure_code(
    code_data: ProcedureCodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> ProcedureCodeResponse:
    """Create a new procedure code (admin only).

    Args:
        code_data: Procedure code data
        db: Database session
        current_user: Authenticated superuser (admin only)

    Returns:
        ProcedureCodeResponse: Created procedure code

    Raises:
        HTTPException 400: Invalid data or duplicate code
        HTTPException 403: Not authorized (non-admin users)
        HTTPException 422: Validation error
    """
    try:
        from app.crud import procedure_codes as crud_codes

        code = await crud_codes.create_procedure_code(
            db=db,
            code=code_data.code,
            code_type=code_data.code_type,
            name=code_data.name,
            description=code_data.description,
            category=code_data.category,
            loinc_code=code_data.loinc_code,
            cpt_code=code_data.cpt_code,
            bpjs_code=code_data.bpjs_code,
            standard_cost=code_data.standard_cost,
            bpjs_tariff=code_data.bpjs_tariff,
            specimen_type=code_data.specimen_type,
            body_system=code_data.body_system,
            typical_turnaround_hours=code_data.typical_turnaround_hours,
            contrast_required=code_data.contrast_required,
            ionizing_radiation=code_data.ionizing_radiation,
        )

        return ProcedureCodeResponse(
            id=code.id,
            code=code.code,
            code_type=code.code_type,
            name=code.name,
            description=code.description,
            category=code.category,
            loinc_code=code.loinc_code,
            cpt_code=code.cpt_code,
            bpjs_code=code.bpjs_code,
            standard_cost=code.standard_cost,
            bpjs_tariff=code.bpjs_tariff,
            is_active=code.is_active,
            specimen_type=code.specimen_type,
            body_system=code.body_system,
            typical_turnaround_hours=code.typical_turnaround_hours,
            contrast_required=getattr(code, 'contrast_required', None),
            ionizing_radiation=getattr(code, 'ionizing_radiation', None),
            created_at=code.created_at,
            updated_at=code.updated_at,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/procedure-codes/{code_id}", response_model=ProcedureCodeResponse)
async def update_procedure_code(
    code_id: int,
    code_update: ProcedureCodeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> ProcedureCodeResponse:
    """Update an existing procedure code (admin only).

    Args:
        code_id: Procedure code ID
        code_update: Updated procedure code data
        db: Database session
        current_user: Authenticated superuser (admin only)

    Returns:
        ProcedureCodeResponse: Updated procedure code

    Raises:
        HTTPException 403: Not authorized (non-admin users)
        HTTPException 404: Procedure code not found
        HTTPException 422: Validation error
    """
    try:
        from app.crud import procedure_codes as crud_codes

        code = await crud_codes.update_procedure_code(
            db=db,
            code_id=code_id,
            code_update=code_update,
        )

        if not code:
            raise HTTPException(status_code=404, detail="Procedure code not found")

        return ProcedureCodeResponse(
            id=code.id,
            code=code.code,
            code_type=code.code_type,
            name=code.name,
            description=code.description,
            category=code.category,
            loinc_code=code.loinc_code,
            cpt_code=code.cpt_code,
            bpjs_code=code.bpjs_code,
            standard_cost=code.standard_cost,
            bpjs_tariff=code.bpjs_tariff,
            is_active=code.is_active,
            specimen_type=code.specimen_type,
            body_system=code.body_system,
            typical_turnaround_hours=code.typical_turnaround_hours,
            contrast_required=getattr(code, 'contrast_required', None),
            ionizing_radiation=getattr(code, 'ionizing_radiation', None),
            created_at=code.created_at,
            updated_at=code.updated_at,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
