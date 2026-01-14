"""BPJS Claims CRUD Operations

This module provides comprehensive CRUD operations for BPJS claims management including:
- Claim lifecycle management (create, update, delete, status tracking)
- Claim items and procedures
- Document management and verification
- Submission to BPJS API
- Verification queries handling
- Reporting and statistics

Supports BPJS claim requirements including:
- INA-CBG (Indonesian Case Base Groups) package claims
- E-Claim submission format
- Verification query management
- Deadline tracking
- Document requirements validation
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_, or_, func as sql_func, desc, update, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from decimal import Decimal

# Import models when they are created
# from app.models.bpjs_claims import (
#     BPJSClaim, BPJSClaimItem, BPJSClaimDocument,
#     BPJSClaimSubmission, BPJSVerificationQuery,
#     ClaimStatus, ClaimType, SubmissionStatus, QueryStatus
# )
# from app.schemas.bpjs_claims import (
#     BPJSClaimCreate, BPJSClaimUpdate,
#     BPJSClaimItemCreate, BPJSClaimItemUpdate,
#     BPJSClaimDocumentCreate
# )


# =============================================================================
# Claim Management - Basic CRUD
# =============================================================================

async def get_bpjs_claim(
    db: AsyncSession,
    claim_id: int,
) -> Optional[Any]:
    """
    Get BPJS claim by ID with all relationships.

    Args:
        db: Database session
        claim_id: Claim ID

    Returns:
        BPJSClaim object or None
    """
    # stmt = (
    #     select(BPJSClaim)
    #     .options(
    #         selectinload(BPJSClaim.items),
    #         selectinload(BPJSClaim.documents),
    #         selectinload(BPJSClaim.submissions),
    #         selectinload(BPJSClaim.verification_queries),
    #         selectinload(BPJSClaim.patient),
    #         selectinload(BPJSClaim.encounter),
    #         selectinload(BPJSClaim.invoice)
    #     )
    #     .where(BPJSClaim.id == claim_id)
    # )
    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()
    return None


async def get_bpjs_claim_by_number(
    db: AsyncSession,
    claim_number: str,
) -> Optional[Any]:
    """
    Get BPJS claim by claim number.

    Args:
        db: Database session
        claim_number: Unique claim number

    Returns:
        BPJSClaim object or None
    """
    # stmt = select(BPJSClaim).where(BPJSClaim.claim_number == claim_number)
    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()
    return None


async def get_bpjs_claims(
    db: AsyncSession,
    patient_id: Optional[int] = None,
    encounter_id: Optional[int] = None,
    invoice_id: Optional[int] = None,
    status: Optional[str] = None,
    claim_type: Optional[str] = None,
    service_type: Optional[str] = None,
    submission_date_from: Optional[date] = None,
    submission_date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    List BPJS claims with filtering and pagination.

    Args:
        db: Database session
        patient_id: Filter by patient
        encounter_id: Filter by encounter
        invoice_id: Filter by invoice
        status: Filter by status
        claim_type: Filter by claim type (inpatient, outpatient)
        service_type: Filter by service type
        submission_date_from: Filter by submission date start
        submission_date_to: Filter by submission date end
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (list of claims, total count)
    """
    # conditions = []
    # if patient_id:
    #     conditions.append(BPJSClaim.patient_id == patient_id)
    # if encounter_id:
    #     conditions.append(BPJSClaim.encounter_id == encounter_id)
    # if invoice_id:
    #     conditions.append(BPJSClaim.invoice_id == invoice_id)
    # if status:
    #     conditions.append(BPJSClaim.status == status)
    # if claim_type:
    #     conditions.append(BPJSClaim.claim_type == claim_type)
    # if service_type:
    #     conditions.append(BPJSClaim.service_type == service_type)
    # if submission_date_from:
    #     conditions.append(BPJSClaim.submission_date >= submission_date_from)
    # if submission_date_to:
    #     conditions.append(BPJSClaim.submission_date <= submission_date_to)

    # stmt = select(BPJSClaim)
    # if conditions:
    #     stmt = stmt.where(and_(*conditions))

    # count_stmt = select(sql_func.count(BPJSClaim.id))
    # if conditions:
    #     count_stmt = count_stmt.where(and_(*conditions))

    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()

    # stmt = stmt.options(selectinload(BPJSClaim.items))
    # stmt = stmt.order_by(BPJSClaim.created_at.desc())
    # stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    # result = await db.execute(stmt)
    # claims = result.scalars().all()

    # return list(claims), total
    return [], 0


async def create_bpjs_claim(
    db: AsyncSession,
    claim_data: Dict[str, Any],
    created_by_id: int,
) -> Any:
    """
    Create a new BPJS claim.

    Args:
        db: Database session
        claim_data: Claim creation data
        created_by_id: User ID creating the claim

    Returns:
        Created BPJSClaim object
    """
    # Generate claim number
    claim_number = await generate_claim_number(db)

    # db_claim = BPJSClaim(
    #     claim_number=claim_number,
    #     patient_id=claim_data.get('patient_id'),
    #     encounter_id=claim_data.get('encounter_id'),
    #     invoice_id=claim_data.get('invoice_id'),
    #     sep_number=claim_data.get('sep_number'),
    #     claim_type=claim_data.get('claim_type', 'inpatient'),
    #     service_type=claim_data.get('service_type'),
    #     cbg_code=claim_data.get('cbg_code'),
    #     admission_date=claim_data.get('admission_date'),
    #     discharge_date=claim_data.get('discharge_date'),
    #     treatment_class=claim_data.get('treatment_class'),
    #     diagnosis_codes=claim_data.get('diagnosis_codes', []),
    #     procedure_codes=claim_data.get('procedure_codes', []),
    #     status='draft',
    #     notes=claim_data.get('notes'),
    #     created_by_id=created_by_id,
    # )

    # db.add(db_claim)
    # await db.flush()

    # # Add claim items if provided
    # if 'items' in claim_data:
    #     for item_data in claim_data['items']:
    #         await add_claim_item(db, db_claim.id, item_data, created_by_id)

    # # Calculate package rate
    # if db_claim.cbg_code:
    #     await calculate_package_rate(db, db_claim.id)

    # await db.commit()
    # await db.refresh(db_claim)

    # return db_claim
    return None


