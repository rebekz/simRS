"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import type {
  VitalSignsPatientInfo,
  VitalSignsFormState,
  VitalSignsRecord,
  VitalSignsAlert,
  MEWS,
  BloodPressurePosition,
  BloodPressureSite,
  CuffSize,
  HeartRhythm,
  PulseQuality,
  PulseSite,
  BreathingPattern,
  BreathingEffort,
  BreathSound,
  OxygenDelivery,
  TemperatureSite,
  TemperatureCategory,
  SpO2Category,
  BMICategory,
  PainScale,
  PainQuality,
  PainOnset,
  GCSEyeOpening,
  GCSVerbal,
  GCSMotor,
  GlucoseMeasurementType,
  GlucoseTiming,
  GlucoseSampleType,
  GlucoseCategory,
} from "@/types/vital-signs";
import {
  VITAL_SIGNS_NORMAL_RANGES,
  CRITICAL_VALUES,
  MEWS_SCORE,
  PAIN_SCALE,
  GCS_SCALE,
  VALIDATION_RULES,
  COMMON_LABELS,
  determineTrend,
} from "@/constants/vital-signs";

interface PatientSearchResult {
  id: number;
  medical_record_number: string;
  name: string;
  date_of_birth: string;
  gender: "male" | "female";
  bpjs_number?: string;
  bpjs_status?: string;
}

