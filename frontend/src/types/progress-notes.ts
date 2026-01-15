/**
 * Progress Notes Types for SIMRS
 * Comprehensive type definitions for progress notes documentation
 * Compatible with Indonesian healthcare requirements and standards
 * Supports SOAP note format and various note types
 */

// ============================================================================
// NOTE TYPES - All Indonesian Progress Note Types
// ============================================================================

/**
 * Progress note types in Indonesian healthcare context
 */
export type ProgressNoteType =
  | 'daily_progress'      // Catatan Harian - Daily progress notes
  | 'nursing'             // Catatan Keperawatan - Nursing notes
  | 'physician'           // Catatan Dokter - Physician notes
  | 'consultation'        // Catatan Konsultasi - Consultation notes
  | 'procedure'           // Catatan Tindakan - Procedure notes
  | 'discharge'           // Catatan Pulang - Discharge notes
  | 'transfer';           // Catatan Rujukan Internal - Transfer notes

/**
 * Progress note category for organization
 */
export type ProgressNoteCategory =
  | 'admission'           // Rawat inap
  | 'daily_care'          // Perawatan harian
  | 'emergency'           // Gawat darurat
  | 'outpatient'          // Rawat jalan
  | 'icu'                 // ICU
  | 'surgery'             // Bedah
  | 'delivery'            // Persalinan
  | 'pediatric'           // Anak
  | 'geriatric';          // Geriatri

/**
 * Note priority/urgency level
 */
export type NotePriority =
  | 'routine'             // Rutin
  | 'urgent'              // Segera
  | 'critical'            // Kritis
  | 'follow_up';          // Tindak lanjut

// ============================================================================
// PATIENT INFORMATION TYPES - Patient Data for Progress Notes
// ============================================================================

/**
 * Patient information for progress notes context
 */
export interface ProgressNotePatientInfo {
  /** Patient ID */
  patient_id: string;

  /** Medical record number (Rekam Medis) */
  rm_number: string;

  /** Patient name */
  name: string;

  /** Date of birth */
  date_of_birth: string;

  /** Age in years */
  age_years: number;

  /** Age in months (for pediatrics) */
  age_months?: number;

  /** Age in days (for neonates) */
  age_days?: number;

  /** Gender */
  gender: 'male' | 'female';

  /** Blood type */
  blood_type?: 'A' | 'B' | 'AB' | 'O';

  /** Rh factor */
  rh_factor?: 'positive' | 'negative';

  /** Known allergies */
  allergies: Allergy[];

  /** Active diagnoses */
  diagnoses: ActiveDiagnosis[];

  /** Current medications */
  current_medications: CurrentMedication[];

  /** Comorbidities */
  comorbidities?: string[];

  /** Advance directives */
  advance_directives?: string;

  /** Code status */
  code_status?: CodeStatus;
}

/**
 * Allergy information
 */
export interface Allergy {
  /** Allergen (substance) */
  allergen: string;

  /** Allergy type */
  type: AllergyType;

  /** Severity */
  severity: AllergySeverity;

  /** Reaction description */
  reaction: string;

  /** Onset date */
  onset_date?: string;

  /** Is this allergy active? */
  is_active: boolean;

  /** Verified by */
  verified_by?: string;
}

/**
 * Allergy types
 */
export type AllergyType =
  | 'drug'                // Obat
  | 'food'                // Makanan
  | 'environmental'       // Lingkungan
  | 'latex'               // Lateks
  | 'other';              // Lainnya

/**
 * Allergy severity levels
 */
export type AllergySeverity =
  | 'mild'                // Ringan
  | 'moderate'            // Sedang
  | 'severe'              // Berat
  | 'life_threatening';   // Mengancam jiwa

/**
 * Active diagnosis information
 */
export interface ActiveDiagnosis {
  /** Diagnosis code (ICD-10) */
  code: string;

  /** Diagnosis name */
  name: string;

  /** Is this the primary diagnosis? */
  is_primary: boolean;

  /** Diagnosis status */
  status: DiagnosisStatus;

  /** Onset date */
  onset_date: string;

  /** Notes */
  notes?: string;
}

/**
 * Diagnosis status
 */
export type DiagnosisStatus =
  | 'active'              // Aktif
  | 'improving'           // Membaik
  | 'worsening'           // Memburuk
  | 'resolved'            // Sembuh
  | 'chronic';            // Kronis

/**
 * Current medication information
 */
export interface CurrentMedication {
  /** Medication name */
  name: string;

  /** Generic name */
  generic_name?: string;

  /** Dosage */
  dosage: string;

  /** Frequency */
  frequency: string;

  /** Route */
  route: MedicationRoute;

  /** Start date */
  start_date: string;

  /** Indication */
  indication?: string;

  /** Is PRN (as needed)? */
  is_prn: boolean;

  /** PRN indication */
  prn_indication?: string;
}

/**
 * Medication administration routes
 */
export type MedicationRoute =
  | 'oral'                // Oral
  | 'iv'                  // Intravena
  | 'im'                  // Intramuskular
  | 'sc'                  // Subkutan
  | 'sl'                  // Sublingual
  | 'topical'             // Topikal
  | 'inhaled'             // Inhalasi
  | 'rectal'              // Rektal
  | 'nasogastric'         // Nasogastrik
  | 'eye'                 // Mata
  | 'ear'                 // Telinga
  | 'intrathecal';        // Intratekal

/**
 * Patient code status (resuscitation status)
 */
export type CodeStatus =
  | 'full_code'           // Full resuscitation
  | 'dnr'                 // Do Not Resuscitate
  | 'dnar'                // Do Not Attempt Resuscitation
  | 'partial_code';       // Partial measures

// ============================================================================
// CLINICAL STATUS TYPES - SOAP Note Format (Subjective, Objective, Assessment, Plan)
// ============================================================================

/**
 * SOAP note structure - Standard clinical documentation format
 */
export interface SOAPNote {
  /** Subjective - What the patient says or feels */
  subjective: Subjective;

  /** Objective - What you observe, measure, or test */
  objective: Objective;

  /** Assessment - Your interpretation or diagnosis */
  assessment: Assessment;

  /** Plan - What you will do about it */
  plan: Plan;
}

/**
 * Subjective component of SOAP note
 * Patient's reported symptoms, concerns, and history
 */
export interface Subjective {
  /** Chief complaint (Keluhan Utama) in patient's words */
  chief_complaint: string;

  /** History of present illness (Riwayat Penyakit Sekarang) */
  hpi?: string;

  /** Symptom analysis */
  symptoms?: SymptomAnalysis[];

  /** Patient's current condition description */
  condition_description?: string;

  /** Pain assessment */
  pain_assessment?: PainAssessment;

  /** Patient reported concerns */
  concerns?: string[];

  /** Review of systems */
  review_of_systems?: ReviewOfSystems;

  /** Patient's perception of progress */
  patient_perception?: string;

  /** Recent changes reported by patient */
  recent_changes?: string[];

  /** Additional subjective notes */
  notes?: string;
}

/**
 * Symptom analysis for detailed symptom documentation
 */
export interface SymptomAnalysis {
  /** Symptom name */
  symptom: string;

  /** Onset */
  onset: string;

  /** Duration */
  duration: string;

  /** Location */
  location?: string;

  /** Severity (0-10) */
  severity: number;

  /** Quality/description */
  quality: string;

