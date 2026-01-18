"""Prescription Dispensing CRUD Operations for STORY-025

This module provides CRUD operations for:
- Dispensing queue management
- Prescription verification
- Drug barcode scanning
- Stock availability checking
- Label generation
- Patient counseling documentation
- Dispensing history
"""
from typing import List, Optional, Tuple, Dict
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_, or_, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import json
import uuid

from app.models.dispensing import (
    DispensingQueue, DispensingScan, PatientCounseling,
    DispensingLabel, PrescriptionVerificationRecord, StockCheckLog
)
from app.models.prescription import Prescription, PrescriptionItem, BasicPrescriptionTransmission
from app.models.inventory import Drug
from app.models.user import User
from app.schemas.dispensing import (
    DispensingStatus, DispensePriority, VerificationStatus,
    DispensingQueueItem, DispensingQueueResponse,
    PrescriptionVerificationRequest, PrescriptionVerificationResponse,
    DrugScanRequest, DrugScanResponse, CounselingRequest, CounselingNote,
    DispensingCompletion, DispensingCompletionResponse,
    StockCheckResult, DispensingLabel as DispensingLabelSchema,
)


# =============================================================================
# Dispensing Queue Management
# =============================================================================

async def get_dispensing_queue(
    db: AsyncSession,
    status: Optional[DispensingStatus] = None,
    priority: Optional[DispensePriority] = None,
    assigned_to_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[DispensingQueue], int]:
    """Get dispensing queue with filtering and pagination"""
    conditions = []

    if status:
        conditions.append(DispensingQueue.status == status)
    if priority:
        conditions.append(DispensingQueue.priority == priority)
    if assigned_to_id:
        conditions.append(
            or_(
                DispensingQueue.assigned_to_id == assigned_to_id,
                DispensingQueue.assigned_to_id.is_(None),  # Unassigned items
            )
        )

    # Build query
    stmt = select(DispensingQueue)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Get total count
    count_stmt = select(sql_func.count(DispensingQueue.id))
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Apply pagination and ordering (priority first, then created_at)
    stmt = stmt.options(
        selectinload(DispensingQueue.prescription).selectinload(Prescription.items),
        selectinload(DispensingQueue.assigned_to),
        selectinload(DispensingQueue.verified_by),
    )
    stmt = stmt.order_by(
        sql_func.case(
            (DispensingQueue.priority == DispensePriority.STAT, 1),
            (DispensingQueue.priority == DispensePriority.URGENT, 2),
            (DispensingQueue.priority == DispensePriority.ROUTINE, 3),
            else_=4,
        ),
        DispensingQueue.created_at.asc(),
    )
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    queue_items = result.scalars().all()

    return list(queue_items), total


async def get_or_create_dispensing_queue(
    db: AsyncSession,
    prescription_id: int,
) -> DispensingQueue:
    """Get or create dispensing queue entry for a prescription"""
    stmt = select(DispensingQueue).where(DispensingQueue.prescription_id == prescription_id)
    result = await db.execute(stmt)
    queue_item = result.scalar_one_or_none()

    if queue_item:
        return queue_item

    # Get prescription details
    prescription_stmt = select(Prescription).where(Prescription.id == prescription_id)
    prescription_result = await db.execute(prescription_stmt)
    prescription = prescription_result.scalar_one_or_none()

    if not prescription:
        raise ValueError("Prescription not found")

    # Count special drugs
    narcotic_count = 0
    antibiotic_count = 0
    for item in prescription.items:
        drug_stmt = select(Drug).where(Drug.id == item.drug_id)
        drug_result = await db.execute(drug_stmt)
        drug = drug_result.scalar_one_or_none()
        if drug:
            if drug.is_narcotic:
                narcotic_count += 1
            if drug.is_antibiotic:
                antibiotic_count += 1

    # Determine priority
    priority = DispensePriority.STAT if prescription.priority == "stat" else (
        DispensePriority.URGENT if prescription.priority == "urgent" else DispensePriority.ROUTINE
    )

    # Create queue entry
    queue_item = DispensingQueue(
        prescription_id=prescription_id,
        status=DispensingStatus.QUEUED,
        priority=priority,
        total_items=len(prescription.items),
        estimated_ready_time=_calculate_ready_time(priority),
    )

    db.add(queue_item)
    await db.commit()
    await db.refresh(queue_item)

    # Update queue position
    await _update_queue_positions(db)

    return queue_item


