"""Daily Care Documentation Models for STORY-022

This module provides SQLAlchemy models for:
- Nursing documentation (flow sheets, narrative notes, care plans)
- Physician progress notes (daily rounds, assessment and plan)
- Interdisciplinary notes (respiratory, physical therapy, nutrition, social work)
- Shift documentation (shift handoff, change of shift report)
- Digital signatures
- Auto-save functionality
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text, Boolean, Enum as SQLEnum, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


# =============================================================================
# Nursing Documentation Models
# =============================================================================

class NursingFlowSheet(Base):
    """Nursing flow sheet model for vital signs and care observations"""
    __tablename__ = "nursing_flow_sheets"

    id = Column(Integer, primary_key=True, index=True)

    # Admission and nurse
    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    nurse_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Shift information
    shift_date = Column(Date, nullable=False, index=True)
    shift_type = Column(
        SQLEnum("morning", "afternoon", "night", name="shifttype"),
        nullable=False
    )

    # Vital Signs (JSON format for flexibility)
    vital_signs = Column(JSON, nullable=True)  # {temperature: 37.5, bp: "120/80", etc}

    # Intake/Output
    oral_intake_ml = Column(Integer, nullable=True)
    iv_intake_ml = Column(Integer, nullable=True)
    urine_output_ml = Column(Integer, nullable=True)
    stool_output = Column(String(50), nullable=True)
    emesis = Column(Boolean, nullable=True)
    drainage_output = Column(Integer, nullable=True)

    # Skin & Wound Care
    skin_intact = Column(Boolean, nullable=True)
    skin_issues = Column(JSON, nullable=True)  # Array of skin issues
    wound_care_performed = Column(Boolean, nullable=True)
    wound_description = Column(Text, nullable=True)

    # Activity & Mobility
    activity_level = Column(String(50), nullable=True)
    mobility_assistance = Column(String(50), nullable=True)
    fall_risk = Column(String(50), nullable=True)

    # Nutrition & Hydration
    diet_tolerance = Column(String(50), nullable=True)
    eating_assistance = Column(Boolean, nullable=True)
    swallowing_difficulty = Column(Boolean, nullable=True)

    # Elimination
    bowel_pattern = Column(String(50), nullable=True)
    bladder_pattern = Column(String(50), nullable=True)
    incontinence_care = Column(String(50), nullable=True)

    # Behavior & Cognition
    consciousness_level = Column(String(50), nullable=True)
    orientation = Column(String(50), nullable=True)
    behavior = Column(Text, nullable=True)
    restlessness = Column(Boolean, nullable=True)

    # Pain Assessment
    pain_present = Column(Boolean, nullable=True)
    pain_location = Column(String(200), nullable=True)
    pain_score = Column(Integer, nullable=True)
    pain_intervention = Column(Text, nullable=True)

    # Auto-save
    auto_saved = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="nursing_flow_sheets")
    patient = relationship("Patient", backref="nursing_flow_sheets")
    nurse = relationship("User", foreign_keys=[nurse_id], backref="nursing_flow_sheets_created")


class NursingNarrative(Base):
    """Nursing narrative note model"""
    __tablename__ = "nursing_narratives"

    id = Column(Integer, primary_key=True, index=True)

    # Admission and nurse
    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    nurse_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Note details
    note_type = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    is_confidential = Column(Boolean, nullable=False, default=False)

    # Care information
    interventions_performed = Column(JSON, nullable=True)  # Array of interventions
    patient_response = Column(Text, nullable=True)
    complications = Column(JSON, nullable=True)  # Array of complications

    # Signature
    signed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    signed_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="nursing_narratives")
    patient = relationship("Patient", backref="nursing_narratives")
    nurse = relationship("User", foreign_keys=[nurse_id], backref="nursing_narratives_created")
    signed_by = relationship("User", foreign_keys=[signed_by_id], backref="nursing_narratives_signed")


class NursingCarePlan(Base):
    """Nursing care plan model"""
    __tablename__ = "nursing_care_plans"

    id = Column(Integer, primary_key=True, index=True)

    # Admission and nurse
    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    nurse_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Care plan content
    nursing_diagnosis = Column(JSON, nullable=False)  # Array of diagnoses
    goals = Column(JSON, nullable=False)  # Array of goals
    interventions = Column(JSON, nullable=False)  # Array of interventions
    rationale = Column(JSON, nullable=False)  # Array of rationales

    # Evaluation
    evaluation = Column(Text, nullable=True)
    outcome_achieved = Column(Boolean, nullable=True)

    # Dates
    effective_date = Column(Date, nullable=False)
    review_date = Column(Date, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="nursing_care_plans")
    patient = relationship("Patient", backref="nursing_care_plans")
    nurse = relationship("User", backref="nursing_care_plans_created")


class PatientEducation(Base):
    """Patient education documentation model"""
    __tablename__ = "patient_education_records"

    id = Column(Integer, primary_key=True, index=True)

    # Admission and educator
    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    educator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Education details
    education_topic = Column(String(200), nullable=False)
    education_content = Column(Text, nullable=False)

    # Teaching methods
    teaching_method = Column(JSON, nullable=False)  # Array of methods
    barriers_to_learning = Column(JSON, nullable=True)  # Array of barriers

    # Assessment
    patient_understanding = Column(String(50), nullable=False)
    return_demonstration = Column(Boolean, nullable=False, default=False)
    teach_back_method = Column(Boolean, nullable=False, default=False)

    # Follow-up
    follow_up_required = Column(Boolean, nullable=False, default=False)
    follow_up_instructions = Column(Text, nullable=True)

    # Signature
    signed_by_id = Column(Integer, nullable=False)
    signed_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="patient_education")
    patient = relationship("Patient", backref="patient_education")
    educator = relationship("User", backref="education_given")


# =============================================================================
# Physician Documentation Models
# =============================================================================

class PhysicianDailyNote(Base):
    """Physician daily progress note model"""
    __tablename__ = "physician_daily_notes"

    id = Column(Integer, primary_key=True, index=True)

    # Admission and physician
    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    physician_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Note date
    note_date = Column(Date, nullable=False, index=True)

    # SOAP format components
    subjective = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    assessment = Column(Text, nullable=False)
    plan = Column(Text, nullable=False)

    # Diagnosis
    primary_diagnosis = Column(String(500), nullable=False)
    secondary_diagnoses = Column(JSON, nullable=True)  # Array of diagnoses

    # Orders
    new_orders = Column(JSON, nullable=True)  # Array of new orders
    continued_orders = Column(JSON, nullable=True)  # Array of continued orders
    discontinued_orders = Column(JSON, nullable=True)  # Array of discontinued orders

    # Prognosis
    prognosis = Column(String(200), nullable=True)

    # Signature
    signed_by_id = Column(Integer, nullable=False)
    signed_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="physician_daily_notes")
    patient = relationship("Patient", backref="physician_daily_notes")
    physician = relationship("User", backref="physician_daily_notes_created")


# =============================================================================
# Interdisciplinary Documentation Models
# =============================================================================

class RespiratoryTherapyNote(Base):
    """Respiratory therapy documentation model"""
    __tablename__ = "respiratory_therapy_notes"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    therapist_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    note_date = Column(Date, nullable=False)

    therapy_type = Column(String(100), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    frequency = Column(String(50), nullable=True)

    pre_therapy_assessment = Column(Text, nullable=True)
    intervention_provided = Column(Text, nullable=False)
    patient_response = Column(Text, nullable=True)
    post_therapy_assessment = Column(Text, nullable=True)

    recommendations = Column(JSON, nullable=True)  # Array of recommendations

    signed_by_id = Column(Integer, nullable=False)
    signed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="respiratory_therapy_notes")
    patient = relationship("Patient", backref="respiratory_therapy_notes")
    therapist = relationship("User", backref="respiratory_therapy_created")


class PhysicalTherapyNote(Base):
    """Physical therapy documentation model"""
    __tablename__ = "physical_therapy_notes"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    therapist_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    note_date = Column(Date, nullable=False)

    therapy_type = Column(String(100), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    frequency = Column(String(50), nullable=True)

    functional_status = Column(Text, nullable=True)
    treatment_provided = Column(Text, nullable=False)
    patient_response = Column(Text, nullable=True)
    progress_made = Column(Text, nullable=True)

    recommendations = Column(JSON, nullable=True)  # Array of recommendations

    signed_by_id = Column(Integer, nullable=False)
    signed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="physical_therapy_notes")
    patient = relationship("Patient", backref="physical_therapy_notes")
    therapist = relationship("User", backref="physical_therapy_created")


class NutritionNote(Base):
    """Nutrition/dietitian documentation model"""
    __tablename__ = "nutrition_notes"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    dietitian_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    note_date = Column(Date, nullable=False)

    diet_type = Column(String(100), nullable=False)
    calorie_target = Column(Integer, nullable=True)
    protein_target = Column(Integer, nullable=True)

    nutritional_assessment = Column(Text, nullable=True)
    intake_assessment = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=True)  # Array of recommendations

    follow_up_date = Column(Date, nullable=True)

    signed_by_id = Column(Integer, nullable=False)
    signed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="nutrition_notes")
    patient = relationship("Patient", backref="nutrition_notes")
    dietitian = relationship("User", backref="nutrition_notes_created")


class SocialWorkNote(Base):
    """Social work documentation model"""
    __tablename__ = "social_work_notes"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    social_worker_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    note_date = Column(Date, nullable=False)

    psychosocial_assessment = Column(Text, nullable=True)
    support_system = Column(Text, nullable=True)
    barriers_to_discharge = Column(JSON, nullable=True)  # Array of barriers
    discharge_planning = Column(Text, nullable=True)

    interventions_provided = Column(JSON, nullable=True)  # Array of interventions
    referrals_made = Column(JSON, nullable=True)  # Array of referrals

    recommendations = Column(JSON, nullable=True)  # Array of recommendations

    signed_by_id = Column(Integer, nullable=False)
    signed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="social_work_notes")
    patient = relationship("Patient", backref="social_work_notes")
    social_worker = relationship("User", backref="social_work_notes_created")


# =============================================================================
# Shift Documentation Models
# =============================================================================

class ShiftHandoff(Base):
    """Shift handoff documentation model"""
    __tablename__ = "shift_handoffs"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False)

    from_shift = Column(SQLEnum("morning", "afternoon", "night", name="shifttype"), nullable=False)
    to_shift = Column(SQLEnum("morning", "afternoon", "night", name="shifttype"), nullable=False)
    handoff_date = Column(Date, nullable=False)
    handoff_time = Column(DateTime(timezone=True), nullable=False)

    handing_over_nurse_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiving_nurse_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Handoff details
    patient_status_summary = Column(Text, nullable=False)
    critical_events = Column(JSON, nullable=True)  # Array of events
    pending_tasks = Column(JSON, nullable=True)  # Array of tasks
    follow_up_required = Column(JSON, nullable=True)  # Array of follow-ups

    # Patient counts
    total_patients = Column(Integer, nullable=False, default=0)
    stable_patients = Column(Integer, nullable=False, default=0)
    critical_patients = Column(Integer, nullable=False, default=0)
    new_admissions = Column(Integer, nullable=False, default=0)

    verified_by_receiving_nurse = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="shift_handoffs")
    handing_over_nurse = relationship("User", foreign_keys=[handing_over_nurse_id], backref="shifts_handed_over")
    receiving_nurse = relationship("User", foreign_keys=[receiving_nurse_id], backref="shifts_received")


class ChangeOfShiftReport(Base):
    """Change of shift report model"""
    __tablename__ = "change_of_shift_reports"

    id = Column(Integer, primary_key=True, index=True)

    ward_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    shift_date = Column(Date, nullable=False)
    shift_type = Column(SQLEnum("morning", "afternoon", "night", name="shifttype"), nullable=False)
    report_by_nurse_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Ward summary
    total_patients = Column(Integer, nullable=False, default=0)
    total_admissions = Column(Integer, nullable=False, default=0)
    total_discharges = Column(Integer, nullable=False, default=0)
    total_transfers = Column(Integer, nullable=False, default=0)

    # Critical patients
    critical_patient_list = Column(JSON, nullable=True)  # Array of patient IDs

    # Incidents and issues
    incidents_reported = Column(JSON, nullable=True)  # Array of incidents
    equipment_issues = Column(JSON, nullable=True)  # Array of issues
    supply_needs = Column(JSON, nullable=True)  # Array of needs

    # Staffing
    nursing_staff_present = Column(JSON, nullable=True)  # Array of staff names
    staffing_concerns = Column(Text, nullable=True)

    verified_by_supervisor = Column(Boolean, nullable=False, default=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    ward = relationship("Department", backref="change_of_shift_reports")
    report_by_nurse = relationship("User", backref="shift_reports_created")


# =============================================================================
# Digital Signature Model
# =============================================================================

class DigitalSignature(Base):
    """Digital signature model for document signing"""
    __tablename__ = "digital_signatures"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(Integer, nullable=False)
    document_type = Column(String(100), nullable=False)
    signer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    signature_data = Column(Text, nullable=False)  # Encrypted signature
    signed_at = Column(DateTime(timezone=True), nullable=False)

    # Audit
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    signer = relationship("User", backref="signatures_made")


# =============================================================================
# Auto-save Draft Model
# =============================================================================

class AutoSaveDraft(Base):
    """Auto-save draft model for saving in-progress documentation"""
    __tablename__ = "auto_save_drafts"

    id = Column(Integer, primary_key=True, index=True)

    document_type = Column(String(100), nullable=False)
    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    draft_content = Column(JSON, nullable=False)
    last_saved = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="drafts")
    user = relationship("User", backref="drafts")


# =============================================================================
# Discharge Summary Export Model
# =============================================================================

class DischargeSummaryExport(Base):
    """Discharge summary export model"""
    __tablename__ = "discharge_summary_exports"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, unique=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    # Discharge summary data
    summary_data = Column(JSON, nullable=False)

    # Export details
    export_format = Column(String(10), nullable=False)  # pdf, docx, html
    file_url = Column(String(500), nullable=True)

    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="discharge_summary_export")
    patient = relationship("Patient", backref="discharge_summary_exports")
    generated_by = relationship("User", backref="discharge_summary_exports_generated")
