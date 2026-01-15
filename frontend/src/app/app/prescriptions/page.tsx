"use client";

/**
 * Staff Prescriptions Management Page - STORY-011: Prescriptions Management
 *
 * Comprehensive prescription management for medical staff including:
 * - View all prescriptions with filters and search
 * - Filter by patient, status, date range, prescription type
 * - View detailed prescription information
 * - Access prescription history for patients
 * - Monitor prescription status (pending, dispensed, cancelled)
 * - Track medication dispensing
 * - Prescription printing and export
 * - Drug interaction warnings
 * - Dose verification
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  FileText,
  Plus,
  Search,
  Filter,
  Calendar,
  User,
  Pill,
  CheckCircle,
  Clock,
  XCircle,
  AlertTriangle,
  Eye,
  Edit,
  Trash2,
  Printer,
  Download,
  ChevronDown,
  ChevronUp,
  Package,
} from "lucide-react";

// Types
interface Prescription {
  id: number;
  patient_id: number;
  patient_name: string;
  medical_record_number: string;
  prescriber_id: number;
  prescriber_name: string;
  prescription_date: string;
  status: "pending" | "verified" | "dispensed" | "picked_up" | "cancelled";
  prescription_type: "outpatient" | "inpatient" | "discharge";
  priority: "routine" | "urgent" | "stat";
  notes?: string;
  diagnosis?: string;
  items: PrescriptionItem[];
  created_at: string;
  updated_at: string;
  dispenser_id?: number;
  dispenser_name?: string;
  verified_date?: string;
  dispensed_date?: string;
}

interface PrescriptionItem {
  id: number;
  medication_id: number;
  medication_name: string;
  generic_name?: string;
  dosage: string;
  frequency: string;
  duration: string;
  quantity: number;
  unit: string;
  instructions: string;
  status: "active" | "dispensed" | "cancelled";
  warnings?: string[];
}

interface PrescriptionStats {
  total_today: number;
  pending: number;
  verified: number;
  dispensed: number;
  cancelled: number;
}

type StatusFilter = "all" | "pending" | "verified" | "dispensed" | "picked_up" | "cancelled";
type TypeFilter = "all" | "outpatient" | "inpatient" | "discharge";
type PriorityFilter = "all" | "routine" | "urgent" | "stat";

export default function StaffPrescriptionsPage() {
  const router = useRouter();
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [stats, setStats] = useState<PrescriptionStats | null>(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [typeFilter, setTypeFilter] = useState<TypeFilter>("all");
  const [priorityFilter, setPriorityFilter] = useState<PriorityFilter>("all");
  const [dateFilter, setDateFilter] = useState<string>("today");
  const [searchQuery, setSearchQuery] = useState("");

  // UI state
  const [selectedPrescription, setSelectedPrescription] = useState<Prescription | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [expandedPrescription, setExpandedPrescription] = useState<number | null>(null);

  useEffect(() => {
    fetchPrescriptions();
  }, [statusFilter, typeFilter, priorityFilter, dateFilter]);

  const fetchPrescriptions = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const params = new URLSearchParams();
      if (statusFilter !== "all") params.append("status", statusFilter);
      if (typeFilter !== "all") params.append("prescription_type", typeFilter);
      if (priorityFilter !== "all") params.append("priority", priorityFilter);
      if (dateFilter !== "all") params.append("date_filter", dateFilter);
      if (searchQuery) params.append("search", searchQuery);

      const response = await fetch(`/api/v1/prescriptions?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setPrescriptions(data.items || []);
        setStats(data.stats || null);
      } else {
        console.error("Failed to fetch prescriptions");
      }
    } catch (error) {
      console.error("Failed to fetch prescriptions:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyPrescription = async (prescriptionId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/prescriptions/${prescriptionId}/verify`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        fetchPrescriptions();
        alert("Resep berhasil diverifikasi");
      } else {
        alert("Gagal memverifikasi resep");
      }
    } catch (error) {
      console.error("Failed to verify prescription:", error);
      alert("Gagal memverifikasi resep");
    }
  };

  const handleCancelPrescription = async (prescriptionId: number) => {
    if (!confirm("Apakah Anda yakin ingin membatalkan resep ini?")) {
      return;
    }

    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/prescriptions/${prescriptionId}/cancel`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        fetchPrescriptions();
        alert("Resep berhasil dibatalkan");
      } else {
        alert("Gagal membatalkan resep");
      }
    } catch (error) {
      console.error("Failed to cancel prescription:", error);
      alert("Gagal membatalkan resep");
    }
  };

  const handlePrintPrescription = async (prescriptionId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/prescriptions/${prescriptionId}/print`, {
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
        alert("Gagal mencetak resep");
      }
    } catch (error) {
      console.error("Failed to print prescription:", error);
      alert("Gagal mencetak resep");
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      pending: "Menunggu",
      verified: "Terverifikasi",
      dispensed: "Disiapkan",
      picked_up: "Diambil",
      cancelled: "Dibatalkan",
    };
    return labels[status] || status;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: "bg-yellow-100 text-yellow-800",
      verified: "bg-blue-100 text-blue-800",
      dispensed: "bg-purple-100 text-purple-800",
      picked_up: "bg-green-100 text-green-800",
      cancelled: "bg-red-100 text-red-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const getStatusIcon = (status: string) => {
    const icons: Record<string, React.ReactNode> = {
      pending: <Clock className="w-4 h-4" />,
      verified: <CheckCircle className="w-4 h-4" />,
      dispensed: <Package className="w-4 h-4" />,
      picked_up: <CheckCircle className="w-4 h-4" />,
      cancelled: <XCircle className="w-4 h-4" />,
    };
    return icons[status] || <Clock className="w-4 h-4" />;
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      outpatient: "Rawat Jalan",
      inpatient: "Rawat Inap",
      discharge: "Pulang",
    };
    return labels[type] || type;
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

  const filteredPrescriptions = prescriptions.filter((prescription) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        prescription.patient_name.toLowerCase().includes(query) ||
        prescription.medical_record_number.toLowerCase().includes(query) ||
        prescription.prescriber_name.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const handleSearch = () => {
    fetchPrescriptions();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Resep</h1>
          <p className="text-sm text-gray-600 mt-1">Kelola resep pasien</p>
        </div>
        <button
          onClick={() => router.push("/app/prescriptions/new")}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Buat Resep Baru
        </button>
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
                <p className="text-sm text-gray-600">Terverifikasi</p>
                <p className="text-2xl font-bold text-blue-600">{stats.verified}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Disiapkan</p>
                <p className="text-2xl font-bold text-purple-600">{stats.dispensed}</p>
              </div>
              <Package className="w-8 h-8 text-purple-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Dibatalkan</p>
                <p className="text-2xl font-bold text-red-600">{stats.cancelled}</p>
              </div>
              <XCircle className="w-8 h-8 text-red-600" />
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
              placeholder="Cari pasien atau dokter..."
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
            <option value="verified">Terverifikasi</option>
            <option value="dispensed">Disiapkan</option>
            <option value="picked_up">Diambil</option>
            <option value="cancelled">Dibatalkan</option>
          </select>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as TypeFilter)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Semua Tipe</option>
            <option value="outpatient">Rawat Jalan</option>
            <option value="inpatient">Rawat Inap</option>
            <option value="discharge">Pulang</option>
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

      {/* Prescriptions List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredPrescriptions.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <FileText className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada resep</h3>
          <p className="text-gray-600">
            {searchQuery || statusFilter !== "all" || typeFilter !== "all" || priorityFilter !== "all"
              ? "Tidak ada resep yang sesuai dengan filter"
              : "Belum ada resep yang dibuat"}
          </p>
          <button
            onClick={() => router.push("/app/prescriptions/new")}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Buat Resep Pertama
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredPrescriptions.map((prescription) => {
            const isExpanded = expandedPrescription === prescription.id;
            const hasWarnings = prescription.items.some((item) => item.warnings && item.warnings.length > 0);

            return (
              <div key={prescription.id} className="bg-white rounded-lg shadow overflow-hidden">
                {/* Summary Row */}
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getPriorityColor(
                            prescription.priority
                          )}`}
                        >
                          {getPriorityLabel(prescription.priority)}
                        </span>
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                            prescription.status
                          )}`}
                        >
                          {getStatusIcon(prescription.status)}
                          <span className="ml-1">{getStatusLabel(prescription.status)}</span>
                        </span>
                        <span className="text-xs text-gray-500">{getTypeLabel(prescription.prescription_type)}</span>
                        <span className="text-xs text-gray-500">{formatDate(prescription.prescription_date)}</span>
                      </div>

                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          <User className="w-4 h-4 text-gray-400" />
                          <div>
                            <p className="font-medium text-gray-900">{prescription.patient_name}</p>
                            <p className="text-xs text-gray-500">{prescription.medical_record_number}</p>
                          </div>
                        </div>

                        <div className="flex items-center space-x-2">
                          <Pill className="w-4 h-4 text-gray-400" />
                          <div>
                            <p className="text-sm text-gray-900">{prescription.items.length} obat</p>
                            <p className="text-xs text-gray-500">Oleh: {prescription.prescriber_name}</p>
                          </div>
                        </div>

                        {prescription.diagnosis && (
                          <div className="text-sm text-gray-600">
                            <span className="font-medium">Diagnosis:</span> {prescription.diagnosis}
                          </div>
                        )}

                        {hasWarnings && (
                          <div className="flex items-center space-x-1 text-orange-600">
                            <AlertTriangle className="w-4 h-4" />
                            <span className="text-xs font-medium">Peringatan Interaksi</span>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center space-x-2 mt-2 text-xs text-gray-500">
                        {prescription.verified_date && (
                          <span>Terverifikasi: {formatDateTime(prescription.verified_date)}</span>
                        )}
                        {prescription.dispensed_date && (
                          <span>Disiapkan: {formatDateTime(prescription.dispensed_date)}</span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      {prescription.status === "pending" && (
                        <button
                          onClick={() => handleVerifyPrescription(prescription.id)}
                          className="p-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200"
                          title="Verifikasi"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                      )}

                      <button
                        onClick={() => {
                          setSelectedPrescription(prescription);
                          setShowDetailModal(true);
                        }}
                        className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                        title="Lihat Detail"
                      >
                        <Eye className="w-4 h-4" />
                      </button>

                      <button
                        onClick={() => handlePrintPrescription(prescription.id)}
                        className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                        title="Cetak"
                      >
                        <Printer className="w-4 h-4" />
                      </button>

                      {prescription.status === "pending" && (
                        <button
                          onClick={() => handleCancelPrescription(prescription.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                          title="Batalkan"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      )}

                      <button
                        onClick={() => setExpandedPrescription(isExpanded ? null : prescription.id)}
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
                    <h4 className="text-sm font-semibold text-gray-900 mb-3">Obat-obatan</h4>
                    <div className="space-y-3">
                      {prescription.items.map((item) => (
                        <div key={item.id} className="bg-white rounded-lg p-3 border border-gray-200">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-1">
                                <Pill className="w-4 h-4 text-blue-600" />
                                <p className="font-medium text-gray-900">{item.medication_name}</p>
                                {item.generic_name && (
                                  <span className="text-xs text-gray-500">({item.generic_name})</span>
                                )}
                              </div>

                              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-gray-600 mt-2">
                                <div>
                                  <span className="font-medium">Dosis:</span> {item.dosage}
                                </div>
                                <div>
                                  <span className="font-medium">Frekuensi:</span> {item.frequency}
                                </div>
                                <div>
                                  <span className="font-medium">Durasi:</span> {item.duration}
                                </div>
                                <div>
                                  <span className="font-medium">Jumlah:</span> {item.quantity} {item.unit}
                                </div>
                              </div>

                              {item.instructions && (
                                <div className="mt-2 text-sm text-gray-700">
                                  <span className="font-medium">Instruksi:</span> {item.instructions}
                                </div>
                              )}

                              {item.warnings && item.warnings.length > 0 && (
                                <div className="mt-2 p-2 bg-orange-50 border border-orange-200 rounded">
                                  {item.warnings.map((warning, idx) => (
                                    <div key={idx} className="flex items-center space-x-1 text-xs text-orange-800">
                                      <AlertTriangle className="w-3 h-3" />
                                      <span>{warning}</span>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>

                            <span
                              className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                                item.status === "active"
                                  ? "bg-green-100 text-green-800"
                                  : item.status === "dispensed"
                                  ? "bg-blue-100 text-blue-800"
                                  : "bg-red-100 text-red-800"
                              }`}
                            >
                              {item.status === "active" ? "Aktif" : item.status === "dispensed" ? "Disiapkan" : "Dibatalkan"}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>

                    {prescription.notes && (
                      <div className="mt-3 p-3 bg-white rounded-lg border border-gray-200">
                        <p className="text-sm">
                          <span className="font-medium text-gray-900">Catatan:</span> {prescription.notes}
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