  /** What makes it worse */
  aggravating_factors?: string[];

  /** What makes it better */
  relieving_factors?: string[];

  /** Associated symptoms */
  associated_symptoms?: string[];

  /** Timing/pattern */
  timing?: string;

  /** Previous treatments and response */
  previous_treatments?: string;
}

/**
 * Pain assessment documentation
 */
export interface PainAssessment {
  /** Pain score (0-10) */
  score: number;

  /** Pain location */
  location: string;

  /** Pain quality */
  quality: PainQuality;

  /** Onset */
  onset: PainOnset;

  /** Duration */
  duration: string;

  /** Frequency */
  frequency: PainFrequency;

  /** What aggravates the pain */
  aggravating_factors?: string[];

  /** What relieves the pain */
  relieving_factors?: string[];

  /** Current pain management */
  current_management?: string;

  /** Effectiveness of current management */
  management_effectiveness?: string;
}

/**
 * Pain quality descriptions
 */
export type PainQuality =
  | 'sharp'               // Tajam
  | 'dull'                // Tumpul
  | 'throbbing'           // Berdebar
  | 'burning'             // Terbakar
  | 'cramping'            // Kram
  | 'aching'              // Nyeri
  | 'stabbing'            // Tusukan
  | 'pressing'            // Tekan
  | 'radiating'           // Menjalar
  | 'colicky'             // Kolik
  | 'phantom';            // Fantom

/**
 * Pain onset patterns
 */
export type PainOnset =
  | 'acute'               // Akut
  | 'gradual'             // Bertahap
  | 'sudden'              // Tiba-tiba
  | 'intermittent'        // Intermiten
  | 'constant';           // Konstan

/**
 * Pain frequency
 */
export type PainFrequency =
  | 'continuous'          // Terus-menerus
  | 'intermittent'        // Intermiten
  | 'episodic'            // Episodik
  | 'periodic';           // Periodik

/**
 * Review of systems checklist
 */
export interface ReviewOfSystems {
  /** General */
  general?: string;

  /** Constitutional */
  constitutional?: string;

  /** Eyes */
  eyes?: string;

  /** ENT (Ear, Nose, Throat) */
  ent?: string;

  /** Cardiovascular */
  cardiovascular?: string;

  /** Respiratory */
  respiratory?: string;

  /** Gastrointestinal */
  gastrointestinal?: string;

  /** Genitourinary */
  genitourinary?: string;

  /** Musculoskeletal */
  musculoskeletal?: string;

  /** Neurological */
  neurological?: string;

  /** Psychiatric */
  psychiatric?: string;

  /** Endocrine */
  endocrine?: string;

  /** Dermatologic */
  dermatologic?: string;

  /** Positive findings only flag */
  positive_findings_only?: boolean;
}

/**
 * Objective component of SOAP note
 * Observable, measurable findings
 */
export interface Objective {
  /** Vital signs */
  vital_signs?: VitalSignsObjective;

  /** Physical examination findings */
  physical_exam?: PhysicalExamination;

  /** Laboratory results */
  laboratory_results?: LabResult[];

  /** Imaging results */
  imaging_results?: ImagingResult[];

  /** Diagnostic tests */
  diagnostic_tests?: DiagnosticTest[];

  /** Functional status */
  functional_status?: FunctionalStatus;

  /** Mental status */
  mental_status?: MentalStatus;

  /** Nutrition status */
  nutrition_status?: NutritionStatus;

  /** Wound assessment */
  wound_assessment?: WoundAssessment;

  /** Device/equipment status */
  device_status?: DeviceStatus[];

  /** Other objective findings */
  other_findings?: string[];
}

/**
 * Vital signs in objective section
 */
export interface VitalSignsObjective {
  /** Blood pressure */
  blood_pressure?: {
    systolic: number;
    diastolic: number;
    position: string;
  };

  /** Heart rate */
  heart_rate?: {
    rate: number;
    rhythm: string;
  };

  /** Respiratory rate */
  respiratory_rate?: {
    rate: number;
    pattern: string;
  };

  /** Temperature */
  temperature?: {
    value: number;
    unit: 'C' | 'F';
    site: string;
  };

  /** Oxygen saturation */
  spo2?: {
    saturation: number;
    on_oxygen: boolean;
  };

  /** Pain score */
  pain_score?: number;

  /** GCS */
  gcs?: {
    eye: number;
    verbal: number;
    motor: number;
    total: number;
  };

  /** Blood glucose */
  blood_glucose?: {
    value: number;
    timing: string;
  };

  /** Height */
  height?: {
    value: number;
    unit: string;
  };

  /** Weight */
  weight?: {
    value: number;
    unit: string;
  };

  /** BMI */
  bmi?: {
    value: number;
    category: string;
  };

  /** Urine output */
  urine_output?: {
    volume: number;
    period: string;
  };
}

/**
 * Physical examination findings
 */
export interface PhysicalExamination {
  /** General appearance */
  general_appearance?: string;

  /** HEENT (Head, Eyes, Ears, Nose, Throat) */
  heent?: string;

  /** Cardiovascular */
  cardiovascular?: string;

  /** Respiratory */
  respiratory?: string;

  /** Abdomen */
  abdomen?: string;

  /** Musculoskeletal */
  musculoskeletal?: string;

  /** Neurological */
  neurological?: string;

  /** Skin */
  skin?: string;

  /** Lymphatic */
  lymphatic?: string;

  /** Psychiatric */
  psychiatric?: string;

  /** Additional findings by body system */
  additional_findings?: Record<string, string>;
}

/**
 * Laboratory result reference
 */
export interface LabResult {
  /** Test name */
  test_name: string;

  /** Test result */
  result: string;

  /** Normal range */
  normal_range?: string;

  /** Is abnormal? */
  is_abnormal: boolean;

  /** Clinical significance */
  significance?: 'critical' | 'abnormal' | 'borderline' | 'normal';

  /** Test date/time */
  test_datetime: string;

  /** Comments */
  comments?: string;
}

/**
 * Imaging result reference
 */
export interface ImagingResult {
  /** Imaging type */
  imaging_type: ImagingType;

  /** Body part/region */
  body_part: string;

  /** Exam date */
  exam_date: string;

  /** Findings summary */
  findings: string;

  /** Impression */
  impression?: string;

  /** Comparison to previous */
  comparison?: string;

  /** Is there a significant change? */
  significant_change: boolean;
}

/**
 * Imaging types
 */
export type ImagingType =
  | 'xray'                // Rontgen
  | 'ct_scan'             // CT Scan
  | 'mri'                 // MRI
  | 'ultrasound'          // USG
  | 'echocardiography'    // Echocardiography
  | 'mammography'         // Mammografi
  | 'fluoroscopy'         // Fluoroskopi
  | 'pet_scan';           // PET Scan

/**
 * Diagnostic test reference
 */
export interface DiagnosticTest {
  /** Test name */
  test_name: string;

  /** Test type */
  test_type: string;

  /** Result */
  result: string;

  /** Interpretation */
  interpretation?: string;

  /** Test date */
  test_date: string;

  /** Is abnormal? */
  is_abnormal: boolean;
}

/**
 * Functional status assessment
 */
export interface FunctionalStatus {
  /** Activity level */
  activity_level: ActivityLevel;

  /** Mobility status */
  mobility: MobilityStatus;

