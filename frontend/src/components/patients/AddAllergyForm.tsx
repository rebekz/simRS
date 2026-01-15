"use client";

/**
 * Add Allergy Form Component for STORY-013
 *
 * Form for adding new patient allergies with comprehensive documentation
 * for patient safety and clinical workflows.
 */

import { useState } from "react";
import { X, AlertTriangle, Pill, Apple, Leaf, Shield } from "lucide-react";

interface AllergyType {
  value: string;
  label: string;
  icon: React.ReactNode;
}

interface Severity {
  value: string;
  label: string;
  color: string;
}

interface Source {
  value: string;
  label: string;
}

interface AddAllergyFormProps {
  patientId: number;
  onSuccess: () => void;
  onCancel: () => void;
}

const allergyTypes: AllergyType[] = [
  { value: "drug", label: "Obat", icon: <Pill className="h-4 w-4" /> },
  { value: "food", label: "Makanan", icon: <Apple className="h-4 w-4" /> },
  { value: "environmental", label: "Lingkungan", icon: <Leaf className="h-4 w-4" /> },
  { value: "other", label: "Lainnya", icon: <Shield className="h-4 w-4" /> },
];

const severities: Severity[] = [
  { value: "mild", label: "Ringan", color: "green" },
  { value: "moderate", label: "Sedang", color: "yellow" },
  { value: "severe", label: "Parah", color: "orange" },
  { value: "life_threatening", label: "Mengancam Jiwa", color: "red" },
];

const sources: Source[] = [
  { value: "patient_reported", label: "Dilaporkan Pasien" },
  { value: "tested", label: "Teruji Lab" },
  { value: "observed", label: "Observasi Klinis" },
  { value: "inferred", label: "Inferensi" },
];

