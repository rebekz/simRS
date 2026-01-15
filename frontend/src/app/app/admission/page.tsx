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

interface Bed {
  id: number;
  bed_number: string;
  ward: string;
  room: string;
  bed_type: "regular" | "vip" | "icu" | "isolation";
  class: "class_1" | "class_2" | "class_3";
  available: boolean;
  daily_rate: number;
}

interface Room {
  id: number;
  room_number: string;
  ward: string;
  floor: number;
  bed_type: "regular" | "vip" | "icu" | "isolation";
  class: "class_1" | "class_2" | "class_3";
  available_beds: number;
  total_beds: number;
  daily_rate: number;
}

interface Doctor {
  id: number;
  name: string;
  specialty: string;
  available: boolean;
}

function AdmissionFormPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const patientId = searchParams.get("patient_id");
  const encounterId = searchParams.get("encounter_id");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [patient, setPatient] = useState<Patient | null>(null);
  const [availableRooms, setAvailableRooms] = useState<Room[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
  const [selectedBed, setSelectedBed] = useState<Bed | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [classFilter, setClassFilter] = useState("");
  const [wardFilter, setWardFilter] = useState("");
  const [bedTypeFilter, setBedTypeFilter] = useState("");

  const [admissionData, setAdmissionData] = useState({
    admission_type: "emergency" as "emergency" | "elective" | "transfer",
    admission_reason: "",
    primary_diagnosis: "",
    secondary_diagnoses: [] as string[],
    currentSecondaryDiagnosis: "",
    attending_physician_id: "",
    referring_physician: "",
    estimated_length_of_stay: "",
    special_instructions: "",
    diet_type: "regular" as "regular" | "fasting" | "soft" | "liquid" | "diabetic" | "low_salt" | "low_fat" | "renal",
    activity_level: "bed_rest" as "bed_rest" | "up_as_tolerated" | "up_with_assistance" | "ambulatory",
    isolation_required: false,
    isolation_type: "" as "standard" | "contact" | "droplet" | "airborne" | "neutropenic",
    deposit_required: false,
    deposit_amount: 0,
  });

  useEffect(() => {
    checkAuth();
    if (patientId) {
      fetchPatient(parseInt(patientId));
    }
    fetchAvailableRooms();
    fetchDoctors();
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

  const fetchAvailableRooms = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const queryParams = new URLSearchParams();
      if (classFilter) queryParams.append("class", classFilter);
      if (wardFilter) queryParams.append("ward", wardFilter);
      if (bedTypeFilter) queryParams.append("bed_type", bedTypeFilter);
      queryParams.append("available", "true");

      const response = await fetch(`/api/v1/admission/rooms/available?${queryParams}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAvailableRooms(data.rooms || []);
      }
    } catch (err) {
      console.error("Failed to fetch rooms:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDoctors = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/doctors/available", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDoctors(data.doctors || []);
      }
    } catch (err) {
      console.error("Failed to fetch doctors:", err);
    }
  };

  const handleRoomSelect = async (room: Room) => {
    setSelectedRoom(room);
    setSelectedBed(null);
  };

  const handleBedSelect = async (bed: Bed) => {
    setSelectedBed(bed);
  };

  const handleAddSecondaryDiagnosis = () => {
    if (admissionData.currentSecondaryDiagnosis.trim()) {
      setAdmissionData({
        ...admissionData,
        secondary_diagnoses: [...admissionData.secondary_diagnoses, admissionData.currentSecondaryDiagnosis.trim()],
        currentSecondaryDiagnosis: "",
      });
    }
  };

  const handleRemoveSecondaryDiagnosis = (index: number) => {
    setAdmissionData({
      ...admissionData,
      secondary_diagnoses: admissionData.secondary_diagnoses.filter((_, i) => i !== index),
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!patient) {
      alert("Pasien tidak ditemukan");
      return;
    }

    if (!selectedBed) {
      alert("Pilih tempat tidur untuk pasien");
      return;
    }

    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    setSubmitting(true);

    try {
      const response = await fetch("/api/v1/admission/admit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          patient_id: patient.id,
          encounter_id: encounterId ? parseInt(encounterId) : null,
          bed_id: selectedBed.id,
          admission_type: admissionData.admission_type,
          admission_reason: admissionData.admission_reason,
          primary_diagnosis: admissionData.primary_diagnosis,
          secondary_diagnoses: admissionData.secondary_diagnoses,
          attending_physician_id: parseInt(admissionData.attending_physician_id),
          referring_physician: admissionData.referring_physician,
          estimated_length_of_stay: admissionData.estimated_length_of_stay ? parseInt(admissionData.estimated_length_of_stay) : null,
          special_instructions: admissionData.special_instructions,
          diet_type: admissionData.diet_type,
          activity_level: admissionData.activity_level,
          isolation_required: admissionData.isolation_required,
          isolation_type: admissionData.isolation_required ? admissionData.isolation_type : null,
          deposit_required: admissionData.deposit_required,
          deposit_amount: admissionData.deposit_required ? admissionData.deposit_amount : null,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create admission");
      }

      const data = await response.json();
      alert(`Pasien berhasil dirawat. No ADM: ${data.admission_number}`);

      router.push(`/app/patients/${patient.id}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to create admission");
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

  const getClassLabel = (cls: string) => {
    const labels: Record<string, string> = {
      class_1: "Kelas 1 (VIP)",
      class_2: "Kelas 2",
      class_3: "Kelas 3",
    };
    return labels[cls] || cls;
  };

  const getClassColor = (cls: string) => {
    const colors: Record<string, string> = {
      class_1: "purple",
      class_2: "blue",
      class_3: "green",
    };
    return colors[cls] || "gray";
  };

  const getBedTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      regular: "Regular",
      vip: "VIP",
      icu: "ICU",
      isolation: "Isolasi",
    };
    return labels[type] || type;
  };

  const getBedTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      regular: "gray",
      vip: "purple",
      icu: "red",
      isolation: "yellow",
    };
    return colors[type] || "gray";
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
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Formulir Rawat Inap</h1>
        <p className="text-gray-600 mt-1">Admisi pasien ke rawat inap</p>
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
                <p className="text-sm text-gray-500">Golongan Darah</p>
                <p className="text-sm font-medium text-gray-900">{patient.blood_type || "-"}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Jaminan</p>
                <p className="text-sm font-medium text-gray-900 capitalize">
                  {patient.insurance_type === "bpjs" && "🏛️ BPJS"}
                  {patient.insurance_type === "insurance" && "🛡️ Asuransi Swasta"}
                  {patient.insurance_type === "corporate" && "🏢 Korporat"}
                  {patient.insurance_type === "self_pay" && "💵 Biaya Pribadi"}
                </p>
              </div>
            </div>

            {patient.allergies && patient.allergies.length > 0 && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-red-900 mb-2">Alergi Pasien</h4>
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
        ) : (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="flex items-center space-x-3">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="text-sm font-medium text-yellow-900">Pasien Belum Dipilih</h3>
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

        {/* Admission Details */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Detail Pemasukan</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipe Pemasukan *</label>
              <select
                required
                value={admissionData.admission_type}
                onChange={(e) => setAdmissionData({ ...admissionData, admission_type: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="emergency">Emergency (UGD)</option>
                <option value="elective">Elective (Terjadwal)</option>
                <option value="transfer">Transfer (Rujukan)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Estimasi Lama Rawat (Hari)</label>
              <input
                type="number"
                min="1"
                value={admissionData.estimated_length_of_stay}
                onChange={(e) => setAdmissionData({ ...admissionData, estimated_length_of_stay: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Contoh: 3"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Alasan Pemasukan *</label>
              <textarea
                required
                value={admissionData.admission_reason}
                onChange={(e) => setAdmissionData({ ...admissionData, admission_reason: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Jelaskan alasan pemasukan pasien"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Diagnosa Utama *</label>
              <input
                type="text"
                required
                value={admissionData.primary_diagnosis}
                onChange={(e) => setAdmissionData({ ...admissionData, primary_diagnosis: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Contoh: Pneumonia (J18.9)"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Diagnosa Sekunder</label>
              <div className="space-y-2">
                {admissionData.secondary_diagnoses.map((diagnosis, idx) => (
                  <div key={idx} className="flex items-center space-x-2 bg-gray-50 px-3 py-2 rounded">
                    <span className="text-sm flex-1">{idx + 1}. {diagnosis}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveSecondaryDiagnosis(idx)}
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
                    value={admissionData.currentSecondaryDiagnosis}
                    onChange={(e) => setAdmissionData({ ...admissionData, currentSecondaryDiagnosis: e.target.value })}
                    onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), handleAddSecondaryDiagnosis())}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Tambah diagnosa sekunder..."
                  />
                  <button
                    type="button"
                    onClick={handleAddSecondaryDiagnosis}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Tambah
                  </button>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Dokter Penanggung Jawab *</label>
              <select
                required
                value={admissionData.attending_physician_id}
                onChange={(e) => setAdmissionData({ ...admissionData, attending_physician_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Pilih Dokter</option>
                {doctors.map(doctor => (
                  <option key={doctor.id} value={doctor.id} disabled={!doctor.available}>
                    {doctor.name} - {doctor.specialty} {!doctor.available && "(Tidak Tersedia)"}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Dokter Perujuk</label>
              <input
                type="text"
                value={admissionData.referring_physician}
                onChange={(e) => setAdmissionData({ ...admissionData, referring_physician: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Nama dokter perujuk (jika ada)"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Instruksi Khusus</label>
              <textarea
                value={admissionData.special_instructions}
                onChange={(e) => setAdmissionData({ ...admissionData, special_instructions: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Instruksi khusus untuk perawatan pasien"
              />
            </div>
          </div>
        </div>

        {/* Room Selection */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Pilih Kamar & Tempat Tidur</h2>
            <div className="flex space-x-2">
              <select
                value={classFilter}
                onChange={(e) => { setClassFilter(e.target.value); fetchAvailableRooms(); }}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              >
                <option value="">Semua Kelas</option>
                <option value="class_1">Kelas 1</option>
                <option value="class_2">Kelas 2</option>
                <option value="class_3">Kelas 3</option>
              </select>
              <select
                value={bedTypeFilter}
                onChange={(e) => { setBedTypeFilter(e.target.value); fetchAvailableRooms(); }}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              >
                <option value="">Semua Tipe</option>
                <option value="regular">Regular</option>
                <option value="vip">VIP</option>
                <option value="icu">ICU</option>
                <option value="isolation">Isolasi</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
            {availableRooms.map((room) => (
              <div
                key={room.id}
                className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedRoom?.id === room.id
                    ? "border-indigo-500 bg-indigo-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
                onClick={() => handleRoomSelect(room)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">Kamar {room.room_number}</h3>
                    <p className="text-sm text-gray-500">{room.ward} - Lt {room.floor}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium bg-${getClassColor(room.class)}-100 text-${getClassColor(room.class)}-700`}>
                    {getClassLabel(room.class)}
                  </span>
                </div>
                <div className="flex items-center space-x-2 mb-2">
                  <span className={`px-2 py-0.5 rounded text-xs bg-${getBedTypeColor(room.bed_type)}-100 text-${getBedTypeColor(room.bed_type)}-700`}>
                    {getBedTypeLabel(room.bed_type)}
                  </span>
                  <span className="text-xs text-gray-500">
                    {room.available_beds}/{room.total_beds} tersedia
                  </span>
                </div>
                <p className="text-sm font-medium text-gray-900">{formatCurrency(room.daily_rate)}</p>
              </div>
            ))}
          </div>

          {selectedRoom && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-3">Tempat Tidur Tersedia - Kamar {selectedRoom.room_number}</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {Array.from({ length: selectedRoom.total_beds }, (_, i) => {
                  const bedNumber = `${selectedRoom.room_number}-${String(i + 1).padStart(2, "0")}`;
                  const isSelected = selectedBed?.bed_number === bedNumber;
                  return (
                    <div
                      key={i}
                      className={`border rounded-lg p-3 text-center cursor-pointer transition-colors ${
                        isSelected
                          ? "border-indigo-500 bg-indigo-100"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                      onClick={() => handleBedSelect({
                        id: selectedRoom.id * 100 + i,
                        bed_number: bedNumber,
                        ward: selectedRoom.ward,
                        room: selectedRoom.room_number,
                        bed_type: selectedRoom.bed_type,
                        class: selectedRoom.class,
                        available: true,
                        daily_rate: selectedRoom.daily_rate,
                      })}
                    >
                      <p className="text-sm font-medium text-gray-900">{bedNumber}</p>
                      <p className="text-xs text-gray-500">{getBedTypeLabel(selectedRoom.bed_type)}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {selectedBed && (
            <div className="mt-4 bg-indigo-50 border border-indigo-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-indigo-900">Tempat Tidur Dipilih</h4>
                  <p className="text-sm text-indigo-700">
                    {selectedBed.bed_number} • {selectedBed.ward} • {selectedBed.room} • {getClassLabel(selectedBed.class)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-indigo-900">{formatCurrency(selectedBed.daily_rate)}</p>
                  <p className="text-xs text-indigo-600">per hari</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Nursing Orders */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Order Perawatan</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipe Diet</label>
              <select
                value={admissionData.diet_type}
                onChange={(e) => setAdmissionData({ ...admissionData, diet_type: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="regular">Regular</option>
                <option value="fasting">Puasa (NPO)</option>
                <option value="soft">Lunak</option>
                <option value="liquid">Cair</option>
                <option value="diabetic">Diabetik</option>
                <option value="low_salt">Rendah Garam</option>
                <option value="low_fat">Rendah Lemak</option>
                <option value="renal">Ginjal</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tingkat Aktivitas</label>
              <select
                value={admissionData.activity_level}
                onChange={(e) => setAdmissionData({ ...admissionData, activity_level: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="bed_rest">Bed Rest (Tirah Baring)</option>
                <option value="up_as_tolerated">Up As Tolerated</option>
                <option value="up_with_assistance">Up With Assistance</option>
                <option value="ambulatory">Ambulatori</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <input
                  type="checkbox"
                  checked={admissionData.isolation_required}
                  onChange={(e) => setAdmissionData({ ...admissionData, isolation_required: e.target.checked })}
                  className="mr-2"
                />
                Perlu Isolasi
              </label>
              {admissionData.isolation_required && (
                <select
                  value={admissionData.isolation_type}
                  onChange={(e) => setAdmissionData({ ...admissionData, isolation_type: e.target.value as any })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 mt-2"
                >
                  <option value="standard">Standard</option>
                  <option value="contact">Contact</option>
                  <option value="droplet">Droplet</option>
                  <option value="airborne">Airborne</option>
                  <option value="neutropenic">Neutropenic</option>
                </select>
              )}
            </div>
          </div>
        </div>

        {/* Deposit */}
        {patient?.insurance_type === "self_pay" && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-4">
              <input
                type="checkbox"
                id="deposit_required"
                checked={admissionData.deposit_required}
                onChange={(e) => setAdmissionData({ ...admissionData, deposit_required: e.target.checked })}
                className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
              />
              <label htmlFor="deposit_required" className="text-sm font-medium text-gray-900">
                Deposit Diperlukan (Untuk Pasien Biaya Pribadi)
              </label>
            </div>
            {admissionData.deposit_required && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Jumlah Deposit</label>
                <input
                  type="number"
                  min="0"
                  step="100000"
                  value={admissionData.deposit_amount}
                  onChange={(e) => setAdmissionData({ ...admissionData, deposit_amount: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Contoh: 1000000"
                />
              </div>
            )}
          </div>
        )}

        {/* Summary */}
        {selectedBed && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Ringkasan Pemasukan</h2>
            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Pasien</span>
                <span className="font-medium text-gray-900">{patient?.name}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Tipe Pemasukan</span>
                <span className="font-medium text-gray-900 capitalize">{admissionData.admission_type}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Kamar & Bed</span>
                <span className="font-medium text-gray-900">{selectedBed.bed_number} ({selectedBed.ward})</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Kelas</span>
                <span className="font-medium text-gray-900">{getClassLabel(selectedBed.class)}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Biaya Kamar/Hari</span>
                <span className="font-medium text-gray-900">{formatCurrency(selectedBed.daily_rate)}</span>
              </div>
              {admissionData.estimated_length_of_stay && (
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Estimasi Biaya</span>
                  <span className="font-medium text-gray-900">
                    {formatCurrency(selectedBed.daily_rate * parseInt(admissionData.estimated_length_of_stay))}
                  </span>
                </div>
              )}
              {admissionData.deposit_required && admissionData.deposit_amount > 0 && (
                <div className="flex justify-between py-2 bg-yellow-50 px-3 rounded">
                  <span className="text-yellow-900 font-medium">Deposit</span>
                  <span className="font-bold text-yellow-900">{formatCurrency(admissionData.deposit_amount)}</span>
                </div>
              )}
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
            disabled={submitting || !selectedBed || !patient}
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
                <span>Rawatkan Pasien</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default function AdmissionFormPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    }>
      <AdmissionFormPageContent />
    </Suspense>
  );
}