  /** Self-care ability */
  self_care: SelfCareAbility;

  /** ADL (Activities of Daily Living) score */
  adl_score?: number;

  /** Functional limitations */
  limitations?: string[];

  /** Assistive devices used */
  assistive_devices?: string[];

  /** Physical therapy needs */
  pt_needs?: string;
}

/**
 * Activity levels
 */
export type ActivityLevel =
  | 'bedbound'            // Terbaring di tempat tidur
  | 'bedrest'             // Istirahat di tempat tidur
  | 'bed_to_chair'        // Tempat tidur ke kursi
  | 'limited'             // Terbatas
  | 'normal'              // Normal
  | 'athletic';           // Atletik

/**
 * Mobility status
 */
export type MobilityStatus =
  | 'independent'         // Mandiri
  | 'requires_assist'     // Membutuhkan bantuan
  | 'requires_device'     // Membutuhkan alat bantu
  | 'dependent'           // Bergantung
  | 'immobile';           // Imobilitas

/**
 * Self-care ability
 */
export type SelfCareAbility =
  | 'independent'         // Mandiri
  | 'requires_assist'     // Membutuhkan bantuan
  | 'dependent';          // Bergantung

/**
 * Mental status examination
 */
export interface MentalStatus {
  /** Alert/oriented status */
  alert_oriented: string;

  /** Level of consciousness */
  consciousness: ConsciousnessLevel;

  /** Mood */
  mood?: string;

  /** Affect */
  affect?: string;

  /** Thought process */
  thought_process?: string;

  /** Memory */
  memory?: string;

  /** Judgment */
  judgment?: string;

  /** Insight */
  insight?: string;

  /** Behavior observations */
  behavior?: string;
}

/**
 * Consciousness levels
 */
export type ConsciousnessLevel =
  | 'alert'               // Sadar penuh
  | 'lethargic'           // Lesu
  | 'obtunded'            // Lamban
  | 'stupor'              // Stupor
  | 'comatose';           // Koma

/**
 * Nutrition status assessment
 */
export interface NutritionStatus {
  /** Dietary restrictions */
  dietary_restrictions?: string[];

  /** Current diet */
  current_diet?: string;

  /** Appetite */
  appetite: AppetiteLevel;

  /** Nutritional concerns */
  concerns?: string[];

  /** Special nutritional requirements */
  special_requirements?: string;

  /** Feeding assistance needed */
  feeding_assistance?: 'none' | 'partial' | 'complete';

  /** Last oral intake */
  last_oral_intake?: string;
}

/**
 * Appetite levels
 */
export type AppetiteLevel =
  | 'good'                // Baik
  | 'fair'                // Cukup
  | 'poor'                // Buruk
  | 'absent';             // Tidak ada

/**
 * Wound assessment
 */
export interface WoundAssessment {
  /** Wound location */
  location: string;

  /** Wound type */
  type: WoundType;

  /** Wound size (length x width x depth) */
  size: {
    length: number;
    width: number;
    depth?: number;
    unit: 'cm' | 'mm';
  };

  /** Wound appearance */
  appearance: string;

  /** Exudate description */
  exudate?: {
    amount: ExudateAmount;
    color?: string;
    odor?: boolean;
    type?: string;
  };

  /** Wound edges */
  edges?: WoundEdge;

  /** Periwound skin */
  periwound_skin?: string;

  /** Pain level at wound site */
  pain?: number;

  /** Signs of infection */
  signs_of_infection?: string[];

  /** Treatment applied */
  treatment?: string;
}

/**
 * Wound types
 */
export type WoundType =
  | 'surgical'            // Luka bedah
  | 'pressure'            // Luka tekan
  | 'traumatic'           // Luka trauma
  | 'burn'                // Luka bakar
  | 'diabetic'            // Luka diabetes
  | 'vascular'            // Luka vaskular
  | 'other';              // Lainnya

/**
 * Exudate amount
 */
export type ExudateAmount =
  | 'none'                // Tidak ada
  | 'scant'               // Sedikit
  | 'moderate'            // Sedang
  | 'copious';            // Banyak

/**
 * Wound edge characteristics
 */
export type WoundEdge =
  | 'clean'               // Bersih
  | 'macerated'           // Makerasi
  | 'rolled'              // Menggulung
  | 'undermined'          // Undermined
  | 'epiboly';            // Epiboly

/**
 * Device/equipment status
 */
export interface DeviceStatus {
  /** Device name */
  device_name: string;

  /** Device type */
  device_type: string;

  /** Location/position */
  location?: string;

  /** Settings/parameters */
  settings?: string;

  /** Is functioning properly? */
  is_functional: boolean;

  /** Issues/concerns */
  concerns?: string;
}

/**
 * Assessment component of SOAP note
 * Clinical judgment and interpretation
 */
export interface Assessment {
  /** Primary diagnosis */
  primary_diagnosis: string;

  /** ICD-10 code */
  icd_code?: string;

  /** Secondary diagnoses */
  secondary_diagnoses?: string[];

  /** Clinical condition summary */
  condition_summary: string;

  /** Severity assessment */
  severity: SeverityLevel;

  /** Clinical status */
  clinical_status: ClinicalStatus;

  /** Progress status */
  progress_status: ProgressStatus;

  /** Response to treatment */
  treatment_response: TreatmentResponse;

  /** Prognosis */
  prognosis?: Prognosis;

  /** Active problems list */
  problems?: Problem[];

  /** Differential diagnoses (if applicable) */
  differential_diagnoses?: string[];

  /** Clinical reasoning */
  clinical_reasoning?: string;

  /** Risk assessment */
  risk_assessment?: RiskAssessment;
}

/**
 * Severity levels
 */
export type SeverityLevel =
  | 'mild'                // Ringan
  | 'moderate'            // Sedang
  | 'severe'              // Berat
  | 'critical';           // Kritis

/**
 * Clinical status
 */
export type ClinicalStatus =
  | 'stable'              // Stabil
  | 'improving'           // Membaik
  | 'deteriorating'       // Memburuk
  | 'critical'            // Kritis
  | 'unchanged';          // Tidak berubah

/**
 * Progress status
 */
export type ProgressStatus =
  | 'improving'           // Membaik
  | 'stable'              // Stabil
  | 'worsening'           // Memburuk
  | 'resolved'            // Sembuh
  | 'complicated';        // Komplikasi

/**
 * Treatment response
 */
export type TreatmentResponse =
  | 'excellent'           // Sangat baik
  | 'good'                // Baik
  | 'fair'                // Cukup
  | 'poor'                // Buruk
  | 'none';               // Tidak ada

/**
 * Prognosis categories
 */
export type Prognosis =
  | 'excellent'           // Sangat baik
  | 'good'                // Baik
  | 'fair'                // Cukup
  | 'guarded'             // Terjaga
  | 'poor'                // Buruk
  | 'terminal';           // Terminal

/**
 * Active problem in problem list
 */
export interface Problem {
  /** Problem name/description */
  problem: string;

  /** Onset date */
  onset_date: string;

  /** Is active? */
  is_active: boolean;

  /** Severity */
  severity: SeverityLevel;

  /** Status */
  status: ProblemStatus;

  /** Notes */
  notes?: string;
}

/**
 * Problem status
 */
export type ProblemStatus =
  | 'acute'               // Akut
  | 'chronic'             // Kronis
  | 'resolving'           // Membaik
  | 'resolved'            // Sembuh
  | 'recurrent';          // Kambuh

