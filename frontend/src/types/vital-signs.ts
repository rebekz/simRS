/**
 * Vital Signs Types for SIMRS
 * Comprehensive type definitions for vital signs monitoring and documentation
 * Compatible with Indonesian healthcare requirements and standards
 */

// ============================================================================
// VITAL SIGNS MEASUREMENT TYPES - Core Vital Signs Data
// ============================================================================

/**
 * Blood pressure measurement
 */
export interface BloodPressure {
  /** Systolic pressure (mmHg) - Normal: 90-120 */
  systolic: number;

  /** Diastolic pressure (mmHg) - Normal: 60-80 */
  diastolic: number;

  /** Mean arterial pressure (calculated) */
  mean_arterial_pressure?: number;

  /** Measurement position */
  position: BloodPressurePosition;

  /** Measurement site */
  site: BloodPressureSite;

  /** Cuff size used */
  cuff_size: CuffSize;

  /** Is this an automated measurement? */
  is_automated: boolean;
}

/**
 * Blood pressure measurement position
 */
export type BloodPressurePosition =
  | 'supine'          // Berbaring
  | 'sitting'         // Duduk
  | 'standing'        // Berdiri
  | 'left_lateral';   // Miring kiri (for pregnant patients)

/**
 * Blood pressure measurement site
 */
export type BloodPressureSite =
  | 'right_arm'       // Lengan kanan
  | 'left_arm'        // Lengan kiri
  | 'right_thigh'     // Paha kanan
  | 'left_thigh'      // Paha kiri
  | 'right_leg'       // Kaki kanan
  | 'left_leg';       // Kaki kiri

/**
 * Blood pressure cuff size
 */
export type CuffSize =
  | 'pediatric'       // Anak-anak
  | 'small'           // Kecil
  | 'regular'         // Reguler
  | 'large'           // Besar
  | 'extra_large';    // Extra besar

/**
 * Heart rate measurement
 */
export interface HeartRate {
  /** Heart rate (bpm) - Normal: 60-100 */
  rate: number;

  /** Heart rhythm */
  rhythm: HeartRhythm;

  /** Pulse quality */
  pulse_quality: PulseQuality;

  /** Pulse sites checked */
  pulse_sites: PulseSite[];

  /** Is pulse regular? */
  is_regular: boolean;

  /** Any irregularities noted */
  irregularities?: string[];
}

/**
 * Heart rhythm types
 */
export type HeartRhythm =
  | 'regular_sinus'   // Sinus reguler
  | 'irregular'       // Tidak reguler
  | 'atrial_fibrillation'  // Fibrilasi atrium
  | 'tachycardia'     // Takikardia
  | 'bradycardia';    // Bradikardia

/**
 * Pulse quality
 */
export type PulseQuality =
  | 'strong'          // Kuat
  | 'normal'          // Normal
  | 'weak'            // Lemah
  | 'thready';        // Lemah sekali

/**
 * Pulse measurement sites
 */
export type PulseSite =
  | 'radial'          // Arteri radialis
  | 'carotid'         // Arteri karotis
  | 'brachial'        // Arteri brakialis
  | 'femoral'         // Arteri femoralis
  | 'popliteal'       // Arteri poplitea
  | 'dorsalis_pedis'  // Arteri dorsalis pedis
  | 'temporal';       // Arteri temporalis

/**
 * Respiratory rate measurement
 */
export interface RespiratoryRate {
  /** Respiratory rate (breaths/min) - Normal: 12-20 */
  rate: number;

  /** Breathing pattern */
  pattern: BreathingPattern;

  /** Breathing effort */
  effort: BreathingEffort;

  /** Breath sounds */
  breath_sounds: BreathSound;

  /** Oxygen delivery method (if applicable) */
  oxygen_delivery?: OxygenDelivery;

  /** Oxygen flow rate (L/min) */
  oxygen_flow_rate?: number;

  /** Is there respiratory distress? */
  is_in_distress: boolean;

  /** Additional notes */
  notes?: string;
}

/**
 * Breathing pattern
 */
export type BreathingPattern =
  | 'regular'         // Reguler
  | 'irregular'       // Tidak reguler
  | 'cheyne_stokes'   // Cheyne-Stokes
  | 'kussmaul'        // Kussmaul
  | 'biot'            // Biot
  | 'apneustic';      // Apneustik

/**
 * Breathing effort
 */
export type BreathingEffort =
  | 'normal'          // Normal
  | 'increased'       // Meningkat
  | 'decreased'       // Menurun
  | 'absent';         // Tidak ada

/**
 * Breath sounds
 */
export type BreathSound =
  | 'clear'           // Jernih
  | 'diminished'      // Berkurang
  | 'wheeze'          // Mengi
  | 'crackles'        // Ronkhi
  | 'rhonchi'         // Ronki
  | 'stridor'         // Stridor
  | 'absent';         // Tidak ada

/**
 * Oxygen delivery methods
 */
export type OxygenDelivery =
  | 'none'            // Tidak ada
  | 'nasal_cannula'   // Selang nasal
  | 'face_mask'       // Masker wajah
  | 'venturi_mask'    // Masker venturi
  | 'non_rebreather'  // Masker non-rebreather
  | 'tracheostomy'    // Trakeostomi
  | 'mechanical_ventilator';  // Ventilator mekanis

/**
 * Body temperature measurement
 */
export interface Temperature {
  /** Temperature value */
  value: number;

  /** Unit of measurement */
  unit: TemperatureUnit;

  /** Measurement site */
  site: TemperatureSite;

  /** Temperature category */
  category: TemperatureCategory;

  /** Is this an automated measurement? */
  is_automated: boolean;
}

/**
 * Temperature units
 */
export type TemperatureUnit = 'celsius' | 'fahrenheit';

/**
 * Temperature measurement sites
 */
