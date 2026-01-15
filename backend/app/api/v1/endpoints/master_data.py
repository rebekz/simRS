"""
Master Data API Endpoints

This module provides REST API endpoints for managing master/reference data
including ICD-10 codes, LOINC codes, drugs, procedures, room classes, and insurance.
"""

import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db, get_request_info, require_permission
from backend.app.models.user import User
from backend.app.schemas.master_data import (
    # ICD-10
    ICD10CodeCreate,
    ICD10CodeUpdate,
    ICD10CodeResponse,
    ICD10CodeSearchResponse,
    # LOINC
    LOINCCodeCreate,
    LOINCCodeUpdate,
    LOINCCodeResponse,
    LOINCCodeSearchResponse,
    # Drug
    DrugFormularyCreate,
    DrugFormularyUpdate,
    DrugFormularyResponse,
    DrugFormularySearchResponse,
    # Procedure
    ProcedureCodeCreate,
    ProcedureCodeUpdate,
    ProcedureCodeResponse,
    ProcedureCodeSearchResponse,
    # Room Class
    RoomClassCreate,
    RoomClassUpdate,
    RoomClassResponse,
    # Insurance
    InsuranceCompanyCreate,
    InsuranceCompanyUpdate,
    InsuranceCompanyResponse,
    InsurancePlanCreate,
    InsurancePlanUpdate,
    InsurancePlanResponse,
    # Reference Data
    ReferenceDataCreate,
    ReferenceDataUpdate,
    ReferenceDataResponse,
    # Statistics
    MasterDataStatistics,
    # Import
    DataImportRequest,
    DataImportResponse,
)
from backend.app.crud import master_data as crud
from backend.app.core.audit import create_audit_log

router = APIRouter()


# ICD-10 Code Endpoints

@router.post("/icd10-codes", response_model=ICD10CodeResponse, status_code=status.HTTP_201_CREATED)
async def create_icd10_code(
    code_data: ICD10CodeCreate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "create")),
):
    """Create a new ICD-10 code."""
    try:
        # Check if code already exists
        existing = await crud.get_icd10_code_by_code(db, code_data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ICD-10 code already exists"
            )

        code = await crud.create_icd10_code(db, code_data.dict())

        # Audit log
        background_tasks.add_task(
            create_audit_log,
            db=db,
            action="MASTER_DATA_ICD10_CREATED",
            resource_type="ICD10Code",
            resource_id=str(code.id),
            request_info=request_info,
            changes={"code": code.code, "description": code.description_indonesian},
        )

        return code
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/icd10-codes/{code_id}", response_model=ICD10CodeResponse)
async def get_icd10_code(
    code_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """Get ICD-10 code by ID."""
    code = await crud.get_icd10_code_by_id(db, code_id)
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ICD-10 code not found"
        )
    return code


@router.get("/icd10-codes", response_model=ICD10CodeSearchResponse)
async def list_icd10_codes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    chapter: Optional[str] = None,
    search: Optional[str] = None,
    is_common: Optional[bool] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """List ICD-10 codes with filtering and pagination."""
    start_time = time.time()
    codes, total = await crud.list_icd10_codes(
        db=db,
        skip=skip,
        limit=limit,
        chapter=chapter,
        search=search,
        is_common=is_common,
        is_active=is_active,
    )

    return ICD10CodeSearchResponse(
        total=total,
        results=codes,
        search_time_ms=int((time.time() - start_time) * 1000),
    )


@router.get("/icd10-codes/search/{search_term}", response_model=List[ICD10CodeResponse])
async def search_icd10_codes(
    search_term: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """Full-text search for ICD-10 codes."""
    return await crud.search_icd10_codes(db, search_term, limit)


@router.patch("/icd10-codes/{code_id}", response_model=ICD10CodeResponse)
async def update_icd10_code(
    code_id: int,
    update_data: ICD10CodeUpdate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "update")),
):
    """Update ICD-10 code."""
    code = await crud.update_icd10_code(db, code_id, update_data.dict(exclude_unset=True))
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ICD-10 code not found"
        )

    # Audit log
    background_tasks.add_task(
        create_audit_log,
        db=db,
        action="MASTER_DATA_ICD10_UPDATED",
        resource_type="ICD10Code",
        resource_id=str(code_id),
        request_info=request_info,
        changes=update_data.dict(exclude_unset=True),
    )

    return code


# LOINC Code Endpoints

