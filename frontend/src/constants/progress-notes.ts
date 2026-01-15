/**
 * Progress Notes Form Constants
 * Constants untuk Form Catatan Perkembangan Pasien (Progress Notes)
 */

// ================================
// Tipe Catatan (Note Type Options)
// ================================
export const NOTE_TYPES = [
  { value: 'daily', label: 'Catatan Harian', description: 'Catatan perkembangan pasien harian' },
  { value: 'nursing', label: 'Catatan Perawat', description: 'Catatan keperawatan' },
  { value: 'physician', label: 'Catatan Dokter', description: 'Catatan dokter penanggung jawab' },
  { value: 'consultation', label: 'Catatan Konsultasi', description: 'Catatan konsultasi spesialis' },
  { value: 'procedure', label: 'Catatan Prosedur', description: 'Catatan prosedur medis' },
  { value: 'discharge', label: 'Catatan Pulang', description: 'Catatan saat pasien pulang' },
  { value: 'transfer', label: 'Catatan Rujukan', description: 'Catatan rujukan pasien' },
] as const;

export type NoteType = typeof NOTE_TYPES[number]['value'];

// ================================
// Status Klinis (Clinical Status)
// ================================
export const CLINICAL_STATUS = [
  { value: 'stable', label: 'Stabil', color: 'green', description: 'Kondisi pasien stabil' },
  { value: 'improved', label: 'Membaik', color: 'blue', description: 'Kondisi pasien menunjukkan perbaikan' },
  { value: 'worsened', label: 'Memburuk', color: 'orange', description: 'Kondisi pasien memburuk' },
  { value: 'critical', label: 'Kritis', color: 'red', description: 'Kondisi pasien kritis' },
] as const;

export type ClinicalStatus = typeof CLINICAL_STATUS[number]['value'];

// ================================
// Template SOAP Note
// ================================

// Template Subjective
export const SOAP_SUBJECTIVE_TEMPLATES = {
  chief_complaint: 'Keluhan Utama: {complaint}',
  symptom_duration: 'Durasi: {duration}',
  pain_scale: 'Skala Nyeri: {scale}/10',
  patient_statement: 'Pasien mengatakan: "{statement}"',
  review_of_systems: 'Review Sistem: {systems}',
  history_present_illness: 'Riwayat Penyakit Sekarang: {history}',
  general_condition: 'Kondisi Umum: {condition}',
} as const;

// Template Objective
export const SOAP_OBJECTIVE_TEMPLATES = {
  vital_signs: 'Tanda Vital: TD {bp}, N {hr}, RR {rr}, T {temp}°C, SpO2 {spo2}%',
  physical_exam: 'Pemeriksaan Fisik: {findings}',
  laboratory_results: 'Hasil Laboratorium: {results}',
  imaging_results: 'Hasil Pemeriksaan Radiologi: {results}',
  neurology_status: 'Status Neurologi: GCS {gcs}, pupils {pupils}',
  cardiovascular_status: 'Status Kardiovaskular: Jantung {heart}, lung {lung}',
  consciousness_level: 'Tingkat Kesadaran: {level}',
  intake_output: 'Input/Output: Masuk {intake}ml, Keluar {output}ml',
} as const;

// Template Assessment
export const SOAP_ASSESSMENT_TEMPLATES = {
  primary_diagnosis: 'Diagnosa Utama: {diagnosis}',
  secondary_diagnosis: 'Diagnosa Sekunder: {diagnosis}',
  clinical_condition: 'Kondisi Klinis: {condition}',
  problem_list: 'Daftar Masalah: {problems}',
  severity_assessment: 'Penilaian Keparahan: {severity}',
  prognosis: 'Prognosis: {prognosis}',
  differential_diagnosis: 'Diagnosa Diferensial: {diagnosis}',
} as const;

// Template Plan
export const SOAP_PLAN_TEMPLATES = {
  medication_plan: 'Rencana Obat: {medications}',
  diagnostic_plan: 'Rencana Diagnostik: {diagnostics}',
  treatment_plan: 'Rencana Tatalaksana: {treatment}',
  follow_up_plan: 'Rencana Tindak Lanjut: {followup}',
  referral_plan: 'Rencana Rujukan: {referral}',
  patient_education: 'Edukasi Pasien: {education}',
  diet_plan: 'Rencana Diet: {diet}',
  activity_plan: 'Rencana Aktivitas: {activity}',
} as const;

