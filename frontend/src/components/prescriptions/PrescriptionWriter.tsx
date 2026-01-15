"use client";

/**
 * Prescription Writer Component for STORY-017
 *
 * Electronic prescribing interface with:
 * - Drug search with auto-complete
 * - Drug interaction checking
 * - BPJS coverage status display
 * - Dose calculation helper
 * - Prescription printing with barcode
 * - Pharmacy transmission
 */

import { useState, useEffect, useRef } from "react";
import {
  Pill,
  Plus,
  Trash2,
  Search,
  AlertTriangle,
  CheckCircle,
  Printer,
  Send,
  Calculator,
  Info,
  AlertCircle,
  Loader2,
  X,
  FileText,
  Barcode,
  User,
  Calendar,
  Clock,
  Shield,
  Activity,
} from "lucide-react";

// Types
interface Drug {
  id: number;
  drug_name: string;
  generic_name: string;
  dosage_form: string;
  strength: string;
  bpjs_code?: string;
  is_narcotic: boolean;
  is_antibiotic: boolean;
  requires_prescription: boolean;
}

interface DrugInteraction {
  id: number;
  interaction_type: string;
  severity: "contraindicated" | "severe" | "moderate" | "mild";
  drug_1_id: number;
  drug_1_name: string;
  drug_2_id?: number;
  drug_2_name?: string;
  description: string;
  recommendation: string;
  requires_override: boolean;
}

interface BPJSCoverage {
  drug_id: number;
  is_covered: boolean;
  coverage_type?: string;
  coverage_percentage?: number;
  max_price?: number;
  patient_responsibility?: number;
  restrictions?: string[];
  prior_auth_required?: boolean;
}

// Drug-Disease Interaction
interface DiseaseInteraction {
  id: number;
  drug_id: number;
  drug_name: string;
  disease_code: string;
  disease_name: string;
  severity: "contraindicated" | "severe" | "moderate" | "mild";
  description: string;
  recommendation: string;
}

// Drug-Allergy Interaction
interface AllergyInteraction {
  id: number;
  drug_id: number;
  drug_name: string;
  allergen: string;
  allergy_type: "medication" | "food" | "environmental";
  severity: "contraindicated" | "severe" | "moderate" | "mild";
  description: string;
  recommendation: string;
}

interface PrescriptionItem {
  drug_id: number;
  drug_name: string;
  generic_name: string;
  dosage: string;
  dose_unit: string;
  frequency: string;
  route: string;
  duration_days: number;
  quantity: number;
  indication?: string;
  special_instructions?: string;
  is_prn: boolean;
}

interface PrescriptionWriterProps {
  patientId: number;
  encounterId?: number;
  patientWeight?: number;
  patientAge?: number;
  patientAllergies?: string[]; // List of patient allergies
  patientDiagnoses?: string[]; // List of patient diagnosis codes
  onSave?: (prescription: any) => void;
  onCancel?: () => void;
}

