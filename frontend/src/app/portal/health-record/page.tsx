"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

interface AllergyItem {
  id: number;
  allergy_type: string;
  allergen: string;
  severity: string;
  reaction: string;
  status: string;
  onset_date: string | null;
}

interface DiagnosisItem {
  id: number;
  icd_10_code: string;
  diagnosis_name: string;
  diagnosis_type: string;
  is_chronic: boolean;
  encounter_date: string;
  patient_friendly_description: string | null;
}

interface MedicationItem {
  id: number;
  treatment_name: string;
  dosage: string | null;
  frequency: string | null;
  is_active: boolean;
  encounter_date: string;
}

interface EncounterItem {
  id: number;
  encounter_type: string;
  encounter_date: string;
  department: string | null;
  doctor_name: string | null;
  chief_complaint: string | null;
  status: string;
}

interface TimelineEvent {
  id: string;
  event_type: string;
  title: string;
  description: string | null;
  date: string;
}

interface HealthRecord {
  demographics: {
    full_name: string;
    medical_record_number: string;
    date_of_birth: string;
    gender: string;
    blood_type: string | null;
    phone: string | null;
    email: string | null;
    address: string | null;
    city: string | null;
    province: string | null;
  };
  allergies: {
    active_allergies: AllergyItem[];
    resolved_allergies: AllergyItem[];
    has_severe_allergies: boolean;
  };
  diagnoses: {
    active_diagnoses: DiagnosisItem[];
    chronic_conditions: DiagnosisItem[];
  };
  medications: {
    current_medications: MedicationItem[];
    past_medications: MedicationItem[];
  };
  encounter_history: {
    encounters: EncounterItem[];
    total: number;
  };
  timeline: {
    events: TimelineEvent[];
    total_events: number;
  };
}