// Template SOAP lengkap
export const SOAP_NOTE_TEMPLATES = {
  initial_admission: {
    subjective: 'Pasien masuk dengan keluhan {complaint} sejak {duration}. Menyangkal riwayat penyakit serupa.',
    objective: 'Kesadaran compos mentis, TD {bp}/mmHg, N {hr}/menit, RR {rr}/menit, T {temp}°C, SpO2 {spo2}%. Pemeriksaan fisik dalam batas normal.',
    assessment: 'Pasien dengan {diagnosis}. Kondisi umum {status}.',
    plan: 'Rawat inap, pemberian obat sesuai standar, monitoring tanda vital, {additional_plan}.',
  },
  daily_progress: {
    subjective: 'Pasien mengeluh {complaint} jika ada. Nafsu makan {appetite}. Tidur {sleep}.',
    objective: 'TD {bp}/mmHg, N {hr}/menit, RR {rr}/menit, T {temp}°C, SpO2 {spo2}%. {physical_exam}.',
    assessment: 'Kondisi pasien {status}. {progress}.',
    plan: 'Lanjutkan terapi saat ini. {additional_plan}. Monitoring tanda vital rutin.',
  },
  pre_procedure: {
    subjective: 'Pasien akan menjalani prosedur {procedure}. Menyangkal alergi obat/makanan.',
    objective: 'Kondisi umum baik, tanda vital stabil. Status pra-bedak OK.',
    assessment: 'Pasien dalam kondisi {status} untuk prosedur {procedure}.',
    plan: 'Lanjutkan prosedur {procedure} sesuai jadwal. Persiapan {preparation}.',
  },
  post_procedure: {
    subjective: 'Pasien post prosedur {procedure}. Mengeluh {complaint}.',
    objective: 'TD {bp}/mmHg, N {hr}/menit, RR {rr}/menit, T {temp}°C, SpO2 {spo2}%. Luka {wound_condition}.',
    assessment: 'Kondisi post {procedure} {status}. {complications}.',
    plan: 'Monitoring tanda vital {frequency}. Pain control {pain_management}. {additional_plan}.',
  },
  discharge: {
    subjective: 'Pasien akan pulang hari ini. Kondisi {condition}.',
    objective: 'TD {bp}/mmHg, N {hr}/menit, RR {rr}/menit, T {temp}°C, SpO2 {spo2}%. Kondisi umum {status}.',
    assessment: 'Pasien {diagnosis} dalam kondisi {status} untuk pulang.',
    plan: 'Pulang dengan obat {medications}. Kontrol {followup}. Edukasi {education}.',
  },
} as const;

// ================================
// Kategori Intervensi
// ================================
export const INTERVENTION_CATEGORIES = [
  {
    value: 'medication',
    label: 'Obat-obatan',
    subcategories: ['Obat Oral', 'Obat Injeksi', 'Obat Topikal', 'Obat Inhalasi', 'Obat IV'],
  },
  {
    value: 'procedure',
    label: 'Prosedur',
    subcategories: ['Pemasangan Infus', 'Pemasangan Kateter', 'Pemasangan NGT', 'Luka Operasi', 'Pemasangan O2'],
  },
  {
    value: 'treatment',
    label: 'Tatalaksana',
    subcategories: ['Terapi Oksigen', 'Terapi Nebulisasi', 'Terapi Fisik', 'Terapi Wicara', 'Terapi Okupasi'],
  },
  {
    value: 'nutrition',
    label: 'Nutrisi',
    subcategories: ['Diet Biasa', 'Diet Lunak', 'Diet PPA', 'Diet Rendah Garam', 'Diet Rendah Lemak', 'Diet DM', 'Diet Renal', 'NPO', 'Parenteral'],
  },
  {
    value: 'activity',
    label: 'Aktivitas',
    subcategories: ['Bed Rest Total', 'Bed Rest Partial', 'Up as needed', 'Ambulatory', 'Mobilisasi'],
  },
  {
    value: 'education',
    label: 'Edukasi',
    subcategories: ['Edukasi Obat', 'Edukasi Diet', 'Edukasi Aktivitas', 'Edukasi hygiene', 'Edukasi Keluarga'],
  },
  {
    value: 'monitoring',
    label: 'Monitoring',
    subcategories: ['Tanda Vital', 'Input Output', 'Berat Badan', 'Gula Darah', 'Kesadaran'],
  },
  {
    value: 'hygiene',
    label: 'Kebersihan Diri',
    subcategories: ['Mandi', 'Keramas', 'Ganti Pakaian', 'Perawatan Mulut', 'Perawatan Kulit'],
  },
] as const;

export type InterventionCategory = typeof INTERVENTION_CATEGORIES[number]['value'];

// ================================
// Aturan Validasi
// ================================

// Batasan karakter
export const CHARACTER_LIMITS = {
  chief_complaint: 500,
  subjective: 2000,
  objective: 2000,
  assessment: 1500,
  plan: 2000,
  note: 5000,
  intervention: 1000,
  diagnosis: 500,
  patient_statement: 1000,
} as const;

