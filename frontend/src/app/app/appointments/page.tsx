"use client";

/**
 * Staff Appointments Management Page
 *
 * Comprehensive appointment management for staff including:
 * - View all appointments with filters
 * - Create new appointments
 * - Edit existing appointments
 * - Cancel appointments
 * - View appointment details
 * - Manage appointment status
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Calendar,
  Clock,
  User,
  Phone,
  Mail,
  Plus,
  Search,
  Filter,
  ChevronDown,
  CheckCircle,
  XCircle,
  Clock as PendingIcon,
  Eye,
  Edit,
  Trash2,
  Video,
  Stethoscope,
} from "lucide-react";

// Types
interface Appointment {
  id: number;
  patient_id: number;
  patient_name: string;
  patient_phone?: string;
  patient_email?: string;
  doctor_id: number;
  doctor_name: string;
  department: string;
  appointment_date: string;
  appointment_time: string;
  end_time?: string;
  appointment_type: "consultation" | "follow_up" | "procedure" | "vaccination" | "telemedicine";
  status: "scheduled" | "confirmed" | "checked_in" | "in_progress" | "completed" | "cancelled" | "no_show";
  reason: string;
  notes?: string;
  created_at: string;
}

interface AppointmentListResponse {
  items: Appointment[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function StaffAppointmentsPage() {
  const router = useRouter();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [dateFilter, setDateFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    fetchAppointments();
  }, [currentPage, statusFilter, dateFilter, typeFilter]);

  const fetchAppointments = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const params = new URLSearchParams();
      params.append("page", currentPage.toString());
      params.append("page_size", "20");
      if (statusFilter !== "all") params.append("status", statusFilter);
      if (dateFilter !== "all") params.append("date_filter", dateFilter);
      if (typeFilter !== "all") params.append("appointment_type", typeFilter);
      if (searchQuery) params.append("search", searchQuery);

      const response = await fetch(
        `/api/v1/appointments?${params}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data: AppointmentListResponse = await response.json();
        setAppointments(data.items);
        setTotalPages(data.total_pages);
        setTotalCount(data.total);
      } else {
        console.error("Failed to fetch appointments");
      }
    } catch (error) {
      console.error("Failed to fetch appointments:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelAppointment = async (appointmentId: number) => {
    if (!confirm("Apakah Anda yakin ingin membatalkan janji temu ini?")) {
      return;
    }

    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/appointments/${appointmentId}/cancel`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        fetchAppointments();
      } else {
        alert("Gagal membatalkan janji temu");
      }
    } catch (error) {
      console.error("Failed to cancel appointment:", error);
      alert("Gagal membatalkan janji temu");
    }
  };

  const handleConfirmAppointment = async (appointmentId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/appointments/${appointmentId}/confirm`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        fetchAppointments();
      } else {
        alert("Gagal mengonfirmasi janji temu");
      }
    } catch (error) {
      console.error("Failed to confirm appointment:", error);
      alert("Gagal mengonfirmasi janji temu");
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "scheduled":
        return "bg-blue-100 text-blue-800";
      case "confirmed":
        return "bg-green-100 text-green-800";
      case "checked_in":
        return "bg-purple-100 text-purple-800";
      case "in_progress":
        return "bg-yellow-100 text-yellow-800";
      case "completed":
        return "bg-gray-100 text-gray-800";
      case "cancelled":
        return "bg-red-100 text-red-800";
      case "no_show":
        return "bg-orange-100 text-orange-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "scheduled":
        return "Terjadwal";
      case "confirmed":
        return "Dikonfirmasi";
      case "checked_in":
        return "Check-In";
      case "in_progress":
        return "Sedang Berlangsung";
      case "completed":
        return "Selesai";
      case "cancelled":
        return "Dibatalkan";
      case "no_show":
        return "Tidak Hadir";
      default:
        return status;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case "consultation":
        return "Konsultasi";
      case "follow_up":
        return "Kontrol";
      case "procedure":
        return "Tindakan";
      case "vaccination":
        return "Vaksinasi";
      case "telemedicine":
        return "Telemedicine";
      default:
        return type;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "consultation":
      case "follow_up":
        return <Stethoscope className="w-4 h-4" />;
      case "procedure":
        return <Clock className="w-4 h-4" />;
      case "vaccination":
        return <CheckCircle className="w-4 h-4" />;
      case "telemedicine":
        return <Video className="w-4 h-4" />;
      default:
        return <Calendar className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return "Hari Ini";
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return "Besok";
    } else {
      return date.toLocaleDateString("id-ID", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Janji Temu</h1>
          <p className="text-sm text-gray-600 mt-1">Kelola janji temu pasien</p>
        </div>
        <button
          onClick={() => router.push("/app/appointments/new")}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Buat Janji Temu
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Hari Ini</p>
              <p className="text-2xl font-bold text-gray-900">
                {appointments.filter((a) => {
                  const today = new Date().toDateString();
                  return new Date(a.appointment_date).toDateString() === today;
                }).length}
              </p>
            </div>
            <Calendar className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Terjadwal</p>
              <p className="text-2xl font-bold text-blue-600">
                {appointments.filter((a) => a.status === "scheduled").length}
              </p>
            </div>
            <PendingIcon className="w-8 h-8 text-yellow-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Dikonfirmasi</p>
              <p className="text-2xl font-bold text-green-600">
                {appointments.filter((a) => a.status === "confirmed").length}
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Selesai</p>
              <p className="text-2xl font-bold text-gray-600">
                {appointments.filter((a) => a.status === "completed").length}
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-gray-600" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-64">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Cari pasien atau dokter..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter") fetchAppointments();
              }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Semua Status</option>
            <option value="scheduled">Terjadwal</option>
            <option value="confirmed">Dikonfirmasi</option>
            <option value="checked_in">Check-In</option>
            <option value="in_progress">Sedang Berlangsung</option>
            <option value="completed">Selesai</option>
            <option value="cancelled">Dibatalkan</option>
            <option value="no_show">Tidak Hadir</option>
          </select>

          {/* Date Filter */}
          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Semua Tanggal</option>
            <option value="today">Hari Ini</option>
            <option value="tomorrow">Besok</option>
            <option value="week">Minggu Ini</option>
            <option value="month">Bulan Ini</option>
          </select>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Semua Tipe</option>
            <option value="consultation">Konsultasi</option>
            <option value="follow_up">Kontrol</option>
            <option value="procedure">Tindakan</option>
            <option value="vaccination">Vaksinasi</option>
            <option value="telemedicine">Telemedicine</option>
          </select>
        </div>
      </div>

      {/* Appointments List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : appointments.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Calendar className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada janji temu</h3>
          <p className="text-gray-600 mb-4">
            {searchQuery || statusFilter !== "all" || dateFilter !== "all" || typeFilter !== "all"
              ? "Tidak ada janji temu yang sesuai dengan filter"
              : "Belum ada janji temu yang dijadwalkan"}
          </p>
          <button
            onClick={() => router.push("/app/appointments/new")}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Buat Janji Temu Baru
          </button>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Pasien
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Dokter
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Tanggal & Waktu
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Tipe
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Aksi
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {appointments.map((appointment) => (
                    <tr key={appointment.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <User className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{appointment.patient_name}</p>
                            <div className="flex items-center space-x-2 mt-1">
                              {appointment.patient_phone && (
                                <p className="text-xs text-gray-500 flex items-center">
                                  <Phone className="w-3 h-3 mr-1" />
                                  {appointment.patient_phone}
                                </p>
                              )}
                              {appointment.patient_email && (
                                <p className="text-xs text-gray-500 flex items-center">
                                  <Mail className="w-3 h-3 mr-1" />
                                  {appointment.patient_email}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>

                      <td className="px-6 py-4">
                        <p className="text-sm font-medium text-gray-900">{appointment.doctor_name}</p>
                        <p className="text-xs text-gray-500">{appointment.department}</p>
                      </td>

                      <td className="px-6 py-4">
                        <p className="text-sm font-medium text-gray-900">
                          {formatDate(appointment.appointment_date)}
                        </p>
                        <p className="text-xs text-gray-500">
                          {appointment.appointment_time} - {appointment.end_time || "Selesai"}
                        </p>
                      </td>

                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          {getTypeIcon(appointment.appointment_type)}
                          <span className="text-sm text-gray-700">
                            {getTypeLabel(appointment.appointment_type)}
                          </span>
                        </div>
                      </td>

                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                            appointment.status
                          )}`}
                        >
                          {getStatusLabel(appointment.status)}
                        </span>
                      </td>

                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end space-x-2">
                          {appointment.status === "scheduled" && (
                            <button
                              onClick={() => handleConfirmAppointment(appointment.id)}
                              className="p-2 text-green-600 hover:bg-green-50 rounded-lg"
                              title="Konfirmasi"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                          )}

                          <button
                            onClick={() => router.push(`/app/appointments/${appointment.id}`)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                            title="Lihat Detail"
                          >
                            <Eye className="w-4 h-4" />
                          </button>

                          {appointment.status !== "completed" && appointment.status !== "cancelled" && (
                            <button
                              onClick={() => router.push(`/app/appointments/${appointment.id}/edit`)}
                              className="p-2 text-gray-600 hover:bg-gray-50 rounded-lg"
                              title="Edit"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                          )}

                          {appointment.status !== "completed" && appointment.status !== "cancelled" && (
                            <button
                              onClick={() => handleCancelAppointment(appointment.id)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                              title="Batalkan"
                            >
                              <XCircle className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <p className="text-sm text-gray-600">
                Menampilkan {(currentPage - 1) * 20 + 1} sampai{" "}
                {Math.min(currentPage * 20, totalCount)} dari {totalCount} janji temu
              </p>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Sebelumnya
                </button>

                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-lg">
                  {currentPage}
                </span>

                <button
                  onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Selanjutnya
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
