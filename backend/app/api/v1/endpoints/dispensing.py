"""Prescription Dispensing API endpoints for STORY-025

This module provides API endpoints for:
- Dispensing queue management
- Drug barcode scanning
- Prescription verification
- Stock availability checking
- Label generation
- Patient counseling documentation
- Dispensing history and statistics
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_current_active_user, get_db
from app.models.user import User
from app.schemas.dispensing import (
    DispensingQueueItem, DispensingQueueResponse,
    PrescriptionVerificationRequest, PrescriptionVerificationResponse,
    DrugScanRequest, DrugScanResponse,
    StockCheckResult,
    LabelGenerationRequest, LabelGenerationResponse,
    CounselingRequest, CounselingNote,
    DispensingCompletion, DispensingCompletionResponse,
    DispensingHistoryResponse, DispensingHistoryItem,
    DispensingStatistics,
    DispensingStatus, DispensePriority,
)
from app.crud import dispensing as crud


router = APIRouter()


# =============================================================================
# Dispensing Queue Endpoints
# =============================================================================

@router.get("/dispensing/queue", response_model=DispensingQueueResponse)
async def get_dispensing_queue(
    status: Optional[DispensingStatus] = Query(None),
    priority: Optional[DispensePriority] = Query(None),
    assigned_to_me: bool = Query(False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get dispensing queue with filtering"""
    assigned_to_id = current_user.id if assigned_to_me else None

    queue_items, total = await crud.get_dispensing_queue(
        db=db,
        status=status,
        priority=priority,
        assigned_to_id=assigned_to_id,
        page=page,
        page_size=page_size,
    )

    # Build response
    response_items = []
    for item in queue_items:
        response_items.append(_build_queue_item(item))

    # Calculate statistics
    by_priority = {"stat": 0, "urgent": 0, "routine": 0}
    by_status = {}

    for item in response_items:
        by_priority[item.priority.value] = by_priority.get(item.priority.value, 0) + 1
        by_status[item.status.value] = by_status.get(item.status.value, 0) + 1

    return DispensingQueueResponse(
        queue=response_items,
        total=total,
        by_priority=by_priority,
        by_status=by_status,
        page=page,
        page_size=page_size,
    )


@router.get("/dispensing/statistics", response_model=DispensingStatistics)
async def get_dispensing_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get dispensing statistics"""
    stats = await crud.get_queue_statistics(db=db)
    return DispensingStatistics(**stats)


@router.post("/dispensing/queue/{prescription_id}/start", response_model=DispensingQueueItem)
async def start_dispensing(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Start dispensing a prescription (assign to pharmacist)"""
    queue_item = await crud.update_dispensing_status(
        db=db,
        prescription_id=prescription_id,
        status=DispensingStatus.IN_PROGRESS,
        assigned_to_id=current_user.id,
    )

    return _build_queue_item(queue_item)


# =============================================================================
# Drug Scanning Endpoints
# =============================================================================