export type TemperatureSite =
  | 'oral'            // Oral
  | 'axillary'        // Aksila
  | 'rectal'          // Rektal
  | 'tympanic'        // Timpapan
  | 'temporal'        // Dahi (arteri temporalis)
  | 'esophageal';     // Esofagus

/**
 * Temperature categories
 */
export type TemperatureCategory =
  | 'hypothermia'     // Hipotermia (< 35°C)
  | 'below_normal'    // Di bawah normal (35-36°C)
  | 'normal'          // Normal (36.5-37.5°C)
  | 'above_normal'    // Di atas normal (37.5-38°C)
  | 'fever'           // Demam (> 38°C)
  | 'hyperpyrexia';   // Hiperpireksia (> 40°C)

/**
 * Oxygen saturation measurement
 */
export interface SpO2 {
  /** Oxygen saturation percentage (%) - Normal: 95-100 */
  saturation: number;

  /** Is patient on oxygen supplementation? */
  on_oxygen: boolean;

  /** Oxygen delivery method (if applicable) */
  oxygen_delivery?: OxygenDelivery;

  /** Oxygen flow rate (L/min) */
  oxygen_flow_rate?: number;

  /** SpO2 category */
  category: SpO2Category;

  /** Is waveform pleth present? */
  has_pleth: boolean;
}

/**
 * SpO2 categories
 */
export type SpO2Category =
  | 'normal'          // Normal (95-100%)
  | 'mild_hypoxia'    // Hipoxia ringan (91-94%)
  | 'moderate_hypoxia'  // Hipoxia sedang (85-90%)
  | 'severe_hypoxia'  // Hipoxia berat (< 85%)
  | 'critical';       // Kritis (< 70%)

/**
 * Weight measurement
 */
export interface Weight {
  /** Weight value */
  value: number;

  /** Unit of measurement */
  unit: WeightUnit;

  /** Measurement type */
  type: WeightType;

  /** Is patient able to stand? */
  is_able_to_stand: boolean;

  /** Was actual weight measured or estimated? */
  is_estimated: boolean;

  /** Weight-for-age percentile (for pediatrics) */
  weight_for_age_percentile?: number;

  /** Weight-for-height percentile (for pediatrics) */
  weight_for_height_percentile?: number;
}

/**
 * Weight units
 */
export type WeightUnit = 'kg' | 'grams' | 'pounds';

/**
 * Weight measurement types
 */
export type WeightType =
  | 'actual'          // Aktual
  | 'estimated'       // Perkiraan
  | 'dry'             // Berat badan kering
  | 'ideal';          // Berat badan ideal

/**
 * Height measurement
 */
export interface Height {
  /** Height value */
  value: number;

  /** Unit of measurement */
  unit: HeightUnit;

  /** Measurement type */
  type: HeightType;

  /** Is patient able to stand? */
  is_able_to_stand: boolean;

  /** Was actual height measured or estimated? */
  is_estimated: boolean;

  /** Height-for-age percentile (for pediatrics) */
  height_for_age_percentile?: number;
}

/**
 * Height units
 */
export type HeightUnit = 'cm' | 'm' | 'inches';

/**
 * Height measurement types
 */
export type HeightType =
  | 'standing'        // Berdiri
  | 'recumbent'       // Berbaring
  | 'estimated'       // Perkiraan
  | 'arm_span';       // Panjang lengan (for non-ambulatory)

/**
 * Body Mass Index (BMI) measurement
 */
export interface BMI {
  /** BMI value */
  value: number;

  /** BMI category */
  category: BMICategory;

  /** Is BMI calculated from actual measurements? */
  is_calculated: boolean;
}

/**
 * BMI categories (according to WHO Asia-Pacific criteria for Indonesians)
 */
export type BMICategory =
  | 'underweight_severe'    // Kurus berat (< 16.0)
  | 'underweight_moderate'  // Kurus sedang (16.0 - 16.9)
  | 'underweight_mild'      // Kurus ringan (17.0 - 18.4)
  | 'normal'                // Normal (18.5 - 22.9 for Asians)
  | 'overweight'            // Gemuk (23.0 - 24.9 for Asians)
  | 'obese_I'               // Obesitas I (25.0 - 29.9 for Asians)
  | 'obese_II';             // Obesitas II (≥ 30.0 for Asians)

/**
 * Pain score assessment
 */
export interface PainScore {
  /** Pain score (0-10) */
  score: number;

  /** Pain scale used */
  scale: PainScale;

  /** Pain location */
  location: string;

  /** Pain quality/description */
  quality: PainQuality[];

  /** Pain duration */
  duration: string;

  /** Pain onset */
  onset: PainOnset;

  /** What aggravates the pain */
  aggravating_factors?: string[];

  /** What relieves the pain */
  relieving_factors?: string[];

  /** Associated symptoms */
  associated_symptoms?: string[];
}

/**
 * Pain assessment scales
 */
export type PainScale =
  | 'numeric_0_10'    // Skala numerik 0-10
  | 'faces'           // Skala wajah (FLACC/FACES)
  | 'visual_analog'   // Skala analog visual
  | 'flacc'           // FLACC scale (for non-verbal)
  | 'cpp';            // Comfort, Pain, Pediatric Scale (for infants)

/**
 * Pain quality descriptions
 */
export type PainQuality =
  | 'sharp'           // Tajam
  | 'dull'            // Tumpul
  | 'throbbing'       // Berdebar
  | 'burning'         // Terbakar
  | 'cramping'        // Kram
  | 'aching'          // Nyeri
  | 'stabbing'        // Tusukan
  | 'pressing'        // Tekan
  | 'radiating'       // Menjalar
  | 'colicky';        // Kolik

/**
 * Pain onset patterns
 */
export type PainOnset =
  | 'acute'           // Akut
  | 'gradual'         // Bertahap
  | 'sudden'          // Tiba-tiba
  | 'intermittent'    // Intermiten
  | 'constant';       // Konstan

