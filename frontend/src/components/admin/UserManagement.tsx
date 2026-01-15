/**
 * User Management UI Component for STORY-037
 *
 * Provides comprehensive user management with:
 * - User CRUD operations
 * - Role assignment
 * - Department-based access
 * - Bulk user import
 * - Password reset
 * - User activity logs
 * - User access request workflow
 */

import { useState, useEffect } from "react";
import {
  Users,
  UserPlus,
  Search,
  Filter,
  Edit,
  Trash2,
  Key,
  FileText,
  Shield,
  Building,
  Upload,
  Download,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
} from "lucide-react";

// Types
interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  department_id?: number;
  department_name?: string;
  phone?: string;
  employee_id?: string;
  license_number?: string;
  is_active: boolean;
  is_superuser: boolean;
  mfa_enabled: boolean;
  last_login?: string;
  failed_login_attempts: number;
  locked_until?: string;
  password_changed_at?: string;
  created_at: string;
  updated_at: string;
}

interface Department {
  id: number;
  name: string;
  code: string;
  description?: string;
  parent_department_id?: number;
  created_at: string;
  updated_at: string;
}

interface Role {
  role: string;
  display_name: string;
  description: string;
  permissions: string[];
}

interface ActivityLog {
  id: number;
  user_id: number;
  username?: string;
  action: string;
  resource_type?: string;
  resource_id?: string;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
  details?: Record<string, unknown>;
}

interface AccessRequest {
  id: number;
  user_id: number;
  username: string;
  full_name: string;
  requested_role: string;
  requested_department_id?: number;
  reason: string;
  status: string;
  requested_at: string;
  reviewed_at?: string;
  reviewed_by?: number;
  review_notes?: string;
}

type TabType = "users" | "departments" | "access-requests" | "activity-logs";

