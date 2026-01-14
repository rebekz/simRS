"""Procedure Codes CRUD Operations

This module provides CRUD operations for procedure codes including:
- LOINC codes for laboratory tests
- CPT/HCPCS codes for radiology and medical procedures
- Local hospital procedure codes
- Code searching and filtering
"""
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, and_, or_, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

# Temporarily using dict until models are created
# TODO: Import from app.models.procedure_codes when models are available
# from app.models.procedure_codes import ProcedureCode, LOINCCode, LocalLabCode, LocalRadiologyCode


class ProcedureCodeType:
    """Procedure code type constants"""
    LOINC = "loinc"  # Laboratory tests
    CPT = "cpt"  # Current Procedural Terminology
    HCPCS = "hcpcs"  # Healthcare Common Procedure Coding System
    LOCAL_LAB = "local_lab"  # Local lab codes
    LOCAL_RADIOLOGY = "local_radiology"  # Local radiology codes
    ICD_9_CM = "icd_9_cm"  # ICD-9-CM Procedures (deprecated)
    ICD_10_PCS = "icd_10_pcs"  # ICD-10-PCS Procedures


class ProcedureCategory:
    """Procedure category constants"""
    LABORATORY = "laboratory"
    RADIOLOGY = "radiology"
    SURGERY = "surgery"
    MEDICINE = "medicine"
    ANESTHESIA = "anesthesia"
    PATHOLOGY = "pathology"
    RADIOLOGY_THERAPY = "radiology_therapy"
    DIAGNOSTIC = "diagnostic"
    THERAPEUTIC = "therapeutic"


class LabSection:
    """LOINC lab section categories"""
    CHEMISTRY = "CHEM"  # Clinical chemistry
    HEMATOLOGY = "HEM"  # Hematology
    IMMUNOLOGY = "IMM"  # Immunology
    MICROBIOLOGY = "MIC"  # Microbiology
    SEROLOGY = "SER"  # Serology
    COAGULATION = "COAG"  # Coagulation
    URINALYSIS = "UA"  # Urinalysis
    ENDOCRINOLOGY = "ENDO"  # Endocrinology
    TOXICOLOGY = "TOX"  # Toxicology
    BLOOD_BANK = "BB"  # Blood bank/transfusion
    MOLECULAR = "MOL"  # Molecular diagnostics
    HISTOLOGY = "HIST"  # Histology
    CYTOLOGY = "CYT"  # Cytology


# =============================================================================
# Generic Procedure Code CRUD
# =============================================================================

async def get_procedure_code(
    db: AsyncSession,
    code_id: int,
) -> Optional[Dict[str, Any]]:
    """Get procedure code by ID

    Args:
        db: Async database session
        code_id: Procedure code ID

    Returns:
        Procedure code dict or None if not found
    """
    # TODO: Replace with actual model query when ProcedureCode model exists
    # stmt = select(ProcedureCode).where(ProcedureCode.id == code_id)
    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()

    # Placeholder until model exists
    return None


async def get_procedure_codes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    code_type: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """List procedure codes with filtering and pagination

    Args:
        db: Async database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        code_type: Filter by code type (loinc, cpt, local_lab, etc)
        category: Filter by category (laboratory, radiology, surgery, etc)
        is_active: Filter by active status

    Returns:
        Tuple of (procedure codes list, total count)
    """
    # TODO: Replace with actual model query when ProcedureCode model exists
    # conditions = []
    #
    # if code_type:
    #     conditions.append(ProcedureCode.code_type == code_type)
    # if category:
    #     conditions.append(ProcedureCode.category == category)
    # if is_active is not None:
    #     conditions.append(ProcedureCode.is_active == is_active)
    #
    # # Get total count
    # count_stmt = select(sql_func.count(ProcedureCode.id))
    # if conditions:
    #     count_stmt = count_stmt.where(and_(*conditions))
    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()
    #
    # # Build query
    # stmt = select(ProcedureCode)
    # if conditions:
    #     stmt = stmt.where(and_(*conditions))
    #
    # stmt = stmt.order_by(ProcedureCode.code, ProcedureCode.name)
    # stmt = stmt.offset(skip).limit(limit)
    #
    # result = await db.execute(stmt)
    # codes = result.scalars().all()
    #
    # return list(codes), total

    # Placeholder until model exists
    return [], 0


