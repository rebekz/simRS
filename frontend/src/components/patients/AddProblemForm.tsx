"use client";

/**
 * Add Problem Form Component for STORY-012
 *
 * Form for adding new problems/diagnoses to patient problem list with ICD-10 code selection
 */

import { useState, useEffect } from "react";
import { ICD10Selector } from "@/components/patients/ICD10Selector";

interface ICD10Code {
  id: number;
  code: string;
  code_full: string;
  description_indonesian: string;
  description_english?: string;
  chapter: string;
  is_common: boolean;
}

interface AddProblemFormProps {
  patientId: number;
  encounterId?: number;
  onSuccess: () => void;
  onCancel: () => void;
}

interface ProblemCreate {
  patient_id: number;
  encounter_id?: number;
  icd10_code_id: number;
  problem_name: string;
  description?: string;
  status: "active" | "chronic" | "acute";
  onset_date?: string;
  is_chronic: boolean;
  severity?: "mild" | "moderate" | "severe";
  clinical_notes?: string;
  treatment_plan?: string;
  follow_up_required: boolean;
  follow_up_date?: string;
  certainty?: "confirmed" | "probable" | "possible";
}

export function AddProblemForm({ patientId, encounterId, onSuccess, onCancel }: AddProblemFormProps) {
  const [selectedCode, setSelectedCode] = useState<ICD10Code | null>(null);
  const [showICD10Selector, setShowICD10Selector] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<ProblemCreate>({
    patient_id: patientId,
    encounter_id: encounterId,
    icd10_code_id: 0,
    problem_name: "",
    description: "",
    status: "active",
    is_chronic: false,
    follow_up_required: false,
    certainty: "probable",
  });

  useEffect(() => {
    if (selectedCode) {
      setFormData((prev) => ({
        ...prev,
        icd10_code_id: selectedCode.id,
        problem_name: selectedCode.description_indonesian,
      }));
    }
  }, [selectedCode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!selectedCode) {
      setError("Please select an ICD-10 code");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/api/v1/problems", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("staff_access_token")}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to add problem");
      }

      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add problem");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Add Problem/Diagnosis</h2>
            <p className="text-sm text-gray-600 mt-1">
              Add a new problem to the patient's problem list
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* ICD-10 Code Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ICD-10 Code <span className="text-red-500">*</span>
              </label>
              <button
                type="button"
                onClick={() => setShowICD10Selector(true)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 text-left flex items-center justify-between"
              >
                {selectedCode ? (
                  <div className="flex items-center space-x-3">
                    <span className="font-mono text-sm bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                      {selectedCode.code}
                    </span>
                    <span className="text-gray-900">{selectedCode.description_indonesian}</span>
                  </div>
                ) : (
                  <span className="text-gray-500">Select ICD-10 diagnosis code...</span>
                )}
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
              {selectedCode && (
                <p className="text-xs text-gray-500 mt-1">
                  Chapter: {selectedCode.chapter}
                  {selectedCode.is_common && " • Common code"}
                </p>
              )}
            </div>

            {/* Problem Name */}
            <div>
              <label htmlFor="problem_name" className="block text-sm font-medium text-gray-700 mb-2">
                Problem Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="problem_name"
                value={formData.problem_name}
                onChange={(e) => setFormData({ ...formData, problem_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Type 2 Diabetes Mellitus"
                required
              />
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Additional details about this problem..."
              />
            </div>

            {/* Status and Severity */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">
                  Status <span className="text-red-500">*</span>
                </label>
                <select
                  id="status"
                  value={formData.status}
                  onChange={(e) => setFormData({
                    ...formData,
                    status: e.target.value as "active" | "chronic" | "acute",
                    is_chronic: e.target.value === "chronic",
                  })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="active">Active</option>
                  <option value="chronic">Chronic</option>
                  <option value="acute">Acute</option>
                </select>
              </div>

              <div>
                <label htmlFor="severity" className="block text-sm font-medium text-gray-700 mb-2">
                  Severity
                </label>
                <select
                  id="severity"
                  value={formData.severity}
                  onChange={(e) => setFormData({
                    ...formData,
                    severity: e.target.value as "mild" | "moderate" | "severe",
                  })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select severity</option>
                  <option value="mild">Mild</option>
                  <option value="moderate">Moderate</option>
                  <option value="severe">Severe</option>
                </select>
              </div>
            </div>

            {/* Onset Date */}
            <div>
              <label htmlFor="onset_date" className="block text-sm font-medium text-gray-700 mb-2">
                Onset Date
              </label>
              <input
                type="date"
                id="onset_date"
                value={formData.onset_date || ""}
                onChange={(e) => setFormData({ ...formData, onset_date: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Certainty */}
            <div>
              <label htmlFor="certainty" className="block text-sm font-medium text-gray-700 mb-2">
                Diagnostic Certainty
              </label>
              <select
                id="certainty"
                value={formData.certainty}
                onChange={(e) => setFormData({
                  ...formData,
                  certainty: e.target.value as "confirmed" | "probable" | "possible",
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="confirmed">Confirmed</option>
                <option value="probable">Probable</option>
                <option value="possible">Possible</option>
              </select>
            </div>

            {/* Clinical Notes */}
            <div>
              <label htmlFor="clinical_notes" className="block text-sm font-medium text-gray-700 mb-2">
                Clinical Notes
              </label>
              <textarea
                id="clinical_notes"
                value={formData.clinical_notes}
                onChange={(e) => setFormData({ ...formData, clinical_notes: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Relevant clinical findings, symptoms, observations..."
              />
            </div>

            {/* Treatment Plan */}
            <div>
              <label htmlFor="treatment_plan" className="block text-sm font-medium text-gray-700 mb-2">
                Treatment Plan
              </label>
              <textarea
                id="treatment_plan"
                value={formData.treatment_plan}
                onChange={(e) => setFormData({ ...formData, treatment_plan: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Planned treatment, medications, interventions..."
              />
            </div>

            {/* Follow-up */}
            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <label className="text-sm font-medium text-gray-700">
                  Follow-up Required
                </label>
                <button
                  type="button"
                  onClick={() => setFormData({ ...formData, follow_up_required: !formData.follow_up_required })}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    formData.follow_up_required ? "bg-blue-600" : "bg-gray-200"
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                      formData.follow_up_required ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
              </div>

              {formData.follow_up_required && (
                <div>
                  <label htmlFor="follow_up_date" className="block text-sm font-medium text-gray-700 mb-2">
                    Follow-up Date
                  </label>
                  <input
                    type="date"
                    id="follow_up_date"
                    value={formData.follow_up_date || ""}
                    onChange={(e) => setFormData({ ...formData, follow_up_date: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || !selectedCode}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Adding..." : "Add Problem"}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* ICD-10 Selector Modal */}
      {showICD10Selector && (
        <ICD10Selector
          onSelect={(code) => {
            setSelectedCode(code);
            setShowICD10Selector(false);
          }}
          onClose={() => setShowICD10Selector(false)}
          currentCodeId={selectedCode?.id}
        />
      )}
    </>
  );
}
