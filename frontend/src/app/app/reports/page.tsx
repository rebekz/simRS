"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface ReportSummary {
  report_type: string;
  report_name: string;
  category: "operational" | "clinical" | "financial" | "administrative";
  description: string;
  last_generated?: string;
  is_scheduled: boolean;
  schedule_frequency?: "daily" | "weekly" | "monthly" | "quarterly" | "yearly";
}

interface ReportData {
  period: string;
  total_patients: number;
  new_patients: number;
  returning_patients: number;
  total_visits: number;
  outpatient_visits: number;
  inpatient_visits: number;
  emergency_visits: number;
  total_revenue: number;
  total_expenses: number;
  net_profit: number;
  pending_claims: number;
  approved_claims: number;
  rejected_claims: number;
  top_diagnoses: DiagnosisCount[];
  top_procedures: ProcedureCount[];
  department_stats: DepartmentStat[];
}

interface DiagnosisCount {
  diagnosis_code: string;
  diagnosis_name: string;
  count: number;
  percentage: number;
}

interface ProcedureCount {
  procedure_code: string;
  procedure_name: string;
  count: number;
  percentage: number;
}

interface DepartmentStat {
  department_name: string;
  patient_count: number;
  revenue: number;
  avg_patient_rating?: number;
}

export default function ReportsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"dashboard" | "operational" | "clinical" | "financial" | "administrative">("dashboard");
  const [selectedPeriod, setSelectedPeriod] = useState<"today" | "week" | "month" | "quarter" | "year">("month");
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [availableReports, setAvailableReports] = useState<ReportSummary[]>([]);

  useEffect(() => {
    checkAuth();
    fetchReportData();
    fetchAvailableReports();
  }, [selectedPeriod]);

  const checkAuth = () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
    }
  };

  const fetchReportData = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/reports/summary?period=${selectedPeriod}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch report data");
      }

      const data = await response.json();
      setReportData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load reports");
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableReports = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/reports/available", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAvailableReports(data.reports || []);
      }
    } catch (err) {
      console.error("Failed to fetch available reports:", err);
    }
  };

  const handleGenerateReport = async (reportType: string) => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/reports/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          report_type: reportType,
          period: selectedPeriod,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate report");
      }

      const data = await response.json();
      alert(`Laporan "${data.report_name}" berhasil dibuat`);
      fetchReportData();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to generate report");
    }
  };

  const handleExportReport = async (reportType: string, format: "pdf" | "excel" | "csv") => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/reports/export`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          report_type: reportType,
          period: selectedPeriod,
          format,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to export report");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report-${reportType}-${selectedPeriod}.${format === "excel" ? "xlsx" : format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to export report");
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

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      operational: "blue",
      clinical: "green",
      financial: "purple",
      administrative: "orange",
    };
    return colors[category] || "gray";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Laporan & Analitik</h1>
          <p className="text-gray-600 mt-1">Dashboard laporan operasional, klinis, dan keuangan</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value as any)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="today">Hari Ini</option>
            <option value="week">Minggu Ini</option>
            <option value="month">Bulan Ini</option>
            <option value="quarter">Kuartal Ini</option>
            <option value="year">Tahun Ini</option>
          </select>
          <button
            onClick={() => router.push("/app/reports/custom")}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>Laporan Kustom</span>
          </button>
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

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px overflow-x-auto">
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`px-6 py-4 text-sm font-medium whitespace-nowrap ${
                activeTab === "dashboard"
                  ? "border-b-2 border-indigo-500 text-indigo-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab("operational")}
              className={`px-6 py-4 text-sm font-medium whitespace-nowrap ${
                activeTab === "operational"
                  ? "border-b-2 border-indigo-500 text-indigo-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Operasional
            </button>
            <button
              onClick={() => setActiveTab("clinical")}
              className={`px-6 py-4 text-sm font-medium whitespace-nowrap ${
                activeTab === "clinical"
                  ? "border-b-2 border-indigo-500 text-indigo-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Klinis
            </button>
            <button
              onClick={() => setActiveTab("financial")}
              className={`px-6 py-4 text-sm font-medium whitespace-nowrap ${
                activeTab === "financial"
                  ? "border-b-2 border-indigo-500 text-indigo-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Keuangan
            </button>
            <button
              onClick={() => setActiveTab("administrative")}
              className={`px-6 py-4 text-sm font-medium whitespace-nowrap ${
                activeTab === "administrative"
                  ? "border-b-2 border-indigo-500 text-indigo-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Administratif
            </button>
          </nav>
        </div>

        {/* Dashboard Tab */}
        {activeTab === "dashboard" && reportData && (
          <div className="p-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100 text-sm">Total Pasien</p>
                    <p className="text-3xl font-bold mt-1">{formatNumber(reportData.total_patients)}</p>
                    <p className="text-blue-100 text-xs mt-2">
                      +{formatNumber(reportData.new_patients)} baru
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
                    <span className="text-2xl">👥</span>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100 text-sm">Total Kunjungan</p>
                    <p className="text-3xl font-bold mt-1">{formatNumber(reportData.total_visits)}</p>
                    <p className="text-green-100 text-xs mt-2">
                      {formatNumber(reportData.outpatient_visits)} rawat jalan
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
                    <span className="text-2xl">🏥</span>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100 text-sm">Pendapatan</p>
                    <p className="text-2xl font-bold mt-1">{formatCurrency(reportData.total_revenue)}</p>
                    <p className="text-green-200 text-xs mt-2">
                      Profit: {formatCurrency(reportData.net_profit)}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
                    <span className="text-2xl">💰</span>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-6 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-orange-100 text-sm">Klaim BPJS</p>
                    <p className="text-3xl font-bold mt-1">{formatNumber(reportData.approved_claims)}</p>
                    <p className="text-orange-100 text-xs mt-2">
                      {formatNumber(reportData.pending_claims)} pending
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
                    <span className="text-2xl">🏛️</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Visit Distribution */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribusi Kunjungan</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Rawat Jalan</span>
                      <span className="font-medium">{formatNumber(reportData.outpatient_visits)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${(reportData.outpatient_visits / reportData.total_visits) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Rawat Inap</span>
                      <span className="font-medium">{formatNumber(reportData.inpatient_visits)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${(reportData.inpatient_visits / reportData.total_visits) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">IGD</span>
                      <span className="font-medium">{formatNumber(reportData.emergency_visits)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-red-500 h-2 rounded-full"
                        style={{ width: `${(reportData.emergency_visits / reportData.total_visits) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* BPJS Claims Status */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Status Klaim BPJS</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Disetujui</span>
                      <span className="font-medium text-green-600">{formatNumber(reportData.approved_claims)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{
                          width: `${(reportData.approved_claims / (reportData.pending_claims + reportData.approved_claims + reportData.rejected_claims)) * 100}%`
                        }}
                      ></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Pending</span>
                      <span className="font-medium text-yellow-600">{formatNumber(reportData.pending_claims)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-yellow-500 h-2 rounded-full"
                        style={{
                          width: `${(reportData.pending_claims / (reportData.pending_claims + reportData.approved_claims + reportData.rejected_claims)) * 100}%`
                        }}
                      ></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Ditolak</span>
                      <span className="font-medium text-red-600">{formatNumber(reportData.rejected_claims)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-red-500 h-2 rounded-full"
                        style={{
                          width: `${(reportData.rejected_claims / (reportData.pending_claims + reportData.approved_claims + reportData.rejected_claims)) * 100}%`
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Top Diagnoses */}
            {reportData.top_diagnoses && reportData.top_diagnoses.length > 0 && (
              <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Diagnosa Teratas</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2 text-sm font-medium text-gray-600">Kode</th>
                        <th className="text-left py-2 text-sm font-medium text-gray-600">Diagnosa</th>
                        <th className="text-center py-2 text-sm font-medium text-gray-600">Jumlah</th>
                        <th className="text-center py-2 text-sm font-medium text-gray-600">Persentase</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reportData.top_diagnoses.map((diagnosis, idx) => (
                        <tr key={idx} className="border-b">
                          <td className="py-3 text-sm font-medium text-gray-900">{diagnosis.diagnosis_code}</td>
                          <td className="py-3 text-sm text-gray-700">{diagnosis.diagnosis_name}</td>
                          <td className="py-3 text-sm text-center text-gray-900">{formatNumber(diagnosis.count)}</td>
                          <td className="py-3 text-sm text-center text-gray-600">{diagnosis.percentage.toFixed(1)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Department Stats */}
            {reportData.department_stats && reportData.department_stats.length > 0 && (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistik Departemen</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2 text-sm font-medium text-gray-600">Departemen</th>
                        <th className="text-center py-2 text-sm font-medium text-gray-600">Jumlah Pasien</th>
                        <th className="text-right py-2 text-sm font-medium text-gray-600">Pendapatan</th>
                        <th className="text-center py-2 text-sm font-medium text-gray-600">Rating</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reportData.department_stats.map((dept, idx) => (
                        <tr key={idx} className="border-b">
                          <td className="py-3 text-sm font-medium text-gray-900">{dept.department_name}</td>
                          <td className="py-3 text-sm text-center text-gray-700">{formatNumber(dept.patient_count)}</td>
                          <td className="py-3 text-sm text-right text-gray-900">{formatCurrency(dept.revenue)}</td>
                          <td className="py-3 text-sm text-center text-gray-600">
                            {dept.avg_patient_rating ? (
                              <span className="flex items-center justify-center">
                                <span className="text-yellow-500 mr-1">⭐</span>
                                {dept.avg_patient_rating.toFixed(1)}
                              </span>
                            ) : (
                              "-"
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Operational, Clinical, Financial, Administrative Tabs */}
        {activeTab !== "dashboard" && (
          <div className="p-6">
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {activeTab === "operational" && "Laporan Operasional"}
                {activeTab === "clinical" && "Laporan Klinis"}
                {activeTab === "financial" && "Laporan Keuangan"}
                {activeTab === "administrative" && "Laporan Administratif"}
              </h3>
              <p className="text-gray-600 text-sm">
                Pilih laporan untuk dibuat atau diekspor
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {availableReports
                .filter((report) => report.category === activeTab)
                .map((report) => (
                  <div key={report.report_type} className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div className={`px-2 py-1 rounded text-xs font-medium bg-${getCategoryColor(report.category)}-100 text-${getCategoryColor(report.category)}-700`}>
                        {report.category}
                      </div>
                      {report.is_scheduled && (
                        <span className="text-xs text-gray-500">
                          {report.schedule_frequency === "daily" && "Harian"}
                          {report.schedule_frequency === "weekly" && "Mingguan"}
                          {report.schedule_frequency === "monthly" && "Bulanan"}
                          {report.schedule_frequency === "quarterly" && "Kuartalan"}
                          {report.schedule_frequency === "yearly" && "Tahunan"}
                        </span>
                      )}
                    </div>
                    <h4 className="font-semibold text-gray-900 mb-2">{report.report_name}</h4>
                    <p className="text-sm text-gray-600 mb-4">{report.description}</p>
                    {report.last_generated && (
                      <p className="text-xs text-gray-500 mb-4">
                        Terakhir dibuat: {new Date(report.last_generated).toLocaleDateString("id-ID")}
                      </p>
                    )}
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleGenerateReport(report.report_type)}
                        className="flex-1 px-3 py-2 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700"
                      >
                        Buat
                      </button>
                      <div className="relative">
                        <button
                          onClick={() => handleExportReport(report.report_type, "pdf")}
                          className="px-3 py-2 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300"
                          title="Export PDF"
                        >
                          PDF
                        </button>
                      </div>
                      <button
                        onClick={() => handleExportReport(report.report_type, "excel")}
                        className="px-3 py-2 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300"
                        title="Export Excel"
                      >
                        XLS
                      </button>
                    </div>
                  </div>
                ))}
            </div>

            {availableReports.filter((report) => report.category === activeTab).length === 0 && (
              <div className="text-center py-12">
                <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada laporan</h3>
                <p className="text-gray-600">Belum ada laporan untuk kategori ini</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
