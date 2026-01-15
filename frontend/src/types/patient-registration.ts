/**
 * Patient Registration Types for SIMRS
 * Comprehensive type definitions for patient registration with BPJS and insurance integration
 * Compatible with Indonesian healthcare requirements and regulations
 */

// ============================================================================
// PATIENT TYPES - Core Patient Information
// ============================================================================

/**
 * Gender options for patient registration
 */
export type PatientGender = 'male' | 'female';

/**
 * Marital status options according to Indonesian standards
 */
export type MaritalStatus =
  | 'single'           // Belum menikah
  | 'married'          // Menikah
  | 'widowed'          // Janda/Duda
  | 'divorced';        // Cerai hidup

/**
 * Religion options according to Indonesian standards
 */
export type Religion =
  | 'islam'
  | 'christian_protestant'
  | 'christian_catholic'
  | 'hindu'
  | 'buddha'
  | 'confucian'
  | 'other';

/**
 * Blood type options
 */
export type BloodType = 'A' | 'B' | 'AB' | 'O' | 'unknown';

/**
 * Education level according to Indonesian standards
 */
export type EducationLevel =
  | 'no_education'         // Tidak sekolah
  | 'elementary'           // SD
  | 'junior_high'          // SMP
  | 'senior_high'          // SMA
  | 'vocational'           // SMK
  | 'diploma'              // D1/D2/D3
  | 'bachelor'             // S1
  | 'master'               // S2
  | 'doctorate'            // S3
  | 'other';

/**
 * Patient personal information
 */
export interface PatientPersonalInfo {
  /** Full name according to ID card (KTP) */
  full_name: string;

  /** NIK - Nomor Induk Kependudukan (16 digits) */
  nik: string;

  /** Date of birth */
  date_of_birth: string;

  /** Place of birth */
  place_of_birth: string;

  /** Gender */
  gender: PatientGender;

  /** Blood type */
  blood_type: BloodType;

  /** Marital status */
  marital_status: MaritalStatus;

  /** Religion */
  religion: Religion;

  /** Occupation */
  occupation: string;

  /** Education level */
  education_level: EducationLevel;
}

/**
 * Patient contact information
 */
export interface PatientContactInfo {
  /** Primary phone number (Indonesian format: +62 or 08xx) */
  phone: string;

  /** Secondary phone number (optional) */
  phone_secondary?: string;

  /** Email address (optional) */
  email?: string;

  /** Full address */
  address: string;

  /** Province */
  province: string;

  /** City/Kabupaten */
  city: string;

  /** District/Kecamatan */
  district: string;

  /** Village/Kelurahan */
  village: string;

  /** Postal code (5 digits) */
  postal_code: string;
}

/**
 * Patient identification documents
 */
export interface PatientDocuments {
  /** KTP (Kartu Tanda Penduduk) number */
  ktp_number?: string;

  /** KTP image URL */
  ktp_image_url?: string;

  /** KK (Kartu Keluarga) number */
  kk_number?: string;

  /** Passport number (for foreigners) */
  passport_number?: string;

  /** Passport expiry date */
  passport_expiry?: string;
}

// ============================================================================
// BPJS TYPES - BPJS Insurance Information
// ============================================================================

/**
 * BPJS Kesehatan membership status
 */
export type BPJSStatus = 'active' | 'inactive' | 'expired' | 'suspended';

/**
 * BPJS participant type (Jenis Peserta)
 */
export type BPJSParticipantType =
  | 'peserta'           // Regular participant
  | 'peserta_pbi'       // PBI (Penerima Bantuan Iuran)
  | 'peserta_ppu'       // PPU (Pegawai Pemerintah)
  | 'peserta_swasta';   // Private sector employee

/**
 * BPJS health care class (Kelas Rawat)
 */
export type BPJSClass = 1 | 2 | 3;

/**
 * BPJS Kesehatan information
 */
export interface BPJSInfo {
  /** BPJS card number (13 digits) */
  bpjs_number: string;

  /** BPJS membership status */
  bpjs_status: BPJSStatus;

  /** Participant type */
  participant_type: BPJSParticipantType;

  /** Healthcare class */
  health_care_class: BPJSClass;

  /** Primary healthcare facility (Faskes Tingkat 1) */
  faskes_tk1: string;

  /** Faskes ID */
  faskes_id?: string;

  /** BPJS registration date */
  registration_date: string;

  /** BPJS expiry date (for non-active participants) */
  expiry_date?: string;

  /** BPJS card image URL */
  bpjs_card_image_url?: string;

  /** Is BPJS the primary insurance? */
  is_primary_insurance: boolean;
}

// ============================================================================
// INSURANCE TYPES - Private Insurance Information
// ============================================================================

/**
 * Insurance type
 */