async def update_dispensing_status(
    db: AsyncSession,
    prescription_id: int,
    status: DispensingStatus,
    assigned_to_id: Optional[int] = None,
    notes: Optional[str] = None,
) -> DispensingQueue:
    """Update dispensing status"""
    queue_item = await get_or_create_dispensing_queue(db, prescription_id)

    queue_item.status = status
    if assigned_to_id:
        queue_item.assigned_to_id = assigned_to_id
    if notes:
        queue_item.dispensing_notes = notes

    # Update timestamps based on status
    if status == DispensingStatus.IN_PROGRESS:
        queue_item.started_at = datetime.utcnow()
    elif status == DispensingStatus.AWAITING_VERIFICATION:
        queue_item.items_scanned = queue_item.total_items  # Assume all scanned
    elif status == DispensingStatus.VERIFIED:
        queue_item.verified_at = datetime.utcnow()
    elif status == DispensingStatus.READY_FOR_PICKUP:
        queue_item.completed_at = datetime.utcnow()
    elif status == DispensingStatus.DISPENSED:
        queue_item.dispensed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(queue_item)

    # Update queue positions
    await _update_queue_positions(db)

    return queue_item


async def get_queue_statistics(
    db: AsyncSession,
) -> Dict:
    """Get dispensing queue statistics"""
    # Count by status
    status_stmt = select(
        DispensingQueue.status,
        sql_func.count(DispensingQueue.id)
    ).group_by(DispensingQueue.status)
    status_result = await db.execute(status_stmt)
    by_status = {status.value: count for status, count in status_result.all()}

    # Count by priority
    priority_stmt = select(
        DispensingQueue.priority,
        sql_func.count(DispensingQueue.id)
    ).group_by(DispensingQueue.priority)
    priority_result = await db.execute(priority_stmt)
    by_priority = {priority.value: count for priority, count in priority_result.all()}

    # Today's stats
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())

    today_dispensed_stmt = select(sql_func.count(DispensingQueue.id)).where(
        and_(
            DispensingQueue.dispensed_at >= today_start,
            DispensingQueue.status == DispensingStatus.DISPENSED
        )
    )
    today_dispensed_result = await db.execute(today_dispensed_stmt)
    today_dispensed = today_dispensed_result.scalar_one() or 0

    # Average dispensing time
    avg_time_stmt = select(sql_func.avg(
        sql_func.extract('epoch', DispensingQueue.completed_at - DispensingQueue.started_at)
    )).where(
        and_(
            DispensingQueue.completed_at >= today_start,
            DispensingQueue.started_at.isnot(None)
        )
    )
    avg_time_result = await db.execute(avg_time_stmt)
    avg_time_seconds = avg_time_result.scalar_one()
    avg_time_minutes = round(avg_time_seconds / 60, 2) if avg_time_seconds else 0

    # Current queue length
    queue_length_stmt = select(sql_func.count(DispensingQueue.id)).where(
        DispensingQueue.status == DispensingStatus.QUEUED
    )
    queue_length_result = await db.execute(queue_length_stmt)
    queue_length = queue_length_result.scalar_one() or 0

    return {
        "today_dispensed": today_dispensed,
        "today_pending": by_status.get("queued", 0) + by_status.get("in_progress", 0),
        "today_completed": today_dispensed,
        "average_dispensing_time_minutes": avg_time_minutes,
        "queue_length": queue_length,
        "by_priority": by_priority,
        "by_status": by_status,
        "narcotic_dispensed_today": 0,  # Would need to scan drugs to count
        "antibiotic_dispensed_today": 0,
    }


# =============================================================================
# Drug Scanning
# =============================================================================