/**
 * Glasgow Coma Scale (GCS) assessment
 */
export interface GCS {
  /** Eye opening response */
  eye_opening: GCSEyeOpening;

  /** Verbal response */
  verbal: GCSVerbal;

  /** Motor response */
  motor: GCSMotor;

  /** Total GCS score (3-15) */
  total_score: number;

  /** GCS category */
  category: GCSCategory;
}

/**
 * GCS Eye opening response
 */
export type GCSEyeOpening =
  | 'spontaneous'     // Spontan (4)
  | 'to_sound'        // Terhadap suara (3)
  | 'to_pressure'     // Terhadap tekanan (2)
  | 'none';           // Tidak ada (1)

/**
 * GCS Verbal response
 */
export type GCSVerbal =
  | 'oriented'        // Terorientasi (5)
  | 'confused'        // Bingung (4)
  | 'inappropriate'   // Tidak tepat (3)
  | 'incomprehensible'  // Tidak dapat dimengerti (2)
  | 'none';           // Tidak ada (1)

/**
 * GCS Motor response
 */
export type GCSMotor =
  | 'obeys'           // Mengikuti perintah (6)
  | 'localizes'       // Melokalisasi (5)
  | 'withdraws'       // Menarik (4)
  | 'abnormal_flexion'  // Fleksi abnormal (3)
  | 'extension'       // Ekstensi (2)
  | 'none';           // Tidak ada (1)

/**
 * GCS categories
 */
export type GCSCategory =
  | 'severe_injury'   // Cedera berat (3-8)
  | 'moderate_injury' // Cedera sedang (9-12)
  | 'mild_injury';    // Cedera ringan (13-15)

/**
 * Blood glucose measurement
 */
export interface BloodGlucose {
  /** Glucose value (mg/dL) */
  value: number;

  /** Measurement type */
  type: GlucoseMeasurementType;

  /** Timing relative to meal */
  timing: GlucoseTiming;

  /** Glucose category */
  category: GlucoseCategory;

  /** Sample type */
  sample_type: GlucoseSampleType;
}

/**
 * Glucose measurement types
 */
export type GlucoseMeasurementType =
  | 'random'          // Acak
  | 'fasting'         // Puasa
  | 'postprandial'    // Postprandial (2 jam setelah makan)
  | 'bedtime';        // Sebelum tidur

/**
 * Glucose timing relative to meals
 */
export type GlucoseTiming =
  | 'fasting'         // Puasa (8+ jam)
  | 'pre_meal'        // Sebelum makan
  | 'post_meal'       // Setelah makan
  | 'bedtime';        // Sebelum tidur

/**
 * Glucose categories
 */
export type GlucoseCategory =
  | 'hypoglycemia_severe'   // Hipoglikemia berat (< 40)
  | 'hypoglycemia_moderate' // Hipoglikemia sedang (40-69)
  | 'normal'                // Normal (70-99 fasting, < 140 random)
  | 'impaired'              // Impaired (100-125 fasting, 140-199 random)
  | 'hyperglycemia';        // Hiperglikemia (≥ 126 fasting, ≥ 200 random)

/**
 * Glucose sample types
 */
export type GlucoseSampleType =
  | 'capillary'       // Kapiler (fingerstick)
  | 'venous'          // Vena
  | 'arterial';       // Arteri

// ============================================================================
// PATIENT INFORMATION TYPES - Patient Data for Vital Signs
// ============================================================================

/**
 * Patient information for vital signs monitoring
 */
export interface VitalSignsPatientInfo {
  /** Patient ID */
  patient_id: string;

  /** Medical record number */
  rm_number: string;

  /** Patient name */
  name: string;

  /** Date of birth */
  date_of_birth: string;

  /** Age in years */
  age_years?: number;

  /** Age in months (for pediatrics) */
  age_months?: number;

  /** Gender */
  gender: 'male' | 'female';

  /** Weight (for reference) */
  weight?: number;

  /** Height (for reference) */
  height?: number;

  /** Known allergies */
  allergies?: string[];

  /** Active comorbidities affecting vital signs */
  comorbidities?: string[];

  /** Baseline vital signs (if known) */
  baseline_vitals?: BaselineVitals;
}

/**
 * Baseline vital signs for comparison
 */
export interface BaselineVitals {
  /** Baseline blood pressure */
  baseline_bp?: {
    systolic: number;
    diastolic: number;
    date: string;
  };

  /** Baseline heart rate */
  baseline_hr?: {
    rate: number;
    date: string;
  };

  /** Baseline respiratory rate */
  baseline_rr?: {
    rate: number;
    date: string;
  };

  /** Baseline SpO2 */
  baseline_spo2?: {
    saturation: number;
    on_oxygen: boolean;
    date: string;
  };

  /** Notes about baseline */
  notes?: string;
}

// ============================================================================
// MEASUREMENT CONTEXT TYPES - Location, Device, Performer
// ============================================================================

/**
 * Measurement context information
 */
export interface MeasurementContext {
  /** Where was the measurement taken? */
  location: MeasurementLocation;

  /** Device/instrument used */
  device?: MeasurementDevice;

  /** Who performed the measurement */
  performer: MeasurementPerformer;

  /** Date and time of measurement */
  timestamp: string;

  /** Measurement circumstance */
  circumstance?: MeasurementCircumstance;
}

/**
 * Measurement location
 */
export type MeasurementLocation =
  | 'emergency'       // IGD
  | 'inpatient'       // Rawat inap
  | 'outpatient'      // Rawat jalan
  | 'icu'             // ICU
  | 'picu'            // PICU
  | 'nicu'            // NICU
  | 'ward'            // Ward
  | 'operating_room'  // Ruang operasi
  | 'recovery_room'   // Ruang pemulihan
  | 'home'            // Rumah
  | 'clinic';         // Klinik

/**
 * Measurement device information
 */
