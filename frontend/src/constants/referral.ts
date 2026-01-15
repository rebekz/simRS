/**
 * Referral Letter Constants
 * Constants for the Referral Letter Form
 * All labels in Indonesian language
 */

// ===============================
// Referral Type Options
// ===============================

export const REFERRAL_TYPES = [
  { value: 'internal', label: 'Rujukan Internal', description: 'Rujukan ke poliklinik/UNIT lain dalam rumah sakit' },
  { value: 'external', label: 'Rujukan Eksternal', description: 'Rujukan ke fasilitas kesehatan lain' },
  { value: 'bpjs', label: 'Rujukan BPJS', description: 'Rujukan menggunakan sistem BPJS Kesehatan' },
  { value: 'emergency', label: 'Rujukan Emergency', description: 'Rujukan ke IGD untuk kasus gawat darurat' },
  { value: 'control', label: 'Rujukan Kontrol', description: 'Rujukan untuk kontrol/kunjungan ulang' },
  { value: 'specialist', label: 'Rujukan Spesialis', description: 'Rujukan ke dokter spesialis' },
] as const;

export type ReferralType = typeof REFERRAL_TYPES[number]['value'];

// ===============================
// Priority Options
// ===============================

export const REFERRAL_PRIORITIES = [
  { value: 'routine', label: 'Biasa', code: 'RUTIN', description: 'Rujukan rutin' },
  { value: 'urgent', label: 'Segera', code: 'URGENT', description: 'Rujukan prioritas tinggi' },
  { value: 'emergency', label: 'Gawat Darurat', code: 'EMERGENCY', description: 'Kasus gawat darurat' },
] as const;

export type ReferralPriority = typeof REFERRAL_PRIORITIES[number]['value'];

// ===============================
// Facility Type Options
// ===============================

export const FACILITY_TYPES = [
  { value: 'hospital', label: 'Rumah Sakit', code: 'RS' },
  { value: 'clinic', label: 'Klinik', code: 'KLINIK' },
  { value: 'health_center', label: 'Puskesmas', code: 'PUSKESMAS' },
  { value: 'doctor_practice', label: 'Praktik Dokter', code: 'PRAKTIK' },
] as const;

export type FacilityType = typeof FACILITY_TYPES[number]['value'];

// ===============================
// Specialist Categories
// ===============================

export const SPECIALIST_CATEGORIES = [
  { value: 'cardiology', label: 'Spesialis Jantung dan Pembuluh Darah', code: 'JANTUNG' },
  { value: 'neurology', label: 'Spesialis Saraf', code: 'SARAF' },
  { value: 'pediatrics', label: 'Spesialis Anak', code: 'ANAK' },
  { value: 'obgyn', label: 'Spesialis Kandungan', code: 'KANDUNGAN' },
  { value: 'surgery', label: 'Spesialis Bedah', code: 'BEDAH' },
  { value: 'orthopedics', label: 'Spesialis Orthopedi', code: 'ORTHOPEDI' },
  { value: 'dermatology', label: 'Spesialis Kulit dan Kelamin', code: 'KULIT' },
  { value: 'ophthalmology', label: 'Spesialis Mata', code: 'MATA' },
  { value: 'ent', label: 'Spesialis THT', code: 'THT' },
  { value: 'psychiatry', label: 'Spesialis Jiwa', code: 'JIWA' },
  { value: 'internal_medicine', label: 'Spesialis Penyakit Dalam', code: 'PENYAKIT_DALAM' },
  { value: 'pulmonology', label: 'Spesialis Paru', code: 'PARU' },
  { value: 'nephrology', label: 'Spesialis Ginjal', code: 'GINJAL' },
  { value: 'urology', label: 'Spesialis Urologi', code: 'UROLOGI' },
  { value: 'oncology', label: 'Spesialis Onkologi', code: 'ONKOLOGI' },
  { value: 'radiology', label: 'Spesialis Radiologi', code: 'RADIOLOGI' },
  { value: 'anesthesiology', label: 'Spesialis Anestesi', code: 'ANESTESI' },
  { value: 'rehab_medicine', label: 'Spesialis Rehabilitasi Medik', code: 'REHAB' },
] as const;