export default function VitalSignsPage() {
  const router = useRouter();

  // Form state
  const [selectedPatient, setSelectedPatient] = useState<VitalSignsPatientInfo | null>(null);
  const [patientSearchQuery, setPatientSearchQuery] = useState("");
  const [patientSearchResults, setPatientSearchResults] = useState<PatientSearchResult[]>([]);
  const [showPatientResults, setShowPatientResults] = useState(false);
  const [searchingPatient, setSearchingPatient] = useState(false);

  // Vital signs measurements
  const [bloodPressureSystolic, setBloodPressureSystolic] = useState<number>(120);
  const [bloodPressureDiastolic, setBloodPressureDiastolic] = useState<number>(80);
  const [bloodPressurePosition, setBloodPressurePosition] = useState<BloodPressurePosition>("sitting");
  const [bloodPressureSite, setBloodPressureSite] = useState<BloodPressureSite>("right_arm");
  const [cuffSize, setCuffSize] = useState<CuffSize>("regular");
  const [bpAutomated, setBpAutomated] = useState<boolean>(false);

  const [heartRate, setHeartRate] = useState<number>(72);
  const [heartRhythm, setHeartRhythm] = useState<HeartRhythm>("regular_sinus");
  const [pulseQuality, setPulseQuality] = useState<PulseQuality>("normal");
  const [heartRateRegular, setHeartRateRegular] = useState<boolean>(true);

  const [respiratoryRate, setRespiratoryRate] = useState<number>(16);
  const [breathingPattern, setBreathingPattern] = useState<BreathingPattern>("regular");
  const [breathingEffort, setBreathingEffort] = useState<BreathingEffort>("normal");
  const [breathSounds, setBreathSounds] = useState<BreathSound>("clear");
  const [onOxygen, setOnOxygen] = useState<boolean>(false);
  const [oxygenDelivery, setOxygenDelivery] = useState<OxygenDelivery>("none");
  const [oxygenFlowRate, setOxygenFlowRate] = useState<number>(0);

  const [temperature, setTemperature] = useState<number>(36.5);
  const [temperatureSite, setTemperatureSite] = useState<TemperatureSite>("oral");
  const [temperatureAutomated, setTemperatureAutomated] = useState<boolean>(false);

  const [spo2, setSpo2] = useState<number>(98);
  const [spo2Category, setSpo2Category] = useState<SpO2Category>("normal");
  const [hasPleth, setHasPleth] = useState<boolean>(true);

  const [weight, setWeight] = useState<number>(65);
  const [height, setHeight] = useState<number>(165);
  const [bmi, setBmi] = useState<number>(0);
  const [bmiCategory, setBmiCategory] = useState<BMICategory>("normal");

  const [painScore, setPainScore] = useState<number>(0);
  const [painLocation, setPainLocation] = useState<string>("");
  const [painQuality, setPainQuality] = useState<PainQuality[]>([]);
  const [painDuration, setPainDuration] = useState<string>("");
  const [painOnset, setPainOnset] = useState<PainOnset>("acute");

  const [gcsEye, setGcsEye] = useState<GCSEyeOpening>("spontaneous");
  const [gcsVerbal, setGcsVerbal] = useState<GCSVerbal>("oriented");
  const [gcsMotor, setGcsMotor] = useState<GCSMotor>("obeys");
  const [gcsTotal, setGcsTotal] = useState<number>(15);

  const [bloodGlucose, setBloodGlucose] = useState<number>(0);
  const [glucoseType, setGlucoseType] = useState<GlucoseMeasurementType>("random");
  const [glucoseTiming, setGlucoseTiming] = useState<GlucoseTiming>("pre_meal");
  const [glucoseSampleType, setGlucoseSampleType] = useState<GlucoseSampleType>("capillary");
  const [glucoseCategory, setGlucoseCategory] = useState<GlucoseCategory>("normal");

  // Clinical context
  const [measurementDateTime, setMeasurementDateTime] = useState<string>(
    new Date().toISOString().slice(0, 16)
  );
  const [measurementLocation, setMeasurementLocation] = useState<string>("ward");
  const [deviceUsed, setDeviceUsed] = useState<string>("");
  const [clinicalNotes, setClinicalNotes] = useState<string>("");
  const [symptoms, setSymptoms] = useState<string>("");
  const [actionsTaken, setActionsTaken] = useState<string>("");

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [alerts, setAlerts] = useState<VitalSignsAlert[]>([]);
  const [mewsScore, setMewsScore] = useState<MEWS | null>(null);
  const [vitalsHistory, setVitalsHistory] = useState<VitalSignsRecord[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  // Check authentication
  useEffect(() => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
    }
  }, [router]);

  // Calculate BMI when weight or height changes
  useEffect(() => {
    if (weight > 0 && height > 0) {
      const heightInMeters = height / 100;
      const calculatedBMI = weight / (heightInMeters * heightInMeters);
      setBmi(Math.round(calculatedBMI * 10) / 10);

      // Determine BMI category (WHO Asia-Pacific for Indonesians)
      let category: BMICategory = "normal";
      if (calculatedBMI < 16) category = "underweight_severe";
      else if (calculatedBMI < 17) category = "underweight_moderate";
      else if (calculatedBMI < 18.5) category = "underweight_mild";
      else if (calculatedBMI < 23) category = "normal";
      else if (calculatedBMI < 25) category = "overweight";
      else if (calculatedBMI < 30) category = "obese_I";
      else category = "obese_II";

      setBmiCategory(category);
    }
  }, [weight, height]);

  // Calculate GCS total
  useEffect(() => {
    const eyeScores = { spontaneous: 4, to_sound: 3, to_pressure: 2, none: 1 };
    const verbalScores = { oriented: 5, confused: 4, inappropriate: 3, incomprehensible: 2, none: 1 };
    const motorScores = { obeys: 6, localizes: 5, withdraws: 4, abnormal_flexion: 3, extension: 2, none: 1 };

    const total = eyeScores[gcsEye] + verbalScores[gcsVerbal] + motorScores[gcsMotor];
    setGcsTotal(total);
  }, [gcsEye, gcsVerbal, gcsMotor]);

  // Determine SpO2 category
  useEffect(() => {
    let category: SpO2Category = "normal";
    if (spo2 >= 95) category = "normal";
    else if (spo2 >= 91) category = "mild_hypoxia";
    else if (spo2 >= 85) category = "moderate_hypoxia";
    else if (spo2 >= 70) category = "severe_hypoxia";
    else category = "critical";

    setSpo2Category(category);
  }, [spo2]);

  // Determine glucose category
  useEffect(() => {
    if (bloodGlucose === 0) return;

    let category: GlucoseCategory = "normal";
    if (bloodGlucose < 40) category = "hypoglycemia_severe";
    else if (bloodGlucose < 70) category = "hypoglycemia_moderate";
    else if (bloodGlucose < 100 && glucoseType === "fasting") category = "normal";
    else if (bloodGlucose < 140 && glucoseType === "random") category = "normal";
    else if (bloodGlucose < 126 && glucoseType === "fasting") category = "impaired";
    else if (bloodGlucose < 200 && glucoseType === "random") category = "impaired";
    else category = "hyperglycemia";

    setGlucoseCategory(category);
  }, [bloodGlucose, glucoseType]);

  // Calculate MEWS score
  useEffect(() => {
    if (heartRate > 0 && bloodPressureSystolic > 0 && respiratoryRate > 0 && temperature > 0) {
      let mewsTotal = 0;

      // Heart rate score
      if (heartRate <= 40) mewsTotal += 3;
      else if (heartRate <= 50) mewsTotal += 1;
      else if (heartRate <= 100) mewsTotal += 0;
      else if (heartRate <= 110) mewsTotal += 1;
      else if (heartRate <= 130) mewsTotal += 2;
      else mewsTotal += 3;

      // Systolic BP score
      if (bloodPressureSystolic <= 70) mewsTotal += 3;
      else if (bloodPressureSystolic <= 80) mewsTotal += 2;
      else if (bloodPressureSystolic <= 100) mewsTotal += 1;
      else if (bloodPressureSystolic <= 199) mewsTotal += 0;
      else mewsTotal += 3;

      // Respiratory rate score
      if (respiratoryRate <= 8) mewsTotal += 3;
      else if (respiratoryRate <= 11) mewsTotal += 1;
      else if (respiratoryRate <= 20) mewsTotal += 0;
      else if (respiratoryRate <= 25) mewsTotal += 2;
      else mewsTotal += 3;

      // Temperature score
      if (temperature <= 35) mewsTotal += 3;
      else if (temperature <= 36) mewsTotal += 1;
      else if (temperature <= 37.5) mewsTotal += 0;
      else if (temperature <= 38.5) mewsTotal += 1;
      else mewsTotal += 3;

      // Consciousness score (based on GCS)
      if (gcsTotal >= 14) mewsTotal += 0;
      else if (gcsTotal >= 11) mewsTotal += 1;
      else if (gcsTotal >= 9) mewsTotal += 2;
      else mewsTotal += 3;

      // Determine category
      let category = "low";
      if (mewsTotal >= 7) category = "critical";
      else if (mewsTotal >= 5) category = "high";
      else if (mewsTotal >= 3) category = "medium";

      setMewsScore({
        total_score: mewsTotal,
        category: category as any,
        components: {
          systolic_bp_score: 0,
          heart_rate_score: 0,
          respiratory_rate_score: 0,
          temperature_score: 0,
          consciousness_score: 0,
        },
        calculated_at: new Date().toISOString(),
        recommended_action: "routine_observations" as any,
        requires_rrt: mewsTotal >= 5,
        requires_icu: mewsTotal >= 7,
      });
    }
  }, [heartRate, bloodPressureSystolic, respiratoryRate, temperature, gcsTotal]);

  // Generate alerts based on vital signs
  useEffect(() => {
    const newAlerts: VitalSignsAlert[] = [];

    // Blood pressure alerts
    if (bloodPressureSystolic > 0) {
      if (bloodPressureSystolic >= CRITICAL_VALUES.bloodPressure.systolic.criticalHigh.value) {
        newAlerts.push({
          vital_sign_type: "blood_pressure",
          severity: "critical",
          category: "critical_high",
          actual_value: bloodPressureSystolic,
          normal_range: { min: 90, max: 120, age_adjusted: false },
          critical_thresholds: {
            critical_high: CRITICAL_VALUES.bloodPressure.systolic.criticalHigh.value,
            warning_high: CRITICAL_VALUES.bloodPressure.systolic.warningHigh.value,
          },
          message_id: "bp_critical_high",
          message: "Hipertensi Darurat - Segera evaluasi dan beri terapi",
          suggested_actions: ["Evaluasi status neurologis", "Konsultasikan dengan dokter", "Pantau tanda vital setiap 5 menit"],
          requires_immediate_notification: true,
        });
      } else if (bloodPressureSystolic <= CRITICAL_VALUES.bloodPressure.systolic.criticalLow.value) {
        newAlerts.push({
          vital_sign_type: "blood_pressure",
          severity: "critical",
          category: "critical_low",
          actual_value: bloodPressureSystolic,
          normal_range: { min: 90, max: 120, age_adjusted: false },
          critical_thresholds: {
            critical_low: CRITICAL_VALUES.bloodPressure.systolic.criticalLow.value,
            warning_low: CRITICAL_VALUES.bloodPressure.systolic.warningLow.value,
          },
          message_id: "bp_critical_low",
          message: "Hipotensi Berat - Segera beri resusitasi cairan",
          suggested_actions: ["Pasang infus jika belum ada", "Berikan cairan resusitasi", "Elevasi ekstremitas bawah"],
          requires_immediate_notification: true,
        });
      }
    }

    // Temperature alerts
    if (temperature > 0) {
      if (temperature >= CRITICAL_VALUES.temperature.criticalHigh.value) {
        newAlerts.push({
          vital_sign_type: "temperature",
          severity: "critical",
          category: "critical_high",
          actual_value: temperature,
          normal_range: { min: 36.1, max: 37.5, age_adjusted: false },
          critical_thresholds: {
            critical_high: CRITICAL_VALUES.temperature.criticalHigh.value,
            warning_high: CRITICAL_VALUES.temperature.warningHigh.value,
          },
          message_id: "temp_critical_high",
          message: "Hipertermi Berat - Segera beri tindakan pendinginan",
          suggested_actions: ["Kompres dingin", "Berikan antipiretik", "Pantau suhu setiap 15 menit"],
          requires_immediate_notification: true,
        });
      } else if (temperature <= CRITICAL_VALUES.temperature.criticalLow.value) {
        newAlerts.push({
          vital_sign_type: "temperature",
          severity: "critical",
          category: "critical_low",
          actual_value: temperature,
          normal_range: { min: 36.1, max: 37.5, age_adjusted: false },
          critical_thresholds: {
            critical_low: CRITICAL_VALUES.temperature.criticalLow.value,
            warning_low: CRITICAL_VALUES.temperature.warningLow.value,
          },
          message_id: "temp_critical_low",
          message: "Hipotermi Berat - Segera beri tindakan pemanasan",
          suggested_actions: ["Ganti selimut hangat", "Berikan cairan hangat", "Pantau suhu setiap 15 menit"],
          requires_immediate_notification: true,
        });
      }
    }

    // Heart rate alerts
    if (heartRate > 0) {
      if (heartRate >= CRITICAL_VALUES.heartRate.criticalHigh.value) {
        newAlerts.push({
          vital_sign_type: "heart_rate",
          severity: "critical",
          category: "critical_high",
          actual_value: heartRate,
          normal_range: { min: 60, max: 100, age_adjusted: false },
          critical_thresholds: {
            critical_high: CRITICAL_VALUES.heartRate.criticalHigh.value,
            warning_high: CRITICAL_VALUES.heartRate.warningHigh.value,
          },
          message_id: "hr_critical_high",
          message: "Takikardi Berat - Evaluasi ritme jantung",
          suggested_actions: ["Pasang EKG monitoring", "Periksa nadi perifer", "Konsultasikan dengan dokter"],
          requires_immediate_notification: true,
        });
      } else if (heartRate <= CRITICAL_VALUES.heartRate.criticalLow.value) {
        newAlerts.push({
          vital_sign_type: "heart_rate",
          severity: "critical",
          category: "critical_low",
          actual_value: heartRate,
          normal_range: { min: 60, max: 100, age_adjusted: false },
          critical_thresholds: {
            critical_low: CRITICAL_VALUES.heartRate.criticalLow.value,
            warning_low: CRITICAL_VALUES.heartRate.warningLow.value,
          },
          message_id: "hr_critical_low",
          message: "Bradikardi Berat - Evaluasi ritme jantung",
          suggested_actions: ["Pasang EKG monitoring", "Periksa tingkat kesadaran", "Siapkan peralatan resusitasi"],
          requires_immediate_notification: true,
        });
      }
    }

    // SpO2 alerts
    if (spo2 > 0 && spo2 <= CRITICAL_VALUES.oxygenSaturation.criticalLow.value) {
      newAlerts.push({
        vital_sign_type: "spo2",
        severity: "critical",
        category: "critical_low",
        actual_value: spo2,
        normal_range: { min: 95, max: 100, age_adjusted: false },
        critical_thresholds: {
          critical_low: CRITICAL_VALUES.oxygenSaturation.criticalLow.value,
          warning_low: CRITICAL_VALUES.oxygenSaturation.warningLow.value,
        },
        message_id: "spo2_critical_low",
        message: "Hipoksemia Berat - Segera beri oksigen tambahan",
        suggested_actions: ["Berikan oksigen tambahan", "Evaluasi jalan napas", "Siapkan intubasi jika perlu"],
        requires_immediate_notification: true,
      });
    }

    // Respiratory rate alerts
    if (respiratoryRate > 0) {
      if (respiratoryRate >= CRITICAL_VALUES.respiratoryRate.criticalHigh.value) {
        newAlerts.push({
          vital_sign_type: "respiratory_rate",
          severity: "critical",
          category: "critical_high",
          actual_value: respiratoryRate,
          normal_range: { min: 12, max: 20, age_adjusted: false },
          critical_thresholds: {
            critical_high: CRITICAL_VALUES.respiratoryRate.criticalHigh.value,
            warning_high: CRITICAL_VALUES.respiratoryRate.warningHigh.value,
          },
          message_id: "rr_critical_high",
          message: "Tahipnea Berat - Evaluasi status pernapasan",
          suggested_actions: ["Evaluasi jalan napas", "Periksa bunyi napas", "Pertimbangkan oksigen tambahan"],
          requires_immediate_notification: true,
        });
      } else if (respiratoryRate <= CRITICAL_VALUES.respiratoryRate.criticalLow.value) {
        newAlerts.push({
          vital_sign_type: "respiratory_rate",
          severity: "critical",
          category: "critical_low",
          actual_value: respiratoryRate,
          normal_range: { min: 12, max: 20, age_adjusted: false },
          critical_thresholds: {
            critical_low: CRITICAL_VALUES.respiratoryRate.criticalLow.value,
            warning_low: CRITICAL_VALUES.respiratoryRate.warningLow.value,
          },
          message_id: "rr_critical_low",
          message: "Bradipnea Berat - Evaluasi status pernapasan",
          suggested_actions: ["Evaluasi kesadaran", "Siapkan peralatan resusitasi", "Panggil dokter segera"],
          requires_immediate_notification: true,
        });
      }
    }

    // Pain score alerts
    if (painScore >= 7) {
      newAlerts.push({
        vital_sign_type: "pain_score",
        severity: "high",
        category: "too_high",
        actual_value: painScore,
        normal_range: { min: 0, max: 3, age_adjusted: false },
        critical_thresholds: {
          critical_high: 10,
          warning_high: 7,
        },
        message_id: "pain_severe",
        message: `Nyeri Berat (Skala ${painScore}/10) - Evaluasi dan beri analgesik`,
        suggested_actions: ["Evaluasi lokasi dan karakter nyeri", "Berikan analgesik sesuai order", "Dokumentasikan respons"],
        requires_immediate_notification: false,
      });
    }

    setAlerts(newAlerts);
  }, [
    bloodPressureSystolic,
    temperature,
    heartRate,
    spo2,
    respiratoryRate,
    painScore,
  ]);

  // Search patients
  const searchPatients = async (query: string) => {
    if (!query || query.length < 2) {
      setPatientSearchResults([]);
      setShowPatientResults(false);
      return;
    }

    setSearchingPatient(true);
    const token = localStorage.getItem("staff_access_token");

    try {
      const response = await fetch(
        `/api/v1/patients/search?q=${encodeURIComponent(query)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Gagal mencari pasien");
      }

      const data = await response.json();
      setPatientSearchResults(data.patients || []);
      setShowPatientResults(true);
    } catch (err) {
      console.error("Error searching patients:", err);
      setPatientSearchResults([]);
    } finally {
      setSearchingPatient(false);
    }
  };

  // Debounced patient search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchPatients(patientSearchQuery);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [patientSearchQuery]);

  // Fetch vital signs history
  const fetchVitalsHistory = async (patientId: number) => {
    setLoadingHistory(true);
    const token = localStorage.getItem("staff_access_token");

    try {
      const response = await fetch(
        `/api/v1/clinical/vitals/history/${patientId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Gagal mengambil riwayat tanda vital");
      }

      const data = await response.json();
      setVitalsHistory(data.records || []);
    } catch (err) {
      console.error("Error fetching vitals history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  // Select patient
  const handleSelectPatient = (patient: PatientSearchResult) => {
    setSelectedPatient({
      patient_id: patient.id.toString(),
      rm_number: patient.medical_record_number,
      name: patient.name,
      date_of_birth: patient.date_of_birth,
      gender: patient.gender,
    });
    setShowPatientResults(false);
    setPatientSearchQuery("");
    fetchVitalsHistory(patient.id);
  };

  // Save vital signs
  const handleSaveVitals = async () => {
    if (!selectedPatient) {
      setError("Pilih pasien terlebih dahulu");
      return;
    }

    // Validation
    if (
      !bloodPressureSystolic ||
      !bloodPressureDiastolic ||
      !heartRate ||
      !respiratoryRate ||
      !temperature ||
      !spo2
    ) {
      setError("Lengkapi semua tanda vital wajib");
      return;
    }

    if (bloodPressureSystolic <= bloodPressureDiastolic) {
      setError("Tekanan darah sistolik harus lebih tinggi dari diastolik");
      return;
    }

    setLoading(true);
    setError(null);
    const token = localStorage.getItem("staff_access_token");

    try {
      const response = await fetch("/api/v1/clinical/vitals", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          patient_id: selectedPatient.patient_id,
          measurements: {
            blood_pressure: {
              systolic: bloodPressureSystolic,
              diastolic: bloodPressureDiastolic,
              position: bloodPressurePosition,
              site: bloodPressureSite,
              cuff_size: cuffSize,
              is_automated: bpAutomated,
            },
            heart_rate: {
              rate: heartRate,
              rhythm: heartRhythm,
              pulse_quality: pulseQuality,
              pulse_sites: ["radial"],
              is_regular: heartRateRegular,
            },
            respiratory_rate: {
              rate: respiratoryRate,
              pattern: breathingPattern,
              effort: breathingEffort,
              breath_sounds: breathSounds,
              oxygen_delivery: onOxygen ? oxygenDelivery : "none",
              oxygen_flow_rate: onOxygen ? oxygenFlowRate : undefined,
              is_in_distress: false,
            },
            temperature: {
              value: temperature,
              unit: "celsius",
              site: temperatureSite,
              category: temperatureCategory(temperature),
              is_automated: temperatureAutomated,
            },
            spo2: {
              saturation: spo2,
              on_oxygen: onOxygen,
              oxygen_delivery: onOxygen ? oxygenDelivery : undefined,
              oxygen_flow_rate: onOxygen ? oxygenFlowRate : undefined,
              category: spo2Category,
              has_pleth: hasPleth,
            },
            weight: {
              value: weight,
              unit: "kg",
              type: "actual",
              is_able_to_stand: true,
              is_estimated: false,
            },
            height: {
              value: height,
              unit: "cm",
              type: "standing",
              is_able_to_stand: true,
              is_estimated: false,
            },
            bmi: {
              value: bmi,
              category: bmiCategory,
              is_calculated: true,
            },
            pain_score: painScore > 0 ? {
              score: painScore,
              scale: "numeric_0_10",
              location: painLocation,
              quality: painQuality,
              duration: painDuration,
              onset: painOnset,
            } : undefined,
            gcs: {
              eye_opening: gcsEye,
              verbal: gcsVerbal,
              motor: gcsMotor,
              total_score: gcsTotal,
              category: gcsTotal >= 13 ? "mild_injury" : gcsTotal >= 9 ? "moderate_injury" : "severe_injury",
            },
            blood_glucose: bloodGlucose > 0 ? {
              value: bloodGlucose,
              type: glucoseType,
              timing: glucoseTiming,
              category: glucoseCategory,
              sample_type: glucoseSampleType,
            } : undefined,
          },
          context: {
            location: measurementLocation as any,
            device: {
              device_type: "manual",
              is_functional: true,
            },
            performer: {
              id: "1",
              name: "Perawat",
              role: "nurse",
            },
            timestamp: measurementDateTime,
          },
          alerts: {
            alerts: alerts,
            critical_count: alerts.filter(a => a.severity === "critical").length,
            high_count: alerts.filter(a => a.severity === "high").length,
            moderate_count: alerts.filter(a => a.severity === "moderate").length,
            overall_status: alerts.length > 0 ? "warning" : "normal",
          },
          ews_scores: mewsScore ? {
            mews: mewsScore,
            relevant_score: "mews",
          } : undefined,
          notes: clinicalNotes,
        }),
      });

      if (!response.ok) {
        throw new Error("Gagal menyimpan tanda vital");
      }

      const data = await response.json();
      setSuccessMessage("Tanda vital berhasil disimpan");
      setTimeout(() => {
        router.push(`/app/clinical/vitals/${data.vital_signs_id}`);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan tanda vital");
    } finally {
      setLoading(false);
    }
  };

  // Helper function to determine temperature category
  const temperatureCategory = (temp: number): TemperatureCategory => {
    if (temp < 35) return "hypothermia";
    if (temp < 36) return "below_normal";
    if (temp <= 37.5) return "normal";
    if (temp <= 38) return "above_normal";
    if (temp <= 40) return "fever";
    return "hyperpyrexia";
  };

  // Calculate patient age
  const calculateAge = (dateOfBirth: string): number => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  // Print vital signs
  const handlePrint = () => {
    window.print();
  };

  // Export to PDF
  const handleExportPDF = () => {
    alert("Fitur export PDF akan segera tersedia");
  };

  return (
    <div className="space-y-6 print:space-y-4">
      {/* Page Header */}
      <div className="flex justify-between items-center print:hidden">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Pemantauan Tanda Vital</h1>
          <p className="text-gray-600 mt-1">Catat dan monitor tanda vital pasien</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => router.push("/app/clinical")}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Kembali
          </button>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            {showHistory ? "Sembunyikan Riwayat" : "Lihat Riwayat"}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Success Message */}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-3">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <p className="text-green-800">{successMessage}</p>
        </div>
      )}

      {/* Critical Alerts */}
      {alerts.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-red-900 mb-3">
            Peringatan Kritis ({alerts.length})
          </h3>
          <div className="space-y-2">
            {alerts.map((alert, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-white rounded-lg border border-red-200">
                <svg className="w-5 h-5 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div className="flex-1">
                  <p className="font-medium text-red-900">{alert.message}</p>
                  {alert.suggested_actions && (
                    <ul className="mt-2 text-sm text-red-700 list-disc list-inside">
                      {alert.suggested_actions.map((action, i) => (
                        <li key={i}>{action}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* MEWS Score Display */}
      {mewsScore && (
        <div className={`rounded-lg p-4 border-2 ${
          mewsScore.total_score >= 7
            ? "bg-red-50 border-red-500"
            : mewsScore.total_score >= 5
            ? "bg-orange-50 border-orange-500"
            : mewsScore.total_score >= 3
            ? "bg-yellow-50 border-yellow-500"
            : "bg-green-50 border-green-500"
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Skor MEWS</h3>
              <p className="text-sm text-gray-600">
                {mewsScore.total_score >= 7
                  ? "Risiko Kritis - Segera hubungi dokter dan resusitasi"
                  : mewsScore.total_score >= 5
                  ? "Risiko Tinggi - Segera beri tindakan medis"
                  : mewsScore.total_score >= 3
                  ? "Risiko Sedang - Tingkatkan frekuensi pemantauan"
                  : "Risiko Rendah - Pantau rutin"}
              </p>
            </div>
            <div className="text-right">
              <p className="text-4xl font-bold">{mewsScore.total_score}</p>
              <p className="text-sm text-gray-600">dari 15+</p>
            </div>
          </div>
        </div>
      )}

      {/* Patient Selection Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Pilih Pasien</h2>

        <div className="relative">
          <input
            type="text"
            placeholder="Cari berdasarkan No RM, nama, atau nomor BPJS..."
            value={patientSearchQuery}
            onChange={(e) => setPatientSearchQuery(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            disabled={!!selectedPatient}
          />
          {searchingPatient && (
            <div className="absolute right-3 top-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
            </div>
          )}
        </div>

        {/* Patient Search Results */}
        {showPatientResults && patientSearchResults.length > 0 && (
          <div className="mt-4 border border-gray-200 rounded-lg divide-y divide-gray-200 max-h-64 overflow-y-auto">
            {patientSearchResults.map((patient) => (
              <button
                key={patient.id}
                onClick={() => handleSelectPatient(patient)}
                className="w-full px-4 py-3 hover:bg-gray-50 text-left"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{patient.name}</p>
                    <p className="text-sm text-gray-600">
                      {patient.medical_record_number} • {calculateAge(patient.date_of_birth)} tahun •{" "}
                      {patient.gender === "male" ? "Laki-laki" : "Perempuan"}
                    </p>
                  </div>
                  {patient.bpjs_number && (
                    <div className="text-right">
                      <p className="text-xs text-gray-500">BPJS</p>
                      <p className="text-sm font-medium text-gray-900">{patient.bpjs_number}</p>
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Selected Patient Card */}
        {selectedPatient && (
          <div className="mt-4 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-gray-900">{selectedPatient.name}</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {selectedPatient.rm_number} • {calculateAge(selectedPatient.date_of_birth)} tahun •{" "}
                  {selectedPatient.gender === "male" ? "Laki-laki" : "Perempuan"}
                </p>
              </div>
              <button
                onClick={() => {
                  setSelectedPatient(null);
                  setVitalsHistory([]);
                }}
                className="text-gray-400 hover:text-red-600"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Vital Signs History Section */}
      {showHistory && selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Riwayat Tanda Vital</h2>

          {loadingHistory ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : vitalsHistory.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium text-gray-700">Waktu</th>
                    <th className="px-4 py-2 text-center font-medium text-gray-700">TD (mmHg)</th>
                    <th className="px-4 py-2 text-center font-medium text-gray-700">Nadi</th>
                    <th className="px-4 py-2 text-center font-medium text-gray-700">RR</th>
                    <th className="px-4 py-2 text-center font-medium text-gray-700">Suhu (°C)</th>
                    <th className="px-4 py-2 text-center font-medium text-gray-700">SpO2 (%)</th>
                    <th className="px-4 py-2 text-center font-medium text-gray-700">MEWS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {vitalsHistory.slice(0, 10).map((record) => (
                    <tr key={record.id}>
                      <td className="px-4 py-2">
                        {new Date(record.created_at).toLocaleString("id-ID")}
                      </td>
                      <td className="px-4 py-2 text-center">
                        {record.measurements.blood_pressure?.systolic}/
                        {record.measurements.blood_pressure?.diastolic}
                      </td>
                      <td className="px-4 py-2 text-center">
                        {record.measurements.heart_rate?.rate}
                      </td>
                      <td className="px-4 py-2 text-center">
                        {record.measurements.respiratory_rate?.rate}
                      </td>
                      <td className="px-4 py-2 text-center">
                        {record.measurements.temperature?.value}
                      </td>
                      <td className="px-4 py-2 text-center">
                        {record.measurements.spo2?.saturation}
                      </td>
                      <td className="px-4 py-2 text-center">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          (record.ews_scores?.mews?.total_score || 0) >= 7
                            ? "bg-red-100 text-red-700"
                            : (record.ews_scores?.mews?.total_score || 0) >= 5
                            ? "bg-orange-100 text-orange-700"
                            : (record.ews_scores?.mews?.total_score || 0) >= 3
                            ? "bg-yellow-100 text-yellow-700"
                            : "bg-green-100 text-green-700"
                        }`}>
                          {record.ews_scores?.mews?.total_score || 0}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>Belum ada riwayat tanda vital</p>
            </div>
          )}
        </div>
      )}

      {/* Basic Vital Signs Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Tanda Vital Dasar</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Blood Pressure */}
            <div className={`p-4 rounded-lg border-2 ${
              bloodPressureSystolic >= CRITICAL_VALUES.bloodPressure.systolic.criticalHigh.value ||
              bloodPressureSystolic <= CRITICAL_VALUES.bloodPressure.systolic.criticalLow.value
                ? "bg-red-50 border-red-500"
                : bloodPressureSystolic >= CRITICAL_VALUES.bloodPressure.systolic.warningHigh.value ||
                  bloodPressureSystolic <= CRITICAL_VALUES.bloodPressure.systolic.warningLow.value
                ? "bg-yellow-50 border-yellow-500"
                : "bg-gray-50 border-gray-200"
            }`}>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tekanan Darah (mmHg) *
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  value={bloodPressureSystolic}
                  onChange={(e) => setBloodPressureSystolic(Number(e.target.value))}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  min={40}
                  max={300}
                />
                <span className="text-gray-500">/</span>
                <input
                  type="number"
                  value={bloodPressureDiastolic}
                  onChange={(e) => setBloodPressureDiastolic(Number(e.target.value))}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  min={20}
                  max={200}
                />
              </div>
              <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                <select
                  value={bloodPressurePosition}
                  onChange={(e) => setBloodPressurePosition(e.target.value as BloodPressurePosition)}
                  className="px-2 py-1 border border-gray-300 rounded"
                >
                  <option value="sitting">Duduk</option>
                  <option value="supine">Berbaring</option>
                  <option value="standing">Berdiri</option>
                  <option value="left_lateral">Miring Kiri</option>
                </select>
                <select
                  value={bloodPressureSite}
                  onChange={(e) => setBloodPressureSite(e.target.value as BloodPressureSite)}
                  className="px-2 py-1 border border-gray-300 rounded"
                >
                  <option value="right_arm">Lengan Kanan</option>
                  <option value="left_arm">Lengan Kiri</option>
                </select>
              </div>
              <div className="mt-2 flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="bpAuto"
                  checked={bpAutomated}
                  onChange={(e) => setBpAutomated(e.target.checked)}
                  className="rounded"
                />
                <label htmlFor="bpAuto" className="text-xs text-gray-600">Otomatis</label>
              </div>
              <p className="mt-2 text-xs text-gray-500">
                Normal: {VITAL_SIGNS_NORMAL_RANGES.adult.bloodPressure.systolic.min}/
                {VITAL_SIGNS_NORMAL_RANGES.adult.bloodPressure.diastolic.min} -
                {VITAL_SIGNS_NORMAL_RANGES.adult.bloodPressure.systolic.max}/
                {VITAL_SIGNS_NORMAL_RANGES.adult.bloodPressure.diastolic.max}
              </p>
            </div>

            {/* Heart Rate */}
            <div className={`p-4 rounded-lg border-2 ${
              heartRate >= CRITICAL_VALUES.heartRate.criticalHigh.value ||
              heartRate <= CRITICAL_VALUES.heartRate.criticalLow.value
                ? "bg-red-50 border-red-500"
                : heartRate >= CRITICAL_VALUES.heartRate.warningHigh.value ||
                  heartRate <= CRITICAL_VALUES.heartRate.warningLow.value
                ? "bg-yellow-50 border-yellow-500"
                : "bg-gray-50 border-gray-200"
            }`}>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Frekuensi Jantung (x/menit) *
              </label>
              <input
                type="number"
                value={heartRate}
                onChange={(e) => setHeartRate(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                min={0}
                max={300}
              />
              <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                <select
                  value={heartRhythm}
                  onChange={(e) => setHeartRhythm(e.target.value as HeartRhythm)}
                  className="px-2 py-1 border border-gray-300 rounded"
                >
                  <option value="regular_sinus">Reguler</option>
                  <option value="irregular">Tidak Reguler</option>
                  <option value="atrial_fibrillation">Fibrilasi Atrium</option>
                  <option value="tachycardia">Takikardia</option>
                  <option value="bradycardia">Bradikardia</option>
                </select>
                <select
                  value={pulseQuality}
                  onChange={(e) => setPulseQuality(e.target.value as PulseQuality)}
                  className="px-2 py-1 border border-gray-300 rounded"
                >
                  <option value="strong">Kuat</option>
                  <option value="normal">Normal</option>
                  <option value="weak">Lemah</option>
                  <option value="thready">Lemah Sekali</option>
                </select>
              </div>
              <div className="mt-2 flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="hrRegular"
                  checked={heartRateRegular}
                  onChange={(e) => setHeartRateRegular(e.target.checked)}
                  className="rounded"
                />
                <label htmlFor="hrRegular" className="text-xs text-gray-600">Reguler</label>
              </div>
              <p className="mt-2 text-xs text-gray-500">
                Normal: {VITAL_SIGNS_NORMAL_RANGES.adult.heartRate.min}-
                {VITAL_SIGNS_NORMAL_RANGES.adult.heartRate.max} x/menit
              </p>
            </div>

            {/* Respiratory Rate */}
            <div className={`p-4 rounded-lg border-2 ${
              respiratoryRate >= CRITICAL_VALUES.respiratoryRate.criticalHigh.value ||
              respiratoryRate <= CRITICAL_VALUES.respiratoryRate.criticalLow.value
                ? "bg-red-50 border-red-500"
                : respiratoryRate >= CRITICAL_VALUES.respiratoryRate.warningHigh.value ||
                  respiratoryRate <= CRITICAL_VALUES.respiratoryRate.warningLow.value
                ? "bg-yellow-50 border-yellow-500"
                : "bg-gray-50 border-gray-200"
            }`}>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Frekuensi Pernapasan (x/menit) *
              </label>
              <input
                type="number"
                value={respiratoryRate}
                onChange={(e) => setRespiratoryRate(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                min={0}
                max={100}
              />
              <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                <select
                  value={breathingPattern}
                  onChange={(e) => setBreathingPattern(e.target.value as BreathingPattern)}
                  className="px-2 py-1 border border-gray-300 rounded"
                >
                  <option value="regular">Reguler</option>
                  <option value="irregular">Tidak Reguler</option>
                  <option value="cheyne_stokes">Cheyne-Stokes</option>
                  <option value="kussmaul">Kussmaul</option>
                </select>
                <select
                  value={breathingEffort}
                  onChange={(e) => setBreathingEffort(e.target.value as BreathingEffort)}
                  className="px-2 py-1 border border-gray-300 rounded"
                >
                  <option value="normal">Normal</option>
                  <option value="increased">Meningkat</option>
                  <option value="decreased">Menurun</option>
                </select>
              </div>
              <p className="mt-2 text-xs text-gray-500">
                Normal: {VITAL_SIGNS_NORMAL_RANGES.adult.respiratoryRate.min}-
                {VITAL_SIGNS_NORMAL_RANGES.adult.respiratoryRate.max} x/menit
              </p>
            </div>

            {/* Temperature */}
            <div className={`p-4 rounded-lg border-2 ${
              temperature >= CRITICAL_VALUES.temperature.criticalHigh.value ||
              temperature <= CRITICAL_VALUES.temperature.criticalLow.value
                ? "bg-red-50 border-red-500"
                : temperature >= CRITICAL_VALUES.temperature.warningHigh.value ||
                  temperature <= CRITICAL_VALUES.temperature.warningLow.value
                ? "bg-yellow-50 border-yellow-500"
                : "bg-gray-50 border-gray-200"
            }`}>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Suhu Tubuh (°C) *
              </label>
              <input
                type="number"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                min={30}
                max={45}
              />
              <div className="mt-2 flex items-center space-x-2">
                <select
                  value={temperatureSite}
                  onChange={(e) => setTemperatureSite(e.target.value as TemperatureSite)}
                  className="flex-1 px-2 py-1 border border-gray-300 rounded text-xs"
                >
                  <option value="oral">Oral</option>
                  <option value="axillary">Aksila</option>
                  <option value="rectal">Rektal</option>
                  <option value="tympanic">Timpapan</option>
                  <option value="temporal">Dahi</option>
                </select>
                <input
                  type="checkbox"
                  id="tempAuto"
                  checked={temperatureAutomated}
                  onChange={(e) => setTemperatureAutomated(e.target.checked)}
                  className="rounded"
                />
                <label htmlFor="tempAuto" className="text-xs text-gray-600">Auto</label>
              </div>
              <p className="mt-2 text-xs text-gray-500">
                Normal: {VITAL_SIGNS_NORMAL_RANGES.adult.temperature.min}-
                {VITAL_SIGNS_NORMAL_RANGES.adult.temperature.max} °C
              </p>
            </div>

            {/* SpO2 */}
            <div className={`p-4 rounded-lg border-2 ${
              spo2 <= CRITICAL_VALUES.oxygenSaturation.criticalLow.value
                ? "bg-red-50 border-red-500"
                : spo2 <= CRITICAL_VALUES.oxygenSaturation.warningLow.value
                ? "bg-yellow-50 border-yellow-500"
                : "bg-gray-50 border-gray-200"
            }`}>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Saturasi Oksigen (%) *
              </label>
              <input
                type="number"
                value={spo2}
                onChange={(e) => setSpo2(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                min={0}
                max={100}
              />
              <div className="mt-2 flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="onOxygen"
                  checked={onOxygen}
                  onChange={(e) => setOnOxygen(e.target.checked)}
                  className="rounded"
                />
                <label htmlFor="onOxygen" className="text-xs text-gray-600">Oksigen</label>
              </div>
              {onOxygen && (
                <div className="mt-2 grid grid-cols-2 gap-2">
                  <select
                    value={oxygenDelivery}
                    onChange={(e) => setOxygenDelivery(e.target.value as OxygenDelivery)}
                    className="px-2 py-1 border border-gray-300 rounded text-xs"
                  >
                    <option value="nasal_cannula">Nasal</option>
                    <option value="face_mask">Masker</option>
                    <option value="venturi_mask">Venturi</option>
                    <option value="non_rebreather">Non-rebreather</option>
                  </select>
                  <input
                    type="number"
                    placeholder="L/mnt"
                    value={oxygenFlowRate || ""}
                    onChange={(e) => setOxygenFlowRate(Number(e.target.value))}
                    className="px-2 py-1 border border-gray-300 rounded text-xs"
                    min={0}
                    max={15}
                  />
                </div>
              )}
              <p className="mt-2 text-xs text-gray-500">
                Normal: {VITAL_SIGNS_NORMAL_RANGES.adult.oxygenSaturation.min}-
                {VITAL_SIGNS_NORMAL_RANGES.adult.oxygenSaturation.max}%
              </p>
            </div>

            {/* Weight & Height */}
            <div className="p-4 rounded-lg border-2 bg-gray-50 border-gray-200">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Berat & Tinggi Badan
              </label>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-gray-600">Berat (kg)</label>
                  <input
                    type="number"
                    value={weight}
                    onChange={(e) => setWeight(Number(e.target.value))}
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    min={0}
                    max={300}
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-600">Tinggi (cm)</label>
                  <input
                    type="number"
                    value={height}
                    onChange={(e) => setHeight(Number(e.target.value))}
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    min={0}
                    max={300}
                  />
                </div>
              </div>
              {bmi > 0 && (
                <div className="mt-2 p-2 bg-white rounded border border-gray-200">
                  <p className="text-xs text-gray-600">BMI: <span className="font-semibold">{bmi}</span></p>
                  <p className="text-xs text-gray-500 capitalize">{bmiCategory.replace(/_/g, " ")}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Neurological Assessment Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Asesmen Neurologis</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Pain Score */}
            <div className={`p-4 rounded-lg border-2 ${
              painScore >= 7 ? "bg-red-50 border-red-500" :
              painScore >= 4 ? "bg-yellow-50 border-yellow-500" :
              "bg-gray-50 border-gray-200"
            }`}>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Skala Nyeri (0-10)
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={painScore}
                  onChange={(e) => setPainScore(Number(e.target.value))}
                  className="flex-1"
                />
                <span className="text-2xl font-bold w-12 text-center">{painScore}</span>
              </div>
              <div className="mt-2 flex items-center justify-between text-xs text-gray-600">
                <span>Tidak Ada</span>
                <span>Sedang</span>
                <span>Terburuk</span>
              </div>
              {painScore > 0 && (
                <div className="mt-3 space-y-2">
                  <input
                    type="text"
                    placeholder="Lokasi nyeri"
                    value={painLocation}
                    onChange={(e) => setPainLocation(e.target.value)}
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                  <input
                    type="text"
                    placeholder="Durasi nyeri"
                    value={painDuration}
                    onChange={(e) => setPainDuration(e.target.value)}
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </div>
              )}
            </div>

            {/* GCS */}
            <div className={`p-4 rounded-lg border-2 ${
              gcsTotal <= 8 ? "bg-red-50 border-red-500" :
              gcsTotal <= 12 ? "bg-yellow-50 border-yellow-500" :
              "bg-gray-50 border-gray-200"
            }`}>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Glasgow Coma Scale (GCS)
              </label>
              <div className="grid grid-cols-3 gap-2 mb-3">
                <div>
                  <label className="text-xs text-gray-600">Mata (E)</label>
                  <select
                    value={gcsEye}
                    onChange={(e) => setGcsEye(e.target.value as GCSEyeOpening)}
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  >
                    <option value="spontaneous">4 - Spontan</option>
                    <option value="to_sound">3 - Suara</option>
                    <option value="to_pressure">2 - Nyeri</option>
                    <option value="none">1 - Tidak Ada</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-600">Verbal (V)</label>
                  <select
                    value={gcsVerbal}
                    onChange={(e) => setGcsVerbal(e.target.value as GCSVerbal)}
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  >
                    <option value="oriented">5 - Terorientasi</option>
                    <option value="confused">4 - Bingung</option>
                    <option value="inappropriate">3 - Tidak Tepat</option>
                    <option value="incomprehensible">2 - Tidak Jelas</option>
                    <option value="none">1 - Tidak Ada</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-600">Motorik (M)</label>
                  <select
                    value={gcsMotor}
                    onChange={(e) => setGcsMotor(e.target.value as GCSMotor)}
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  >
                    <option value="obeys">6 - Mengikuti</option>
                    <option value="localizes">5 - Lokalisasi</option>
                    <option value="withdraws">4 - Menarik</option>
                    <option value="abnormal_flexion">3 - Fleksi Abnormal</option>
                    <option value="extension">2 - Ekstensi</option>
                    <option value="none">1 - Tidak Ada</option>
                  </select>
                </div>
              </div>
              <div className="flex items-center justify-center">
                <div className="text-center">
                  <p className="text-xs text-gray-600">Total GCS</p>
                  <p className="text-3xl font-bold">{gcsTotal}/15</p>
                </div>
              </div>
            </div>
          </div>

          {/* Blood Glucose */}
          <div className="mt-6 p-4 rounded-lg border-2 bg-gray-50 border-gray-200">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Gula Darah (mg/dL)
            </label>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <input
                type="number"
                placeholder="mg/dL"
                value={bloodGlucose || ""}
                onChange={(e) => setBloodGlucose(Number(e.target.value))}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                min={0}
                max={600}
              />
              <select
                value={glucoseType}
                onChange={(e) => setGlucoseType(e.target.value as GlucoseMeasurementType)}
                className="px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="random">Acak</option>
                <option value="fasting">Puasa</option>
                <option value="postprandial">Postprandial</option>
                <option value="bedtime">Sebelum Tidur</option>
              </select>
              <select
                value={glucoseSampleType}
                onChange={(e) => setGlucoseSampleType(e.target.value as GlucoseSampleType)}
                className="px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="capillary">Kapiler</option>
                <option value="venous">Vena</option>
                <option value="arterial">Arteri</option>
              </select>
              {bloodGlucose > 0 && (
                <div className="flex items-center">
                  <span className={`px-3 py-2 rounded-lg text-sm font-medium ${
                    glucoseCategory === "normal" ? "bg-green-100 text-green-700" :
                    glucoseCategory === "impaired" ? "bg-yellow-100 text-yellow-700" :
                    "bg-red-100 text-red-700"
                  }`}>
                    {glucoseCategory.replace(/_/g, " ")}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Clinical Context & Notes Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Konteks Klinis & Catatan</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tanggal & Waktu Pengukuran
              </label>
              <input
                type="datetime-local"
                value={measurementDateTime}
                onChange={(e) => setMeasurementDateTime(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lokasi Pengukuran
              </label>
              <select
                value={measurementLocation}
                onChange={(e) => setMeasurementLocation(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="ward">Ward</option>
                <option value="icu">ICU</option>
                <option value="emergency">IGD</option>
                <option value="outpatient">Rawat Jalan</option>
                <option value="clinic">Klinik</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Gejala & Observasi
              </label>
              <textarea
                rows={2}
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                placeholder="Catat gejala atau observasi yang ditemukan..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tindakan yang Diberikan
              </label>
              <textarea
                rows={2}
                value={actionsTaken}
                onChange={(e) => setActionsTaken(e.target.value)}
                placeholder="Catat tindakan yang telah diberikan..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Catatan Klinis
              </label>
              <textarea
                rows={3}
                value={clinicalNotes}
                onChange={(e) => setClinicalNotes(e.target.value)}
                placeholder="Tambahkan catatan klinis tambahan..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {selectedPatient && (
        <div className="flex flex-wrap gap-3 justify-end print:hidden">
          <button
            onClick={() => router.push("/app/clinical")}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Batal
          </button>
          <button
            onClick={handlePrint}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Print Preview
          </button>
          <button
            onClick={handleExportPDF}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Export PDF
          </button>
          <button
            onClick={handleSaveVitals}
            disabled={loading}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? "Menyimpan..." : "Simpan Tanda Vital"}
          </button>
        </div>
      )}
    </div>
  );
}
