/**
 * Surgery Consent Types for SIMRS
 * Comprehensive type definitions for Indonesian surgery consent forms (Formulir Persetujuan Tindakan Medis)
 * Compatible with Indonesian healthcare regulations (Permenkes No. 290/Menkes/Per/III/2008)
 * and legal requirements for informed consent (Persetujuan Pemberian Informasi Medis - PPID)
 */

// ============================================================================
// CONSENT TYPE ENUMERATIONS
// ============================================================================

/**
 * All Indonesian surgery consent types
 * - SURGERY: Persetujuan Tindakan Operasi - Surgery consent
 * - ANESTHESIA: Persetujuan Tindakan Anestesi - Anesthesia consent
 * - BLOOD_TRANSFUSION: Persetujuan Transfusi Darah - Blood transfusion consent
 * - PROCEDURE: Persetujuan Tindakan Medis - Medical procedure consent
 * - DIAGNOSTIC: Persetujuan Pemeriksaan Diagnostik - Diagnostic procedure consent
 * - SPECIAL_PROCEDURE: Persetujuan Tindakan Khusus - Special procedure consent
 * - PEDIATRIC: Persetujuan Tindakan Anak - Pediatric consent (with guardian)
 * - EMERGENCY: Persetujuan Kondisi Gawat Darurat - Emergency consent
 */
export type SurgeryConsentType =
  | 'SURGERY'
  | 'ANESTHESIA'
  | 'BLOOD_TRANSFUSION'
  | 'PROCEDURE'
  | 'DIAGNOSTIC'
  | 'SPECIAL_PROCEDURE'
  | 'PEDIATRIC'
  | 'EMERGENCY';

/**
 * Consent form status workflow
 */
export type ConsentFormStatus =
  | 'draft'           // Being edited
  | 'pending'         // Awaiting patient consent
  | 'acknowledged'    // Patient has received information
  | 'consented'       // Patient has given consent
  | 'refused'         // Patient has refused consent
  | 'cancelled'       // Procedure cancelled
  | 'completed'       // Procedure completed
  | 'expired';        // Consent expired

/**
 * Consent withdrawal status
 */
export type ConsentWithdrawalStatus =
  | 'not_withdrawn'
  | 'withdrawn'
  | 'partial_withdrawal';

/**
 * Consent relationship types
 */
export type ConsentRelationshipType =
  | 'self'            // Patient consents for themselves
  | 'guardian'        // Legal guardian consents
  | 'parent'          // Parent consents for child
  | 'spouse'          // Spouse consents
  | 'power_of_attorney' // Legal representative
  | 'court_appointed'; // Court-appointed guardian

/**
 * Witness status
 */
export type WitnessType = 'family_witness' | 'healthcare_witness' | 'independent_witness' | 'none';

/**
 * Signature status
 */
export type SignatureStatus = 'pending' | 'digital' | 'wet' | 'thumbprint' | 'proxy';

/**
 * Emergency classification
 */
export type EmergencyClassification = 'emergency' | 'urgent' | 'elective' | 'emergency_life_threatening';

/**
 * Anesthesia type
 */
export type AnesthesiaType =
  | 'local'           // Anestesi Lokal
  | 'regional'        // Anestesi Regional (Spinal/Epidural)
  | 'general'         // Anestesi Umum
  | 'sedation'        // Sedasi
  | 'none';           // Tanpa Anestesi

/**
 * Procedure complexity
 */
export type ProcedureComplexity = 'minor' | 'intermediate' | 'major' | 'complex';

/**
 * Risk level
 */
export type RiskLevel = 'very_low' | 'low' | 'moderate' | 'high' | 'very_high';

/**
 * Blood transfusion urgency
 */
export type BloodTransfusionUrgency = 'elective' | 'urgent' | 'emergency';

// ============================================================================
// PATIENT INFORMATION TYPES
// ============================================================================

/**
 * Patient information for surgery consent
 */
export interface ConsentPatientInfo {
  /** Patient ID */
  patient_id: number;

  /** Medical record number (Nomor Rekam Medis) */
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

  /** Blood type (Golongan Darah) */
  blood_type: 'A' | 'B' | 'AB' | 'O' | 'unknown';

  /** RH factor */
  rh_factor: 'positive' | 'negative' | 'unknown';

  /** Phone number */
  phone: string;

  /** Address */
  address: string;

  /** City/Kabupaten */
  city: string;

  /** Province */
  province: string;

  /** Marital status */
  marital_status: 'single' | 'married' | 'widowed' | 'divorced';

  /** Religion (for religious considerations) */
  religion: 'islam' | 'christian_protestant' | 'christian_catholic' | 'hindu' | 'buddha' | 'confucian' | 'other';

  /** BPJS number */
  bpjs_number?: string;

  /** Insurance provider */
  insurance_provider?: string;

  /** Is patient a minor */
  is_minor: boolean;

  /** Is patient mentally competent */
  is_mentally_competent: boolean;

  /** Requires legal guardian consent */
  requires_guardian_consent: boolean;

  /** Patient allergies */
  allergies: string[];

  /** Known comorbidities */
  comorbidities: string[];
}

/**
 * Patient selection option for consent form
 */
