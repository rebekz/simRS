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
  pregnancy_status?: 'unknown' | 'not_pregnant' | 'possibly_pregnant' | 'pregnant';
  implants?: string[];
}

interface RadiologyProcedure {
  id: number;
  code: string;
  name: string;
  name_id?: string;
  modality: string;
  body_part: string;
  contrast_required: boolean;
  preparation_instructions?: string;
  tat_hours?: number;
  price?: number;
  bpjs_code?: string;
}

interface RadiologyOrderItem {
  procedure_id: number;
  procedure_code: string;
  procedure_name: string;
  modality: string;
  body_part: string;
  priority: 'routine' | 'urgent' | 'stat';
  clinical_indication: string;
  contrast_required: boolean;
}

interface SafetyScreening {
  is_pregnant: boolean;
  pregnancy_trimester?: number;
  has_implants: boolean;
  implant_details?: string;
  has_contrast_allergy: boolean;
  allergy_details?: string;
  kidney_disease: boolean;
  claustrophobia: boolean;
}

interface RadiologyOrderFormProps {
  patientId: number;
  encounterId: number;
  patientInfo?: PatientInfo;
  onSubmit?: (orderId: number) => void;
  onCancel?: () => void;
}

const MODALITIES = [
  { value: 'XRAY', label: 'X-Ray' },
  { value: 'CT', label: 'CT Scan' },
  { value: 'MRI', label: 'MRI' },
  { value: 'USG', label: 'USG' },
  { value: 'MAMMO', label: 'Mammografi' },
  { value: 'FLUORO', label: 'Fluoroskopi' },
  { value: 'BONE_DENSITY', label: 'Densitometri Tulang' },
  { value: 'PET_CT', label: 'PET-CT' },
];

const BODY_PARTS = [
  'Kepala',
  'Leher',
  'Dada',
  'Perut',
  'Pinggul',
  'Ekstremitas Atas',
  'Ekstremitas Bawah',
  'Tulang Belakang',
  'Lainnya'
];

