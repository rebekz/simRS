"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type DocumentCategory = "all" | "clinical_notes" | "lab_results" | "radiology" | "prescriptions" | "insurance" | "id" | "other";

interface MedicalDocument {
  id: number;
  document_name: string;
  category: string;
  upload_date: string;
  file_type: string;
  file_size: number;
  status: "active" | "archived" | "pending";
  description: string | null;
  uploaded_by: string;
}

interface DocumentStatistics {
  total_documents: number;
  clinical_notes: number;
  lab_results: number;
  radiology: number;
  prescriptions: number;
  insurance: number;
  id_documents: number;
  other: number;
}

interface MedicalDocumentsResponse {
  documents: MedicalDocument[];
  statistics: DocumentStatistics;
  total: number;
  page: number;
  per_page: number;
}

export default function MedicalRecordsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<MedicalDocumentsResponse | null>(null);
  const [activeTab, setActiveTab] = useState<DocumentCategory>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedDocument, setSelectedDocument] = useState<MedicalDocument | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<MedicalDocument | null>(null);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  useEffect(() => {
    checkAuth();
    fetchMedicalDocuments();
  }, [currentPage]);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchMedicalDocuments = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/portal/documents/medical?page=${currentPage}&per_page=10`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push("/portal/login");
          return;
        }
        throw new Error("Gagal memuat rekam medis");
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal memuat rekam medis");
    } finally {
      setLoading(false);
    }
  };

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      clinical_notes: "Catatan Klinis",
      lab_results: "Hasil Lab",
      radiology: "Radiologi",
      prescriptions: "Resep",
      insurance: "Asuransi",
      id: "Identitas",
      other: "Lainnya",
    };
    return labels[category] || category;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-green-100 text-green-700";
      case "archived": return "bg-gray-100 text-gray-700";
      case "pending": return "bg-yellow-100 text-yellow-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      active: "Aktif",
      archived: "Diarsipkan",
      pending: "Menunggu",
    };
    return labels[status] || status;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("id-ID", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const getCategoryCount = (category: DocumentCategory) => {
    if (!data) return 0;
    if (category === "all") return data.total;
    return data.statistics[category === "id" ? "id_documents" : category + "s" as keyof DocumentStatistics] as number || 0;
  };

  const getFilteredDocuments = () => {
    if (!data) return [];

    let filtered = data.documents;

    // Filter by category
    if (activeTab !== "all") {
      filtered = filtered.filter(doc => doc.category === activeTab);
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(doc =>
        doc.document_name.toLowerCase().includes(query) ||
        (doc.description && doc.description.toLowerCase().includes(query))
      );
    }

    return filtered;
  };

  const handleViewDetails = (document: MedicalDocument) => {
    setSelectedDocument(document);
    setShowDetailModal(true);
  };

  const handleCloseDetailModal = () => {
    setShowDetailModal(false);
    setSelectedDocument(null);
  };

  const handleDownload = async () => {
    if (!selectedDocument) return;

    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/portal/documents/medical/${selectedDocument.id}/download`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Gagal mengunduh dokumen");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = selectedDocument.document_name;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      showSuccessMessage("Dokumen berhasil diunduh");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Gagal mengunduh dokumen");
    }
  };

  const handleShare = () => {
    // Mock share functionality
    alert("Fitur berbagi dokumen akan segera tersedia. Anda dapat membagikan dokumen melalui tautan aman yang dikirim ke email penerima.");
  };

  const handleDeleteClick = (document: MedicalDocument) => {
    setDocumentToDelete(document);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    if (!documentToDelete) return;

    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/portal/documents/medical/${documentToDelete.id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Gagal menghapus dokumen");
      }

      showSuccessMessage("Dokumen berhasil dihapus");
      setShowDeleteModal(false);
      setDocumentToDelete(null);
      fetchMedicalDocuments();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Gagal menghapus dokumen");
    }
  };

  const handleArchive = async (document: MedicalDocument) => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/portal/documents/medical/${document.id}/archive`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ status: "archived" }),
      });

      if (!response.ok) {
        throw new Error("Gagal mengarsipkan dokumen");
      }

      showSuccessMessage("Dokumen berhasil diarsipkan");
      fetchMedicalDocuments();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Gagal mengarsipkan dokumen");
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    setUploadingFile(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("document_name", file.name);
      formData.append("category", activeTab === "all" ? "other" : activeTab);

      const response = await fetch("/api/v1/portal/documents/medical/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Gagal mengunggah dokumen");
      }

      showSuccessMessage("Dokumen berhasil diunggah");
      setShowUploadModal(false);
      fetchMedicalDocuments();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Gagal mengunggah dokumen");
    } finally {
      setUploadingFile(false);
      // Reset file input
      event.target.value = "";
    }
  };

  const showSuccessMessage = (message: string) => {
    setActionSuccess(message);
    setTimeout(() => setActionSuccess(null), 3000);
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Memuat rekam medis...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <a href="/portal/dashboard" className="text-indigo-600 hover:underline text-sm">
                ← Kembali ke Dashboard
              </a>
              <h1 className="text-2xl font-bold text-gray-900 mt-1">Rekam Medis & Dokumen</h1>
            </div>
            <button
              onClick={() => setShowUploadModal(true)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Unggah Dokumen
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {actionSuccess && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-800">{actionSuccess}</p>
          </div>
        )}

        {data && (
          <>
            {/* Statistics Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-lg shadow-md p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Total Dokumen</p>
                    <p className="text-2xl font-bold text-gray-900">{data.statistics.total_documents}</p>
                  </div>
                  <svg className="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Catatan Klinis</p>
                    <p className="text-2xl font-bold text-indigo-600">{data.statistics.clinical_notes}</p>
                  </div>
                  <svg className="w-8 h-8 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Hasil Lab</p>
                    <p className="text-2xl font-bold text-green-600">{data.statistics.lab_results}</p>
                  </div>
                  <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                  </svg>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Radiologi</p>
                    <p className="text-2xl font-bold text-purple-600">{data.statistics.radiology}</p>
                  </div>
                  <svg className="w-8 h-8 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Category Tabs */}
            <div className="bg-white rounded-lg shadow-md mb-6">
              <div className="border-b border-gray-200">
                <nav className="flex flex-wrap">
                  <button
                    onClick={() => { setActiveTab("all"); setCurrentPage(1); }}
                    className={`px-4 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "all"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Semua ({getCategoryCount("all")})
                  </button>
                  <button
                    onClick={() => { setActiveTab("clinical_notes"); setCurrentPage(1); }}
                    className={`px-4 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "clinical_notes"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Catatan Klinis ({getCategoryCount("clinical_notes")})
                  </button>
                  <button
                    onClick={() => { setActiveTab("lab_results"); setCurrentPage(1); }}
                    className={`px-4 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "lab_results"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Hasil Lab ({getCategoryCount("lab_results")})
                  </button>
                  <button
                    onClick={() => { setActiveTab("radiology"); setCurrentPage(1); }}
                    className={`px-4 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "radiology"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Radiologi ({getCategoryCount("radiology")})
                  </button>
                  <button
                    onClick={() => { setActiveTab("prescriptions"); setCurrentPage(1); }}
                    className={`px-4 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "prescriptions"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Resep ({getCategoryCount("prescriptions")})
                  </button>
                  <button
                    onClick={() => { setActiveTab("insurance"); setCurrentPage(1); }}
                    className={`px-4 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "insurance"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Asuransi ({getCategoryCount("insurance")})
                  </button>
                  <button
                    onClick={() => { setActiveTab("id"); setCurrentPage(1); }}
                    className={`px-4 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "id"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Identitas ({getCategoryCount("id")})
                  </button>
                  <button
                    onClick={() => { setActiveTab("other"); setCurrentPage(1); }}
                    className={`px-4 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "other"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Lainnya ({getCategoryCount("other")})
                  </button>
                </nav>
              </div>

              {/* Search Bar */}
              <div className="p-4 border-b border-gray-200">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Cari dokumen berdasarkan nama..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                  <svg className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Document List */}
            <div className="space-y-4">
              {getFilteredDocuments().length === 0 ? (
                <div className="bg-white rounded-lg shadow-md p-8 text-center">
                  <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-gray-500">Tidak ada dokumen ditemukan</p>
                  {searchQuery && (
                    <p className="text-sm text-gray-400 mt-2">Coba kata kunci pencarian lain</p>
                  )}
                </div>
              ) : (
                getFilteredDocuments().map((document) => (
                  <DocumentCard
                    key={document.id}
                    document={document}
                    onViewDetails={handleViewDetails}
                    onDelete={handleDeleteClick}
                    onArchive={handleArchive}
                  />
                ))
              )}
            </div>

            {/* Pagination */}
            {data.total > data.per_page && (
              <div className="mt-6 flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Menampilkan halaman {currentPage} dari {Math.ceil(data.total / data.per_page)}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage >= Math.ceil(data.total / data.per_page)}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Detail Modal */}
      {showDetailModal && selectedDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">Detail Dokumen</h2>
                <button
                  onClick={handleCloseDetailModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{selectedDocument.document_name}</h3>
                  <div className="flex items-center gap-2 mt-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(selectedDocument.status)}`}>
                      {getStatusLabel(selectedDocument.status)}
                    </span>
                    <span className="px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-700">
                      {getCategoryLabel(selectedDocument.category)}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Tanggal Unggah</p>
                    <p className="font-medium text-gray-900">{formatDate(selectedDocument.upload_date)}</p>
                  </div>

                  <div>
                    <p className="text-sm text-gray-500">Unggah Oleh</p>
                    <p className="font-medium text-gray-900">{selectedDocument.uploaded_by}</p>
                  </div>

                  <div>
                    <p className="text-sm text-gray-500">Tipe File</p>
                    <p className="font-medium text-gray-900">{selectedDocument.file_type.toUpperCase()}</p>
                  </div>

                  <div>
                    <p className="text-sm text-gray-500">Ukuran File</p>
                    <p className="font-medium text-gray-900">{formatFileSize(selectedDocument.file_size)}</p>
                  </div>

                  {selectedDocument.description && (
                    <div className="md:col-span-2">
                      <p className="text-sm text-gray-500">Deskripsi</p>
                      <p className="font-medium text-gray-900">{selectedDocument.description}</p>
                    </div>
                  )}
                </div>

                <div className="flex gap-3 pt-4 border-t">
                  <button
                    onClick={handleDownload}
                    className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center justify-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Unduh
                  </button>
                  <button
                    onClick={handleShare}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center justify-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                    </svg>
                    Bagikan
                  </button>
                  <button
                    onClick={handleCloseDetailModal}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    Tutup
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">Unggah Dokumen</h2>
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Pilih File
                  </label>
                  <input
                    type="file"
                    onChange={handleFileUpload}
                    disabled={uploadingFile}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Format yang didukung: PDF, JPG, PNG, DOC, DOCX (Maks. 10MB)
                  </p>
                </div>

                {uploadingFile && (
                  <div className="flex items-center justify-center py-4">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                    <span className="ml-3 text-sm text-gray-600">Mengunggah...</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && documentToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">Konfirmasi Hapus</h2>
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                <p className="text-gray-700">
                  Apakah Anda yakin ingin menghapus dokumen "<strong>{documentToDelete.document_name}</strong>"?
                </p>
                <p className="text-sm text-red-600">
                  Tindakan ini tidak dapat dibatalkan.
                </p>

                <div className="flex gap-3 pt-4">
                  <button
                    onClick={handleDeleteConfirm}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                  >
                    Ya, Hapus
                  </button>
                  <button
                    onClick={() => setShowDeleteModal(false)}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    Batal
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

interface DocumentCardProps {
  document: MedicalDocument;
  onViewDetails: (document: MedicalDocument) => void;
  onDelete: (document: MedicalDocument) => void;
  onArchive: (document: MedicalDocument) => void;
}

function DocumentCard({ document, onViewDetails, onDelete, onArchive }: DocumentCardProps) {
  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      clinical_notes: "Catatan Klinis",
      lab_results: "Hasil Lab",
      radiology: "Radiologi",
      prescriptions: "Resep",
      insurance: "Asuransi",
      id: "Identitas",
      other: "Lainnya",
    };
    return labels[category] || category;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-green-100 text-green-700";
      case "archived": return "bg-gray-100 text-gray-700";
      case "pending": return "bg-yellow-100 text-yellow-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      active: "Aktif",
      archived: "Diarsipkan",
      pending: "Menunggu",
    };
    return labels[status] || status;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("id-ID", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const getFileIcon = (fileType: string) => {
    const iconClasses = "w-8 h-8";

    switch (fileType.toLowerCase()) {
      case "pdf":
        return (
          <svg className={`${iconClasses} text-red-500`} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
          </svg>
        );
      case "jpg":
      case "jpeg":
      case "png":
        return (
          <svg className={`${iconClasses} text-green-500`} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
          </svg>
        );
      case "doc":
      case "docx":
        return (
          <svg className={`${iconClasses} text-blue-500`} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg className={`${iconClasses} text-gray-500`} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4 flex-1">
          <div className="flex-shrink-0">
            {getFileIcon(document.file_type)}
          </div>

          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-lg font-semibold text-gray-900">{document.document_name}</h3>
              <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(document.status)}`}>
                {getStatusLabel(document.status)}
              </span>
              <span className="px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-700">
                {getCategoryLabel(document.category)}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Tanggal Unggah</p>
                <p className="font-medium">{formatDate(document.upload_date)}</p>
              </div>
              <div>
                <p className="text-gray-500">Tipe File</p>
                <p className="font-medium">{document.file_type.toUpperCase()}</p>
              </div>
              <div>
                <p className="text-gray-500">Ukuran</p>
                <p className="font-medium">{formatFileSize(document.file_size)}</p>
              </div>
              <div>
                <p className="text-gray-500">Unggah Oleh</p>
                <p className="font-medium">{document.uploaded_by}</p>
              </div>
            </div>

            {document.description && (
              <p className="text-sm text-gray-600 mt-2">{document.description}</p>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-2 ml-4">
          <button
            onClick={() => onViewDetails(document)}
            className="px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Lihat
          </button>
          {document.status === "active" && (
            <button
              onClick={() => onArchive(document)}
              className="px-3 py-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 text-sm"
            >
              Arsipkan
            </button>
          )}
          <button
            onClick={() => onDelete(document)}
            className="px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 text-sm"
          >
            Hapus
          </button>
        </div>
      </div>
    </div>
  );
}
