/**
 * Vital Signs Constants
 * Konstanta untuk Formulir Pemantauan Tanda Vital
 */

// ============================================================================
// RENTANG NORMAL TANDA VITAL
// ============================================================================

export const VITAL_SIGNS_NORMAL_RANGES = {
  // Rentang Normal Dewasa
  adult: {
    temperature: {
      min: 36.1,
      max: 37.5,
      unit: '°C',
      label: 'Suhu Tubuh'
    },
    heartRate: {
      min: 60,
      max: 100,
      unit: 'x/menit',
      label: 'Nadi'
    },
    respiratoryRate: {
      min: 12,
      max: 20,
      unit: 'x/menit',
      label: 'Pernapasan'
    },
    bloodPressure: {
      systolic: {
        min: 90,
        max: 120,
        label: 'Tekanan Darah Sistolik'
      },
      diastolic: {
        min: 60,
        max: 80,
        label: 'Tekanan Darah Diastolik'
      },
      unit: 'mmHg'
    },
    oxygenSaturation: {
      min: 95,
      max: 100,
      unit: '%',
      label: 'Saturasi Oksigen'
    },
    weight: {
      min: 40,
      max: 150,
      unit: 'kg',
      label: 'Berat Badan'
    },
    height: {
      min: 100,
      max: 220,
      unit: 'cm',
      label: 'Tinggi Badan'
    },
    bmi: {
      min: 18.5,
      max: 24.9,
      unit: 'kg/m²',
      label: 'Indeks Massa Tubuh'
    }
  },

  // Rentang Normal Anak-anak (Pediatric)
  pediatric: {
    neonate: {
      ageRange: '0-28 hari',
      heartRate: { min: 100, max: 205, unit: 'x/menit' },
      respiratoryRate: { min: 30, max: 60, unit: 'x/menit' },
      systolicBP: { min: 50, max: 70, unit: 'mmHg' },
      diastolicBP: { min: 25, max: 45, unit: 'mmHg' },
      temperature: { min: 36.5, max: 37.5, unit: '°C' }
    },
    infant: {
      ageRange: '1-12 bulan',
      heartRate: { min: 90, max: 180, unit: 'x/menit' },
      respiratoryRate: { min: 25, max: 50, unit: 'x/menit' },
      systolicBP: { min: 70, max: 100, unit: 'mmHg' },
      diastolicBP: { min: 40, max: 60, unit: 'mmHg' },
      temperature: { min: 36.5, max: 37.5, unit: '°C' }
    },
    toddler: {
      ageRange: '1-3 tahun',
      heartRate: { min: 80, max: 150, unit: 'x/menit' },
      respiratoryRate: { min: 20, max: 30, unit: 'x/menit' },
      systolicBP: { min: 80, max: 110, unit: 'mmHg' },
      diastolicBP: { min: 45, max: 65, unit: 'mmHg' },
      temperature: { min: 36.5, max: 37.5, unit: '°C' }
    },
    preschool: {
      ageRange: '3-6 tahun',
      heartRate: { min: 70, max: 130, unit: 'x/menit' },
      respiratoryRate: { min: 18, max: 25, unit: 'x/menit' },
      systolicBP: { min: 85, max: 115, unit: 'mmHg' },
      diastolicBP: { min: 50, max: 70, unit: 'mmHg' },
      temperature: { min: 36.5, max: 37.5, unit: '°C' }
    },
    schoolAge: {
      ageRange: '6-12 tahun',
      heartRate: { min: 60, max: 110, unit: 'x/menit' },
      respiratoryRate: { min: 15, max: 22, unit: 'x/menit' },
      systolicBP: { min: 90, max: 120, unit: 'mmHg' },
      diastolicBP: { min: 55, max: 75, unit: 'mmHg' },
      temperature: { min: 36.5, max: 37.5, unit: '°C' }
    },
    adolescent: {
      ageRange: '12-18 tahun',
      heartRate: { min: 55, max: 105, unit: 'x/menit' },
      respiratoryRate: { min: 12, max: 20, unit: 'x/menit' },
      systolicBP: { min: 95, max: 135, unit: 'mmHg' },
      diastolicBP: { min: 60, max: 80, unit: 'mmHg' },
      temperature: { min: 36.5, max: 37.5, unit: '°C' }
    }
  }
};