export type SpecialistCategory = typeof SPECIALIST_CATEGORIES[number]['value'];

// ICD-10 Mapping by Specialist
export const SPECIALIST_ICD10_MAPPING: Record<SpecialistCategory, string[]> = {
  cardiology: ['I*', 'Q20-Q28'], // Diseases of the circulatory system
  neurology: ['G*', 'I60-I69'], // Diseases of the nervous system
  pediatrics: ['P00-P96', 'Q00-Q99'], // Certain conditions originating in the perinatal period
  obgyn: ['O00-O99', 'N70-N98'], // Pregnancy, childbirth and the puerperium
  surgery: ['K*', 'M*', 'T*'], // Digestive, musculoskeletal, injury
  orthopedics: ['M00-M99', 'S*', 'T*'], // Musculoskeletal and connective tissue
  dermatology: ['L00-L99', 'A00-A64'], // Diseases of the skin and subcutaneous tissue
  ophthalmology: ['H00-H59'], // Diseases of the eye and adnexa
  ent: ['H60-H95', 'J00-J06', 'J30-J39'], // Diseases of the ear and respiratory system
  psychiatry: ['F00-F99'], // Mental and behavioral disorders
  internal_medicine: ['E*', 'J*', 'K*'], // Endocrine, respiratory, digestive
  pulmonology: ['J00-J99'], // Diseases of the respiratory system
  nephrology: ['N00-N19'], // Diseases of the genitourinary system
  urology: ['N20-N99'], // Diseases of the genitourinary system
  oncology: ['C00-D48'], // Neoplasms
  radiology: ['Z*'], // Factors influencing health status
  anesthesiology: ['*'], // All codes
  rehab_medicine: ['M00-M99', 'G80-G83'], // Musculoskeletal and cerebral palsy
};

// ===============================
// Validation Rules
// ===============================

export const REFERRAL_VALIDATION_RULES = {
  // Required fields for each referral type
  requiredFieldsByType: {
    internal: ['patientId', 'patientName', 'diagnosis', 'destinationFacility', 'referralReason'],
    external: ['patientId', 'patientName', 'diagnosis', 'destinationFacility', 'facilityType', 'referralReason'],
    bpjs: ['patientId', 'patientName', 'bpjsNumber', 'diagnosis', 'destinationFacility', 'facilityType', 'bpjsFacilityCode'],
    emergency: ['patientId', 'patientName', 'diagnosis', 'destinationFacility', 'referralReason', 'vitalSigns'],
    control: ['patientId', 'patientName', 'diagnosis', 'controlDate', 'referralReason'],
    specialist: ['patientId', 'patientName', 'diagnosis', 'specialistCategory', 'referralReason'],
  } as Record<ReferralType, string[]>,

  // BPJS specific required fields
  bpjsRequiredFields: [
    'bpjsNumber',
    'bpjsFacilityCode',
    'diagnosisCode',
    'referralNumber',
    'referralDate',
  ],

  // Field validation patterns
  patterns: {
    bpjsNumber: /^[0-9]{13}$/, // 13 digits for BPJS number
    referralNumber: /^[0-9]{10,20}$/, // 10-20 digits for referral number
    facilityCode: /^[0-9]{5,10}$/, // 5-10 digits for facility code
    diagnosisCode: /^[A-Z][0-9][A-Z0-9](\.[A-Z0-9])?$/, // ICD-10 code pattern
  },

  // Maximum lengths
  maxLengths: {
    referralReason: 1000,
    clinicalNotes: 2000,
    treatmentSummary: 2000,
    additionalInfo: 500,
  },
};

// ===============================
// BPJS Integration Rules
// ===============================

