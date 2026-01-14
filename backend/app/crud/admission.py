"""Admission Workflow CRUD Operations for STORY-021

This module provides CRUD operations for:
- Patient admission workflow
- Bed selection and assignment
- Room transfer workflow
- BPJS SEP updates
- Admission documentation
- Estimated discharge tracking
- Discharge criteria tracking
"""
from typing import List, Optional, Dict
from datetime import datetime, date
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import Session

from app.models.admission import (
    AdmissionOrder, RoomTransfer, AdmissionDocumentation,
    AdmissionDocument, DischargeReadinessAssessment, BedChangeHistory
)
from app.schemas.admission import (
    AdmissionOrderCreate, BedSelectionRequest, RoomTransferRequest,
    RoomTransferApproval, AdmissionDocumentation, DischargeCriteriaChecklist,
    EstimatedDischargeUpdate, DischargeReadinessAssessment as DischargeReadinessSchema
)


# =============================================================================
# Admission Order CRUD
# =============================================================================

def get_admission(db: Session, admission_id: int) -> Optional[AdmissionOrder]:
    """Get admission by ID"""
    return db.query(AdmissionOrder).filter(AdmissionOrder.id == admission_id).first()


def get_admissions(
    db: Session,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AdmissionOrder]:
    """Get list of admissions with optional filtering"""
    query = db.query(AdmissionOrder)

    if patient_id:
        query = query.filter(AdmissionOrder.patient_id == patient_id)
    if doctor_id:
        query = query.filter(AdmissionOrder.doctor_id == doctor_id)
    if status:
        query = query.filter(AdmissionOrder.status == status)

    return query.order_by(AdmissionOrder.created_at.desc()).offset(skip).limit(limit).all()


def create_admission_order(
    db: Session,
    order: AdmissionOrderCreate,
    order_number: str,
    created_by_id: int
) -> AdmissionOrder:
    """Create a new admission order"""
    # Check if patient has active admission
    active_admission = db.query(AdmissionOrder).filter(
        and_(
            AdmissionOrder.patient_id == order.patient_id,
            AdmissionOrder.status.in_(["pending", "admitted", "transferred"])
        )
    ).first()

    if active_admission:
        raise ValueError(f"Patient already has an active admission: {active_admission.order_number}")

    # Create admission order
    db_admission = AdmissionOrder(
        **order.model_dump(exclude={'bpjs_sep_number'}),
        order_number=order_number,
        status="pending"
    )
    db.add(db_admission)
    db.commit()
    db.refresh(db_admission)

    return db_admission


def update_admission_status(
    db: Session,
    admission_id: int,
    status: str,
    discharge_date: Optional[datetime] = None
) -> Optional[AdmissionOrder]:
    """Update admission status"""
    admission = get_admission(db, admission_id)
    if not admission:
        return None

    admission.status = status
    if discharge_date and status == "discharged":
        admission.discharge_date = discharge_date

    db.commit()
    db.refresh(admission)
    return admission


def assign_bed_to_admission(
    db: Session,
    admission_id: int,
    bed_id: int,
    expected_discharge_date: Optional[date] = None,
    notes: Optional[str] = None
) -> Optional[AdmissionOrder]:
    """Assign bed to admission"""
    admission = get_admission(db, admission_id)
    if not admission:
        return None

    # Update admission
    admission.assigned_bed_id = bed_id
    admission.admission_date = datetime.now()
    admission.expected_discharge_date = expected_discharge_date
    admission.status = "admitted"

    # Create bed change history
    bed_change = BedChangeHistory(
        admission_id=admission_id,
        patient_id=admission.patient_id,
        to_bed_id=bed_id,
        change_type="admission",
        change_reason=notes or "Initial admission",
        changed_by_id=admission.doctor_id
    )
    db.add(bed_change)

    db.commit()
    db.refresh(admission)
    return admission


# =============================================================================
# Room Transfer CRUD
# =============================================================================

