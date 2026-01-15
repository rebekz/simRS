"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle, User, Phone, MapPin, Calendar, Camera, Upload, ArrowRight, AlertCircle } from "lucide-react";
import { BPJSEligibilityCheck } from "@/components/bpjs/BPJSEligibilityCheck";
import { BPJSData } from "@/types";
import { BPJSErrorDisplay } from "@/components/bpjs/BPJSErrorDisplay";
import { Badge } from "@/components/ui/Badge";

/**
 * WEB-S-3.1: BPJS-First New Patient Registration
 *
 * Key Features:
 * - BPJS card verification is PRIMARY and prominent
 * - Auto-fill patient data from BPJS
 * - <5 clicks for BPJS patients
 * - Manual registration as secondary option
 * - Queue number generation after registration
 *
 * Click Count for BPJS Flow:
 * 1. Click "Verifikasi" button
 * 2. Click "Auto-Fill Data Pasien" (if BPJS active)
 * 3. Enter emergency contact (no click - just typing)
 * 4. Select department (1 click)
 * 5. Click "Daftar" (submit)
 * Total: 4 clicks (≤5 target met)
 */

interface FormErrors {
  fullName?: string;
  nik?: string;
  dateOfBirth?: string;
  phoneNumber?: string;
  emergencyName?: string;
  emergencyPhone?: string;
  department?: string;
}

interface QueueTicket {
  queueNumber: string;
  rmNumber: string;
  department: string;
  estimatedWait: string;
}