export interface ConsentPatientSelect {
  value: number;
  label: string;
  medical_record_number: string;
  nik: string;
  date_of_birth: string;
  gender: 'male' | 'female';
  age_years: number;
  blood_type: string;
  is_minor: boolean;
  bpjs_number?: string;
  insurance_provider?: string;
}

// ============================================================================
// PROCEDURE INFORMATION TYPES
// ============================================================================

/**
 * Surgical procedure information
 */
export interface SurgicalProcedureInfo {
  /** Procedure ID */
  procedure_id?: number;

  /** Procedure code (ICD-9-CM or local coding) */
  procedure_code?: string;

  /** Procedure name (Indonesian) */
  procedure_name_id: string;

  /** Procedure name (English/Latin) */
  procedure_name_en?: string;

  /** Procedure description in Indonesian */
  procedure_description_id: string;

  /** Procedure description in English */
  procedure_description_en?: string;

  /** Procedure complexity */
  complexity: ProcedureComplexity;

  /** Surgical category */
  surgical_category: string;

  /** Body system involved */
  body_system: string;

  /** Surgical approach (open, laparoscopic, robotic, etc.) */
  surgical_approach: string;

  /** Expected duration in minutes */
  expected_duration_minutes: number;

  /** Expected blood loss in mL */
  expected_blood_loss_ml: number;

  /** Expected hospital stay in days */
  expected_hospital_stay_days: number;

  /** Is this a repeat procedure */
  is_repeat_procedure: boolean;

  /** Previous procedure dates */
  previous_procedure_dates?: string[];

  /** Alternative procedures available */
  alternative_procedures?: string[];

  /** Consequences of refusing procedure */
  consequences_of_refusal: string;

  /** Success rate percentage */
  success_rate_percentage?: number;

  /** Is this experimental/innovative */
  is_experimental: boolean;

  /** Research protocol number (if applicable) */
  research_protocol_number?: string;
}

/**
 * Diagnostic procedure information
 */
export interface DiagnosticProcedureInfo {
  /** Diagnostic procedure ID */
  procedure_id?: number;

  /** Procedure name */
  procedure_name: string;

  /** Procedure description */
  procedure_description: string;

  /** Diagnostic category */
  diagnostic_category: 'imaging' | 'laboratory' | 'endoscopic' | 'cardiac' | 'neurological' | 'other';

  /** Is contrast required */
  requires_contrast: boolean;

  /** Is sedation required */
  requires_sedation: boolean;

  /** Is fasting required */
  requires_fasting: boolean;

  /** Fasting duration in hours */
  fasting_duration_hours?: number;

  /** Special preparations required */
  special_preparations?: string[];

  /** Expected duration in minutes */
  expected_duration_minutes: number;
}

/**
 * Blood transfusion information
 */
export interface BloodTransfusionInfo {
  /** Transfusion ID */
  transfusion_id?: number;

  /** Blood product type */
  blood_product_type: 'whole_blood' | 'prbc' | 'platelets' | 'ffp' | 'cryoprecipitate' | 'other';

  /** Blood product description */
  blood_product_description: string;

  /** Expected number of units */
  expected_units: number;

  /** Urgency level */
  urgency: BloodTransfusionUrgency;

  /** Indication for transfusion */
  indication: string;

  /** Is blood matching required */
  requires_matching: boolean;

  /** Required blood type */
  required_blood_type: 'A' | 'B' | 'AB' | 'O';

  /** Required RH factor */
  required_rh: 'positive' | 'negative';

  /** Is autologous transfusion possible */
  autologous_possible: boolean;

  /** Transfusion reaction risks */
  transfusion_risks: string[];
}

// ============================================================================
// ANESTHESIA INFORMATION TYPES
// ============================================================================

/**
 * Anesthesia information
 */
export interface AnesthesiaInfo {
  /** Anesthesia type */
  anesthesia_type: AnesthesiaType;

  /** Anesthesia description in Indonesian */
  anesthesia_description_id: string;

  /** Anesthesia description in English */
  anesthesia_description_en?: string;

  /** Anesthesiologist ID */
  anesthesiologist_id: number;

  /** Anesthesiologist name */
  anesthesiologist_name: string;

  /** Anesthesiologist license number (SIPA) */
  anesthesiologist_license: string;

  /** Pre-anesthesia assessment required */
  requires_pre_assessment: boolean;

  /** Pre-anesthesia assessment date */
  pre_assessment_date?: string;

  /** ASA Physical Status Classification */
  asa_classification: 'ASA_I' | 'ASA_II' | 'ASA_III' | 'ASA_IV' | 'ASA_V' | 'ASA_VI';

  /** Airway assessment */
  airway_assessment?: {
    mallampati_score?: number;
    thyromental_distance?: string;
    mouth_opening?: string;
    neck_mobility?: string;
  };

  /** Fasting status (NPO) */
  fasting_status?: {
    is_npocompliant: boolean;
    last_food_intake?: string;
    last_fluid_intake?: string;
  };

  /** Premedication required */
  requires_premedication: boolean;

  /** Premedication details */
  premedication_details?: string;

  /** Regional anesthesia specific */
  regional_details?: {
    technique: 'spinal' | 'epidural' | 'nerve_block' | 'combined';
    level?: string;
    local_anesthetic: string;
  };

