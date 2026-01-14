"""BPJS SEP CRUD operations for STORY-019: BPJS SEP Generation

This module provides CRUD operations for BPJS SEP (Surat Eligibilitas Peserta)
management, including creation, updating, cancellation, and history tracking.
"""
from datetime import datetime, date, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bpjs_sep import BPJSSEP, BPJSSEPHistory, SEPStatus
from app.models.encounter import Encounter
from app.models.patient import Patient
from app.models.user import User
from app.schemas.sep import (
    SEPCreate,
    SEPUpdate,
    SEPCancel,
    SEPInfo,
    SEPSummary,
    SEPHistoryEntry,
    SEPValidationRequest,
    SEPValidationResponse,
    SEPListQuery,
    SEPListResponse,
    SEPStatistics,
    SEPAutoPopulateData,
)


async def get_sep_by_id(
    db: AsyncSession,
    sep_id: int,
) -> Optional[BPJSSEP]:
    """Get SEP by ID."""
    stmt = select(BPJSSEP).where(
        and_(
            BPJSSEP.id == sep_id,
            BPJSSEP.is_deleted == False,
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_sep_by_number(
    db: AsyncSession,
    sep_number: str,
) -> Optional[BPJSSEP]:
    """Get SEP by SEP number."""
    stmt = select(BPJSSEP).where(
        and_(
            BPJSSEP.sep_number == sep_number,
            BPJSSEP.is_deleted == False,
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_sep_by_encounter(
    db: AsyncSession,
    encounter_id: int,
) -> Optional[BPJSSEP]:
    """Get SEP by encounter ID."""
    stmt = select(BPJSSEP).where(
        and_(
            BPJSSEP.encounter_id == encounter_id,
            BPJSSEP.is_deleted == False,
        )
    ).order_by(desc(BPJSSEP.created_at))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_seps(
    db: AsyncSession,
    query: SEPListQuery,
) -> tuple[List[BPJSSEP], int]:
    """
    List SEPs with filtering and pagination.

    Returns:
        Tuple of (list of SEPs, total count)
    """
    # Build base query with filters
    conditions = [BPJSSEP.is_deleted == False]

    if query.patient_id:
        conditions.append(BPJSSEP.patient_id == query.patient_id)
    if query.encounter_id:
        conditions.append(BPJSSEP.encounter_id == query.encounter_id)
    if query.status:
        conditions.append(BPJSSEP.status == query.status)
    if query.service_type:
        conditions.append(BPJSSEP.service_type == query.service_type)
    if query.sep_number:
        conditions.append(BPJSSEP.sep_number.ilike(f"%{query.sep_number}%"))
    if query.date_from:
        conditions.append(BPJSSEP.sep_date >= query.date_from)
    if query.date_to:
        conditions.append(BPJSSEP.sep_date <= query.date_to)

    # Count query
    count_stmt = select(func.count(BPJSSEP.id)).where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()

    # Data query with pagination
    offset = (query.page - 1) * query.page_size
    data_stmt = (
        select(BPJSSEP)
        .where(and_(*conditions))
        .order_by(desc(BPJSSEP.created_at))
        .offset(offset)
        .limit(query.page_size)
    )
    data_result = await db.execute(data_stmt)
    seps = list(data_result.scalars().all())

    return seps, total


async def validate_sep_data(
    db: AsyncSession,
    validation_data: SEPValidationRequest,
) -> SEPValidationResponse:
    """
    Validate SEP data before creation.

    Checks:
    - Patient eligibility (optional, requires BPJS API)
    - Required fields
    - Valid codes
    """
    errors = []
    warnings = []

    # Basic validation
    if not validation_data.bpjs_card_number.isdigit():
        errors.append("BPJS card number must be numeric")

    if validation_data.service_type not in ['RI', 'RJ']:
        errors.append("Service type must be RI or RJ")

    if validation_data.service_type == 'RJ' and not validation_data.polyclinic_code:
        errors.append("Polyclinic code is required for outpatient (RJ) service")

    if len(validation_data.initial_diagnosis_code) < 3:
        errors.append("Initial diagnosis code must be at least 3 characters")

    # Check if patient exists (by BPJS card number)
    patient_stmt = select(Patient).where(
        Patient.insurance_number == validation_data.bpjs_card_number
    )
    patient_result = await db.execute(patient_stmt)
    patient = patient_result.scalar_one_or_none()

    if not patient:
        warnings.append("Patient not found in system with this BPJS card number")

    is_valid = len(errors) == 0

    return SEPValidationResponse(
        is_valid=is_valid,
        message="Validation passed" if is_valid else "Validation failed",
        errors=errors,
        warnings=warnings,
    )


async def get_auto_populate_data(
    db: AsyncSession,
    encounter_id: int,
) -> Optional[SEPAutoPopulateData]:
    """
    Gather data for auto-populating SEP from encounter.

    Collects patient information, encounter details, doctor information,
    and diagnosis codes to pre-fill SEP creation form.
    """
    # Get encounter with relationships
    encounter_stmt = (
        select(Encounter)
        .options(
            selectinload(Encounter.patient),
            selectinload(Encounter.doctor),
            selectinload(Encounter.diagnoses),
        )
        .where(Encounter.id == encounter_id)
    )
    encounter_result = await db.execute(encounter_stmt)
    encounter = encounter_result.scalar_one_or_none()

    if not encounter:
        return None

    patient = encounter.patient
    if not patient:
        return None

    # Determine service type from encounter type
    service_type_map = {
        'outpatient': 'RJ',
        'inpatient': 'RI',
        'emergency': 'RI',
    }
    service_type = service_type_map.get(encounter.encounter_type, 'RJ')

    # Get primary diagnosis
    primary_diagnosis = None
    diagnosis_code = None
    diagnosis_name = None

    for diagnosis in encounter.diagnoses:
        if diagnosis.diagnosis_type == 'primary':
            primary_diagnosis = diagnosis
            diagnosis_code = diagnosis.icd_10_code
            diagnosis_name = diagnosis.diagnosis_name
            break

    # Get doctor information
    doctor_code = None
    doctor_name = None

    if encounter.doctor:
        # Use doctor_id as code for now (should be mapped to BPJS doctor code)
        doctor_code = str(encounter.doctor_id)
        doctor_name = encounter.doctor.full_name if hasattr(encounter.doctor, 'full_name') else None

    return SEPAutoPopulateData(
        encounter_id=encounter.id,
        patient_id=patient.id,
        patient_name=patient.full_name,
        bpjs_card_number=patient.insurance_number or "",
        sep_date=encounter.encounter_date or date.today(),
        service_type=service_type,
        ppk_code="",  # Should come from hospital settings
        department=encounter.department or "",
        doctor_code=doctor_code,
        doctor_name=doctor_name,
        chief_complaint=encounter.chief_complaint,
        initial_diagnosis_code=diagnosis_code,
        initial_diagnosis_name=diagnosis_name,
        mrn=patient.medical_record_number,
        patient_phone=patient.phone,
    )


async def create_sep(
    db: AsyncSession,
    sep_data: SEPCreate,
    bpjs_response: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
) -> BPJSSEP:
    """
    Create a new SEP record.

    Args:
        db: Database session
        sep_data: SEP creation data
        bpjs_response: BPJS API response data (if submitted to BPJS)
        user_id: ID of user creating the SEP

    Returns:
        Created BPJSSEP object
    """
    # Determine initial status
    status = SEPStatus.SUBMITTED if bpjs_response else SEPStatus.DRAFT

    # Extract SEP number from BPJS response if available
    sep_number = None
    if bpjs_response and 'response' in bpjs_response:
        sep_number = bpjs_response['response'].get('sep', {}).get('noSEP')

    sep = BPJSSEP(
        encounter_id=sep_data.encounter_id,
        patient_id=sep_data.patient_id,
        sep_number=sep_number,
        sep_date=sep_data.sep_date,
        service_type=sep_data.service_type,
        bpjs_card_number=sep_data.bpjs_card_number,
        patient_name="",  # Will be fetched from patient
        mrn=sep_data.mrn,
        ppk_code=sep_data.ppk_code,
        polyclinic_code=sep_data.polyclinic_code,
        treatment_class=sep_data.treatment_class,
        initial_diagnosis_code=sep_data.initial_diagnosis_code,
        initial_diagnosis_name=sep_data.initial_diagnosis_name,
        doctor_code=sep_data.doctor_code,
        doctor_name=sep_data.doctor_name,
        referral_number=sep_data.referral_number,
        referral_ppk_code=sep_data.referral_ppk_code,
        is_executive=sep_data.is_executive,
        cob_flag=sep_data.cob_flag,
        notes=sep_data.notes,
        patient_phone=sep_data.patient_phone,
        status=status,
        bpjs_response=bpjs_response,
        created_by=user_id,
    )

    db.add(sep)
    await db.commit()
    await db.refresh(sep)

    # Create history entry
    await create_sep_history(
        db=db,
        sep_id=sep.id,
        action="created",
        new_status=status,
        new_data=sep_to_dict(sep),
        bpjs_request=None,
        bpjs_response=bpjs_response,
        reason="SEP created",
        user_id=user_id,
    )

    return sep


async def update_sep(
    db: AsyncSession,
    sep_update: SEPUpdate,
    bpjs_response: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
) -> Optional[BPJSSEP]:
    """
    Update an existing SEP.

    Args:
        db: Database session
        sep_update: SEP update data
        bpjs_response: BPJS API response data (if submitted to BPJS)
        user_id: ID of user updating the SEP

    Returns:
        Updated BPJSSEP object or None if not found
    """
    # Get existing SEP
    sep = await get_sep_by_id(db, sep_update.sep_id)
    if not sep:
        return None

    # Store previous data for history
    previous_data = sep_to_dict(sep)
    previous_status = sep.status

    # Update fields
    if sep_update.polyclinic_code is not None:
        sep.polyclinic_code = sep_update.polyclinic_code
    if sep_update.treatment_class is not None:
        sep.treatment_class = sep_update.treatment_class
    if sep_update.doctor_code is not None:
        sep.doctor_code = sep_update.doctor_code
    if sep_update.doctor_name is not None:
        sep.doctor_name = sep_update.doctor_name
    if sep_update.initial_diagnosis_code is not None:
        sep.initial_diagnosis_code = sep_update.initial_diagnosis_code
    if sep_update.initial_diagnosis_name is not None:
        sep.initial_diagnosis_name = sep_update.initial_diagnosis_name
    if sep_update.notes is not None:
        sep.notes = sep_update.notes
    if sep_update.patient_phone is not None:
        sep.patient_phone = sep_update.patient_phone

    # Update BPJS response if provided
    if bpjs_response:
        sep.bpjs_response = bpjs_response
        # Update SEP number if changed
        if 'response' in bpjs_response:
            new_sep_number = bpjs_response['response'].get('sep', {}).get('noSEP')
            if new_sep_number:
                sep.sep_number = new_sep_number

        # Update status
        sep.status = SEPStatus.UPDATED

    sep.updated_by = user_id
    sep.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(sep)

    # Create history entry
    await create_sep_history(
        db=db,
        sep_id=sep.id,
        action="updated",
        previous_status=previous_status,
        new_status=sep.status,
        previous_data=previous_data,
        new_data=sep_to_dict(sep),
        bpjs_request=None,
        bpjs_response=bpjs_response,
        reason=sep_update.reason,
        user_id=user_id,
    )

    return sep


async def cancel_sep(
    db: AsyncSession,
    sep_cancel: SEPCancel,
    bpjs_response: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
) -> Optional[BPJSSEP]:
    """
    Cancel (delete) an SEP.

    Args:
        db: Database session
        sep_cancel: SEP cancellation data
        bpjs_response: BPJS API response data
        user_id: ID of user cancelling the SEP

    Returns:
        Cancelled BPJSSEP object or None if not found
    """
    # Get existing SEP
    sep = await get_sep_by_id(db, sep_cancel.sep_id)
    if not sep:
        return None

    # Store previous data for history
    previous_data = sep_to_dict(sep)
    previous_status = sep.status

    # Soft delete
    sep.is_deleted = True
    sep.deleted_at = datetime.now(timezone.utc)
    sep.deleted_by = user_id
    sep.deletion_reason = sep_cancel.reason
    sep.status = SEPStatus.CANCELLED
    sep.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(sep)

    # Create history entry
    await create_sep_history(
        db=db,
        sep_id=sep.id,
        action="cancelled",
        previous_status=previous_status,
        new_status=sep.status,
        previous_data=previous_data,
        new_data=sep_to_dict(sep),
        bpjs_request=None,
        bpjs_response=bpjs_response,
        reason=sep_cancel.reason,
        user_id=user_id,
    )

    return sep


async def get_sep_history(
    db: AsyncSession,
    sep_id: int,
) -> List[BPJSSEPHistory]:
    """Get SEP history by SEP ID."""
    stmt = select(BPJSSEPHistory).where(
        BPJSSEPHistory.sep_id == sep_id
    ).order_by(desc(BPJSSEPHistory.changed_at))

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_sep_history(
    db: AsyncSession,
    sep_id: int,
    action: str,
    new_status: Optional[str] = None,
    previous_status: Optional[str] = None,
    previous_data: Optional[Dict[str, Any]] = None,
    new_data: Optional[Dict[str, Any]] = None,
    bpjs_request: Optional[Dict[str, Any]] = None,
    bpjs_response: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    user_id: Optional[int] = None,
) -> BPJSSEPHistory:
    """Create a SEP history entry."""
    history = BPJSSEPHistory(
        sep_id=sep_id,
        action=action,
        previous_status=previous_status,
        new_status=new_status,
        previous_data=previous_data,
        new_data=new_data,
        bpjs_request=bpjs_request,
        bpjs_response=bpjs_response,
        reason=reason,
        changed_by=user_id,
    )

    db.add(history)
    await db.commit()
    await db.refresh(history)

    return history


async def get_sep_statistics(
    db: AsyncSession,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> SEPStatistics:
    """Get SEP statistics for dashboard."""
    # Build base conditions
    conditions = [BPJSSEP.is_deleted == False]

    if date_from:
        conditions.append(BPJSSEP.sep_date >= date_from)
    if date_to:
        conditions.append(BPJSSEP.sep_date <= date_to)

    base_stmt = select(func.count(BPJSSEP.id)).where(and_(*conditions))

    # Total SEPs
    total_seps = await db.scalar(base_stmt)

    # By status
    status_counts = {}
    for status in [SEPStatus.DRAFT, SEPStatus.SUBMITTED, SEPStatus.APPROVED,
                   SEPStatus.UPDATED, SEPStatus.CANCELLED, SEPStatus.ERROR]:
        stmt = base_stmt.where(BPJSSEP.status == status)
        count = await db.scalar(stmt)
        status_counts[f"{status}_seps"] = count or 0

    # By service type
    outpatient_stmt = base_stmt.where(BPJSSEP.service_type == 'RJ')
    outpatient_count = await db.scalar(outpatient_stmt) or 0

    inpatient_stmt = base_stmt.where(BPJSSEP.service_type == 'RI')
    inpatient_count = await db.scalar(inpatient_stmt) or 0

    # Today
    today = date.today()
    today_stmt = base_stmt.where(BPJSSEP.sep_date == today)
    today_count = await db.scalar(today_stmt) or 0

    # This month
    month_start = date(today.year, today.month, 1)
    month_stmt = base_stmt.where(BPJSSEP.sep_date >= month_start)
    month_count = await db.scalar(month_stmt) or 0

    return SEPStatistics(
        total_seps=total_seps or 0,
        active_seps=status_counts.get('approved_seps', 0),
        draft_seps=status_counts.get('draft_seps', 0),
        submitted_seps=status_counts.get('submitted_seps', 0),
        approved_seps=status_counts.get('approved_seps', 0),
        updated_seps=status_counts.get('updated_seps', 0),
        cancelled_seps=status_counts.get('cancelled_seps', 0),
        error_seps=status_counts.get('error_seps', 0),
        outpatient_seps=outpatient_count,
        inpatient_seps=inpatient_count,
        today_count=today_count,
        this_month_count=month_count,
    )


def sep_to_dict(sep: BPJSSEP) -> Dict[str, Any]:
    """Convert SEP object to dictionary for history storage."""
    return {
        "sep_id": sep.id,
        "sep_number": sep.sep_number,
        "encounter_id": sep.encounter_id,
        "patient_id": sep.patient_id,
        "sep_date": sep.sep_date.isoformat() if sep.sep_date else None,
        "service_type": sep.service_type,
        "bpjs_card_number": sep.bpjs_card_number,
        "ppk_code": sep.ppk_code,
        "polyclinic_code": sep.polyclinic_code,
        "treatment_class": sep.treatment_class,
        "initial_diagnosis_code": sep.initial_diagnosis_code,
        "initial_diagnosis_name": sep.initial_diagnosis_name,
        "doctor_code": sep.doctor_code,
        "doctor_name": sep.doctor_name,
        "status": sep.status,
    }
