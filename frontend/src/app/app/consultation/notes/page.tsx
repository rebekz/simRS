"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

interface Patient {
  id: number;
  name: string;
  medical_record_number: string;
  age: number;
  gender: string;
  blood_type?: string;
  allergies?: string[];
  chronic_conditions?: string[];
}

interface Encounter {
  id: number;
  encounter_type: "outpatient" | "inpatient" | "emergency";
  department: string;
  attending_physician: string;
  start_time: string;
}

interface SOAPNote {
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
}

interface Vitals {
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  heart_rate?: number;
  respiratory_rate?: number;
  temperature?: number;
  oxygen_saturation?: number;
  weight?: number;
  height?: number;
  bmi?: number;
  pain_score?: number;
  consciousness_level?: string;
  glasgow_coma_scale?: number;
}

export default function SOAPNotesPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const patientId = searchParams.get("patient_id");
  const encounterId = searchParams.get("encounter_id");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [patient, setPatient] = useState<Patient | null>(null);
  const [encounter, setEncounter] = useState<Encounter | null>(null);
  const [existingNote, setExistingNote] = useState<SOAPNote | null>(null);
  const [vitals, setVitals] = useState<Vitals>({});
  const [soap, setSOAP] = useState<SOAPNote>({
    subjective: "",
    objective: "",
    assessment: "",
    plan: "",
  });
  const [diagnoses, setDiagnoses] = useState<string[]>([]);
  const [currentDiagnosis, setCurrentDiagnosis] = useState("");
  const [procedures, setProcedures] = useState<string[]>([]);
  const [currentProcedure, setCurrentProcedure] = useState("");
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<"subjective" | "objective" | "assessment" | "plan">("subjective");
  const [vitalsExpanded, setVitalsExpanded] = useState(false);

  useEffect(() => {
    checkAuth();
    if (patientId) {
      fetchPatient(parseInt(patientId));
    }
    if (encounterId) {
      fetchEncounter(parseInt(encounterId));
      fetchExistingNote(parseInt(encounterId));
    }
  }, [patientId, encounterId]);

  const checkAuth = () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
    }
  };

  const fetchPatient = async (id: number) => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/patients/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPatient(data);
      }
    } catch (err) {
      console.error("Failed to fetch patient:", err);
    }
  };

  const fetchEncounter = async (id: number) => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/encounters/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setEncounter(data);
      }
    } catch (err) {
      console.error("Failed to fetch encounter:", err);
    }
  };

  const fetchExistingNote = async (id: number) => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/encounters/${id}/soap-note`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setExistingNote(data);
        setSOAP(data);
        if (data.diagnoses) setDiagnoses(data.diagnoses);
        if (data.procedures) setProcedures(data.procedures);
        if (data.vitals) setVitals(data.vitals);
      }
    } catch (err) {
      console.error("Failed to fetch existing note:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (saveAndClose: boolean = false) => {
    if (!encounter) {
      alert("Encounter tidak ditemukan");
      return;
    }

    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    setSaving(true);

    try {
      const payload = {
        encounter_id: encounter.id,
        subjective: soap.subjective,
        objective: soap.objective,
        assessment: soap.assessment,
        plan: soap.plan,
        diagnoses,
        procedures,
        vitals,
      };

      const response = await fetch("/api/v1/clinical-notes/soap", {
        method: existingNote ? "PUT" : "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to save SOAP note");
      }

      const data = await response.json();
      alert("Catatan SOAP berhasil disimpan");

      if (saveAndClose) {
        router.push("/app/patients");
      } else {
        setExistingNote(data);
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to save SOAP note");
    } finally {
      setSaving(false);
    }
  };

  const handleAddDiagnosis = () => {
    if (currentDiagnosis.trim()) {
      setDiagnoses([...diagnoses, currentDiagnosis.trim()]);
      setCurrentDiagnosis("");
    }
  };

  const handleRemoveDiagnosis = (index: number) => {
    setDiagnoses(diagnoses.filter((_, i) => i !== index));
  };

  const handleAddProcedure = () => {
    if (currentProcedure.trim()) {
      setProcedures([...procedures, currentProcedure.trim()]);
      setCurrentProcedure("");
    }
  };

  const handleRemoveProcedure = (index: number) => {
    setProcedures(procedures.filter((_, i) => i !== index));
  };

  const getSectionStatus = (section: keyof SOAPNote) => {
    const content = soap[section];
    if (!content) return "empty";
    if (content.length < 50) return "minimal";
    return "complete";
  };

  const calculateBMI = () => {
    if (vitals.weight && vitals.height) {
      const heightM = vitals.height / 100;
      return (vitals.weight / (heightM * heightM)).toFixed(1);
    }
    return "";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Catatan SOAP</h1>
          <p className="text-gray-600 mt-1">Dokumentasi klinis pasien</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => handleSave(false)}
            disabled={saving}
            className="px-4 py-2 border border-indigo-600 text-indigo-600 rounded-lg hover:bg-indigo-50 disabled:opacity-50 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
            </svg>
            <span>Simpan</span>
          </button>
          <button
            onClick={() => router.push(`/app/lab/order?patient_id=${patientId}&encounter_id=${encounterId}`)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span>Order Lab</span>
          </button>
          <button
            onClick={() => router.push(`/app/radiology/order?patient_id=${patientId}&encounter_id=${encounterId}`)}
            className="px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span>Order Radiologi</span>
          </button>
          <button
            onClick={() => router.push(`/app/prescriptions/new?patient_id=${patientId}&encounter_id=${encounterId}`)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <span>Resep</span>
          </button>
          <button
            onClick={() => handleSave(true)}
            disabled={saving}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center space-x-2"
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Menyimpan...</span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Selesai</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center space-x-3">
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Patient & Encounter Info */}
      {patient && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
            <div>
              <p className="text-sm text-gray-500">Nama Pasien</p>
              <p className="text-sm font-medium text-gray-900">{patient.name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">No RM</p>
              <p className="text-sm font-medium text-gray-900">{patient.medical_record_number}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Usia/JK</p>
              <p className="text-sm font-medium text-gray-900">{patient.age} th / {patient.gender === "male" ? "L" : "P"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Gol. Darah</p>
              <p className="text-sm font-medium text-gray-900">{patient.blood_type || "-"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Departemen</p>
              <p className="text-sm font-medium text-gray-900">{encounter?.department || "-"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Tipe Kunjungan</p>
              <p className="text-sm font-medium text-gray-900 capitalize">{encounter?.encounter_type || "-"}</p>
            </div>
          </div>

          {/* Allergies & Chronic Conditions */}
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            {patient.allergies && patient.allergies.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-xs font-medium text-red-900 mb-2">Alergi</p>
                <div className="flex flex-wrap gap-2">
                  {patient.allergies.map((allergy, idx) => (
                    <span key={idx} className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs">
                      {allergy}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {patient.chronic_conditions && patient.chronic_conditions.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p className="text-xs font-medium text-yellow-900 mb-2">Kondisi Kronis</p>
                <div className="flex flex-wrap gap-2">
                  {patient.chronic_conditions.map((condition, idx) => (
                    <span key={idx} className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs">
                      {condition}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* SOAP Sections Tabs */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex">
            {[
              { key: "subjective", label: "S - Subjektif", color: "blue" },
              { key: "objective", label: "O - Objektif", color: "green" },
              { key: "assessment", label: "A - Asesmen", color: "purple" },
              { key: "plan", label: "P - Rencana", color: "orange" },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? `border-${tab.color}-500 text-${tab.color}-600`
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <div className="flex items-center space-x-2">
                  <span>{tab.label}</span>
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    getSectionStatus(tab.key as keyof SOAPNote) === "complete"
                      ? "bg-green-100 text-green-700"
                      : getSectionStatus(tab.key as keyof SOAPNote) === "minimal"
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-gray-100 text-gray-500"
                  }`}>
                    {getSectionStatus(tab.key as keyof SOAPNote) === "complete" && "✓"}
                    {getSectionStatus(tab.key as keyof SOAPNote) === "minimal" && "!"}
                    {getSectionStatus(tab.key as keyof SOAPNote) === "empty" && "○"}
                  </span>
                </div>
              </button>
            ))}
          </nav>
        </div>

        {/* Subjective Section */}
        {activeTab === "subjective" && (
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Subjektif - Keluhan Pasien</h3>
            <p className="text-sm text-gray-600 mb-4">
              Catat keluhan utama, riwayat penyakit saat ini, dan informasi yang diberikan pasien.
            </p>
            <textarea
              value={soap.subjective}
              onChange={(e) => setSOAP({ ...soap, subjective: e.target.value })}
              rows={10}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Contoh: Pasien mengeluh sakit kepala sejak 3 hari yang lalu. Nyeri dirasakan di daerah frontal, berdenyut, skala 7/10. Diperberat oleh aktivitas dan cahaya terang, diringankan oleh istirahat di tempat gelap. Tidak ada mual, muntah, atau gangguan penglihatan. Pasien juga mengeluh demam ringan..."
            />
            <div className="mt-3 text-sm text-gray-500">
              Karakter: {soap.subjective.length}
            </div>
          </div>
        )}

        {/* Objective Section */}
        {activeTab === "objective" && (
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Objektif - Pemeriksaan Fisik</h3>
            <p className="text-sm text-gray-600 mb-4">
              Catat temuan pemeriksaan fisik dan hasil pemeriksaan penunjang.
            </p>

            {/* Vitals Toggle */}
            <div className="mb-4">
              <button
                onClick={() => setVitalsExpanded(!vitalsExpanded)}
                className="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                <svg className={`w-5 h-5 transition-transform ${vitalsExpanded ? "rotate-90" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                <span>Tanda Vital</span>
              </button>

              {vitalsExpanded && (
                <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-4 bg-gray-50 p-4 rounded-lg">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Tekanan Darah</label>
                    <div className="flex space-x-2">
                      <input
                        type="number"
                        placeholder="Syst"
                        value={vitals.blood_pressure_systolic || ""}
                        onChange={(e) => setVitals({ ...vitals, blood_pressure_systolic: parseInt(e.target.value) || undefined })}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                      <input
                        type="number"
                        placeholder="Dias"
                        value={vitals.blood_pressure_diastolic || ""}
                        onChange={(e) => setVitals({ ...vitals, blood_pressure_diastolic: parseInt(e.target.value) || undefined })}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">mmHg</p>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Nadi</label>
                    <input
                      type="number"
                      value={vitals.heart_rate || ""}
                      onChange={(e) => setVitals({ ...vitals, heart_rate: parseInt(e.target.value) || undefined })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      placeholder="x/menit"
                    />
                    <p className="text-xs text-gray-500 mt-1">x/menit</p>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Pernapasan</label>
                    <input
                      type="number"
                      value={vitals.respiratory_rate || ""}
                      onChange={(e) => setVitals({ ...vitals, respiratory_rate: parseInt(e.target.value) || undefined })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      placeholder="x/menit"
                    />
                    <p className="text-xs text-gray-500 mt-1">x/menit</p>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Suhu</label>
                    <input
                      type="number"
                      step="0.1"
                      value={vitals.temperature || ""}
                      onChange={(e) => setVitals({ ...vitals, temperature: parseFloat(e.target.value) || undefined })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      placeholder="°C"
                    />
                    <p className="text-xs text-gray-500 mt-1">°C</p>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">SpO2</label>
                    <input
                      type="number"
                      value={vitals.oxygen_saturation || ""}
                      onChange={(e) => setVitals({ ...vitals, oxygen_saturation: parseInt(e.target.value) || undefined })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      placeholder="%"
                    />
                    <p className="text-xs text-gray-500 mt-1">%</p>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Berat</label>
                    <input
                      type="number"
                      value={vitals.weight || ""}
                      onChange={(e) => {
                        const newVitals = { ...vitals, weight: parseFloat(e.target.value) || undefined };
                        const bmi = calculateBMI();
                        if (bmi) newVitals.bmi = parseFloat(bmi);
                        setVitals(newVitals);
                      }}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      placeholder="kg"
                    />
                    <p className="text-xs text-gray-500 mt-1">kg</p>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Tinggi</label>
                    <input
                      type="number"
                      value={vitals.height || ""}
                      onChange={(e) => {
                        const newVitals = { ...vitals, height: parseFloat(e.target.value) || undefined };
                        const bmi = calculateBMI();
                        if (bmi) newVitals.bmi = parseFloat(bmi);
                        setVitals(newVitals);
                      }}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      placeholder="cm"
                    />
                    <p className="text-xs text-gray-500 mt-1">cm</p>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">BMI</label>
                    <input
                      type="text"
                      value={vitals.bmi || calculateBMI() || ""}
                      readOnly
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm bg-gray-100"
                    />
                    <p className="text-xs text-gray-500 mt-1">kg/m²</p>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Skor Nyeri</label>
                    <input
                      type="number"
                      min="0"
                      max="10"
                      value={vitals.pain_score || ""}
                      onChange={(e) => setVitals({ ...vitals, pain_score: parseInt(e.target.value) || undefined })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      placeholder="0-10"
                    />
                    <p className="text-xs text-gray-500 mt-1">0-10</p>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Kesadaran</label>
                    <select
                      value={vitals.consciousness_level || ""}
                      onChange={(e) => setVitals({ ...vitals, consciousness_level: e.target.value })}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    >
                      <option value="">Pilih</option>
                      <option value="alert">Alert</option>
                      <option value="verbal">Verbal</option>
                      <option value="pain">Pain</option>
                      <option value="unresponsive">Unresponsive</option>
                    </select>
                  </div>
                </div>
              )}
            </div>

            {/* Physical Exam */}
            <textarea
              value={soap.objective}
              onChange={(e) => setSOAP({ ...soap, objective: e.target.value })}
              rows={10}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              placeholder="Contoh:&#10;&#10;Keadaan umum: compos mentis, kesadaran baik&#10;TTV: TD 120/80 mmHg, N 80x/menit, RR 18x/menit, Suhu 36.5°C, SpO2 98%&#10;&#10;Kepala: normocephalic, konjungiva anemis -, sklera ikterik -&#10;Mata: pupil isokor, refleks cahaya +/+, frenkus +&#10;Telinga: Tympanik membrane normal&#10;Hidung: tidak ada sekret, deviasi septum -&#10;Tenggorokan: tonsil T1-T1, tidak ada eksudat&#10;Leher: KGB tidak membesar, tiroid tidak membesar&#10;Dada: bentuk normal, simetris&#10;Jantung: B1 dan B2 reguler, tidak ada murmur&#10;Paru: vesikuler, tidak ada ronkhi&#10;Abdomen: supel, tidak ada tahanan, tidak ada massa&#10;Ekstremitas: tidak ada edema, akral hangat..."
            />
            <div className="mt-3 text-sm text-gray-500">
              Karakter: {soap.objective.length}
            </div>
          </div>
        )}

        {/* Assessment Section */}
        {activeTab === "assessment" && (
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Asesmen - Diagnosa</h3>
            <p className="text-sm text-gray-600 mb-4">
              Tulis diagnosa kerja berdasarkan subjektif dan objektif.
            </p>

            {/* Diagnosis List */}
            <div className="mb-4">
              <div className="flex space-x-2 mb-3">
                <input
                  type="text"
                  value={currentDiagnosis}
                  onChange={(e) => setCurrentDiagnosis(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleAddDiagnosis()}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="Tambah diagnosa (ICD-10 atau deskriptif)..."
                />
                <button
                  type="button"
                  onClick={handleAddDiagnosis}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Tambah
                </button>
              </div>

              {diagnoses.length > 0 && (
                <div className="space-y-2">
                  {diagnoses.map((diagnosis, idx) => (
                    <div key={idx} className="flex items-center justify-between bg-gray-50 px-4 py-2 rounded-lg">
                      <span className="text-sm text-gray-900">{idx + 1}. {diagnosis}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveDiagnosis(idx)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Assessment Text */}
            <textarea
              value={soap.assessment}
              onChange={(e) => setSOAP({ ...soap, assessment: e.target.value })}
              rows={8}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              placeholder="Contoh:&#10;&#10;Diagnosa Kerja:&#10;1. Tension Type Headache (G43.x)&#10;2. Hipertensi esensial (I10)&#10;&#10;Diagnosa Banding:&#10;- Migrain tanpa aura (G43.0)&#10;- Sakit kepala cluster (G44.1)&#10;&#10;Etiologi: Kemungkinan akibat stres dan kurang istirahat&#10;Prognosis: Bon, dengan pengobatan dan modifikasi gaya hidup"
            />
            <div className="mt-3 text-sm text-gray-500">
              Karakter: {soap.assessment.length}
            </div>
          </div>
        )}

        {/* Plan Section */}
        {activeTab === "plan" && (
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Rencana - Tatalaksana</h3>
            <p className="text-sm text-gray-600 mb-4">
              Rencana pengobatan dan tindakan lanjutan.
            </p>

            {/* Procedures List */}
            <div className="mb-4">
              <div className="flex space-x-2 mb-3">
                <input
                  type="text"
                  value={currentProcedure}
                  onChange={(e) => setCurrentProcedure(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleAddProcedure()}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  placeholder="Tambah tindakan/prosedur..."
                />
                <button
                  type="button"
                  onClick={handleAddProcedure}
                  className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
                >
                  Tambah
                </button>
              </div>

              {procedures.length > 0 && (
                <div className="space-y-2">
                  {procedures.map((procedure, idx) => (
                    <div key={idx} className="flex items-center justify-between bg-gray-50 px-4 py-2 rounded-lg">
                      <span className="text-sm text-gray-900">{idx + 1}. {procedure}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveProcedure(idx)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <textarea
              value={soap.plan}
              onChange={(e) => setSOAP({ ...soap, plan: e.target.value })}
              rows={10}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              placeholder="Contoh:&#10;&#10;1. Edukasi tentang manajemen stres&#10;2. Istirahat yang cukup 7-8 jam per hari&#10;3. Analgetik: Paracetamol 500mg 3x1 per oral (setelah makan)&#10;4. Follow up 1 minggu jika keluhan berlanjut&#10;&#10;Non-farmakologi:&#10;- Kompres dingin pada kepala&#10;- Pijat lembut pada area temple&#10;- Hindari trigger factor (cahaya terang, suara bising)&#10;&#10;Edukasi:&#10;- Segera ke IGD jika: sakit kepala hebat tiba-tiba, disertai muntah proyektil, gangguan penglihatan, kelemahan anggota gerak&#10;- Jaga pola tidur yang teratur&#10;- Kelola stres dengan teknik relaksasi"
            />
            <div className="mt-3 text-sm text-gray-500">
              Karakter: {soap.plan.length}
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions Footer */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => router.push(`/app/lab/order?patient_id=${patientId}&encounter_id=${encounterId}`)}
            className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 flex items-center space-x-2"
          >
            <span>🔬</span>
            <span>Order Lab</span>
          </button>
          <button
            onClick={() => router.push(`/app/radiology/order?patient_id=${patientId}&encounter_id=${encounterId}`)}
            className="px-4 py-2 bg-cyan-100 text-cyan-700 rounded-lg hover:bg-cyan-200 flex items-center space-x-2"
          >
            <span>📷</span>
            <span>Order Radiologi</span>
          </button>
          <button
            onClick={() => router.push(`/app/prescriptions/new?patient_id=${patientId}&encounter_id=${encounterId}`)}
            className="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 flex items-center space-x-2"
          >
            <span>💊</span>
            <span>Buat Resep</span>
          </button>
          <button
            onClick={() => window.open(`/app/patients/${patientId}/medical-history`, "_blank")}
            className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 flex items-center space-x-2"
          >
            <span>📋</span>
            <span>Riwayat Medis</span>
          </button>
          <button
            onClick={() => handleSave(false)}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center space-x-2"
          >
            <span>💾</span>
            <span>Simpan Draft</span>
          </button>
        </div>
      </div>
    </div>
  );
}