// ============================================================================
// NILAI KRITIS DAN BATAS PERINGATAN
// ============================================================================

export const CRITICAL_VALUES = {
  temperature: {
    criticalHigh: {
      value: 40,
      label: 'Hipertermi Berat',
      action: 'Segera beri tindakan pendinginan'
    },
    criticalLow: {
      value: 35,
      label: 'Hipotermi Berat',
      action: 'Segera beri tindakan pemanasan'
    },
    warningHigh: {
      value: 38.5,
      label: 'Demam Tinggi',
      action: 'Pantau dan beri antipiretik'
    },
    warningLow: {
      value: 36,
      label: 'Hipotermi Ringan',
      action: 'Pantau suhu tubuh'
    }
  },
  heartRate: {
    criticalHigh: {
      value: 150,
      label: 'Takikardi Berat',
      action: 'Evaluasi ritme jantung'
    },
    criticalLow: {
      value: 40,
      label: 'Bradikardi Berat',
      action: 'Evaluasi ritme jantung'
    },
    warningHigh: {
      value: 120,
      label: 'Takikardi Ringan',
      action: 'Pantau frekuensi nadi'
    },
    warningLow: {
      value: 50,
      label: 'Bradikardi Ringan',
      action: 'Pantau frekuensi nadi'
    }
  },
  respiratoryRate: {
    criticalHigh: {
      value: 35,
      label: 'Tahipnea Berat',
      action: 'Evaluasi status pernapasan'
    },
    criticalLow: {
      value: 8,
      label: 'Bradipnea Berat',
      action: 'Evaluasi status pernapasan'
    },
    warningHigh: {
      value: 25,
      label: 'Tahipnea Ringan',
      action: 'Pantau frekuensi napas'
    },
    warningLow: {
      value: 10,
      label: 'Bradipnea Ringan',
      action: 'Pantau frekuensi napas'
    }
  },
  bloodPressure: {
    systolic: {
      criticalHigh: {
        value: 180,
        label: 'Hipertensi Darurat',
        action: 'Segera evaluasi dan beri terapi'
      },
      criticalLow: {
        value: 80,
        label: 'Hipotensi Berat',
        action: 'Segera beri resusitasi cairan'
      },
      warningHigh: {
        value: 140,
        label: 'Hipertensi',
        action: 'Pantau tekanan darah'
      },
      warningLow: {
        value: 90,
        label: 'Hipotensi Ringan',
        action: 'Pantau tekanan darah'
      }
    },
    diastolic: {
      criticalHigh: {
        value: 110,
        label: 'Hipertensi Darurat',
        action: 'Segera evaluasi dan beri terapi'
      },
      criticalLow: {
        value: 50,
        label: 'Hipotensi Berat',
        action: 'Segera beri resusitasi cairan'
      },
      warningHigh: {
        value: 90,
        label: 'Hipertensi',
        action: 'Pantau tekanan darah'
      },
      warningLow: {
        value: 60,
        label: 'Hipotensi Ringan',
        action: 'Pantau tekanan darah'
      }
    }
  },
  oxygenSaturation: {
    criticalLow: {
      value: 90,
      label: 'Hipoksemia Berat',
      action: 'Segera beri oksigen tambahan'
    },
    warningLow: {
      value: 94,
      label: 'Hipoksemia Ringan',
      action: 'Pantau saturasi oksigen'
    }
  }
};

// ============================================================================
// SATUAN PENGUKURAN
// ============================================================================

