"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface TriagePatient {
  id: number;
  patient_id: number;
  patient_name: string;
  medical_record_number: string;
  age: number;
  gender: string;
  chief_complaint: string;
  triage_category: "red" | "yellow" | "green" | "black";
  triage_score: number;
  vital_signs: VitalSigns;
  arrival_time: string;
  triaged_by: string;
  triage_time: string;
  status: "waiting" | "in_progress" | "admitted" | "discharged" | "deceased";
  department: string;
  notes?: string;
  allergies?: string[];
  chronic_conditions?: string[];
}

interface VitalSigns {
  blood_pressure_systolic: number;
  blood_pressure_diastolic: number;
  heart_rate: number;
  respiratory_rate: number;
  temperature: number;
  oxygen_saturation: number;
  pain_score: number;
  consciousness_level: "alert" | "verbal" | "pain" | "unresponsive";
  glasgow_coma_scale?: number;
}

export default function EmergencyDepartmentPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [patients, setPatients] = useState<TriagePatient[]>([]);
  const [expandedPatient, setExpandedPatient] = useState<number | null>(null);
  const [filters, setFilters] = useState({
    category: "",
    status: "",
    department: "",
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [stats, setStats] = useState({
    totalToday: 0,
    red: 0,
    yellow: 0,
    green: 0,
    black: 0,
    avgWaitTime: 0,
  });

  useEffect(() => {
    checkAuth();
    fetchPatients();
    fetchStats();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
    }
  };

  const fetchPatients = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const queryParams = new URLSearchParams();
      if (filters.category) queryParams.append("category", filters.category);
      if (filters.status) queryParams.append("status", filters.status);
      if (filters.department) queryParams.append("department", filters.department);
      if (searchQuery) queryParams.append("search", searchQuery);

      const response = await fetch(`/api/v1/emergency/triage?${queryParams}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch emergency patients");
      }

      const data = await response.json();
      setPatients(data.patients || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load patients");
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/emergency/statistics", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats({
          totalToday: data.total_today || 0,
          red: data.red || 0,
          yellow: data.yellow || 0,
          green: data.green || 0,
          black: data.black || 0,
          avgWaitTime: data.avg_wait_time || 0,
        });
      }
    } catch (err) {
      console.error("Failed to fetch statistics:", err);
    }
  };

  const handleUpdateStatus = async (patientId: number, newStatus: string) => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/emergency/triage/${patientId}/status`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error("Failed to update status");
      }

      fetchPatients();
      fetchStats();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to update status");
    }
  };

  const handleReTriage = async (patientId: number) => {
    router.push(`/app/emergency/${patientId}/retriage`);
  };

  const getTriageCategoryConfig = (category: string) => {
    const configs: Record<string, { label: string; description: string; color: string; bgColor: string; priority: number }> = {
      red: {
        label: "MERAH (Resusitasi)",
        description: "Ancaman nyawa segera - perlu tindakan instan",
        color: "text-red-700",
        bgColor: "bg-red-100",
        priority: 1,
      },
      yellow: {
        label: "KUNING (Urgent)",
        description: "Kondisi serius - perlu tindakan segera",
        color: "text-yellow-700",
        bgColor: "bg-yellow-100",
        priority: 2,
      },
      green: {
        label: "HIJAU (Non-Urgent)",
        description: "Kondisi stabil - dapat menunggu",
        color: "text-green-700",
        bgColor: "bg-green-100",
        priority: 3,
      },
      black: {
        label: "HITAM (Meninggal)",
        description: "Tanpa tanda-tanda kehidupan",
        color: "text-gray-700",
        bgColor: "bg-gray-200",
        priority: 4,
      },
    };

    return configs[category] || configs.green;
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; className: string }> = {
      waiting: { label: "Menunggu", className: "bg-blue-100 text-blue-700" },
      in_progress: { label: "Ditangani", className: "bg-yellow-100 text-yellow-700" },
      admitted: { label: "Dirawat", className: "bg-green-100 text-green-700" },
      discharged: { label: "Pulang", className: "bg-gray-100 text-gray-700" },
      deceased: { label: "Meninggal", className: "bg-black text-white" },
    };

    const config = statusConfig[status] || statusConfig.waiting;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.className}`}>
        {config.label}
      </span>
    );
  };

  const getConsciousnessBadge = (level: string) => {
    const levelConfig: Record<string, { label: string; className: string }> = {
      alert: { label: "Alert (A)", className: "bg-green-100 text-green-700" },
      verbal: { label: "Verbal (V)", className: "bg-yellow-100 text-yellow-700" },
      pain: { label: "Pain (P)", className: "bg-orange-100 text-orange-700" },
      unresponsive: { label: "Unresponsive (U)", className: "bg-red-100 text-red-700" },
    };

    const config = levelConfig[level] || levelConfig.alert;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.className}`}>
        {config.label}
      </span>
    );
  };

  const isVitalSignsAbnormal = (vitalSigns: VitalSigns) => {
    return (
      vitalSigns.blood_pressure_systolic < 90 ||
      vitalSigns.blood_pressure_systolic > 180 ||
      vitalSigns.heart_rate < 50 ||
      vitalSigns.heart_rate > 120 ||
      vitalSigns.respiratory_rate < 10 ||
      vitalSigns.respiratory_rate > 30 ||
      vitalSigns.temperature < 35 ||
      vitalSigns.temperature > 40 ||
      vitalSigns.oxygen_saturation < 90 ||
      vitalSigns.pain_score >= 7
    );
  };

  const toggleExpand = (patientId: number) => {
    setExpandedPatient(expandedPatient === patientId ? null : patientId);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Instalasi Gawat Darurat (IGD)</h1>
          <p className="text-gray-600 mt-1">Sistem triage dan manajemen pasien emergency</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => router.push("/app/emergency/protocols")}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>Protokol</span>
          </button>
          <button
            onClick={() => router.push("/app/emergency/triage/new")}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center space-x-2 animate-pulse"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>Pasien Baru</span>
          </button>
        </div>
      </div>

      {/* Statistics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-100 text-sm">Merah</p>
              <p className="text-3xl font-bold mt-1">{stats.red}</p>
              <p className="text-red-100 text-xs mt-2">Resusitasi</p>
            </div>
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🚨</span>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-400 to-yellow-500 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm">Kuning</p>
              <p className="text-3xl font-bold mt-1">{stats.yellow}</p>
              <p className="text-yellow-100 text-xs mt-2">Urgent</p>
            </div>
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⚠️</span>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Hijau</p>
              <p className="text-3xl font-bold mt-1">{stats.green}</p>
              <p className="text-green-100 text-xs mt-2">Non-Urgent</p>
            </div>
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <span className="text-2xl">✅</span>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-gray-600 to-gray-700 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 text-sm">Hitam</p>
              <p className="text-3xl font-bold mt-1">{stats.black}</p>
              <p className="text-gray-300 text-xs mt-2">Meninggal</p>
            </div>
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⚫</span>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Hari Ini</p>
              <p className="text-3xl font-bold mt-1">{stats.totalToday}</p>
              <p className="text-blue-100 text-xs mt-2">Pasien</p>
            </div>
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🏥</span>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Rata-rata</p>
              <p className="text-2xl font-bold mt-1">{Math.round(stats.avgWaitTime)}m</p>
              <p className="text-purple-100 text-xs mt-2">Waktu Tunggu</p>
            </div>
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⏱️</span>
            </div>
          </div>
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

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Kategori Triage</label>
            <select
              value={filters.category}
              onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            >
              <option value="">Semua</option>
              <option value="red">Merah (Resusitasi)</option>
              <option value="yellow">Kuning (Urgent)</option>
              <option value="green">Hijau (Non-Urgent)</option>
              <option value="black">Hitam (Meninggal)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            >
              <option value="">Semua</option>
              <option value="waiting">Menunggu</option>
              <option value="in_progress">Ditangani</option>
              <option value="admitted">Dirawat</option>
              <option value="discharged">Pulang</option>
              <option value="deceased">Meninggal</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Departemen</label>
            <select
              value={filters.department}
              onChange={(e) => setFilters({ ...filters, department: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            >
              <option value="">Semua</option>
              <option value="igd">IGD</option>
              <option value="poly">Poli</option>
              <option value="inpatient">Rawat Inap</option>
              <option value="icu">ICU</option>
              <option value="operating_room">OK</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => {
                setFilters({ category: "", status: "", department: "" });
                setSearchQuery("");
                fetchPatients();
              }}
              className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Reset
            </button>
          </div>
        </div>

        <div className="mt-4">
          <input
            type="text"
            placeholder="Cari berdasarkan nama pasien, No RM, atau keluhan..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
          />
        </div>
      </div>

      {/* Patients List */}
      {patients.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada pasien IGD</h3>
          <p className="text-gray-600">Belum ada pasien di IGD atau pasien telah dipindahkan</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prioritas</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pasien</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Keluhan</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Tanda Vital</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Waktu</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Aksi</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {patients
                  .sort((a, b) => getTriageCategoryConfig(a.triage_category).priority - getTriageCategoryConfig(b.triage_category).priority)
                  .map((patient) => {
                    const config = getTriageCategoryConfig(patient.triage_category);
                    const hasAbnormalVitals = isVitalSignsAbnormal(patient.vital_signs);
                    const waitTime = Date.now() - new Date(patient.arrival_time).getTime();
                    const waitMinutes = Math.floor(waitTime / 60000);

                    return (
                      <>
                        <tr
                          key={patient.id}
                          className={`hover:bg-gray-50 cursor-pointer ${patient.triage_category === "red" ? "bg-red-50" : ""}`}
                          onClick={() => toggleExpand(patient.id)}
                        >
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className={`px-3 py-2 rounded-lg ${config.bgColor} ${config.color}`}>
                              <div className="text-xs font-semibold">{config.label}</div>
                              <div className="text-xs mt-1 opacity-75">Score: {patient.triage_score}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{patient.patient_name}</div>
                            <div className="text-xs text-gray-500">{patient.medical_record_number}</div>
                            <div className="text-xs text-gray-400">
                              {patient.age} th • {patient.gender === "male" ? "L" : "P"}
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="text-sm text-gray-900 max-w-xs truncate">{patient.chief_complaint}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {getStatusBadge(patient.status)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            {hasAbnormalVitals && (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700 animate-pulse">
                                ⚠️ Abnormal
                              </span>
                            )}
                            {!hasAbnormalVitals && (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                                ✅ Stabil
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right">
                            <div className="text-sm text-gray-900">{waitMinutes} menit</div>
                            <div className="text-xs text-gray-500">
                              {new Date(patient.arrival_time).toLocaleTimeString("id-ID", {
                                hour: "2-digit",
                                minute: "2-digit",
                              })}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <div className="flex items-center justify-center space-x-2">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleReTriage(patient.id);
                                }}
                                className="p-1 text-gray-400 hover:text-blue-600"
                                title="Re-Triage"
                              >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg>
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  toggleExpand(patient.id);
                                }}
                                className="p-1 text-gray-400 hover:text-blue-600"
                                title="Detail"
                              >
                                {expandedPatient === patient.id ? (
                                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                                  </svg>
                                ) : (
                                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                  </svg>
                                )}
                              </button>
                            </div>
                          </td>
                        </tr>
                        {expandedPatient === patient.id && (
                          <tr>
                            <td colSpan={7} className="px-6 py-4 bg-gray-50">
                              <div className="space-y-4">
                                {/* Patient Information */}
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                  <div>
                                    <p className="text-xs text-gray-500">Departemen</p>
                                    <p className="text-sm font-medium text-gray-900 capitalize">{patient.department}</p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-gray-500">Ditriage Oleh</p>
                                    <p className="text-sm font-medium text-gray-900">{patient.triaged_by}</p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-gray-500">Waktu Triage</p>
                                    <p className="text-sm font-medium text-gray-900">
                                      {new Date(patient.triage_time).toLocaleString("id-ID")}
                                    </p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-gray-500">Waktu Tunggu</p>
                                    <p className="text-sm font-medium text-gray-900">{waitMinutes} menit</p>
                                  </div>
                                </div>

                                {/* Vital Signs */}
                                <div className="bg-white rounded-lg p-4 border border-gray-200">
                                  <h4 className="text-sm font-medium text-gray-900 mb-3">Tanda Vital</h4>
                                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div>
                                      <p className="text-xs text-gray-500">Tekanan Darah</p>
                                      <p className={`text-sm font-medium ${
                                        patient.vital_signs.blood_pressure_systolic < 90 || patient.vital_signs.blood_pressure_systolic > 180
                                          ? "text-red-600"
                                          : "text-gray-900"
                                      }`}>
                                        {patient.vital_signs.blood_pressure_systolic}/{patient.vital_signs.blood_pressure_diastolic} mmHg
                                      </p>
                                    </div>
                                    <div>
                                      <p className="text-xs text-gray-500">Nadi</p>
                                      <p className={`text-sm font-medium ${
                                        patient.vital_signs.heart_rate < 50 || patient.vital_signs.heart_rate > 120
                                          ? "text-red-600"
                                          : "text-gray-900"
                                      }`}>
                                        {patient.vital_signs.heart_rate} x/menit
                                      </p>
                                    </div>
                                    <div>
                                      <p className="text-xs text-gray-500">Pernapasan</p>
                                      <p className={`text-sm font-medium ${
                                        patient.vital_signs.respiratory_rate < 10 || patient.vital_signs.respiratory_rate > 30
                                          ? "text-red-600"
                                          : "text-gray-900"
                                      }`}>
                                        {patient.vital_signs.respiratory_rate} x/menit
                                      </p>
                                    </div>
                                    <div>
                                      <p className="text-xs text-gray-500">Suhu</p>
                                      <p className={`text-sm font-medium ${
                                        patient.vital_signs.temperature < 35 || patient.vital_signs.temperature > 40
                                          ? "text-red-600"
                                          : "text-gray-900"
                                      }`}>
                                        {patient.vital_signs.temperature}°C
                                      </p>
                                    </div>
                                    <div>
                                      <p className="text-xs text-gray-500">SpO2</p>
                                      <p className={`text-sm font-medium ${
                                        patient.vital_signs.oxygen_saturation < 90
                                          ? "text-red-600"
                                          : "text-gray-900"
                                      }`}>
                                        {patient.vital_signs.oxygen_saturation}%
                                      </p>
                                    </div>
                                    <div>
                                      <p className="text-xs text-gray-500">Skor Nyeri</p>
                                      <p className={`text-sm font-medium ${
                                        patient.vital_signs.pain_score >= 7
                                          ? "text-red-600"
                                          : patient.vital_signs.pain_score >= 4
                                          ? "text-yellow-600"
                                          : "text-gray-900"
                                      }`}>
                                        {patient.vital_signs.pain_score}/10
                                      </p>
                                    </div>
                                    <div>
                                      <p className="text-xs text-gray-500">Kesadaran</p>
                                      <div className="flex items-center space-x-2">
                                        {getConsciousnessBadge(patient.vital_signs.consciousness_level)}
                                        {patient.vital_signs.glasgow_coma_scale && (
                                          <span className="text-sm text-gray-600">
                                            (GCS: {patient.vital_signs.glasgow_coma_scale})
                                          </span>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                </div>

                                {/* Allergies and Conditions */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  {patient.allergies && patient.allergies.length > 0 && (
                                    <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                                      <h4 className="text-sm font-medium text-red-900 mb-2">Alergi</h4>
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
                                    <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                                      <h4 className="text-sm font-medium text-yellow-900 mb-2">Kondisi Kronis</h4>
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

                                {/* Notes */}
                                {patient.notes && (
                                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                                    <h4 className="text-sm font-medium text-blue-900 mb-2">Catatan</h4>
                                    <p className="text-sm text-blue-800">{patient.notes}</p>
                                  </div>
                                )}

                                {/* Actions */}
                                <div className="flex flex-wrap gap-2 pt-4 border-t">
                                  {patient.status === "waiting" && (
                                    <>
                                      <button
                                        onClick={() => handleUpdateStatus(patient.id, "in_progress")}
                                        className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                                      >
                                        Mulai Penanganan
                                      </button>
                                      <button
                                        onClick={() => router.push(`/app/emergency/${patient.id}/examine`)}
                                        className="px-3 py-1 bg-purple-600 text-white text-sm rounded hover:bg-purple-700"
                                      >
                                        Pemeriksaan
                                      </button>
                                    </>
                                  )}
                                  {patient.status === "in_progress" && (
                                    <>
                                      <button
                                        onClick={() => router.push(`/app/emergency/${patient.id}/admit`)}
                                        className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                                      >
                                        Rawat Inap
                                      </button>
                                      <button
                                        onClick={() => handleUpdateStatus(patient.id, "admitted")}
                                        className="px-3 py-1 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700"
                                      >
                                        Pindahkan
                                      </button>
                                      <button
                                        onClick={() => router.push(`/app/emergency/${patient.id}/discharge`)}
                                        className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
                                      >
                                        Pulangkan
                                      </button>
                                    </>
                                  )}
                                  <button
                                    onClick={() => handleReTriage(patient.id)}
                                    className="px-3 py-1 bg-orange-600 text-white text-sm rounded hover:bg-orange-700"
                                  >
                                    Re-Triage
                                  </button>
                                  <button
                                    onClick={() => router.push(`/app/emergency/${patient.id}/print`)}
                                    className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
                                  >
                                    Cetak
                                  </button>
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