export default function BPJSFirstRegistrationPage() {
  const router = useRouter();

  // BPJS verification state
  const [bpjsData, setBpjsData] = useState<BPJSData | null>(null);
  const [bpjsError, setBpjsError] = useState<string | null>(null);

  // Registration mode
  const [registrationMode, setRegistrationMode] = useState<"bpjs" | "manual">("bpjs");

  // Patient data (auto-filled from BPJS or manual)
  const [fullName, setFullName] = useState("");
  const [nik, setNik] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [placeOfBirth, setPlaceOfBirth] = useState("");
  const [gender, setGender] = useState<"male" | "female" | "">("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [address, setAddress] = useState("");
  const [bpjsNumber, setBpjsNumber] = useState("");

  // Emergency contact (always required)
  const [emergencyName, setEmergencyName] = useState("");
  const [emergencyRelationship, setEmergencyRelationship] = useState("");
  const [emergencyPhone, setEmergencyPhone] = useState("");

  // Additional info (optional)
  const [photo, setPhoto] = useState<string | null>(null);
  const [insuranceType, setInsuranceType] = useState<"bpjs" | "asuransi" | "umum">("bpjs");
  const [department, setDepartment] = useState("");

  // UI state
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const [queueTicket, setQueueTicket] = useState<QueueTicket | null>(null);

  // Department options
  const departments = [
    { value: "igd", label: "IGD (Instalasi Gawat Darurat)" },
    { value: "int", label: "Poli Penyakit Dalam" },
    { value: "ana", label: "Poli Anak" },
    { value: "bed", label: "Poli Bedah" },
    { value: "obg", label: "Poli Kandungan" },
    { value: "mat", label: "Poli Mata" },
    { value: "kul", label: "Peli Kulit & Kelamin" },
    { value: "par", label: "Poli Paru" },
    { value: "sar", label: "Poli Saraf" },
    { value: "jant", label: "Poli Jantung" },
    { value: "tht", label: "Poli THT" },
    { value: "gig", label: "Poli Gigi" },
  ];

  /**
   * Handle BPJS verification success
   * Auto-fills patient data from BPJS response
   */
  const handleBPJSVerified = useCallback((data: BPJSData) => {
    setBpjsData(data);
    setBpjsError(null);
    setBpjsNumber(data.cardNumber);
    setFullName(data.nama);
    setNik(data.nik);

    // Auto-fill gender from NIK (2nd last digit: even = female, odd = male)
    if (data.nik.length >= 16) {
      const genderDigit = parseInt(data.nik[8]);
      setGender(genderDigit % 2 === 0 ? "female" : "male");
    }

    // Estimate DOB from BPJS data (simplified - in production, BPJS provides DOB)
    // For now, we'll leave it empty or use a placeholder
    // setEstimatedDateOfBirth(data.nik);

    // Clear any previous errors
    setErrors({});

    // Auto-switch to BPJS mode
    setRegistrationMode("bpjs");
    setInsuranceType("bpjs");

    console.log("BPJS Verified:", data);
  }, []);

  /**
   * Handle BPJS verification error
   */
  const handleBPJSError = useCallback((error: string) => {
    setBpjsError(error);
    setBpjsData(null);
  }, []);

  /**
   * Auto-fill patient data from BPJS (user clicked the button)
   */
  const handleAutoFill = useCallback(() => {
    if (bpjsData) {
      handleBPJSVerified(bpjsData);
    }
  }, [bpjsData, handleBPJSVerified]);

  /**
   * Validate form before submission
   */
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!fullName.trim()) {
      newErrors.fullName = "Nama lengkap wajib diisi";
    }

    if (!nik.trim()) {
      newErrors.nik = "NIK wajib diisi";
    } else if (!/^\d{16}$/.test(nik)) {
      newErrors.nik = "NIK harus 16 digit angka";
    }

    if (!dateOfBirth) {
      newErrors.dateOfBirth = "Tanggal lahir wajib diisi";
    }

    if (!phoneNumber.trim()) {
      newErrors.phoneNumber = "Nomor telepon wajib diisi";
    } else if (!/^\d{10,15}$/.test(phoneNumber.replace(/\D/g, ""))) {
      newErrors.phoneNumber = "Nomor telepon tidak valid (10-15 digit)";
    }

    if (!emergencyName.trim()) {
      newErrors.emergencyName = "Nama kontak darurat wajib diisi";
    }

    if (!emergencyPhone.trim()) {
      newErrors.emergencyPhone = "Telepon kontak darurat wajib diisi";
    }

    if (!department) {
      newErrors.department = "Pilih poli tujuan";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Generate mock RM number and queue number
      const rmNumber = `RM${new Date().getFullYear()}${String(Math.floor(Math.random() * 10000)).padStart(4, "0")}`;
      const queueNumber = `${department.toUpperCase()}-${String(Math.floor(Math.random() * 100) + 1).padStart(3, "0")}`;

      setQueueTicket({
        queueNumber,
        rmNumber,
        department: departments.find((d) => d.value === department)?.label || department,
        estimatedWait: "15-30 menit",
      });

      setRegistrationSuccess(true);
    } catch (err) {
      console.error("Registration error:", err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reset form for new registration
   */
  const handleNewRegistration = () => {
    setBpjsData(null);
    setBpjsError(null);
    setRegistrationMode("bpjs");
    setFullName("");
    setNik("");
    setDateOfBirth("");
    setPlaceOfBirth("");
    setGender("");
    setPhoneNumber("");
    setAddress("");
    setBpjsNumber("");
    setEmergencyName("");
    setEmergencyRelationship("");
    setEmergencyPhone("");
    setPhoto(null);
    setInsuranceType("bpjs");
    setDepartment("");
    setErrors({});
    setRegistrationSuccess(false);
    setQueueTicket(null);
  };

  /**
   * Render success ticket
   */
  if (registrationSuccess && queueTicket) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-teal-50 via-blue-50 to-white flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl overflow-hidden">
          {/* Success Header */}
          <div className="bg-gradient-to-r from-teal-500 to-teal-600 p-8 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-white rounded-full mb-4">
              <CheckCircle className="w-12 h-12 text-teal-600" />
            </div>
            <h1 className="text-2xl font-bold text-white">Pendaftaran Berhasil!</h1>
            <p className="text-teal-100 mt-2">Pasien telah terdaftar di sistem</p>
          </div>

          {/* Queue Ticket */}
          <div className="p-8">
            <div className="text-center mb-6">
              <p className="text-sm text-gray-600 mb-2">Nomor Antrian</p>
              <p className="text-5xl font-bold text-teal-600">{queueTicket.queueNumber}</p>
            </div>

            <div className="space-y-4 mb-6">
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <span className="text-gray-600">No. Rekam Medis</span>
                <span className="font-semibold text-gray-900">{queueTicket.rmNumber}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <span className="text-gray-600">Nama Pasien</span>
                <span className="font-semibold text-gray-900">{fullName}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <span className="text-gray-600">Poli Tujuan</span>
                <span className="font-semibold text-gray-900">{queueTicket.department}</span>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-gray-600">Estimasi Tunggu</span>
                <span className="font-semibold text-teal-600">{queueTicket.estimatedWait}</span>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-blue-900">Informasi Penting</p>
                  <p className="text-xs text-blue-800 mt-1">
                    Silakan menunggu di ruang tunggu. Nomor antrian akan dipanggil melalui pengeras suara dan layar display.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={handleNewRegistration}
                className="flex-1 px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 font-medium transition-colors"
              >
                Daftar Pasien Baru
              </button>
              <button
                type="button"
                onClick={() => router.push("/patients")}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
              >
                Daftar Pasien
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-blue-50 to-white py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-teal-600 rounded-2xl mb-4">
            <User className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Pendaftaran Pasien Baru</h1>
          <p className="text-gray-600 mt-2">Daftar pasien baru dengan cepat dan mudah</p>
        </div>

        {/* Registration Mode Toggle */}
        {!bpjsData && (
          <div className="bg-white rounded-xl shadow-md p-6 mb-6">
            <div className="flex items-center justify-center gap-4">
              <button
                type="button"
                onClick={() => setRegistrationMode("bpjs")}
                className={`flex-1 max-w-xs px-6 py-4 rounded-lg font-medium transition-all ${
                  registrationMode === "bpjs"
                    ? "bg-teal-600 text-white shadow-lg shadow-teal-200"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                <div className="text-center">
                  <div className="text-lg font-semibold">Dengan BPJS</div>
                  <div className="text-xs mt-1 opacity-80">Auto-fill data (≤5 klik)</div>
                </div>
              </button>

              <div className="text-gray-400 font-semibold">ATAU</div>

              <button
                type="button"
                onClick={() => setRegistrationMode("manual")}
                className={`flex-1 max-w-xs px-6 py-4 rounded-lg font-medium transition-all ${
                  registrationMode === "manual"
                    ? "bg-gray-700 text-white shadow-lg"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                <div className="text-center">
                  <div className="text-lg font-semibold">Manual</div>
                  <div className="text-xs mt-1 opacity-80">Isi form lengkap</div>
                </div>
              </button>
            </div>
          </div>
        )}

        {/* BPJS Verification (Primary Mode) */}
        {registrationMode === "bpjs" && !bpjsData && (
          <div className="mb-6">
            <BPJSEligibilityCheck
              onVerified={handleBPJSVerified}
              onError={handleBPJSError}
              showAutoFillButton={true}
            />
            {bpjsError && (
              <div className="mt-4">
                <BPJSErrorDisplay
                  error={{
                    code: "BPJS_ERROR",
                    type: "validation" as const,
                    title: "Verifikasi BPJS Gagal",
                    message: bpjsError,
                    suggestion: "Pastikan nomor kartu BPJS benar atau coba daftar manual",
                    retryable: true,
                    userAction: "Coba lagi atau daftar manual",
                  }}
                  onRetry={async () => setBpjsError(null)}
                  onDismiss={() => setBpjsError(null)}
                />
              </div>
            )}
          </div>
        )}

        {/* Registration Form */}
        {(bpjsData || registrationMode === "manual") && (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Patient Information Card */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="bg-gradient-to-r from-teal-500 to-teal-600 px-6 py-4">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Informasi Pasien
                </h2>
                {bpjsData && (
                  <div className="mt-2">
                    <Badge variant="success" className="bg-white text-teal-700">
                      Data dari BPJS: {bpjsData.nama}
                    </Badge>
                  </div>
                )}
              </div>

              <div className="p-6 space-y-4">
                {/* Full Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nama Lengkap <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    disabled={!!bpjsData}
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 ${
                      errors.fullName ? "border-red-500" : "border-gray-300"
                    } ${bpjsData ? "bg-gray-100" : "bg-white"}`}
                    placeholder="Nama lengkap sesuai KTP"
                  />
                  {errors.fullName && <p className="text-red-600 text-sm mt-1">{errors.fullName}</p>}
                </div>

                {/* NIK and BPJS Number */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      NIK <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={nik}
                      onChange={(e) => setNik(e.target.value.replace(/\D/g, ""))}
                      disabled={!!bpjsData}
                      maxLength={16}
                      className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 ${
                        errors.nik ? "border-red-500" : "border-gray-300"
                      } ${bpjsData ? "bg-gray-100" : "bg-white"}`}
                      placeholder="16 digit NIK"
                    />
                    {errors.nik && <p className="text-red-600 text-sm mt-1">{errors.nik}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      No. BPJS
                    </label>
                    <input
                      type="text"
                      value={bpjsNumber}
                      onChange={(e) => setBpjsNumber(e.target.value.replace(/\D/g, ""))}
                      disabled={!!bpjsData}
                      maxLength={13}
                      className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 border-gray-300 ${bpjsData ? "bg-gray-100" : "bg-white"}`}
                      placeholder="13 digit (opsional)"
                    />
                  </div>
                </div>

                {/* Date and Place of Birth */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tanggal Lahir <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      value={dateOfBirth}
                      onChange={(e) => setDateOfBirth(e.target.value)}
                      max={new Date().toISOString().split("T")[0]}
                      className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 ${
                        errors.dateOfBirth ? "border-red-500" : "border-gray-300"
                      } bg-white`}
                    />
                    {errors.dateOfBirth && <p className="text-red-600 text-sm mt-1">{errors.dateOfBirth}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tempat Lahir
                    </label>
                    <input
                      type="text"
                      value={placeOfBirth}
                      onChange={(e) => setPlaceOfBirth(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
                      placeholder="Kota kelahiran"
                    />
                  </div>
                </div>

                {/* Gender and Phone */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Jenis Kelamin <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={gender}
                      onChange={(e) => setGender(e.target.value as "male" | "female" | "")}
                      disabled={!!bpjsData}
                      className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 border-gray-300 ${bpjsData ? "bg-gray-100" : "bg-white"}`}
                    >
                      <option value="">Pilih jenis kelamin</option>
                      <option value="male">Laki-laki</option>
                      <option value="female">Perempuan</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      No. Telepon <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="tel"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, ""))}
                      className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 ${
                        errors.phoneNumber ? "border-red-500" : "border-gray-300"
                      } bg-white`}
                      placeholder="08xxxxxxxxxx"
                    />
                    {errors.phoneNumber && <p className="text-red-600 text-sm mt-1">{errors.phoneNumber}</p>}
                  </div>
                </div>

                {/* Address */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Alamat Lengkap
                  </label>
                  <textarea
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    rows={2}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
                    placeholder="Alamat lengkap pasien"
                  />
                </div>

                {/* Photo Upload (Optional) */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                  <div className="text-center">
                    {photo ? (
                      <div className="space-y-4">
                        <img
                          src={photo}
                          alt="Patient photo"
                          className="w-32 h-32 object-cover rounded-lg mx-auto"
                        />
                        <button
                          type="button"
                          onClick={() => setPhoto(null)}
                          className="text-red-600 text-sm hover:underline"
                        >
                          Hapus Foto
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div className="flex justify-center gap-4">
                          <button
                            type="button"
                            onClick={() => {/* TODO: Camera capture */}}
                            className="flex flex-col items-center gap-2 px-4 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                          >
                            <Camera className="w-6 h-6 text-gray-600" />
                            <span className="text-sm text-gray-700">Kamera</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => {/* TODO: File upload */}}
                            className="flex flex-col items-center gap-2 px-4 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                          >
                            <Upload className="w-6 h-6 text-gray-600" />
                            <span className="text-sm text-gray-700">Upload</span>
                          </button>
                        </div>
                        <p className="text-xs text-gray-500">Foto pasien (opsional)</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Emergency Contact Card */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="bg-gradient-to-r from-red-500 to-red-600 px-6 py-4">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                  <Phone className="w-5 h-5" />
                  Kontak Darurat <span className="text-red-200 text-sm font-normal">(Wajib)</span>
                </h2>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nama Kontak Darurat <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={emergencyName}
                    onChange={(e) => setEmergencyName(e.target.value)}
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 ${
                      errors.emergencyName ? "border-red-500" : "border-gray-300"
                    } bg-white`}
                    placeholder="Nama kontak darurat"
                  />
                  {errors.emergencyName && <p className="text-red-600 text-sm mt-1">{errors.emergencyName}</p>}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Hubungan
                    </label>
                    <input
                      type="text"
                      value={emergencyRelationship}
                      onChange={(e) => setEmergencyRelationship(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
                      placeholder="Suami/Istri/Orang Tua/Saudara"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Telepon <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="tel"
                      value={emergencyPhone}
                      onChange={(e) => setEmergencyPhone(e.target.value.replace(/\D/g, ""))}
                      className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 ${
                        errors.emergencyPhone ? "border-red-500" : "border-gray-300"
                      } bg-white`}
                      placeholder="08xxxxxxxxxx"
                    />
                    {errors.emergencyPhone && <p className="text-red-600 text-sm mt-1">{errors.emergencyPhone}</p>}
                  </div>
                </div>
              </div>
            </div>

            {/* Department Selection Card */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Poli Tujuan <span className="text-blue-200 text-sm font-normal">(Pilih Satu)</span>
                </h2>
              </div>

              <div className="p-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Pilih Poli <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 ${
                      errors.department ? "border-red-500" : "border-gray-300"
                    } bg-white`}
                  >
                    <option value="">-- Pilih Poli Tujuan --</option>
                    {departments.map((dept) => (
                      <option key={dept.value} value={dept.value}>
                        {dept.label}
                      </option>
                    ))}
                  </select>
                  {errors.department && <p className="text-red-600 text-sm mt-1">{errors.department}</p>}
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => {
                  setBpjsData(null);
                  setRegistrationMode("bpjs");
                }}
                className="px-6 py-4 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
              >
                Kembali
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-6 py-4 bg-gradient-to-r from-teal-600 to-teal-700 text-white rounded-lg hover:from-teal-700 hover:to-teal-800 font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Memproses...
                  </>
                ) : (
                  <>
                    Daftar Pasien Baru
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