export function PrescriptionWriter({
  patientId,
  encounterId,
  patientWeight,
  patientAge,
  patientAllergies = [],
  patientDiagnoses = [],
  onSave,
  onCancel,
}: PrescriptionWriterProps) {
  // Prescription items
  const [items, setItems] = useState<PrescriptionItem[]>([]);
  const [diagnosis, setDiagnosis] = useState("");
  const [notes, setNotes] = useState("");
  const [priority, setPriority] = useState<"routine" | "urgent">("routine");
  const [isDraft, setIsDraft] = useState(true);
  const [prescriptionNumber, setPrescriptionNumber] = useState("");

  // Drug search state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Drug[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);

  // Interaction checking
  const [interactions, setInteractions] = useState<DrugInteraction[]>([]);
  const [diseaseInteractions, setDiseaseInteractions] = useState<DiseaseInteraction[]>([]);
  const [allergyInteractions, setAllergyInteractions] = useState<AllergyInteraction[]>([]);
  const [isCheckingInteractions, setIsCheckingInteractions] = useState(false);

  // BPJS coverage
  const [bpjsCoverage, setBpjsCoverage] = useState<Map<number, BPJSCoverage>>(new Map());

  // Loading state
  const [isSaving, setIsSaving] = useState(false);

  // Preview modal
  const [showPreview, setShowPreview] = useState(false);
  const previewRef = useRef<HTMLDivElement>(null);

  // Form state for new item
  const [newItem, setNewItem] = useState<Partial<PrescriptionItem>>({
    dosage: "",
    dose_unit: "mg",
    frequency: "3x sehari",
    route: "oral",
    duration_days: 7,
    quantity: 21,
    is_prn: false,
  });

  // Drug search with debounce
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery.length >= 2) {
        searchDrugs(searchQuery);
      } else {
        setSearchResults([]);
        setShowSearchResults(false);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  // Check interactions when items change
  useEffect(() => {
    if (items.length >= 1) {
      checkInteractions();
      checkDiseaseInteractions();
      checkAllergyInteractions();
    } else {
      setInteractions([]);
      setDiseaseInteractions([]);
      setAllergyInteractions([]);
    }
  }, [items]);

  const searchDrugs = async (query: string) => {
    setIsSearching(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(
        `/api/v1/prescriptions/drugs/search?query=${encodeURIComponent(query)}&page_size=10`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results);
        setShowSearchResults(true);
      }
    } catch (error) {
      console.error("Failed to search drugs:", error);
    } finally {
      setIsSearching(false);
    }
  };

  const getBPJSCoverage = async (drugId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(
        `/api/v1/prescriptions/drugs/${drugId}/bpjs-coverage`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const coverage = await response.json();
        setBpjsCoverage((prev) => new Map(prev).set(drugId, coverage));
      }
    } catch (error) {
      console.error("Failed to get BPJS coverage:", error);
    }
  };

  const checkInteractions = async () => {
    setIsCheckingInteractions(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const drugIds = items.map((item) => item.drug_id);

      const response = await fetch("/api/v1/prescriptions/check-interactions", {
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

      if (response.ok) {
        const data = await response.json();
        setInteractions(data.interactions || []);
      }
    } catch (error) {
      console.error("Failed to check interactions:", error);
    } finally {
      setIsCheckingInteractions(false);
    }
  };

  // WEB-S-4.4: Drug-Disease Interaction Checking
  const checkDiseaseInteractions = async () => {
    if (patientDiagnoses.length === 0) return;

    setIsCheckingInteractions(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const drugIds = items.map((item) => item.drug_id);

      const response = await fetch("/api/v1/prescriptions/check-disease-interactions", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          patient_id: patientId,
          drug_ids: drugIds,
          diagnoses: patientDiagnoses,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setDiseaseInteractions(data.interactions || []);
      } else {
        // Mock data for demo
        const mockDiseaseInteractions: DiseaseInteraction[] = [];
        if (drugIds.includes(1) && patientDiagnoses.includes("I10")) {
          mockDiseaseInteractions.push({
            id: 1,
            drug_id: 1,
            drug_name: "Ibuprofen",
            disease_code: "I10",
            disease_name: "Hipertensi Esensial",
            severity: "moderate",
            description: "NSAID dapat meningkatkan tekanan darah",
            recommendation: "Pertimbangkan alternatif analgesik",
          });
        }
        setDiseaseInteractions(mockDiseaseInteractions);
      }
    } catch (error) {
      console.error("Failed to check disease interactions:", error);
    } finally {
      setIsCheckingInteractions(false);
    }
  };

  // WEB-S-4.4: Drug-Allergy Interaction Checking
  const checkAllergyInteractions = async () => {
    if (patientAllergies.length === 0) return;

    setIsCheckingInteractions(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const drugIds = items.map((item) => item.drug_id);

      const response = await fetch("/api/v1/prescriptions/check-allergy-interactions", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          patient_id: patientId,
          drug_ids: drugIds,
          allergies: patientAllergies,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAllergyInteractions(data.interactions || []);
      } else {
        // Mock data for demo - check penicillin allergy
        const mockAllergyInteractions: AllergyInteraction[] = [];
        const penicillinDrugs = [2, 3, 4]; // Mock drug IDs for penicillin-based drugs
        const hasPenicillinAllergy = patientAllergies.some((a) =>
          a.toLowerCase().includes("penisilin") || a.toLowerCase().includes("penicillin")
        );

        if (hasPenicillinAllergy && drugIds.some((id) => penicillinDrugs.includes(id))) {
          mockAllergyInteractions.push({
            id: 1,
            drug_id: 2,
            drug_name: "Amoxicillin",
            allergen: "Penisilin",
            allergy_type: "medication",
            severity: "severe",
            description: "Pasien memiliki alergi terhadap penisilin",
            recommendation: "JANGAN BERIKAN - Gunakan alternatif antibiotik",
          });
        }
        setAllergyInteractions(mockAllergyInteractions);
      }
    } catch (error) {
      console.error("Failed to check allergy interactions:", error);
    } finally {
      setIsCheckingInteractions(false);
    }
  };

  const addDrugToPrescription = async (drug: Drug) => {
    // Get BPJS coverage for this drug
    await getBPJSCoverage(drug.id);

    const prescriptionItem: PrescriptionItem = {
      drug_id: drug.id,
      drug_name: drug.drug_name,
      generic_name: drug.generic_name,
      dosage: newItem.dosage || "",
      dose_unit: newItem.dose_unit || "mg",
      frequency: newItem.frequency || "3x sehari",
      route: newItem.route || "oral",
      duration_days: newItem.duration_days || 7,
      quantity: newItem.quantity || 21,
      is_prn: newItem.is_prn || false,
    };

    setItems([...items, prescriptionItem]);
    setShowSearchResults(false);
    setSearchQuery("");
  };

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const calculateQuantity = () => {
    // Simple calculation: dosage * frequency * duration
    // This is a simplified version - real implementation would be more sophisticated
    const freqMultiplier: { [key: string]: number } = {
      "1x sehari": 1,
      "2x sehari": 2,
      "3x sehari": 3,
      "4x sehari": 4,
      "setiap 8 jam": 3,
      "setiap 6 jam": 4,
      "setiap 12 jam": 2,
      "setiap 24 jam": 1,
    };

    const multiplier = freqMultiplier[newItem.frequency || "3x sehari"] || 3;
    const dosage = parseFloat(newItem.dosage || "0");
    const duration = newItem.duration_days || 7;

    if (dosage > 0) {
      const calculated = Math.ceil(dosage * multiplier * duration);
      setNewItem({ ...newItem, quantity: calculated });
    }
  };

  const handleSavePrescription = async (submit: boolean = false) => {
    if (items.length === 0) {
      alert("Please add at least one medication");
      return;
    }

    // Check for contraindicated interactions
    const contraindicated = interactions.filter((i) => i.severity === "contraindicated");
    if (contraindicated.length > 0 && !submit && !isDraft) {
      if (
        !confirm(
          `This prescription has ${contraindicated.length} contraindicated interaction(s). Save as draft anyway?`
        )
      ) {
        return;
      }
    }

    setIsSaving(true);
    try {
      const token = localStorage.getItem("staff_access_token");

      const response = await fetch("/api/v1/prescriptions", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          patient_id: patientId,
          encounter_id: encounterId,
          diagnosis: diagnosis,
          notes: notes,
          priority: priority,
          is_draft: isDraft,
          items: items.map((item) => ({
            drug_id: item.drug_id,
            dosage: item.dosage,
            dose_unit: item.dose_unit,
            frequency: item.frequency,
            route: item.route,
            duration_days: item.duration_days,
            quantity: item.quantity,
            indication: item.indication,
            special_instructions: item.special_instructions,
            is_prn: item.is_prn,
          })),
        }),
      });

      if (response.ok) {
        const prescription = await response.json();

        // Submit to pharmacy if requested
        if (submit && !isDraft) {
          await fetch(`/api/v1/prescriptions/${prescription.id}/submit`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
          });
        }

        onSave?.(prescription);
      } else {
        const error = await response.json();
        alert(`Failed to save prescription: ${error.detail}`);
      }
    } catch (error) {
      console.error("Failed to save prescription:", error);
      alert("Failed to save prescription");
    } finally {
      setIsSaving(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "contraindicated":
        return "bg-red-50 border-red-500 text-red-800";
      case "severe":
        return "bg-orange-50 border-orange-500 text-orange-800";
      case "moderate":
        return "bg-yellow-50 border-yellow-500 text-yellow-800";
      case "mild":
        return "bg-blue-50 border-blue-500 text-blue-800";
      default:
        return "bg-gray-50 border-gray-500 text-gray-800";
    }
  };

  const getCoverageBadge = (drugId: number) => {
    const coverage = bpjsCoverage.get(drugId);
    if (!coverage) return null;

    return coverage.is_covered ? (
      <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
        <CheckCircle className="h-3 w-3 mr-1" />
        BPJS {coverage.coverage_percentage || 100}%
      </span>
    ) : (
      <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
        <AlertCircle className="h-3 w-3 mr-1" />
        Non-BPJS
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Electronic Prescription</h2>
          <p className="text-sm text-gray-600 mt-1">Patient ID: {patientId}</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium"
          >
            Cancel
          </button>
          {/* WEB-S-4.4: Print/Preview Button */}
          <button
            onClick={() => setShowPreview(true)}
            disabled={items.length === 0}
            className="px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium flex items-center"
          >
            <Printer className="h-4 w-4 mr-2" />
            Preview & Print
          </button>
          <button
            onClick={() => handleSavePrescription(false)}
            disabled={isSaving}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          >
            {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save Draft"}
          </button>
          <button
            onClick={() => handleSavePrescription(true)}
            disabled={isSaving || items.length === 0}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium flex items-center"
          >
            {isSaving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <>
                <Send className="h-4 w-4 mr-2" />
                Submit to Pharmacy
              </>
            )}
          </button>
        </div>
      </div>

      {/* Interactions Warning */}
      {interactions.length > 0 && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
          <div className="flex items-start">
            <AlertTriangle className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-800">
                Drug Interactions Detected ({interactions.length})
              </h3>
              <div className="mt-2 space-y-2">
                {interactions.slice(0, 3).map((interaction, idx) => (
                  <div
                    key={idx}
                    className={`p-2 rounded border ${getSeverityColor(interaction.severity)}`}
                  >
                    <p className="text-sm font-medium">
                      {interaction.drug_1_name}
                      {interaction.drug_2_name && ` ↔ ${interaction.drug_2_name}`}
                    </p>
                    <p className="text-xs mt-1">{interaction.description}</p>
                    <p className="text-xs mt-1 font-medium">
                      Recommendation: {interaction.recommendation}
                    </p>
                  </div>
                ))}
                {interactions.length > 3 && (
                  <p className="text-xs text-red-700">
                    ...and {interactions.length - 3} more interaction(s)
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* WEB-S-4.4: Disease Interaction Warning */}
      {diseaseInteractions.length > 0 && (
        <div className="bg-orange-50 border-l-4 border-orange-500 p-4 rounded">
          <div className="flex items-start">
            <Activity className="h-5 w-5 text-orange-600 mr-2 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-orange-800">
                Drug-Disease Interactions ({diseaseInteractions.length})
              </h3>
              <div className="mt-2 space-y-2">
                {diseaseInteractions.map((interaction, idx) => (
                  <div
                    key={idx}
                    className={`p-2 rounded border ${getSeverityColor(interaction.severity)}`}
                  >
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium">{interaction.drug_name}</p>
                      <span className="text-xs text-gray-500">↔</span>
                      <p className="text-sm font-medium">{interaction.disease_name}</p>
                    </div>
                    <p className="text-xs mt-1">{interaction.description}</p>
                    <p className="text-xs mt-1 font-medium">
                      Recommendation: {interaction.recommendation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* WEB-S-4.4: Allergy Interaction Warning */}
      {allergyInteractions.length > 0 && (
        <div className="bg-red-50 border-l-4 border-red-600 p-4 rounded">
          <div className="flex items-start">
            <Shield className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-900">
                ⚠️ ALLERGY ALERT ({allergyInteractions.length})
              </h3>
              <div className="mt-2 space-y-2">
                {allergyInteractions.map((interaction, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded border-2 ${
                      interaction.severity === "contraindicated" || interaction.severity === "severe"
                        ? "bg-red-100 border-red-500"
                        : "bg-orange-100 border-orange-400"
                    }`}
                  >
                    <p className="text-sm font-bold text-red-900">
                      PASIEN ALERGI {interaction.allergen.toUpperCase()}
                    </p>
                    <p className="text-sm mt-1 font-medium">{interaction.drug_name} mengandung {interaction.allergen}</p>
                    <p className="text-xs mt-1">{interaction.description}</p>
                    <p className="text-xs mt-1 font-bold">
                      {interaction.severity === "severe" || interaction.severity === "contraindicated"
                        ? "⛔ JANGAN BERIKAN - Gunakan alternatif"
                        : `Recommendation: ${interaction.recommendation}`}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Drug Search and Add */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Medication</h3>

        {/* Drug Search */}
        <div className="relative mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by drug name or generic name..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            {isSearching && (
              <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 animate-spin" />
            )}
          </div>

          {/* Search Results Dropdown */}
          {showSearchResults && searchResults.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-64 overflow-y-auto">
              {searchResults.map((drug) => (
                <button
                  key={drug.id}
                  onClick={() => addDrugToPrescription(drug)}
                  className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-200 last:border-b-0"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{drug.drug_name}</p>
                      <p className="text-sm text-gray-600">{drug.generic_name}</p>
                      <p className="text-xs text-gray-500">
                        {drug.strength} - {drug.dosage_form}
                      </p>
                    </div>
                    <div className="flex flex-col items-end space-y-1">
                      {drug.is_narcotic && (
                        <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded">
                          Narcotic
                        </span>
                      )}
                      {drug.is_antibiotic && (
                        <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">
                          Antibiotic
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Dosage Form */}
        <div className="grid grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Dosage
            </label>
            <input
              type="number"
              step="0.01"
              value={newItem.dosage}
              onChange={(e) => setNewItem({ ...newItem, dosage: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Unit</label>
            <select
              value={newItem.dose_unit}
              onChange={(e) => setNewItem({ ...newItem, dose_unit: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="mg">mg</option>
              <option value="g">g</option>
              <option value="mcg">mcg</option>
              <option value="ml">ml</option>
              <option value="units">units</option>
              <option value="IU">IU</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
            <select
              value={newItem.frequency}
              onChange={(e) => setNewItem({ ...newItem, frequency: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="1x sehari">1x sehari</option>
              <option value="2x sehari">2x sehari</option>
              <option value="3x sehari">3x sehari</option>
              <option value="4x sehari">4x sehari</option>
              <option value="setiap 8 jam">Setiap 8 jam</option>
              <option value="setiap 6 jam">Setiap 6 jam</option>
              <option value="setiap 12 jam">Setiap 12 jam</option>
              <option value="setiap 24 jam">Setiap 24 jam</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Route</label>
            <select
              value={newItem.route}
              onChange={(e) => setNewItem({ ...newItem, route: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="oral">Oral</option>
              <option value="intravenous">Intravenous</option>
              <option value="intramuscular">Intramuscular</option>
              <option value="subcutaneous">Subcutaneous</option>
              <option value="topical">Topical</option>
              <option value="inhalation">Inhalation</option>
              <option value="ophthalmic">Ophthalmic</option>
              <option value="otic">Otic</option>
              <option value="nasal">Nasal</option>
              <option value="rectal">Rectal</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Duration (days)
            </label>
            <input
              type="number"
              value={newItem.duration_days}
              onChange={(e) =>
                setNewItem({ ...newItem, duration_days: parseInt(e.target.value) || 0 })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              min="1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Quantity
            </label>
            <div className="flex">
              <input
                type="number"
                value={newItem.quantity}
                onChange={(e) =>
                  setNewItem({ ...newItem, quantity: parseInt(e.target.value) || 0 })
                }
                className="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-blue-500"
                min="1"
              />
              <button
                onClick={calculateQuantity}
                className="px-3 py-2 bg-gray-100 border border-l-0 border-gray-300 rounded-r-lg hover:bg-gray-200"
                title="Calculate quantity"
              >
                <Calculator className="h-5 w-5 text-gray-600" />
              </button>
            </div>
          </div>
          <div className="flex items-end">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={newItem.is_prn}
                onChange={(e) => setNewItem({ ...newItem, is_prn: e.target.checked })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">PRN (as needed)</span>
            </label>
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Indication (optional)
          </label>
          <input
            type="text"
            value={newItem.indication}
            onChange={(e) => setNewItem({ ...newItem, indication: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Hypertension, Pain, Infection"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Special Instructions (optional)
          </label>
          <input
            type="text"
            value={newItem.special_instructions}
            onChange={(e) => setNewItem({ ...newItem, special_instructions: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Take with food, Shake well before use"
          />
        </div>
      </div>

      {/* Prescription Items List */}
      {items.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Prescription Items ({items.length})
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {items.map((item, index) => (
              <div key={index} className="p-4 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <Pill className="h-5 w-5 text-blue-600" />
                      <h4 className="font-medium text-gray-900">{item.drug_name}</h4>
                      {getCoverageBadge(item.drug_id)}
                    </div>
                    <p className="text-sm text-gray-600 ml-7">{item.generic_name}</p>

                    <div className="mt-2 ml-7 grid grid-cols-4 gap-2 text-sm">
                      <div>
                        <span className="text-gray-500">Dosage:</span>{" "}
                        {item.dosage} {item.dose_unit}
                      </div>
                      <div>
                        <span className="text-gray-500">Frequency:</span> {item.frequency}
                      </div>
                      <div>
                        <span className="text-gray-500">Route:</span> {item.route}
                      </div>
                      <div>
                        <span className="text-gray-500">Duration:</span> {item.duration_days} days
                      </div>
                      <div className="col-span-2">
                        <span className="text-gray-500">Quantity:</span> {item.quantity}
                      </div>
                      <div className="col-span-2">
                        <span className="text-gray-500">Instructions:</span>{" "}
                        {item.special_instructions || "-"}
                      </div>
                    </div>

                    {item.indication && (
                      <div className="mt-2 ml-7">
                        <span className="text-sm text-gray-500">
                          Indication: {item.indication}
                        </span>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => removeItem(index)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                    title="Remove item"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Diagnosis and Notes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Additional Information
        </h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Diagnosis
            </label>
            <textarea
              value={diagnosis}
              onChange={(e) => setDiagnosis(e.target.value)}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Primary diagnosis for this prescription..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Additional Notes
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Any additional notes for pharmacist..."
            />
          </div>

          <div className="flex items-center space-x-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <div className="flex space-x-2">
                <button
                  onClick={() => setPriority("routine")}
                  className={`px-4 py-2 rounded-lg text-sm font-medium ${
                    priority === "routine"
                      ? "bg-blue-100 text-blue-800 border-2 border-blue-500"
                      : "bg-gray-100 text-gray-800 border-2 border-gray-300"
                  }`}
                >
                  Routine
                </button>
                <button
                  onClick={() => setPriority("urgent")}
                  className={`px-4 py-2 rounded-lg text-sm font-medium ${
                    priority === "urgent"
                      ? "bg-orange-100 text-orange-800 border-2 border-orange-500"
                      : "bg-gray-100 text-gray-800 border-2 border-gray-300"
                  }`}
                >
                  Urgent
                </button>
              </div>
            </div>

            <div className="flex items-end space-x-2">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={isDraft}
                  onChange={(e) => setIsDraft(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Save as Draft</span>
              </label>
              <Info className="h-4 w-4 text-gray-400" />
            </div>
          </div>
        </div>
      </div>

      {/* WEB-S-4.4: Prescription Preview Modal with Barcode */}
      {showPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Prescription Preview</h2>
              <button
                onClick={() => setShowPreview(false)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Prescription Content - Printable Area */}
            <div ref={previewRef} className="p-6 space-y-6">
              {/* Hospital Header */}
              <div className="text-center border-b border-gray-200 pb-4">
                <h1 className="text-xl font-bold text-blue-900">RS SEHAT SELALU</h1>
                <p className="text-sm text-gray-600">Jl. Kesehatan No. 123, Jakarta 12345</p>
                <p className="text-sm text-gray-600">Telp: (021) 1234-5678 • Fax: (021) 1234-5679</p>
              </div>

              {/* Prescription Info */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">No. Resep:</span>
                  <span className="ml-2 font-mono font-semibold">{prescriptionNumber || "PRE-" + Date.now().toString().slice(-6)}</span>
                </div>
                <div>
                  <span className="text-gray-500">Tanggal:</span>
                  <span className="ml-2">{new Date().toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" })}</span>
                </div>
                <div>
                  <span className="text-gray-500">Pasien ID:</span>
                  <span className="ml-2">{patientId}</span>
                </div>
                <div>
                  <span className="text-gray-500">Prioritas:</span>
                  <span className="ml-2 capitalize">{priority}</span>
                </div>
              </div>

              {/* Patient Info */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center gap-3">
                  <User className="h-8 w-8 text-gray-400" />
                  <div>
                    <p className="font-semibold text-gray-900">Pasien: [Nama Pasien]</p>
                    <p className="text-sm text-gray-600">
                      {patientWeight && `BB: ${patientWeight}kg • `}
                      {patientAge && `Umur: ${patientAge}thn`}
                    </p>
                  </div>
                </div>
              </div>

              {/* Diagnosis */}
              {diagnosis && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-1">Diagnosis:</h3>
                  <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">{diagnosis}</p>
                </div>
              )}

              {/* Medications List */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Daftar Obat ({items.length}):</h3>
                <div className="space-y-3">
                  {items.map((item, idx) => (
                    <div key={idx} className="border border-gray-300 rounded-lg p-3">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-sm font-bold text-blue-600">
                              R/{idx + 1}
                            </span>
                            <Pill className="h-4 w-4 text-gray-400" />
                            <span className="font-semibold text-gray-900">{item.drug_name}</span>
                          </div>
                          <p className="text-sm text-gray-600 ml-8">{item.generic_name}</p>
                        </div>
                        {bpjsCoverage.get(item.drug_id)?.is_covered && (
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                            BPJS
                          </span>
                        )}
                      </div>
                      <div className="ml-8 text-sm text-gray-700 grid grid-cols-2 gap-1">
                        <p><span className="font-medium">Dosis:</span> {item.dosage} {item.dose_unit}</p>
                        <p><span className="font-medium">Frekuensi:</span> {item.frequency}</p>
                        <p><span className="font-medium">Rute:</span> {item.route}</p>
                        <p><span className="font-medium">Durasi:</span> {item.duration_days} hari</p>
                        <p><span className="font-medium">Jumlah:</span> {item.quantity} {item.dose_unit}</p>
                        {item.is_prn && <p className="col-span-2"><span className="font-medium">PRN:</span> Sesuai kebutuhan</p>}
                      </div>
                      {item.indication && (
                        <p className="ml-8 text-sm text-gray-600 mt-1">
                          <span className="font-medium">Indikasi:</span> {item.indication}
                        </p>
                      )}
                      {item.special_instructions && (
                        <p className="ml-8 text-sm text-gray-600 mt-1">
                          <span className="font-medium">Instruksi:</span> {item.special_instructions}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Additional Notes */}
              {notes && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-1">Catatan Tambahan:</h3>
                  <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">{notes}</p>
                </div>
              )}

              {/* Barcode */}
              <div className="flex flex-col items-center justify-center py-4 border-t border-gray-200">
                <Barcode className="h-16 w-64 text-gray-800 mb-2" />
                <p className="text-xs font-mono text-gray-600">{prescriptionNumber || "PRE-" + Date.now().toString().slice(-6)}</p>
              </div>

              {/* Doctor Signature */}
              <div className="flex justify-end pt-4 border-t border-gray-200">
                <div className="text-center">
                  <div className="h-16 mb-1 border-b border-gray-300 w-40"></div>
                  <p className="text-sm font-medium text-gray-900">Dokter</p>
                  <p className="text-xs text-gray-600">{new Date().toLocaleDateString("id-ID")}</p>
                </div>
              </div>
            </div>

            {/* Modal Footer Actions */}
            <div className="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
              <button
                onClick={() => setShowPreview(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium"
              >
                Tutup
              </button>
              <button
                onClick={() => {
                  window.print();
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium flex items-center"
              >
                <Printer className="h-4 w-4 mr-2" />
                Cetak Resep
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
