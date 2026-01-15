/**
 * Medical Certificate Types for SIMRS
 * Comprehensive type definitions for Indonesian medical certificates (Surat Medis)
 * Compatible with Indonesian healthcare requirements and regulations
 */

// ============================================================================
// CERTIFICATE TYPE ENUMERATIONS
// ============================================================================

/**
 * All Indonesian medical certificate types
 * - SICK_LEAVE: Surat Sakit - Certificate for sick leave from work/school
 * - MEDICAL_FITNESS: Surat Keterangan Sehat - General health certificate
 * - FIT_FOR_WORK: Surat Keterangan Fit untuk Bekerja - Fit to work certificate
 * - PREGNANCY: Surat Keterangan Hamil - Pregnancy certificate
 * - HEALTHY_CHILD: Surat Keterangan Anak Sehat - Healthy child certificate
 * - DEATH: Surat Keterangan Kematian - Death certificate
 * - MEDICAL_REPORT: Surat Keterangan Medis - General medical report
 */
export type CertificateType =
  | 'SICK_LEAVE'
  | 'MEDICAL_FITNESS'
  | 'FIT_FOR_WORK'
  | 'PREGNANCY'
  | 'HEALTHY_CHILD'
  | 'DEATH'
  | 'MEDICAL_REPORT';

/**
 * Certificate status workflow
 */
export type CertificateStatus =
  | 'draft'        // Being edited
  | 'pending'      // Awaiting approval/signature
  | 'approved'     // Approved and signed
  | 'printed'      // Printed and issued
  | 'void'         // Cancelled/voided
  | 'expired';     // Past validity period

/**
 * Certificate template format
 */
export type CertificateFormat = 'standard' | 'bpjs' | 'insurance' | 'custom';

/**
 * Signature status
 */
export type SignatureStatus = 'pending' | 'digital' | 'wet' | 'stamp_only';

// ============================================================================
// PATIENT INFORMATION TYPES
// ============================================================================

/**
 * Patient information for medical certificate
 */
export interface CertificatePatientInfo {
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
  blood_type: 'A' | 'B' | 'AB' | 'O' | 'unknown';

  /** Phone number */
  phone: string;

  /** Address */
  address: string;

  /** City/Kabupaten */
  city: string;

  /** Province */
  province: string;

  /** Occupation (required for work-related certificates) */
  occupation?: string;

  /** Workplace/School name (for fit for work/school certificates) */
  workplace_name?: string;

  /** Workplace/School address */
  workplace_address?: string;

  /** BPJS number (if applicable) */
  bpjs_number?: string;

  /** Insurance provider (if applicable) */
  insurance_provider?: string;
}

/**
 * Patient selection option for certificate form
 */
export interface CertificatePatientSelect {
  value: number;
  label: string;
  medical_record_number: string;
  nik: string;
  date_of_birth: string;
  gender: 'male' | 'female';
  age_years: number;
  bpjs_number?: string;
  insurance_provider?: string;
}

// ============================================================================
// CERTIFICATE DETAILS TYPES
// ============================================================================

/**
 * Certificate identification and issue details
 */
export interface CertificateDetails {
  /** Certificate ID */
  id?: number;

  /** Certificate number (auto-generated) */
  certificate_number?: string;

  /** Certificate type */
  certificate_type: CertificateType;

  /** Certificate format */
  format: CertificateFormat;

  /** Issue date (date of examination) */
  issue_date: string;

  /** Examination start time */
  examination_time?: string;

  /** Valid from date (can differ from issue date) */
  valid_from: string;

  /** Valid until date */
  valid_until: string;

  /** Duration in days (for sick leave) */
  duration_days?: number;

  /** Purpose of certificate (e.g., "Untuk keperluan kerja") */
  purpose: string;

  /** Is for official use (e.g., BPJS, insurance) */
  is_official: boolean;

  /** Number of copies */
  copies: number;

  /** Certificate status */
  status: CertificateStatus;

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
}

/**
 * Sick leave specific details
 */
export interface SickLeaveDetails {
  /** Duration in days */
  duration_days: number;

  /** Start date of leave */
  start_date: string;

  /** End date of leave */
  end_date: string;

