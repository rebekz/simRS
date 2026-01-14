"use client";

/**
 * Allergy List Component for STORY-013
 *
 * Displays and manages patient allergies with:
 * - Type and severity filtering
 * - Add/Edit/Delete functionality
 * - NKA (No Known Allergies) option
 * - Source documentation tracking
 */

import { useState, useEffect } from "react";
import {
  Plus,
  Edit2,
  Trash2,
  Shield,
  AlertCircle,
  Apple,
  Pill,
  Leaf,
  CheckCircle,
  XCircle,
} from "lucide-react";

// Types
interface Allergy {
  id: number;
  patient_id: number;
  allergy_type: "drug" | "food" | "environmental" | "other";
  allergen: string;
  allergen_code?: string;
  severity: "mild" | "moderate" | "severe" | "life_threatening";
  reaction: string;
  status: "active" | "resolved" | "unconfirmed";
  onset_date?: string;
  source: "patient_reported" | "tested" | "observed" | "inferred";
  clinical_notes?: string;
  alternatives?: string[];
  recorded_by_name?: string;
  created_at: string;
}

interface AllergySummary {
  has_allergies: boolean;
  no_known_allergies: boolean;
  total_allergies: number;
  active_allergies: number;
  severe_allergies: number;
  drug_allergies: number;
  food_allergies: number;
  environmental_allergies: number;
}

interface AllergyListProps {
  patientId: number;
}