/**
 * Risk assessment
 */
export interface RiskAssessment {
  /** Fall risk */
  fall_risk: RiskLevel;

  /** Pressure ulcer risk */
  pressure_ulcer_risk: RiskLevel;

  /** Infection risk */
  infection_risk: RiskLevel;

  /** Bleeding risk */
  bleeding_risk?: RiskLevel;

  /** Other risks */
  other_risks?: Array<{
    risk: string;
    level: RiskLevel;
  }>;
}

/**
 * Risk levels
 */
export type RiskLevel =
  | 'low'                 // Rendah
  | 'moderate'            // Sedang
  | 'high'                // Tinggi
  | 'very_high';          // Sangat tinggi

/**
 * Plan component of SOAP note
 * Action items and next steps
 */
export interface Plan {
  /** Diagnostic plan */
  diagnostic_plan?: DiagnosticPlan[];

  /** Treatment plan */
  treatment_plan?: TreatmentPlan[];

  /** Medication plan */
  medication_plan?: MedicationPlan[];

  /** Nursing care plan */
  nursing_plan?: NursingPlan[];

  /** Consultations requested */
  consultations?: ConsultationPlan[];

  ** Patient education */
  patient_education?: PatientEducation[];

  /** Discharge planning */
  discharge_planning?: DischargePlanning;

  /** Follow-up plan */
  follow_up: FollowUpPlan;

  /** Goals */
  goals?: Goal[];

  /** Precautions */
  precautions?: string[];

  /** Additional notes */
  notes?: string;
}

/**
 * Diagnostic plan item
 */
export interface DiagnosticPlan {
  /** Test/procedure name */
  test_name: string;

  /** Test type */
  test_type: string;

  ** Indication */
  indication: string;

  /** Priority */
  priority: PlanPriority;

  /** When to perform */
  timing: string;

  /** Who to order from */
  ordered_by?: string;

  /** Special instructions */
  instructions?: string;

  /** Estimated completion date */
  expected_completion?: string;
}

/**
 * Plan priority
 */
export type PlanPriority =
  | 'routine'             // Rutin
  | 'urgent'              // Segera
  | 'stat'                // Segera sekali
  | 'elective';           // Elektif

/**
 * Treatment plan item
 */
export interface TreatmentPlan {
  ** Treatment name */
  treatment: string;

  /** Treatment type */
  type: TreatmentType;

  /** Indication */
  indication: string;

  /** Frequency/dosage */
  frequency: string;

  /** Duration */
  duration: string;

  /** Who will perform */
  performed_by?: string;

  /** Start date */
  start_date: string;

  /** Expected outcomes */
  expected_outcomes?: string;
}

/**
 * Treatment types
 */
export type TreatmentType =
  | 'medication'          // Obat
  | 'procedure'           // Tindakan
  | 'therapy'             // Terapi
  | 'rehabilitation'      // Rehabilitasi
  | 'surgery'             // Bedah
  | 'monitoring'          // Monitoring
  | 'dietary'             // Diet
  | 'other';              // Lainnya

/**
 * Medication plan item
 */
export interface MedicationPlan {
  /** Medication name */
  medication: string;

  /** Generic name */
  generic_name?: string;

  /** Dosage */
  dosage: string;

  /** Route */
  route: MedicationRoute;

  /** Frequency */
  frequency: string;

  /** Indication */
  indication: string;

  /** Duration */
  duration: string;

  /** Is PRN? */
  is_prn: boolean;

  /** PRN indication */
  prn_indication?: string;

  /** Special instructions */
  instructions?: string;

  /** Start date */
  start_date: string;

  /** Prescribed by */
  prescribed_by: string;
}

/**
 * Nursing care plan item
 */
export interface NursingPlan {
  /** Nursing intervention */
  intervention: string;

  /** Goal/outcome */
  goal: string;

  /** Frequency */
  frequency?: string;

  ** Priority */
  priority: PlanPriority;

  /** Who will perform */
  performed_by?: string;

  /** Start date */
  start_date?: string;

  /** Evaluation criteria */
  evaluation_criteria?: string;
}

/**
 * Consultation plan
 */
export interface ConsultationPlan {
  /** Specialty to consult */
  specialty: string;

  /** Reason for consultation */
  reason: string;

  ** Specific questions */
  questions?: string[];

  /** Priority */
  priority: PlanPriority;

  /** When consultation needed */
  timing: string;

  ** Consulted by */
  consulted_by?: string;
}

/**
 * Patient education item
 */
export interface PatientEducation {
  /** Topic */
  topic: string;

  /** Content/instructions */
  content: string;

  /** Method used */
  method: EducationMethod;

  /** Patient understanding */
  understanding: UnderstandingLevel;

  /** Who provided education */
  provided_by: string;

  /** Date provided */
  date_provided: string;

  ** Follow-up needed? */
  follow_up_needed: boolean;
}

/**
 * Education methods
 */
export type EducationMethod =
  | 'verbal'              // Lisan
  | 'written'             // Tertulis
  | 'demonstration'       // Demonstrasi
  | 'video'               // Video
  | 'handout'             // Brosur
  | 'other';              // Lainnya

/**
 * Understanding levels
 */
export type UnderstandingLevel =
  | 'full'                // Penuh
  | 'partial'             // Sebagian
  | 'minimal'             // Minimal
  | 'none';               // Tidak ada

/**
 * Discharge planning
 */
export interface DischargePlanning {
  /** Anticipated discharge date */
  anticipated_date?: string;

  /** Discharge destination */
  destination?: DischargeDestination;

  ** Discharge criteria */
  criteria?: string[];

  /** Equipment needed */
  equipment_needed?: string[];

  /** Services needed */
  services_needed?: string[];

  /** Family/patient education completed */
  education_completed?: boolean;

  /** Pending items */
  pending_items?: string[];
}

/**
 * Discharge destinations
 */
export type DischargeDestination =
  | 'home'                // Rumah
  | 'home_with_services'  // Rumah dengan layanan
  | 'rehab_facility'      // Fasilitas rehabilitasi
  | 'skilled_nursing'     // Perawat terampil
  | 'long_term_care'      // Perawatan jangka panjang
  | 'other_hospital'      // Rumah sakit lain
  | 'transfer'            // Rujukan
  | 'ama';                // Atas permintaan sendiri

/**
 * Follow-up plan
 */
export interface FollowUpPlan {
  /** Follow-up needed? */
  follow_up_needed: boolean;

  /** When to follow up */
  timing?: string;

  /** Follow-up location */
  location?: string;

  /** Which specialty/department */
  specialty?: string;

  /** Specific provider (if any) */
  provider?: string;

  ** Purpose of follow-up */
  purpose?: string;

  /** Contact information */
  contact_info?: string;
}

/**
 * Goal for patient care
 */
export interface Goal {
  /** Goal description */
  goal: string;

  ** Goal type */
  type: GoalType;

  /** Target/measurable outcome */
  target?: string;

  /** Time frame */
  time_frame?: string;

  ** Is goal achieved? */
  achieved: boolean;

  /** Progress toward goal */
  progress?: GoalProgress;
}

/**
 * Goal types
 */
export type GoalType =
  | 'clinical'            // Klinis
  | 'functional'          // Fungsional
  | 'educational'         // Edukasi
  | 'discharge'           // Pulang
  | 'quality_of_life';    // Kualitas hidup

