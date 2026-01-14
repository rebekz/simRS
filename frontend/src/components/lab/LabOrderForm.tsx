"use client";

import React, { useState, useEffect } from 'react';

// Types
interface PatientInfo {
  patient_id: number;
  medical_record_number: string;
  full_name: string;
  age?: number;
  gender: 'male' | 'female';
  blood_type?: string;
  allergies?: string[];
}

interface LabTest {
  id: number;
  code: string;
  name: string;
  name_id?: string;
  category: string;
  specimen_type: string;
  fasting_required: boolean;
  preparation_instructions?: string;
  tat_hours?: number;
  price?: number;
  bpjs_code?: string;
}

interface LabOrderItem {
  test_id: number;
  test_code: string;
  test_name: string;
  specimen_type: string;
  priority: 'routine' | 'urgent' | 'stat';
  clinical_indication: string;
  fasting_required: boolean;
}

interface LabOrderFormProps {
  patientId: number;
  encounterId: number;
  patientInfo?: PatientInfo;
  onSubmit?: (orderId: number) => void;
  onCancel?: () => void;
}

const SPECIMEN_TYPES = [
  { value: 'blood', label: 'Darah' },
  { value: 'urine', label: 'Urin' },
  { value: 'swab', label: 'Swab' },
  { value: 'tissue', label: 'Jaringan' },
  { value: 'fluid', label: 'Cairan Tubuh' },
  { value: 'stool', label: 'Feses' },
  { value: 'sputum', label: 'Sputum' },
  { value: 'other', label: 'Lainnya' },
];

const CATEGORY_OPTIONS = [
  'Hematologi',
  'Kimia Klinis',
  'Imunologi',
  'Mikrobiologi',
  'Urinalisis',
  'Parasitologi',
  'Hormon',
  'Coagulation',
  'Lainnya'
];

