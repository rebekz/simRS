"""Daily Care Documentation API Endpoints for STORY-022

This module provides REST API endpoints for:
- Nursing documentation (flow sheets, narrative notes, care plans)
- Physician progress notes (daily rounds, assessment and plan)
- Interdisciplinary notes (respiratory, physical therapy, nutrition, social work)
- Shift documentation (shift handoff, change of shift report)
- Digital signatures
- Auto-save functionality
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.daily_care import (
    NursingFlowSheetCreate, NursingFlowSheetResponse,
    NursingNarrativeNote, NursingCarePlan as NursingCarePlanSchema,
    PatientEducation as PatientEducationSchema,
    PhysicianDailyNote as PhysicianDailyNoteSchema,
    RespiratoryTherapyNote as RespiratoryTherapyNoteSchema,
    PhysicalTherapyNote as PhysicalTherapyNoteSchema,
    NutritionNote as NutritionNoteSchema,
    SocialWorkNote as SocialWorkNoteSchema,
    ShiftHandoff as ShiftHandoffSchema,
    ChangeOfShiftReport as ChangeOfShiftReportSchema,
    DigitalSignature as DigitalSignatureSchema,
    AutoSaveDraft as AutoSaveDraftSchema,
    DischargeSummaryExport as DischargeSummaryExportSchema,
    DocumentationListResponse, ShiftType
)
from app.crud import daily_care as crud
from app.models.daily_care import NursingFlowSheet


router = APIRouter()


# =============================================================================
# Nursing Flow Sheet Endpoints
# =============================================================================

@router.post("/flow-sheets", response_model=NursingFlowSheetResponse)
async def create_nursing_flow_sheet(
    obj_in: NursingFlowSheetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create nursing flow sheet (Lembar Observasi Keperawatan)"""
    # Verify user is a nurse
    if current_user.role not in ["nurse", "doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Only nurses can create flow sheets")

    flow_sheet = await crud.create_nursing_flow_sheet(db, obj_in, current_user.id)
    return flow_sheet