  /** Must rest at home (rawat inap) */
  must_rest_at_home: boolean;

  /** Must be hospitalized (rawat inap) */
  requires_hospitalization: boolean;

  /** Can do light activities */
  can_do_light_activities: boolean;

  /** Follow-up required */
  requires_follow_up: boolean;

  /** Follow-up date */
  follow_up_date?: string;

  /** Return to work restrictions */
  restrictions?: string[];
}

/**
 * Medical fitness specific details
 */
export interface MedicalFitnessDetails {
  /** General health status */
  health_status: 'fit' | 'fit_with_restrictions' | 'unfit';

  /** Specific fitness category */
  fitness_category?: 'general' | 'driving' | 'heavy_machinery' | 'sports' | 'travel';

  /** Restrictions or limitations */
  restrictions?: string[];

  /** Recommendations */
  recommendations?: string[];

  /** Next check-up date */
  next_checkup_date?: string;

  /** Validity period for fitness certificate */
  validity_months?: number;
}

/**
 * Pregnancy certificate specific details
 */
export interface PregnancyDetails {
  /** Pregnancy age in weeks */
  gestational_age_weeks: number;

  /** Pregnancy age in days */
  gestational_age_days?: number;

  /** Estimated due date (HPL) */
  estimated_due_date: string;

  /** Current pregnancy status */
  pregnancy_status: 'normal' | 'high_risk' | 'complicated';

  /** Number of fetuses */
  fetus_count: number;

  /** Fetal heart rate detected */
  fetal_heart_rate?: number;

  /** Ultrasound findings */
  ultrasound_findings?: string;

  /** Recommendations */
  recommendations?: string[];

  /** Next ANC visit date */
  next_anc_date?: string;
}

/**
 * Healthy child certificate specific details
 */
export interface HealthyChildDetails {
  /** Child's age in months */
  age_months: number;

  /** Weight in kg */
  weight_kg: number;

  /** Height in cm */
  height_cm: number;

  /** Head circumference in cm */
  head_circumference_cm?: number;

  /** Nutritional status */
  nutritional_status: 'good' | 'underweight' | 'overweight' | 'obese';

  /** Development status */
  development_status: 'normal' | 'delayed' | 'advanced';

  /** Vaccination status */
  vaccination_status: 'complete' | 'incomplete' | 'unknown';

  /** Last vaccination date */
  last_vaccination_date?: string;

  /** Recommended vaccinations */
  recommended_vaccinations?: string[];

  /** Developmental milestones achieved */
  milestones?: string[];
}

/**
 * Death certificate specific details
 */
export interface DeathDetails {
  /** Date and time of death */
  death_datetime: string;

  /** Place of death */
  place_of_death: string;

  /** Cause of death (primary) */
  cause_of_death_primary: string;

  /** Cause of death (secondary/complications) */
  cause_of_death_secondary?: string;

  /** Manner of death */
  manner_of_death: 'natural' | 'accident' | 'suicide' | 'homicide' | 'pending_investigation' | 'unknown';

  /** Was autopsy performed */
  autopsy_performed: boolean;

  /** Autopsy findings (if applicable) */
  autopsy_findings?: string;

  /** Was death reported to authorities */
  reported_to_authorities: boolean;

  /** Police report number (if applicable) */
  police_report_number?: string;

  /** Body released to */
  body_released_to: string;

  /** Relationship to deceased */
  relationship_to_deceased: string;

  /** Burial permit number */
  burial_permit_number?: string;
}

/**
 * Medical report specific details
 */
export interface MedicalReportDetails {
  /** Report category */
  report_category: string;

  /** Examination type */
  examination_type: string;

  /** Examination findings */
  findings: string;

  /** Diagnosis/Conclusion */
  diagnosis: string;

  ** Recommendations */
  recommendations?: string[];

  /** Prognosis */
  prognosis?: string;

  /** Attached investigations (lab, imaging) */
  attached_investigations?: string[];

  /** Report confidentiality level */
  confidentiality: 'normal' | 'confidential' | 'strict';
}

// ============================================================================
// CLINICAL INFORMATION TYPES
// ============================================================================

/**
 * Clinical information for certificate
 */
