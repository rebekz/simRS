"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";

interface TestResultItem {
  test_name: string;
  result_value: string;
  unit: string | null;
  reference_range: string | null;
  abnormal_flag: string | null;
  is_abnormal: boolean;
  is_critical: boolean;
}

interface LabResultDetail {
  id: number;
  order_number: string;
  test_name: string;
  test_code: string;
  loinc_code: string | null;
  status: string;
  priority: string;
  clinical_indication: string | null;
  specimen_type: string | null;
  results: TestResultItem[];
  results_interpretation: string | null;
  reference_range: string | null;
  abnormal_flag: boolean | null;
  test_description: string | null;
  what_it_measures: string | null;
  what_results_mean: string | null;
  ordered_at: string;
  specimen_collected_at: string | null;
  completed_at: string | null;
  ordered_by_name: string;
}

export default function LabResultDetailPage() {
  const router = useRouter();
  const params = useParams();
  const labOrderId = parseInt(params.id as string);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<LabResultDetail | null>(null);

  useEffect(() => {
    checkAuth();
    fetchLabResultDetail();
  }, [labOrderId]);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchLabResultDetail = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/portal/lab-results/${labOrderId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push("/portal/login");
          return;
        }
        if (response.status === 404) {
          setError("Lab result not found");
          setLoading(false);
          return;
        }
        throw new Error("Failed to fetch lab result details");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load lab result");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "N/A";
    const date = new Date(dateStr);
    return date.toLocaleDateString("id-ID", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getResultColor = (item: TestResultItem) => {
    if (item.is_critical) return "text-red-600 bg-red-50";
    if (item.is_abnormal) return "text-yellow-600 bg-yellow-50";
    return "text-gray-900";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading lab result...</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-md p-8 max-w-md text-center">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 2a10 10 0 100 20 10 10 0 000-20z" />
          </svg>
          <p className="text-gray-500 mb-4">{error || "Lab result not found"}</p>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link href="/portal/lab-results" className="text-indigo-600 hover:underline text-sm">
            ← Back to Lab Results
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-2">{result.test_name}</h1>
          <p className="text-sm text-gray-500 mt-1">Order #{result.order_number}</p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Banner */}
        <div className={`mb-6 p-4 rounded-lg ${
          result.status === "completed" ? "bg-green-50 border border-green-200" :
          result.status === "pending" || result.status === "processing" ? "bg-yellow-50 border border-yellow-200" :
          "bg-gray-50 border border-gray-200"
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium capitalize">{result.status}</p>
              <p className="text-sm text-gray-600 mt-1">
                {result.status === "completed" ? "Results are available for viewing" :
                 result.status === "pending" ? "Results are pending" :
                 "Results are being processed"}
              </p>
            </div>
            {result.priority === "stat" && (
              <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
                STAT
              </span>
            )}
          </div>
        </div>

        {/* Test Information */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Test Information</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Test Code</p>
              <p className="font-medium">{result.test_code}</p>
            </div>
            {result.loinc_code && (
              <div>
                <p className="text-gray-500">LOINC Code</p>
                <p className="font-medium">{result.loinc_code}</p>
              </div>
            )}
            <div>
              <p className="text-gray-500">Specimen Type</p>
              <p className="font-medium capitalize">{result.specimen_type || "N/A"}</p>
            </div>
            <div>
              <p className="text-gray-500">Ordered By</p>
              <p className="font-medium">{result.ordered_by_name}</p>
            </div>
            <div>
              <p className="text-gray-500">Ordered At</p>
              <p className="font-medium">{formatDate(result.ordered_at)}</p>
            </div>
            {result.specimen_collected_at && (
              <div>
                <p className="text-gray-500">Specimen Collected</p>
                <p className="font-medium">{formatDate(result.specimen_collected_at)}</p>
              </div>
            )}
            {result.completed_at && (
              <div>
                <p className="text-gray-500">Completed At</p>
                <p className="font-medium">{formatDate(result.completed_at)}</p>
              </div>
            )}
          </div>
          {result.clinical_indication && (
            <div className="mt-4">
              <p className="text-gray-500 text-sm">Clinical Indication</p>
              <p className="text-gray-900">{result.clinical_indication}</p>
            </div>
          )}
        </div>

        {/* Results */}
        {result.results.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Results</h2>
            <div className="space-y-3">
              {result.results.map((item, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-2 ${
                    item.is_critical ? "border-red-300 bg-red-50" :
                    item.is_abnormal ? "border-yellow-300 bg-yellow-50" :
                    "border-gray-200 bg-gray-50"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{item.test_name}</p>
                      <div className="flex items-center gap-4 mt-1">
                        <span className={`text-2xl font-bold ${getResultColor(item)}`}>
                          {item.result_value}
                        </span>
                        {item.unit && (
                          <span className="text-gray-600">{item.unit}</span>
                        )}
                      </div>
                      {item.reference_range && (
                        <p className="text-sm text-gray-600 mt-1">
                          Reference: {item.reference_range}
                        </p>
                      )}
                    </div>
                    {(item.is_abnormal || item.is_critical) && (
                      <div className="ml-4 flex flex-col items-end gap-1">
                        {item.is_critical && (
                          <span className="px-2 py-1 bg-red-600 text-white text-xs rounded">
                            Critical
                          </span>
                        )}
                        {item.abnormal_flag && !item.is_critical && (
                          <span className="px-2 py-1 bg-yellow-600 text-white text-xs rounded">
                            {item.abnormal_flag}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Interpretation */}
        {result.results_interpretation && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Interpretation</h2>
            <p className="text-gray-700">{result.results_interpretation}</p>
          </div>
        )}

        {/* Patient-Friendly Explanation */}
        {(result.test_description || result.what_it_measures || result.what_results_mean) && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Understanding Your Results</h2>
            {result.test_description && (
              <div className="mb-3">
                <p className="font-medium text-gray-700">What This Test Measures</p>
                <p className="text-gray-700 text-sm mt-1">{result.what_it_measures}</p>
              </div>
            )}
            {result.what_results_mean && (
              <div>
                <p className="font-medium text-gray-700">What The Results Mean</p>
                <p className="text-gray-700 text-sm mt-1">{result.what_results_mean}</p>
              </div>
            )}
          </div>
        )}

        {/* Disclaimer */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            <strong>Disclaimer:</strong> These results are for informational purposes only.
            Please consult with your healthcare provider for proper interpretation and medical advice.
            Abnormal results may require follow-up testing or evaluation.
          </p>
        </div>
      </main>
    </div>
  );
}
