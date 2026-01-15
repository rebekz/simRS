"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface RadiologyResultListItem {
  id: number;
  order_number: string;
  procedure_name: string;
  modality: string;
  body_part: string | null;
  exam_date: string;
  status: string;
  has_critical_findings: boolean;
  has_report: boolean;
  ordered_by: string;
}

interface RadiologyResultsListResponse {
  recent_results: RadiologyResultListItem[];
  historical_results: RadiologyResultListItem[];
  total_recent: number;
  total_historical: number;
  pending_count: number;
  critical_alerts: number;
}

export default function RadiologyResultsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<RadiologyResultsListResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"recent" | "historical">("recent");

  useEffect(() => {
    checkAuth();
    fetchRadiologyResults();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchRadiologyResults = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/portal/radiology-results?include_historical=true", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push("/portal/login");
          return;
        }
        throw new Error("Failed to fetch radiology results");
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load radiology results");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-100 text-green-700";
      case "ordered":
      case "scheduled": return "bg-yellow-100 text-yellow-700";
      case "in_progress": return "bg-blue-100 text-blue-700";
      case "cancelled": return "bg-red-100 text-red-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  const getModalityIcon = (modality: string) => {
    switch (modality.toUpperCase()) {
      case "CT": return "🔷";
      case "MRI": return "🧲";
      case "XRAY": return "💡";
      case "US": return "〰️";
      case "FLUOROSCOPY": return "📺";
      case "MAMMOGRAPHY": return "🎗️";
      case "NUCLEAR_MEDICINE":
      case "PET": return "☢️";
      default: return "📷";
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading radiology results...</p>
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
          <h1 className="text-2xl font-bold text-gray-900 mt-1">Radiology Results</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {results && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-white rounded-lg shadow p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Recent Exams</p>
                    <p className="text-2xl font-bold text-gray-900">{results.total_recent}</p>
                  </div>
                  <svg className="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Pending</p>
                    <p className="text-2xl font-bold text-yellow-600">{results.pending_count}</p>
                  </div>
                  <svg className="w-8 h-8 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>

              {results.critical_alerts > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg shadow p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-red-600">Critical Findings</p>
                      <p className="text-2xl font-bold text-red-700">{results.critical_alerts}</p>
                    </div>
                    <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                </div>
              )}
            </div>

            {/* Tabs */}
            <div className="bg-white rounded-lg shadow-md mb-6">
              <div className="border-b border-gray-200">
                <nav className="flex">
                  <button
                    onClick={() => setActiveTab("recent")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "recent"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Recent Results ({results.total_recent})
                  </button>
                  <button
                    onClick={() => setActiveTab("historical")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "historical"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Historical ({results.total_historical})
                  </button>
                </nav>
              </div>
            </div>

            {/* Results List */}
            <div className="space-y-4">
              {activeTab === "recent" && (
                <>
                  {results.recent_results.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-md p-8 text-center">
                      <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <p className="text-gray-500">No recent radiology results</p>
                    </div>
                  ) : (
                    results.recent_results.map((result) => (
                      <RadiologyResultCard key={result.id} result={result} />
                    ))
                  )}
                </>
              )}

              {activeTab === "historical" && (
                <>
                  {results.historical_results.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
                      No historical radiology results
                    </div>
                  ) : (
                    results.historical_results.map((result) => (
                      <RadiologyResultCard key={result.id} result={result} />
                    ))
                  )}
                </>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

interface RadiologyResultCardProps {
  result: RadiologyResultListItem;
}

function RadiologyResultCard({ result }: RadiologyResultCardProps) {
  const getModalityIcon = (modality: string) => {
    switch (modality.toUpperCase()) {
      case "CT": return "🔷";
      case "MRI": return "🧲";
      case "XRAY": return "💡";
      case "US": return "〰️";
      case "FLUOROSCOPY": return "📺";
      case "MAMMOGRAPHY": return "🎗️";
      case "NUCLEAR_MEDICINE":
      case "PET": return "☢️";
      default: return "📷";
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-100 text-green-700";
      case "ordered":
      case "scheduled": return "bg-yellow-100 text-yellow-700";
      case "in_progress": return "bg-blue-100 text-blue-700";
      case "cancelled": return "bg-red-100 text-red-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4 flex-1">
          <div className="text-4xl">{getModalityIcon(result.modality)}</div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-lg font-semibold text-gray-900">{result.procedure_name}</h3>
              <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(result.status)}`}>
                {result.status.replace("_", " ")}
              </span>
              {result.has_critical_findings && (
                <span className="px-2 py-1 text-xs font-medium rounded bg-red-100 text-red-700 flex items-center gap-1">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  Critical
                </span>
              )}
            </div>

            <div className="flex flex-wrap gap-4 text-sm">
              <div>
                <p className="text-gray-500">Modality</p>
                <p className="font-medium">{result.modality}</p>
              </div>
              {result.body_part && (
                <div>
                  <p className="text-gray-500">Body Part</p>
                  <p className="font-medium capitalize">{result.body_part}</p>
                </div>
              )}
              <div>
                <p className="text-gray-500">Exam Date</p>
                <p className="font-medium">{formatDate(result.exam_date)}</p>
              </div>
              <div>
                <p className="text-gray-500">Ordered By</p>
                <p className="font-medium">{result.ordered_by}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="ml-4 flex flex-col gap-2 items-end">
          {result.has_report && (
            <a
              href={`/portal/radiology/${result.id}`}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm"
            >
              View Report
            </a>
          )}
          <a
            href={`/portal/radiology/${result.id}`}
            className="text-sm text-indigo-600 hover:underline"
          >
            View Details
          </a>
        </div>
      </div>
    </div>
  );
}
