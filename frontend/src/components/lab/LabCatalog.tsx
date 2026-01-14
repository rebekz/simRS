"use client";

import React, { useState, useEffect } from 'react';

// Types
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
  description?: string;
}

interface LabCatalogProps {
  onTestSelect?: (test: LabTest) => void;
  selectedTestIds?: number[];
  categoryFilter?: string;
  maxResults?: number;
}

const CATEGORIES = [
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

export default function LabCatalog({
  onTestSelect,
  selectedTestIds = [],
  categoryFilter: initialCategory = '',
  maxResults = 50
}: LabCatalogProps) {
  const [tests, setTests] = useState<LabTest[]>([]);
  const [filteredTests, setFilteredTests] = useState<LabTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(initialCategory);
  const [selectedTest, setSelectedTest] = useState<LabTest | null>(null);

  // Load catalog
  useEffect(() => {
    fetchCatalog();
  }, []);

  // Filter tests
  useEffect(() => {
    let filtered = tests;

    // Category filter
    if (selectedCategory) {
      filtered = filtered.filter(t => t.category === selectedCategory);
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(t =>
        t.name.toLowerCase().includes(query) ||
        t.name_id?.toLowerCase().includes(query) ||
        t.code.toLowerCase().includes(query)
      );
    }

    setFilteredTests(filtered.slice(0, maxResults));
  }, [tests, selectedCategory, searchQuery, maxResults]);

  const fetchCatalog = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/lab/tests/catalog?page_size=200');
      const data = await response.json();
      setTests(data.results || []);
    } catch (error) {
      console.error('Failed to fetch lab catalog:', error);
    } finally {
      setLoading(false);
    }
  };

  function handleTestClick(test: LabTest) {
    setSelectedTest(test);
  }

  function handleAddTest() {
    if (selectedTest && onTestSelect) {
      onTestSelect(selectedTest);
      setSelectedTest(null);
    }
  }

  function isTestSelected(testId: number): boolean {
    return selectedTestIds.includes(testId);
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Katalog Pemeriksaan Laboratorium</h2>

      {/* Search and Filter */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Cari Pemeriksaan
          </label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Ketik nama, kode, atau kategori..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Kategori
          </label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Semua Kategori</option>
            {CATEGORIES.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )}

      {/* Test Grid */}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTests.map((test) => {
            const isSelected = isTestSelected(test.id);
            const isCurrentlySelected = selectedTest?.id === test.id;

            return (
              <div
                key={test.id}
                onClick={() => handleTestClick(test)}
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
                      {test.name_id || test.name}
                    </div>
                    <div className="text-sm text-gray-600">{test.code}</div>
                  </div>
                  {isSelected && (
                    <span className="ml-2 px-2 py-1 bg-green-600 text-white text-xs rounded">
                      Ditambahkan
                    </span>
                  )}
                </div>

                <div className="space-y-1 text-sm">
                  <div className="text-gray-600">
                    <span className="font-medium">Kategori:</span> {test.category}
                  </div>
                  <div className="text-gray-600">
                    <span className="font-medium">Spesimen:</span> {test.specimen_type}
                  </div>

                  {test.tat_hours && (
                    <div className="text-gray-600">
                      <span className="font-medium">Waktu:</span> {test.tat_hours} jam
                    </div>
                  )}

                  {test.price && (
                    <div className="font-semibold text-gray-900">
                      Rp {test.price.toLocaleString('id-ID')}
                    </div>
                  )}
                </div>

                {test.fasting_required && (
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <span className="inline-flex items-center px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">
                      ⚠️ Puasa Required
                    </span>
                  </div>
                )}

                {test.bpjs_code && (
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                      BPJS: {test.bpjs_code}
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* No Results */}
      {!loading && filteredTests.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="mt-2">Tidak ada pemeriksaan ditemukan</p>
          <p className="text-sm">Coba ubah kata kunci pencarian atau filter kategori</p>
        </div>
      )}

      {/* Test Detail Modal */}
      {selectedTest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-gray-900">
                  {selectedTest.name_id || selectedTest.name}
                </h3>
                <button
                  onClick={() => setSelectedTest(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Kode:</span>
                    <p className="text-gray-900">{selectedTest.code}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Kategori:</span>
                    <p className="text-gray-900">{selectedTest.category}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Spesimen:</span>
                    <p className="text-gray-900">{selectedTest.specimen_type}</p>
                  </div>
                  {selectedTest.tat_hours && (
                    <div>
                      <span className="font-medium text-gray-700">Waktu Pengerjaan:</span>
                      <p className="text-gray-900">{selectedTest.tat_hours} jam</p>
                    </div>
                  )}
                </div>

                {selectedTest.description && (
                  <div>
                    <span className="font-medium text-gray-700">Deskripsi:</span>
                    <p className="text-gray-900 mt-1">{selectedTest.description}</p>
                  </div>
                )}

                {selectedTest.preparation_instructions && (
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                    <span className="font-medium text-yellow-900">Instruksi Persiapan:</span>
                    <p className="text-yellow-900 mt-1 text-sm">
                      {selectedTest.preparation_instructions}
                    </p>
                  </div>
                )}

                {selectedTest.fasting_required && (
                  <div className="p-3 bg-orange-50 border border-orange-200 rounded">
                    <div className="flex items-start">
                      <span className="text-orange-400 text-xl mr-2">⚠️</span>
                      <div>
                        <span className="font-medium text-orange-900">Puasa Diperlukan</span>
                        <p className="text-orange-900 mt-1 text-sm">
                          Pasien harus puasa minimal 8-12 jam sebelum pengambilan spesimen.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {selectedTest.price && (
                  <div className="p-4 bg-green-50 border border-green-200 rounded">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-green-900">Biaya:</span>
                      <span className="text-xl font-bold text-green-900">
                        Rp {selectedTest.price.toLocaleString('id-ID')}
                      </span>
                    </div>
                  </div>
                )}

                {selectedTest.bpjs_code && (
                  <div className="flex items-center text-sm">
                    <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-green-700 font-medium">
                      Covered by BPJS ({selectedTest.bpjs_code})
                    </span>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end gap-3">
                <button
                  onClick={() => setSelectedTest(null)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Tutup
                </button>
                {!isTestSelected(selectedTest.id) && onTestSelect && (
                  <button
                    onClick={handleAddTest}
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
