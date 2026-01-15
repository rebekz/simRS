"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import {
  Search,
  User,
  Phone,
  Calendar,
  CreditCard,
  Filter,
  X,
  Clock,
  ChevronDown,
  ChevronUp,
  Download,
  History,
  Eye,
  Edit,
  Stethoscope,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";

/**
 * WEB-S-3.6: Patient Search & Lookup
 *
 * Key Features:
 * - Search by RM, BPJS, NIK (main search bar)
 * - Search by name + DOB combination
 * - Search by phone number
 * - Fuzzy search for names (typos tolerated)
 * - Search results with photo, name, RM, BPJS status
 * - Full patient profile modal
 * - Search history (recent searches)
 * - Advanced filters (registration date, department)
 * - Export results to CSV
 * - <5 seconds performance target
 */

// ============================================================================
// TYPES
// ============================================================================

type SearchType = "quick" | "name-dob" | "phone";
type BPJSStatus = "active" | "inactive" | "expired" | "suspended" | null;

interface Patient {
  id: string;
  rmNumber: string;
  name: string;
  nik: string;
  bpjsNumber: string | null;
  bpjsStatus: BPJSStatus;
  phone: string;
  dateOfBirth: string;
  age: number;
  gender: "male" | "female";
  address: string;
  registrationDate: string;
  lastVisit: string;
  photo: string | null;
  department: string;
  bloodType?: string;
  allergies?: string[];
}

interface SearchHistoryItem {
  id: string;
  query: string;
  type: SearchType;
  timestamp: string;
}

interface AdvancedFilters {
  registrationStartDate: string;
  registrationEndDate: string;
  departments: string[];
}

// ============================================================================
// MOCK DATA
// ============================================================================

const MOCK_PATIENTS: Patient[] = [
  {
    id: "1",
    rmNumber: "RM2024001",
    name: "AHMAD SUSANTO",
    nik: "3201010101010001",
    bpjsNumber: "1234567890123",
    bpjsStatus: "active",
    phone: "081234567890",
    dateOfBirth: "1979-05-15",
    age: 45,
    gender: "male",
    address: "Jl. Merdeka No. 123, Jakarta",
    registrationDate: "2024-01-10",
    lastVisit: "2026-01-10",
    photo: null,
    department: "Penyakit Dalam",
    bloodType: "O",
    allergies: ["Penisilin"],
  },
  {
    id: "2",
    rmNumber: "RM2024002",
    name: "SITI RAHAYU",
    nik: "3202020202020002",
    bpjsNumber: "9876543210987",
    bpjsStatus: "active",
    phone: "081234567891",
    dateOfBirth: "1992-08-22",
    age: 32,
    gender: "female",
    address: "Jl. Sudirman No. 45, Bandung",
    registrationDate: "2024-01-12",
    lastVisit: "2026-01-12",
    photo: null,
    department: "Anak",
    bloodType: "A",
    allergies: [],
  },
  {
    id: "3",
    rmNumber: "RM2024003",
    name: "BUDI SANTOSO",
    nik: "3203030303030003",
    bpjsNumber: "1111111111111",
    bpjsStatus: "expired",
    phone: "081234567892",
    dateOfBirth: "1966-12-10",
    age: 58,
    gender: "male",
    address: "Jl. Gatot Subroto No. 78, Surabaya",
    registrationDate: "2024-02-15",
    lastVisit: "2025-12-20",
    photo: null,
    department: "Penyakit Dalam",
    bloodType: "B",
    allergies: ["Aspirin"],
  },
  {
    id: "4",
    rmNumber: "RM2024004",
    name: "DEWI LESTARI",
    nik: "3204040404040004",
    bpjsNumber: "2222222222222",
    bpjsStatus: "suspended",
    phone: "081234567893",
    dateOfBirth: "1996-03-18",
    age: 28,
    gender: "female",
    address: "Jl. Ahmad Yani No. 234, Semarang",
    registrationDate: "2024-03-01",
    lastVisit: "2026-01-05",
    photo: null,
    department: "Kandungan",
    bloodType: "AB",
    allergies: [],
  },
  {
    id: "5",
    rmNumber: "RM2024005",
    name: "EKO PRASETYO",
    nik: "3205050505050005",
    bpjsNumber: null,
    bpjsStatus: null,
    phone: "081234567894",
    dateOfBirth: "1985-07-30",
    age: 39,
    gender: "male",
    address: "Jl. Diponegoro No. 56, Yogyakarta",
    registrationDate: "2024-03-10",
    lastVisit: "2026-01-14",
    photo: null,
    department: "Bedah",
    bloodType: "O",
    allergies: ["Latex"],
  },
  {
    id: "6",
    rmNumber: "RM2024006",
    name: "RINA WATI",
    nik: "3206060606060006",
    bpjsNumber: "3333333333333",
    bpjsStatus: "active",
    phone: "081234567895",
    dateOfBirth: "1978-11-25",
    age: 46,
    gender: "female",
    address: "Jl. Pemuda No. 89, Malang",
    registrationDate: "2024-04-05",
    lastVisit: "2026-01-08",
    photo: null,
    department: "Mata",
    bloodType: "A",
    allergies: [],
  },
  {
    id: "7",
    rmNumber: "RM2024007",
    name: "AGUS SETIAWAN",
    nik: "3207070707070007",
    bpjsNumber: "4444444444444",
    bpjsStatus: "active",
    phone: "081234567896",
    dateOfBirth: "1972-02-14",
    age: 52,
    gender: "male",
    address: "Jl. Hayam Wuruk No. 12, Jakarta",
    registrationDate: "2024-04-20",
    lastVisit: "2026-01-13",
    photo: null,
    department: "Penyakit Dalam",
    bloodType: "B",
    allergies: [],
  },
  {
    id: "8",
    rmNumber: "RM2024008",
    name: "LILIS SURYANI",
    nik: "3208080808080008",
    bpjsNumber: "5555555555555",
    bpjsStatus: "active",
    phone: "081234567897",
    dateOfBirth: "1987-09-05",
    age: 37,
    gender: "female",
    address: "Jl. Asia Afrika No. 67, Bandung",
    registrationDate: "2024-05-15",
    lastVisit: "2026-01-11",
    photo: null,
    department: "Kandungan",
    bloodType: "O",
    allergies: ["Sulfonamides"],
  },
];