async def scan_drug(
    db: AsyncSession,
    prescription_id: int,
    scan_request: DrugScanRequest,
    pharmacist_id: int,
) -> DrugScanResponse:
    """Scan drug barcode for verification"""
    # Get dispensing queue item
    queue_item = await get_or_create_dispensing_queue(db, prescription_id)

    # Get prescription item
    item_stmt = select(PrescriptionItem).where(PrescriptionItem.id == scan_request.prescription_item_id)
    item_result = await db.execute(item_stmt)
    item = item_result.scalar_one_or_none()

    if not item:
        return DrugScanResponse(
            match=False,
            quantity_match=False,
            quantity_scanned=0,
            quantity_remaining=scan_request.quantity_expected,
            can_proceed=False,
            errors=["Prescription item not found"],
        )

    # Get scanned drug
    scanned_drug_stmt = select(Drug).where(Drug.barcode == scan_request.barcode)
    scanned_drug_result = await db.execute(scanned_drug_stmt)
    scanned_drug = scanned_drug_result.scalar_one_or_none()

    if not scanned_drug:
        return DrugScanResponse(
            match=False,
            expected_drug={"id": item.drug_id, "name": item.drug_name},
            quantity_match=False,
            quantity_scanned=0,
            quantity_remaining=scan_request.quantity_expected,
            can_proceed=False,
            errors=["Drug barcode not found"],
        )

    # Check if drugs match
    drugs_match = scanned_drug.id == item.drug_id
    warnings = []
    errors = []

    if not drugs_match:
        errors.append(f"Drug mismatch: Scanned {scanned_drug.name}, Expected {item.drug_name}")

    # Check stock
    stock_available = scanned_drug.stock_quantity >= scan_request.quantity_expected
    if not stock_available:
        warnings.append(f"Insufficient stock: {scanned_drug.stock_quantity} available, {scan_request.quantity_expected} required")

    # Create scan record
    scan_record = DispensingScan(
        dispensing_id=queue_item.id,
        prescription_item_id=item.id,
        scanned_barcode=scan_request.barcode,
        scanned_drug_id=scanned_drug.id,
        scanned_drug_name=scanned_drug.name,
        scanned_drug_batch=scanned_drug.batch_number,
        expected_drug_id=item.drug_id,
        expected_drug_name=item.drug_name,
        expected_quantity=scan_request.quantity_expected,
        is_match=drugs_match,
        quantity_scanned=scan_request.quantity_expected,
        scanned_by_id=pharmacist_id,
        warnings=warnings,
        errors=errors,
    )

    db.add(scan_record)

    # Update queue item progress
    if drugs_match:
        queue_item.items_scanned += 1
        if queue_item.items_scanned >= queue_item.total_items:
            queue_item.status = DispensingStatus.AWAITING_VERIFICATION

    await db.commit()
    await db.refresh(queue_item)

    return DrugScanResponse(
        match=drugs_match,
        scanned_drug={"id": scanned_drug.id, "name": scanned_drug.name, "generic_name": scanned_drug.generic_name},
        expected_drug={"id": item.drug_id, "name": item.drug_name},
        quantity_match=True,
        quantity_scanned=scan_request.quantity_expected,
        quantity_remaining=max(0, scan_request.quantity_expected - scan_request.quantity_expected),
        can_proceed=drugs_match and stock_available,
        warnings=warnings,
        errors=errors,
    )


# =============================================================================
# Prescription Verification
# =============================================================================

async def verify_prescription_for_dispensing(
    db: AsyncSession,
    prescription_id: int,
    verification: PrescriptionVerificationRequest,
    verifier_id: int,
    verifier_name: str,
    verifier_role: str,
) -> PrescriptionVerificationResponse:
    """Verify prescription before final dispensing"""
    # Get or create verification record
    stmt = select(PrescriptionVerificationRecord).where(
        PrescriptionVerificationRecord.prescription_id == prescription_id
    )
    result = await db.execute(stmt)
    verification_record = result.scalar_one_or_none()

    if verification_record:
        # Update existing record
        verification_record.verification_status = VerificationStatus.APPROVED if not verification.issues_found else VerificationStatus.FLAGGED
        verification_record.issues_found = verification.issues_found
        verification_record.requires_intervention = verification.requires_intervention
        verification_record.intervention_notes = verification.intervention_notes
        verification_record.interactions_overridden = verification.interactions_overridden
        verification_record.override_reason = verification.override_reason
        verification_record.verification_notes = verification.verification_notes
        verification_record.can_proceed = not verification.issues_found or verification.interactions_overridden
        verification_record.verified_date = datetime.utcnow()
    else:
        # Create new verification record
        verification_record = PrescriptionVerificationRecord(
            prescription_id=prescription_id,
            dispensing_id=(await get_or_create_dispensing_queue(db, prescription_id)).id,
            verification_status=VerificationStatus.APPROVED if not verification.issues_found else VerificationStatus.FLAGGED,
            verified_by_id=verifier_id,
            verified_by_role=verifier_role,
            patient_verified=verification.patient_verified,
            issues_found=verification.issues_found,
            requires_intervention=verification.requires_intervention,
            intervention_notes=verification.intervention_notes,
            interactions_overridden=verification.interactions_overridden,
            override_reason=verification.override_reason,
            verification_notes=verification.verification_notes,
            can_proceed=not verification.issues_found or verification.interactions_overridden,
        )
        db.add(verification_record)

    await db.commit()
    await db.refresh(verification_record)

    # Update dispensing status if verified
    if verification_record.can_proceed:
        await update_dispensing_status(
            db,
            prescription_id,
            DispensingStatus.VERIFIED,
            notes=verification.verification_notes,
        )

    return PrescriptionVerificationResponse(
        prescription_id=prescription_id,
        verification_id=verification_record.id,
        status=verification_record.verification_status,
        verified_by=verifier_name,
        verified_by_role=verifier_role,
        verified_date=verification_record.verified_date,
        notes=verification.verification_notes,
        issues_found=verification.issues_found,
        can_proceed=verification_record.can_proceed,
        requires_intervention=verification_record.requires_intervention,
        intervention_notes=verification.intervention_notes,
    )


