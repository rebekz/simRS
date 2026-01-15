"use client";

import { useState, useEffect, useCallback, useMemo, useRef } from "react";
import { useRouter } from "next/navigation";
import { Search, Clock, User, Calendar, Phone, CreditCard, CheckCircle, Loader2, X, ArrowRight } from "lucide-react";
import { BPJSEligibilityCheck } from "@/components/bpjs/BPJSEligibilityCheck";
import { BPJSData, BPJSStatus } from "@/types";
import { Badge } from "@/components/ui/Badge";

/**
 * WEB-S-3.2: Returning Patient Quick Check-In
 *
 * Key Features:
 * - Patient search by RM, BPJS, NIK, name, phone
 * - Keyboard shortcut (Ctrl+K / Cmd+K)
 * - <30 seconds total target
 * - Auto BPJS eligibility check
 * - Queue number assignment
 * - Success ticket display
 *
 * Performance Targets:
 * - Search: <2 seconds
 * - Check-in flow: <30 seconds total
 */

// Mock patient database (in production, this comes from API)
const MOCK_PATIENTS = [
  {
    id: "1",
    rmNumber: "RM2024001",
    name: "AHMAD SUSANTO",
    nik: "3201010101010001",
    bpjsNumber: "1234567890123",
    bpjsStatus: "active" as BPJSStatus,
    phone: "081234567890",
    lastVisit: "2026-01-10",
    age: 45,
    gender: "male" as const,
  },
  {
    id: "2",
    rmNumber: "RM2024002",
    name: "SITI RAHAYU",
    nik: "3202020202020002",
    bpjsNumber: "9876543210987",
    bpjsStatus: "active" as BPJSStatus,
    phone: "081234567891",
    lastVisit: "2026-01-12",
    age: 32,
    gender: "female" as const,
  },
  {
    id: "3",
    rmNumber: "RM2024003",
    name: "BUDI SANTOSO",
    nik: "3203030303030003",
    bpjsNumber: "1111111111111",
    bpjsStatus: "expired" as BPJSStatus,
    phone: "081234567892",
    lastVisit: "2025-12-20",
    age: 58,
    gender: "male" as const,
  },
  {
    id: "4",
    rmNumber: "RM2024004",
    name: "DEWI LESTARI",
    nik: "3204040404040004",
    bpjsNumber: "2222222222222",
    bpjsStatus: "suspended" as BPJSStatus,
    phone: "081234567893",
    lastVisit: "2026-01-05",
    age: 28,
    gender: "female" as const,
  },
  {
    id: "5",
    rmNumber: "RM2024005",
    name: "EKO PRASETYO",
    nik: "3205050505050005",
    bpjsNumber: null,
    bpjsStatus: null,
    phone: "081234567894",
    lastVisit: "2026-01-14",
    age: 39,
    gender: "male" as const,
  },
];

// Department options
const DEPARTMENTS = [
  { value: "igd", label: "IGD (Instalasi Gawat Darurat)" },
  { value: "int", label: "Poli Penyakit Dalam" },
  { value: "ana", label: "Poli Anak" },
  { value: "bed", label: "Poli Bedah" },
  { value: "obg", label: "Poli Kandungan" },
  { value: "mat", label: "Poli Mata" },
  { value: "kul", label: "Poli Kulit & Kelamin" },
  { value: "par", label: "Poli Paru" },
  { value: "sar", label: "Poli Saraf" },
  { value: "jant", label: "Poli Jantung" },
  { value: "tht", label: "Poli THT" },
  { value: "gig", label: "Poli Gigi" },
];

interface FormErrors {
  department?: string;
}

interface QueueTicket {
  queueNumber: string;
  rmNumber: string;
  patientName: string;
  department: string;
  estimatedWait: string;
  checkInTime: string;
}

