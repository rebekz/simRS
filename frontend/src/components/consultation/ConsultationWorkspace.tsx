"use client";

/**
 * Consultation Workspace Component for STORY-016: Doctor Consultation Workflow
 *
 * Comprehensive consultation interface integrating:
 * - Patient summary with allergies, medications, problems
 * - Clinical documentation (SOAP notes)
 * - Diagnosis entry with ICD-10 codes
 * - Treatment planning
 * - Patient education materials
 */

import { useState, useEffect } from "react";
import { User, FileText, Pills, AlertCircle, CheckCircle, Clock, Video, AlertTriangle } from "lucide-react";
import { SOAPNoteEditor } from "../clinical/SOAPNoteEditor";
import { ICD10Selector } from "../patients/ICD10Selector";

// Types
interface PatientSummary {
  patient_id: number;
  medical_record_number: string;
  full_name: string;
  date_of_birth: string;
  age: number;
  gender: string;
  phone: string;
  email?: string;
  blood_type?: string;
  last_visit_date?: string;
  chronic_problems: string[];
  active_allergies: string[];
  current_medications: string[];
}

interface ConsultationSession {
  encounter_id: number;
  patient_id: number;
  status: string;
  start_time: string;
  encounter_type: string;
  department?: string;
}

interface ConsultationWorkspaceProps {
  patientId: number;
  encounterId?: number;
  onComplete?: (encounterId: number) => void;
}

