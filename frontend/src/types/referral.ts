/**
 * Referral Letter Types for SIMRS
 * Comprehensive type definitions for Indonesian referral letters (Surat Rujukan)
 * Compatible with Indonesian healthcare requirements, BPJS regulations, and referral formats
 */

// ============================================================================
// REFERRAL TYPE ENUMERATIONS
// ============================================================================

/**
 * All Indonesian referral types
 * - INTERNAL: Rujukan Internal - Referral within the same hospital/facility
 * - EXTERNAL: Rujukan Eksternal - Referral to other healthcare facilities
 * - BPJS: Rujukan BPJS - BPJS-specific referral for insured patients
 * - EMERGENCY: Rujukan Gawat Darurat - Emergency referral
 * - FOLLOW_UP: Rujukan Follow-up - Follow-up referral after treatment
 * - SPECIALIST: Rujukan Spesialis - Referral to specialist doctor
 */
export type ReferralType =
  | 'INTERNAL'
  | 'EXTERNAL'
  | 'BPJS'
  | 'EMERGENCY'
  | 'FOLLOW_UP'
  | 'SPECIALIST';

/**
 * Referral priority levels
 * - ROUTINE: Regular priority, non-urgent
 * - URGENT: Urgent but not emergency
 * - EMERGENCY: Emergency/ life-threatening
 * - ASAP: As soon as possible
 */
export type ReferralPriority = 'ROUTINE' | 'URGENT' | 'EMERGENCY' | 'ASAP';

/**
 * Referral status workflow
 */
export type ReferralStatus =
  | 'draft'           // Being edited
  | 'pending'         // Awaiting review/approval
  | 'approved'        // Approved and issued
  | 'printed'         // Printed and given to patient
  | 'acknowledged'    // Received/acknowledged by destination
  | 'completed'       // Patient received care at destination
  | 'cancelled'       // Cancelled before completion
  | 'expired';        // Past validity period

/**
 * Referral format/template
 */
export type ReferralFormat = 'standard' | 'bpjs' | 'emergency' | 'specialist' | 'custom';

/**
 * Destination facility type
 */
export type FacilityType =
  | 'hospital'
  | 'clinic'
  | 'health_center'
  | 'specialist_clinic'
  | 'diagnostic_center'
  | 'laboratory'
  | 'radiology'
  | 'pharmacy'
  | 'practice';

/**
 * BPJS referral tier/level
 */
export type BPJSTier = 'tier_1' | 'tier_2' | 'tier_3';

/**
 * BPJS referral type classification
 */
export type BPJSReferralType =
  | 'rujuk_balik_prb'      // PRB return referral
  | 'rujuk_igd'            // Emergency department referral
  | 'rujuk_spesialis'      // Specialist referral
  | 'rujuk_kontrol'        // Control/follow-up referral
  | 'rujuk_rawat_inap';    // Inpatient care referral

/**
 * Specialization categories for referrals
 */
export type SpecializationCategory =
  | 'internal_medicine'
  | 'pediatrics'
  | 'surgery'
  | 'obgyn'
  | 'cardiology'
  | 'neurology'
  | 'orthopedics'
  | 'ophthalmology'
  | 'ent'
  | 'psychiatry'
  | 'dermatology'
  | 'urology'
  | 'pulmonology'
  | 'radiology'
  | 'anesthesiology'
  | 'other';

// ============================================================================
// PATIENT INFORMATION TYPES
// ============================================================================

/**
 * Patient information for referral
 */
export interface ReferralPatientInfo {
  /** Patient ID */
  patient_id: number;

  /** Medical record number (RM number) */
  medical_record_number: string;

  /** Full name according to registration */
  full_name: string;

  /** NIK - Nomor Induk Kependudukan (16 digits) */
  nik: string;

  /** Date of birth */
  date_of_birth: string;

  /** Age in years */
  age_years: number;

  /** Age in months (for infants) */
  age_months?: number;

  /** Age in days (for newborns) */
  age_days?: number;

  /** Gender */
  gender: 'male' | 'female';

  /** Blood type */
  blood_type?: 'A' | 'B' | 'AB' | 'O' | 'unknown';

  /** Phone number */
  phone: string;

  /** Alternative phone number */
  phone_alternative?: string;

  /** Address */
  address: string;

  /** City/Kabupaten */
  city: string;

  /** Province */
  province: string;

  /** Postal code */
  postal_code?: string;

  /** BPJS number (if applicable) */
  bpjs_number?: string;

  /** BPJS class (1, 2, or 3) */
  bpjs_class?: number;

