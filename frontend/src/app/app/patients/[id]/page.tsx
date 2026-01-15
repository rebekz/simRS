"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ProblemList } from "@/components/patients/ProblemList";
import { ClinicalNotesList } from "@/components/clinical/ClinicalNotesList";

interface PatientHistory {
  patient_id: number;
  medical_record_number: string;
  full_name: string;
  date_of_birth: string;
  age: number;
  gender: string;
  blood_type: string | null;
  phone: string | null;
  email: string | null;
  address: string | null;
  city: string | null;
  emergency_contacts: Array<{
    id: number;
    name: string;
    relationship: string;
    phone: string;
  }>;
  primary_insurance: {
    type: string;
    number: string;
  } | null;
  insurance_status: string;
  allergies: Array<{
    id: number;
    allergen: string;
    severity: string;
    reaction: string | null;
  }>;
  current_medications: Array<{
    id: number;
    medication_name: string;
    dosage: string;
    frequency: string;
  }>;
  chronic_conditions: Array<{
    id: number;
    condition_name: string;
    diagnosed_date: string | null;
  }>;
  recent_encounters: Array<{
    id: number;
    encounter_number: string;
    encounter_type: string;
    start_date: string;
    department_name: string | null;
    doctor_name: string | null;
    chief_complaint: string | null;
    primary_diagnosis: string | null;
  }>;
  encounter_timeline: Array<{
    date: string;
    encounter_type: string;
    department: string;
    doctor: string | null;
  }>;
  total_encounters: number;
  last_encounter_date: string | null;
  last_department: string | null;
  last_doctor: string | null;
  data_completeness: {
    completeness_percentage: number;
    is_complete: boolean;
  };
  last_updated: string;
}