export default function RadiologyOrderForm({
  patientId,
  encounterId,
  patientInfo,
  onSubmit,
  onCancel
}: RadiologyOrderFormProps) {
  const [selectedProcedures, setSelectedProcedures] = useState<RadiologyOrderItem[]>([]);
  const [clinicalIndication, setClinicalIndication] = useState('');
  const [priority, setPriority] = useState<'routine' | 'urgent' | 'stat'>('routine');
  const [notes, setNotes] = useState('');

  // Safety screening
  const [safetyScreening, setSafetyScreening] = useState<SafetyScreening>({
    is_pregnant: false,
    has_implants: false,
    has_contrast_allergy: false,
    kidney_disease: false,
    claustrophobia: false,
  });

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<RadiologyProcedure[]>([]);
  const [searching, setSearching] = useState(false);
  const [selectedModality, setSelectedModality] = useState('');
  const [selectedBodyPart, setSelectedBodyPart] = useState('');

  // UI state
  const [submitting, setSubmitting] = useState(false);
  const [loadingPatient, setLoadingPatient] = useState(!patientInfo);
  const [currentPatientInfo, setCurrentPatientInfo] = useState<PatientInfo | undefined>(patientInfo);
  const [showCatalog, setShowCatalog] = useState(false);
  const [showSafetyAlert, setShowSafetyAlert] = useState(false);

  // Load patient info
  useEffect(() => {
    if (!patientInfo) {
      fetchPatientInfo();
    }
  }, [patientId, patientInfo]);

  // Search procedures
  useEffect(() => {
    const searchProcedures = async () => {
      if (searchQuery.length < 2 && !selectedModality && !selectedBodyPart) {
        setSearchResults([]);
        return;
      }

      setSearching(true);
      try {
        const params = new URLSearchParams();
        if (searchQuery) params.append('query', searchQuery);
        if (selectedModality) params.append('modality', selectedModality);
        if (selectedBodyPart) params.append('body_part', selectedBodyPart);
        params.append('page_size', '50');

        const response = await fetch(`/api/v1/radiology/procedures/catalog?${params}`);
        const data = await response.json();
        setSearchResults(data.results || []);
      } catch (error) {
        console.error('Procedure search failed:', error);
      } finally {
        setSearching(false);
      }
    };

    const debounceTimer = setTimeout(searchProcedures, 300);
    return () => clearTimeout(debounceTimer);
  }, [searchQuery, selectedModality, selectedBodyPart]);

  // Check safety alerts
  useEffect(() => {
    if (selectedProcedures.length > 0) {
      const needsMRI = selectedProcedures.some(p => p.modality === 'MRI');
      const needsContrast = selectedProcedures.some(p => p.contrast_required);

      if ((needsMRI && safetyScreening.has_implants) ||
          (needsContrast && safetyScreening.has_contrast_allergy) ||
          (needsContrast && safetyScreening.kidney_disease) ||
          safetyScreening.is_pregnant) {
        setShowSafetyAlert(true);
      } else {
        setShowSafetyAlert(false);
      }
    }
  }, [selectedProcedures, safetyScreening]);

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

  function handleAddProcedure(procedure: RadiologyProcedure) {
    const existingIndex = selectedProcedures.findIndex(p => p.procedure_id === procedure.id);

    if (existingIndex >= 0) {
      return;
    }

    const newOrderItem: RadiologyOrderItem = {
      procedure_id: procedure.id,
      procedure_code: procedure.code,
      procedure_name: procedure.name_id || procedure.name,
      modality: procedure.modality,
      body_part: procedure.body_part,
      priority,
      clinical_indication: clinicalIndication,
      contrast_required: procedure.contrast_required,
    };

    setSelectedProcedures([...selectedProcedures, newOrderItem]);
    setShowCatalog(false);
    setSearchQuery('');
  }

  function handleRemoveProcedure(index: number) {
    setSelectedProcedures(selectedProcedures.filter((_, i) => i !== index));
  }

  function handleUpdatePriority(index: number, newPriority: 'routine' | 'urgent' | 'stat') {
    const updated = [...selectedProcedures];
    updated[index].priority = newPriority;
    setSelectedProcedures(updated);
  }

  function handleUpdateContrast(index: number, required: boolean) {
    const updated = [...selectedProcedures];
    updated[index].contrast_required = required;
    setSelectedProcedures(updated);
  }

  async function handleSubmit() {
    if (selectedProcedures.length === 0) {
      alert('Harap pilih minimal satu prosedur radiologi');
      return;
    }

    if (!clinicalIndication.trim()) {
      alert('Harap isi indikasi klinis');
      return;
    }

    if (showSafetyAlert) {
      const confirmed = confirm(
        'Ada peringatan keamanan yang perlu diperhatikan. Lanjutkan dengan pesanan ini?'
      );
      if (!confirmed) return;
    }

    setSubmitting(true);
    try {
      const response = await fetch('/api/v1/radiology/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: patientId,
          encounter_id: encounterId,
          procedures: selectedProcedures,
          clinical_indication: clinicalIndication,
          priority,
          safety_screening: safetyScreening,
          notes,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Gagal membuat pesanan radiologi');
      }

      const order = await response.json();
      onSubmit?.(order.id);
    } catch (error) {
      console.error('Submit failed:', error);
      alert(error instanceof Error ? error.message : 'Gagal membuat pesanan radiologi');
    } finally {
      setSubmitting(false);
    }
  }

  const totalPrice = searchResults
    .filter(r => selectedProcedures.some(s => s.procedure_id === r.id))
    .reduce((sum, p) => sum + (p.price || 0), 0);

  if (loadingPatient) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Pemeriksaan Radiologi</h2>

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

      {/* Safety Screening */}
      <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h3 className="text-sm font-semibold text-yellow-900 mb-3">
          Screning Keamanan Pasien
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={safetyScreening.is_pregnant}
              onChange={(e) => setSafetyScreening({ ...safetyScreening, is_pregnant: e.target.checked })}
              className="mr-2"
            />
            Hamil
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={safetyScreening.has_implants}
              onChange={(e) => setSafetyScreening({ ...safetyScreening, has_implants: e.target.checked })}
              className="mr-2"
            />
            Memiliki Implan (Pace maker, logam, dll)
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={safetyScreening.has_contrast_allergy}
              onChange={(e) => setSafetyScreening({ ...safetyScreening, has_contrast_allergy: e.target.checked })}
              className="mr-2"
            />
            Alergi Kontras
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={safetyScreening.kidney_disease}
              onChange={(e) => setSafetyScreening({ ...safetyScreening, kidney_disease: e.target.checked })}
              className="mr-2"
            />
            Penyakit Ginjal
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={safetyScreening.claustrophobia}
              onChange={(e) => setSafetyScreening({ ...safetyScreening, claustrophobia: e.target.checked })}
              className="mr-2"
            />
            Klaustrofobia (takut ruang sempit)
          </label>
        </div>

        {safetyScreening.is_pregnant && (
          <div className="mt-3">
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Trimester Kehamilan (jika diketahui):
            </label>
            <select
              value={safetyScreening.pregnancy_trimester || ''}
              onChange={(e) => setSafetyScreening({
                ...safetyScreening,
                pregnancy_trimester: parseInt(e.target.value) || undefined
              })}
              className="px-3 py-2 border border-gray-300 rounded text-sm"
            >
              <option value="">Tidak diketahui</option>
              <option value="1">Trimester 1</option>
              <option value="2">Trimester 2</option>
              <option value="3">Trimester 3</option>
            </select>
          </div>
        )}

        {(safetyScreening.has_implants || safetyScreening.has_contrast_allergy) && (
          <div className="mt-3">
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Detail Tambahan:
            </label>
            <input
              type="text"
              value={safetyScreening.implant_details || safetyScreening.allergy_details || ''}
              onChange={(e) => {
                if (safetyScreening.has_implants) {
                  setSafetyScreening({ ...safetyScreening, implant_details: e.target.value });
                } else {
                  setSafetyScreening({ ...safetyScreening, allergy_details: e.target.value });
                }
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
              placeholder="Jelaskan detail tambahan..."
            />
          </div>
        )}
      </div>

      {/* Safety Alert */}
      {showSafetyAlert && (
        <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-400 rounded">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-red-400 text-xl">⚠️</span>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-red-800">
                Peringatan Keamanan
              </h4>
              <div className="mt-1 text-sm text-red-700">
                {safetyScreening.is_pregnant && (
                  <div>• Pasien hamil - konsultasikan dengan radiologist</div>
                )}
                {(safetyScreening.has_implants && selectedProcedures.some(p => p.modality === 'MRI')) && (
                  <div>• Implan terdeteksi - MRI mungkin tidak aman</div>
                )}
                {(safetyScreening.has_contrast_allergy && selectedProcedures.some(p => p.contrast_required)) && (
                  <div>• Alergi kontras - perlu premedikasi</div>
                )}
                {(safetyScreening.kidney_disease && selectedProcedures.some(p => p.contrast_required)) && (
                  <div>• Penyakit ginjal - risiko nephrogenic systemic fibrosis</div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Procedure Catalog */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Prosedur yang Diminta</h3>
          <button
            onClick={() => setShowCatalog(!showCatalog)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            {showCatalog ? 'Tutup Katalog' : '+ Tambah Prosedur'}
          </button>
        </div>

        {showCatalog && (
          <div className="border border-gray-200 rounded-lg p-4 mb-4">
            {/* Filters */}
            <div className="mb-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Modalitas
                </label>
                <select
                  value={selectedModality}
                  onChange={(e) => setSelectedModality(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Semua Modalitas</option>
                  {MODALITIES.map(mod => (
                    <option key={mod.value} value={mod.value}>{mod.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bagian Tubuh
                </label>
                <select
                  value={selectedBodyPart}
                  onChange={(e) => setSelectedBodyPart(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Semua Bagian Tubuh</option>
                  {BODY_PARTS.map(part => (
                    <option key={part} value={part}>{part}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Search */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cari Prosedur
              </label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Ketik nama prosedur atau kode..."
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
                {searchResults.map((procedure) => {
                  const isAdded = selectedProcedures.some(p => p.procedure_id === procedure.id);
                  return (
                    <div
                      key={procedure.id}
                      className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 flex justify-between items-start"
                    >
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{procedure.name_id || procedure.name}</div>
                        <div className="text-sm text-gray-600">
                          {procedure.code} - {procedure.modality} - {procedure.body_part}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {procedure.contrast_required && (
                            <span className="text-blue-600">• Kontras Required</span>
                          )}
                          {procedure.tat_hours && (
                            <span className="ml-2">• {procedure.tat_hours}j</span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {procedure.price && (
                          <span className="text-sm font-medium text-gray-700">
                            Rp {procedure.price.toLocaleString('id-ID')}
                          </span>
                        )}
                        <button
                          onClick={() => handleAddProcedure(procedure)}
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
                Tidak ada prosedur ditemukan
              </div>
            )}
          </div>
        )}

        {/* Selected Procedures */}
        {selectedProcedures.length > 0 ? (
          <div className="space-y-3">
            {selectedProcedures.map((item, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 relative">
                <button
                  onClick={() => handleRemoveProcedure(index)}
                  className="absolute top-2 right-2 text-red-600 hover:text-red-800"
                >
                  ✕
                </button>

                <div className="font-semibold text-gray-900 mb-3">
                  {item.procedure_name}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Prioritas
                    </label>
                    <select
                      value={item.priority}
                      onChange={(e) => handleUpdatePriority(index, e.target.value as any)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    >
                      <option value="routine">Rutin</option>
                      <option value="urgent">Segera</option>
                      <option value="stat">Stat</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Modalitas
                    </label>
                    <input
                      type="text"
                      value={item.modality}
                      readOnly
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-gray-50"
                    />
                  </div>

                  <div className="flex items-center pt-6">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={item.contrast_required}
                        onChange={(e) => handleUpdateContrast(index, e.target.checked)}
                        className="mr-2"
                      />
                      Kontras Diperlukan
                    </label>
                  </div>
                </div>

                <div className="mt-2 text-sm text-gray-600">
                  Bagian Tubuh: {item.body_part}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500 border-2 border-dashed border-gray-300 rounded-lg">
            Belum ada prosedur yang dipilih
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
          placeholder="Catatan tambahan untuk radiologi..."
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
          disabled={submitting || selectedProcedures.length === 0}
          className={`px-6 py-2 rounded-lg transition-colors ${
            submitting || selectedProcedures.length === 0
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
