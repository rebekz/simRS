"""Daily Care Documentation Schemas for STORY-022

This module provides Pydantic schemas for:
- Nursing documentation (flow sheets, narrative notes, care plans)
- Physician progress notes (daily rounds, assessment and plan)
- Interdisciplinary notes (respiratory, physical therapy, nutrition, social work)
- Shift documentation (shift handoff, change of shift report)
- Digital signatures
- Auto-save functionality
- Discharge summary export
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# Documentation Enums
# =============================================================================

class NoteType(str, Enum):
    """Types of clinical documentation notes"""
    NURSING_FLOW_SHEET = "nursing_flow_sheet"  # Lembar observasi keperawatan
    NURSING_NARRATIVE = "nursing_narrative"  # Catatan keperawatan naratif
    NURSING_CARE_PLAN = "nursing_care_plan"  # Rencana asuhan keperawatan
    PATIENT_EDUCATION = "patient_education"  # Edukasi pasien
    PHYSICIAN_DAILY = "physician_daily"  # Catatan harian dokter
    PHYSICIAN_PROGRESS = "physician_progress"  # Catatan perkembangan
    PHYSICIAN_ORDERS = "physician_orders"  # Perintah dokter
    RESPIRATORY_THERAPY = "respiratory_therapy"  # Terapi napas
    PHYSICAL_THERAPY = "physical_therapy"  # Fisioterapi
    NUTRITION = "nutrition"  # Nutrisi
    SOCIAL_WORK = "social_work"  # Pekerjaan sosial
    SHIFT_HANDOFF = "shift_handoff"  # Serah terima shift
    CHANGE_OF_SHIFT = "change_of_shift"  # Laporan ganti shift


class ShiftType(str, Enum):
    """Shift types"""
    MORNING = "morning"  # Pagi (07:00-14:00)
    AFTERNOON = "afternoon"  # Siang (14:00-21:00)
    NIGHT = "night"  # Malam (21:00-07:00)


class VitalSign(str, Enum):
    """Vital signs to track"""
    TEMPERATURE = "temperature"  # Suhu tubuh
    BLOOD_PRESSURE = "blood_pressure"  # Tekanan darah
    HEART_RATE = "heart_rate"  # Denyut jantung
    RESPIRATORY_RATE = "respiratory_rate"  # Denyut napas
    OXYGEN_SATURATION = "oxygen_saturation"  # Saturasi oksigen (SpO2)
    WEIGHT = "weight"  # Berat badan
    HEIGHT = "height"  # Tinggi badan
    PAIN_LEVEL = "pain_level"  # Tingkat nyeri (0-10)
    BLOOD_GLUCOSE = "blood_glucose"  # Gula darah
    CONSCIOUSNESS = "consciousness"  # Kesadaran (GCS)


# =============================================================================
# Nursing Documentation Schemas
# =============================================================================

class NursingFlowSheetBase(BaseModel):
    """Base nursing flow sheet schema"""
    admission_id: int
    patient_id: int
    nurse_id: int
    shift_date: date
    shift_type: ShiftType

    # Vital Signs
    vital_signs: Dict[str, Any] = Field(default_factory=dict)

    # Intake/Output
    oral_intake_ml: Optional[int] = None
    iv_intake_ml: Optional[int] = None
    urine_output_ml: Optional[int] = None
    stool_output: Optional[str] = None  # normal, diarrhea, constipated
    emesis: Optional[bool] = None
    drainage_output: Optional[int] = None

    # Skin & Wound Care
    skin_intact: Optional[bool] = None
    skin_issues: Optional[List[str]] = None  # redness, rash, wound, etc
    wound_care_performed: Optional[bool] = None
    wound_description: Optional[str] = None

    # Activity & Mobility
    activity_level: Optional[str] = None  # bed_rest, BRP, ambulatory
    mobility_assistance: Optional[str] = None  # independent, assistive, dependent
    fall_risk: Optional[str] = None  # low, moderate, high

    # Nutrition & Hydration
    diet_tolerance: Optional[str] = None  # good, fair, poor, NPO
    eating_assistance: Optional[bool] = None
    swallowing_difficulty: Optional[bool] = None

    # Elimination
    bowel_pattern: Optional[str] = None
    bladder_pattern: Optional[str] = None  # continent, catheter, incontinent
    incontinence_care: Optional[str] = None

    # Behavior & Cognition
    consciousness_level: Optional[str] = None  # alert, lethargic, stupor, coma
    orientation: Optional[str] = None  # oriented x3, x2, x1, disoriented
    behavior: Optional[str] = None
    restlessness: Optional[bool] = None

    # Pain Assessment
    pain_present: Optional[bool] = None
    pain_location: Optional[str] = None
    pain_score: Optional[int] = None  # 0-10 scale
    pain_intervention: Optional[str] = None


class NursingFlowSheetCreate(NursingFlowSheetBase):
    """Schema for creating nursing flow sheet"""
    pass


class NursingFlowSheetResponse(NursingFlowSheetBase):
    """Schema for nursing flow sheet response"""
    id: int
    auto_saved: bool = False
    created_at: datetime
    updated_at: datetime

    # Denormalized fields
    patient_name: Optional[str] = None
    nurse_name: Optional[str] = None

    class Config:
        from_attributes = True


class NursingNarrativeNote(BaseModel):
    """Schema for nursing narrative note"""
    admission_id: int
    patient_id: int
    nurse_id: int
    note_type: NoteType
    content: str = Field(..., description="Catatan naratif keperawatan")
    is_confidential: bool = False

    # Care interventions performed
    interventions_performed: Optional[List[str]] = None
    patient_response: Optional[str] = None
    complications: Optional[List[str]] = None

    # Signature
    signed_by_id: int
    signed_at: Optional[datetime] = None


class NursingCarePlan(BaseModel):
    """Schema for nursing care plan"""
    admission_id: int
    patient_id: int
    nurse_id: int

    # Nursing diagnoses
    nursing_diagnosis: List[str] = Field(..., description="Diagnosa keperawatan")

    # Goals and outcomes
    goals: List[str] = Field(..., description="Tujuan dan hasil yang diharapkan")

    # Interventions
    interventions: List[str] = Field(..., description="Intervensi yang akan dilakukan")
    rationale: List[str] = Field(..., description="Rasional/Alasan")

    # Evaluation
    evaluation: Optional[str] = None
    outcome_achieved: Optional[bool] = None

    # Timestamps
    effective_date: date
    review_date: Optional[date] = None


class PatientEducation(BaseModel):
    """Schema for patient education documentation"""
    admission_id: int
    patient_id: int
    educator_id: int

    education_topic: str = Field(..., description="Topik edukasi")
    education_content: str = Field(..., description="Konten edukasi yang diberikan")

    teaching_method: List[str] = Field(..., description="Metode pengajaran")
    barriers_to_learning: Optional[List[str]] = None
    patient_understanding: str = Field(..., description="Pemahaman pasien")

    return_demonstration: bool = False
    teach_back_method: bool = False

    # Follow-up
    follow_up_required: bool = False
    follow_up_instructions: Optional[str] = None

    signed_by_id: int
    signed_at: Optional[datetime] = None


# =============================================================================
# Physician Documentation Schemas
# =============================================================================

class PhysicianDailyNote(BaseModel):
    """Schema for physician daily progress note"""
    admission_id: int
    patient_id: int
    physician_id: int
    note_date: date

    # Subjective and Objective
    subjective: Optional[str] = None  # Keluhan pasien
    objective: Optional[str] = None  # Hasil pemeriksaan fisik & lab

    # Assessment and Plan
    assessment: str = Field(..., description="Penilaian/Assessment")
    plan: str = Field(..., description="Rencana tatalaksana")

    # Diagnosis
    primary_diagnosis: str
    secondary_diagnoses: Optional[List[str]] = None

    # Orders
    new_orders: Optional[List[str]] = None
    continued_orders: Optional[List[str]] = None
    discontinued_orders: Optional[List[str]] = None

    # Prognosis
    prognosis: Optional[str] = None

    # Signature
    signed_by_id: int
    signed_at: Optional[datetime] = None


class PhysicianProgressNote(BaseModel):
    """Schema for physician progress note (SOAP)"""
    admission_id: int
    patient_id: int
    physician_id: int

    # SOAP format
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: str = Field(..., description="Assessment SOAP note")
    plan: str = Field(..., description="Plan SOAP note")

    # Additional
    diagnosis: Optional[str] = None
    changes: Optional[str] = Field(None, description="Perubahan status/kondisi")

    # Signature
    signed_by_id: int
    signed_at: Optional[datetime] = None


# =============================================================================
# Interdisciplinary Documentation Schemas
# =============================================================================

class RespiratoryTherapyNote(BaseModel):
    """Schema for respiratory therapy documentation"""
    admission_id: int
    patient_id: int
    therapist_id: int
    note_date: date

    therapy_type: str  # oxygen_therapy, nebulization, chest_pt, suctioning
    duration_minutes: Optional[int] = None
    frequency: Optional[str] = None

    pre_therapy_assessment: Optional[str] = None
    intervention_provided: str
    patient_response: Optional[str] = None
    post_therapy_assessment: Optional[str] = None

    recommendations: Optional[List[str]] = None

    signed_by_id: int
    signed_at: Optional[datetime] = None


class PhysicalTherapyNote(BaseModel):
    """Schema for physical therapy documentation"""
    admission_id: int
    patient_id: int
    therapist_id: int
    note_date: date

    therapy_type: str  # mobility, gait_training, exercise, etc
    duration_minutes: Optional[int] = None
    frequency: Optional[str] = None

    functional_status: Optional[str] = None
    treatment_provided: str
    patient_response: Optional[str] = None
    progress_made: Optional[str] = None

    recommendations: Optional[List[str]] = None

    signed_by_id: int
    signed_at: Optional[datetime] = None


class NutritionNote(BaseModel):
    """Schema for nutrition/dietitian documentation"""
    admission_id: int
    patient_id: int
    dietitian_id: int
    note_date: date

    diet_type: str  # regular, diabetic, renal, low_sodium, etc
    calorie_target: Optional[int] = None
    protein_target: Optional[int] = None

    nutritional_assessment: Optional[str] = None
    intake_assessment: Optional[str] = None
    recommendations: Optional[List[str]] = None

    follow_up_date: Optional[date] = None

    signed_by_id: int
    signed_at: Optional[datetime] = None


class SocialWorkNote(BaseModel):
    """Schema for social work documentation"""
    admission_id: int
    patient_id: int
    social_worker_id: int
    note_date: date

    psychosocial_assessment: Optional[str] = None
    support_system: Optional[str] = None
    barriers_to_discharge: Optional[List[str]] = None
    discharge_planning: Optional[str] = None

    interventions_provided: Optional[List[str]] = None
    referrals_made: Optional[List[str]] = None

    recommendations: Optional[List[str]] = None

    signed_by_id: int
    signed_at: Optional[datetime] = None


# =============================================================================
# Shift Documentation Schemas
# =============================================================================

class ShiftHandoff(BaseModel):
    """Schema for shift handoff documentation"""
    admission_id: int
    from_shift: ShiftType
    to_shift: ShiftType
    handoff_date: date
    handoff_time: datetime

    handing_over_nurse_id: int
    receiving_nurse_id: int

    # Patient status summary
    patient_status_summary: str = Field(..., description="Ringkasan status pasien")

    # Critical events
    critical_events: Optional[List[str]] = None
    pending_tasks: Optional[List[str]] = None
    follow_up_required: Optional[List[str]] = None

    # Patient count
    total_patients: int
    stable_patients: int
    critical_patients: int
    new_admissions: int

    verified_by_receiving_nurse: bool = False


class ChangeOfShiftReport(BaseModel):
    """Schema for change of shift report"""
    ward_id: int
    shift_date: date
    shift_type: ShiftType
    report_by_nurse_id: int

    # Overall ward status
    total_patients: int
    total_admissions: int
    total_discharges: int
    total_transfers: int

    # Critical patients
    critical_patient_list: Optional[List[int]] = None

    # Incidents
    incidents_reported: Optional[List[str]] = None

    # Equipment status
    equipment_issues: Optional[List[str]] = None
    supply_needs: Optional[List[str]] = None

    # Staffing
    nursing_staff_present: Optional[List[str]] = None
    staffing_concerns: Optional[str] = None

    verified_by_supervisor: bool = False
    verified_at: Optional[datetime] = None


# =============================================================================
# Digital Signature Schema
# =============================================================================

class DigitalSignature(BaseModel):
    """Schema for digital signature"""
    document_id: int
    document_type: str
    signer_id: int
    signature_data: str  # Encrypted signature data
    signed_at: datetime = Field(default_factory=datetime.now)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


# =============================================================================
# Auto-save Schema
# =============================================================================

class AutoSaveDraft(BaseModel):
    """Schema for auto-save draft"""
    document_type: NoteType
    admission_id: int
    user_id: int
    draft_content: Dict[str, Any]
    last_saved: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Discharge Summary Schema
# =============================================================================

class DischargeSummaryExport(BaseModel):
    """Schema for discharge summary export"""
    admission_id: int
    patient_id: int

    # Patient info
    patient_name: str
    mrn: str
    date_of_birth: date
    gender: str

    # Admission info
    admission_date: datetime
    discharge_date: datetime
    length_of_stay_days: int

    # Clinical info
    admission_diagnosis: str
    discharge_diagnosis: str
    procedures_performed: Optional[List[str]] = None

    # Course of illness
    course_of_illness: Optional[str] = None

    # Treatment summary
    treatments_given: List[str]
    medications_prescribed: List[str]

    # Discharge planning
    discharge_destination: str  # home, facility, transfer, etc
    discharge_condition: str

    # Follow-up
    follow_up_appointments: Optional[List[str]] = None
    discharge_instructions: str
    medications_at_discharge: List[str]

    # Export format
    export_format: str = Field("pdf", description="pdf, docx, html")
    generated_by_id: int
    generated_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Documentation List Response
# =============================================================================

class DocumentationListResponse(BaseModel):
    """Schema for documentation list response"""
    admission_id: int
    patient_id: int
    patient_name: str
    total_notes: int

    # Notes by type
    nursing_notes: int
    physician_notes: int
    therapy_notes: int
    shift_notes: int

    # Most recent notes
    recent_notes: List[Dict[str, Any]] = Field(default_factory=list)
