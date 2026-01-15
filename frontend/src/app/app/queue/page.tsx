"use client";

/**
 * Patient Queue Management Page - STORY-010: Queue Management System
 *
 * Comprehensive queue management for staff including:
 * - View active queue by department/polyclinic
 * - Call next patient
 * - Update queue status
 * - Queue statistics
 * - Patient wait time tracking
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Users,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Volume2,
  SkipForward,
  Bell,
  Calendar,
  User,
  Phone,
  Filter,
  Search,
  ChevronRight,
} from "lucide-react";

// Types
interface QueueItem {
  id: number;
  patient_id: number;
  patient_name: string;
  medical_record_number: string;
  queue_number: string;
  department: string;
  polyclinic: string;
  appointment_id?: number;
  appointment_time?: string;
  check_in_time: string;
  status: "waiting" | "called" | "serving" | "completed" | "skipped" | "cancelled";
  priority: "normal" | "urgent" | "emergency";
  doctor_id?: number;
  doctor_name?: string;
  estimated_wait_time?: number;
  service_type?: string;
  notes?: string;
}

interface QueueStats {
  total_waiting: number;
  total_called: number;
  total_serving: number;
  total_completed: number;
  avg_wait_time: number;
  longest_wait: number;
}

export default function QueueManagementPage() {
  const router = useRouter();
  const [queueItems, setQueueItems] = useState<QueueItem[]>([]);
  const [stats, setStats] = useState<QueueStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDepartment, setSelectedDepartment] = useState<string>("all");
  const [selectedPolyclinic, setSelectedPolyclinic] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    fetchQueueData();
  }, [selectedDepartment, selectedPolyclinic]);

  const fetchQueueData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const params = new URLSearchParams();
      if (selectedDepartment !== "all") params.append("department", selectedDepartment);
      if (selectedPolyclinic !== "all") params.append("polyclinic", selectedPolyclinic);

      const response = await fetch(
        `/api/v1/queue/active?${params}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setQueueItems(data.items || []);
        setStats(data.stats || null);
      } else {
        console.error("Failed to fetch queue data");
      }
    } catch (error) {
      console.error("Failed to fetch queue data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCallPatient = async (queueId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/queue/${queueId}/call`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        fetchQueueData();
        // Play sound or show notification
        alert(`Pasien dipanggil!`);
      } else {
        alert("Gagal memanggil pasien");
      }
    } catch (error) {
      console.error("Failed to call patient:", error);
      alert("Gagal memanggil pasien");
    }
  };

  const handleStartService = async (queueId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/queue/${queueId}/serve`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        fetchQueueData();
      } else {
        alert("Gagal memulai pelayanan");
      }
    } catch (error) {
      console.error("Failed to start service:", error);
      alert("Gagal memulai pelayanan");
    }
  };

  const handleCompleteService = async (queueId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/queue/${queueId}/complete`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        fetchQueueData();
      } else {
        alert("Gagal menyelesaikan pelayanan");
      }
    } catch (error) {
      console.error("Failed to complete service:", error);
      alert("Gagal menyelesaikan pelayanan");
    }
  };

  const handleSkipPatient = async (queueId: number) => {
    if (!confirm("Lewati pasien ini? Pasien akan dipindahkan ke akhir antrian.")) {
      return;
    }

    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/queue/${queueId}/skip`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        fetchQueueData();
      } else {
        alert("Gagal melewati pasien");
      }
    } catch (error) {
      console.error("Failed to skip patient:", error);
      alert("Gagal melewati pasien");
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "waiting":
        return "bg-blue-100 text-blue-800";
      case "called":
        return "bg-yellow-100 text-yellow-800";
      case "serving":
        return "bg-purple-100 text-purple-800";
      case "completed":
        return "bg-green-100 text-green-800";
      case "skipped":
        return "bg-orange-100 text-orange-800";
      case "cancelled":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "waiting":
        return "Menunggu";
      case "called":
        return "Dipanggil";
      case "serving":
        return "Dilayani";
      case "completed":
        return "Selesai";
      case "skipped":
        return "Dilewati";
      case "cancelled":
        return "Batal";
      default:
        return status;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "emergency":
        return "bg-red-100 text-red-800 border-red-300";
      case "urgent":
        return "bg-orange-100 text-orange-800 border-orange-300";
      case "normal":
        return "bg-blue-100 text-blue-800 border-blue-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case "emergency":
        return "🔴 Gawat Darurat";
      case "urgent":
        return "🟠 Urgent";
      case "normal":
        return "🔵 Biasa";
      default:
        return priority;
    }
  };

  const formatWaitTime = (checkInTime: string) => {
    const checkIn = new Date(checkInTime);
    const now = new Date();
    const diff = Math.floor((now.getTime() - checkIn.getTime()) / 1000 / 60);

    if (diff < 1) return "Baru saja";
    if (diff < 60) return `${diff} menit`;
    const hours = Math.floor(diff / 60);
    const minutes = diff % 60;
    return `${hours}j ${minutes}m`;
  };

  const filteredQueueItems = queueItems.filter((item) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        item.patient_name.toLowerCase().includes(query) ||
        item.medical_record_number.toLowerCase().includes(query) ||
        item.queue_number.toLowerCase().includes(query)
      );
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Antrian Pasien</h1>
          <p className="text-sm text-gray-600 mt-1">Kelola antrian pasien secara real-time</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => router.push("/app/queue/settings")}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
          >
            <Filter className="w-4 h-4 mr-2" />
            Pengaturan
          </button>
          <button
            onClick={fetchQueueData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <Bell className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Menunggu</p>
                <p className="text-2xl font-bold text-blue-600">{stats.total_waiting}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Dipanggil</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.total_called}</p>
              </div>
              <Bell className="w-8 h-8 text-yellow-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Dilayani</p>
                <p className="text-2xl font-bold text-purple-600">{stats.total_serving}</p>
              </div>
              <Clock className="w-8 h-8 text-purple-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Selesai</p>
                <p className="text-2xl font-bold text-green-600">{stats.total_completed}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Rata-rata Tunggu</p>
                <p className="text-2xl font-bold text-gray-900">{stats.avg_wait_time}m</p>
              </div>
              <Clock className="w-8 h-8 text-gray-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Terlama Lama</p>
                <p className="text-2xl font-bold text-orange-600">{stats.longest_wait}m</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-orange-600" />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap items-center gap-4">
          {/* Department Filter */}
          <div className="flex-1 min-w-48">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Departemen
            </label>
            <select
              value={selectedDepartment}
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Semua Departemen</option>
              <option value="poli-umum">Poli Umum</option>
              <option value="poli-anak">Poli Anak</option>
              <option value="poli-kandungan">Poli Kandungan</option>
              <option value="poli-penyakit-dalam">Poli Penyakit Dalam</option>
              <option value="poli-bedah">Poli Bedah</option>
              <option value="poli-mata">Poli Mata</option>
              <option value="poli-tht">Poli THT</option>
              <option value="igd">IGD</option>
            </select>
          </div>

          {/* Search */}
          <div className="flex-1 min-w-64">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cari Pasien
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Nama atau No. RM..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Queue List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredQueueItems.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Users className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada antrian</h3>
          <p className="text-gray-600">
            {searchQuery || selectedDepartment !== "all"
              ? "Tidak ada antrian yang sesuai dengan filter"
              : "Tidak ada pasien dalam antrian saat ini"}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    No. Antrian
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Pasien
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Poli / Departemen
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Waktu Tunggu
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Prioritas
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
                {filteredQueueItems
                  .sort((a, b) => {
                    // Sort by priority (emergency first, then by check-in time)
                    const priorityOrder = { emergency: 0, urgent: 1, normal: 2 };
                    const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
                    if (priorityDiff !== 0) return priorityDiff;
                    return new Date(a.check_in_time).getTime() - new Date(b.check_in_time).getTime();
                  })
                  .map((item) => (
                    <tr
                      key={item.id}
                      className={`hover:bg-gray-50 ${
                        item.status === "called" ? "bg-yellow-50" : ""
                      } ${
                        item.priority === "emergency" ? "bg-red-50" : ""
                      }`}
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-blue-600 text-white rounded-lg flex items-center justify-center font-bold text-lg">
                            {item.queue_number}
                          </div>
                        </div>
                      </td>

                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                            <User className="w-5 h-5 text-gray-600" />
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{item.patient_name}</p>
                            <p className="text-sm text-gray-500">{item.medical_record_number}</p>
                          </div>
                        </div>
                      </td>

                      <td className="px-6 py-4">
                        <p className="text-sm text-gray-900">{item.polyclinic || item.department}</p>
                        {item.doctor_name && (
                          <p className="text-xs text-gray-500">{item.doctor_name}</p>
                        )}
                      </td>

                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          <Clock className="w-4 h-4 text-gray-500" />
                          <span className="text-sm text-gray-700">
                            {formatWaitTime(item.check_in_time)}
                          </span>
                        </div>
                        {item.appointment_time && (
                          <p className="text-xs text-gray-500 mt-1">
                            Jadwal: {item.appointment_time}
                          </p>
                        )}
                      </td>

                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(
                            item.priority
                          )}`}
                        >
                          {getPriorityLabel(item.priority)}
                        </span>
                      </td>

                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                            item.status
                          )}`}
                        >
                          {getStatusLabel(item.status)}
                        </span>
                      </td>

                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end space-x-2">
                          {item.status === "waiting" && (
                            <button
                              onClick={() => handleCallPatient(item.id)}
                              className="p-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200"
                              title="Panggil Pasien"
                            >
                              <Volume2 className="w-4 h-4" />
                            </button>
                          )}

                          {item.status === "called" && (
                            <button
                              onClick={() => handleStartService(item.id)}
                              className="p-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200"
                              title="Mulai Layani"
                            >
                              <Clock className="w-4 h-4" />
                            </button>
                          )}

                          {item.status === "serving" && (
                            <button
                              onClick={() => handleCompleteService(item.id)}
                              className="p-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200"
                              title="Selesaikan"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                          )}

                          {(item.status === "waiting" || item.status === "called") && (
                            <button
                              onClick={() => handleSkipPatient(item.id)}
                              className="p-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200"
                              title="Lewati"
                            >
                              <SkipForward className="w-4 h-4" />
                            </button>
                          )}

                          <button
                            onClick={() => router.push(`/app/patients/${item.patient_id}`)}
                            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                            title="Lihat Profil"
                          >
                            <ChevronRight className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