@router.get("/flow-sheets/{sheet_id}", response_model=NursingFlowSheetResponse)
async def get_nursing_flow_sheet(
    sheet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get nursing flow sheet by ID"""
    flow_sheet = await crud.get_nursing_flow_sheet(db, sheet_id)
    if not flow_sheet:
        raise HTTPException(status_code=404, detail="Flow sheet not found")
    return flow_sheet


@router.get("/admissions/{admission_id}/flow-sheets", response_model=List[NursingFlowSheetResponse])
async def get_nursing_flow_sheets(
    admission_id: int,
    shift_date: Optional[date] = None,
    shift_type: Optional[ShiftType] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get nursing flow sheets for admission"""
    flow_sheets = await crud.get_nursing_flow_sheets_by_admission(
        db, admission_id, shift_date, shift_type
    )
    return flow_sheets


@router.get("/admissions/{admission_id}/flow-sheets/latest", response_model=NursingFlowSheetResponse)
async def get_latest_nursing_flow_sheet(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get latest nursing flow sheet for admission"""
    flow_sheet = await crud.get_latest_nursing_flow_sheet(db, admission_id)
    if not flow_sheet:
        raise HTTPException(status_code=404, detail="No flow sheets found")
    return flow_sheet


@router.put("/flow-sheets/{sheet_id}", response_model=NursingFlowSheetResponse)
async def update_nursing_flow_sheet(
    sheet_id: int,
    obj_in: dict,
    auto_saved: bool = Query(False, description="True if auto-saved"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update nursing flow sheet"""
    # Verify user created this flow sheet
    existing = await crud.get_nursing_flow_sheet(db, sheet_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Flow sheet not found")
    if existing.nurse_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Can only update your own flow sheets")

    flow_sheet = await crud.update_nursing_flow_sheet(db, sheet_id, obj_in, auto_saved)
    return flow_sheet


# =============================================================================
# Nursing Narrative Endpoints
# =============================================================================

@router.post("/narratives", response_model=dict)
async def create_nursing_narrative(
    obj_in: NursingNarrativeNote,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create nursing narrative note (Catatan Keperawatan Naratif)"""
    # Verify user is a nurse
    if current_user.role not in ["nurse", "doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Only nurses can create narrative notes")

    narrative = await crud.create_nursing_narrative(db, obj_in)
    return {"id": narrative.id, "created_at": narrative.created_at}


@router.get("/admissions/{admission_id}/narratives", response_model=List[dict])
async def get_nursing_narratives(
    admission_id: int,
    note_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get nursing narratives for admission"""
    narratives = await crud.get_nursing_narratives(db, admission_id, note_type, limit)
    return [
        {
            "id": n.id,
            "note_type": n.note_type,
            "content": n.content,
            "is_confidential": n.is_confidential,
            "nurse_id": n.nurse_id,
            "created_at": n.created_at,
            "signed_at": n.signed_at
        }
        for n in narratives
    ]


@router.post("/narratives/{narrative_id}/sign", response_model=dict)
async def sign_nursing_narrative(
    narrative_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sign nursing narrative note"""
    narrative = await crud.sign_nursing_narrative(db, narrative_id, current_user.id)
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    return {"signed": True, "signed_at": narrative.signed_at}


# =============================================================================
# Nursing Care Plan Endpoints
# =============================================================================

@router.post("/care-plans", response_model=dict)
async def create_nursing_care_plan(
    obj_in: NursingCarePlanSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create nursing care plan (Rencana Asuhan Keperawatan)"""
    # Verify user is a nurse
    if current_user.role not in ["nurse", "doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Only nurses can create care plans")

    care_plan = await crud.create_nursing_care_plan(db, obj_in)
    return {"id": care_plan.id, "created_at": care_plan.created_at}


@router.get("/admissions/{admission_id}/care-plans", response_model=List[dict])
async def get_nursing_care_plans(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get nursing care plans for admission"""
    care_plans = await crud.get_nursing_care_plans(db, admission_id)
    return [
        {
            "id": cp.id,
            "nursing_diagnosis": cp.nursing_diagnosis,
            "goals": cp.goals,
            "effective_date": cp.effective_date,
            "evaluation": cp.evaluation,
            "outcome_achieved": cp.outcome_achieved
        }
        for cp in care_plans
    ]


@router.put("/care-plans/{plan_id}", response_model=dict)
async def update_nursing_care_plan(
    plan_id: int,
    obj_in: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update nursing care plan"""
    care_plan = await crud.update_nursing_care_plan(db, plan_id, obj_in)
    if not care_plan:
        raise HTTPException(status_code=404, detail="Care plan not found")
    return {"updated": True}


# =============================================================================
# Patient Education Endpoints
# =============================================================================

@router.post("/patient-education", response_model=dict)
async def create_patient_education(
    obj_in: PatientEducationSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create patient education record"""
    # Verify user is a nurse or doctor
    if current_user.role not in ["nurse", "doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Only clinical staff can create education records")

    education = await crud.create_patient_education(db, obj_in)
    return {"id": education.id, "created_at": education.created_at}


@router.get("/admissions/{admission_id}/education", response_model=List[dict])
async def get_patient_education_records(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get patient education records for admission"""
    records = await crud.get_patient_education_records(db, admission_id)
    return [
        {
            "id": r.id,
            "education_topic": r.education_topic,
            "teaching_method": r.teaching_method,
            "patient_understanding": r.patient_understanding,
            "follow_up_required": r.follow_up_required,
            "created_at": r.created_at
        }
        for r in records
    ]


# =============================================================================
# Physician Documentation Endpoints
# =============================================================================

@router.post("/physician-daily-notes", response_model=dict)
async def create_physician_daily_note(
    obj_in: PhysicianDailyNoteSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create physician daily progress note (Catatan Harian Dokter)"""
    # Verify user is a doctor
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Only doctors can create physician notes")

    note = await crud.create_physician_daily_note(db, obj_in)
    return {"id": note.id, "created_at": note.created_at}


@router.get("/admissions/{admission_id}/physician-notes", response_model=List[dict])
async def get_physician_daily_notes(
    admission_id: int,
    note_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get physician daily notes for admission"""
    notes = await crud.get_physician_daily_notes(db, admission_id, note_date)
    return [
        {
            "id": n.id,
            "note_date": n.note_date,
            "subjective": n.subjective,
            "objective": n.objective,
            "assessment": n.assessment,
            "plan": n.plan,
            "primary_diagnosis": n.primary_diagnosis,
            "signed_at": n.signed_at
        }
        for n in notes
    ]


@router.get("/admissions/{admission_id}/physician-notes/latest", response_model=dict)
async def get_latest_physician_note(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get latest physician daily note for admission"""
    notes = await crud.get_physician_daily_notes(db, admission_id)
    if not notes:
        raise HTTPException(status_code=404, detail="No physician notes found")
    note = notes[0]
    return {
        "id": note.id,
        "note_date": note.note_date,
        "subjective": note.subjective,
        "objective": note.objective,
        "assessment": note.assessment,
        "plan": note.plan,
        "primary_diagnosis": note.primary_diagnosis,
        "signed_at": note.signed_at
    }


# =============================================================================
# Interdisciplinary Documentation Endpoints
# =============================================================================

@router.post("/respiratory-therapy-notes", response_model=dict)
async def create_respiratory_therapy_note(
    obj_in: RespiratoryTherapyNoteSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create respiratory therapy note"""
    note = await crud.create_respiratory_therapy_note(db, obj_in)
    return {"id": note.id, "created_at": note.created_at}


@router.get("/admissions/{admission_id}/respiratory-notes", response_model=List[dict])
async def get_respiratory_therapy_notes(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get respiratory therapy notes for admission"""
    notes = await crud.get_respiratory_therapy_notes(db, admission_id)
    return [
        {
            "id": n.id,
            "note_date": n.note_date,
            "therapy_type": n.therapy_type,
            "intervention_provided": n.intervention_provided,
            "patient_response": n.patient_response
        }
        for n in notes
    ]


@router.post("/physical-therapy-notes", response_model=dict)
async def create_physical_therapy_note(
    obj_in: PhysicalTherapyNoteSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create physical therapy note"""
    note = await crud.create_physical_therapy_note(db, obj_in)
    return {"id": note.id, "created_at": note.created_at}


@router.get("/admissions/{admission_id}/physical-therapy-notes", response_model=List[dict])
async def get_physical_therapy_notes(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get physical therapy notes for admission"""
    notes = await crud.get_physical_therapy_notes(db, admission_id)
    return [
        {
            "id": n.id,
            "note_date": n.note_date,
            "therapy_type": n.therapy_type,
            "treatment_provided": n.treatment_provided,
            "progress_made": n.progress_made
        }
        for n in notes
    ]


@router.post("/nutrition-notes", response_model=dict)
async def create_nutrition_note(
    obj_in: NutritionNoteSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create nutrition/dietitian note"""
    note = await crud.create_nutrition_note(db, obj_in)
    return {"id": note.id, "created_at": note.created_at}


@router.get("/admissions/{admission_id}/nutrition-notes", response_model=List[dict])
async def get_nutrition_notes(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get nutrition notes for admission"""
    notes = await crud.get_nutrition_notes(db, admission_id)
    return [
        {
            "id": n.id,
            "note_date": n.note_date,
            "diet_type": n.diet_type,
            "nutritional_assessment": n.nutritional_assessment,
            "recommendations": n.recommendations
        }
        for n in notes
    ]


@router.post("/social-work-notes", response_model=dict)
async def create_social_work_note(
    obj_in: SocialWorkNoteSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create social work note"""
    note = await crud.create_social_work_note(db, obj_in)
    return {"id": note.id, "created_at": note.created_at}


@router.get("/admissions/{admission_id}/social-work-notes", response_model=List[dict])
async def get_social_work_notes(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get social work notes for admission"""
    notes = await crud.get_social_work_notes(db, admission_id)
    return [
        {
            "id": n.id,
            "note_date": n.note_date,
            "psychosocial_assessment": n.psychosocial_assessment,
            "discharge_planning": n.discharge_planning,
            "referrals_made": n.referrals_made
        }
        for n in notes
    ]


# =============================================================================
# Shift Documentation Endpoints
# =============================================================================

@router.post("/shift-handoffs", response_model=dict)
async def create_shift_handoff(
    obj_in: ShiftHandoffSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create shift handoff documentation (Serah Terima Shift)"""
    handoff = await crud.create_shift_handoff(db, obj_in)
    return {"id": handoff.id, "created_at": handoff.created_at}


@router.get("/admissions/{admission_id}/shift-handoffs", response_model=List[dict])
async def get_shift_handoffs(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get shift handoffs for admission"""
    handoffs = await crud.get_shift_handoffs(db, admission_id)
    return [
        {
            "id": h.id,
            "from_shift": h.from_shift,
            "to_shift": h.to_shift,
            "handoff_date": h.handoff_date,
            "handoff_time": h.handoff_time,
            "patient_status_summary": h.patient_status_summary,
            "verified": h.verified_by_receiving_nurse
        }
        for h in handoffs
    ]


@router.post("/shift-handoffs/{handoff_id}/verify", response_model=dict)
async def verify_shift_handoff(
    handoff_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify shift handoff by receiving nurse"""
    handoff = await crud.verify_shift_handoff(db, handoff_id)
    if not handoff:
        raise HTTPException(status_code=404, detail="Handoff not found")
    return {"verified": True}


@router.post("/change-of-shift-reports", response_model=dict)
async def create_change_of_shift_report(
    obj_in: ChangeOfShiftReportSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create change of shift report (Laporan Ganti Shift)"""
    report = await crud.create_change_of_shift_report(db, obj_in)
    return {"id": report.id, "created_at": report.created_at}


@router.get("/wards/{ward_id}/change-of-shift-reports", response_model=List[dict])
async def get_change_of_shift_reports(
    ward_id: int,
    shift_date: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get change of shift reports for ward and date"""
    reports = await crud.get_change_of_shift_reports(db, ward_id, shift_date)
    return [
        {
            "id": r.id,
            "shift_type": r.shift_type,
            "total_patients": r.total_patients,
            "critical_patients": r.critical_patient_list,
            "incidents_reported": r.incidents_reported,
            "verified": r.verified_by_supervisor
        }
        for r in reports
    ]


@router.post("/change-of-shift-reports/{report_id}/verify", response_model=dict)
async def verify_change_of_shift_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify change of shift report by supervisor"""
    report = await crud.verify_change_of_shift_report(db, report_id, current_user.id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"verified": True, "verified_at": report.verified_at}


# =============================================================================
# Digital Signature Endpoints
# =============================================================================

@router.post("/signatures", response_model=dict)
async def create_digital_signature(
    obj_in: DigitalSignatureSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create digital signature for document"""
    # Verify signer is the current user
    if obj_in.signer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only sign for yourself")

    signature = await crud.create_digital_signature(db, obj_in)
    return {"id": signature.id, "signed_at": signature.signed_at}


@router.get("/documents/{document_id}/signatures", response_model=List[dict])
async def get_document_signatures(
    document_id: int,
    document_type: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get signatures for document"""
    signatures = await crud.get_document_signatures(db, document_id, document_type)
    return [
        {
            "id": s.id,
            "signer_id": s.signer_id,
            "signed_at": s.signed_at,
            "ip_address": s.ip_address
        }
        for s in signatures
    ]


# =============================================================================
# Auto-save Draft Endpoints
# =============================================================================

@router.post("/drafts", response_model=dict)
async def save_draft(
    obj_in: AutoSaveDraftSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save or update auto-save draft"""
    # Verify user owns this draft
    if obj_in.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only save drafts for yourself")

    draft = await crud.save_draft(db, obj_in)
    return {"id": draft.id, "last_saved": draft.last_saved}


@router.get("/drafts/{document_type}/{admission_id}", response_model=dict)
async def get_draft(
    document_type: str,
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get auto-save draft for document"""
    draft = await crud.get_draft(db, document_type, admission_id, current_user.id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return {
        "id": draft.id,
        "draft_content": draft.draft_content,
        "last_saved": draft.last_saved
    }


@router.delete("/drafts/{draft_id}", response_model=dict)
async def delete_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete auto-save draft"""
    deleted = await crud.delete_draft(db, draft_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Draft not found")
    return {"deleted": True}


@router.get("/drafts", response_model=List[dict])
async def get_user_drafts(
    admission_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all drafts for current user"""
    drafts = await crud.get_user_drafts(db, current_user.id, admission_id)
    return [
        {
            "id": d.id,
            "document_type": d.document_type,
            "admission_id": d.admission_id,
            "last_saved": d.last_saved
        }
        for d in drafts
    ]


# =============================================================================
# Documentation Summary Endpoints
# =============================================================================

@router.get("/admissions/{admission_id}/summary", response_model=DocumentationListResponse)
async def get_documentation_summary(
    admission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get summary of all documentation for admission"""
    from app.crud.admission import get_admission_order

    admission = await get_admission_order(db, admission_id)
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")

    summary = await crud.get_documentation_summary(db, admission_id)

    return DocumentationListResponse(
        admission_id=admission_id,
        patient_id=admission.patient_id,
        patient_name="",  # Would need to join with patients table
        total_notes=summary["total_notes"],
        nursing_notes=summary["nursing_notes"],
        physician_notes=summary["physician_notes"],
        therapy_notes=summary["therapy_notes"],
        shift_notes=summary["shift_notes"],
        recent_notes=[]
    )
