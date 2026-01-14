"use client";

import React, { useState, useEffect } from 'react';

// Types
interface Drug {
  id: number;
  name: string;
  generic_name: string;
  dosage_form?: string;
  strength?: string;
  bpjs_code?: string;
  is_narcotic: boolean;
  is_antibiotic: boolean;
  stock_available?: number;
}

interface PrescriptionItem {
  drug_id: number;
  drug_name: string;
  generic_name: string;
  dosage: string;
  dose_unit: string;
  frequency: string;
  route: string;
  duration_days?: number;
  quantity?: number;
  indication?: string;
  special_instructions?: string;
  is_prn: boolean;
}

interface DrugInteraction {
  id: number;
  interaction_type: string;
  severity: string;
  drug_1_name: string;
  drug_2_name?: string;
  description: string;
  recommendation: string;
}

type Route = 'oral' | 'intravenous' | 'intramuscular' | 'subcutaneous' | 'topical' | 'inhalation' | 'nasal' | 'ophthalmic' | 'otic' | 'rectal' | 'vaginal' | 'other';

interface PrescriptionWriterProps {
  patientId: number;
  encounterId: number;
  onSubmit?: (prescriptionId: number) => void;
  onCancel?: () => void;
}

const ROUTE_OPTIONS: { value: Route; label: string }[] = [
  { value: 'oral', label: 'Oral' },
  { value: 'intravenous', label: 'Intravena (IV)' },
  { value: 'intramuscular', label: 'Intramuskular (IM)' },
  { value: 'subcutaneous', label: 'Subkutan' },
  { value: 'topical', label: 'Topikal' },
  { value: 'inhalation', label: 'Inhalasi' },
  { value: 'nasal', label: 'Nasal' },
  { value: 'ophthalmic', label: 'Mata' },
  { value: 'otic', label: 'Telinga' },
  { value: 'rectal', label: 'Rektal' },
  { value: 'other', label: 'Lainnya' },
];

const FREQUENCY_OPTIONS = [
  { value: '1x sehari', label: '1x sehari' },
  { value: '2x sehari', label: '2x sehari' },
  { value: '3x sehari', label: '3x sehari' },
  { value: '4x sehari', label: '4x sehari' },
  { value: 'SORE', label: 'Sore (setiap hari)' },
  { value: 'PAGI', label: 'Pagi (setiap hari)' },
  { value: 'MALAM', label: 'Malam (setiap hari)' },
  { value: 'PRN', label: 'Saat perlu (PRN)' },
  { value: 'STAT', label: 'Stat (segera)' },
];

