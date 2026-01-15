"use client";

/**
 * Staff Training & Development Page - STORY-020-05: Training Module Access & Progress Tracking
 *
 * Comprehensive training management for staff including:
 * - View assigned training modules
 * - Access training materials (videos, documents, presentations)
 * - Complete online training courses
 * - Take quizzes and assessments
 * - Track training progress (completion percentage, remaining modules)
 * - View training history and certificates
 * - Download training completion certificates
 * - Set training reminders and deadlines
 * - Mandatory training alerts (compliance training, safety training)
 * - Competency tracking (clinical skills, technical skills)
 * - Continuing education credits tracking (SKP/SKPB)
 * - Training recommendation engine based on role
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  BookOpen,
  Play,
  CheckCircle,
  Clock,
  Trophy,
  Target,
  AlertTriangle,
  Download,
  Search,
  Filter,
  Calendar,
  Award,
  TrendingUp,
  FileText,
  Video,
  Image,
  Link as LinkIcon,
  ExternalLink,
  ChevronRight,
  Star,
  Flag,
  Eye,
} from "lucide-react";

// Types
interface TrainingModule {
  id: number;
  title: string;
  description: string;
  category:
    | "compliance"
    | "safety"
    | "clinical"
    | "technical"
    | "soft_skills"
    | "leadership"
    | "onboarding";
  type: "video" | "document" | "presentation" | "interactive" | "quiz" | "scorm";
  status: "not_started" | "in_progress" | "completed" | "overdue";
  progress: number; // 0-100
  duration_minutes: number;
  is_mandatory: boolean;
  due_date?: string;
  assigned_date: string;
  completed_date?: string;
  score?: number;
  passing_score: number;
  attempts: number;
  max_attempts: number;
  instructor?: string;
  materials: TrainingMaterial[];
  quiz?: Quiz;
  certificate_url?: string;
  credits?: number; // SKP/SKPB credits
}

interface TrainingMaterial {
  id: number;
  type: "video" | "pdf" | "presentation" | "link" | "document";
  title: string;
  url: string;
  duration_minutes?: number;
  file_size?: string;
  order: number;
}

interface Quiz {
  id: number;
  total_questions: number;
  passing_score: number;
  time_limit_minutes?: number;
  attempts_allowed: number;
  attempts_used: number;
  best_score?: number;
}

interface TrainingCertificate {
  id: number;
  training_id: number;
  training_title: string;
  completion_date: string;
  score: number;
  certificate_url: string;
  credits: number;
  instructor: string;
  valid_until?: string;
}

interface Competency {
  id: number;
  name: string;
  category: "clinical" | "technical" | "soft_skill";
  proficiency_level: "beginner" | "intermediate" | "advanced" | "expert";
  last_assessed: string;
  next_assessment?: string;
  status: "current" | "expiring_soon" | "expired" | "not_assessed";
}

interface CreditSummary {
  year: number;
  total_credits: number;
  required_credits: number;
  breakdown: {
    category: string;
    credits: number;
  }[];
}

type CategoryFilter = "all" | "compliance" | "safety" | "clinical" | "technical" | "soft_skills" | "leadership" | "onboarding";
type StatusFilter = "all" | "not_started" | "in_progress" | "completed" | "overdue";

export default function StaffTrainingPage() {
  const router = useRouter();
  const [trainingModules, setTrainingModules] = useState<TrainingModule[]>([]);
  const [certificates, setCertificates] = useState<TrainingCertificate[]>([]);
  const [competencies, setCompetencies] = useState<Competency[]>([]);
  const [creditSummary, setCreditSummary] = useState<CreditSummary | null>(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>("all");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [searchQuery, setSearchQuery] = useState("");

  // UI state
  const [selectedModule, setSelectedModule] = useState<TrainingModule | null>(null);
  const [showModuleModal, setShowModuleModal] = useState(false);

  useEffect(() => {
    fetchTrainingData();
  }, [categoryFilter, statusFilter]);

  const fetchTrainingData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const params = new URLSearchParams();
      if (categoryFilter !== "all") params.append("category", categoryFilter);
      if (statusFilter !== "all") params.append("status", statusFilter);

      const [modulesRes, certificatesRes, competenciesRes, creditsRes] = await Promise.all([
        fetch(`/api/v1/staff/training/modules?${params}`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch("/api/v1/staff/training/certificates", {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch("/api/v1/staff/training/competencies", {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`/api/v1/staff/training/credits?year=${new Date().getFullYear()}`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (modulesRes.ok) {
        const modulesData = await modulesRes.json();
        setTrainingModules(modulesData.items || []);
      }

      if (certificatesRes.ok) {
        const certsData = await certificatesRes.json();
        setCertificates(certsData.items || []);
      }

      if (competenciesRes.ok) {
        const compData = await competenciesRes.json();
        setCompetencies(compData.items || []);
      }

      if (creditsRes.ok) {
        const creditsData = await creditsRes.json();
        setCreditSummary(creditsData);
      }
    } catch (error) {
      console.error("Failed to fetch training data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartModule = (module: TrainingModule) => {
    setSelectedModule(module);
    setShowModuleModal(true);
  };

  const handleDownloadCertificate = async (certId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/staff/training/certificates/${certId}/download`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `sertifikat-${certId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert("Gagal mengunduh sertifikat");
      }
    } catch (error) {
      console.error("Failed to download certificate:", error);
      alert("Gagal mengunduh sertifikat");
    }
  };

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      compliance: "Kepatuhan",
      safety: "K3 & Keselamatan",
      clinical: "Klinis",
      technical: "Teknis",
      soft_skills: "Soft Skills",
      leadership: "Kepemimpinan",
      onboarding: "Onboarding",
    };
    return labels[category] || category;
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      compliance: "bg-red-100 text-red-800 border-red-300",
      safety: "bg-orange-100 text-orange-800 border-orange-300",
      clinical: "bg-blue-100 text-blue-800 border-blue-300",
      technical: "bg-purple-100 text-purple-800 border-purple-300",
      soft_skills: "bg-green-100 text-green-800 border-green-300",
      leadership: "bg-indigo-100 text-indigo-800 border-indigo-300",
      onboarding: "bg-teal-100 text-teal-800 border-teal-300",
    };
    return colors[category] || "bg-gray-100 text-gray-800 border-gray-300";
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      not_started: "Belum Dimulai",
      in_progress: "Sedang Berjalan",
      completed: "Selesai",
      overdue: "Terlambat",
    };
    return labels[status] || status;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      not_started: "bg-gray-100 text-gray-800",
      in_progress: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      overdue: "bg-red-100 text-red-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const getTypeIcon = (type: string) => {
    const icons: Record<string, React.ReactNode> = {
      video: <Video className="w-4 h-4" />,
      document: <FileText className="w-4 h-4" />,
      presentation: <Image className="w-4 h-4" />,
      interactive: <Play className="w-4 h-4" />,
      quiz: <Target className="w-4 h-4" />,
      scorm: <BookOpen className="w-4 h-4" />,
    };
    return icons[type] || <FileText className="w-4 h-4" />;
  };

  const getCompetencyStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      current: "bg-green-100 text-green-800",
      expiring_soon: "bg-yellow-100 text-yellow-800",
      expired: "bg-red-100 text-red-800",
      not_assessed: "bg-gray-100 text-gray-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const getCompetencyStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      current: "Aktif",
      expiring_soon: "Akan Kedaluwarsa",
      expired: "Kedaluwarsa",
      not_assessed: "Belum Dinilai",
    };
    return labels[status] || status;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("id-ID", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes} menit`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}j ${mins}m` : `${hours} jam`;
  };

  const filteredModules = trainingModules.filter((module) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        module.title.toLowerCase().includes(query) ||
        module.description.toLowerCase().includes(query) ||
        getCategoryLabel(module.category).toLowerCase().includes(query)
      );
    }
    return true;
  });

  const mandatoryModules = trainingModules.filter((m) => m.is_mandatory && m.status !== "completed");
  const overdueModules = trainingModules.filter((m) => m.status === "overdue");
  const inProgressModules = trainingModules.filter((m) => m.status === "in_progress");
  const completedThisYear = certificates.filter(
    (c) => new Date(c.completion_date).getFullYear() === new Date().getFullYear()
  ).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Pelatihan & Pengembangan</h1>
          <p className="text-sm text-gray-600 mt-1">Kelola pelatihan dan sertifikasi Anda</p>
        </div>
      </div>

      {/* Stats Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pelatihan Wajib</p>
              <p className="text-2xl font-bold text-orange-600">{mandatoryModules.length}</p>
            </div>
            <Flag className="w-8 h-8 text-orange-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Terlambat</p>
              <p className="text-2xl font-bold text-red-600">{overdueModules.length}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Sedang Berjalan</p>
              <p className="text-2xl font-bold text-blue-600">{inProgressModules.length}</p>
            </div>
            <Clock className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Selesai Tahun Ini</p>
              <p className="text-2xl font-bold text-green-600">{completedThisYear}</p>
            </div>
            <Trophy className="w-8 h-8 text-green-600" />
          </div>
        </div>
      </div>

      {/* Credit Summary */}
      {creditSummary && (
        <div className="bg-gradient-to-r from-purple-600 to-purple-700 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold">SKP/SKPB {creditSummary.year}</h2>
              <p className="text-purple-100 text-sm">Satuan Kredit Pemeliharaan</p>
            </div>
            <Award className="w-8 h-8 text-purple-200" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/10 rounded-lg p-4">
              <p className="text-purple-100 text-sm">Total Kredit</p>
              <p className="text-2xl font-bold">{creditSummary.total_credits} SKP</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <p className="text-purple-100 text-sm">Wajib</p>
              <p className="text-2xl font-bold">{creditSummary.required_credits} SKP</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <p className="text-purple-100 text-sm">Sisa Kebutuhan</p>
              <p className="text-2xl font-bold">
                {Math.max(0, creditSummary.required_credits - creditSummary.total_credits)} SKP
              </p>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <p className="text-purple-100 text-sm">Progress</p>
              <p className="text-2xl font-bold">
                {Math.round((creditSummary.total_credits / creditSummary.required_credits) * 100)}%
              </p>
            </div>
          </div>
          {creditSummary.breakdown && creditSummary.breakdown.length > 0 && (
            <div className="mt-4 pt-4 border-t border-white/20">
              <p className="text-sm text-purple-100 mb-2">Rincian per Kategori:</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {creditSummary.breakdown.map((item, idx) => (
                  <div key={idx} className="text-xs">
                    <span className="text-purple-200">{item.category}:</span>{" "}
                    <span className="font-semibold">{item.credits} SKP</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Competencies Overview */}
      {competencies.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Kompetensi</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {competencies.slice(0, 6).map((competency) => (
              <div key={competency.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">{competency.name}</h3>
                  <Star className="w-4 h-4 text-yellow-500" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">Tingkat</span>
                    <span className="text-sm font-medium capitalize text-gray-900">
                      {competency.proficiency_level.replace("_", " ")}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">Terakhir Dinilai</span>
                    <span className="text-xs text-gray-900">{formatDate(competency.last_assessed)}</span>
                  </div>
                  <span
                    className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getCompetencyStatusColor(
                      competency.status
                    )}`}
                  >
                    {getCompetencyStatusLabel(competency.status)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Training Modules */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Modul Pelatihan</h2>
          <div className="flex flex-wrap items-center gap-4">
            {/* Search */}
            <div className="relative flex-1 min-w-64">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Cari pelatihan..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Category Filter */}
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value as CategoryFilter)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Semua Kategori</option>
              <option value="compliance">Kepatuhan</option>
              <option value="safety">K3 & Keselamatan</option>
              <option value="clinical">Klinis</option>
              <option value="technical">Teknis</option>
              <option value="soft_skills">Soft Skills</option>
              <option value="leadership">Kepemimpinan</option>
              <option value="onboarding">Onboarding</option>
            </select>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Semua Status</option>
              <option value="not_started">Belum Dimulai</option>
              <option value="in_progress">Sedang Berjalan</option>
              <option value="completed">Selesai</option>
              <option value="overdue">Terlambat</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredModules.length === 0 ? (
          <div className="p-12 text-center">
            <BookOpen className="mx-auto h-16 w-16 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada modul pelatihan</h3>
            <p className="text-gray-600">
              {searchQuery || categoryFilter !== "all" || statusFilter !== "all"
                ? "Tidak ada pelatihan yang sesuai dengan filter"
                : "Belum ada pelatihan yang ditugaskan"}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredModules.map((module) => (
              <div key={module.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      {module.is_mandatory && (
                        <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-medium">
                          Wajib
                        </span>
                      )}
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${getCategoryColor(
                          module.category
                        )}`}
                      >
                        {getCategoryLabel(module.category)}
                      </span>
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                          module.status
                        )}`}
                      >
                        {getStatusLabel(module.status)}
                      </span>
                      <div className="flex items-center space-x-1 text-xs text-gray-500">
                        {getTypeIcon(module.type)}
                        <span>{module.type.replace("_", " ").toUpperCase()}</span>
                      </div>
                    </div>

                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{module.title}</h3>
                    <p className="text-sm text-gray-600 mb-4">{module.description}</p>

                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4" />
                        <span>{formatDuration(module.duration_minutes)}</span>
                      </div>
                      {module.due_date && (
                        <div className="flex items-center space-x-2">
                          <Calendar className="w-4 h-4" />
                          <span>Tenggat: {formatDate(module.due_date)}</span>
                        </div>
                      )}
                      {module.instructor && (
                        <div className="flex items-center space-x-2">
                          <span>Instruktor: {module.instructor}</span>
                        </div>
                      )}
                      {module.credits && module.credits > 0 && (
                        <div className="flex items-center space-x-2">
                          <Award className="w-4 h-4" />
                          <span className="font-medium text-purple-600">{module.credits} SKP</span>
                        </div>
                      )}
                    </div>

                    {/* Progress Bar */}
                    {module.status === "in_progress" && (
                      <div className="mt-4">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs text-gray-500">Progress</span>
                          <span className="text-xs font-medium text-gray-700">{module.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all"
                            style={{ width: `${module.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    )}

                    {/* Quiz Info */}
                    {module.quiz && module.status === "in_progress" && (
                      <div className="mt-3 text-xs text-gray-500">
                        <span>Kuis: {module.quiz.total_questions} soal | </span>
                        <span>Nilai lulus: {module.quiz.passing_score}% | </span>
                        <span>Percobaan: {module.quiz.attempts_used}/{module.quiz.attempts_allowed}</span>
                        {module.quiz.best_score && <span> | Terbaik: {module.quiz.best_score}%</span>}
                      </div>
                    )}

                    {/* Score Display */}
                    {module.status === "completed" && module.score !== undefined && (
                      <div className="mt-3">
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                            module.score >= module.passing_score
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          <Trophy className="w-4 h-4 mr-1" />
                          Nilai: {module.score}%
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="ml-4 flex items-center space-x-2">
                    {module.status === "completed" && module.certificate_url ? (
                      <button
                        onClick={() => handleDownloadCertificate(module.certificate_url ? 0 : 0)}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Sertifikat
                      </button>
                    ) : module.status === "completed" ? (
                      <button
                        onClick={() => handleStartModule(module)}
                        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        Lihat
                      </button>
                    ) : (
                      <button
                        onClick={() => handleStartModule(module)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
                      >
                        {module.status === "not_started" ? (
                          <>
                            <Play className="w-4 h-4 mr-2" />
                            Mulai
                          </>
                        ) : (
                          <>
                            <ChevronRight className="w-4 h-4 mr-2" />
                            Lanjutkan
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Certificates Section */}
      {certificates.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Sertifikat</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {certificates.map((cert) => (
              <div key={cert.id} className="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-colors">
                <div className="flex items-start space-x-3">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Award className="w-6 h-6 text-purple-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 text-sm mb-1">{cert.training_title}</h3>
                    <p className="text-xs text-gray-500 mb-2">{formatDate(cert.completion_date)}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-gray-900">Nilai: {cert.score}%</span>
                      {cert.credits > 0 && (
                        <span className="text-xs text-purple-600 font-medium">{cert.credits} SKP</span>
                      )}
                    </div>
                    {cert.valid_until && (
                      <p className="text-xs text-gray-500 mt-1">
                        Berlaku sampai: {formatDate(cert.valid_until)}
                      </p>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleDownloadCertificate(cert.id)}
                  className="mt-3 w-full px-3 py-2 border border-purple-300 text-purple-700 rounded-lg hover:bg-purple-50 flex items-center justify-center text-sm"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Unduh Sertifikat
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Module Detail Modal (Placeholder) */}
      {showModuleModal && selectedModule && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{selectedModule.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{getCategoryLabel(selectedModule.category)}</p>
                </div>
                <button
                  onClick={() => {
                    setShowModuleModal(false);
                    setSelectedModule(null);
                  }}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              <div>
                <p className="text-gray-700">{selectedModule.description}</p>
              </div>

              {/* Training Materials */}
              {selectedModule.materials && selectedModule.materials.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-3">Materi Pelatihan</h4>
                  <div className="space-y-2">
                    {selectedModule.materials.map((material) => (
                      <div
                        key={material.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex items-center space-x-3">
                          {getTypeIcon(material.type)}
                          <div>
                            <p className="font-medium text-gray-900">{material.title}</p>
                            <div className="flex items-center space-x-2 text-xs text-gray-500">
                              <span className="uppercase">{material.type}</span>
                              {material.duration_minutes && <span>| {formatDuration(material.duration_minutes)}</span>}
                              {material.file_size && <span>| {material.file_size}</span>}
                            </div>
                          </div>
                        </div>
                        <a
                          href={material.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-3 py-1 text-blue-600 hover:bg-blue-50 rounded text-sm flex items-center"
                        >
                          Buka <ExternalLink className="w-3 h-3 ml-1" />
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Quiz Section */}
              {selectedModule.quiz && selectedModule.status !== "completed" && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="text-sm font-semibold text-blue-900 mb-2">Kuis Penilaian</h4>
                  <div className="text-sm text-blue-800 space-y-1">
                    <p>Jumlah soal: {selectedModule.quiz.total_questions}</p>
                    <p>Nilai minimum lulus: {selectedModule.quiz.passing_score}%</p>
                    {selectedModule.quiz.time_limit_minutes && (
                      <p>Waktu: {selectedModule.quiz.time_limit_minutes} menit</p>
                    )}
                    <p>Percobaan tersisa: {selectedModule.quiz.attempts_allowed - selectedModule.quiz.attempts_used}</p>
                  </div>
                </div>
              )}

              {/* Start/Continue Quiz Button */}
              {selectedModule.quiz && selectedModule.status !== "completed" && (
                <button className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center font-medium">
                  <Target className="w-5 h-5 mr-2" />
                  Mulai Kuis
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
