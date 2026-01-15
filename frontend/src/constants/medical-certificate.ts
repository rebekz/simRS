/**
 * Medical Certificate Constants
 * Constants untuk Form Surat Keterangan Medis
 * All labels in Indonesian language
 */

// ==================== CERTIFICATE TYPES ====================
export const CERTIFICATE_TYPES = {
  SICK_LEAVE: 'sick_leave',
  MEDICAL_FITNESS: 'medical_fitness',
  FIT_FOR_WORK: 'fit_for_work',
  PREGNANCY: 'pregnancy',
  HEALTHY_CHILD: 'healthy_child',
  DEATH_CERTIFICATE: 'death_certificate',
  MEDICAL_REPORT: 'medical_report',
} as const;

export const CERTIFICATE_TYPE_OPTIONS = [
  {
    value: CERTIFICATE_TYPES.SICK_LEAVE,
    label: 'Surat Sakit',
    description: 'Surat keterangan istirahat karena sakit',
    icon: '🏥',
  },
  {
    value: CERTIFICATE_TYPES.MEDICAL_FITNESS,
    label: 'Surat Keterangan Sehat',
    description: 'Surat keterangan kesehatan umum',
    icon: '✓',
  },
  {
    value: CERTIFICATE_TYPES.FIT_FOR_WORK,
    label: 'Surat Keterangan Fit untuk Bekerja',
    description: 'Surat keterangan fit bekerja',
    icon: '💼',
  },
  {
    value: CERTIFICATE_TYPES.PREGNANCY,
    label: 'Surat Keterangan Hamil',
    description: 'Surat keterangan kehamilan',
    icon: '🤰',
  },
  {
    value: CERTIFICATE_TYPES.HEALTHY_CHILD,
    label: 'Surat Keterangan Anak Sehat',
    description: 'Surat keterangan kesehatan anak',
    icon: '👶',
  },
  {
    value: CERTIFICATE_TYPES.DEATH_CERTIFICATE,
    label: 'Surat Keterangan Kematian',
    description: 'Surat keterangan kematian',
    icon: '🕯️',
  },
  {
    value: CERTIFICATE_TYPES.MEDICAL_REPORT,
    label: 'Surat Keterangan Medis',
    description: 'Laporan medis umum',
    icon: '📋',
  },
] as const;

// ==================== DURATION OPTIONS ====================
export const DURATION_DAYS = [1, 2, 3, 7, 14, 30] as const;

export const DURATION_OPTIONS = [
  { value: 1, label: '1 Hari' },
  { value: 2, label: '2 Hari' },
  { value: 3, label: '3 Hari' },
  { value: 7, label: '7 Hari' },
  { value: 14, label: '14 Hari' },
  { value: 30, label: '30 Hari' },
  { value: 'custom', label: 'Durasi Khusus' },
] as const;