def get_room_transfer(db: Session, transfer_id: int) -> Optional[RoomTransfer]:
    """Get room transfer by ID"""
    return db.query(RoomTransfer).filter(RoomTransfer.id == transfer_id).first()


def get_room_transfers(
    db: Session,
    admission_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[RoomTransfer]:
    """Get list of room transfers with optional filtering"""
    query = db.query(RoomTransfer)

    if admission_id:
        query = query.filter(RoomTransfer.admission_id == admission_id)
    if status:
        query = query.filter(RoomTransfer.status == status)

    return query.order_by(RoomTransfer.created_at.desc()).offset(skip).limit(limit).all()


def create_room_transfer_request(
    db: Session,
    transfer: RoomTransferRequest
) -> RoomTransfer:
    """Create a new room transfer request"""
    db_transfer = RoomTransfer(
        admission_id=transfer.admission_id,
        patient_id=get_admission(db, transfer.admission_id).patient_id,
        from_bed_id=transfer.from_bed_id,
        to_bed_id=transfer.to_bed_id,
        reason=transfer.reason,
        transfer_type=transfer.transfer_type,
        requested_by_id=transfer.requested_by_id,
        notes=transfer.notes
    )
    db.add(db_transfer)
    db.commit()
    db.refresh(db_transfer)
    return db_transfer


def approve_room_transfer(
    db: Session,
    transfer_id: int,
    approval: RoomTransferApproval
) -> Optional[RoomTransfer]:
    """Approve or reject room transfer request"""
    transfer = get_room_transfer(db, transfer_id)
    if not transfer or transfer.status != "requested":
        return None

    if approval.approved:
        transfer.status = "approved"
        transfer.approved_by_id = approval.approved_by_id
        transfer.approved_at = datetime.now()
        transfer.approval_notes = approval.notes
    else:
        transfer.status = "cancelled"
        transfer.approval_notes = approval.notes

    db.commit()
    db.refresh(transfer)
    return transfer


def complete_room_transfer(
    db: Session,
    transfer_id: int,
    completed_by_id: int
) -> Optional[RoomTransfer]:
    """Complete room transfer and update admission"""
    transfer = get_room_transfer(db, transfer_id)
    if not transfer or transfer.status != "approved":
        return None

    # Update admission bed
    admission = get_admission(db, transfer.admission_id)
    if admission:
        admission.assigned_bed_id = transfer.to_bed_id
        admission.status = "transferred"

        # Create bed change history
        bed_change = BedChangeHistory(
            admission_id=transfer.admission_id,
            patient_id=transfer.patient_id,
            from_bed_id=transfer.from_bed_id,
            to_bed_id=transfer.to_bed_id,
            change_type="transfer",
            change_reason=transfer.reason,
            changed_by_id=completed_by_id
        )
        db.add(bed_change)

    # Update transfer
    transfer.status = "completed"
    transfer.completed_at = datetime.now()
    transfer.completed_by_id = completed_by_id

    db.commit()
    db.refresh(transfer)
    return transfer


def get_bed_change_history(
    db: Session,
    admission_id: Optional[int] = None,
    patient_id: Optional[int] = None
) -> List[BedChangeHistory]:
    """Get bed change history"""
    query = db.query(BedChangeHistory)

    if admission_id:
        query = query.filter(BedChangeHistory.admission_id == admission_id)
    if patient_id:
        query = query.filter(BedChangeHistory.patient_id == patient_id)

    return query.order_by(BedChangeHistory.changed_at.desc()).all()


# =============================================================================
# Admission Documentation CRUD
# =============================================================================

def get_admission_documentation(db: Session, admission_id: int) -> Optional[AdmissionDocumentation]:
    """Get admission documentation"""
    return db.query(AdmissionDocumentation).filter(
        AdmissionDocumentation.admission_id == admission_id
    ).first()


def upsert_admission_documentation(
    db: Session,
    documentation: AdmissionDocumentation
) -> AdmissionDocumentation:
    """Create or update admission documentation"""
    existing = get_admission_documentation(db, documentation.admission_id)

    if existing:
        # Update
        for field, value in documentation.model_dump(exclude_unset=True).items():
            if hasattr(existing, field):
                setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create
        import json
        db_doc = AdmissionDocumentation(
            admission_id=documentation.admission_id,
            admission_notes=documentation.admission_notes,
            allergies=json.dumps(documentation.allergies) if documentation.allergies else None,
            current_medications=json.dumps(documentation.current_medications) if documentation.current_medications else None,
            advance_directives=documentation.advance_directives,
            emergency_contact=documentation.emergency_contact,
            insurance_info=json.dumps(documentation.insurance_info) if documentation.insurance_info else None
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        return db_doc


# =============================================================================
# Discharge Readiness CRUD
# =============================================================================

def create_discharge_readiness_assessment(
    db: Session,
    assessment: DischargeReadinessSchema
) -> DischargeReadinessAssessment:
    """Create discharge readiness assessment"""
    import json
    db_assessment = DischargeReadinessAssessment(
        admission_id=assessment.admission_id,
        is_ready=assessment.is_ready,
        readiness_score=assessment.readiness_score,
        criteria_met=json.dumps(assessment.criteria_met) if assessment.criteria_met else None,
        criteria_not_met=json.dumps(assessment.criteria_not_met) if assessment.criteria_not_met else None,
        barriers_to_discharge=json.dumps(assessment.barriers_to_discharge) if assessment.barriers_to_discharge else None,
        required_follow_up=json.dumps(assessment.required_follow_up) if assessment.required_follow_up else None,
        assessed_by_id=assessment.assessed_by_id,
        notes=assessment.notes
    )
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


def get_latest_discharge_assessment(
    db: Session,
    admission_id: int
) -> Optional[DischargeReadinessAssessment]:
    """Get latest discharge readiness assessment for admission"""
    return db.query(DischargeReadinessAssessment).filter(
        DischargeReadinessAssessment.admission_id == admission_id
    ).order_by(DischargeReadinessAssessment.assessed_at.desc()).first()


# =============================================================================
# Admission Summary
# =============================================================================

def get_admission_summary(db: Session, admission_id: int) -> Optional[Dict]:
    """Get comprehensive admission summary"""
    admission = get_admission(db, admission_id)
    if not admission:
        return None

    # Calculate length of stay
    los_days = 0
    if admission.admission_date:
        end_date = admission.discharge_date or datetime.now()
        los_days = (end_date - admission.admission_date).days

    # Get latest discharge assessment
    latest_assessment = get_latest_discharge_assessment(db, admission_id)

    return {
        "admission_id": admission.id,
        "patient_id": admission.patient_id,
        "patient_name": admission.patient.full_name if admission.patient else None,
        "admission_type": admission.admission_type,
        "admission_date": admission.admission_date,
        "current_bed": {
            "bed_id": admission.assigned_bed_id,
            "bed_number": admission.assigned_bed.bed_number if admission.assigned_bed else None,
            "room_number": admission.assigned_bed.room_number if admission.assigned_bed else None,
            "room_class": admission.assigned_bed.room_class if admission.assigned_bed else None
        } if admission.assigned_bed else None,
        "attending_doctor": admission.doctor.full_name if admission.doctor else None,
        "current_status": admission.status,
        "length_of_stay_days": los_days,
        "estimated_discharge_date": admission.expected_discharge_date,
        "discharge_readiness_score": latest_assessment.readiness_score if latest_assessment else None
    }


def get_admission_statistics(db: Session) -> Dict:
    """Get admission statistics"""
    total = db.query(AdmissionOrder).count()
    active = db.query(AdmissionOrder).filter(
        AdmissionOrder.status == "admitted"
    ).count()
    pending = db.query(AdmissionOrder).filter(
        AdmissionOrder.status == "pending"
    ).count()
    discharged = db.query(AdmissionOrder).filter(
        AdmissionOrder.status == "discharged"
    ).count()

    return {
        "total_admissions": total,
        "active_admissions": active,
        "pending_admissions": pending,
        "discharged_today": discharged
    }