export interface CertificateClinicalInfo {
  /** Primary diagnosis (ICD-10 code) */
  primary_diagnosis_code?: string;

  /** Primary diagnosis (description) */
  primary_diagnosis: string;

  /** Secondary diagnoses */
  secondary_diagnoses?: string[];

  /** ICD-10 codes for secondary diagnoses */
  secondary_diagnosis_codes?: string[];

  /** Chief complaint */
  chief_complaint?: string;

  /** History of present illness */
  history_present_illness?: string;

  /** Physical examination findings */
  physical_examination?: string;

  /** Vital signs */
  vital_signs?: VitalSigns;

  ** Laboratory findings */
  lab_findings?: string;

  /** Imaging findings */
  imaging_findings?: string;

  /** Other diagnostic findings */
  other_findings?: string;

  /** Treatment given */
  treatment_given?: string;

  ** Medications prescribed */
  medications?: MedicationInfo[];

  /** Clinical notes */
  clinical_notes?: string;
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
}

/**
 * Examination information
 */
export interface ExaminationInfo {
  /** Examination date */
  examination_date: string;

  /** Examination type */
  examination_type: string;

  /** Examination findings */
  findings: string;

  ** Examiner name */
  examiner_name?: string;

  /** Examiner ID */
  examiner_id?: number;

  /** Attachment URLs (images, documents) */
  attachments?: string[];
}

// ============================================================================
// DOCTOR INFORMATION TYPES
// ============================================================================

/**
 * Doctor information for certificate
 */
export interface CertificateDoctorInfo {
  /** Doctor ID */
  doctor_id: number;

  /** Doctor's full name */
  doctor_name: string;

  /** Doctor's title/degree (e.g., "dr. Sp.PD") */
  doctor_title: string;

  /** Specialization */
  specialization?: string;

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

  /** Signature status */
  signature_status: SignatureStatus;

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
export interface CertificateDoctorSelect {
  value: number;
  label: string;
  title: string;
  specialization?: string;
  sip_number: string;
  department: string;
}

// ============================================================================
// FACILITY INFORMATION TYPES
// ============================================================================

/**
 * Facility information for certificate
 */
export interface CertificateFacilityInfo {
  /** Facility ID */
  facility_id: number;

  /** Facility name */
  facility_name: string;

  /** Facility type */
  facility_type: 'hospital' | 'clinic' | 'health_center' | 'practice';

  /** License number */
  license_number?: string;

  /** Address */
  address: string;

  /** City/Kabupaten */
  city: string;

  /** Province */
  province: string;

  /** Postal code */
  postal_code: string;

  /** Phone number */
  phone: string;

  /** Email */
  email?: string;

  /** Website */
  website?: string;

  /** Logo URL */
  logo_url?: string;

  /** Stamp URL */
  stamp_url?: string;

  /** BPJS facility code (if applicable) */
  bpjs_facility_code?: string;

  /** Is BPJS accredited facility */
  is_bpjs_accredited: boolean;
}

// ============================================================================
// FORM STATE TYPES
// ============================================================================

/**
 * Medical certificate form state
 */
export interface MedicalCertificateFormState {
  // Certificate type and basics
  certificate_type: CertificateType;
  format: CertificateFormat;
  purpose: string;
  is_official: boolean;
  copies: number;

  // Patient information
  patient_id: number | null;
  patient_info: CertificatePatientInfo | null;

  // Certificate details
  issue_date: string;
  examination_time?: string;
  valid_from: string;
  valid_until: string;
  duration_days?: number;

  // Type-specific details
  sick_leave_details?: SickLeaveDetails;
  medical_fitness_details?: MedicalFitnessDetails;
  pregnancy_details?: PregnancyDetails;
  healthy_child_details?: HealthyChildDetails;
  death_details?: DeathDetails;
  medical_report_details?: MedicalReportDetails;

  // Clinical information
  primary_diagnosis: string;
  primary_diagnosis_code?: string;
  secondary_diagnoses?: string[];
  secondary_diagnosis_codes?: string[];
  chief_complaint?: string;
  physical_examination?: string;
  vital_signs?: VitalSigns;
  lab_findings?: string;
  imaging_findings?: string;
  clinical_notes?: string;

