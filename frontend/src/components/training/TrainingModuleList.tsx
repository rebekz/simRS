"use client";

/**
 * Training Module List Component for STORY-038
 *
 * Provides comprehensive module browser with:
 * - Filter by category, difficulty, status
 * - Search functionality
 * - Module cards with details
 * - Start/Continue buttons
 * - Completion indicators
 */

import { useState, useEffect } from "react";
import {
  BookOpen,
  Search,
  Filter,
  Play,
  CheckCircle,
  Clock,
  Star,
  Users,
  TrendingUp,
  Grid,
  List,
  SlidersHorizontal,
  Video,
  FileText,
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
  prerequisites?: number[];
  created_at: string;
  updated_at: string;
  enrollment_count?: number;
  completion_rate?: number;
  rating?: number;
  user_status?: "not_started" | "in_progress" | "completed";
  user_progress?: number;
}

interface Category {
  name: string;
  count: number;
}

export function TrainingModuleList() {
  const [modules, setModules] = useState<TrainingModule[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Filter states
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedDifficulty, setSelectedDifficulty] = useState("");
  const [selectedContentType, setSelectedContentType] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadModules();
  }, []);

  const loadModules = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");

      const response = await fetch("/api/v1/training/modules", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setModules(data.modules || []);

        // Extract unique categories
        const categoryMap = new Map<string, number>();
        data.modules?.forEach((module: TrainingModule) => {
          categoryMap.set(module.category, (categoryMap.get(module.category) || 0) + 1);
        });
        setCategories(
          Array.from(categoryMap.entries()).map(([name, count]) => ({ name, count }))
        );
      }
    } catch (error) {
      console.error("Failed to load modules:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getDifficultyBadge = (difficulty: string) => {
    switch (difficulty) {
      case "beginner":
        return (
          <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
            <Star className="h-3 w-3 mr-1" />
            Pemula
          </span>
        );
      case "intermediate":
        return (
          <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
            <Star className="h-3 w-3 mr-1" />
            Menengah
          </span>
        );
      case "advanced":
        return (
          <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">
            <Star className="h-3 w-3 mr-1" />
            Lanjutan
          </span>
        );
      default:
        return null;
    }
  };

  const getStatusBadge = (status?: string) => {
    if (!status) return null;

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
        return null;
    }
  };

  const getContentTypeIcon = (type: string) => {
    switch (type) {
      case "video":
        return <Video className="h-4 w-4" />;
      case "document":
        return <FileText className="h-4 w-4" />;
      case "interactive":
        return <MousePointer className="h-4 w-4" />;
      case "scorm":
        return <Package className="h-4 w-4" />;
      default:
        return <BookOpen className="h-4 w-4" />;
    }
  };

  const getCategoryEmoji = (category: string) => {
    const emojiMap: Record<string, string> = {
      keperawatan: "👩‍⚕️",
      kedokteran: "👨‍⚕️",
      farmasi: "💊",
      keamanan: "🔒",
      keselamatan: "⚠️",
      administrasi: "📋",
      keperawatan_gawat_darurat: "🚑",
      manajemen_rumah_sakit: "🏥",
    };
    return emojiMap[category.toLowerCase()] || "📚";
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}j ${mins}m`;
    }
    return `${mins}m`;
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`h-4 w-4 ${
              star <= rating ? "fill-yellow-400 text-yellow-400" : "text-gray-300"
            }`}
          />
        ))}
      </div>
    );
  };

  const filteredModules = modules.filter((module) => {
    // Search filter
    if (
      searchTerm &&
      !module.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !module.description.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !module.code.toLowerCase().includes(searchTerm.toLowerCase())
    ) {
      return false;
    }

    // Category filter
    if (selectedCategory && module.category !== selectedCategory) {
      return false;
    }

    // Difficulty filter
    if (selectedDifficulty && module.difficulty !== selectedDifficulty) {
      return false;
    }

    // Content type filter
    if (selectedContentType && module.content_type !== selectedContentType) {
      return false;
    }

    // Status filter
    if (selectedStatus && module.user_status !== selectedStatus) {
      return false;
    }

    return true;
  });

  if (isLoading && modules.length === 0) {
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
            Modul Pelatihan
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Jelajahi dan mulai modul pelatihan yang tersedia
          </p>
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex items-center space-x-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Cari modul pelatihan..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm w-full focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Toggle Filters */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <SlidersHorizontal className="h-4 w-4 mr-2" />
            Filter
            {(selectedCategory || selectedDifficulty || selectedContentType || selectedStatus) && (
              <span className="ml-2 inline-flex items-center justify-center px-2 py-0.5 text-xs font-bold leading-none text-white bg-blue-600 rounded-full">
                {[selectedCategory, selectedDifficulty, selectedContentType, selectedStatus].filter(
                  Boolean
                ).length}
              </span>
            )}
          </button>

          {/* View Mode Toggle */}
          <div className="flex items-center border border-gray-300 rounded-md">
            <button
              onClick={() => setViewMode("grid")}
              className={`px-3 py-2 ${
                viewMode === "grid"
                  ? "bg-blue-50 text-blue-600"
                  : "bg-white text-gray-500 hover:bg-gray-50"
              }`}
            >
              <Grid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`px-3 py-2 ${
                viewMode === "list"
                  ? "bg-blue-50 text-blue-600"
                  : "bg-white text-gray-500 hover:bg-gray-50"
              }`}
            >
              <List className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Filter Panel */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Kategori
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Semua Kategori</option>
                  {categories.map((cat) => (
                    <option key={cat.name} value={cat.name}>
                      {cat.name} ({cat.count})
                    </option>
                  ))}
                </select>
              </div>

              {/* Difficulty Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tingkat Kesulitan
                </label>
                <select
                  value={selectedDifficulty}
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Semua Tingkat</option>
                  <option value="beginner">Pemula</option>
                  <option value="intermediate">Menengah</option>
                  <option value="advanced">Lanjutan</option>
                </select>
              </div>

              {/* Content Type Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipe Konten
                </label>
                <select
                  value={selectedContentType}
                  onChange={(e) => setSelectedContentType(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Semua Tipe</option>
                  <option value="video">Video</option>
                  <option value="document">Dokumen</option>
                  <option value="interactive">Interaktif</option>
                  <option value="scorm">SCORM</option>
                </select>
              </div>

              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Semua Status</option>
                  <option value="not_started">Belum Dimulai</option>
                  <option value="in_progress">Sedang Berjalan</option>
                  <option value="completed">Selesai</option>
                </select>
              </div>
            </div>

            {/* Clear Filters */}
            <div className="mt-3 flex items-center justify-end">
              <button
                onClick={() => {
                  setSelectedCategory("");
                  setSelectedDifficulty("");
                  setSelectedContentType("");
                  setSelectedStatus("");
                }}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Hapus semua filter
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Results Count */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <p>
          Menampilkan {filteredModules.length} dari {modules.length} modul
        </p>
      </div>

      {/* Grid View */}
      {viewMode === "grid" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredModules.map((module) => (
            <div
              key={module.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow overflow-hidden"
            >
              {/* Module Header */}
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-3xl">{getCategoryEmoji(module.category)}</span>
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{module.title}</h3>
                      <p className="text-xs text-gray-500">{module.code}</p>
                    </div>
                  </div>
                  {module.is_mandatory && (
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">
                      Wajib
                    </span>
                  )}
                </div>

                <p className="text-sm text-gray-600 mt-3 line-clamp-2">{module.description}</p>

                {/* Module Info */}
                <div className="mt-4 space-y-2">
                  <div className="flex items-center text-sm text-gray-500">
                    {getContentTypeIcon(module.content_type)}
                    <span className="ml-2 capitalize">
                      {module.content_type === "video"
                        ? "Video"
                        : module.content_type === "document"
                        ? "Dokumen"
                        : module.content_type === "scorm"
                        ? "SCORM"
                        : "Interaktif"}
                    </span>
                    <span className="mx-2">•</span>
                    <Clock className="h-4 w-4" />
                    <span className="ml-1">{formatDuration(module.duration_minutes)}</span>
                  </div>

                  <div className="flex items-center text-sm text-gray-500">
                    <FileText className="h-4 w-4" />
                    <span className="ml-1">{module.total_lessons} pelajaran</span>
                  </div>

                  {module.enrollment_count !== undefined && (
                    <div className="flex items-center text-sm text-gray-500">
                      <Users className="h-4 w-4" />
                      <span className="ml-1">{module.enrollment_count} peserta</span>
                    </div>
                  )}
                </div>

                {/* Badges */}
                <div className="mt-4 flex items-center space-x-2">
                  {getDifficultyBadge(module.difficulty)}
                  {module.user_status && getStatusBadge(module.user_status)}
                </div>

                {/* Progress */}
                {module.user_progress !== undefined && module.user_status === "in_progress" && (
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <span>Progres</span>
                      <span>{module.user_progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${module.user_progress}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                {/* Rating */}
                {module.rating !== undefined && (
                  <div className="mt-3 flex items-center space-x-2">
                    {renderStars(module.rating)}
                    <span className="text-xs text-gray-500">({module.rating})</span>
                  </div>
                )}
              </div>

              {/* Action Button */}
              <div className="px-6 pb-6">
                <button
                  className={`w-full inline-flex items-center justify-center px-4 py-2 border rounded-md text-sm font-medium ${
                    module.user_status === "completed"
                      ? "border-gray-300 text-gray-700 bg-gray-50"
                      : "border-transparent text-white bg-blue-600 hover:bg-blue-700"
                  }`}
                >
                  {module.user_status === "completed" ? (
                    <>
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Selesai
                    </>
                  ) : module.user_status === "in_progress" ? (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Lanjutkan
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Mulai
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* List View */}
      {viewMode === "list" && (
        <div className="bg-white shadow rounded-lg divide-y divide-gray-200">
          {filteredModules.map((module) => (
            <div key={module.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <span className="text-4xl">{getCategoryEmoji(module.category)}</span>
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h3 className="text-lg font-medium text-gray-900">{module.title}</h3>
                      {module.is_mandatory && (
                        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">
                          Wajib
                        </span>
                      )}
                      {getDifficultyBadge(module.difficulty)}
                      {module.user_status && getStatusBadge(module.user_status)}
                    </div>
                    <p className="text-sm text-gray-500">{module.code}</p>
                    <p className="text-sm text-gray-600 mt-2">{module.description}</p>

                    <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                      <div className="flex items-center">
                        {getContentTypeIcon(module.content_type)}
                        <span className="ml-1 capitalize">{module.content_type}</span>
                      </div>
                      <div className="flex items-center">
                        <Clock className="h-4 w-4" />
                        <span className="ml-1">{formatDuration(module.duration_minutes)}</span>
                      </div>
                      <div className="flex items-center">
                        <FileText className="h-4 w-4" />
                        <span className="ml-1">{module.total_lessons} pelajaran</span>
                      </div>
                      {module.enrollment_count && (
                        <div className="flex items-center">
                          <Users className="h-4 w-4" />
                          <span className="ml-1">{module.enrollment_count} peserta</span>
                        </div>
                      )}
                      {module.completion_rate !== undefined && (
                        <div className="flex items-center">
                          <TrendingUp className="h-4 w-4" />
                          <span className="ml-1">{module.completion_rate}% selesai</span>
                        </div>
                      )}
                    </div>

                    {module.user_progress !== undefined && module.user_status === "in_progress" && (
                      <div className="mt-3 max-w-xs">
                        <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                          <span>Progres</span>
                          <span>{module.user_progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${module.user_progress}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="ml-6">
                  <button
                    className={`inline-flex items-center px-4 py-2 border rounded-md text-sm font-medium ${
                      module.user_status === "completed"
                        ? "border-gray-300 text-gray-700 bg-gray-50"
                        : "border-transparent text-white bg-blue-600 hover:bg-blue-700"
                    }`}
                  >
                    {module.user_status === "completed" ? (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Selesai
                      </>
                    ) : module.user_status === "in_progress" ? (
                      <>
                        <Play className="h-4 w-4 mr-2" />
                        Lanjutkan
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-2" />
                        Mulai
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {filteredModules.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <BookOpen className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <p>Tidak ada modul yang cocok dengan filter</p>
          <button
            onClick={() => {
              setSearchTerm("");
              setSelectedCategory("");
              setSelectedDifficulty("");
              setSelectedContentType("");
              setSelectedStatus("");
            }}
            className="mt-4 text-sm text-blue-600 hover:text-blue-800"
          >
            Hapus filter
          </button>
        </div>
      )}
    </div>
  );
}
