/**
 * Medication List UI Component for STORY-014
 *
 * Provides comprehensive medication list management with:
 * - Current medications display
 * - Past medications history
 * - Drug interaction checking
 * - Duplicate therapy warnings
 * - Medication reconciliation
 */

import { useState, useEffect } from "react";
import {
  Pill,
  AlertTriangle,
  Clock,
  History,
  CheckCircle,
  XCircle,
  Search,
  Filter,
  Plus,
  Edit,
  Ban,
  FileText,
  RefreshCw,
  AlertCircle,
} from "lucide-react";

// Types
interface Medication {
  id: number;
  patient_id: number;
  drug_id: number;
  drug_name: string;
  generic_name: string;
  dosage?: string;
  dose_unit?: string;
  frequency?: string;
  route?: string;
  indication?: string;
  prescriber_id?: number;
  prescriber_name?: string;
  prescription_date?: string;
  start_date: string;
  end_date?: string;
  status: string;
  notes?: string;
  batch_number?: string;
  manufacturer?: string;
  discontinuation_reason?: string;
  bpjs_code?: string;
  is_narcotic: boolean;
  is_antibiotic: boolean;
  requires_prescription: boolean;
  created_at: string;
  updated_at: string;
}

interface DrugInteraction {
  id: number;
  interaction_type: string;
  severity: string;
  drug_1_id: number;
  drug_1_name: string;
  drug_2_id?: number;
  drug_2_name?: string;
  description: string;
  recommendation: string;
  requires_override: boolean;
}

interface DuplicateTherapy {
  drug_1_id: number;
  drug_1_name: string;
  drug_2_id: number;
  drug_2_name: string;
  therapeutic_class: string;
  severity: string;
  recommendation: string;
}

interface MedicationListProps {
  patientId: number;
}

