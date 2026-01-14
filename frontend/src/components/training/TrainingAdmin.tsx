"use client";

/**
 * Training Admin Component for STORY-038
 *
 * Provides admin panel with:
 * - Module management (create, edit, delete)
 * - Assignment management (assign to users/roles/departments)
 * - Bulk assignment interface
 * - Compliance reports
 * - Completion statistics
 * - User progress tracking
 */

import { useState, useEffect } from "react";
import {
  BookOpen,
  Plus,
  Edit,
  Trash2,
  Users,
  Building,
  Shield,
  FileText,
  CheckCircle,
  Clock,
  AlertCircle,
  Search,
  Filter,
  Download,
  Upload,
  TrendingUp,
  BarChart3,
  UserCheck,
  Calendar,
  RefreshCw,
  Save,
  X,
  Video,
  FileText as FileIcon,
  MousePointer,
  Package,
} from "lucide-react";

// Types
interface TrainingModule {
  id: number;
  title: string;
  code: string;
  category: string;
  description: string;
  duration_minutes: number;
  difficulty: "beginner" | "intermediate" | "advanced";
  content_type: "video" | "document" | "interactive" | "scorm";
  total_lessons: number;
  is_mandatory: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  enrollment_count?: number;
  completion_rate?: number;
}

interface Assignment {
  id: number;
  module_id: number;
  module_title: string;
  assignee_type: "user" | "role" | "department";
  assignee_id: number;
  assignee_name?: string;
  due_date?: string;
  assigned_date: string;
  assigned_by: string;
  completion_count: number;
  total_assignees: number;
}

interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role: string;
  department_name?: string;
}

interface Department {
  id: number;
  name: string;
  code: string;
}

type TabType = "modules" | "assignments" | "compliance" | "reports";

