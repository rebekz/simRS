"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

interface RadiologyExam {
  id: number;
  exam_code: string;
  exam_name: string;
  modality: "xray" | "ct" | "mri" | "ultrasound" | "mammography" | "fluoroscopy" | "nuclear_medicine" | "pet_scan";
  body_part: string;
  view: string;
  contrast_required: boolean;
  contrast_type?: "iodinated" | "gadolinium" | "barium" | "air";
  price: number;
  bpjs_tariff?: number;
  is_bpjs_covered: boolean;
  preparation_instructions?: string;
  duration_minutes: number;
  pregnancy_contraindication: boolean;
}

interface Patient {
  id: number;
  name: string;
  medical_record_number: string;
  age: number;
  gender: string;
  allergies?: string[];
  pregnancy_status?: "unknown" | "not_pregnant" | "pregnant";
  weight?: number;
  implantable_devices?: string[];
}

interface Scheduler {
  id: number;
  name: string;
  available: boolean;
}

function RadiologyOrderPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const patientId = searchParams.get("patient_id");
  const encounterId = searchParams.get("encounter_id");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [patient, setPatient] = useState<Patient | null>(null);
  const [availableExams, setAvailableExams] = useState<RadiologyExam[]>([]);
  const [selectedExam, setSelectedExam] = useState<RadiologyExam | null>(null);
  const [schedulers, setSchedulers] = useState<Scheduler[]>([]);
  const [clinicalInfo, setClinicalInfo] = useState({
    diagnosis: "",
    symptoms: "",
    clinical_indication: "",
    priority: "routine" as "routine" | "urgent" | "stat",
    requested_procedure: "",
    scheduler_id: "",
    scheduled_date: "",
    scheduled_time: "",
    contrast_allergy: false,
    claustrophobia: false,
  });
  const [submitting, setSubmitting] = useState(false);
  const [modalityFilter, setModalityFilter] = useState("");

  useEffect(() => {
    checkAuth();
    if (patientId) {
      fetchPatient(parseInt(patientId));
    }
    fetchAvailableExams();
    fetchSchedulers();
  }, [patientId]);

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

  const fetchAvailableExams = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/radiology/exams/available", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAvailableExams(data.exams || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load radiology exams");
    } finally {
      setLoading(false);
    }
  };

  const fetchSchedulers = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/radiology/schedulers", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSchedulers(data.schedulers || []);
      }
    } catch (err) {
      console.error("Failed to fetch schedulers:", err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedExam) {
      alert("Pilih pemeriksaan radiologi");
      return;
    }

    if (!patient) {
      alert("Pasien tidak ditemukan");
      return;
    }

    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    setSubmitting(true);

    try {
      const response = await fetch("/api/v1/radiology/orders", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          patient_id: patient.id,
          encounter_id: encounterId ? parseInt(encounterId) : null,
          exam_id: selectedExam.id,
          diagnosis: clinicalInfo.diagnosis,
          symptoms: clinicalInfo.symptoms,
          clinical_indication: clinicalInfo.clinical_indication,
          priority: clinicalInfo.priority,
          requested_procedure: clinicalInfo.requested_procedure,
          scheduler_id: clinicalInfo.scheduler_id ? parseInt(clinicalInfo.scheduler_id) : null,
          scheduled_date: clinicalInfo.scheduled_date || null,
          scheduled_time: clinicalInfo.scheduled_time || null,
          contrast_allergy: clinicalInfo.contrast_allergy,
          claustrophobia: clinicalInfo.claustrophobia,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create radiology order");
      }

      const data = await response.json();
      alert(`Pemeriksaan radiologi berhasil dipesan. Order ID: ${data.order_id}`);

      router.push("/app/radiology");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to create radiology order");
    } finally {
      setSubmitting(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("id-ID", {
      style: "currency",
      currency: "IDR",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const getModalityIcon = (modality: string) => {
    const icons: Record<string, string> = {
      xray: "📷",
      ct: "🔬",
      mri: "🧠",
      ultrasound: "🔊",
      mammography: "🎀",
      fluoroscopy: "🎥",
      nuclear_medicine: "☢️",
      pet_scan: "💉",
    };
    return icons[modality] || "📸";
  };

  const getModalityBadge = (modality: string) => {
    const modalityConfig: Record<string, { label: string; className: string }> = {
      xray: { label: "X-Ray", className: "bg-blue-100 text-blue-700" },
      ct: { label: "CT Scan", className: "bg-purple-100 text-purple-700" },
      mri: { label: "MRI", className: "bg-green-100 text-green-700" },
      ultrasound: { label: "USG", className: "bg-cyan-100 text-cyan-700" },
      mammography: { label: "Mammography", className: "bg-pink-100 text-pink-700" },
      fluoroscopy: { label: "Fluoroscopy", className: "bg-orange-100 text-orange-700" },
      nuclear_medicine: { label: "Nuclear Med", className: "bg-yellow-100 text-yellow-700" },
      pet_scan: { label: "PET Scan", className: "bg-indigo-100 text-indigo-700" },
    };

    const config = modalityConfig[modality] || modalityConfig.xray;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.className}`}>
        {getModalityIcon(modality)} {config.label}
      </span>
    );
  };

  const modalities = Array.from(new Set(availableExams.map(e => e.modality)));

  const filteredExams = modalityFilter
    ? availableExams.filter(e => e.modality === modalityFilter)
    : availableExams;

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
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Pemeriksaan Radiologi</h1>
        <p className="text-gray-600 mt-1">Buat pesanan pemeriksaan radiologi untuk pasien</p>
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

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Patient Information */}
        {patient ? (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi Pasien</h2>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div>
                <p className="text-sm text-gray-500">Nama Pasien</p>
                <p className="text-sm font-medium text-gray-900">{patient.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">No RM</p>
                <p className="text-sm font-medium text-gray-900">{patient.medical_record_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Usia/Jenis Kelamin</p>
                <p className="text-sm font-medium text-gray-900">{patient.age} th / {patient.gender === "male" ? "L" : "P"}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Berat Badan</p>
                <p className="text-sm font-medium text-gray-900">{patient.weight ? `${patient.weight} kg` : "-"}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Status Kehamilan</p>
                <p className="text-sm font-medium text-gray-900">
                  {patient.pregnancy_status === "pregnant" && "🤰 Hamil"}
                  {patient.pregnancy_status === "not_pregnant" && "Tidak Hamil"}
                  {patient.pregnancy_status === "unknown" && "Tidak Diketahui"}
                </p>
              </div>
            </div>

            {/* Allergies Warning */}
            {patient.allergies && patient.allergies.length > 0 && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div>
                    <h4 className="text-sm font-medium text-red-900">Alergi Pasien</h4>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {patient.allergies.map((allergy, idx) => (
                        <span key={idx} className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs">
                          {allergy}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Implantable Devices */}
            {patient.implantable_devices && patient.implantable_devices.length > 0 && (
              <div className="mt-4 bg-orange-50 border border-orange-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <svg className="w-6 h-6 text-orange-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <h4 className="text-sm font-medium text-orange-900">Perangkat Implan</h4>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {patient.implantable_devices.map((device, idx) => (
                        <span key={idx} className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
                          {device}
                        </span>
                      ))}
                    </div>
                    <p className="text-xs text-orange-700 mt-2">
      Perangkat implan mungkin tidak kompatibel dengan MRI tertentu
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="flex items-center space-x-3">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="text-sm font-medium text-yellow-900">Pasien Belum Dipilih</h3>
                <p className="text-sm text-yellow-700 mt-1">
                  Silakan pilih pasien terlebih dahulu atau akses halaman ini dari halaman konsultasi pasien.
                </p>
                <button
                  type="button"
                  onClick={() => router.push("/app/patients")}
                  className="mt-3 px-4 py-2 bg-yellow-600 text-white text-sm rounded hover:bg-yellow-700"
                >
                  Pilih Pasien
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Clinical Information */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi Klinis</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Diagnosa Kerja *</label>
              <input
                type="text"
                required
                value={clinicalInfo.diagnosis}
                onChange={(e) => setClinicalInfo({ ...clinicalInfo, diagnosis: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Masukkan diagnosa kerja"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Gejala/Keluhan</label>
              <input
                type="text"
                value={clinicalInfo.symptoms}
                onChange={(e) => setClinicalInfo({ ...clinicalInfo, symptoms: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Masukkan gejala atau keluhan pasien"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Indikasi Klinis</label>
              <textarea
                value={clinicalInfo.clinical_indication}
                onChange={(e) => setClinicalInfo({ ...clinicalInfo, clinical_indication: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Jelaskan indikasi klinis untuk pemeriksaan ini"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Prioritas</label>
              <select
                value={clinicalInfo.priority}
                onChange={(e) => setClinicalInfo({ ...clinicalInfo, priority: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="routine">Routine</option>
                <option value="urgent">Urgent</option>
                <option value="stat">Stat (Segera)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Prosedur yang Diminta</label>
              <input
                type="text"
                value={clinicalInfo.requested_procedure}
                onChange={(e) => setClinicalInfo({ ...clinicalInfo, requested_procedure: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Contoh: CT Kepak dengan Kontras"
              />
            </div>
          </div>
        </div>

        {/* Exam Selection */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Pilih Pemeriksaan</h2>
            <select
              value={modalityFilter}
              onChange={(e) => setModalityFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Semua Modalitas</option>
              {modalities.map(mod => (
                <option key={mod} value={mod}>{mod.toUpperCase()}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
            {filteredExams.map((exam) => {
              const isSelected = selectedExam?.id === exam.id;
              const isPregnant = patient?.pregnancy_status === "pregnant";
              const hasContraindication = isPregnant && exam.pregnancy_contraindication;

              return (
                <div
                  key={exam.id}
                  className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                    isSelected ? "border-indigo-500 bg-indigo-50" : "border-gray-200 hover:border-gray-300"
                  } ${hasContraindication ? "opacity-50" : ""}`}
                  onClick={() => !hasContraindication && setSelectedExam(exam)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="exam"
                          checked={isSelected}
                          onChange={() => setSelectedExam(exam)}
                          disabled={hasContraindication}
                          className="w-4 h-4 text-indigo-600 focus:ring-indigo-500"
                        />
                        <h3 className="font-medium text-gray-900">{exam.exam_name}</h3>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        {exam.exam_code} • {exam.body_part} • {exam.view}
                      </p>
                    </div>
                    {getModalityBadge(exam.modality)}
                  </div>

                  <div className="flex items-center justify-between mt-3">
                    <div className="flex items-center space-x-2">
                      {exam.contrast_required && (
                        <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs">
                          Kontras
                        </span>
                      )}
                      <span className="text-xs text-gray-400">
                        {exam.duration_minutes} menit
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">{formatCurrency(exam.price)}</p>
                      {exam.is_bpjs_covered && (
                        <p className="text-xs text-green-600">Covered BPJS</p>
                      )}
                    </div>
                  </div>

                  {hasContraindication && (
                    <div className="mt-2 bg-red-100 text-red-700 px-2 py-1 rounded text-xs">
                      ⚠️ Tidak direkomendasikan untuk pasien hamil
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {filteredExams.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Tidak ada pemeriksaan yang cocok dengan filter
            </div>
          )}
        </div>

        {/* Selected Exam Details & Scheduling */}
        {selectedExam && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Detail & Jadwal Pemeriksaan</h2>

            {/* Exam Details */}
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">{selectedExam.exam_name}</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Modalitas</p>
                  <p className="font-medium">{selectedExam.modality.toUpperCase()}</p>
                </div>
                <div>
                  <p className="text-gray-500">Bagian Tubuh</p>
                  <p className="font-medium">{selectedExam.body_part}</p>
                </div>
                <div>
                  <p className="text-gray-500">Posisi/View</p>
                  <p className="font-medium">{selectedExam.view}</p>
                </div>
                <div>
                  <p className="text-gray-500">Durasi</p>
                  <p className="font-medium">{selectedExam.duration_minutes} menit</p>
                </div>
              </div>

              {selectedExam.contrast_required && (
                <div className="mt-4 bg-purple-50 border border-purple-200 rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={clinicalInfo.contrast_allergy}
                      onChange={(e) => setClinicalInfo({ ...clinicalInfo, contrast_allergy: e.target.checked })}
                      className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                    />
                    <label className="text-sm text-purple-900">
                      Pasien memiliki alergi terhadap kontras ({selectedExam.contrast_type})
                    </label>
                  </div>
                </div>
              )}

              {selectedExam.modality === "mri" && (
                <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={clinicalInfo.claustrophobia}
                      onChange={(e) => setClinicalInfo({ ...clinicalInfo, claustrophobia: e.target.checked })}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <label className="text-sm text-blue-900">
                      Pasien memiliki klaustrofobia (takut ruang sempit)
                    </label>
                  </div>
                </div>
              )}

              {selectedExam.preparation_instructions && (
                <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <h4 className="text-sm font-medium text-yellow-900 mb-1">Instruksi Persiapan</h4>
                  <p className="text-sm text-yellow-800">{selectedExam.preparation_instructions}</p>
                </div>
              )}

              <div className="mt-4 pt-4 border-t">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Biaya Pemeriksaan</span>
                  <span className="text-lg font-bold text-indigo-600">{formatCurrency(selectedExam.price)}</span>
                </div>
                {selectedExam.is_bpjs_covered && selectedExam.bpjs_tariff && (
                  <div className="flex justify-between items-center text-sm mt-1">
                    <span className="text-gray-600">Tarif BPJS</span>
                    <span className="text-green-600">{formatCurrency(selectedExam.bpjs_tariff)}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Scheduling */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Radiologist/Scheduler</label>
                <select
                  value={clinicalInfo.scheduler_id}
                  onChange={(e) => setClinicalInfo({ ...clinicalInfo, scheduler_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">Pilih Scheduler</option>
                  {schedulers.map(scheduler => (
                    <option key={scheduler.id} value={scheduler.id} disabled={!scheduler.available}>
                      {scheduler.name} {!scheduler.available && "(Tidak Tersedia)"}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tanggal Jadwal</label>
                <input
                  type="date"
                  value={clinicalInfo.scheduled_date}
                  onChange={(e) => setClinicalInfo({ ...clinicalInfo, scheduled_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Waktu Jadwal</label>
                <input
                  type="time"
                  value={clinicalInfo.scheduled_time}
                  onChange={(e) => setClinicalInfo({ ...clinicalInfo, scheduled_time: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>

            {/* Warnings */}
            {(clinicalInfo.contrast_allergy || clinicalInfo.claustrophobia) && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div>
                    <h4 className="text-sm font-medium text-red-900">Perhatian</h4>
                    <ul className="text-sm text-red-700 mt-1 list-disc list-inside">
                      {clinicalInfo.contrast_allergy && <li>Pasien memiliki alergi kontras - perlu premedikasi</li>}
                      {clinicalInfo.claustrophobia && <li>Pasien memiliki klaustrofobia - pertimbangkan sedasi</li>}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Batal
          </button>
          <button
            type="submit"
            disabled={submitting || !selectedExam || !patient}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {submitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Memproses...</span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Buat Pesanan</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default function RadiologyOrderPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    }>
      <RadiologyOrderPageContent />
    </Suspense>
  );
}