export interface MeasurementDevice {
  /** Device type */
  device_type: string;

  /** Device brand/model */
  device_brand?: string;

  /** Device serial number */
  device_serial?: string;

  /** Last calibration date */
  last_calibration?: string;

  /** Is device working properly? */
  is_functional: boolean;
}

/**
 * Person who performed the measurement
 */
export interface MeasurementPerformer {
  /** Performer ID */
  id: string;

  /** Performer name */
  name: string;

  /** Performer role */
  role: VitalSignsPerformerRole;

  /** Department */
  department?: string;
}

/**
 * Performer roles for vital signs measurement
 */
export type VitalSignsPerformerRole =
  | 'doctor'          // Dokter
  | 'nurse'           // Perawat
  | 'midwife'         // Bidan
  | 'paramedic'       // Paramedis
  | 'student'         // Siswa/mahasiswa
  | 'patient';        // Pasien (self-measurement)

/**
 * Measurement circumstances
 */
export type MeasurementCircumstance =
  | 'rest'            // Istirahat
  | 'post_exercise'   // Setelah aktivitas
  | 'post_medication' // Setelah obat
  | 'post_procedure'  // Setelah tindakan
  | 'pain'            // Saat nyeri
  | 'stress'          // Stres
  | 'sleep';          // Tidur

// ============================================================================
// ALERT/WARNING TYPES - Abnormal Value Detection, Critical Alerts
// ============================================================================

/**
 * Vital signs alert configuration
 */
export interface VitalSignsAlert {
  /** Vital sign type with alert */
  vital_sign_type: VitalSignType;

  /** Alert severity */
  severity: AlertSeverity;

  /** Alert category */
  category: AlertCategory;

  /** Actual value measured */
  actual_value: number;

  /** Expected normal range */
  normal_range: NormalRange;

  /** Critical thresholds */
  critical_thresholds: CriticalThresholds;

  /** Alert message (Indonesian) */
  message_id: string;

  /** Alert message in Indonesian */
  message: string;

  /** Suggested actions */
  suggested_actions?: string[];

  /** Requires immediate notification? */
  requires_immediate_notification: boolean;

  /** Who should be notified */
  notify_roles?: VitalSignsPerformerRole[];
}

/**
 * Vital sign types
 */
export type VitalSignType =
  | 'blood_pressure'
  | 'heart_rate'
  | 'respiratory_rate'
  | 'temperature'
  | 'spo2'
  | 'weight'
  | 'height'
  | 'bmi'
  | 'pain_score'
  | 'gcs'
  | 'blood_glucose';

/**
 * Alert severity levels
 */
export type AlertSeverity =
  | 'critical'        // Kritis - memerlukan tindakan segera
  | 'high'            // Tinggi - memerlukan perhatian segera
  | 'moderate'        // Sedang - memerlukan monitoring
  | 'low'             // Rendah - catatan saja
  | 'info';           // Informasi

/**
 * Alert categories
 */
export type AlertCategory =
  | 'too_high'        // Terlalu tinggi
  | 'too_low'         // Terlalu rendah
  | 'abnormal'        // Abnormal
  | 'critical_high'   // Kritis tinggi
  | 'critical_low'    // Kritis rendah
  | 'missing'         // Data tidak ada
  | 'inconsistent';   // Tidak konsisten

/**
 * Normal range for a vital sign
 */
export interface NormalRange {
  /** Minimum normal value */
  min: number;

  /** Maximum normal value */
  max: number;

  /** Is this age-adjusted? */
  age_adjusted: boolean;

  /** Age group if adjusted */
  age_group?: AgeGroup;

  /** Notes about the range */
  notes?: string;
}

/**
 * Critical thresholds for vital signs
 */
export interface CriticalThresholds {
  /** Critical high threshold */
  critical_high?: number;

  /** Critical low threshold */
  critical_low?: number;

  /** Warning high threshold */
  warning_high?: number;

  /** Warning low threshold */
  warning_low?: number;
}

/**
 * Age groups for vital signs ranges
 */
export type AgeGroup =
  | 'neonate'         // Neonatus (0-28 hari)
  | 'infant'          // Bayi (1-12 bulan)
  | 'toddler'         // Balita (1-3 tahun)
  | 'preschool'       // Pra-sekolah (3-6 tahun)
  | 'school_age'      // Usia sekolah (6-12 tahun)
  | 'adolescent'      // Remaja (12-18 tahun)
  | 'adult'           // Dewasa (18-60 tahun)
  | 'elderly';        // Lansia (> 60 tahun)

/**
 * Collection of alerts for a vital signs assessment
 */
export interface VitalSignsAlerts {
  /** All alerts generated */
  alerts: VitalSignsAlert[];

  /** Critical alerts count */
  critical_count: number;

  /** High priority alerts count */
  high_count: number;

  /** Moderate alerts count */
  moderate_count: number;

  /** Overall alert status */
  overall_status: AlertOverallStatus;
}

/**
 * Overall alert status
 */
export type AlertOverallStatus =
  | 'critical'        // Ada alert kritis
  | 'warning'         // Ada alert peringatan
  | 'caution'         // Ada alert hati-hati
  | 'normal';         // Semua normal

// ============================================================================
// TREND TYPES - Trend Indicators, Historical Data
// ============================================================================

/**
 * Vital sign trend information
 */
export interface VitalSignTrend {
  /** Vital sign type */
  vital_sign_type: VitalSignType;

  /** Current value */
  current_value: number;

  /** Previous value */
  previous_value?: number;

  /** Trend direction */
  trend: TrendDirection;

  /** Percentage change */
  percent_change?: number;

  /** Absolute change */
  absolute_change?: number;

  /** Is this a significant change? */
  is_significant: boolean;

  /** Significance threshold */
  significance_threshold: number;

  /** Historical data points */
  history: VitalSignHistoryPoint[];

  /** Trend interpretation */
  interpretation?: string;
}