export const MEASUREMENT_UNITS = {
  temperature: {
    unit: '°C',
    alternatives: ['°F'],
    conversion: {
      toFahrenheit: (celsius: number) => (celsius * 9/5) + 32,
      toCelsius: (fahrenheit: number) => (fahrenheit - 32) * 5/9
    }
  },
  heartRate: {
    unit: 'x/menit',
    alternatives: ['x/menit']
  },
  respiratoryRate: {
    unit: 'x/menit',
    alternatives: ['x/menit']
  },
  bloodPressure: {
    unit: 'mmHg',
    alternatives: ['kPa'],
    conversion: {
      tokPa: (mmHg: number) => mmHg * 0.1333,
      toMmHg: (kPa: number) => kPa / 0.1333
    }
  },
  oxygenSaturation: {
    unit: '%',
    alternatives: ['%']
  },
  weight: {
    unit: 'kg',
    alternatives: ['gram', 'pound'],
    conversion: {
      toGram: (kg: number) => kg * 1000,
      toPound: (kg: number) => kg * 2.20462
    }
  },
  height: {
    unit: 'cm',
    alternatives: ['meter', 'inci'],
    conversion: {
      toMeter: (cm: number) => cm / 100,
      toInch: (cm: number) => cm / 2.54
    }
  },
  bmi: {
    unit: 'kg/m²',
    alternatives: ['kg/m²']
  }
};

// ============================================================================
// SKOR MEWS (Modified Early Warning Score)
// ============================================================================

export const MEWS_SCORE = {
  name: 'Modified Early Warning Score',
  description: 'Skor Peringatan Dini Termodifikasi',
  parameters: {
    heartRate: {
      label: 'Frekuensi Jantung',
      scores: [
        { range: [0, 40], score: 3, description: 'Sangat Lambat' },
        { range: [41, 50], score: 1, description: 'Lambat' },
        { range: [51, 100], score: 0, description: 'Normal' },
        { range: [101, 110], score: 1, description: 'Cepat' },
        { range: [111, 130], score: 2, description: 'Sangat Cepat' },
        { range: 131, score: 3, description: 'Ekstrem' }
      ]
    },
    systolicBP: {
      label: 'Tekanan Darah Sistolik',
      scores: [
        { range: [0, 70], score: 3, description: 'Sangat Rendah' },
        { range: [71, 80], score: 2, description: 'Rendah' },
        { range: [81, 100], score: 1, description: 'Agak Rendah' },
        { range: [101, 199], score: 0, description: 'Normal' },
        { range: 200, score: 3, description: 'Sangat Tinggi' }
      ]
    },
    respiratoryRate: {
      label: 'Frekuensi Pernapasan',
      scores: [
        { range: [0, 8], score: 3, description: 'Sangat Lambat' },
        { range: [9, 11], score: 1, description: 'Lambat' },
        { range: [12, 20], score: 0, description: 'Normal' },
        { range: [21, 25], score: 2, description: 'Cepat' },
        { range: 26, score: 3, description: 'Sangat Cepat' }
      ]
    },
    temperature: {
      label: 'Suhu Tubuh',
      scores: [
        { range: [0, 35], score: 3, description: 'Hipotermi Berat' },
        { range: [35.1, 36], score: 1, description: 'Hipotermi Ringan' },
        { range: [36.1, 37.5], score: 0, description: 'Normal' },
        { range: [37.6, 38.5], score: 1, description: 'Demam Ringan' },
        { range: 38.6, score: 3, description: 'Demam Berat' }
      ]
    },
    consciousness: {
      label: 'Kesadaran',
      scores: [
        { value: 'alert', score: 0, description: 'Sadar Penuh' },
        { value: 'voice', score: 1, description: 'Respon Suara' },
        { value: 'pain', score: 2, description: 'Respon Nyeri' },
        { value: 'unresponsive', score: 3, description: 'Tidak Responsif' }
      ]
    }
  },
  riskLevels: {
    low: {
      range: [0, 2],
      label: 'Risiko Rendah',
      action: 'Pantau rutin',
      color: 'green'
    },
    medium: {
      range: [3, 4],
      label: 'Risiko Sedang',
      action: 'Tingkatkan frekuensi pemantauan',
      color: 'yellow'
    },
    high: {
      range: [5, 6],
      label: 'Risiko Tinggi',
      action: 'Segera beri tindakan medis',
      color: 'orange'
    },
    critical: {
      range: [7, 15],
      label: 'Risiko Kritis',
      action: 'Segera hubungi dokter dan resusitasi',
      color: 'red'
    }
  }
};

// ============================================================================
// SKOR EWS (Early Warning Score)
// ============================================================================

