"""
Master Data CRUD Operations

This module provides CRUD operations for managing master/reference data
including ICD-10 codes, LOINC codes, drugs, procedures, room classes, and insurance.
"""

import time
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.master_data import (
    ICD10Code,
    LOINCCode,
    DrugFormulary,
    ProcedureCode,
    RoomClass,
    InsuranceCompany,
    InsurancePlan,
    ReferenceData,
)


# ICD-10 Code CRUD

async def create_icd10_code(db: AsyncSession, code_data: Dict[str, Any]) -> ICD10Code:
    """Create a new ICD-10 code."""
    db_code = ICD10Code(**code_data)
    db.add(db_code)
    await db.commit()
    await db.refresh(db_code)
    return db_code


async def get_icd10_code_by_id(db: AsyncSession, code_id: int) -> Optional[ICD10Code]:
    """Get ICD-10 code by ID."""
    result = await db.execute(select(ICD10Code).where(ICD10Code.id == code_id))
    return result.scalar_one_or_none()


async def get_icd10_code_by_code(db: AsyncSession, code: str) -> Optional[ICD10Code]:
    """Get ICD-10 code by code."""
    result = await db.execute(select(ICD10Code).where(ICD10Code.code == code))
    return result.scalar_one_or_none()


async def list_icd10_codes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    chapter: Optional[str] = None,
    search: Optional[str] = None,
    is_common: Optional[bool] = None,
    is_active: Optional[bool] = None,
) -> tuple[List[ICD10Code], int]:
    """List ICD-10 codes with filtering and pagination."""
    query = select(ICD10Code)
    count_query = select(func.count(ICD10Code.id))

    conditions = []

    if chapter:
        conditions.append(ICD10Code.chapter == chapter)
    if search:
        search_pattern = "%{}%".format(search)
        conditions.append(
            or_(
                ICD10Code.code.ilike(search_pattern),
                ICD10Code.description_indonesian.ilike(search_pattern),
                ICD10Code.description_english.ilike(search_pattern),
            )
        )
    if is_common is not None:
        conditions.append(ICD10Code.is_common == is_common)
    if is_active is not None:
        conditions.append(ICD10Code.is_active == is_active)

    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(ICD10Code.code).offset(skip).limit(limit)
    result = await db.execute(query)
    codes = result.scalars().all()

    return list(codes), total


async def search_icd10_codes(
    db: AsyncSession,
    search_term: str,
    limit: int = 20,
) -> List[ICD10Code]:
    """Full-text search for ICD-10 codes."""
    search_pattern = "%{}%".format(search_term)

    query = (
        select(ICD10Code)
        .where(
            and_(
                ICD10Code.is_active == True,
                or_(
                    ICD10Code.code.ilike(search_pattern),
                    ICD10Code.description_indonesian.ilike(search_pattern),
                    ICD10Code.description_english.ilike(search_pattern),
                )
            )
        )
        .order_by(ICD10Code.usage_count.desc(), ICD10Code.code)
        .limit(limit)
    )

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_icd10_code(db: AsyncSession, code_id: int, update_data: Dict[str, Any]) -> Optional[ICD10Code]:
    """Update ICD-10 code."""
    db_code = await get_icd10_code_by_id(db, code_id)
    if not db_code:
        return None

    for field, value in update_data.items():
        if hasattr(db_code, field):
            setattr(db_code, field, value)

    await db.commit()
    await db.refresh(db_code)
    return db_code


async def increment_icd10_usage(db: AsyncSession, code_id: int) -> None:
    """Increment usage count for ICD-10 code."""
    db_code = await get_icd10_code_by_id(db, code_id)
    if db_code:
        db_code.usage_count += 1
        await db.commit()


# LOINC Code CRUD

async def create_loinc_code(db: AsyncSession, code_data: Dict[str, Any]) -> LOINCCode:
    """Create a new LOINC code."""
    db_code = LOINCCode(**code_data)
    db.add(db_code)
    await db.commit()
    await db.refresh(db_code)
    return db_code