# =============================================================================
# Stock Availability
# =============================================================================

async def check_stock_availability(
    db: AsyncSession,
    prescription_id: int,
) -> List[StockCheckResult]:
    """Check stock availability for all items in a prescription"""
    # Get prescription
    prescription_stmt = select(Prescription).options(
        selectinload(Prescription.items)
    ).where(Prescription.id == prescription_id)
    prescription_result = await db.execute(prescription_stmt)
    prescription = prescription_result.scalar_one_or_none()

    if not prescription:
        raise ValueError("Prescription not found")

    results = []

    for item in prescription.items:
        # Get drug
        drug_stmt = select(Drug).where(Drug.id == item.drug_id)
        drug_result = await db.execute(drug_stmt)
        drug = drug_result.scalar_one_or_none()

        if not drug:
            results.append(StockCheckResult(
                drug_id=item.drug_id,
                drug_name=item.drug_name,
                generic_name=item.generic_name,
                required_quantity=item.quantity or 0,
                available_quantity=0,
                stock_available=False,
            ))
            continue

        required_quantity = item.quantity or 0
        available_quantity = drug.stock_quantity or 0
        stock_available = available_quantity >= required_quantity

        # Log the check
        stock_check = StockCheckLog(
            prescription_id=prescription_id,
            drug_id=drug.id,
            required_quantity=required_quantity,
            available_quantity=available_quantity,
            stock_available=stock_available,
            checked_by_id=prescription.prescriber_id,  # Default to prescriber
        )
        db.add(stock_check)

        result = StockCheckResult(
            drug_id=drug.id,
            drug_name=drug.name,
            generic_name=drug.generic_name,
            required_quantity=required_quantity,
            available_quantity=available_quantity,
            stock_available=stock_available,
            estimated_restock_date=None,
        )

        # Find alternatives if stock insufficient
        if not stock_available:
            alternative_stmt = select(Drug).where(
                and_(
                    Drug.therapeutic_class == drug.therapeutic_class,
                    Drug.id != drug.id,
                    Drug.stock_quantity >= required_quantity,
                )
            ).limit(3)
            alternative_result = await db.execute(alternative_stmt)
            alternatives = alternative_result.scalars().all()
            result.alternative_drugs = [
                {"id": a.id, "name": a.name, "generic_name": a.generic_name}
                for a in alternatives
            ]

        results.append(result)

    await db.commit()

    return results


# =============================================================================
# Label Generation
# =============================================================================