  /** Insurance provider (if applicable) */
  insurance_provider?: string;

  /** Insurance policy number */
  insurance_policy_number?: string;

  /** Next of kin name */
  next_of_kin_name?: string;

  /** Next of kin relationship */
  next_of_kin_relationship?: string;

  /** Next of kin phone */
  next_of_kin_phone?: string;

  /** Patient allergies */
  allergies?: string[];

  /** Patient comorbidities */
  comorbidities?: string[];
}

/**
 * Patient selection option for referral form
 */
export interface ReferralPatientSelect {
  value: number;
  label: string;
  medical_record_number: string;
  nik: string;
  date_of_birth: string;
  gender: 'male' | 'female';
  age_years: number;
  bpjs_number?: string;
  bpjs_class?: number;
  insurance_provider?: string;
}

// ============================================================================
// REFERRAL DETAILS TYPES
// ============================================================================

/**
 * Referral identification and details
 */
export interface ReferralDetails {
  /** Referral ID */
  id?: number;

  /** Referral number (auto-generated) */
  referral_number?: string;

  /** BPJS referral number (for BPJS referrals) */
  bpjs_referral_number?: string;

  /** Referral type */
  referral_type: ReferralType;

  /** Referral priority */
  priority: ReferralPriority;

  /** Referral format/template */
  format: ReferralFormat;

  /** Referral date */
  referral_date: string;

  /** Referral time */
  referral_time?: string;

  /** Valid from date */
  valid_from: string;

  /** Valid until date */
  valid_until: string;

  /** Reason for referral */
  reason_for_referral: string;

  /** Specific reason details */
  reason_details?: string;

  /** Referral status */
  status: ReferralStatus;

  /** Is urgent referral */
  is_urgent: boolean;

  /** Is emergency referral */
  is_emergency: boolean;

  /** Internal notes (not printed) */
  internal_notes?: string;

  /** Created by (user ID) */
  created_by?: string;

  /** Created at timestamp */
  created_at?: string;

  /** Updated by (user ID) */
  updated_by?: string;

  /** Updated at timestamp */
  updated_at?: string;

  /** Approved by */
  approved_by?: string;

  /** Approved at */
  approved_at?: string;

  /** Printed at */
  printed_at?: string;

  /** Printed by */
  printed_by?: string;
}

/**
 * BPJS-specific referral details
 */
export interface BPJSReferralDetails {
  /** BPJS referral number */
  bpjs_referral_number: string;

  /** BPJS referral type */
  referral_type: BPJSReferralType;

  /** BPJS tier/level */
  tier: BPJSTier;

  /** Referring BPJS facility code */
  referring_facility_code: string;

  /** Destination BPJS facility code */
  destination_facility_code: string;

  /** BPJS patient diagnosis code (ICD-10) */
  diagnosis_code: string;

  /** BPJS procedure code (if applicable) */
  procedure_code?: string;

  /** POLY/Unit name */
  poli_name?: string;

  /** SEP number (Surat Eligibilitas Peserta) */
  sep_number?: string;

  /** SEP date */
  sep_date?: string;

  /** SKDP number (Surat Kontrol Pengobatan Penyakit Kronis) */
  skdp_number?: string;

  /** Is PRB referral (Program Pengelolaan Penyakit Kronis) */
  is_prb: boolean;

  /** PRB number (if applicable) */
  prb_number?: string;

  /** Estimated service cost */
  estimated_cost?: number;

  /** BPJS approval status */
  approval_status: 'pending' | 'approved' | 'rejected';

  /** BPJS approval date */
  approval_date?: string;

  /** BPJS approved by */
  approved_by?: string;
}

// ============================================================================
// DESTINATION FACILITY TYPES
// ============================================================================

/**
 * Destination facility information for referral
 */
export interface DestinationFacility {
  /** Facility ID */
  facility_id?: number;

  /** Facility name */
  facility_name: string;

  /** Facility type */
  facility_type: FacilityType;

  /** BPJS facility code (if applicable) */
  bpjs_facility_code?: string;

  /** Facility license number */
  license_number?: string;

  /** Address */
  address: string;

  /** City/Kabupaten */
  city: string;

  /** Province */
  province: string;

  /** Postal code */
  postal_code?: string;

  /** Phone number */
  phone: string;

  /** Alternative phone */
  phone_alternative?: string;

  /** Fax number */
  fax?: string;

  /** Email */
  email?: string;

  /** Website */
  website?: string;

  /** Destination department/unit */
  department?: string;

  /** Destination specialization */
  specialization?: SpecializationCategory;