  /** General anesthesia specific */
  general_details?: {
    airway_device: 'endotracheal_tube' | 'lma' | 'face_mask' | 'other';
    induction_agent: string;
    maintenance_agent: string;
  };

  /** Post-anesthesia care required */
  requires_post_anesthesia_care: boolean;

  /** Expected recovery time */
  expected_recovery_time_minutes?: number;
}

/**
 * ASA Physical Status Classification descriptions
 */
export const ASA_CLASSIFICATIONS = {
  ASA_I: 'Pasien sehat secara normal, tanpa penyakit organik, fisiologis, atau psikiatrik',
  ASA_II: 'Penyakit sistem ringan sampai sedang, tanpa batasan fungsional',
  ASA_III: 'Penyakit sistem berat dengan batasan fungsional yang nyata',
  ASA_IV: 'Penyakit sistem berat yang mengancam nyawa secara konstan',
  ASA_V: 'Pasien moribund yang tidak diharapkan hidup 24 jam tanpa operasi',
  ASA_VI: 'Pasien dinyatakan meninggal dengan tujuan donor organ',
};

// ============================================================================
// RISKS AND BENEFITS TYPES
// ============================================================================

/**
 * Risk category and severity
 */
export interface ProcedureRisk {
  /** Risk ID */
  id?: number;

  /** Risk category */
  category: 'common' | 'uncommon' | 'rare' | 'very_rare';

  /** Risk name in Indonesian */
  risk_name_id: string;

  /** Risk name in English */
  risk_name_en?: string;

  /** Risk description in Indonesian */
  risk_description_id: string;

  /** Risk description in English */
  risk_description_en?: string;

  /** Risk level */
  severity: RiskLevel;

  /** Probability percentage */
  probability_percentage?: number;

  /** Is this risk life-threatening */
  is_life_threatening: boolean;

  /** Mitigation strategies */
  mitigation_strategies?: string[];

  /** Requires special consent disclosure */
  requires_special_disclosure: boolean;
}

/**
 * Procedure benefits
 */
export interface ProcedureBenefit {
  /** Benefit ID */
  id?: number;

  /** Benefit in Indonesian */
  benefit_id: string;

  /** Benefit in English */
  benefit_en?: string;

  /** Benefit description */
  description: string;

  /** Expected outcome */
  expected_outcome: string;

  /** Time to benefit */
  time_to_benefit?: string;
}

/**
 * Alternative treatment options
 */
export interface AlternativeTreatment {
  /** Treatment name */
  treatment_name: string;

  /** Treatment description */
  description: string;

  /** Pros of this alternative */
  pros: string[];

  /** Cons of this alternative */
  cons: string[];

  /** Success rate */
  success_rate_percentage?: number;

  /** Why not chosen (if applicable) */
  why_not_chosen?: string;
}

/**
 * Consequences of no treatment
 */
export interface NoTreatmentConsequences {
  /** Expected progression without treatment */
  expected_progression: string;

  /** Risks of delaying treatment */
  delay_risks: string[];

  /** Irreversible consequences */
  irreversible_consequences: string[];

  /** Impact on quality of life */
  quality_of_life_impact: string;

  /** Life expectancy impact */
  life_expectancy_impact?: string;
}

/**
 * Risks and benefits comprehensive information
 */
export interface RisksAndBenefits {
  /** Common risks (>1% incidence) */
  common_risks: ProcedureRisk[];

  /** Uncommon risks (0.1% to 1% incidence) */
  uncommon_risks: ProcedureRisk[];

  /** Rare risks (0.01% to 0.1% incidence) */
  rare_risks: ProcedureRisk[];

  /** Very rare risks (<0.01% incidence) */
  very_rare_risks: ProcedureRisk[];

  /** Procedure benefits */
  benefits: ProcedureBenefit[];

  /** Expected success rate */
  expected_success_rate_percentage: number;

  /** Alternative treatments */
  alternative_treatments: AlternativeTreatment[];

  /** Consequences of refusing treatment */
  consequences_of_refusal: NoTreatmentConsequences;

  /** Special risks for this patient */
  patient_specific_risks?: string[];

  /** Additional disclosures required */
  additional_disclosures?: string[];
}

// ============================================================================
// PATIENT CONSENT TYPES
// ============================================================================

/**
 * Patient consent acknowledgment
 */
export interface PatientConsent {
  /** Consent form ID */
  consent_id?: number;

  /** Consent type */
  consent_type: SurgeryConsentType;

  /** Relationship to patient */
  relationship_type: ConsentRelationshipType;

  /** Is consent given */
  is_consent_given: boolean;

  /** Consent given date */
  consent_date?: string;

  /** Consent given time */
  consent_time?: string;

  /** Is consent withdrawn */
  is_withdrawn: boolean;

  /** Withdrawal date */
  withdrawal_date?: string;

  /** Withdrawal reason */
  withdrawal_reason?: string;

  /** Patient understands the procedure */
  understands_procedure: boolean;

  /** Patient understands the risks */
  understands_risks: boolean;

  /** Patient understands the benefits */
  understands_benefits: boolean;

  /** Patient understands alternatives */
  understands_alternatives: boolean;

  /** Patient understands consequences of refusal */
  understands_consequences_of_refusal: boolean;