export function MedicationList({ patientId }: MedicationListProps) {
  const [currentMedications, setCurrentMedications] = useState<Medication[]>([]);
  const [pastMedications, setPastMedications] = useState<Medication[]>([]);
  const [interactions, setInteractions] = useState<DrugInteraction[]>([]);
  const [duplicates, setDuplicates] = useState<DuplicateTherapy[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // UI state
  const [activeTab, setActiveTab] = useState<"current" | "history" | "reconcile">("current");
  const [showPast, setShowPast] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    loadData();
  }, [patientId, showPast]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");

      // Load medications
      const medsResponse = await fetch(`/api/v1/patients/${patientId}/medications?include_past=${showPast}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (medsResponse.ok) {
        const data = await medsResponse.json();
        setCurrentMedications(data.current_medications || []);
        setPastMedications(data.past_medications || []);

        // Check for interactions if there are current medications
        if (data.current_medications && data.current_medications.length > 1) {
          const drugIds = data.current_medications.map((m: Medication) => m.drug_id);
          await checkInteractions(drugIds);
        }
      }
    } catch (error) {
      console.error("Failed to load medications:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const checkInteractions = async (drugIds: number[]) => {
    try {
      const token = localStorage.getItem("staff_access_token");

      // Check drug-drug interactions
      const interactionResponse = await fetch("/api/v1/medications/check-interactions", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          patient_id: patientId,
          drug_ids: drugIds,
        }),
      });

      if (interactionResponse.ok) {
        const data = await interactionResponse.json();
        setInteractions(data.interactions || []);
      }

      // Check duplicate therapies
      const duplicateResponse = await fetch("/api/v1/medications/check-duplicates", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(drugIds),
      });

      if (duplicateResponse.ok) {
        const data = await duplicateResponse.json();
        setDuplicates(data || []);
      }
    } catch (error) {
      console.error("Failed to check interactions:", error);
    }
  };

  const stopMedication = async (medicationId: number, reason: string) => {
    try {
      const token = localStorage.getItem("staff_access_token");

      const response = await fetch(`/api/v1/medications/${medicationId}/stop?reason=${encodeURIComponent(reason)}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        loadData();
      } else {
        alert("Gagal menghentikan obat");
      }
    } catch (error) {
      console.error("Error stopping medication:", error);
    }
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case "contraindicated":
        return "bg-red-50 border-red-200 text-red-800";
      case "severe":
        return "bg-red-50 border-red-200 text-red-800";
      case "moderate":
        return "bg-yellow-50 border-yellow-200 text-yellow-800";
      case "mild":
        return "bg-blue-50 border-blue-200 text-blue-800";
      default:
        return "bg-gray-50 border-gray-200 text-gray-800";
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "contraindicated":
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">Kontraindikasi</span>;
      case "severe":
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">Berat</span>;
      case "moderate":
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Sedang</span>;
      case "mild":
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Ringan</span>;
      default:
        return null;
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleDateString("id-ID", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const displayMedications = activeTab === "current" ? currentMedications : pastMedications;

  if (isLoading && currentMedications.length === 0) {
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
          <h2 className="text-xl font-bold text-gray-900 flex items-center">
            <Pill className="h-5 w-5 mr-2" />
            Daftar Obat
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Riwayat obat pasien saat ini dan masa lalu
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={loadData}
            disabled={isLoading}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </button>
          <button
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Tambah Obat
          </button>
        </div>
      </div>

      {/* Interactions and Warnings */}
      {(interactions.length > 0 || duplicates.length > 0) && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2 text-yellow-600" />
            Peringatan Interaksi ({interactions.length + duplicates.length})
          </h3>

          <div className="space-y-3">
            {interactions.map((interaction, idx) => (
              <div
                key={idx}
                className={`border-l-4 p-4 rounded-md ${getSeverityClass(interaction.severity)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      {getSeverityBadge(interaction.severity)}
                      <span className="text-sm font-medium">
                        {interaction.drug_1_name}
                        {interaction.drug_2_name && ` ↔ ${interaction.drug_2_name}`}
                      </span>
                    </div>
                    <p className="text-sm mb-1">{interaction.description}</p>
                    <p className="text-xs font-medium">Rekomendasi: {interaction.recommendation}</p>
                  </div>
                </div>
              </div>
            ))}

            {duplicates.map((dup, idx) => (
              <div
                key={`dup-${idx}`}
                className="border-l-4 border-orange-500 bg-orange-50 p-4 rounded-md"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        Duplikasi Terapi
                      </span>
                      <span className="text-sm font-medium">
                        {dup.drug_1_name} ↔ {dup.drug_2_name}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">
                      Kelas terapi: {dup.therapeutic_class}
                    </p>
                    <p className="text-xs mt-1">{dup.recommendation}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab("current")}
            className={`${
              activeTab === "current"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Obat Saat Ini ({currentMedications.length})
          </button>
          <button
            onClick={() => setActiveTab("history")}
            className={`${
              activeTab === "history"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Riwayat Obat ({pastMedications.length})
          </button>
          <button
            onClick={() => setActiveTab("reconcile")}
            className={`${
              activeTab === "reconcile"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Rekonsiliasi
          </button>
        </nav>
      </div>

      {/* Current Medications Tab */}
      {activeTab === "current" && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Obat Saat Ini</h3>
            <div className="relative">
              <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Cari obat..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div className="space-y-3">
            {displayMedications
              .filter(
                (med) =>
                  !searchTerm ||
                  med.drug_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  med.generic_name.toLowerCase().includes(searchTerm.toLowerCase())
              )
              .map((med) => (
                <div key={med.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="text-sm font-medium text-gray-900">{med.drug_name}</h4>
                        {med.is_narcotic && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                            Narkotik
                          </span>
                        )}
                        {med.is_antibiotic && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                            Antibiotik
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500">{med.generic_name}</p>

                      <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-gray-500">Dosis:</span>{" "}
                          {med.dosage && med.dose_unit ? `${med.dosage} ${med.dose_unit}` : "-"}
                        </div>
                        <div>
                          <span className="text-gray-500">Frekuensi:</span> {med.frequency || "-"}
                        </div>
                        <div>
                          <span className="text-gray-500">Rute:</span> {med.route || "-"}
                        </div>
                        <div>
                          <span className="text-gray-500">Indikasi:</span> {med.indication || "-"}
                        </div>
                        <div>
                          <span className="text-gray-500">Mulai:</span> {formatDate(med.start_date)}
                        </div>
                        <div>
                          <span className="text-gray-500">Dokter:</span> {med.prescriber_name || "-"}
                        </div>
                      </div>

                      {med.notes && (
                        <div className="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded">
                          <span className="font-medium">Catatan:</span> {med.notes}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => {/* TODO: Edit */}}
                        className="text-blue-600 hover:text-blue-900"
                        title="Edit"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => {
                          const reason = prompt("Alasan penghentian obat:");
                          if (reason) stopMedication(med.id, reason);
                        }}
                        className="text-red-600 hover:text-red-900"
                        title="Hentikan"
                      >
                        <Ban className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
          </div>

          {displayMedications.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Pill className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Tidak ada obat</p>
            </div>
          )}
        </div>
      )}

      {/* History Tab */}
      {activeTab === "history" && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Riwayat Obat</h3>

          <div className="space-y-3">
            {pastMedications
              .filter(
                (med) =>
                  !searchTerm ||
                  med.drug_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  med.generic_name.toLowerCase().includes(searchTerm.toLowerCase())
              )
              .map((med) => (
                <div key={med.id} className="border rounded-lg p-4 bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="text-sm font-medium text-gray-700">{med.drug_name}</h4>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                          med.status === "stopped" ? "bg-red-100 text-red-800" : "bg-gray-100 text-gray-800"
                        }`}>
                          {med.status === "stopped" ? "Dihentikan" : "Selesai"}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500">{med.generic_name}</p>

                      <div className="mt-2 text-sm text-gray-600">
                        <p>
                          {med.dosage && med.dose_unit && `${med.dosage} ${med.dose_unit}`}
                          {med.frequency && ` - ${med.frequency}`}
                        </p>
                        <p className="text-xs mt-1">
                          {formatDate(med.start_date)} - {formatDate(med.end_date || "")}
                        </p>
                        {med.discontinuation_reason && (
                          <p className="text-xs text-red-600 mt-1">
                            Alasan: {med.discontinuation_reason}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
          </div>

          {pastMedications.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <History className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Tidak ada riwayat obat</p>
            </div>
          )}
        </div>
      )}

      {/* Reconciliation Tab */}
      {activeTab === "reconcile" && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Rekonsiliasi Obat</h3>
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>Fitur rekonsiliasi akan segera tersedia</p>
          </div>
        </div>
      )}
    </div>
  );
}