export default function LabOrderForm({
  patientId,
  encounterId,
  patientInfo,
  onSubmit,
  onCancel
}: LabOrderFormProps) {
  const [selectedTests, setSelectedTests] = useState<LabOrderItem[]>([]);
  const [clinicalIndication, setClinicalIndication] = useState('');
  const [priority, setPriority] = useState<'routine' | 'urgent' | 'stat'>('routine');
  const [notes, setNotes] = useState('');

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<LabTest[]>([]);
  const [searching, setSearching] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  // UI state
  const [submitting, setSubmitting] = useState(false);
  const [loadingPatient, setLoadingPatient] = useState(!patientInfo);
  const [currentPatientInfo, setCurrentPatientInfo] = useState<PatientInfo | undefined>(patientInfo);
  const [showCatalog, setShowCatalog] = useState(false);

  // Load patient info
  useEffect(() => {
    if (!patientInfo) {
      fetchPatientInfo();
    }
  }, [patientId, patientInfo]);

  // Search tests
  useEffect(() => {
    const searchTests = async () => {
      if (searchQuery.length < 2 && !selectedCategory) {
        setSearchResults([]);
        return;
      }

      setSearching(true);
      try {
        const params = new URLSearchParams();
        if (searchQuery) params.append('query', searchQuery);
        if (selectedCategory) params.append('category', selectedCategory);
        params.append('page_size', '50');

        const response = await fetch(`/api/v1/lab/tests/catalog?${params}`);
        const data = await response.json();
        setSearchResults(data.results || []);
      } catch (error) {
        console.error('Test search failed:', error);
      } finally {
        setSearching(false);
      }
    };

    const debounceTimer = setTimeout(searchTests, 300);
    return () => clearTimeout(debounceTimer);
  }, [searchQuery, selectedCategory]);

  const fetchPatientInfo = async () => {
    setLoadingPatient(true);
    try {
      const response = await fetch(`/api/v1/patients/${patientId}/summary`);
      if (response.ok) {
        const data = await response.json();
        setCurrentPatientInfo(data);
      }
    } catch (error) {
      console.error('Failed to fetch patient info:', error);
    } finally {
      setLoadingPatient(false);
    }
  };

  function handleAddTest(test: LabTest) {
    const existingIndex = selectedTests.findIndex(t => t.test_id === test.id);

    if (existingIndex >= 0) {
      // Test already added
      return;
    }

    const newOrderItem: LabOrderItem = {
      test_id: test.id,
      test_code: test.code,
      test_name: test.name_id || test.name,
      specimen_type: test.specimen_type,
      priority,
      clinical_indication: clinicalIndication,
      fasting_required: test.fasting_required,
    };

    setSelectedTests([...selectedTests, newOrderItem]);
    setShowCatalog(false);
    setSearchQuery('');
  };

  function handleRemoveTest(index: number) {
    setSelectedTests(selectedTests.filter((_, i) => i !== index));
  }

  function handleUpdateTestPriority(index: number, newPriority: 'routine' | 'urgent' | 'stat') {
    const updated = [...selectedTests];
    updated[index].priority = newPriority;
    setSelectedTests(updated);
  }

  function handleUpdateSpecimen(index: number, specimenType: string) {
    const updated = [...selectedTests];
    updated[index].specimen_type = specimenType;
    setSelectedTests(updated);
  }

  async function handleSubmit() {
    if (selectedTests.length === 0) {
      alert('Harap pilih minimal satu pemeriksaan laboratorium');
      return;
    }

    if (!clinicalIndication.trim()) {
      alert('Harap isi indikasi klinis');
      return;
    }

    setSubmitting(true);
    try {
      const response = await fetch('/api/v1/lab/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: patientId,
          encounter_id: encounterId,
          tests: selectedTests,
          clinical_indication: clinicalIndication,
          priority,
          notes,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Gagal membuat pesanan laboratorium');
      }

      const order = await response.json();
      onSubmit?.(order.id);
    } catch (error) {
      console.error('Submit failed:', error);
      alert(error instanceof Error ? error.message : 'Gagal membuat pesanan laboratorium');
    } finally {
      setSubmitting(false);
    }
  }

  const hasFastingTest = selectedTests.some(t => t.fasting_required);
  const totalPrice = searchResults
    .filter(r => selectedTests.some(s => s.test_id === r.id))
    .reduce((sum, t) => sum + (t.price || 0), 0);

  if (loadingPatient) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Pemeriksaan Laboratorium</h2>

      {/* Patient Info */}
      {currentPatientInfo && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">Informasi Pasien</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">No. RM:</span>
              <p className="font-medium text-gray-900">{currentPatientInfo.medical_record_number}</p>
            </div>
            <div>
              <span className="text-gray-600">Nama:</span>
              <p className="font-medium text-gray-900">{currentPatientInfo.full_name}</p>
            </div>
            <div>
              <span className="text-gray-600">Usia:</span>
              <p className="font-medium text-gray-900">{currentPatientInfo.age} tahun</p>
            </div>
            <div>
              <span className="text-gray-600">Jenis Kelamin:</span>
              <p className="font-medium text-gray-900">
                {currentPatientInfo.gender === 'male' ? 'Laki-laki' : 'Perempuan'}
              </p>
            </div>
          </div>
          {currentPatientInfo.allergies && currentPatientInfo.allergies.length > 0 && (
            <div className="mt-3 pt-3 border-t border-blue-200">
              <span className="text-gray-600 text-sm">Alergi:</span>
              <div className="flex flex-wrap gap-2 mt-1">
                {currentPatientInfo.allergies.map((allergy, idx) => (
                  <span key={idx} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded">
                    {allergy}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Test Catalog */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Pemeriksaan yang Diminta</h3>
          <button
            onClick={() => setShowCatalog(!showCatalog)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            {showCatalog ? 'Tutup Katalog' : '+ Tambah Pemeriksaan'}
          </button>
        </div>

        {showCatalog && (
          <div className="border border-gray-200 rounded-lg p-4 mb-4">
            {/* Category Filter */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Kategori
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full md:w-64 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Semua Kategori</option>
                {CATEGORY_OPTIONS.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            {/* Search */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cari Pemeriksaan
              </label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Ketik nama pemeriksaan atau kode..."
              />
            </div>

            {/* Search Results */}
            {searching && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            )}

            {!searching && searchResults.length > 0 && (
              <div className="max-h-64 overflow-y-auto space-y-2">
                {searchResults.map((test) => {
                  const isAdded = selectedTests.some(t => t.test_id === test.id);
                  return (
                    <div
                      key={test.id}
                      className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 flex justify-between items-start"
                    >
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{test.name_id || test.name}</div>
                        <div className="text-sm text-gray-600">{test.code} - {test.category}</div>
                        <div className="text-xs text-gray-500 mt-1">
                          Spesimen: {test.specimen_type}
                          {test.fasting_required && (
                            <span className="ml-2 text-orange-600">• Puasa required</span>
                          )}
                          {test.tat_hours && (
                            <span className="ml-2">• {test.tat_hours}j</span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {test.price && (
                          <span className="text-sm font-medium text-gray-700">
                            Rp {test.price.toLocaleString('id-ID')}
                          </span>
                        )}
                        <button
                          onClick={() => handleAddTest(test)}
                          disabled={isAdded}
                          className={`px-3 py-1 rounded text-sm ${
                            isAdded
                              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                              : 'bg-green-600 text-white hover:bg-green-700'
                          }`}
                        >
                          {isAdded ? 'Ditambahkan' : 'Tambah'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {!searching && searchQuery.length >= 2 && searchResults.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                Tidak ada pemeriksaan ditemukan
              </div>
            )}
          </div>
        )}

        {/* Selected Tests */}
        {selectedTests.length > 0 ? (
          <div className="space-y-3">
            {selectedTests.map((item, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 relative">
                <button
                  onClick={() => handleRemoveTest(index)}
                  className="absolute top-2 right-2 text-red-600 hover:text-red-800"
                >
                  ✕
                </button>

                <div className="font-semibold text-gray-900 mb-3">{item.test_name}</div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Prioritas
                    </label>
                    <select
                      value={item.priority}
                      onChange={(e) => handleUpdateTestPriority(index, e.target.value as any)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    >
                      <option value="routine">Rutin</option>
                      <option value="urgent">Segera</option>
                      <option value="stat">Stat</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Jenis Spesimen
                    </label>
                    <select
                      value={item.specimen_type}
                      onChange={(e) => handleUpdateSpecimen(index, e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    >
                      {SPECIMEN_TYPES.map(type => (
                        <option key={type.value} value={type.value}>{type.label}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {item.fasting_required && (
                  <div className="mt-3 p-2 bg-orange-50 border border-orange-200 rounded text-sm text-orange-800">
                    ⚠️ Pemeriksaan ini memerlukan puasa minimal 8-12 jam
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500 border-2 border-dashed border-gray-300 rounded-lg">
            Belum ada pemeriksaan yang dipilih
          </div>
        )}
      </div>

      {/* Clinical Information */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Indikasi Klinis <span className="text-red-500">*</span>
        </label>
        <textarea
          value={clinicalIndication}
          onChange={(e) => setClinicalIndication(e.target.value)}
          rows={3}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Jelaskan indikasi klinis, diagnosis kerja, atau tujuan pemeriksaan..."
        />
      </div>

      {/* Priority */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Prioritas Pesanan
        </label>
        <div className="flex gap-4">
          <label className="flex items-center">
            <input
              type="radio"
              value="routine"
              checked={priority === 'routine'}
              onChange={(e) => setPriority(e.target.value as any)}
              className="mr-2"
            />
            Rutin
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="urgent"
              checked={priority === 'urgent'}
              onChange={(e) => setPriority(e.target.value as any)}
              className="mr-2"
            />
            Segera
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="stat"
              checked={priority === 'stat'}
              onChange={(e) => setPriority(e.target.value as any)}
              className="mr-2"
            />
            Stat (Khusus)
          </label>
        </div>
      </div>

      {/* Fasting Alert */}
      {hasFastingTest && (
        <div className="mb-6 p-4 bg-orange-50 border-l-4 border-orange-400 rounded">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-orange-400 text-xl">⚠️</span>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-orange-800">
                Persiapan Puasa Diperlukan
              </h4>
              <div className="mt-1 text-sm text-orange-700">
                Beberapa pemeriksaan memerlukan puasa 8-12 jam. Pastikan pasien sudah diinformasikan.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Additional Notes */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Catatan Tambahan
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Catatan tambahan untuk laboratorium..."
        />
      </div>

      {/* Price Estimate */}
      {totalPrice > 0 && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex justify-between items-center">
            <span className="font-medium text-green-900">Perkiraan Total Biaya:</span>
            <span className="text-lg font-bold text-green-900">
              Rp {totalPrice.toLocaleString('id-ID')}
            </span>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-end gap-4">
        {onCancel && (
          <button
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Batal
          </button>
        )}
        <button
          onClick={handleSubmit}
          disabled={submitting || selectedTests.length === 0}
          className={`px-6 py-2 rounded-lg transition-colors ${
            submitting || selectedTests.length === 0
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700 text-white'
          }`}
        >
          {submitting ? 'Menyimpan...' : 'Buat Pesanan'}
        </button>
      </div>
    </div>
  );
}