  /** Patient has opportunity to ask questions */
  has_opportunity_to_ask_questions: boolean;

  /** Patient questions answered satisfactorily */
  questions_answered_satisfactorily: boolean;

  /** Patient understands they can withdraw consent */
  understands_can_withdraw: boolean;

  /** Consent is voluntary without coercion */
  is_voluntary: boolean;

  /** Patient signature */
  patient_signature: ConsentSignature;

  /** Guardian signature (if applicable) */
  guardian_signature?: ConsentSignature;

  /** Witness signature */
  witness_signature?: ConsentSignature;

  /** Additional patient comments */
  patient_comments?: string;

  /** Special considerations */
  special_considerations?: string[];

  /** Translation provided (if needed) */
  translation_provided?: {
    language: string;
    translator_name: string;
    translator_signature?: string;
  };
}

/**
 * Consent signature information
 */
export interface ConsentSignature {
  /** Signatory name */
  full_name: string;

  /** Signatory relationship */
  relationship?: string;

  /** Signature type */
  signature_type: SignatureStatus;

  /** Signature image URL */
  signature_url?: string;

  /** Digital signature ID */
  digital_signature_id?: string;

  /** Date signed */
  date_signed: string;

  /** Time signed */
  time_signed: string;

  /** IP address (for digital signatures) */
  ip_address?: string;

  /** Device information */
  device_info?: string;

  /** Location (if digital) */
  location?: string;

  /** Thumbprint image (if applicable) */
  thumbprint_url?: string;

  /** Proxy signer name (if signed by proxy) */
  proxy_signer_name?: string;

  /** Proxy signer relationship */
  proxy_signer_relationship?: string;

  /** Proxy signature reason */
  proxy_reason?: string;
}

/**
 * Witness information
 */
export interface ConsentWitness {
  /** Witness ID */
  witness_id?: number;

  /** Witness type */
  witness_type: WitnessType;

  /** Witness full name */
  full_name: string;

  /** Witness relationship to patient (if family) */
  relationship?: string;

  /** Witness occupation */
  occupation?: string;

  /** Witness address */
  address?: string;

  /** Witness phone */
  phone?: string;

  /** Witness signature */
  signature: ConsentSignature;

  /** Witness statement */
  statement?: string;
}

/**
 * Informed consent process tracking
 */
export interface InformedConsentProcess {
  /** Process ID */
  process_id?: number;

  /** Information provided date */
  information_provided_date: string;

  /** Information provided time */
  information_provided_time: string;

  /** Person providing information */
  provider_name: string;

  /** Provider role */
  provider_role: string;

  /** Duration of information session (minutes) */
  session_duration_minutes: number;

  /** Topics discussed */
  topics_discussed: string[];

  /** Educational materials provided */
  educational_materials?: string[];

  /** Patient questions recorded */
  patient_questions?: string[];

  /** Patient understanding assessment */
  understanding_assessment?: {
    diagnosis_understood: boolean;
    procedure_understood: boolean;
    risks_understood: boolean;
    benefits_understood: boolean;
    alternatives_understood: boolean;
    consent_voluntary: boolean;
  };

  /** Follow-up discussion required */
  requires_followup: boolean;

  /** Follow-up scheduled date */
  followup_date?: string;

  /** Interpreter used */
  interpreter_used?: boolean;
  interpreter_name?: string;
}

// ============================================================================
// DOCTOR INFORMATION TYPES
// ============================================================================

/**
 * Surgeon/Doctor information
 */
export interface SurgeonInfo {
  /** Doctor ID */
  doctor_id: number;

  /** Doctor's full name */
  doctor_name: string;

  /** Doctor's title/degree (e.g., "dr. Sp.B") */
  doctor_title: string;

  /** Specialization */
  specialization: string;

  /** Sub-specialization (if applicable) */
  sub_specialization?: string;

  /** SIP number (Surat Izin Praktik) */
  sip_number: string;

  /** SIP issue date */
  sip_issue_date: string;

  /** SIP expiry date */
  sip_expiry_date: string;

  /** STR number (Surat Tanda Registrasi) */
  str_number: string;

  /** Hospital ID number */
  hospital_id_number?: string;

  /** Department/Unit */
  department: string;

  /** Phone number */
  phone?: string;

  /** Email */
  email?: string;

  /** Years of experience */
  years_of_experience?: number;

  /** Number of similar procedures performed */
  similar_procedures_count?: number;

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

  /** Additional notes */
  notes?: string;

  /** Performing role (primary surgeon, assistant, etc.) */
  role: 'primary_surgeon' | 'assistant_surgeon' | 'consultant' | 'supervisor';
}

/**
 * Doctor selection option
 */
export interface SurgeonSelect {
  value: number;
  label: string;
  title: string;
  specialization: string;
  sub_specialization?: string;
  sip_number: string;
  department: string;
  years_of_experience?: number;
}

/**
 * Medical team information
 */
export interface MedicalTeam {
  /** Primary surgeon */
  primary_surgeon: SurgeonInfo;

  /** Assistant surgeons */
  assistant_surgeons?: SurgeonInfo[];

  /** Anesthesiologist */
  anesthesiologist?: SurgeonInfo;

  /** Consulting physicians */
  consulting_physicians?: SurgeonInfo[];