async def update_bpjs_claim(
    db: AsyncSession,
    claim_id: int,
    claim_update: Dict[str, Any],
    updated_by_id: int,
) -> Optional[Any]:
    """
    Update an existing BPJS claim.

    Args:
        db: Database session
        claim_id: Claim ID
        claim_update: Update data
        updated_by_id: User ID updating the claim

    Returns:
        Updated BPJSClaim or None
    """
    # claim = await get_bpjs_claim(db, claim_id)
    # if not claim:
    #     return None

    # # Only allow updates to draft or pending claims
    # if claim.status not in ['draft', 'pending', 'returned']:
    #     raise ValueError("Can only update draft, pending, or returned claims")

    # # Track previous status for audit
    # previous_status = claim.status

    # for field, value in claim_update.items():
    #     if field in ['items', 'documents']:
    #         continue  # Handle separately
    #     if hasattr(claim, field) and value is not None:
    #         setattr(claim, field, value)

    # claim.updated_by_id = updated_by_id

    # # Recalculate package rate if CBG code changed
    # if 'cbg_code' in claim_update and claim_update['cbg_code']:
    #     await calculate_package_rate(db, claim_id)

    # await db.commit()
    # await db.refresh(claim)

    # # Log status change
    # if 'status' in claim_update and claim_update['status'] != previous_status:
    #     await log_claim_status_change(db, claim_id, previous_status, claim_update['status'], updated_by_id)

    # return claim
    return None


async def delete_bpjs_claim(
    db: AsyncSession,
    claim_id: int,
    deleted_by_id: int,
    reason: Optional[str] = None,
) -> bool:
    """
    Soft delete a BPJS claim (only draft or rejected claims).

    Args:
        db: Database session
        claim_id: Claim ID
        deleted_by_id: User ID deleting the claim
        reason: Deletion reason

    Returns:
        True if deleted, False otherwise
    """
    # claim = await get_bpjs_claim(db, claim_id)
    # if not claim:
    #     return False

    # if claim.status not in ['draft', 'rejected']:
    #     raise ValueError("Can only delete draft or rejected claims")

    # claim.is_deleted = True
    # claim.deleted_at = datetime.utcnow()
    # claim.deleted_by_id = deleted_by_id
    # claim.deletion_reason = reason

    # await db.commit()
    # return True
    return False


# =============================================================================
# Claim Management - Query Functions
# =============================================================================