  /** Destination doctor name (if specific doctor) */
  doctor_name?: string;

  /** Destination doctor SIP */
  doctor_sip?: string;

  /** Contact person */
  contact_person?: string;

  /** Is BPJS accredited facility */
  is_bpjs_accredited?: boolean;

  /** Distance from current facility (km) */
  distance_km?: number;

  /** Estimated travel time (minutes) */
  estimated_travel_time_minutes?: number;

  /** Notes about facility */
  notes?: string;
}

/**
 * Internal department/unit for internal referrals
 */
export interface InternalDepartment {
  /** Department ID */
  department_id: number;

  /** Department name */
  department_name: string;

  /** Department code */
  department_code: string;

  /** Floor/location */
  location?: string;

  /** Phone extension */
  extension?: string;

  /** Head of department */
  head_of_department?: string;

  /** Operating hours */
  operating_hours?: string;

  /** Is available for referral */
  is_available: boolean;

  /** Notes */
  notes?: string;
}

/**
 * Facility selection option
 */
export interface FacilitySelectOption {
  value: number;
  label: string;
  facility_type: FacilityType;
  city: string;
  province: string;
  bpjs_facility_code?: string;
  is_bpjs_accredited?: boolean;
  specialization?: string;
}

// ============================================================================
// CLINICAL INFORMATION TYPES
// ============================================================================

/**
 * Clinical information for referral
 */
export interface ReferralClinicalInfo {
  /** Primary diagnosis (ICD-10 code) */
  primary_diagnosis_code?: string;

  /** Primary diagnosis (description) */
  primary_diagnosis: string;

  /** Secondary diagnoses */
  secondary_diagnoses?: string[];

  /** ICD-10 codes for secondary diagnoses */
  secondary_diagnosis_codes?: string[];

  /** Chief complaint */
  chief_complaint: string;

  /** History of present illness */
  history_present_illness?: string;

  /** Duration of illness */
  illness_duration?: string;

  /** Severity of condition */
  severity: 'mild' | 'moderate' | 'severe' | 'critical';

  /** Physical examination findings */
  physical_examination?: string;

  /** Vital signs */
  vital_signs?: VitalSigns;

  /** Laboratory findings */
  lab_findings?: string;

  /** Imaging findings */
  imaging_findings?: string;

  /** Other diagnostic findings */
  other_findings?: string;

  /** Treatment given so far */
  treatment_given?: string;

  /** Medications prescribed */
  medications?: MedicationInfo[];

  /** Patient response to treatment */
  treatment_response?: string;

  /** Clinical notes */
  clinical_notes?: string;

  /** Prognosis */
  prognosis?: 'good' | 'fair' | 'guarded' | 'poor';

  /** Recommended investigations at destination */
  recommended_investigations?: string[];

  /** Specific procedures requested */
  procedures_requested?: string[];

  /** Expected outcomes */
  expected_outcomes?: string[];
}

/**
 * Vital signs record
 */
export interface VitalSigns {
  /** Blood pressure systolic (mmHg) */
  blood_pressure_systolic?: number;

  /** Blood pressure diastolic (mmHg) */
  blood_pressure_diastolic?: number;

  /** Heart rate (bpm) */
  heart_rate?: number;

  /** Respiratory rate (breaths/min) */
  respiratory_rate?: number;

  /** Body temperature (°C) */
  temperature?: number;

  /** Oxygen saturation (%) */
  oxygen_saturation?: number;

  /** Weight (kg) */
  weight_kg?: number;

  /** Height (cm) */
  height_cm?: number;

  /** BMI */
  bmi?: number;

  /** Pain score (0-10) */
  pain_score?: number;

  /** Consciousness level (GCS) */
  glasgow_coma_scale?: number;

  /** Blood glucose */
  blood_glucose?: number;
}

/**
 * Medication information
 */
export interface MedicationInfo {
  /** Medication name */
  name: string;

  /** Dosage */
  dosage: string;

  /** Frequency */
  frequency: string;

  /** Route of administration */
  route: 'oral' | 'intravenous' | 'intramuscular' | 'topical' | 'inhalation' | 'other';

  /** Duration */
  duration?: string;

  /** Instructions */
  instructions?: string;

  /** Start date */
  start_date?: string;

  /** End date */
  end_date?: string;
}

/**
 * Attachment information
 */
export interface ReferralAttachment {
  /** Temporary ID (for new attachments) */
  temp_id?: string;

  /** Attachment ID (for saved attachments) */
  id?: number;

  /** Attachment type */
  attachment_type: 'lab_result' | 'imaging' | 'ecg' | 'document' | 'photo' | 'other';

