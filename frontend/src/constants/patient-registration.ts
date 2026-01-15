/**
 * Patient Registration Form Constants
 * Contains all dropdown options, validation rules, and constants for patient registration
 */

// Gender Options
export const GENDER_OPTIONS = [
  { value: 'male', label: 'Laki-laki' },
  { value: 'female', label: 'Perempuan' },
] as const;

// Marital Status Options
export const MARITAL_STATUS_OPTIONS = [
  { value: 'single', label: 'Belum Menikah' },
  { value: 'married', label: 'Menikah' },
  { value: 'widowed', label: 'Janda/Duda' },
  { value: 'divorced', label: 'Cerai' },
] as const;

// Religion Options (Indonesia)
export const RELIGION_OPTIONS = [
  { value: 'islam', label: 'Islam' },
  { value: 'kristen', label: 'Kristen' },
  { value: 'katolik', label: 'Katolik' },
  { value: 'hindu', label: 'Hindu' },
  { value: 'buddha', label: 'Buddha' },
  { value: 'konghucu', label: 'Konghucu' },
  { value: 'lainnya', label: 'Lainnya' },
] as const;

// Blood Type Options
export const BLOOD_TYPE_OPTIONS = [
  { value: 'A', label: 'A' },
  { value: 'B', label: 'B' },
  { value: 'AB', label: 'AB' },
  { value: 'O', label: 'O' },
  { value: 'A+', label: 'A+' },
  { value: 'A-', label: 'A-' },
  { value: 'B+', label: 'B+' },
  { value: 'B-', label: 'B-' },
  { value: 'AB+', label: 'AB+' },
  { value: 'AB-', label: 'AB-' },
  { value: 'O+', label: 'O+' },
  { value: 'O-', label: 'O-' },
  { value: 'unknown', label: 'Tidak Tahu' },
] as const;

// Education Level Options
export const EDUCATION_LEVEL_OPTIONS = [
  { value: 'none', label: 'Tidak Sekolah' },
  { value: 'sd', label: 'SD' },
  { value: 'smp', label: 'SMP' },
  { value: 'sma_smk', label: 'SMA/SMK' },
  { value: 'd3', label: 'D3' },
  { value: 's1', label: 'S1' },
  { value: 's2', label: 'S2' },
  { value: 's3', label: 'S3' },
] as const;

// Occupation Categories (Indonesia)
export const OCCUPATION_OPTIONS = [
  { value: 'pns', label: 'PNS' },
  { value: 'tni_polri', label: 'TNI/Polri' },
  { value: 'swasta', label: 'Swasta' },
  { value: 'wiraswasta', label: 'Wiraswasta' },
  { value: 'petani', label: 'Petani' },
  { value: 'nelayan', label: 'Nelayan' },
  { value: 'buruh', label: 'Buruh' },
  { value: 'ibu_rumah_tangga', label: 'Ibu Rumah Tangga' },
  { value: 'pelajar_mahasiswa', label: 'Pelajar/Mahasiswa' },
  { value: 'lainnya', label: 'Lainnya' },
] as const;

// BPJS Class Options
export const BPJS_CLASS_OPTIONS = [
  { value: '1', label: 'Kelas 1' },
  { value: '2', label: 'Kelas 2' },
  { value: '3', label: 'Kelas 3' },
] as const;

// Insurance Type Options
export const INSURANCE_TYPE_OPTIONS = [
  { value: 'inpatient', label: 'Rawat Inap' },
  { value: 'outpatient', label: 'Rawat Jalan' },
  { value: 'both', label: 'Keduanya' },
] as const;

// Relationship Options (for Emergency Contact)
export const RELATIONSHIP_OPTIONS = [
  { value: 'spouse', label: 'Suami/Istri' },
  { value: 'parent', label: 'Orang Tua' },
  { value: 'sibling', label: 'Saudara' },
  { value: 'child', label: 'Anak' },
  { value: 'friend', label: 'Teman' },
  { value: 'other', label: 'Lainnya' },
] as const;