const DEPARTMENTS = [
  "Penyakit Dalam",
  "Anak",
  "Bedah",
  "Kandungan",
  "Mata",
  "THT",
  "Kulit & Kelamin",
  "Saraf",
  "Jantung",
  "Paru",
];

// ============================================================================
// COMPONENTS
// ============================================================================

/**
 * BPJS Status Badge Component
 */
function BPJSStatusBadge({ status, size = "sm" }: { status: BPJSStatus; size?: "sm" | "md" }) {
  if (!status) {
    return (
      <Badge variant="neutral" className={size === "sm" ? "text-xs" : "text-sm"}>
        Non-BPJS
      </Badge>
    );
  }

  const getStatusConfig = () => {
    switch (status) {
      case "active":
        return {
          label: "Aktif",
          variant: "success" as const,
        };
      case "inactive":
        return {
          label: "Tidak Aktif",
          variant: "error" as const,
        };
      case "expired":
        return {
          label: "Kadaluarsa",
          variant: "neutral" as const,
        };
      case "suspended":
        return {
          label: "Ditangguhkan",
          variant: "warning" as const,
        };
    }
  };

  const config = getStatusConfig();
  return <Badge variant={config.variant} className={size === "sm" ? "text-xs" : "text-sm"}>{config.label}</Badge>;
}

/**
 * Simple fuzzy match (approximate matching)
 */