export default function PrescriptionWriter({ patientId, encounterId, onSubmit, onCancel }: PrescriptionWriterProps) {
  const [items, setItems] = useState<PrescriptionItem[]>([createEmptyItem()]);
  const [diagnosis, setDiagnosis] = useState('');
  const [notes, setNotes] = useState('');
  const [priority, setPriority] = useState<'routine' | 'urgent' | 'stat'>('routine');
  const [isDraft, setIsDraft] = useState(false);

  // Drug search state
  const [drugSearchQuery, setDrugSearchQuery] = useState('');
  const [drugSearchResults, setDrugSearchResults] = useState<Drug[]>([]);
  const [searchingDrugs, setSearchingDrugs] = useState(false);
  const [selectedItemIndex, setSelectedItemIndex] = useState<number | null>(null);

  // Interaction checking state
  const [interactions, setInteractions] = useState<DrugInteraction[]>([]);
  const [checkingInteractions, setCheckingInteractions] = useState(false);
  const [canPrescribe, setCanPrescribe] = useState(true);

  // UI state
  const [submitting, setSubmitting] = useState(false);
  const [showDrugSearch, setShowDrugSearch] = useState(false);

  // Search drugs
  useEffect(() => {
    const searchDrugs = async () => {
      if (drugSearchQuery.length < 2) {
        setDrugSearchResults([]);
        return;
      }

      setSearchingDrugs(true);
      try {
        const response = await fetch(
          `/api/v1/prescriptions/drugs/search?query=${encodeURIComponent(drugSearchQuery)}&page_size=20`
        );
        const data = await response.json();
        setDrugSearchResults(data.results || []);
      } catch (error) {
        console.error('Drug search failed:', error);
      } finally {
        setSearchingDrugs(false);
      }
    };

    const debounceTimer = setTimeout(searchDrugs, 300);
    return () => clearTimeout(debounceTimer);
  }, [drugSearchQuery]);

  // Check interactions when items change
  useEffect(() => {
    const checkInteractions = async () => {
      const drugIds = items.filter(item => item.drug_id > 0).map(item => item.drug_id);
      if (drugIds.length < 2) {
        setInteractions([]);
        setCanPrescribe(true);
        return;
      }

      setCheckingInteractions(true);
      try {
        const response = await fetch('/api/v1/prescriptions/check-interactions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ patient_id: patientId, drug_ids: drugIds }),
        });
        const data = await response.json();
        setInteractions(data.interactions || []);
        setCanPrescribe(data.can_prescribe);
      } catch (error) {
        console.error('Interaction check failed:', error);
      } finally {
        setCheckingInteractions(false);
      }
    };

    const timer = setTimeout(checkInteractions, 500);
    return () => clearTimeout(timer);
  }, [items, patientId]);

  function createEmptyItem(): PrescriptionItem {
    return {
      drug_id: 0,
      drug_name: '',
      generic_name: '',
      dosage: '',
      dose_unit: '',
      frequency: '3x sehari',
      route: 'oral',
      duration_days: undefined,
      quantity: undefined,
      indication: '',
      special_instructions: '',
      is_prn: false,
    };
  }

  function handleAddItem() {
    setItems([...items, createEmptyItem()]);
  }

  function handleRemoveItem(index: number) {
    if (items.length === 1) {
      // Keep at least one item, just clear it
      setItems([createEmptyItem()]);
    } else {
      setItems(items.filter((_, i) => i !== index));
    }
  }

  function handleItemChange(index: number, field: keyof PrescriptionItem, value: any) {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    setItems(newItems);
  }

  function handleDrugSelect(drug: Drug, index: number) {
    const newItems = [...items];
    newItems[index] = {
      ...newItems[index],
      drug_id: drug.id,
      drug_name: drug.name,
      generic_name: drug.generic_name,
      dosage: drug.strength || '',
      dose_unit: '',
    };
    setItems(newItems);
    setShowDrugSearch(false);
    setDrugSearchQuery('');
    setSelectedItemIndex(null);
  }

  function getSeverityColor(severity: string): string {
    switch (severity) {
      case 'contraindicated':
        return 'bg-red-100 border-red-500 text-red-800';
      case 'severe':
        return 'bg-red-50 border-red-400 text-red-700';
      case 'moderate':
        return 'bg-yellow-50 border-yellow-400 text-yellow-700';
      case 'mild':
        return 'bg-blue-50 border-blue-400 text-blue-700';
      default:
        return 'bg-gray-50 border-gray-300 text-gray-700';
    }
  }

  async function handleSubmit() {
    // Validate
    const validItems = items.filter(item => item.drug_id > 0);
    if (validItems.length === 0) {
      alert('Harap pilih minimal satu obat');
      return;
    }

    if (!canPrescribe && !isDraft) {
      alert('Tidak dapat membuat resep karena ada interaksi kontraindikasi. Simpan sebagai draf atau hubungi dokter spesialis.');
      return;
    }

    setSubmitting(true);
    try {
      const response = await fetch('/api/v1/prescriptions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: patientId,
          encounter_id: encounterId,
          items: validItems,
          diagnosis,
          notes,
          priority,
          is_draft: isDraft,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Gagal membuat resep');
      }

      const prescription = await response.json();
      onSubmit?.(prescription.id);
    } catch (error) {
      console.error('Submit failed:', error);
      alert(error instanceof Error ? error.message : 'Gagal membuat resep');
    } finally {
      setSubmitting(false);
    }
  }

  const narcoticCount = items.filter(i => i.drug_id > 0 && drugSearchResults.find(d => d.id === i.drug_id)?.is_narcotic).length;
  const antibioticCount = items.filter(i => i.drug_id > 0 && drugSearchResults.find(d => d.id === i.drug_id)?.is_antibiotic).length;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Resep Elektronik</h2>

      {/* Diagnosis */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Diagnosis (ICD-10)
        </label>
        <input
          type="text"
          value={diagnosis}
          onChange={(e) => setDiagnosis(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Contoh: J01 - Akut sinusitis maksilaris"
        />
      </div>

      {/* Priority */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Prioritas
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
              Stat
          </label>
        </div>
      </div>

      {/* Prescription Items */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Obat-obatan</h3>
          <button
            onClick={handleAddItem}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + Tambah Obat
          </button>
        </div>

        {items.map((item, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4 mb-4 relative">
            {items.length > 1 && (
              <button
                onClick={() => handleRemoveItem(index)}
                className="absolute top-2 right-2 text-red-600 hover:text-red-800"
              >
                ✕
              </button>
            )}

            {/* Drug Search */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nama Obat {index + 1}
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={selectedItemIndex === index ? drugSearchQuery : item.drug_name || drugSearchQuery}
                  onFocus={() => {
                    setSelectedItemIndex(index);
                    setShowDrugSearch(true);
                  }}
                  onChange={(e) => setDrugSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ketik nama obat atau generik..."
                />
                {showDrugSearch && selectedItemIndex === index && drugSearchResults.length > 0 && (
                  <div className="absolute z-10 w-full bg-white border border-gray-300 rounded-lg mt-1 max-h-60 overflow-y-auto shadow-lg">
                    {drugSearchResults.map((drug) => (
                      <button
                        key={drug.id}
                        onClick={() => handleDrugSelect(drug, index)}
                        className="w-full px-4 py-3 text-left hover:bg-gray-100 border-b border-gray-200 last:border-b-0"
                      >
                        <div className="font-medium text-gray-900">{drug.name}</div>
                        <div className="text-sm text-gray-600">
                          {drug.generic_name} {drug.strength && `(${drug.strength})`}
                        </div>
                        {drug.is_narcotic && (
                          <span className="inline-block px-2 py-1 bg-red-100 text-red-800 text-xs rounded mt-1">
                            Narkotik
                          </span>
                        )}
                        {drug.is_antibiotic && (
                          <span className="inline-block px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded mt-1 ml-1">
                            Antibiotik
                          </span>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Dosage, Unit, Frequency, Route */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dosis
                </label>
                <input
                  type="text"
                  value={item.dosage}
                  onChange={(e) => handleItemChange(index, 'dosage', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Satuan
                </label>
                <input
                  type="text"
                  value={item.dose_unit}
                  onChange={(e) => handleItemChange(index, 'dose_unit', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="mg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Frekuensi
                </label>
                <select
                  value={item.frequency}
                  onChange={(e) => handleItemChange(index, 'frequency', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  {FREQUENCY_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rute
                </label>
                <select
                  value={item.route}
                  onChange={(e) => handleItemChange(index, 'route', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  {ROUTE_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Duration and Quantity */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Durasi (hari)
                </label>
                <input
                  type="number"
                  value={item.duration_days || ''}
                  onChange={(e) => handleItemChange(index, 'duration_days', parseInt(e.target.value) || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="7"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Jumlah
                </label>
                <input
                  type="number"
                  value={item.quantity || ''}
                  onChange={(e) => handleItemChange(index, 'quantity', parseInt(e.target.value) || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="21"
                />
              </div>
            </div>

            {/* Indication */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Indikasi (alasan penggunaan)
              </label>
              <input
                type="text"
                value={item.indication}
                onChange={(e) => handleItemChange(index, 'indication', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Contoh: Demam, Batuk"
              />
            </div>

            {/* Special Instructions & PRN */}
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Instruksi Khusus
                </label>
                <input
                  type="text"
                  value={item.special_instructions}
                  onChange={(e) => handleItemChange(index, 'special_instructions', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Contoh: diminum setelah makan"
                />
              </div>
              <div className="flex items-center pt-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={item.is_prn}
                    onChange={(e) => handleItemChange(index, 'is_prn', e.target.checked)}
                    className="mr-2"
                  />
                  PRN (Saat perlu)
                </label>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Additional Notes */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Catatan Tambahan
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={3}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Catatan tambahan untuk farmasi..."
        />
      </div>

      {/* Interaction Alerts */}
      {checkingInteractions && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            <span className="text-blue-800">Memeriksa interaksi obat...</span>
          </div>
        </div>
      )}

      {interactions.length > 0 && (
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-800 mb-3">
            Peringatan Interaksi Obat ({interactions.length})
          </h4>
          <div className="space-y-3">
            {interactions.map((interaction) => (
              <div key={interaction.id} className={`p-4 border-l-4 rounded-lg ${getSeverityColor(interaction.severity)}`}>
                <div className="font-semibold mb-1">
                  {interaction.drug_1_name}
                  {interaction.drug_2_name && ` + ${interaction.drug_2_name}`}
                </div>
                <div className="text-sm mb-2">{interaction.description}</div>
                <div className="text-sm font-medium">Rekomendasi: {interaction.recommendation}</div>
              </div>
            ))}
          </div>
          {!canPrescribe && (
            <div className="mt-4 p-3 bg-red-100 border border-red-400 rounded-lg text-red-800">
              <strong>Perhatian:</strong> Resep tidak dapat dibuat karena adanya interaksi kontraindikasi.
              Simpan sebagai draf atau konsultasikan dengan dokter spesialis.
            </div>
          )}
        </div>
      )}

      {/* Special Drug Indicators */}
      {(narcoticCount > 0 || antibioticCount > 0) && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="font-semibold text-yellow-900 mb-2">Perhatian Khusus:</div>
          {narcoticCount > 0 && (
            <div className="text-yellow-800">• {narcoticCount} obat narkotik - memerlukan dokumentasi tambahan</div>
          )}
          {antibioticCount > 0 && (
            <div className="text-yellow-800">• {antibioticCount} antibiotik - pastikan indikasi jelas</div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between items-center">
        <div className="flex items-center">
          <label className="flex items-center mr-4">
            <input
              type="checkbox"
              checked={isDraft}
              onChange={(e) => setIsDraft(e.target.checked)}
              className="mr-2"
            />
            Simpan sebagai Draf
          </label>
        </div>
        <div className="flex gap-4">
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
            disabled={submitting || (!canPrescribe && !isDraft)}
            className={`px-6 py-2 rounded-lg transition-colors ${
              submitting || (!canPrescribe && !isDraft)
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {submitting ? 'Menyimpan...' : isDraft ? 'Simpan Draf' : 'Buat Resep'}
          </button>
        </div>
      </div>
    </div>
  );
}
