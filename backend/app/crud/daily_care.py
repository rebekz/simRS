"""Daily Care Documentation CRUD Operations for STORY-022

This module provides CRUD operations for:
- Nursing documentation (flow sheets, narrative notes, care plans)
- Physician progress notes (daily rounds, assessment and plan)
- Interdisciplinary notes (respiratory, physical therapy, nutrition, social work)
- Shift documentation (shift handoff, change of shift report)
- Digital signatures
- Auto-save functionality
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_care import (
    NursingFlowSheet, NursingNarrative, NursingCarePlan, PatientEducation,
    PhysicianDailyNote, RespiratoryTherapyNote, PhysicalTherapyNote,
    NutritionNote, SocialWorkNote, ShiftHandoff, ChangeOfShiftReport,
    DigitalSignature, AutoSaveDraft, DischargeSummaryExport
)
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
    DischargeSummaryExport as DischargeSummaryExportSchema
)


# =============================================================================
# Nursing Documentation CRUD
# =============================================================================

async def create_nursing_flow_sheet(
    db: AsyncSession,
    obj_in: NursingFlowSheetCreate,
    nurse_id: int
) -> NursingFlowSheet:
    """Create nursing flow sheet entry"""
    db_obj = NursingFlowSheet(**obj_in.model_dump(), nurse_id=nurse_id)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_nursing_flow_sheet(
    db: AsyncSession,
    sheet_id: int
) -> Optional[NursingFlowSheet]:
    """Get nursing flow sheet by ID"""
    result = await db.execute(
        select(NursingFlowSheet)
        .where(NursingFlowSheet.id == sheet_id)
    )
    return result.scalar_one_or_none()


async def get_nursing_flow_sheets_by_admission(
    db: AsyncSession,
    admission_id: int,
    shift_date: Optional[date] = None,
    shift_type: Optional[str] = None
) -> List[NursingFlowSheet]:
    """Get nursing flow sheets for admission with optional filters"""
    query = select(NursingFlowSheet).where(
        NursingFlowSheet.admission_id == admission_id
    )

    if shift_date:
        query = query.where(NursingFlowSheet.shift_date == shift_date)
    if shift_type:
        query = query.where(NursingFlowSheet.shift_type == shift_type)

    query = query.order_by(NursingFlowSheet.shift_date.desc(), NursingFlowSheet.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_latest_nursing_flow_sheet(
    db: AsyncSession,
    admission_id: int
) -> Optional[NursingFlowSheet]:
    """Get latest nursing flow sheet for admission"""
    result = await db.execute(
        select(NursingFlowSheet)
        .where(NursingFlowSheet.admission_id == admission_id)
        .order_by(NursingFlowSheet.shift_date.desc(), NursingFlowSheet.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def update_nursing_flow_sheet(
    db: AsyncSession,
    sheet_id: int,
    obj_in: Dict[str, Any],
    auto_saved: bool = False
) -> Optional[NursingFlowSheet]:
    """Update nursing flow sheet"""
    db_obj = await get_nursing_flow_sheet(db, sheet_id)
    if not db_obj:
        return None

    for field, value in obj_in.items():
        setattr(db_obj, field, value)

    db_obj.auto_saved = auto_saved
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def create_nursing_narrative(
    db: AsyncSession,
    obj_in: NursingNarrativeNote
) -> NursingNarrative:
    """Create nursing narrative note"""
    db_obj = NursingNarrative(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_nursing_narratives(
    db: AsyncSession,
    admission_id: int,
    note_type: Optional[str] = None,
    limit: int = 100
) -> List[NursingNarrative]:
    """Get nursing narratives for admission"""
    query = select(NursingNarrative).where(
        NursingNarrative.admission_id == admission_id
    )

    if note_type:
        query = query.where(NursingNarrative.note_type == note_type)

    query = query.order_by(NursingNarrative.created_at.desc()).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def sign_nursing_narrative(
    db: AsyncSession,
    narrative_id: int,
    signed_by_id: int
) -> Optional[NursingNarrative]:
    """Sign nursing narrative note"""
    db_obj = await db.execute(
        select(NursingNarrative).where(NursingNarrative.id == narrative_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    db_obj.signed_by_id = signed_by_id
    db_obj.signed_at = datetime.now()
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def create_nursing_care_plan(
    db: AsyncSession,
    obj_in: NursingCarePlanSchema
) -> NursingCarePlan:
    """Create nursing care plan"""
    db_obj = NursingCarePlan(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_nursing_care_plans(
    db: AsyncSession,
    admission_id: int
) -> List[NursingCarePlan]:
    """Get nursing care plans for admission"""
    result = await db.execute(
        select(NursingCarePlan)
        .where(NursingCarePlan.admission_id == admission_id)
        .order_by(NursingCarePlan.effective_date.desc())
    )
    return list(result.scalars().all())


async def update_nursing_care_plan(
    db: AsyncSession,
    plan_id: int,
    obj_in: Dict[str, Any]
) -> Optional[NursingCarePlan]:
    """Update nursing care plan"""
    db_obj = await db.execute(
        select(NursingCarePlan).where(NursingCarePlan.id == plan_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    for field, value in obj_in.items():
        setattr(db_obj, field, value)

    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def create_patient_education(
    db: AsyncSession,
    obj_in: PatientEducationSchema
) -> PatientEducation:
    """Create patient education record"""
    db_obj = PatientEducation(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_patient_education_records(
    db: AsyncSession,
    admission_id: int
) -> List[PatientEducation]:
    """Get patient education records for admission"""
    result = await db.execute(
        select(PatientEducation)
        .where(PatientEducation.admission_id == admission_id)
        .order_by(PatientEducation.created_at.desc())
    )
    return list(result.scalars().all())


# =============================================================================
# Physician Documentation CRUD
# =============================================================================

async def create_physician_daily_note(
    db: AsyncSession,
    obj_in: PhysicianDailyNoteSchema
) -> PhysicianDailyNote:
    """Create physician daily progress note"""
    db_obj = PhysicianDailyNote(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_physician_daily_notes(
    db: AsyncSession,
    admission_id: int,
    note_date: Optional[date] = None
) -> List[PhysicianDailyNote]:
    """Get physician daily notes for admission"""
    query = select(PhysicianDailyNote).where(
        PhysicianDailyNote.admission_id == admission_id
    )

    if note_date:
        query = query.where(PhysicianDailyNote.note_date == note_date)

    query = query.order_by(PhysicianDailyNote.note_date.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_physician_daily_note_by_date(
    db: AsyncSession,
    admission_id: int,
    note_date: date
) -> Optional[PhysicianDailyNote]:
    """Get physician daily note for specific date"""
    result = await db.execute(
        select(PhysicianDailyNote)
        .where(
            and_(
                PhysicianDailyNote.admission_id == admission_id,
                PhysicianDailyNote.note_date == note_date
            )
        )
    )
    return result.scalar_one_or_none()


async def sign_physician_daily_note(
    db: AsyncSession,
    note_id: int,
    signed_by_id: int
) -> Optional[PhysicianDailyNote]:
    """Sign physician daily note"""
    db_obj = await db.execute(
        select(PhysicianDailyNote).where(PhysicianDailyNote.id == note_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    db_obj.signed_by_id = signed_by_id
    db_obj.signed_at = datetime.now()
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# =============================================================================
# Interdisciplinary Documentation CRUD
# =============================================================================

async def create_respiratory_therapy_note(
    db: AsyncSession,
    obj_in: RespiratoryTherapyNoteSchema
) -> RespiratoryTherapyNote:
    """Create respiratory therapy note"""
    db_obj = RespiratoryTherapyNote(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_respiratory_therapy_notes(
    db: AsyncSession,
    admission_id: int
) -> List[RespiratoryTherapyNote]:
    """Get respiratory therapy notes for admission"""
    result = await db.execute(
        select(RespiratoryTherapyNote)
        .where(RespiratoryTherapyNote.admission_id == admission_id)
        .order_by(RespiratoryTherapyNote.note_date.desc())
    )
    return list(result.scalars().all())


async def create_physical_therapy_note(
    db: AsyncSession,
    obj_in: PhysicalTherapyNoteSchema
) -> PhysicalTherapyNote:
    """Create physical therapy note"""
    db_obj = PhysicalTherapyNote(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_physical_therapy_notes(
    db: AsyncSession,
    admission_id: int
) -> List[PhysicalTherapyNote]:
    """Get physical therapy notes for admission"""
    result = await db.execute(
        select(PhysicalTherapyNote)
        .where(PhysicalTherapyNote.admission_id == admission_id)
        .order_by(PhysicalTherapyNote.note_date.desc())
    )
    return list(result.scalars().all())


async def create_nutrition_note(
    db: AsyncSession,
    obj_in: NutritionNoteSchema
) -> NutritionNote:
    """Create nutrition note"""
    db_obj = NutritionNote(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_nutrition_notes(
    db: AsyncSession,
    admission_id: int
) -> List[NutritionNote]:
    """Get nutrition notes for admission"""
    result = await db.execute(
        select(NutritionNote)
        .where(NutritionNote.admission_id == admission_id)
        .order_by(NutritionNote.note_date.desc())
    )
    return list(result.scalars().all())


async def create_social_work_note(
    db: AsyncSession,
    obj_in: SocialWorkNoteSchema
) -> SocialWorkNote:
    """Create social work note"""
    db_obj = SocialWorkNote(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_social_work_notes(
    db: AsyncSession,
    admission_id: int
) -> List[SocialWorkNote]:
    """Get social work notes for admission"""
    result = await db.execute(
        select(SocialWorkNote)
        .where(SocialWorkNote.admission_id == admission_id)
        .order_by(SocialWorkNote.note_date.desc())
    )
    return list(result.scalars().all())


# =============================================================================
# Shift Documentation CRUD
# =============================================================================

async def create_shift_handoff(
    db: AsyncSession,
    obj_in: ShiftHandoffSchema
) -> ShiftHandoff:
    """Create shift handoff documentation"""
    db_obj = ShiftHandoff(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_shift_handoffs(
    db: AsyncSession,
    admission_id: int
) -> List[ShiftHandoff]:
    """Get shift handoffs for admission"""
    result = await db.execute(
        select(ShiftHandoff)
        .where(ShiftHandoff.admission_id == admission_id)
        .order_by(ShiftHandoff.handoff_date.desc(), ShiftHandoff.handoff_time.desc())
    )
    return list(result.scalars().all())


async def verify_shift_handoff(
    db: AsyncSession,
    handoff_id: int
) -> Optional[ShiftHandoff]:
    """Verify shift handoff by receiving nurse"""
    db_obj = await db.execute(
        select(ShiftHandoff).where(ShiftHandoff.id == handoff_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    db_obj.verified_by_receiving_nurse = True
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def create_change_of_shift_report(
    db: AsyncSession,
    obj_in: ChangeOfShiftReportSchema
) -> ChangeOfShiftReport:
    """Create change of shift report"""
    db_obj = ChangeOfShiftReport(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_change_of_shift_reports(
    db: AsyncSession,
    ward_id: int,
    shift_date: date
) -> List[ChangeOfShiftReport]:
    """Get change of shift reports for ward and date"""
    result = await db.execute(
        select(ChangeOfShiftReport)
        .where(
            and_(
                ChangeOfShiftReport.ward_id == ward_id,
                ChangeOfShiftReport.shift_date == shift_date
            )
        )
        .order_by(ChangeOfShiftReport.shift_type)
    )
    return list(result.scalars().all())


async def verify_change_of_shift_report(
    db: AsyncSession,
    report_id: int,
    supervisor_id: int
) -> Optional[ChangeOfShiftReport]:
    """Verify change of shift report by supervisor"""
    db_obj = await db.execute(
        select(ChangeOfShiftReport).where(ChangeOfShiftReport.id == report_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    db_obj.verified_by_supervisor = True
    db_obj.verified_at = datetime.now()
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# =============================================================================
# Digital Signature CRUD
# =============================================================================

async def create_digital_signature(
    db: AsyncSession,
    obj_in: DigitalSignatureSchema
) -> DigitalSignature:
    """Create digital signature"""
    db_obj = DigitalSignature(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_document_signatures(
    db: AsyncSession,
    document_id: int,
    document_type: str
) -> List[DigitalSignature]:
    """Get signatures for document"""
    result = await db.execute(
        select(DigitalSignature)
        .where(
            and_(
                DigitalSignature.document_id == document_id,
                DigitalSignature.document_type == document_type
            )
        )
        .order_by(DigitalSignature.signed_at.desc())
    )
    return list(result.scalars().all())


async def verify_document_signed(
    db: AsyncSession,
    document_id: int,
    document_type: str,
    signer_id: int
) -> bool:
    """Check if document is signed by specific user"""
    result = await db.execute(
        select(DigitalSignature)
        .where(
            and_(
                DigitalSignature.document_id == document_id,
                DigitalSignature.document_type == document_type,
                DigitalSignature.signer_id == signer_id
            )
        )
    )
    return result.scalar_one_or_none() is not None


# =============================================================================
# Auto-save Draft CRUD
# =============================================================================

async def save_draft(
    db: AsyncSession,
    obj_in: AutoSaveDraftSchema
) -> AutoSaveDraft:
    """Save or update auto-save draft"""
    # Check if draft exists for this document type, admission, and user
    result = await db.execute(
        select(AutoSaveDraft)
        .where(
            and_(
                AutoSaveDraft.document_type == obj_in.document_type,
                AutoSaveDraft.admission_id == obj_in.admission_id,
                AutoSaveDraft.user_id == obj_in.user_id
            )
        )
    )
    existing_draft = result.scalar_one_or_none()

    if existing_draft:
        # Update existing draft
        existing_draft.draft_content = obj_in.draft_content
        existing_draft.last_saved = obj_in.last_saved
        await db.commit()
        await db.refresh(existing_draft)
        return existing_draft
    else:
        # Create new draft
        db_obj = AutoSaveDraft(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


async def get_draft(
    db: AsyncSession,
    document_type: str,
    admission_id: int,
    user_id: int
) -> Optional[AutoSaveDraft]:
    """Get auto-save draft for document"""
    result = await db.execute(
        select(AutoSaveDraft)
        .where(
            and_(
                AutoSaveDraft.document_type == document_type,
                AutoSaveDraft.admission_id == admission_id,
                AutoSaveDraft.user_id == user_id
            )
        )
    )
    return result.scalar_one_or_none()


async def delete_draft(
    db: AsyncSession,
    draft_id: int
) -> bool:
    """Delete auto-save draft"""
    db_obj = await db.execute(
        select(AutoSaveDraft).where(AutoSaveDraft.id == draft_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return False

    await db.delete(db_obj)
    await db.commit()
    return True


async def get_user_drafts(
    db: AsyncSession,
    user_id: int,
    admission_id: Optional[int] = None
) -> List[AutoSaveDraft]:
    """Get all drafts for user, optionally filtered by admission"""
    query = select(AutoSaveDraft).where(AutoSaveDraft.user_id == user_id)

    if admission_id:
        query = query.where(AutoSaveDraft.admission_id == admission_id)

    query = query.order_by(AutoSaveDraft.last_saved.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


# =============================================================================
# Discharge Summary Export CRUD
# =============================================================================

async def create_discharge_summary_export(
    db: AsyncSession,
    obj_in: DischargeSummaryExportSchema
) -> DischargeSummaryExport:
    """Create discharge summary export"""
    db_obj = DischargeSummaryExport(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_discharge_summary(
    db: AsyncSession,
    admission_id: int
) -> Optional[DischargeSummaryExport]:
    """Get discharge summary for admission"""
    result = await db.execute(
        select(DischargeSummaryExport)
        .where(DischargeSummaryExport.admission_id == admission_id)
    )
    return result.scalar_one_or_none()


async def update_discharge_summary_file(
    db: AsyncSession,
    summary_id: int,
    file_url: str
) -> Optional[DischargeSummaryExport]:
    """Update discharge summary with generated file URL"""
    db_obj = await db.execute(
        select(DischargeSummaryExport).where(DischargeSummaryExport.id == summary_id)
    )
    db_obj = db_obj.scalar_one_or_none()
    if not db_obj:
        return None

    db_obj.file_url = file_url
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# =============================================================================
# Documentation Summary
# =============================================================================

async def get_documentation_summary(
    db: AsyncSession,
    admission_id: int
) -> Dict[str, Any]:
    """Get summary of all documentation for admission"""
    # Count nursing notes
    nursing_count = await db.execute(
        select(func.count(NursingNarrative.id))
        .where(NursingNarrative.admission_id == admission_id)
    )
    nursing_count = nursing_count.scalar() or 0

    # Count physician notes
    physician_count = await db.execute(
        select(func.count(PhysicianDailyNote.id))
        .where(PhysicianDailyNote.admission_id == admission_id)
    )
    physician_count = physician_count.scalar() or 0

    # Count therapy notes
    therapy_count = await db.execute(
        select(func.count(RespiratoryTherapyNote.id))
        .where(RespiratoryTherapyNote.admission_id == admission_id)
    )
    respiratory_count = therapy_count.scalar() or 0

    therapy_count = await db.execute(
        select(func.count(PhysicalTherapyNote.id))
        .where(PhysicalTherapyNote.admission_id == admission_id)
    )
    pt_count = therapy_count.scalar() or 0

    therapy_count = await db.execute(
        select(func.count(NutritionNote.id))
        .where(NutritionNote.admission_id == admission_id)
    )
    nutrition_count = therapy_count.scalar() or 0

    therapy_count = await db.execute(
        select(func.count(SocialWorkNote.id))
        .where(SocialWorkNote.admission_id == admission_id)
    )
    social_count = therapy_count.scalar() or 0

    total_therapy = respiratory_count + pt_count + nutrition_count + social_count

    # Count shift notes
    shift_count = await db.execute(
        select(func.count(ShiftHandoff.id))
        .where(ShiftHandoff.admission_id == admission_id)
    )
    shift_count = shift_count.scalar() or 0

    return {
        "admission_id": admission_id,
        "nursing_notes": nursing_count,
        "physician_notes": physician_count,
        "therapy_notes": total_therapy,
        "shift_notes": shift_count,
        "total_notes": nursing_count + physician_count + total_therapy + shift_count
    }