// ==================== ICD-10 CODE CATEGORIES ====================
export const ICD10_CATEGORIES = [
  {
    code: 'A00-B99',
    description: 'Penyakit Menular',
    subcategories: [
      'A00-A09: Penyakit Infeksi Usus',
      'A15-A19: Tuberkulosis',
      'A20-A28: Penyakit Zoonotik Bakteri',
      'A30-A49: Penyakit Bakteri Lain',
      'A50-A64: Infeksi Menular Seksual',
      'A65-A79: Spirochetosis',
      'A80-A89: Infeksi Virus CNS',
      'A90-A99: Demam Arbovirus',
      'B00-B09: Infeksi Virus Kulit & Mukosa',
      'B15-B19: Hepatitis Virus',
      'B20-B24: Penyakit HIV',
      'B25-B34: Virus Lain',
      'B35-B49: Mikosis',
      'B50-B64: Penyakit Protozoa',
      'B65-B83: Helmintiasis',
      'B85-B89: Pedikulosis & Penyakit Akibat Artropoda',
      'B90-B94: Sekuela penyakit menular',
      'B95-B97: Bakteri, virus, dan protozoa penyebab',
      'B99: Penyakit menular lain',
    ],
  },
  {
    code: 'C00-D48',
    description: 'Neoplasma (Tumor)',
    subcategories: [
      'C00-C14: Neoplasma Ganas Bibir, Rongga Mulut & Farinks',
      'C15-C26: Neoplasma Ganas Organ Pencernaan',
      'C30-C39: Neoplasma Ganas Pernapasan & Intrathorak',
      'C40-C41: Neoplasma Ganas Tulang & Sendi',
      'C43-C44: Neoplasma Ganas Kulit',
      'C45-C49: Neoplasma Ganas Jaringan Ikat',
      'C50-C58: Neoplasma Ganas Organ Genitalia Wanita',
      'C60-C63: Neoplasma Ganas Organ Genitalia Pria',
      'C64-C68: Neoplasma Ganas Organ Urinarius',
      'C69-C72: Neoplasma Ganas Mata, Otak & CNS',
      'C73-C75: Neoplasma Ganas Kelenjar Endokrin',
      'C76-C80: Neoplasma Ganas Lokasi Sekunder & Tidak Ditentukan',
      'C81-C96: Penyakit Limfoid & Hematopoietik',
      'C97: Neoplasma Ganas Multipel',
      'D00-D09: Neoplasma In Situ',
      'D10-D36: Neoplasma Jinak',
      'D37-D48: Neoplasma Perilaku Tidak Pasti',
    ],
  },
  {
    code: 'D50-D89',
    description: 'Penyakit Darah & Organ Pembentuk Darah',
    subcategories: [
      'D50-D53: Anemia Gizi',
      'D55-D59: Anemia Hemolitik',
      'D60-D64: Aplastik & Anemia Lain',
      'D65-D69: Gangguan Pembekuan Darah',
      'D70-D77: Penyakit Sel Darah Putih',
      'D80-D89: Penyakit Kekebalan',
    ],
  },
  {
    code: 'E00-E90',
    description: 'Penyakit Endokrin, Gizi & Metabolik',
    subcategories: [
      'E00-E07: Gangguan Tiroid',
      'E10-E14: Diabetes Mellitus',
      'E15-E16: Hipoglikemia',
      'E20-E35: Gangguan Kelenjar Lain',
      'E40-E46: Malnutrisi Energi-Protein',
      'E50-E64: Defisiensi Vitamin Lain',
      'E65-E68: Obesitas & Kelebihan Nutrisi',
      'E70-E90: Gangguan Metabolik Lain',
    ],
  },
  {
    code: 'F00-F99',
    description: 'Gangguan Mental & Perilaku',
    subcategories: [
      'F00-F09: Organik, termasuk Simtomatik',
      'F10-F19: Gangguan Penggunaan Zat Psikoaktif',
      'F20-F29: Skizofrenia & Psikotik Lain',
      'F30-F39: Gangguan Mood',
      'F40-F48: Gangguan Neurotik & Stres',
      'F50-F59: Sindrom Perilaku Terkait Fisiologis',
      'F60-F69: Gangguan Kepribadian',
      'F70-F79: Retardasi Mental',
      'F80-F89: Gangguan Perkembangan',
      'F90-F98: Gangguan Emosi & Perilaku Childhood',
      'F99: Gangguan mental lain',
    ],
  },
  {
    code: 'G00-H95',
    description: 'Penyakit Sistem Saraf & Indra',
    subcategories: [
      'G00-G09: Penyakit Inflamasi CNS',
      'G10-G14: Gangguan Degeneratif CNS',
      'G20-G26: Ekstrapiramidal & Gangguan Gerak',
      'G30-G32: Penyakit Degeneratif CNS Lain',
      'G35-G37: Penyakit Demyelinating',
      'G40-G47: Gangguan Episodik & Paroksismal',
      'G50-G59: Gangguan Saraf, Akar & Pleksus',
      'G60-G64: Polineuropati & Gangguan Lain',
      'G70-G73: Gangguan Myoneural & Muskular',
      'G80-G83: Serebral Palsy & Sindrom Paralitik',
      'G90-G99: Penyakit Lain Sistem Saraf',
      'H00-H06: Penyakit Kelopak Mata, Lakrimal & Orbita',
      'H10-H13: Penyakit Konjunktiva',
      'H15-H22: Penyakit Sklera, Kornea, Iris & Badan Siliaris',
      'H25-H28: Lensa',
      'H30-H36: Koroid & Retina',
      'H40-H42: Glaukoma',
      'H43-H45: Vitreus & Globe',
      'H46-H48: Saraf Optik & Jalur Visual',
      'H49-H52: Gangguan Otot Mata, Binokular & Akomodasi',
      'H53-H54: Gangguan Penglihatan',
      'H55-H59: Penyakit Mata & Adneksa Lain',
      'H60-H62: Penyakit Telinga Luar',
      'H65-H75: Penyakit Telinga Tengah & Mastoid',
      'H80-H83: Penyakit Telinga Dalam',
      'H90-H95: Gangguan Pendengaran',
    ],
  },
  {
    code: 'I00-I99',
    description: 'Penyakit Sistem Sirkulasi',
    subcategories: [
      'I00-I02: Demam Rematik Akut',
      'I05-I09: Penyakit Jantung Rematik Kronis',
      'I10-I15: Penyakit Hipertensif',
      'I20-I25: Penyakit Jantung Iskemik',
      'I26-I28: Penyakit Vaskuler Paru',
      'I30-I52: Penyakit Jantung Lain',
      'I60-I69: Penyakit Serebrovaskular',
      'I70-I79: Penyakit Arteri, Arterioli & Kapiler',
      'I80-I89: Penyakit Vena & Pembuluh Limfatik',
      'I90-I99: Penyakit Sirkulasi Lain',
    ],
  },
  {
    code: 'J00-J99',
    description: 'Penyakit Sistem Pernapasan',
    subcategories: [
      'J00-J06: Infeksi Saluran Pernapasan Atas',
      'J09-J18: Influenza & Pneumonia',
      'J20-J22: Bronkitis Akut Lain',
      'J30-J39: Penyakit Saluran Pernapasan Atas Lain',
      'J40-J47: Penyakit Saluran Pernapasan Bawah Kronis',
      'J60-J70: Penyakit Paru Karena Agen Eksternal',
      'J80-J84: Penyakit Paru Lain',
      'J85-J86: Supurasi & Necrosis Paru',
      'J90-J94: Penyakit Pleura',
      'J95-J99: Penyakit Pernapasan Lain',
    ],
  },
  {
    code: 'K00-K93',
    description: 'Penyakit Sistem Pencernaan',
    subcategories: [
      'K00-K14: Penyakit Rongga Mulut, Kelenjar Ludah & Rahang',
      'K20-K31: Penyakit Esophagus, Lambung & Duodenum',
      'K35-K38: Penyakit Apendiks',
      'K40-K46: Hernia',
      'K50-K52: Enteritis & Kolitis Noninfektif',
      'K55-K63: Penyakit Usus Lain',
      'K65-K67: Penyakit Peritoneum',
      'K70-K77: Penyakit Hati',
      'K80-K87: Penyakit Kandung Empedu & Bilier',
      'K90-K93: Penyakit Pencernaan Lain',
    ],
  },
  {
    code: 'L00-L99',
    description: 'Penyakit Kulit & Jaringan Subkutan',
    subcategories: [
      'L00-L08: Infeksi Kulit & Subkutan',
      'L10-L14: Bulosa Dermatoses',
      'L20-L30: Dermatitis & Eksim',
      'L40-L45: Papuloskuamosa',
      'L50-L54: Urtikaria & Eritema',
      'L55-L59: Penyakit Terkait Radiasi',
      'L60-L75: Penyakit Kuku & Appendages',
      'L80-L99: Penyakit Kulit Lain',
    ],
  },
  {
    code: 'M00-M99',
    description: 'Penyakit Sistem Muskuloskeletal & Jaringan Ikat',
    subcategories: [
      'M00-M03: Infeksi Artropati',
      'M05-M14: Arthropati Inflamatori',
      'M15-M19: Osteoartritis',
      'M20-M25: Penyakit Sendi Lain',
      'M30-M36: Gangguan Jaringan Ikat Sistemik',
      'M40-M54: Dorsopathi',
      'M60-M63: Gangguan Otot',
      'M65-M68: Gangguan Sinovium & Ligamen',
      'M70-M79: Gangguan Jaringan Lunak',
      'M80-M85: Osteopati & Kondisi Tulang',
      'M86-M90: Osteomielitis',
      'M91-M94: Osteochondropati',
      'M95-M99: Gangguan Muskuloskeletal Lain',
    ],
  },
  {
    code: 'N00-N99',
    description: 'Penyakit Sistem Genitourinari',
    subcategories: [
      'N00-N08: Glomerular',
      'N10-N19: Penyakit Ginjal Tubulointerstitial',
      'N20-N23: Urolithiasis',
      'N25-N29: Gangguan Ginjal & Ureter Lain',
      'N30-N39: Penyakit Organ Urinarius Lain',
      'N40-N51: Penyakit Organ Genitalia Pria',
      'N60-N64: Gangguan Payudara',
      'N70-N77: Penyakit Organ Genitalia Wanita',
      'N80-N98: Gangguan Genitalia Wanita Lain',
      'N99: Gangguan Genitourinari Lain',
    ],
  },
  {
    code: 'O00-O99',
    description: 'Kehamilan, Persalinan & Nifas',
    subcategories: [
      'O00-O08: Kehamilan Ektopik',
      'O10-O16: Edema, Proteinuria & Hipertensif Kehamilan',
      'O20-O29: Komplikasi Kehamilan Lain',
      'O30-O48: Perawatan Kehamilan',
      'O60-O64: Komplikasi Persalinan',
      'O65-O71: Komplikasi Persalinan & Penyerahan',
      'O75-O79: Komplikasi Persalinan & Nifas Lain',
      'O80-O84: Penyerahan',
      'O85-O92: Komplikasi Nifas',
      'O94-O99: Komplikasi Obstetrik Lain',
    ],
  },
  {
    code: 'P00-P96',
    description: 'Kondisi Asal Perinatal',
    subcategories: [
      'P00-P04: Kondisi Fetus & Newborn Terkait Ibu',
      'P05-P08: Gangguan Terkait Kehamilan Berat & Durasi',
      'P09-P09: Trauma Kelahiran',
      'P10-P15: Trauma Birth CNS',
      'P20-P29: Gangguan Pernapasan & Kardiovaskular Perinatal',
      'P35-P39: Infeksi Spesifik Perinatal',
      'P50-P61: Gangguan Hemoragik & Hematologis Fetus',
      'P70-P74: Gangguan Endokrin & Metabolik Transitori',
      'P75-P78: Gangguan Sistem Pencernaan Fetus',
      'P80-P83: Kondisi Terkati Integumen Fetus',
      'P90-P96: Gangguan Lain Perinatal',
    ],
  },
  {
    code: 'Q00-Q99',
    description: 'Malformasi Kongenital',
    subcategories: [
      'Q00-Q07: Malformasi CNS',
      'Q10-Q18: Malformasi Mata, Telinga, & Wajah',
      'Q20-Q28: Malformasi Sirkulasi',
      'Q30-Q34: Malformasi Pernapasan',
      'Q35-Q37: Celah Bibir & Langit-langit',
      'Q38-Q45: Malformasi Pencernaan Lain',
      'Q50-Q56: Malformasi Genitalia',
      'Q60-Q64: Malformasi Urinarius',
      'Q65-Q79: Malformasi Muskuloskeletal',
      'Q80-Q89: Malformasi Lain',
      'Q90-Q99: Anomali Kromosom',
    ],
  },
  {
    code: 'R00-R99',
    description: 'Gejala, Tanda & Hasil Lab Abnormal',
    subcategories: [
      'R00-R09: Gejala Sirkulasi & Pernapasan',
      'R10-R19: Gejala Pencernaan & Abdomen',
      'R20-R23: Gejala Kulit & Jaringan Subkutan',
      'R25-R29: Gejala Sistem Saraf & Muskuloskeletal',
      'R30-R39: Gejala Urinarius',
      'R40-R46: Gejala Kognitif, Persepsi, Emosi & Perilaku',
      'R47-R49: Gejala Bicara & Suara',
      'R50-R69: Gejala Umum Lain',
      'R70-R79: Hasil Lab Abnormal',
      'R80-R82: Hasil Urinalisis Abnormal',
      'R83-R89: Hasil Cairan Tubuh Lain Abnormal',
      'R90-R94: Hasil Diagnostik Imaging Abnormal',
      'R95-R99: Kematian Tak Terduga & Tak Dijelaskan',
    ],
  },
  {
    code: 'S00-T98',
    description: 'Cedera, Keracunan & Konsekuensi Eksternal',
    subcategories: [
      'S00-S09: Cedera Kepala',
      'S10-S19: Cedera Leher',
      'S20-S29: Cedera Toraks',
      'S30-S39: Cedera Abdomen, Lumbar & Panggul',
      'S40-S49: Cedera Bahu & Lengan Atas',
      'S50-S59: Cedera Siku & Lengan Bawah',
      'S60-S69: Cedera Pergelangan Tangan & Tangan',
      'S70-S79: Cedera Pinggul & Paha',
      'S80-S89: Cedera Lutum & Kaki Bawah',
      'S90-S99: Cedera Pergelelangan Kaki & Kaki',
      'T00-T07: Cedera Multipel',
      'T08-T14: Cedera Lokasi Tak Ditentukan',
      'T15-T19: Efek Benda Asing',
      'T20-T32: Luka Bakar & Korosi',
      'T33-T35: Frostbite',
      'T36-T50: Keracunan Obat & Obat Biologi',
      'T51-T65: Efek Toksik Zat Nonmedis',
      'T66-T78: Efek Lain & Tak Ditentukan',
      'T79: Komplikasi Awal Cedera',
      'T80-T88: Komplikasi Perawatan Bedah & Medis Lain',
      'T90-T98: Sekuela Cedera',
    ],
  },
  {
    code: 'V01-Y98',
    description: 'Penyebab Eksternal Morbiditas & Mortalitas',
    subcategories: [
      'V01-V99: Kecelakaan Transportasi',
      'W00-W19: Jatuh',
      'W20-W49: Cedera Akibat Kontak Mekanis',
      'W50-W64: Cedera Akibat Kontak Mekanis Lain',
      'W65-W74: Cedera Akibat Tenggelam',
      'W75-W84: Cedera Akibat Respirasi Lain',
      'W85-W99: Cedera Akibat Arus Listrik',
      'X00-X09: Paparan Api & Asap',
      'X10-X19: Kontak Dengan Panas & Zat Panas',
      'X20-X29: Kontak Dengan Hewan & Tanaman Beracun',
      'X30-X39: Paparan Gaya Alam Lain',
      'X40-X49: Keracunan Tak Sengaja',
      'X50-X57: Overexertion & Perjalanan',
      'X58-X59: Cedera Tak Sengaja Lain',
      'X60-X84: Bunuh Diri Intensional',
      'X85-Y09: Assult',
      'Y10-Y34: Peristiwa Tak Ditentukan',
      'Y35-Y36: Intervensi Hukum & Operasi Perang',
      'Y40-Y84: Komplikasi Perawatan Medis & Bedah',
      'Y85-Y89: Sekuela Penyebab Eksternal',
      'Y90-Y98: Faktor Tambahan',
    ],
  },
  {
    code: 'Z00-Z99',
    description: 'Faktor Mempengaruhi Status Kesehatan',
    subcategories: [
      'Z00-Z13: Kontak Dengan Layanan Kesehatan untuk Pemeriksaan',
      'Z14-Z99: Kontak Dengan Layanan Kesehatan untuk Lainnya',
    ],
  },
] as const;