export const BPJS_INTEGRATION_RULES = {
  // Required fields for BPJS referrals
  requiredFields: [
    'noKartu', // BPJS card number
    'kodeFaskes', // Facility code
    'diagnosa', // Diagnosis code (ICD-10)
    'noRujukan', // Referral number
    'tglRujukan', // Referral date
  ],

  // BPJS diagnosis categories
  diagnosisCategories: [
    { code: '1', description: 'Infeksi dan parasit' },
    { code: '2', description: 'Tumor neoplasma' },
    { code: '3', description: 'Penyakit darah' },
    { code: '4', description: 'Penyakit endokrin' },
    { code: '5', description: 'Gangguan mental' },
    { code: '6', description: 'Penyakit saraf' },
    { code: '7', description: 'Penyakit mata' },
    { code: '8', description: 'Penyakit THT' },
    { code: '9', description: 'Penyakit sirkulasi' },
    { code: '10', description: 'Penyakit napas' },
    { code: '11', description: 'Penyakit pencernaan' },
    { code: '12', description: 'Penyakit kulit' },
    { code: '13', description: 'Penyakit tulang' },
    { code: '14', description: 'Penyakit genitourinaria' },
    { code: '15', description: 'Kehamilan' },
    { code: '16', description: 'Kelahiran' },
    { code: '17', description: 'Penyakit perinatal' },
    { code: '18', description: 'Kelainan kongenital' },
  ],

  // BPJS facility tiers
  facilityTiers: [
    { code: '1', description: 'Faskes Tingkat 1 (Puskesmas/Klinik Pratama)' },
    { code: '2', description: 'Faskes Tingkat 2 (RS)' },
  ],

  // BPJS referral types
  referralTypes: [
    { code: '1', description: 'Rujukan Internal' },
    { code: '2', description: 'Rujukan Eksternal' },
  ],
};

// ===============================
// Referral Template Configurations
// ===============================

export const REFERRAL_TEMPLATE_CONFIG = {
  // Standard Indonesian referral format
  format: {
    header: {
      title: 'SURAT RUJUKAN',
      hospitalName: 'Nama Rumah Sakit',
      address: 'Alamat Rumah Sakit',
      phoneNumber: 'Telepon',
      logoUrl: '/assets/hospital-logo.png',
    },
    sections: [
      'patientInfo',
      'referralInfo',
      'clinicalInfo',
      'reasonForReferral',
      'providerInfo',
    ],
    footer: {
      stampArea: true,
      signatures: ['doctorSignature', 'hospitalStamp'],
    },
  },

  // Print layout settings
  printLayout: {
    pageSize: 'A4' as const,
    margins: {
      top: '20mm',
      bottom: '20mm',
      left: '20mm',
      right: '20mm',
    },
    fontSize: 12,
    lineHeight: 1.5,
    fontFamily: 'Arial, sans-serif',
  },

  // Label translations
  labels: {
    // Patient Information
    patientInfo: 'INFORMASI PASIEN',
    patientName: 'Nama Pasien',
    patientId: 'No. Rekam Medis',
    dateOfBirth: 'Tanggal Lahir',
    gender: 'Jenis Kelamin',
    address: 'Alamat',
    phoneNumber: 'No. Telepon',

    // Referral Information
    referralInfo: 'INFORMASI RUJUKAN',
    referralNumber: 'Nomor Rujukan',
    referralDate: 'Tanggal Rujukan',
    referralType: 'Jenis Rujukan',
    referralPriority: 'Prioritas',
    destinationFacility: 'Fasilitas Tujuan',
    facilityType: 'Jenis Fasilitas',
    specialistCategory: 'Spesialis Tujuan',

    // Clinical Information
    clinicalInfo: 'INFORMASI KLINIS',
    diagnosis: 'Diagnosis',
    diagnosisCode: 'Kode Diagnosis (ICD-10)',
    chiefComplaint: 'Keluhan Utama',
    vitalSigns: 'Tanda Vital',
    physicalExamination: 'Pemeriksaan Fisik',
    laboratoryResults: 'Hasil Laboratorium',
    radiologyResults: 'Hasil Radiologi',
    treatmentSummary: 'Ringkasan Pengobatan',

    // Referral Reason
    reasonForReferral: 'ALASAN RUJUKAN',
    referralReason: 'Alasan Rujukan',
    specialInstructions: 'Instruksi Khusus',
    followupPlan: 'Rencana Tindak Lanjut',

    // Provider Information
    providerInfo: 'INFORMASI DOKTER',
    doctorName: 'Nama Dokter',
    doctorLicense: 'No. SIP',
    doctorSpecialization: 'Spesialisasi',
    referralDate2: 'Tanggal Rujukan',

    // BPJS Information
    bpjsInfo: 'INFORMASI BPJS',
    bpjsNumber: 'No. Kartu BPJS',
    bpjsFacilityCode: 'Kode Faskes BPJS',

    // Signatures
    doctorSignature: 'Dokter Perujuk',
    medicalRecord: 'Rekam Medis',
    signature: 'Tanda Tangan',
    stamp: 'Stempel',
  },

  // Gender labels
  genderLabels: {
    male: 'Laki-laki',
    female: 'Perempuan',
    other: 'Lainnya',
  },

  // Urgency labels
  urgencyLabels: {
    routine: 'Biasa',
    urgent: 'Segera',
    emergency: 'Gawat Darurat',
  },
};

