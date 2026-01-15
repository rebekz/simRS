"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

interface Patient {
  id: number;
  name: string;
  medical_record_number: string;
  age: number;
  gender: string;
  blood_type?: string;
  allergies?: string[];
  insurance_type?: "bpjs" | "insurance" | "self_pay" | "corporate";
  insurance_number?: string;
}

interface Admission {
  id: number;
  admission_number: string;
  admission_date: string;
  discharge_date?: string;
  room: string;
  bed: string;
  ward: string;
  class: string;
  daily_rate: number;
  attending_physician: string;
  primary_diagnosis: string;
  secondary_diagnoses: string[];
}

interface DischargeSummary {
  discharge_date: string;
  discharge_time: string;
  discharge_status: "recovered" | "improved" | "unimproved" | "deceased" | "transferred" | "lama" | "request";
  discharge_destination: "home" | "transfer_facility" | "rehab" | "nursing_home" | "other";
  transfer_facility_name?: string;
  discharge_diagnosis: string;
  principal_procedure?: string;
  secondary_procedures: string[];
  complications?: string;
  outcome: string;
  treatment_summary: string;
  discharge_medications: DischargeMedication[];
  instructions: string[];
  follow_up_appointments: FollowUpAppointment[];
  referral_specialties: string[];
  health_education: string[];
  given_documents: string[];
}

interface DischargeMedication {
  name: string;
  dosage: string;
  frequency: string;
  duration: string;
  indication: string;
}

interface FollowUpAppointment {
  specialty: string;
  doctor_name?: string;
  scheduled_date?: string;
  reason: string;
}

function DischargeFormPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const patientId = searchParams.get("patient_id");
  const admissionId = searchParams.get("admission_id");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [patient, setPatient] = useState<Patient | null>(null);
  const [admission, setAdmission] = useState<Admission | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [dischargeData, setDischargeData] = useState<DischargeSummary>({
    discharge_date: new Date().toISOString().split("T")[0],
    discharge_time: new Date().toTimeString().slice(0, 5),
    discharge_status: "improved",
    discharge_destination: "home",
    transfer_facility_name: "",
    discharge_diagnosis: "",
    principal_procedure: "",
    secondary_procedures: [],
    complications: "",
    outcome: "",
    treatment_summary: "",
    discharge_medications: [],
    instructions: [],
    follow_up_appointments: [],
    referral_specialties: [],
    health_education: [],
    given_documents: [],
  });

  const [currentMedication, setCurrentMedication] = useState<DischargeMedication>({
    name: "",
    dosage: "",
    frequency: "",
    duration: "",
    indication: "",
  });

  const [currentInstruction, setCurrentInstruction] = useState("");
  const [currentFollowUp, setCurrentFollowUp] = useState<FollowUpAppointment>({
    specialty: "",
    doctor_name: "",
    scheduled_date: "",
    reason: "",
  });
  const [currentHealthEducation, setCurrentHealthEducation] = useState("");
  const [currentProcedure, setCurrentProcedure] = useState("");

  useEffect(() => {
    checkAuth();
    if (patientId) {
      fetchPatient(parseInt(patientId));
    }
    if (admissionId) {
      fetchAdmission(parseInt(admissionId));
    }
  }, [patientId, admissionId]);

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

  const fetchAdmission = async (id: number) => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/admission/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAdmission(data);
        setDischargeData(prev => ({
          ...prev,
          discharge_diagnosis: data.primary_diagnosis || "",
        }));
      }
    } catch (err) {
      console.error("Failed to fetch admission:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddMedication = () => {
    if (currentMedication.name && currentMedication.dosage && currentMedication.frequency) {
      setDischargeData({
        ...dischargeData,
        discharge_medications: [...dischargeData.discharge_medications, currentMedication],
      });
      setCurrentMedication({
        name: "",
        dosage: "",
        frequency: "",
        duration: "",
        indication: "",
      });
    }
  };

  const handleRemoveMedication = (index: number) => {
    setDischargeData({
      ...dischargeData,
      discharge_medications: dischargeData.discharge_medications.filter((_, i) => i !== index),
    });
  };

  const handleAddInstruction = () => {
    if (currentInstruction.trim()) {
      setDischargeData({
        ...dischargeData,
        instructions: [...dischargeData.instructions, currentInstruction.trim()],
      });
      setCurrentInstruction("");
    }
  };

  const handleRemoveInstruction = (index: number) => {
    setDischargeData({
      ...dischargeData,
      instructions: dischargeData.instructions.filter((_, i) => i !== index),
    });
  };

  const handleAddFollowUp = () => {
    if (currentFollowUp.specialty && currentFollowUp.reason) {
      setDischargeData({
        ...dischargeData,
        follow_up_appointments: [...dischargeData.follow_up_appointments, currentFollowUp],
      });
      setCurrentFollowUp({
        specialty: "",
        doctor_name: "",
        scheduled_date: "",
        reason: "",
      });
    }
  };

  const handleRemoveFollowUp = (index: number) => {
    setDischargeData({
      ...dischargeData,
      follow_up_appointments: dischargeData.follow_up_appointments.filter((_, i) => i !== index),
    });
  };

  const handleAddHealthEducation = () => {
    if (currentHealthEducation.trim()) {
      setDischargeData({
        ...dischargeData,
        health_education: [...dischargeData.health_education, currentHealthEducation.trim()],
      });
      setCurrentHealthEducation("");
    }
  };

  const handleRemoveHealthEducation = (index: number) => {
    setDischargeData({
      ...dischargeData,
      health_education: dischargeData.health_education.filter((_, i) => i !== index),
    });
  };

  const handleAddProcedure = () => {
    if (currentProcedure.trim()) {
      setDischargeData({
        ...dischargeData,
        secondary_procedures: [...dischargeData.secondary_procedures, currentProcedure.trim()],
      });
      setCurrentProcedure("");
    }
  };

  const handleRemoveProcedure = (index: number) => {
    setDischargeData({
      ...dischargeData,
      secondary_procedures: dischargeData.secondary_procedures.filter((_, i) => i !== index),
    });
  };

  const handleToggleDocument = (doc: string) => {
    setDischargeData({
      ...dischargeData,
      given_documents: dischargeData.given_documents.includes(doc)
        ? dischargeData.given_documents.filter(d => d !== doc)
        : [...dischargeData.given_documents, doc],
    });
  };

  const handleToggleReferral = (specialty: string) => {
    setDischargeData({
      ...dischargeData,
      referral_specialties: dischargeData.referral_specialties.includes(specialty)
        ? dischargeData.referral_specialties.filter(s => s !== specialty)
        : [...dischargeData.referral_specialties, specialty],
    });
  };

  const calculateLengthOfStay = () => {
    if (!admission?.admission_date) return 0;
    const admissionDate = new Date(admission.admission_date);
    const discharge = new Date(dischargeData.discharge_date);
    const diff = Math.floor((discharge.getTime() - admissionDate.getTime()) / (1000 * 60 * 60 * 24));
    return diff > 0 ? diff : 0;
  };

  const calculateEstimatedCost = () => {
    if (!admission) return 0;
    const los = calculateLengthOfStay() + 1; // Include admission day
    return admission.daily_rate * los;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!patient || !admission) {
      alert("Data pasien atau admisi tidak ditemukan");
      return;
    }

    if (dischargeData.discharge_status === "deceased") {
      const confirmed = confirm("Apakah pasien benar-benar meninggal? Tindakan ini akan merekam kematian pasien.");
      if (!confirmed) return;
    }

    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    setSubmitting(true);

    try {
      const payload = {
        admission_id: admission.id,
        patient_id: patient.id,
        ...dischargeData,
      };

      const response = await fetch("/api/v1/discharge", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to create discharge");
      }

      const data = await response.json();
      alert(`Pasien berhasil dipulangkan. Surat Kontrol: ${data.control_number}`);

      router.push(`/app/patients/${patient.id}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to create discharge");
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

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat("id-ID").format(num);
  };

  const availableDocuments = [
    "Surat Kontrol",
    "Surat Sakit",
    "Surat Rujukan",
    "Ringkasan Rawat Inap",
    "Hasil Lab",
    "Hasil Radiologi",
    "Keping Resep Asli",
    "Epidemiologi Report",
  ];

  const availableSpecialties = [
    "Penyakit Dalam",
    "Bedah",
    "Anak",
    "Kandungan",
    "Mata",
    "THT",
    "Kulit & Kelamin",
    "Syaraf",
    "Jantung",
    "Paru",
    "Gigi",
    "Orthopedi",
    "Urologi",
    "Psikiatri",
  ];

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
        <h1 className="text-2xl font-bold text-gray-900">Formulir Pulang</h1>
        <p className="text-gray-600 mt-1">Dokumentasi pemulangan pasien rawat inap</p>
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
        {/* Patient & Admission Info */}
        {patient && admission && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Informasi Pasien</h2>
                <div className="space-y-1">
                  <p className="text-sm"><span className="text-gray-500">Nama:</span> <span className="font-medium text-gray-900">{patient.name}</span></p>
                  <p className="text-sm"><span className="text-gray-500">No RM:</span> <span className="font-medium text-gray-900">{patient.medical_record_number}</span></p>
                  <p className="text-sm"><span className="text-gray-500">Usia/JK:</span> <span className="font-medium text-gray-900">{patient.age} th / {patient.gender === "male" ? "L" : "P"}</span></p>
                  <p className="text-sm"><span className="text-gray-500">Jaminan:</span> <span className="font-medium text-gray-900 capitalize">{patient.insurance_type}</span></p>
                </div>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Informasi Rawat Inap</h2>
                <div className="space-y-1">
                  <p className="text-sm"><span className="text-gray-500">No ADM:</span> <span className="font-medium text-gray-900">{admission.admission_number}</span></p>
                  <p className="text-sm"><span className="text-gray-500">Kamar/Bed:</span> <span className="font-medium text-gray-900">{admission.room} / {admission.bed}</span></p>
                  <p className="text-sm"><span className="text-gray-500">Ruangan:</span> <span className="font-medium text-gray-900">{admission.ward} - {admission.class}</span></p>
                  <p className="text-sm"><span className="text-gray-500">Tanggal Masuk:</span> <span className="font-medium text-gray-900">{new Date(admission.admission_date).toLocaleDateString("id-ID")}</span></p>
                  <p className="text-sm"><span className="text-gray-500">Lama Rawat:</span> <span className="font-medium text-gray-900">{calculateLengthOfStay()} hari</span></p>
                  <p className="text-sm"><span className="text-gray-500">DPJP:</span> <span className="font-medium text-gray-900">{admission.attending_physician}</span></p>
                </div>
              </div>
            </div>

            {patient.allergies && patient.allergies.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-xs font-medium text-red-900 mb-2">Alergi Pasien</p>
                <div className="flex flex-wrap gap-2">
                  {patient.allergies.map((allergy, idx) => (
                    <span key={idx} className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs">
                      {allergy}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Discharge Details */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Detail Pemulangan</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tanggal Pulang *</label>
              <input
                type="date"
                required
                value={dischargeData.discharge_date}
                onChange={(e) => setDischargeData({ ...dischargeData, discharge_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Waktu Pulang</label>
              <input
                type="time"
                value={dischargeData.discharge_time}
                onChange={(e) => setDischargeData({ ...dischargeData, discharge_time: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status Pulang *</label>
              <select
                required
                value={dischargeData.discharge_status}
                onChange={(e) => setDischargeData({ ...dischargeData, discharge_status: e.target.value as any })}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 ${
                  dischargeData.discharge_status === "deceased"
                    ? "bg-red-50 border-red-300 focus:border-red-500 focus:ring-red-500"
                    : "border-gray-300"
                }`}
              >
                <option value="recovered">Sembuh</option>
                <option value="improved">Membaik</option>
                <option value="unimproved">Tidak Membaik</option>
                <option value="transferred">Dirujuk</option>
                <option value="lama">Pulang Atas Permintaan (PAP)</option>
                <option value="request">Pulang Paksa</option>
                <option value="deceased">Meninggal</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tujuan Pulang *</label>
              <select
                required
                value={dischargeData.discharge_destination}
                onChange={(e) => setDischargeData({ ...dischargeData, discharge_destination: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="home">Pulang ke Rumah</option>
                <option value="transfer_facility">Transfer ke Fasilitas Lain</option>
                <option value="rehab">Rehabilitasi</option>
                <option value="nursing_home">Nursing Home</option>
                <option value="other">Lainnya</option>
              </select>
            </div>

            {dischargeData.discharge_destination === "transfer_facility" && (
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Nama Fasilitas Tujuan</label>
                <input
                  type="text"
                  value={dischargeData.transfer_facility_name}
                  onChange={(e) => setDischargeData({ ...dischargeData, transfer_facility_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Nama rumah sakit atau fasilitas kesehatan tujuan"
                />
              </div>
            )}
          </div>
        </div>

        {/* Diagnosis & Procedures */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Diagnosa & Prosedur</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Diagnosa Saat Pulang *</label>
              <input
                type="text"
                required
                value={dischargeData.discharge_diagnosis}
                onChange={(e) => setDischargeData({ ...dischargeData, discharge_diagnosis: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Diagnosa akhir atau diagnosa kerja"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Prosedur Utama</label>
              <input
                type="text"
                value={dischargeData.principal_procedure || ""}
                onChange={(e) => setDischargeData({ ...dischargeData, principal_procedure: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Prosedur utama yang dilakukan"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Prosedur Sekunder</label>
              <div className="space-y-2">
                {dischargeData.secondary_procedures.map((proc, idx) => (
                  <div key={idx} className="flex items-center space-x-2 bg-gray-50 px-3 py-2 rounded">
                    <span className="text-sm flex-1">{idx + 1}. {proc}</span>
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
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={currentProcedure}
                    onChange={(e) => setCurrentProcedure(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), handleAddProcedure())}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Tambah prosedur sekunder..."
                  />
                  <button
                    type="button"
                    onClick={handleAddProcedure}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Tambah
                  </button>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Komplikasi</label>
              <textarea
                value={dischargeData.complications || ""}
                onChange={(e) => setDischargeData({ ...dischargeData, complications: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Komplikasi yang terjadi selama rawat inap (jika ada)"
              />
            </div>
          </div>
        </div>

        {/* Treatment Summary & Outcome */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Ringkasan Perawatan & Outcome</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ringkasan Perawatan *</label>
              <textarea
                required
                value={dischargeData.treatment_summary}
                onChange={(e) => setDischargeData({ ...dischargeData, treatment_summary: e.target.value })}
                rows={5}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Ringkasan perawatan selama rawat inap, tatalaksana yang diberikan, dan respon pasien"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Outcome/Hasil Akhir *</label>
              <textarea
                required
                value={dischargeData.outcome}
                onChange={(e) => setDischargeData({ ...dischargeData, outcome: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Kondisi pasien saat pulang, rekomendasi, dan prognosis"
              />
            </div>
          </div>
        </div>

        {/* Discharge Medications */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Obat Pulang</h2>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Nama Obat</label>
                <input
                  type="text"
                  value={currentMedication.name}
                  onChange={(e) => setCurrentMedication({ ...currentMedication, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Nama obat"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Dosis</label>
                <input
                  type="text"
                  value={currentMedication.dosage}
                  onChange={(e) => setCurrentMedication({ ...currentMedication, dosage: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Contoh: 500mg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Frekuensi</label>
                <input
                  type="text"
                  value={currentMedication.frequency}
                  onChange={(e) => setCurrentMedication({ ...currentMedication, frequency: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Contoh: 3x1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Durasi</label>
                <input
                  type="text"
                  value={currentMedication.duration}
                  onChange={(e) => setCurrentMedication({ ...currentMedication, duration: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Contoh: 7 hari"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Indikasi</label>
                <input
                  type="text"
                  value={currentMedication.indication}
                  onChange={(e) => setCurrentMedication({ ...currentMedication, indication: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Untuk apa obat ini diberikan"
                />
              </div>
              <div className="flex items-end">
                <button
                  type="button"
                  onClick={handleAddMedication}
                  className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Tambah Obat
                </button>
              </div>
            </div>

            {dischargeData.discharge_medications.length > 0 && (
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Obat</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Dosis</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Frekuensi</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Durasi</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Indikasi</th>
                      <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Aksi</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {dischargeData.discharge_medications.map((med, idx) => (
                      <tr key={idx}>
                        <td className="px-4 py-2 text-sm text-gray-900">{med.name}</td>
                        <td className="px-4 py-2 text-sm text-gray-600">{med.dosage}</td>
                        <td className="px-4 py-2 text-sm text-gray-600">{med.frequency}</td>
                        <td className="px-4 py-2 text-sm text-gray-600">{med.duration}</td>
                        <td className="px-4 py-2 text-sm text-gray-600">{med.indication}</td>
                        <td className="px-4 py-2 text-center">
                          <button
                            type="button"
                            onClick={() => handleRemoveMedication(idx)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Instructions & Education */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Instruksi & Edukasi Kesehatan</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Instructions */}
            <div>
              <h3 className="font-medium text-gray-900 mb-3">Instruksi Khusus</h3>
              <div className="space-y-2 mb-3">
                {dischargeData.instructions.map((instruction, idx) => (
                  <div key={idx} className="flex items-start space-x-2 bg-blue-50 px-3 py-2 rounded">
                    <span className="text-blue-600 flex-shrink-0">{idx + 1}.</span>
                    <span className="text-sm text-blue-900 flex-1">{instruction}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveInstruction(idx)}
                      className="text-red-600 hover:text-red-800 flex-shrink-0"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={currentInstruction}
                  onChange={(e) => setCurrentInstruction(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), handleAddInstruction())}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                  placeholder="Tambah instruksi..."
                />
                <button
                  type="button"
                  onClick={handleAddInstruction}
                  className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                >
                  Tambah
                </button>
              </div>
            </div>

            {/* Health Education */}
            <div>
              <h3 className="font-medium text-gray-900 mb-3">Edukasi Kesehatan</h3>
              <div className="space-y-2 mb-3">
                {dischargeData.health_education.map((edu, idx) => (
                  <div key={idx} className="flex items-start space-x-2 bg-green-50 px-3 py-2 rounded">
                    <span className="text-green-600 flex-shrink-0">📚</span>
                    <span className="text-sm text-green-900 flex-1">{edu}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveHealthEducation(idx)}
                      className="text-red-600 hover:text-red-800 flex-shrink-0"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={currentHealthEducation}
                  onChange={(e) => setCurrentHealthEducation(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), handleAddHealthEducation())}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                  placeholder="Tambah edukasi..."
                />
                <button
                  type="button"
                  onClick={handleAddHealthEducation}
                  className="px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                >
                  Tambah
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Follow-up & Referrals */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Rencana Kontrol & Rujukan</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Follow-up Appointments */}
            <div>
              <h3 className="font-medium text-gray-900 mb-3">Rencana Kontrol</h3>
              <div className="space-y-2 mb-3">
                {dischargeData.follow_up_appointments.map((appt, idx) => (
                  <div key={idx} className="bg-purple-50 px-3 py-2 rounded">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-purple-900">{appt.specialty}</p>
                        {appt.doctor_name && <p className="text-xs text-purple-600">{appt.doctor_name}</p>}
                        {appt.scheduled_date && <p className="text-xs text-purple-600">{new Date(appt.scheduled_date).toLocaleDateString("id-ID")}</p>}
                        <p className="text-xs text-purple-500">{appt.reason}</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveFollowUp(idx)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-2 gap-2 mb-2">
                <select
                  value={currentFollowUp.specialty}
                  onChange={(e) => setCurrentFollowUp({ ...currentFollowUp, specialty: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-sm"
                >
                  <option value="">Pilih Poli</option>
                  {availableSpecialties.map(spec => (
                    <option key={spec} value={spec}>{spec}</option>
                  ))}
                </select>
                <input
                  type="date"
                  value={currentFollowUp.scheduled_date || ""}
                  onChange={(e) => setCurrentFollowUp({ ...currentFollowUp, scheduled_date: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-sm"
                />
              </div>
              <div className="grid grid-cols-2 gap-2 mb-2">
                <input
                  type="text"
                  placeholder="Nama dokter (opsional)"
                  value={currentFollowUp.doctor_name || ""}
                  onChange={(e) => setCurrentFollowUp({ ...currentFollowUp, doctor_name: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-sm"
                />
                <button
                  type="button"
                  onClick={handleAddFollowUp}
                  className="px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm"
                >
                  Tambah
                </button>
              </div>
            </div>

            {/* Referrals */}
            <div>
              <h3 className="font-medium text-gray-900 mb-3">Rujukan ke Spesialis</h3>
              <div className="grid grid-cols-2 gap-2">
                {availableSpecialties.map(specialty => (
                  <button
                    key={specialty}
                    type="button"
                    onClick={() => handleToggleReferral(specialty)}
                    className={`px-3 py-2 rounded-lg text-sm text-left transition-colors ${
                      dischargeData.referral_specialties.includes(specialty)
                        ? "bg-orange-600 text-white"
                        : "bg-orange-100 text-orange-700 hover:bg-orange-200"
                    }`}
                  >
                    {dischargeData.referral_specialties.includes(specialty) && "✓ "}
                    {specialty}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Documents Given */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Dokumen yang Diberikan</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {availableDocuments.map(doc => (
              <button
                key={doc}
                type="button"
                onClick={() => handleToggleDocument(doc)}
                className={`px-4 py-3 rounded-lg text-sm transition-colors ${
                  dischargeData.given_documents.includes(doc)
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {dischargeData.given_documents.includes(doc) && "✓ "}
                {doc}
              </button>
            ))}
          </div>
        </div>

        {/* Cost Summary */}
        {admission && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Ringkasan Biaya</h2>
            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Biaya Kamar/Hari</span>
                <span className="font-medium text-gray-900">{formatCurrency(admission.daily_rate)}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Lama Rawat</span>
                <span className="font-medium text-gray-900">{calculateLengthOfStay()} hari</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Kelas</span>
                <span className="font-medium text-gray-900 capitalize">{admission.class.replace("_", " ")}</span>
              </div>
              <div className="flex justify-between py-2 bg-indigo-50 px-3 rounded">
                <span className="text-indigo-900 font-medium">Estimasi Total</span>
                <span className="text-lg font-bold text-indigo-900">{formatCurrency(calculateEstimatedCost())}</span>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-3">
              * Estimasi biaya kamar saja. Total biaya akan dihitung setelah penghitungan tagihan lengkap.
            </p>
          </div>
        )}

        {/* Death Warning */}
        {dischargeData.discharge_status === "deceased" && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-start space-x-3">
              <svg className="w-8 h-8 text-red-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div>
                <h3 className="text-lg font-medium text-red-900">Kematian Pasien</h3>
                <p className="text-sm text-red-700 mt-2">
                  Anda akan merekam kematian pasien. Tindakan ini akan memicu protokol kematian dan memerlukan dokumentasi tambahan termasuk surat kematian medis.
                </p>
              </div>
            </div>
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
            disabled={submitting || !patient || !admission}
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
                <span>Pulangkan Pasien</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default function DischargeFormPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    }>
      <DischargeFormPageContent />
    </Suspense>
  );
}
