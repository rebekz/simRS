"use client";

/**
 * Staff Laboratory Results Page - STORY-007: Laboratory Results Management
 *
 * Comprehensive laboratory results management for medical staff including:
 * - View all lab results with filters and search
 * - Filter by patient, test type, status, date range
 * - View detailed lab results with reference ranges
 * - Identify abnormal and critical values
 * - Access patient lab history
 * - Monitor pending lab orders
 * - Track lab specimen status
 * - Print and export lab results
 * - Critical value alerts and acknowledgments
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  TestTube,
  Plus,
  Search,
  Filter,
  Calendar,
  User,
  FileText,
  CheckCircle,
  Clock,
  AlertTriangle,
  AlertCircle,
  Eye,
  Download,
  Printer,
  ChevronDown,
  ChevronUp,
  TrendingUp,
  TrendingDown,
  Activity,
} from "lucide-react";

// Types
interface LabResult {
  id: number;
  patient_id: number;
  patient_name: string;
  medical_record_number: string;
  encounter_id?: number;
  order_id: number;
  order_number: string;
  test_type: string;
  test_category: "hematology" | "chemistry" | "immunology" | "microbiology" | "urinalysis" | "parasitology" | "serology" | "coagulation";
  specimen_type: string;
  collection_date: string;
  collection_time?: string;
  received_date?: string;
  tested_date?: string;
  verified_date?: string;
  status: "pending" | "in_progress" | "completed" | "verified" | "cancelled";
  priority: "routine" | "urgent" | "stat";
  ordered_by: string;
  performed_by?: string;
  verified_by?: string;
  notes?: string;
  results: LabResultItem[];
  critical_values?: CriticalValue[];
}

interface LabResultItem {
  id: number;
  test_name: string;
  result_value: string;
  unit: string;
  reference_range: string;
  flag: "normal" | "high" | "low" | "critical" | "abnormal";
  notes?: string;
  perform_date?: string;
}

interface CriticalValue {
  id: number;
  test_name: string;
  value: string;
  critical_range: string;
  acknowledged: boolean;
  acknowledged_by?: string;
  acknowledged_at?: string;
  notified_physician: boolean;
  notified_at?: string;
}

interface LabStats {
  total_today: number;
  pending: number;
  in_progress: number;
  completed: number;
  critical: number;
}

type StatusFilter = "all" | "pending" | "in_progress" | "completed" | "verified" | "cancelled";
type CategoryFilter = "all" | "hematology" | "chemistry" | "immunology" | "microbiology" | "urinalysis" | "parasitology" | "serology" | "coagulation";
type PriorityFilter = "all" | "routine" | "urgent" | "stat";

export default function StaffLabResultsPage() {
  const router = useRouter();
  const [labResults, setLabResults] = useState<LabResult[]>([]);
  const [stats, setStats] = useState<LabStats | null>(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>("all");
  const [priorityFilter, setPriorityFilter] = useState<PriorityFilter>("all");
  const [dateFilter, setDateFilter] = useState<string>("today");
  const [searchQuery, setSearchQuery] = useState("");

  // UI state
  const [selectedResult, setSelectedResult] = useState<LabResult | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [expandedResult, setExpandedResult] = useState<number | null>(null);

  useEffect(() => {
    fetchLabResults();
  }, [statusFilter, categoryFilter, priorityFilter, dateFilter]);

  const fetchLabResults = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const params = new URLSearchParams();
      if (statusFilter !== "all") params.append("status", statusFilter);
      if (categoryFilter !== "all") params.append("test_category", categoryFilter);
      if (priorityFilter !== "all") params.append("priority", priorityFilter);
      if (dateFilter !== "all") params.append("date_filter", dateFilter);
      if (searchQuery) params.append("search", searchQuery);

      const response = await fetch(`/api/v1/lab/results?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setLabResults(data.items || []);
        setStats(data.stats || null);
      } else {
        console.error("Failed to fetch lab results");
      }
    } catch (error) {
      console.error("Failed to fetch lab results:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledgeCritical = async (resultId: number, criticalValueId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(
        `/api/v1/lab/results/${resultId}/critical-values/${criticalValueId}/acknowledge`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        fetchLabResults();
        alert("Nilai kritis diakui");
      } else {
        alert("Gagal mengakui nilai kritis");
      }
    } catch (error) {
      console.error("Failed to acknowledge critical value:", error);
      alert("Gagal mengakui nilai kritis");
    }
  };

  const handleVerifyResult = async (resultId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/lab/results/${resultId}/verify`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        fetchLabResults();
        alert("Hasil lab berhasil diverifikasi");
      } else {
        alert("Gagal memverifikasi hasil lab");
      }
    } catch (error) {
      console.error("Failed to verify lab result:", error);
      alert("Gagal memverifikasi hasil lab");
    }
  };

  const handlePrintResult = async (resultId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/lab/results/${resultId}/print`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const printWindow = window.open(url);
        if (printWindow) {
          printWindow.onload = () => {
            printWindow.print();
            window.URL.revokeObjectURL(url);
          };
        }
      } else {
        alert("Gagal mencetak hasil lab");
      }
    } catch (error) {
      console.error("Failed to print lab result:", error);
      alert("Gagal mencetak hasil lab");
    }
  };

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      hematology: "Hematologi",
      chemistry: "Kimia Klinik",
      immunology: "Imunologi",
      microbiology: "Mikrobiologi",
      urinalysis: "Urin Analisa",
      parasitology: "Parasitologi",
      serology: "Serologi",
      coagulation: "Koagulasi",
    };
    return labels[category] || category;
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      hematology: "bg-purple-100 text-purple-800",
      chemistry: "bg-blue-100 text-blue-800",
      immunology: "bg-green-100 text-green-800",
      microbiology: "bg-orange-100 text-orange-800",
      urinalysis: "bg-yellow-100 text-yellow-800",
      parasitology: "bg-teal-100 text-teal-800",
      serology: "bg-indigo-100 text-indigo-800",
      coagulation: "bg-pink-100 text-pink-800",
    };
    return colors[category] || "bg-gray-100 text-gray-800";
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      pending: "Menunggu",
      in_progress: "Diproses",
      completed: "Selesai",
      verified: "Terverifikasi",
      cancelled: "Dibatalkan",
    };
    return labels[status] || status;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: "bg-yellow-100 text-yellow-800",
      in_progress: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      verified: "bg-emerald-100 text-emerald-800",
      cancelled: "bg-red-100 text-red-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const getStatusIcon = (status: string) => {
    const icons: Record<string, React.ReactNode> = {
      pending: <Clock className="w-4 h-4" />,
      in_progress: <Activity className="w-4 h-4" />,
      completed: <CheckCircle className="w-4 h-4" />,
      verified: <CheckCircle className="w-4 h-4" />,
      cancelled: <AlertCircle className="w-4 h-4" />,
    };
    return icons[status] || <Clock className="w-4 h-4" />;
  };

  const getPriorityLabel = (priority: string) => {
    const labels: Record<string, string> = {
      routine: "Biasa",
      urgent: "Urgent",
      stat: "STAT",
    };
    return labels[priority] || priority;
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      routine: "bg-gray-100 text-gray-800",
      urgent: "bg-orange-100 text-orange-800",
      stat: "bg-red-100 text-red-800",
    };
    return colors[priority] || "bg-gray-100 text-gray-800";
  };

  const getFlagIcon = (flag: string) => {
    if (flag === "critical") {
      return <AlertTriangle className="w-4 h-4 text-red-600" />;
    }
    if (flag === "high") {
      return <TrendingUp className="w-4 h-4 text-orange-600" />;
    }
    if (flag === "low") {
      return <TrendingDown className="w-4 h-4 text-blue-600" />;
    }
    return null;
  };

  const getFlagColor = (flag: string) => {
    const colors: Record<string, string> = {
      normal: "bg-gray-100 text-gray-800",
      high: "bg-orange-100 text-orange-800",
      low: "bg-blue-100 text-blue-800",
      critical: "bg-red-100 text-red-800",
      abnormal: "bg-yellow-100 text-yellow-800",
    };
    return colors[flag] || "bg-gray-100 text-gray-800";
  };

  const getFlagLabel = (flag: string) => {
    const labels: Record<string, string> = {
      normal: "Normal",
      high: "Tinggi",
      low: "Rendah",
      critical: "Kritis",
      abnormal: "Abnormal",
    };
    return labels[flag] || flag;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (date.toDateString() === today.toDateString()) {
      return "Hari Ini";
    }

    return date.toLocaleDateString("id-ID", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("id-ID", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const filteredResults = labResults.filter((result) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        result.patient_name.toLowerCase().includes(query) ||
        result.medical_record_number.toLowerCase().includes(query) ||
        result.order_number.toLowerCase().includes(query) ||
        result.test_type.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const handleSearch = () => {
    fetchLabResults();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Hasil Laboratorium</h1>
          <p className="text-sm text-gray-600 mt-1">Kelola hasil pemeriksaan laboratorium</p>
        </div>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Hari Ini</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_today}</p>
              </div>
              <Calendar className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Menunggu</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
              </div>
              <Clock className="w-8 h-8 text-yellow-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Diproses</p>
                <p className="text-2xl font-bold text-blue-600">{stats.in_progress}</p>
              </div>
              <Activity className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Selesai</p>
                <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Nilai Kritis</p>
                <p className="text-2xl font-bold text-red-600">{stats.critical}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-64">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Cari pasien, nomor order, atau tes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter") handleSearch();
              }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Semua Status</option>
            <option value="pending">Menunggu</option>
            <option value="in_progress">Diproses</option>
            <option value="completed">Selesai</option>
            <option value="verified">Terverifikasi</option>
            <option value="cancelled">Dibatalkan</option>
          </select>

          {/* Category Filter */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value as CategoryFilter)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Semua Kategori</option>
            <option value="hematology">Hematologi</option>
            <option value="chemistry">Kimia Klinik</option>
            <option value="immunology">Imunologi</option>
            <option value="microbiology">Mikrobiologi</option>
            <option value="urinalysis">Urin Analisa</option>
            <option value="parasitology">Parasitologi</option>
            <option value="serology">Serologi</option>
            <option value="coagulation">Koagulasi</option>
          </select>

          {/* Priority Filter */}
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value as PriorityFilter)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Semua Prioritas</option>
            <option value="routine">Biasa</option>
            <option value="urgent">Urgent</option>
            <option value="stat">STAT</option>
          </select>

          {/* Date Filter */}
          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="today">Hari Ini</option>
            <option value="week">Minggu Ini</option>
            <option value="month">Bulan Ini</option>
            <option value="all">Semua Waktu</option>
          </select>
        </div>
      </div>

      {/* Lab Results List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredResults.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <TestTube className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada hasil lab</h3>
          <p className="text-gray-600">
            {searchQuery || statusFilter !== "all" || categoryFilter !== "all"
              ? "Tidak ada hasil lab yang sesuai dengan filter"
              : "Belum ada hasil pemeriksaan laboratorium"}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredResults.map((result) => {
            const isExpanded = expandedResult === result.id;
            const hasCriticalValues = result.critical_values && result.critical_values.length > 0;
            const hasAbnormalResults = result.results.some((r) => r.flag !== "normal");

            return (
              <div key={result.id} className="bg-white rounded-lg shadow overflow-hidden">
                {/* Summary Row */}
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getPriorityColor(
                            result.priority
                          )}`}
                        >
                          {getPriorityLabel(result.priority)}
                        </span>
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                            result.status
                          )}`}
                        >
                          {getStatusIcon(result.status)}
                          <span className="ml-1">{getStatusLabel(result.status)}</span>
                        </span>
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getCategoryColor(
                            result.test_category
                          )}`}
                        >
                          {getCategoryLabel(result.test_category)}
                        </span>
                        <span className="text-xs text-gray-500">{formatDate(result.collection_date)}</span>
                      </div>

                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          <FileText className="w-4 h-4 text-gray-400" />
                          <div>
                            <p className="font-medium text-gray-900">Order #{result.order_number}</p>
                            <p className="text-xs text-gray-500">{result.test_type}</p>
                          </div>
                        </div>

                        <div className="flex items-center space-x-2">
                          <User className="w-4 h-4 text-gray-400" />
                          <div>
                            <p className="font-medium text-gray-900">{result.patient_name}</p>
                            <p className="text-xs text-gray-500">{result.medical_record_number}</p>
                          </div>
                        </div>

                        <div className="text-sm text-gray-600">
                          <span className="font-medium">Spesimen:</span> {result.specimen_type}
                        </div>

                        <div className="text-sm text-gray-600">
                          <span className="font-medium">Dokter:</span> {result.ordered_by}
                        </div>

                        {hasCriticalValues && (
                          <div className="flex items-center space-x-1 text-red-600 animate-pulse">
                            <AlertTriangle className="w-4 h-4" />
                            <span className="text-xs font-medium">NILAI KRITIS</span>
                          </div>
                        )}

                        {hasAbnormalResults && !hasCriticalValues && (
                          <div className="flex items-center space-x-1 text-orange-600">
                            <AlertCircle className="w-4 h-4" />
                            <span className="text-xs font-medium">Hasil Abnormal</span>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center space-x-2 mt-2 text-xs text-gray-500">
                        {result.received_date && <span>Diterima: {formatDateTime(result.received_date)}</span>}
                        {result.tested_date && <span>Dites: {formatDateTime(result.tested_date)}</span>}
                        {result.verified_date && <span>Diverifikasi: {formatDateTime(result.verified_date)}</span>}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      {result.status === "completed" && (
                        <button
                          onClick={() => handleVerifyResult(result.id)}
                          className="p-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200"
                          title="Verifikasi"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                      )}

                      <button
                        onClick={() => {
                          setSelectedResult(result);
                          setShowDetailModal(true);
                        }}
                        className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                        title="Lihat Detail"
                      >
                        <Eye className="w-4 h-4" />
                      </button>

                      {(result.status === "completed" || result.status === "verified") && (
                        <button
                          onClick={() => handlePrintResult(result.id)}
                          className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                          title="Cetak"
                        >
                          <Printer className="w-4 h-4" />
                        </button>
                      )}

                      <button
                        onClick={() => setExpandedResult(isExpanded ? null : result.id)}
                        className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                        title="Expand"
                      >
                        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="border-t border-gray-200 p-4 bg-gray-50">
                    {/* Critical Values Alert */}
                    {hasCriticalValues && (
                      <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <div className="flex items-center space-x-2 mb-3">
                          <AlertTriangle className="w-5 h-5 text-red-600" />
                          <h4 className="text-sm font-semibold text-red-900">NILAI KRITIS - Membutuhkan Perhatian Segera!</h4>
                        </div>
                        <div className="space-y-2">
                          {result.critical_values?.map((cv) => (
                            <div key={cv.id} className="flex items-center justify-between text-sm">
                              <div>
                                <span className="font-medium text-red-900">{cv.test_name}:</span>{" "}
                                <span className="text-red-700 font-bold">{cv.value}</span>
                                <span className="text-red-600 ml-2">(Kritis: {cv.critical_range})</span>
                              </div>
                              {!cv.acknowledged && (
                                <button
                                  onClick={() => handleAcknowledgeCritical(result.id, cv.id)}
                                  className="px-3 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700"
                                >
                                  Akui
                                </button>
                              )}
                              {cv.acknowledged && (
                                <span className="text-xs text-green-700">
                                  ✓ Diakui oleh {cv.acknowledged_by}
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Lab Results */}
                    <h4 className="text-sm font-semibold text-gray-900 mb-3">Hasil Pemeriksaan</h4>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-100">
                          <tr>
                            <th className="px-4 py-2 text-left font-medium text-gray-700">Pemeriksaan</th>
                            <th className="px-4 py-2 text-left font-medium text-gray-700">Hasil</th>
                            <th className="px-4 py-2 text-left font-medium text-gray-700">Nilai Rujukan</th>
                            <th className="px-4 py-2 text-left font-medium text-gray-700">Flag</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {result.results.map((item) => (
                            <tr key={item.id} className={item.flag === "critical" ? "bg-red-50" : ""}>
                              <td className="px-4 py-3">
                                <p className="font-medium text-gray-900">{item.test_name}</p>
                              </td>
                              <td className="px-4 py-3">
                                <span className="font-semibold text-gray-900">{item.result_value}</span>{" "}
                                <span className="text-gray-500">{item.unit}</span>
                              </td>
                              <td className="px-4 py-3 text-gray-600">{item.reference_range}</td>
                              <td className="px-4 py-3">
                                <div className="flex items-center space-x-2">
                                  {getFlagIcon(item.flag)}
                                  <span
                                    className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getFlagColor(
                                      item.flag
                                    )}`}
                                  >
                                    {getFlagLabel(item.flag)}
                                  </span>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {result.notes && (
                      <div className="mt-4 p-3 bg-white rounded-lg border border-gray-200">
                        <p className="text-sm">
                          <span className="font-medium text-gray-900">Catatan:</span> {result.notes}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