/**
 * Trend directions
 */
export type TrendDirection =
  | 'improving'       // Membaik
  | 'stable'          // Stabil
  | 'worsening'       // Memburuk
  | 'fluctuating'     // Fluktuatif
  | 'unknown';        // Tidak diketahui (insufficient data)

/**
 * Historical vital sign data point
 */
export interface VitalSignHistoryPoint {
  /** Measurement timestamp */
  timestamp: string;

  /** Value */
  value: number;

  /** Was this an abnormal value? */
  is_abnormal: boolean;

  /** Notes */
  notes?: string;
}

/**
 * Collection of trends for all vital signs
 */
export interface VitalSignsTrends {
  /** Blood pressure trends */
  blood_pressure_systolic?: VitalSignTrend;
  blood_pressure_diastolic?: VitalSignTrend;

  /** Heart rate trend */
  heart_rate?: VitalSignTrend;

  /** Respiratory rate trend */
  respiratory_rate?: VitalSignTrend;

  /** Temperature trend */
  temperature?: VitalSignTrend;

  /** SpO2 trend */
  spo2?: VitalSignTrend;

  /** Blood glucose trend */
  blood_glucose?: VitalSignTrend;

  /** Overall trend status */
  overall_status: TrendDirection;
}

// ============================================================================
// EARLY WARNING SCORE TYPES - MEWS/EWS Calculations
// ============================================================================

/**
 * Modified Early Warning Score (MEWS) calculation
 */
export interface MEWS {
  /** Total MEWS score (0-15+) */
  total_score: number;

  /** MEWS category */
  category: MEWSCategory;

  /** Individual component scores */
  components: MEWSComponents;

  /** Calculated timestamp */
  calculated_at: string;

  /** Recommended action based on score */
  recommended_action: MEWSAction;

  /** Requires rapid response team? */
  requires_rrt: boolean;

  /** Requires ICU admission? */
  requires_icu: boolean;
}

/**
 * MEWS components
 */
export interface MEWSComponents {
  /** Systolic blood pressure score (0-3) */
  systolic_bp_score: number;

  /** Heart rate score (0-3) */
  heart_rate_score: number;

  /** Respiratory rate score (0-3) */
  respiratory_rate_score: number;

  /** Temperature score (0-2) */
  temperature_score: number;

  /** Level of consciousness score (0-3) */
  consciousness_score: number;
}

/**
 * MEWS categories
 */
export type MEWSCategory =
  | 'low'             // Rendah (0-2): Monitoring rutin
  | 'medium'          // Sedang (3-4): Perawatan lebih intensif
  | 'high'            // Tinggi (5-6): Pertimbangkan rujukan ke ICU
  | 'critical';       // Kritis (7+): Segera rujuk ke ICU/RRT

/**
 * MEWS recommended actions
 */
export type MEWSAction =
  | 'routine_observations'        // Observasi rutin
  | 'increase_observation_frequency'  // Tingkatkan frekuensi observasi
  | 'inform_medical_staff'        // Informasikan tenaga medis
  | 'consider_icu_consultation'  // Pertimbangkan konsultasi ICU
  | 'immediate_icu_consultation'; // Segera konsultasi ICU

/**
 * Pediatric Early Warning Score (PEWS) calculation
 */
export interface PEWS {
  /** Total PEWS score (0-16+) */
  total_score: number;

  /** PEWS category */
  category: PEWSCategory;

  /** Individual component scores */
  components: PEWSComponents;

  /** Calculated timestamp */
  calculated_at: string;

  /** Recommended action based on score */
  recommended_action: PEWSAction;

  /** Requires rapid response team? */
  requires_rrt: boolean;

  /** Requires PICU admission? */
  requires_picu: boolean;
}

/**
 * PEWS components
 */
export interface PEWSComponents {
  /** Behavior score (0-4) */
  behavior_score: number;

  /** Cardiovascular score (0-4) */
  cardiovascular_score: number;

  /** Respiratory score (0-4) */
  respiratory_score: number;
}

/**
 * PEWS categories
 */
export type PEWSCategory =
  | 'low'             // Rendah (0-2): Monitoring rutin
  | 'medium'          // Sedang (3-5): Perawatan lebih intensif
  | 'high'            // Tinggi (6-7): Pertimbangkan rujukan ke PICU
  | 'critical';       // Kritis (8+): Segera rujuk ke PICU/RRT

/**
 * PEWS recommended actions
 */
export type PEWSAction =
  | 'routine_observations'        // Observasi rutin
  | 'increase_observation_frequency'  // Tingkatkan frekuensi observasi
  | 'inform_medical_staff'        // Informasikan tenaga medis
  | 'consider_picu_consultation'  // Pertimbangkan konsultasi PICU
  | 'immediate_picu_consultation'; // Segera konsultasi PICU

/**
 * National Early Warning Score 2 (NEWS2) calculation
 */
export interface NEWS2 {
  /** Total NEWS2 score (0-20+) */
  total_score: number;

  /** NEWS2 category */
  category: NEWS2Category;

  /** Individual component scores */
  components: NEWS2Components;

  /** Is SPO2 on air or oxygen? */
  spo2_scale: 'news2_air' | 'news2_oxygen';

  /** Calculated timestamp */
  calculated_at: string;

  /** Recommended action based on score */
  recommended_action: NEWS2Action;

  /** Requires urgent response? */
  requires_urgent_response: boolean;
}

/**
 * NEWS2 components
 */
export interface NEWS2Components {
  /** Respiration rate score (0-3) */
  respiration_rate_score: number;

  /** SpO2 score (0-3) */
  spo2_score: number;

  /** Air or oxygen score (0-2) */
  air_or_oxygen_score: number;

  /** Systolic blood pressure score (0-3) */
  systolic_bp_score: number;

  /** Pulse rate score (0-3) */
  pulse_rate_score: number;

