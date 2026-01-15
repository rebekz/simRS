"use client";

/**
 * Staff Shift Scheduling Page - STORY-020-02: Shift Scheduling & Swap Requests
 *
 * Comprehensive shift management for staff including:
 * - View personal shift calendar (daily, weekly, monthly views)
 * - View shift details (date, time, department, role, supervisor)
 * - Request shift swaps with colleagues
 * - Accept or decline shift swap requests
 * - View available shifts for pickup (open shifts)
 * - Request overtime assignments
 * - Submit availability preferences
 * - View upcoming shift assignments
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Calendar,
  Clock,
  MapPin,
  User,
  RefreshCw,
  Plus,
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  XCircle,
  AlertCircle,
  Users,
  Briefcase,
  Timer,
  Send,
  Eye,
  ChevronDown,
  Calendar as CalendarIcon,
} from "lucide-react";

// Types
interface Shift {
  id: number;
  staff_id: number;
  shift_type: "morning" | "afternoon" | "night" | "special";
  date: string;
  start_time: string;
  end_time: string;
  department: string;
  unit?: string;
  role: string;
  supervisor_id?: number;
  supervisor_name?: string;
  status: "scheduled" | "in_progress" | "completed" | "missed" | "cancelled";
  is_overtime: boolean;
  notes?: string;
  break_duration?: number;
  location?: string;
}

interface SwapRequest {
  id: number;
  requester_id: number;
  requester_name: string;
  requester_shift_id: number;
  requester_shift_date: string;
  requester_shift_time: string;
  target_id: number;
  target_name: string;
  target_shift_id: number;
  target_shift_date: string;
  target_shift_time: string;
  reason: string;
  status: "pending" | "accepted" | "rejected" | "cancelled";
  created_at: string;
  responded_at?: string;
  response_note?: string;
}

interface OpenShift {
  id: number;
  shift_id: number;
  date: string;
  start_time: string;
  end_time: string;
  department: string;
  unit?: string;
  role: string;
  required_qualifications: string[];
  is_overtime: boolean;
  hourly_rate?: number;
  notes?: string;
}

interface AvailabilityPreference {
  id: number;
  staff_id: number;
  day_of_week: number;
  preferred_shift_type: "morning" | "afternoon" | "night" | "any";
  unavailable: boolean;
  notes?: string;
}

type ViewMode = "day" | "week" | "month";
type FilterStatus = "all" | "scheduled" | "in_progress" | "completed" | "missed" | "cancelled";

export default function StaffSchedulePage() {
  const router = useRouter();
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [swapRequests, setSwapRequests] = useState<SwapRequest[]>([]);
  const [openShifts, setOpenShifts] = useState<OpenShift[]>([]);
  const [loading, setLoading] = useState(true);

  // View controls
  const [viewMode, setViewMode] = useState<ViewMode>("week");
  const [currentDate, setCurrentDate] = useState(new Date());
  const [statusFilter, setStatusFilter] = useState<FilterStatus>("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Modal states
  const [showSwapModal, setShowSwapModal] = useState(false);
  const [showOvertimeModal, setShowOvertimeModal] = useState(false);
  const [showAvailabilityModal, setShowAvailabilityModal] = useState(false);
  const [selectedShift, setSelectedShift] = useState<Shift | null>(null);

  useEffect(() => {
    fetchScheduleData();
  }, [currentDate, viewMode, statusFilter]);

  const fetchScheduleData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const params = new URLSearchParams();
      params.append("view", viewMode);
      params.append("date", currentDate.toISOString().split("T")[0]);
      if (statusFilter !== "all") params.append("status", statusFilter);

      const [shiftsRes, swapsRes, openRes] = await Promise.all([
        fetch(`/api/v1/staff/schedule/shifts?${params}`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch("/api/v1/staff/schedule/swap-requests", {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch("/api/v1/staff/schedule/open-shifts", {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (shiftsRes.ok) {
        const shiftsData = await shiftsRes.json();
        setShifts(shiftsData.items || []);
      }

      if (swapsRes.ok) {
        const swapsData = await swapsRes.json();
        setSwapRequests(swapsData.items || []);
      }

      if (openRes.ok) {
        const openData = await openRes.json();
        setOpenShifts(openData.items || []);
      }
    } catch (error) {
      console.error("Failed to fetch schedule data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestSwap = async (shiftId: number, targetStaffId: number, reason: string) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch("/api/v1/staff/schedule/swap-requests", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          shift_id: shiftId,
          target_staff_id: targetStaffId,
          reason: reason,
        }),
      });

      if (response.ok) {
        fetchScheduleData();
        setShowSwapModal(false);
        alert("Permintaan tukar shift berhasil dikirim");
      } else {
        alert("Gagal mengirim permintaan tukar shift");
      }
    } catch (error) {
      console.error("Failed to request swap:", error);
      alert("Gagal mengirim permintaan tukar shift");
    }
  };

  const handleRespondSwap = async (swapId: number, action: "accept" | "reject", note?: string) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/staff/schedule/swap-requests/${swapId}/${action}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ response_note: note }),
      });

      if (response.ok) {
        fetchScheduleData();
        alert(action === "accept" ? "Tukar shift diterima" : "Tukar shift ditolak");
      } else {
        alert("Gagal merespons permintaan tukar shift");
      }
    } catch (error) {
      console.error("Failed to respond to swap:", error);
      alert("Gagal merespons permintaan tukar shift");
    }
  };

  const handlePickupShift = async (openShiftId: number) => {
    if (!confirm("Apakah Anda yakin ingin mengambil shift ini?")) {
      return;
    }

    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/staff/schedule/open-shifts/${openShiftId}/pickup`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        fetchScheduleData();
        alert("Shift berhasil diambil");
      } else {
        alert("Gagal mengambil shift");
      }
    } catch (error) {
      console.error("Failed to pickup shift:", error);
      alert("Gagal mengambil shift");
    }
  };

  const getShiftTypeLabel = (type: string) => {
    switch (type) {
      case "morning":
        return "Pagi";
      case "afternoon":
        return "Siang";
      case "night":
        return "Malam";
      case "special":
        return "Khusus";
      default:
        return type;
    }
  };

  const getShiftTypeColor = (type: string) => {
    switch (type) {
      case "morning":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "afternoon":
        return "bg-orange-100 text-orange-800 border-orange-300";
      case "night":
        return "bg-indigo-100 text-indigo-800 border-indigo-300";
      case "special":
        return "bg-purple-100 text-purple-800 border-purple-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "scheduled":
        return "bg-blue-100 text-blue-800";
      case "in_progress":
        return "bg-yellow-100 text-yellow-800";
      case "completed":
        return "bg-green-100 text-green-800";
      case "missed":
        return "bg-red-100 text-red-800";
      case "cancelled":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "scheduled":
        return "Terjadwal";
      case "in_progress":
        return "Sedang Berlangsung";
      case "completed":
        return "Selesai";
      case "missed":
        return "Terlewat";
      case "cancelled":
        return "Dibatalkan";
      default:
        return status;
    }
  };

  const getSwapStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "accepted":
        return "bg-green-100 text-green-800";
      case "rejected":
        return "bg-red-100 text-red-800";
      case "cancelled":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getSwapStatusLabel = (status: string) => {
    switch (status) {
      case "pending":
        return "Menunggu";
      case "accepted":
        return "Diterima";
      case "rejected":
        return "Ditolak";
      case "cancelled":
        return "Dibatalkan";
      default:
        return status;
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

  const navigateDate = (direction: "prev" | "next") => {
    const newDate = new Date(currentDate);
    switch (viewMode) {
      case "day":
        newDate.setDate(newDate.getDate() + (direction === "next" ? 1 : -1));
        break;
      case "week":
        newDate.setDate(newDate.getDate() + (direction === "next" ? 7 : -7));
        break;
      case "month":
        newDate.setMonth(newDate.getMonth() + (direction === "next" ? 1 : -1));
        break;
    }
    setCurrentDate(newDate);
  };

  const filteredShifts = shifts.filter((shift) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        shift.department.toLowerCase().includes(query) ||
        shift.role.toLowerCase().includes(query) ||
        (shift.supervisor_name && shift.supervisor_name.toLowerCase().includes(query)) ||
        (shift.location && shift.location.toLowerCase().includes(query))
      );
    }
    return true;
  });

  const upcomingShifts = shifts.filter((s) => {
    const shiftDate = new Date(s.date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return shiftDate >= today && s.status === "scheduled";
  }).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()).slice(0, 5);

  const pendingSwaps = swapRequests.filter((s) => s.status === "pending");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Jadwal Shift</h1>
          <p className="text-sm text-gray-600 mt-1">Kelola jadwal dan permintaan tukar shift</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowAvailabilityModal(true)}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
          >
            <Timer className="w-4 h-4 mr-2" />
            Ketersediaan
          </button>
          <button
            onClick={() => setShowOvertimeModal(true)}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Lembur
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Shift Bulan Ini</p>
              <p className="text-2xl font-bold text-gray-900">
                {shifts.filter((s) => {
                  const shiftDate = new Date(s.date);
                  const now = new Date();
                  return shiftDate.getMonth() === now.getMonth() && shiftDate.getFullYear() === now.getFullYear();
                }).length}
              </p>
            </div>
            <Calendar className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Shift Minggu Ini</p>
              <p className="text-2xl font-bold text-gray-900">
                {shifts.filter((s) => {
                  const shiftDate = new Date(s.date);
                  const now = new Date();
                  const weekStart = new Date(now);
                  weekStart.setDate(now.getDate() - now.getDay());
                  const weekEnd = new Date(weekStart);
                  weekEnd.setDate(weekStart.getDate() + 6);
                  return shiftDate >= weekStart && shiftDate <= weekEnd;
                }).length}
              </p>
            </div>
            <Briefcase className="w-8 h-8 text-purple-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Permintaan Tukar</p>
              <p className="text-2xl font-bold text-yellow-600">{pendingSwaps.length}</p>
            </div>
            <RefreshCw className="w-8 h-8 text-yellow-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Shift Tersedia</p>
              <p className="text-2xl font-bold text-green-600">{openShifts.length}</p>
            </div>
            <Users className="w-8 h-8 text-green-600" />
          </div>
        </div>
      </div>

      {/* Upcoming Shifts */}
      {upcomingShifts.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Shift Mendatang</h2>
          <div className="space-y-3">
            {upcomingShifts.map((shift) => (
              <div key={shift.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-600 text-white rounded-lg flex items-center justify-center">
                    <CalendarIcon className="w-6 h-6" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{formatDate(shift.date)}</p>
                    <p className="text-sm text-gray-600">
                      {shift.start_time} - {shift.end_time}
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium border ${getShiftTypeColor(
                      shift.shift_type
                    )}`}
                  >
                    {getShiftTypeLabel(shift.shift_type)}
                  </span>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{shift.department}</p>
                    <p className="text-xs text-gray-500">{shift.role}</p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setSelectedShift(shift);
                    setShowSwapModal(true);
                  }}
                  className="px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-lg text-sm flex items-center"
                >
                  <RefreshCw className="w-4 h-4 mr-1" />
                  Tukar
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Swap Requests */}
      {swapRequests.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Permintaan Tukar Shift</h2>
          <div className="space-y-4">
            {swapRequests.map((swap) => (
              <div key={swap.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${getSwapStatusColor(
                          swap.status
                        )}`}
                      >
                        {getSwapStatusLabel(swap.status)}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(swap.created_at).toLocaleDateString("id-ID")}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-blue-50 rounded-lg p-3">
                        <p className="text-xs text-blue-600 font-medium mb-1">Shift Anda</p>
                        <p className="font-medium text-gray-900">{formatDate(swap.requester_shift_date)}</p>
                        <p className="text-sm text-gray-600">{swap.requester_shift_time}</p>
                      </div>

                      <div className="bg-green-50 rounded-lg p-3">
                        <p className="text-xs text-green-600 font-medium mb-1">Shift Target</p>
                        <p className="font-medium text-gray-900">{formatDate(swap.target_shift_date)}</p>
                        <p className="text-sm text-gray-600">{swap.target_shift_time}</p>
                      </div>
                    </div>

                    {swap.reason && (
                      <div className="mt-3">
                        <p className="text-sm text-gray-600">
                          <span className="font-medium">Alasan:</span> {swap.reason}
                        </p>
                      </div>
                    )}

                    {swap.response_note && (
                      <div className="mt-3">
                        <p className="text-sm text-gray-600">
                          <span className="font-medium">Respon:</span> {swap.response_note}
                        </p>
                      </div>
                    )}
                  </div>

                  {swap.status === "pending" && (
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => handleRespondSwap(swap.id, "accept")}
                        className="p-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200"
                        title="Terima"
                      >
                        <CheckCircle className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleRespondSwap(swap.id, "reject")}
                        className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                        title="Tolak"
                      >
                        <XCircle className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Schedule View Controls */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            {/* View Mode */}
            <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode("day")}
                className={`px-3 py-1 rounded-md text-sm font-medium ${
                  viewMode === "day" ? "bg-white text-blue-600 shadow" : "text-gray-600"
                }`}
              >
                Hari
              </button>
              <button
                onClick={() => setViewMode("week")}
                className={`px-3 py-1 rounded-md text-sm font-medium ${
                  viewMode === "week" ? "bg-white text-blue-600 shadow" : "text-gray-600"
                }`}
              >
                Minggu
              </button>
              <button
                onClick={() => setViewMode("month")}
                className={`px-3 py-1 rounded-md text-sm font-medium ${
                  viewMode === "month" ? "bg-white text-blue-600 shadow" : "text-gray-600"
                }`}
              >
                Bulan
              </button>
            </div>

            {/* Navigation */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => navigateDate("prev")}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="text-sm font-medium text-gray-900 min-w-48 text-center">
                {currentDate.toLocaleDateString("id-ID", {
                  month: "long",
                  year: "numeric",
                  ...(viewMode === "day" && { day: "numeric" }),
                })}
              </span>
              <button
                onClick={() => navigateDate("next")}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as FilterStatus)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
            >
              <option value="all">Semua Status</option>
              <option value="scheduled">Terjadwal</option>
              <option value="in_progress">Sedang Berlangsung</option>
              <option value="completed">Selesai</option>
              <option value="missed">Terlewat</option>
              <option value="cancelled">Dibatalkan</option>
            </select>

            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Cari..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm w-64"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Shift List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredShifts.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Calendar className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada shift</h3>
          <p className="text-gray-600">
            {searchQuery || statusFilter !== "all"
              ? "Tidak ada shift yang sesuai dengan filter"
              : "Tidak ada shift yang dijadwalkan untuk periode ini"}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Tanggal
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Waktu
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Departemen
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Peran
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Supervisor
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
                {filteredShifts.map((shift) => (
                  <tr key={shift.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <CalendarIcon className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{formatDate(shift.date)}</p>
                          {shift.is_overtime && (
                            <span className="text-xs text-orange-600">Lembur</span>
                          )}
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-900">
                          {shift.start_time} - {shift.end_time}
                        </span>
                      </div>
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border mt-1 ${getShiftTypeColor(
                          shift.shift_type
                        )}`}
                      >
                        {getShiftTypeLabel(shift.shift_type)}
                      </span>
                    </td>

                    <td className="px-6 py-4">
                      <p className="text-sm font-medium text-gray-900">{shift.department}</p>
                      {shift.unit && (
                        <p className="text-xs text-gray-500">{shift.unit}</p>
                      )}
                      {shift.location && (
                        <div className="flex items-center space-x-1 mt-1">
                          <MapPin className="w-3 h-3 text-gray-400" />
                          <span className="text-xs text-gray-500">{shift.location}</span>
                        </div>
                      )}
                    </td>

                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-900">{shift.role}</p>
                    </td>

                    <td className="px-6 py-4">
                      {shift.supervisor_name ? (
                        <div className="flex items-center space-x-2">
                          <User className="w-4 h-4 text-gray-400" />
                          <span className="text-sm text-gray-700">{shift.supervisor_name}</span>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">-</span>
                      )}
                    </td>

                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          shift.status
                        )}`}
                      >
                        {getStatusLabel(shift.status)}
                      </span>
                    </td>

                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => {
                            setSelectedShift(shift);
                            setShowSwapModal(true);
                          }}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                          title="Tukar Shift"
                        >
                          <RefreshCw className="w-4 h-4" />
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

      {/* Open Shifts */}
      {openShifts.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Shift Tersedia</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {openShifts.map((openShift) => (
              <div key={openShift.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-medium text-gray-900">{formatDate(openShift.date)}</p>
                    <p className="text-sm text-gray-600">
                      {openShift.start_time} - {openShift.end_time}
                    </p>
                  </div>
                  {openShift.is_overtime && (
                    <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs font-medium">
                      Lembur
                    </span>
                  )}
                </div>

                <div className="space-y-2 mb-4">
                  <div>
                    <p className="text-xs text-gray-500">Departemen</p>
                    <p className="text-sm font-medium text-gray-900">{openShift.department}</p>
                    {openShift.unit && (
                      <p className="text-xs text-gray-600">{openShift.unit}</p>
                    )}
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Peran</p>
                    <p className="text-sm text-gray-900">{openShift.role}</p>
                  </div>
                  {openShift.required_qualifications && openShift.required_qualifications.length > 0 && (
                    <div>
                      <p className="text-xs text-gray-500">Kualifikasi</p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {openShift.required_qualifications.map((qual, idx) => (
                          <span key={idx} className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs">
                            {qual}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {openShift.hourly_rate && (
                    <div>
                      <p className="text-xs text-gray-500">Rate per Jam</p>
                      <p className="text-sm font-medium text-green-600">
                        IDR {openShift.hourly_rate.toLocaleString("id-ID")}
                      </p>
                    </div>
                  )}
                  {openShift.notes && (
                    <div>
                      <p className="text-xs text-gray-500">Catatan</p>
                      <p className="text-xs text-gray-700">{openShift.notes}</p>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => handlePickupShift(openShift.id)}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Ambil Shift
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Swap Modal (Placeholder) */}
      {showSwapModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Tukar Shift</h3>
            <p className="text-sm text-gray-600 mb-4">
              Fitur ini akan memungkinkan Anda memilih kolega untuk menukar shift.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowSwapModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Tutup
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Availability Modal (Placeholder) */}
      {showAvailabilityModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Preferensi Ketersediaan</h3>
            <p className="text-sm text-gray-600 mb-4">
              Atur preferensi ketersediaan shift Anda (hari dan jenis shift yang diinginkan).
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowAvailabilityModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Tutup
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Overtime Modal (Placeholder) */}
      {showOvertimeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Permintaan Lembur</h3>
            <p className="text-sm text-gray-600 mb-4">
              Ajukan permintaan lembur untuk shift tertentu atau daftar untuk ketersediaan lembur.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowOvertimeModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Tutup
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
