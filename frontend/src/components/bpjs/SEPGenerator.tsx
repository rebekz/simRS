"use client";

/**
 * BPJS SEP Generator Component for STORY-019
 *
 * Automatic SEP (Surat Eligibilitas Peserta) generation with:
 * - Auto-populate from encounter data
 * - BPJS eligibility validation
 * - SEP creation and submission
 * - SEP update and cancellation
 * - Offline SEP creation
 * - SEP history tracking
 */

import { useState, useEffect } from "react";
import {
  FileText,
  CheckCircle,
  AlertCircle,
  Loader2,
  Clock,
  XCircle,
  Info,
  RefreshCw,
  Eye,
  Trash2,
  Download,
} from "lucide-react";

// Types
interface SEPAutoPopulateData {
  encounter_id: number;
  patient_id: number;
  patient_name: string;
  bpjs_card_number: string;
  mrn: string;
  sep_date: string;
  service_type: "RJ" | "RI"; // Rawat Jalan / Rawat Inap
  ppk_code: string;
  polyclinic_code: string;
  treatment_class: string;
  initial_diagnosis_code: string;
  initial_diagnosis_name: string;
  doctor_code: string;
  doctor_name: string;
  patient_phone: string;
  referral_number?: string;
  referral_ppk_code?: string;
  is_executive: boolean;
  cob_flag?: boolean;
  notes: string;
}

interface SEPValidation {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  bpjs_eligibility?: {
    eligible: boolean;
    message: string;
  };
}

interface SEPInfo {
  sep_id: number;
  sep_number: string;
  encounter_id: number;
  patient_id: number;
  patient_name: string;
  bpjs_card_number: string;
  sep_date: string;
  service_type: string;
  ppk_code: string;
  polyclinic_code: string;
  treatment_class: string;
  initial_diagnosis_code: string;
  initial_diagnosis_name: string;
  doctor_name: string;
  referral_number?: string;
  is_executive: boolean;
  cob_flag?: boolean;
  notes: string;
  status: "draft" | "submitted" | "updated" | "cancelled";
  created_at: string;
  updated_at: string;
}

interface SEPGeneratorProps {
  encounterId: number;
  patientId: number;
  onSEPCreated?: (sep: SEPInfo) => void;
  onCancel?: () => void;
}

