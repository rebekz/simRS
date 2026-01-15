/**
 * Emergency Triage Calculation Utility
 *
 * Simplified triage algorithm for rapid patient assessment in IGD.
 * Based on the Emergency Triage System (ETS) principles.
 *
 * Triage Levels:
 * - MERAH: Gawat Darurat (Emergency) - score >= 5
 * - KUNING: Semi-Urgent - score >= 3
 * - HIJAU: Non-Urgent - score < 3
 */

export interface RapidVitalsInput {
  bloodPressureSystolic: number;
  bloodPressureDiastolic: number;
  heartRate: number;
  respiratoryRate: number;
  oxygenSaturation: number;
  temperature: number;
  glasgowComaScale?: number;
  painScore?: number;
}

export interface TriageResult {
  level: 'merah' | 'kuning' | 'hijau';
  label: string;
  description: string;
  score: number;
  criticalFindings: string[];
  recommendations: string[];
  colorClass: string;
  bgColorClass: string;
  priority: number;
}

/**
 * Calculate triage level from vital signs
 * Returns triage result with color coding, findings, and recommendations
 */
export function calculateTriage(vitals: RapidVitalsInput): TriageResult {
  let score = 0;
  const criticalFindings: string[] = [];

  // Blood Pressure Assessment
  if (vitals.bloodPressureSystolic < 90 || vitals.bloodPressureDiastolic < 60) {
    score += 3;
    criticalFindings.push('Hipotensi berat (TD < 90/60 mmHg)');
  } else if (vitals.bloodPressureSystolic > 180 || vitals.bloodPressureDiastolic > 110) {
    score += 1;
    criticalFindings.push('Hipertensi berat (TD > 180/110 mmHg)');
  }

  // Heart Rate Assessment
  if (vitals.heartRate > 120) {
    score += 2;
    criticalFindings.push(`Takikardia berat (${vitals.heartRate} x/menit)`);
  } else if (vitals.heartRate < 50) {
    score += 2;
    criticalFindings.push(`Bradikardia (${vitals.heartRate} x/menit)`);
  }

  // Respiratory Rate Assessment
  if (vitals.respiratoryRate > 24) {
    score += 2;
    criticalFindings.push(`Takipnea berat (${vitals.respiratoryRate} x/menit)`);
  } else if (vitals.respiratoryRate < 10) {
    score += 2;
    criticalFindings.push(`Bradipnea (${vitals.respiratoryRate} x/menit)`);
  }

  // Oxygen Saturation Assessment
  if (vitals.oxygenSaturation < 90) {
    score += 3;
    criticalFindings.push(`Hipokemia berat (SpO2 ${vitals.oxygenSaturation}%)`);
  } else if (vitals.oxygenSaturation < 94) {
    score += 1;
    criticalFindings.push(`Hipokemia ringan (SpO2 ${vitals.oxygenSaturation}%)`);
  }

  // Temperature Assessment
  if (vitals.temperature < 35) {
    score += 2;
    criticalFindings.push(`Hipotermia (${vitals.temperature.toFixed(1)}°C)`);
  } else if (vitals.temperature > 40) {
    score += 2;
    criticalFindings.push(`Hiperpireksia (${vitals.temperature.toFixed(1)}°C)`);
  }

  // Glasgow Coma Scale Assessment
  if (vitals.glasgowComaScale !== undefined) {
    if (vitals.glasgowComaScale < 9) {
      score += 3;
      criticalFindings.push(`GCS sangat rendah (${vitals.glasgowComaScale}/15) - Coma`);
    } else if (vitals.glasgowComaScale < 14) {
      score += 2;
      criticalFindings.push(`GCS menurun (${vitals.glasgowComaScale}/15)`);
    }
  }

  // Pain Score Assessment
  if (vitals.painScore !== undefined && vitals.painScore >= 8) {
    score += 1;
    criticalFindings.push(`Nyeri berat (skor ${vitals.painScore}/10)`);
  }

  // Determine triage level
  let level: 'merah' | 'kuning' | 'hijau';
  let label: string;
  let description: string;
  let recommendations: string[];
  let colorClass: string;
  let bgColorClass: string;
  let priority: number;

  if (score >= 5) {
    level = 'merah';
    label = 'MERAH (Resusitasi)';
    description = 'Gawat Darurat - Ancaman nyawa segera. Perlu tindakan instan.';
    recommendations = [
      'Segera panggil tim resusitasi',
      'Pasang infus & oksigen segera',
      'Monitoring ECG kontinyu',
      'Siapkan alat resusitasi',
      'Dokter IGD harus segera memeriksa'
    ];
    colorClass = 'text-red-700';
    bgColorClass = 'bg-red-50 border-red-500';
    priority = 1;
  } else if (score >= 3) {
    level = 'kuning';
    label = 'KUNING (Urgent)';
    description = 'Kondisi serius - Perlu tindakan segera. Risiko kemunduran cepat.';
    recommendations = [
      'Prioritasi pemeriksaan medis',
      'Monitoring vital signs setiap 15 menit',
      'Dokter harus memeriksa dalam 30 menit',
      'Siapkan tindakan darurat jika kemunduran'
    ];
    colorClass = 'text-yellow-700';
    bgColorClass = 'bg-yellow-50 border-yellow-500';
    priority = 2;
  } else {
    level = 'hijau';
    label = 'HIJAU (Non-Urgent)';
    description = 'Kondisi stabil - Dapat menunggu. Tidak ada risiko kemunduran.';
    recommendations = [
      'Pasien dapat menunggu giliran',
      'Berikan instruksi untuk segera melaporkan perubahan',
      'Dokter memeriksa sesuai antrian',
      'Observasi standar'
    ];
    colorClass = 'text-green-700';
    bgColorClass = 'bg-green-50 border-green-500';
    priority = 3;
  }

  return {
    level,
    label,
    description,
    score,
    criticalFindings,
    recommendations,
    colorClass,
    bgColorClass,
    priority
  };
}