async def search_procedure_codes(
    db: AsyncSession,
    query: str,
    code_type: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    """Search procedure codes by name, description, or code

    Args:
        db: Async database session
        query: Search query string
        code_type: Filter by code type (optional)
        category: Filter by category (optional)
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (matching procedure codes list, total count)
    """
    # TODO: Replace with actual model query when ProcedureCode model exists
    # search_pattern = f"%{query}%"
    #
    # conditions = [
    #     or_(
    #         ProcedureCode.code.ilike(search_pattern),
    #         ProcedureCode.name.ilike(search_pattern),
    #         ProcedureCode.description.ilike(search_pattern),
    #         ProcedureCode.keywords.ilike(search_pattern),
    #     )
    # ]
    #
    # if code_type:
    #     conditions.append(ProcedureCode.code_type == code_type)
    # if category:
    #     conditions.append(ProcedureCode.category == category)
    #
    # # Get total count
    # count_stmt = select(sql_func.count(ProcedureCode.id)).where(and_(*conditions))
    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()
    #
    # # Build query
    # stmt = select(ProcedureCode).where(and_(*conditions))
    # stmt = stmt.order_by(ProcedureCode.name)
    # stmt = stmt.offset(skip).limit(limit)
    #
    # result = await db.execute(stmt)
    # codes = result.scalars().all()
    #
    # return list(codes), total

    # Placeholder until model exists
    return [], 0


async def create_procedure_code(
    db: AsyncSession,
    code_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Create new procedure code

    Args:
        db: Async database session
        code_data: Dictionary containing:
            - code: Unique procedure code
            - code_type: Type of code (loinc, cpt, local_lab, etc)
            - name: Procedure name
            - description: Optional detailed description
            - category: Category (laboratory, radiology, etc)
            - section: Optional section/subcategory
            - keywords: Optional search keywords (comma-separated)
            - is_active: Default True
            - standard_fee: Optional standard price
            - bpjs_code: Optional BPJS/SATUSEHAT mapping code
            - loinc_code: Optional LOINC mapping (for local codes)

    Returns:
        Created procedure code

    Raises:
        HTTPException: If code already exists or validation fails
    """
    # TODO: Replace with actual model when ProcedureCode model exists
    # # Check if code already exists
    # existing_stmt = select(ProcedureCode).where(
    #     and_(
    #         ProcedureCode.code == code_data["code"],
    #         ProcedureCode.code_type == code_data.get("code_type", ProcedureCodeType.LOCAL_LAB)
    #     )
    # )
    # existing_result = await db.execute(existing_stmt)
    # if existing_result.scalar_one_or_none():
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=f"Procedure code {code_data['code']} already exists"
    #     )
    #
    # # Create procedure code
    # db_code = ProcedureCode(
    #     code=code_data["code"],
    #     code_type=code_data.get("code_type", ProcedureCodeType.LOCAL_LAB),
    #     name=code_data["name"],
    #     description=code_data.get("description"),
    #     category=code_data.get("category"),
    #     section=code_data.get("section"),
    #     keywords=code_data.get("keywords"),
    #     is_active=code_data.get("is_active", True),
    #     standard_fee=code_data.get("standard_fee"),
    #     bpjs_code=code_data.get("bpjs_code"),
    #     loinc_code=code_data.get("loinc_code"),
    # )
    #
    # db.add(db_code)
    # await db.commit()
    # await db.refresh(db_code)
    #
    # return db_code

    # Placeholder until model exists
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Procedure code model not yet implemented"
    )


async def update_procedure_code(
    db: AsyncSession,
    code_id: int,
    update_data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Update procedure code

    Args:
        db: Async database session
        code_id: Procedure code ID
        update_data: Dictionary containing fields to update

    Returns:
        Updated procedure code or None if not found
    """
    # TODO: Replace with actual model when ProcedureCode model exists
    # code = await get_procedure_code(db, code_id)
    # if not code:
    #     return None
    #
    # # Update fields
    # if "name" in update_data:
    #     code.name = update_data["name"]
    # if "description" in update_data:
    #     code.description = update_data["description"]
    # if "category" in update_data:
    #     code.category = update_data["category"]
    # if "section" in update_data:
    #     code.section = update_data["section"]
    # if "keywords" in update_data:
    #     code.keywords = update_data["keywords"]
    # if "is_active" in update_data:
    #     code.is_active = update_data["is_active"]
    # if "standard_fee" in update_data:
    #     code.standard_fee = update_data["standard_fee"]
    # if "bpjs_code" in update_data:
    #     code.bpjs_code = update_data["bpjs_code"]
    # if "loinc_code" in update_data:
    #     code.loinc_code = update_data["loinc_code"]
    #
    # code.updated_at = datetime.now(timezone.utc)
    # await db.commit()
    # await db.refresh(code)
    #
    # return code

    # Placeholder until model exists
    return None


# =============================================================================
# LOINC Code CRUD (Laboratory)
# =============================================================================

async def get_loinc_codes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    section: Optional[str] = None,
    system: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """Get LOINC codes for laboratory tests

    Args:
        db: Async database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        section: Filter by lab section (CHEM, HEM, etc)
        system: Filter by system (Blood, Urine, etc)

    Returns:
        Tuple of (LOINC codes list, total count)
    """
    # TODO: Replace with actual model query when LOINCCode model exists
    # conditions = [ProcedureCode.code_type == ProcedureCodeType.LOINC]
    #
    # if section:
    #     conditions.append(ProcedureCode.section == section)
    # if system:
    #     conditions.append(ProcedureCode.system == system)
    #
    # # Get total count
    # count_stmt = select(sql_func.count(ProcedureCode.id)).where(and_(*conditions))
    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()
    #
    # # Build query
    # stmt = select(ProcedureCode).where(and_(*conditions))
    # stmt = stmt.order_by(ProcedureCode.code)
    # stmt = stmt.offset(skip).limit(limit)
    #
    # result = await db.execute(stmt)
    # codes = result.scalars().all()
    #
    # return list(codes), total

    # Placeholder until model exists
    return [], 0


async def search_loinc_codes(
    db: AsyncSession,
    query: str,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    """Search LOINC codes by name, code, or description

    Args:
        db: Async database session
        query: Search query
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (matching LOINC codes list, total count)
    """
    return await search_procedure_codes(
        db=db,
        query=query,
        code_type=ProcedureCodeType.LOINC,
        skip=skip,
        limit=limit,
    )


# =============================================================================
# Local Lab Code CRUD
# =============================================================================

async def get_local_lab_codes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    section: Optional[str] = None,
    is_active: Optional[bool] = True,
) -> Tuple[List[Dict[str, Any]], int]:
    """Get local hospital laboratory codes

    Args:
        db: Async database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        section: Filter by lab section
        is_active: Filter by active status

    Returns:
        Tuple of (local lab codes list, total count)
    """
    # TODO: Replace with actual model query when LocalLabCode model exists
    # conditions = [ProcedureCode.code_type == ProcedureCodeType.LOCAL_LAB]
    #
    # if section:
    #     conditions.append(ProcedureCode.section == section)
    # if is_active is not None:
    #     conditions.append(ProcedureCode.is_active == is_active)
    #
    # # Get total count
    # count_stmt = select(sql_func.count(ProcedureCode.id)).where(and_(*conditions))
    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()
    #
    # # Build query
    # stmt = select(ProcedureCode).where(and_(*conditions))
    # stmt = stmt.order_by(ProcedureCode.code)
    # stmt = stmt.offset(skip).limit(limit)
    #
    # result = await db.execute(stmt)
    # codes = result.scalars().all()
    #
    # return list(codes), total

    # Placeholder until model exists
    return [], 0


async def create_local_lab_code(
    db: AsyncSession,
    code_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Create local hospital laboratory code

    Args:
        db: Async database session
        code_data: Dictionary containing lab code details plus:
            - section: Lab section (CHEM, HEM, etc)
            - sample_type: Required sample type
            - container_type: Required container
            - fasting_required: Boolean
            - turnaround_minutes: Expected turnaround time
            - loinc_code: Optional mapping to LOINC

    Returns:
        Created local lab code
    """
    # Add code type if not present
    if "code_type" not in code_data:
        code_data = {**code_data, "code_type": ProcedureCodeType.LOCAL_LAB}

    return await create_procedure_code(db, code_data)


# =============================================================================
# Local Radiology Code CRUD
# =============================================================================

async def get_local_radiology_codes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    modality: Optional[str] = None,
    is_active: Optional[bool] = True,
) -> Tuple[List[Dict[str, Any]], int]:
    """Get local hospital radiology codes

    Args:
        db: Async database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        modality: Filter by imaging modality (x_ray, ct, mri, etc)
        is_active: Filter by active status

    Returns:
        Tuple of (local radiology codes list, total count)
    """
    # TODO: Replace with actual model query when LocalRadiologyCode model exists
    # conditions = [ProcedureCode.code_type == ProcedureCodeType.LOCAL_RADIOLOGY]
    #
    # if modality:
    #     conditions.append(ProcedureCode.modality == modality)
    # if is_active is not None:
    #     conditions.append(ProcedureCode.is_active == is_active)
    #
    # # Get total count
    # count_stmt = select(sql_func.count(ProcedureCode.id)).where(and_(*conditions))
    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()
    #
    # # Build query
    # stmt = select(ProcedureCode).where(and_(*conditions))
    # stmt = stmt.order_by(ProcedureCode.code)
    # stmt = stmt.offset(skip).limit(limit)
    #
    # result = await db.execute(stmt)
    # codes = result.scalars().all()
    #
    # return list(codes), total

    # Placeholder until model exists
    return [], 0


async def create_local_radiology_code(
    db: AsyncSession,
    code_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Create local hospital radiology code

    Args:
        db: Async database session
        code_data: Dictionary containing radiology code details plus:
            - modality: Imaging modality (x_ray, ct, mri, etc)
            - body_part_default: Default body part
            - contrast_type: Optional contrast type
            - duration_minutes: Expected procedure duration
            - preparation: Patient preparation instructions
            - cpt_code: Optional CPT code mapping

    Returns:
        Created local radiology code
    """
    # Add code type if not present
    if "code_type" not in code_data:
        code_data = {**code_data, "code_type": ProcedureCodeType.LOCAL_RADIOLOGY}

    return await create_procedure_code(db, code_data)


# =============================================================================
# Helper Functions
# =============================================================================

async def get_common_lab_tests(
    db: AsyncSession,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Get commonly ordered laboratory tests

    Args:
        db: Async database session
        limit: Maximum number of tests to return

    Returns:
        List of common lab tests
    """
    # TODO: Implement with actual model and usage tracking
    # This would return the most frequently ordered lab tests
    return []


async def get_common_radiology_tests(
    db: AsyncSession,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Get commonly ordered radiology tests

    Args:
        db: Async database session
        limit: Maximum number of tests to return

    Returns:
        List of common radiology tests
    """
    # TODO: Implement with actual model and usage tracking
    # This would return the most frequently ordered radiology tests
    return []


async def map_bpjs_to_local_code(
    db: AsyncSession,
    bpjs_code: str,
    code_type: str,
) -> Optional[Dict[str, Any]]:
    """Map BPJS procedure code to local hospital code

    Args:
        db: Async database session
        bpjs_code: BPJS procedure code
        code_type: Type of code (lab or radiology)

    Returns:
        Mapped local procedure code or None if not found
    """
    # TODO: Implement with actual model
    # stmt = select(ProcedureCode).where(
    #     and_(
    #         ProcedureCode.bpjs_code == bpjs_code,
    #         ProcedureCode.code_type == code_type,
    #         ProcedureCode.is_active == True,
    #     )
    # )
    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()

    return None
