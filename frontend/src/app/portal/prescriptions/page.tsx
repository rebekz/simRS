"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface MedicationInfo {
  drug_id: number;
  drug_name: string;
  generic_name: string;
  dosage: string;
  dose_unit: string;
  frequency: string;
  route: string;
  duration_days: number | null;
  quantity: number;
  quantity_dispensed: number;
  refills_allowed: number;
  refills_used: number;
  refills_remaining: number;
  instructions: string | null;
  warnings: string[] | null;
}

interface PrescriptionItem {
  id: number;
  prescription_number: string;
  prescription_date: string;
  prescriber_name: string;
  diagnosis: string | null;
  status: string;
  medications: MedicationInfo[];
  is_fully_dispensed: boolean;
  can_refill: boolean;
  refills_remaining: number;
  expires_at: string | null;
}

interface PrescriptionListResponse {
  active_prescriptions: PrescriptionItem[];
  past_prescriptions: PrescriptionItem[];
  total_active: number;
  total_past: number;
}

export default function MyPrescriptionsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [prescriptions, setPrescriptions] = useState<PrescriptionListResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"active" | "past">("active");
  const [selectedMedications, setSelectedMedications] = useState<Set<string>>(new Set());

  useEffect(() => {
    checkAuth();
    fetchPrescriptions();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const fetchPrescriptions = async () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/portal/prescriptions", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push("/portal/login");
          return;
        }
        throw new Error("Failed to fetch prescriptions");
      }

      const data = await response.json();
      setPrescriptions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load prescriptions");
    } finally {
      setLoading(false);
    }
  };

  const toggleMedicationSelection = (prescriptionId: number, medicationIndex: number) => {
    const key = `${prescriptionId}-${medicationIndex}`;
    const newSelection = new Set(selectedMedications);
    if (newSelection.has(key)) {
      newSelection.delete(key);
    } else {
      newSelection.add(key);
    }
    setSelectedMedications(newSelection);
  };

  const handleRequestRefill = () => {
    if (selectedMedications.size === 0) {
      alert("Please select at least one medication to refill");
      return;
    }

    // Store selected medications in sessionStorage for the refill page
    const selected = Array.from(selectedMedications).map(key => {
      const [prescriptionId, medicationIndex] = key.split("-").map(Number);
      const tab = activeTab;
      const prescriptionList = tab === "active" ? prescriptions?.active_prescriptions : prescriptions?.past_prescriptions;
      const prescription = prescriptionList?.find(p => p.id === prescriptionId);
      const medication = prescription?.medications[medicationIndex];
      return {
        prescription_id: prescriptionId,
        prescription_item_id: prescriptionId, // This would need to be the actual item ID
        drug_id: medication?.drug_id,
        drug_name: medication?.drug_name,
        quantity_requested: medication?.quantity,
      };
    });

    sessionStorage.setItem("refillItems", JSON.stringify(selected));
    router.push("/portal/prescriptions/refill");
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("id-ID", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const getRefillStatusColor = (refillsRemaining: number) => {
    if (refillsRemaining === 0) return "text-red-600";
    if (refillsRemaining <= 2) return "text-yellow-600";
    return "text-green-600";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading prescriptions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <a href="/portal/dashboard" className="text-indigo-600 hover:underline text-sm">
                ← Back to Dashboard
              </a>
              <h1 className="text-2xl font-bold text-gray-900 mt-1">My Prescriptions</h1>
            </div>
            {selectedMedications.size > 0 && (
              <button
                onClick={handleRequestRefill}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Request Refill ({selectedMedications.size})
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {prescriptions && (
          <>
            <div className="bg-white rounded-lg shadow-md mb-6">
              <div className="border-b border-gray-200">
                <nav className="flex">
                  <button
                    onClick={() => setActiveTab("active")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "active"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Active ({prescriptions.total_active})
                  </button>
                  <button
                    onClick={() => setActiveTab("past")}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === "past"
                        ? "border-indigo-600 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    Past ({prescriptions.total_past})
                  </button>
                </nav>
              </div>
            </div>

            <div className="space-y-4">
              {activeTab === "active" && (
                <>
                  {prescriptions.active_prescriptions.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-md p-8 text-center">
                      <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                      </svg>
                      <p className="text-gray-500">No active prescriptions</p>
                    </div>
                  ) : (
                    prescriptions.active_prescriptions.map((rx) => (
                      <PrescriptionCard
                        key={rx.id}
                        prescription={rx}
                        selectedMedications={selectedMedications}
                        onToggleSelection={toggleMedicationSelection}
                        showRefill={true}
                      />
                    ))
                  )}
                </>
              )}

              {activeTab === "past" && (
                <>
                  {prescriptions.past_prescriptions.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
                      No past prescriptions
                    </div>
                  ) : (
                    prescriptions.past_prescriptions.map((rx) => (
                      <PrescriptionCard
                        key={rx.id}
                        prescription={rx}
                        selectedMedications={selectedMedications}
                        onToggleSelection={toggleMedicationSelection}
                        showRefill={false}
                      />
                    ))
                  )}
                </>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' });
}

function getRefillStatusColor(refillsRemaining: number): string {
  if (refillsRemaining === 0) return 'text-red-600';
  if (refillsRemaining <= 2) return 'text-yellow-600';
  return 'text-green-600';
}

interface PrescriptionCardProps {
  prescription: PrescriptionItem;
  selectedMedications: Set<string>;
  onToggleSelection: (prescriptionId: number, medicationIndex: number) => void;
  showRefill: boolean;
}

function PrescriptionCard({ prescription, selectedMedications, onToggleSelection, showRefill }: PrescriptionCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Prescription #{prescription.prescription_number}</h3>
          <p className="text-sm text-gray-500">Dr. {prescription.prescriber_name} • {formatDate(prescription.prescription_date)}</p>
          {prescription.diagnosis && (
            <p className="text-sm text-gray-700 mt-1"><strong>Diagnosis:</strong> {prescription.diagnosis}</p>
          )}
        </div>
        <div className="text-right">
          <span className={`px-2 py-1 text-xs font-medium rounded capitalize ${
            prescription.status === "active" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-700"
          }`}>
            {prescription.status}
          </span>
          {showRefill && (
            <p className={`text-sm mt-2 font-medium ${getRefillStatusColor(prescription.refills_remaining)}`}>
              {prescription.refills_remaining} refills remaining
            </p>
          )}
        </div>
      </div>

      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-700">Medications</h4>
        {prescription.medications.map((med, index) => {
          const key = `${prescription.id}-${index}`;
          const isSelected = selectedMedications.has(key);

          return (
            <div
              key={index}
              className={`p-3 border rounded-lg ${
                isSelected ? "border-indigo-500 bg-indigo-50" : "border-gray-200"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{med.drug_name}</p>
                  <p className="text-sm text-gray-600">{med.generic_name} • {med.dosage} {med.dose_unit}</p>
                  <p className="text-sm text-gray-600">{med.frequency} • {med.route}</p>
                  {med.instructions && (
                    <p className="text-sm text-gray-700 mt-1">{med.instructions}</p>
                  )}
                  <div className="flex gap-4 mt-2 text-xs text-gray-500">
                    <span>Qty: {med.quantity_dispensed}/{med.quantity}</span>
                    <span>Refills: {med.refills_used}/{med.refills_allowed}</span>
                  </div>
                  {med.warnings && med.warnings.length > 0 && (
                    <div className="mt-2">
                      {med.warnings.map((warning, i) => (
                        <p key={i} className="text-xs text-yellow-700">⚠️ {warning}</p>
                      ))}
                    </div>
                  )}
                </div>
                {showRefill && med.refills_remaining > 0 && (
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => onToggleSelection(prescription.id, index)}
                    className="ml-4 h-5 w-5 text-indigo-600 rounded focus:ring-indigo-500"
                  />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