  /** Level of consciousness score (0-3) */
  consciousness_score: number;

  /** Temperature score (0-3) */
  temperature_score: number;
}

/**
 * NEWS2 categories
 */
export type NEWS2Category =
  | 'low'             // Rendah (0-4): Rawat inap / observasi
  | 'medium_low'      // Sedang rendah (5-6): Tinjau oleh dokter
  | 'medium_high'     // Sedang tinggi (7): Pertimbangkan perawatan tingkat lanjut
  | 'high';           // Tinggi (8+): Perawatan kritis segera

/**
 * NEWS2 recommended actions
 */
export type NEWS2Action =
  | 'routine_monitoring'          // Monitoring rutin
  | 'ward_based_escalation'       // Eskalasi berbasis ruang rawat
  | 'urgent_ward_based_escalation'  // Eskalasi mendesak berbasis ruang rawat
  | 'emergency_response';         // Respon darurat

// ============================================================================
// FORM STATE TYPES - For Managing the Vital Signs Form
// ============================================================================

/**
 * Vital signs form state
 */
export interface VitalSignsFormState {
  /** Current form step */
  current_step: VitalSignsFormStep;

  /** Vital signs measurements */
  measurements: VitalSignsMeasurements;

  /** Measurement context */
  context: MeasurementContext;

  /** Form validation errors */
  validation_errors: VitalSignsValidationError[];

  /** Is form dirty (has unsaved changes) */
  is_dirty: boolean;

  /** Is form valid */
  is_valid: boolean;

  /** Is submitting */
  is_submitting: boolean;

  /** Alerts generated */
  alerts?: VitalSignsAlerts;

  /** Trends calculated */
  trends?: VitalSignsTrends;

  /** Early warning scores */
  ews_scores?: EarlyWarningScores;

  /** Additional notes */
  notes?: string;

  /** Form mode */
  mode: FormMode;
}

/**
 * Vital signs form steps
 */
export type VitalSignsFormStep =
  | 'basic_measurements'      // Pengukuran dasar (BP, HR, RR, Temp, SpO2)
  | 'additional_measurements'  // Pengukuran tambahan (Weight, Height, BMI)
  | 'neurological_assessment'  // Asesmen neurologis (GCS, Pain)
  | 'laboratory'              // Laboratorium (Blood Glucose)
  | 'review';                 // Review

/**
 * Vital signs measurements collection
 */
export interface VitalSignsMeasurements {
  /** Blood pressure */
  blood_pressure?: BloodPressure;

  /** Heart rate */
  heart_rate?: HeartRate;

  /** Respiratory rate */
  respiratory_rate?: RespiratoryRate;

  /** Temperature */
  temperature?: Temperature;

  /** SpO2 */
  spo2?: SpO2;

  /** Weight */
  weight?: Weight;

  /** Height */
  height?: Height;

  /** BMI (calculated) */
  bmi?: BMI;

  /** Pain score */
  pain_score?: PainScore;

  /** GCS */
  gcs?: GCS;

  /** Blood glucose */
  blood_glucose?: BloodGlucose;
}

/**
 * Vital signs validation error
 */
export interface VitalSignsValidationError {
  /** Field with error */
  field: string;

  /** Error message (Indonesian) */
  message: string;

  /** Error severity */
  severity: 'error' | 'warning';

  /** Vital sign type */
  vital_sign_type: VitalSignType;
}

/**
 * Early warning scores collection
 */
export interface EarlyWarningScores {
  /** MEWS for adults */
  mews?: MEWS;

  /** PEWS for pediatrics */
  pews?: PEWS;

  /** NEWS2 */
  news2?: NEWS2;

  /** Which score is relevant */
  relevant_score: 'mews' | 'pews' | 'news2';
}

/**
 * Form modes
 */
export type FormMode =
  | 'create'          // Membuat catatan baru
  | 'edit'            // Mengedit catatan yang ada
  | 'view'            // Melihat catatan
  | 'templates';      // Template

/**
 * Form action types for state management
 */
export type VitalSignsFormAction =
  | { type: 'SET_STEP'; payload: VitalSignsFormStep }
  | { type: 'SET_BLOOD_PRESSURE'; payload: BloodPressure }
  | { type: 'SET_HEART_RATE'; payload: HeartRate }
  | { type: 'SET_RESPIRATORY_RATE'; payload: RespiratoryRate }
  | { type: 'SET_TEMPERATURE'; payload: Temperature }
  | { type: 'SET_SPO2'; payload: SpO2 }
  | { type: 'SET_WEIGHT'; payload: Weight }
  | { type: 'SET_HEIGHT'; payload: Height }
  | { type: 'SET_BMI'; payload: BMI }
  | { type: 'SET_PAIN_SCORE'; payload: PainScore }
  | { type: 'SET_GCS'; payload: GCS }
  | { type: 'SET_BLOOD_GLUCOSE'; payload: BloodGlucose }
  | { type: 'SET_CONTEXT'; payload: Partial<MeasurementContext> }
  | { type: 'SET_NOTES'; payload: string }
  | { type: 'CALCULATE_BMI' }
  | { type: 'CALCULATE_EWS' }
  | { type: 'VALIDATE' }
  | { type: 'SUBMIT' }
  | { type: 'RESET' }
  | { type: 'SET_MODE'; payload: FormMode };

// ============================================================================
// API REQUEST/RESPONSE TYPES - For Backend Integration
// ============================================================================

/**
 * Create vital signs record request
 */
export interface CreateVitalSignsRequest {
  /** Patient ID */
  patient_id: string;

  /** Visit/Encounter ID (if applicable) */
  visit_id?: string;

  /** Vital signs measurements */
  measurements: VitalSignsMeasurements;

  /** Measurement context */
  context: MeasurementContext;

  /** Alerts generated */
  alerts?: VitalSignsAlerts;

  /** Early warning scores */
  ews_scores?: EarlyWarningScores;