@router.post("/loinc-codes", response_model=LOINCCodeResponse, status_code=status.HTTP_201_CREATED)
async def create_loinc_code(
    code_data: LOINCCodeCreate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "create")),
):
    """Create a new LOINC code."""
    try:
        # Check if code already exists
        existing = await crud.get_loinc_code_by_num(db, code_data.loinc_num)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LOINC code already exists"
            )

        code = await crud.create_loinc_code(db, code_data.dict())

        # Audit log
        background_tasks.add_task(
            create_audit_log,
            db=db,
            action="MASTER_DATA_LOINC_CREATED",
            resource_type="LOINCCode",
            resource_id=str(code.id),
            request_info=request_info,
            changes={"loinc_num": code.loinc_num, "component": code.component},
        )

        return code
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/loinc-codes/{code_id}", response_model=LOINCCodeResponse)
async def get_loinc_code(
    code_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """Get LOINC code by ID."""
    code = await crud.get_loinc_code_by_id(db, code_id)
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LOINC code not found"
        )
    return code


@router.get("/loinc-codes", response_model=LOINCCodeSearchResponse)
async def list_loinc_codes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    class_name: Optional[str] = None,
    search: Optional[str] = None,
    is_common: Optional[bool] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """List LOINC codes with filtering and pagination."""
    start_time = time.time()
    codes, total = await crud.list_loinc_codes(
        db=db,
        skip=skip,
        limit=limit,
        class_name=class_name,
        search=search,
        is_common=is_common,
        is_active=is_active,
    )

    return LOINCCodeSearchResponse(
        total=total,
        results=codes,
        search_time_ms=int((time.time() - start_time) * 1000),
    )


@router.get("/loinc-codes/search/{search_term}", response_model=List[LOINCCodeResponse])
async def search_loinc_codes(
    search_term: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """Full-text search for LOINC codes."""
    return await crud.search_loinc_codes(db, search_term, limit)


@router.patch("/loinc-codes/{code_id}", response_model=LOINCCodeResponse)
async def update_loinc_code(
    code_id: int,
    update_data: LOINCCodeUpdate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "update")),
):
    """Update LOINC code."""
    code = await crud.update_loinc_code(db, code_id, update_data.dict(exclude_unset=True))
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LOINC code not found"
        )

    # Audit log
    background_tasks.add_task(
        create_audit_log,
        db=db,
        action="MASTER_DATA_LOINC_UPDATED",
        resource_type="LOINCCode",
        resource_id=str(code_id),
        request_info=request_info,
        changes=update_data.dict(exclude_unset=True),
    )

    return code


# Drug Formulary Endpoints

@router.post("/drugs", response_model=DrugFormularyResponse, status_code=status.HTTP_201_CREATED)
async def create_drug(
    drug_data: DrugFormularyCreate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "create")),
):
    """Create a new drug formulary entry."""
    try:
        drug = await crud.create_drug(db, drug_data.dict())

        # Audit log
        background_tasks.add_task(
            create_audit_log,
            db=db,
            action="MASTER_DATA_DRUG_CREATED",
            resource_type="DrugFormulary",
            resource_id=str(drug.id),
            request_info=request_info,
            changes={"generic_name": drug.generic_name, "dosage_form": drug.dosage_form},
        )

        return drug
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/drugs/{drug_id}", response_model=DrugFormularyResponse)
async def get_drug(
    drug_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """Get drug by ID."""
    drug = await crud.get_drug_by_id(db, drug_id)
    if not drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drug not found"
        )
    return drug


@router.get("/drugs", response_model=DrugFormularySearchResponse)
async def list_drugs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    generic_name: Optional[str] = None,
    dosage_form: Optional[str] = None,
    bpjs_covered: Optional[bool] = None,
    is_narcotic: Optional[bool] = None,
    is_antibiotic: Optional[bool] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """List drugs with filtering and pagination."""
    start_time = time.time()
    drugs, total = await crud.list_drugs(
        db=db,
        skip=skip,
        limit=limit,
        generic_name=generic_name,
        dosage_form=dosage_form,
        bpjs_covered=bpjs_covered,
        is_narcotic=is_narcotic,
        is_antibiotic=is_antibiotic,
        search=search,
        is_active=is_active,
    )

    return DrugFormularySearchResponse(
        total=total,
        results=drugs,
        search_time_ms=int((time.time() - start_time) * 1000),
    )


@router.get("/drugs/search/{search_term}", response_model=List[DrugFormularyResponse])
async def search_drugs(
    search_term: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """Full-text search for drugs."""
    return await crud.search_drugs(db, search_term, limit)


@router.patch("/drugs/{drug_id}", response_model=DrugFormularyResponse)
async def update_drug(
    drug_id: int,
    update_data: DrugFormularyUpdate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "update")),
):
    """Update drug formulary entry."""
    drug = await crud.update_drug(db, drug_id, update_data.dict(exclude_unset=True))
    if not drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drug not found"
        )

    # Audit log
    background_tasks.add_task(
        create_audit_log,
        db=db,
        action="MASTER_DATA_DRUG_UPDATED",
        resource_type="DrugFormulary",
        resource_id=str(drug_id),
        request_info=request_info,
        changes=update_data.dict(exclude_unset=True),
    )

    return drug


