"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

interface LabTest {
  id: number;
  test_code: string;
  test_name: string;
  test_category: string;
  sample_type: string;
  container: string;
  price: number;
  bpjs_tariff?: number;
  is_bpjs_covered: boolean;
  preparation_instructions?: string;
  fasting_required: boolean;
  turnaround_time: string;
}

interface Patient {
  id: number;
  name: string;
  medical_record_number: string;
  age: number;
  gender: string;
  allergies?: string[];
  pregnancy_status?: "unknown" | "not_pregnant" | "pregnant";
}

export default function LabOrderPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const patientId = searchParams.get("patient_id");
  const encounterId = searchParams.get("encounter_id");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [patient, setPatient] = useState<Patient | null>(null);
  const [availableTests, setAvailableTests] = useState<LabTest[]>([]);
  const [selectedTests, setSelectedTests] = useState<Set<number>>(new Set());
  const [testDetails, setTestDetails] = useState<Map<number, string>>(new Map());
  const [clinicalInfo, setClinicalInfo] = useState({
    diagnosis: "",
    symptoms: "",
    clinical_indication: "",
    priority: "routine" as "routine" | "urgent" | "stat",
    fasting_required: false,
  });
  const [submitting, setSubmitting] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState("");

  useEffect(() => {
    checkAuth();
    if (patientId) {
      fetchPatient(parseInt(patientId));
    }
    fetchAvailableTests();
  }, [patientId]);

  const checkAuth = () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
    }
  };

  const fetchPatient = async (id: number) => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/patients/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPatient(data);
      }
    } catch (err) {
      console.error("Failed to fetch patient:", err);
    }
  };

  const fetchAvailableTests = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/lab/tests/available", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAvailableTests(data.tests || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load lab tests");
    } finally {
      setLoading(false);
    }
  };

  const toggleTestSelection = (testId: number) => {
    const newSelection = new Set(selectedTests);
    if (newSelection.has(testId)) {
      newSelection.delete(testId);
      setTestDetails(prev => {
        const next = new Map(prev);
        next.delete(testId);
        return next;
      });
    } else {
      newSelection.add(testId);
    }
    setSelectedTests(newSelection);
  };

  const handleTestDetailChange = (testId: number, detail: string) => {
    setTestDetails(prev => new Map(prev).set(testId, detail));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedTests.size === 0) {
      alert("Pilih setidaknya satu pemeriksaan laboratorium");
      return;
    }

    if (!patient) {
      alert("Pasien tidak ditemukan");
      return;
    }

    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    setSubmitting(true);

    try {
      const tests = Array.from(selectedTests).map(testId => ({
        test_id: testId,
        additional_notes: testDetails.get(testId) || "",
      }));

      const response = await fetch("/api/v1/lab/orders", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          patient_id: patient.id,
          encounter_id: encounterId ? parseInt(encounterId) : null,
          tests,
          diagnosis: clinicalInfo.diagnosis,
          symptoms: clinicalInfo.symptoms,
          clinical_indication: clinicalInfo.clinical_indication,
          priority: clinicalInfo.priority,
          fasting_required: clinicalInfo.fasting_required,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create lab order");
      }

      const data = await response.json();
      alert(`Pemeriksaan laboratorium berhasil dipesan. Order ID: ${data.order_id}`);

      // Redirect to lab results page
      router.push("/app/lab");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to create lab order");
    } finally {
      setSubmitting(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("id-ID", {
      style: "currency",
      currency: "IDR",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const categories = Array.from(new Set(availableTests.map(t => t.test_category)));

  const filteredTests = categoryFilter
    ? availableTests.filter(t => t.test_category === categoryFilter)
    : availableTests;

  const selectedTestsList = availableTests.filter(t => selectedTests.has(t.id));
  const totalCost = selectedTestsList.reduce((sum, t) => sum + t.price, 0);
  const totalBPJS = selectedTestsList.filter(t => t.is_bpjs_covered).reduce((sum, t) => sum + (t.bpjs_tariff || 0), 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Pemeriksaan Laboratorium</h1>
        <p className="text-gray-600 mt-1">Buat pesanan pemeriksaan laboratorium untuk pasien</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center space-x-3">
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Patient Information */}
        {patient ? (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi Pasien</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-500">Nama Pasien</p>
                <p className="text-sm font-medium text-gray-900">{patient.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">No RM</p>
                <p className="text-sm font-medium text-gray-900">{patient.medical_record_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Usia/Jenis Kelamin</p>
                <p className="text-sm font-medium text-gray-900">{patient.age} th / {patient.gender === "male" ? "L" : "P"}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Status Kehamilan</p>
                <p className="text-sm font-medium text-gray-900">
                  {patient.pregnancy_status === "pregnant" && "🤰 Hamil"}
                  {patient.pregnancy_status === "not_pregnant" && "Tidak Hamil"}
                  {patient.pregnancy_status === "unknown" && "Tidak Diketahui"}
                </p>
              </div>
            </div>

            {/* Allergies Warning */}
            {patient.allergies && patient.allergies.length > 0 && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div>
                    <h4 className="text-sm font-medium text-red-900">Alergi Pasien</h4>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {patient.allergies.map((allergy, idx) => (
                        <span key={idx} className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs">
                          {allergy}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="flex items-center space-x-3">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="text-sm font-medium text-yellow-900">Pasien Belum Dipilih</h3>
                <p className="text-sm text-yellow-700 mt-1">
                  Silakan pilih pasien terlebih dahulu atau akses halaman ini dari halaman konsultasi pasien.
                </p>
                <button
                  type="button"
                  onClick={() => router.push("/app/patients")}
                  className="mt-3 px-4 py-2 bg-yellow-600 text-white text-sm rounded hover:bg-yellow-700"
                >
                  Pilih Pasien
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Clinical Information */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Informasi Klinis</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Diagnosa Kerja *</label>
              <input
                type="text"
                required
                value={clinicalInfo.diagnosis}
                onChange={(e) => setClinicalInfo({ ...clinicalInfo, diagnosis: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Masukkan diagnosa kerja"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Gejala/Keluhan</label>
              <input
                type="text"
                value={clinicalInfo.symptoms}
                onChange={(e) => setClinicalInfo({ ...clinicalInfo, symptoms: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Masukkan gejala atau keluhan pasien"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Indikasi Klinis</label>
              <textarea
                value={clinicalInfo.clinical_indication}
                onChange={(e) => setClinicalInfo({ ...clinicalInfo, clinical_indication: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Jelaskan indikasi klinis untuk pemeriksaan ini"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Prioritas</label>
              <select
                value={clinicalInfo.priority}
                onChange={(e) => setClinicalInfo({ ...clinicalInfo, priority: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="routine">Routine</option>
                <option value="urgent">Urgent</option>
                <option value="stat">Stat (Segera)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <input
                  type="checkbox"
                  checked={clinicalInfo.fasting_required}
                  onChange={(e) => setClinicalInfo({ ...clinicalInfo, fasting_required: e.target.checked })}
                  className="mr-2"
                />
                Pasien Perlu Puasa
              </label>
              <p className="text-xs text-gray-500 mt-1">Centang jika pasien perlu puasa sebelum pemeriksaan</p>
            </div>
          </div>
        </div>

        {/* Lab Tests Selection */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Pilih Pemeriksaan</h2>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Semua Kategori</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {filteredTests.map((test) => {
              const isSelected = selectedTests.has(test.id);
              const needsFasting = test.fasting_required;

              return (
                <div
                  key={test.id}
                  className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                    isSelected ? "border-indigo-500 bg-indigo-50" : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() => toggleTestSelection(test.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleTestSelection(test.id)}
                          className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                        />
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <h3 className="font-medium text-gray-900">{test.test_name}</h3>
                            {needsFasting && (
                              <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 rounded text-xs">
                                Perlu Puasa
                              </span>
                            )}
                            {test.is_bpjs_covered && (
                              <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs">
                                BPJS
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-500 mt-1">
                            {test.test_code} • {test.sample_type} • {test.container}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            TAT: {test.turnaround_time}
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="text-right ml-4">
                      <p className="text-sm font-medium text-gray-900">{formatCurrency(test.price)}</p>
                      {test.is_bpjs_covered && test.bpjs_tariff && (
                        <p className="text-xs text-green-600">
                          BPJS: {formatCurrency(test.bpjs_tariff)}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Additional Notes Field */}
                  {isSelected && (
                    <div className="mt-3 pl-7">
                      <input
                        type="text"
                        placeholder="Catatan tambahan untuk pemeriksaan ini (opsional)"
                        value={testDetails.get(test.id) || ""}
                        onChange={(e) => handleTestDetailChange(test.id, e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {filteredTests.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Tidak ada pemeriksaan yang cocok dengan filter
            </div>
          )}
        </div>

        {/* Order Summary */}
        {selectedTests.size > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Ringkasan Pesanan</h2>
            <div className="space-y-3">
              {selectedTestsList.map((test) => (
                <div key={test.id} className="flex justify-between items-center py-2 border-b">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{test.test_name}</p>
                    <p className="text-xs text-gray-500">{test.test_code}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">{formatCurrency(test.price)}</p>
                    {test.is_bpjs_covered && (
                      <p className="text-xs text-green-600">Covered BPJS</p>
                    )}
                  </div>
                </div>
              ))}

              <div className="pt-4 border-t">
                <div className="flex justify-between items-center text-lg font-bold">
                  <span>Total</span>
                  <span className="text-indigo-600">{formatCurrency(totalCost)}</span>
                </div>
                {totalBPJS > 0 && (
                  <div className="flex justify-between items-center text-sm mt-2">
                    <span className="text-gray-600">Total BPJS</span>
                    <span className="text-green-600">{formatCurrency(totalBPJS)}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Fasting Warning */}
            {selectedTestsList.some(t => t.fasting_required) && (
              <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <svg className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <h4 className="text-sm font-medium text-yellow-900">Instruksi Puasa</h4>
                    <p className="text-sm text-yellow-700 mt-1">
                      Beberapa pemeriksaan yang dipilih memerlukan puasa. Informasikan kepada pasien untuk puasa minimal 8-10 jam sebelum pengambilan sampel.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Batal
          </button>
          <button
            type="submit"
            disabled={submitting || selectedTests.size === 0 || !patient}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {submitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Memproses...</span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Buat Pesanan</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