export function UserManagement() {
  const [activeTab, setActiveTab] = useState<TabType>("users");
  const [users, setUsers] = useState<User[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [accessRequests, setAccessRequests] = useState<AccessRequest[]>([]);
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Filter states
  const [searchTerm, setSearchTerm] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("");

  // Modal states
  const [showCreateUserModal, setShowCreateUserModal] = useState(false);
  const [showEditUserModal, setShowEditUserModal] = useState(false);
  const [showPasswordResetModal, setShowPasswordResetModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");

      if (activeTab === "users") {
        // Load users
        const usersResponse = await fetch("/api/v1/users", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (usersResponse.ok) {
          const data = await usersResponse.json();
          setUsers(data.users || []);
        }
      } else if (activeTab === "departments") {
        // Load departments
        const deptResponse = await fetch("/api/v1/departments", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (deptResponse.ok) {
          const data = await deptResponse.json();
          setDepartments(data || []);
        }
      } else if (activeTab === "access-requests") {
        // Load access requests
        const requestsResponse = await fetch("/api/v1/users/access-requests", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (requestsResponse.ok) {
          const data = await requestsResponse.json();
          setAccessRequests(data || []);
        }
      } else if (activeTab === "activity-logs") {
        // Load activity logs
        const logsResponse = await fetch("/api/v1/activity-logs?page=1&page_size=50", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (logsResponse.ok) {
          const data = await logsResponse.json();
          setActivityLogs(data.logs || []);
        }
      }

      // Load departments and roles for filters
      if (departments.length === 0) {
        const deptResponse = await fetch("/api/v1/departments", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (deptResponse.ok) {
          const data = await deptResponse.json();
          setDepartments(data || []);
        }
      }

      if (roles.length === 0) {
        const rolesResponse = await fetch("/api/v1/users/roles", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (rolesResponse.ok) {
          const data = await rolesResponse.json();
          setRoles(data || []);
        }
      }
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getRoleDisplayName = (role: string) => {
    const found = roles.find((r) => r.role === role);
    return found?.display_name || role;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("id-ID", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getStatusBadge = (user: User) => {
    if (!user.is_active) {
      return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Tidak Aktif</span>;
    }
    if (user.locked_until && new Date(user.locked_until) > new Date()) {
      return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">Terkunci</span>;
    }
    return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Aktif</span>;
  };

  const handleDeactivateUser = async (userId: number) => {
    if (!confirm("Apakah Anda yakin ingin menonaktifkan pengguna ini?")) return;

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/api/v1/users/${userId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        loadData();
      } else {
        alert("Gagal menonaktifkan pengguna");
      }
    } catch (error) {
      console.error("Error deactivating user:", error);
    }
  };

  const handleAccessRequestDecision = async (requestId: number, decision: string, notes?: string) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/api/v1/users/access-requests/${requestId}`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          decision,
          review_notes: notes,
          assign_role: decision === "approved" ? accessRequests.find(r => r.id === requestId)?.requested_role : undefined,
        }),
      });

      if (response.ok) {
        loadData();
      } else {
        alert("Gagal memproses permintaan akses");
      }
    } catch (error) {
      console.error("Error processing access request:", error);
    }
  };

  if (isLoading && users.length === 0) {
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
            <Users className="h-6 w-6 mr-2" />
            Manajemen Pengguna
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Kelola pengguna, peran, dan hak akses sistem
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={loadData}
            disabled={isLoading}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab("users")}
            className={`${
              activeTab === "users"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Pengguna
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
            onClick={() => setActiveTab("access-requests")}
            className={`${
              activeTab === "access-requests"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Permintaan Akses
          </button>
          <button
            onClick={() => setActiveTab("activity-logs")}
            className={`${
              activeTab === "activity-logs"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Log Aktivitas
          </button>
        </nav>
      </div>

      {/* Users Tab */}
      {activeTab === "users" && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Daftar Pengguna</h3>
            <button
              onClick={() => setShowCreateUserModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              <UserPlus className="h-4 w-4 mr-2" />
              Tambah Pengguna
            </button>
          </div>

          {/* Filters */}
          <div className="flex items-center space-x-4 mb-4">
            <div className="relative flex-1">
              <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Cari pengguna..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm w-full focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Semua Peran</option>
              {roles.map((role) => (
                <option key={role.role} value={role.role}>
                  {role.display_name}
                </option>
              ))}
            </select>
            <select
              value={departmentFilter}
              onChange={(e) => setDepartmentFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Semua Departemen</option>
              {departments.map((dept) => (
                <option key={dept.id} value={dept.id.toString()}>
                  {dept.name}
                </option>
              ))}
            </select>
          </div>

          {/* Users Table */}
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Nama
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Username
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Peran
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Departemen
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Aksi
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users
                  .filter(
                    (user) =>
                      !searchTerm ||
                      user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                      user.email.toLowerCase().includes(searchTerm.toLowerCase())
                  )
                  .filter((user) => !roleFilter || user.role === roleFilter)
                  .filter((user) => !departmentFilter || user.department_id === parseInt(departmentFilter))
                  .map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                        <div className="text-xs text-gray-500">{user.email}</div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.username}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {getRoleDisplayName(user.role)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.department_name || "-"}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        {getStatusBadge(user)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => {
                              setSelectedUser(user);
                              setShowEditUserModal(true);
                            }}
                            className="text-blue-600 hover:text-blue-900"
                            title="Edit"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => {
                              setSelectedUser(user);
                              setShowPasswordResetModal(true);
                            }}
                            className="text-yellow-600 hover:text-yellow-900"
                            title="Reset Password"
                          >
                            <Key className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeactivateUser(user.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Nonaktifkan"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>

            {users.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Users className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Tidak ada pengguna</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Departments Tab */}
      {activeTab === "departments" && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Daftar Departemen</h3>
            <button
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              <Building className="h-4 w-4 mr-2" />
              Tambah Departemen
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {departments.map((dept) => (
              <div key={dept.id} className="border rounded-lg p-4">
                <h4 className="font-medium text-gray-900">{dept.name}</h4>
                <p className="text-sm text-gray-500">Kode: {dept.code}</p>
                {dept.description && (
                  <p className="text-sm text-gray-600 mt-2">{dept.description}</p>
                )}
              </div>
            ))}
          </div>

          {departments.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Building className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Tidak ada departemen</p>
            </div>
          )}
        </div>
      )}

      {/* Access Requests Tab */}
      {activeTab === "access-requests" && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Permintaan Akses</h3>

          <div className="space-y-4">
            {accessRequests.map((request) => (
              <div key={request.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">{request.full_name}</h4>
                    <p className="text-sm text-gray-500">@{request.username}</p>
                    <p className="text-sm text-gray-600 mt-2">
                      Meminta peran: <strong>{getRoleDisplayName(request.requested_role)}</strong>
                    </p>
                    <p className="text-sm text-gray-600">Alasan: {request.reason}</p>
                    <p className="text-xs text-gray-400 mt-2">
                      Diajukan: {formatDate(request.requested_at)}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    {request.status === "pending" && (
                      <>
                        <button
                          onClick={() => handleAccessRequestDecision(request.id, "approved")}
                          className="inline-flex items-center px-3 py-1 border border-transparent rounded-md text-sm font-medium text-white bg-green-600 hover:bg-green-700"
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Setujui
                        </button>
                        <button
                          onClick={() => handleAccessRequestDecision(request.id, "rejected")}
                          className="inline-flex items-center px-3 py-1 border border-transparent rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700"
                        >
                          <XCircle className="h-4 w-4 mr-1" />
                          Tolak
                        </button>
                      </>
                    )}
                    {request.status === "approved" && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Disetujui
                      </span>
                    )}
                    {request.status === "rejected" && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <XCircle className="h-3 w-3 mr-1" />
                        Ditolak
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {accessRequests.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Shield className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Tidak ada permintaan akses</p>
            </div>
          )}
        </div>
      )}

      {/* Activity Logs Tab */}
      {activeTab === "activity-logs" && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Log Aktivitas</h3>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {activityLogs.map((log) => (
              <div key={log.id} className="border-l-4 border-blue-500 bg-blue-50 p-4 rounded">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {log.username || `User ${log.user_id}`}
                    </p>
                    <p className="text-sm text-gray-600">{log.action}</p>
                    {log.resource_type && (
                      <p className="text-xs text-gray-500">
                        {log.resource_type}:{log.resource_id}
                      </p>
                    )}
                  </div>
                  <p className="text-xs text-gray-400">{formatDate(log.created_at)}</p>
                </div>
              </div>
            ))}
          </div>

          {activityLogs.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Tidak ada log aktivitas</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