// ==================== VALIDATION RULES ====================
export const VALIDATION_RULES = {
  // Duration validation
  MAX_DURATION_DAYS: {
    DEFAULT: 30,
    SICK_LEAVE: 14,
    SICK_LEAVE_WITH_APPROVAL: 30,
    PREGNANCY: 90,
  },

  // Date validation
  DATE_VALIDATION: {
    MAX_CERTIFICATE_DAYS_IN_PAST: 7, // Maximum days in past for certificate date
    MAX_FUTURE_DAYS: 0, // Certificates cannot be future dated
    MIN_DURATION_DAYS: 1,
    MAX_DURATION_CUSTOM: 180, // For custom duration
  },

  // Required fields per certificate type
  REQUIRED_FIELDS: {
    [CERTIFICATE_TYPES.SICK_LEAVE]: [
      'patientName',
      'patientNIK',
      'diagnosis',
      'icd10Code',
      'duration',
      'startDate',
      'doctorName',
      'doctor SIP',
      'medicalFacility',
    ],
    [CERTIFICATE_TYPES.MEDICAL_FITNESS]: [
      'patientName',
      'patientNIK',
      'examinationDate',
      'healthStatus',
      'doctorName',
      'doctorSIP',
      'medicalFacility',
    ],
    [CERTIFICATE_TYPES.FIT_FOR_WORK]: [
      'patientName',
      'patientNIK',
      'examinationDate',
      'workCapability',
      'restrictions',
      'doctorName',
      'doctorSIP',
      'medicalFacility',
    ],
    [CERTIFICATE_TYPES.PREGNANCY]: [
      'patientName',
      'patientNIK',
      'pregnancyAge',
      'estimatedDeliveryDate',
      'examinationDate',
      'doctorName',
      'doctorSIP',
      'medicalFacility',
    ],
    [CERTIFICATE_TYPES.HEALTHY_CHILD]: [
      'childName',
      'childNIK',
      'birthDate',
      'examinationDate',
      'healthStatus',
      'doctorName',
      'doctorSIP',
      'medicalFacility',
    ],
    [CERTIFICATE_TYPES.DEATH_CERTIFICATE]: [
      'deceasedName',
      'deceasedNIK',
      'deathDate',
      'deathTime',
      'causeOfDeath',
      'placeOfDeath',
      'doctorName',
      'doctorSIP',
      'medicalFacility',
    ],
    [CERTIFICATE_TYPES.MEDICAL_REPORT]: [
      'patientName',
      'patientNIK',
      'reportDate',
      'findings',
      'doctorName',
      'doctorSIP',
      'medicalFacility',
    ],
  },

  // Field-specific validations
  FIELD_VALIDATIONS: {
    NIK_LENGTH: 16,
    NIK_REGEX: /^\d{16}$/,
    PHONE_REGEX: /^(\+62|62|0)[0-9]{9,12}$/,
    DOCTOR_SIP_LENGTH_MIN: 6,
    DOCTOR_SIP_LENGTH_MAX: 20,
  },

  // Business rules
  BUSINESS_RULES: {
    MIN_PATIENT_AGE: 0,
    MAX_PATIENT_AGE: 150,
    MIN_PREGNANCY_WEEKS: 0,
    MAX_PREGNANCY_WEEKS: 42,
    MIN_CHILD_AGE_YEARS: 0,
    MAX_CHILD_AGE_YEARS: 18,
  },
} as const;