/**
 * Goal progress
 */
export type GoalProgress =
  | 'not_started'         // Belum dimulai
  | 'in_progress'         // Sedang berjalan
  | 'maintaining'         // Memelihara
  | 'achieved';           // Tercapai

// ============================================================================
// VITAL SIGNS TYPES - Vital Signs Measurements in Progress Notes
// ============================================================================

/**
 * Vital signs summary for progress notes
 */
export interface VitalSignsSummary {
  /** Blood pressure */
  blood_pressure?: string;

  /** Heart rate */
  heart_rate?: string;

  /** Respiratory rate */
  respiratory_rate?: string;

  /** Temperature */
  temperature?: string;

  /** Oxygen saturation */
  spo2?: string;

  /** Pain score */
  pain_score?: string;

  ** GCS */
  gcs?: string;

  /** Blood glucose */
  blood_glucose?: string;

  /** Urine output */
  urine_output?: string;

  /** Summary statement */
  summary: string;

  /** Significant abnormalities */
  abnormalities?: string[];
}

// ============================================================================
// INTERVENTIONS TYPES - Medications, Procedures, Treatments
// ============================================================================

/**
 * Intervention performed
 */
export interface Intervention {
  /** Intervention name */
  name: string;

  /** Intervention type */
  type: InterventionType;

  /** Indication */
  indication: string;

  /** Details of intervention */
  details: string;

  /** Performed by */
  performed_by: string;

  ** Performed date/time */
  performed_at: string;

  /** Duration */
  duration?: string;

  /** Outcome */
  outcome?: string;

  /** Complications (if any) */
  complications?: string[];

  ** Follow-up required? */
  follow_up_required: boolean;

  /** Follow-up instructions */
  follow_up_instructions?: string;
}

/**
 * Intervention types
 */
export type InterventionType =
  | 'medication'          // Pemberian obat
  | 'procedure'           // Tindakan
  | 'therapy'             // Terapi
  | 'monitoring'          // Monitoring
  | 'diagnostic'          // Diagnostik
  | 'counseling'          // Konseling
  | 'education'           // Edukasi
  | 'rehabilitation'      // Rehabilitasi
  | 'surgery'             // Bedah
  | 'other';              // Lainnya

/**
 * Medication administration record
 */
export interface MedicationAdministration {
  /** Medication name */
  medication: string;

  /** Dosage */
  dosage: string;

  /** Route */
  route: MedicationRoute;

  /** Time administered */
  time_administered: string;

  /** Administered by */
  administered_by: string;

  /** Site (if applicable) */
  site?: string;

  /** Was this PRN? */
  is_prn: boolean;

  /** PRN indication */
  prn_indication?: string;

  /** Response to medication */
  response?: string;

  /** Side effects observed */
  side_effects?: string[];

  /** Was dose withheld? */
  dose_held?: boolean;

  /** Reason for holding dose */
  hold_reason?: string;
}

/**
 * Procedure performed
 */
export interface ProcedurePerformed {
  /** Procedure name */
  procedure_name: string;

  /** Procedure code (if applicable) */
  procedure_code?: string;

  ** Indication */
  indication: string;

  /** Consent obtained? */
  consent_obtained: boolean;

  ** Consent type */
  consent_type?: 'written' | 'verbal' | 'implied';

  /** Performed by */
  performed_by: string;

  ** Assisted by */
  assisted_by?: string[];

  /** Anesthesia used */
  anesthesia?: AnesthesiaType;

  /** Start time */
  start_time: string;

  /** End time */
  end_time?: string;

  ** Procedure details */
  details: string;

  ** Equipment used */
  equipment_used?: string[];

  /** Complications */
  complications?: string[];

  /** Immediate outcome */
  outcome: string;

  /** Post-procedure instructions */
  post_procedure_instructions?: string;

  ** Specimens obtained */
  specimens?: string[];
}

/**
 * Anesthesia types
 */
export type AnesthesiaType =
  | 'none'                // Tidak ada
  | 'local'               // Lokal
  | 'regional'            // Regional
  | 'general'             // Umum
  | 'sedation';           // Sedasi

/**
 * Treatment provided
 */
export interface Treatment {
  /** Treatment name */
  treatment: string;

  /** Treatment type */
  type: TreatmentType;

  /** Indication */
  indication: string;

  ** Details */
  details: string;

  /** Started by */
  started_by: string;

  /** Start date */
  start_date: string;

  /** Duration */
  duration?: string;

  /** Frequency */
  frequency?: string;

  ** Current status */
  status: TreatmentStatus;

  ** Progress/response */
  progress?: string;

  ** Expected outcomes */
  expected_outcomes?: string;

  ** Actual outcomes */
  actual_outcomes?: string;
}

/**
 * Treatment status
 */
export type TreatmentStatus =
  | 'planned'             // Rencana
  | 'in_progress'         // Sedang berjalan
  | 'completed'           // Selesai
  | 'discontinued'        // Dihentikan
  | 'on_hold';            // Ditunda

/**
 * Monitoring activity
 */
export interface MonitoringActivity {
  /** What is being monitored */
  parameter: string;

  /** Monitoring method */
  method: string;

  /** Frequency */
  frequency: string;

  ** Normal range */
  normal_range?: string;

  /** Current value */
  current_value?: string;

  ** Is value abnormal? */
  is_abnormal?: boolean;

  ** Trends observed */
  trends?: string;

  ** Actions taken */
  actions_taken?: string;

  ** Next monitoring time */
  next_monitoring?: string;
}

// ============================================================================
// RESPONSE TYPES - Patient Response, Side Effects, Complications
// ============================================================================

/**
 * Patient response to treatment
 */
export interface PatientResponse {
  ** Treatment/intervention */
  treatment: string;

  /** Response type */
  response_type: ResponseType;

  ** Response description */
  description: string;

  ** Onset of response */
  onset: string;

  ** Duration of response */
  duration?: string;

  ** Severity (if adverse) */
  severity?: SeverityLevel;

  ** Actions taken */
  actions_taken?: string;

  ** Is response expected? */
  is_expected: boolean;

  ** Requires intervention? */
  requires_intervention: boolean;

  /** Follow-up needed */
  follow_up_needed?: string;
}

/**
 * Response types
 */
export type ResponseType =
  | 'improvement'         // Perbaikan
  | 'stabilization'       // Stabilisasi
  | 'deterioration'       // Pemburukan
  | 'no_change'           // Tidak ada perubahan
  | 'adverse_effect'      // Efek samping
  | 'complication'        // Komplikasi
  | 'allergic_reaction';  // Reaksi alergi

/**
 * Side effect observed
 */
export interface SideEffect {
  ** Side effect name */
  name: string;

  ** Suspected cause (medication/treatment) */
  suspected_cause: string;

  ** Onset time */
  onset: string;

  ** Severity */
  severity: SeverityLevel;

  ** Description */
  description: string;

  ** Duration */
  duration?: string;

  ** Is expected? */
  is_expected: boolean;

  ** Actions taken */
  actions_taken: string;

  ** Outcome of actions */
  outcome?: string;

  ** Was medication/treatment changed? */
  treatment_changed: boolean;

  ** Change details */
  change_details?: string;

  ** Reported to prescriber? */
  reported_to_prescriber: boolean;
}

