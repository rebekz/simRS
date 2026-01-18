"""Discharge Planning CRUD Operations for STORY-023

This module provides CRUD operations for:
- Discharge readiness assessment
- Discharge orders
- Discharge summary generation
- Medication reconciliation
- Follow-up appointment scheduling
- BPJS claim finalization
- SEP closure
- Discharge instructions
- Discharge checklist
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.discharge import (
    DischargeReadiness, DischargeOrder, DischargeSummary,
    DischargeMedicationReconciliation, FollowUpAppointment,
    BPJSClaimFinalization, SEPClosure,
    PatientDischargeInstructions, DischargeChecklist
)
from app.schemas.discharge import (
    DischargeReadinessAssessment, DischargeOrder as DischargeOrderSchema,
    DischargeSummary as DischargeSummarySchema,
    MedicationReconciliation as MedicationReconciliationSchema,
    FollowUpAppointment as FollowUpAppointmentSchema,
    BPJSClaimFinalization as BPJSClaimFinalizationSchema,
    SEPClosure as SEPClosureSchema,
    PatientDischargeInstructions as PatientDischargeInstructionsSchema,
    DischargeChecklist as DischargeChecklistSchema
)


# =============================================================================
# Discharge Readiness Assessment CRUD
# =============================================================================

async def create_discharge_readiness(
    db: AsyncSession,
    obj_in: DischargeReadinessAssessment
) -> DischargeReadiness:
    """Create discharge readiness assessment"""
    db_obj = DischargeReadiness(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_discharge_readiness(
    db: AsyncSession,
    admission_id: int
) -> Optional[DischargeReadiness]:
    """Get latest discharge readiness assessment for admission"""
    result = await db.execute(
        select(DischargeReadiness)
        .where(DischargeReadiness.admission_id == admission_id)
        .order_by(DischargeReadiness.assessed_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def update_discharge_readiness(
    db: AsyncSession,
    readiness_id: int,
    obj_in: Dict[str, Any]
) -> Optional[DischargeReadiness]:
    """Update discharge readiness assessment"""
    db_obj = await db.execute(
        select(DischargeReadiness).where(DischargeReadiness.id == readiness_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    for field, value in obj_in.items():
        setattr(db_obj, field, value)

    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# =============================================================================
# Discharge Orders CRUD
# =============================================================================

async def create_discharge_order(
    db: AsyncSession,
    obj_in: DischargeOrderSchema
) -> DischargeOrder:
    """Create discharge order"""
    db_obj = DischargeOrder(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_discharge_order(
    db: AsyncSession,
    admission_id: int
) -> Optional[DischargeOrder]:
    """Get discharge order for admission"""
    result = await db.execute(
        select(DischargeOrder)
        .where(DischargeOrder.admission_id == admission_id)
        .order_by(DischargeOrder.ordered_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def update_discharge_order(
    db: AsyncSession,
    order_id: int,
    obj_in: Dict[str, Any]
) -> Optional[DischargeOrder]:
    """Update discharge order"""
    db_obj = await db.execute(
        select(DischargeOrder).where(DischargeOrder.id == order_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    for field, value in obj_in.items():
        setattr(db_obj, field, value)

    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def complete_discharge(
    db: AsyncSession,
    admission_id: int,
    actual_discharge_date: datetime
) -> Optional[DischargeOrder]:
    """Complete discharge process"""
    db_obj = await get_discharge_order(db, admission_id)
    if not db_obj:
        return None

    db_obj.discharge_status = "discharged"
    db_obj.actual_discharge_date = actual_discharge_date
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# =============================================================================
# Discharge Summary CRUD
# =============================================================================

async def create_discharge_summary(
    db: AsyncSession,
    obj_in: DischargeSummarySchema
) -> DischargeSummary:
    """Create discharge summary"""
    db_obj = DischargeSummary(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_discharge_summary(
    db: AsyncSession,
    admission_id: int
) -> Optional[DischargeSummary]:
    """Get discharge summary for admission"""
    result = await db.execute(
        select(DischargeSummary).where(DischargeSummary.admission_id == admission_id)
    )
    return result.scalar_one_or_none()


async def update_discharge_summary_file(
    db: AsyncSession,
    summary_id: int,
    file_url: str
) -> Optional[DischargeSummary]:
    """Update discharge summary with generated file URL"""
    db_obj = await db.execute(
        select(DischargeSummary).where(DischargeSummary.id == summary_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    db_obj.file_url = file_url
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# =============================================================================
# Medication Reconciliation CRUD
# =============================================================================

async def create_medication_reconciliation(
    db: AsyncSession,
    obj_in: MedicationReconciliationSchema
) -> DischargeMedicationReconciliation:
    """Create medication reconciliation"""
    db_obj = DischargeMedicationReconciliation(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_medication_reconciliation(
    db: AsyncSession,
    admission_id: int
) -> Optional[DischargeMedicationReconciliation]:
    """Get medication reconciliation for admission"""
    result = await db.execute(
        select(DischargeMedicationReconciliation)
        .where(DischargeMedicationReconciliation.admission_id == admission_id)
        .order_by(DischargeMedicationReconciliation.reconciliation_date.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def verify_medication_reconciliation(
    db: AsyncSession,
    reconciliation_id: int,
    physician_id: int
) -> Optional[DischargeMedicationReconciliation]:
    """Verify medication reconciliation by physician"""
    db_obj = await db.execute(
        select(DischargeMedicationReconciliation).where(DischargeMedicationReconciliation.id == reconciliation_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    db_obj.verified_by_physician = True
    db_obj.verified_at = datetime.now()
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# =============================================================================
# Follow-up Appointment CRUD
# =============================================================================

async def create_follow_up_appointment(
    db: AsyncSession,
    obj_in: FollowUpAppointmentSchema
) -> FollowUpAppointment:
    """Create follow-up appointment"""
    db_obj = FollowUpAppointment(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_follow_up_appointments(
    db: AsyncSession,
    admission_id: int
) -> List[FollowUpAppointment]:
    """Get follow-up appointments for admission"""
    result = await db.execute(
        select(FollowUpAppointment)
        .where(FollowUpAppointment.admission_id == admission_id)
        .order_by(FollowUpAppointment.appointment_date, FollowUpAppointment.appointment_time)
    )
    return list(result.scalars().all())


async def get_upcoming_appointments(
    db: AsyncSession,
    patient_id: int
) -> List[FollowUpAppointment]:
    """Get upcoming follow-up appointments for patient"""
    result = await db.execute(
        select(FollowUpAppointment)
        .where(
            and_(
                FollowUpAppointment.patient_id == patient_id,
                FollowUpAppointment.appointment_date >= date.today()
            )
        )
        .order_by(FollowUpAppointment.appointment_date, FollowUpAppointment.appointment_time)
    )
    return list(result.scalars().all())


async def confirm_appointment(
    db: AsyncSession,
    appointment_id: int
) -> Optional[FollowUpAppointment]:
    """Confirm follow-up appointment"""
    db_obj = await db.execute(
        select(FollowUpAppointment).where(FollowUpAppointment.id == appointment_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    db_obj.confirmed = True
    db_obj.confirmed_at = datetime.now()
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# =============================================================================
# BPJS Claim Finalization CRUD
# =============================================================================

async def create_bpjs_claim_finalization(
    db: AsyncSession,
    obj_in: BPJSClaimFinalizationSchema
) -> BPJSClaimFinalization:
    """Create BPJS claim finalization"""
    db_obj = BPJSClaimFinalization(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_bpjs_claim_finalization(
    db: AsyncSession,
    admission_id: int
) -> Optional[BPJSClaimFinalization]:
    """Get BPJS claim finalization for admission"""
    result = await db.execute(
        select(BPJSClaimFinalization).where(BPJSClaimFinalization.admission_id == admission_id)
    )
    return result.scalar_one_or_none()


async def validate_bpjs_claim(
    db: AsyncSession,
    claim_id: int,
    validated_by: int,
    notes: Optional[str] = None
) -> Optional[BPJSClaimFinalization]:
    """Validate BPJS claim"""
    db_obj = await db.execute(
        select(BPJSClaimFinalization).where(BPJSClaimFinalization.id == claim_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    db_obj.validated_by = validated_by
    db_obj.validated_at = datetime.now()
    db_obj.validation_notes = notes
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def submit_bpjs_claim(
    db: AsyncSession,
    claim_id: int,
    submission_number: str
) -> Optional[BPJSClaimFinalization]:
    """Submit BPJS claim"""
    db_obj = await db.execute(
        select(BPJSClaimFinalization).where(BPJSClaimFinalization.id == claim_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    db_obj.submitted_to_bpjs = True
    db_obj.submitted_at = datetime.now()
    db_obj.claim_submission_number = submission_number
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# =============================================================================
# SEP Closure CRUD
# =============================================================================

async def create_sep_closure(
    db: AsyncSession,
    obj_in: SEPClosureSchema
) -> SEPClosure:
    """Create SEP closure"""
    db_obj = SEPClosure(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_sep_closure(
    db: AsyncSession,
    admission_id: int
) -> Optional[SEPClosure]:
    """Get SEP closure for admission"""
    result = await db.execute(
        select(SEPClosure).where(SEPClosure.admission_id == admission_id)
    )
    return result.scalar_one_or_none()


async def close_sep(
    db: AsyncSession,
    closure_id: int,
    closed_by_id: int,
    sep_update_response: Optional[Dict[str, Any]] = None
) -> Optional[SEPClosure]:
    """Close SEP"""
    db_obj = await db.execute(
        select(SEPClosure).where(SEPClosure.id == closure_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    db_obj.closed_by_id = closed_by_id
    db_obj.closed_at = datetime.now()
    db_obj.sep_updated = True
    db_obj.sep_update_response = sep_update_response
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# =============================================================================
# Patient Discharge Instructions CRUD
# =============================================================================

async def create_patient_discharge_instructions(
    db: AsyncSession,
    obj_in: PatientDischargeInstructionsSchema
) -> PatientDischargeInstructions:
    """Create patient discharge instructions"""
    db_obj = PatientDischargeInstructions(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_patient_discharge_instructions(
    db: AsyncSession,
    admission_id: int
) -> Optional[PatientDischargeInstructions]:
    """Get patient discharge instructions for admission"""
    result = await db.execute(
        select(PatientDischargeInstructions).where(PatientDischargeInstructions.admission_id == admission_id)
    )
    return result.scalar_one_or_none()


# =============================================================================
# Discharge Checklist CRUD
# =============================================================================

async def create_discharge_checklist(
    db: AsyncSession,
    obj_in: DischargeChecklistSchema
) -> DischargeChecklist:
    """Create discharge checklist"""
    db_obj = DischargeChecklist(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_discharge_checklist(
    db: AsyncSession,
    admission_id: int
) -> Optional[DischargeChecklist]:
    """Get discharge checklist for admission"""
    result = await db.execute(
        select(DischargeChecklist).where(DischargeChecklist.admission_id == admission_id)
    )
    return result.scalar_one_or_none()


async def update_checklist_item(
    db: AsyncSession,
    checklist_id: int,
    category: str,
    item_index: int,
    completed: bool,
    completed_by_id: int,
    notes: Optional[str] = None
) -> Optional[DischargeChecklist]:
    """Update discharge checklist item"""
    db_obj = await db.execute(
        select(DischargeChecklist).where(DischargeChecklist.id == checklist_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    # Get the category items
    category_items = getattr(db_obj, f"{category}_criteria")
    if item_index >= len(category_items):
        return None

    # Update the item
    category_items[item_index]["completed"] = completed
    category_items[item_index]["completed_by_id"] = completed_by_id
    category_items[item_index]["completed_at"] = datetime.now().isoformat()
    if notes:
        category_items[item_index]["notes"] = notes

    setattr(db_obj, f"{category}_criteria", category_items)

    # Check if all criteria are met
    all_items = []
    for cat in ["clinical", "medication", "documentation", "logistics", "education", "follow_up"]:
        all_items.extend(getattr(db_obj, f"{cat}_criteria"))

    db_obj.all_criteria_met = all(item.get("completed", False) for item in all_items)

    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def verify_discharge_checklist(
    db: AsyncSession,
    checklist_id: int,
    verified_by_id: int
) -> Optional[DischargeChecklist]:
    """Verify discharge checklist"""
    db_obj = await db.execute(
        select(DischargeChecklist).where(DischargeChecklist.id == checklist_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    db_obj.verified_by_id = verified_by_id
    db_obj.verified_at = datetime.now()
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# =============================================================================
# Discharge Summary
# =============================================================================

async def get_discharge_summary_overview(
    db: AsyncSession,
    admission_id: int
) -> Optional[Dict[str, Any]]:
    """Get complete discharge summary overview"""
    # Get discharge order
    discharge_order = await get_discharge_order(db, admission_id)

    # Get discharge readiness
    readiness = await get_discharge_readiness(db, admission_id)

    # Get medication reconciliation
    reconciliation = await get_medication_reconciliation(db, admission_id)

    # Get follow-up appointments
    appointments = await get_follow_up_appointments(db, admission_id)

    # Get BPJS claim
    bpjs_claim = await get_bpjs_claim_finalization(db, admission_id)

    # Get SEP closure
    sep_closure = await get_sep_closure(db, admission_id)

    return {
        "admission_id": admission_id,
        "discharge_order": {
            "status": discharge_order.discharge_status if discharge_order else None,
            "destination": discharge_order.discharge_destination if discharge_order else None,
            "condition": discharge_order.discharge_condition if discharge_order else None,
            "estimated_date": discharge_order.estimated_discharge_date if discharge_order else None,
            "actual_date": discharge_order.actual_discharge_date if discharge_order else None,
        },
        "readiness": {
            "is_ready": readiness.is_ready if readiness else None,
            "readiness_score": readiness.readiness_score if readiness else None,
            "barriers": readiness.barriers_to_discharge if readiness else None,
        },
        "medication_reconciliation": {
            "completed": reconciliation.verified_by_physician if reconciliation else None,
            "reconciliation_date": reconciliation.reconciliation_date if reconciliation else None,
        },
        "follow_up_appointments": [
            {
                "date": appt.appointment_date,
                "time": appt.appointment_time,
                "specialty": appt.specialty,
                "type": appt.appointment_type,
                "confirmed": appt.confirmed,
            }
            for appt in appointments
        ],
        "bpjs_claim": {
            "submitted": bpjs_claim.submitted_to_bpjs if bpjs_claim else None,
            "claim_status": bpjs_claim.claim_status if bpjs_claim else None,
            "total_amount": bpjs_claim.total_claim_amount if bpjs_claim else None,
        },
        "sep_closure": {
            "closed": sep_closure.sep_updated if sep_closure else None,
            "closed_at": sep_closure.closed_at if sep_closure else None,
        },
    }
