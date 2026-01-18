"""Discharge Planning Models for STORY-023

This module provides SQLAlchemy models for:
- Discharge readiness assessment
- Discharge orders
- Discharge summary
- Medication reconciliation
- Follow-up appointments
- BPJS claim finalization
- SEP closure
- Discharge instructions
- Discharge checklist
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text, Boolean, Enum as SQLEnum, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


# =============================================================================
# Discharge Readiness Assessment
# =============================================================================

class DischargeReadiness(Base):
    """Discharge readiness assessment model"""
    __tablename__ = "discharge_readiness"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    assessed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Readiness criteria (JSON for flexibility)
    criteria = Column(JSON, nullable=False)  # DischargeReadinessCriteria

    # Overall readiness
    is_ready = Column(Boolean, nullable=False, default=False)
    readiness_score = Column(Float, nullable=False)  # 0-100 scale

    # Barriers to discharge
    barriers_to_discharge = Column(JSON, nullable=True)  # Array of barriers

    # Required actions
    required_actions = Column(JSON, nullable=True)  # Array of actions

    # Estimated discharge date
    estimated_discharge_date = Column(Date, nullable=True)

    # Assessment timestamp
    assessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Notes
    notes = Column(Text, nullable=True)

    # Relationships
    admission = relationship("AdmissionOrder", backref="discharge_readiness")
    patient = relationship("Patient", backref="discharge_readiness")
    assessed_by = relationship("User", foreign_keys=[assessed_by_id], backref="readiness_assessments")


# =============================================================================
# Discharge Orders
# =============================================================================

class DischargeOrder(Base):
    """Discharge order model"""
    __tablename__ = "discharge_orders"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    physician_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Discharge details
    discharge_status = Column(SQLEnum("planned", "ready", "pending", "discharged", name="dischargestatus"), nullable=False)
    discharge_destination = Column(SQLEnum("home", "transfer", "facility", "left_against_advice", "deceased", name="dischargedestination"), nullable=False)
    discharge_condition = Column(SQLEnum("improved", "stable", "unchanged", "worsened", name="dischargecondition"), nullable=False)

    # Discharge medications (JSON array)
    discharge_medications = Column(JSON, nullable=False)

    # Discharge instructions (JSON array)
    discharge_instructions = Column(JSON, nullable=False)

    # Activity restrictions (JSON array)
    activity_restrictions = Column(JSON, nullable=True)

    # Diet instructions
    diet_instructions = Column(Text, nullable=True)

    # Wound care instructions
    wound_care_instructions = Column(Text, nullable=True)

    # Follow-up appointments (JSON array - references follow_up_appointments)
    follow_up_appointments = Column(JSON, nullable=True)

    # Medical equipment needed (JSON array)
    medical_equipment = Column(JSON, nullable=True)

    # Transportation arrangements
    transportation_arranged = Column(Boolean, nullable=False, default=False)
    transportation_type = Column(String(50), nullable=True)

    # Responsible adult
    responsible_adult_name = Column(String(200), nullable=True)
    responsible_adult_relationship = Column(String(100), nullable=True)
    responsible_adult_contact = Column(String(50), nullable=True)

    # Special needs (JSON array)
    special_needs = Column(JSON, nullable=True)

    # Order timestamp
    ordered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Discharge dates
    estimated_discharge_date = Column(Date, nullable=True)
    actual_discharge_date = Column(DateTime(timezone=True), nullable=True)

    # Physician notes
    physician_notes = Column(Text, nullable=True)

    # Relationships
    admission = relationship("AdmissionOrder", backref="discharge_orders")
    patient = relationship("Patient", backref="discharge_orders")
    physician = relationship("User", foreign_keys=[physician_id], backref="discharge_orders_created")


# =============================================================================
# Discharge Summary
# =============================================================================

class DischargeSummary(Base):
    """Discharge summary model"""
    __tablename__ = "discharge_summaries"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, unique=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    # Patient info (denormalized for summary)
    patient_name = Column(String(200), nullable=False)
    mrn = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=False)

    # Admission info (denormalized)
    admission_date = Column(DateTime(timezone=True), nullable=False)
    discharge_date = Column(DateTime(timezone=True), nullable=False)
    length_of_stay_days = Column(Integer, nullable=False)

    # Diagnoses
    admission_diagnosis = Column(Text, nullable=False)
    discharge_diagnosis = Column(Text, nullable=False)
    secondary_diagnoses = Column(JSON, nullable=True)

    # Procedures performed
    procedures_performed = Column(JSON, nullable=True)

    # Course of illness
    course_of_illness = Column(Text, nullable=True)

    # Treatments given
    treatments_given = Column(JSON, nullable=False)
    medications_administered = Column(JSON, nullable=False)

    # Complications
    complications = Column(JSON, nullable=True)

    # Discharge condition
    discharge_condition = Column(SQLEnum("improved", "stable", "unchanged", "worsened", name="dischargecondition"), nullable=False)

    # Discharge medications
    discharge_medications = Column(JSON, nullable=False)

    # Discharge instructions
    discharge_instructions = Column(JSON, nullable=False)

    # Follow-up information
    follow_up_appointments = Column(JSON, nullable=True)

    # Responsible physician
    attending_physician = Column(String(200), nullable=False)

    # Generated by
    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Generation timestamp
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Export format and file URL
    export_format = Column(String(10), nullable=False)  # pdf, docx, html
    file_url = Column(String(500), nullable=True)

    # Relationships
    admission = relationship("AdmissionOrder", backref="discharge_summary")
    patient = relationship("Patient", backref="discharge_summaries")
    generated_by = relationship("User", backref="summaries_generated")


# =============================================================================
# Medication Reconciliation
# =============================================================================

class DischargeMedicationReconciliation(Base):
    """Discharge-specific medication reconciliation model

    This extends the general MedicationReconciliation with discharge-specific fields.
    Note: Renamed to avoid conflict with medication.MedicationReconciliation.
    """
    __tablename__ = "discharge_medication_reconciliations"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    pharmacist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    physician_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Reconciliation date
    reconciliation_date = Column(Date, nullable=False)

    # Reconciled medications (JSON arrays)
    medications_to_continue = Column(JSON, nullable=False)
    medications_to_discontinue = Column(JSON, nullable=False)
    medications_to_change = Column(JSON, nullable=False)
    new_medications = Column(JSON, nullable=False)

    # Notes
    reconciliation_notes = Column(Text, nullable=True)
    pharmacist_notes = Column(Text, nullable=True)

    # Verification
    verified_by_physician = Column(Boolean, nullable=False, default=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Table options - allow extending from medication.MedicationReconciliation
    __table_args__ = {'extend_existing': True}

    # Relationships
    admission = relationship("AdmissionOrder", backref="discharge_medication_reconciliations")
    patient = relationship("Patient", backref="discharge_medication_reconciliations")
    pharmacist = relationship("User", foreign_keys=[pharmacist_id], backref="discharge_reconciliations_performed")
    physician = relationship("User", foreign_keys=[physician_id], backref="discharge_reconciliations_approved")


# =============================================================================
# Follow-up Appointments
# =============================================================================

class FollowUpAppointment(Base):
    """Follow-up appointment model"""
    __tablename__ = "follow_up_appointments"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    scheduled_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Appointment details
    appointment_type = Column(SQLEnum("outpatient", "telephone", "video", "home_visit", name="followuptype"), nullable=False)
    specialty = Column(String(100), nullable=False)
    physician_name = Column(String(200), nullable=True)

    # Schedule
    appointment_date = Column(Date, nullable=False, index=True)
    appointment_time = Column(String(10), nullable=False)  # HH:MM format

    # Location/Contact
    location = Column(String(200), nullable=True)
    contact_number = Column(String(50), nullable=True)
    video_link = Column(String(500), nullable=True)

    # Purpose
    purpose = Column(Text, nullable=False)

    # Priority
    priority = Column(String(20), nullable=False, server_default="routine")

    # Reminders (JSON array of methods)
    send_reminder = Column(Boolean, nullable=False, default=True)
    reminder_method = Column(JSON, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Confirmation
    confirmed = Column(Boolean, nullable=False, default=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="follow_up_appointments")
    patient = relationship("Patient", backref="follow_up_appointments")
    scheduled_by = relationship("User", backref="appointments_scheduled")


# =============================================================================
# BPJS Claim Finalization
# =============================================================================

class BPJSClaimFinalization(Base):
    """BPJS claim finalization model"""
    __tablename__ = "bpjs_claim_finalizations"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, unique=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    # SEP number
    sep_number = Column(String(50), nullable=False, unique=True)

    # Claim data
    final_diagnosis = Column(Text, nullable=False)
    procedure_codes = Column(JSON, nullable=True)
    icd_10_codes = Column(JSON, nullable=False)

    # Service details
    admission_type = Column(String(50), nullable=False)
    class_type = Column(String(20), nullable=False)
    bed_type = Column(String(50), nullable=False)
    room_number = Column(String(50), nullable=False)

    # Dates
    admission_date = Column(DateTime(timezone=True), nullable=False)
    discharge_date = Column(DateTime(timezone=True), nullable=False)
    length_of_stay_days = Column(Integer, nullable=False)

    # Professional fees
    doctor_visit_count = Column(Integer, nullable=False)
    doctor_visit_fees = Column(Float, nullable=True)
    consultation_fees = Column(Float, nullable=True)
    procedure_fees = Column(Float, nullable=True)

    # Service charges
    room_charges = Column(Float, nullable=True)
    medication_charges = Column(Float, nullable=True)
    laboratory_charges = Column(Float, nullable=True)
    radiology_charges = Column(Float, nullable=True)
    other_charges = Column(Float, nullable=True)

    # Total
    total_claim_amount = Column(Float, nullable=False)

    # Validation
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    validation_notes = Column(Text, nullable=True)

    # Submission
    submitted_to_bpjs = Column(Boolean, nullable=False, default=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    claim_submission_number = Column(String(100), nullable=True)

    # Status
    claim_status = Column(String(50), nullable=False, server_default="pending")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="bpjs_claim")
    patient = relationship("Patient", backref="discharge_bpjs_claims")
    validated_by_user = relationship("User", backref="claims_validated")


# =============================================================================
# SEP Closure
# =============================================================================

class SEPClosure(Base):
    """SEP closure model"""
    __tablename__ = "sep_closures"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, unique=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    # SEP details
    sep_number = Column(String(50), nullable=False, unique=True)

    # Closure details
    closure_reason = Column(String(50), nullable=False)
    discharge_status = Column(SQLEnum("planned", "ready", "pending", "discharged", name="dischargestatus"), nullable=False)
    discharge_condition = Column(SQLEnum("improved", "stable", "unchanged", "worsened", name="dischargecondition"), nullable=False)

    # Final diagnosis
    final_diagnosis = Column(Text, nullable=False)
    icd_10_code = Column(String(20), nullable=False)

    # Discharge date
    discharge_date = Column(DateTime(timezone=True), nullable=False)

    # Length of stay
    length_of_stay_days = Column(Integer, nullable=False)

    # Outcome
    patient_outcome = Column(String(50), nullable=False)

    # Follow-up required
    follow_up_required = Column(Boolean, nullable=False, default=False)
    follow_up_instructions = Column(Text, nullable=True)

    # Closed by
    closed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # SEP status update confirmation
    sep_updated = Column(Boolean, nullable=False, default=False)
    sep_update_response = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="sep_closure")
    patient = relationship("Patient", backref="sep_closures")
    closed_by = relationship("User", backref="seps_closed")


# =============================================================================
# Patient Discharge Instructions
# =============================================================================

class PatientDischargeInstructions(Base):
    """Patient discharge instructions model"""
    __tablename__ = "patient_discharge_instructions"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, unique=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    # Summary
    summary = Column(Text, nullable=False)

    # Diagnoses (patient-friendly)
    diagnoses = Column(JSON, nullable=False)

    # Treatments received
    treatments_received = Column(JSON, nullable=False)

    # Discharge medications
    medications = Column(JSON, nullable=False)

    # Activity instructions
    activity_instructions = Column(JSON, nullable=False)

    # Diet instructions
    diet_instructions = Column(JSON, nullable=False)

    # Wound care
    wound_care_instructions = Column(JSON, nullable=True)

    # Warning signs
    warning_signs = Column(JSON, nullable=False)

    # Emergency care instructions
    emergency_care_instructions = Column(JSON, nullable=False)

    # Follow-up appointments
    follow_up_appointments = Column(JSON, nullable=False)

    # Contact information
    emergency_contact = Column(String(200), nullable=False)
    hospital_contact = Column(String(200), nullable=False)

    # Generated by
    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Language
    language = Column(String(10), nullable=False, server_default="id")

    # Delivery method
    delivery_method = Column(String(20), nullable=False, server_default="printed")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="patient_instructions")
    patient = relationship("Patient", backref="patient_instructions")
    generated_by = relationship("User", backref="instructions_generated")


# =============================================================================
# Discharge Checklist
# =============================================================================

class DischargeChecklist(Base):
    """Discharge checklist model"""
    __tablename__ = "discharge_checklists"

    id = Column(Integer, primary_key=True, index=True)

    admission_id = Column(Integer, ForeignKey("admission_orders.id"), nullable=False, unique=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    # Checklist items (JSON arrays)
    clinical_criteria = Column(JSON, nullable=False)
    medication_criteria = Column(JSON, nullable=False)
    documentation_criteria = Column(JSON, nullable=False)
    logistics_criteria = Column(JSON, nullable=False)
    education_criteria = Column(JSON, nullable=False)
    follow_up_criteria = Column(JSON, nullable=False)

    # Overall completion
    all_criteria_met = Column(Boolean, nullable=False, default=False)

    # Verified by
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    admission = relationship("AdmissionOrder", backref="discharge_checklist")
    patient = relationship("Patient", backref="discharge_checklist")
    verified_by = relationship("User", backref="checklists_verified")