/**
 * Complication occurred
 */
export interface Complication {
  ** Complication name */
  name: string;

  ** Type */
  type: ComplicationType;

  ** Severity */
  severity: SeverityLevel;

  ** Onset time */
  onset: string;

  ** Description */
  description: string;

  ** Risk factors */
  risk_factors?: string[];

  ** Preventive measures in place */
  preventive_measures?: string[];

  ** Actions taken */
  actions_taken: string;

  ** Current status */
  status: ComplicationStatus;

  ** Resolved? */
  resolved: boolean;

  ** Resolution date */
  resolution_date?: string;

  ** Sequelae */
  sequelae?: string[];

  ** Family notified */
  family_notified: boolean;
}

/**
 * Complication types
 */
export type ComplicationType =
  | 'infection'           // Infeksi
  | 'bleeding'            // Perdarahan
  | 'thrombotic'          // Trombotik
  | 'pulmonary'           // Pulmoner
  | 'cardiac'             // Kardiovaskular
  | 'renal'               // Renal
  | 'neurologic'          // Neurologis
  | 'surgical'            // Bedah
  | 'medication'          // Obat
  | 'procedural'          // Prosedur
  | 'other';              // Lainnya

/**
 * Complication status
 */
export type ComplicationStatus =
  | 'active'              // Aktif
  | 'resolving'           // Membaik
  | 'resolved'            // Sembuh
  | 'chronic';            // Kronis

/**
 * Adverse event
 */
export interface AdverseEvent {
  ** Event description */
  event_description: string;

  ** Event type */
  event_type: AdverseEventType;

  ** Severity */
  severity: SeverityLevel;

  ** Date/time of event */
  event_datetime: string;

  ** Suspected cause */
  suspected_cause: string;

  ** Was this preventable? */
  preventable: boolean;

  ** Immediate actions taken */
  immediate_actions: string;

  ** Patient outcome */
  patient_outcome: AdverseEventOutcome;

  ** Reported to */
  reported_to: string[];

  ** Report date */
  report_date: string;

  ** Follow-up required */
  follow_up_required: boolean;

  ** Preventive measures implemented */
  preventive_measures?: string[];
}

/**
 * Adverse event types
 */
export type AdverseEventType =
  | 'fall'                // Jatuh
  | 'medication_error'    // Kesalahan obat
  | 'pressure_injury'     // Luka tekan
  | 'infection'           // Infeksi
  | 'allergic_reaction'   // Reaksi alergi
  | 'procedure_complication'  // Komplikasi prosedur
  | 'equipment_malfunction'   // Kerusakan alat
  | 'other';              // Lainnya

/**
 * Adverse event outcomes
 */
export type AdverseEventOutcome =
  | 'no_harm'             // Tidak ada cedera
  | 'mild_harm'           // Cedera ringan
  | 'moderate_harm'       // Cedera sedang
  | 'severe_harm'         // Cedera berat
  | 'death';              // Kematian

// ============================================================================
// FORM STATE TYPES - For Managing the Progress Notes Form
// ============================================================================

/**
 * Progress notes form state
 */
export interface ProgressNotesFormState {
  /** Current form step */
  current_step: ProgressNotesFormStep;

  ** Note type */
  note_type: ProgressNoteType;

  /** Patient information */
  patient_info: ProgressNotePatientInfo;

  ** SOAP note data */
  soap_note: SOAPNote;

  ** Vital signs summary */
  vital_signs_summary?: VitalSignsSummary;

  /** Interventions performed */
  interventions?: Intervention[];

  /** Patient responses */
  patient_responses?: PatientResponse[];

  /** Side effects */
  side_effects?: SideEffect[];

  ** Complications */
  complications?: Complication[];

  /** Form validation errors */
  validation_errors: ValidationError[];

  ** Is form dirty (has unsaved changes) */
  is_dirty: boolean;

  ** Is form valid */
  is_valid: boolean;

  ** Is submitting */
  is_submitting: boolean;

  ** Additional notes */
  additional_notes?: string;

  ** Form mode */
  mode: FormMode;

  ** Sign-off status */
  sign_off: SignOffStatus;
}

/**
 * Progress notes form steps
 */
export type ProgressNotesFormStep =
  | 'patient_info'        // Informasi pasien
  | 'subjective'          // Subjektif
  | 'objective'           // Objektif
  | 'assessment'          // Asesmen
  | 'plan'                // Rencana
  | 'interventions'       // Intervensi
  | 'response'            // Respon
  | 'review';             // Review

/**
 * Form modes
 */
export type FormMode =
  | 'create'              // Membuat catatan baru
  | 'edit'                // Mengedit catatan yang ada
  | 'view'                // Melihat catatan
  | 'template';           // Template

/**
 * Validation error
 */
export interface ValidationError {
  /** Field with error */
  field: string;

  /** Error message (Indonesian) */
  message: string;

  /** Error severity */
  severity: 'error' | 'warning';

  /** Step where error occurred */
  step: ProgressNotesFormStep;
}

/**
 * Sign-off status
 */
export interface SignOffStatus {
  ** Is signed off? */
  is_signed_off: boolean;

  ** Signed by */
  signed_by?: string;

  /** Signed at */
  signed_at?: string;

  ** Signature type */
  signature_type?: 'electronic' | 'digital' | 'image';

  ** Cosigner required? */
  cosigner_required: boolean;

  ** Cosigned by */
  cosigned_by?: string;

  ** Cosigned at */
  cosigned_at?: string;

  ** Verification status */
  verification_status: 'pending' | 'verified' | 'rejected';
}

/**
 * Form action types for state management
 */
export type ProgressNotesFormAction =
  | { type: 'SET_STEP'; payload: ProgressNotesFormStep }
  | { type: 'SET_NOTE_TYPE'; payload: ProgressNoteType }
  | { type: 'SET_PATIENT_INFO'; payload: ProgressNotePatientInfo }
  | { type: 'SET_SUBJECTIVE'; payload: Subjective }
  | { type: 'SET_OBJECTIVE'; payload: Objective }
  | { type: 'SET_ASSESSMENT'; payload: Assessment }
  | { type: 'SET_PLAN'; payload: Plan }
  | { type: 'SET_VITAL_SIGNS'; payload: VitalSignsSummary }
  | { type: 'ADD_INTERVENTION'; payload: Intervention }
  | { type: 'REMOVE_INTERVENTION'; payload: string }
  | { type: 'ADD_PATIENT_RESPONSE'; payload: PatientResponse }
  | { type: 'REMOVE_PATIENT_RESPONSE'; payload: string }
  | { type: 'ADD_SIDE_EFFECT'; payload: SideEffect }
  | { type: 'REMOVE_SIDE_EFFECT'; payload: string }
  | { type: 'ADD_COMPLICATION'; payload: Complication }
  | { type: 'REMOVE_COMPLICATION'; payload: string }
  | { type: 'SET_ADDITIONAL_NOTES'; payload: string }
  | { type: 'VALIDATE' }
  | { type: 'SUBMIT' }
  | { type: 'RESET' }
  | { type: 'SET_MODE'; payload: FormMode }
  | { type: 'SIGN_OFF'; payload: SignOffStatus };

// ============================================================================
// API REQUEST/RESPONSE TYPES - For Backend Integration
// ============================================================================

/**
 * Create progress note request
 */