export function AddAllergyForm({ patientId, onSuccess, onCancel }: AddAllergyFormProps) {
  const [formData, setFormData] = useState({
    allergy_type: "drug" as string,
    allergen: "",
    severity: "moderate" as string,
    reaction: "",
    reaction_details: "",
    status: "active" as string,
    onset_date: "",
    source: "patient_reported" as string,
    clinical_notes: "",
    alternatives: "", // comma-separated
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.allergen.trim()) {
      setError("Nama alergen wajib diisi");
      return;
    }

    if (!formData.reaction.trim()) {
      setError("Reaksi alergi wajib diisi");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/api/v1/allergies", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("staff_access_token")}`,
        },
        body: JSON.stringify({
          patient_id: patientId,
          allergy_type: formData.allergy_type,
          allergen: formData.allergen.trim(),
          severity: formData.severity,
          reaction: formData.reaction.trim(),
          reaction_details: formData.reaction_details.trim() || undefined,
          status: formData.status,
          onset_date: formData.onset_date || undefined,
          source: formData.source,
          clinical_notes: formData.clinical_notes.trim() || undefined,
          alternatives: formData.alternatives ? formData.alternatives.split(",").map(a => a.trim()).filter(a => a) : undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to add allergy");
      }

      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add allergy");
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "life_threatening": return "bg-red-100 text-red-800 border-red-300";
      case "severe": return "bg-orange-100 text-orange-800 border-orange-300";
      case "moderate": return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "mild": return "bg-green-100 text-green-800 border-green-300";
      default: return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Tambah Alergi Pasien</h2>
              <p className="text-sm text-gray-600 mt-1">
                Dokumentasi alergi untuk keamanan pasien
              </p>
            </div>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Warning for life-threatening */}
          {formData.severity === "life_threatening" && (
            <div className="mt-4 bg-red-50 border-l-4 border-red-500 p-4 rounded">
              <div className="flex items-start">
                <AlertTriangle className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-red-800">
                    PERINGATAN: Alergi yang mengancam jiwa
                  </p>
                  <p className="text-xs text-red-700 mt-1">
                    Alergi ini akan menampilkan peringatan prominen di seluruh sistem.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Allergy Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Tipe Alergi <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-2 gap-3">
              {allergyTypes.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, allergy_type: type.value })}
                  className={`p-4 border-2 rounded-lg flex items-center space-x-3 transition-colors ${
                    formData.allergy_type === type.value
                      ? "border-blue-500 bg-blue-50 text-blue-700"
                      : "border-gray-300 hover:border-gray-400"
                  }`}
                >
                  {type.icon}
                  <span className="font-medium">{type.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Allergen */}
          <div>
            <label htmlFor="allergen" className="block text-sm font-medium text-gray-700 mb-2">
              Nama Alergen <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="allergen"
              value={formData.allergen}
              onChange={(e) => setFormData({ ...formData, allergen: e.target.value })}
              placeholder="Contoh: Paracetamol, Penicillin, Kacang, Debu"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Nama zat atau bahan yang menyebabkan alergi
            </p>
          </div>

          {/* Severity */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Tingkat Keparahan <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-2 gap-3">
              {severities.map((severity) => (
                <button
                  key={severity.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, severity: severity.value })}
                  className={`p-3 border-2 rounded-lg flex items-center justify-center transition-colors ${
                    formData.severity === severity.value
                      ? `border-${severity.color}-500 bg-${severity.color}-50`
                      : "border-gray-300 hover:border-gray-400"
                  }`}
                >
                  <span className="font-medium">{severity.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Reaction */}
          <div>
            <label htmlFor="reaction" className="block text-sm font-medium text-gray-700 mb-2">
              Reaksi Alergi <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="reaction"
              value={formData.reaction}
              onChange={(e) => setFormData({ ...formData, reaction: e.target.value })}
              placeholder="Contoh: Ruam, Gatal-gatal, Sesak Napas"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          {/* Reaction Details */}
          <div>
            <label htmlFor="reaction_details" className="block text-sm font-medium text-gray-700 mb-2">
              Detail Reaksi
            </label>
            <textarea
              id="reaction_details"
              value={formData.reaction_details}
              onChange={(e) => setFormData({ ...formData, reaction_details: e.target.value })}
              rows={2}
              placeholder="Deskripsikan reaksi lebih detail..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Onset Date */}
          <div>
            <label htmlFor="onset_date" className="block text-sm font-medium text-gray-700 mb-2">
              Tanggal Mulai
            </label>
            <input
              type="date"
              id="onset_date"
              value={formData.onset_date}
              onChange={(e) => setFormData({ ...formData, onset_date: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Source */}
          <div>
            <label htmlFor="source" className="block text-sm font-medium text-gray-700 mb-2">
              Sumber Informasi
            </label>
            <select
              id="source"
              value={formData.source}
              onChange={(e) => setFormData({ ...formData, source: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {sources.map((source) => (
                <option key={source.value} value={source.value}>
                  {source.label}
                </option>
              ))}
            </select>
          </div>

          {/* Alternatives */}
          <div>
            <label htmlFor="alternatives" className="block text-sm font-medium text-gray-700 mb-2">
              Alternatif Aman
            </label>
            <input
              type="text"
              id="alternatives"
              value={formData.alternatives}
              onChange={(e) => setFormData({ ...formData, alternatives: e.target.value })}
              placeholder="Contoh: Ibuprofen, Aspirin (pisahkan dengan koma)"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Pilihan obat/makanan yang aman sebagai alternatif
            </p>
          </div>

          {/* Clinical Notes */}
          <div>
            <label htmlFor="clinical_notes" className="block text-sm font-medium text-gray-700 mb-2">
              Catatan Klinis
            </label>
            <textarea
              id="clinical_notes"
              value={formData.clinical_notes}
              onChange={(e) => setFormData({ ...formData, clinical_notes: e.target.value })}
              rows={3}
              placeholder="Catatan tambahan untuk referensi klinis..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Footer */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
            >
              {loading ? "Menyimpan..." : "Simpan Alergi"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