  // Doctor information
  doctor_id: number | null;
  doctor_info: CertificateDoctorInfo | null;

  // Facility information (auto-filled from current facility)
  facility_info: CertificateFacilityInfo;

  // Attachments
  attachments: CertificateAttachment[];

  // Status tracking
  status: CertificateStatus;
  is_dirty: boolean;
  is_valid: boolean;
  is_submitting: boolean;
  validation_errors: FormValidationError[];

  // Notes
  internal_notes?: string;
}

/**
 * Certificate attachment
 */
export interface CertificateAttachment {
  /** Temporary ID (for new attachments) */
  temp_id?: string;

  /** Attachment ID (for saved attachments) */
  id?: number;

  /** Attachment type */
  attachment_type: 'lab_result' | 'imaging' | 'document' | 'photo' | 'other';

  /** File name */
  file_name: string;

  /** File URL */
  file_url: string;

  /** File size in bytes */
  file_size?: number;

  /** MIME type */
  mime_type?: string;

  /** Upload date */
  upload_date?: string;

  /** Is new upload */
  is_new: boolean;

  /** Is deleted */
  is_deleted: boolean;
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
export type MedicalCertificateFormAction =
  | { type: 'SET_CERTIFICATE_TYPE'; payload: CertificateType }
  | { type: 'SET_PATIENT'; payload: CertificatePatientInfo }
  | { type: 'SET_DOCTOR'; payload: CertificateDoctorInfo }
  | { type: 'SET_FIELD'; field: keyof MedicalCertificateFormState; value: any }
  | { type: 'SET_SICK_LEAVE_DETAILS'; payload: SickLeaveDetails }
  | { type: 'SET_MEDICAL_FITNESS_DETAILS'; payload: MedicalFitnessDetails }
  | { type: 'SET_PREGNANCY_DETAILS'; payload: PregnancyDetails }
  | { type: 'SET_HEALTHY_CHILD_DETAILS'; payload: HealthyChildDetails }
  | { type: 'SET_DEATH_DETAILS'; payload: DeathDetails }
  | { type: 'SET_MEDICAL_REPORT_DETAILS'; payload: MedicalReportDetails }
  | { type: 'ADD_ATTACHMENT'; payload: CertificateAttachment }
  | { type: 'REMOVE_ATTACHMENT'; payload: { temp_id: string } }
  | { type: 'VALIDATE' }
  | { type: 'SUBMIT' }
  | { type: 'RESET' };

// ============================================================================
// VALIDATION CONSTRAINTS
// ============================================================================

/**
 * Medical certificate validation constraints
 */
export interface CertificateValidationConstraints {
  // Patient constraints
  patient_required: boolean;
  patient_must_have_valid_nik: boolean;

  // Date constraints
  issue_date_min_offset_days: number;
  issue_date_max_offset_days: number;
  valid_from_min_offset_days: number;
  validity_duration_min_days: number;
  validity_duration_max_days: number;

  // Sick leave constraints
  sick_leave_max_days: number;
  sick_leave_min_days: number;

  // Content constraints
  diagnosis_required: boolean;
  diagnosis_min_length: number;
  diagnosis_max_length: number;

  // Purpose constraints
  purpose_required: boolean;
  purpose_min_length: number;
  purpose_max_length: number;

  // Doctor constraints
  doctor_required: boolean;
  doctor_must_have_valid_sip: boolean;

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
export const DEFAULT_CERTIFICATE_VALIDATION_CONSTRAINTS: CertificateValidationConstraints = {
  // Patient
  patient_required: true,
  patient_must_have_valid_nik: true,

  // Dates
  issue_date_min_offset_days: -7,
  issue_date_max_offset_days: 7,
  valid_from_min_offset_days: -30,
  validity_duration_min_days: 1,
  validity_duration_max_days: 365,

  // Sick leave
  sick_leave_min_days: 1,
  sick_leave_max_days: 90,

  // Content
  diagnosis_required: true,
  diagnosis_min_length: 3,
  diagnosis_max_length: 500,

  // Purpose
  purpose_required: true,
  purpose_min_length: 5,
  purpose_max_length: 200,

  // Doctor
  doctor_required: true,
  doctor_must_have_valid_sip: true,

  // Attachments
  attachment_max_size_mb: 10,
  attachment_allowed_types: [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/jpg'
  ],
  max_attachments: 10,

  // Notes
  notes_max_length: 1000,
  internal_notes_max_length: 2000,
};

// ============================================================================
// API REQUEST/RESPONSE TYPES
// ============================================================================

/**
 * Create certificate request
 */
export interface CreateCertificateRequest {
  certificate_type: CertificateType;
  format: CertificateFormat;
  patient_id: number;
  doctor_id: number;
  issue_date: string;
  valid_from: string;
  valid_until: string;
  purpose: string;
  is_official: boolean;
  copies: number;

