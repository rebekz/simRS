"""Discharge Planning API Endpoints for STORY-023

This module provides REST API endpoints for:
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
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.discharge import (
    DischargeReadinessAssessment, DischargeReadinessResponse,
    DischargeOrder as DischargeOrderSchema, DischargeOrderResponse,
    DischargeSummary as DischargeSummarySchema, DischargeSummaryResponse,
    MedicationReconciliation as MedicationReconciliationSchema,
    FollowUpAppointment as FollowUpAppointmentSchema, FollowUpAppointmentResponse,
    BPJSClaimFinalization as BPJSClaimFinalizationSchema,
    SEPClosure as SEPClosureSchema, SEPClosureResponse,
    PatientDischargeInstructions as PatientDischargeInstructionsSchema,
    DischargeChecklist as DischargeChecklistSchema
)
from app.crud import discharge as crud


router = APIRouter()


# =============================================================================
# Discharge Readiness Assessment Endpoints
# =============================================================================

@router.post("/readiness", response_model=DischargeReadinessResponse)
async def create_discharge_readiness(
    obj_in: DischargeReadinessAssessment,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create discharge readiness assessment"""
    # Verify user is clinical staff
    if current_user.role not in ["doctor", "nurse", "admin"]:
        raise HTTPException(status_code=403, detail="Only clinical staff can assess readiness")

    readiness = await crud.create_discharge_readiness(db, obj_in)
    return readiness