  /** File name */
  file_name: string;

  /** File URL */
  file_url: string;

  /** File size in bytes */
  file_size?: number;

  /** MIME type */
  mime_type?: string;

  /** Description */
  description?: string;

  /** Upload date */
  upload_date?: string;

  /** Is new upload */
  is_new: boolean;

  /** Is deleted */
  is_deleted: boolean;
}

// ============================================================================
// DOCTOR INFORMATION TYPES
// ============================================================================

/**
 * Referring doctor information
 */
export interface ReferringDoctorInfo {
  /** Doctor ID */
  doctor_id: number;

  /** Doctor's full name */
  doctor_name: string;

  /** Doctor's title/degree (e.g., "dr. Sp.PD") */
  doctor_title: string;

  /** Specialization */
  specialization?: string;

  /** Specialization category */
  specialization_category?: SpecializationCategory;

  /** SIP number (Surat Izin Praktik) */
  sip_number: string;

  /** SIP issue date */
  sip_issue_date?: string;

  /** STR number (Surat Tanda Registrasi) */
  str_number?: string;

  /** Medical license number */
  license_number?: string;

  /** Department/Unit */
  department: string;

  /** Phone number */
  phone?: string;

  /** Extension */
  extension?: string;

  /** Email */
  email?: string;

  /** Signature status */
  signature_status: 'pending' | 'digital' | 'wet' | 'stamp_only';

  /** Signature image URL */
  signature_url?: string;

  /** Digital signature ID */
  digital_signature_id?: string;

  /** Date signed */
  date_signed?: string;

  /** Stamp image URL */
  stamp_url?: string;

  /** Notes */
  notes?: string;
}

/**
 * Doctor selection option
 */
export interface ReferralDoctorSelect {
  value: number;
  label: string;
  title: string;
  specialization?: string;
  specialization_category?: SpecializationCategory;
  sip_number: string;
  department: string;
}

// ============================================================================
// FORM STATE TYPES
// ============================================================================

/**
 * Referral form state
 */
export interface ReferralFormState {
  // Referral type and basics
  referral_type: ReferralType;
  priority: ReferralPriority;
  format: ReferralFormat;
  is_urgent: boolean;
  is_emergency: boolean;

  // Patient information
  patient_id: number | null;
  patient_info: ReferralPatientInfo | null;

  // Referral details
  referral_date: string;
  referral_time?: string;
  valid_from: string;
  valid_until: string;
  reason_for_referral: string;
  reason_details?: string;

  // BPJS information (if applicable)
  bpjs_details?: BPJSReferralDetails;

  // Destination facility
  destination_type: 'internal' | 'external';
  destination_facility: DestinationFacility | null;
  internal_department?: InternalDepartment | null;

  // Clinical information
  primary_diagnosis: string;
  primary_diagnosis_code?: string;
  secondary_diagnoses?: string[];
  secondary_diagnosis_codes?: string[];
  chief_complaint: string;
  history_present_illness?: string;
  physical_examination?: string;
  vital_signs?: VitalSigns;
  lab_findings?: string;
  imaging_findings?: string;
  treatment_given?: string;
  treatment_response?: string;
  severity: 'mild' | 'moderate' | 'severe' | 'critical';
  clinical_notes?: string;

  // Attachments
  attachments: ReferralAttachment[];

  // Doctor information
  referring_doctor_id: number | null;
  referring_doctor_info: ReferringDoctorInfo | null;

  // Status tracking
  status: ReferralStatus;
  is_dirty: boolean;
  is_valid: boolean;
  is_submitting: boolean;
  validation_errors: FormValidationError[];

  // Notes
  internal_notes?: string;
}

/**
 * Form validation error
 */
export interface FormValidationError {
  /** Field name with error */
  field: string;

  /** Error message */
  message: string;

  /** Error severity */
  severity: 'error' | 'warning';
}

/**
 * Form action types
 */
export type ReferralFormAction =
  | { type: 'SET_REFERRAL_TYPE'; payload: ReferralType }
  | { type: 'SET_PRIORITY'; payload: ReferralPriority }
  | { type: 'SET_PATIENT'; payload: ReferralPatientInfo }
  | { type: 'SET_DOCTOR'; payload: ReferringDoctorInfo }
  | { type: 'SET_DESTINATION_FACILITY'; payload: DestinationFacility }
  | { type: 'SET_INTERNAL_DEPARTMENT'; payload: InternalDepartment }
  | { type: 'SET_BPJS_DETAILS'; payload: BPJSReferralDetails }
  | { type: 'SET_FIELD'; field: keyof ReferralFormState; value: any }
  | { type: 'ADD_ATTACHMENT'; payload: ReferralAttachment }
  | { type: 'REMOVE_ATTACHMENT'; payload: { temp_id: string } }
  | { type: 'VALIDATE' }
  | { type: 'SUBMIT' }
  | { type: 'RESET' };