export function AllergyList({ patientId }: AllergyListProps) {
  const [allergies, setAllergies] = useState<Allergy[]>([]);
  const [summary, setSummary] = useState<AllergySummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("active");
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [showNkaModal, setShowNkaModal] = useState(false);

  useEffect(() => {
    fetchAllergies();
  }, [patientId, statusFilter, typeFilter]);

  const fetchAllergies = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.append("status_filter", statusFilter);
      if (typeFilter) params.append("type_filter", typeFilter);

      const response = await fetch(
        `/api/v1/allergies/patient/${patientId}?${params}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAllergies(data.allergies);
        setSummary({
          has_allergies: data.has_allergies,
          no_known_allergies: data.no_known_allergies,
          total_allergies: data.total_allergies,
          active_allergies: data.active_allergies,
          severe_allergies: data.severe_allergies,
          drug_allergies: data.drug_allergies,
          food_allergies: data.food_allergies,
          environmental_allergies: data.environmental_allergies,
        });
      }
    } catch (error) {
      console.error("Failed to fetch allergies:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "drug":
        return <Pill className="h-4 w-4" />;
      case "food":
        return <Apple className="h-4 w-4" />;
      case "environmental":
        return <Leaf className="h-4 w-4" />;
      default:
        return <Shield className="h-4 w-4" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "life_threatening":
        return "bg-red-100 text-red-800 border-red-300";
      case "severe":
        return "bg-orange-100 text-orange-800 border-orange-300";
      case "moderate":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "mild":
        return "bg-green-100 text-green-800 border-green-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800";
      case "resolved":
        return "bg-gray-100 text-gray-800";
      case "unconfirmed":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const handleDeleteAllergy = async (allergyId: number) => {
    if (!confirm("Apakah Anda yakin ingin menghapus alergi ini?")) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/allergies/${allergyId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (response.ok) {
        fetchAllergies();
      }
    } catch (error) {
      console.error("Failed to delete allergy:", error);
    }
  };

  const handleRecordNKA = async () => {
    try {
      const response = await fetch("/api/v1/allergies/nka", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          patient_id: patientId,
          recorded_by: 1, // Would get from auth context
        }),
      });

      if (response.ok) {
        alert("NKA (No Known Allergies) berhasil dicatat");
        setShowNkaModal(false);
        fetchAllergies();
      }
    } catch (error) {
      console.error("Failed to record NKA:", error);
    }
  };

  if (isLoading) {
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
          <h2 className="text-2xl font-bold text-gray-900">Daftar Alergi</h2>
          <p className="text-sm text-gray-600 mt-1">Pasien ID: {patientId}</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowNkaModal(true)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            NKA (Tidak Ada Alergi)
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Tambah Alergi
          </button>
        </div>
      </div>

      {/* Statistics */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">Total Alergi</dt>
              <dd className="mt-1 text-3xl font-semibold text-gray-900">
                {summary.total_allergies}
              </dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">Aktif</dt>
              <dd className="mt-1 text-3xl font-semibold text-green-600">
                {summary.active_allergies}
              </dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">Parah/Sangat</dt>
              <dd className="mt-1 text-3xl font-semibold text-orange-600">
                {summary.severe_allergies}
              </dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">Obat</dt>
              <dd className="mt-1 text-3xl font-semibold text-blue-600">
                {summary.drug_allergies}
              </dd>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4">
        <span className="text-sm font-medium text-gray-700">Status:</span>
        <div className="flex space-x-2">
          <button
            onClick={() => setStatusFilter("active")}
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              statusFilter === "active"
                ? "bg-green-100 text-green-800"
                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
            }`}
          >
            Aktif
          </button>
          <button
            onClick={() => setStatusFilter("resolved")}
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              statusFilter === "resolved"
                ? "bg-gray-200 text-gray-800"
                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
            }`}
          >
            Sembuh
          </button>
          <button
            onClick={() => setStatusFilter("")}
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              statusFilter === ""
                ? "bg-blue-100 text-blue-800"
                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
            }`}
          >
            Semua
          </button>
        </div>

        <span className="text-sm font-medium text-gray-700 ml-4">Tipe:</span>
        <div className="flex space-x-2">
          <button
            onClick={() => setTypeFilter("drug")}
            className={`px-3 py-1 rounded-full text-sm font-medium flex items-center ${
              typeFilter === "drug"
                ? "bg-blue-100 text-blue-800"
                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
            }`}
          >
            <Pill className="h-3 w-3 mr-1" />
            Obat
          </button>
          <button
            onClick={() => setTypeFilter("food")}
            className={`px-3 py-1 rounded-full text-sm font-medium flex items-center ${
              typeFilter === "food"
                ? "bg-green-100 text-green-800"
                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
            }`}
          >
            <Apple className="h-3 w-3 mr-1" />
            Makanan
          </button>
          <button
            onClick={() => setTypeFilter("environmental")}
            className={`px-3 py-1 rounded-full text-sm font-medium flex items-center ${
              typeFilter === "environmental"
                ? "bg-purple-100 text-purple-800"
                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
            }`}
          >
            <Leaf className="h-3 w-3 mr-1" />
            Lingkungan
          </button>
          <button
            onClick={() => setTypeFilter("")}
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              typeFilter === ""
                ? "bg-blue-100 text-blue-800"
                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
            }`}
          >
            Semua
          </button>
        </div>
      </div>

      {/* Allergy List */}
      {allergies.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <Shield className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Tidak ada alergi</h3>
          <p className="mt-1 text-sm text-gray-500">
            {statusFilter === "active"
              ? "Tidak ada alergi aktif untuk pasien ini."
              : "Tidak ada alergi ditemukan."}
          </p>
          <button
            onClick={() => setShowNkaModal(true)}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100"
          >
            Catat NKA (Tidak Ada Alergi)
          </button>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {allergies.map((allergy) => (
              <li key={allergy.id}>
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      {/* Allergen and Type */}
                      <div className="flex items-center space-x-3">
                        {getTypeIcon(allergy.allergy_type)}
                        <h3 className="text-lg font-medium text-gray-900">
                          {allergy.allergen}
                        </h3>
                        {allergy.severity === "life_threatening" && (
                          <AlertCircle className="h-5 w-5 text-red-600" />
                        )}
                      </div>

                      {/* Reaction */}
                      <p className="mt-1 text-sm text-gray-600">
                        <span className="font-medium">Reaksi:</span> {allergy.reaction}
                      </p>

                      {/* Metadata */}
                      <div className="mt-2 flex flex-wrap items-center gap-2">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getSeverityColor(
                            allergy.severity
                          )}`}
                        >
                          {allergy.severity === "life_threatening" && "⚠️ "}
                          {allergy.severity.charAt(0).toUpperCase() +
                            allergy.severity.slice(1).replace("_", " ")}
                        </span>

                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(
                            allergy.status
                          )}`}
                        >
                          {allergy.status.charAt(0).toUpperCase() + allergy.status.slice(1)}
                        </span>

                        {allergy.onset_date && (
                          <span className="inline-flex items-center text-xs text-gray-500">
                            Onset: {new Date(allergy.onset_date).toLocaleDateString()}
                          </span>
                        )}

                        <span className="inline-flex items-center text-xs text-gray-500">
                          Sumber:{" "}
                          {allergy.source === "patient_reported"
                            ? "Pasien"
                            : allergy.source === "tested"
                            ? "Teruji"
                            : allergy.source === "observed"
                            ? "Observasi"
                            : "Inferensi"}
                        </span>
                      </div>

                      {/* Clinical Notes */}
                      {allergy.clinical_notes && (
                        <p className="mt-2 text-sm text-gray-500 italic">
                          Catatan: {allergy.clinical_notes}
                        </p>
                      )}

                      {/* Alternatives */}
                      {allergy.alternatives && allergy.alternatives.length > 0 && (
                        <div className="mt-2">
                          <span className="text-xs font-medium text-gray-700">
                            Alternatif aman:
                          </span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {allergy.alternatives.map((alt, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-green-100 text-green-800"
                              >
                                {alt}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Attribution */}
                      <div className="mt-2 text-xs text-gray-500">
                        {allergy.recorded_by_name && (
                          <span>Dicatat oleh {allergy.recorded_by_name}</span>
                        )}
                        <span className="mx-2">•</span>
                        <span>
                          {new Date(allergy.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="ml-4 flex-shrink-0 flex items-center space-x-2">
                      <button
                        className="p-2 text-gray-600 hover:bg-gray-100 rounded-full"
                        title="Edit allergy"
                      >
                        <Edit2 className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleDeleteAllergy(allergy.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-full"
                        title="Delete allergy"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* NKA Confirmation Modal */}
      {showNkaModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="px-4 py-3 sm:px-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Konfirmasi NKA (Tidak Ada Alergi)
              </h3>
            </div>
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-start">
                <CheckCircle className="h-6 w-6 text-green-600 mr-3 flex-shrink-0" />
                <div>
                  <p className="text-sm text-gray-700">
                    Apakah Anda yakin pasien tidak memiliki alergi yang diketahui?
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    Ini akan dicatat bahwa pasien telah ditanya tentang alergi.
                  </p>
                </div>
              </div>
            </div>
            <div className="px-4 py-3 sm:px-6 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setShowNkaModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={handleRecordNKA}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
              >
                Ya, Konfirmasi NKA
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Allergy Modal Placeholder */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-4 py-3 sm:px-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Tambah Alergi</h3>
            </div>
            <div className="px-4 py-5 sm:p-6">
              <p className="text-sm text-gray-600">
                Form tambah alergi akan diimplementasikan di sini.
              </p>
              {/* TODO: Implement AddAllergyForm component */}
            </div>
            <div className="px-4 py-3 sm:px-6 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                Simpan
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