@router.post("/dispensing/scan", response_model=DrugScanResponse)
async def scan_drug(
    scan_request: DrugScanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Scan drug barcode for verification"""
    scan_response = await crud.scan_drug(
        db=db,
        prescription_id=scan_request.prescription_id if hasattr(scan_request, 'prescription_id') else 0,
        scan_request=scan_request,
        pharmacist_id=current_user.id,
    )

    return scan_response


# =============================================================================
# Stock Availability Endpoints
# =============================================================================

@router.get("/dispensing/prescriptions/{prescription_id}/stock-check", response_model=List[StockCheckResult])
async def check_stock_availability(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Check stock availability for prescription items"""
    results = await crud.check_stock_availability(db=db, prescription_id=prescription_id)
    return results


# =============================================================================
# Prescription Verification Endpoints
# =============================================================================

@router.post("/dispensing/prescriptions/{prescription_id}/verify", response_model=PrescriptionVerificationResponse)
async def verify_prescription(
    prescription_id: int,
    verification: PrescriptionVerificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Verify prescription before final dispensing"""
    # Override prescription_id from URL
    verification.prescription_id = prescription_id

    verification_response = await crud.verify_prescription_for_dispensing(
        db=db,
        prescription_id=prescription_id,
        verification=verification,
        verifier_id=current_user.id,
        verifier_name=current_user.full_name,
        verifier_role="pharmacist",  # Could be based on user role
    )

    return verification_response


# =============================================================================
# Label Generation Endpoints
# =============================================================================

@router.post("/dispensing/prescriptions/{prescription_id}/labels", response_model=LabelGenerationResponse)
async def generate_labels(
    prescription_id: int,
    prescription_item_id: int,
    include_barcode: bool = True,
    include_warnings: bool = True,
    copies: int = Query(default=1, ge=1, le=4),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Generate dispensing labels for prescription items"""
    labels, label_urls = await crud.generate_dispensing_labels(
        db=db,
        prescription_id=prescription_id,
        prescription_item_id=prescription_item_id,
        generated_by_id=current_user.id,
        generated_by_name=current_user.full_name,
        include_barcode=include_barcode,
        include_warnings=include_warnings,
        copies=copies,
    )

    return LabelGenerationResponse(
        labels=labels,
        label_urls=label_urls,
        generated_at=labels[0].dispensed_date,
        generated_by=current_user.full_name,
    )


# =============================================================================
# Patient Counseling Endpoints
# =============================================================================

@router.post("/dispensing/counseling", response_model=CounselingNote)
async def create_counseling_record(
    counseling: CounselingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create patient counseling documentation"""
    counseling_record = await crud.create_counseling_record(
        db=db,
        counseling=counseling,
        counselor_id=current_user.id,
        counselor_name=current_user.full_name,
    )

    return CounselingNote(
        prescription_id=counseling_record.prescription_id,
        patient_id=counseling_record.patient_id,
        counselor_id=counseling_record.counselor_id,
        counselor_name=counseling_record.counselor_name,
        counseling_date=counseling_record.counseling_date,
        discussed_purpose=counseling_record.discussed_purpose,
        discussed_dosage=counseling_record.discussed_dosage,
        discussed_timing=counseling_record.discussed_timing,
        discussed_side_effects=counseling_record.discussed_side_effects,
        discussed_interactions=counseling_record.discussed_interactions,
        discussed_storage=counseling_record.discussed_storage,
        discussed_special_instructions=counseling_record.discussed_special_instructions,
        patient_understood=counseling_record.patient_understood,
        patient_questions=counseling_record.patient_questions,
        concerns_raised=counseling_record.concerns_raised,
        counseling_notes=counseling_record.counseling_notes,
        follow_up_required=counseling_record.follow_up_required,
        follow_up_notes=counseling_record.follow_up_notes,
        patient_signature=counseling_record.patient_signature,
        caregiver_name=counseling_record.caregiver_name,
    )


# =============================================================================
# Dispensing Completion Endpoints
# =============================================================================

@router.post("/dispensing/prescriptions/{prescription_id}/complete", response_model=DispensingCompletionResponse)
async def complete_dispensing(
    prescription_id: int,
    completion: DispensingCompletion,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Complete the dispensing process"""
    # Override prescription_id from URL
    completion.prescription_id = prescription_id
    completion.dispenser_id = current_user.id

    completion_response = await crud.complete_dispensing(
        db=db,
        completion=completion,
    )

    return completion_response


@router.post("/dispensing/prescriptions/{prescription_id}/dispense-to-patient", response_model=DispensingCompletionResponse)
async def dispense_to_patient(
    prescription_id: int,
    patient_verified: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark prescription as dispensed to patient"""
    # Update status to DISPENSED
    queue_item = await crud.update_dispensing_status(
        db=db,
        prescription_id=prescription_id,
        status=DispensingStatus.DISPENSED,
        notes=f"Dispensed to patient by {current_user.full_name}",
    )

    return DispensingCompletionResponse(
        prescription_id=prescription_id,
        prescription_number="",  # Would load from prescription
        status=DispensingStatus.DISPENSED,
        dispensed_date=queue_item.dispensed_at or datetime.utcnow(),
        dispensed_by=current_user.full_name,
        items_dispensed=queue_item.total_items,
        total_items=queue_item.total_items,
        ready_for_pickup=False,
        patient_notified=False,
    )


# =============================================================================
# Dispensing History Endpoints
# =============================================================================

@router.get("/dispensing/history", response_model=DispensingHistoryResponse)
async def get_dispensing_history(
    patient_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),  # YYYY-MM-DD format
    date_to: Optional[str] = Query(None),  # YYYY-MM-DD format
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get dispensing history with filtering"""
    from datetime import datetime

    # Parse dates
    date_from_parsed = None
    date_to_parsed = None

    if date_from:
        date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d").date()
    if date_to:
        date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d").date()

    history, total = await crud.get_dispensing_history(
        db=db,
        patient_id=patient_id,
        date_from=date_from_parsed,
        date_to=date_to_parsed,
        page=page,
        page_size=page_size,
    )

    # Build response
    history_items = []
    for item in history:
        history_items.append(_build_history_item(item))

    return DispensingHistoryResponse(
        patient_id=patient_id,
        history=history_items,
        total=total,
        date_range={"from": date_from_parsed, "to": date_to_parsed} if date_from_parsed or date_to_parsed else None,
        page=page,
        page_size=page_size,
    )


# =============================================================================
# Helper Functions
# =============================================================================

def _build_queue_item(queue_item) -> DispensingQueueItem:
    """Build queue item response"""
    from app.schemas.dispensing import DispensingStatus, DispensePriority

    # Get prescription details
    prescription = queue_item.prescription

    # Get patient info (would load from prescription.patient)
    patient_name = prescription.patient.name if prescription.patient else "Unknown"

    # Get prescriber info
    prescriber_name = prescription.prescriber.full_name if prescription.prescriber else None

    # Count special drugs
    narcotic_count = 0
    antibiotic_count = 0

    for item in prescription.items:
        # Would check drug properties
        pass

    return DispensingQueueItem(
        prescription_id=prescription.id,
        prescription_number=prescription.prescription_number,
        patient_id=prescription.patient_id,
        patient_name=patient_name,
        patient_bpjs_number=prescription.patient.bpjs_number if prescription.patient else None,
        priority=DispensePriority(queue_item.priority),
        status=DispensingStatus(queue_item.status),
        submitted_date=prescription.submitted_date or prescription.created_at,
        estimated_ready_time=queue_item.estimated_ready_time,
        prescriber_name=prescriber_name,
        total_items=queue_item.total_items,
        items_dispensed=queue_item.items_scanned,
        narcotic_count=narcotic_count,
        antibiotic_count=antibiotic_count,
        requires_cold_storage=False,  # Would check drug properties
        has_special_instructions=False,  # Would check items
        queue_position=queue_item.queue_position,
        estimated_wait_minutes=queue_item.estimated_wait_minutes,
        verified=queue_item.verified_at is not None,
        verified_by=queue_item.verified_by.full_name if queue_item.verified_by else None,
        verified_date=queue_item.verified_at,
        created_at=queue_item.created_at,
    )


def _build_history_item(queue_item) -> DispensingHistoryItem:
    """Build history item response"""
    prescription = queue_item.prescription

    # Get patient info
    patient_name = prescription.patient.name if prescription.patient else "Unknown"

    # Get dispenser info
    dispenser_name = queue_item.assigned_to.full_name if queue_item.assigned_to else "Unknown"

    # Get counselor info
    counselor_name = None
    if hasattr(prescription, 'counseling') and prescription.counseling:
        counselor_name = prescription.counseling.counselor_name

    return DispensingHistoryItem(
        prescription_id=prescription.id,
        prescription_number=prescription.prescription_number,
        patient_id=prescription.patient_id,
        patient_name=patient_name,
        dispensed_date=queue_item.dispensed_at or queue_item.completed_at,
        dispenser_name=dispenser_name,
        items_dispensed=[],  # Would build from prescription.items
        total_items=len(prescription.items),
        total_cost=prescription.estimated_cost,
        bpjs_claimed=prescription.bpjs_coverage_estimate,
        patient_paid=prescription.patient_cost_estimate,
        counseling_documented=counselor_name is not None,
        counselor_name=counselor_name,
    )
