"use client";

/**
 * BPJS SEP Generator Component for STORY-019
 *
 * Provides BPJS SEP (Surat Eligibilitas Peserta) generation with:
 * - Auto-population from consultation data
 * - Validation before submission
 * - Automatic SEP creation in <10 seconds
 * - SEP updates and cancellation
 * - SEP history tracking
 */

import { useState, useEffect } from "react";
import {
  FileText,
  CheckCircle,
  AlertTriangle,
  Clock,
  User,
  RefreshCw,
  X,
  Info,
} from "lucide-react";

// Types
interface SEPAutoPopulateData {
  encounter_id: number;
  patient_id: number;
  patient_name: string;
  bpjs_card_number: string;
  sep_date: string;
  service_type: string;
  ppk_code: string;
  department: string;
  doctor_code?: string;
  doctor_name?: string;
  chief_complaint?: string;
  initial_diagnosis_code?: string;
  initial_diagnosis_name?: string;
  mrn?: string;
  patient_phone?: string;
}

interface SEPValidationResponse {
  is_valid: boolean;
  message: string;
  errors: string[];
  warnings: string[];
}

interface SEPAutoPopulateResponse {
  sep_data: SEPAutoPopulateData;
  validation: SEPValidationResponse;
  can_create: boolean;
  missing_fields: string[];
}

interface SEPInfo {
  sep_id: number;
  sep_number: string | null;
  patient_name: string;
  bpjs_card_number: string;
  sep_date: string;
  service_type: string;
  initial_diagnosis: string;
  status: string;
  created_at: string;
}

interface SEPGeneratorProps {
  encounterId: number;
  patientId: number;
  onSEPCreated?: (sepInfo: SEPInfo) => void;
}