export function ConsultationWorkspace({ patientId, encounterId, onComplete }: ConsultationWorkspaceProps) {
  const [activeTab, setActiveTab] = useState("summary");
  const [patientSummary, setPatientSummary] = useState<PatientSummary | null>(null);
  const [consultationSession, setConsultationSession] = useState<ConsultationSession | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (encounterId) {
      fetchConsultationSession(encounterId);
    }
    fetchPatientSummary();
  }, [patientId, encounterId]);

  const fetchPatientSummary = async () => {
    try {
      const response = await fetch(`/api/v1/consultation/patient-summary/${patientId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("staff_access_token")}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPatientSummary(data);
      }
    } catch (error) {
      console.error("Failed to fetch patient summary:", error);
    }
  };

  const fetchConsultationSession = async (id: number) => {
    try {
      const response = await fetch(`/api/v1/consultation/session/${id}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("staff_access_token")}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setConsultationSession(data);
      }
    } catch (error) {
      console.error("Failed to fetch consultation session:", error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: "summary", label: "Patient Summary", icon: User },
    { id: "soap", label: "SOAP Note", icon: FileText },
    { id: "diagnosis", label: "Diagnosis", icon: AlertCircle },
    { id: "treatment", label: "Treatment", icon: Pills },
    { id: "education", label: "Education", icon: Video },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Patient Info */}
        {patientSummary && (
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-xl font-bold text-blue-600">
                  {patientSummary.full_name.charAt(0)}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 truncate">{patientSummary.full_name}</h3>
                <p className="text-xs text-gray-500">{patientSummary.medical_record_number}</p>
              </div>
            </div>
            <div className="space-y-1 text-xs text-gray-600">
              <div className="flex justify-between">
                <span>Age/Gender:</span>
                <span className="font-medium">{patientSummary.age} / {patientSummary.gender}</span>
              </div>
              <div className="flex justify-between">
                <span>Blood Type:</span>
                <span className="font-medium">{patientSummary.blood_type || "-"}</span>
              </div>
              {consultationSession && (
                <div className="flex justify-between">
                  <span>Status:</span>
                  <span className="font-medium capitalize">{consultationSession.status}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Quick Stats */}
        {patientSummary && (
          <div className="p-4 border-b border-gray-200 space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600 flex items-center">
                <AlertCircle className="w-4 h-4 mr-2 text-red-500" />
                Allergies
              </span>
              <span className={`font-medium ${patientSummary.active_allergies.length > 0 ? 'text-red-600' : 'text-gray-400'}`}>
                {patientSummary.active_allergies.length}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600 flex items-center">
                <Pills className="w-4 h-4 mr-2 text-blue-500" />
                Medications
              </span>
              <span className={`font-medium ${patientSummary.current_medications.length > 0 ? 'text-blue-600' : 'text-gray-400'}`}>
                {patientSummary.current_medications.length}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600 flex items-center">
                <FileText className="w-4 h-4 mr-2 text-purple-500" />
                Chronic Problems
              </span>
              <span className={`font-medium ${patientSummary.chronic_problems.length > 0 ? 'text-purple-600' : 'text-gray-400'}`}>
                {patientSummary.chronic_problems.length}
              </span>
            </div>
          </div>
        )}

        {/* Session Timer */}
        {consultationSession && (
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center text-sm text-gray-600 mb-2">
              <Clock className="w-4 h-4 mr-2" />
              Session Duration
            </div>
            <ConsultationTimer startTime={consultationSession.start_time} />
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Tabs */}
        <div className="bg-white border-b border-gray-200 px-6">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === "summary" && patientSummary && (
            <PatientSummaryTab summary={patientSummary} />
          )}

          {activeTab === "soap" && (
            <SOAPNoteEditor
              patientId={patientId}
              encounterId={encounterId}
              onSave={() => {
                // Refresh session data
                if (encounterId) fetchConsultationSession(encounterId);
              }}
              onSign={(noteId) => {
                console.log("Clinical note signed:", noteId);
              }}
            />
          )}

          {activeTab === "diagnosis" && encounterId && (
            <DiagnosisTab encounterId={encounterId} />
          )}

          {activeTab === "treatment" && encounterId && (
            <TreatmentTab encounterId={encounterId} />
          )}

          {activeTab === "education" && (
            <EducationTab />
          )}
        </div>
      </div>
    </div>
  );
}

// Sub-components
function ConsultationTimer({ startTime }: { startTime: string }) {
  const [elapsed, setElapsed] = useState("");

  useEffect(() => {
    const updateElapsed = () => {
      const start = new Date(startTime);
      const now = new Date();
      const diff = Math.floor((now.getTime() - start.getTime()) / 1000 / 60);
      const hours = Math.floor(diff / 60);
      const minutes = diff % 60;
      setElapsed(`${hours}h ${minutes}m`);
    };

    updateElapsed();
    const interval = setInterval(updateElapsed, 60000);
    return () => clearInterval(interval);
  }, [startTime]);

  return <div className="text-lg font-semibold text-gray-900">{elapsed}</div>;
}

function PatientSummaryTab({ summary }: { summary: PatientSummary }) {
  return (
    <div className="space-y-6">
      {/* Alerts */}
      {summary.active_allergies.length > 0 && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-800">Active Allergies</h3>
              <div className="mt-2 flex flex-wrap gap-2">
                {summary.active_allergies.map((allergy, idx) => (
                  <span key={idx} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    {allergy}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chronic Problems */}
      {summary.chronic_problems.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Chronic Conditions</h3>
          <div className="flex flex-wrap gap-2">
            {summary.chronic_problems.map((problem, idx) => (
              <span key={idx} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                {problem}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Current Medications */}
      {summary.current_medications.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Current Medications</h3>
          <div className="space-y-2">
            {summary.current_medications.map((med, idx) => (
              <div key={idx} className="p-3 bg-blue-50 rounded-lg">
                <p className="text-sm font-medium text-blue-900">{med}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Last Visit */}
      {summary.last_visit_date && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Last Visit</h3>
          <p className="text-sm text-gray-600">
            {new Date(summary.last_visit_date).toLocaleDateString("id-ID", {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </p>
        </div>
      )}
    </div>
  );
}

function DiagnosisTab({ encounterId }: { encounterId: number }) {
  const [diagnoses, setDiagnoses] = useState<any[]>([]);
  const [showICD10Selector, setShowICD10Selector] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Diagnoses</h2>
        <button
          onClick={() => setShowICD10Selector(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
        >
          Add Diagnosis
        </button>
      </div>

      {diagnoses.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No diagnoses recorded
        </div>
      ) : (
        <div className="space-y-3">
          {diagnoses.map((dx) => (
            <div key={dx.id} className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">{dx.diagnosis_name}</p>
                  <p className="text-sm text-gray-600">{dx.icd_10_code}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${
                  dx.diagnosis_type === "primary" ? "bg-blue-100 text-blue-800" : "bg-gray-100 text-gray-800"
                }`}>
                  {dx.diagnosis_type}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showICD10Selector && (
        <ICD10Selector
          onSelect={(code) => {
            // Add diagnosis logic here
            setShowICD10Selector(false);
          }}
          onClose={() => setShowICD10Selector(false)}
        />
      )}
    </div>
  );
}

function TreatmentTab({ encounterId }: { encounterId: number }) {
  const [treatments, setTreatments] = useState<any[]>([]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Treatment Plan</h2>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
          Add Treatment
        </button>
      </div>

      {treatments.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No treatments prescribed
        </div>
      ) : (
        <div className="space-y-3">
          {treatments.map((tx) => (
            <div key={tx.id} className="p-4 border border-gray-200 rounded-lg">
              <p className="font-medium text-gray-900">{tx.treatment_name}</p>
              {tx.dosage && <p className="text-sm text-gray-600">Dosage: {tx.dosage}</p>}
              {tx.frequency && <p className="text-sm text-gray-600">Frequency: {tx.frequency}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function EducationTab() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-gray-900">Patient Education Materials</h2>
      <div className="text-center py-12 text-gray-500">
        Education materials will be displayed based on diagnoses
      </div>
    </div>
  );
}
