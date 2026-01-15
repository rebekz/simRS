"use client";

/**
 * Staff Radiology Results Page - STORY-008: Radiology Results Management
 *
 * Comprehensive radiology results management for medical staff including:
 * - View all radiology exams with filters and search
 * - Filter by patient, modality, status, date range
 * - View detailed radiology results and images
 * - Access radiology images and reports
 * - Monitor pending radiology orders
 * - Track exam status (scheduled, in progress, completed, reported)
 * - Print and export radiology reports
 * - Critical findings alerts
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
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
  Image as ImageIcon,
  Activity,
  Camera,
} from "lucide-react";

// Types
interface RadiologyExam {
  id: number;
  patient_id: number;
  patient_name: string;
  medical_record_number: string;
  encounter_id?: number;
  order_id: number;
  order_number: string;
  exam_type: string;
  exam_name: string;
  modality: "xray" | "ct" | "mri" | "ultrasound" | "mammography" | "fluoroscopy" | "nuclear_medicine" | "pet_scan";
  body_part: string;
  view_position?: string;
  scheduled_date: string;
  scheduled_time?: string;
  performed_date?: string;
  reported_date?: string;
  status: "scheduled" | "in_progress" | "completed" | "reported" | "cancelled";
  priority: "routine" | "urgent" | "stat";
  ordering_physician: string;
  performing_technician?: string;
  reporting_radiologist?: string;
  clinical_indication?: string;
  contrast_used: boolean;
  contrast_type?: string;
  findings?: string;
  impression?: string;
  images: RadiologyImage[];
  critical_findings?: CriticalFinding[];
}

interface RadiologyImage {
  id: number;
  image_type: "original" | "processed" | "thumbnail";
  image_url: string;
  capture_date?: string;
  sequence_number?: number;
}

interface CriticalFinding {
  id: number;
  finding: string;
  severity: "mild" | "moderate" | "severe";
  acknowledged: boolean;
  acknowledged_by?: string;
  acknowledged_at?: string;
  notified_physician: boolean;
}

interface RadiologyStats {
  total_today: number;
  scheduled: number;
  in_progress: number;
  completed: number;
  reported: number;
}

type StatusFilter = "all" | "scheduled" | "in_progress" | "completed" | "reported" | "cancelled";
type ModalityFilter = "all" | "xray" | "ct" | "mri" | "ultrasound" | "mammography" | "fluoroscopy" | "nuclear_medicine" | "pet_scan";
type PriorityFilter = "all" | "routine" | "urgent" | "stat";

export default function StaffRadiologyPage() {
  const router = useRouter();
  const [radiologyExams, setRadiologyExams] = useState<RadiologyExam[]>([]);
  const [stats, setStats] = useState<RadiologyStats | null>(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [modalityFilter, setModalityFilter] = useState<ModalityFilter>("all");
  const [priorityFilter, setPriorityFilter] = useState<PriorityFilter>("all");
  const [dateFilter, setDateFilter] = useState<string>("today");
  const [searchQuery, setSearchQuery] = useState("");

  // UI state
  const [selectedExam, setSelectedExam] = useState<RadiologyExam | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [expandedExam, setExpandedExam] = useState<number | null>(null);

  useEffect(() => {
    fetchRadiologyExams();
  }, [statusFilter, modalityFilter, priorityFilter, dateFilter]);

  const fetchRadiologyExams = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const params = new URLSearchParams();
      if (statusFilter !== "all") params.append("status", statusFilter);
      if (modalityFilter !== "all") params.append("modality", modalityFilter);
      if (priorityFilter !== "all") params.append("priority", priorityFilter);
      if (dateFilter !== "all") params.append("date_filter", dateFilter);
      if (searchQuery) params.append("search", searchQuery);

      const response = await fetch(`/api/v1/radiology/exams?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setRadiologyExams(data.items || []);
        setStats(data.stats || null);
      } else {
        console.error("Failed to fetch radiology exams");
      }
    } catch (error) {
      console.error("Failed to fetch radiology exams:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledgeCritical = async (examId: number, findingId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(
        `/api/v1/radiology/exams/${examId}/critical-findings/${findingId}/acknowledge`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        fetchRadiologyExams();
        alert("Temuan kritis diakui");
      } else {
        alert("Gagal mengakui temuan kritis");
      }
    } catch (error) {
      console.error("Failed to acknowledge critical finding:", error);
      alert("Gagal mengakui temuan kritis");
    }
  };

  const handleViewImages = (exam: RadiologyExam) => {
    setSelectedExam(exam);
    setShowDetailModal(true);
  };

  const handlePrintReport = async (examId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/radiology/exams/${examId}/print`, {
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
        alert("Gagal mencetak laporan radiologi");
      }
    } catch (error) {
      console.error("Failed to print radiology report:", error);
      alert("Gagal mencetak laporan radiologi");
    }
  };

  const getModalityLabel = (modality: string) => {
    const labels: Record<string, string> = {
      xray: "X-Ray",
      ct: "CT Scan",
      mri: "MRI",
      ultrasound: "USG",
      mammography: "Mamografi",
      fluoroscopy: "Fluoroskopi",
      nuclear_medicine: "Medisin Nuklir",
      pet_scan: "PET Scan",
    };
    return labels[modality] || modality;
  };

  const getModalityIcon = (modality: string) => {
    const icons: Record<string, React.ReactNode> = {
      xray: <ImageIcon className="w-4 h-4" />,
      ct: <Activity className="w-4 h-4" />,
      mri: <Camera className="w-4 h-4" />,
      ultrasound: <Activity className="w-4 h-4" />,
      mammography: <ImageIcon className="w-4 h-4" />,
      fluoroscopy: <Camera className="w-4 h-4" />,
      nuclear_medicine: <Activity className="w-4 h-4" />,
      pet_scan: <Activity className="w-4 h-4" />,
    };
    return icons[modality] || <ImageIcon className="w-4 h-4" />;
  };

  const getModalityColor = (modality: string) => {
    const colors: Record<string, string> = {
      xray: "bg-blue-100 text-blue-800",
      ct: "bg-purple-100 text-purple-800",
      mri: "bg-green-100 text-green-800",
      ultrasound: "bg-yellow-100 text-yellow-800",
      mammography: "bg-pink-100 text-pink-800",
      fluoroscopy: "bg-orange-100 text-orange-800",
      nuclear_medicine: "bg-red-100 text-red-800",
      pet_scan: "bg-indigo-100 text-indigo-800",
    };
    return colors[modality] || "bg-gray-100 text-gray-800";
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      scheduled: "Terjadwal",
      in_progress: "Diproses",
      completed: "Selesai",
      reported: "Dilaporkan",
      cancelled: "Dibatalkan",
    };
    return labels[status] || status;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      scheduled: "bg-blue-100 text-blue-800",
      in_progress: "bg-yellow-100 text-yellow-800",
      completed: "bg-green-100 text-green-800",
      reported: "bg-emerald-100 text-emerald-800",
      cancelled: "bg-red-100 text-red-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const getStatusIcon = (status: string) => {
    const icons: Record<string, React.ReactNode> = {
      scheduled: <Calendar className="w-4 h-4" />,
      in_progress: <Activity className="w-4 h-4" />,
      completed: <CheckCircle className="w-4 h-4" />,
      reported: <FileText className="w-4 h-4" />,
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

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      mild: "bg-yellow-100 text-yellow-800",
      moderate: "bg-orange-100 text-orange-800",
      severe: "bg-red-100 text-red-800",
    };
    return colors[severity] || "bg-gray-100 text-gray-800";
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

  const filteredExams = radiologyExams.filter((exam) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        exam.patient_name.toLowerCase().includes(query) ||
        exam.medical_record_number.toLowerCase().includes(query) ||
        exam.order_number.toLowerCase().includes(query) ||
        exam.exam_name.toLowerCase().includes(query) ||
        exam.exam_type.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const handleSearch = () => {
    fetchRadiologyExams();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Radiologi</h1>
          <p className="text-sm text-gray-600 mt-1">Kelola hasil pemeriksaan radiologi</p>
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
                <p className="text-sm text-gray-600">Terjadwal</p>
                <p className="text-2xl font-bold text-blue-600">{stats.scheduled}</p>
              </div>
              <Calendar className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Diproses</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.in_progress}</p>
              </div>
              <Activity className="w-8 h-8 text-yellow-600" />
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
                <p className="text-sm text-gray-600">Dilaporkan</p>
                <p className="text-2xl font-bold text-emerald-600">{stats.reported}</p>
              </div>
              <FileText className="w-8 h-8 text-emerald-600" />
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
              placeholder="Cari pasien, nomor order, atau pemeriksaan..."
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
            <option value="scheduled">Terjadwal</option>
            <option value="in_progress">Diproses</option>
            <option value="completed">Selesai</option>
            <option value="reported">Dilaporkan</option>
            <option value="cancelled">Dibatalkan</option>
          </select>

          {/* Modality Filter */}
          <select
            value={modalityFilter}
            onChange={(e) => setModalityFilter(e.target.value as ModalityFilter)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Semua Modalitas</option>
            <option value="xray">X-Ray</option>
            <option value="ct">CT Scan</option>
            <option value="mri">MRI</option>
            <option value="ultrasound">USG</option>
            <option value="mammography">Mamografi</option>
            <option value="fluoroscopy">Fluoroskopi</option>
            <option value="nuclear_medicine">Medisin Nuklir</option>
            <option value="pet_scan">PET Scan</option>
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

      {/* Radiology Exams List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredExams.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <ImageIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada pemeriksaan radiologi</h3>
          <p className="text-gray-600">
            {searchQuery || statusFilter !== "all" || modalityFilter !== "all"
              ? "Tidak ada pemeriksaan yang sesuai dengan filter"
              : "Belum ada pemeriksaan radiologi yang dijadwalkan"}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredExams.map((exam) => {
            const isExpanded = expandedExam === exam.id;
            const hasCriticalFindings = exam.critical_findings && exam.critical_findings.length > 0;
            const hasImages = exam.images && exam.images.length > 0;
            const isReported = exam.status === "reported";

            return (
              <div key={exam.id} className="bg-white rounded-lg shadow overflow-hidden">
                {/* Summary Row */}
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getPriorityColor(
                            exam.priority
                          )}`}
                        >
                          {getPriorityLabel(exam.priority)}
                        </span>
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                            exam.status
                          )}`}
                        >
                          {getStatusIcon(exam.status)}
                          <span className="ml-1">{getStatusLabel(exam.status)}</span>
                        </span>
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getModalityColor(
                            exam.modality
                          )}`}
                        >
                          {getModalityIcon(exam.modality)}
                          <span className="ml-1">{getModalityLabel(exam.modality)}</span>
                        </span>
                        <span className="text-xs text-gray-500">{formatDate(exam.scheduled_date)}</span>
                        {exam.contrast_used && (
                          <span className="text-xs text-blue-600 font-medium">Dengan Kontras</span>
                        )}
                      </div>

                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          <FileText className="w-4 h-4 text-gray-400" />
                          <div>
                            <p className="font-medium text-gray-900">Order #{exam.order_number}</p>
                            <p className="text-xs text-gray-500">{exam.exam_name}</p>
                          </div>
                        </div>

                        <div className="flex items-center space-x-2">
                          <User className="w-4 h-4 text-gray-400" />
                          <div>
                            <p className="font-medium text-gray-900">{exam.patient_name}</p>
                            <p className="text-xs text-gray-500">{exam.medical_record_number}</p>
                          </div>
                        </div>

                        <div className="text-sm text-gray-600">
                          <span className="font-medium">{exam.body_part}</span>
                          {exam.view_position && <span> - {exam.view_position}</span>}
                        </div>

                        <div className="text-sm text-gray-600">
                          <span className="font-medium">Dokter:</span> {exam.ordering_physician}
                        </div>

                        {hasCriticalFindings && (
                          <div className="flex items-center space-x-1 text-red-600">
                            <AlertTriangle className="w-4 h-4" />
                            <span className="text-xs font-medium">TEMUAN KRITIS</span>
                          </div>
                        )}

                        {hasImages && (
                          <div className="flex items-center space-x-1 text-gray-600">
                            <ImageIcon className="w-4 h-4" />
                            <span className="text-xs font-medium">{exam.images.length} Gambar</span>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center space-x-2 mt-2 text-xs text-gray-500">
                        {exam.scheduled_time && <span>Jadwal: {exam.scheduled_time}</span>}
                        {exam.performed_date && <span>Dikerjakan: {formatDateTime(exam.performed_date)}</span>}
                        {exam.reported_date && <span>Dilaporkan: {formatDateTime(exam.reported_date)}</span>}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      {hasImages && (
                        <button
                          onClick={() => handleViewImages(exam)}
                          className="p-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200"
                          title="Lihat Gambar"
                        >
                          <ImageIcon className="w-4 h-4" />
                        </button>
                      )}

                      <button
                        onClick={() => {
                          setSelectedExam(exam);
                          setShowDetailModal(true);
                        }}
                        className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                        title="Lihat Detail"
                      >
                        <Eye className="w-4 h-4" />
                      </button>

                      {isReported && (
                        <button
                          onClick={() => handlePrintReport(exam.id)}
                          className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                          title="Cetak Laporan"
                        >
                          <Printer className="w-4 h-4" />
                        </button>
                      )}

                      <button
                        onClick={() => setExpandedExam(isExpanded ? null : exam.id)}
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
                    {/* Clinical Indication */}
                    {exam.clinical_indication && (
                      <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <p className="text-sm">
                          <span className="font-medium text-blue-900">Indikasi Klinis:</span>{" "}
                          <span className="text-blue-800">{exam.clinical_indication}</span>
                        </p>
                      </div>
                    )}

                    {/* Critical Findings Alert */}
                    {hasCriticalFindings && (
                      <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <div className="flex items-center space-x-2 mb-3">
                          <AlertTriangle className="w-5 h-5 text-red-600" />
                          <h4 className="text-sm font-semibold text-red-900">TEMUAN KRITIS</h4>
                        </div>
                        <div className="space-y-2">
                          {exam.critical_findings?.map((cf) => (
                            <div key={cf.id} className="flex items-start justify-between text-sm">
                              <div className="flex-1">
                                <p className="font-medium text-red-900">{cf.finding}</p>
                                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ml-2 ${getSeverityColor(
                                  cf.severity
                                )}`}>
                                  {cf.severity === "mild" ? "Ringan" : cf.severity === "moderate" ? "Sedang" : "Berat"}
                                </span>
                              </div>
                              {!cf.acknowledged && (
                                <button
                                  onClick={() => handleAcknowledgeCritical(exam.id, cf.id)}
                                  className="px-3 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700 ml-2"
                                >
                                  Akui
                                </button>
                              )}
                              {cf.acknowledged && (
                                <span className="text-xs text-green-700 ml-2">
                                  ✓ Diakui oleh {cf.acknowledged_by}
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Findings & Impression */}
                    {(exam.findings || exam.impression) && (
                      <div className="mb-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                        {exam.findings && (
                          <div className="p-3 bg-white rounded-lg border border-gray-200">
                            <h5 className="text-sm font-semibold text-gray-900 mb-2">Temuan</h5>
                            <p className="text-sm text-gray-700 whitespace-pre-line">{exam.findings}</p>
                          </div>
                        )}
                        {exam.impression && (
                          <div className="p-3 bg-white rounded-lg border border-gray-200">
                            <h5 className="text-sm font-semibold text-gray-900 mb-2">Kesimpulan</h5>
                            <p className="text-sm text-gray-700 whitespace-pre-line">{exam.impression}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Images Preview */}
                    {hasImages && (
                      <div className="mb-4">
                        <h4 className="text-sm font-semibold text-gray-900 mb-3">Gambar ({exam.images.length})</h4>
                        <div className="flex flex-wrap gap-2">
                          {exam.images.slice(0, 4).map((image) => (
                            <div
                              key={image.id}
                              className="w-24 h-24 bg-gray-200 rounded-lg overflow-hidden border border-gray-300"
                            >
                              <img
                                src={image.image_url}
                                alt="Radiology image"
                                className="w-full h-full object-cover"
                              />
                            </div>
                          ))}
                          {exam.images.length > 4 && (
                            <div className="w-24 h-24 bg-gray-100 rounded-lg flex items-center justify-center">
                              <span className="text-sm text-gray-600">+{exam.images.length - 4}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Performer & Reporter */}
                    <div className="text-xs text-gray-500">
                      {exam.performing_technician && <span>Teknisi: {exam.performing_technician} | </span>}
                      {exam.reporting_radiologist && <span>Radiolog: {exam.reporting_radiologist}</span>}
                    </div>
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