export function SEPGenerator({ encounterId, patientId, onSEPCreated }: SEPGeneratorProps) {
  const [autoPopulateData, setAutoPopulateData] = useState<SEPAutoPopulateData | null>(null);
  const [validation, setValidation] = useState<SEPValidationResponse | null>(null);
  const [canCreate, setCanCreate] = useState(false);
  const [missingFields, setMissingFields] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sepCreated, setSepCreated] = useState<SEPInfo | null>(null);

  // Override fields
  const [polyclinicCode, setPolyclinicCode] = useState("");
  const [treatmentClass, setTreatmentClass] = useState("");
  const [notes, setNotes] = useState("");

  // Load auto-populate data on mount
  useEffect(() => {
    loadAutoPopulateData();
  }, [encounterId]);

  const loadAutoPopulateData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/sep/auto-populate/${encounterId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (response.ok) {
        const data: SEPAutoPopulateResponse = await response.json();
        setAutoPopulateData(data.sep_data);
        setValidation(data.validation);
        setCanCreate(data.can_create);
        setMissingFields(data.missing_fields);

        // Set override fields
        if (data.sep_data.polyclinic_code) {
          setPolyclinicCode(data.sep_data.polyclinic_code);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Gagal memuat data SEP");
      }
    } catch (error) {
      console.error("Failed to load auto-populate data:", error);
      setError("Gagal terhubung ke server");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateSEP = async () => {
    if (!autoPopulateData) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch("/api/v1/sep", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          encounter_id: encounterId,
          patient_id: patientId,
          bpjs_card_number: autoPopulateData.bpjs_card_number,
          sep_date: autoPopulateData.sep_date,
          service_type: autoPopulateData.service_type,
          ppk_code: autoPopulateData.ppk_code,
          initial_diagnosis_code: autoPopulateData.initial_diagnosis_code || "",
          initial_diagnosis_name: autoPopulateData.initial_diagnosis_name || "",
          polyclinic_code: polyclinicCode || undefined,
          treatment_class: treatmentClass || undefined,
          doctor_code: autoPopulateData.doctor_code,
          doctor_name: autoPopulateData.doctor_name,
          mrn: autoPopulateData.mrn,
          patient_phone: autoPopulateData.patient_phone,
          notes: notes,
          user: localStorage.getItem("user_email") || "doctor",
        }),
      });

      if (response.ok) {
        const sepInfo: SEPInfo = await response.json();
        setSepCreated(sepInfo);
        onSEPCreated?.(sepInfo);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Gagal membuat SEP");
      }
    } catch (error) {
      console.error("Failed to create SEP:", error);
      setError("Gagal terhubung ke server");
    } finally {
      setIsSubmitting(false);
    }
  };

  const getServiceTypeLabel = (serviceType: string) => {
    return serviceType === "RI" ? "Rawat Inap" : "Rawat Jalan";
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case "submitted":
      case "approved":
        return "bg-green-100 text-green-800";
      case "draft":
        return "bg-gray-100 text-gray-800";
      case "error":
        return "bg-red-100 text-red-800";
      default:
        return "bg-blue-100 text-blue-800";
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      draft: "Draft",
      submitted: "Terkirim",
      approved: "Disetujui",
      updated: "Diperbarui",
      cancelled: "Dibatalkan",
      error: "Error",
    };
    return labels[status] || status;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error && !autoPopulateData) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-start">
          <AlertTriangle className="h-6 w-6 text-red-600 mr-3 mt-1" />
          <div>
            <h3 className="text-lg font-medium text-red-800">Gagal Memuat Data</h3>
            <p className="text-red-700 mt-1">{error}</p>
            <button
              onClick={loadAutoPopulateData}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Coba Lagi
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (sepCreated) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="flex items-start">
          <CheckCircle className="h-8 w-8 text-green-600 mr-4 mt-1" />
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-green-900">SEP Berhasil Dibuat!</h3>

            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-green-700">Nomor SEP</label>
                <p className="text-lg font-bold text-green-900">{sepCreated.sep_number || "-"}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-green-700">Tanggal SEP</label>
                <p className="text-green-900">{new Date(sepCreated.sep_date).toLocaleDateString('id-ID')}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-green-700">Nama Pasien</label>
                <p className="text-green-900">{sepCreated.patient_name}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-green-700">Diagnosis Awal</label>
                <p className="text-green-900">{sepCreated.initial_diagnosis}</p>
              </div>
            </div>

            <div className="mt-4 flex items-center justify-between">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeClass(sepCreated.status)}`}>
                {getStatusLabel(sepCreated.status)}
              </span>

              <button
                onClick={() => setSepCreated(null)}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Buat SEP Baru
              </button>
            </div>
          </div>
        </div>
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
            BPJS SEP Generator
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Surat Eligibilitas Peserta akan dibuat otomatis dari data konsultasi
          </p>
        </div>
      </div>

      {autoPopulateData && (
        <>
          {/* Validation Status */}
          {validation && (
            <div
              className={`border-l-4 p-4 rounded-md ${
                validation.is_valid
                  ? "bg-green-50 border-green-400"
                  : "bg-yellow-50 border-yellow-400"
              }`}
            >
              <div className="flex">
                {validation.is_valid ? (
                  <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-yellow-400 mr-2" />
                )}
                <div className="flex-1">
                  <h3
                    className={`text-sm font-medium ${
                      validation.is_valid ? "text-green-800" : "text-yellow-800"
                    }`}
                  >
                    {validation.is_valid ? "Data Valid" : "Validasi Diperlukan"}
                  </h3>
                  {validation.errors.length > 0 && (
                    <ul className="mt-2 text-sm text-yellow-700 list-disc list-inside">
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

          {/* Missing Fields Alert */}
          {missingFields.length > 0 && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4">
              <div className="flex">
                <AlertTriangle className="h-5 w-5 text-red-400 mr-2" />
                <div>
                  <h3 className="text-sm font-medium text-red-800">Data Belum Lengkap</h3>
                  <p className="text-sm text-red-700 mt-1">
                    Field berikut harus diisi sebelum membuat SEP:
                  </p>
                  <ul className="mt-2 text-sm text-red-700 list-disc list-inside">
                    {missingFields.map((field, idx) => (
                      <li key={idx}>{field}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Patient Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Informasi Pasien
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-xs font-medium text-gray-500">Nama Pasien</label>
                <p className="text-sm font-medium text-gray-900">{autoPopulateData.patient_name}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500">Nomor Kartu BPJS</label>
                <p className="text-sm font-medium text-gray-900">{autoPopulateData.bpjs_card_number}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500">No. RM</label>
                <p className="text-sm font-medium text-gray-900">{autoPopulateData.mrn || "-"}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500">Jenis Pelayanan</label>
                <p className="text-sm font-medium text-gray-900">
                  {getServiceTypeLabel(autoPopulateData.service_type)}
                </p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500">Tanggal SEP</label>
                <p className="text-sm font-medium text-gray-900">
                  {new Date(autoPopulateData.sep_date).toLocaleDateString('id-ID')}
                </p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500">Diagnosis Awal</label>
                <p className="text-sm font-medium text-gray-900">
                  {autoPopulateData.initial_diagnosis_name || "-"}
                </p>
              </div>
            </div>
          </div>

          {/* Override Fields */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Override Data (Opsional)</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {autoPopulateData.service_type === "RJ" && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Kode Poli
                  </label>
                  <input
                    type="text"
                    value={polyclinicCode}
                    onChange={(e) => setPolyclinicCode(e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="Contoh: INT"
                  />
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Kelas Rawat
                </label>
                <select
                  value={treatmentClass}
                  onChange={(e) => setTreatmentClass(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="">Pilih Kelas</option>
                  <option value="3">Kelas 3</option>
                  <option value="2">Kelas 2</option>
                  <option value="1">Kelas 1</option>
                  <option value="VVIP">VVIP</option>
                  <option value="VIP">VIP</option>
                </select>
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Catatan
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                maxLength={200}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Catatan tambahan..."
              />
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start">
              <Info className="h-5 w-5 text-blue-600 mr-3 mt-0.5" />
              <div className="text-sm text-blue-800">
                <p className="font-medium">Informasi</p>
                <ul className="mt-2 space-y-1">
                  <li>• Data akan diambil dari konsultasi yang sedang berlangsung</li>
                  <li>• SEP akan dikirim ke API BPJS VClaim untuk pembuatan otomatis</li>
                  <li>• Nomor SEP akan diterbitkan setelah validasi berhasil</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              onClick={loadAutoPopulateData}
              disabled={isLoading}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-300"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh Data
            </button>
            <button
              onClick={handleCreateSEP}
              disabled={isSubmitting || !canCreate || isLoading}
              className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Memproses...
                </>
              ) : (
                <>
                  <CheckCircle className="h-5 w-5 mr-2" />
                  Buat SEP
                </>
              )}
            </button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start">
                <AlertTriangle className="h-5 w-5 text-red-400 mr-2" />
                <div className="text-sm text-red-800">
                  <p className="font-medium">Error</p>
                  <p className="mt-1">{error}</p>
                </div>
                <button
                  onClick={() => setError(null)}
                  className="ml-auto text-red-600 hover:text-red-800"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