export function TrainingAdmin() {
  const [activeTab, setActiveTab] = useState<TabType>("modules");
  const [modules, setModules] = useState<TrainingModule[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Modal states
  const [showModuleModal, setShowModuleModal] = useState(false);
  const [showAssignmentModal, setShowAssignmentModal] = useState(false);
  const [selectedModule, setSelectedModule] = useState<TrainingModule | null>(null);

  // Filter states
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  // Form states
  const [moduleForm, setModuleForm] = useState({
    title: "",
    code: "",
    category: "",
    description: "",
    duration_minutes: 0,
    difficulty: "beginner" as "beginner" | "intermediate" | "advanced",
    content_type: "video" as "video" | "document" | "interactive" | "scorm",
    is_mandatory: false,
    is_active: true,
  });

  const [assignmentForm, setAssignmentForm] = useState({
    module_id: 0,
    assignee_type: "user" as "user" | "role" | "department",
    assignee_ids: [] as number[],
    due_date: "",
  });

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");

      if (activeTab === "modules") {
        const response = await fetch("/api/v1/training/admin/modules", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setModules(data.modules || []);
        }
      } else if (activeTab === "assignments") {
        const response = await fetch("/api/v1/training/admin/assignments", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setAssignments(data.assignments || []);
        }
      }

      // Load users and departments for assignment modal
      if (users.length === 0) {
        const usersResponse = await fetch("/api/v1/users", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (usersResponse.ok) {
          const data = await usersResponse.json();
          setUsers(data.users || []);
        }
      }

      if (departments.length === 0) {
        const deptResponse = await fetch("/api/v1/departments", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (deptResponse.ok) {
          const data = await deptResponse.json();
          setDepartments(data || []);
        }
      }
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateModule = async () => {
    try {
      const token = localStorage.getItem("token");

      const response = await fetch("/api/v1/training/admin/modules", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(moduleForm),
      });

      if (response.ok) {
        setShowModuleModal(false);
        resetModuleForm();
        loadData();
        alert("Modul berhasil dibuat");
      } else {
        alert("Gagal membuat modul");
      }
    } catch (error) {
      console.error("Error creating module:", error);
    }
  };

  const handleUpdateModule = async () => {
    if (!selectedModule) return;

    try {
      const token = localStorage.getItem("token");

      const response = await fetch(`/api/v1/training/admin/modules/${selectedModule.id}`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(moduleForm),
      });

      if (response.ok) {
        setShowModuleModal(false);
        setSelectedModule(null);
        resetModuleForm();
        loadData();
        alert("Modul berhasil diperbarui");
      } else {
        alert("Gagal memperbarui modul");
      }
    } catch (error) {
      console.error("Error updating module:", error);
    }
  };

  const handleDeleteModule = async (moduleId: number) => {
    if (!confirm("Apakah Anda yakin ingin menghapus modul ini?")) return;

    try {
      const token = localStorage.getItem("token");

      const response = await fetch(`/api/v1/training/admin/modules/${moduleId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        loadData();
        alert("Modul berhasil dihapus");
      } else {
        alert("Gagal menghapus modul");
      }
    } catch (error) {
      console.error("Error deleting module:", error);
    }
  };

  const handleCreateAssignment = async () => {
    try {
      const token = localStorage.getItem("token");

      const response = await fetch("/api/v1/training/admin/assignments", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(assignmentForm),
      });

      if (response.ok) {
        setShowAssignmentModal(false);
        resetAssignmentForm();
        loadData();
        alert("Penugasan berhasil dibuat");
      } else {
        alert("Gagal membuat penugasan");
      }
    } catch (error) {
      console.error("Error creating assignment:", error);
    }
  };

  const handleBulkAssignment = async (file: File) => {
    try {
      const token = localStorage.getItem("token");
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/api/v1/training/admin/assignments/bulk", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (response.ok) {
        alert("Penugasan massal berhasil");
        loadData();
      } else {
        alert("Gagal melakukan penugasan massal");
      }
    } catch (error) {
      console.error("Error creating bulk assignment:", error);
    }
  };

  const resetModuleForm = () => {
    setModuleForm({
      title: "",
      code: "",
      category: "",
      description: "",
      duration_minutes: 0,
      difficulty: "beginner",
      content_type: "video",
      is_mandatory: false,
      is_active: true,
    });
  };

  const resetAssignmentForm = () => {
    setAssignmentForm({
      module_id: 0,
      assignee_type: "user",
      assignee_ids: [],
      due_date: "",
    });
  };

  const openModuleModal = (module?: TrainingModule) => {
    if (module) {
      setSelectedModule(module);
      setModuleForm({
        title: module.title,
        code: module.code,
        category: module.category,
        description: module.description,
        duration_minutes: module.duration_minutes,
        difficulty: module.difficulty,
        content_type: module.content_type,
        is_mandatory: module.is_mandatory,
        is_active: module.is_active,
      });
    } else {
      setSelectedModule(null);
      resetModuleForm();
    }
    setShowModuleModal(true);
  };

  const getContentTypeIcon = (type: string) => {
    switch (type) {
      case "video":
        return <Video className="h-4 w-4" />;
      case "document":
        return <FileIcon className="h-4 w-4" />;
      case "interactive":
        return <MousePointer className="h-4 w-4" />;
      case "scorm":
        return <Package className="h-4 w-4" />;
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

  if (isLoading && modules.length === 0 && assignments.length === 0) {
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
            <Shield className="h-6 w-6 mr-2" />
            Admin Pelatihan
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Kelola modul, penugasan, dan kepatuhan pelatihan
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab("modules")}
            className={`${
              activeTab === "modules"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            <BookOpen className="h-4 w-4 inline mr-2" />
            Modul
          </button>
          <button
            onClick={() => setActiveTab("assignments")}
            className={`${
              activeTab === "assignments"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            <Users className="h-4 w-4 inline mr-2" />
            Penugasan
          </button>
          <button
            onClick={() => setActiveTab("compliance")}
            className={`${
              activeTab === "compliance"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            <CheckCircle className="h-4 w-4 inline mr-2" />
            Kepatuhan
          </button>
          <button
            onClick={() => setActiveTab("reports")}
            className={`${
              activeTab === "reports"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            <BarChart3 className="h-4 w-4 inline mr-2" />
            Laporan
          </button>
        </nav>
      </div>

      {/* Modules Tab */}
      {activeTab === "modules" && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Daftar Modul</h3>
            <button
              onClick={() => openModuleModal()}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Tambah Modul
            </button>
          </div>

          {/* Filters */}
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center space-x-4">
              <div className="relative flex-1">
                <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Cari modul..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm w-full focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Modules Table */}
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Modul
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Kategori
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Tipe
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Durasi
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Peserta
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Aksi
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {modules
                  .filter(
                    (m) =>
                      !searchTerm ||
                      m.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                      m.code.toLowerCase().includes(searchTerm.toLowerCase())
                  )
                  .map((module) => (
                    <tr key={module.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{module.title}</div>
                          <div className="text-xs text-gray-500">{module.code}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {module.category}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center text-sm text-gray-900">
                          {getContentTypeIcon(module.content_type)}
                          <span className="ml-2 capitalize">{module.content_type}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {module.duration_minutes} menit
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {module.enrollment_count || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          {module.is_mandatory && (
                            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">
                              Wajib
                            </span>
                          )}
                          {module.is_active ? (
                            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                              Aktif
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
                              Nonaktif
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => openModuleModal(module)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Edit"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteModule(module.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Hapus"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>

            {modules.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <BookOpen className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Tidak ada modul</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Assignments Tab */}
      {activeTab === "assignments" && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Daftar Penugasan</h3>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => {
                  const input = document.createElement("input");
                  input.type = "file";
                  input.accept = ".csv,.xlsx";
                  input.onchange = (e) => {
                    const file = (e.target as HTMLInputElement).files?.[0];
                    if (file) handleBulkAssignment(file);
                  };
                  input.click();
                }}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <Upload className="h-4 w-4 mr-2" />
                Upload Massal
              </button>
              <button
                onClick={() => {
                  resetAssignmentForm();
                  setShowAssignmentModal(true);
                }}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Buat Penugasan
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Modul
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Penerima
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Tipe
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Tenggat
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Progres
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {assignments.map((assignment) => (
                  <tr key={assignment.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {assignment.module_title}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {assignment.assignee_name || `${assignment.assignee_type} ${assignment.assignee_id}`}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 capitalize">
                      {assignment.assignee_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {assignment.due_date ? formatDate(assignment.due_date) : "-"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {assignment.completion_count} / {assignment.total_assignees}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {assignments.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Users className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Tidak ada penugasan</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Compliance Tab */}
      {activeTab === "compliance" && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Status Kepatuhan</h3>
          <div className="text-center py-8 text-gray-500">
            <CheckCircle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>Fitur kepatuhan akan segera tersedia</p>
          </div>
        </div>
      )}

      {/* Reports Tab */}
      {activeTab === "reports" && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Laporan Pelatihan</h3>
          <div className="text-center py-8 text-gray-500">
            <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>Fitur laporan akan segera tersedia</p>
          </div>
        </div>
      )}

      {/* Module Modal */}
      {showModuleModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                {selectedModule ? "Edit Modul" : "Tambah Modul Baru"}
              </h3>
              <button
                onClick={() => {
                  setShowModuleModal(false);
                  setSelectedModule(null);
                }}
                className="text-gray-400 hover:text-gray-500"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Judul</label>
                <input
                  type="text"
                  value={moduleForm.title}
                  onChange={(e) => setModuleForm({ ...moduleForm, title: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Kode</label>
                  <input
                    type="text"
                    value={moduleForm.code}
                    onChange={(e) => setModuleForm({ ...moduleForm, code: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Kategori</label>
                  <input
                    type="text"
                    value={moduleForm.category}
                    onChange={(e) => setModuleForm({ ...moduleForm, category: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Deskripsi</label>
                <textarea
                  value={moduleForm.description}
                  onChange={(e) => setModuleForm({ ...moduleForm, description: e.target.value })}
                  rows={3}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Durasi (menit)</label>
                  <input
                    type="number"
                    value={moduleForm.duration_minutes}
                    onChange={(e) =>
                      setModuleForm({ ...moduleForm, duration_minutes: parseInt(e.target.value) })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Tingkat Kesulitan</label>
                  <select
                    value={moduleForm.difficulty}
                    onChange={(e) =>
                      setModuleForm({
                        ...moduleForm,
                        difficulty: e.target.value as "beginner" | "intermediate" | "advanced",
                      })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="beginner">Pemula</option>
                    <option value="intermediate">Menengah</option>
                    <option value="advanced">Lanjutan</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Tipe Konten</label>
                <select
                  value={moduleForm.content_type}
                  onChange={(e) =>
                    setModuleForm({
                      ...moduleForm,
                      content_type: e.target.value as "video" | "document" | "interactive" | "scorm",
                    })
                  }
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="video">Video</option>
                  <option value="document">Dokumen</option>
                  <option value="interactive">Interaktif</option>
                  <option value="scorm">SCORM</option>
                </select>
              </div>

              <div className="flex items-center space-x-4">
                <label className="inline-flex items-center">
                  <input
                    type="checkbox"
                    checked={moduleForm.is_mandatory}
                    onChange={(e) => setModuleForm({ ...moduleForm, is_mandatory: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                  <span className="ml-2 text-sm text-gray-700">Wajib</span>
                </label>
                <label className="inline-flex items-center">
                  <input
                    type="checkbox"
                    checked={moduleForm.is_active}
                    onChange={(e) => setModuleForm({ ...moduleForm, is_active: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                  <span className="ml-2 text-sm text-gray-700">Aktif</span>
                </label>
              </div>
            </div>

            <div className="mt-6 flex items-center justify-end space-x-3">
              <button
                onClick={() => {
                  setShowModuleModal(false);
                  setSelectedModule(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={selectedModule ? handleUpdateModule : handleCreateModule}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                <Save className="h-4 w-4 mr-2" />
                {selectedModule ? "Update" : "Simpan"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Assignment Modal */}
      {showAssignmentModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Buat Penugasan Baru</h3>
              <button
                onClick={() => setShowAssignmentModal(false)}
                className="text-gray-400 hover:text-gray-500"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Modul</label>
                <select
                  value={assignmentForm.module_id}
                  onChange={(e) =>
                    setAssignmentForm({ ...assignmentForm, module_id: parseInt(e.target.value) })
                  }
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="">Pilih Modul</option>
                  {modules.map((module) => (
                    <option key={module.id} value={module.id}>
                      {module.title} ({module.code})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Tipe Penerima</label>
                <select
                  value={assignmentForm.assignee_type}
                  onChange={(e) =>
                    setAssignmentForm({
                      ...assignmentForm,
                      assignee_type: e.target.value as "user" | "role" | "department",
                    })
                  }
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="user">Pengguna</option>
                  <option value="role">Peran</option>
                  <option value="department">Departemen</option>
                </select>
              </div>

              {assignmentForm.assignee_type === "user" && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Pengguna</label>
                  <select
                    multiple
                    value={assignmentForm.assignee_ids.map(String)}
                    onChange={(e) =>
                      setAssignmentForm({
                        ...assignmentForm,
                        assignee_ids: Array.from(e.target.selectedOptions, (opt) => parseInt(opt.value)),
                      })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm h-32"
                  >
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.full_name} ({user.username})
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Tahan Ctrl/Cmd untuk memilih multiple
                  </p>
                </div>
              )}

              {assignmentForm.assignee_type === "department" && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Departemen</label>
                  <select
                    multiple
                    value={assignmentForm.assignee_ids.map(String)}
                    onChange={(e) =>
                      setAssignmentForm({
                        ...assignmentForm,
                        assignee_ids: Array.from(e.target.selectedOptions, (opt) => parseInt(opt.value)),
                      })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm h-32"
                  >
                    {departments.map((dept) => (
                      <option key={dept.id} value={dept.id}>
                        {dept.name}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Tahan Ctrl/Cmd untuk memilih multiple
                  </p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700">Tenggat Waktu</label>
                <input
                  type="date"
                  value={assignmentForm.due_date}
                  onChange={(e) => setAssignmentForm({ ...assignmentForm, due_date: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>

            <div className="mt-6 flex items-center justify-end space-x-3">
              <button
                onClick={() => setShowAssignmentModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={handleCreateAssignment}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                <Save className="h-4 w-4 mr-2" />
                Simpan
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
