"""Discharge Planning Schemas for STORY-023

This module provides Pydantic schemas for:
- Discharge readiness assessment
- Discharge orders
- Discharge summary generation
- Medication reconciliation
- Follow-up appointment scheduling
- BPJS claim finalization
- SEP closure
- Discharge instructions
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# Discharge Enums
# =============================================================================

class DischargeStatus(str, Enum):
    """Discharge process status"""
    PLANNED = "planned"  # Rencana pemulangan
    READY = "ready"  # Siap dipulangkan
    PENDING = "pending"  # Menunggu persetujuan/klarifikasi
    DISCHARGED = "discharged"  # Sudah dipulangkan


class DischargeDestination(str, Enum):
    """Discharge destination"""
    HOME = "home"  # Pulang ke rumah
    TRANSFER = "transfer"  # Rujukan ke rumah sakit lain
    FACILITY = "facility"  # Fasilitas perawatan (nursing home, rehab)
    LEFT_AGAINST_ADVICE = "left_against_advice"  # Pulang atas permintaan sendiri
    DECEASED = "deceased"  # Meninggal


class DischargeCondition(str, Enum):
    """Patient condition at discharge"""
    IMPROVED = "improved"  # Membaik
    STABLE = "stable"  # Stabil
    UNCHANGED = "unchanged"  # Tetap
    WORSENED = "worsened"  # Memburuk


class FollowUpType(str, Enum):
    """Follow-up appointment type"""
    OUTPATIENT = "outpatient"  # Rawat jalan
    TELEPHONE = "telephone"  # Follow-up via telepon
    VIDEO = "video"  # Follow-up video call
    HOME_VISIT = "home_visit"  # Kunjungan rumah


class MedicationReconciliationStatus(str, Enum):
    """Medication reconciliation status"""
    RECONCILED = "reconciled"  # Sudah direkonsiliasi
    PENDING = "pending"  # Menunggu rekonsiliasi
    DISCONTINUED = "discontinued"  # Dihentikan
    CHANGED = "changed"  # Diubah


# =============================================================================
# Discharge Readiness Assessment
# =============================================================================

class DischargeReadinessCriteria(BaseModel):
    """Individual discharge readiness criteria"""
    clinically_stable: bool = Field(..., description="Pasien secara klinis stabil")
    vital_signs_stable: bool = Field(..., description="Tanda vital stabil 24 jam terakhir")
    afebrile_24h: bool = Field(..., description="Tidak demam 24 jam terakhir")
    pain_controlled: bool = Field(..., description="Nyeri terkontrol")
    medications_prescribed: bool = Field(..., description "Obat sudah diresepkan")
    education_completed: bool = Field(..., description="Edukasi pasien selesai")
    follow_up_scheduled: bool = Field(..., description="Follow-up dijadwalkan")
    arrangements_made: bool = Field(..., description="Aransemen pulang siap")


class DischargeReadinessAssessment(BaseModel):
    """Discharge readiness assessment"""
    admission_id: int
    patient_id: int
    assessed_by_id: int

    # Readiness criteria
    criteria: DischargeReadinessCriteria

    # Overall readiness
    is_ready: bool = Field(..., description="Pasien siap dipulangkan")
    readiness_score: float = Field(..., ge=0, le=100, description="Skala kesiapan 0-100")

    # Criteria not met
    barriers_to_discharge: Optional[List[str]] = Field(None, description="Hambatan pemulangan")

    # Required before discharge
    required_actions: Optional[List[str]] = Field(None, description="Tindakan yang diperlukan")

    # Estimated discharge date
    estimated_discharge_date: Optional[date] = None

    # Assessment timestamp
    assessed_at: datetime = Field(default_factory=datetime.now)

    # Notes
    notes: Optional[str] = None


# =============================================================================
# Discharge Orders
# =============================================================================

class DischargeMedication(BaseModel):
    """Discharge medication"""
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    route: str  # oral, IV, IM, etc.
    indication: Optional[str] = None
    special_instructions: Optional[str] = None


class DischargeInstruction(BaseModel):
    """Specific discharge instruction"""
    category: str  # activity, diet, wound_care, symptoms, etc.
    instruction: str
    priority: str = "normal"  # normal, important, critical


class ActivityRestriction(BaseModel):
    """Activity restriction at discharge"""
    activity_type: str  # driving, working, lifting, exercise, etc.
    restriction_level: str  # no_restriction, limited, prohibited
    duration: Optional[str] = None  # e.g., "2 weeks", "until follow-up"


class DischargeOrder(BaseModel):
    """Discharge orders"""
    admission_id: int
    patient_id: int
    physician_id: int

    # Discharge details
    discharge_status: DischargeStatus
    discharge_destination: DischargeDestination
    discharge_condition: DischargeCondition

    # Discharge medications
    discharge_medications: List[DischargeMedication]

    # Discharge instructions
    discharge_instructions: List[DischargeInstruction]

    # Activity restrictions
    activity_restrictions: List[ActivityRestriction]

    # Diet instructions
    diet_instructions: Optional[str] = None

    # Wound care instructions
    wound_care_instructions: Optional[str] = None

    # Follow-up appointments
    follow_up_appointments: List[Dict[str, Any]]  # From follow-up scheduling

    # Medical equipment needed
    medical_equipment: Optional[List[str]] = None

    # Transportation arrangements
    transportation_arranged: bool = False
    transportation_type: Optional[str] = None  # ambulan, pribadi,antar-jemput

    # Responsible adult
    responsible_adult_name: Optional[str] = None
    responsible_adult_relationship: Optional[str] = None
    responsible_adult_contact: Optional[str] = None

    # Special needs
    special_needs: Optional[List[str]] = None

    # Order timestamp
    ordered_at: datetime = Field(default_factory=datetime.now)

    # Discharge date (estimated or actual)
    estimated_discharge_date: Optional[date] = None
    actual_discharge_date: Optional[datetime] = None

    # Physician notes
    physician_notes: Optional[str] = None


# =============================================================================
# Discharge Summary
# =============================================================================

class DischargeSummary(BaseModel):
    """Discharge summary for automatic generation"""
    admission_id: int
    patient_id: int

    # Patient info (denormalized for summary)
    patient_name: str
    mrn: str
    date_of_birth: date
    gender: str

    # Admission info (denormalized)
    admission_date: datetime
    discharge_date: datetime
    length_of_stay_days: int

    # Diagnoses
    admission_diagnosis: str
    discharge_diagnosis: str
    secondary_diagnoses: Optional[List[str]] = None

    # Procedures performed
    procedures_performed: Optional[List[str]] = None

    # Course of illness
    course_of_illness: Optional[str] = None

    # Treatments given
    treatments_given: List[str]
    medications_administered: List[str]

    # Complications
    complications: Optional[List[str]] = None

    # Discharge condition
    discharge_condition: DischargeCondition

    # Discharge medications
    discharge_medications: List[str]

    # Discharge instructions
    discharge_instructions: List[str]

    # Follow-up information
    follow_up_appointments: List[Dict[str, Any]]

    # Responsible physician
    attending_physician: str

    # Generated by
    generated_by_id: int

    # Generation timestamp
    generated_at: datetime = Field(default_factory=datetime.now)

    # Export format
    export_format: str = "pdf"  # pdf, docx, html


# =============================================================================
# Medication Reconciliation
# =============================================================================

class ReconciledMedication(BaseModel):
    """Single reconciled medication"""
    medication_name: str
    admission_medication: Optional[str] = None
    home_medication: Optional[str] = None
    reconciled_medication: str
    reconciliation_status: MedicationReconciliationStatus
    reason_for_change: Optional[str] = None


class MedicationReconciliation(BaseModel):
    """Medication reconciliation at discharge"""
    admission_id: int
    patient_id: int
    pharmacist_id: int
    physician_id: int

    # Reconciliation date
    reconciliation_date: date

    # Medications to continue
    medications_to_continue: List[ReconciledMedication]

    # Medications to discontinue
    medications_to_discontinue: List[ReconciledMedication]

    # Medications to change
    medications_to_change: List[ReconciledMedication]

    # New medications at discharge
    new_medications: List[ReconciledMedication]

    # Reconciliation notes
    reconciliation_notes: Optional[str] = None

    # Pharmacist notes
    pharmacist_notes: Optional[str] = None

    # Verified by
    verified_by_physician: bool = False
    verified_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Follow-up Appointment
# =============================================================================

class FollowUpAppointment(BaseModel):
    """Follow-up appointment"""
    admission_id: int
    patient_id: int
    scheduled_by_id: int

    # Appointment details
    appointment_type: FollowUpType
    specialty: str  # e.g., "Cardiology", "Surgery", "Internal Medicine"
    physician_name: Optional[str] = None

    # Schedule
    appointment_date: date
    appointment_time: str  # HH:MM format

    # Location/Contact
    location: Optional[str] = None  # Clinic name, room number
    contact_number: Optional[str] = None
    video_link: Optional[str] = None  # For video follow-up

    # Purpose
    purpose: str  # e.g., "Post-operative check", "Wound assessment", "Lab review"

    # Priority
    priority: str = "routine"  # routine, urgent, emergency

    # Reminders
    send_reminder: bool = True
    reminder_method: Optional[List[str]] = None  # sms, email, phone

    # Notes
    notes: Optional[str] = None

    # Confirmation
    confirmed: bool = False
    confirmed_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# BPJS Claim Finalization
# =============================================================================

class BPJSClaimFinalization(BaseModel):
    """BPJS claim finalization at discharge"""
    admission_id: int
    patient_id: int

    # SEP number
    sep_number: str

    # Claim data
    final_diagnosis: str
    procedure_codes: Optional[List[str]] = None  # ICD-9-CM procedure codes
    icd_10_codes: List[str]  # ICD-10 diagnosis codes

    # Service details
    admission_type: str  # rawat inap, rawat gabung, etc.
    class_type: str  # kelas 1, 2, 3, vip, vvip
    bed_type: str  # kelas rawat inap
    room_number: str

    # Dates
    admission_date: datetime
    discharge_date: datetime
    length_of_stay_days: int

    # Professional fees
    doctor_visit_count: int
    doctor_visit_fees: Optional[float] = None
    consultation_fees: Optional[float] = None
    procedure_fees: Optional[float] = None

    // Service charges
    room_charges: Optional[float] = None
    medication_charges: Optional[float] = None
    laboratory_charges: Optional[float] = None
    radiology_charges: Optional[float] = None
    other_charges: Optional[float] = None

    // Total
    total_claim_amount: float

    // Validation
    validated_by: int
    validated_at: Optional[datetime] = None
    validation_notes: Optional[str] = None

    // Submission
    submitted_to_bpjs: bool = False
    submitted_at: Optional[datetime] = None
    claim_submission_number: Optional[str] = None

    // Status
    claim_status: str = "pending"  // pending, approved, rejected, partially_approved

    // Timestamps
    created_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# SEP Closure
# =============================================================================

class SEPClosure(BaseModel):
    """SEP (Surat Eligensi Peserta) closure at discharge"""
    admission_id: int
    patient_id: int

    # SEP details
    sep_number: str

    # Closure details
    closure_reason: str  # completed, transferred, deceased, left_against_advice
    discharge_status: DischargeStatus
    discharge_condition: DischargeCondition

    // Final diagnosis
    final_diagnosis: str
    icd_10_code: str

    // Discharge date
    discharge_date: datetime

    // Length of stay
    length_of_stay_days: int

    // Outcome
    patient_outcome: str  // sembuh, membaik, stabil, memburuk, meninggal

    // Follow-up required
    follow_up_required: bool
    follow_up_instructions: Optional[str] = None

    // Closed by
    closed_by_id: int
    closed_at: Optional[datetime] = None

    // SEP status update confirmation
    sep_updated: bool = False
    sep_update_response: Optional[Dict[str, Any]] = None

    // Timestamps
    created_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Discharge Instructions for Patient
# =============================================================================

class PatientDischargeInstructions(BaseModel):
    """Patient-friendly discharge instructions"""
    admission_id: int
    patient_id: int

    // Summary
    summary: str = Field(..., description="Ringkasan rawat inap")

    // Diagnoses (patient-friendly)
    diagnoses: List[str]

    // Treatments received
    treatments_received: List[str]

    // Discharge medications
    medications: List[Dict[str, str]]  // name, dosage, when_to_take, special_instructions

    // Activity instructions
    activity_instructions: List[str]

    // Diet instructions
    diet_instructions: List[str]

    // Wound care (if applicable)
    wound_care_instructions: Optional[List[str]] = None

    // What to watch for (red flags)
    warning_signs: List[str]

    // When to seek emergency care
    emergency_care_instructions: List[str]

    // Follow-up appointments
    follow_up_appointments: List[Dict[str, Any]]

    // Contact information
    emergency_contact: str
    hospital_contact: str

    // Generated by
    generated_by_id: int

    // Language
    language: str = "id"  // id, en

    // Delivery method
    delivery_method: str = "printed"  // printed, email, sms

    // Timestamps
    created_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Discharge Checklist
# =============================================================================

class DischargeChecklistItem(BaseModel):
    """Single discharge checklist item"""
    item: str
    completed: bool
    completed_by_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


class DischargeChecklist(BaseModel):
    """Discharge criteria checklist"""
    admission_id: int
    patient_id: int

    // Clinical criteria
    clinical_criteria: List[DischargeChecklistItem]

    // Medication criteria
    medication_criteria: List[DischargeChecklistItem]

    // Documentation criteria
    documentation_criteria: List[DischargeChecklistItem]

    // Logistics criteria
    logistics_criteria: List[DischargeChecklistItem]

    // Education criteria
    education_criteria: List[DischargeChecklistItem]

    // Follow-up criteria
    follow_up_criteria: List[DischargeChecklistItem]

    // Overall completion
    all_criteria_met: bool = False

    // Verified by
    verified_by_id: Optional[int] = None
    verified_at: Optional[datetime] = None

    // Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Response Schemas
# =============================================================================

class DischargeReadinessResponse(DischargeReadinessAssessment):
    """Discharge readiness assessment response"""
    id: int
    assessed_by_name: Optional[str] = None


class DischargeOrderResponse(DischargeOrder):
    """Discharge order response"""
    id: int
    physician_name: Optional[str] = None


class DischargeSummaryResponse(DischargeSummary):
    """Discharge summary response"""
    id: int
    generated_by_name: Optional[str] = None
    file_url: Optional[str] = None


class FollowUpAppointmentResponse(FollowUpAppointment):
    """Follow-up appointment response"""
    id: int
    scheduled_by_name: Optional[str] = None


class SEPClosureResponse(SEPClosure):
    """SEP closure response"""
    id: int
    closed_by_name: Optional[str] = None