async def get_loinc_code_by_id(db: AsyncSession, code_id: int) -> Optional[LOINCCode]:
    """Get LOINC code by ID."""
    result = await db.execute(select(LOINCCode).where(LOINCCode.id == code_id))
    return result.scalar_one_or_none()


async def get_loinc_code_by_num(db: AsyncSession, loinc_num: str) -> Optional[LOINCCode]:
    """Get LOINC code by LOINC number."""
    result = await db.execute(select(LOINCCode).where(LOINCCode.loinc_num == loinc_num))
    return result.scalar_one_or_none()


async def list_loinc_codes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    class_name: Optional[str] = None,
    search: Optional[str] = None,
    is_common: Optional[bool] = None,
    is_active: Optional[bool] = None,
) -> tuple[List[LOINCCode], int]:
    """List LOINC codes with filtering and pagination."""
    query = select(LOINCCode)
    count_query = select(func.count(LOINCCode.id))

    conditions = []

    if class_name:
        conditions.append(LOINCCode.class_name == class_name)
    if search:
        search_pattern = "%{}%".format(search)
        conditions.append(
            or_(
                LOINCCode.loinc_num.ilike(search_pattern),
                LOINCCode.component.ilike(search_pattern),
                LOINCCode.long_common_name.ilike(search_pattern),
            )
        )
    if is_common is not None:
        conditions.append(LOINCCode.is_common == is_common)
    if is_active is not None:
        conditions.append(LOINCCode.is_active == is_active)

    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(LOINCCode.loinc_num).offset(skip).limit(limit)
    result = await db.execute(query)
    codes = result.scalars().all()

    return list(codes), total


async def search_loinc_codes(
    db: AsyncSession,
    search_term: str,
    limit: int = 20,
) -> List[LOINCCode]:
    """Full-text search for LOINC codes."""
    search_pattern = "%{}%".format(search_term)

    query = (
        select(LOINCCode)
        .where(
            and_(
                LOINCCode.is_active == True,
                or_(
                    LOINCCode.loinc_num.ilike(search_pattern),
                    LOINCCode.component.ilike(search_pattern),
                    LOINCCode.long_common_name.ilike(search_pattern),
                    LOINCCode.short_name.ilike(search_pattern),
                )
            )
        )
        .order_by(LOINCCode.usage_count.desc(), LOINCCode.loinc_num)
        .limit(limit)
    )

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_loinc_code(db: AsyncSession, code_id: int, update_data: Dict[str, Any]) -> Optional[LOINCCode]:
    """Update LOINC code."""
    db_code = await get_loinc_code_by_id(db, code_id)
    if not db_code:
        return None

    for field, value in update_data.items():
        if hasattr(db_code, field):
            setattr(db_code, field, value)

    await db.commit()
    await db.refresh(db_code)
    return db_code


async def increment_loinc_usage(db: AsyncSession, code_id: int) -> None:
    """Increment usage count for LOINC code."""
    db_code = await get_loinc_code_by_id(db, code_id)
    if db_code:
        db_code.usage_count += 1
        await db.commit()


# Drug Formulary CRUD

async def create_drug(db: AsyncSession, drug_data: Dict[str, Any]) -> DrugFormulary:
    """Create a new drug formulary entry."""
    db_drug = DrugFormulary(**drug_data)
    db.add(db_drug)
    await db.commit()
    await db.refresh(db_drug)
    return db_drug


async def get_drug_by_id(db: AsyncSession, drug_id: int) -> Optional[DrugFormulary]:
    """Get drug by ID."""
    result = await db.execute(select(DrugFormulary).where(DrugFormulary.id == drug_id))
    return result.scalar_one_or_none()


