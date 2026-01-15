/**
 * Surgery Consent Form Constants
 * Constants for Surgery Consent Form - Konstanta Formulir Persetujuan Bedah
 */

// ============================================
// CONSENT TYPE OPTIONS - JENIS PERSETUJUAN
// ============================================
export const CONSENT_TYPES = {
  INFORMED_CONSENT_SURGERY: {
    value: 'informed_consent_surgery',
    label: 'Persetujuan Informasi Bedah',
    description: 'Persetujuan tindakan operasi/pembedahan',
    code: 'ICS'
  },
  ANESTHESIA_CONSENT: {
    value: 'anesthesia_consent',
    label: 'Persetujuan Anestesi',
    description: 'Persetujuan tindakan anestesi',
    code: 'IAC'
  },
  BLOOD_TRANSFUSION_CONSENT: {
    value: 'blood_transfusion_consent',
    label: 'Persetujuan Transfusi Darah',
    description: 'Persetujuan transfusi darah dan produk darah',
    code: 'IBTC'
  },
  PROCEDURE_SPECIFIC_CONSENT: {
    value: 'procedure_specific_consent',
    label: 'Persetujuan Prosedur Khusus',
    description: 'Persetujuan untuk prosedur medis khusus',
    code: 'IPSC'
  },
  HIGH_RISK_CONSENT: {
    value: 'high_risk_consent',
    label: 'Persetujuan Risiko Tinggi',
    description: 'Persetujuan untuk tindakan bedah risiko tinggi',
    code: 'IHRC'
  }
} as const;

// ============================================
// SURGICAL CATEGORY OPTIONS - KATEGORI BEDAH
// ============================================
export const SURGICAL_CATEGORIES = {
  GENERAL_SURGERY: {
    value: 'general_surgery',
    label: 'Bedah Umum',
    description: 'Tindakan bedah dasar dan emergensi',
    procedures: ['Apendisitis', 'Hernia', 'Kolesistektomi', 'Laparotomi']
  },
  ORTHOPEDIC: {
    value: 'orthopedic',
    label: 'Bedah Orthopedi',
    description: 'Tindakan bedah tulang dan sendi',
    procedures: ['FR (Fiksasi Reduksi Terbuka)', 'Aritroplasti', 'Tendon Repair', 'Amputasi']
  },
  NEUROSURGERY: {
    value: 'neurosurgery',
    label: 'Bedah Saraf',
    description: 'Tindakan bedah otak dan saraf tulang belakang',
    procedures: ['Kraniotomi', 'Diskectomy', 'Laminektomi', 'Shunt']
  },
  CARDIOVASCULAR: {
    value: 'cardiovascular',
    label: 'Bedah Jantung & Pembuluh Darah',
    description: 'Tindakan bedah kardiovaskular',
    procedures: ['CABG', 'Valve Replacement', 'Aneurysm Repair', 'Bypass']
  },
  THORACIC: {
    value: 'thoracic',
    label: 'Bedah Thorak',
    description: 'Tindakan bedah dada dan paru',
    procedures: ['Lobectomy', 'Pneumonectomy', 'Decortication', 'Thoracostomy']
  },
  ABDOMINAL: {
    value: 'abdominal',
    label: 'Bedah Abdomen',
    description: 'Tindakan bedah organ abdomen',
    procedures: ['Gastrectomy', 'Colectomy', 'Hepatectomy', 'Nephrectomy']
  },
  PELVIC: {
    value: 'pelvic',
    label: 'Bedah Panggul',
    description: 'Tindakan bedah area panggul',
    procedures: ['Hysterectomy', 'Prostatectomy', 'C-Section', 'Oophorectomy']
  },
  PLASTIC_SURGERY: {
    value: 'plastic_surgery',
    label: 'Bedah Plastik',
    description: 'Tindakan bedah rekonstruksi dan estetik',
    procedures: ['Skin Graft', 'Flap Surgery', 'Reconstruction', 'Excision']
  },
  OPHTHALMOLOGY: {
    value: 'ophthalmology',
    label: 'Bedah Mata',
    description: 'Tindakan bedah mata',
    procedures: ['Katarak', 'Glaukoma', 'Vitrectomy', 'Strabismus']
  },
  ENT: {
    value: 'ent',
    label: 'Bedah THT',
    description: 'Tindakan bedah telinga, hidung, tenggorok',
    procedures: ['Tonsilectomy', 'Adenoidectomy', 'Septoplasty', 'Mastoidectomy']
  },
  UROLOGY: {
    value: 'urology',
    label: 'Bedah Urologi',
    description: 'Tindakan bedah saluran kemih',
    procedures: ['Lithotripsy', 'TURP', 'Nephrolithotomy', 'Cystectomy']
  },
  GYNECOLOGY: {
    value: 'gynecology',
    label: 'Bedah Kandungan',
    description: 'Tindakan bedah reproduksi wanita',
    procedures: ['Myomectomy', 'Oophorectomy', 'Salpingectomy', 'Cone Biopsy']
  },
  PEDIATRIC_SURGERY: {
    value: 'pediatric_surgery',
    label: 'Bedah Anak',
    description: 'Tindakan bedah pasien anak',
    procedures: ['Pyloromyotomy', 'Imperforate Anus Repair', 'Tracheoesophageal Repair']
  },
  VASCULAR: {
    value: 'vascular',
    label: 'Bedah Vaskular',
    description: 'Tindakan bedah pembuluh darah',
    procedures: ['Endarterectomy', 'Bypass Graft', 'Embolectomy', 'Thrombectomy']
  },
  ONCOLOGIC_SURGERY: {
    value: 'oncologic_surgery',
    label: 'Bedah Onkologi',
    description: 'Tindakan bedah tumor dan kanker',
    procedures: ['Tumor Resection', 'Lymphadenectomy', 'Debulking', 'Amputation']
  }
} as const;