function fuzzyMatch(query: string, text: string): boolean {
  const queryLower = query.toLowerCase();
  const textLower = text.toLowerCase();

  // Exact match
  if (textLower.includes(queryLower)) {
    return true;
  }

  // Fuzzy match - allow up to 2 character differences
  if (queryLower.length >= 3) {
    let matchCount = 0;
    let queryIndex = 0;

    for (let i = 0; i < textLower.length && queryIndex < queryLower.length; i++) {
      if (textLower[i] === queryLower[queryIndex]) {
        matchCount++;
        queryIndex++;
      }
    }

    // Allow up to 2 character mismatches for 3-5 char queries, more for longer
    const threshold = queryLower.length <= 5 ? queryLower.length - 2 : queryLower.length - 3;
    return matchCount >= threshold;
  }

  return false;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function PatientSearchPage() {
  // Search state
  const [searchType, setSearchType] = useState<SearchType>("quick");
  const [quickQuery, setQuickQuery] = useState("");
  const [nameQuery, setNameQuery] = useState("");
  const [dobQuery, setDobQuery] = useState("");
  const [phoneQuery, setPhoneQuery] = useState("");

  // Results state
  const [searchResults, setSearchResults] = useState<Patient[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // Profile modal state
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [showProfileModal, setShowProfileModal] = useState(false);

  // Search history
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([
    {
      id: "1",
      query: "RM2024001",
      type: "quick",
      timestamp: "2026-01-16 14:30",
    },
    {
      id: "2",
      query: "081234567890",
      type: "phone",
      timestamp: "2026-01-16 14:25",
    },
    {
      id: "3",
      query: "Ahmad Susanto",
      type: "name-dob",
      timestamp: "2026-01-16 14:20",
    },
  ]);

  // Advanced filters
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [advancedFilters, setAdvancedFilters] = useState<AdvancedFilters>({
    registrationStartDate: "",
    registrationEndDate: "",
    departments: [],
  });

  /**
   * Quick search by RM, BPJS, or NIK
   */
  const handleQuickSearch = useCallback(() => {
    if (!quickQuery.trim()) return;

    setIsSearching(true);
    setHasSearched(true);

    // Simulate search delay
    setTimeout(() => {
      const results = MOCK_PATIENTS.filter((patient) => {
        return (
          patient.rmNumber.toLowerCase().includes(quickQuery.toLowerCase()) ||
          (patient.bpjsNumber && patient.bpjsNumber.includes(quickQuery)) ||
          patient.nik.includes(quickQuery)
        );
      });

      setSearchResults(results);
      setIsSearching(false);

      // Add to history
      addToHistory(quickQuery, "quick");
    }, 300);
  }, [quickQuery]);

  /**
   * Search by name + DOB
   */
  const handleNameDOBSearch = useCallback(() => {
    if (!nameQuery.trim()) return;

    setIsSearching(true);
    setHasSearched(true);

    setTimeout(() => {
      const results = MOCK_PATIENTS.filter((patient) => {
        const nameMatch = fuzzyMatch(nameQuery, patient.name);
        const dobMatch = !dobQuery || patient.dateOfBirth === dobQuery;
        return nameMatch && dobMatch;
      });

      setSearchResults(results);
      setIsSearching(false);

      // Add to history
      addToHistory(nameQuery, "name-dob");
    }, 300);
  }, [nameQuery, dobQuery]);

  /**
   * Search by phone
   */
  const handlePhoneSearch = useCallback(() => {
    if (!phoneQuery.trim()) return;

    setIsSearching(true);
    setHasSearched(true);

    setTimeout(() => {
      const results = MOCK_PATIENTS.filter((patient) => {
        return patient.phone.includes(phoneQuery);
      });

      setSearchResults(results);
      setIsSearching(false);

      // Add to history
      addToHistory(phoneQuery, "phone");
    }, 300);
  }, [phoneQuery]);

  /**
   * Add to search history
   */
  const addToHistory = (query: string, type: SearchType) => {
    const newItem: SearchHistoryItem = {
      id: Date.now().toString(),
      query,
      type,
      timestamp: new Date().toLocaleString("id-ID"),
    };

    setSearchHistory((prev) => [newItem, ...prev].slice(0, 10)); // Keep last 10
  };

  /**
   * Repeat search from history
   */
  const handleHistoryClick = (item: SearchHistoryItem) => {
    setSearchType(item.type);

    if (item.type === "quick") {
      setQuickQuery(item.query);
      setTimeout(() => {
        setQuickQuery(item.query);
        handleQuickSearch();
      }, 0);
    } else if (item.type === "phone") {
      setPhoneQuery(item.query);
      setTimeout(() => {
        setPhoneQuery(item.query);
        handlePhoneSearch();
      }, 0);
    } else if (item.type === "name-dob") {
      setNameQuery(item.query);
      setTimeout(() => {
        setNameQuery(item.query);
        handleNameDOBSearch();
      }, 0);
    }
  };

  /**
   * View patient profile
   */
  const handleViewProfile = (patient: Patient) => {
    setSelectedPatient(patient);
    setShowProfileModal(true);
  };

  /**
   * Apply advanced filters
   */
  const applyAdvancedFilters = useCallback(() => {
    if (!hasSearched) return;

    let filtered = [...searchResults];

    // Filter by registration date
    if (advancedFilters.registrationStartDate) {
      filtered = filtered.filter((p) => p.registrationDate >= advancedFilters.registrationStartDate);
    }
    if (advancedFilters.registrationEndDate) {
      filtered = filtered.filter((p) => p.registrationDate <= advancedFilters.registrationEndDate);
    }

    // Filter by departments
    if (advancedFilters.departments.length > 0) {
      filtered = filtered.filter((p) => advancedFilters.departments.includes(p.department));
    }

    setSearchResults(filtered);
  }, [hasSearched, searchResults, advancedFilters]);

  /**
   * Export to CSV
   */
  const handleExportCSV = () => {
    const headers = ["RM Number", "Nama", "NIK", "BPJS Number", "BPJS Status", "Telepon", "Tanggal Lahir", "Usia", "Jenis Kelamin", "Alamat", "Departemen"];
    const csvContent = [
      headers.join(","),
      ...searchResults.map((p) =>
        [
          p.rmNumber,
          p.name,
          p.nik,
          p.bpjsNumber || "",
          p.bpjsStatus || "",
          p.phone,
          p.dateOfBirth,
          p.age,
          p.gender,
          `"${p.address}"`,
          p.department,
        ].join(",")
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `patient-search-${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  /**
   * Handle keyboard shortcuts
   */
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === "Enter") {
        if (searchType === "quick") {
          handleQuickSearch();
        } else if (searchType === "name-dob") {
          handleNameDOBSearch();
        } else if (searchType === "phone") {
          handlePhoneSearch();
        }
      }
    };

    document.addEventListener("keydown", handleKeyPress);
    return () => document.removeEventListener("keydown", handleKeyPress);
  }, [searchType, handleQuickSearch, handleNameDOBSearch, handlePhoneSearch]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
              <Search className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Patient Search & Lookup</h1>
              <p className="text-sm text-gray-600">Temukan pasien dalam &lt;5 detik</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Search Type Tabs */}
        <div className="bg-white rounded-xl shadow-md p-2 mb-6">
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setSearchType("quick")}
              className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all ${
                searchType === "quick"
                  ? "bg-blue-600 text-white shadow-md"
                  : "bg-gray-50 text-gray-700 hover:bg-gray-100"
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <Search className="w-4 h-4" />
                <span>Cepat (RM/BPJS/NIK)</span>
              </div>
            </button>
            <button
              type="button"
              onClick={() => setSearchType("name-dob")}
              className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all ${
                searchType === "name-dob"
                  ? "bg-blue-600 text-white shadow-md"
                  : "bg-gray-50 text-gray-700 hover:bg-gray-100"
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <User className="w-4 h-4" />
                <span>Nama + Tanggal Lahir</span>
              </div>
            </button>
            <button
              type="button"
              onClick={() => setSearchType("phone")}
              className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all ${
                searchType === "phone"
                  ? "bg-blue-600 text-white shadow-md"
                  : "bg-gray-50 text-gray-700 hover:bg-gray-100"
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <Phone className="w-4 h-4" />
                <span>Nomor Telepon</span>
              </div>
            </button>
          </div>
        </div>

        {/* Search Forms */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Main Search Area */}
          <div className="lg:col-span-2">
            {/* Quick Search */}
            {searchType === "quick" && (
              <div className="bg-white rounded-xl shadow-md p-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cari berdasarkan Nomor RM, BPJS, atau NIK
                </label>
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={quickQuery}
                    onChange={(e) => setQuickQuery(e.target.value)}
                    placeholder="Contoh: RM2024001, 1234567890123, atau 3201010101010001"
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    autoFocus
                  />
                  <button
                    type="button"
                    onClick={handleQuickSearch}
                    disabled={isSearching || !quickQuery.trim()}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center gap-2"
                  >
                    <Search className="w-4 h-4" />
                    {isSearching ? "Mencari..." : "Cari"}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Tekan Enter untuk mencari
                </p>
              </div>
            )}

            {/* Name + DOB Search */}
            {searchType === "name-dob" && (
              <div className="bg-white rounded-xl shadow-md p-6">
                <label className="block text-sm font-medium text-gray-700 mb-4">
                  Cari berdasarkan Nama Pasien (opsional + Tanggal Lahir)
                </label>
                <div className="space-y-4">
                  <div>
                    <input
                      type="text"
                      value={nameQuery}
                      onChange={(e) => setNameQuery(e.target.value)}
                      placeholder="Masukkan nama pasien..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      autoFocus
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Pencarian fuzzy - toleransi kesalahan ketik
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tanggal Lahir (Opsional)
                    </label>
                    <input
                      type="date"
                      value={dobQuery}
                      onChange={(e) => setDobQuery(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={handleNameDOBSearch}
                    disabled={isSearching || !nameQuery.trim()}
                    className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center justify-center gap-2"
                  >
                    <Search className="w-4 h-4" />
                    {isSearching ? "Mencari..." : "Cari Pasien"}
                  </button>
                </div>
              </div>
            )}

            {/* Phone Search */}
            {searchType === "phone" && (
              <div className="bg-white rounded-xl shadow-md p-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cari berdasarkan Nomor Telepon
                </label>
                <div className="flex gap-3">
                  <input
                    type="tel"
                    value={phoneQuery}
                    onChange={(e) => setPhoneQuery(e.target.value)}
                    placeholder="Contoh: 081234567890"
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    autoFocus
                  />
                  <button
                    type="button"
                    onClick={handlePhoneSearch}
                    disabled={isSearching || !phoneQuery.trim()}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center gap-2"
                  >
                    <Search className="w-4 h-4" />
                    {isSearching ? "Mencari..." : "Cari"}
                  </button>
                </div>
              </div>
            )}

            {/* Advanced Filters Toggle */}
            <button
              type="button"
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className="mt-4 w-full px-4 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 flex items-center justify-center gap-2 text-sm font-medium"
            >
              <Filter className="w-4 h-4" />
              Filter Lanjutan
              {showAdvancedFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {/* Advanced Filters Panel */}
            {showAdvancedFilters && (
              <div className="mt-4 bg-gray-50 rounded-lg p-4 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tanggal Registrasi (Dari)
                    </label>
                    <input
                      type="date"
                      value={advancedFilters.registrationStartDate}
                      onChange={(e) =>
                        setAdvancedFilters({ ...advancedFilters, registrationStartDate: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tanggal Registrasi (Sampai)
                    </label>
                    <input
                      type="date"
                      value={advancedFilters.registrationEndDate}
                      onChange={(e) =>
                        setAdvancedFilters({ ...advancedFilters, registrationEndDate: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Departemen
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {DEPARTMENTS.map((dept) => (
                      <label key={dept} className="inline-flex items-center">
                        <input
                          type="checkbox"
                          checked={advancedFilters.departments.includes(dept)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setAdvancedFilters({
                                ...advancedFilters,
                                departments: [...advancedFilters.departments, dept],
                              });
                            } else {
                              setAdvancedFilters({
                                ...advancedFilters,
                                departments: advancedFilters.departments.filter((d) => d !== dept),
                              });
                            }
                          }}
                          className="mr-1"
                        />
                        <span className="text-sm text-gray-700">{dept}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={applyAdvancedFilters}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
                  >
                    Terapkan Filter
                  </button>
                  <button
                    type="button"
                    onClick={() =>
                      setAdvancedFilters({
                        registrationStartDate: "",
                        registrationEndDate: "",
                        departments: [],
                      })
                    }
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm font-medium"
                  >
                    Reset
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Search History */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <History className="w-5 h-5" />
                Pencarian Terakhir
              </h3>
              <button
                type="button"
                onClick={() => setSearchHistory([])}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Hapus Semua
              </button>
            </div>

            <div className="space-y-2">
              {searchHistory.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">Belum ada riwayat pencarian</p>
              ) : (
                searchHistory.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => handleHistoryClick(item)}
                    className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors group"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">{item.query}</p>
                        <p className="text-xs text-gray-500">{item.timestamp}</p>
                      </div>
                      <Search className="w-4 h-4 text-gray-400 group-hover:text-blue-600" />
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Search Results */}
        {hasSearched && (
          <div className="bg-white rounded-xl shadow-md overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">
                Hasil Pencarian ({searchResults.length} pasien)
              </h2>
              {searchResults.length > 0 && (
                <button
                  type="button"
                  onClick={handleExportCSV}
                  className="px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg flex items-center gap-2 text-sm font-medium"
                >
                  <Download className="w-4 h-4" />
                  Export CSV
                </button>
              )}
            </div>

            {searchResults.length === 0 ? (
              <div className="p-12 text-center text-gray-500">
                <Search className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium">Tidak ditemukan</p>
                <p className="text-sm">Coba kata kunci lain atau periksa kembali pencarian Anda</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
                {searchResults.map((patient) => (
                  <div
                    key={patient.id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow bg-white"
                  >
                    {/* Patient Header */}
                    <div className="flex items-start gap-3 mb-3">
                      {/* Photo Placeholder */}
                      <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <User className="w-8 h-8 text-gray-400" />
                      </div>

                      {/* Patient Info */}
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-gray-900 truncate">{patient.name}</h3>
                        <p className="text-sm text-gray-600">{patient.rmNumber}</p>
                        <div className="mt-1">
                          <BPJSStatusBadge status={patient.bpjsStatus} />
                        </div>
                      </div>
                    </div>

                    {/* Patient Details */}
                    <div className="space-y-2 text-sm text-gray-600 mb-4">
                      <div className="flex justify-between">
                        <span>Usia:</span>
                        <span className="font-medium text-gray-900">{patient.age} tahun</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Jenis Kelamin:</span>
                        <span className="font-medium text-gray-900">
                          {patient.gender === "male" ? "Laki-laki" : "Perempuan"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Telepon:</span>
                        <span className="font-medium text-gray-900">{patient.phone}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Departemen:</span>
                        <span className="font-medium text-gray-900">{patient.department}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Kunjungan Terakhir:</span>
                        <span className="font-medium text-gray-900">{patient.lastVisit}</span>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => handleViewProfile(patient)}
                        className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium flex items-center justify-center gap-1"
                      >
                        <Eye className="w-3 h-3" />
                        Lihat Profil
                      </button>
                      <button
                        type="button"
                        className="px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm font-medium"
                      >
                        <Edit className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Patient Profile Modal */}
      {showProfileModal && selectedPatient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                  <User className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">{selectedPatient.name}</h2>
                  <p className="text-blue-100">{selectedPatient.rmNumber}</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => {
                  setShowProfileModal(false);
                  setSelectedPatient(null);
                }}
                className="text-white hover:text-blue-100"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6">
              {/* Patient Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                {/* Left Column */}
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">Informasi Personal</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">NIK:</span>
                        <span className="font-medium text-gray-900">{selectedPatient.nik}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tanggal Lahir:</span>
                        <span className="font-medium text-gray-900">{selectedPatient.dateOfBirth}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Usia:</span>
                        <span className="font-medium text-gray-900">{selectedPatient.age} tahun</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Jenis Kelamin:</span>
                        <span className="font-medium text-gray-900">
                          {selectedPatient.gender === "male" ? "Laki-laki" : "Perempuan"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Golongan Darah:</span>
                        <span className="font-medium text-gray-900">{selectedPatient.bloodType || "-"}</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">Kontak</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Telepon:</span>
                        <span className="font-medium text-gray-900">{selectedPatient.phone}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Alamat:</span>
                        <span className="font-medium text-gray-900 text-right">{selectedPatient.address}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Right Column */}
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">BPJS</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">No. BPJS:</span>
                        <span className="font-medium text-gray-900 font-mono">
                          {selectedPatient.bpjsNumber || "-"}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Status:</span>
                        <BPJSStatusBadge status={selectedPatient.bpjsStatus} size="md" />
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">Medis</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Departemen:</span>
                        <span className="font-medium text-gray-900">{selectedPatient.department}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Alergi:</span>
                        <span className="font-medium text-gray-900">
                          {selectedPatient.allergies && selectedPatient.allergies.length > 0
                            ? selectedPatient.allergies.join(", ")
                            : "-"}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">Registrasi</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tgl. Registrasi:</span>
                        <span className="font-medium text-gray-900">{selectedPatient.registrationDate}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Kunjungan Terakhir:</span>
                        <span className="font-medium text-gray-900">{selectedPatient.lastVisit}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium flex items-center justify-center gap-2"
                >
                  <Stethoscope className="w-4 h-4" />
                  Mulai Kunjungan
                </button>
                <button
                  type="button"
                  className="px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium flex items-center justify-center gap-2"
                >
                  <Edit className="w-4 h-4" />
                  Edit Profil
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowProfileModal(false);
                    setSelectedPatient(null);
                  }}
                  className="px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
                >
                  Tutup
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