  /** Notes */
  notes?: string;

  /** Is this a rapid assessment? */
  is_rapid_assessment?: boolean;
}

/**
 * Create vital signs record response
 */
export interface CreateVitalSignsResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Vital signs record ID */
    vital_signs_id: string;

    /** Timestamp created */
    created_at: string;

    /** Created by */
    created_by: string;

    /** Record summary */
    summary: VitalSignsRecordSummary;
  };

  /** Response message */
  message?: string;

  /** Error details */
  error?: ApiError;
}

/**
 * Vital signs record summary
 */
export interface VitalSignsRecordSummary {
  /** Record ID */
  id: string;

  /** Patient ID */
  patient_id: string;

  /** Patient name */
  patient_name: string;

  /** Measurement timestamp */
  timestamp: string;

  /** Key vital signs */
  key_vitals: {
    blood_pressure?: { systolic: number; diastolic: number };
    heart_rate?: number;
    respiratory_rate?: number;
    temperature?: number;
    spo2?: number;
  };

  /** Alert count */
  alert_count: number;

  /** Critical alert count */
  critical_alert_count: number;

  /** MEWS/PEWS/NEWS2 score */
  ews_score?: number;
}

/**
 * Get vital signs history request
 */
export interface GetVitalSignsHistoryRequest {
  /** Patient ID */
  patient_id: string;

  /** Visit ID (optional) */
  visit_id?: string;

  /** Date range start */
  date_from?: string;

  /** Date range end */
  date_to?: string;

  /** Vital sign types to include */
  vital_sign_types?: VitalSignType[];

  /** Maximum records to return */
  limit?: number;

  /** Offset for pagination */
  offset?: number;
}

/**
 * Get vital signs history response
 */
export interface GetVitalSignsHistoryResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Vital signs records */
    records: VitalSignsRecord[];

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
 * Complete vital signs record
 */
export interface VitalSignsRecord {
  /** Record ID */
  id: string;

  /** Patient ID */
  patient_id: string;

  /** Visit ID */
  visit_id?: string;

  /** Measurements */
  measurements: VitalSignsMeasurements;

  /** Context */
  context: MeasurementContext;

  /** Alerts */
  alerts?: VitalSignsAlerts;

  /** Trends */
  trends?: VitalSignsTrends;

  /** Early warning scores */
  ews_scores?: EarlyWarningScores;

  /** Notes */
  notes?: string;

  /** Created at */
  created_at: string;

  /** Created by */
  created_by: string;

  /** Updated at */
  updated_at?: string;

  /** Updated by */
  updated_by?: string;
}

/**
 * Update vital signs record request
 */
export interface UpdateVitalSignsRequest {
  /** Record ID */
  vital_signs_id: string;

  /** Measurements to update */
  measurements: Partial<VitalSignsMeasurements>;

  /** Context to update */
  context?: Partial<MeasurementContext>;

  /** Notes to update */
  notes?: string;

  /** Reason for update */
  update_reason: string;
}

/**
 * Update vital signs record response
 */
export interface UpdateVitalSignsResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Updated record ID */
    vital_signs_id: string;

    /** Updated at timestamp */
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
 * Delete vital signs record request
 */
export interface DeleteVitalSignsRequest {
  /** Record ID */
  vital_signs_id: string;

  /** Reason for deletion */
  deletion_reason: string;
}

/**
 * Delete vital signs record response
 */
export interface DeleteVitalSignsResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Deleted record ID */
    vital_signs_id: string;

    /** Deleted at timestamp */
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
 * Get vital signs trends request
 */
export interface GetVitalSignsTrendsRequest {
  /** Patient ID */
  patient_id: string;

  /** Vital sign types to analyze */
  vital_sign_types: VitalSignType[];

  /** Time range */
  time_range: TrendTimeRange;

  /** Date from */
  date_from?: string;

  /** Date to */
  date_to?: string;
}

/**
 * Trend time ranges
 */
export type TrendTimeRange =
  | 'last_24_hours'    // 24 jam terakhir
  | 'last_48_hours'    // 48 jam terakhir
  | 'last_7_days'      // 7 hari terakhir
  | 'last_30_days'     // 30 hari terakhir
  | 'custom';          // Kustom

/**
 * Get vital signs trends response
 */
export interface GetVitalSignsTrendsResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Trends for each vital sign */
    trends: VitalSignsTrends;

    /** Analysis period */
    analysis_period: {
      from: string;
      to: string;
      duration_hours: number;
    };

    /** Significant findings */
    significant_findings: string[];
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
 * Validate vital signs request
 */
export interface ValidateVitalSignsRequest {
  /** Patient ID */
  patient_id: string;

  /** Age group */
  age_group: AgeGroup;

  /** Gender */
  gender: 'male' | 'female';

  /** Measurements to validate */
  measurements: Partial<VitalSignsMeasurements>;
}

/**
 * Validate vital signs response
 */
export interface ValidateVitalSignsResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Is valid */
    is_valid: boolean;

    /** Validation errors */
    errors: VitalSignsValidationError[];

    /** Alerts generated */
    alerts: VitalSignsAlerts;

    /** Early warning scores */
    ews_scores?: EarlyWarningScores;
  };

  /** Response message */
  message?: string;

  /** Error details */
  error?: ApiError;
}

// ============================================================================
// VALIDATION CONSTRAINTS - Normal Ranges and Alert Thresholds
// ============================================================================

/**
 * Vital signs validation constraints by age group
 */
export interface VitalSignsValidationConstraints {
  /** Age group */
  age_group: AgeGroup;

  /** Blood pressure constraints */
  blood_pressure: {
    systolic: NormalRange;
    diastolic: NormalRange;
    critical: CriticalThresholds;
  };

  /** Heart rate constraints */
  heart_rate: {
    normal: NormalRange;
    critical: CriticalThresholds;
  };