  /** Scrub nurse */
  scrub_nurse?: {
    name: string;
    license_number: string;
  };

  /** Circulating nurse */
  circulating_nurse?: {
    name: string;
    license_number: string;
  };
}

// ============================================================================
// FACILITY INFORMATION TYPES
// ============================================================================

/**
 * Facility information for consent
 */
export interface ConsentFacilityInfo {
  /** Facility ID */
  facility_id: number;

  /** Facility name */
  facility_name: string;

  /** Facility type */
  facility_type: 'hospital' | 'clinic' | 'surgical_center' | 'maternity';

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

  /** BPJS facility code */
  bpjs_facility_code?: string;

  /** Is BPJS accredited facility */
  is_bpjs_accredited: boolean;

  /** Hospital accreditation status */
  accreditation_status?: 'internasional' | 'paripurna' | 'utama' | 'madya' | 'dasar';

  /** Operating room number */
  operating_room_number?: string;

  /** Floor/Unit */
  floor_unit?: string;
}

// ============================================================================
// FORM STATE TYPES
// ============================================================================

/**
 * Surgery consent form state
 */
export interface SurgeryConsentFormState {
  // Form identification
  consent_form_id?: number;
  consent_form_number?: string;

  // Consent type and status
  consent_type: SurgeryConsentType;
  consent_status: ConsentFormStatus;
  emergency_classification: EmergencyClassification;

  // Patient information
  patient_id: number | null;
  patient_info: ConsentPatientInfo | null;

  // Procedure information
  procedure_info: SurgicalProcedureInfo | DiagnosticProcedureInfo | BloodTransfusionInfo;
  scheduled_date: string;
  scheduled_time: string;

  // Anesthesia information
  anesthesia_required: boolean;
  anesthesia_info?: AnesthesiaInfo;

  // Risks and benefits
  risks_and_benefits: RisksAndBenefits;

  // Patient consent
  patient_consent: PatientConsent;
  witness?: ConsentWitness;

  // Medical team
  primary_surgeon_id: number | null;
  primary_surgeon_info: SurgeonInfo | null;
  medical_team: MedicalTeam | null;

  // Facility information
  facility_info: ConsentFacilityInfo;

  // Informed consent process
  informed_consent_process: InformedConsentProcess;

  // Attachments
  attachments: ConsentAttachment[];

  // Form management
  is_dirty: boolean;
  is_valid: boolean;
  is_submitting: boolean;
  validation_errors: FormValidationError[];

  // Timestamps
  created_at?: string;
  updated_at?: string;
  consent_date?: string;

  // Notes
  internal_notes?: string;

  // Blood transfusion specific
  blood_transfusion_info?: BloodTransfusionInfo;
}

/**
 * Consent attachment
 */
export interface ConsentAttachment {
  /** Temporary ID (for new attachments) */
  temp_id?: string;

  /** Attachment ID (for saved attachments) */
  id?: number;

  /** Attachment type */
  attachment_type: 'lab_result' | 'imaging' | 'ecg' | 'consent_form' | 'document' | 'photo' | 'other';

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

  /** Description */
  description?: string;

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
export type SurgeryConsentFormAction =
  | { type: 'SET_CONSENT_TYPE'; payload: SurgeryConsentType }
  | { type: 'SET_PATIENT'; payload: ConsentPatientInfo }
  | { type: 'SET_PROCEDURE_INFO'; payload: SurgicalProcedureInfo | DiagnosticProcedureInfo | BloodTransfusionInfo }
  | { type: 'SET_ANESTHESIA_INFO'; payload: AnesthesiaInfo }
  | { type: 'SET_RISKS_AND_BENEFITS'; payload: RisksAndBenefits }
  | { type: 'SET_PATIENT_CONSENT'; payload: PatientConsent }
  | { type: 'SET_WITNESS'; payload: ConsentWitness }
  | { type: 'SET_PRIMARY_SURGEON'; payload: SurgeonInfo }
  | { type: 'SET_MEDICAL_TEAM'; payload: MedicalTeam }
  | { type: 'SET_SCHEDULED_DATE_TIME'; payload: { date: string; time: string } }
  | { type: 'SET_INFORMED_CONSENT_PROCESS'; payload: InformedConsentProcess }
  | { type: 'ADD_ATTACHMENT'; payload: ConsentAttachment }
  | { type: 'REMOVE_ATTACHMENT'; payload: { temp_id: string } }
  | { type: 'VALIDATE' }
  | { type: 'SUBMIT' }
  | { type: 'RESET' };

// ============================================================================
// VALIDATION CONSTRAINTS
// ============================================================================

/**
 * Surgery consent validation constraints
 */
export interface SurgeryConsentValidationConstraints {
  // Patient constraints
  patient_required: boolean;
  patient_must_have_valid_nik: boolean;
  patient_age_minimum: number;

  // Procedure constraints
  procedure_name_required: boolean;
  procedure_name_min_length: number;
  procedure_description_required: boolean;
  procedure_description_min_length: number;
  scheduled_date_min_hours_advance: number;

  // Anesthesia constraints
  anesthesia_required_for_surgery: boolean;
  anesthesiologist_required: boolean;
  pre_assessment_required_hours_before: number;

