"""Admission Workflow API Endpoints for STORY-021

This module provides API endpoints for:
- Patient admission workflow
- Bed selection and assignment
- Room transfer workflow
- BPJS SEP updates
- Admission documentation
- Estimated discharge tracking
- Discharge criteria tracking
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.admission import (
    AdmissionOrderCreate, AdmissionOrderResponse,
    BedSelectionRequest, BedSelectionResponse, AvailableBedOption,
    RoomTransferRequest, RoomTransferApproval, RoomTransferResponse,
    AdmissionDocumentation, AdmissionDocumentResponse,
    DischargeCriteriaChecklist, DischargeReadinessAssessment,
    EstimatedDischargeUpdate, BPJSSEPUpdate, BPJSSEPResponse,
    AdmissionSummary, AdmissionListResponse
)
from app.crud.admission import (
    # Admission operations
    get_admission, get_admissions, create_admission_order, update_admission_status,
    assign_bed_to_admission,
    # Transfer operations
    get_room_transfer, get_room_transfers, create_room_transfer_request,
    approve_room_transfer, complete_room_transfer, get_bed_change_history,
    # Documentation operations
    get_admission_documentation, upsert_admission_documentation,
    # Discharge operations
    create_discharge_readiness_assessment, get_latest_discharge_assessment,
    # Summary
    get_admission_summary, get_admission_statistics
)
from app.crud.bed import get_available_beds, BedAvailabilityFilter


router = APIRouter()


# =============================================================================
# Admission Order Endpoints
# =============================================================================

@router.post("/orders", response_model=AdmissionOrderResponse, status_code=status.HTTP_201_CREATED)
def create_admission_order_endpoint(
    order: AdmissionOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> AdmissionOrderResponse:
    """Create a new admission order (doctor only)"""
    if current_user.role not in ["doctor", "admin", "superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create admission orders"
        )

    # Generate order number
    order_number = f"ADM-{datetime.now().strftime('%Y%m%d')}-{order.patient_id:04d}"

    try:
        admission = create_admission_order(db, order, order_number, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Enrich response
    admission.patient_name = admission.patient.full_name if admission.patient else None
    admission.patient_mrn = admission.patient.mrn if admission.patient else None
    admission.doctor_name = admission.doctor.full_name if admission.doctor else None

    return admission


@router.get("/orders", response_model=List[AdmissionOrderResponse])
def list_admission_orders(
    patient_id: Optional[int] = Query(None),
    doctor_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[AdmissionOrderResponse]:
    """List admission orders with optional filtering"""
    admissions = get_admissions(db, patient_id=patient_id, doctor_id=doctor_id, status=status_filter, skip=skip, limit=limit)

    # Enrich responses
    for admission in admissions:
        admission.patient_name = admission.patient.full_name if admission.patient else None
        admission.patient_mrn = admission.patient.mrn if admission.patient else None
        admission.doctor_name = admission.doctor.full_name if admission.doctor else None
        if admission.assigned_bed:
            admission.assigned_bed_number = admission.assigned_bed.bed_number
            admission.assigned_room_number = admission.assigned_bed.room_number
            admission.assigned_room_class = admission.assigned_bed.room_class

    return admissions


@router.get("/orders/{admission_id}", response_model=AdmissionOrderResponse)
def get_admission_order_endpoint(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> AdmissionOrderResponse:
    """Get admission order details"""
    admission = get_admission(db, admission_id)
    if not admission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admission order not found"
        )

    admission.patient_name = admission.patient.full_name if admission.patient else None
    admission.patient_mrn = admission.patient.mrn if admission.patient else None
    admission.doctor_name = admission.doctor.full_name if admission.doctor else None
    if admission.assigned_bed:
        admission.assigned_bed_number = admission.assigned_bed.bed_number
        admission.assigned_room_number = admission.assigned_bed.room_number
        admission.assigned_room_class = admission.assigned_bed.room_class

    return admission


@router.get("/orders/{admission_id}/summary", response_model=AdmissionSummary)
def get_admission_summary_endpoint(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> AdmissionSummary:
    """Get comprehensive admission summary"""
    summary = get_admission_summary(db, admission_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admission not found"
        )
    return AdmissionSummary(**summary)


# =============================================================================
# Bed Selection Endpoints
# =============================================================================

@router.get("/available-beds", response_model=List[AvailableBedOption])
def get_available_beds_for_admission(
    room_class: Optional[str] = Query(None),
    ward_id: Optional[int] = Query(None),
    gender_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[AvailableBedOption]:
    """Get available beds for admission with filtering"""
    from app.schemas.bed import BedStatus, RoomClass, GenderType

    filters = BedAvailabilityFilter(
        ward_id=ward_id,
        room_class=RoomClass(room_class) if room_class else None,
        gender_type=GenderType(gender_type) if gender_type else None,
        availability_status=BedStatus.AVAILABLE
    )

    beds, _ = get_available_beds(db, filters, skip=0, limit=limit)

    # Get ward names
    from app.models.hospital import Department
    ward_names = {w.id: w.name for w in db.query(Department).all()}

    available_beds = []
    for bed in beds:
        available_beds.append(AvailableBedOption(
            bed_id=bed.id,
            bed_number=bed.bed_number,
            room_number=bed.room_number,
            room_class=bed.room_class,
            ward_id=bed.ward_id,
            ward_name=ward_names.get(bed.ward_id, f"Ward {bed.ward_id}"),
            bed_type=bed.bed_type,
            floor=bed.floor,
            gender_type=bed.gender_type
        ))

    return available_beds


@router.post("/orders/{admission_id}/assign-bed", response_model=BedSelectionResponse)
def assign_bed_endpoint(
    admission_id: int,
    selection: BedSelectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BedSelectionResponse:
    """Assign bed to admission"""
    admission = assign_bed_to_admission(
        db,
        admission_id,
        selection.bed_id,
        selection.notes
    )

    if not admission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admission not found"
        )

    bed = admission.assigned_bed
    return BedSelectionResponse(
        admission_id=admission.id,
        patient_id=admission.patient_id,
        patient_name=admission.patient.full_name if admission.patient else "",
        bed_id=bed.id,
        bed_number=bed.bed_number,
        room_number=bed.room_number,
        room_class=bed.room_class,
        ward_id=bed.ward_id,
        assigned_at=admission.admission_date or datetime.now(),
        assigned_by=current_user.full_name,
        expected_discharge_date=admission.expected_discharge_date,
        notes=selection.notes
    )


# =============================================================================
# Room Transfer Endpoints
# =============================================================================

@router.post("/transfers", response_model=RoomTransferResponse, status_code=status.HTTP_201_CREATED)
def create_room_transfer_endpoint(
    transfer: RoomTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> RoomTransferResponse:
    """Create room transfer request (doctor/nurse only)"""
    if current_user.role not in ["doctor", "nurse", "admin", "superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    transfer_created = create_room_transfer_request(db, transfer)

    from_bed = transfer_created.from_bed
    to_bed = transfer_created.to_bed

    return RoomTransferResponse(
        transfer_id=transfer_created.id,
        admission_id=transfer_created.admission_id,
        patient_id=transfer_created.patient_id,
        patient_name=transfer_created.patient.full_name if transfer_created.patient else "",
        from_bed={
            "bed_id": from_bed.id,
            "bed_number": from_bed.bed_number,
            "room_number": from_bed.room_number
        },
        to_bed={
            "bed_id": to_bed.id,
            "bed_number": to_bed.bed_number,
            "room_number": to_bed.room_number
        },
        reason=transfer_created.reason,
        transfer_type=transfer_created.transfer_type,
        status=transfer_created.status,
        requested_at=transfer_created.requested_at,
        requested_by=transfer_created.requested_by.full_name,
        notes=transfer_created.notes
    )


@router.post("/transfers/{transfer_id}/approve", response_model=RoomTransferResponse)
def approve_room_transfer_endpoint(
    transfer_id: int,
    approval: RoomTransferApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> RoomTransferResponse:
    """Approve or reject room transfer (admin/supervisor only)"""
    if current_user.role not in ["admin", "superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    transfer = approve_room_transfer(db, transfer_id, approval)
    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found or invalid status"
        )

    from_bed = transfer.from_bed
    to_bed = transfer.to_bed

    return RoomTransferResponse(
        transfer_id=transfer.id,
        admission_id=transfer.admission_id,
        patient_id=transfer.patient_id,
        patient_name=transfer.patient.full_name if transfer.patient else "",
        from_bed={
            "bed_id": from_bed.id,
            "bed_number": from_bed.bed_number,
            "room_number": from_bed.room_number
        },
        to_bed={
            "bed_id": to_bed.id,
            "bed_number": to_bed.bed_number,
            "room_number": to_bed.room_number
        },
        reason=transfer.reason,
        transfer_type=transfer.transfer_type,
        status=transfer.status,
        requested_at=transfer.requested_at,
        requested_by=transfer.requested_by.full_name,
        approved_by=transfer.approved_by.full_name if transfer.approved_by else None,
        approved_at=transfer.approved_at,
        notes=transfer.notes
    )


@router.post("/transfers/{transfer_id}/complete", response_model=RoomTransferResponse)
def complete_room_transfer_endpoint(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> RoomTransferResponse:
    """Complete approved room transfer (nurse only)"""
    if current_user.role not in ["nurse", "admin", "superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only nurses can complete transfers"
        )

    transfer = complete_room_transfer(db, transfer_id, current_user.id)
    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found or not approved"
        )

    from_bed = transfer.from_bed
    to_bed = transfer.to_bed

    return RoomTransferResponse(
        transfer_id=transfer.id,
        admission_id=transfer.admission_id,
        patient_id=transfer.patient_id,
        patient_name=transfer.patient.full_name if transfer.patient else "",
        from_bed={
            "bed_id": from_bed.id,
            "bed_number": from_bed.bed_number,
            "room_number": from_bed.room_number
        },
        to_bed={
            "bed_id": to_bed.id,
            "bed_number": to_bed.bed_number,
            "room_number": to_bed.room_number
        },
        reason=transfer.reason,
        transfer_type=transfer.transfer_type,
        status=transfer.status,
        requested_at=transfer.requested_at,
        requested_by=transfer.requested_by.full_name,
        approved_by=transfer.approved_by.full_name if transfer.approved_by else None,
        approved_at=transfer.approved_at,
        completed_at=transfer.completed_at,
        notes=transfer.notes
    )


@router.get("/orders/{admission_id}/transfers", response_model=List[RoomTransferResponse])
def get_admission_transfers(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[RoomTransferResponse]:
    """Get all room transfers for an admission"""
    transfers = get_room_transfers(db, admission_id=admission_id)

    result = []
    for transfer in transfers:
        from_bed = transfer.from_bed
        to_bed = transfer.to_bed

        result.append(RoomTransferResponse(
            transfer_id=transfer.id,
            admission_id=transfer.admission_id,
            patient_id=transfer.patient_id,
            patient_name=transfer.patient.full_name if transfer.patient else "",
            from_bed={
                "bed_id": from_bed.id,
                "bed_number": from_bed.bed_number,
                "room_number": from_bed.room_number
            },
            to_bed={
                "bed_id": to_bed.id,
                "bed_number": to_bed.bed_number,
                "room_number": to_bed.room_number
            },
            reason=transfer.reason,
            transfer_type=transfer.transfer_type,
            status=transfer.status,
            requested_at=transfer.requested_at,
            requested_by=transfer.requested_by.full_name,
            approved_by=transfer.approved_by.full_name if transfer.approved_by else None,
            approved_at=transfer.approved_at,
            completed_at=transfer.completed_at,
            notes=transfer.notes
        ))

    return result


@router.get("/orders/{admission_id}/bed-history", response_model=List[dict])
def get_bed_history_endpoint(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[dict]:
    """Get bed change history for admission"""
    history = get_bed_change_history(db, admission_id=admission_id)

    result = []
    for h in history:
        result.append({
            "change_type": h.change_type,
            "from_bed": {
                "bed_number": h.from_bed.bed_number,
                "room_number": h.from_bed.room_number
            } if h.from_bed else None,
            "to_bed": {
                "bed_number": h.to_bed.bed_number,
                "room_number": h.to_bed.room_number
            } if h.to_bed else None,
            "reason": h.change_reason,
            "changed_at": h.changed_at,
            "changed_by": h.changed_by.full_name
        })

    return result


# =============================================================================
# Admission Documentation Endpoints
# =============================================================================

@router.get("/orders/{admission_id}/documentation")
def get_documentation_endpoint(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get admission documentation"""
    doc = get_admission_documentation(db, admission_id)
    if not doc:
        return {}

    import json
    return {
        "admission_id": doc.admission_id,
        "admission_notes": doc.admission_notes,
        "allergies": json.loads(doc.allergies) if doc.allergies else [],
        "current_medications": json.loads(doc.current_medications) if doc.current_medications else [],
        "advance_directives": doc.advance_directives,
        "emergency_contact": doc.emergency_contact,
        "insurance_info": json.loads(doc.insurance_info) if doc.insurance_info else None
    }


