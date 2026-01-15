"use client";

import { useState, useMemo } from "react";
import {
  FileText,
  Download,
  Calendar,
  CheckCircle,
  XCircle,
  Clock,
  Activity,
  TrendingUp,
  TrendingDown,
  Filter,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";

/**
 * WEB-S-2.5: BPJS History & Audit
 *
 * Key Features:
 * - BPJS eligibility check log (timestamp, action, success/failure)
 * - SEP creation history by patient
 * - API call success/failure statistics
 * - Export to CSV (admin only)
 * - Date range filtering
 * - Detailed audit logs for troubleshooting
 */

// ============================================================================
// TYPES
// ============================================================================

type BPJSAction = "ELIGIBILITY_CHECK" | "SEP_CREATE" | "SEP_UPDATE" | "SEP_CANCEL";

type BPJSLogStatus = "success" | "failed";

interface BPJSLogEntry {
  id: string;
  timestamp: string;
  action: BPJSAction;
  status: BPJSLogStatus;
  bpjsNumber?: string;
  patientName?: string;
  sepNumber?: string;
  errorMessage?: string;
  responseTime: number; // milliseconds
}

interface BPJSStatistics {
  totalCalls: number;
  successCalls: number;
  failedCalls: number;
  successRate: string;
  avgResponseTime: string;
  todayCalls: number;
  todaySuccess: number;
  todayFailed: number;
}

// ============================================================================
// MOCK DATA
// ============================================================================

const MOCK_BPJS_LOGS: BPJSLogEntry[] = [
  // Recent successful eligibility checks
  {
    id: "1",
    timestamp: "2026-01-16 14:35:22",
    action: "ELIGIBILITY_CHECK",
    status: "success",
    bpjsNumber: "1234567890123",
    patientName: "AHMAD SUSANTO",
    responseTime: 450,
  },
  {
    id: "2",
    timestamp: "2026-01-16 14:30:15",
    action: "ELIGIBILITY_CHECK",
    status: "success",
    bpjsNumber: "9876543210987",
    patientName: "SITI RAHAYU",
    responseTime: 520,
  },
  {
    id: "3",
    timestamp: "2026-01-16 14:25:43",
    action: "SEP_CREATE",
    status: "success",
    bpjsNumber: "1234567890123",
    patientName: "AHMAD SUSANTO",
    sepNumber: "0001R00110160001",
    responseTime: 780,
  },
  {
    id: "4",
    timestamp: "2026-01-16 14:20:18",
    action: "ELIGIBILITY_CHECK",
    status: "failed",
    bpjsNumber: "1111111111111",
    patientName: "BUDI SANTOSO",
    errorMessage: "Kartu BPJS tidak ditemukan atau kadaluarsa",
    responseTime: 380,
  },
  {
    id: "5",
    timestamp: "2026-01-16 14:15:55",
    action: "ELIGIBILITY_CHECK",
    status: "success",
    bpjsNumber: "2222222222222",
    patientName: "DEWI LESTARI",
    responseTime: 490,
  },
  {
    id: "6",
    timestamp: "2026-01-16 14:10:32",
    action: "SEP_CREATE",
    status: "success",
    bpjsNumber: "9876543210987",
    patientName: "SITI RAHAYU",
    sepNumber: "0001R00210160002",
    responseTime: 820,
  },
  {
    id: "7",
    timestamp: "2026-01-16 14:05:14",
    action: "ELIGIBILITY_CHECK",
    status: "success",
    bpjsNumber: "3333333333333",
    patientName: "EKO PRASETYO",
    responseTime: 410,
  },
  {
    id: "8",
    timestamp: "2026-01-16 14:00:47",
    action: "SEP_CREATE",
    status: "failed",
    bpjsNumber: "1111111111111",
    patientName: "BUDI SANTOSO",
    errorMessage: "Pasien tidak eligible untuk pelayanan saat ini",
    responseTime: 650,
  },
  // Yesterday's logs
  {
    id: "9",
    timestamp: "2026-01-15 16:45:33",
    action: "ELIGIBILITY_CHECK",
    status: "success",
    bpjsNumber: "4444444444444",
    patientName: "RINA WATI",
    responseTime: 530,
  },
  {
    id: "10",
    timestamp: "2026-01-15 16:30:21",
    action: "SEP_CREATE",
    status: "success",
    bpjsNumber: "4444444444444",
    patientName: "RINA WATI",
    sepNumber: "0001R00310150101",
    responseTime: 910,
  },
  {
    id: "11",
    timestamp: "2026-01-15 16:15:18",
    action: "ELIGIBILITY_CHECK",
    status: "failed",
    bpjsNumber: "5555555555555",
    patientName: "AGUS SETIAWAN",
    errorMessage: "Koneksi BPJS timeout",
    responseTime: 5000,
  },
  {
    id: "12",
    timestamp: "2026-01-15 16:00:42",
    action: "ELIGIBILITY_CHECK",
    status: "success",
    bpjsNumber: "6666666666666",
    patientName: "LILIS SURYANI",
    responseTime: 460,
  },
  {
    id: "13",
    timestamp: "2026-01-15 15:45:29",
    action: "SEP_UPDATE",
    status: "success",
    bpjsNumber: "1234567890123",
    patientName: "AHMAD SUSANTO",
    sepNumber: "0001R00110160001",
    responseTime: 720,
  },
  {
    id: "14",
    timestamp: "2026-01-15 15:30:15",
    action: "ELIGIBILITY_CHECK",
    status: "success",
    bpjsNumber: "7777777777777",
    patientName: "DEDI KURNIAWAN",
    responseTime: 540,
  },
  {
    id: "15",
    timestamp: "2026-01-15 15:15:38",
    action: "ELIGIBILITY_CHECK",
    status: "success",
    bpjsNumber: "8888888888888",
    patientName: "YULIATI",
    responseTime: 390,
  },
  // More logs for statistics
  {
    id: "16",
    timestamp: "2026-01-15 14:45:22",
    action: "ELIGIBILITY_CHECK",
    status: "failed",
    bpjsNumber: "9999999999999",
    patientName: "HENDRO W",
    errorMessage: "Format nomor kartu tidak valid",
    responseTime: 250,
  },
  {
    id: "17",
    timestamp: "2026-01-15 14:30:45",
    action: "ELIGIBILITY_CHECK",
    status: "success",
    bpjsNumber: "1010101010101",
    patientName: "SUSILO",
    responseTime: 480,
  },
  {
    id: "18",
    timestamp: "2026-01-15 14:15:18",
    action: "SEP_CREATE",
    status: "success",
    bpjsNumber: "7777777777777",
    patientName: "DEDI KURNIAWAN",
    sepNumber: "0001R00410150102",
    responseTime: 850,
  },
  {
    id: "19",
    timestamp: "2026-01-15 14:00:33",
    action: "ELIGIBILITY_CHECK",
    status: "success",
    bpjsNumber: "2020202020202",
    patientName: "SRI REJEKI",
    responseTime: 510,
  },
  {
    id: "20",
    timestamp: "2026-01-15 13:45:27",
    action: "ELIGIBILITY_CHECK",
    status: "success",
    bpjsNumber: "3030303030303",
    patientName: "JUMADI",
    responseTime: 430,
  },
];

// ============================================================================
// COMPONENTS
// ============================================================================

/**
 * Action Badge Component
 */
function ActionBadge({ action }: { action: BPJSAction }) {
  const getActionConfig = () => {
    switch (action) {
      case "ELIGIBILITY_CHECK":
        return {
          label: "Eligibility Check",
          bgClass: "bg-blue-100",
          textClass: "text-blue-700",
          borderClass: "border-blue-300",
        };
      case "SEP_CREATE":
        return {
          label: "Buat SEP",
          bgClass: "bg-green-100",
          textClass: "text-green-700",
          borderClass: "border-green-300",
        };
      case "SEP_UPDATE":
        return {
          label: "Update SEP",
          bgClass: "bg-purple-100",
          textClass: "text-purple-700",
          borderClass: "border-purple-300",
        };
      case "SEP_CANCEL":
        return {
          label: "Batal SEP",
          bgClass: "bg-red-100",
          textClass: "text-red-700",
          borderClass: "border-red-300",
        };
    }
  };

  const config = getActionConfig();

  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full border-2 text-xs font-medium ${config.bgClass} ${config.textClass} ${config.borderClass}`}
    >
      {config.label}
    </span>
  );
}

/**
 * Status Badge Component
 */
function StatusBadge({ status }: { status: BPJSLogStatus }) {
  if (status === "success") {
    return (
      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full border-2 text-xs font-medium bg-green-100 text-green-700 border-green-300">
        <CheckCircle className="w-3 h-3" />
        Sukses
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full border-2 text-xs font-medium bg-red-100 text-red-700 border-red-300">
      <XCircle className="w-3 h-3" />
      Gagal
    </span>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function BPJSHistoryPage() {
  const [logs, setLogs] = useState<BPJSLogEntry[]>(MOCK_BPJS_LOGS);
  const [selectedAction, setSelectedAction] = useState<BPJSAction | "all">("all");
  const [selectedStatus, setSelectedStatus] = useState<BPJSLogStatus | "all">("all");
  const [sortField, setSortField] = useState<"timestamp" | "responseTime">("timestamp");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const [isAdmin] = useState(true); // Mock admin check

  /**
   * Calculate statistics from logs
   */
  const statistics = useMemo((): BPJSStatistics => {
    const total = logs.length;
    const success = logs.filter((l) => l.status === "success").length;
    const failed = logs.filter((l) => l.status === "failed").length;
    const avgResponse = Math.round(
      logs.reduce((sum, log) => sum + log.responseTime, 0) / total
    );

    // Today's stats
    const todayLogs = logs.filter((l) => l.timestamp.startsWith("2026-01-16"));
    const todayTotal = todayLogs.length;
    const todaySuccess = todayLogs.filter((l) => l.status === "success").length;
    const todayFailed = todayLogs.filter((l) => l.status === "failed").length;

    return {
      totalCalls: total,
      successCalls: success,
      failedCalls: failed,
      successRate: ((success / total) * 100).toFixed(1) + "%",
      avgResponseTime: avgResponse + "ms",
      todayCalls: todayTotal,
      todaySuccess: todaySuccess,
      todayFailed: todayFailed,
    };
  }, [logs]);

  /**
   * Filter and sort logs
   */
  const filteredLogs = useMemo(() => {
    let filtered = [...logs];

    // Filter by action
    if (selectedAction !== "all") {
      filtered = filtered.filter((l) => l.action === selectedAction);
    }

    // Filter by status
    if (selectedStatus !== "all") {
      filtered = filtered.filter((l) => l.status === selectedStatus);
    }

    // Sort
    filtered.sort((a, b) => {
      let comparison = 0;

      if (sortField === "timestamp") {
        comparison = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
      } else if (sortField === "responseTime") {
        comparison = a.responseTime - b.responseTime;
      }

      return sortDirection === "asc" ? comparison : -comparison;
    });

    return filtered;
  }, [logs, selectedAction, selectedStatus, sortField, sortDirection]);

  /**
   * Handle sort toggle
   */
  const handleSort = (field: "timestamp" | "responseTime") => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  /**
   * Export to CSV
   */
  const handleExportCSV = () => {
    if (!isAdmin) {
      alert("Akses ditolak. Halaman ini hanya untuk administrator.");
      return;
    }

    // Create CSV content
    const headers = ["Timestamp", "Action", "Status", "BPJS Number", "Patient Name", "SEP Number", "Error Message", "Response Time (ms)"];
    const csvContent = [
      headers.join(","),
      ...filteredLogs.map((log) =>
        [
          log.timestamp,
          log.action,
          log.status,
          log.bpjsNumber || "",
          log.patientName || "",
          log.sepNumber || "",
          log.errorMessage || "",
          log.responseTime,
        ].join(",")
      ),
    ].join("\n");

    // Create download link
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `bpjs-history-${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">BPJS History & Audit</h1>
                <p className="text-sm text-gray-600">Riwayat interaksi API BPJS dan statistik</p>
              </div>
            </div>

            <button
              type="button"
              onClick={handleExportCSV}
              disabled={!isAdmin}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm font-medium"
              title={!isAdmin ? "Akses ditolak. Hanya untuk administrator." : "Export ke CSV"}
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {/* Success Rate */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-600">Success Rate</p>
                <p className="text-3xl font-bold text-green-600">{statistics.successRate}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                {parseFloat(statistics.successRate) >= 90 ? (
                  <TrendingUp className="w-6 h-6 text-green-600" />
                ) : (
                  <TrendingDown className="w-6 h-6 text-yellow-600" />
                )}
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Activity className="w-4 h-4" />
              <span>{statistics.successCalls} sukses dari {statistics.totalCalls} total</span>
            </div>
          </div>

          {/* Total Calls */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-600">Total Calls</p>
                <p className="text-3xl font-bold text-blue-600">{statistics.totalCalls}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Calendar className="w-4 h-4" />
              <span>Hari ini: {statistics.todayCalls} calls</span>
            </div>
          </div>

          {/* Failed Calls */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-600">Failed Calls</p>
                <p className="text-3xl font-bold text-red-600">{statistics.failedCalls}</p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <XCircle className="w-6 h-6 text-red-600" />
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Calendar className="w-4 h-4" />
              <span>Hari ini: {statistics.todayFailed} gagal</span>
            </div>
          </div>

          {/* Avg Response Time */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-600">Avg Response</p>
                <p className="text-3xl font-bold text-purple-600">{statistics.avgResponseTime}</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Activity className="w-4 h-4" />
              <span>Target: &lt;1000ms</span>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-600" />
              <span className="font-medium text-gray-700">Filter:</span>
            </div>

            <div className="flex-1 flex gap-4">
              {/* Action Filter */}
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Aksi
                </label>
                <select
                  value={selectedAction}
                  onChange={(e) => setSelectedAction(e.target.value as BPJSAction | "all")}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                >
                  <option value="all">Semua Aksi</option>
                  <option value="ELIGIBILITY_CHECK">Eligibility Check</option>
                  <option value="SEP_CREATE">Buat SEP</option>
                  <option value="SEP_UPDATE">Update SEP</option>
                  <option value="SEP_CANCEL">Batal SEP</option>
                </select>
              </div>

              {/* Status Filter */}
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value as BPJSLogStatus | "all")}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                >
                  <option value="all">Semua Status</option>
                  <option value="success">Sukses</option>
                  <option value="failed">Gagal</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Logs Table */}
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">Riwayat API BPJS</h2>
            <span className="text-sm text-blue-100">
              Menampilkan {filteredLogs.length} dari {logs.length} entri
            </span>
          </div>

          {filteredLogs.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">Tidak ada riwayat</p>
              <p className="text-sm">Tidak ditemukan data yang sesuai dengan filter</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Timestamp
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Aksi
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      No. BPJS
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Pasien
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      No. SEP
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Error / Response
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                        onClick={() => handleSort("responseTime")}>
                      <div className="flex items-center gap-1">
                        Response Time
                        {sortField === "responseTime" && (
                          sortDirection === "asc" ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                        )}
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {log.timestamp}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <ActionBadge action={log.action} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={log.status} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">
                        {log.bpjsNumber || "-"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {log.patientName || "-"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">
                        {log.sepNumber || "-"}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-md">
                        {log.errorMessage ? (
                          <span className="text-red-600">{log.errorMessage}</span>
                        ) : (
                          <span className="text-green-600">OK</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span
                          className={`font-medium ${
                            log.responseTime < 500
                              ? "text-green-600"
                              : log.responseTime < 1000
                              ? "text-yellow-600"
                              : "text-red-600"
                          }`}
                        >
                          {log.responseTime}ms
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Footer Info */}
        <div className="mt-6 text-sm text-gray-600">
          <p>
            <strong>Info:</strong> Halaman ini menampilkan riwayat semua panggilan API BPJS untuk keperluan audit dan troubleshooting.
            Data di-refresh secara real-time dari sistem.
          </p>
        </div>
      </div>
    </div>
  );
}