export type InsuranceType = 'individual' | 'group' | 'corporate' | 'government';

/**
 * Insurance coverage type
 */
export type InsuranceCoverageType = 'inpatient' | 'outpatient' | 'both';

/**
 * Private insurance information
 */
export interface InsuranceInfo {
  /** Insurance provider name */
  provider_name: string;

  /** Policy/member number */
  policy_number: string;

  /** Member name (if different from patient) */
  member_name?: string;

  /** Relationship to policyholder */
  relationship_to_holder?: string;

  /** Insurance type */
  insurance_type: InsuranceType;

  /** Coverage type */
  coverage_type: InsuranceCoverageType;

  /** Policy effective date */
  effective_date: string;

  /** Policy expiry date */
  expiry_date: string;

  /** Maximum coverage amount */
  max_coverage_amount?: number;

  /** Current remaining balance */
  remaining_balance?: number;

  /** Insurance provider phone */
  provider_phone?: string;

  /** Insurance card image URL */
  insurance_card_image_url?: string;

  /** Is this the primary insurance? */
  is_primary_insurance: boolean;
}

// ============================================================================
// EMERGENCY CONTACT TYPES
// ============================================================================

/**
 * Emergency contact relationship
 */
export type EmergencyContactRelationship =
  | 'spouse'
  | 'parent'
  | 'child'
  | 'sibling'
  | 'friend'
  | 'other';

/**
 * Emergency contact information
 */
export interface EmergencyContact {
  /** Full name */
  full_name: string;

  /** Relationship to patient */
  relationship: EmergencyContactRelationship;

  /** Primary phone number */
  phone: string;

  /** Secondary phone number (optional) */
  phone_secondary?: string;

  /** Address (if different from patient) */
  address?: string;
}

// ============================================================================
// MEDICAL INFO TYPES - Medical Background
// ============================================================================

/**
 * Allergy severity
 */
export type AllergySeverity = 'mild' | 'moderate' | 'severe' | 'life_threatening';

/**
 * Allergy type
 */
export type AllergyType = 'drug' | 'food' | 'environmental' | 'other';

/**
 * Patient allergy
 */
export interface PatientAllergy {
  /** Allergen name */
  allergen: string;

  /** Allergy type */
  type: AllergyType;

  /** Severity level */
  severity: AllergySeverity;

  /** Reaction description */
  reaction: string;

  /** onset date */
  onset_date?: string;
}

/**
 * Chronic condition
 */
export interface ChronicCondition {
  /** Condition name */
  condition_name: string;

  /** ICD-10 code */
  icd_code?: string;

  /** Diagnosis date */
  diagnosis_date: string;

  /** Is currently active */
  is_active: boolean;

  /** Notes */
  notes?: string;
}

/**
 * Medical background information
 */
export interface MedicalBackground {
  /** Known allergies */
  allergies: PatientAllergy[];

  /** Chronic diseases/conditions */
  chronic_conditions: ChronicCondition[];

  /** Blood type */
  blood_type: BloodType;

  /** Additional medical notes */
  medical_notes?: string;

  /** Special requirements or accommodations */
  special_requirements?: string;
}

// ============================================================================
// FORM STATE TYPES - For Managing Registration Form
// ============================================================================

/**
 * Patient registration form state
 */
export interface PatientRegistrationFormState {
  /** Form step (1: Personal Info, 2: Contact, 3: Insurance, 4: Emergency, 5: Medical) */
  current_step: number;

  /** Personal information */
  personal_info: PatientPersonalInfo;

  /** Contact information */
  contact_info: PatientContactInfo;

  /** Identification documents */
  documents: PatientDocuments;

  /** BPJS information */
  bpjs_info: BPJSInfo | null;

  /** Private insurance information */
  insurance_info: InsuranceInfo | null;

  /** Emergency contact */
  emergency_contact: EmergencyContact;

  /** Medical background */
  medical_background: MedicalBackground;

  /** Has BPJS insurance */
  has_bpjs: boolean;

  /** Has private insurance */
  has_insurance: boolean;

  /** Photo/Avatar URL */
  photo_url?: string;

  /** Form validation errors */
  validation_errors: FormValidationError[];

  /** Is form dirty (has unsaved changes) */
  is_dirty: boolean;

  /** Is form valid */
  is_valid: boolean;

  /** Is submitting */
  is_submitting: boolean;