@router.get("/admissions/{admission_id}/readiness", response_model=DischargeReadinessResponse)
async def get_discharge_readiness(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get discharge readiness assessment for admission"""
    readiness = await crud.get_discharge_readiness(db, admission_id)
    if not readiness:
        raise HTTPException(status_code=404, detail="Readiness assessment not found")
    return readiness


@router.put("/readiness/{readiness_id}", response_model=DischargeReadinessResponse)
async def update_discharge_readiness(
    readiness_id: int,
    obj_in: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update discharge readiness assessment"""
    readiness = await crud.update_discharge_readiness(db, readiness_id, obj_in)
    if not readiness:
        raise HTTPException(status_code=404, detail="Readiness assessment not found")
    return readiness


# =============================================================================
# Discharge Orders Endpoints
# =============================================================================

@router.post("/orders", response_model=DischargeOrderResponse)
async def create_discharge_order(
    obj_in: DischargeOrderSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create discharge order (Dokter Only)"""
    # Verify user is a doctor
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Only doctors can create discharge orders")

    order = await crud.create_discharge_order(db, obj_in)
    return order


@router.get("/admissions/{admission_id}/orders", response_model=DischargeOrderResponse)
async def get_discharge_order(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get discharge order for admission"""
    order = await crud.get_discharge_order(db, admission_id)
    if not order:
        raise HTTPException(status_code=404, detail="Discharge order not found")
    return order


@router.put("/orders/{order_id}", response_model=DischargeOrderResponse)
async def update_discharge_order(
    order_id: int,
    obj_in: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update discharge order"""
    order = await crud.update_discharge_order(db, order_id, obj_in)
    if not order:
        raise HTTPException(status_code=404, detail="Discharge order not found")
    return order


@router.post("/admissions/{admission_id}/complete-discharge", response_model=dict)
async def complete_discharge(
    admission_id: int,
    actual_discharge_date: datetime = Query(default_factory=datetime.now),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Complete discharge process"""
    # Verify user is a doctor
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Only doctors can complete discharge")

    order = await crud.complete_discharge(db, admission_id, actual_discharge_date)
    if not order:
        raise HTTPException(status_code=404, detail="Discharge order not found")
    return {"discharged": True, "discharge_date": actual_discharge_date}


# =============================================================================
# Discharge Summary Endpoints
# =============================================================================

@router.post("/summaries", response_model=DischargeSummaryResponse)
async def create_discharge_summary(
    obj_in: DischargeSummarySchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate discharge summary"""
    summary = await crud.create_discharge_summary(db, obj_in)
    return summary


@router.get("/admissions/{admission_id}/summaries", response_model=DischargeSummaryResponse)
async def get_discharge_summary(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get discharge summary for admission"""
    summary = await crud.get_discharge_summary(db, admission_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Discharge summary not found")
    return summary


@router.put("/summaries/{summary_id}/file", response_model=dict)
async def update_discharge_summary_file(
    summary_id: int,
    file_url: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update discharge summary with generated file URL"""
    summary = await crud.update_discharge_summary_file(db, summary_id, file_url)
    if not summary:
        raise HTTPException(status_code=404, detail="Discharge summary not found")
    return {"file_url": file_url}


# =============================================================================
# Medication Reconciliation Endpoints
# =============================================================================

@router.post("/medication-reconciliation", response_model=dict)
async def create_medication_reconciliation(
    obj_in: MedicationReconciliationSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create medication reconciliation (Apoteker Only)"""
    # Verify user is pharmacist or doctor
    if current_user.role not in ["pharmacist", "doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Only pharmacists or doctors can create reconciliation")

    reconciliation = await crud.create_medication_reconciliation(db, obj_in)
    return {"id": reconciliation.id, "reconciliation_date": reconciliation.reconciliation_date}


@router.get("/admissions/{admission_id}/medication-reconciliation", response_model=dict)
async def get_medication_reconciliation(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get medication reconciliation for admission"""
    reconciliation = await crud.get_medication_reconciliation(db, admission_id)
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Medication reconciliation not found")

    return {
        "id": reconciliation.id,
        "reconciliation_date": reconciliation.reconciliation_date,
        "medications_to_continue": reconciliation.medications_to_continue,
        "medications_to_discontinue": reconciliation.medications_to_discontinue,
        "medications_to_change": reconciliation.medications_to_change,
        "new_medications": reconciliation.new_medications,
        "verified_by_physician": reconciliation.verified_by_physician,
        "verified_at": reconciliation.verified_at
    }


@router.post("/medication-reconciliation/{reconciliation_id}/verify", response_model=dict)
async def verify_medication_reconciliation(
    reconciliation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify medication reconciliation (Dokter Only)"""
    # Verify user is a doctor
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Only doctors can verify reconciliation")

    reconciliation = await crud.verify_medication_reconciliation(db, reconciliation_id, current_user.id)
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Medication reconciliation not found")
    return {"verified": True, "verified_at": reconciliation.verified_at}


# =============================================================================
# Follow-up Appointment Endpoints
# =============================================================================

@router.post("/follow-up-appointments", response_model=FollowUpAppointmentResponse)
async def create_follow_up_appointment(
    obj_in: FollowUpAppointmentSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create follow-up appointment"""
    appointment = await crud.create_follow_up_appointment(db, obj_in)
    return appointment


@router.get("/admissions/{admission_id}/follow-up-appointments", response_model=List[FollowUpAppointmentResponse])
async def get_follow_up_appointments(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get follow-up appointments for admission"""
    appointments = await crud.get_follow_up_appointments(db, admission_id)
    return appointments


@router.get("/patients/{patient_id}/upcoming-appointments", response_model=List[FollowUpAppointmentResponse])
async def get_upcoming_appointments(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get upcoming follow-up appointments for patient"""
    appointments = await crud.get_upcoming_appointments(db, patient_id)
    return appointments


@router.post("/follow-up-appointments/{appointment_id}/confirm", response_model=dict)
async def confirm_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Confirm follow-up appointment"""
    appointment = await crud.confirm_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"confirmed": True, "confirmed_at": appointment.confirmed_at}


# =============================================================================
# BPJS Claim Finalization Endpoints
# =============================================================================

@router.post("/bpjs-claims", response_model=dict)
async def create_bpjs_claim_finalization(
    obj_in: BPJSClaimFinalizationSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create BPJS claim finalization"""
    claim = await crud.create_bpjs_claim_finalization(db, obj_in)
    return {
        "id": claim.id,
        "sep_number": claim.sep_number,
        "total_claim_amount": claim.total_claim_amount
    }


@router.get("/admissions/{admission_id}/bpjs-claims", response_model=dict)
async def get_bpjs_claim_finalization(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get BPJS claim finalization for admission"""
    claim = await crud.get_bpjs_claim_finalization(db, admission_id)
    if not claim:
        raise HTTPException(status_code=404, detail="BPJS claim not found")

    return {
        "id": claim.id,
        "sep_number": claim.sep_number,
        "final_diagnosis": claim.final_diagnosis,
        "total_claim_amount": claim.total_claim_amount,
        "claim_status": claim.claim_status,
        "submitted_to_bpjs": claim.submitted_to_bpjs,
        "submitted_at": claim.submitted_at
    }


@router.post("/bpjs-claims/{claim_id}/validate", response_model=dict)
async def validate_bpjs_claim(
    claim_id: int,
    validation_notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Validate BPJS claim"""
    claim = await crud.validate_bpjs_claim(db, claim_id, current_user.id, validation_notes)
    if not claim:
        raise HTTPException(status_code=404, detail="BPJS claim not found")
    return {"validated": True, "validated_at": claim.validated_at}


@router.post("/bpjs-claims/{claim_id}/submit", response_model=dict)
async def submit_bpjs_claim(
    claim_id: int,
    submission_number: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit BPJS claim"""
    claim = await crud.submit_bpjs_claim(db, claim_id, submission_number)
    if not claim:
        raise HTTPException(status_code=404, detail="BPJS claim not found")
    return {
        "submitted": True,
        "submitted_at": claim.submitted_at,
        "submission_number": submission_number
    }


# =============================================================================
# SEP Closure Endpoints
# =============================================================================

@router.post("/sep-closures", response_model=SEPClosureResponse)
async def create_sep_closure(
    obj_in: SEPClosureSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create SEP closure"""
    closure = await crud.create_sep_closure(db, obj_in)
    return closure


@router.get("/admissions/{admission_id}/sep-closures", response_model=SEPClosureResponse)
async def get_sep_closure(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get SEP closure for admission"""
    closure = await crud.get_sep_closure(db, admission_id)
    if not closure:
        raise HTTPException(status_code=404, detail="SEP closure not found")
    return closure


@router.post("/sep-closures/{closure_id}/close", response_model=dict)
async def close_sep(
    closure_id: int,
    sep_update_response: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Close SEP"""
    closure = await crud.close_sep(db, closure_id, current_user.id, sep_update_response)
    if not closure:
        raise HTTPException(status_code=404, detail="SEP closure not found")
    return {
        "closed": True,
        "closed_at": closure.closed_at,
        "sep_updated": closure.sep_updated
    }


# =============================================================================
# Patient Discharge Instructions Endpoints
# =============================================================================

@router.post("/patient-instructions", response_model=dict)
async def create_patient_discharge_instructions(
    obj_in: PatientDischargeInstructionsSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create patient discharge instructions"""
    instructions = await crud.create_patient_discharge_instructions(db, obj_in)
    return {
        "id": instructions.id,
        "language": instructions.language,
        "delivery_method": instructions.delivery_method
    }


@router.get("/admissions/{admission_id}/patient-instructions", response_model=dict)
async def get_patient_discharge_instructions(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get patient discharge instructions for admission"""
    instructions = await crud.get_patient_discharge_instructions(db, admission_id)
    if not instructions:
        raise HTTPException(status_code=404, detail="Patient instructions not found")

    return {
        "id": instructions.id,
        "summary": instructions.summary,
        "diagnoses": instructions.diagnoses,
        "medications": instructions.medications,
        "activity_instructions": instructions.activity_instructions,
        "diet_instructions": instructions.diet_instructions,
        "warning_signs": instructions.warning_signs,
        "follow_up_appointments": instructions.follow_up_appointments,
        "emergency_contact": instructions.emergency_contact,
        "hospital_contact": instructions.hospital_contact
    }


# =============================================================================
# Discharge Checklist Endpoints
# =============================================================================

@router.post("/checklists", response_model=dict)
async def create_discharge_checklist(
    obj_in: DischargeChecklistSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create discharge checklist"""
    checklist = await crud.create_discharge_checklist(db, obj_in)
    return {
        "id": checklist.id,
        "all_criteria_met": checklist.all_criteria_met
    }


@router.get("/admissions/{admission_id}/checklists", response_model=dict)
async def get_discharge_checklist(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get discharge checklist for admission"""
    checklist = await crud.get_discharge_checklist(db, admission_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Discharge checklist not found")

    return {
        "id": checklist.id,
        "clinical_criteria": checklist.clinical_criteria,
        "medication_criteria": checklist.medication_criteria,
        "documentation_criteria": checklist.documentation_criteria,
        "logistics_criteria": checklist.logistics_criteria,
        "education_criteria": checklist.education_criteria,
        "follow_up_criteria": checklist.follow_up_criteria,
        "all_criteria_met": checklist.all_criteria_met,
        "verified_by_id": checklist.verified_by_id,
        "verified_at": checklist.verified_at
    }


@router.put("/checklists/{checklist_id}/items/{category}/{item_index}", response_model=dict)
async def update_checklist_item(
    checklist_id: int,
    category: str,
    item_index: int,
    completed: bool,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update discharge checklist item"""
    checklist = await crud.update_checklist_item(
        db, checklist_id, category, item_index, completed, current_user.id, notes
    )
    if not checklist:
        raise HTTPException(status_code=404, detail="Discharge checklist not found")
    return {
        "updated": True,
        "all_criteria_met": checklist.all_criteria_met,
        "verified_at": checklist.verified_at
    }


@router.post("/checklists/{checklist_id}/verify", response_model=dict)
async def verify_discharge_checklist(
    checklist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify discharge checklist"""
    checklist = await crud.verify_discharge_checklist(db, checklist_id, current_user.id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Discharge checklist not found")
    return {
        "verified": True,
        "verified_at": checklist.verified_at,
        "all_criteria_met": checklist.all_criteria_met
    }


# =============================================================================
# Discharge Summary Overview
# =============================================================================

@router.get("/admissions/{admission_id}/summary", response_model=dict)
async def get_discharge_summary_overview(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get complete discharge summary overview"""
    summary = await crud.get_discharge_summary_overview(db, admission_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Admission not found")
    return summary