async def generate_dispensing_labels(
    db: AsyncSession,
    prescription_id: int,
    prescription_item_id: int,
    generated_by_id: int,
    generated_by_name: str,
    include_barcode: bool = True,
    include_warnings: bool = True,
    copies: int = 1,
) -> Tuple[List[DispensingLabelSchema], List[str]]:
    """Generate dispensing labels for prescription items"""
    # Get prescription item
    item_stmt = select(PrescriptionItem).where(PrescriptionItem.id == prescription_item_id)
    item_result = await db.execute(item_stmt)
    item = item_result.scalar_one_or_none()

    if not item:
        raise ValueError("Prescription item not found")

    # Get prescription
    prescription_stmt = select(Prescription).where(Prescription.id == prescription_id)
    prescription_result = await db.execute(prescription_stmt)
    prescription = prescription_result.scalar_one_or_none()

    # Get drug details
    drug_stmt = select(Drug).where(Drug.id == item.drug_id)
    drug_result = await db.execute(drug_stmt)
    drug = drug_result.scalar_one_or_none()

    # Build warnings
    warnings = []
    if drug and drug.is_narcotic:
        warnings.append("⚠️ NARKOTIK - Harus dengan resep dokter")
    if drug and drug.is_antibiotic:
        warnings.append("⚠️ ANTIBIOTIK - Selesaikan seluruh obat sesuai anjuran")
    if include_warnings and item.special_instructions:
        warnings.append(f"⚠️ {item.special_instructions}")

    # Generate label barcode
    label_barcode = f"LBL-{prescription.prescription_number}-{item.id}-{uuid.uuid4().hex[:6].upper()}"

    # Build label
    label = DispensingLabelSchema(
        prescription_number=prescription.prescription_number,
        patient_name="",  # Would load from prescription.patient
        patient_id=prescription.patient_id,
        drug_name=item.drug_name,
        generic_name=item.generic_name,
        dosage=item.dosage,
        dose_unit=item.dose_unit,
        frequency=item.frequency,
        route=item.route,
        duration_days=item.duration_days,
        quantity_dispensed=item.quantity_dispensed or item.quantity or 0,
        special_instructions=item.special_instructions,
        warnings=warnings,
        preparation_instructions=None,  # Would add for compounds
        storage_instructions=None,  # Would add for cold storage
        dispensed_date=datetime.utcnow(),
        expires_at=None,  # For compounded medications
        dispenser_name=generated_by_name,
        barcode=label_barcode if include_barcode else "",
        warning_emoji="⚠️" if warnings else "",
    )

    # Save label to database
    dispensing = await get_or_create_dispensing_queue(db, prescription_id)

    label_record = DispensingLabel(
        dispensing_id=dispensing.id,
        prescription_item_id=item.id,
        label_data=label.model_dump(),
        label_text=_format_label_text(label),
        barcode=label_barcode,
        warning_emoji="⚠️" if warnings else None,
        generated_by_id=generated_by_id,
        print_count=copies,
    )
    db.add(label_record)
    await db.commit()

    # Generate label URLs
    label_urls = [f"/api/v1/dispensing/labels/{label_record.id}/print"] * copies

    return [label], label_urls


def _format_label_text(label: DispensingLabelSchema) -> str:
    """Format label as printable text"""
    lines = [
        f"RESEP: {label.prescription_number}",
        f"PASIEN: {label.patient_name} (ID: {label.patient_id})",
        f"OBAT: {label.drug_name}",
        f"GENERIK: {label.generic_name}",
        f"DOSIS: {label.dosage} {label.dose_unit}",
        f"FREKUENSI: {label.frequency}",
        f"RUTE: {label.route}",
    ]

    if label.duration_days:
        lines.append(f"DURASI: {label.duration_days} hari")

    lines.append(f"JUMLAH: {label.quantity_dispensed}")

    if label.special_instructions:
        lines.append(f"INSTRUKSI: {label.special_instructions}")

    for warning in label.warnings:
        lines.append(warning)

    lines.append(f"DISPENSER: {label.dispenser_name}")
    lines.append(f"TANGGAL: {label.dispensed_date.strftime('%d/%m/%Y %H:%M')}")

    return "\n".join(lines)


# =============================================================================
# Patient Counseling
# =============================================================================

async def create_counseling_record(
    db: AsyncSession,
    counseling: CounselingRequest,
    counselor_id: int,
    counselor_name: str,
) -> PatientCounseling:
    """Create patient counseling documentation"""
    counseling_record = PatientCounseling(
        prescription_id=counseling.prescription_id,
        patient_id=0,  # Would load from prescription
        counselor_id=counselor_id,
        counselor_name=counselor_name,
        discussed_purpose=counseling.discussed_purpose,
        discussed_dosage=counseling.discussed_dosage,
        discussed_timing=counseling.discussed_timing,
        discussed_side_effects=counseling.discussed_side_effects,
        discussed_interactions=counseling.discussed_interactions,
        discussed_storage=counseling.discussed_storage,
        discussed_special_instructions=counseling.discussed_special_instructions,
        patient_understood=counseling.patient_understood,
        patient_questions=counseling.patient_questions,
        concerns_raised=counseling.concerns_raised,
        counseling_notes=counseling.counseling_notes,
        follow_up_required=counseling.follow_up_required,
        follow_up_notes=counseling.follow_up_notes,
        patient_signature=counseling.patient_signature,
        caregiver_name=counseling.caregiver_name,
    )

    db.add(counseling_record)
    await db.commit()
    await db.refresh(counseling_record)

    return counseling_record


