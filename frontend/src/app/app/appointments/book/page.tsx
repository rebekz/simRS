"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

interface Patient {
  id: number;
  name: string;
  medical_record_number: string;
  age: number;
  gender: string;
  phone?: string;
  blood_type?: string;
  allergies?: string[];
  insurance_type?: "bpjs" | "insurance" | "self_pay" | "corporate";
}

interface Doctor {
  id: number;
  name: string;
  specialty: string;
  department: string;
  available: boolean;
  consultation_fee: number;
  bpjs_tariff?: number;
}

interface Schedule {
  id: number;
  doctor_id: number;
  date: string;
  start_time: string;
  end_time: string;
  available: boolean;
  clinic: string;
}

interface TimeSlot {
  time: string;
  available: boolean;
  doctor: string;
}

function AppointmentBookingPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const patientId = searchParams.get("patient_id");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [patient, setPatient] = useState<Patient | null>(null);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);
  const [submitting, setSubmitting] = useState(false);

  const [selectedDepartment, setSelectedDepartment] = useState("");
  const [selectedSpecialty, setSelectedSpecialty] = useState("");
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);

  const [bookingData, setBookingData] = useState({
    appointment_type: "new" as "new" | "follow_up" | "consultation",
    chief_complaint: "",
    symptoms: "",
    urgency: "routine" as "routine" | "urgent" | "emergency",
    notes: "",
    preferred_time: "" as "morning" | "afternoon" | "evening",
    phone: "",
  });

  const departments = [
    { id: "internal_medicine", name: "Penyakit Dalam", specialties: ["Internal Medicine", "Cardiology", "Pulmonology", "Gastroenterology", "Nephrology", "Endocrinology"] },
    { id: "surgery", name: "Bedah", specialties: ["General Surgery", "Orthopedics", "Neurosurgery", "Urology", "Cardiothoracic"] },
    { id: "pediatrics", name: "Anak", specialties: ["Pediatrics", "Neonatology"] },
    { id: "obgyn", name: "Kandungan", specialties: ["Obstetrics", "Gynecology"] },
    { id: "eye", name: "Mata", specialties: ["Ophthalmology"] },
    { id: "ent", name: "THT", specialties: ["Otolaryngology"] },
    { id: "dermatology", name: "Kulit & Kelamin", specialties: ["Dermatology", "Venereology"] },
    { id: "neurology", name: "Saraf", specialties: ["Neurology"] },
    { id: "psychiatry", name: "Jiwa", specialties: ["Psychiatry"] },
    { id: "dental", name: "Gigi", specialties: ["Dentistry", "Oral Surgery"] },
    { id: "orthopedics", name: "Orthopedi", specialties: ["Orthopedics"] },
  ];

  useEffect(() => {
    checkAuth();
    if (patientId) {
      fetchPatient(parseInt(patientId));
    }
  }, [patientId]);

  useEffect(() => {
    if (selectedDepartment || selectedSpecialty) {
      fetchDoctors();
    }
  }, [selectedDepartment, selectedSpecialty]);

  useEffect(() => {
    if (selectedDoctor && selectedDate) {
      fetchAvailableSlots();
    }
  }, [selectedDoctor, selectedDate]);

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
        setBookingData(prev => ({ ...prev, phone: data.phone || "" }));
      }
    } catch (err) {
      console.error("Failed to fetch patient:", err);
    }
  };

  const fetchDoctors = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const queryParams = new URLSearchParams();
      if (selectedSpecialty) queryParams.append("specialty", selectedSpecialty);
      if (selectedDepartment) queryParams.append("department", selectedDepartment);

      const response = await fetch(`/api/v1/doctors/available?${queryParams}`, {
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

  const fetchAvailableSlots = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token || !selectedDoctor) return;

    try {
      const response = await fetch(
        `/api/v1/appointments/slots?doctor_id=${selectedDoctor.id}&date=${selectedDate}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAvailableSlots(data.slots || []);
      }
    } catch (err) {
      console.error("Failed to fetch slots:", err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!patient) {
      alert("Pasien tidak ditemukan");
      return;
    }

    if (!selectedDoctor) {
      alert("Pilih dokter");
      return;
    }

    if (!selectedDate) {
      alert("Pilih tanggal janji temu");
      return;
    }

    if (!selectedSlot) {
      alert("Pilih jam janji temu");
      return;
    }

    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    setSubmitting(true);

    try {
      const payload = {
        patient_id: patient.id,
        doctor_id: selectedDoctor.id,
        schedule_id: selectedSlot.available ? null : null,
        appointment_date: selectedDate,
        appointment_time: selectedSlot.time,
        appointment_type: bookingData.appointment_type,
        chief_complaint: bookingData.chief_complaint,
        symptoms: bookingData.symptoms,
        urgency: bookingData.urgency,
        notes: bookingData.notes,
        phone: bookingData.phone,
      };

      const response = await fetch("/api/v1/appointments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to create appointment");
      }

      const data = await response.json();
      alert(`Janji temu berhasil dibuat. No Antrian: ${data.queue_number}`);

      router.push("/app/appointments");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to create appointment");
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

  const generateTimeSlots = () => {
    const slots: TimeSlot[] = [];
    const startHour = 8;
    const endHour = 17;

    for (let hour = startHour; hour < endHour; hour++) {
      for (let min = 0; min < 60; min += 30) {
        const time = `${hour.toString().padStart(2, "0")}:${min.toString().padStart(2, "0")}`;
        const isAvailable = availableSlots.some(
          slot => slot.time === time && slot.available
        );
        slots.push({
          time,
          available: isAvailable || availableSlots.length === 0,
          doctor: selectedDoctor?.name || "",
        });
      }
    }
    return slots;
  };

  const getTimeSlotStatus = (slot: TimeSlot) => {
    if (slot.available) {
      return { label: "Tersedia", className: "bg-green-100 text-green-700" };
    }
    return { label: "Penuh", className: "bg-red-100 text-red-700" };
  };

  const getUrgencyBadge = (urgency: string) => {
    const badges: Record<string, { label: string; className: string }> = {
      routine: { label: "Routine", className: "bg-blue-100 text-blue-700" },
      urgent: { label: "Urgent", className: "bg-yellow-100 text-yellow-700" },
      emergency: { label: "Emergency", className: "bg-red-100 text-red-700" },
    };
    return badges[urgency] || badges.routine;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Buat Janji Temu</h1>
        <p className="text-gray-600 mt-1">Jadwalkan janji temu pasien rawat jalan</p>
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
                  {patient.insurance_type === "insurance" && "🛡️ Asuransi"}
                  {patient.insurance_type === "corporate" && "🏢 Korporat"}
                  {patient.insurance_type === "self_pay" && "💵 Biaya Pribadi"}
                </p>
              </div>
            </div>

            {patient.allergies && patient.allergies.length > 0 && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
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

        {/* Department & Doctor Selection */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Pilih Dokter</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Departemen</label>
              <select
                value={selectedDepartment}
                onChange={(e) => {
                  setSelectedDepartment(e.target.value);
                  setSelectedSpecialty("");
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Pilih Departemen</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>{dept.name}</option>
                ))}
              </select>
            </div>

            {selectedDepartment && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Spesialis</label>
                <select
                  value={selectedSpecialty}
                  onChange={(e) => {
                    setSelectedSpecialty(e.target.value);
                    setSelectedDoctor(null);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">Pilih Spesialis</option>
                  {departments
                    .find((d) => d.id === selectedDepartment)
                    ?.specialties.map((spec) => (
                      <option key={spec} value={spec}>{spec}</option>
                    ))}
                </select>
              </div>
            )}

            {selectedSpecialty && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Dokter Tersedia</label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {doctors.map((doctor) => {
                    const isSelected = selectedDoctor?.id === doctor.id;
                    return (
                      <div
                        key={doctor.id}
                        onClick={() => doctor.available && setSelectedDoctor(doctor)}
                        className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                          isSelected
                            ? "border-indigo-500 bg-indigo-50"
                            : doctor.available
                            ? "border-gray-200 hover:border-gray-300"
                            : "border-gray-200 bg-gray-50 opacity-50"
                        }`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <h3 className="font-medium text-gray-900">{doctor.name}</h3>
                            <p className="text-sm text-gray-500">{doctor.specialty}</p>
                            <p className="text-xs text-gray-400">{doctor.department}</p>
                          </div>
                          {!doctor.available && (
                            <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs">
                              Tidak Tersedia
                            </span>
                          )}
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">{formatCurrency(doctor.consultation_fee)}</span>
                          {doctor.bpjs_tariff && (
                            <span className="text-xs text-green-600">
                              BPJS: {formatCurrency(doctor.bpjs_tariff)}
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Date & Time Selection */}
        {selectedDoctor && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Pilih Tanggal & Jam</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tanggal Janji Temu *</label>
                <input
                  type="date"
                  required
                  min={new Date().toISOString().split("T")[0]}
                  value={selectedDate}
                  onChange={(e) => {
                    setSelectedDate(e.target.value);
                    setSelectedSlot(null);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              {selectedDate && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">Jam Tersedia</label>
                  <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
                    {generateTimeSlots().map((slot) => {
                      const status = getTimeSlotStatus(slot);
                      return (
                        <button
                          key={slot.time}
                          type="button"
                          onClick={() => slot.available && setSelectedSlot(slot)}
                          disabled={!slot.available}
                          className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                            selectedSlot?.time === slot.time
                              ? "bg-indigo-600 text-white"
                              : slot.available
                              ? "bg-white border border-gray-300 hover:border-indigo-500 hover:bg-indigo-50"
                              : "bg-gray-100 text-gray-400 cursor-not-allowed"
                          }`}
                        >
                          {slot.time}
                        </button>
                      );
                    })}
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Waktu dalam format 24 jam. Hijau: tersedia, Merah: penuh.
                  </p>
                </div>
              )}

              {selectedSlot && (
                <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-indigo-900">Waktu Dipilih</h4>
                      <p className="text-sm text-indigo-700">
                        {new Date(selectedDate).toLocaleDateString("id-ID", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
                      </p>
                      <p className="text-lg font-bold text-indigo-900">{selectedSlot.time}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setSelectedSlot(null)}
                      className="text-indigo-600 hover:text-indigo-800"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Appointment Details */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Detail Janji Temu</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipe Janji Temu *</label>
              <select
                required
                value={bookingData.appointment_type}
                onChange={(e) => setBookingData({ ...bookingData, appointment_type: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="new">Baru</option>
                <option value="follow_up">Kontrol</option>
                <option value="consultation">Konsultasi</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tingkat Urgensi</label>
              <select
                value={bookingData.urgency}
                onChange={(e) => setBookingData({ ...bookingData, urgency: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="routine">Routine</option>
                <option value="urgent">Urgent</option>
                <option value="emergency">Emergency</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Keluhan Utama *</label>
              <input
                type="text"
                required
                value={bookingData.chief_complaint}
                onChange={(e) => setBookingData({ ...bookingData, chief_complaint: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Keluhan utama pasien"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Gejala Tambahan</label>
              <textarea
                value={bookingData.symptoms}
                onChange={(e) => setBookingData({ ...bookingData, symptoms: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Gejala atau informasi tambahan yang relevan"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">No. Telepon</label>
              <input
                type="tel"
                value={bookingData.phone}
                onChange={(e) => setBookingData({ ...bookingData, phone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="08xxxxxxxxxx"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Catatan</label>
              <textarea
                value={bookingData.notes}
                onChange={(e) => setBookingData({ ...bookingData, notes: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Catatan tambahan (opsional)"
              />
            </div>
          </div>
        </div>

        {/* Summary */}
        {selectedDoctor && selectedDate && selectedSlot && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Ringkasan Janji Temu</h2>
            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Pasien</span>
                <span className="font-medium text-gray-900">{patient?.name}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Dokter</span>
                <span className="font-medium text-gray-900">{selectedDoctor.name}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Spesialis</span>
                <span className="font-medium text-gray-900">{selectedDoctor.specialty}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Tanggal</span>
                <span className="font-medium text-gray-900">
                  {new Date(selectedDate).toLocaleDateString("id-ID", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Jam</span>
                <span className="font-medium text-gray-900">{selectedSlot.time}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Tipe</span>
                <span className="font-medium text-gray-900 capitalize">{bookingData.appointment_type}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-gray-600 font-medium">Biaya Konsultasi</span>
                <span className="text-lg font-bold text-indigo-900">{formatCurrency(selectedDoctor.consultation_fee)}</span>
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
            disabled={submitting || !patient || !selectedDoctor || !selectedDate || !selectedSlot}
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
                <span>Buat Janji Temu</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default function AppointmentBookingPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    }>
      <AppointmentBookingPageContent />
    </Suspense>
  );
}