@router.put("/orders/{admission_id}/documentation")
def update_documentation_endpoint(
    admission_id: int,
    documentation: AdmissionDocumentation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update admission documentation"""
    if current_user.role not in ["doctor", "nurse", "admin", "superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    doc = upsert_admission_documentation(db, documentation)
    import json
    return {
        "admission_id": doc.admission_id,
        "admission_notes": doc.admission_notes,
        "allergies": json.loads(doc.allergies) if doc.allergies else [],
        "current_medications": json.loads(doc.current_medications) if doc.current_medications else [],
        "advance_directives": doc.advance_directives,
        "emergency_contact": doc.emergency_contact,
        "insurance_info": json.loads(doc.insurance_info) if doc.insurance_info else None
    }


# =============================================================================
# Discharge Readiness Endpoints
# =============================================================================

@router.post("/orders/{admission_id}/discharge-assessment")
def create_discharge_assessment_endpoint(
    admission_id: int,
    assessment: DischargeReadinessAssessment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create discharge readiness assessment (doctor only)"""
    if current_user.role not in ["doctor", "admin", "superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create discharge assessments"
        )

    assessment_created = create_discharge_readiness_assessment(db, assessment)

    import json
    return {
        "id": assessment_created.id,
        "admission_id": assessment_created.admission_id,
        "is_ready": assessment_created.is_ready,
        "readiness_score": assessment_created.readiness_score,
        "criteria_met": json.loads(assessment_created.criteria_met) if assessment_created.criteria_met else [],
        "criteria_not_met": json.loads(assessment_created.criteria_not_met) if assessment_created.criteria_not_met else [],
        "barriers_to_discharge": json.loads(assessment_created.barriers_to_discharge) if assessment_created.barriers_to_discharge else [],
        "required_follow_up": json.loads(assessment_created.required_follow_up) if assessment_created.required_follow_up else [],
        "assessed_at": assessment_created.assessed_at,
        "notes": assessment_created.notes
    }


@router.get("/orders/{admission_id}/discharge-assessment")
def get_discharge_assessment_endpoint(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get latest discharge readiness assessment"""
    assessment = get_latest_discharge_assessment(db, admission_id)

    if not assessment:
        return None

    import json
    return {
        "id": assessment.id,
        "admission_id": assessment.admission_id,
        "is_ready": assessment.is_ready,
        "readiness_score": assessment.readiness_score,
        "criteria_met": json.loads(assessment.criteria_met) if assessment.criteria_met else [],
        "criteria_not_met": json.loads(assessment.criteria_not_met) if assessment.criteria_not_met else [],
        "barriers_to_discharge": json.loads(assessment.barriers_to_discharge) if assessment.barriers_to_discharge else [],
        "required_follow_up": json.loads(assessment.required_follow_up) if assessment.required_follow_up else [],
        "assessed_at": assessment.assessed_at,
        "notes": assessment.notes
    }


# =============================================================================
# Statistics Endpoint
# =============================================================================

@router.get("/statistics")
def get_statistics_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get admission statistics"""
    return get_admission_statistics(db)