// Validation Rules
export const VALIDATION_RULES = {
  // NIK (Nomor Induk Kependudukan) validation
  NIK: {
    LENGTH: 16,
    PATTERN: /^[0-9]{16}$/,
    ERROR_MESSAGE: 'NIK harus 16 digit angka',
  },

  // Phone number validation (Indonesian format)
  PHONE: {
    PATTERN: /^(\+62|62|0)[0-9]{9,13}$/,
    ERROR_MESSAGE: 'Nomor telepon tidak valid. Gunakan format: +62xxx atau 0xxx',
    EXAMPLES: ['+6281234567890', '081234567890', '6281234567890'],
  },

  // Email validation
  EMAIL: {
    PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    ERROR_MESSAGE: 'Alamat email tidak valid',
  },

  // Postal code validation (Indonesia)
  POSTAL_CODE: {
    LENGTH: 5,
    PATTERN: /^[0-9]{5}$/,
    ERROR_MESSAGE: 'Kode pos harus 5 digit angka',
  },
} as const;

// Required Fields for Patient Registration
export const REQUIRED_FIELDS = [
  'nik',
  'name',
  'gender',
  'birthDate',
  'birthPlace',
  'maritalStatus',
  'religion',
  'bloodType',
  'education',
  'occupation',
  'address',
  'province',
  'city',
  'district',
  'village',
  'postalCode',
  'phoneNumber',
] as const;

// Required Fields for BPJS Information
export const BPJS_REQUIRED_FIELDS = [
  'bpjsNumber',
  'bpjsClass',
  'insuranceType',
] as const;

// Required Fields for Emergency Contact
export const EMERGENCY_CONTACT_REQUIRED_FIELDS = [
  'emergencyName',
  'emergencyRelationship',
  'emergencyPhone',
] as const;

// Field Labels (Indonesian)
export const FIELD_LABELS = {
  // Personal Information
  nik: 'NIK (Nomor Induk Kependudukan)',
  name: 'Nama Lengkap',
  gender: 'Jenis Kelamin',
  birthDate: 'Tanggal Lahir',
  birthPlace: 'Tempat Lahir',
  maritalStatus: 'Status Perkawinan',
  religion: 'Agama',
  bloodType: 'Golongan Darah',
  education: 'Pendidikan Terakhir',
  occupation: 'Pekerjaan',

  // Address Information
  address: 'Alamat Lengkap',
  province: 'Provinsi',
  city: 'Kabupaten/Kota',
  district: 'Kecamatan',
  village: 'Kelurahan/Desa',
  postalCode: 'Kode Pos',
  phoneNumber: 'Nomor Telepon',
  email: 'Alamat Email',

  // BPJS Information
  bpjsNumber: 'Nomor BPJS',
  bpjsClass: 'Kelas BPJS',
  insuranceType: 'Jenis Asuransi',

  // Emergency Contact
  emergencyName: 'Nama Kontak Darurat',
  emergencyRelationship: 'Hubungan dengan Pasien',
  emergencyPhone: 'Nomor Telepon Kontak Darurat',
  emergencyAddress: 'Alamat Kontak Darurat',
} as const;

// Type exports for TypeScript
export type GenderOption = typeof GENDER_OPTIONS[number]['value'];
export type MaritalStatusOption = typeof MARITAL_STATUS_OPTIONS[number]['value'];
export type ReligionOption = typeof RELIGION_OPTIONS[number]['value'];
export type BloodTypeOption = typeof BLOOD_TYPE_OPTIONS[number]['value'];
export type EducationLevelOption = typeof EDUCATION_LEVEL_OPTIONS[number]['value'];
export type OccupationOption = typeof OCCUPATION_OPTIONS[number]['value'];
export type BPJSClassOption = typeof BPJS_CLASS_OPTIONS[number]['value'];
export type InsuranceTypeOption = typeof INSURANCE_TYPE_OPTIONS[number]['value'];
export type RelationshipOption = typeof RELATIONSHIP_OPTIONS[number]['value'];