// Field wajib per tipe catatan
export const REQUIRED_FIELDS_BY_NOTE_TYPE: Record<NoteType, string[]> = {
  daily: ['patientId', 'noteDate', 'noteTime', 'clinicalStatus', 'subjective', 'objective', 'assessment', 'plan'],
  nursing: ['patientId', 'noteDate', 'noteTime', 'subjective', 'objective', 'interventions'],
  physician: ['patientId', 'noteDate', 'noteTime', 'diagnosis', 'subjective', 'objective', 'assessment', 'plan'],
  consultation: ['patientId', 'noteDate', 'noteTime', 'consultant', 'subjective', 'objective', 'assessment', 'plan'],
  procedure: ['patientId', 'noteDate', 'noteTime', 'procedureName', 'indication', 'procedureDetails'],
  discharge: ['patientId', 'noteDate', 'noteTime', 'dischargeSummary', 'dischargeMedications', 'followUpPlan'],
  transfer: ['patientId', 'noteDate', 'noteTime', 'transferReason', 'transferSummary', 'destination'],
};

// Validasi SOAP note
export const SOAP_VALIDATION = {
  subjective_required: ['daily', 'nursing', 'physician', 'consultation'],
  objective_required: ['daily', 'nursing', 'physician', 'consultation'],
  assessment_required: ['daily', 'physician', 'consultation'],
  plan_required: ['daily', 'physician', 'consultation', 'discharge'],
  vital_signs_required: ['daily', 'nursing', 'physician', 'consultation'],
  diagnosis_required: ['physician', 'consultation', 'discharge'],
} as const;

// Validasi karakter
export const validateCharacterLimit = (text: string, field: keyof typeof CHARACTER_LIMITS): boolean => {
  return text.length <= CHARACTER_LIMITS[field];
};

// ================================
// Template Catatan Perkembangan
// ================================

// Template umum
export const PROGRESS_NOTE_TEMPLATES = {
  admission: {
    title: 'Catatan Masuk Rawat Inap',
    template: `Pasien {name}, {age} tahun, jenis kelamin {gender}, masuk tanggal {date} dengan keluhan {complaint}.

Riwayat Penyakit:
{medical_history}

Pemeriksaan Fisik:
- Kesadaran: {consciousness}
- Tanda Vital: TD {bp}, N {hr}, RR {rr}, T {temp}, SpO2 {spo2}
- Pemeriksaan Fisik: {physical_exam}

Rencana Tatalaksana:
{plan}`,
  },

  daily_round: {
    title: 'Catatan Visit Harian',
    template: `Tanggal: {date}
Jam: {time}

Subjektif:
{subjective}

Objektif:
- Tanda Vital: TD {bp}, N {hr}, RR {rr}, T {temp}, SpO2 {spo2}
- Pemeriksaan Fisik: {physical_exam}

Asesmen:
{assessment}

Rencana:
{plan}

Dokter,
{doctor_name}
NIP. {nip}`,
  },

  nursing_care: {
    title: 'Catatan Asuhan Keperawatan',
    template: `Tanggal/Jam: {datetime}

Subjektif:
{subjective}

Objektif:
- Tanda Vital: {vital_signs}
- Kondisi Umum: {general_condition}
- Status Fungsional: {functional_status}
- Intervensi: {interventions}

Evaluasi:
{evaluation}`,
  },

  pre_discharge: {
    title: 'Catatan Pra Pulang',
    template: `Tanggal: {date}

Kondisi Saat Pulang:
- Kesadaran: {consciousness}
- Tanda Vital: {vital_signs}
- Kondisi Umum: {general_condition}

Diagnosa Akhir:
{diagnosis}

Pengobatan Saat Pulang:
{medications}

Instruksi Tindak Lanjut:
{instructions}

Kontrol: {followup_date} di {location}`,
  },
} as const;

