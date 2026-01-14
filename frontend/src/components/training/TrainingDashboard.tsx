"use client";

/**
 * Training Dashboard Component for STORY-038
 *
 * Provides comprehensive training overview with:
 * - Overall training statistics
 * - My assignments list with status badges
 * - Progress bars for each module
 * - Quick links to start/resume training
 * - Mandatory training alerts
 */

import { useState, useEffect } from "react";
import {
  BookOpen,
  Clock,
  AlertCircle,
  CheckCircle,
  Play,
  TrendingUp,
  Users,
  Award,
  AlertTriangle,
  RefreshCw,
  FileText,
  Video,
  Link as LinkIcon,
} from "lucide-react";

// Types
interface TrainingAssignment {
  id: number;
  module_id: number;
  module_title: string;
  module_code: string;
  category: string;
  description: string;
  duration_minutes: number;
  is_mandatory: boolean;
  due_date?: string;
  assigned_date: string;
  status: "not_started" | "in_progress" | "completed" | "overdue";
  progress_percentage: number;
  content_type: "video" | "document" | "interactive" | "scorm";
  total_lessons: number;
  completed_lessons: number;
  last_accessed?: string;
}

interface TrainingStatistics {
  total_assignments: number;
  completed_count: number;
  in_progress_count: number;
  overdue_count: number;
  completion_rate: number;
  mandatory_completed: number;
  mandatory_total: number;
  total_hours_spent: number;
}