// ===============================
// Form Field Labels
// ===============================

export const REFERRAL_FORM_LABELS = {
  // Patient Section
  patientSection: 'Informasi Pasien',
  selectPatient: 'Pilih Pasien',
  patientName: 'Nama Lengkap',
  patientId: 'No. Rekam Medis',
  dateOfBirth: 'Tanggal Lahir',
  age: 'Usia',
  gender: 'Jenis Kelamin',
  phoneNumber: 'No. Telepon',
  address: 'Alamat',
  bpjsNumber: 'Nomor Kartu BPJS',

  // Referral Section
  referralSection: 'Informasi Rujukan',
  referralType: 'Jenis Rujukan',
  referralPriority: 'Prioritas',
  referralDate: 'Tanggal Rujukan',
  controlDate: 'Tanggal Kontrol',
  destinationFacility: 'Fasilitas Kesehatan Tujuan',
  facilityType: 'Jenis Fasilitas',
  specialistCategory: 'Kategori Spesialis',
  bpjsFacilityCode: 'Kode Faskes BPJS',

  // Clinical Section
  clinicalSection: 'Informasi Klinis',
  diagnosis: 'Diagnosis Utama',
  diagnosisCode: 'Kode Diagnosis (ICD-10)',
  secondaryDiagnosis: 'Diagnosis Sekunder',
  chiefComplaint: 'Keluhan Utama',
  vitalSigns: 'Tanda Vital',
  physicalExamination: 'Pemeriksaan Fisik',
  laboratoryResults: 'Hasil Pemeriksaan Penunjang',
  treatmentSummary: 'Ringkasan Pengobatan',

  // Reason Section
  reasonSection: 'Alasan Rujukan',
  referralReason: 'Alasan Rujukan',
  specialInstructions: 'Instruksi Khusus',

  // Provider Section
  providerSection: 'Informasi Dokter',
  referringDoctor: 'Dokter Perujuk',
  doctorDepartment: 'Poliklinik/Unit',
};

// ===============================
// Error Messages
// ===============================

export const REFERRAL_ERROR_MESSAGES = {
  required: 'Kolom ini wajib diisi',
  invalidBPJSNumber: 'Nomor BPJS harus 13 digit angka',
  invalidDiagnosisCode: 'Format kode diagnosis tidak valid (ICD-10)',
  maxLength: 'Maksimal {maxLength} karakter',
  invalidDate: 'Format tanggal tidak valid',
  futureDate: 'Tanggal tidak boleh di masa depan',
  invalidPhone: 'Format nomor telepon tidak valid',
};