// ============================================================================
// VALIDATION CONSTRAINTS
// ============================================================================

/**
 * Referral validation constraints
 */
export interface ReferralValidationConstraints {
  // Patient constraints
  patient_required: boolean;
  patient_must_have_valid_nik: boolean;

  // Date constraints
  referral_date_min_offset_days: number;
  referral_date_max_offset_days: number;
  valid_from_min_offset_days: number;
  validity_duration_min_days: number;
  validity_duration_max_days: number;

  // Content constraints
  diagnosis_required: boolean;
  diagnosis_min_length: number;
  diagnosis_max_length: number;

  // Reason constraints
  reason_required: boolean;
  reason_min_length: number;
  reason_max_length: number;

  // Chief complaint constraints
  chief_complaint_required: boolean;
  chief_complaint_min_length: number;
  chief_complaint_max_length: number;

  // Doctor constraints
  doctor_required: boolean;
  doctor_must_have_valid_sip: boolean;

  // Facility constraints
  facility_required: boolean;

  // BPJS constraints
  bpjs_number_required_for_bpjs_referral: boolean;

  // Attachment constraints
  attachment_max_size_mb: number;
  attachment_allowed_types: string[];
  max_attachments: number;

  // Notes constraints
  notes_max_length: number;
  internal_notes_max_length: number;
}

/**
 * Default validation constraints for Indonesian healthcare
 */
export const DEFAULT_REFERRAL_VALIDATION_CONSTRAINTS: ReferralValidationConstraints = {
  // Patient
  patient_required: true,
  patient_must_have_valid_nik: true,

  // Dates
  referral_date_min_offset_days: -7,
  referral_date_max_offset_days: 7,
  valid_from_min_offset_days: -30,
  validity_duration_min_days: 1,
  validity_duration_max_days: 180, // 6 months

  // Content
  diagnosis_required: true,
  diagnosis_min_length: 3,
  diagnosis_max_length: 500,

  // Reason
  reason_required: true,
  reason_min_length: 10,
  reason_max_length: 1000,

  // Chief complaint
  chief_complaint_required: true,
  chief_complaint_min_length: 5,
  chief_complaint_max_length: 500,

  // Doctor
  doctor_required: true,
  doctor_must_have_valid_sip: true,

  // Facility
  facility_required: true,

  // BPJS
  bpjs_number_required_for_bpjs_referral: true,

  // Attachments
  attachment_max_size_mb: 10,
  attachment_allowed_types: [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/jpg'
  ],
  max_attachments: 20,

  // Notes
  notes_max_length: 2000,
  internal_notes_max_length: 3000,
};

// ============================================================================
// API REQUEST/RESPONSE TYPES
// ============================================================================

/**
 * Create referral request
 */
export interface CreateReferralRequest {
  referral_type: ReferralType;
  priority: ReferralPriority;
  format: ReferralFormat;
  patient_id: number;
  doctor_id: number;
  referral_date: string;
  referral_time?: string;
  valid_from: string;
  valid_until: string;
  reason_for_referral: string;
  reason_details?: string;

  // Destination
  destination_type: 'internal' | 'external';
  destination_facility_id?: number;
  internal_department_id?: number;

  // BPJS information (if applicable)
  bpjs_details?: BPJSReferralDetails;

  // Clinical information
  primary_diagnosis: string;
  primary_diagnosis_code?: string;
  secondary_diagnoses?: string[];
  secondary_diagnosis_codes?: string[];
  chief_complaint: string;
  history_present_illness?: string;
  physical_examination?: string;
  vital_signs?: VitalSigns;
  lab_findings?: string;
  imaging_findings?: string;
  treatment_given?: string;
  treatment_response?: string;
  severity: 'mild' | 'moderate' | 'severe' | 'critical';
  clinical_notes?: string;

  // Attachments
  attachment_urls?: string[];

  // Notes
  internal_notes?: string;
}

/**
 * Create referral response
 */
