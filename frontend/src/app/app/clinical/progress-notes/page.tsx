"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import type {
  ProgressNotePatientInfo,
  ProgressNoteType,
  SOAPNote,
  VitalSignsSummary,
  Intervention,
  PatientResponse,
  SideEffect,
  Complication,
  ProgressNotesFormStep,
  FormMode,
  SignOffStatus,
} from "@/types/progress-notes";
import {
  NOTE_TYPES,
  CLINICAL_STATUS,
  CHARACTER_LIMITS,
  SOAP_NOTE_TEMPLATES,
  INTERVENTION_CATEGORIES,
  getNoteTypeLabel,
  getClinicalStatusLabel,
  getClinicalStatusColor,
} from "@/constants/progress-notes";

interface PatientSearchResult {
  id: number;
  medical_record_number: string;
  name: string;
  date_of_birth: string;
  gender: "male" | "female";
  bpjs_number?: string;
  bpjs_status?: string;
}

export default function ProgressNotesPage() {
  const router = useRouter();

  // Form mode
  const [formMode, setFormMode] = useState<FormMode>("create");
  const [currentStep, setCurrentStep] = useState<ProgressNotesFormStep>("patient_info");

  // Patient selection
  const [selectedPatient, setSelectedPatient] = useState<ProgressNotePatientInfo | null>(null);
  const [patientSearchQuery, setPatientSearchQuery] = useState("");
  const [patientSearchResults, setPatientSearchResults] = useState<PatientSearchResult[]>([]);
  const [showPatientResults, setShowPatientResults] = useState(false);
  const [searchingPatient, setSearchingPatient] = useState(false);

  // Note type selection
  const [noteType, setNoteType] = useState<ProgressNoteType>("daily_progress");
  const [noteDateTime, setNoteDateTime] = useState<string>(new Date().toISOString().slice(0, 16));

  // SOAP Note sections
  const [subjective, setSubjective] = useState({
    chief_complaint: "",
    hpi: "",
    condition_description: "",
    concerns: [] as string[],
    notes: "",
  });

  const [objective, setObjective] = useState({
    vital_signs_summary: "",
    physical_exam: "",
    laboratory_results: "",
    imaging_results: "",
    mental_status: "",
    nutrition_status: "",
  });

  const [assessment, setAssessment] = useState({
    primary_diagnosis: "",
    icd_code: "",
    secondary_diagnoses: [] as string[],
    condition_summary: "",
    severity: "moderate" as const,
    clinical_status: "stable" as const,
    progress_status: "stable" as const,
    treatment_response: "good" as const,
    prognosis: "good" as const,
    clinical_reasoning: "",
  });

  const [plan, setPlan] = useState({
    diagnostic_plan: "",
    treatment_plan: "",
    medication_plan: "",
    nursing_plan: "",
    patient_education: "",
    follow_up_plan: "",
    goals: "",
    precautions: "" as string | string[],
    notes: "",
  });

  // Vital Signs
  const [vitalSigns, setVitalSigns] = useState({
    blood_pressure_systolic: 120,
    blood_pressure_diastolic: 80,
    heart_rate: 72,
    respiratory_rate: 16,
    temperature: 36.5,
    spo2: 98,
    pain_score: 0,
  });

  // Interventions
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [newIntervention, setNewIntervention] = useState({
    name: "",
    type: "medication" as const,
    indication: "",
    details: "",
  });

  // Response section
  const [patientResponses, setPatientResponses] = useState<PatientResponse[]>([]);
  const [sideEffects, setSideEffects] = useState<SideEffect[]>([]);
  const [complications, setComplications] = useState<Complication[]>([]);

  // Additional notes
  const [additionalNotes, setAdditionalNotes] = useState("");

  // Sign-off
  const [signOff, setSignOff] = useState<SignOffStatus>({
    is_signed_off: false,
    cosigner_required: false,
    verification_status: "pending",
  });

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  // Check authentication
  useEffect(() => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
    }
  }, [router]);

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

  // Select patient
  const handleSelectPatient = (patient: PatientSearchResult) => {
    setSelectedPatient({
      patient_id: patient.id.toString(),
      rm_number: patient.medical_record_number,
      name: patient.name,
      date_of_birth: patient.date_of_birth,
      age_years: calculateAge(patient.date_of_birth),
      gender: patient.gender,
      allergies: [],
      diagnoses: [],
      current_medications: [],
    });
    setShowPatientResults(false);
    setPatientSearchQuery("");
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

  // Add intervention
  const handleAddIntervention = () => {
    if (!newIntervention.name || !newIntervention.type) {
      setError("Lengkapi data intervensi");
      return;
    }

    const intervention: Intervention = {
      name: newIntervention.name,
      type: newIntervention.type,
      indication: newIntervention.indication,
      details: newIntervention.details,
      performed_by: "CurrentUser",
      performed_at: new Date().toISOString(),
      follow_up_required: false,
    };

    setInterventions([...interventions, intervention]);
    setNewIntervention({
      name: "",
      type: "medication",
      indication: "",
      details: "",
    });
  };

  // Remove intervention
  const handleRemoveIntervention = (index: number) => {
    setInterventions(interventions.filter((_, i) => i !== index));
  };

  // Validate form
  const validateForm = (): boolean => {
    const errors: string[] = [];

    if (!selectedPatient) {
      errors.push("Pilih pasien terlebih dahulu");
    }

    if (!subjective.chief_complaint && !subjective.condition_description) {
      errors.push("Isi keluhan utama atau kondisi pasien");
    }

    if (!assessment.primary_diagnosis) {
      errors.push("Isi diagnosa utama");
    }

    if (!plan.treatment_plan) {
      errors.push("Isi rencana tatalaksana");
    }

    setValidationErrors(errors);
    return errors.length === 0;
  };

  // Save progress note
  const handleSaveNote = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);
    const token = localStorage.getItem("staff_access_token");

    try {
      const soapNote: SOAPNote = {
        subjective: {
          chief_complaint: subjective.chief_complaint,
          hpi: subjective.hpi,
          condition_description: subjective.condition_description,
          concerns: subjective.concerns,
          notes: subjective.notes,
        },
        objective: {
          vital_signs: {
            blood_pressure: {
              systolic: vitalSigns.blood_pressure_systolic,
              diastolic: vitalSigns.blood_pressure_diastolic,
              position: "sitting",
            },
            heart_rate: {
              rate: vitalSigns.heart_rate,
              rhythm: "regular",
            },
            respiratory_rate: {
              rate: vitalSigns.respiratory_rate,
              pattern: "regular",
            },
            temperature: {
              value: vitalSigns.temperature,
              unit: "C",
              site: "oral",
            },
            spo2: {
              saturation: vitalSigns.spo2,
              on_oxygen: false,
            },
            pain_score: vitalSigns.pain_score,
          },
          physical_exam: objective.physical_exam,
          laboratory_results: objective.laboratory_results ? [{ test_name: objective.laboratory_results, result: "", is_abnormal: false, test_datetime: new Date().toISOString() }] : undefined,
        },
        assessment: {
          primary_diagnosis: assessment.primary_diagnosis,
          icd_code: assessment.icd_code,
          secondary_diagnoses: assessment.secondary_diagnoses,
          condition_summary: assessment.condition_summary,
          severity: assessment.severity,
          clinical_status: assessment.clinical_status,
          progress_status: assessment.progress_status,
          treatment_response: assessment.treatment_response,
          prognosis: assessment.prognosis,
          clinical_reasoning: assessment.clinical_reasoning,
        },
        plan: {
          diagnostic_plan: plan.diagnostic_plan ? [{ test_name: plan.diagnostic_plan, test_type: "lab", indication: plan.diagnostic_plan, priority: "routine", timing: "ASAP" }] : undefined,
          treatment_plan: plan.treatment_plan ? [{ treatment: plan.treatment_plan, type: "medication", indication: plan.treatment_plan, frequency: "scheduled", duration: "ongoing", start_date: new Date().toISOString() }] : undefined,
          medication_plan: plan.medication_plan ? [{ medication: plan.medication_plan, dosage: "as prescribed", route: "oral", frequency: "scheduled", indication: plan.medication_plan, duration: "ongoing", is_prn: false, start_date: new Date().toISOString(), prescribed_by: "CurrentUser" }] : undefined,
          nursing_plan: plan.nursing_plan ? [{ intervention: plan.nursing_plan, goal: "improve patient condition", priority: "routine", performed_by: "nurse" }] : undefined,
          patient_education: plan.patient_education ? [{ topic: plan.patient_education, content: plan.patient_education, method: "verbal", understanding: "full", provided_by: "CurrentUser", date_provided: new Date().toISOString(), follow_up_needed: false }] : undefined,
          follow_up: {
            follow_up_needed: !!plan.follow_up_plan,
            timing: plan.follow_up_plan,
          },
          goals: plan.goals ? [{ goal: plan.goals, type: "clinical", achieved: false }] : undefined,
          precautions: Array.isArray(plan.precautions) ? plan.precautions : plan.precautions ? [plan.precautions] : [],
          notes: plan.notes,
        },
      };

      const response = await fetch("/api/v1/clinical/progress-notes", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          patient_id: selectedPatient?.patient_id,
          note_type: noteType,
          soap_note: soapNote,
          interventions: interventions.length > 0 ? interventions : undefined,
          additional_notes: additionalNotes,
        }),
      });

      if (!response.ok) {
        throw new Error("Gagal menyimpan catatan perkembangan");
      }

      const data = await response.json();
      setSuccessMessage("Catatan perkembangan berhasil disimpan");
      setTimeout(() => {
        router.push(`/app/clinical/progress-notes/${data.note_id}`);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal menyimpan catatan perkembangan");
    } finally {
      setLoading(false);
    }
  };

  // Apply SOAP template
  const applySOAPTemplate = (templateKey: keyof typeof SOAP_NOTE_TEMPLATES) => {
    const template = SOAP_NOTE_TEMPLATES[templateKey];
    if (template) {
      setSubjective({
        ...subjective,
        chief_complaint: template.subjective.includes("{complaint}")
          ? subjective.chief_complaint || "keluhan"
          : template.subjective,
        condition_description: template.subjective,
        notes: "",
      });
      setObjective({
        ...objective,
        vital_signs_summary: template.objective,
        physical_exam: "Pemeriksaan fisik dalam batas normal",
      });
      setAssessment({
        ...assessment,
        condition_summary: template.assessment,
      });
      setPlan({
        ...plan,
        treatment_plan: template.plan,
      });
    }
  };

  // Print note
  const handlePrint = () => {
    window.print();
  };

  // Export to PDF
  const handleExportPDF = () => {
    alert("Fitur export PDF akan segera tersedia");
  };

  // Sign note
  const handleSignNote = () => {
    setSignOff({
      ...signOff,
      is_signed_off: true,
      signed_by: "CurrentUser",
      signed_at: new Date().toISOString(),
      signature_type: "electronic",
      verification_status: "verified",
    });
    setSuccessMessage("Catatan telah ditandatangani");
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  return (
    <div className="space-y-6 print:space-y-4">
      {/* Page Header */}
      <div className="flex justify-between items-center print:hidden">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Catatan Perkembangan Pasien</h1>
          <p className="text-gray-600 mt-1">Dokumentasikan perkembangan klinis pasien</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => router.push("/app/clinical")}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Kembali
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

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-yellow-900 mb-2">Mohon lengkapi field berikut:</h3>
          <ul className="text-sm text-yellow-800 list-disc list-inside">
            {validationErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Patient Information Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">1. Informasi Pasien</h2>

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
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Selected Patient Card */}
        {selectedPatient && (
          <div className="mt-4 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
            <div className="flex items-start justify-between">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 flex-1">
                <div>
                  <p className="text-sm text-gray-600">Nama Pasien</p>
                  <p className="font-semibold text-gray-900">{selectedPatient.name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">No RM</p>
                  <p className="font-semibold text-gray-900">{selectedPatient.rm_number}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Usia & Jenis Kelamin</p>
                  <p className="font-semibold text-gray-900">
                    {selectedPatient.age_years} tahun •{" "}
                    {selectedPatient.gender === "male" ? "Laki-laki" : "Perempuan"}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedPatient(null)}
                className="text-gray-400 hover:text-red-600 ml-4"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Note Type Selection */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">2. Tipe Catatan</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            {NOTE_TYPES.map((type) => (
              <button
                key={type.value}
                onClick={() => setNoteType(type.value as ProgressNoteType)}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  noteType === type.value
                    ? "border-indigo-500 bg-indigo-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <p className="font-medium text-gray-900">{type.label}</p>
                <p className="text-sm text-gray-600 mt-1">{type.description}</p>
              </button>
            ))}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tanggal & Waktu Catatan
            </label>
            <input
              type="datetime-local"
              value={noteDateTime}
              onChange={(e) => setNoteDateTime(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>
      )}

      {/* SOAP Note Section - Subjective */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">3. Catatan SOAP</h2>
            <div className="flex gap-2">
              <button
                onClick={() => applySOAPTemplate("daily_progress")}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                Template Harian
              </button>
              <button
                onClick={() => applySOAPTemplate("initial_admission")}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                Template Masuk
              </button>
              <button
                onClick={() => applySOAPTemplate("discharge")}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                Template Pulang
              </button>
            </div>
          </div>

          {/* Subjective */}
          <div className="mb-6">
            <h3 className="text-md font-semibold text-gray-800 mb-3 flex items-center">
              <span className="w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center mr-2 text-sm font-bold">S</span>
              Subjektif (Apa yang dirasakan/dikeluhkan pasien)
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Keluhan Utama *
                </label>
                <textarea
                  rows={2}
                  value={subjective.chief_complaint}
                  onChange={(e) => setSubjective({ ...subjective, chief_complaint: e.target.value })}
                  placeholder="Keluhan utama pasien dalam kata-kata pasien sendiri..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  maxLength={CHARACTER_LIMITS.chief_complaint}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {subjective.chief_complaint.length}/{CHARACTER_LIMITS.chief_complaint} karakter
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Riwayat Penyakit Sekarang
                </label>
                <textarea
                  rows={3}
                  value={subjective.hpi}
                  onChange={(e) => setSubjective({ ...subjective, hpi: e.target.value })}
                  placeholder="Detail riwayat penyakit sekarang..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  maxLength={CHARACTER_LIMITS.subjective}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Kondisi Umum / Deskripsi
                </label>
                <textarea
                  rows={2}
                  value={subjective.condition_description}
                  onChange={(e) => setSubjective({ ...subjective, condition_description: e.target.value })}
                  placeholder="Deskripsi kondisi pasien secara umum..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Catatan Tambahan Subjektif
                </label>
                <textarea
                  rows={2}
                  value={subjective.notes}
                  onChange={(e) => setSubjective({ ...subjective, notes: e.target.value })}
                  placeholder="Catatan tambahan..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* Objective */}
          <div className="mb-6">
            <h3 className="text-md font-semibold text-gray-800 mb-3 flex items-center">
              <span className="w-8 h-8 bg-green-100 text-green-700 rounded-full flex items-center justify-center mr-2 text-sm font-bold">O</span>
              Objektif (Data yang diamati/terukur)
            </h3>

            <div className="space-y-4">
              {/* Vital Signs */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Tanda Vital</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                  <div>
                    <label className="text-xs text-gray-600">TD (mmHg)</label>
                    <div className="flex items-center space-x-1">
                      <input
                        type="number"
                        value={vitalSigns.blood_pressure_systolic}
                        onChange={(e) => setVitalSigns({ ...vitalSigns, blood_pressure_systolic: Number(e.target.value) })}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        min={40}
                        max={300}
                      />
                      <span className="text-gray-400">/</span>
                      <input
                        type="number"
                        value={vitalSigns.blood_pressure_diastolic}
                        onChange={(e) => setVitalSigns({ ...vitalSigns, blood_pressure_diastolic: Number(e.target.value) })}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        min={20}
                        max={200}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-xs text-gray-600">Nadi (x/mnt)</label>
                    <input
                      type="number"
                      value={vitalSigns.heart_rate}
                      onChange={(e) => setVitalSigns({ ...vitalSigns, heart_rate: Number(e.target.value) })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      min={0}
                      max={300}
                    />
                  </div>

                  <div>
                    <label className="text-xs text-gray-600">RR (x/mnt)</label>
                    <input
                      type="number"
                      value={vitalSigns.respiratory_rate}
                      onChange={(e) => setVitalSigns({ ...vitalSigns, respiratory_rate: Number(e.target.value) })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      min={0}
                      max={100}
                    />
                  </div>

                  <div>
                    <label className="text-xs text-gray-600">Suhu (°C)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={vitalSigns.temperature}
                      onChange={(e) => setVitalSigns({ ...vitalSigns, temperature: Number(e.target.value) })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      min={30}
                      max={45}
                    />
                  </div>

                  <div>
                    <label className="text-xs text-gray-600">SpO2 (%)</label>
                    <input
                      type="number"
                      value={vitalSigns.spo2}
                      onChange={(e) => setVitalSigns({ ...vitalSigns, spo2: Number(e.target.value) })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      min={0}
                      max={100}
                    />
                  </div>

                  <div>
                    <label className="text-xs text-gray-600">Nyeri (0-10)</label>
                    <input
                      type="number"
                      value={vitalSigns.pain_score}
                      onChange={(e) => setVitalSigns({ ...vitalSigns, pain_score: Number(e.target.value) })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      min={0}
                      max={10}
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Pemeriksaan Fisik
                </label>
                <textarea
                  rows={3}
                  value={objective.physical_exam}
                  onChange={(e) => setObjective({ ...objective, physical_exam: e.target.value })}
                  placeholder="Hasil pemeriksaan fisik..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hasil Laboratorium
                </label>
                <textarea
                  rows={2}
                  value={objective.laboratory_results}
                  onChange={(e) => setObjective({ ...objective, laboratory_results: e.target.value })}
                  placeholder="Hasil pemeriksaan laboratorium yang relevan..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hasil Radiologi
                </label>
                <textarea
                  rows={2}
                  value={objective.imaging_results}
                  onChange={(e) => setObjective({ ...objective, imaging_results: e.target.value })}
                  placeholder="Hasil pemeriksaan radiologi yang relevan..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status Mental
                </label>
                <textarea
                  rows={1}
                  value={objective.mental_status}
                  onChange={(e) => setObjective({ ...objective, mental_status: e.target.value })}
                  placeholder="Kesadaran dan status mental pasien..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status Nutrisi
                </label>
                <textarea
                  rows={1}
                  value={objective.nutrition_status}
                  onChange={(e) => setObjective({ ...objective, nutrition_status: e.target.value })}
                  placeholder="Status nutrisi dan intake makanan..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* Assessment */}
          <div className="mb-6">
            <h3 className="text-md font-semibold text-gray-800 mb-3 flex items-center">
              <span className="w-8 h-8 bg-yellow-100 text-yellow-700 rounded-full flex items-center justify-center mr-2 text-sm font-bold">A</span>
              Asesmen (Penilaian klinis)
            </h3>

            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Diagnosa Utama *
                  </label>
                  <input
                    type="text"
                    value={assessment.primary_diagnosis}
                    onChange={(e) => setAssessment({ ...assessment, primary_diagnosis: e.target.value })}
                    placeholder="Diagnosa utama..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Kode ICD-10
                  </label>
                  <input
                    type="text"
                    value={assessment.icd_code}
                    onChange={(e) => setAssessment({ ...assessment, icd_code: e.target.value })}
                    placeholder="Kode ICD-10..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ringkasan Kondisi
                </label>
                <textarea
                  rows={2}
                  value={assessment.condition_summary}
                  onChange={(e) => setAssessment({ ...assessment, condition_summary: e.target.value })}
                  placeholder="Ringkasan kondisi klinis pasien..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Keparahan
                  </label>
                  <select
                    value={assessment.severity}
                    onChange={(e) => setAssessment({ ...assessment, severity: e.target.value as any })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="mild">Ringan</option>
                    <option value="moderate">Sedang</option>
                    <option value="severe">Berat</option>
                    <option value="critical">Kritis</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status Klinis
                  </label>
                  <select
                    value={assessment.clinical_status}
                    onChange={(e) => setAssessment({ ...assessment, clinical_status: e.target.value as any })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="stable">Stabil</option>
                    <option value="improving">Membaik</option>
                    <option value="deteriorating">Memburuk</option>
                    <option value="critical">Kritis</option>
                    <option value="unchanged">Tidak Berubah</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Progress
                  </label>
                  <select
                    value={assessment.progress_status}
                    onChange={(e) => setAssessment({ ...assessment, progress_status: e.target.value as any })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="improving">Membaik</option>
                    <option value="stable">Stabil</option>
                    <option value="worsening">Memburuk</option>
                    <option value="resolved">Sembuh</option>
                    <option value="complicated">Komplikasi</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Respon Terapi
                  </label>
                  <select
                    value={assessment.treatment_response}
                    onChange={(e) => setAssessment({ ...assessment, treatment_response: e.target.value as any })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="excellent">Sangat Baik</option>
                    <option value="good">Baik</option>
                    <option value="fair">Cukup</option>
                    <option value="poor">Buruk</option>
                    <option value="none">Tidak Ada</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prognosis
                </label>
                <select
                  value={assessment.prognosis}
                  onChange={(e) => setAssessment({ ...assessment, prognosis: e.target.value as any })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="excellent">Sangat Baik</option>
                  <option value="good">Baik</option>
                  <option value="fair">Cukup</option>
                  <option value="guarded">Terjaga</option>
                  <option value="poor">Buruk</option>
                  <option value="terminal">Terminal</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Alasan Klinis
                </label>
                <textarea
                  rows={2}
                  value={assessment.clinical_reasoning}
                  onChange={(e) => setAssessment({ ...assessment, clinical_reasoning: e.target.value })}
                  placeholder="Penjelasan klinis dan alasan diagnosis..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* Plan */}
          <div>
            <h3 className="text-md font-semibold text-gray-800 mb-3 flex items-center">
              <span className="w-8 h-8 bg-red-100 text-red-700 rounded-full flex items-center justify-center mr-2 text-sm font-bold">P</span>
              Rencana (Rencana tatalaksana)
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rencana Diagnostik
                </label>
                <textarea
                  rows={2}
                  value={plan.diagnostic_plan}
                  onChange={(e) => setPlan({ ...plan, diagnostic_plan: e.target.value })}
                  placeholder="Rencana pemeriksaan diagnostik..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rencana Tatalaksana *
                </label>
                <textarea
                  rows={3}
                  value={plan.treatment_plan}
                  onChange={(e) => setPlan({ ...plan, treatment_plan: e.target.value })}
                  placeholder="Rencana tatalaksana pasien..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rencana Obat
                </label>
                <textarea
                  rows={2}
                  value={plan.medication_plan}
                  onChange={(e) => setPlan({ ...plan, medication_plan: e.target.value })}
                  placeholder="Rencana pemberian obat..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rencana Keperawatan
                </label>
                <textarea
                  rows={2}
                  value={plan.nursing_plan}
                  onChange={(e) => setPlan({ ...plan, nursing_plan: e.target.value })}
                  placeholder="Rencana asuhan keperawatan..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Edukasi Pasien
                </label>
                <textarea
                  rows={2}
                  value={plan.patient_education}
                  onChange={(e) => setPlan({ ...plan, patient_education: e.target.value })}
                  placeholder="Edukasi yang diberikan kepada pasien..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rencana Tindak Lanjut
                </label>
                <textarea
                  rows={2}
                  value={plan.follow_up_plan}
                  onChange={(e) => setPlan({ ...plan, follow_up_plan: e.target.value })}
                  placeholder="Rencana tindak lanjut..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tujuan
                </label>
                <textarea
                  rows={1}
                  value={plan.goals}
                  onChange={(e) => setPlan({ ...plan, goals: e.target.value })}
                  placeholder="Tujuan pengobatan..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Precautions (Peringatan)
                </label>
                <textarea
                  rows={1}
                  value={typeof plan.precautions === "string" ? plan.precautions : plan.precautions?.join(", ")}
                  onChange={(e) => setPlan({ ...plan, precautions: e.target.value })}
                  placeholder="Hal-hal yang perlu diwaspadai..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Catatan Tambahan
                </label>
                <textarea
                  rows={1}
                  value={plan.notes}
                  onChange={(e) => setPlan({ ...plan, notes: e.target.value })}
                  placeholder="Catatan tambahan..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Interventions Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">4. Intervensi</h2>

          {/* Add Intervention Form */}
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Tambah Intervensi</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs text-gray-600 mb-1">Kategori</label>
                <select
                  value={newIntervention.type}
                  onChange={(e) => setNewIntervention({ ...newIntervention, type: e.target.value as any })}
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                >
                  {INTERVENTION_CATEGORIES.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Nama Intervensi</label>
                <input
                  type="text"
                  value={newIntervention.name}
                  onChange={(e) => setNewIntervention({ ...newIntervention, name: e.target.value })}
                  placeholder="Nama intervensi..."
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Indikasi</label>
                <input
                  type="text"
                  value={newIntervention.indication}
                  onChange={(e) => setNewIntervention({ ...newIntervention, indication: e.target.value })}
                  placeholder="Indikasi..."
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                />
              </div>
              <div className="flex items-end">
                <button
                  onClick={handleAddIntervention}
                  className="w-full px-3 py-1 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700"
                >
                  Tambah
                </button>
              </div>
            </div>
            <div className="mt-2">
              <label className="block text-xs text-gray-600 mb-1">Detail</label>
              <textarea
                rows={1}
                value={newIntervention.details}
                onChange={(e) => setNewIntervention({ ...newIntervention, details: e.target.value })}
                placeholder="Detail intervensi..."
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
              />
            </div>
          </div>

          {/* Interventions List */}
          {interventions.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-700">Daftar Intervensi</h3>
              {interventions.map((intervention, index) => (
                <div key={index} className="flex items-start justify-between p-3 bg-white border border-gray-200 rounded-lg">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{intervention.name}</p>
                    <p className="text-sm text-gray-600">
                      {intervention.type} • {intervention.indication}
                    </p>
                    {intervention.details && (
                      <p className="text-xs text-gray-500 mt-1">{intervention.details}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleRemoveIntervention(index)}
                    className="text-red-600 hover:text-red-800 ml-4"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Response Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">5. Respon Pasien</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Respon Terhadap Tatalaksana
              </label>
              <textarea
                rows={2}
                value={patientResponses.map(r => r.description).join("\n")}
                onChange={(e) => {
                  const responses = e.target.value.split("\n").filter(r => r.trim());
                  setPatientResponses(responses.map(r => ({
                    treatment: r,
                    response_type: "improvement",
                    description: r,
                    onset: new Date().toISOString(),
                    is_expected: true,
                    requires_intervention: false,
                  })));
                }}
                placeholder="Respon pasien terhadap tatalaksana..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Efek Samping yang Dialami
              </label>
              <textarea
                rows={2}
                value={sideEffects.map(s => s.name + ": " + s.description).join("\n")}
                onChange={(e) => {
                  const effects = e.target.value.split("\n").filter(e => e.trim());
                  setSideEffects(effects.map(e => ({
                    name: e.split(":")[0] || e,
                    suspected_cause: "Obat/Terapi",
                    onset: new Date().toISOString(),
                    severity: "mild",
                    description: e,
                    is_expected: false,
                    actions_taken: "Dokumentasi",
                    treatment_changed: false,
                    reported_to_prescriber: false,
                  })));
                }}
                placeholder="Efek samping yang dialami pasien..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Komplikasi
              </label>
              <textarea
                rows={2}
                value={complications.map(c => c.name + ": " + c.description).join("\n")}
                onChange={(e) => {
                  const comps = e.target.value.split("\n").filter(c => c.trim());
                  setComplications(comps.map(c => ({
                    name: c.split(":")[0] || c,
                    type: "other",
                    severity: "moderate",
                    onset: new Date().toISOString(),
                    description: c,
                    actions_taken: "Monitoring",
                    status: "active",
                    resolved: false,
                    family_notified: false,
                  })));
                }}
                placeholder="Komplikasi yang terjadi..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Additional Notes Section */}
      {selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">6. Catatan Tambahan</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Catatan Tambahan
              </label>
              <textarea
                rows={4}
                value={additionalNotes}
                onChange={(e) => setAdditionalNotes(e.target.value)}
                placeholder="Catatan tambahan yang tidak tercakup dalam bagian lain..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                maxLength={CHARACTER_LIMITS.note}
              />
              <p className="text-xs text-gray-500 mt-1">
                {additionalNotes.length}/{CHARACTER_LIMITS.note} karakter
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Sign-off Status */}
      {selectedPatient && signOff.is_signed_off && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="font-medium text-green-900">Catatan Tertandatangani</p>
              <p className="text-sm text-green-700">
                Ditandatangani oleh {signOff.signed_by} pada{" "}
                {signOff.signed_at && new Date(signOff.signed_at).toLocaleString("id-ID")}
              </p>
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
          {!signOff.is_signed_off && (
            <button
              onClick={handleSignNote}
              className="px-6 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
            >
              Tanda Tangan
            </button>
          )}
          <button
            onClick={handleSaveNote}
            disabled={loading}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? "Menyimpan..." : "Simpan Catatan"}
          </button>
        </div>
      )}
    </div>
  );
}