// ==================== CERTIFICATE TEMPLATE CONFIGURATIONS ====================
export const CERTIFICATE_TEMPLATES = {
  // Standard Indonesian certificate format
  FORMAT: {
    HEADER: {
      title: 'SURAT KETERANGAN MEDIS',
      showLogo: true,
      showMedicalFacilityName: true,
      showMedicalFacilityAddress: true,
      showMedicalFacilityPhone: true,
    },
    BODY: {
      showPatientInfo: true,
      showMedicalInfo: true,
      showDoctorInfo: true,
      showBarcode: true,
      showQRCode: true,
    },
    FOOTER: {
      showSignature: true,
      showStamp: true,
      showIssueDate: true,
      showCertificateNumber: true,
    },
  },

  // Print layout settings (in pixels for 80mm thermal printer)
  PRINT_LAYOUT: {
    PAGE_WIDTH: 794, // A4 width in pixels at 96 DPI
    PAGE_HEIGHT: 1123, // A4 height in pixels at 96 DPI
    MARGINS: {
      TOP: 40,
      RIGHT: 40,
      BOTTOM: 40,
      LEFT: 40,
    },
    FONT_SIZES: {
      TITLE: 24,
      SUBTITLE: 14,
      BODY: 12,
      FOOTER: 10,
      LABEL: 11,
    },
    LINE_HEIGHT: 1.5,
    SPACING: {
      SECTION_TOP: 20,
      FIELD_ROW: 8,
      LABEL_VALUE: 4,
    },
  },

  // PDF generation options
  PDF_OPTIONS: {
    orientation: 'portrait' as const,
    unit: 'mm' as const,
    format: 'a4' as const,
    compress: true,
    precision: 2,
    fontSize: 12,
    lineHeight: 1.5,
    autoPaging: true,
    printHeaders: false,
    printFooter: false,
  },

  // Certificate numbering format
  CERTIFICATE_NUMBER_FORMAT: {
    PREFIX: 'SKM',
    SEPARATOR: '/',
    DATE_FORMAT: 'YYYYMMDD',
    SEQUENCE_LENGTH: 4,
    EXAMPLE: 'SKM/20250115/0001',
  },

  // Display labels in Indonesian
  LABELS: {
    PATIENT_INFO: 'INFORMASI PASIEN',
    PATIENT_NAME: 'Nama Lengkap',
    PATIENT_NIK: 'NIK',
    PATIENT_DOB: 'Tanggal Lahir',
    PATIENT_AGE: 'Umur',
    PATIENT_GENDER: 'Jenis Kelamin',
    PATIENT_ADDRESS: 'Alamat',
    PATIENT_PHONE: 'No. Telepon',

    MEDICAL_INFO: 'INFORMASI MEDIS',
    CERTIFICATE_TYPE: 'Jenis Surat',
    CERTIFICATE_NUMBER: 'Nomor Surat',
    ISSUE_DATE: 'Tanggal Terbit',
    EXAMINATION_DATE: 'Tanggal Pemeriksaan',
    DIAGNOSIS: 'Diagnosis',
    ICD10_CODE: 'Kode ICD-10',
    DURATION: 'Durasi',
    START_DATE: 'Tanggal Mulai',
    END_DATE: 'Tanggal Selesai',
    NOTES: 'Keterangan Tambahan',

    DOCTOR_INFO: 'INFORMASI DOKTER',
    DOCTOR_NAME: 'Nama Dokter',
    DOCTOR_SIP: 'No. SIP',
    DOCTOR_SPECIALTY: 'Spesialis',
    DOCTOR_SIGNATURE: 'Tanda Tangan',

    MEDICAL_FACILITY: 'FASILITAS KESEHATAN',
    FACILITY_NAME: 'Nama Fasilitas',
    FACILITY_ADDRESS: 'Alamat',
    FACILITY_PHONE: 'No. Telepon',

    CERTIFICATION: 'SERTIFIKASI',
    CERTIFIED_TRUE: 'Demikian surat keterangan ini dibuat dengan sebenarnya untuk dipergunakan sebagaimana mestinya.',

    DAYS_SUFFIX: 'hari',
    MALE: 'Laki-laki',
    FEMALE: 'Perempuan',
    YEARS: 'tahun',
    MONTHS: 'bulan',
    WEEKS: 'minggu',
  },
} as const;

