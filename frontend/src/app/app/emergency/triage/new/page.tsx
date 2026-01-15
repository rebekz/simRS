"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { FormInput } from "@/components/ui/form/FormInput";
import { calculateTriage, type RapidVitalsInput, type TriageResult } from "@/lib/triage";
import { Badge } from "@/components/ui/Badge";

interface VitalsFormState {
  bloodPressureSystolic: string;
  bloodPressureDiastolic: string;
  heartRate: string;
  respiratoryRate: string;
  oxygenSaturation: string;
  temperature: string;
  glasgowComaScale: string;
  painScore: string;
}

interface FormErrors {
  [key: string]: string;
}

export default function RapidTriagePage() {
  const router = useRouter();
  const timerRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(Date.now());

  const [formState, setFormState] = useState<VitalsFormState>({
    bloodPressureSystolic: "",
    bloodPressureDiastolic: "",
    heartRate: "",
    respiratoryRate: "",
    oxygenSaturation: "",
    temperature: "",
    glasgowComaScale: "15",
    painScore: "0",
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [triageResult, setTriageResult] = useState<TriageResult | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Timer effect
  useEffect(() => {
    timerRef.current = window.setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
      setElapsedTime(elapsed);
    }, 1000);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  // Auto-calculate triage on form changes
  useEffect(() => {
    const vitals = getVitalsAsNumbers();
    if (hasRequiredVitals(vitals)) {
      const result = calculateTriage(vitals);
      setTriageResult(result);
    } else {
      setTriageResult(null);
    }
  }, [formState]);

  const getVitalsAsNumbers = (): RapidVitalsInput => {
    return {
      bloodPressureSystolic: Number(formState.bloodPressureSystolic) || 0,
      bloodPressureDiastolic: Number(formState.bloodPressureDiastolic) || 0,
      heartRate: Number(formState.heartRate) || 0,
      respiratoryRate: Number(formState.respiratoryRate) || 0,
      oxygenSaturation: Number(formState.oxygenSaturation) || 0,
      temperature: Number(formState.temperature) || 0,
      glasgowComaScale: Number(formState.glasgowComaScale) || 15,
      painScore: Number(formState.painScore) || 0,
    };
  };

  const hasRequiredVitals = (vitals: RapidVitalsInput): boolean => {
    return (
      vitals.bloodPressureSystolic > 0 &&
      vitals.bloodPressureDiastolic > 0 &&
      vitals.heartRate > 0 &&
      vitals.respiratoryRate > 0 &&
      vitals.oxygenSaturation > 0 &&
      vitals.temperature > 0
    );
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formState.bloodPressureSystolic || Number(formState.bloodPressureSystolic) <= 0) {
      newErrors.bloodPressureSystolic = "Tekanan darah sistolik wajib diisi";
    }
    if (!formState.bloodPressureDiastolic || Number(formState.bloodPressureDiastolic) <= 0) {
      newErrors.bloodPressureDiastolic = "Tekanan darah diastolik wajib diisi";
    }
    if (!formState.heartRate || Number(formState.heartRate) <= 0) {
      newErrors.heartRate = "Frekuensi nadi wajib diisi";
    }
    if (!formState.respiratoryRate || Number(formState.respiratoryRate) <= 0) {
      newErrors.respiratoryRate = "Frekuensi napas wajib diisi";
    }
    if (!formState.oxygenSaturation || Number(formState.oxygenSaturation) <= 0) {
      newErrors.oxygenSaturation = "Saturasi oksigen wajib diisi";
    }
    if (!formState.temperature || Number(formState.temperature) <= 0) {
      newErrors.temperature = "Suhu tubuh wajib diisi";
    }

    // Validate ranges
    const systolic = Number(formState.bloodPressureSystolic);
    const diastolic = Number(formState.bloodPressureDiastolic);
    if (systolic > 0 && diastolic > 0 && diastolic >= systolic) {
      newErrors.bloodPressureDiastolic = "Diastolik harus lebih kecil dari sistolik";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    // Simulate API call to save triage
    await new Promise((resolve) => setTimeout(resolve, 500));

    // Navigate to emergency page with result
    router.push("/app/emergency");
  };

  const handleReset = () => {
    setFormState({
      bloodPressureSystolic: "",
      bloodPressureDiastolic: "",
      heartRate: "",
      respiratoryRate: "",
      oxygenSaturation: "",
      temperature: "",
      glasgowComaScale: "15",
      painScore: "0",
    });
    setErrors({});
    setTriageResult(null);
    startTimeRef.current = Date.now();
    setElapsedTime(0);
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const getTimerColor = (): string => {
    if (elapsedTime < 60) return "text-green-600";
    if (elapsedTime < 90) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Triage Cepat IGD</h1>
          <p className="text-gray-600 mt-1">Assessment triage dalam &lt;2 menit</p>
        </div>
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={() => router.push("/app/emergency")}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            Batal
          </button>
        </div>
      </div>

      {/* Timer Card */}
      <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${elapsedTime < 60 ? "border-green-500" : elapsedTime < 90 ? "border-yellow-500" : "border-red-500"}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Waktu Triage</p>
            <p className={`text-4xl font-bold ${getTimerColor()} font-mono`}>
              {formatTime(elapsedTime)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Target</p>
            <p className="text-lg font-medium text-gray-900">&lt; 2 menit</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Vitals Entry Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Tanda Vital</h2>

              {/* Blood Pressure - Combined Input */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <FormInput
                  label="Tekanan Darah Sistolik"
                  type="number"
                  placeholder="120"
                  required
                  error={errors.bloodPressureSystolic}
                  value={formState.bloodPressureSystolic}
                  onChange={(e) => setFormState({ ...formState, bloodPressureSystolic: e.target.value })}
                  hint="mmHg"
                  min={50}
                  max={300}
                  step={1}
                />
                <FormInput
                  label="Tekanan Darah Diastolik"
                  type="number"
                  placeholder="80"
                  required
                  error={errors.bloodPressureDiastolic}
                  value={formState.bloodPressureDiastolic}
                  onChange={(e) => setFormState({ ...formState, bloodPressureDiastolic: e.target.value })}
                  hint="mmHg"
                  min={30}
                  max={200}
                  step={1}
                />
              </div>

              {/* Heart Rate & Respiratory Rate */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <FormInput
                  label="Frekuensi Nadi"
                  type="number"
                  placeholder="80"
                  required
                  error={errors.heartRate}
                  value={formState.heartRate}
                  onChange={(e) => setFormState({ ...formState, heartRate: e.target.value })}
                  hint="x/menit"
                  min={30}
                  max={200}
                  step={1}
                />
                <FormInput
                  label="Frekuensi Napas"
                  type="number"
                  placeholder="16"
                  required
                  error={errors.respiratoryRate}
                  value={formState.respiratoryRate}
                  onChange={(e) => setFormState({ ...formState, respiratoryRate: e.target.value })}
                  hint="x/menit"
                  min={4}
                  max={60}
                  step={1}
                />
              </div>

              {/* SpO2 & Temperature */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <FormInput
                  label="Saturasi Oksigen (SpO2)"
                  type="number"
                  placeholder="98"
                  required
                  error={errors.oxygenSaturation}
                  value={formState.oxygenSaturation}
                  onChange={(e) => setFormState({ ...formState, oxygenSaturation: e.target.value })}
                  hint="%"
                  min={70}
                  max={100}
                  step={1}
                />
                <FormInput
                  label="Suhu Tubuh"
                  type="number"
                  placeholder="36.5"
                  required
                  error={errors.temperature}
                  value={formState.temperature}
                  onChange={(e) => setFormState({ ...formState, temperature: e.target.value })}
                  hint="°C"
                  min={30}
                  max={45}
                  step={0.1}
                />
              </div>

              {/* GCS & Pain Score */}
              <div className="grid grid-cols-2 gap-4">
                <FormInput
                  label="Glasgow Coma Scale"
                  type="number"
                  placeholder="15"
                  value={formState.glasgowComaScale}
                  onChange={(e) => setFormState({ ...formState, glasgowComaScale: e.target.value })}
                  hint="3-15"
                  min={3}
                  max={15}
                  step={1}
                />
                <FormInput
                  label="Skor Nyeri"
                  type="number"
                  placeholder="0"
                  value={formState.painScore}
                  onChange={(e) => setFormState({ ...formState, painScore: e.target.value })}
                  hint="0-10"
                  min={0}
                  max={10}
                  step={1}
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4 border-t">
              <button
                type="button"
                onClick={handleReset}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Reset
              </button>
              <button
                type="submit"
                disabled={!triageResult || isSubmitting}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
              >
                {isSubmitting ? "Menyimpan..." : "Simpan Triage"}
              </button>
            </div>
          </form>
        </div>

        {/* Triage Result Card */}
        <div className="lg:col-span-1">
          {triageResult ? (
            <div className={`rounded-lg shadow border-2 ${triageResult.bgColorClass} p-6 space-y-4 sticky top-6`}>
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Hasil Triage</p>
                <h3 className={`text-xl font-bold ${triageResult.colorClass}`}>
                  {triageResult.label}
                </h3>
                <p className={`text-sm ${triageResult.colorClass} mt-1`}>
                  {triageResult.description}
                </p>
              </div>

              <div className="border-t border-gray-200 pt-4">
                <p className="text-sm text-gray-600 mb-2">Skor Triage</p>
                <p className={`text-3xl font-bold ${triageResult.colorClass}`}>
                  {triageResult.score}
                </p>
              </div>

              {triageResult.criticalFindings.length > 0 && (
                <div className="border-t border-gray-200 pt-4">
                  <p className="text-sm font-medium text-gray-900 mb-2">Temuan Kritis:</p>
                  <ul className="space-y-1">
                    {triageResult.criticalFindings.map((finding, idx) => (
                      <li key={idx} className="text-sm text-red-700 flex items-start">
                        <span className="mr-2">•</span>
                        <span>{finding}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="border-t border-gray-200 pt-4">
                <p className="text-sm font-medium text-gray-900 mb-2">Rekomendasi:</p>
                <ul className="space-y-2">
                  {triageResult.recommendations.map((rec, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start">
                      <span className="mr-2 text-gray-400">{idx + 1}.</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {triageResult.level === "merah" && (
                <div className="border-t border-gray-200 pt-4">
                  <button
                    type="button"
                    className="w-full px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-bold animate-pulse flex items-center justify-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                    AKTIFKAN KODE BIRU
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg shadow p-6 text-center">
              <svg className="w-12 h-12 text-gray-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-gray-600">Isi semua tanda vital untuk melihat hasil triage</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