export function TrainingDashboard() {
  const [assignments, setAssignments] = useState<TrainingAssignment[]>([]);
  const [statistics, setStatistics] = useState<TrainingStatistics | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");

      // Load assignments
      const assignmentsResponse = await fetch("/api/v1/training/my-assignments", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (assignmentsResponse.ok) {
        const data = await assignmentsResponse.json();
        setAssignments(data.assignments || []);
      }

      // Load statistics
      const statsResponse = await fetch("/api/v1/training/my-statistics", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (statsResponse.ok) {
        const data = await statsResponse.json();
        setStatistics(data);
      }
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string, isMandatory: boolean, dueDate?: string) => {
    const isOverdue = dueDate && new Date(dueDate) < new Date() && status !== "completed";

    if (isOverdue) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <AlertTriangle className="h-3 w-3 mr-1" />
          Terlambat
        </span>
      );
    }

    switch (status) {
      case "completed":
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="h-3 w-3 mr-1" />
            Selesai
          </span>
        );
      case "in_progress":
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            <Clock className="h-3 w-3 mr-1" />
            Sedang Berjalan
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            Belum Dimulai
          </span>
        );
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case "keperawatan":
        return "👩‍⚕️";
      case "kedokteran":
        return "👨‍⚕️";
      case "farmasi":
        return "💊";
      case "keamanan":
        return "🔒";
      case "keselamatan":
        return "⚠️";
      case "administrasi":
        return "📋";
      default:
        return "📚";
    }
  };

  const getContentTypeIcon = (type: string) => {
    switch (type) {
      case "video":
        return <Video className="h-4 w-4" />;
      case "document":
        return <FileText className="h-4 w-4" />;
      case "interactive":
        return <LinkIcon className="h-4 w-4" />;
      default:
        return <BookOpen className="h-4 w-4" />;
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

  const getOverdueAssignments = () => {
    return assignments.filter(
      (a) => a.due_date && new Date(a.due_date) < new Date() && a.status !== "completed"
    );
  };

  const getMandatoryIncomplete = () => {
    return assignments.filter((a) => a.is_mandatory && a.status !== "completed");
  };

  if (isLoading && assignments.length === 0) {
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
            <BookOpen className="h-6 w-6 mr-2" />
            Dashboard Pelatihan
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Pantau progres pelatihan dan penugasan Anda
          </p>
        </div>
        <button
          onClick={loadDashboardData}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* Alerts Section */}
      {(getOverdueAssignments().length > 0 || getMandatoryIncomplete().length > 0) && (
        <div className="space-y-3">
          {getOverdueAssignments().length > 0 && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-md">
              <div className="flex items-start">
                <AlertCircle className="h-5 w-5 text-red-400 mr-3 mt-0.5" />
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-red-800">
                    {getOverdueAssignments().length} Pelatihan Terlambat
                  </h3>
                  <p className="text-sm text-red-700 mt-1">
                    Segera selesaikan pelatihan yang melewati batas waktu
                  </p>
                </div>
              </div>
            </div>
          )}

          {getMandatoryIncomplete().length > 0 && (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-md">
              <div className="flex items-start">
                <AlertTriangle className="h-5 w-5 text-yellow-400 mr-3 mt-0.5" />
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-yellow-800">
                    {getMandatoryIncomplete().length} Pelatihan Wajib Belum Selesai
                  </h3>
                  <p className="text-sm text-yellow-700 mt-1">
                    Pelatihan wajib harus diselesaikan untuk kepatuhan
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Completion Rate */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Tingkat Penyelesaian</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {statistics.completion_rate.toFixed(1)}%
                </p>
              </div>
              <div className="bg-blue-100 rounded-full p-3">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${statistics.completion_rate}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Completed */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Selesai</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {statistics.completed_count}
                </p>
                <p className="text-xs text-gray-500">
                  dari {statistics.total_assignments} penugasan
                </p>
              </div>
              <div className="bg-green-100 rounded-full p-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>

          {/* In Progress */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Sedang Berjalan</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {statistics.in_progress_count}
                </p>
              </div>
              <div className="bg-blue-100 rounded-full p-3">
                <Clock className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>

          {/* Overdue */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Terlambat</p>
                <p className="text-2xl font-bold text-red-600 mt-1">
                  {statistics.overdue_count}
                </p>
              </div>
              <div className="bg-red-100 rounded-full p-3">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Additional Stats */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center">
              <Award className="h-5 w-5 text-yellow-600 mr-3" />
              <div>
                <p className="text-xs text-gray-500">Pelatihan Wajib</p>
                <p className="text-sm font-semibold text-gray-900">
                  {statistics.mandatory_completed} / {statistics.mandatory_total}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center">
              <BookOpen className="h-5 w-5 text-purple-600 mr-3" />
              <div>
                <p className="text-xs text-gray-500">Total Modul</p>
                <p className="text-sm font-semibold text-gray-900">
                  {statistics.total_assignments}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center">
              <Clock className="h-5 w-5 text-green-600 mr-3" />
              <div>
                <p className="text-xs text-gray-500">Total Waktu</p>
                <p className="text-sm font-semibold text-gray-900">
                  {statistics.total_hours_spent.toFixed(1)} jam
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* My Assignments */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Penugasan Saya</h3>
          <p className="text-sm text-gray-600">
            Daftar pelatihan yang ditugaskan untuk Anda
          </p>
        </div>

        <div className="divide-y divide-gray-200">
          {assignments.map((assignment) => (
            <div key={assignment.id} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{getCategoryIcon(assignment.category)}</span>
                    <div>
                      <div className="flex items-center space-x-2">
                        <h4 className="text-sm font-medium text-gray-900">
                          {assignment.module_title}
                        </h4>
                        {assignment.is_mandatory && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                            Wajib
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500">
                        {assignment.module_code} • {assignment.category}
                      </p>
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 mt-2">{assignment.description}</p>

                  <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                    <div className="flex items-center">
                      {getContentTypeIcon(assignment.content_type)}
                      <span className="ml-1">
                        {assignment.content_type === "video"
                          ? "Video"
                          : assignment.content_type === "document"
                          ? "Dokumen"
                          : "Interaktif"}
                      </span>
                    </div>
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      {formatDuration(assignment.duration_minutes)}
                    </div>
                    {assignment.due_date && (
                      <div className="flex items-center">
                        <AlertCircle className="h-4 w-4 mr-1" />
                        {formatDate(assignment.due_date)}
                      </div>
                    )}
                    <div className="flex items-center">
                      <FileText className="h-4 w-4 mr-1" />
                      {assignment.completed_lessons} / {assignment.total_lessons} pelajaran
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <span>Progres</span>
                      <span>{assignment.progress_percentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          assignment.status === "completed"
                            ? "bg-green-600"
                            : assignment.status === "overdue"
                            ? "bg-red-600"
                            : "bg-blue-600"
                        }`}
                        style={{ width: `${assignment.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                <div className="ml-6 flex flex-col items-end space-y-2">
                  {getStatusBadge(assignment.status, assignment.is_mandatory, assignment.due_date)}

                  <button
                    className={`inline-flex items-center px-3 py-1.5 border rounded-md text-sm font-medium ${
                      assignment.status === "completed"
                        ? "border-gray-300 text-gray-700 bg-gray-50 cursor-default"
                        : "border-transparent text-white bg-blue-600 hover:bg-blue-700"
                    }`}
                  >
                    {assignment.status === "completed" ? (
                      <>
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Selesai
                      </>
                    ) : assignment.status === "not_started" ? (
                      <>
                        <Play className="h-4 w-4 mr-1" />
                        Mulai
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-1" />
                        Lanjutkan
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {assignments.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <BookOpen className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>Belum ada penugasan pelatihan</p>
          </div>
        )}
      </div>
    </div>
  );
}