export interface CreateReferralResponse {
  success: boolean;
  data?: {
    /** Generated referral ID */
    referral_id: number;

    /** Referral number */
    referral_number: string;

    /** BPJS referral number (if applicable) */
    bpjs_referral_number?: string;

    /** Referral details */
    referral: ReferralLetter;
  };
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * Update referral request
 */
export interface UpdateReferralRequest extends Partial<CreateReferralRequest> {
  id: number;
}

/**
 * Referral list query parameters
 */
export interface ReferralListQuery {
  page?: number;
  per_page?: number;
  referral_type?: ReferralType;
  status?: ReferralStatus;
  priority?: ReferralPriority;
  patient_id?: number;
  doctor_id?: number;
  destination_facility_id?: number;
  start_date?: string;
  end_date?: string;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

/**
 * Referral list response
 */
export interface ReferralListResponse {
  items: ReferralSummary[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

/**
 * Complete referral letter structure
 */
export interface ReferralLetter {
  id: number;
  referral_number: string;
  bpjs_referral_number?: string;
  referral_type: ReferralType;
  priority: ReferralPriority;
  format: ReferralFormat;

  // Patient
  patient: ReferralPatientInfo;

  // Referral details
  referral_date: string;
  referral_time?: string;
  valid_from: string;
  valid_until: string;
  reason_for_referral: string;
  reason_details?: string;

  // BPJS information (if applicable)
  bpjs_details?: BPJSReferralDetails;

  // Destination
  destination_type: 'internal' | 'external';
  destination_facility?: DestinationFacility;
  internal_department?: InternalDepartment;

  // Clinical information
  primary_diagnosis: string;
  primary_diagnosis_code?: string;
  secondary_diagnoses?: string[];
  secondary_diagnosis_codes?: string[];
  chief_complaint: string;
  history_present_illness?: string;
  physical_examination?: string;
  vital_signs?: VitalSigns;
  lab_findings?: string;
  imaging_findings?: string;
  treatment_given?: string;
  treatment_response?: string;
  severity: 'mild' | 'moderate' | 'severe' | 'critical';
  clinical_notes?: string;

  // Referring doctor
  referring_doctor: ReferringDoctorInfo;

  // Status
  status: ReferralStatus;
  is_urgent: boolean;
  is_emergency: boolean;

  // Attachments
  attachments?: ReferralAttachment[];

  // Notes
  internal_notes?: string;

  // Metadata
  created_by: string;
  created_at: string;
  updated_by?: string;
  updated_at?: string;
  approved_by?: string;
  approved_at?: string;
  printed_at?: string;
  printed_by?: string;
  acknowledged_at?: string;
  completed_at?: string;
}

/**
 * Referral summary for list view
 */
export interface ReferralSummary {
  id: number;
  referral_number: string;
  bpjs_referral_number?: string;
  referral_type: ReferralType;
  priority: ReferralPriority;
  referral_date: string;
  valid_until: string;
  patient_name: string;
  medical_record_number: string;
  doctor_name: string;
  destination_facility: string;
  primary_diagnosis: string;
  status: ReferralStatus;
  is_urgent: boolean;
  is_emergency: boolean;
  is_expired: boolean;
  days_until_expiry: number;
  created_at: string;
}

/**
 * Referral print request
 */
export interface PrintReferralRequest {
  referral_id: number;
  copies: number;
  printer_name?: string;
  duplex?: boolean;
  color?: boolean;
  include_attachments?: boolean;
}

/**
 * Referral print response
 */
export interface PrintReferralResponse {
  success: boolean;
  data?: {
    print_job_id?: string;
    print_url?: string;
    referral_url: string;
    qr_code_url?: string;
  };
  message?: string;
  error?: {
    code: string;
    message: string;
  };
}

/**
 * Referral statistics
 */
export interface ReferralStatistics {
  today_total: number;
  today_by_type: Record<ReferralType, number>;
  pending: number;
  approved: number;
  printed: number;
  acknowledged: number;
  completed: number;
  cancelled: number;
  expired: number;
  this_week: number;
  this_month: number;
  by_priority: Record<ReferralPriority, number>;
  by_status: Record<ReferralStatus, number>;
}

/**
 * Referral validation result
 */
export interface ReferralValidationResult {
  is_valid: boolean;
  field_errors: Array<{
    field: string;
    errors: string[];
  }>;
  general_errors: string[];
  warnings: string[];
}

/**
 * BPJS referral eligibility check
 */
export interface BPJSEligibilityCheck {
  bpjs_number: string;
  is_eligible: boolean;
  membership_status: string;
  membership_tier: BPJSTier;
  facility_code: string;
  facility_name: string;
  referral_quota_remaining: number;
  referral_quota_used: number;
  referral_quota_total: number;
  last_referral_date?: string;
  can_make_referral: boolean;
  rejection_reason?: string;
}

/**
 * BPJS referral submission response
 */
export interface BPJSReferralSubmission {
  success: boolean;
  bpjs_referral_number?: string;
  approval_code?: string;
  approval_date?: string;
  valid_from?: string;
  valid_until?: string;
  error_code?: string;
  error_message?: string;
}

// ============================================================================
// HELPER TYPES
// ============================================================================

/**
 * Referral type with Indonesian label
 */
export interface ReferralTypeOption {
  value: ReferralType;
  label: string;
  label_indonesian: string;
  description: string;
}

/**
 * Referral type options with labels
 */
export const REFERRAL_TYPE_OPTIONS: ReferralTypeOption[] = [
  {
    value: 'INTERNAL',
    label: 'Internal Referral',
    label_indonesian: 'Rujukan Internal',
    description: 'Referral within the same hospital/facility',
  },
  {
    value: 'EXTERNAL',
    label: 'External Referral',
    label_indonesian: 'Rujukan Eksternal',
    description: 'Referral to other healthcare facilities',
  },
  {
    value: 'BPJS',
    label: 'BPJS Referral',
    label_indonesian: 'Rujukan BPJS',
    description: 'BPJS-specific referral for insured patients',
  },
  {
    value: 'EMERGENCY',
    label: 'Emergency Referral',
    label_indonesian: 'Rujukan Gawat Darurat',
    description: 'Emergency/life-threatening referral',
  },
  {
    value: 'FOLLOW_UP',
    label: 'Follow-up Referral',
    label_indonesian: 'Rujukan Follow-up',
    description: 'Follow-up referral after treatment',
  },
  {
    value: 'SPECIALIST',
    label: 'Specialist Referral',
    label_indonesian: 'Rujukan Spesialis',
    description: 'Referral to specialist doctor',
  },
];

/**
 * Get referral type label in Indonesian
 */
export function getReferralTypeLabel(type: ReferralType): string {
  return REFERRAL_TYPE_OPTIONS.find(opt => opt.value === type)?.label_indonesian || type;
}

/**
 * Referral priority with Indonesian label
 */
export interface ReferralPriorityOption {
  value: ReferralPriority;
  label: string;
  label_indonesian: string;
  color: string;
}

/**
 * Referral priority options
 */
export const REFERRAL_PRIORITY_OPTIONS: ReferralPriorityOption[] = [
  {
    value: 'ROUTINE',
    label: 'Routine',
    label_indonesian: 'Rutin',
    color: 'green',
  },
  {
    value: 'URGENT',
    label: 'Urgent',
    label_indonesian: 'Urgent',
    color: 'orange',
  },
  {
    value: 'EMERGENCY',
    label: 'Emergency',
    label_indonesian: 'Gawat Darurat',
    color: 'red',
  },
  {
    value: 'ASAP',
    label: 'ASAP',
    label_indonesian: 'Segera',
    color: 'yellow',
  },
];

/**
 * Referral status with Indonesian label
 */
export interface ReferralStatusOption {
  value: ReferralStatus;
  label: string;
  label_indonesian: string;
  color: string;
}

/**
 * Referral status options
 */
export const REFERRAL_STATUS_OPTIONS: ReferralStatusOption[] = [
  {
    value: 'draft',
    label: 'Draft',
    label_indonesian: 'Konsep',
    color: 'gray',
  },
  {
    value: 'pending',
    label: 'Pending',
    label_indonesian: 'Menunggu',
    color: 'yellow',
  },
  {
    value: 'approved',
    label: 'Approved',
    label_indonesian: 'Disetujui',
    color: 'blue',
  },
  {
    value: 'printed',
    label: 'Printed',
    label_indonesian: 'Dicetak',
    color: 'green',
  },
  {
    value: 'acknowledged',
    label: 'Acknowledged',
    label_indonesian: 'Diterima',
    color: 'cyan',
  },
  {
    value: 'completed',
    label: 'Completed',
    label_indonesian: 'Selesai',
    color: 'emerald',
  },
  {
    value: 'cancelled',
    label: 'Cancelled',
    label_indonesian: 'Dibatalkan',
    color: 'red',
  },
  {
    value: 'expired',
    label: 'Expired',
    label_indonesian: 'Kadaluarsa',
    color: 'orange',
  },
];

/**
 * Specialization category with Indonesian label
 */
export interface SpecializationCategoryOption {
  value: SpecializationCategory;
  label: string;
  label_indonesian: string;
}

/**
 * Specialization category options
 */
export const SPECIALIZATION_CATEGORY_OPTIONS: SpecializationCategoryOption[] = [
  {
    value: 'internal_medicine',
    label: 'Internal Medicine',
    label_indonesian: 'Penyakit Dalam',
  },
  {
    value: 'pediatrics',
    label: 'Pediatrics',
    label_indonesian: 'Anak',
  },
  {
    value: 'surgery',
    label: 'Surgery',
    label_indonesian: 'Bedah',
  },
  {
    value: 'obgyn',
    label: 'Obstetrics & Gynecology',
    label_indonesian: 'Kandungan',
  },
  {
    value: 'cardiology',
    label: 'Cardiology',
    label_indonesian: 'Jantung',
  },
  {
    value: 'neurology',
    label: 'Neurology',
    label_indonesian: 'Saraf',
  },
  {
    value: 'orthopedics',
    label: 'Orthopedics',
    label_indonesian: 'Orthopedi',
  },
  {
    value: 'ophthalmology',
    label: 'Ophthalmology',
    label_indonesian: 'Mata',
  },
  {
    value: 'ent',
    label: 'ENT',
    label_indonesian: 'THT',
  },
  {
    value: 'psychiatry',
    label: 'Psychiatry',
    label_indonesian: 'Jiwa',
  },
  {
    value: 'dermatology',
    label: 'Dermatology',
    label_indonesian: 'Kulit & Kelamin',
  },
  {
    value: 'urology',
    label: 'Urology',
    label_indonesian: 'Urologi',
  },
  {
    value: 'pulmonology',
    label: 'Pulmonology',
    label_indonesian: 'Paru',
  },
  {
    value: 'radiology',
    label: 'Radiology',
    label_indonesian: 'Radiologi',
  },
  {
    value: 'anesthesiology',
    label: 'Anesthesiology',
    label_indonesian: 'Anestesi',
  },
  {
    value: 'other',
    label: 'Other',
    label_indonesian: 'Lainnya',
  },
];

/**
 * Facility type with Indonesian label
 */
export interface FacilityTypeOption {
  value: FacilityType;
  label: string;
  label_indonesian: string;
}

/**
 * Facility type options
 */
export const FACILITY_TYPE_OPTIONS: FacilityTypeOption[] = [
  {
    value: 'hospital',
    label: 'Hospital',
    label_indonesian: 'Rumah Sakit',
  },
  {
    value: 'clinic',
    label: 'Clinic',
    label_indonesian: 'Klinik',
  },
  {
    value: 'health_center',
    label: 'Health Center',
    label_indonesian: 'Puskesmas',
  },
  {
    value: 'specialist_clinic',
    label: 'Specialist Clinic',
    label_indonesian: 'Klinik Spesialis',
  },
  {
    value: 'diagnostic_center',
    label: 'Diagnostic Center',
    label_indonesian: 'Pusat Diagnostik',
  },
  {
    value: 'laboratory',
    label: 'Laboratory',
    label_indonesian: 'Laboratorium',
  },
  {
    value: 'radiology',
    label: 'Radiology',
    label_indonesian: 'Radiologi',
  },
  {
    value: 'pharmacy',
    label: 'Pharmacy',
    label_indonesian: 'Apotek',
  },
  {
    value: 'practice',
    label: 'Medical Practice',
    label_indonesian: 'Praktek Dokter',
  },
];

/**
 * BPJS referral type with Indonesian label
 */
export interface BPJSReferralTypeOption {
  value: BPJSReferralType;
  label: string;
  label_indonesian: string;
  description: string;
}

/**
 * BPJS referral type options
 */
export const BPJS_REFERRAL_TYPE_OPTIONS: BPJSReferralTypeOption[] = [
  {
    value: 'rujuk_balik_prb',
    label: 'PRB Return Referral',
    label_indonesian: 'Rujuk Balik PRB',
    description: 'Chronic disease management return referral',
  },
  {
    value: 'rujuk_igd',
    label: 'Emergency Department Referral',
    label_indonesian: 'Rujukan IGD',
    description: 'Emergency department referral',
  },
  {
    value: 'rujuk_spesialis',
    label: 'Specialist Referral',
    label_indonesian: 'Rujukan Spesialis',
    description: 'Referral to specialist doctor',
  },
  {
    value: 'rujuk_kontrol',
    label: 'Control Referral',
    label_indonesian: 'Rujukan Kontrol',
    description: 'Follow-up/control referral',
  },
  {
    value: 'rujuk_rawat_inap',
    label: 'Inpatient Referral',
    label_indonesian: 'Rujukan Rawat Inap',
    description: 'Referral for inpatient care',
  },
];