export default function QuickCheckInPage() {
  const router = useRouter();

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<typeof MOCK_PATIENTS>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);

  // Selected patient state
  const [selectedPatient, setSelectedPatient] = useState<typeof MOCK_PATIENTS[0] | null>(null);
  const [bpjsData, setBpjsData] = useState<BPJSData | null>(null);

  // Check-in form state
  const [visitDate, setVisitDate] = useState(new Date().toISOString().split("T")[0]);
  const [department, setDepartment] = useState("");
  const [errors, setErrors] = useState<FormErrors>({});

  // Loading and success states
  const [loading, setLoading] = useState(false);
  const [checkingBPJS, setCheckingBPJS] = useState(false);
  const [checkInSuccess, setCheckInSuccess] = useState(false);
  const [queueTicket, setQueueTicket] = useState<QueueTicket | null>(null);

  // Refs
  const searchInputRef = useRef<HTMLInputElement>(null);

  /**
   * Keyboard shortcut: Ctrl+K / Cmd+K to focus search
   */
  useEffect(() => {
    const handleShortcut = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };

    document.addEventListener("keydown", handleShortcut);
    return () => document.removeEventListener("keydown", handleShortcut);
  }, []);

  /**
   * Search patients with debouncing
   */
  const searchPatients = useMemo(() => {
    return (query: string) => {
      if (!query || query.length < 2) {
        setSearchResults([]);
        setShowResults(false);
        return;
      }

      const q = query.toLowerCase();
      const results = MOCK_PATIENTS.filter((p) => {
        return (
          p.rmNumber.toLowerCase().includes(q) ||
          p.bpjsNumber?.includes(q) ||
          p.nik.includes(q) ||
          p.name.toLowerCase().includes(q) ||
          p.phone.includes(q)
        );
      });

      setSearchResults(results);
      setShowResults(true);
    };
  }, []);

  /**
   * Debounced search handler
   */
  useEffect(() => {
    if (!searchQuery) {
      setShowResults(false);
      return;
    }

    const delay = 300; // 300ms debounce
    const timer = setTimeout(() => {
      setIsSearching(true);
      searchPatients(searchQuery);
      setTimeout(() => setIsSearching(false), 100);
    }, delay);

    return () => clearTimeout(timer);
  }, [searchQuery, searchPatients]);

  /**
   * Handle patient selection
   */
  const handleSelectPatient = (patient: typeof MOCK_PATIENTS[0]) => {
    setSelectedPatient(patient);
    setShowResults(false);
    setSearchQuery("");
    setBpjsData(null);

    // Auto-check BPJS eligibility if patient has BPJS
    if (patient.bpjsNumber) {
      setCheckingBPJS(true);
      // Simulate BPJS check (in production, call real API)
      setTimeout(() => {
        setCheckingBPJS(false);
      }, 1500);
    }
  };

  /**
   * Handle BPJS verification complete
   */
  const handleBPJSVerified = (data: BPJSData) => {
    setBpjsData(data);
    setCheckingBPJS(false);
  };

  /**
   * Handle check-in form submission
   */
  const handleCheckIn = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate
    const newErrors: FormErrors = {};
    if (!department) {
      newErrors.department = "Pilih poli tujuan";
    }
    setErrors(newErrors);

    if (Object.keys(newErrors).length > 0) {
      return;
    }

    setLoading(true);

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Generate queue number
      const deptCode = department.toUpperCase();
      const queueNum = String(Math.floor(Math.random() * 100) + 1).padStart(3, "0");
      const queueNumber = `${deptCode}-${queueNum}`;

      // Generate queue ticket
      setQueueTicket({
        queueNumber,
        rmNumber: selectedPatient!.rmNumber,
        patientName: selectedPatient!.name,
        department: DEPARTMENTS.find((d) => d.value === department)?.label || department,
        estimatedWait: "15-30 menit",
        checkInTime: new Date().toLocaleTimeString("id-ID", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      });

      setCheckInSuccess(true);
    } catch (err) {
      console.error("Check-in error:", err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reset for new check-in
   */
  const handleNewCheckIn = () => {
    setSelectedPatient(null);
    setSearchQuery("");
    setBpjsData(null);
    setDepartment("");
    setErrors({});
    setCheckInSuccess(false);
    setQueueTicket(null);
    searchInputRef.current?.focus();
  };

  /**
   * Render success ticket
   */
  if (checkInSuccess && queueTicket) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-teal-50 via-blue-50 to-white flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl overflow-hidden">
          {/* Success Header */}
          <div className="bg-gradient-to-r from-teal-500 to-teal-600 p-8 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-white rounded-full mb-4">
              <CheckCircle className="w-12 h-12 text-teal-600" />
            </div>
            <h1 className="text-2xl font-bold text-white">Check-In Berhasil!</h1>
            <p className="text-teal-100 mt-2">Pasien terdaftar untuk pemeriksaan</p>
          </div>

          {/* Queue Ticket */}
          <div className="p-8">
            <div className="text-center mb-6">
              <p className="text-sm text-gray-600 mb-2">Nomor Antrian</p>
              <p className="text-5xl font-bold text-teal-600">{queueTicket.queueNumber}</p>
            </div>

            <div className="space-y-4 mb-6">
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <span className="text-gray-600">No. RM</span>
                <span className="font-semibold text-gray-900">{queueTicket.rmNumber}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <span className="text-gray-600">Nama Pasien</span>
                <span className="font-semibold text-gray-900">{queueTicket.patientName}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <span className="text-gray-600">Poli Tujuan</span>
                <span className="font-semibold text-gray-900">{queueTicket.department}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <span className="text-gray-600">Jam Check-In</span>
                <span className="font-semibold text-gray-900">{queueTicket.checkInTime}</span>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-gray-600">Estimasi Tunggu</span>
                <span className="font-semibold text-teal-600">{queueTicket.estimatedWait}</span>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-start gap-3">
                <Clock className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-blue-900">Informasi</p>
                  <p className="text-xs text-blue-800 mt-1">
                    Silakan menunggu di ruang tunggu. Nomor antrian akan dipanggil melalui pengeras suara dan layar display.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={handleNewCheckIn}
                className="flex-1 px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 font-medium transition-colors"
              >
                Check-In Pasien Lain
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

  /**
   * Render main page
   */
  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-blue-50 to-white py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-teal-600 rounded-2xl mb-4">
            <User className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Quick Check-In</h1>
          <p className="text-gray-600 mt-2">Cek-in pasien lama dengan cepat</p>
        </div>

        {/* Search Section (always visible) */}
        {!selectedPatient && (
          <div className="bg-white rounded-xl shadow-md p-6 mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cari Pasien
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                {isSearching ? (
                  <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
                ) : (
                  <Search className="w-5 h-5 text-gray-400" />
                )}
              </div>
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Cari by RM, BPJS, NIK, Nama, Telepon..."
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                autoFocus
              />
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <kbd className="inline-flex items-center rounded border border-gray-300 px-2 text-xs font-sans font-medium text-gray-500">
                  ⌘K
                </kbd>
              </div>
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => {
                    setSearchQuery("");
                    setShowResults(false);
                  }}
                  className="absolute inset-y-0 right-12 pr-3 flex items-center"
                >
                  <X className="w-5 h-5 text-gray-400 hover:text-gray-600" />
                </button>
              )}
            </div>

            {/* Search Results */}
            {showResults && searchResults.length > 0 && (
              <div className="mt-4 border border-gray-200 rounded-lg overflow-hidden">
                {searchResults.map((patient) => (
                  <button
                    key={patient.id}
                    type="button"
                    onClick={() => handleSelectPatient(patient)}
                    className="w-full px-4 py-3 hover:bg-gray-50 transition-colors border-b border-gray-200 last:border-b-0 text-left"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-medium text-gray-900">{patient.name}</p>
                          {patient.bpjsStatus && (
                            <BPJSStatusBadge status={patient.bpjsStatus} size="sm" />
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mt-1">RM: {patient.rmNumber}</p>
                        <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                          <span>NIK: {patient.nik}</span>
                          {patient.bpjsNumber && <span>BPJS: {patient.bpjsNumber}</span>}
                        </div>
                      </div>
                      <ArrowRight className="w-5 h-5 text-gray-400" />
                    </div>
                  </button>
                ))}
              </div>
            )}

            {showResults && searchResults.length === 0 && (
              <div className="mt-4 text-center py-8 text-gray-500">
                <User className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>Pasien tidak ditemukan</p>
                <p className="text-sm">Coba kata kunci lain atau daftarkan pasien baru</p>
              </div>
            )}

            {/* Demo data hint */}
            {!searchQuery && (
              <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm font-medium text-blue-900 mb-2">Demo Data (Cari salah satu):</p>
                <ul className="text-xs text-blue-800 space-y-1">
                  <li><strong>RM2024001:</strong> AHMAD SUSANTO (BPJS Aktif)</li>
                  <li><strong>RM2024002:</strong> SITI RAHAYU (BPJS Aktif)</li>
                  <li><strong>RM2024003:</strong> BUDI SANTOSO (BPJS Kadaluarsa)</li>
                  <li><strong>081234567894:</strong> EKO PRASETYO (Tanpa BPJS)</li>
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Selected Patient & Check-In Form */}
        {selectedPatient && (
          <form onSubmit={handleCheckIn} className="space-y-6">
            {/* Patient Info Card */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="bg-gradient-to-r from-teal-500 to-teal-600 px-6 py-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Informasi Pasien
                </h2>
                <button
                  type="button"
                  onClick={() => setSelectedPatient(null)}
                  className="text-teal-100 hover:text-white text-sm"
                >
                  Ganti Pasien
                </button>
              </div>

              <div className="p-6">
                <div className="flex items-start gap-4">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                    <User className="w-8 h-8 text-gray-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{selectedPatient.name}</h3>
                    <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
                      <div>
                        <span className="text-gray-500">No. RM:</span>
                        <span className="ml-2 font-medium text-gray-900">{selectedPatient.rmNumber}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Usia:</span>
                        <span className="ml-2 font-medium text-gray-900">{selectedPatient.age} tahun</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Jenis Kelamin:</span>
                        <span className="ml-2 font-medium text-gray-900">{selectedPatient.gender === "male" ? "Laki-laki" : "Perempuan"}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Kunjungan Terakhir:</span>
                        <span className="ml-2 font-medium text-gray-900">{selectedPatient.lastVisit}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* BPJS Status & Auto-Check */}
                {selectedPatient.bpjsNumber && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <CreditCard className="w-4 h-4 text-blue-600" />
                        <span className="text-sm font-medium text-gray-700">Status BPJS</span>
                      </div>
                      {checkingBPJS && (
                        <div className="flex items-center gap-2 text-sm text-blue-600">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>Memeriksa...</span>
                        </div>
                      )}
                    </div>

                    {bpjsData && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <div className="flex items-center gap-2 text-green-700">
                          <CheckCircle className="w-4 h-4" />
                          <span className="text-sm font-medium">BPJS Aktif</span>
                        </div>
                        <p className="text-xs text-green-600 mt-1">
                          {bpjsData.nama} - {bpjsData.faskes}
                        </p>
                      </div>
                    )}

                    {!bpjsData && selectedPatient.bpjsStatus !== "active" && (
                      <BPJSEligibilityCheck
                        onVerified={handleBPJSVerified}
                        onError={(error) => console.error("BPJS Error:", error)}
                        showAutoFillButton={false}
                        className="mt-3"
                      />
                    )}
                  </div>
                )}

                {!selectedPatient.bpjsNumber && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                      <p className="text-sm text-yellow-700">
                        Pasien tidak terdaftar sebagai peserta BPJS
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Check-In Form Card */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Detail Kunjungan
                </h2>
              </div>

              <div className="p-6 space-y-4">
                {/* Visit Date */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tanggal Kunjungan
                  </label>
                  <input
                    type="date"
                    value={visitDate}
                    onChange={(e) => setVisitDate(e.target.value)}
                    min={new Date().toISOString().split("T")[0]}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                  />
                </div>

                {/* Department Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Poli Tujuan <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 ${
                      errors.department ? "border-red-500" : "border-gray-300"
                    } bg-white`}
                  >
                    <option value="">-- Pilih Poli Tujuan --</option>
                    {DEPARTMENTS.map((dept) => (
                      <option key={dept.value} value={dept.value}>
                        {dept.label}
                      </option>
                    ))}
                  </select>
                  {errors.department && <p className="text-red-600 text-sm mt-1">{errors.department}</p>}
                </div>
              </div>
            </div>

            {/* Submit Actions */}
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setSelectedPatient(null)}
                className="px-6 py-4 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
              >
                Kembali
              </button>
              <button
                type="submit"
                disabled={loading || checkingBPJS}
                className="flex-1 px-6 py-4 bg-gradient-to-r from-teal-600 to-teal-700 text-white rounded-lg hover:from-teal-700 hover:to-teal-800 font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Memproses...
                  </>
                ) : (
                  <>
                    Check-In Pasien
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

// Helper component for BPJS badge
function BPJSStatusBadge({ status, size = "md" }: { status: BPJSStatus; size?: "sm" | "md" | "lg" }) {
  const getStatusConfig = () => {
    switch (status) {
      case "active":
        return {
          bgClass: "bg-green-100",
          textClass: "text-green-700",
          borderClass: "border-green-300",
          label: "Aktif",
        };
      case "inactive":
        return {
          bgClass: "bg-red-100",
          textClass: "text-red-700",
          borderClass: "border-red-300",
          label: "Tidak Aktif",
        };
      case "expired":
        return {
          bgClass: "bg-gray-100",
          textClass: "text-gray-700",
          borderClass: "border-gray-300",
          label: "Kadaluarsa",
        };
      case "suspended":
        return {
          bgClass: "bg-yellow-100",
          textClass: "text-yellow-700",
          borderClass: "border-yellow-300",
          label: "Ditangguhkan",
        };
      default:
        return {
          bgClass: "bg-gray-100",
          textClass: "text-gray-700",
          borderClass: "border-gray-300",
          label: "Tidak Diketahui",
        };
    }
  };

  const config = getStatusConfig();
  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-2 py-1 text-xs",
    lg: "px-3 py-1.5 text-sm",
  };

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border-2 ${config.bgClass} ${config.textClass} ${config.borderClass} ${sizeClasses[size]}`}
    >
      <span className="font-medium">{config.label}</span>
    </span>
  );
}