  // Risk disclosure constraints
  common_risks_required: boolean;
  benefits_required: boolean;
  alternatives_required: boolean;
  consequences_of_refusal_required: boolean;

  // Consent constraints
  patient_signature_required: boolean;
  guardian_signature_required_if_minor: boolean;
  witness_required_for_emergency: boolean;
  witness_required_for_high_risk: boolean;

  // Doctor constraints
  surgeon_required: boolean;
  surgeon_must_have_valid_sip: boolean;

  // Date constraints
  consent_date_not_future: boolean;
  consent_expiry_days: number;

  // Attachment constraints
  attachment_max_size_mb: number;
  attachment_allowed_types: string[];
  max_attachments: number;

  // Notes constraints
  patient_comments_max_length: number;
  internal_notes_max_length: number;
}

/**
 * Default validation constraints for Indonesian healthcare
 */
export const DEFAULT_SURGERY_CONSENT_VALIDATION_CONSTRAINTS: SurgeryConsentValidationConstraints = {
  // Patient
  patient_required: true,
  patient_must_have_valid_nik: true,
  patient_age_minimum: 0,

  // Procedure
  procedure_name_required: true,
  procedure_name_min_length: 5,
  procedure_description_required: true,
  procedure_description_min_length: 20,
  scheduled_date_min_hours_advance: 2,

  // Anesthesia
  anesthesia_required_for_surgery: true,
  anesthesiologist_required: true,
  pre_assessment_required_hours_before: 24,

  // Risk disclosure
  common_risks_required: true,
  benefits_required: true,
  alternatives_required: true,
  consequences_of_refusal_required: true,

  // Consent
  patient_signature_required: true,
  guardian_signature_required_if_minor: true,
  witness_required_for_emergency: true,
  witness_required_for_high_risk: true,

  // Doctor
  surgeon_required: true,
  surgeon_must_have_valid_sip: true,

  // Dates
  consent_date_not_future: true,
  consent_expiry_days: 30,

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
  patient_comments_max_length: 1000,
  internal_notes_max_length: 2000,
};

// ============================================================================
// API REQUEST/RESPONSE TYPES
// ============================================================================

/**
 * Create surgery consent request
 */
export interface CreateSurgeryConsentRequest {
  consent_type: SurgeryConsentType;
  patient_id: number;
  primary_surgeon_id: number;
  anesthesiologist_id?: number;
  scheduled_date: string;
  scheduled_time: string;
  emergency_classification: EmergencyClassification;

  // Procedure information
  procedure_info: SurgicalProcedureInfo | DiagnosticProcedureInfo | BloodTransfusionInfo;

  // Anesthesia information (if required)
  anesthesia_info?: AnesthesiaInfo;

  // Risks and benefits
  risks_and_benefits: RisksAndBenefits;

  // Informed consent process
  informed_consent_process: InformedConsentProcess;

  // Patient consent
  patient_consent: PatientConsent;
  witness?: ConsentWitness;

  // Medical team
  medical_team?: MedicalTeam;

  // Attachments
  attachment_urls?: string[];