  // Type-specific details
  sick_leave_details?: SickLeaveDetails;
  medical_fitness_details?: MedicalFitnessDetails;
  pregnancy_details?: PregnancyDetails;
  healthy_child_details?: HealthyChildDetails;
  death_details?: DeathDetails;
  medical_report_details?: MedicalReportDetails;

  // Clinical information
  primary_diagnosis: string;
  primary_diagnosis_code?: string;
  secondary_diagnoses?: string[];
  secondary_diagnosis_codes?: string[];
  chief_complaint?: string;
  physical_examination?: string;
  vital_signs?: VitalSigns;
  lab_findings?: string;
  imaging_findings?: string;
  clinical_notes?: string;

  // Attachments
  attachment_urls?: string[];

  // Notes
  internal_notes?: string;
}

/**
 * Create certificate response
 */
export interface CreateCertificateResponse {
  success: boolean;
  data?: {
    /** Generated certificate ID */
    certificate_id: number;

    /** Certificate number */
    certificate_number: string;

    /** Issue date */
    issue_date: string;

    /** Certificate details */
    certificate: MedicalCertificate;
  };
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * Update certificate request
 */
export interface UpdateCertificateRequest extends Partial<CreateCertificateRequest> {
  id: number;
}

/**
 * Certificate list query parameters
 */
export interface CertificateListQuery {
  page?: number;
  per_page?: number;
  certificate_type?: CertificateType;
  status?: CertificateStatus;
  patient_id?: number;
  doctor_id?: number;
  start_date?: string;
  end_date?: string;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

/**
 * Certificate list response
 */
export interface CertificateListResponse {
  items: CertificateSummary[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

/**
 * Complete medical certificate structure
 */
export interface MedicalCertificate {
  id: number;
  certificate_number: string;
  certificate_type: CertificateType;
  format: CertificateFormat;

  // Patient
  patient: CertificatePatientInfo;

  // Certificate details
  issue_date: string;
  examination_time?: string;
  valid_from: string;
  valid_until: string;
  duration_days?: number;
  purpose: string;
  is_official: boolean;
  copies: number;

  // Type-specific details
  sick_leave_details?: SickLeaveDetails;
  medical_fitness_details?: MedicalFitnessDetails;
  pregnancy_details?: PregnancyDetails;
  healthy_child_details?: HealthyChildDetails;
  death_details?: DeathDetails;
  medical_report_details?: MedicalReportDetails;

  // Clinical information
  primary_diagnosis: string;
  primary_diagnosis_code?: string;
  secondary_diagnoses?: string[];
  secondary_diagnosis_codes?: string[];
  chief_complaint?: string;
  physical_examination?: string;
  vital_signs?: VitalSigns;
  lab_findings?: string;
  imaging_findings?: string;
  clinical_notes?: string;

  // Doctor
  doctor: CertificateDoctorInfo;

  // Facility
  facility: CertificateFacilityInfo;

  // Status
  status: CertificateStatus;

  // Attachments
  attachments?: CertificateAttachment[];

  // Notes
  internal_notes?: string;

  // Metadata
  created_by: string;
  created_at: string;
  updated_by?: string;
  updated_at?: string;
  printed_at?: string;
  printed_by?: string;
}

/**
 * Certificate summary for list view
 */
export interface CertificateSummary {
  id: number;
  certificate_number: string;
  certificate_type: CertificateType;
  issue_date: string;
  valid_until: string;
  patient_name: string;
  medical_record_number: string;
  doctor_name: string;
  purpose: string;
  status: CertificateStatus;
  is_official: boolean;
  is_expired: boolean;
  days_until_expiry: number;
  created_at: string;
}

/**
 * Certificate print request
 */
export interface PrintCertificateRequest {
  certificate_id: number;
  copies: number;
  printer_name?: string;
  duplex?: boolean;
  color?: boolean;
}

/**
 * Certificate print response
 */
export interface PrintCertificateResponse {
  success: boolean;
  data?: {
    print_job_id?: string;
    print_url?: string;
    certificate_url: string;
    qr_code_url?: string;
  };
  message?: string;
  error?: {
    code: string;
    message: string;
  };
}

/**
 * Certificate statistics
 */
export interface CertificateStatistics {
  today_total: number;
  today_by_type: Record<CertificateType, number>;
  pending: number;
  approved: number;
  printed: number;
  void: number;
  expired: number;
  this_week: number;
  this_month: number;
}

/**
 * Certificate validation result
 */
export interface CertificateValidationResult {
  is_valid: boolean;
  field_errors: Array<{
    field: string;
    errors: string[];
  }>;
  general_errors: string[];
  warnings: string[];
}

/**
 * Certificate template configuration
 */
export interface CertificateTemplateConfig {
  certificate_type: CertificateType;
  template_name: string;
  format: CertificateFormat;
  header_text?: string;
  footer_text?: string;
  logo_position: 'left' | 'center' | 'right';
  show_qr_code: boolean;
  show_barcode: boolean;
  show_watermark: boolean;
  watermark_text?: string;
  page_orientation: 'portrait' | 'landscape';
  margins: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
}

// ============================================================================
// HELPER TYPES
// ============================================================================

/**
 * Certificate type with Indonesian label
 */
export interface CertificateTypeOption {
  value: CertificateType;
  label: string;
  label_indonesian: string;
  description: string;
}

/**
 * Certificate type options with labels
 */
export const CERTIFICATE_TYPE_OPTIONS: CertificateTypeOption[] = [
  {
    value: 'SICK_LEAVE',
    label: 'Sick Leave Certificate',
    label_indonesian: 'Surat Sakit',
    description: 'Certificate for sick leave from work or school',
  },
  {
    value: 'MEDICAL_FITNESS',
    label: 'Medical Fitness Certificate',
    label_indonesian: 'Surat Keterangan Sehat',
    description: 'General health certificate for various purposes',
  },
  {
    value: 'FIT_FOR_WORK',
    label: 'Fit for Work Certificate',
    label_indonesian: 'Surat Keterangan Fit untuk Bekerja',
    description: 'Certificate stating patient is fit to work',
  },
  {
    value: 'PREGNANCY',
    label: 'Pregnancy Certificate',
    label_indonesian: 'Surat Keterangan Hamil',
    description: 'Certificate confirming pregnancy and gestational age',
  },
  {
    value: 'HEALTHY_CHILD',
    label: 'Healthy Child Certificate',
    label_indonesian: 'Surat Keterangan Anak Sehat',
    description: 'Certificate for child health and development status',
  },
  {
    value: 'DEATH',
    label: 'Death Certificate',
    label_indonesian: 'Surat Keterangan Kematian',
    description: 'Certificate confirming death and cause',
  },
  {
    value: 'MEDICAL_REPORT',
    label: 'Medical Report',
    label_indonesian: 'Surat Keterangan Medis',
    description: 'General medical report for various purposes',
  },
];

/**
 * Get certificate type label in Indonesian
 */
export function getCertificateTypeLabel(type: CertificateType): string {
  return CERTIFICATE_TYPE_OPTIONS.find(opt => opt.value === type)?.label_indonesian || type;
}

/**
 * Certificate status with Indonesian label
 */
export interface CertificateStatusOption {
  value: CertificateStatus;
  label: string;
  label_indonesian: string;
  color: string;
}

/**
 * Certificate status options
 */
export const CERTIFICATE_STATUS_OPTIONS: CertificateStatusOption[] = [
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
    value: 'void',
    label: 'Void',
    label_indonesian: 'Batal',
    color: 'red',
  },
  {
    value: 'expired',
    label: 'Expired',
    label_indonesian: 'Kadaluarsa',
    color: 'orange',
  },
];
