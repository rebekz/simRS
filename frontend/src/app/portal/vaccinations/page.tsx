"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface VaccinationRecord {
  id: number;
  vaccine_name: string;
  vaccine_type: string;
  date_administered: string;
  dose_number: number;
  total_doses: number;
  batch_number: string;
  administering_facility: string;
  administering_doctor: string;
  site: string;
  adverse_events: string | null;
  next_due_date: string | null;
  status: "complete" | "incomplete" | "scheduled" | "overdue";
  notes: string | null;
  created_at: string;
}

interface VaccinationStatus {
  total_vaccinations: number;
  complete_regimens: number;
  incomplete_regimens: number;
  overdue_vaccinations: number;
  upcoming_vaccinations: number;
}

interface VaccinationSummary {
  vaccination_status: VaccinationStatus;
  recent_vaccinations: VaccinationRecord[];
  upcoming_vaccinations: VaccinationRecord[];
  overdue_vaccinations: VaccinationRecord[];
  all_vaccinations: VaccinationRecord[];
}

export default function VaccinationRecordsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<VaccinationSummary | null>(null);
  const [selectedVaccination, setSelectedVaccination] = useState<VaccinationRecord | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [activeTab, setActiveTab] = useState<"all" | "complete" | "incomplete" | "upcoming" | "overdue">("all");

  useEffect(() => {
    checkAuth();
    fetchVaccinationRecords();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchVaccinationRecords = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/portal/vaccinations", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push("/portal/login");
          return;
        }
        throw new Error("Failed to fetch vaccination records");
      }

      const data = await response.json();
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load vaccination records");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "complete": return "bg-green-100 text-green-700";
      case "scheduled": return "bg-blue-100 text-blue-700";
      case "incomplete": return "bg-yellow-100 text-yellow-700";
      case "overdue": return "bg-red-100 text-red-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("id-ID", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const handleViewDetails = (vaccination: VaccinationRecord) => {
    setSelectedVaccination(vaccination);
    setShowDetailModal(true);
  };

  const handleCloseModal = () => {
    setShowDetailModal(false);
    setSelectedVaccination(null);
  };

  const handleDownloadCertificate = async () => {
    if (!selectedVaccination) return;

    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/portal/vaccinations/${selectedVaccination.id}/certificate`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to download certificate");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `vaccination-certificate-${selectedVaccination.id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to download certificate");
    }
  };

  const getFilteredVaccinations = () => {
    if (!summary) return [];

    switch (activeTab) {
      case "complete":
        return summary.all_vaccinations.filter(v => v.status === "complete");
      case "incomplete":
        return summary.all_vaccinations.filter(v => v.status === "incomplete");
      case "upcoming":
        return summary.upcoming_vaccinations;
      case "overdue":
        return summary.overdue_vaccinations;
      default:
        return summary.all_vaccinations;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading vaccination records...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <a href="/portal/dashboard" className="text-indigo-600 hover:underline text-sm">
            ← Back to Dashboard
          </a>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">Vaccination Records</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {summary && (
          <>
            {/* Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-lg shadow-md p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Total Vaccinations</p>
                    <p className="text-2xl font-bold text-gray-900">{summary.vaccination_status.total_vaccinations}</p>
                  </div>
                  <svg className="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Complete Regimens</p>
                    <p className="text-2xl font-bold text-green-600">{summary.vaccination_status.complete_regimens}</p>
                  </div>
                  <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Incomplete Regimens</p>
                    <p className="text-2xl font-bold text-yellow-600">{summary.vaccination_status.incomplete_regimens}</p>
                  </div>
                  <svg className="w-8 h-8 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Overdue Vaccinations</p>
                    <p className="text-2xl font-bold text-red-600">{summary.vaccination_status.overdue_vaccinations}</p>
                  </div>
                  <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Filter Tabs */}
            <div className="bg-white rounded-lg shadow-md mb-6">
              <div className="border-b border-gray-200">
                <nav className="flex">
                  <button
                    onClick={() => setActiveTab("all")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "all"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    All ({summary.all_vaccinations.length})
                  </button>
                  <button
                    onClick={() => setActiveTab("complete")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "complete"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Complete ({summary.vaccination_status.complete_regimens})
                  </button>
                  <button
                    onClick={() => setActiveTab("incomplete")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "incomplete"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Incomplete ({summary.vaccination_status.incomplete_regimens})
                  </button>
                  <button
                    onClick={() => setActiveTab("upcoming")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "upcoming"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Upcoming ({summary.vaccination_status.upcoming_vaccinations})
                  </button>
                  <button
                    onClick={() => setActiveTab("overdue")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "overdue"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Overdue ({summary.vaccination_status.overdue_vaccinations})
                  </button>
                </nav>
              </div>
            </div>

            {/* Vaccination List */}
            <div className="space-y-4">
              {getFilteredVaccinations().length === 0 ? (
                <div className="bg-white rounded-lg shadow-md p-8 text-center">
                  <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                  </svg>
                  <p className="text-gray-500">No vaccination records found</p>
                </div>
              ) : (
                getFilteredVaccinations().map((vaccination) => (
                  <VaccinationCard
                    key={vaccination.id}
                    vaccination={vaccination}
                    onViewDetails={handleViewDetails}
                  />
                ))
              )}
            </div>
          </>
        )}
      </main>

      {/* Detail Modal */}
      {showDetailModal && selectedVaccination && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">Vaccination Details</h2>
                <button
                  onClick={handleCloseModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-2 mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">{selectedVaccination.vaccine_name}</h3>
                  <span className={`px-3 py-1 text-sm font-medium rounded capitalize ${getStatusColor(selectedVaccination.status)}`}>
                    {selectedVaccination.status}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Vaccine Type</p>
                    <p className="font-medium text-gray-900">{selectedVaccination.vaccine_type}</p>
                  </div>

                  <div>
                    <p className="text-sm text-gray-500">Date Administered</p>
                    <p className="font-medium text-gray-900">{formatDate(selectedVaccination.date_administered)}</p>
                  </div>

                  <div>
                    <p className="text-sm text-gray-500">Dose</p>
                    <p className="font-medium text-gray-900">
                      {selectedVaccination.dose_number} of {selectedVaccination.total_doses}
                    </p>
                  </div>

                  <div>
                    <p className="text-sm text-gray-500">Batch Number</p>
                    <p className="font-medium text-gray-900">{selectedVaccination.batch_number}</p>
                  </div>

                  <div>
                    <p className="text-sm text-gray-500">Administering Facility</p>
                    <p className="font-medium text-gray-900">{selectedVaccination.administering_facility}</p>
                  </div>

                  <div>
                    <p className="text-sm text-gray-500">Administering Doctor</p>
                    <p className="font-medium text-gray-900">{selectedVaccination.administering_doctor}</p>
                  </div>

                  <div>
                    <p className="text-sm text-gray-500">Site</p>
                    <p className="font-medium text-gray-900">{selectedVaccination.site}</p>
                  </div>

                  {selectedVaccination.next_due_date && (
                    <div>
                      <p className="text-sm text-gray-500">Next Due Date</p>
                      <p className="font-medium text-gray-900">{formatDate(selectedVaccination.next_due_date)}</p>
                    </div>
                  )}

                  {selectedVaccination.adverse_events && (
                    <div className="md:col-span-2">
                      <p className="text-sm text-gray-500">Adverse Events</p>
                      <p className="font-medium text-gray-900">{selectedVaccination.adverse_events}</p>
                    </div>
                  )}

                  {selectedVaccination.notes && (
                    <div className="md:col-span-2">
                      <p className="text-sm text-gray-500">Notes</p>
                      <p className="font-medium text-gray-900">{selectedVaccination.notes}</p>
                    </div>
                  )}
                </div>

                <div className="flex gap-3 pt-4 border-t">
                  <button
                    onClick={handleDownloadCertificate}
                    className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center justify-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download Certificate
                  </button>
                  <button
                    onClick={handleCloseModal}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    Close
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

interface VaccinationCardProps {
  vaccination: VaccinationRecord;
  onViewDetails: (vaccination: VaccinationRecord) => void;
}

function VaccinationCard({ vaccination, onViewDetails }: VaccinationCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "complete": return "bg-green-100 text-green-700";
      case "scheduled": return "bg-blue-100 text-blue-700";
      case "incomplete": return "bg-yellow-100 text-yellow-700";
      case "overdue": return "bg-red-100 text-red-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("id-ID", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">{vaccination.vaccine_name}</h3>
            <span className={`px-2 py-1 text-xs font-medium rounded capitalize ${getStatusColor(vaccination.status)}`}>
              {vaccination.status}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Vaccine Type</p>
              <p className="font-medium">{vaccination.vaccine_type}</p>
            </div>
            <div>
              <p className="text-gray-500">Date Administered</p>
              <p className="font-medium">{formatDate(vaccination.date_administered)}</p>
            </div>
            <div>
              <p className="text-gray-500">Dose</p>
              <p className="font-medium">{vaccination.dose_number} of {vaccination.total_doses}</p>
            </div>
            <div>
              <p className="text-gray-500">Facility</p>
              <p className="font-medium">{vaccination.administering_facility}</p>
            </div>
          </div>

          {vaccination.next_due_date && (
            <div className="mt-3 text-sm">
              <p className="text-gray-500">Next Due Date</p>
              <p className="font-medium text-gray-900">{formatDate(vaccination.next_due_date)}</p>
            </div>
          )}
        </div>

        <button
          onClick={() => onViewDetails(vaccination)}
          className="ml-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm"
        >
          View Details
        </button>
      </div>
    </div>
  );
}