  // Notes
  internal_notes?: string;
}

/**
 * Create surgery consent response
 */
export interface CreateSurgeryConsentResponse {
  success: boolean;
  data?: {
    /** Generated consent form ID */
    consent_form_id: number;

    /** Consent form number */
    consent_form_number: string;

    /** Consent form details */
    consent_form: SurgeryConsentForm;
  };
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * Update surgery consent request
 */
export interface UpdateSurgeryConsentRequest extends Partial<CreateSurgeryConsentRequest> {
  id: number;
}

/**
 * Surgery consent list query parameters
 */
export interface SurgeryConsentListQuery {
  page?: number;
  per_page?: number;
  consent_type?: SurgeryConsentType;
  status?: ConsentFormStatus;
  patient_id?: number;
  surgeon_id?: number;
  start_date?: string;
  end_date?: string;
  scheduled_date?: string;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

/**
 * Surgery consent list response
 */
export interface SurgeryConsentListResponse {
  items: SurgeryConsentSummary[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

/**
 * Complete surgery consent form structure
 */
export interface SurgeryConsentForm {
  id: number;
  consent_form_number: string;
  consent_type: SurgeryConsentType;
  consent_status: ConsentFormStatus;
  emergency_classification: EmergencyClassification;

  // Patient
  patient: ConsentPatientInfo;

  // Procedure
  procedure_info: SurgicalProcedureInfo | DiagnosticProcedureInfo | BloodTransfusionInfo;
  scheduled_date: string;
  scheduled_time: string;

  // Anesthesia
  anesthesia_required: boolean;
  anesthesia_info?: AnesthesiaInfo;

  // Risks and benefits
  risks_and_benefits: RisksAndBenefits;

  // Informed consent process
  informed_consent_process: InformedConsentProcess;

  // Patient consent
  patient_consent: PatientConsent;
  witness?: ConsentWitness;

  // Medical team
  primary_surgeon: SurgeonInfo;
  medical_team?: MedicalTeam;

  // Facility
  facility: ConsentFacilityInfo;

  // Attachments
  attachments?: ConsentAttachment[];

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
 * Surgery consent summary for list view
 */
export interface SurgeryConsentSummary {
  id: number;
  consent_form_number: string;
  consent_type: SurgeryConsentType;
  consent_status: ConsentFormStatus;
  emergency_classification: EmergencyClassification;
  scheduled_date: string;
  scheduled_time: string;
  patient_name: string;
  medical_record_number: string;
  procedure_name: string;
  surgeon_name: string;
  is_consent_given: boolean;
  consent_date?: string;
  created_at: string;
}

/**
 * Surgery consent print request
 */
export interface PrintSurgeryConsentRequest {
  consent_form_id: number;
  copies: number;
  include_attachments: boolean;
  printer_name?: string;
  duplex?: boolean;
  color?: boolean;
}

/**
 * Surgery consent print response
 */
export interface PrintSurgeryConsentResponse {
  success: boolean;
  data?: {
    print_job_id?: string;
    print_url?: string;
    consent_form_url: string;
    qr_code_url?: string;
  };
  message?: string;
  error?: {
    code: string;
    message: string;
  };
}

/**
 * Consent withdrawal request
 */
export interface WithdrawConsentRequest {
  consent_form_id: number;
  withdrawal_reason: string;
  withdrawn_by: number; // User ID
  withdrawal_date: string;
  witness_present: boolean;
  witness_signature_url?: string;
}

/**
 * Consent withdrawal response
 */
export interface WithdrawConsentResponse {
  success: boolean;
  data?: {
    consent_form_id: number;
    withdrawal_date: string;
    new_status: ConsentFormStatus;
  };
  message?: string;
  error?: {
    code: string;
    message: string;
  };
}

/**
 * Surgery consent statistics
 */
export interface SurgeryConsentStatistics {
  today_total: number;
  today_by_type: Record<SurgeryConsentType, number>;
  pending: number;
  consented: number;
  refused: number;
  completed: number;
  cancelled: number;
  this_week: number;
  this_month: number;
}

/**
 * Surgery consent validation result
 */
export interface SurgeryConsentValidationResult {
  is_valid: boolean;
  field_errors: Array<{
    field: string;
    errors: string[];
  }>;
  general_errors: string[];
  warnings: string[];
}

/**
 * Surgery consent template configuration
 */
export interface SurgeryConsentTemplateConfig {
  consent_type: SurgeryConsentType;
  template_name: string;
  language: 'id' | 'en' | 'both';
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
// HELPER TYPES AND CONSTANTS
// ============================================================================

/**
 * Surgery consent type with Indonesian label
 */
export interface SurgeryConsentTypeOption {
  value: SurgeryConsentType;
  label: string;
  label_indonesian: string;
  description: string;
}

/**
 * Surgery consent type options with labels
 */
export const SURGERY_CONSENT_TYPE_OPTIONS: SurgeryConsentTypeOption[] = [
  {
    value: 'SURGERY',
    label: 'Surgery Consent',
    label_indonesian: 'Persetujuan Tindakan Operasi',
    description: 'Informed consent for surgical procedures',
  },
  {
    value: 'ANESTHESIA',
    label: 'Anesthesia Consent',
    label_indonesian: 'Persetujuan Tindakan Anestesi',
    description: 'Informed consent for anesthesia administration',
  },
  {
    value: 'BLOOD_TRANSFUSION',
    label: 'Blood Transfusion Consent',
    label_indonesian: 'Persetujuan Transfusi Darah',
    description: 'Informed consent for blood transfusion',
  },
  {
    value: 'PROCEDURE',
    label: 'Medical Procedure Consent',
    label_indonesian: 'Persetujuan Tindakan Medis',
    description: 'Informed consent for medical procedures',
  },
  {
    value: 'DIAGNOSTIC',
    label: 'Diagnostic Procedure Consent',
    label_indonesian: 'Persetujuan Pemeriksaan Diagnostik',
    description: 'Informed consent for diagnostic procedures',
  },
  {
    value: 'SPECIAL_PROCEDURE',
    label: 'Special Procedure Consent',
    label_indonesian: 'Persetujuan Tindakan Khusus',
    description: 'Informed consent for special procedures',
  },
  {
    value: 'PEDIATRIC',
    label: 'Pediatric Consent',
    label_indonesian: 'Persetujuan Tindakan Anak',
    description: 'Informed consent for pediatric patients (with guardian)',
  },
  {
    value: 'EMERGENCY',
    label: 'Emergency Consent',
    label_indonesian: 'Persetujuan Kondisi Gawat Darurat',
    description: 'Emergency consent procedures',
  },
];

/**
 * Get consent type label in Indonesian
 */
export function getSurgeryConsentTypeLabel(type: SurgeryConsentType): string {
  return SURGERY_CONSENT_TYPE_OPTIONS.find(opt => opt.value === type)?.label_indonesian || type;
}

/**
 * Consent form status with Indonesian label
 */
export interface ConsentFormStatusOption {
  value: ConsentFormStatus;
  label: string;
  label_indonesian: string;
  color: string;
}

/**
 * Consent form status options
 */
export const CONSENT_FORM_STATUS_OPTIONS: ConsentFormStatusOption[] = [
  {
    value: 'draft',
    label: 'Draft',
    label_indonesian: 'Konsep',
    color: 'gray',
  },
  {
    value: 'pending',
    label: 'Pending',
    label_indonesian: 'Menunggu Persetujuan',
    color: 'yellow',
  },
  {
    value: 'acknowledged',
    label: 'Acknowledged',
    label_indonesian: 'Sudah Menerima Informasi',
    color: 'blue',
  },
  {
    value: 'consented',
    label: 'Consented',
    label_indonesian: 'Disetujui',
    color: 'green',
  },
  {
    value: 'refused',
    label: 'Refused',
    label_indonesian: 'Ditolak',
    color: 'red',
  },
  {
    value: 'cancelled',
    label: 'Cancelled',
    label_indonesian: 'Dibatalkan',
    color: 'orange',
  },
  {
    value: 'completed',
    label: 'Completed',
    label_indonesian: 'Selesai',
    color: 'purple',
  },
  {
    value: 'expired',
    label: 'Expired',
    label_indonesian: 'Kadaluarsa',
    color: 'gray',
  },
];

/**
 * Anesthesia type with Indonesian label
 */
export interface AnesthesiaTypeOption {
  value: AnesthesiaType;
  label_indonesian: string;
  description: string;
}

/**
 * Anesthesia type options
 */
export const ANESTHESIA_TYPE_OPTIONS: AnesthesiaTypeOption[] = [
  {
    value: 'local',
    label_indonesian: 'Anestesi Lokal',
    description: 'Anestesi pada area tertentu saja',
  },
  {
    value: 'regional',
    label_indonesian: 'Anestesi Regional',
    description: 'Anestesi spinal atau epidural',
  },
  {
    value: 'general',
    label_indonesian: 'Anestesi Umum',
    description: 'Pasien tidur total',
  },
  {
    value: 'sedation',
    label_indonesian: 'Sedasi',
    description: 'Pasien relaks tapi tetap sadar',
  },
  {
    value: 'none',
    label_indonesian: 'Tanpa Anestesi',
    description: 'Tindakan tanpa anestesi',
  },
];

/**
 * Risk level with Indonesian label
 */
export interface RiskLevelOption {
  value: RiskLevel;
  label_indonesian: string;
  color: string;
}

/**
 * Risk level options
 */
export const RISK_LEVEL_OPTIONS: RiskLevelOption[] = [
  {
    value: 'very_low',
    label_indonesian: 'Sangat Rendah (<0.01%)',
    color: 'green',
  },
  {
    value: 'low',
    label_indonesian: 'Rendah (0.01-1%)',
    color: 'light-green',
  },
  {
    value: 'moderate',
    label_indonesian: 'Sedang (1-10%)',
    color: 'yellow',
  },
  {
    value: 'high',
    label_indonesian: 'Tinggi (10-50%)',
    color: 'orange',
  },
  {
    value: 'very_high',
    label_indonesian: 'Sangat Tinggi (>50%)',
    color: 'red',
  },
];

/**
 * Blood product type with Indonesian label
 */
export interface BloodProductTypeOption {
  value: BloodTransfusionInfo['blood_product_type'];
  label_indonesian: string;
  description: string;
}

/**
 * Blood product type options
 */
export const BLOOD_PRODUCT_TYPE_OPTIONS: BloodProductTypeOption[] = [
  {
    value: 'whole_blood',
    label_indonesian: 'Darah Utuh',
    description: 'Whole blood transfusion',
  },
  {
    value: 'prbc',
    label_indonesian: 'Packed Red Blood Cells',
    description: 'Red blood cell concentrate',
  },
  {
    value: 'platelets',
    label_indonesian: 'Trombosit',
    description: 'Platelet concentrate',
  },
  {
    value: 'ffp',
    label_indonesian: 'Fresh Frozen Plasma',
    description: 'Plasma frozen segar',
  },
  {
    value: 'cryoprecipitate',
    label_indonesian: 'Kriopresipitat',
    description: 'Cryoprecipitate',
  },
  {
    value: 'other',
    label_indonesian: 'Lainnya',
    description: 'Other blood products',
  },
];

/**
 * Common surgical risks for reference
 */
export const COMMON_SURGICAL_RISKS: Partial<ProcedureRisk>[] = [
  {
    category: 'common',
    risk_name_id: 'Perdarahan',
    risk_name_en: 'Bleeding',
    severity: 'moderate',
    is_life_threatening: false,
    probability_percentage: 5,
  },
  {
    category: 'common',
    risk_name_id: 'Infeksi Luka Operasi',
    risk_name_en: 'Surgical Site Infection',
    severity: 'moderate',
    is_life_threatening: false,
    probability_percentage: 3,
  },
  {
    category: 'uncommon',
    risk_name_id: 'Gangguan Pembekuan Darah',
    risk_name_en: 'Blood Clotting Disorders',
    severity: 'high',
    is_life_threatening: true,
    probability_percentage: 0.5,
  },
  {
    category: 'rare',
    risk_name_id: 'Kerusakan Saraf',
    risk_name_en: 'Nerve Damage',
    severity: 'high',
    is_life_threatening: false,
    probability_percentage: 0.1,
  },
  {
    category: 'rare',
    risk_name_id: 'Reaksi Anestesi Berat',
    risk_name_en: 'Severe Anesthesia Reaction',
    severity: 'very_high',
    is_life_threatening: true,
    probability_percentage: 0.01,
  },
];