// ==================== BPJS INTEGRATION RULES ====================
export const BPJS_RULES = {
  // BPJS API endpoints
  API: {
    BASE_URL: process.env.REACT_APP_BPJS_API_URL || 'https://api.bpjs-kesehatan.go.id',
    ENDPOINTS: {
      SEP: '/vclaim-rest/SEP',
      RUJUKAN: '/vclaim-rest/Rujukan',
      PESERTA: '/vclaim-rest/Peserta',
      DIAGNOSA: '/vclaim-rest/referensi/diagnosa',
      POLI: '/vclaim-rest/referensi/poli',
      FASKES: '/vclaim-rest/referensi/faskes',
    },
  },

  // Required fields for BPJS claims
  REQUIRED_FIELDS_FOR_CLAIM: {
    [CERTIFICATE_TYPES.SICK_LEAVE]: [
      'bpjsCardNumber',
      'sepNumber',
      'diagnosis',
      'icd10Code',
      'doctorName',
      'doctorSIP',
      'medicalFacilityCode',
      'visitDate',
      'severityLevel',
    ],
  },

  // BPJS sick leave certificate format (Surat Keterangan Istirahat - SKI)
  SICK_LEAVE_FORMAT: {
    REQUIRED_FIELDS: [
      'patientBPJSNumber',
      'sepNumber',
      'diagnosis',
      'icd10Code',
      'restDuration',
      'restStartDate',
      'doctorSIP',
      'medicalFacilityCode',
    ],
    MAX_DURATION_DAYS: 14, // Standard BPJS max without special approval
    EXTENDED_DURATION_DAYS: 30, // With specialist approval
    SEVERITY_LEVELS: [
      { value: 'light', label: 'Ringan', maxDays: 3 },
      { value: 'moderate', label: 'Sedang', maxDays: 7 },
      { value: 'severe', label: 'Berat', maxDays: 14 },
    ],
    REST_TYPES: [
      { value: 'total', label: 'Istirahat Total' },
      { value: 'partial', label: 'Istirahat Sebagian' },
      { value: 'hospitalization', label: 'Rawat Inap' },
    ],
  },

  // BPJS status codes
  STATUS_CODES: {
    ACTIVE: 'Aktif',
    INACTIVE: 'Tidak Aktif',
    SUSPENDED: 'Kepesertaan DITANGGUHKAN',
    EXPIRED: 'Kepesertaan BERHAKTI',
  },

  // Faskes types
  FASKES_TYPES: {
    PUSKESMAS: '1',
    KLINIK_PRATAMA: '2',
    RUMAH_SAKIT: '3',
    KLINIK_UTAMA: '4',
  },

  // Validation rules for BPJS
  VALIDATION: {
    BPJS_NUMBER_LENGTH: 13,
    BPJS_NUMBER_REGEX: /^\d{13}$/,
    SEP_NUMBER_LENGTH: 19,
    SEP_NUMBER_REGEX: /^\d{1}[A-Z]{2}\d{3}[A-Z]{3}\d{5}[A-Z]{3}$/,
    MEDICAL_FACILITY_CODE_LENGTH: 8,
    MIN_AGE_FOR_BPJS: 0,
    MAX_AGE_FOR_BPJS: 120,
  },

  // Claim types
  CLAIM_TYPES: {
    SICK_LEAVE: 'SKI', // Surat Keterangan Istirahat
    MEDICAL_CERTIFICATE: 'SKM', // Surat Keterangan Medis
    REFERAL: 'Rujukan',
  },

  // Error messages in Indonesian
  ERROR_MESSAGES: {
    INVALID_BPJS_NUMBER: 'Nomor BPJS tidak valid',
    INVALID_SEP_NUMBER: 'Nomor SEP tidak valid',
    PATIENT_NOT_FOUND: 'Data peserta tidak ditemukan',
    MEMBERSHIP_INACTIVE: 'Keanggotaan tidak aktif',
    INVALID_MEDICAL_FACILITY: 'Kode fasilitas kesehatan tidak valid',
    MAX_DURATION_EXCEEDED: 'Durasi istirahat melebihi batas yang diizinkan',
    REQUIRED_FIELD_MISSING: 'Field wajib tidak lengkap',
  },
} as const;