// ============================================
// ANESTHESIA TYPE OPTIONS - JENIS ANESTESI
// ============================================
export const ANESTHESIA_TYPES = {
  GENERAL_ANESTHESIA: {
    value: 'general_anesthesia',
    label: 'Anestesi Umum',
    description: 'Pasien tidur total dengan ventilasi',
    monitoring: ['ECG', 'NIBP', 'SpO2', 'ETCO2', 'Temperature'],
    riskLevel: 'high'
  },
  SPINAL_ANESTHESIA: {
    value: 'spinal_anesthesia',
    label: 'Anestesi Spinal',
    description: 'Bius tulang belakang - numb area bawah',
    monitoring: ['ECG', 'NIBP', 'SpO2'],
    riskLevel: 'medium'
  },
  EPIDURAL_ANESTHESIA: {
    value: 'epidural_anesthesia',
    label: 'Anestesi Epidural',
    description: 'Bius epidural - catheter terus menerus',
    monitoring: ['ECG', 'NIBP', 'SpO2'],
    riskLevel: 'medium'
  },
  REGIONAL_ANESTHESIA: {
    value: 'regional_anesthesia',
    label: 'Anestesi Regional',
    description: 'Bius blok saraf regional',
    monitoring: ['ECG', 'NIBP', 'SpO2'],
    riskLevel: 'medium'
  },
  LOCAL_ANESTHESIA: {
    value: 'local_anesthesia',
    label: 'Anestesi Lokal',
    description: 'Bius lokal pada area operasi',
    monitoring: ['NIBP', 'SpO2'],
    riskLevel: 'low'
  },
  CONSCIOUS_SEDATION: {
    value: 'conscious_sedation',
    label: 'Sedasi Sadar',
    description: 'Pasien rileks tetapi sadar',
    monitoring: ['ECG', 'NIBP', 'SpO2', 'Consciousness'],
    riskLevel: 'low'
  },
  MAC_ANESTHESIA: {
    value: 'mac_anesthesia',
    label: 'Monitored Anesthesia Care (MAC)',
    description: 'Sedasi dengan monitoring penuh',
    monitoring: ['ECG', 'NIBP', 'SpO2', 'Respiratory Rate'],
    riskLevel: 'medium'
  },
  COMBINED_ANESTHESIA: {
    value: 'combined_anesthesia',
    label: 'Anestesi Kombinasi',
    description: 'Kombinasi lebih dari satu teknik',
    monitoring: ['ECG', 'NIBP', 'SpO2', 'ETCO2', 'Temperature'],
    riskLevel: 'high'
  }
} as const;