export interface CreateProgressNoteRequest {
  /** Patient ID */
  patient_id: string;

  /** Visit/Encounter ID */
  visit_id: string;

  ** Note type */
  note_type: ProgressNoteType;

  ** Note category */
  category: ProgressNoteCategory;

  ** SOAP note data */
  soap_note: SOAPNote;

  ** Vital signs summary */
  vital_signs_summary?: VitalSignsSummary;

  /** Interventions */
  interventions?: Intervention[];

  /** Patient responses */
  patient_responses?: PatientResponse[];

  /** Side effects */
  side_effects?: SideEffect[];

  ** Complications */
  complications?: Complication[];

  /** Additional notes */
  additional_notes?: string;

  ** Priority */
  priority: NotePriority;

  ** Is this an addendum? */
  is_addendum?: boolean;

  ** Parent note ID (if addendum) */
  parent_note_id?: string;

  ** Tags/keywords */
  tags?: string[];
}

/**
 * Create progress note response
 */
export interface CreateProgressNoteResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Note ID */
    note_id: string;

    /** Created timestamp */
    created_at: string;

    /** Created by */
    created_by: string;

    /** Note summary */
    summary: ProgressNoteSummary;
  };

  /** Response message */
  message?: string;

  /** Error details */
  error?: ApiError;
}

/**
 * Progress note summary
 */
export interface ProgressNoteSummary {
  /** Note ID */
  id: string;

  /** Patient ID */
  patient_id: string;

  /** Patient name */
  patient_name: string;

  /** Note type */
  note_type: ProgressNoteType;

  /** Note date/time */
  note_datetime: string;

  ** Created by */
  created_by: string;

  /** Primary diagnosis/problem */
  primary_problem: string;

  ** Clinical status */
  clinical_status: ClinicalStatus;

  ** Brief summary */
  summary: string;

  ** Has interventions? */
  has_interventions: boolean;

  ** Has complications? */
  has_complications: boolean;
}

/**
 * Get progress notes request
 */
export interface GetProgressNotesRequest {
  /** Patient ID */
  patient_id: string;

  /** Visit ID (optional) */
  visit_id?: string;

  ** Note type filter */
  note_type?: ProgressNoteType;

  ** Date range start */
  date_from?: string;

  /** Date range end */
  date_to?: string;

  ** Maximum records to return */
  limit?: number;

  ** Offset for pagination */
  offset?: number;

  ** Sort order */
  sort_order?: 'asc' | 'desc';

  ** Include addendums? */
  include_addendums?: boolean;
}

/**
 * Get progress notes response
 */
export interface GetProgressNotesResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Progress notes */
    notes: ProgressNoteRecord[];

    /** Total count */
    total_count: number;

    /** Has more records */
    has_more: boolean;
  };

  /** Response message */
  message?: string;

  /** Error details */
  error?: ApiError;
}

/**
 * Complete progress note record
 */
export interface ProgressNoteRecord {
  /** Note ID */
  id: string;

  /** Patient ID */
  patient_id: string;

  /** Visit ID */
  visit_id: string;

  /** Note type */
  note_type: ProgressNoteType;

  /** Category */
  category: ProgressNoteCategory;

  /** Priority */
  priority: NotePriority;

  /** SOAP note */
  soap_note: SOAPNote;

  /** Vital signs summary */
  vital_signs_summary?: VitalSignsSummary;

  /** Interventions */
  interventions?: Intervention[];

  /** Patient responses */
  patient_responses?: PatientResponse[];

  /** Side effects */
  side_effects?: SideEffect[];

  /** Complications */
  complications?: Complication[];

  /** Additional notes */
  additional_notes?: string;

  /** Created at */
  created_at: string;

  /** Created by */
  created_by: string;

  /** Updated at */
  updated_at?: string;

  /** Updated by */
  updated_by?: string;

  /** Sign-off status */
  sign_off: SignOffStatus;

  /** Is addendum */
  is_addendum: boolean;

  /** Parent note ID (if addendum) */
  parent_note_id?: string;

  /** Tags */
  tags?: string[];

  /** Attachment IDs */
  attachment_ids?: string[];
}

/**
 * Update progress note request
 */
export interface UpdateProgressNoteRequest {
  /** Note ID */
  note_id: string;

  ** SOAP note data to update */
  soap_note?: Partial<SOAPNote>;

  /** Vital signs summary to update */
  vital_signs_summary?: VitalSignsSummary;

  /** Interventions to add/update */
  interventions?: Intervention[];

  /** Patient responses to add/update */
  patient_responses?: PatientResponse[];

  /** Side effects to add/update */
  side_effects?: SideEffect[];

  /** Complications to add/update */
  complications?: Complication[];

  /** Additional notes to update */
  additional_notes?: string;

  /** Reason for update */
  update_reason: string;

  ** Tags to update */
  tags?: string[];
}

/**
 * Update progress note response
 */
export interface UpdateProgressNoteResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Updated note ID */
    note_id: string;

    /** Updated timestamp */
    updated_at: string;

    /** Updated by */
    updated_by: string;
  };

  /** Response message */
  message?: string;

  /** Error details */
  error?: ApiError;
}

/**
 * Delete progress note request
 */
export interface DeleteProgressNoteRequest {
  /** Note ID */
  note_id: string;

  /** Reason for deletion */
  deletion_reason: string;
}

/**
 * Delete progress note response
 */
export interface DeleteProgressNoteResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Deleted note ID */
    note_id: string;

    /** Deleted timestamp */
    deleted_at: string;

    /** Deleted by */
    deleted_by: string;
  };

  /** Response message */
  message?: string;

  /** Error details */
  error?: ApiError;
}

/**
 * Sign off progress note request
 */
export interface SignOffProgressNoteRequest {
  /** Note ID */
  note_id: string;

  /** Password or PIN for verification */
  credential: string;

  /** Signature type */
  signature_type: 'electronic' | 'digital' | 'image';

  /** Requires cosigner */
  requires_cosigner?: boolean;

  /** Cosigner ID */
  cosigner_id?: string;
}

/**
 * Sign off progress note response
 */
export interface SignOffProgressNoteResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Note ID */
    note_id: string;

    /** Sign-off timestamp */
    signed_at: string;

    /** Signed by */
    signed_by: string;

    /** Verification status */
    verification_status: 'pending' | 'verified' | 'rejected';
  };

  /** Response message */
  message?: string;

  /** Error details */
  error?: ApiError;
}

/**
 * Get progress note templates request
 */
export interface GetProgressNoteTemplatesRequest {
  /** Note type filter */
  note_type?: ProgressNoteType;

  /** Specialty filter */
  specialty?: string;

  /** Department filter */
  department?: string;
}

/**
 * Progress note template
 */
export interface ProgressNoteTemplate {
  /** Template ID */
  id: string;

  /** Template name */
  name: string;

  /** Note type */
  note_type: ProgressNoteType;

  /** Specialty */
  specialty?: string;

  /** Department */
  department?: string;

  /** Description */
  description?: string;

  /** Default SOAP structure */
  default_soap: Partial<SOAPNote>;

  ** Common phrases/templates */
  common_phrases?: {
    subjective?: string[];
    objective?: string[];
    assessment?: string[];
    plan?: string[];
  };

  ** Is this a system template? */
  is_system: boolean;

  ** Created by */
  created_by: string;

  ** Created at */
  created_at: string;

