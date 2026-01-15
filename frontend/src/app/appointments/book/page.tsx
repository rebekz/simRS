"use client";

import { useState, useMemo } from "react";
import {
  Calendar,
  Clock,
  User,
  Phone,
  CreditCard,
  CheckCircle,
  Bell,
  ChevronRight,
  Info,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";

/**
 * WEB-S-3.5: Online Appointment Booking
 *
 * Key Features:
 * - Public-facing booking page (no authentication required)
 * - Department, doctor, date, time slot selection
 * - Patient details form (name, phone, optional BPJS)
 * - Booking confirmation with queue number
 * - Available slot management
 * - SMS reminder option
 */

// ============================================================================
// TYPES
// ============================================================================

interface Department {
  id: string;
  name: string;
  icon: string;
}

interface Doctor {
  id: string;
  name: string;
  department: string;
  specialization: string;
  available: boolean;
}

interface TimeSlot {
  id: string;
  time: string;
  available: boolean;
  quota: number;
  quotaMax: number;
}

interface BookingFormData {
  department: string;
  doctor: string;
  date: string;
  timeSlot: string;
  patientName: string;
  patientPhone: string;
  bpjsNumber: string;
  reminder: boolean;
}

// ============================================================================
// MOCK DATA
// ============================================================================

const DEPARTMENTS: Department[] = [
  { id: "ana", name: "Poli Anak", icon: "👶" },
  { id: "int", name: "Poli Penyakit Dalam", icon: "🏥" },
  { id: "bed", name: "Poli Bedah", icon: "🔪" },
  { id: "obg", name: "Poli Kandungan", icon: "🤱" },
  { id: "mat", name: "Poli Mata", icon: "👁️" },
  { id: "kul", name: "Poli Kulit & Kelamin", icon: "🧴" },
];

const DOCTORS: Doctor[] = [
  {
    id: "dr-ahmad",
    name: "dr. Ahmad Sp.A",
    department: "ana",
    specialization: "Anak",
    available: true,
  },
  {
    id: "dr-siti",
    name: "dr. Siti Sp.A",
    department: "ana",
    specialization: "Anak",
    available: true,
  },
  {
    id: "dr-budi",
    name: "dr. Budi Sp.PD",
    department: "int",
    specialization: "Penyakit Dalam",
    available: true,
  },
  {
    id: "dr-rina",
    name: "dr. Rina Sp.PD",
    department: "int",
    specialization: "Penyakit Dalam",
    available: true,
  },
  {
    id: "dr-dedi",
    name: "dr. Dedi Sp.B",
    department: "bed",
    specialization: "Bedah Umum",
    available: false,
  },
  {
    id: "dr-lilis",
    name: "dr. Lilis Sp.OG",
    department: "obg",
    specialization: "Kandungan",
    available: true,
  },
  {
    id: "dr-agus",
    name: "dr. Agus Sp.M",
    department: "mat",
    specialization: "Mata",
    available: true,
  },
  {
    id: "dr-yuli",
    name: "dr. Yuli Sp.KK",
    department: "kul",
    specialization: "Kulit & Kelamin",
    available: true,
  },
];

// Generate time slots for a department
const generateTimeSlots = (departmentId: string): TimeSlot[] => {
  const slots = [
    { id: "08:00", time: "08:00", available: true, quota: 5, quotaMax: 5 },
    { id: "08:30", time: "08:30", available: true, quota: 3, quotaMax: 5 },
    { id: "09:00", time: "09:00", available: true, quota: 2, quotaMax: 5 },
    { id: "09:30", time: "09:30", available: true, quota: 5, quotaMax: 5 },
    { id: "10:00", time: "10:00", available: true, quota: 4, quotaMax: 5 },
    { id: "10:30", time: "10:30", available: false, quota: 0, quotaMax: 5 },
    { id: "11:00", time: "11:00", available: true, quota: 5, quotaMax: 5 },
    { id: "11:30", time: "11:30", available: true, quota: 5, quotaMax: 5 },
    { id: "13:00", time: "13:00", available: true, quota: 5, quotaMax: 5 },
    { id: "13:30", time: "13:30", available: true, quota: 3, quotaMax: 5 },
    { id: "14:00", time: "14:00", available: true, quota: 5, quotaMax: 5 },
    { id: "14:30", time: "14:30", available: true, quota: 5, quotaMax: 5 },
    { id: "15:00", time: "15:00", available: true, quota: 5, quotaMax: 5 },
    { id: "15:30", time: "15:30", available: true, quota: 5, quotaMax: 5 },
    { id: "16:00", time: "16:00", available: true, quota: 5, quotaMax: 5 },
  ];

  return slots;
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function AppointmentBookingPage() {
  // Form state
  const [formData, setFormData] = useState<BookingFormData>({
    department: "",
    doctor: "",
    date: "",
    timeSlot: "",
    patientName: "",
    patientPhone: "",
    bpjsNumber: "",
    reminder: false,
  });

  // UI state
  const [step, setStep] = useState(1); // 1: Service, 2: Details, 3: Confirm, 4: Success
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [bookingResult, setBookingResult] = useState<{
    bookingNumber: string;
    queueNumber: string;
    estimatedWait: string;
  } | null>(null);

  // Computed values
  const selectedDepartment = DEPARTMENTS.find((d) => d.id === formData.department);
  const selectedDoctor = DOCTORS.find((d) => d.id === formData.doctor);
  const availableTimeSlots = useMemo(() => {
    if (!formData.department) return [];
    return generateTimeSlots(formData.department);
  }, [formData.department]);

  const selectedTimeSlot = availableTimeSlots.find((s) => s.id === formData.timeSlot);

  /**
   * Handle department change
   */
  const handleDepartmentChange = (departmentId: string) => {
    setFormData({
      ...formData,
      department: departmentId,
      doctor: "", // Reset doctor when department changes
      timeSlot: "", // Reset time slot
    });
    setErrors({ ...errors, department: "", doctor: "" });
  };

  /**
   * Handle date change
   */
  const handleDateChange = (date: string) => {
    setFormData({
      ...formData,
      date,
      timeSlot: "", // Reset time slot when date changes
    });
    setErrors({ ...errors, date: "", timeSlot: "" });
  };

  /**
   * Validate step 1 (service selection)
   */
  const validateStep1 = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.department) {
      newErrors.department = "Silakan pilih poli tujuan";
    }
    if (!formData.doctor) {
      newErrors.doctor = "Silakan pilih dokter";
    }
    if (!formData.date) {
      newErrors.date = "Silakan pilih tanggal kunjungan";
    }
    if (!formData.timeSlot) {
      newErrors.timeSlot = "Silakan pilih jam kunjungan";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Validate step 2 (patient details)
   */
  const validateStep2 = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.patientName.trim()) {
      newErrors.patientName = "Nama pasien wajib diisi";
    }
    if (!formData.patientPhone.trim()) {
      newErrors.patientPhone = "Nomor telepon wajib diisi";
    } else if (!/^08\d{8,11}$/.test(formData.patientPhone)) {
      newErrors.patientPhone = "Format nomor telepon tidak valid (contoh: 081234567890)";
    }
    if (formData.bpjsNumber && !/^\d{13}$/.test(formData.bpjsNumber)) {
      newErrors.bpjsNumber = "Nomor BPJS harus 13 digit";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle continue to step 2
   */
  const handleContinueStep2 = () => {
    if (validateStep1()) {
      setStep(2);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  /**
   * Handle back to step 1
   */
  const handleBackStep1 = () => {
    setStep(1);
  };

  /**
   * Handle submit booking
   */
  const handleSubmitBooking = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateStep2()) return;

    setIsSubmitting(true);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Generate booking number and queue number
    const today = new Date();
    const dateStr = today.toISOString().split("T")[0].replace(/-/g, "");
    const randomId = Math.floor(Math.random() * 1000).toString().padStart(3, "0");
    const bookingNumber = `BK-${dateStr}-${randomId}`;

    const deptCode = formData.department.toUpperCase();
    const queueNum = Math.floor(Math.random() * 50) + 1;
    const queueNumber = `${deptCode}-${queueNum.toString().padStart(3, "0")}`;

    setBookingResult({
      bookingNumber,
      queueNumber,
      estimatedWait: "15-30 menit",
    });

    setIsSubmitting(false);
    setStep(4); // Success
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  /**
   * Handle new booking
   */
  const handleNewBooking = () => {
    setFormData({
      department: "",
      doctor: "",
      date: "",
      timeSlot: "",
      patientName: "",
      patientPhone: "",
      bpjsNumber: "",
      reminder: false,
    });
    setErrors({});
    setBookingResult(null);
    setStep(1);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  /**
   * Get minimum date (today)
   */
  const getMinDate = () => {
    const today = new Date();
    return today.toISOString().split("T")[0];
  };

  /**
   * Get maximum date (30 days from now)
   */
  const getMaxDate = () => {
    const date = new Date();
    date.setDate(date.getDate() + 30);
    return date.toISOString().split("T")[0];
  };

  /**
   * Format date for display
   */
  const formatDateDisplay = (dateString: string) => {
    const date = new Date(dateString);
    const options: Intl.DateTimeFormatOptions = {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    };
    return date.toLocaleDateString("id-ID", options);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-3xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Booking Janji Temu Online</h1>
              <p className="text-sm text-gray-600">Jadwalkan kunjungan tanpa antri</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-8">
        {/* Progress Steps */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${
                step >= 1 ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-600"
              }`}>
                1
              </div>
              <div className="flex-1">
                <p className={`text-sm font-medium ${step >= 1 ? "text-blue-600" : "text-gray-500"}`}>
                  Pilih Jadwal
                </p>
              </div>
            </div>

            <div className="w-12 h-0.5 bg-gray-200 mx-2"></div>

            <div className="flex items-center gap-3 flex-1">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${
                step >= 2 ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-600"
              }`}>
                2
              </div>
              <div className="flex-1">
                <p className={`text-sm font-medium ${step >= 2 ? "text-blue-600" : "text-gray-500"}`}>
                  Data Pasien
                </p>
              </div>
            </div>

            <div className="w-12 h-0.5 bg-gray-200 mx-2"></div>

            <div className="flex items-center gap-3 flex-1">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${
                step >= 3 ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-600"
              }`}>
                3
              </div>
              <div className="flex-1">
                <p className={`text-sm font-medium ${step >= 3 ? "text-blue-600" : "text-gray-500"}`}>
                  Konfirmasi
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* STEP 1: Service Selection */}
        {step === 1 && (
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Pilih Jadwal Kunjungan</h2>

            <div className="space-y-6">
              {/* Department Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Poli Tujuan <span className="text-red-500">*</span>
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {DEPARTMENTS.map((dept) => (
                    <button
                      key={dept.id}
                      type="button"
                      onClick={() => handleDepartmentChange(dept.id)}
                      className={`p-4 rounded-lg border-2 text-left transition-all ${
                        formData.department === dept.id
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-2xl">{dept.icon}</span>
                        <span className="font-medium text-gray-900">{dept.name}</span>
                      </div>
                    </button>
                  ))}
                </div>
                {errors.department && (
                  <p className="text-red-600 text-sm mt-2">{errors.department}</p>
                )}
              </div>

              {/* Doctor Selection */}
              {formData.department && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Dokter <span className="text-red-500">*</span>
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {DOCTORS
                      .filter((d) => d.department === formData.department)
                      .map((doctor) => (
                        <button
                          key={doctor.id}
                          type="button"
                          onClick={() => setFormData({ ...formData, doctor: doctor.id })}
                          disabled={!doctor.available}
                          className={`p-4 rounded-lg border-2 text-left transition-all ${
                            formData.doctor === doctor.id
                              ? "border-blue-500 bg-blue-50"
                              : "border-gray-200 hover:border-gray-300"
                          } ${!doctor.available ? "opacity-50 cursor-not-allowed" : ""}`}
                        >
                          <div>
                            <p className="font-medium text-gray-900">{doctor.name}</p>
                            <p className="text-sm text-gray-600">{doctor.specialization}</p>
                            {!doctor.available && (
                              <Badge variant="neutral" className="mt-2 text-xs">Tidak Tersedia</Badge>
                            )}
                          </div>
                        </button>
                      ))}
                  </div>
                  {errors.doctor && (
                    <p className="text-red-600 text-sm mt-2">{errors.doctor}</p>
                  )}
                </div>
              )}

              {/* Date Selection */}
              {formData.doctor && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Tanggal Kunjungan <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    value={formData.date}
                    onChange={(e) => handleDateChange(e.target.value)}
                    min={getMinDate()}
                    max={getMaxDate()}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  {errors.date && (
                    <p className="text-red-600 text-sm mt-2">{errors.date}</p>
                  )}
                </div>
              )}

              {/* Time Slot Selection */}
              {formData.date && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Jam Kunjungan <span className="text-red-500">*</span>
                  </label>
                  <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
                    {availableTimeSlots.map((slot) => (
                      <button
                        key={slot.id}
                        type="button"
                        onClick={() => setFormData({ ...formData, timeSlot: slot.id })}
                        disabled={!slot.available}
                        className={`p-3 rounded-lg border-2 text-center transition-all ${
                          formData.timeSlot === slot.id
                            ? "border-blue-500 bg-blue-600 text-white"
                            : slot.available
                            ? "border-gray-200 hover:border-blue-300 hover:bg-blue-50"
                            : "border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed"
                        }`}
                      >
                        <div className="text-lg font-bold">{slot.time}</div>
                        <div className="text-xs">
                          {slot.available ? `${slot.quota}/${slot.quotaMax}` : "Penuh"}
                        </div>
                      </button>
                    ))}
                  </div>
                  {errors.timeSlot && (
                    <p className="text-red-600 text-sm mt-2">{errors.timeSlot}</p>
                  )}
                </div>
              )}

              {/* Continue Button */}
              {formData.timeSlot && (
                <div className="pt-4 border-t border-gray-200">
                  <button
                    type="button"
                    onClick={handleContinueStep2}
                    className="w-full px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium flex items-center justify-center gap-2"
                  >
                    Lanjut
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* STEP 2: Patient Details */}
        {step === 2 && (
          <form onSubmit={handleSubmitBooking} className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Data Pasien</h2>

            {/* Booking Summary */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h3 className="text-sm font-semibold text-blue-900 mb-3">Ringkasan Booking</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-blue-700">Poli:</span>
                  <span className="font-medium text-blue-900">{selectedDepartment?.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">Dokter:</span>
                  <span className="font-medium text-blue-900">{selectedDoctor?.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">Tanggal:</span>
                  <span className="font-medium text-blue-900">
                    {formData.date && formatDateDisplay(formData.date)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">Jam:</span>
                  <span className="font-medium text-blue-900">{selectedTimeSlot?.time}</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {/* Patient Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nama Lengkap <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={formData.patientName}
                    onChange={(e) => setFormData({ ...formData, patientName: e.target.value })}
                    placeholder="Masukkan nama lengkap pasien"
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                {errors.patientName && (
                  <p className="text-red-600 text-sm mt-1">{errors.patientName}</p>
                )}
              </div>

              {/* Phone Number */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nomor Telepon <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <input
                    type="tel"
                    value={formData.patientPhone}
                    onChange={(e) => setFormData({ ...formData, patientPhone: e.target.value })}
                    placeholder="081234567890"
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                {errors.patientPhone && (
                  <p className="text-red-600 text-sm mt-1">{errors.patientPhone}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">Format: 08xxxxxxxxx</p>
              </div>

              {/* BPJS Number (Optional) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  No. BPJS <span className="text-gray-500">(opsional)</span>
                </label>
                <div className="relative">
                  <CreditCard className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={formData.bpjsNumber}
                    onChange={(e) => setFormData({ ...formData, bpjsNumber: e.target.value })}
                    placeholder="13 digit nomor BPJS"
                    maxLength={13}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                {errors.bpjsNumber && (
                  <p className="text-red-600 text-sm mt-1">{errors.bpjsNumber}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">Jika pasien peserta BPJS</p>
              </div>

              {/* Reminder Checkbox */}
              <div className="flex items-start gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <Bell className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.reminder}
                      onChange={(e) => setFormData({ ...formData, reminder: e.target.checked })}
                      className="mt-1"
                    />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        Ingatkan saya jadwal kunjungan ini
                      </p>
                      <p className="text-xs text-gray-600 mt-1">
                        Kami akan mengirim pengingat melalui WhatsApp/SMS 1 hari sebelum jadwal
                      </p>
                    </div>
                  </label>
                </div>
              </div>

              {/* Info Message */}
              <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div className="flex-1 text-sm text-blue-900">
                  <p className="font-medium mb-1">Informasi Penting:</p>
                  <ul className="space-y-1 text-xs">
                    <li>• Harap datang 15 menit sebelum jadwal kunjungan</li>
                    <li>• Bawa kartu identitas dan kartu BPJS (jika ada)</li>
                    <li>• Bila tidak dapat datang, harap hubungi kami untuk membatalkan</li>
                  </ul>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={handleBackStep1}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
                >
                  Kembali
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center justify-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Memproses...
                    </>
                  ) : (
                    <>
                      Lanjut ke Konfirmasi
                      <ChevronRight className="w-5 h-5" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        )}

        {/* STEP 3: Confirmation */}
        {step === 3 && (
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Konfirmasi Booking</h2>

            <div className="space-y-6">
              {/* Booking Details */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-sm font-semibold text-blue-900 mb-4">Detail Kunjungan</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-blue-700">Poli:</span>
                    <p className="font-medium text-blue-900 mt-1">{selectedDepartment?.name}</p>
                  </div>
                  <div>
                    <span className="text-blue-700">Dokter:</span>
                    <p className="font-medium text-blue-900 mt-1">{selectedDoctor?.name}</p>
                  </div>
                  <div>
                    <span className="text-blue-700">Tanggal:</span>
                    <p className="font-medium text-blue-900 mt-1">
                      {formData.date && formatDateDisplay(formData.date)}
                    </p>
                  </div>
                  <div>
                    <span className="text-blue-700">Jam:</span>
                    <p className="font-medium text-blue-900 mt-1">{selectedTimeSlot?.time} WIB</p>
                  </div>
                </div>
              </div>

              {/* Patient Details */}
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Data Pasien</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-600">Nama:</span>
                    <p className="font-medium text-gray-900 mt-1">{formData.patientName}</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Telepon:</span>
                    <p className="font-medium text-gray-900 mt-1">{formData.patientPhone}</p>
                  </div>
                  {formData.bpjsNumber && (
                    <div>
                      <span className="text-gray-600">No. BPJS:</span>
                      <p className="font-medium text-gray-900 mt-1">{formData.bpjsNumber}</p>
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <Bell className="w-4 h-4 text-yellow-600" />
                    <span className="text-gray-600">
                      {formData.reminder ? "Akan diingatkan" : "Tidak ada pengingatan"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Warning */}
              <div className="flex items-start gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <Info className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                <div className="flex-1 text-sm text-yellow-900">
                  <p className="font-medium mb-1">Pastikan data sudah benar</p>
                  <p className="text-xs">
                    Setelah dikonfirmasi, booking tidak dapat dibatalkan. Silakan periksa kembali jadwal
                    dan data diri Anda sebelum melanjutkan.
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleBackStep1}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
                >
                  Ubah Jadwal
                </button>
                <button
                  type="button"
                  onClick={handleSubmitBooking}
                  disabled={isSubmitting}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  Konfirmasi Booking
                </button>
              </div>
            </div>
          </div>
        )}

        {/* STEP 4: Success */}
        {step === 4 && bookingResult && (
          <div className="bg-white rounded-xl shadow-2xl overflow-hidden">
            {/* Success Header */}
            <div className="bg-gradient-to-r from-green-500 to-green-600 p-8 text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-white rounded-full mb-4">
                <CheckCircle className="w-12 h-12 text-green-600" />
              </div>
              <h1 className="text-2xl font-bold text-white">Booking Berhasil!</h1>
              <p className="text-green-100 mt-2">Janji temu Anda telah terkonfirmasi</p>
            </div>

            {/* Booking Details */}
            <div className="p-8">
              {/* Queue Number */}
              <div className="text-center mb-6">
                <p className="text-sm text-gray-600 mb-2">Nomor Antrian</p>
                <p className="text-5xl font-bold text-green-600">{bookingResult.queueNumber}</p>
              </div>

              <div className="space-y-4 mb-6">
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">No. Booking</span>
                  <span className="font-semibold text-gray-900">{bookingResult.bookingNumber}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">Nama Pasien</span>
                  <span className="font-semibold text-gray-900">{formData.patientName}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">Poli</span>
                  <span className="font-semibold text-gray-900">{selectedDepartment?.name}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">Dokter</span>
                  <span className="font-semibold text-gray-900">{selectedDoctor?.name}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">Tanggal</span>
                  <span className="font-semibold text-gray-900">
                    {formData.date && formatDateDisplay(formData.date)}
                  </span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">Jam</span>
                  <span className="font-semibold text-gray-900">{selectedTimeSlot?.time} WIB</span>
                </div>
                <div className="flex justify-between items-center py-3">
                  <span className="text-gray-600">Telepon</span>
                  <span className="font-semibold text-gray-900">{formData.patientPhone}</span>
                </div>
              </div>

              {/* Info Box */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <div className="flex items-start gap-3">
                  <Clock className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-blue-900">Informasi:</p>
                    <p className="text-xs text-blue-800 mt-1">
                      Estimasi tunggu: <span className="font-semibold">{bookingResult.estimatedWait}</span>
                    </p>
                    <p className="text-xs text-blue-800 mt-1">
                      Harap datang 15 menit sebelum jadwal kunjungan
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleNewBooking}
                  className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                >
                  Booking Baru
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-sm p-4 text-center">
          <p className="text-sm text-gray-600">
            Butuh bantuan? Hubungi kami di{" "}
            <a href="tel:1400" className="text-blue-600 hover:text-blue-700 font-medium">
              1400
            </a>{" "}
            atau{" "}
            <a href="mailto:info@rsudsehatselalu.co.id" className="text-blue-600 hover:text-blue-700 font-medium">
              info@rsudsehatselalu.co.id
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