// ============================================
// RISK TEMPLATES - TEMPLATE RISIKO
// ============================================
export const RISK_TEMPLATES = {
  GENERAL_SURGICAL_RISKS: {
    category: 'general_surgical',
    title: 'Risiko Bedah Umum',
    risks: [
      {
        code: 'BLEEDING',
        label: 'Perdararan',
        severity: 'medium',
        description: 'Kehilangan darah yang mungkin memerlukan transfusi'
      },
      {
        code: 'INFECTION',
        label: 'Infeksi',
        severity: 'medium',
        description: 'Infeksi luka operasi atau infeksi sistemik'
      },
      {
        code: 'SCAR',
        label: 'Bekas Luka',
        severity: 'low',
        description: 'Pembentukan jaringan parut atau keloid'
      },
      {
        code: 'PAIN',
        label: 'Nyeri',
        severity: 'low',
        description: 'Nyeri pasca bedah yang dapat dikelola'
      },
      {
        code: 'DVT',
        label: 'Pembekuan Darah (DVT/PE)',
        severity: 'high',
        description: 'Deep Vein Thrombosis atau Pulmonary Embolism'
      },
      {
        code: 'ORGAN_INJURY',
        label: 'Cedera Organ',
        severity: 'high',
        description: 'Cedera pada organ sekitar area operasi'
      },
      {
        code: 'DEATH',
        label: 'Kematian',
        severity: 'critical',
        description: 'Risiko kematian dari prosedur atau anestesi'
      }
    ]
  },
  ANESTHESIA_RISKS: {
    category: 'anesthesia',
    title: 'Risiko Anestesi',
    risks: [
      {
        code: 'NAUSEA',
        label: 'Mual dan Muntah',
        severity: 'low',
        description: 'Efek samping umum pasca anestesi'
      },
      {
        code: 'SORE_THROAT',
        label: 'Sakit Tenggorokan',
        severity: 'low',
        description: 'Akibat intubasi selama operasi'
      },
      {
        code: 'DENTAL_DAMAGE',
        label: 'Cedera Gigi',
        severity: 'low',
        description: 'Kerusakan gigi selama intubasi'
      },
      {
        code: 'ALLERGIC_REACTION',
        label: 'Reaksi Alergi',
        severity: 'medium',
        description: 'Reaksi terhadap obat anestesi'
      },
      {
        code: 'MALIGNANT_HYPERTHERMIA',
        label: 'Hipertermia Maligna',
        severity: 'critical',
        description: 'Reaksi serius terhadap obat anestesi tertentu'
      },
      {
        code: 'CARDIAC_COMPLICATIONS',
        label: 'Komplikasi Jantung',
        severity: 'high',
        description: 'Aritmia, serangan jantung, atau penurunan tekanan darah'
      },
      {
        code: 'RESPIRATORY_COMPLICATIONS',
        label: 'Komplikasi Pernapasan',
        severity: 'high',
        description: 'Gagal napas, pneumonia, atau bronkospasme'
      },
      {
        code: 'NERVE_INJURY',
        label: 'Cedera Saraf',
        severity: 'medium',
        description: 'Cedera saraf akibat posisi atau teknik'
      },
      {
        code: 'AWARENESS',
        label: 'Kesadaran Intraoperatif',
        severity: 'medium',
        description: 'Pasien sadar selama operasi (jarang terjadi)'
      }
    ]
  },
  BLOOD_TRANSFUSION_RISKS: {
    category: 'blood_transfusion',
    title: 'Risiko Transfusi Darah',
    risks: [
      {
        code: 'TRANSFUSION_REACTION',
        label: 'Reaksi Transfusi',
        severity: 'medium',
        description: 'Reaksi alergi atau hemolitik akut'
      },
      {
        code: 'INFECTION_TRANSMISSION',
        label: 'Transmisi Infeksi',
        severity: 'low',
        description: 'HIV, Hepatitis, atau infeksi lain (sangat jarang)'
      },
      {
        code: 'FLUID_OVERLOAD',
        label: 'Overload Cairan',
        severity: 'medium',
        description: 'Beban cairan berlebih pada sirkulasi'
      },
      {
        code: 'ELECTROLYTE_IMBALANCE',
        label: 'Ketidakseimbangan Elektrolit',
        severity: 'medium',
        description: 'Perubahan kadar kalium, kalsium, dll'
      }
    ]
  },
  PROCEDURE_SPECIFIC_RISKS: {
    category: 'procedure_specific',
    title: 'Risiko Prosedur Khusus',
    risks: [
      {
        code: 'INCONTINENCE',
        label: 'Inkontinensia',
        severity: 'medium',
        description: 'Kehilangan kontrol kandung kemih atau usus'
      },
      {
        code: 'IMPOTENCE',
        label: 'Disfungsi Ereksi',
        severity: 'medium',
        description: 'Gangguan fungsi seksual paska operasi'
      },
      {
        code: 'STENOSIS',
        label: 'Stenosis',
        severity: 'medium',
        description: 'Penyempitan saluran atau lubang tubuh'
      },
      {
        code: 'LEAK',
        label: 'Kebocoran Anastomosis',
        severity: 'high',
        description: 'Kebocoran pada sambungan usus atau organ'
      },
      {
        code: 'ADHESIONS',
        label: 'Adhesi',
        severity: 'medium',
        description: 'Jaringan parut yang menyebabkan organ menempel'
      },
      {
        code: 'LYMPHEDEMA',
        label: 'Limfedema',
        severity: 'medium',
        description: 'Pembengkakan akibat gangguan sistem getah bening'
      }
    ]
  }
} as const;

