"use client";

/**
 * Patient Problem List Component for STORY-012
 *
 * Displays and manages patient problems/diagnoses with:
 * - Active and resolved problem tracking
 * - Chronic condition indicators
 * - Severity classification
 * - Clinical notes and treatment plans
 * - Follow-up tracking
 */

import { useState, useEffect } from "react";
import { Plus, Edit2, CheckCircle, AlertCircle, Clock, Calendar, FileText } from "lucide-react";

// Types
interface Problem {
  id: number;
  patient_id: number;
  encounter_id?: number;
  icd10_code_id: number;
  icd10_code: string;
  problem_name: string;
  description?: string;
  status: "active" | "resolved" | "chronic" | "acute";
  onset_date?: string;
  resolved_date?: string;
  is_chronic: boolean;
  severity?: string;
  clinical_notes?: string;
  treatment_plan?: string;
  follow_up_required: boolean;
  follow_up_date?: string;
  certainty?: string;
  icd10_description?: string;
  icd10_chapter?: string;
  diagnosed_by_name?: string;
  recorded_by_name?: string;
  created_at: string;
  updated_at: string;
}

interface PatientProblemListResponse {
  patient_id: number;
  medical_record_number: string;
  full_name: string;
  problems: Problem[];
  total_problems: number;
  active_problems: number;
  chronic_problems: number;
  resolved_problems: number;
}

interface ProblemListProps {
  patientId: number;
  onProblemClick?: (problem: Problem) => void;
}