// Template spesialisasi
export const SPECIALTY_TEMPLATES = {
  internal_medicine: {
    name: 'Penyakit Dalam',
    template: `Fokus: Sistem organ dalam
Riwayat Penyakit Kronis: {chronic_diseases}
Status Kardiovaskular: {cardio_status}
Status Respiratory: {respiratory_status}
Status Gastrointestinal: {gi_status}
Status Neurologis: {neuro_status}`,
  },

  surgery: {
    name: 'Bedah',
    template: `Fokus: Kondisi Pra/Post Bedah
Status Luka Operasi: {wound_status}
Drain: {drain_status}
Status Ambulasi: {ambulation_status}
Status Nutrisi: {nutrition_status}
Toleransi Oral: {oral_tolerance}`,
  },

  pediatrics: {
    name: 'Anak',
    template: `Fokus: Kesehatan Anak
Berat Badan: {weight}
Tinggi Badan: {height}
Status Tumbuh Kembang: {development_status}
Status Imunisasi: {immunization_status}
Status Nutrisi: {nutrition_status}
Kondisi Orang Tua: {parents_condition}`,
  },

  obstetrics_gynecology: {
    name: 'Kandungan',
    template: `Fokus: Kesehatan Ibu dan Bayi
Usia Kehamilan: {gestational_age}
Janin: {fetal_condition}
Kontraksi: {contraction_status}
Kondisi Ibu: {mother_condition}
Riwayat Kehamilan: {pregnancy_history}`,
  },

  neurology: {
    name: 'Saraf',
    template: `Fokus: Sistem Saraf
GCS: {gcs}
Status Pupil: {pupil_status}
Status Motorik: {motor_status}
Status Sensorik: {sensory_status}
Reflek: {reflexes}
Status Mental: {mental_status}`,
  },

  cardiology: {
    name: 'Jantung',
    template: `Fokus: Sistem Kardiovaskular
Status Jantung: {heart_status}
EKG: {ecg_findings}
Echocardiography: {echo_findings}
Status Hemodinamik: {hemodynamic_status}
Status Perifer: {peripheral_status}`,
  },

  pulmonology: {
    name: 'Paru',
    template: `Fokus: Sistem Respiratory
Status Pernapasan: {breathing_status}
Status Paru: {lung_status}
Oksigenasi: {oxygenation_status}
Batuk: {cough_status}
Sputum: {sputum_status}`,
  },

  orthopedics: {
    name: 'Orthopedi',
    template: `Fokus: Sistem Muskuloskeletal
Status Fraktur: {fracture_status}
Status Imobilisasi: {immobilization_status}
Status Sendi: {joint_status}
Status Otot: {muscle_status}
Status Ambulasi: {ambulation_status}`,
  },

  emergency: {
    name: 'IGD',
    template: `Fokus: Kondisi Gawat Darurat
Triase: {triage_level}
Keluhan Utama: {chief_complaint}
Mekanisme Cedera: {injury_mechanism}
Status Stabilisasi: {stabilization_status}
Rencana Tatalaksana: {emergency_plan}`,
  },

  icu: {
    name: 'ICU',
    template: `Fokus: Perawatan Intensif
Score SOFA: {sofa_score}
Status Ventilasi: {ventilation_status}
Status Hemodinamik: {hemodynamic_status}
Status Infeksi: {infection_status}
Balance Cairan: {fluid_balance}
Status Sedasi: {sedation_status}`,
  },
} as const;

// ================================
// Helper Functions
// ================================

/**
 * Get note type label by value
 */
export const getNoteTypeLabel = (value: NoteType): string => {
  return NOTE_TYPES.find(type => type.value === value)?.label || value;
};

/**
 * Get clinical status label by value
 */
export const getClinicalStatusLabel = (value: ClinicalStatus): string => {
  return CLINICAL_STATUS.find(status => status.value === value)?.label || value;
};

/**
 * Get clinical status color by value
 */
export const getClinicalStatusColor = (value: ClinicalStatus): string => {
  return CLINICAL_STATUS.find(status => status.value === value)?.color || 'gray';
};

/**
 * Get required fields for note type
 */
export const getRequiredFields = (noteType: NoteType): string[] => {
  return REQUIRED_FIELDS_BY_NOTE_TYPE[noteType] || [];
};

/**
 * Get template by specialty
 */
export const getSpecialtyTemplate = (specialty: keyof typeof SPECIALTY_TEMPLATES): string => {
  return SPECIALTY_TEMPLATES[specialty]?.template || '';
};

/**
 * Format SOAP note from templates
 */
export const formatSOAPNote = (
  type: keyof typeof SOAP_NOTE_TEMPLATES,
  data: Record<string, string>
): { subjective: string; objective: string; assessment: string; plan: string } => {
  const template = SOAP_NOTE_TEMPLATES[type];
  if (!template) {
    return { subjective: '', objective: '', assessment: '', plan: '' };
  }

  return {
    subjective: template.subjective.replace(/\{(\w+)\}/g, (_, key) => data[key] || ''),
    objective: template.objective.replace(/\{(\w+)\}/g, (_, key) => data[key] || ''),
    assessment: template.assessment.replace(/\{(\w+)\}/g, (_, key) => data[key] || ''),
    plan: template.plan.replace(/\{(\w+)\}/g, (_, key) => data[key] || ''),
  };
};
