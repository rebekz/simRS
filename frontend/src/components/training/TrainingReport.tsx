"use client";

/**
 * Training Report Component for STORY-038
 *
 * Provides comprehensive reports with:
 * - Completion rates by department
 * - User compliance status
 * - Module statistics
 * - Export to CSV functionality
 * - Date range filtering
 */

import { useState, useEffect } from "react";
import {
  FileText,
  Download,
  Calendar,
  Filter,
  BarChart3,
  TrendingUp,
  Users,
  CheckCircle,
  Clock,
  AlertTriangle,
  Award,
  Building,
  RefreshCw,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

// Types
interface DepartmentReport {
  department_id: number;
  department_name: string;
  total_employees: number;
  assigned_count: number;
  completed_count: number;
  in_progress_count: number;
  overdue_count: number;
  completion_rate: number;
  average_time_spent: number;
}

interface ModuleReport {
  module_id: number;
  module_title: string;
  module_code: string;
  category: string;
  total_assigned: number;
  completed_count: number;
  in_progress_count: number;
  not_started_count: number;
  completion_rate: number;
  average_completion_time: number;
  average_score?: number;
}

interface UserCompliance {
  user_id: number;
  username: string;
  full_name: string;
  department_name?: string;
  role: string;
  total_assigned: number;
  mandatory_assigned: number;
  mandatory_completed: number;
  completion_rate: number;
  compliance_status: "compliant" | "non_compliant" | "pending";
  overdue_count: number;
}

interface ReportSummary {
  total_employees: number;
  total_assignments: number;
  total_completions: number;
  overall_completion_rate: number;
  compliant_employees: number;
  non_compliant_employees: number;
  mandatory_completion_rate: number;
}

export function TrainingReport() {
  const [departmentReports, setDepartmentReports] = useState<DepartmentReport[]>([]);
  const [moduleReports, setModuleReports] = useState<ModuleReport[]>([]);
  const [userCompliance, setUserCompliance] = useState<UserCompliance[]>([]);
  const [summary, setSummary] = useState<ReportSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Filter states
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [selectedDepartment, setSelectedDepartment] = useState("");
  const [selectedModule, setSelectedModule] = useState("");
  const [activeTab, setActiveTab] = useState<"summary" | "departments" | "modules" | "users">(
    "summary"
  );

  // Sort states
  const [sortField, setSortField] = useState<string>("completion_rate");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const [expandedDepartments, setExpandedDepartments] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadReports();
  }, [startDate, endDate, selectedDepartment, selectedModule]);

  const loadReports = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");

      const params = new URLSearchParams();
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);
      if (selectedDepartment) params.append("department_id", selectedDepartment);
      if (selectedModule) params.append("module_id", selectedModule);

      // Load summary
      const summaryResponse = await fetch(`/api/v1/training/reports/summary?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (summaryResponse.ok) {
        const data = await summaryResponse.json();
        setSummary(data);
      }

      // Load department reports
      const deptResponse = await fetch(`/api/v1/training/reports/departments?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (deptResponse.ok) {
        const data = await deptResponse.json();
        setDepartmentReports(data.departments || []);
      }

      // Load module reports
      const moduleResponse = await fetch(`/api/v1/training/reports/modules?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (moduleResponse.ok) {
        const data = await moduleResponse.json();
        setModuleReports(data.modules || []);
      }

      // Load user compliance
      const userResponse = await fetch(`/api/v1/training/reports/compliance?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (userResponse.ok) {
        const data = await userResponse.json();
        setUserCompliance(data.users || []);
      }
    } catch (error) {
      console.error("Failed to load reports:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const exportToCSV = async (reportType: "departments" | "modules" | "compliance") => {
    try {
      const token = localStorage.getItem("token");

      const params = new URLSearchParams();
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);
      if (selectedDepartment) params.append("department_id", selectedDepartment);
      if (selectedModule) params.append("module_id", selectedModule);

      const response = await fetch(
        `/api/v1/training/reports/${reportType}/export?${params}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `training-${reportType}-${new Date().toISOString().split("T")[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert("Gagal mengekspor laporan");
      }
    } catch (error) {
      console.error("Error exporting report:", error);
    }
  };

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const getSortedData = <T,>(data: T[], field: string, direction: "asc" | "desc"): T[] => {
    return [...data].sort((a: any, b: any) => {
      if (a[field] < b[field]) return direction === "asc" ? -1 : 1;
      if (a[field] > b[field]) return direction === "asc" ? 1 : -1;
      return 0;
    });
  };

  const toggleDepartmentExpanded = (deptId: number) => {
    setExpandedDepartments((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(deptId)) {
        newSet.delete(deptId);
      } else {
        newSet.add(deptId);
      }
      return newSet;
    });
  };

  const getComplianceBadge = (status: string) => {
    switch (status) {
      case "compliant":
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="h-3 w-3 mr-1" />
            Patuh
          </span>
        );
      case "non_compliant":
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <AlertTriangle className="h-3 w-3 mr-1" />
            Tidak Patuh
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <Clock className="h-3 w-3 mr-1" />
            Pending
          </span>
        );
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("id-ID", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}j ${mins}m`;
    }
    return `${mins}m`;
  };

  const SortIcon = ({ field }: { field: string }) => {
    if (sortField !== field) return null;
    return sortDirection === "asc" ? (
      <ChevronUp className="h-4 w-4 inline ml-1" />
    ) : (
      <ChevronDown className="h-4 w-4 inline ml-1" />
    );
  };

  if (isLoading && !summary) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <BarChart3 className="h-6 w-6 mr-2" />
            Laporan Pelatihan
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Analisis penyelesaian, kepatuhan, dan statistik pelatihan
          </p>
        </div>
        <button
          onClick={loadReports}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Calendar className="h-4 w-4 text-gray-400" />
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
            />
            <span className="text-gray-500">s/d</span>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <button
            onClick={() => {
              setStartDate("");
              setEndDate("");
              setSelectedDepartment("");
              setSelectedModule("");
            }}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Reset Filter
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && activeTab === "summary" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Pegawai</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{summary.total_employees}</p>
              </div>
              <div className="bg-blue-100 rounded-full p-3">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Penyelesaian</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {summary.total_completions}
                </p>
                <p className="text-xs text-gray-500">
                  dari {summary.total_assignments} penugasan
                </p>
              </div>
              <div className="bg-green-100 rounded-full p-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Tingkat Penyelesaian</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {summary.overall_completion_rate.toFixed(1)}%
                </p>
                <div className="flex items-center mt-1">
                  <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                  <span className="text-xs text-green-600">+2.5% dari bulan lalu</span>
                </div>
              </div>
              <div className="bg-purple-100 rounded-full p-3">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Kepatuhan</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {summary.compliant_employees}/{summary.total_employees}
                </p>
                <p className="text-xs text-gray-500">pegawai patuh</p>
              </div>
              <div className="bg-yellow-100 rounded-full p-3">
                <Award className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab("summary")}
            className={`${
              activeTab === "summary"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Ringkasan
          </button>
          <button
            onClick={() => setActiveTab("departments")}
            className={`${
              activeTab === "departments"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Departemen
          </button>
          <button
            onClick={() => setActiveTab("modules")}
            className={`${
              activeTab === "modules"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Modul
          </button>
          <button
            onClick={() => setActiveTab("users")}
            className={`${
              activeTab === "users"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Kepatuhan Pengguna
          </button>
        </nav>
      </div>

      {/* Summary Tab */}
      {activeTab === "summary" && summary && (
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Ringkasan Eksekutif</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">
                  {summary.overall_completion_rate.toFixed(1)}%
                </div>
                <p className="text-sm text-gray-600 mt-1">Tingkat Penyelesaian Keseluruhan</p>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">
                  {summary.mandatory_completion_rate.toFixed(1)}%
                </div>
                <p className="text-sm text-gray-600 mt-1">Tingkat Penyelesaian Wajib</p>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">
                  {Math.round(summary.total_completions / summary.total_employees)}
                </div>
                <p className="text-sm text-gray-600 mt-1">Rata-rata Penyelesaian/Pegawai</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Departments Tab */}
      {activeTab === "departments" && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Laporan Departemen</h3>
            <button
              onClick={() => exportToCSV("departments")}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort("department_name")}>
                    Departemen <SortIcon field="department_name" />
                  </th>
                  <th
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort("total_employees")}
                  >
                    Total Pegawai <SortIcon field="total_employees" />
                  </th>
                  <th
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort("assigned_count")}
                  >
                    Ditugaskan <SortIcon field="assigned_count" />
                  </th>
                  <th
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort("completed_count")}
                  >
                    Selesai <SortIcon field="completed_count" />
                  </th>
                  <th
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort("completion_rate")}
                  >
                    Tingkat Penyelesaian <SortIcon field="completion_rate" />
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {getSortedData(departmentReports, sortField, sortDirection).map((dept) => (
                  <tr key={dept.department_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      <div className="flex items-center space-x-2">
                        <Building className="h-4 w-4 text-gray-400" />
                        <span>{dept.department_name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {dept.total_employees}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {dept.assigned_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {dept.completed_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              dept.completion_rate >= 80
                                ? "bg-green-600"
                                : dept.completion_rate >= 50
                                ? "bg-yellow-600"
                                : "bg-red-600"
                            }`}
                            style={{ width: `${dept.completion_rate}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {dept.completion_rate.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {departmentReports.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Building className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Tidak ada data departemen</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modules Tab */}
      {activeTab === "modules" && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Laporan Modul</h3>
            <button
              onClick={() => exportToCSV("modules")}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort("module_title")}>
                    Modul <SortIcon field="module_title" />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Kategori
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort("total_assigned")}>
                    Total Ditugaskan <SortIcon field="total_assigned" />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort("completed_count")}>
                    Selesai <SortIcon field="completed_count" />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort("completion_rate")}>
                    Tingkat Penyelesaian <SortIcon field="completion_rate" />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Rata-rata Waktu
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {getSortedData(moduleReports, sortField, sortDirection).map((module) => (
                  <tr key={module.module_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{module.module_title}</div>
                        <div className="text-xs text-gray-500">{module.module_code}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {module.category}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {module.total_assigned}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {module.completed_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              module.completion_rate >= 80
                                ? "bg-green-600"
                                : module.completion_rate >= 50
                                ? "bg-yellow-600"
                                : "bg-red-600"
                            }`}
                            style={{ width: `${module.completion_rate}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {module.completion_rate.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {module.average_completion_time
                        ? formatDuration(module.average_completion_time)
                        : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {moduleReports.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Tidak ada data modul</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Users Compliance Tab */}
      {activeTab === "users" && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Kepatuhan Pengguna</h3>
            <button
              onClick={() => exportToCSV("compliance")}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort("full_name")}>
                    Pengguna <SortIcon field="full_name" />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Departemen
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort("total_assigned")}>
                    Total Ditugaskan <SortIcon field="total_assigned" />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort("mandatory_completed")}>
                    Wajib Selesai <SortIcon field="mandatory_completed" />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort("completion_rate")}>
                    Tingkat Penyelesaian <SortIcon field="completion_rate" />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {getSortedData(userCompliance, sortField, sortDirection).map((user) => (
                  <tr key={user.user_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                        <div className="text-xs text-gray-500">@{user.username}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {user.department_name || "-"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {user.total_assigned}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {user.mandatory_completed} / {user.mandatory_assigned}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              user.completion_rate >= 80
                                ? "bg-green-600"
                                : user.completion_rate >= 50
                                ? "bg-yellow-600"
                                : "bg-red-600"
                            }`}
                            style={{ width: `${user.completion_rate}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {user.completion_rate.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getComplianceBadge(user.compliance_status)}
                      {user.overdue_count > 0 && (
                        <div className="text-xs text-red-600 mt-1">
                          {user.overdue_count} terlambat
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {userCompliance.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Users className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Tidak ada data pengguna</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