// ============================================
// VALIDATION RULES - ATURAN VALIDASI
// ============================================
export const VALIDATION_RULES = {
  REQUIRED_FIELDS: {
    [CONSENT_TYPES.INFORMED_CONSENT_SURGERY.value]: [
      'patientName',
      'patientAge',
      'diagnosis',
      'procedure',
      'anesthesiaType',
      'risksAcknowledged',
      'consentSignature',
      'physicianSignature',
      'date',
      'witnessSignature'
    ],
    [CONSENT_TYPES.ANESTHESIA_CONSENT.value]: [
      'patientName',
      'patientAge',
      'anesthesiaType',
      'anesthesiaRisks',
      'alternativesDiscussed',
      'consentSignature',
      'anesthesiologistSignature',
      'date',
      'witnessSignature'
    ],
    [CONSENT_TYPES.BLOOD_TRANSFUSION_CONSENT.value]: [
      'patientName',
      'patientAge',
      'bloodType',
      'transfusionIndication',
      'transfusionRisks',
      'refusalAcknowledged',
      'consentSignature',
      'physicianSignature',
      'date',
      'witnessSignature'
    ],
    [CONSENT_TYPES.PROCEDURE_SPECIFIC_CONSENT.value]: [
      'patientName',
      'patientAge',
      'procedureDescription',
      'procedureRisks',
      'alternatives',
      'consentSignature',
      'physicianSignature',
      'date',
      'witnessSignature'
    ],
    [CONSENT_TYPES.HIGH_RISK_CONSENT.value]: [
      'patientName',
      'patientAge',
      'highRiskProcedures',
      'mortalityRisk',
      'alternativesDiscussed',
      'familyNotified',
      'consentSignature',
      'physicianSignature',
      'departmentHeadSignature',
      'date',
      'witnessSignature'
    ]
  },

  AGE_VERIFICATION: {
    MINOR_AGE_THRESHOLD: 17,
    ADULT_AGE_THRESHOLD: 18,
    ELDERLY_AGE_THRESHOLD: 60,
    MINOR_CONSENT_RULES: {
      requireParentGuardian: true,
      guardianSignature: true,
      guardianRelationship: true,
      ageLimit: 17,
      emancipatedMinorExceptions: ['married', 'employed', 'military']
    },
    ELDERLY_CONSIDERATIONS: {
      requireAdditionalRisksDisclosure: true,
      requireCaregiverDiscussion: true,
      anesthesiaAdjustment: true
    }
  },

  WITNESS_REQUIREMENTS: {
    MINOR_PATIENT: {
      count: 2,
      qualifications: ['Orang tua/wali', 'Saksi independen'],
      relationshipRequired: true
    },
    ADULT_PATIENT: {
      count: 1,
      qualifications: ['Staf rumah sakit', 'Relawan'],
      relationshipNotRequired: true
    },
    HIGH_RISK_PROCEDURES: {
      count: 2,
      qualifications: ['Staf medis', 'Keluarga', 'Saksi independen'],
      oneMedicalWitness: true
    },
    EMERGENCY_PROCEDURES: {
      count: 2,
      qualifications: ['Dokter penanggung jawab', 'Saksi'],
      emergencyDocumentation: true
    }
  },

  SIGNATURE_REQUIREMENTS: {
    PATIENT_SIGNATURE: {
      required: true,
      handwritten: true,
      dateRequired: true,
      timeRequired: true
    },
    PHYSICIAN_SIGNATURE: {
      required: true,
      handwritten: true,
      licenseNumber: true,
      dateRequired: true,
      timeRequired: true
    },
    ANESTHESIOLOGIST_SIGNATURE: {
      requiredForTypes: ['informed_consent_surgery', 'anesthesia_consent'],
      handwritten: true,
      licenseNumber: true,
      dateRequired: true
    },
    WITNESS_SIGNATURE: {
      required: true,
      handwritten: true,
      name: true,
      relationship: 'conditional', // required if family member
      dateRequired: true
    },
    GUARDIAN_SIGNATURE: {
      requiredForMinors: true,
      handwritten: true,
      relationship: true,
      identificationDocument: true,
      dateRequired: true
    }
  },

  FIELD_VALIDATION: {
    patientName: {
      required: true,
      minLength: 3,
      maxLength: 100,
      pattern: /^[a-zA-Z\s,.'-]+$/
    },
    medicalRecordNumber: {
      required: true,
      pattern: /^[A-Z0-9-]+$/
    },
    date: {
      required: true,
      format: 'YYYY-MM-DD',
      notInFuture: true
    },
    time: {
      required: true,
      format: 'HH:mm',
      twentyFourHour: true
    },
    age: {
      required: true,
      min: 0,
      max: 150,
      numeric: true
    },
    phoneNumber: {
      pattern: /^[0-9+()-\s]+$/
    },
    licenseNumber: {
      requiredForSignatures: true,
      minLength: 5,
      maxLength: 50
    }
  }
} as const;

// ============================================
// LEGAL COMPLIANCE RULES - ATURAN KEPATUHAN HUKUM
// ============================================
export const LEGAL_COMPLIANCE = {
  INDONESIAN_MEDICAL_CONSENT_LAW: {
    lawReference: 'UU Praktik Kedokteran No. 29 Tahun 2004',
    informedConsentRequired: true,
    verbalConsentInsufficient: true,
    writtenConsentMandatory: true,
    patientRights: [
      'Hak mendapatkan informasi lengkap',
      'Hak menolak atau menerima tindakan',
      'Hak mendapatkan penjelasan tentang risiko',
      'Hak menanyakan alternatif pengobatan',
      'Hak mendapatkan opini dokter lain (second opinion)'
    ]
  },

  CONSENT_VALIDITY_PERIODS: {
    ELECTIVE_PROCEDURES: {
      validityPeriod: '30 days',
      renewalRequired: true,
      conditions: 'Jika ditunda lebih dari 30 hari'
    },
    URGENT_PROCEDURES: {
      validityPeriod: '24 hours',
      renewalRequired: 'conditional',
      conditions: 'Jika kondisi pasien berubah signifikan'
    },
    EMERGENCY_PROCEDURES: {
      validityPeriod: 'until procedure completion',
      verbalConsentAcceptable: true,
      writtenConsentRequiredAsap: true,
      familyConsentRequired: true
    },
    HIGH_RISK_PROCEDURES: {
      validityPeriod: '7 days',
      renewalRequired: true,
      confirmation24Hours: true
    }
  },

  CONSENT_REVOCATION: {
    canRevokeBeforeProcedure: true,
    canRevokeUntilAnesthesia: true,
    cannotRevokeAfterProcedureStart: true,
    revocationDocumentation: 'Wajib dokumentasi written revocation',
    revocationAcknowledgement: 'Pasien harus memahami konsekuensi'
  },

  MINOR_CONSENT_LAWS: {
    ageOfMajority: 18,
    parentalConsentRequired: true,
    emergencyException: true,
    courtOrderException: true,
    emancipatedMinorException: true,
    matureMinorDoctrine: 'Tidak berlaku di Indonesia'
  },

  DISCLOSURE_REQUIREMENTS: {
    diagnosis: {
      required: true,
      inLaymanTerms: 'Harus dapat dimengerti pasien'
    },
    proposedProcedure: {
      required: true,
      descriptionRequired: true,
      alternativesRequired: true
    },
    risks: {
      materialRisks: true,
      probabilityOfOccurrence: true,
      severityOfConsequences: true
    },
    benefits: {
      expectedBenefits: true,
      likelihoodOfSuccess: true
    },
    alternatives: {
      surgicalAlternatives: true,
      nonSurgicalAlternatives: true,
      noTreatmentConsequences: true
    }
  },

  DOCUMENTATION_REQUIREMENTS: {
    language: 'Bahasa Indonesia',
    patientCopyProvided: true,
    originalInMedicalRecord: true,
    electronicCopyMaintained: true,
    amendmentsAllowed: true,
    amendmentDocumentation: 'Tanda tangan dan tanggal perubahan'
  },

  LIABILITY_PROTECTIONS: {
    physicianDocumentationProtection: true,
    goodFaithDisclosure: true,
    standardOfCareDisclosure: true,
    materialRiskDisclosure: true,
    emergencyDoctrineProtection: true
  }
} as const;

// ============================================
// CONSENT TEMPLATE CONFIGURATIONS - KONFIGURASI TEMPLATE PERSETUJUAN
// ============================================
export const CONSENT_TEMPLATES = {
  STANDARD_INDONESIAN_FORMAT: {
    header: {
      title: 'FORMULIR PERSETUJUAN INFORMASI (INFORMED CONSENT)',
      hospitalName: 'required',
      hospitalAddress: 'required',
      medicalRecordNumber: 'required',
      formNumber: 'auto-generated',
      version: '1.0',
      lastUpdated: '2024-01-01'
    },
    patientInformation: {
      sectionTitle: 'I. INFORMASI PASIEN',
      fields: [
        'Nama Lengkap',
        'No. Rekam Medis',
        'Tanggal Lahir / Umur',
        'Jenis Kelamin',
        'Alamat',
        'No. Telepon'
      ]
    },
    medicalInformation: {
      sectionTitle: 'II. INFORMASI MEDIS',
      fields: [
        'Diagnosis',
        'Rencana Tindakan / Prosedur',
        'Tanggal dan Waktu Rencana Tindakan',
        'Dokter Penanggung Jawab',
        'Dokter Anesthesi',
        'Jenis Anestesi'
      ]
    },
    disclosure: {
      sectionTitle: 'III. PENJELASAN INFORMASI',
      subsections: [
        {
          title: 'A. Tindakan yang akan dilakukan',
          content: 'Deskripsi tindakan operasi/prosedur yang akan dilakukan'
        },
        {
          title: 'B. Tujuan tindakan',
          content: 'Tujuan dan manfaat yang diharapkan dari tindakan'
        },
        {
          title: 'C. Risiko dan komplikasi',
          content: 'Risiko yang mungkin terjadi termasuk yang paling berat dan paling ringan'
        },
        {
          title: 'D. Alternatif tindakan',
          content: 'Alternatif pengobatan lain dan konsekuensi tidak melakukan tindakan'
        },
        {
          title: 'E. Prognosis',
          content: 'Prediksi hasil yang diharapkan'
        }
      ]
    },
    understandingConfirmation: {
      sectionTitle: 'IV. PERNYATAAN PEMAHAMAN',
      statements: [
        'Saya telah mendapatkan penjelasan yang cukup mengenai penyakit saya',
        'Saya mengerti tindakan yang akan dilakukan beserta tujuannya',
        'Saya mengerti risiko dan komplikasi yang mungkin terjadi',
        'Saya mengerti ada alternatif tindakan lain',
        'Saya mengerti konsekuensi jika menolak tindakan',
        'Saya diberikan kesempatan untuk bertanya dan jawaban telah memuaskan'
      ]
    },
    consentSection: {
      sectionTitle: 'V. PERSETUJUAN',
      options: [
        'Saya menyetujui tindakan yang dijelaskan di atas',
        'Saya menolak tindakan yang dijelaskan di atas',
        'Saya masih mempertimbangkan dan akan memberikan keputusan kemudian'
      ]
    },
    signatures: {
      sectionTitle: 'VI. TANDA TANGAN',
      signatories: [
        {
          role: 'Pasien / Keluarga',
          signatureRequired: true,
          nameRequired: true,
          relationshipRequired: 'conditional',
          dateRequired: true,
          timeRequired: true
        },
        {
          role: 'Saksi 1',
          signatureRequired: true,
          nameRequired: true,
          relationshipRequired: 'conditional',
          dateRequired: true,
          timeRequired: true
        },
        {
          role: 'Saksi 2',
          signatureRequired: 'conditional',
          nameRequired: 'conditional',
          dateRequired: 'conditional',
          timeRequired: 'conditional'
        },
        {
          role: 'Dokter Penanggung Jawab',
          signatureRequired: true,
          nameRequired: true,
          licenseNumberRequired: true,
          dateRequired: true,
          timeRequired: true
        },
        {
          role: 'Dokter Anesthesi',
          signatureRequired: 'conditional',
          nameRequired: 'conditional',
          licenseNumberRequired: true,
          dateRequired: 'conditional',
          timeRequired: 'conditional'
        }
      ]
    }
  },

  PRINT_LAYOUT_SETTINGS: {
    pageSize: 'A4',
    orientation: 'portrait',
    margins: {
      top: '20mm',
      bottom: '20mm',
      left: '20mm',
      right: '20mm'
    },
    fonts: {
      header: {
        family: 'Arial',
        size: 14,
        weight: 'bold',
        alignment: 'center'
      },
      sectionTitle: {
        family: 'Arial',
        size: 12,
        weight: 'bold',
        alignment: 'left'
      },
      body: {
        family: 'Arial',
        size: 11,
        weight: 'normal',
        alignment: 'left'
      },
      signature: {
        family: 'Arial',
        size: 10,
        weight: 'normal',
        alignment: 'left'
      }
    },
    spacing: {
      lineSpacing: 1.5,
      paragraphSpacing: 6,
      sectionSpacing: 12
    },
    signatureArea: {
      height: '60mm',
      width: '80mm',
      borderWidth: 1,
      borderStyle: 'solid'
    },
    checkboxes: {
      size: 'medium',
      style: 'square'
    },
    watermark: {
      enabled: false,
      text: 'DRAFT',
      opacity: 0.1
    }
  },

  EMERGENCY_CONSENT_TEMPLATE: {
    header: 'FORMULIR PERSETUJUAN INFORMASI KONDISI GAWAT DARURAT',
    additionalFields: [
      'Waktu masuk',
      'Kondisi darurat',
      'Kondisi pasien tidak memungkinkan menandatangani',
      'Pihak yang memberikan persetujuan',
      'Hubungan dengan pasien'
    ],
    specialNotes: [
      'Dokumentasi mengenai kondisi darurat',
      'Alasan tidak dapat menunggu persetujuan tertulis',
      'Upaya mendapatkan persetujuan keluarga'
    ]
  },

  REFUSAL_CONSENT_TEMPLATE: {
    header: 'FORMULIR PENOLAKAN PERSETUJUAN INFORMASI',
    sections: [
      {
        title: 'Alasan Penolakan',
        fields: [
          'Alasan pribadi/keluarga',
          'Alasan keagamaan',
          'Alasan finansial',
          'Ingin mencari pengobatan lain',
          'Lainnya'
        ]
      },
      {
        title: 'Konsekuensi Penolakan',
        documentation: [
          'Penjelasan dokter mengenai konsekuensi',
          'Risiko kesehatan',
          'Perkiraan prognosis tanpa tindakan',
          'Alternatif yang tersedia'
        ]
      },
      {
        title: 'Pernyataan Penolakan',
        statement: 'Saya menyatakan menolak tindakan yang dijelaskan di atas dengan sadar dan tanpa paksaan'
      }
    ]
  }
} as const;

// ============================================
// ADDITIONAL CONSTANTS - KONSTANTA TAMBAHAN
// ============================================
export const COMMON_CONSTANTS = {
  YES_NO_OPTIONS: [
    { value: 'yes', label: 'Ya' },
    { value: 'no', label: 'Tidak' }
  ],

  GENDER_OPTIONS: [
    { value: 'male', label: 'Laki-laki' },
    { value: 'female', label: 'Perempuan' }
  ],

  RELATIONSHIP_OPTIONS: [
    { value: 'spouse', label: 'Suami/Istri' },
    { value: 'parent', label: 'Orang Tua' },
    { value: 'child', label: 'Anak' },
    { value: 'sibling', label: 'Saudara Kandung' },
    { value: 'guardian', label: 'Wali' },
    { value: 'relative', label: 'Kerabat' },
    { value: 'other', label: 'Lainnya' }
  ],

  PROCEDURE_URGENCY: [
    { value: 'elective', label: 'Elektif (Terjadwal)', description: 'Dapat direncanakan' },
    { value: 'urgent', label: 'Urgent', description: 'Harus segera tapi tidak emergensi' },
    { value: 'emergency', label: 'Emergensi', description: 'Segera diperlukan' }
  ],

  ASA_CLASSIFICATION: [
    { value: 'asa1', label: 'ASA I', description: 'Pasien sehat tanpa penyakit sistemik' },
    { value: 'asa2', label: 'ASA II', description: 'Penyakit sistemik ringan' },
    { value: 'asa3', label: 'ASA III', description: 'Penyakit sistemik berat dengan batas fungsional' },
    { value: 'asa4', label: 'ASA IV', description: 'Penyakit sistemik berat yang mengancam jiwa' },
    { value: 'asa5', label: 'ASA V', description: 'Pasien moribund tidak mungkin hidup 24 jam' },
    { value: 'asa6', label: 'ASA VI', description: 'Pasien brain-dead untuk donor organ' }
  ]
} as const;

// ============================================
// EXPORT ALL CONSTANTS
// ============================================
export const SURGERY_CONSENT_CONSTANTS = {
  CONSENT_TYPES,
  SURGICAL_CATEGORIES,
  ANESTHESIA_TYPES,
  RISK_TEMPLATES,
  VALIDATION_RULES,
  LEGAL_COMPLIANCE,
  CONSENT_TEMPLATES,
  COMMON_CONSTANTS
} as const;