export function ProblemList({ patientId, onProblemClick }: ProblemListProps) {
  const [problems, setProblems] = useState<PatientProblemListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);

  useEffect(() => {
    fetchProblems();
  }, [patientId, statusFilter]);

  const fetchProblems = async () => {
    setIsLoading(true);
    try {
      const params = statusFilter ? `?status_filter=${statusFilter}` : "";
      const response = await fetch(`/api/v1/problems/patient/${patientId}${params}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProblems(data);
      }
    } catch (error) {
      console.error("Failed to fetch problems:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800";
      case "resolved":
        return "bg-gray-100 text-gray-800";
      case "chronic":
        return "bg-purple-100 text-purple-800";
      case "acute":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case "mild":
        return "bg-green-100 text-green-800";
      case "moderate":
        return "bg-yellow-100 text-yellow-800";
      case "severe":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getCertaintyColor = (certainty?: string) => {
    switch (certainty) {
      case "confirmed":
        return "bg-blue-100 text-blue-800";
      case "probable":
        return "bg-yellow-100 text-yellow-800";
      case "possible":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-50 text-gray-600";
    }
  };

  const handleProblemClick = (problem: Problem) => {
    setSelectedProblem(problem);
    if (onProblemClick) {
      onProblemClick(problem);
    } else {
      setShowEditModal(true);
    }
  };

  const handleResolveProblem = async (problemId: number) => {
    try {
      const response = await fetch(`/api/v1/problems/${problemId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({ status: "resolved" }),
      });

      if (response.ok) {
        fetchProblems();
      }
    } catch (error) {
      console.error("Failed to resolve problem:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!problems) {
    return <div className="text-center text-gray-500 py-8">No problems found</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Problem List</h2>
          <p className="text-sm text-gray-600 mt-1">
            {problems.medical_record_number} - {problems.full_name}
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Problem
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Total Problems</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">
              {problems.total_problems}
            </dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Active</dt>
            <dd className="mt-1 text-3xl font-semibold text-green-600">
              {problems.active_problems}
            </dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Chronic</dt>
            <dd className="mt-1 text-3xl font-semibold text-purple-600">
              {problems.chronic_problems}
            </dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Resolved</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-600">
              {problems.resolved_problems}
            </dd>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-4">
        <span className="text-sm font-medium text-gray-700">Filter by status:</span>
        <div className="flex space-x-2">
          <button
            onClick={() => setStatusFilter("")}
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              statusFilter === ""
                ? "bg-blue-100 text-blue-800"
                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
            }`}
          >
            All
          </button>
          <button
            onClick={() => setStatusFilter("active")}
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              statusFilter === "active"
                ? "bg-green-100 text-green-800"
                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
            }`}
          >
            Active
          </button>
          <button
            onClick={() => setStatusFilter("chronic")}
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              statusFilter === "chronic"
                ? "bg-purple-100 text-purple-800"
                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
            }`}
          >
            Chronic
          </button>
          <button
            onClick={() => setStatusFilter("resolved")}
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              statusFilter === "resolved"
                ? "bg-gray-200 text-gray-800"
                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
            }`}
          >
            Resolved
          </button>
        </div>
      </div>

      {/* Problems List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {problems.problems.map((problem) => (
            <li key={problem.id}>
              <button
                onClick={() => handleProblemClick(problem)}
                className="w-full px-4 py-4 sm:px-6 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 text-left"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    {/* ICD-10 Code and Problem Name */}
                    <div className="flex items-center space-x-3">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 font-mono">
                        {problem.icd10_code}
                      </span>
                      <h3 className="text-lg font-medium text-gray-900 truncate">
                        {problem.problem_name}
                      </h3>
                      {problem.is_chronic && (
                        <AlertCircle className="h-5 w-5 text-purple-600" title="Chronic condition" />
                      )}
                    </div>

                    {/* Description */}
                    {problem.description && (
                      <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                        {problem.description}
                      </p>
                    )}

                    {/* ICD-10 Description */}
                    {problem.icd10_description && (
                      <p className="mt-1 text-sm text-gray-500 italic">
                        {problem.icd10_description}
                      </p>
                    )}

                    {/* Metadata */}
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(
                          problem.status
                        )}`}
                      >
                        {problem.status.charAt(0).toUpperCase() + problem.status.slice(1)}
                      </span>

                      {problem.severity && (
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getSeverityColor(
                            problem.severity
                          )}`}
                        >
                          {problem.severity}
                        </span>
                      )}

                      {problem.certainty && (
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getCertaintyColor(
                            problem.certainty
                          )}`}
                        >
                          {problem.certainty}
                        </span>
                      )}

                      {problem.onset_date && (
                        <span className="inline-flex items-center text-xs text-gray-500">
                          <Calendar className="h-3 w-3 mr-1" />
                          Onset: {new Date(problem.onset_date).toLocaleDateString()}
                        </span>
                      )}

                      {problem.follow_up_required && problem.follow_up_date && (
                        <span className="inline-flex items-center text-xs text-orange-600">
                          <Clock className="h-3 w-3 mr-1" />
                          Follow-up: {new Date(problem.follow_up_date).toLocaleDateString()}
                        </span>
                      )}
                    </div>

                    {/* Clinical Notes Preview */}
                    {problem.clinical_notes && (
                      <div className="mt-2 flex items-start text-xs text-gray-600">
                        <FileText className="h-3 w-3 mr-1 mt-0.5 flex-shrink-0" />
                        <span className="line-clamp-1">{problem.clinical_notes}</span>
                      </div>
                    )}

                    {/* Attribution */}
                    <div className="mt-2 text-xs text-gray-500">
                      {problem.diagnosed_by_name && (
                        <span>Diagnosed by {problem.diagnosed_by_name}</span>
                      )}
                      <span className="mx-2">•</span>
                      <span>
                        Recorded {new Date(problem.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="ml-4 flex-shrink-0 flex items-center space-x-2">
                    {problem.status === "active" && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleResolveProblem(problem.id);
                        }}
                        className="p-2 text-green-600 hover:bg-green-50 rounded-full"
                        title="Mark as resolved"
                      >
                        <CheckCircle className="h-5 w-5" />
                      </button>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleProblemClick(problem);
                      }}
                      className="p-2 text-gray-600 hover:bg-gray-100 rounded-full"
                      title="Edit problem"
                    >
                      <Edit2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </button>
            </li>
          ))}
        </ul>

        {problems.problems.length === 0 && (
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No problems</h3>
            <p className="mt-1 text-sm text-gray-500">
              No problems found for this patient.
            </p>
          </div>
        )}
      </div>

      {/* Add Problem Modal Placeholder */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-4 py-3 sm:px-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Add Problem</h3>
            </div>
            <div className="px-4 py-5 sm:p-6">
              <p className="text-sm text-gray-600">
                Add problem form would go here. For now, this is a placeholder.
              </p>
              {/* TODO: Implement AddProblemForm component */}
            </div>
            <div className="px-4 py-3 sm:px-6 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                Add Problem
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Problem Modal Placeholder */}
      {showEditModal && selectedProblem && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-4 py-3 sm:px-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Edit Problem</h3>
            </div>
            <div className="px-4 py-5 sm:p-6">
              <p className="text-sm text-gray-600">
                Edit problem form would go here. For now, this is a placeholder.
              </p>
              {/* TODO: Implement EditProblemForm component */}
              <pre className="mt-4 text-xs bg-gray-100 p-2 rounded overflow-auto">
                {JSON.stringify(selectedProblem, null, 2)}
              </pre>
            </div>
            <div className="px-4 py-3 sm:px-6 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setSelectedProblem(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setSelectedProblem(null);
                }}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