async def list_drugs(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    generic_name: Optional[str] = None,
    dosage_form: Optional[str] = None,
    bpjs_covered: Optional[bool] = None,
    is_narcotic: Optional[bool] = None,
    is_antibiotic: Optional[bool] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> tuple[List[DrugFormulary], int]:
    """List drugs with filtering and pagination."""
    query = select(DrugFormulary)
    count_query = select(func.count(DrugFormulary.id))

    conditions = []

    if generic_name:
        conditions.append(DrugFormulary.generic_name.ilike("%{}%".format(generic_name)))
    if dosage_form:
        conditions.append(DrugFormulary.dosage_form == dosage_form)
    if bpjs_covered is not None:
        conditions.append(DrugFormulary.bpjs_covered == bpjs_covered)
    if is_narcotic is not None:
        conditions.append(DrugFormulary.is_narcotic == is_narcotic)
    if is_antibiotic is not None:
        conditions.append(DrugFormulary.is_antibiotic == is_antibiotic)
    if search:
        search_pattern = "%{}%".format(search)
        conditions.append(
            or_(
                DrugFormulary.generic_name.ilike(search_pattern),
                DrugFormulary.brand_names.astext.ilike(search_pattern),
            )
        )
    if is_active is not None:
        conditions.append(DrugFormulary.is_active == is_active)

    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(DrugFormulary.generic_name).offset(skip).limit(limit)
    result = await db.execute(query)
    drugs = result.scalars().all()

    return list(drugs), total


async def search_drugs(
    db: AsyncSession,
    search_term: str,
    limit: int = 20,
) -> List[DrugFormulary]:
    """Full-text search for drugs."""
    search_pattern = "%{}%".format(search_term)

    query = (
        select(DrugFormulary)
        .where(
            and_(
                DrugFormulary.is_active == True,
                or_(
                    DrugFormulary.generic_name.ilike(search_pattern),
                    DrugFormulary.brand_names.astext.ilike(search_pattern),
                )
            )
        )
        .order_by(DrugFormulary.generic_name)
        .limit(limit)
    )

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_drug(db: AsyncSession, drug_id: int, update_data: Dict[str, Any]) -> Optional[DrugFormulary]:
    """Update drug formulary entry."""
    db_drug = await get_drug_by_id(db, drug_id)
    if not db_drug:
        return None

    for field, value in update_data.items():
        if hasattr(db_drug, field):
            setattr(db_drug, field, value)

    await db.commit()
    await db.refresh(db_drug)
    return db_drug


# Procedure Code CRUD

async def create_procedure_code(db: AsyncSession, procedure_data: Dict[str, Any]) -> ProcedureCode:
    """Create a new procedure code."""
    db_procedure = ProcedureCode(**procedure_data)
    db.add(db_procedure)
    await db.commit()
    await db.refresh(db_procedure)
    return db_procedure


async def get_procedure_code_by_id(db: AsyncSession, procedure_id: int) -> Optional[ProcedureCode]:
    """Get procedure code by ID."""
    result = await db.execute(select(ProcedureCode).where(ProcedureCode.id == procedure_id))
    return result.scalar_one_or_none()


async def get_procedure_code_by_code(db: AsyncSession, code: str) -> Optional[ProcedureCode]:
    """Get procedure code by code."""
    result = await db.execute(select(ProcedureCode).where(ProcedureCode.code == code))
    return result.scalar_one_or_none()


async def list_procedure_codes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    code_system: Optional[str] = None,
    code_type: Optional[str] = None,
    department: Optional[str] = None,
    bpjs_covered: Optional[bool] = None,
    is_surgical: Optional[bool] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> tuple[List[ProcedureCode], int]:
    """List procedure codes with filtering and pagination."""
    query = select(ProcedureCode)
    count_query = select(func.count(ProcedureCode.id))

    conditions = []

    if code_system:
        conditions.append(ProcedureCode.code_system == code_system)
    if code_type:
        conditions.append(ProcedureCode.code_type == code_type)
    if department:
        conditions.append(ProcedureCode.department.ilike("%{}%".format(department)))
    if bpjs_covered is not None:
        conditions.append(ProcedureCode.bpjs_covered == bpjs_covered)
    if is_surgical is not None:
        conditions.append(ProcedureCode.is_surgical == is_surgical)
    if search:
        search_pattern = "%{}%".format(search)
        conditions.append(
            or_(
                ProcedureCode.code.ilike(search_pattern),
                ProcedureCode.description_indonesian.ilike(search_pattern),
                ProcedureCode.description_english.ilike(search_pattern),
            )
        )
    if is_active is not None:
        conditions.append(ProcedureCode.is_active == is_active)

    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(ProcedureCode.code).offset(skip).limit(limit)
    result = await db.execute(query)
    procedures = result.scalars().all()

    return list(procedures), total


async def search_procedure_codes(
    db: AsyncSession,
    search_term: str,
    limit: int = 20,
) -> List[ProcedureCode]:
    """Full-text search for procedure codes."""
    search_pattern = "%{}%".format(search_term)

    query = (
        select(ProcedureCode)
        .where(
            and_(
                ProcedureCode.is_active == True,
                or_(
                    ProcedureCode.code.ilike(search_pattern),
                    ProcedureCode.description_indonesian.ilike(search_pattern),
                    ProcedureCode.description_english.ilike(search_pattern),
                )
            )
        )
        .order_by(ProcedureCode.usage_count.desc(), ProcedureCode.code)
        .limit(limit)
    )

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_procedure_code(db: AsyncSession, procedure_id: int, update_data: Dict[str, Any]) -> Optional[ProcedureCode]:
    """Update procedure code."""
    db_procedure = await get_procedure_code_by_id(db, procedure_id)
    if not db_procedure:
        return None

    for field, value in update_data.items():
        if hasattr(db_procedure, field):
            setattr(db_procedure, field, value)

    await db.commit()
    await db.refresh(db_procedure)
    return db_procedure


async def increment_procedure_usage(db: AsyncSession, procedure_id: int) -> None:
    """Increment usage count for procedure code."""
    db_procedure = await get_procedure_code_by_id(db, procedure_id)
    if db_procedure:
        db_procedure.usage_count += 1
        await db.commit()


# Room Class CRUD

async def create_room_class(db: AsyncSession, room_data: Dict[str, Any]) -> RoomClass:
    """Create a new room class."""
    db_room = RoomClass(**room_data)
    db.add(db_room)
    await db.commit()
    await db.refresh(db_room)
    return db_room


async def get_room_class_by_id(db: AsyncSession, room_id: int) -> Optional[RoomClass]:
    """Get room class by ID."""
    result = await db.execute(select(RoomClass).where(RoomClass.id == room_id))
    return result.scalar_one_or_none()


async def get_room_class_by_code(db: AsyncSession, code: str) -> Optional[RoomClass]:
    """Get room class by code."""
    result = await db.execute(select(RoomClass).where(RoomClass.code == code))
    return result.scalar_one_or_none()


async def list_room_classes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
) -> tuple[List[RoomClass], int]:
    """List room classes."""
    query = select(RoomClass)
    count_query = select(func.count(RoomClass.id))

    if is_active is not None:
        query = query.where(RoomClass.is_active == is_active)
        count_query = count_query.where(RoomClass.is_active == is_active)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(RoomClass.daily_rate.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    rooms = result.scalars().all()

    return list(rooms), total


async def update_room_class(db: AsyncSession, room_id: int, update_data: Dict[str, Any]) -> Optional[RoomClass]:
    """Update room class."""
    db_room = await get_room_class_by_id(db, room_id)
    if not db_room:
        return None

    for field, value in update_data.items():
        if hasattr(db_room, field):
            setattr(db_room, field, value)

    await db.commit()
    await db.refresh(db_room)
    return db_room


# Insurance Company CRUD

async def create_insurance_company(db: AsyncSession, company_data: Dict[str, Any]) -> InsuranceCompany:
    """Create a new insurance company."""
    db_company = InsuranceCompany(**company_data)
    db.add(db_company)
    await db.commit()
    await db.refresh(db_company)
    return db_company


async def get_insurance_company_by_id(db: AsyncSession, company_id: int) -> Optional[InsuranceCompany]:
    """Get insurance company by ID."""
    result = await db.execute(select(InsuranceCompany).where(InsuranceCompany.id == company_id))
    return result.scalar_one_or_none()


async def get_insurance_company_by_code(db: AsyncSession, code: str) -> Optional[InsuranceCompany]:
    """Get insurance company by code."""
    result = await db.execute(select(InsuranceCompany).where(InsuranceCompany.code == code))
    return result.scalar_one_or_none()


async def list_insurance_companies(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    insurance_type: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> tuple[List[InsuranceCompany], int]:
    """List insurance companies."""
    query = select(InsuranceCompany)
    count_query = select(func.count(InsuranceCompany.id))

    conditions = []

    if insurance_type:
        conditions.append(InsuranceCompany.insurance_type == insurance_type)
    if search:
        search_pattern = "%{}%".format(search)
        conditions.append(
            or_(
                InsuranceCompany.name.ilike(search_pattern),
                InsuranceCompany.code.ilike(search_pattern),
            )
        )
    if is_active is not None:
        conditions.append(InsuranceCompany.is_active == is_active)

    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(InsuranceCompany.name).offset(skip).limit(limit)
    result = await db.execute(query)
    companies = result.scalars().all()

    return list(companies), total


async def update_insurance_company(db: AsyncSession, company_id: int, update_data: Dict[str, Any]) -> Optional[InsuranceCompany]:
    """Update insurance company."""
    db_company = await get_insurance_company_by_id(db, company_id)
    if not db_company:
        return None

    for field, value in update_data.items():
        if hasattr(db_company, field):
            setattr(db_company, field, value)

    await db.commit()
    await db.refresh(db_company)
    return db_company


# Insurance Plan CRUD

async def create_insurance_plan(db: AsyncSession, plan_data: Dict[str, Any]) -> InsurancePlan:
    """Create a new insurance plan."""
    db_plan = InsurancePlan(**plan_data)
    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)
    return db_plan


async def get_insurance_plan_by_id(db: AsyncSession, plan_id: int) -> Optional[InsurancePlan]:
    """Get insurance plan by ID."""
    result = await db.execute(select(InsurancePlan).where(InsurancePlan.id == plan_id))
    return result.scalar_one_or_none()


async def list_insurance_plans(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    plan_type: Optional[str] = None,
    coverage_type: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> tuple[List[InsurancePlan], int]:
    """List insurance plans."""
    query = select(InsurancePlan)
    count_query = select(func.count(InsurancePlan.id))

    conditions = []

    if company_id:
        conditions.append(InsurancePlan.company_id == company_id)
    if plan_type:
        conditions.append(InsurancePlan.plan_type == plan_type)
    if coverage_type:
        conditions.append(InsurancePlan.coverage_type == coverage_type)
    if is_active is not None:
        conditions.append(InsurancePlan.is_active == is_active)

    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(InsurancePlan.plan_name).offset(skip).limit(limit)
    result = await db.execute(query)
    plans = result.scalars().all()

    return list(plans), total


async def update_insurance_plan(db: AsyncSession, plan_id: int, update_data: Dict[str, Any]) -> Optional[InsurancePlan]:
    """Update insurance plan."""
    db_plan = await get_insurance_plan_by_id(db, plan_id)
    if not db_plan:
        return None

    for field, value in update_data.items():
        if hasattr(db_plan, field):
            setattr(db_plan, field, value)

    await db.commit()
    await db.refresh(db_plan)
    return db_plan


# Reference Data CRUD

async def create_reference_data(db: AsyncSession, data: Dict[str, Any]) -> ReferenceData:
    """Create new reference data."""
    db_data = ReferenceData(**data)
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)
    return db_data


async def get_reference_data_by_id(db: AsyncSession, data_id: int) -> Optional[ReferenceData]:
    """Get reference data by ID."""
    result = await db.execute(select(ReferenceData).where(ReferenceData.id == data_id))
    return result.scalar_one_or_none()


async def list_reference_data(
    db: AsyncSession,
    category: str,
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[int] = None,
    is_active: Optional[bool] = None,
) -> tuple[List[ReferenceData], int]:
    """List reference data by category."""
    query = select(ReferenceData)
    count_query = select(func.count(ReferenceData.id))

    conditions = [ReferenceData.category == category]

    if parent_id is not None:
        conditions.append(ReferenceData.parent_id == parent_id)
    if is_active is not None:
        conditions.append(ReferenceData.is_active == is_active)

    query = query.where(and_(*conditions))
    count_query = count_query.where(and_(*conditions))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(ReferenceData.display_order, ReferenceData.name).offset(skip).limit(limit)
    result = await db.execute(query)
    data_list = result.scalars().all()

    return list(data_list), total


async def update_reference_data(db: AsyncSession, data_id: int, update_data: Dict[str, Any]) -> Optional[ReferenceData]:
    """Update reference data."""
    db_data = await get_reference_data_by_id(db, data_id)
    if not db_data:
        return None

    for field, value in update_data.items():
        if hasattr(db_data, field):
            setattr(db_data, field, value)

    await db.commit()
    await db.refresh(db_data)
    return db_data


# Statistics

async def get_master_data_statistics(db: AsyncSession) -> Dict[str, Any]:
    """Get statistics for all master data tables."""
    start_time = time.time()

    # ICD-10 statistics
    icd10_total_result = await db.execute(select(func.count(ICD10Code.id)))
    icd10_total = icd10_total_result.scalar() or 0
    icd10_active_result = await db.execute(select(func.count(ICD10Code.id)).where(ICD10Code.is_active == True))
    icd10_active = icd10_active_result.scalar() or 0

    # LOINC statistics
    loinc_total_result = await db.execute(select(func.count(LOINCCode.id)))
    loinc_total = loinc_total_result.scalar() or 0
    loinc_active_result = await db.execute(select(func.count(LOINCCode.id)).where(LOINCCode.is_active == True))
    loinc_active = loinc_active_result.scalar() or 0

    # Drug statistics
    drug_total_result = await db.execute(select(func.count(DrugFormulary.id)))
    drug_total = drug_total_result.scalar() or 0
    drug_active_result = await db.execute(select(func.count(DrugFormulary.id)).where(DrugFormulary.is_active == True))
    drug_active = drug_active_result.scalar() or 0

    # Procedure statistics
    procedure_total_result = await db.execute(select(func.count(ProcedureCode.id)))
    procedure_total = procedure_total_result.scalar() or 0
    procedure_active_result = await db.execute(select(func.count(ProcedureCode.id)).where(ProcedureCode.is_active == True))
    procedure_active = procedure_active_result.scalar() or 0

    # Insurance company statistics
    company_total_result = await db.execute(select(func.count(InsuranceCompany.id)))
    company_total = company_total_result.scalar() or 0
    company_active_result = await db.execute(select(func.count(InsuranceCompany.id)).where(InsuranceCompany.is_active == True))
    company_active = company_active_result.scalar() or 0

    # Insurance plan statistics
    plan_total_result = await db.execute(select(func.count(InsurancePlan.id)))
    plan_total = plan_total_result.scalar() or 0
    plan_active_result = await db.execute(select(func.count(InsurancePlan.id)).where(InsurancePlan.is_active == True))
    plan_active = plan_active_result.scalar() or 0

    # Room class statistics
    room_total_result = await db.execute(select(func.count(RoomClass.id)))
    room_total = room_total_result.scalar() or 0
    room_active_result = await db.execute(select(func.count(RoomClass.id)).where(RoomClass.is_active == True))
    room_active = room_active_result.scalar() or 0

    return {
        "icd10_codes_total": icd10_total,
        "icd10_codes_active": icd10_active,
        "loinc_codes_total": loinc_total,
        "loinc_codes_active": loinc_active,
        "drugs_total": drug_total,
        "drugs_active": drug_active,
        "procedures_total": procedure_total,
        "procedures_active": procedure_active,
        "insurance_companies_total": company_total,
        "insurance_companies_active": company_active,
        "insurance_plans_total": plan_total,
        "insurance_plans_active": plan_active,
        "room_classes_total": room_total,
        "room_classes_active": room_active,
        "query_time_ms": int((time.time() - start_time) * 1000),
    }
