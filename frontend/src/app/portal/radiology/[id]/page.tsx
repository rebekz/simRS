"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";

interface RadiologyResultDetail {
  id: number;
  order_number: string;
  accession_number: string | null;
  procedure_code: string;
  procedure_name: string;
  modality: string;
  body_part: string | null;
  view_position: string | null;
  status: string;
  priority: string;
  clinical_indication: string | null;
  clinical_history: string | null;
  contrast_required: boolean;
  contrast_type: string | null;
  radiation_dose_msv: number | null;
  preliminary_report: string | null;
  preliminary_report_at: string | null;
  final_report: string | null;
  final_report_at: string | null;
  findings: string | null;
  impression: string | null;
  critical_findings: boolean;
  critical_findings_notified: boolean;
  image_count: number | null;
  series_count: number | null;
  ordered_at: string;
  scheduled_at: string | null;
  procedure_completed_at: string | null;
  ordered_by_name: string;
  radiologist_name: string | null;
}

export default function RadiologyResultDetailPage() {
  const router = useRouter();
  const params = useParams();
  const radiologyOrderId = parseInt(params.id as string);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RadiologyResultDetail | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);

  useEffect(() => {
    checkAuth();
    fetchRadiologyResultDetail();
  }, [radiologyOrderId]);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchRadiologyResultDetail = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/portal/radiology-results/${radiologyOrderId}`, {
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
          setError("Radiology result not found");
          setLoading(false);
          return;
        }
        throw new Error("Failed to fetch radiology result details");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load radiology result");
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading radiology result...</p>
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
          <p className="text-gray-500 mb-4">{error || "Radiology result not found"}</p>
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
          <a href="/portal/radiology" className="text-indigo-600 hover:underline text-sm">
            ← Back to Radiology Results
          </a>
          <div className="flex items-center gap-3 mt-2">
            <span className="text-4xl">{getModalityIcon(result.modality)}</span>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{result.procedure_name}</h1>
              <p className="text-sm text-gray-500">Order #{result.order_number}</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Banner */}
        <div className={`mb-6 p-4 rounded-lg ${
          result.status === "completed" ? "bg-green-50 border border-green-200" :
          result.status === "in_progress" ? "bg-blue-50 border border-blue-200" :
          result.status === "scheduled" ? "bg-yellow-50 border border-yellow-200" :
          "bg-gray-50 border border-gray-200"
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium capitalize">{result.status.replace("_", " ")}</p>
              <p className="text-sm text-gray-600 mt-1">
                {result.status === "completed" ? "Report is available for viewing" :
                 result.status === "in_progress" ? "Exam is being performed" :
                 result.status === "scheduled" ? "Exam is scheduled" :
                 "Status pending"}
              </p>
            </div>
            {result.priority === "stat" && (
              <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
                STAT
              </span>
            )}
          </div>
        </div>

        {/* Critical Finding Alert */}
        {result.critical_findings && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-3">
              <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="font-medium text-red-800">Critical Finding Detected</p>
                <p className="text-sm text-red-700">Please contact your healthcare provider to discuss these results.</p>
              </div>
            </div>
          </div>
        )}

        {/* Exam Information */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Exam Information</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Procedure Code</p>
              <p className="font-medium">{result.procedure_code}</p>
            </div>
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
            {result.view_position && (
              <div>
                <p className="text-gray-500">View/Position</p>
                <p className="font-medium">{result.view_position}</p>
              </div>
            )}
            <div>
              <p className="text-gray-500">Ordered By</p>
              <p className="font-medium">{result.ordered_by_name}</p>
            </div>
            {result.radiologist_name && (
              <div>
                <p className="text-gray-500">Radiologist</p>
                <p className="font-medium">{result.radiologist_name}</p>
              </div>
            )}
            <div>
              <p className="text-gray-500">Ordered At</p>
              <p className="font-medium">{formatDate(result.ordered_at)}</p>
            </div>
            {result.scheduled_at && (
              <div>
                <p className="text-gray-500">Scheduled For</p>
                <p className="font-medium">{formatDate(result.scheduled_at)}</p>
              </div>
            )}
            {result.procedure_completed_at && (
              <div>
                <p className="text-gray-500">Completed At</p>
                <p className="font-medium">{formatDate(result.procedure_completed_at)}</p>
              </div>
            )}
          </div>
          {(result.clinical_indication || result.clinical_history) && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              {result.clinical_indication && (
                <div className="mb-3">
                  <p className="text-gray-500 text-sm">Clinical Indication</p>
                  <p className="text-gray-900">{result.clinical_indication}</p>
                </div>
              )}
              {result.clinical_history && (
                <div>
                  <p className="text-gray-500 text-sm">Clinical History</p>
                  <p className="text-gray-900">{result.clinical_history}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Imaging Study Info */}
        {(result.image_count || result.series_count || result.contrast_required || result.radiation_dose_msv) && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Imaging Study Details</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              {result.series_count && (
                <div>
                  <p className="text-gray-500">Series Count</p>
                  <p className="font-medium">{result.series_count}</p>
                </div>
              )}
              {result.image_count && (
                <div>
                  <p className="text-gray-500">Image Count</p>
                  <p className="font-medium">{result.image_count}</p>
                </div>
              )}
              <div>
                <p className="text-gray-500">Contrast Used</p>
                <p className="font-medium">{result.contrast_required ? `Yes (${result.contrast_type || "N/A"})` : "No"}</p>
              </div>
              {result.radiation_dose_msv && (
                <div>
                  <p className="text-gray-500">Radiation Dose</p>
                  <p className="font-medium">{result.radiation_dose_msv} mSv</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Reports */}
        {(result.preliminary_report || result.final_report) && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Radiology Report</h2>

            {result.final_report && (
              <>
                <div className="mb-4 pb-4 border-b border-gray-200">
                  <div className="flex items-center gap-2 mb-3">
                    <h3 className="font-medium text-gray-900">Final Report</h3>
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">Final</span>
                  </div>
                  {result.final_report_at && (
                    <p className="text-xs text-gray-500 mb-2">Signed: {formatDate(result.final_report_at)}</p>
                  )}
                  {result.radiologist_name && (
                    <p className="text-xs text-gray-500 mb-3">Radiologist: {result.radiologist_name}</p>
                  )}
                  {result.findings && (
                    <div className="mb-3">
                      <p className="text-sm font-medium text-gray-700 mb-1">Findings:</p>
                      <p className="text-sm text-gray-900 whitespace-pre-wrap">{result.findings}</p>
                    </div>
                  )}
                  {result.impression && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Impression:</p>
                      <p className="text-sm text-gray-900 whitespace-pre-wrap">{result.impression}</p>
                    </div>
                  )}
                </div>
              </>
            )}

            {result.preliminary_report && !result.final_report && (
              <>
                <div className="mb-4 pb-4 border-b border-gray-200">
                  <div className="flex items-center gap-2 mb-3">
                    <h3 className="font-medium text-gray-900">Preliminary Report</h3>
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded">Preliminary</span>
                  </div>
                  {result.preliminary_report_at && (
                    <p className="text-xs text-gray-500 mb-2">{formatDate(result.preliminary_report_at)}</p>
                  )}
                  <p className="text-sm text-gray-900 whitespace-pre-wrap">{result.preliminary_report}</p>
                </div>
              </>
            )}
          </div>
        )}

        {/* Disclaimer */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            <strong>Disclaimer:</strong> These results are for informational purposes only.
            Please consult with your healthcare provider for proper interpretation and medical advice.
          </p>
        </div>
      </main>
    </div>
  );
}