export const EWS_SCORE = {
  name: 'Early Warning Score',
  description: 'Skor Peringatan Dini',
  parameters: {
    heartRate: {
      label: 'Frekuensi Jantung',
      scores: [
        { range: [0, 40], score: 3 },
        { range: [41, 50], score: 1 },
        { range: [51, 100], score: 0 },
        { range: [101, 111], score: 1 },
        { range: [112, 130], score: 2 },
        { range: 131, score: 3 }
      ]
    },
    systolicBP: {
      label: 'Tekanan Darah Sistolik',
      scores: [
        { range: [0, 90], score: 3 },
        { range: [91, 100], score: 2 },
        { range: [101, 110], score: 1 },
        { range: [111, 219], score: 0 },
        { range: 220, score: 3 }
      ]
    },
    respiratoryRate: {
      label: 'Frekuensi Pernapasan',
      scores: [
        { range: [0, 8], score: 3 },
        { range: [9, 11], score: 1 },
        { range: [12, 20], score: 0 },
        { range: [21, 25], score: 2 },
        { range: 26, score: 3 }
      ]
    },
    temperature: {
      label: 'Suhu Tubuh',
      scores: [
        { range: [0, 35], score: 3 },
        { range: [35.1, 36], score: 1 },
        { range: [36.1, 37.5], score: 0 },
        { range: [37.6, 38.5], score: 1 },
        { range: 38.6, score: 3 }
      ]
    },
    oxygenSaturation: {
      label: 'Saturasi Oksigen',
      scores: [
        { range: [0, 91], score: 3 },
        { range: [92, 93], score: 2 },
        { range: [94, 95], score: 1 },
        { range: 96, score: 0 }
      ],
      note: 'Jika pasien menggunakan oksigen, tambah 1 poin'
    },
    consciousness: {
      label: 'Kesadaran',
      scores: [
        { value: 'alert', score: 0 },
        { value: 'confusion', score: 1 },
        { value: 'voice', score: 2 },
        { value: 'pain', score: 3 },
        { value: 'unresponsive', score: 3 }
      ]
    }
  }
};

// ============================================================================
// SKALA NYERI
// ============================================================================