// ==================== TYPE EXPORTS ====================
export type CertificateType = (typeof CERTIFICATE_TYPE_OPTIONS)[number]['value'];
export type DurationOption = (typeof DURATION_OPTIONS)[number]['value'];
export type ICD10Category = (typeof ICD10_CATEGORIES)[number];

// ==================== HELPER FUNCTIONS ====================
/**
 * Get certificate type label
 */
export const getCertificateTypeLabel = (type: CertificateType): string => {
  const option = CERTIFICATE_TYPE_OPTIONS.find((opt) => opt.value === type);
  return option?.label || type;
};

/**
 * Get duration label
 */
export const getDurationLabel = (days: number | 'custom'): string => {
  const option = DURATION_OPTIONS.find((opt) => opt.value === days);
  return option?.label || `${days} Hari`;
};

/**
 * Check if duration exceeds BPJS limit
 */
export const exceedsBPJSLimit = (days: number, severityLevel?: string): boolean => {
  const limit = severityLevel === 'severe'
    ? BPJS_RULES.SICK_LEAVE_FORMAT.EXTENDED_DURATION_DAYS
    : BPJS_RULES.SICK_LEAVE_FORMAT.MAX_DURATION_DAYS;
  return days > limit;
};

/**
 * Validate Indonesian NIK
 */
export const validateNIK = (nik: string): boolean => {
  return VALIDATION_RULES.FIELD_VALIDATIONS.NIK_REGEX.test(nik);
};

/**
 * Validate BPJS number
 */
export const validateBPJSNumber = (number: string): boolean => {
  return BPJS_RULES.VALIDATION.BPJS_NUMBER_REGEX.test(number);
};