export default function HealthRecordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const section = searchParams.get("section") || "overview";

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [record, setRecord] = useState<HealthRecord | null>(null);

  useEffect(() => {
    checkAuth();
    fetchHealthRecord();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchHealthRecord = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/portal/health-record", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push("/portal/login");
          return;
        }
        throw new Error("Failed to fetch health record");
      }

      const data = await response.json();
      setRecord(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load health record");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your health records...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <a href="/portal/dashboard" className="text-indigo-600 hover:underline text-sm">
                ← Back to Dashboard
              </a>
              <h1 className="text-2xl font-bold text-gray-900 mt-1">My Health Record</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {record && (
          <>
            {/* Navigation Tabs */}
            <div className="bg-white rounded-lg shadow-md mb-6">
              <div className="border-b border-gray-200">
                <nav className="flex -mb-px overflow-x-auto">
                  {[
                    { id: "overview", label: "Overview" },
                    { id: "demographics", label: "Personal Info" },
                    { id: "allergies", label: "Allergies" },
                    { id: "diagnoses", label: "Diagnoses" },
                    { id: "medications", label: "Medications" },
                    { id: "encounters", label: "Visit History" },
                    { id: "timeline", label: "Timeline" },
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => router.push(`/portal/health-record?section=${tab.id}`)}
                      className={`px-6 py-4 text-sm font-medium whitespace-nowrap border-b-2 ${
                        section === tab.id
                          ? "border-indigo-600 text-indigo-600"
                          : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </nav>
              </div>
            </div>

            {/* Content Sections */}
            {section === "overview" && <OverviewSection record={record} />}
            {section === "demographics" && <DemographicsSection record={record} />}
            {section === "allergies" && <AllergiesSection record={record} />}
            {section === "diagnoses" && <DiagnosesSection record={record} />}
            {section === "medications" && <MedicationsSection record={record} />}
            {section === "encounters" && <EncountersSection record={record} />}
            {section === "timeline" && <TimelineSection record={record} />}
          </>
        )}
      </main>
    </div>
  );
}

function OverviewSection({ record }: { record: HealthRecord }) {
  const age = Math.floor(
    (new Date().getTime() - new Date(record.demographics.date_of_birth).getTime()) /
      (1000 * 60 * 60 * 24 * 365.25)
  );

  return (
    <div className="space-y-6">
      {/* Personal Summary */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Personal Summary</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-500">Name</p>
            <p className="font-medium">{record.demographics.full_name}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Age</p>
            <p className="font-medium">{age} years</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Gender</p>
            <p className="font-medium capitalize">{record.demographics.gender}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Blood Type</p>
            <p className="font-medium">{record.demographics.blood_type || "Not recorded"}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">MRN</p>
            <p className="font-medium">{record.demographics.medical_record_number}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Total Visits</p>
            <p className="font-medium">{record.encounter_history.total}</p>
          </div>
        </div>
      </div>

      {/* Health Alerts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className={`bg-white rounded-lg shadow-md p-6 border-l-4 ${
          record.allergies.has_severe_allergies ? "border-red-500" : "border-green-500"
        }`}>
          <h3 className="font-semibold text-gray-900 mb-2">Allergies</h3>
          <p className="text-2xl font-bold mb-1">{record.allergies.active_allergies.length}</p>
          <p className="text-sm text-gray-600">Active allergies recorded</p>
          {record.allergies.has_severe_allergies && (
            <p className="text-sm text-red-600 mt-2">⚠️ Severe allergies present</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <h3 className="font-semibold text-gray-900 mb-2">Chronic Conditions</h3>
          <p className="text-2xl font-bold mb-1">{record.diagnoses.chronic_conditions.length}</p>
          <p className="text-sm text-gray-600">Chronic conditions being managed</p>
        </div>
      </div>

      {/* Current Medications */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Medications</h2>
        {record.medications.current_medications.length === 0 ? (
          <p className="text-gray-500">No current medications recorded</p>
        ) : (
          <div className="space-y-3">
            {record.medications.current_medications.slice(0, 5).map((med) => (
              <div key={med.id} className="p-3 bg-gray-50 rounded-lg">
                <p className="font-medium">{med.treatment_name}</p>
                <p className="text-sm text-gray-600">{med.dosage} • {med.frequency}</p>
              </div>
            ))}
            {record.medications.current_medications.length > 5 && (
              <button
                onClick={() => document.querySelector('[data-section="medications"]')?.scrollIntoView({ behavior: 'smooth' })}
                className="text-indigo-600 hover:underline text-sm"
              >
                View all {record.medications.current_medications.length} medications →
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function DemographicsSection({ record }: { record: HealthRecord }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h2>
      <div className="space-y-4">
        <InfoRow label="Full Name" value={record.demographics.full_name} />
        <InfoRow label="Medical Record Number" value={record.demographics.medical_record_number} />
        <InfoRow label="Date of Birth" value={new Date(record.demographics.date_of_birth).toLocaleDateString("id-ID")} />
        <InfoRow label="Gender" value={record.demographics.gender.charAt(0).toUpperCase() + record.demographics.gender.slice(1)} />
        <InfoRow label="Blood Type" value={record.demographics.blood_type || "Not recorded"} />
        <InfoRow label="Phone" value={record.demographics.phone || "Not recorded"} />
        <InfoRow label="Email" value={record.demographics.email || "Not recorded"} />
        <InfoRow label="Address" value={record.demographics.address || "Not recorded"} />
        {record.demographics.city && (
          <InfoRow label="City" value={`${record.demographics.city}${record.demographics.province ? `, ${record.demographics.province}` : ""}`} />
        )}
      </div>
    </div>
  );
}

function AllergiesSection({ record }: { record: HealthRecord }) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Active Allergies</h2>
        {record.allergies.active_allergies.length === 0 ? (
          <p className="text-gray-500">No active allergies recorded</p>
        ) : (
          <div className="space-y-4">
            {record.allergies.active_allergies.map((allergy) => (
              <div key={allergy.id} className={`p-4 rounded-lg border ${
                allergy.severity === "life_threatening" || allergy.severity === "severe"
                  ? "bg-red-50 border-red-200"
                  : allergy.severity === "moderate"
                  ? "bg-yellow-50 border-yellow-200"
                  : "bg-green-50 border-green-200"
              }`}>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">{allergy.allergen}</h3>
                    <p className="text-sm text-gray-600 capitalize">{allergy.allergy_type} allergy</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded ${
                    allergy.severity === "life_threatening" ? "bg-red-200 text-red-800" :
                    allergy.severity === "severe" ? "bg-red-100 text-red-700" :
                    allergy.severity === "moderate" ? "bg-yellow-100 text-yellow-700" :
                    "bg-green-100 text-green-700"
                  }`}>
                    {allergy.severity}
                  </span>
                </div>
                <p className="mt-2 text-sm text-gray-700"><strong>Reaction:</strong> {allergy.reaction}</p>
                {allergy.onset_date && (
                  <p className="text-xs text-gray-500 mt-1">
                    Onset: {new Date(allergy.onset_date).toLocaleDateString("id-ID")}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {record.allergies.resolved_allergies.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Resolved Allergies</h2>
          <div className="space-y-3">
            {record.allergies.resolved_allergies.map((allergy) => (
              <div key={allergy.id} className="p-3 bg-gray-50 rounded-lg">
                <p className="font-medium">{allergy.allergen}</p>
                <p className="text-sm text-gray-600">{allergy.reaction}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function DiagnosesSection({ record }: { record: HealthRecord }) {
  return (
    <div className="space-y-6">
      {record.diagnoses.chronic_conditions.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Chronic Conditions</h2>
          <div className="space-y-4">
            {record.diagnoses.chronic_conditions.map((diagnosis) => (
              <div key={diagnosis.id} className="p-4 bg-blue-50 rounded-lg">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">{diagnosis.diagnosis_name}</h3>
                    <p className="text-sm text-gray-600">ICD-10: {diagnosis.icd_10_code}</p>
                  </div>
                  <span className="px-2 py-1 text-xs font-medium bg-blue-200 text-blue-800 rounded">Chronic</span>
                </div>
                {diagnosis.patient_friendly_description && (
                  <p className="mt-2 text-sm text-gray-700">{diagnosis.patient_friendly_description}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">All Diagnoses</h2>
        <div className="space-y-4">
          {record.diagnoses.active_diagnoses.map((diagnosis) => (
            <div key={diagnosis.id} className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{diagnosis.diagnosis_name}</h3>
                  <p className="text-sm text-gray-600">ICD-10: {diagnosis.icd_10_code} • Diagnosed {new Date(diagnosis.encounter_date).toLocaleDateString("id-ID")}</p>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded capitalize ${
                  diagnosis.diagnosis_type === "primary" ? "bg-indigo-100 text-indigo-700" : "bg-gray-100 text-gray-700"
                }`}>
                  {diagnosis.diagnosis_type}
                </span>
              </div>
              {diagnosis.patient_friendly_description && (
                <p className="mt-2 text-sm text-gray-700">{diagnosis.patient_friendly_description}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MedicationsSection({ record }: { record: HealthRecord }) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Medications</h2>
        {record.medications.current_medications.length === 0 ? (
          <p className="text-gray-500">No current medications recorded</p>
        ) : (
          <div className="space-y-4">
            {record.medications.current_medications.map((med) => (
              <div key={med.id} className="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                <h3 className="font-semibold text-gray-900">{med.treatment_name}</h3>
                <div className="mt-2 text-sm text-gray-700">
                  {med.dosage && <p><strong>Dosage:</strong> {med.dosage}</p>}
                  {med.frequency && <p><strong>Frequency:</strong> {med.frequency}</p>}
                  <p className="text-xs text-gray-500 mt-1">Prescribed {new Date(med.encounter_date).toLocaleDateString("id-ID")}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {record.medications.past_medications.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Past Medications</h2>
          <div className="space-y-3">
            {record.medications.past_medications.map((med) => (
              <div key={med.id} className="p-3 bg-gray-50 rounded-lg">
                <p className="font-medium">{med.treatment_name}</p>
                <p className="text-sm text-gray-600">{med.dosage} • {med.frequency}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function EncountersSection({ record }: { record: HealthRecord }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Visit History</h2>
      {record.encounter_history.encounters.length === 0 ? (
        <p className="text-gray-500">No visits recorded</p>
      ) : (
        <div className="space-y-4">
          {record.encounter_history.encounters.map((encounter) => (
            <div key={encounter.id} className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900 capitalize">{encounter.encounter_type.replace("_", " ")}</h3>
                  <p className="text-sm text-gray-600">{new Date(encounter.encounter_date).toLocaleDateString("id-ID", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}</p>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded capitalize ${
                  encounter.status === "completed" ? "bg-green-100 text-green-700" :
                  encounter.status === "active" ? "bg-blue-100 text-blue-700" :
                  "bg-gray-100 text-gray-700"
                }`}>
                  {encounter.status}
                </span>
              </div>
              {encounter.department && <p className="text-sm text-gray-700 mt-2"><strong>Department:</strong> {encounter.department}</p>}
              {encounter.doctor_name && <p className="text-sm text-gray-700"><strong>Doctor:</strong> {encounter.doctor_name}</p>}
              {encounter.chief_complaint && <p className="text-sm text-gray-700"><strong>Reason:</strong> {encounter.chief_complaint}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function TimelineSection({ record }: { record: HealthRecord }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Health Timeline</h2>
      <div className="relative">
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
        <div className="space-y-6">
          {record.timeline.events.map((event, index) => (
            <div key={event.id} className="relative pl-10">
              <div className="absolute left-2.5 w-3 h-3 bg-indigo-600 rounded-full border-2 border-white"></div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-500 mb-1">
                  {new Date(event.date).toLocaleDateString("id-ID", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </p>
                <h3 className="font-semibold text-gray-900">{event.title}</h3>
                {event.description && <p className="text-sm text-gray-600 mt-1">{event.description}</p>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid grid-cols-3 gap-4 py-2 border-b border-gray-100">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="col-span-2 font-medium">{value}</p>
    </div>
  );
}