export const PAIN_SCALE = {
  numeric: {
    name: 'Skala Nyeri Numerik',
    type: 'numeric',
    range: [0, 10],
    levels: [
      { value: 0, label: 'Tidak Ada Nyeri', description: 'Tidak ada rasa sakit', color: '#4CAF50' },
      { value: 1, label: 'Nyeri Sangat Ringan', description: 'Hampir tidak terasa', color: '#8BC34A' },
      { value: 2, label: 'Nyeri Ringan', description: 'Mengganggu sedikit', color: '#CDDC39' },
      { value: 3, label: 'Nyeri Ringan', description: 'Mengganggu aktivitas', color: '#FFEB3B' },
      { value: 4, label: 'Nyeri Sedang', description: 'Mengganggu konsentrasi', color: '#FFC107' },
      { value: 5, label: 'Nyeri Sedang', description: 'Perlu obat pereda nyeri', color: '#FF9800' },
      { value: 6, label: 'Nyeri Agak Berat', description: 'Sangat mengganggu', color: '#FF5722' },
      { value: 7, label: 'Nyeri Berat', description: 'Sulit berkonsentrasi', color: '#F44336' },
      { value: 8, label: 'Nyeri Berat', description: 'Sulit melakukan aktivitas', color: '#E91E63' },
      { value: 9, label: 'Nyeri Sangat Berat', description: 'Hampir tidak tertahankan', color: '#9C27B0' },
      { value: 10, label: 'Nyeri Terburuk', description: 'Nyeri yang tidak tertahankan', color: '#673AB7' }
    ]
  },

  wongBaker: {
    name: 'Skala Wong-Baker FACES',
    type: 'faces',
    faces: [
      { value: 0, label: 'Tidak Ada Nyeri', description: 'Tertawa atau senang', emoji: '😊' },
      { value: 2, label: 'Sedikit Nyeri', description: 'Sedikit khawatir', emoji: '😐' },
      { value: 4, label: 'Nyeri Sedang', description: 'Ada sedikit rasa sakit', emoji: '😕' },
      { value: 6, label: 'Nyeri Banyak', description: 'Sakit tapi masih bisa tertawa', emoji: '😟' },
      { value: 8, label: 'Nyeri Sangat Banyak', description: 'Sangat sakit, menangis', emoji: '😢' },
      { value: 10, label: 'Nyeri Terburuk', description: 'Sakit sekali', emoji: '😭' }
    ]
  },

  flacc: {
    name: 'Skala FLACC (Untuk Pasien Tidak Bisa Komunikasi)',
    type: 'flacc',
    categories: [
      {
        name: 'Wajah (Face)',
        parameter: 'face',
        scores: [
          { value: 0, label: 'Tidak ada ekspresi khusus atau senyum' },
          { value: 1, label: 'Kadang-kadang cemberut, cemas, merengut' },
          { value: 2, label: 'Sering cemberut, meringis, menangis' }
        ]
      },
      {
        name: 'Kaki (Legs)',
        parameter: 'legs',
        scores: [
          { value: 0, label: 'Posisi normal atau santai' },
          { value: 1, label: 'Gelisah, cemas, tegang' },
          { value: 2, label: 'Menendang, melengkung, mengetuk-ngetuk' }
        ]
      },
      {
        name: 'Aktivitas (Activity)',
        parameter: 'activity',
        scores: [
          { value: 0, label: 'Berbaring tenang, posisi normal' },
          { value: 1, label: 'Gerak badan, menggeliat, bergoyang' },
          { value: 2, label: 'Melengkung, kaku, menggeliat hebat' }
        ]
      },
      {
        name: 'Menangis (Cry)',
        parameter: 'cry',
        scores: [
          { value: 0, label: 'Tidak menangis' },
          { value: 1, label: 'Meres atau mengeluh' },
          { value: 2, label: 'Menangis terus-menerus, menjerit' }
        ]
      },
      {
        name: 'Ketenangan (Consolability)',
        parameter: 'consolability',
        scores: [
          { value: 0, label: 'Tenang, tidak perlu ditenangkan' },
          { value: 1, label: 'Bisa ditenangkan dengan sentuhan, bicara' },
          { value: 2, label: 'Sulit ditenangkan atau tidak bisa ditenangkan' }
        ]
      }
    ],
    interpretation: [
      { range: [0, 1], label: 'Tidak ada nyeri' },
      { range: [2, 3], label: 'Nyeri ringan' },
      { range: [4, 6], label: 'Nyeri sedang' },
      { range: [7, 10], label: 'Nyeri berat' }
    ]
  }
};

// ============================================================================
// SKALA GCS (Glasgow Coma Scale)
// ============================================================================

export const GCS_SCALE = {
  name: 'Glasgow Coma Scale',
  description: 'Skala Koma Glasgow',
  maxScore: 15,
  minScore: 3,

  eye: {
    name: 'Respon Mata (E)',
    scores: [
      { value: 4, label: 'Spontan', description: 'Mata terbuka spontan tanpa stimulasi' },
      { value: 3, label: 'Panggilan Suara', description: 'Mata terbuka saat dipanggil' },
      { value: 2, label: 'Rangsang Nyeri', description: 'Mata terbuka saat dirangsang nyeri' },
      { value: 1, label: 'Tidak Ada Respon', description: 'Mata tetap tertutup' }
    ]
  },

  verbal: {
    name: 'Respon Verbal (V)',
    scores: [
      { value: 5, label: 'Terorientasi', description: 'Pasien sadar penuh dan bisa berkomunikasi' },
      { value: 4, label: 'Bingung', description: 'Pasien bicara tapi tidak tepat' },
      { value: 3, label: 'Kata Tidak Jelas', description: 'Hanya mengucapkan kata-kata tidak jelas' },
      { value: 2, label: 'Suara Tidak Jelas', description: 'Hanya mengeluarkan suara tidak jelas' },
      { value: 1, label: 'Tidak Ada Respon', description: 'Tidak ada respon verbal sama sekali' }
    ]
  },

  motor: {
    name: 'Respon Motorik (M)',
    scores: [
      { value: 6, label: 'Mematuhi Perintah', description: 'Bisa mengikuti perintah' },
      { value: 5, label: 'Lokalisasi Nyeri', description: 'Bisa melokalisasi rangsang nyeri' },
      { value: 4, label: 'Normal Fleksi', description: 'Fleksi normal terhadap nyeri' },
      { value: 3, label: 'Dekortikasi', description: 'Fleksi abnormal, lengan menekuk' },
      { value: 2, label: 'Deserebrasi', description: 'Ekstensi abnormal, lengan lurus' },
      { value: 1, label: 'Tidak Ada Respon', description: 'Tidak ada respon motorik' }
    ]
  },

  severity: {
    severe: {
      range: [3, 8],
      label: 'Koma Berat',
      description: 'Trauma otak berat',
      color: 'red'
    },
    moderate: {
      range: [9, 12],
      label: 'Koma Sedang',
      description: 'Trauma otak sedang',
      color: 'orange'
    },
    mild: {
      range: [13, 15],
      label: 'Koma Ringan',
      description: 'Trauma otak ringan',
      color: 'green'
    }
  }
};