# =============================================================================
# Dispensing Completion
# =============================================================================

async def complete_dispensing(
    db: AsyncSession,
    completion: DispensingCompletion,
) -> DispensingCompletionResponse:
    """Complete the dispensing process"""
    # Get prescription
    prescription_stmt = select(Prescription).options(
        selectinload(Prescription.items)
    ).where(Prescription.id == completion.prescription_id)
    prescription_result = await db.execute(prescription_stmt)
    prescription = prescription_result.scalar_one_or_none()

    if not prescription:
        raise ValueError("Prescription not found")

    # Get dispensing queue
    queue_item = await get_or_create_dispensing_queue(db, completion.prescription_id)

    # Update status
    queue_item.status = DispensingStatus.READY_FOR_PICKUP
    queue_item.completed_at = datetime.utcnow()
    queue_item.dispensing_notes = completion.dispenser_notes
    queue_item.verified_by_id = completion.dispenser_id

    # Mark items as dispensed
    items_dispensed = 0
    for item in prescription.items:
        if not completion.partial_dispense or item.id not in (completion.partial_dispense_items or []):
            item.dispense_status = "dispensed"
            item.quantity_dispensed = item.quantity
            items_dispensed += 1

    await db.commit()
    await db.refresh(queue_item)

    return DispensingCompletionResponse(
        prescription_id=prescription.id,
        prescription_number=prescription.prescription_number,
        status=DispensingStatus.READY_FOR_PICKUP,
        dispensed_date=queue_item.completed_at,
        dispensed_by="",  # Would load from user
        items_dispensed=items_dispensed,
        total_items=len(prescription.items),
        ready_for_pickup=True,
        estimated_ready_time=None,
        patient_notified=False,
    )


# =============================================================================
# Helper Functions
# =============================================================================

async def _update_queue_positions(db: AsyncSession) -> None:
    """Update queue positions based on priority and creation time"""
    # Get all queued items
    stmt = select(DispensingQueue).where(
        DispensingQueue.status == DispensingStatus.QUEUED
    ).order_by(
        sql_func.case(
            (DispensingQueue.priority == DispensePriority.STAT, 1),
            (DispensingQueue.priority == DispensePriority.URGENT, 2),
            (DispensingQueue.priority == DispensePriority.ROUTINE, 3),
        ),
        DispensingQueue.created_at.asc(),
    )

    result = await db.execute(stmt)
    queue_items = result.scalars().all()

    # Update positions
    for position, item in enumerate(queue_items, start=1):
        item.queue_position = position
        # Calculate estimated wait time (5 min per item ahead)
        item.estimated_wait_minutes = (position - 1) * 5

    await db.commit()


def _calculate_ready_time(priority: DispensePriority) -> datetime:
    """Calculate estimated ready time based on priority"""
    if priority == DispensePriority.STAT:
        return datetime.utcnow() + timedelta(minutes=15)
    elif priority == DispensePriority.URGENT:
        return datetime.utcnow() + timedelta(minutes=30)
    else:  # ROUTINE
        return datetime.utcnow() + timedelta(hours=2)


async def get_dispensing_history(
    db: AsyncSession,
    patient_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[DispensingQueue], int]:
    """Get dispensing history with filtering"""
    conditions = [
        DispensingQueue.status == DispensingStatus.DISPENSED,
    ]

    if patient_id:
        conditions.append(DispensingQueue.prescription.has(patient_id=patient_id))

    if date_from:
        conditions.append(DispensingQueue.dispensed_at >= datetime.combine(date_from, datetime.min.time()))

    if date_to:
        conditions.append(DispensingQueue.dispensed_at <= datetime.combine(date_to, datetime.max.time()))

    # Build query
    stmt = select(DispensingQueue)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Get total count
    count_stmt = select(sql_func.count(DispensingQueue.id))
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Apply pagination
    stmt = stmt.options(
        selectinload(DispensingQueue.prescription).selectinload(Prescription.items),
    )
    stmt = stmt.order_by(DispensingQueue.dispensed_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    history = result.scalars().all()

    return list(history), total