/**
 * Get vital signs normal ranges for adult patients
 */
export function getVitalSignsNormalRanges() {
  return {
    bloodPressureSystolic: { min: 90, max: 140, unit: 'mmHg', label: 'Tekanan Darah Sistolik' },
    bloodPressureDiastolic: { min: 60, max: 90, unit: 'mmHg', label: 'Tekanan Darah Diastolik' },
    heartRate: { min: 60, max: 100, unit: 'x/menit', label: 'Frekuensi Nadi' },
    respiratoryRate: { min: 12, max: 20, unit: 'x/menit', label: 'Frekuensi Napas' },
    oxygenSaturation: { min: 95, max: 100, unit: '%', label: 'Saturasi Oksigen' },
    temperature: { min: 36.0, max: 37.5, unit: '°C', label: 'Suhu Tubuh' },
    glasgowComaScale: { min: 15, max: 15, unit: '/15', label: 'Glasgow Coma Scale' },
    painScore: { min: 0, max: 3, unit: '/10', label: 'Skor Nyeri' }
  };
}

/**
 * Check if a vital sign value is abnormal
 */
export function isVitalSignAbnormal(
  vitalName: keyof RapidVitalsInput,
  value: number
): { isAbnormal: boolean; severity: 'normal' | 'warning' | 'critical' } {
  const ranges = getVitalSignsNormalRanges();
  const range = ranges[vitalName as keyof typeof ranges];

  if (!range) {
    return { isAbnormal: false, severity: 'normal' };
  }

  if (value < range.min || value > range.max) {
    // Determine severity based on deviation
    const deviationPercent = Math.min(
      Math.abs((value - range.min) / range.min) * 100,
      Math.abs((value - range.max) / range.max) * 100
    );

    if (deviationPercent > 30) {
      return { isAbnormal: true, severity: 'critical' };
    }
    return { isAbnormal: true, severity: 'warning' };
  }

  return { isAbnormal: false, severity: 'normal' };
}

/**
 * Format vital sign value with unit
 */
export function formatVitalSign(value: number, unit: string): string {
  if (unit === '°C') {
    return `${value.toFixed(1)}${unit}`;
  }
  return `${value} ${unit}`;
}