# Procedure Code Endpoints

@router.post("/procedures", response_model=ProcedureCodeResponse, status_code=status.HTTP_201_CREATED)
async def create_procedure_code(
    procedure_data: ProcedureCodeCreate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "create")),
):
    """Create a new procedure code."""
    try:
        # Check if code already exists
        existing = await crud.get_procedure_code_by_code(db, procedure_data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Procedure code already exists"
            )

        procedure = await crud.create_procedure_code(db, procedure_data.dict())

        # Audit log
        background_tasks.add_task(
            create_audit_log,
            db=db,
            action="MASTER_DATA_PROCEDURE_CREATED",
            resource_type="ProcedureCode",
            resource_id=str(procedure.id),
            request_info=request_info,
            changes={"code": procedure.code, "description": procedure.description_indonesian},
        )

        return procedure
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/procedures/{procedure_id}", response_model=ProcedureCodeResponse)
async def get_procedure_code(
    procedure_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """Get procedure code by ID."""
    procedure = await crud.get_procedure_code_by_id(db, procedure_id)
    if not procedure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedure code not found"
        )
    return procedure


@router.get("/procedures", response_model=ProcedureCodeSearchResponse)
async def list_procedure_codes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    code_system: Optional[str] = None,
    code_type: Optional[str] = None,
    department: Optional[str] = None,
    bpjs_covered: Optional[bool] = None,
    is_surgical: Optional[bool] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """List procedure codes with filtering and pagination."""
    start_time = time.time()
    procedures, total = await crud.list_procedure_codes(
        db=db,
        skip=skip,
        limit=limit,
        code_system=code_system,
        code_type=code_type,
        department=department,
        bpjs_covered=bpjs_covered,
        is_surgical=is_surgical,
        search=search,
        is_active=is_active,
    )

    return ProcedureCodeSearchResponse(
        total=total,
        results=procedures,
        search_time_ms=int((time.time() - start_time) * 1000),
    )


@router.get("/procedures/search/{search_term}", response_model=List[ProcedureCodeResponse])
async def search_procedure_codes(
    search_term: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """Full-text search for procedure codes."""
    return await crud.search_procedure_codes(db, search_term, limit)


@router.patch("/procedures/{procedure_id}", response_model=ProcedureCodeResponse)
async def update_procedure_code(
    procedure_id: int,
    update_data: ProcedureCodeUpdate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "update")),
):
    """Update procedure code."""
    procedure = await crud.update_procedure_code(db, procedure_id, update_data.dict(exclude_unset=True))
    if not procedure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedure code not found"
        )

    # Audit log
    background_tasks.add_task(
        create_audit_log,
        db=db,
        action="MASTER_DATA_PROCEDURE_UPDATED",
        resource_type="ProcedureCode",
        resource_id=str(procedure_id),
        request_info=request_info,
        changes=update_data.dict(exclude_unset=True),
    )

    return procedure


# Room Class Endpoints

@router.post("/room-classes", response_model=RoomClassResponse, status_code=status.HTTP_201_CREATED)
async def create_room_class(
    room_data: RoomClassCreate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "create")),
):
    """Create a new room class."""
    try:
        # Check if code already exists
        existing = await crud.get_room_class_by_code(db, room_data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room class code already exists"
            )

        room = await crud.create_room_class(db, room_data.dict())

        # Audit log
        background_tasks.add_task(
            create_audit_log,
            db=db,
            action="MASTER_DATA_ROOM_CLASS_CREATED",
            resource_type="RoomClass",
            resource_id=str(room.id),
            request_info=request_info,
            changes={"code": room.code, "name": room.name},
        )

        return room
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/room-classes/{room_id}", response_model=RoomClassResponse)
async def get_room_class(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """Get room class by ID."""
    room = await crud.get_room_class_by_id(db, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room class not found"
        )
    return room


@router.get("/room-classes", response_model=List[RoomClassResponse])
async def list_room_classes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """List room classes."""
    rooms, _ = await crud.list_room_classes(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
    )
    return rooms


@router.patch("/room-classes/{room_id}", response_model=RoomClassResponse)
async def update_room_class(
    room_id: int,
    update_data: RoomClassUpdate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "update")),
):
    """Update room class."""
    room = await crud.update_room_class(db, room_id, update_data.dict(exclude_unset=True))
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room class not found"
        )

    # Audit log
    background_tasks.add_task(
        create_audit_log,
        db=db,
        action="MASTER_DATA_ROOM_CLASS_UPDATED",
        resource_type="RoomClass",
        resource_id=str(room_id),
        request_info=request_info,
        changes=update_data.dict(exclude_unset=True),
    )

    return room


