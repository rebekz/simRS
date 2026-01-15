"use client";

/**
 * Staff Leave Management Page - STORY-020-03: Leave & Sick Day Request Workflows
 *
 * Comprehensive leave management for staff including:
 * - Submit leave requests online (annual, sick, personal, unpaid)
 * - Select leave type and dates from calendar
 * - Upload supporting documents (medical certificates)
 * - View leave balance (annual, sick, personal, carried over)
 * - Check leave eligibility and accruals
 * - Track request status (pending, approved, rejected, cancelled)
 * - View leave history
 * - Cancel leave requests before approval
 * - Leave calendar (team leave overview)
 * - Multi-level approval workflow tracking
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Calendar,
  Clock,
  FileText,
  CheckCircle,
  XCircle,
  AlertCircle,
  Plus,
  Search,
  Filter,
  Download,
  Upload,
  Send,
  Eye,
  Trash2,
  CalendarDays,
  Info,
  TrendingUp,
  Users,
} from "lucide-react";

// Types
interface LeaveRequest {
  id: number;
  staff_id: number;
  leave_type: "annual" | "sick" | "personal" | "unpaid" | "maternity" | "paternity" | "special";
  start_date: string;
  end_date: string;
  total_days: number;
  reason: string;
  status: "pending" | "approved" | "rejected" | "cancelled";
  attachment_url?: string;
  created_at: string;
  updated_at: string;
  approver?: {
    id: number;
    name: string;
    role: string;
  };
  approval_notes?: string;
  approval_date?: string;
  balance_before?: number;
  balance_after?: number;
}

interface LeaveBalance {
  staff_id: number;
  annual: {
    total: number;
    used: number;
    remaining: number;
    carried_over: number;
  };
  sick: {
    total: number;
    used: number;
    remaining: number;
  };
  personal: {
    total: number;
    used: number;
    remaining: number;
  };
  next_accrual_date?: string;
  accrual_period: string;
}

interface TeamLeave {
  id: number;
  staff_id: number;
  staff_name: string;
  staff_role: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  status: string;
}

type LeaveType = "annual" | "sick" | "personal" | "unpaid" | "maternity" | "paternity" | "special";
type FilterStatus = "all" | "pending" | "approved" | "rejected" | "cancelled";

export default function StaffLeavePage() {
  const router = useRouter();
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [leaveBalance, setLeaveBalance] = useState<LeaveBalance | null>(null);
  const [teamLeave, setTeamLeave] = useState<TeamLeave[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [statusFilter, setStatusFilter] = useState<FilterStatus>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Modal states
  const [showNewRequestModal, setShowNewRequestModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<LeaveRequest | null>(null);

  // New request form
  const [newRequest, setNewRequest] = useState({
    leave_type: "annual" as LeaveType,
    start_date: "",
    end_date: "",
    reason: "",
    attachment: null as File | null,
  });

  useEffect(() => {
    fetchLeaveData();
  }, [statusFilter, typeFilter]);

  const fetchLeaveData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const params = new URLSearchParams();
      if (statusFilter !== "all") params.append("status", statusFilter);
      if (typeFilter !== "all") params.append("leave_type", typeFilter);

      const [requestsRes, balanceRes, teamRes] = await Promise.all([
        fetch(`/api/v1/staff/leave/requests?${params}`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch("/api/v1/staff/leave/balance", {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch("/api/v1/staff/leave/team", {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (requestsRes.ok) {
        const requestsData = await requestsRes.json();
        setLeaveRequests(requestsData.items || []);
      }

      if (balanceRes.ok) {
        const balanceData = await balanceRes.json();
        setLeaveBalance(balanceData);
      }

      if (teamRes.ok) {
        const teamData = await teamRes.json();
        setTeamLeave(teamData.items || []);
      }
    } catch (error) {
      console.error("Failed to fetch leave data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitLeave = async () => {
    if (!newRequest.start_date || !newRequest.end_date || !newRequest.reason) {
      alert("Harap lengkapi semua field wajib");
      return;
    }

    try {
      const token = localStorage.getItem("staff_access_token");
      const formData = new FormData();
      formData.append("leave_type", newRequest.leave_type);
      formData.append("start_date", newRequest.start_date);
      formData.append("end_date", newRequest.end_date);
      formData.append("reason", newRequest.reason);
      if (newRequest.attachment) {
        formData.append("attachment", newRequest.attachment);
      }

      const response = await fetch("/api/v1/staff/leave/requests", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        fetchLeaveData();
        setShowNewRequestModal(false);
        setNewRequest({
          leave_type: "annual",
          start_date: "",
          end_date: "",
          reason: "",
          attachment: null,
        });
        alert("Permintaan cuti berhasil diajukan");
      } else {
        const error = await response.json();
        alert(error.message || "Gagal mengajukan permintaan cuti");
      }
    } catch (error) {
      console.error("Failed to submit leave request:", error);
      alert("Gagal mengajukan permintaan cuti");
    }
  };

  const handleCancelRequest = async (requestId: number) => {
    if (!confirm("Apakah Anda yakin ingin membatalkan permintaan cuti ini?")) {
      return;
    }

    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/staff/leave/requests/${requestId}/cancel`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        fetchLeaveData();
        alert("Permintaan cuti dibatalkan");
      } else {
        alert("Gagal membatalkan permintaan cuti");
      }
    } catch (error) {
      console.error("Failed to cancel leave request:", error);
      alert("Gagal membatalkan permintaan cuti");
    }
  };

  const getLeaveTypeLabel = (type: string) => {
    switch (type) {
      case "annual":
        return "Cuti Tahunan";
      case "sick":
        return "Cuti Sakit";
      case "personal":
        return "Cuti Pribadi";
      case "unpaid":
        return "Cuti Tanpa Gaji";
      case "maternity":
        return "Cuti Melahirkan";
      case "paternity":
        return "Cuti Suami/Istri Melahirkan";
      case "special":
        return "Cuti Khusus";
      default:
        return type;
    }
  };

  const getLeaveTypeColor = (type: string) => {
    switch (type) {
      case "annual":
        return "bg-blue-100 text-blue-800 border-blue-300";
      case "sick":
        return "bg-red-100 text-red-800 border-red-300";
      case "personal":
        return "bg-purple-100 text-purple-800 border-purple-300";
      case "unpaid":
        return "bg-gray-100 text-gray-800 border-gray-300";
      case "maternity":
        return "bg-pink-100 text-pink-800 border-pink-300";
      case "paternity":
        return "bg-cyan-100 text-cyan-800 border-cyan-300";
      case "special":
        return "bg-orange-100 text-orange-800 border-orange-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "approved":
        return "bg-green-100 text-green-800";
      case "rejected":
        return "bg-red-100 text-red-800";
      case "cancelled":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "pending":
        return "Menunggu";
      case "approved":
        return "Disetujui";
      case "rejected":
        return "Ditolak";
      case "cancelled":
        return "Dibatalkan";
      default:
        return status;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "pending":
        return <Clock className="w-4 h-4" />;
      case "approved":
        return <CheckCircle className="w-4 h-4" />;
      case "rejected":
        return <XCircle className="w-4 h-4" />;
      case "cancelled":
        return <XCircle className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("id-ID", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const formatShortDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("id-ID", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };

  const calculateDuration = (startDate: string, endDate: string) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end.getTime() - start.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    return diffDays;
  };

  const filteredRequests = leaveRequests.filter((request) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        request.reason.toLowerCase().includes(query) ||
        getLeaveTypeLabel(request.leave_type).toLowerCase().includes(query)
      );
    }
    return true;
  });

  const pendingRequests = leaveRequests.filter((r) => r.status === "pending");
  const approvedThisYear = leaveRequests.filter(
    (r) => r.status === "approved" && new Date(r.start_date).getFullYear() === new Date().getFullYear()
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cuti & Izin</h1>
          <p className="text-sm text-gray-600 mt-1">Kelola permintaan cuti dan izin</p>
        </div>
        <button
          onClick={() => setShowNewRequestModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Ajukan Cuti
        </button>
      </div>

      {/* Leave Balance Cards */}
      {leaveBalance && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Annual Leave */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Cuti Tahunan</h3>
              <CalendarDays className="w-6 h-6 text-blue-600" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total</span>
                <span className="font-semibold text-gray-900">{leaveBalance.annual.total} hari</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Terpakai</span>
                <span className="font-medium text-red-600">{leaveBalance.annual.used} hari</span>
              </div>
              {leaveBalance.annual.carried_over > 0 && (
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Diambil Tahun Lalu</span>
                  <span className="font-medium text-orange-600">{leaveBalance.annual.carried_over} hari</span>
                </div>
              )}
              <div className="pt-3 border-t border-gray-200">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Sisa</span>
                  <span className="text-lg font-bold text-green-600">{leaveBalance.annual.remaining} hari</span>
                </div>
                {leaveBalance.annual.total > 0 && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{
                          width: `${(leaveBalance.annual.used / leaveBalance.annual.total) * 100}%`,
                        }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {Math.round((leaveBalance.annual.used / leaveBalance.annual.total) * 100)}% terpakai
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sick Leave */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Cuti Sakit</h3>
              <AlertCircle className="w-6 h-6 text-red-600" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total</span>
                <span className="font-semibold text-gray-900">{leaveBalance.sick.total} hari</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Terpakai</span>
                <span className="font-medium text-red-600">{leaveBalance.sick.used} hari</span>
              </div>
              <div className="pt-3 border-t border-gray-200">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Sisa</span>
                  <span className="text-lg font-bold text-green-600">{leaveBalance.sick.remaining} hari</span>
                </div>
                {leaveBalance.sick.total > 0 && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-red-600 h-2 rounded-full"
                        style={{
                          width: `${(leaveBalance.sick.used / leaveBalance.sick.total) * 100}%`,
                        }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {Math.round((leaveBalance.sick.used / leaveBalance.sick.total) * 100)}% terpakai
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Personal Leave */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Cuti Pribadi</h3>
              <Users className="w-6 h-6 text-purple-600" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total</span>
                <span className="font-semibold text-gray-900">{leaveBalance.personal.total} hari</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Terpakai</span>
                <span className="font-medium text-red-600">{leaveBalance.personal.used} hari</span>
              </div>
              <div className="pt-3 border-t border-gray-200">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Sisa</span>
                  <span className="text-lg font-bold text-green-600">{leaveBalance.personal.remaining} hari</span>
                </div>
                {leaveBalance.personal.total > 0 && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full"
                        style={{
                          width: `${(leaveBalance.personal.used / leaveBalance.personal.total) * 100}%`,
                        }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {Math.round((leaveBalance.personal.used / leaveBalance.personal.total) * 100)}% terpakai
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Menunggu Persetujuan</p>
              <p className="text-2xl font-bold text-yellow-600">{pendingRequests.length}</p>
            </div>
            <Clock className="w-8 h-8 text-yellow-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Disetujui Tahun Ini</p>
              <p className="text-2xl font-bold text-green-600">{approvedThisYear.length}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Hari Cuti</p>
              <p className="text-2xl font-bold text-blue-600">
                {approvedThisYear.reduce((sum, r) => sum + r.total_days, 0)}
              </p>
            </div>
            <CalendarDays className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        {leaveBalance?.next_accrual_date && (
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Akumulasi Berikutnya</p>
                <p className="text-sm font-bold text-gray-900">
                  {formatShortDate(leaveBalance.next_accrual_date)}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        )}
      </div>

      {/* Team Leave Calendar (Simplified) */}
      {teamLeave.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Cuti Tim (Bulan Ini)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {teamLeave.slice(0, 6).map((leave) => (
              <div key={leave.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-2">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <Users className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{leave.staff_name}</p>
                    <p className="text-xs text-gray-500">{leave.staff_role}</p>
                  </div>
                </div>
                <div className="mt-3">
                  <span
                    className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${getLeaveTypeColor(
                      leave.leave_type
                    )}`}
                  >
                    {getLeaveTypeLabel(leave.leave_type)}
                  </span>
                  <p className="text-sm text-gray-600 mt-2">
                    {formatShortDate(leave.start_date)} - {formatShortDate(leave.end_date)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-64">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Cari berdasarkan alasan..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as FilterStatus)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Semua Status</option>
            <option value="pending">Menunggu</option>
            <option value="approved">Disetujui</option>
            <option value="rejected">Ditolak</option>
            <option value="cancelled">Dibatalkan</option>
          </select>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Semua Jenis</option>
            <option value="annual">Cuti Tahunan</option>
            <option value="sick">Cuti Sakit</option>
            <option value="personal">Cuti Pribadi</option>
            <option value="unpaid">Cuti Tanpa Gaji</option>
            <option value="maternity">Cuti Melahirkan</option>
            <option value="paternity">Cuti Suami/Istri Melahirkan</option>
            <option value="special">Cuti Khusus</option>
          </select>
        </div>
      </div>

      {/* Leave Requests List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredRequests.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Calendar className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada riwayat cuti</h3>
          <p className="text-gray-600">
            {searchQuery || statusFilter !== "all" || typeFilter !== "all"
              ? "Tidak ada cuti yang sesuai dengan filter"
              : "Belum ada riwayat permintaan cuti"}
          </p>
          <button
            onClick={() => setShowNewRequestModal(true)}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Ajukan Cuti Pertama
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Jenis Cuti
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Tanggal
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Durasi
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Alasan
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
                {filteredRequests.map((request) => (
                  <tr key={request.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getLeaveTypeColor(
                          request.leave_type
                        )}`}
                      >
                        {getLeaveTypeLabel(request.leave_type)}
                      </span>
                      {request.attachment_url && (
                        <div className="flex items-center space-x-1 mt-2">
                          <FileText className="w-3 h-3 text-gray-400" />
                          <span className="text-xs text-gray-500">Lampiran</span>
                        </div>
                      )}
                    </td>

                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-900">{formatShortDate(request.start_date)}</p>
                      <p className="text-xs text-gray-500">s/d {formatShortDate(request.end_date)}</p>
                    </td>

                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <CalendarDays className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-900">{request.total_days} hari</span>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-700 max-w-xs truncate">{request.reason}</p>
                    </td>

                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <div className={getStatusColor(request.status)}>
                          {getStatusIcon(request.status)}
                        </div>
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                            request.status
                          )}`}
                        >
                          {getStatusLabel(request.status)}
                        </span>
                      </div>
                      {request.approver && (
                        <p className="text-xs text-gray-500 mt-1">
                          Oleh: {request.approver.name}
                        </p>
                      )}
                    </td>

                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => {
                            setSelectedRequest(request);
                            setShowDetailModal(true);
                          }}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                          title="Lihat Detail"
                        >
                          <Eye className="w-4 h-4" />
                        </button>

                        {request.status === "pending" && (
                          <button
                            onClick={() => handleCancelRequest(request.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                            title="Batalkan"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}

                        {request.attachment_url && (
                          <a
                            href={request.attachment_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-2 text-gray-600 hover:bg-gray-50 rounded-lg"
                            title="Unduh Lampiran"
                          >
                            <Download className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* New Request Modal */}
      {showNewRequestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Ajukan Permintaan Cuti</h3>
              <p className="text-sm text-gray-600 mt-1">Lengkapi formulir di bawah ini</p>
            </div>

            <div className="p-6 space-y-4">
              {/* Leave Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Jenis Cuti <span className="text-red-500">*</span>
                </label>
                <select
                  value={newRequest.leave_type}
                  onChange={(e) => setNewRequest({ ...newRequest, leave_type: e.target.value as LeaveType })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="annual">Cuti Tahunan</option>
                  <option value="sick">Cuti Sakit</option>
                  <option value="personal">Cuti Pribadi</option>
                  <option value="unpaid">Cuti Tanpa Gaji</option>
                  <option value="maternity">Cuti Melahirkan</option>
                  <option value="paternity">Cuti Suami/Istri Melahirkan</option>
                  <option value="special">Cuti Khusus</option>
                </select>
              </div>

              {/* Dates */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tanggal Mulai <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    value={newRequest.start_date}
                    onChange={(e) => setNewRequest({ ...newRequest, start_date: e.target.value })}
                    min={new Date().toISOString().split("T")[0]}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tanggal Selesai <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    value={newRequest.end_date}
                    onChange={(e) => setNewRequest({ ...newRequest, end_date: e.target.value })}
                    min={newRequest.start_date || new Date().toISOString().split("T")[0]}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Duration calculation */}
              {newRequest.start_date && newRequest.end_date && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <Info className="w-5 h-5 text-blue-600" />
                    <span className="text-sm text-blue-900">
                      Durasi: <strong>{calculateDuration(newRequest.start_date, newRequest.end_date)} hari</strong>
                    </span>
                  </div>
                </div>
              )}

              {/* Reason */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Alasan <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={newRequest.reason}
                  onChange={(e) => setNewRequest({ ...newRequest, reason: e.target.value })}
                  rows={4}
                  placeholder="Jelaskan alasan pengajuan cuti..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Attachment */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Lampiran (Opsional)
                </label>
                <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="space-y-1 text-center">
                    <Upload className="mx-auto h-12 w-12 text-gray-400" />
                    <div className="flex text-sm text-gray-600">
                      <label
                        htmlFor="file-upload"
                        className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                      >
                        <span>Pilih file</span>
                        <input
                          id="file-upload"
                          type="file"
                          className="sr-only"
                          accept=".pdf,.jpg,.jpeg,.png"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) {
                              setNewRequest({ ...newRequest, attachment: file });
                            }
                          }}
                        />
                      </label>
                      <p className="pl-1">atau drag & drop</p>
                    </div>
                    <p className="text-xs text-gray-500">PDF, JPG, PNG hingga 5MB</p>
                    {newRequest.attachment && (
                      <p className="text-sm text-green-600 mt-2">
                        File terpilih: {newRequest.attachment.name}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Balance info */}
              {leaveBalance && newRequest.leave_type === "annual" && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <p className="text-sm text-yellow-900">
                    <strong>Sisa cuti tahunan:</strong> {leaveBalance.annual.remaining} hari
                  </p>
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowNewRequestModal(false);
                  setNewRequest({
                    leave_type: "annual",
                    start_date: "",
                    end_date: "",
                    reason: "",
                    attachment: null,
                  });
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={handleSubmitLeave}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
              >
                <Send className="w-4 h-4 mr-2" />
                Ajukan Permintaan
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Detail Permintaan Cuti</h3>
            </div>

            <div className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Jenis Cuti</p>
                  <span
                    className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border mt-1 ${getLeaveTypeColor(
                      selectedRequest.leave_type
                    )}`}
                  >
                    {getLeaveTypeLabel(selectedRequest.leave_type)}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <div className={getStatusColor(selectedRequest.status)}>
                      {getStatusIcon(selectedRequest.status)}
                    </div>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                        selectedRequest.status
                      )}`}
                    >
                      {getStatusLabel(selectedRequest.status)}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-500">Tanggal</p>
                <p className="font-medium text-gray-900 mt-1">
                  {formatDate(selectedRequest.start_date)} - {formatDate(selectedRequest.end_date)}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-500">Durasi</p>
                <p className="font-medium text-gray-900 mt-1">{selectedRequest.total_days} hari</p>
              </div>

              <div>
                <p className="text-sm text-gray-500">Alasan</p>
                <p className="text-gray-900 mt-1">{selectedRequest.reason}</p>
              </div>

              {selectedRequest.attachment_url && (
                <div>
                  <p className="text-sm text-gray-500">Lampiran</p>
                  <a
                    href={selectedRequest.attachment_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-blue-600 hover:text-blue-700 mt-1"
                  >
                    <Download className="w-4 h-4 mr-1" />
                    Unduh Dokumen
                  </a>
                </div>
              )}

              {selectedRequest.approver && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500 mb-2">Informasi Persetujuan</p>
                  <p className="text-sm">
                    <strong>Disetujui oleh:</strong> {selectedRequest.approver.name} (
                    {selectedRequest.approver.role})
                  </p>
                  {selectedRequest.approval_date && (
                    <p className="text-sm">
                      <strong>Tanggal:</strong> {formatDate(selectedRequest.approval_date)}
                    </p>
                  )}
                  {selectedRequest.approval_notes && (
                    <p className="text-sm mt-2">
                      <strong>Catatan:</strong> {selectedRequest.approval_notes}
                    </p>
                  )}
                </div>
              )}

              <div className="text-xs text-gray-500">
                <p>Diajukan: {new Date(selectedRequest.created_at).toLocaleString("id-ID")}</p>
                <p>Diperbarui: {new Date(selectedRequest.updated_at).toLocaleString("id-ID")}</p>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end">
              <button
                onClick={() => {
                  setShowDetailModal(false);
                  setSelectedRequest(null);
                }}
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