  ** Usage count */
  usage_count: number;
}

/**
 * Get progress note templates response
 */
export interface GetProgressNoteTemplatesResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Templates */
    templates: ProgressNoteTemplate[];

    /** Total count */
    total_count: number;
  };

  /** Response message */
  message?: string;

  /** Error details */
  error?: ApiError;
}

/**
 * API error structure
 */
export interface ApiError {
  /** Error code */
  code: string;

  /** Error message (Indonesian) */
  message: string;

  /** Additional error details */
  details?: Record<string, unknown>;

  /** Error timestamp */
  timestamp?: string;
}

/**
 * Validate progress note request
 */
export interface ValidateProgressNoteRequest {
  /** Note type */
  note_type: ProgressNoteType;

  /** SOAP note data */
  soap_note: Partial<SOAPNote>;

  ** Skip optional fields validation */
  skip_optional_validation?: boolean;
}

/**
 * Validate progress note response
 */
export interface ValidateProgressNoteResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Is valid */
    is_valid: boolean;

    /** Validation errors */
    errors: ValidationError[];

    /** Warnings */
    warnings: ValidationError[];
  };

  /** Response message */
  message?: string;

  /** Error details */
  error?: ApiError;
}

/**
 * Get progress notes statistics request
 */
export interface GetProgressNotesStatsRequest {
  /** Patient ID */
  patient_id: string;

  /** Visit ID (optional) */
  visit_id?: string;

  /** Date range start */
  date_from?: string;

  /** Date range end */
  date_to?: string;
}

/**
 * Progress notes statistics
 */
export interface ProgressNotesStats {
  /** Total notes */
  total_notes: number;

  ** Notes by type */
  notes_by_type: Record<ProgressNoteType, number>;

  ** Notes by category */
  notes_by_category: Record<ProgressNoteCategory, number>;

  ** Notes with complications */
  notes_with_complications: number;

  ** Notes with interventions */
  notes_with_interventions: number;

  ** Most common problems */
  common_problems: Array<{
    problem: string;
    count: number;
  }>;

  ** Clinical status distribution */
  clinical_status_distribution: Record<ClinicalStatus, number>;

  ** Notes per day */
  notes_per_day: Array<{
    date: string;
    count: number;
  }>;
}

/**
 * Get progress notes statistics response
 */
export interface GetProgressNotesStatsResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: ProgressNotesStats;

  /** Response message */
  message?: string;

  /** Error details */
  error?: ApiError;
}

// ============================================================================
// VALIDATION CONSTRAINTS - Field Validation Rules
// ============================================================================

/**
 * Progress notes validation constraints
 */
export interface ProgressNotesValidationConstraints {
  /** Note type constraints */
  note_type: {
    /** Required note types */
    required_fields: Record<ProgressNoteType, string[]>;

    /** Optional note types */
    optional_fields: Record<ProgressNoteType, string[]>;
  };

  ** SOAP constraints */
  soap: {
    /** Subjective max length */
    subjective_max_length: number;

    /** Objective max length */
    objective_max_length: number;

    /** Assessment max length */
    assessment_max_length: number;

    /** Plan max length */
    plan_max_length: number;

    /** Required fields */
    required_fields: string[];
  };

  ** Intervention constraints */
  intervention: {
    /** Max interventions per note */
    max_interventions: number;

    /** Required fields */
    required_fields: string[];
  };

  ** Medication constraints */
  medication: {
    /** Max medications per note */
    max_medications: number;

    /** Required fields */
    required_fields: string[];
  };

  ** Timing constraints */
  timing: {
    /** Max time between note creation and sign-off (hours) */
    max_signoff_delay_hours: number;

    /** Max time for edit after sign-off (hours) */
    max_edit_after_signoff_hours: number;
  };
}

/**
 * Get validation constraints response
 */
export interface GetValidationConstraintsResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Validation constraints */
    constraints: ProgressNotesValidationConstraints;

    /** Last updated */
    last_updated: string;
  };

  /** Response message */
  message?: string;

  /** Error details */
  error?: ApiError;
}

// ============================================================================
// HELPER TYPES - Utility Types for Progress Notes
// ============================================================================

/**
 * Progress note filter options
 */
export interface ProgressNoteFilter {
  ** Note type filter */
  note_type?: ProgressNoteType;

  ** Category filter */
  category?: ProgressNoteCategory;

  ** Priority filter */
  priority?: NotePriority;

  ** Date range filter */
  date_range?: {
    from: string;
    to: string;
  };

  ** Created by filter */
  created_by?: string;

  ** Clinical status filter */
  clinical_status?: ClinicalStatus;

  ** Has complications filter */
  has_complications?: boolean;

  ** Has interventions filter */
  has_interventions?: boolean;

  ** Tags filter */
  tags?: string[];

  ** Search query */
  search_query?: string;
}

/**
 * Progress note sort options
 */
export interface ProgressNoteSort {
  /** Sort field */
  field: ProgressNoteSortField;

  /** Sort order */
  order: 'asc' | 'desc';
}

/**
 * Progress note sort fields
 */
export type ProgressNoteSortField =
  | 'created_at'
  | 'updated_at'
  | 'note_type'
  | 'category'
  | 'priority'
  | 'clinical_status';

/**
 * Progress note export options
 */
export interface ProgressNoteExportOptions {
  /** Export format */
  format: 'pdf' | 'doc' | 'html' | 'json';

  ** Include sections */
  include_sections: {
    patient_info: boolean;
    subjective: boolean;
    objective: boolean;
    assessment: boolean;
    plan: boolean;
    interventions: boolean;
    responses: boolean;
    complications: boolean;
  };

  ** Include signatures */
  include_signatures: boolean;

  ** Include timestamps */
  include_timestamps: boolean;

  ** Language */
  language: 'id' | 'en';

  ** Template ID (if applicable) */
  template_id?: string;
}

/**
 * Progress note export response
 */
export interface ProgressNoteExportResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Export ID */
    export_id: string;

    /** Download URL */
    download_url: string;

    /** Expires at */
    expires_at: string;

    /** File size (bytes) */
    file_size: number;
  };

  /** Response message */
  message?: string;

  /** Error details */
  error?: ApiError;
}

/**
 * Progress note audit log entry
 */
export interface ProgressNoteAuditLog {
  /** Log ID */
  id: string;

  /** Note ID */
  note_id: string;

  /** Action performed */
  action: 'created' | 'updated' | 'deleted' | 'viewed' | 'signed_off' | 'cosigned';

  /** Performed by */
  performed_by: string;

  /** Action timestamp */
  timestamp: string;

  ** Changes made (for updates) */
  changes?: {
    field: string;
    old_value: string;
    new_value: string;
  }[];

  ** IP address */
  ip_address?: string;

  ** User agent */
  user_agent?: string;

  ** Reason (for deletions/updates) */
  reason?: string;
}

/**
 * Progress note collaboration info
 */
export interface ProgressNoteCollaboration {
  ** Can edit */
  can_edit: boolean;

  ** Can delete */
  can_delete: boolean;

  ** Can sign off */
  can_sign_off: boolean;

  ** Can cosign */
  can_cosign: boolean;

  ** Required cosigners */
  required_cosigners?: string[];

  ** Currently locked by */
  locked_by?: string;

  ** Lock expiry */
  lock_expiry?: string;
}