# Insurance Company Endpoints

@router.post("/insurance-companies", response_model=InsuranceCompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_insurance_company(
    company_data: InsuranceCompanyCreate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "create")),
):
    """Create a new insurance company."""
    try:
        # Check if code already exists
        existing = await crud.get_insurance_company_by_code(db, company_data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insurance company code already exists"
            )

        company = await crud.create_insurance_company(db, company_data.dict())

        # Audit log
        background_tasks.add_task(
            create_audit_log,
            db=db,
            action="MASTER_DATA_INSURANCE_COMPANY_CREATED",
            resource_type="InsuranceCompany",
            resource_id=str(company.id),
            request_info=request_info,
            changes={"code": company.code, "name": company.name},
        )

        return company
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/insurance-companies/{company_id}", response_model=InsuranceCompanyResponse)
async def get_insurance_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """Get insurance company by ID."""
    company = await crud.get_insurance_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance company not found"
        )
    return company


@router.get("/insurance-companies", response_model=List[InsuranceCompanyResponse])
async def list_insurance_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    insurance_type: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """List insurance companies."""
    companies, _ = await crud.list_insurance_companies(
        db=db,
        skip=skip,
        limit=limit,
        insurance_type=insurance_type,
        search=search,
        is_active=is_active,
    )
    return companies


@router.patch("/insurance-companies/{company_id}", response_model=InsuranceCompanyResponse)
async def update_insurance_company(
    company_id: int,
    update_data: InsuranceCompanyUpdate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "update")),
):
    """Update insurance company."""
    company = await crud.update_insurance_company(db, company_id, update_data.dict(exclude_unset=True))
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance company not found"
        )

    # Audit log
    background_tasks.add_task(
        create_audit_log,
        db=db,
        action="MASTER_DATA_INSURANCE_COMPANY_UPDATED",
        resource_type="InsuranceCompany",
        resource_id=str(company_id),
        request_info=request_info,
        changes=update_data.dict(exclude_unset=True),
    )

    return company


# Insurance Plan Endpoints

@router.post("/insurance-plans", response_model=InsurancePlanResponse, status_code=status.HTTP_201_CREATED)
async def create_insurance_plan(
    plan_data: InsurancePlanCreate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "create")),
):
    """Create a new insurance plan."""
    try:
        plan = await crud.create_insurance_plan(db, plan_data.dict())

        # Audit log
        background_tasks.add_task(
            create_audit_log,
            db=db,
            action="MASTER_DATA_INSURANCE_PLAN_CREATED",
            resource_type="InsurancePlan",
            resource_id=str(plan.id),
            request_info=request_info,
            changes={"plan_code": plan.plan_code, "plan_name": plan.plan_name},
        )

        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/insurance-plans/{plan_id}", response_model=InsurancePlanResponse)
async def get_insurance_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """Get insurance plan by ID."""
    plan = await crud.get_insurance_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance plan not found"
        )
    return plan


@router.get("/insurance-plans", response_model=List[InsurancePlanResponse])
async def list_insurance_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    company_id: Optional[int] = None,
    plan_type: Optional[str] = None,
    coverage_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """List insurance plans."""
    plans, _ = await crud.list_insurance_plans(
        db=db,
        skip=skip,
        limit=limit,
        company_id=company_id,
        plan_type=plan_type,
        coverage_type=coverage_type,
        is_active=is_active,
    )
    return plans


@router.patch("/insurance-plans/{plan_id}", response_model=InsurancePlanResponse)
async def update_insurance_plan(
    plan_id: int,
    update_data: InsurancePlanUpdate,
    background_tasks: BackgroundTasks,
    request_info: dict = Depends(get_request_info),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "update")),
):
    """Update insurance plan."""
    plan = await crud.update_insurance_plan(db, plan_id, update_data.dict(exclude_unset=True))
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance plan not found"
        )

    # Audit log
    background_tasks.add_task(
        create_audit_log,
        db=db,
        action="MASTER_DATA_INSURANCE_PLAN_UPDATED",
        resource_type="InsurancePlan",
        resource_id=str(plan_id),
        request_info=request_info,
        changes=update_data.dict(exclude_unset=True),
    )

    return plan


# Statistics Endpoint

@router.get("/statistics", response_model=MasterDataStatistics)
async def get_master_data_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("master_data", "view")),
):
    """Get statistics for all master data tables."""
    return await crud.get_master_data_statistics(db)