// ============================================================================
// ATURAN VALIDASI
// ============================================================================

export const VALIDATION_RULES = {
  required: {
    temperature: true,
    heartRate: true,
    respiratoryRate: true,
    systolicBP: true,
    diastolicBP: true,
    oxygenSaturation: true,
    weight: false,
    height: false,
    painScale: false,
    gcs: false
  },

  ranges: {
    temperature: {
      min: 30,
      max: 45,
      message: 'Suhu harus antara 30°C - 45°C'
    },
    heartRate: {
      min: 0,
      max: 300,
      message: 'Frekuensi nadi harus antara 0 - 300 x/menit'
    },
    respiratoryRate: {
      min: 0,
      max: 100,
      message: 'Frekuensi napas harus antara 0 - 100 x/menit'
    },
    systolicBP: {
      min: 40,
      max: 300,
      message: 'Tekanan darah sistolik harus antara 40 - 300 mmHg'
    },
    diastolicBP: {
      min: 20,
      max: 200,
      message: 'Tekanan darah diastolik harus antara 20 - 200 mmHg'
    },
    oxygenSaturation: {
      min: 0,
      max: 100,
      message: 'Saturasi oksigen harus antara 0 - 100%'
    },
    weight: {
      min: 0,
      max: 300,
      message: 'Berat badan harus antara 0 - 300 kg'
    },
    height: {
      min: 0,
      max: 300,
      message: 'Tinggi badan harus antara 0 - 300 cm'
    },
    painScale: {
      min: 0,
      max: 10,
      message: 'Skala nyeri harus antara 0 - 10'
    }
  },

  custom: {
    bloodPressure: {
      systolicMustBeHigher: {
        validate: (systolic: number, diastolic: number) => {
          return systolic > diastolic;
        },
        message: 'Tekanan darah sistolik harus lebih tinggi dari diastolik'
      }
    },
    gcs: {
      totalScore: {
        validate: (total: number) => {
          return total >= 3 && total <= 15;
        },
        message: 'Total skor GCS harus antara 3 - 15'
      }
    }
  }
};

// ============================================================================
// INDIKATOR TREND
// ============================================================================

export const TREND_INDICATORS = {
  improving: {
    label: 'Membaik',
    description: 'Nilai mendekati rentang normal',
    icon: 'arrow-upward',
    color: 'green',
    calculate: (current: number, previous: number, normalMin: number, normalMax: number) => {
      const currentDistance = getDistanceFromNormal(current, normalMin, normalMax);
      const previousDistance = getDistanceFromNormal(previous, normalMin, normalMax);
      return currentDistance < previousDistance;
    }
  },

  stable: {
    label: 'Stabil',
    description: 'Nilai dalam rentang normal',
    icon: 'remove',
    color: 'blue',
    calculate: (current: number, normalMin: number, normalMax: number) => {
      return current >= normalMin && current <= normalMax;
    }
  },

  worsening: {
    label: 'Memburuk',
    description: 'Nilai menjauh dari rentang normal',
    icon: 'arrow-downward',
    color: 'red',
    calculate: (current: number, previous: number, normalMin: number, normalMax: number) => {
      const currentDistance = getDistanceFromNormal(current, normalMin, normalMax);
      const previousDistance = getDistanceFromNormal(previous, normalMin, normalMax);
      return currentDistance > previousDistance;
    }
  },

  noChange: {
    label: 'Tidak Berubah',
    description: 'Nilai sama dengan sebelumnya',
    icon: 'arrow-forward',
    color: 'gray',
    calculate: (current: number, previous: number) => {
      return current === previous;
    }
  }
};