export function SEPGenerator({
  encounterId,
  patientId,
  onSEPCreated,
  onCancel,
}: SEPGeneratorProps) {
  const [sepData, setSepData] = useState<SEPAutoPopulateData | null>(null);
  const [existingSEP, setExistingSEP] = useState<SEPInfo | null>(null);
  const [validation, setValidation] = useState<SEPValidation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load SEP data on mount
  useEffect(() => {
    loadSEPData();
  }, [encounterId]);

  const loadSEPData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("staff_access_token");

      // Check for existing SEP
      const sepResponse = await fetch(`/api/v1/encounter/${encounterId}/sep`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (sepResponse.ok) {
        const sep = await sepResponse.json();
        setExistingSEP(sep);
        setIsLoading(false);
        return;
      }

      // No existing SEP, load auto-populate data
      const autoPopulateResponse = await fetch(
        `/api/v1/sep/auto-populate/${encounterId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (autoPopulateResponse.ok) {
        const data = await autoPopulateResponse.json();
        setSepData(data.sep_data);
        setValidation(data.validation);
      } else {
        const errorData = await autoPopulateResponse.json();
        setError(errorData.detail || "Failed to load SEP data");
      }
    } catch (err) {
      console.error("Failed to load SEP data:", err);
      setError("Failed to load SEP data");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateSEP = async (submitToBPJS: boolean = true) => {
    if (!sepData) {
      setError("No SEP data available");
      return;
    }

    setIsCreating(true);
    setError(null);

    try {
      const token = localStorage.getItem("staff_access_token");

      const response = await fetch(`/api/v1/sep?submit_to_bpjs=${submitToBPJS}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          encounter_id: encounterId,
          patient_id: patientId,
          bpjs_card_number: sepData.bpjs_card_number,
          sep_date: sepData.sep_date,
          service_type: sepData.service_type,
          ppk_code: sepData.ppk_code,
          polyclinic_code: sepData.polyclinic_code,
          treatment_class: sepData.treatment_class || "3",
          initial_diagnosis_code: sepData.initial_diagnosis_code,
          doctor_code: sepData.doctor_code,
          doctor_name: sepData.doctor_name,
          patient_phone: sepData.patient_phone,
          referral_number: sepData.referral_number,
          referral_ppk_code: sepData.referral_ppk_code,
          is_executive: sepData.is_executive,
          cob_flag: sepData.cob_flag,
          notes: sepData.notes,
          user: "Dr. " + (sepData.doctor_name || "System"),
        }),
      });

      if (response.ok) {
        const createdSEP = await response.json();
        setExistingSEP(createdSEP);
        onSEPCreated?.(createdSEP);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to create SEP");
      }
    } catch (err) {
      console.error("Failed to create SEP:", err);
      setError("Failed to create SEP");
    } finally {
      setIsCreating(false);
    }
  };

  const handleUpdateSEP = async () => {
    if (!existingSEP) return;

    setIsUpdating(true);
    setError(null);

    try {
      const token = localStorage.getItem("staff_access_token");

      const response = await fetch(`/api/v1/sep?submit_to_bpjs=true`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sep_id: existingSEP.sep_id,
          treatment_class: existingSEP.treatment_class,
          polyclinic_code: existingSEP.polyclinic_code,
          doctor_code: existingSEP.doctor_name?.split(" ")[0] || "",
          doctor_name: existingSEP.doctor_name,
          notes: existingSEP.notes,
          user: "Dr. System",
        }),
      });

      if (response.ok) {
        const updatedSEP = await response.json();
        setExistingSEP(updatedSEP);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to update SEP");
      }
    } catch (err) {
      console.error("Failed to update SEP:", err);
      setError("Failed to update SEP");
    } finally {
      setIsUpdating(false);
    }
  };

  const handleCancelSEP = async () => {
    if (!existingSEP || !confirm("Are you sure you want to cancel this SEP?")) {
      return;
    }

    setIsCancelling(true);
    setError(null);

    try {
      const token = localStorage.getItem("staff_access_token");

      const response = await fetch(`/api/v1/sep`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sep_id: existingSEP.sep_id,
          sep_number: existingSEP.sep_number,
          user: "Dr. System",
          reason: "Cancelled by user",
        }),
      });

      if (response.ok) {
        setExistingSEP(null);
        // Reload SEP data
        loadSEPData();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to cancel SEP");
      }
    } catch (err) {
      console.error("Failed to cancel SEP:", err);
      setError("Failed to cancel SEP");
    } finally {
      setIsCancelling(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "submitted":
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            <CheckCircle className="h-4 w-4 mr-1" />
            Submitted
          </span>
        );
      case "updated":
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
            <RefreshCw className="h-4 w-4 mr-1" />
            Updated
          </span>
        );
      case "cancelled":
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
            <XCircle className="h-4 w-4 mr-1" />
            Cancelled
          </span>
        );
      case "draft":
      default:
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
            <Clock className="h-4 w-4 mr-1" />
            Draft
          </span>
        );
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Loading SEP data...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <FileText className="h-6 w-6 mr-2" />
            BPJS SEP Generation
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Encounter ID: {encounterId} • Patient ID: {patientId}
          </p>
        </div>
        <div className="flex items-center space-x-3">
          {existingSEP && (
            <>
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium flex items-center"
              >
                <Eye className="h-4 w-4 mr-2" />
                {showHistory ? "Hide History" : "Show History"}
              </button>
              <button
                onClick={handleUpdateSEP}
                disabled={isUpdating || existingSEP.status === "cancelled"}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium flex items-center"
              >
                {isUpdating ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4 mr-2" />
                )}
                Update SEP
              </button>
              <button
                onClick={handleCancelSEP}
                disabled={isCancelling || existingSEP.status === "cancelled"}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium flex items-center"
              >
                {isCancelling ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4 mr-2" />
                )}
                Cancel SEP
              </button>
            </>
          )}
          <button
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium"
          >
            Close
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Existing SEP Display */}
      {existingSEP && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">SEP Information</h3>
                <p className="text-sm text-gray-600 mt-1">
                  SEP Number: <span className="font-mono font-medium text-blue-600">{existingSEP.sep_number}</span>
                </p>
              </div>
              {getStatusBadge(existingSEP.status)}
            </div>
          </div>

          <div className="p-6">
            <div className="grid grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-500">Patient</label>
                <p className="mt-1 text-sm text-gray-900">{existingSEP.patient_name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">BPJS Card Number</label>
                <p className="mt-1 text-sm text-gray-900 font-mono">{existingSEP.bpjs_card_number}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">SEP Date</label>
                <p className="mt-1 text-sm text-gray-900">
                  {new Date(existingSEP.sep_date).toLocaleDateString("id-ID")}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Service Type</label>
                <p className="mt-1 text-sm text-gray-900">
                  {existingSEP.service_type === "RJ" ? "Rawat Jalan" : "Rawat Inap"}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Polyclinic</label>
                <p className="mt-1 text-sm text-gray-900">{existingSEP.polyclinic_code}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Treatment Class</label>
                <p className="mt-1 text-sm text-gray-900">Kelas {existingSEP.treatment_class}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Initial Diagnosis</label>
                <p className="mt-1 text-sm text-gray-900">{existingSEP.initial_diagnosis_name}</p>
                <p className="text-xs text-gray-500 font-mono">{existingSEP.initial_diagnosis_code}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Doctor</label>
                <p className="mt-1 text-sm text-gray-900">{existingSEP.doctor_name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Executive</label>
                <p className="mt-1 text-sm text-gray-900">
                  {existingSEP.is_executive ? "Yes" : "No"}
                </p>
              </div>
            </div>

            {existingSEP.notes && (
              <div className="mt-6">
                <label className="block text-sm font-medium text-gray-500">Notes</label>
                <p className="mt-1 text-sm text-gray-900">{existingSEP.notes}</p>
              </div>
            )}
          </div>

          {/* SEP Actions */}
          <div className="bg-gray-50 px-6 py-4 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Created: {new Date(existingSEP.created_at).toLocaleString("id-ID")}
            </div>
            <button
              onClick={() => window.print()}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm font-medium flex items-center"
            >
              <Download className="h-4 w-4 mr-2" />
              Print SEP
            </button>
          </div>
        </div>
      )}

      {/* SEP Creation Form */}
      {!existingSEP && sepData && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Create New SEP</h3>
            <p className="text-sm text-gray-600 mt-1">
              Auto-populated from encounter data
            </p>
          </div>

          <div className="p-6">
            {/* Validation Status */}
            {validation && (
              <div className={`mb-6 p-4 rounded-lg ${
                validation.is_valid
                  ? "bg-green-50 border border-green-200"
                  : "bg-yellow-50 border border-yellow-200"
              }`}>
                <div className="flex items-start">
                  {validation.is_valid ? (
                    <CheckCircle className="h-5 w-5 text-green-600 mr-2 flex-shrink-0 mt-0.5" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-yellow-600 mr-2 flex-shrink-0 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-gray-900">
                      {validation.is_valid ? "SEP Data Valid" : "SEP Data Validation"}
                    </h4>
                    {validation.errors.length > 0 && (
                      <ul className="mt-2 text-sm text-red-700 list-disc list-inside">
                        {validation.errors.map((error, idx) => (
                          <li key={idx}>{error}</li>
                        ))}
                      </ul>
                    )}
                    {validation.warnings.length > 0 && (
                      <ul className="mt-2 text-sm text-yellow-700 list-disc list-inside">
                        {validation.warnings.map((warning, idx) => (
                          <li key={idx}>{warning}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* SEP Data Display */}
            <div className="grid grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-500">Patient</label>
                <p className="mt-1 text-sm text-gray-900">{sepData.patient_name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">BPJS Card Number</label>
                <p className="mt-1 text-sm text-gray-900 font-mono">{sepData.bpjs_card_number}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Medical Record</label>
                <p className="mt-1 text-sm text-gray-900 font-mono">{sepData.mrn}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">SEP Date</label>
                <p className="mt-1 text-sm text-gray-900">
                  {new Date(sepData.sep_date).toLocaleDateString("id-ID")}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Service Type</label>
                <p className="mt-1 text-sm text-gray-900">
                  {sepData.service_type === "RJ" ? "Rawat Jalan" : "Rawat Inap"}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Facility Code (PPK)</label>
                <p className="mt-1 text-sm text-gray-900 font-mono">{sepData.ppk_code}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Polyclinic Code</label>
                <p className="mt-1 text-sm text-gray-900">{sepData.polyclinic_code}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Treatment Class</label>
                <p className="mt-1 text-sm text-gray-900">Kelas {sepData.treatment_class}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Doctor</label>
                <p className="mt-1 text-sm text-gray-900">{sepData.doctor_name}</p>
                <p className="text-xs text-gray-500 font-mono">{sepData.doctor_code}</p>
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-500">Initial Diagnosis</label>
                <p className="mt-1 text-sm text-gray-900">{sepData.initial_diagnosis_name}</p>
                <p className="text-xs text-gray-500 font-mono">{sepData.initial_diagnosis_code}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Patient Phone</label>
                <p className="mt-1 text-sm text-gray-900">{sepData.patient_phone || "-"}</p>
              </div>
            </div>

            {sepData.referral_number && (
              <div className="mt-6 grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-500">Referral Number</label>
                  <p className="mt-1 text-sm text-gray-900 font-mono">{sepData.referral_number}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">Referral PPK</label>
                  <p className="mt-1 text-sm text-gray-900 font-mono">{sepData.referral_ppk_code}</p>
                </div>
              </div>
            )}

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-start">
              <Info className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
              <div className="flex-1 text-sm text-blue-800">
                <p className="font-medium">SEP will be submitted to BPJS API</p>
                <p className="mt-1">
                  The SEP will be created and submitted to BPJS VClaim API. Make sure all information is correct before submitting.
                </p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="bg-gray-50 px-6 py-4 flex items-center justify-end space-x-3">
            <button
              onClick={() => handleCreateSEP(false)}
              disabled={isCreating || !validation?.is_valid}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
            >
              {isCreating ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
              Save as Draft
            </button>
            <button
              onClick={() => handleCreateSEP(true)}
              disabled={isCreating || !validation?.is_valid}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium flex items-center"
            >
              {isCreating ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Create & Submit SEP
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* SEP History */}
      {showHistory && existingSEP && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">SEP History</h3>
          </div>
          <div className="p-6">
            <p className="text-sm text-gray-500">SEP history tracking will be displayed here.</p>
          </div>
        </div>
      )}
    </div>
  );
}
