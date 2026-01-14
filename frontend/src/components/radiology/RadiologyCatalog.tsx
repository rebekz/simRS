"use client";

import React, { useState, useEffect } from 'react';

// Types
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
  description?: string;
}

interface RadiologyCatalogProps {
  onProcedureSelect?: (procedure: RadiologyProcedure) => void;
  selectedProcedureIds?: number[];
  modalityFilter?: string;
  bodyPartFilter?: string;
  maxResults?: number;
}

const MODALITIES = [
  { value: 'XRAY', label: 'X-Ray', icon: '📷' },
  { value: 'CT', label: 'CT Scan', icon: '🔬' },
  { value: 'MRI', label: 'MRI', icon: '🧲' },
  { value: 'USG', label: 'USG', icon: '📺' },
  { value: 'MAMMO', label: 'Mammografi', icon: '🔍' },
  { value: 'FLUORO', label: 'Fluoroskopi', icon: '🎥' },
  { value: 'BONE_DENSITY', label: 'Densitometri Tulang', icon: '🦴' },
  { value: 'PET_CT', label: 'PET-CT', icon: '⚛️' },
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

export default function RadiologyCatalog({
  onProcedureSelect,
  selectedProcedureIds = [],
  modalityFilter: initialModality = '',
  bodyPartFilter: initialBodyPart = '',
  maxResults = 50
}: RadiologyCatalogProps) {
  const [procedures, setProcedures] = useState<RadiologyProcedure[]>([]);
  const [filteredProcedures, setFilteredProcedures] = useState<RadiologyProcedure[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedModality, setSelectedModality] = useState(initialModality);
  const [selectedBodyPart, setSelectedBodyPart] = useState(initialBodyPart);
  const [selectedProcedure, setSelectedProcedure] = useState<RadiologyProcedure | null>(null);

  // Load catalog
  useEffect(() => {
    fetchCatalog();
  }, []);

  // Filter procedures
  useEffect(() => {
    let filtered = procedures;

    // Modality filter
    if (selectedModality) {
      filtered = filtered.filter(p => p.modality === selectedModality);
    }

    // Body part filter
    if (selectedBodyPart) {
      filtered = filtered.filter(p => p.body_part === selectedBodyPart);
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(query) ||
        p.name_id?.toLowerCase().includes(query) ||
        p.code.toLowerCase().includes(query) ||
        p.body_part.toLowerCase().includes(query)
      );
    }

    setFilteredProcedures(filtered.slice(0, maxResults));
  }, [procedures, selectedModality, selectedBodyPart, searchQuery, maxResults]);

  const fetchCatalog = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/radiology/procedures/catalog?page_size=200');
      const data = await response.json();
      setProcedures(data.results || []);
    } catch (error) {
      console.error('Failed to fetch radiology catalog:', error);
    } finally {
      setLoading(false);
    }
  };

  function handleProcedureClick(procedure: RadiologyProcedure) {
    setSelectedProcedure(procedure);
  }

  function handleAddProcedure() {
    if (selectedProcedure && onProcedureSelect) {
      onProcedureSelect(selectedProcedure);
      setSelectedProcedure(null);
    }
  }

  function isProcedureSelected(procedureId: number): boolean {
    return selectedProcedureIds.includes(procedureId);
  }

  function getModalityInfo(modality: string) {
    return MODALITIES.find(m => m.value === modality) || { label: modality, icon: '🏥' };
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Katalog Pemeriksaan Radiologi</h2>

      {/* Search and Filter */}
      <div className="mb-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Cari Prosedur
          </label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Ketik nama prosedur, kode, atau bagian tubuh..."
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Modalitas
            </label>
            <select
              value={selectedModality}
              onChange={(e) => setSelectedModality(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Semua Modalitas</option>
              {MODALITIES.map(mod => (
                <option key={mod.value} value={mod.value}>
                  {mod.icon} {mod.label}
                </option>
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
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Semua Bagian Tubuh</option>
              {BODY_PARTS.map(part => (
                <option key={part} value={part}>{part}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Modality Quick Filter */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Filter Cepat Modalitas
        </label>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedModality('')}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              !selectedModality
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Semua
          </button>
          {MODALITIES.map(mod => (
            <button
              key={mod.value}
              onClick={() => setSelectedModality(selectedModality === mod.value ? '' : mod.value)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedModality === mod.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {mod.icon} {mod.label}
            </button>
          ))}
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )}

      {/* Procedure Grid */}
      {!loading && (
        <div className="space-y-4">
          {/* Group by Modality */}
          {MODALITIES.filter(mod => !selectedModality || mod.value === selectedModality).map(mod => {
            const modalityProcedures = filteredProcedures.filter(p => p.modality === mod.value);

            if (modalityProcedures.length === 0) return null;

            return (
              <div key={mod.value}>
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                  <span className="mr-2">{mod.icon}</span>
                  {mod.label}
                  <span className="ml-2 text-sm font-normal text-gray-500">
                    ({modalityProcedures.length})
                  </span>
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {modalityProcedures.map((procedure) => {
                    const isSelected = isProcedureSelected(procedure.id);
                    const isCurrentlySelected = selectedProcedure?.id === procedure.id;

                    return (
                      <div
                        key={procedure.id}
                        onClick={() => handleProcedureClick(procedure)}
                        className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                          isCurrentlySelected
                            ? 'border-blue-500 bg-blue-50'
                            : isSelected
                            ? 'border-green-500 bg-green-50'
                            : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                        }`}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex-1">
                            <div className="font-semibold text-gray-900">
                              {procedure.name_id || procedure.name}
                            </div>
                            <div className="text-sm text-gray-600">{procedure.code}</div>
                          </div>
                          {isSelected && (
                            <span className="ml-2 px-2 py-1 bg-green-600 text-white text-xs rounded">
                              Ditambahkan
                            </span>
                          )}
                        </div>

                        <div className="space-y-1 text-sm">
                          <div className="text-gray-600">
                            <span className="font-medium">Bagian:</span> {procedure.body_part}
                          </div>

                          {procedure.tat_hours && (
                            <div className="text-gray-600">
                              <span className="font-medium">Waktu:</span> {procedure.tat_hours} jam
                            </div>
                          )}

                          {procedure.price && (
                            <div className="font-semibold text-gray-900">
                              Rp {procedure.price.toLocaleString('id-ID')}
                            </div>
                          )}
                        </div>

                        <div className="mt-2 flex flex-wrap gap-1">
                          {procedure.contrast_required && (
                            <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                              💉 Kontras
                            </span>
                          )}
                        </div>

                        {procedure.bpjs_code && (
                          <div className="mt-2">
                            <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                              BPJS: {procedure.bpjs_code}
                            </span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* No Results */}
      {!loading && filteredProcedures.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="mt-2">Tidak ada prosedur ditemukan</p>
          <p className="text-sm">Coba ubah kata kunci pencarian atau filter</p>
        </div>
      )}

      {/* Procedure Detail Modal */}
      {selectedProcedure && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">
                      {getModalityInfo(selectedProcedure.modality).icon}
                    </span>
                    <h3 className="text-xl font-bold text-gray-900">
                      {selectedProcedure.name_id || selectedProcedure.name}
                    </h3>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{selectedProcedure.code}</p>
                </div>
                <button
                  onClick={() => setSelectedProcedure(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Modalitas:</span>
                    <p className="text-gray-900">
                      {getModalityInfo(selectedProcedure.modality).label}
                    </p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Bagian Tubuh:</span>
                    <p className="text-gray-900">{selectedProcedure.body_part}</p>
                  </div>
                  {selectedProcedure.tat_hours && (
                    <div>
                      <span className="font-medium text-gray-700">Waktu Pengerjaan:</span>
                      <p className="text-gray-900">{selectedProcedure.tat_hours} jam</p>
                    </div>
                  )}
                </div>

                {selectedProcedure.description && (
                  <div>
                    <span className="font-medium text-gray-700">Deskripsi:</span>
                    <p className="text-gray-900 mt-1">{selectedProcedure.description}</p>
                  </div>
                )}

                {selectedProcedure.preparation_instructions && (
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                    <span className="font-medium text-yellow-900">Instruksi Persiapan:</span>
                    <p className="text-yellow-900 mt-1 text-sm">
                      {selectedProcedure.preparation_instructions}
                    </p>
                  </div>
                )}

                {selectedProcedure.contrast_required && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded">
                    <div className="flex items-start">
                      <span className="text-blue-400 text-xl mr-2">💉</span>
                      <div>
                        <span className="font-medium text-blue-900">Kontras Diperlukan</span>
                        <p className="text-blue-900 mt-1 text-sm">
                          Pemeriksaan ini memerlukan injeksi kontras. Pastikan fungsi ginjal normal.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {selectedProcedure.price && (
                  <div className="p-4 bg-green-50 border border-green-200 rounded">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-green-900">Biaya:</span>
                      <span className="text-xl font-bold text-green-900">
                        Rp {selectedProcedure.price.toLocaleString('id-ID')}
                      </span>
                    </div>
                  </div>
                )}

                {selectedProcedure.bpjs_code && (
                  <div className="flex items-center text-sm">
                    <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-green-700 font-medium">
                      Covered by BPJS ({selectedProcedure.bpjs_code})
                    </span>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end gap-3">
                <button
                  onClick={() => setSelectedProcedure(null)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Tutup
                </button>
                {!isProcedureSelected(selectedProcedure.id) && onProcedureSelect && (
                  <button
                    onClick={handleAddProcedure}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Tambah ke Pesanan
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