export default function PatientHistoryPage() {
  const params = useParams();
  const router = useRouter();
  const patientId = params.id as string;

  const [history, setHistory] = useState<PatientHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    fetchPatientHistory();
  }, [patientId]);

  const fetchPatientHistory = async () => {
    const token = localStorage.getItem("staff_access_token");

    try {
      const response = await fetch(`/api/v1/patients/${patientId}/history?include_encounters=true&include_allergies=true&include_medications=true`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch patient history");
      }

      const data = await response.json();
      setHistory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load patient history");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !history) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-700">{error || "Patient not found"}</p>
        <Link href="/app/patients" className="text-blue-600 hover:underline mt-4 inline-block">
          &larr; Back to Patient List
        </Link>
      </div>
    );
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("id-ID", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link href="/app/patients" className="text-blue-600 hover:underline text-sm">
            &larr; Back to Patient List
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-2">
            Patient History
          </h1>
        </div>
        <div className="flex space-x-3">
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm">
            Print Summary
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
            New Encounter
          </button>
        </div>
      </div>

      {/* Patient Summary Card */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-start space-x-6">
          <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
            <span className="text-2xl font-bold text-blue-600">
              {history.full_name.charAt(0)}
            </span>
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {history.full_name}
                </h2>
                <p className="text-sm text-gray-600">
                  {history.medical_record_number} | {history.gender}, {history.age} years
                </p>
              </div>
              {history.data_completeness.completeness_percentage < 80 && (
                <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs">
                  Profile Incomplete ({history.data_completeness.completeness_percentage}%)
                </span>
              )}
            </div>
            <div className="mt-4 grid grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Blood Type:</span>
                <span className="ml-2 font-medium">{history.blood_type || "Unknown"}</span>
              </div>
              <div>
                <span className="text-gray-600">Phone:</span>
                <span className="ml-2 font-medium">{history.phone || "Not provided"}</span>
              </div>
              <div>
                <span className="text-gray-600">Email:</span>
                <span className="ml-2 font-medium">{history.email || "Not provided"}</span>
              </div>
              <div>
                <span className="text-gray-600">Insurance:</span>
                <span className="ml-2 font-medium">{history.insurance_status}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Indicators */}
      <div className="grid grid-cols-4 gap-4">
        <div className={`p-4 rounded-lg border ${history.allergies.length > 0 ? 'bg-red-50 border-red-200' : 'bg-gray-50 border-gray-200'}`}>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Allergies</span>
            <span className={`text-2xl ${history.allergies.length > 0 ? 'text-red-600' : 'text-gray-400'}`}>
              ⚠️
            </span>
          </div>
          <p className={`text-lg font-semibold mt-2 ${history.allergies.length > 0 ? 'text-red-700' : 'text-gray-500'}`}>
            {history.allergies.length}
          </p>
        </div>

        <div className={`p-4 rounded-lg border ${history.chronic_conditions.length > 0 ? 'bg-orange-50 border-orange-200' : 'bg-gray-50 border-gray-200'}`}>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Chronic Conditions</span>
            <span className={`text-2xl ${history.chronic_conditions.length > 0 ? 'text-orange-600' : 'text-gray-400'}`}>
              📋
            </span>
          </div>
          <p className={`text-lg font-semibold mt-2 ${history.chronic_conditions.length > 0 ? 'text-orange-700' : 'text-gray-500'}`}>
            {history.chronic_conditions.length}
          </p>
        </div>

        <div className={`p-4 rounded-lg border ${history.current_medications.length > 0 ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'}`}>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Active Medications</span>
            <span className="text-2xl">💊</span>
          </div>
          <p className="text-lg font-semibold mt-2 text-blue-700">
            {history.current_medications.length}
          </p>
        </div>

        <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Total Encounters</span>
            <span className="text-2xl">🏥</span>
          </div>
          <p className="text-lg font-semibold mt-2 text-purple-700">
            {history.total_encounters}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {["overview", "clinical-notes", "problems", "encounters", "allergies", "medications", "timeline"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                activeTab === tab
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* Allergies */}
            {history.allergies.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Allergies</h3>
                <div className="space-y-2">
                  {history.allergies.map((allergy) => (
                    <div key={allergy.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                      <div>
                        <span className="font-medium text-red-900">{allergy.allergen}</span>
                        <span className="ml-2 text-sm text-red-700">
                          ({allergy.severity})
                        </span>
                      </div>
                      {allergy.reaction && (
                        <span className="text-sm text-red-600">{allergy.reaction}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Chronic Conditions */}
            {history.chronic_conditions.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Chronic Conditions</h3>
                <div className="flex flex-wrap gap-2">
                  {history.chronic_conditions.map((condition) => (
                    <span
                      key={condition.id}
                      className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm"
                    >
                      {condition.condition_name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Current Medications */}
            {history.current_medications.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Current Medications</h3>
                <div className="space-y-2">
                  {history.current_medications.map((med) => (
                    <div key={med.id} className="p-3 border border-gray-200 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-gray-900">{med.medication_name}</p>
                          <p className="text-sm text-gray-600">{med.dosage} - {med.frequency}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Last Visit */}
            {history.last_encounter_date && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Last Visit</h3>
                <p className="text-gray-700">
                  <span className="font-medium">{formatDate(history.last_encounter_date)}</span>
                  {history.last_department && (
                    <span className="text-gray-600 ml-2">
                      at {history.last_department}
                    </span>
                  )}
                  {history.last_doctor && (
                    <span className="text-gray-600 ml-2">
                      with {history.last_doctor}
                    </span>
                  )}
                </p>
              </div>
            )}
          </div>
        )}

                {activeTab === "clinical-notes" && (
          <ClinicalNotesList patientId={parseInt(patientId)} />
        )}

        {activeTab === "problems" && (
          <ProblemList patientId={parseInt(patientId)} />
        )}

        {activeTab === "encounters" && (
          <div className="space-y-3">
            {history.recent_encounters.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No encounters recorded</p>
            ) : (
              history.recent_encounters.map((encounter) => (
                <div key={encounter.id} className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-gray-900">{encounter.encounter_number}</p>
                      <p className="text-sm text-gray-600">
                        {formatDate(encounter.start_date)}
                      </p>
                    </div>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                      {encounter.encounter_type}
                    </span>
                  </div>
                  {(encounter.department_name || encounter.doctor_name) && (
                    <div className="mt-2 text-sm text-gray-600">
                      {encounter.department_name && <span>{encounter.department_name}</span>}
                      {encounter.department_name && encounter.doctor_name && <span> • </span>}
                      {encounter.doctor_name && <span>{encounter.doctor_name}</span>}
                    </div>
                  )}
                  {encounter.chief_complaint && (
                    <p className="mt-2 text-sm text-gray-700">
                      <span className="font-medium">Chief Complaint:</span> {encounter.chief_complaint}
                    </p>
                  )}
                  {encounter.primary_diagnosis && (
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">Diagnosis:</span> {encounter.primary_diagnosis}
                    </p>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "allergies" && (
          <div className="space-y-3">
            {history.allergies.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No allergies recorded</p>
            ) : (
              history.allergies.map((allergy) => (
                <div key={allergy.id} className="p-4 border border-red-200 bg-red-50 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold text-red-900">{allergy.allergen}</p>
                      <p className="text-sm text-red-700 mt-1">
                        Severity: {allergy.severity}
                      </p>
                      {allergy.reaction && (
                        <p className="text-sm text-red-600 mt-1">
                          Reaction: {allergy.reaction}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "medications" && (
          <div className="space-y-3">
            {history.current_medications.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No current medications</p>
            ) : (
              history.current_medications.map((med) => (
                <div key={med.id} className="p-4 border border-gray-200 rounded-lg">
                  <p className="font-semibold text-gray-900">{med.medication_name}</p>
                  <p className="text-sm text-gray-600 mt-1">
                    {med.dosage} | {med.frequency}
                  </p>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "timeline" && (
          <div className="space-y-4">
            {history.encounter_timeline.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No timeline data</p>
            ) : (
              <div className="relative">
                <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
                {history.encounter_timeline.map((item, index) => (
                  <div key={index} className="relative pl-10 pb-6">
                    <div className="absolute left-2.5 w-3 h-3 bg-blue-600 rounded-full border-2 border-white"></div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">{formatDate(item.date)}</p>
                      <p className="font-medium text-gray-900">{item.department}</p>
                      {item.doctor && <p className="text-sm text-gray-600">{item.doctor}</p>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