  /** General notes */
  notes?: string;
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
 * Form action types for state management
 */
export type PatientRegistrationFormAction =
  | { type: 'SET_FIELD'; step: string; field: string; value: any }
  | { type: 'SET_PERSONAL_INFO'; payload: Partial<PatientPersonalInfo> }
  | { type: 'SET_CONTACT_INFO'; payload: Partial<PatientContactInfo> }
  | { type: 'SET_DOCUMENTS'; payload: Partial<PatientDocuments> }
  | { type: 'SET_BPJS_INFO'; payload: BPJSInfo | null }
  | { type: 'SET_INSURANCE_INFO'; payload: InsuranceInfo | null }
  | { type: 'SET_EMERGENCY_CONTACT'; payload: EmergencyContact }
  | { type: 'SET_MEDICAL_BACKGROUND'; payload: Partial<MedicalBackground> }
  | { type: 'SET_HAS_BPJS'; payload: boolean }
  | { type: 'SET_HAS_INSURANCE'; payload: boolean }
  | { type: 'ADD_ALLERGY'; payload: PatientAllergy }
  | { type: 'UPDATE_ALLERGY'; payload: { index: number; allergy: Partial<PatientAllergy> } }
  | { type: 'REMOVE_ALLERGY'; payload: { index: number } }
  | { type: 'ADD_CHRONIC_CONDITION'; payload: ChronicCondition }
  | { type: 'UPDATE_CHRONIC_CONDITION'; payload: { index: number; condition: Partial<ChronicCondition> } }
  | { type: 'REMOVE_CHRONIC_CONDITION'; payload: { index: number } }
  | { type: 'SET_STEP'; payload: number }
  | { type: 'VALIDATE' }
  | { type: 'SUBMIT' }
  | { type: 'RESET' };

// ============================================================================
// VALIDATION CONSTRAINTS
// ============================================================================

/**
 * Patient registration validation constraints
 */
export interface PatientRegistrationValidationConstraints {
  // NIK constraints
  nik_required: boolean;
  nik_length: number;
  nik_pattern: RegExp;

  // Name constraints
  name_min_length: number;
  name_max_length: number;

  // Phone constraints
  phone_required: boolean;
  phone_pattern: RegExp;

  // Email constraints
  email_pattern: RegExp;

  // Address constraints
  address_min_length: number;
  address_max_length: number;

  // BPJS constraints
  bpjs_number_length: number;
  bpjs_number_required_if_has_bpjs: boolean;

  // Insurance constraints
  insurance_policy_number_required_if_has_insurance: boolean;

  // Date constraints
  min_age: number;
  max_age: number;

  // Photo constraints
  photo_max_size_mb: number;
  photo_allowed_types: string[];

  // Document constraints
  ktp_image_max_size_mb: number;
  bpjs_card_image_max_size_mb: number;
  insurance_card_image_max_size_mb: number;
}

/**
 * Default validation constraints for Indonesian healthcare
 */
export const DEFAULT_PATIENT_VALIDATION_CONSTRAINTS: PatientRegistrationValidationConstraints = {
  // NIK: 16 digits, required
  nik_required: true,
  nik_length: 16,
  nik_pattern: /^\d{16}$/,

  // Name: 2-100 characters
  name_min_length: 2,
  name_max_length: 100,

  // Phone: Indonesian format
  phone_required: true,
  phone_pattern: /^(\+62|62|0)8[1-9][0-9]{6,11}$/,

  // Email: Standard format
  email_pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,

  // Address: 10-500 characters
  address_min_length: 10,
  address_max_length: 500,

  // BPJS: 13 digits
  bpjs_number_length: 13,
  bpjs_number_required_if_has_bpjs: true,

  // Insurance
  insurance_policy_number_required_if_has_insurance: true,

  // Age limits
  min_age: 0,
  max_age: 150,

  // Photo: max 2MB, jpg/png
  photo_max_size_mb: 2,
  photo_allowed_types: ['image/jpeg', 'image/png', 'image/jpg'],

  // Documents: max 5MB each
  ktp_image_max_size_mb: 5,
  bpjs_card_image_max_size_mb: 5,
  insurance_card_image_max_size_mb: 5,
};

// ============================================================================
// API REQUEST/RESPONSE TYPES - For Backend Integration
// ============================================================================

/**
 * Create patient request
 */
export interface CreatePatientRequest {
  personal_info: PatientPersonalInfo;
  contact_info: PatientContactInfo;
  documents?: PatientDocuments;
  bpjs_info?: BPJSInfo;
  insurance_info?: InsuranceInfo;
  emergency_contact: EmergencyContact;
  medical_background: MedicalBackground;
  photo_url?: string;
  notes?: string;
}

/**
 * Create patient response
 */
export interface CreatePatientResponse {
  success: boolean;
  data?: {
    /** Generated patient ID */
    patient_id: number;

    /** Medical record number (RM number) */
    medical_record_number: string;

    /** Registration date */
    registration_date: string;

    /** Patient details */
    patient: PatientPersonalInfo & { id: number };
  };
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * Patient duplicate check request
 */
export interface PatientDuplicateCheckRequest {
  /** NIK to check */
  nik?: string;