async def get_claims_by_encounter(
    db: AsyncSession,
    encounter_id: int,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get all claims for a specific encounter.

    Args:
        db: Database session
        encounter_id: Encounter ID
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (claims, total count)
    """
    return await get_bpjs_claims(
        db=db,
        encounter_id=encounter_id,
        page=page,
        page_size=page_size,
    )


async def get_claims_by_invoice(
    db: AsyncSession,
    invoice_id: int,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get all claims for a specific invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (claims, total count)
    """
    return await get_bpjs_claims(
        db=db,
        invoice_id=invoice_id,
        page=page,
        page_size=page_size,
    )


async def get_claims_by_patient(
    db: AsyncSession,
    patient_id: int,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get all claims for a specific patient.

    Args:
        db: Database session
        patient_id: Patient ID
        status: Optional status filter
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (claims, total count)
    """
    return await get_bpjs_claims(
        db=db,
        patient_id=patient_id,
        status=status,
        page=page,
        page_size=page_size,
    )


async def get_pending_claims(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get claims pending submission or verification.

    Args:
        db: Database session
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (claims, total count)
    """
    return await get_bpjs_claims(
        db=db,
        status='pending',
        page=page,
        page_size=page_size,
    )


async def get_submitted_claims(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get claims submitted to BPJS.

    Args:
        db: Database session
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (claims, total count)
    """
    return await get_bpjs_claims(
        db=db,
        status='submitted',
        page=page,
        page_size=page_size,
    )


async def get_verified_claims(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get verified claims (approved or paid).

    Args:
        db: Database session
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (claims, total count)
    """
    # stmt = select(BPJSClaim).where(
    #     BPJSClaim.status.in_(['verified', 'approved', 'paid'])
    # )
    # count_stmt = select(sql_func.count(BPJSClaim.id)).where(
    #     BPJSClaim.status.in_(['verified', 'approved', 'paid'])
    # )

    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()

    # stmt = stmt.options(selectinload(BPJSClaim.items))
    # stmt = stmt.order_by(BPJSClaim.submission_date.desc())
    # stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    # result = await db.execute(stmt)
    # claims = result.scalars().all()

    # return list(claims), total
    return [], 0


# =============================================================================
# Claim Number and Data Generation
# =============================================================================

async def generate_claim_number(db: AsyncSession) -> str:
    """
    Generate a unique BPJS claim number.
    Format: CLAIM-YYYY-XXXXX (sequential per year)

    Args:
        db: Database session

    Returns:
        Unique claim number
    """
    # year = datetime.now().year
    # pattern = f"CLAIM-{year}-%"

    # stmt = select(sql_func.max(BPJSClaim.claim_number)).filter(
    #     BPJSClaim.claim_number.like(pattern)
    # )
    # result = await db.execute(stmt)
    # last_number = result.scalar()

    # if last_number:
    #     last_sequence = int(last_number.split('-')[-1])
    #     new_sequence = last_sequence + 1
    # else:
    #     new_sequence = 1

    # return f"CLAIM-{year}-{new_sequence:05d}"
    return f"CLAIM-{datetime.now().year}-00001"


async def generate_eclaim_data(
    db: AsyncSession,
    claim_id: int,
) -> Dict[str, Any]:
    """
    Generate e-claim data structure for BPJS API submission.

    Args:
        db: Database session
        claim_id: Claim ID

    Returns:
        E-claim data dictionary in BPJS API format
    """
    # claim = await get_bpjs_claim(db, claim_id)
    # if not claim:
    #     raise ValueError("Claim not found")

    # Get claim items
    # items = await get_claim_items(db, claim_id)

    # eclaim_data = {
    #     "nomorKlaim": claim.claim_number,
    #     "nomorSEP": claim.sep_number,
    #     "tanggalPulang": claim.discharge_date.isoformat() if claim.discharge_date else None,
    #     "jenisRawat": claim.service_type,
    #     "kelasRawat": claim.treatment_class,
    #     "adlSubAcute": 0,  # Activities of Daily Living
    #     "adlChronic": 0,
    #     "tarifPoliEKsekutif": 0,
    #     "namaDokter": claim.doctor_name,
    #     "kodeDokter": claim.doctor_code,
    #     "kodePPK": claim.facility_code,
    #     "namaPPK": claim.facility_name,
    #     "caraMasuk": claim.admission_type,
    #     "tanggalMasuk": claim.admission_date.isoformat() if claim.admission_date else None,
    #     "diagnosa": [
    #         {
    #             "kode": code,
    #             "nama": await _get_diagnosis_name(db, code)
    #         }
    #         for code in claim.diagnosis_codes
    #     ],
    #     "procedure": [
    #         {
    #             "kode": code,
    #             "nama": await _get_procedure_name(db, code),
    #             "tarif": item.unit_price
    #         }
    #         for item in items if item.item_type == 'procedure'
    #     ],
    #     "tarifRS": {
    #         "prosedurNonBedah": sum(i.unit_price for i in items if i.category == 'non_surgical'),
    #         "prosedurBedah": sum(i.unit_price for i in items if i.category == 'surgical'),
    #         "konsultasi": sum(i.unit_price for i in items if i.category == 'consultation'),
    #         "tenagaAhli": sum(i.unit_price for i in items if i.category == 'specialist'),
    #         "keperawatan": sum(i.unit_price for i in items if i.category == 'nursing'),
    #         "penunjang": sum(i.unit_price for i in items if i.category == 'support'),
    #         "radiologi": sum(i.unit_price for i in items if i.category == 'radiology'),
    #         "laboratorium": sum(i.unit_price for i in items if i.category == 'laboratory'),
    #         "pelayananDarurat": sum(i.unit_price for i in items if i.category == 'emergency'),
    #         "rawatIntensif": sum(i.unit_price for i in items if i.category == 'intensive_care'),
    #         "obat": sum(i.unit_price for i in items if i.category == 'medication'),
    #         "obatKronis": sum(i.unit_price for i in items if i.category == 'chronic_medication'),
    #         "obatKemoterapi": sum(i.unit_price for i in items if i.category == 'chemotherapy'),
    #         "akomodasi": sum(i.unit_price for i in items if i.category == 'accommodation'),
    #         "rawatInapIntensif": sum(i.unit_price for i in items if i.category == 'intensive_care'),
    #     },
    #     "biaya": {
    #         "total": claim.total_amount,
    #         "tarif": claim.cbg_rate,
    #         "topup": claim.topup_amount or 0,
    #     },
    #     "status": claim.status,
    # }

    # return eclaim_data
    return {}


async def validate_claim_data(
    db: AsyncSession,
    claim_id: int,
) -> Tuple[bool, List[str]]:
    """
    Validate claim data before submission.

    Args:
        db: Database session
        claim_id: Claim ID

    Returns:
        Tuple of (is_valid, list of validation errors)
    """
    # claim = await get_bpjs_claim(db, claim_id)
    # if not claim:
    #     return False, ["Claim not found"]

    # errors = []

    # # Check required fields
    # if not claim.sep_number:
    #     errors.append("SEP number is required")

    # if not claim.cbg_code:
    #     errors.append("CBG code is required")

    # if not claim.admission_date:
    #     errors.append("Admission date is required")

    # if not claim.discharge_date:
    #     errors.append("Discharge date is required")

    # if not claim.diagnosis_codes:
    #     errors.append("At least one diagnosis code is required")

    # # Validate date logic
    # if claim.admission_date and claim.discharge_date:
    #     if claim.discharge_date < claim.admission_date:
    #         errors.append("Discharge date cannot be before admission date")

    # # Check required documents
    # missing_docs = await get_missing_documents(db, claim_id)
    # if missing_docs:
    #     errors.append(f"Missing required documents: {', '.join(missing_docs)}")

    # # Validate against BPJS rules
    # if claim.cbg_code:
    #     cbg_valid = await _validate_cbg_code(db, claim.cbg_code, claim.claim_type)
    #     if not cbg_valid:
    #         errors.append(f"Invalid CBG code {claim.cbg_code} for claim type {claim.claim_type}")

    # return len(errors) == 0, errors
    return False, ["Validation not implemented"]


async def calculate_package_rate(
    db: AsyncSession,
    claim_id: int,
) -> Dict[str, Any]:
    """
    Calculate INA-CBG package rate for a claim.

    Args:
        db: Database session
        claim_id: Claim ID

    Returns:
        Dictionary with rate calculation details
    """
    # claim = await get_bpjs_claim(db, claim_id)
    # if not claim:
    #     raise ValueError("Claim not found")

    # # Look up CBG rate
    # cbg_rate = await _get_cbg_rate(db, claim.cbg_code, claim.treatment_class)

    # claim.cbg_rate = cbg_rate

    # # Calculate items total
    # items = await get_claim_items(db, claim_id)
    # items_total = sum(item.quantity * item.unit_price for item in items)

    # claim.total_amount = items_total

    # # Calculate topup or reduction
    # if items_total > cbg_rate:
    #     claim.topup_amount = items_total - cbg_rate
    #     claim.reduction_amount = Decimal('0.00')
    # else:
    #     claim.topup_amount = Decimal('0.00')
    #     claim.reduction_amount = cbg_rate - items_total

    # await db.commit()

    # return {
    #     'cbg_code': claim.cbg_code,
    #     'cbg_rate': cbg_rate,
    #     'items_total': items_total,
    #     'topup_amount': claim.topup_amount,
    #     'reduction_amount': claim.reduction_amount,
    #     'total_claimed': claim.total_amount,
    # }

    return {
        'cbg_code': '',
        'cbg_rate': Decimal('0.00'),
        'items_total': Decimal('0.00'),
        'topup_amount': Decimal('0.00'),
        'reduction_amount': Decimal('0.00'),
        'total_claimed': Decimal('0.00'),
    }


async def group_by_inacbg(
    db: AsyncSession,
    start_date: date,
    end_date: date,
) -> List[Dict[str, Any]]:
    """
    Group claims by INA-CBG code for reporting.

    Args:
        db: Database session
        start_date: Start date
        end_date: End date

    Returns:
        List of CBG groups with counts and totals
    """
    # stmt = select(
    #     BPJSClaim.cbg_code,
    #     sql_func.count(BPJSClaim.id).label('claim_count'),
    #     sql_func.sum(BPJSClaim.total_amount).label('total_amount'),
    #     sql_func.sum(BPJSClaim.cbg_rate).label('total_cbg_rate'),
    # ).where(
    #     and_(
    #         BPJSClaim.submission_date >= start_date,
    #         BPJSClaim.submission_date <= end_date,
    #         BPJSClaim.status.in_(['submitted', 'verified', 'approved', 'paid'])
    #     )
    # ).group_by(BPJSClaim.cbg_code)

    # result = await db.execute(stmt)
    # rows = result.all()

    # return [
    #     {
    #         'cbg_code': row.cbg_code,
    #         'claim_count': row.claim_count,
    #         'total_amount': row.total_amount or Decimal('0'),
    #         'total_cbg_rate': row.total_cbg_rate or Decimal('0'),
    #         'average_amount': (row.total_amount / row.claim_count) if row.claim_count > 0 else Decimal('0'),
    #     }
    #     for row in rows
    # ]

    return []


async def check_claim_deadline(
    db: AsyncSession,
    claim_id: int,
) -> Dict[str, Any]:
    """
    Check if claim is within submission deadline.

    Args:
        db: Database session
        claim_id: Claim ID

    Returns:
        Dictionary with deadline information
    """
    # claim = await get_bpjs_claim(db, claim_id)
    # if not claim:
    #     raise ValueError("Claim not found")

    # BPJS claim submission deadline: 3 months from discharge date
    # deadline = claim.discharge_date + timedelta(days=90)
    # today = date.today()

    # days_remaining = (deadline - today).days
    # is_overdue = days_remaining < 0

    # return {
    #     'claim_id': claim_id,
    #     'discharge_date': claim.discharge_date,
    #     'deadline': deadline,
    #     'days_remaining': days_remaining,
    #     'is_overdue': is_overdue,
    #     'status': 'overdue' if is_overdue else ('urgent' if days_remaining < 7 else 'normal'),
    # }

    return {
        'claim_id': claim_id,
        'discharge_date': None,
        'deadline': None,
        'days_remaining': 0,
        'is_overdue': False,
        'status': 'unknown',
    }


# =============================================================================
# Claim Items
# =============================================================================

async def add_claim_item(
    db: AsyncSession,
    claim_id: int,
    item_data: Dict[str, Any],
    created_by_id: int,
) -> Any:
    """
    Add an item to a claim.

    Args:
        db: Database session
        claim_id: Claim ID
        item_data: Item data
        created_by_id: User ID creating the item

    Returns:
        Created claim item
    """
    # claim = await get_bpjs_claim(db, claim_id)
    # if not claim:
    #     raise ValueError("Claim not found")

    # if claim.status not in ['draft', 'pending']:
    #     raise ValueError("Can only add items to draft or pending claims")

    # db_item = BPJSClaimItem(
    #     claim_id=claim_id,
    #     item_type=item_data.get('item_type', 'service'),
    #     category=item_data.get('category'),
    #     code=item_data.get('code'),
    #     description=item_data['description'],
    #     quantity=item_data.get('quantity', 1),
    #     unit_price=item_data['unit_price'],
    #     service_date=item_data.get('service_date'),
    #     provider_id=item_data.get('provider_id'),
    #     notes=item_data.get('notes'),
    #     created_by_id=created_by_id,
    # )

    # db.add(db_item)
    # await db.commit()
    # await db.refresh(db_item)

    # # Recalculate claim totals
    # await calculate_package_rate(db, claim_id)

    # return db_item
    return None


async def update_claim_item(
    db: AsyncSession,
    item_id: int,
    item_update: Dict[str, Any],
    updated_by_id: int,
) -> Optional[Any]:
    """
    Update a claim item.

    Args:
        db: Database session
        item_id: Item ID
        item_update: Update data
        updated_by_id: User ID updating the item

    Returns:
        Updated item or None
    """
    # stmt = select(BPJSClaimItem).where(BPJSClaimItem.id == item_id)
    # result = await db.execute(stmt)
    # item = result.scalar_one_or_none()

    # if not item:
    #     return None

    # # Check if claim is still editable
    # claim = await get_bpjs_claim(db, item.claim_id)
    # if claim.status not in ['draft', 'pending']:
    #     raise ValueError("Can only update items in draft or pending claims")

    # for field, value in item_update.items():
    #     if hasattr(item, field) and value is not None:
    #         setattr(item, field, value)

    # item.updated_by_id = updated_by_id
    # await db.commit()
    # await db.refresh(item)

    # # Recalculate claim totals
    # await calculate_package_rate(db, item.claim_id)

    # return item
    return None


async def remove_claim_item(
    db: AsyncSession,
    item_id: int,
    deleted_by_id: int,
) -> bool:
    """
    Remove a claim item (soft delete).

    Args:
        db: Database session
        item_id: Item ID
        deleted_by_id: User ID deleting the item

    Returns:
        True if removed
    """
    # stmt = select(BPJSClaimItem).where(BPJSClaimItem.id == item_id)
    # result = await db.execute(stmt)
    # item = result.scalar_one_or_none()

    # if not item:
    #     return False

    # claim_id = item.claim_id

    # # Check if claim is still editable
    # claim = await get_bpjs_claim(db, claim_id)
    # if claim.status not in ['draft', 'pending']:
    #     raise ValueError("Can only remove items from draft or pending claims")

    # item.is_deleted = True
    # item.deleted_at = datetime.utcnow()
    # item.deleted_by_id = deleted_by_id

    # await db.commit()

    # # Recalculate claim totals
    # await calculate_package_rate(db, claim_id)

    # return True
    return False


async def get_claim_items(
    db: AsyncSession,
    claim_id: int,
    include_deleted: bool = False,
) -> List[Any]:
    """
    Get all items for a claim.

    Args:
        db: Database session
        claim_id: Claim ID
        include_deleted: Include deleted items

    Returns:
        List of claim items
    """
    # stmt = select(BPJSClaimItem).where(
    #     BPJSClaimItem.claim_id == claim_id
    # )

    # if not include_deleted:
    #     stmt = stmt.where(BPJSClaimItem.is_deleted == False)

    # stmt = stmt.order_by(BPJSClaimItem.created_at)

    # result = await db.execute(stmt)
    # return list(result.scalars().all())
    return []


# =============================================================================
# Documents
# =============================================================================

async def add_claim_document(
    db: AsyncSession,
    claim_id: int,
    document_data: Dict[str, Any],
    created_by_id: int,
) -> Any:
    """
    Add a document to a claim.

    Args:
        db: Database session
        claim_id: Claim ID
        document_data: Document data
        created_by_id: User ID creating the document

    Returns:
        Created claim document
    """
    # claim = await get_bpjs_claim(db, claim_id)
    # if not claim:
    #     raise ValueError("Claim not found")

    # db_document = BPJSClaimDocument(
    #     claim_id=claim_id,
    #     document_type=document_data['document_type'],
    #     file_name=document_data['file_name'],
    #     file_path=document_data['file_path'],
    #     file_size=document_data.get('file_size'),
    #     mime_type=document_data.get('mime_type'),
    #     is_required=document_data.get('is_required', False),
    #     notes=document_data.get('notes'),
    #     created_by_id=created_by_id,
    # )

    # db.add(db_document)
    # await db.commit()
    # await db.refresh(db_document)

    # return db_document
    return None


async def get_claim_documents(
    db: AsyncSession,
    claim_id: int,
    document_type: Optional[str] = None,
) -> List[Any]:
    """
    Get all documents for a claim.

    Args:
        db: Database session
        claim_id: Claim ID
        document_type: Optional filter by document type

    Returns:
        List of claim documents
    """
    # stmt = select(BPJSClaimDocument).where(
    #     BPJSClaimDocument.claim_id == claim_id
    # )

    # if document_type:
    #     stmt = stmt.where(BPJSClaimDocument.document_type == document_type)

    # stmt = stmt.order_by(BPJSClaimDocument.created_at)

    # result = await db.execute(stmt)
    # return list(result.scalars().all())
    return []


async def delete_claim_document(
    db: AsyncSession,
    document_id: int,
    deleted_by_id: int,
) -> bool:
    """
    Delete a claim document (soft delete).

    Args:
        db: Database session
        document_id: Document ID
        deleted_by_id: User ID deleting the document

    Returns:
        True if deleted
    """
    # stmt = select(BPJSClaimDocument).where(BPJSClaimDocument.id == document_id)
    # result = await db.execute(stmt)
    # document = result.scalar_one_or_none()

    # if not document:
    #     return False

    # document.is_deleted = True
    # document.deleted_at = datetime.utcnow()
    # document.deleted_by_id = deleted_by_id

    # await db.commit()
    # return True
    return False


async def upload_document(
    db: AsyncSession,
    claim_id: int,
    document_type: str,
    file_data: bytes,
    file_name: str,
    mime_type: str,
    uploaded_by_id: int,
) -> Any:
    """
    Upload and attach a document to a claim.

    Args:
        db: Database session
        claim_id: Claim ID
        document_type: Type of document
        file_data: File content
        file_name: Original file name
        mime_type: MIME type
        uploaded_by_id: User ID uploading

    Returns:
        Created claim document
    """
    # # Save file to storage
    # file_path = await _save_file_to_storage(claim_id, document_type, file_data, file_name)

    # document_data = {
    #     'document_type': document_type,
    #     'file_name': file_name,
    #     'file_path': file_path,
    #     'file_size': len(file_data),
    #     'mime_type': mime_type,
    # }

    # return await add_claim_document(db, claim_id, document_data, uploaded_by_id)
    return None


async def verify_document(
    db: AsyncSession,
    document_id: int,
    is_valid: bool,
    verified_by_id: int,
    notes: Optional[str] = None,
) -> Optional[Any]:
    """
    Mark a document as verified.

    Args:
        db: Database session
        document_id: Document ID
        is_valid: Whether document is valid
        verified_by_id: User ID verifying
        notes: Optional verification notes

    Returns:
        Updated document or None
    """
    # stmt = select(BPJSClaimDocument).where(BPJSClaimDocument.id == document_id)
    # result = await db.execute(stmt)
    # document = result.scalar_one_or_none()

    # if not document:
    #     return None

    # document.is_verified = True
    # document.is_valid = is_valid
    # document.verified_at = datetime.utcnow()
    # document.verified_by_id = verified_by_id
    # document.verification_notes = notes

    # await db.commit()
    # await db.refresh(document)

    # return document
    return None


async def get_required_documents(
    db: AsyncSession,
    claim_type: str,
    service_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get list of required documents for a claim type.

    Args:
        db: Database session
        claim_type: Type of claim (inpatient, outpatient)
        service_type: Optional service type

    Returns:
        List of required document types
    """
    # Define BPJS required documents by claim type
    required_docs = {
        'inpatient': [
            {'document_type': 'sep', 'name': 'Surat Eligibilitas Peserta', 'is_required': True},
            {'document_type': 'discharge_summary', 'name': 'Resume Medis', 'is_required': True},
            {'document_type': 'billing_statement', 'name': 'Tagihan', 'is_required': True},
            {'document_type': 'identification', 'name': 'Identitas Pasien', 'is_required': True},
        ],
        'outpatient': [
            {'document_type': 'sep', 'name': 'Surat Eligibilitas Peserta', 'is_required': True},
            {'document_type': 'medical_report', 'name': 'Laporan Medis', 'is_required': True},
            {'document_type': 'billing_statement', 'name': 'Tagihan', 'is_required': True},
        ],
    }

    return required_docs.get(claim_type, [])


async def get_missing_documents(
    db: AsyncSession,
    claim_id: int,
) -> List[str]:
    """
    Get list of missing required documents for a claim.

    Args:
        db: Database session
        claim_id: Claim ID

    Returns:
        List of missing document types
    """
    # claim = await get_bpjs_claim(db, claim_id)
    # if not claim:
    #     return []

    # required_docs = await get_required_documents(db, claim.claim_type, claim.service_type)
    # existing_docs = await get_claim_documents(db, claim_id)

    # existing_types = {doc.document_type for doc in existing_docs if not doc.is_deleted}
    # missing = []

    # for req in required_docs:
    #     if req['is_required'] and req['document_type'] not in existing_types:
    #         missing.append(req['name'])

    # return missing
    return []


# =============================================================================
# Submission
# =============================================================================

async def submit_claim_to_bpjs(
    db: AsyncSession,
    claim_id: int,
    submitted_by_id: int,
) -> Dict[str, Any]:
    """
    Submit claim to BPJS API.

    Args:
        db: Database session
        claim_id: Claim ID
        submitted_by_id: User ID submitting

    Returns:
        Submission result dictionary
    """
    # claim = await get_bpjs_claim(db, claim_id)
    # if not claim:
    #     raise ValueError("Claim not found")

    # # Validate claim before submission
    # is_valid, errors = await validate_claim_data(db, claim_id)
    # if not is_valid:
    #     raise ValueError(f"Claim validation failed: {', '.join(errors)}")

    # # Generate e-claim data
    # eclaim_data = await generate_eclaim_data(db, claim_id)

    # # Call BPJS API (placeholder)
    # api_response = await _call_bpjs_api_submit(eclaim_data)

    # # Create submission record
    # submission_data = {
    #     'submission_date': datetime.utcnow().date(),
    #     'eclaim_data': eclaim_data,
    #     'response_data': api_response,
    #     'status': 'submitted' if api_response.get('success') else 'failed',
    #     'response_code': api_response.get('code'),
    #     'response_message': api_response.get('message'),
    # }

    # submission = await log_submission(db, claim_id, submission_data, submitted_by_id)

    # # Update claim status
    # if api_response.get('success'):
    #     claim.status = 'submitted'
    #     claim.submission_date = datetime.utcnow().date()
    #     await db.commit()

    # return {
    #     'success': api_response.get('success', False),
    #     'claim_id': claim_id,
    #     'submission_id': submission.id if submission else None,
    #     'response': api_response,
    # }

    return {
        'success': False,
        'claim_id': claim_id,
        'submission_id': None,
        'response': {'message': 'Not implemented'},
    }


async def check_submission_status(
    db: AsyncSession,
    claim_id: int,
) -> Dict[str, Any]:
    """
    Check submission status from BPJS API.

    Args:
        db: Database session
        claim_id: Claim ID

    Returns:
        Status information
    """
    # claim = await get_bpjs_claim(db, claim_id)
    # if not claim:
    #     raise ValueError("Claim not found")

    # # Get latest submission
    # submission = await get_last_submission_log(db, claim_id)
    # if not submission:
    #     return {'status': 'not_submitted'}

    # # Call BPJS API to check status
    # api_response = await _call_bpjs_api_status(claim.claim_number)

    # # Update submission record
    # submission.response_data = api_response
    # await db.commit()

    # return {
    #     'claim_id': claim_id,
    #     'claim_number': claim.claim_number,
    #     'submission_date': submission.submission_date,
    #     'status': api_response.get('status', 'unknown'),
    #     'response': api_response,
    # }

    return {
        'claim_id': claim_id,
        'status': 'unknown',
    }


async def handle_submission_error(
    db: AsyncSession,
    claim_id: int,
    error_message: str,
    error_code: Optional[str] = None,
) -> Optional[Any]:
    """
    Handle submission error and update claim status.

    Args:
        db: Database session
        claim_id: Claim ID
        error_message: Error message
        error_code: Optional error code

    Returns:
        Updated claim or None
    """
    # claim = await get_bpjs_claim(db, claim_id)
    # if not claim:
    #     return None

    # claim.status = 'error'
    # claim.error_message = error_message
    # claim.error_code = error_code
    # claim.last_error_at = datetime.utcnow()

    # await db.commit()
    # await db.refresh(claim)

    # return claim
    return None


async def retry_submission(
    db: AsyncSession,
    claim_id: int,
    retried_by_id: int,
) -> Dict[str, Any]:
    """
    Retry failed claim submission.

    Args:
        db: Database session
        claim_id: Claim ID
        retried_by_id: User ID retrying

    Returns:
        Submission result
    """
    # claim = await get_bpjs_claim(db, claim_id)
    # if not claim:
    #     raise ValueError("Claim not found")

    # if claim.status != 'error':
    #     raise ValueError("Can only retry claims with error status")

    # # Reset claim status
    # claim.status = 'pending'
    # claim.retry_count = (claim.retry_count or 0) + 1
    # claim.last_retried_at = datetime.utcnow()
    # claim.last_retried_by_id = retried_by_id

    # await db.commit()

    # # Submit again
    # return await submit_claim_to_bpjs(db, claim_id, retried_by_id)

    return {
        'success': False,
        'claim_id': claim_id,
        'message': 'Not implemented',
    }


async def log_submission(
    db: AsyncSession,
    claim_id: int,
    submission_data: Dict[str, Any],
    created_by_id: int,
) -> Any:
    """
    Log claim submission attempt.

    Args:
        db: Database session
        claim_id: Claim ID
        submission_data: Submission details
        created_by_id: User ID creating the log

    Returns:
        Created submission record
    """
    # db_submission = BPJSClaimSubmission(
    #     claim_id=claim_id,
    #     submission_date=submission_data.get('submission_date', date.today()),
    #     eclaim_data=submission_data.get('eclaim_data', {}),
    #     response_data=submission_data.get('response_data', {}),
    #     status=submission_data.get('status', 'pending'),
    #     response_code=submission_data.get('response_code'),
    #     response_message=submission_data.get('response_message'),
    #     created_by_id=created_by_id,
    # )

    # db.add(db_submission)
    # await db.commit()
    # await db.refresh(db_submission)

    # return db_submission
    return None


async def get_submission_logs(
    db: AsyncSession,
    claim_id: int,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get submission logs for a claim.

    Args:
        db: Database session
        claim_id: Claim ID
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (submission logs, total count)
    """
    # stmt = select(BPJSClaimSubmission).where(
    #     BPJSClaimSubmission.claim_id == claim_id
    # )

    # count_stmt = select(sql_func.count(BPJSClaimSubmission.id)).where(
    #     BPJSClaimSubmission.claim_id == claim_id
    # )

    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()

    # stmt = stmt.order_by(desc(BPJSClaimSubmission.created_at))
    # stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    # result = await db.execute(stmt)
    # logs = result.scalars().all()

    # return list(logs), total
    return [], 0


async def get_last_submission_log(
    db: AsyncSession,
    claim_id: int,
) -> Optional[Any]:
    """
    Get the most recent submission log for a claim.

    Args:
        db: Database session
        claim_id: Claim ID

    Returns:
        Latest submission log or None
    """
    # stmt = select(BPJSClaimSubmission).where(
    #     BPJSClaimSubmission.claim_id == claim_id
    # ).order_by(desc(BPJSClaimSubmission.created_at)).limit(1)

    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()
    return None


# =============================================================================
# Verification
# =============================================================================

async def create_verification_query(
    db: AsyncSession,
    claim_id: int,
    query_data: Dict[str, Any],
    created_by_id: int,
) -> Any:
    """
    Create a verification query for a claim.

    Args:
        db: Database session
        claim_id: Claim ID
        query_data: Query details
        created_by_id: User ID creating the query

    Returns:
        Created verification query
    """
    # db_query = BPJSVerificationQuery(
    #     claim_id=claim_id,
    #     query_type=query_data.get('query_type', 'clarification'),
    #     query_text=query_data['query_text'],
    #     response_deadline=query_data.get('response_deadline'),
    #     status='open',
    #     bpjs_reference=query_data.get('bpjs_reference'),
    #     created_by_id=created_by_id,
    # )

    # db.add(db_query)
    # await db.commit()
    # await db.refresh(db_query)

    # # Update claim status
    # claim = await get_bpjs_claim(db, claim_id)
    # if claim:
    #     claim.status = 'verification_required'
    #     await db.commit()

    # return db_query
    return None


async def respond_to_verification(
    db: AsyncSession,
    query_id: int,
    response_text: str,
    respondent_id: int,
    document_ids: Optional[List[int]] = None,
) -> Optional[Any]:
    """
    Respond to a verification query.

    Args:
        db: Database session
        query_id: Query ID
        response_text: Response text
        respondent_id: User ID responding
        document_ids: Optional list of supporting document IDs

    Returns:
        Updated query or None
    """
    # stmt = select(BPJSVerificationQuery).where(BPJSVerificationQuery.id == query_id)
    # result = await db.execute(stmt)
    # query = result.scalar_one_or_none()

    # if not query:
    #     return None

    # if query.status != 'open':
    #     raise ValueError("Can only respond to open queries")

    # query.response_text = response_text
    # query.responded_at = datetime.utcnow()
    # query.respondent_id = respondent_id
    # query.status = 'responded'

    # if document_ids:
    #     query.supporting_documents = document_ids

    # await db.commit()
    # await db.refresh(query)

    # # Update claim status if all queries are resolved
    # claim = await get_bpjs_claim(db, query.claim_id)
    # if claim:
    #     open_queries = await get_verification_queries(db, claim.id, status='open')
    #     if not open_queries:
    #         claim.status = 'pending_verification'

    # await db.commit()

    # return query
    return None


async def get_verification_queries(
    db: AsyncSession,
    claim_id: int,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> List[Any]:
    """
    Get verification queries for a claim.

    Args:
        db: Database session
        claim_id: Claim ID
        status: Optional filter by status
        page: Page number
        page_size: Items per page

    Returns:
        List of verification queries
    """
    # stmt = select(BPJSVerificationQuery).where(
    #     BPJSVerificationQuery.claim_id == claim_id
    # )

    # if status:
    #     stmt = stmt.where(BPJSVerificationQuery.status == status)

    # stmt = stmt.order_by(desc(BPJSVerificationQuery.created_at))
    # stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    # result = await db.execute(stmt)
    # return list(result.scalars().all())
    return []


async def update_query_status(
    db: AsyncSession,
    query_id: int,
    new_status: str,
    updated_by_id: int,
    notes: Optional[str] = None,
) -> Optional[Any]:
    """
    Update verification query status.

    Args:
        db: Database session
        query_id: Query ID
        new_status: New status
        updated_by_id: User ID updating
        notes: Optional notes

    Returns:
        Updated query or None
    """
    # stmt = select(BPJSVerificationQuery).where(BPJSVerificationQuery.id == query_id)
    # result = await db.execute(stmt)
    # query = result.scalar_one_or_none()

    # if not query:
    #     return None

    # query.status = new_status
    # query.updated_at = datetime.utcnow()
    # query.updated_by_id = updated_by_id

    # if notes:
    #     if not query.internal_notes:
    #         query.internal_notes = []
    #     query.internal_notes.append({
    #         'timestamp': datetime.utcnow().isoformat(),
    #         'user_id': updated_by_id,
    #         'note': notes,
    #     })

    # await db.commit()
    # await db.refresh(query)

    # return query
    return None


# =============================================================================
# Reporting
# =============================================================================

async def get_claim_statistics(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    facility_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get comprehensive claim statistics for a date range.

    Args:
        db: Database session
        start_date: Start date
        end_date: End date
        facility_id: Optional facility filter

    Returns:
        Statistics dictionary
    """
    # stmt = select(BPJSClaim).where(
    #     and_(
    #         BPJSClaim.created_at >= start_date,
    #         BPJSClaim.created_at <= end_date,
    #     )
    # )

    # if facility_id:
    #     stmt = stmt.where(BPJSClaim.facility_id == facility_id)

    # result = await db.execute(stmt)
    # claims = result.scalars().all()

    # Calculate statistics
    # total_claims = len(claims)
    # submitted = len([c for c in claims if c.status == 'submitted'])
    # verified = len([c for c in claims if c.status == 'verified'])
    # approved = len([c for c in claims if c.status == 'approved'])
    # paid = len([c for c in claims if c.status == 'paid'])
    # rejected = len([c for c in claims if c.status == 'rejected'])

    # total_amount = sum(c.total_amount or Decimal('0') for c in claims)
    # approved_amount = sum(c.total_amount or Decimal('0') for c in claims if c.status == 'paid')
    # pending_amount = sum(c.total_amount or Decimal('0') for c in claims if c.status in ['submitted', 'verified'])

    return {
        'period': {'start': start_date, 'end': end_date},
        'total_claims': 0,
        'by_status': {
            'draft': 0,
            'pending': 0,
            'submitted': 0,
            'verified': 0,
            'approved': 0,
            'paid': 0,
            'rejected': 0,
        },
        'amounts': {
            'total_claimed': Decimal('0.00'),
            'total_approved': Decimal('0.00'),
            'total_paid': Decimal('0.00'),
            'pending_payment': Decimal('0.00'),
        },
        'approval_rate': Decimal('0.00'),
        'rejection_rate': Decimal('0.00'),
    }


async def get_claim_summary_by_status(
    db: AsyncSession,
    start_date: date,
    end_date: date,
) -> List[Dict[str, Any]]:
    """
    Get claim summary grouped by status.

    Args:
        db: Database session
        start_date: Start date
        end_date: End date

    Returns:
        List of status summaries
    """
    # stmt = select(
    #     BPJSClaim.status,
    #     sql_func.count(BPJSClaim.id).label('claim_count'),
    #     sql_func.sum(BPJSClaim.total_amount).label('total_amount'),
    #     sql_func.sum(BPJSClaim.cbg_rate).label('total_cbg_rate'),
    # ).where(
    #     and_(
    #         BPJSClaim.created_at >= start_date,
    #         BPJSClaim.created_at <= end_date,
    #     )
    # ).group_by(BPJSClaim.status)

    # result = await db.execute(stmt)
    # rows = result.all()

    # return [
    #     {
    #         'status': row.status,
    #         'claim_count': row.claim_count,
    #         'total_amount': row.total_amount or Decimal('0'),
    #         'total_cbg_rate': row.total_cbg_rate or Decimal('0'),
    #     }
    #     for row in rows
    # ]

    return []


async def get_claim_summary_by_package(
    db: AsyncSession,
    start_date: date,
    end_date: date,
) -> List[Dict[str, Any]]:
    """
    Get claim summary grouped by INA-CBG package.

    Args:
        db: Database session
        start_date: Start date
        end_date: End date

    Returns:
        List of package summaries
    """
    # stmt = select(
    #     BPJSClaim.cbg_code,
    #     sql_func.count(BPJSClaim.id).label('claim_count'),
    #     sql_func.sum(BPJSClaim.total_amount).label('total_amount'),
    #     sql_func.avg(BPJSClaim.total_amount).label('avg_amount'),
    # ).where(
    #     and_(
    #         BPJSClaim.submission_date >= start_date,
    #         BPJSClaim.submission_date <= end_date,
    #         BPJSClaim.cbg_code.isnot(None)
    #     )
    # ).group_by(BPJSClaim.cbg_code)

    # result = await db.execute(stmt)
    # rows = result.all()

    # return [
    #     {
    #         'cbg_code': row.cbg_code,
    #         'claim_count': row.claim_count,
    #         'total_amount': row.total_amount or Decimal('0'),
    #         'average_amount': row.avg_amount or Decimal('0'),
    #     }
    #     for row in rows
    # ]

    return []


async def get_upcoming_deadlines(
    db: AsyncSession,
    days_ahead: int = 7,
    status_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get claims with upcoming submission deadlines.

    Args:
        db: Database session
        days_ahead: Number of days to look ahead
        status_filter: Optional status filter

    Returns:
        List of claims with deadline information
    """
    # deadline_date = date.today() + timedelta(days=days_ahead)

    # stmt = select(BPJSClaim).where(
    #     and_(
    #         BPJSClaim.discharge_date.isnot(None),
    #         BPJSClaim.discharge_date + timedelta(days=90) <= deadline_date,
    #         BPJSClaim.status.in_(['draft', 'pending'])
    #     )
    # )

    # if status_filter:
    #     stmt = stmt.where(BPJSClaim.status == status_filter)

    # stmt = stmt.options(selectinload(BPJSClaim.patient))
    # stmt = stmt.order_by(BPJSClaim.discharge_date.desc())

    # result = await db.execute(stmt)
    # claims = result.scalars().all()

    # deadline_info = []
    # for claim in claims:
    #     deadline = claim.discharge_date + timedelta(days=90)
    #     days_remaining = (deadline - date.today()).days

    #     deadline_info.append({
    #         'claim_id': claim.id,
    #         'claim_number': claim.claim_number,
    #         'patient_id': claim.patient_id,
    #         'patient_name': claim.patient.full_name if claim.patient else None,
    #         'discharge_date': claim.discharge_date,
    #         'deadline': deadline,
    #         'days_remaining': days_remaining,
    #         'status': claim.status,
    #         'is_urgent': days_remaining <= 3,
    #     })

    # return deadline_info
    return []


# =============================================================================
# Helper Functions
# =============================================================================

async def _get_diagnosis_name(
    db: AsyncSession,
    diagnosis_code: str,
) -> str:
    """Get diagnosis name from ICD-10 code."""
    # Implementation would query ICD-10 table
    return diagnosis_code


async def _get_procedure_name(
    db: AsyncSession,
    procedure_code: str,
) -> str:
    """Get procedure name from procedure code."""
    # Implementation would query procedure codes table
    return procedure_code


async def _validate_cbg_code(
    db: AsyncSession,
    cbg_code: str,
    claim_type: str,
) -> bool:
    """Validate CBG code against BPJS reference."""
    # Implementation would validate against CBG reference table
    return True


async def _get_cbg_rate(
    db: AsyncSession,
    cbg_code: str,
    treatment_class: Optional[str] = None,
) -> Decimal:
    """Look up CBG rate for a code and treatment class."""
    # Implementation would query CBG rate table
    return Decimal('0.00')


async def _save_file_to_storage(
    claim_id: int,
    document_type: str,
    file_data: bytes,
    file_name: str,
) -> str:
    """Save file to storage and return path."""
    # Implementation would save to filesystem or cloud storage
    return f"/claims/{claim_id}/{document_type}/{file_name}"


async def _call_bpjs_api_submit(
    eclaim_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Call BPJS API to submit claim."""
    # Implementation would make HTTP request to BPJS API
    return {
        'success': False,
        'code': 'NOT_IMPLEMENTED',
        'message': 'BPJS API integration not yet implemented',
    }


async def _call_bpjs_api_status(
    claim_number: str,
) -> Dict[str, Any]:
    """Call BPJS API to check claim status."""
    # Implementation would make HTTP request to BPJS API
    return {
        'status': 'unknown',
        'message': 'BPJS API integration not yet implemented',
    }


async def log_claim_status_change(
    db: AsyncSession,
    claim_id: int,
    previous_status: str,
    new_status: str,
    changed_by_id: int,
) -> Any:
    """Log claim status change for audit trail."""
    # Implementation would create audit log entry
    pass