// Fungsi helper untuk menghitung jarak dari normal
function getDistanceFromNormal(value: number, normalMin: number, normalMax: number): number {
  if (value >= normalMin && value <= normalMax) {
    return 0;
  } else if (value < normalMin) {
    return normalMin - value;
  } else {
    return value - normalMax;
  }
}

// Fungsi untuk menentukan trend
export function determineTrend(
  current: number,
  previous: number | null,
  normalMin: number,
  normalMax: number
): string {
  if (previous === null) {
    return 'noChange';
  }

  if (TREND_INDICATORS.noChange.calculate(current, previous)) {
    return 'noChange';
  }

  if (TREND_INDICATORS.stable.calculate(current, normalMin, normalMax)) {
    return 'stable';
  }

  if (TREND_INDICATORS.improving.calculate(current, previous, normalMin, normalMax)) {
    return 'improving';
  }

  if (TREND_INDICATORS.worsening.calculate(current, previous, normalMin, normalMax)) {
    return 'worsening';
  }

  return 'noChange';
}

// ============================================================================
// LABEL UMUM
// ============================================================================

export const COMMON_LABELS = {
  vitalSigns: 'Tanda Vital',
  patientInformation: 'Informasi Pasien',
  measurementDate: 'Tanggal Pengukuran',
  measurementTime: 'Waktu Pengukuran',
  measuredBy: 'Diukur Oleh',
  notes: 'Catatan Tambahan',
  save: 'Simpan',
  cancel: 'Batal',
  submit: 'Kirim',
  edit: 'Edit',
  delete: 'Hapus',
  confirm: 'Konfirmasi',
  back: 'Kembali',
  next: 'Lanjut',
  required: 'Wajib diisi',
  optional: 'Opsional'
};

// ============================================================================
// KATEGORI TANDA VITAL
// ============================================================================

export const VITAL_SIGN_CATEGORIES = {
  basic: {
    name: 'Dasar',
    description: 'Tanda vital dasar yang harus diukur',
    fields: ['temperature', 'heartRate', 'respiratoryRate', 'bloodPressure', 'oxygenSaturation']
  },
  anthropometry: {
    name: 'Antropometri',
    description: 'Pengukuran fisik pasien',
    fields: ['weight', 'height', 'bmi']
  },
  neurological: {
    name: 'Neurologis',
    description: 'Status neurologis pasien',
    fields: ['gcs', 'pupils', 'painScale']
  },
  additional: {
    name: 'Tambahan',
    description: 'Pengukuran tambahan jika diperlukan',
    fields: ['bloodGlucose', 'urineOutput', 'fluidBalance']
  }
};

// ============================================================================
// FREKUENSI PEMANTAUAN
// ============================================================================

export const MONITORING_FREQUENCY = {
  critical: {
    label: 'Kritis',
    frequency: 'Setiap 5-15 menit',
    color: 'red'
  },
  high: {
    label: 'Tinggi',
    frequency: 'Setiap 15-30 menit',
    color: 'orange'
  },
  moderate: {
    label: 'Sedang',
    frequency: 'Setiap 1-2 jam',
    color: 'yellow'
  },
  low: {
    label: 'Rendah',
    frequency: 'Setiap 4-6 jam',
    color: 'green'
  },
  routine: {
    label: 'Rutin',
    frequency: 'Setiap 8-12 jam',
    color: 'blue'
  }
};

// ============================================================================
// EXPORT ALL
// ============================================================================

export default {
  VITAL_SIGNS_NORMAL_RANGES,
  CRITICAL_VALUES,
  MEASUREMENT_UNITS,
  MEWS_SCORE,
  EWS_SCORE,
  PAIN_SCALE,
  GCS_SCALE,
  VALIDATION_RULES,
  TREND_INDICATORS,
  determineTrend,
  COMMON_LABELS,
  VITAL_SIGN_CATEGORIES,
  MONITORING_FREQUENCY
};