  /** Respiratory rate constraints */
  respiratory_rate: {
    normal: NormalRange;
    critical: CriticalThresholds;
  };

  /** Temperature constraints */
  temperature: {
    normal: NormalRange;
    celsius: { min: number; max: number };
    fahrenheit: { min: number; max: number };
    critical: CriticalThresholds;
  };

  /** SpO2 constraints */
  spo2: {
    normal: NormalRange;
    critical: CriticalThresholds;
    on_oxygen_adjustment: number;
  };

  /** BMI constraints */
  bmi: {
    normal: NormalRange;
    categories: BMIConstraints;
  };

  /** Pain score constraints */
  pain_score: {
    min: number;
    max: number;
    severe_threshold: number;
  };

  /** GCS constraints */
  gcs: {
    min: number;
    max: number;
    critical_threshold: number;
  };

  /** Blood glucose constraints */
  blood_glucose: {
    fasting: NormalRange;
    random: NormalRange;
    critical: CriticalThresholds;
  };
}

/**
 * BMI category constraints
 */
export interface BMIConstraints {
  /** Underweight threshold */
  underweight_threshold: number;

  /** Normal range min/max */
  normal_min: number;
  normal_max: number;

  /** Overweight threshold */
  overweight_threshold: number;

  /** Obese class I threshold */
  obese_i_threshold: number;

  /** Obese class II threshold */
  obese_ii_threshold: number;
}

/**
 * Get validation constraints for age group
 */
export interface GetVitalSignsConstraintsRequest {
  /** Age group */
  age_group: AgeGroup;

  /** Gender */
  gender?: 'male' | 'female';
}

/**
 * Get validation constraints response
 */
export interface GetVitalSignsConstraintsResponse {
  /** Success status */
  success: boolean;

  /** Response data */
  data?: {
    /** Validation constraints */
    constraints: VitalSignsValidationConstraints;

    /** Last updated */
    last_updated: string;
  };

  /** Response message */
  message?: string;

  /** Error details */
  error?: ApiError;
}

// ============================================================================
// HELPER TYPES - Utility Types for Vital Signs
// ============================================================================

/**
 * Vital signs chart data point
 */
export interface VitalSignsChartPoint {
  /** Timestamp */
  timestamp: string;

  /** Value */
  value: number;

  /** Is abnormal */
  is_abnormal: boolean;

  /** Annotation */
  annotation?: string;
}

/**
 * Vital signs chart data
 */
export interface VitalSignsChartData {
  /** Vital sign type */
  vital_sign_type: VitalSignType;

  /** Chart title (Indonesian) */
  title: string;

  /** Y-axis label */
  y_axis_label: string;

  /** Unit */
  unit: string;

  /** Normal range */
  normal_range: NormalRange;

  /** Data points */
  data_points: VitalSignsChartPoint[];
}

/**
 * Vital signs comparison data
 */
export interface VitalSignsComparison {
  /** Current measurement */
  current: VitalSignsRecord;

  /** Previous measurement */
  previous?: VitalSignsRecord;

  /** Baseline measurement */
  baseline?: VitalSignsRecord;

  /** Changes */
  changes: VitalSignsChanges;
}

/**
 * Vital signs changes
 */
export interface VitalSignsChanges {
  /** Blood pressure change */
  blood_pressure?: {
    systolic: number;
    diastolic: number;
    is_significant: boolean;
  };

  /** Heart rate change */
  heart_rate?: {
    change: number;
    is_significant: boolean;
  };

  /** Respiratory rate change */
  respiratory_rate?: {
    change: number;
    is_significant: boolean;
  };

  /** Temperature change */
  temperature?: {
    change: number;
    is_significant: boolean;
  };

  /** SpO2 change */
  spo2?: {
    change: number;
    is_significant: boolean;
  };
}

/**
 * Vital signs report data
 */
export interface VitalSignsReport {
  /** Report ID */
  report_id: string;

  /** Patient ID */
  patient_id: string;

  /** Patient name */
  patient_name: string;

  /** Date range */
  date_range: {
    from: string;
    to: string;
  };

  /** Records included */
  records: VitalSignsRecord[];

  /** Charts */
  charts: VitalSignsChartData[];

  /** Trends */
  trends: VitalSignsTrends;

  /** Summary statistics */
  summary: VitalSignsSummaryStatistics;

  /** Alerts during period */
  alerts: VitalSignsAlerts[];

  /** Generated at */
  generated_at: string;

  /** Generated by */
  generated_by: string;
}

/**
 * Vital signs summary statistics
 */
export interface VitalSignsSummaryStatistics {
  /** Blood pressure statistics */
  blood_pressure: VitalSignStatistics;

  /** Heart rate statistics */
  heart_rate: VitalSignStatistics;

  /** Respiratory rate statistics */
  respiratory_rate: VitalSignStatistics;

  /** Temperature statistics */
  temperature: VitalSignStatistics;

  /** SpO2 statistics */
  spo2: VitalSignStatistics;
}

/**
 * Individual vital sign statistics
 */
export interface VitalSignStatistics {
  /** Minimum value */
  min: number;

  /** Maximum value */
  max: number;

  /** Average value */
  average: number;

  /** Median value */
  median: number;

  /** Standard deviation */
  standard_deviation: number;

  /** Count of abnormal readings */
  abnormal_count: number;

  /** Total readings */
  total_count: number;
}

/**
 * Vital signs notification
 */
export interface VitalSignsNotification {
  /** Notification ID */
  id: string;

  /** Patient ID */
  patient_id: string;

  /** Alert */
  alert: VitalSignsAlert;

  /** Is read */
  is_read: boolean;

  /** Read at */
  read_at?: string;

  /** Created at */
  created_at: string;

  /** Action taken */
  action_taken?: string;

  /** Action taken by */
  action_taken_by?: string;

  /** Action taken at */
  action_taken_at?: string;
}