  /** BPJS number to check */
  bpjs_number?: string;

  /** Phone number to check */
  phone?: string;

  /** Name to check (optional) */
  full_name?: string;

  /** Date of birth (optional, for name matching) */
  date_of_birth?: string;
}

/**
 * Patient duplicate check result
 */
export interface PatientDuplicateResult {
  /** Duplicate patient ID */
  patient_id: number;

  /** Medical record number */
  medical_record_number: string;

  /** Full name */
  full_name: string;

  /** NIK */
  nik: string;

  /** Date of birth */
  date_of_birth: string;

  /** Gender */
  gender: PatientGender;

  /** Phone */
  phone: string;

  /** BPJS number (if available) */
  bpjs_number?: string;

  /** Match percentage */
  match_percentage: number;

  /** Match reason */
  match_reason: string[];
}

/**
 * Patient duplicate check response
 */
export interface PatientDuplicateCheckResponse {
  success: boolean;
  data?: {
    /** Has duplicates */
    has_duplicates: boolean;

    /** Duplicate count */
    duplicate_count: number;

    /** Duplicate patients */
    duplicates: PatientDuplicateResult[];
  };
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * BPJS eligibility check request
 */
export interface BPJSEligibilityCheckRequest {
  /** BPJS card number */
  bpjs_number: string;

  /** NIK */
  nik: string;

  /** Full name */
  full_name: string;

  /** Date of birth */
  date_of_birth: string;
}

/**
 * BPJS eligibility check response
 */
export interface BPJSEligibilityCheckResponse {
  success: boolean;
  data?: {
    /** Is eligible */
    is_eligible: boolean;

    /** BPJS status */
    status: BPJSStatus;

    /** Participant type */
    participant_type: BPJSParticipantType;

    /** Healthcare class */
    health_care_class: BPJSClass;

    /** Primary facility */
    faskes_tk1: string;

    /** Faskes ID */
    faskes_id?: string;

    /** Eligibility date */
    eligibility_date: string;

    /** Expiry date (if applicable) */
    expiry_date?: string;

    /** Member information from BPJS */
    member_info?: {
      nama: string;
      nik: string;
      jenis_peserta: string;
      faskes: string;
      kelas_rawat: string;
    };
  };
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * Patient registration summary (for confirmation)
 */
export interface PatientRegistrationSummary {
  /** Personal info summary */
  personal_summary: {
    full_name: string;
    nik: string;
    date_of_birth: string;
    gender: PatientGender;
    blood_type: BloodType;
  };

  /** Contact summary */
  contact_summary: {
    phone: string;
    email?: string;
    address: string;
    city: string;
  };

  /** Insurance summary */
  insurance_summary: {
    has_bpjs: boolean;
    bpjs_number?: string;
    has_private_insurance: boolean;
    insurance_provider?: string;
  };

  /** Emergency contact summary */
  emergency_contact_summary: {
    full_name: string;
    relationship: string;
    phone: string;
  };

  /** Medical summary */
  medical_summary: {
    has_allergies: boolean;
    allergy_count: number;
    has_chronic_conditions: boolean;
    condition_count: number;
  };
}

// ============================================================================
// HELPER TYPES
// ============================================================================

/**
 * Patient registration form step
 */
export type RegistrationStep =
  | 'personal'
  | 'contact'
  | 'insurance'
  | 'emergency'
  | 'medical'
  | 'review';

/**
 * Form step configuration
 */
export interface FormStepConfig {
  /** Step number */
  step: number;

  /** Step identifier */
  id: RegistrationStep;

  /** Step title */
  title: string;

  /** Step description */
  description: string;

  /** Is step optional */
  optional: boolean;

  /** Required fields in this step */
  required_fields: string[];
}

/**
 * Patient registration form configuration
 */
export interface PatientRegistrationFormConfig {
  /** Form steps configuration */
  steps: FormStepConfig[];

  /** Validation constraints */
  validation_constraints: PatientRegistrationValidationConstraints;

  /** Is BPJS mandatory */
  bpjs_mandatory: boolean;

  /** Is photo mandatory */
  photo_mandatory: boolean;

  /** Allow duplicate registration with warning */
  allow_duplicate_with_warning: boolean;

  /** Auto-check BPJS eligibility */
  auto_check_bpjs_eligibility: boolean;
}

/**
 * Form field error
 */
export interface FieldError {
  field: string;
  errors: string[];
}

/**
 * Form validation result
 */
export interface FormValidationResult {
  /** Is form valid */
  is_valid: boolean;

  /** Field errors */
  field_errors: FieldError[];

  /** General errors */
  general_errors: string[];

  /** Warnings */
  warnings: string[];
}
