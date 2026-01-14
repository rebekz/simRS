"use client";

import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { id } from 'date-fns/locale';

// Types
interface VitalSigns {
  temperature?: number;
  blood_pressure?: string;
  heart_rate?: number;
  respiratory_rate?: number;
  oxygen_saturation?: number;
  weight?: number;
  height?: number;
  pain_level?: number;
  blood_glucose?: number;
  consciousness?: string;
}

interface NursingFlowSheetData {
  admission_id: number;
  patient_id: number;
  shift_date: string;
  shift_type: 'morning' | 'afternoon' | 'night';
  vital_signs: VitalSigns;
  oral_intake_ml?: number;
  iv_intake_ml?: number;
  urine_output_ml?: number;
  stool_output?: string;
  emesis?: boolean;
  drainage_output?: number;
  skin_intact?: boolean;
  skin_issues?: string[];
  wound_care_performed?: boolean;
  wound_description?: string;
  activity_level?: string;
  mobility_assistance?: string;
  fall_risk?: string;
  diet_tolerance?: string;
  eating_assistance?: boolean;
  swallowing_difficulty?: boolean;
  bowel_pattern?: string;
  bladder_pattern?: string;
  incontinence_care?: string;
  consciousness_level?: string;
  orientation?: string;
  behavior?: string;
  restlessness?: boolean;
  pain_present?: boolean;
  pain_location?: string;
  pain_score?: number;
  pain_intervention?: string;
}

const SHIFT_TYPES = [
  { value: 'morning', label: 'Pagi (07:00-14:00)' },
  { value: 'afternoon', label: 'Siang (14:00-21:00)' },
  { value: 'night', label: 'Malam (21:00-07:00)' },
];

const CONSCIOUSNESS_LEVELS = [
  { value: 'alert', label: 'Alert (Sadar)' },
  { value: 'lethargic', label: 'Lethargic (Lesu)' },
  { value: 'stupor', label: 'Stupor' },
  { value: 'coma', label: 'Koma' },
];

const ORIENTATION_LEVELS = [
  { value: 'oriented x3', label: 'Oriented x3 (Orang, Tempat, Waktu)' },
  { value: 'oriented x2', label: 'Oriented x2' },
  { value: 'oriented x1', label: 'Oriented x1' },
  { value: 'disoriented', label: 'Disoriented (Tidak Sadar)' },
];

const DIET_TOLERANCE = [
  { value: 'good', label: 'Baik' },
  { value: 'fair', label: 'Cukup' },
  { value: 'poor', label: 'Buruk' },
  { value: 'NPO', label: 'NPO (Puasa)' },
];

const ACTIVITY_LEVELS = [
  { value: 'bed_rest', label: 'Bed Rest (Istirahat Tidur)' },
  { value: 'BRP', label: 'BRP (Bathroom Privileges)' },
  { value: 'ambulatory', label: 'Ambulatory (Jalan)' },
];

const FALL_RISK_LEVELS = [
  { value: 'low', label: 'Rendah' },
  { value: 'moderate', label: 'Sedang' },
  { value: 'high', label: 'Tinggi' },
];

const STOOL_OUTPUT = [
  { value: 'normal', label: 'Normal' },
  { value: 'diarrhea', label: 'Diare' },
  { value: 'constipated', label: 'Sembelit' },
  { value: 'none', label: 'Tidak Ada' },
];

const BLADDER_PATTERNS = [
  { value: 'continent', label: 'Kontrol Baik' },
  { value: 'catheter', label: 'Kateter' },
  { value: 'incontinent', label: 'Inkontinensia' },
];

export default function NursingFlowSheet({ admissionId, patientId }: { admissionId: number; patientId: number }) {
  const [formData, setFormData] = useState<Partial<NursingFlowSheetData>>({
    admission_id: admissionId,
    patient_id: patientId,
    shift_date: new Date().toISOString().split('T')[0],
    shift_type: 'morning',
    vital_signs: {},
  });
  const [loading, setLoading] = useState(false);
  const [autoSaving, setAutoSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [activeSection, setActiveSection] = useState<string>('vitals');

  // Auto-save every 30 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      if (formData.vital_signs && Object.keys(formData.vital_signs).length > 0) {
        handleAutoSave();
      }
    }, 30000);

    return () => clearInterval(timer);
  }, [formData]);

  async function handleAutoSave() {
    setAutoSaving(true);
    try {
      const response = await fetch('/api/v1/daily-care/flow-sheets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, auto_saved: true }),
      });
      if (response.ok) {
        setLastSaved(new Date());
      }
    } catch (error) {
      console.error('Auto-save failed:', error);
    } finally {
      setAutoSaving(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch('/api/v1/daily-care/flow-sheets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to save flow sheet');
      }

      alert('Lembar observasi keperawatan berhasil disimpan!');
      // Reset form
      setFormData({
        admission_id: admissionId,
        patient_id: patientId,
        shift_date: new Date().toISOString().split('T')[0],
        shift_type: 'morning',
        vital_signs: {},
      });
      setLastSaved(null);
    } catch (error) {
      console.error('Failed to save flow sheet:', error);
      alert('Gagal menyimpan lembar observasi');
    } finally {
      setLoading(false);
    }
  }

  function updateVitalSign(field: keyof VitalSigns, value: any) {
    setFormData({
      ...formData,
      vital_signs: {
        ...formData.vital_signs,
        [field]: value,
      },
    });
  }

  function updateField(field: keyof NursingFlowSheetData, value: any) {
    setFormData({ ...formData, [field]: value });
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Lembar Observasi Keperawatan</h1>
        <p className="text-gray-600">Dokumentasi tanda vital dan asuhan keperawatan</p>
        {lastSaved && (
          <p className="text-sm text-green-600 mt-2">
            Tersimpan otomatis: {format(lastSaved, 'HH:mm:ss')}
          </p>
        )}
        {autoSaving && (
          <p className="text-sm text-blue-600 mt-2">Menyimpan otomatis...</p>
        )}
      </div>

      {/* Shift Info */}
      <div className="bg-white rounded-lg shadow p-4 mb-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tanggal Shift</label>
            <input
              type="date"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              value={formData.shift_date}
              onChange={(e) => updateField('shift_date', e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tipe Shift</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              value={formData.shift_type}
              onChange={(e) => updateField('shift_type', e.target.value)}
            >
              {SHIFT_TYPES.map((type) => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-t-lg shadow border-b">
        <div className="flex overflow-x-auto">
          {[
            { id: 'vitals', label: 'Tanda Vital' },
            { id: 'intake', label: 'Input/Output' },
            { id: 'skin', label: 'Kulit & Luka' },
            { id: 'mobility', label: 'Mobilisasi' },
            { id: 'nutrition', label: 'Nutrisi' },
            { id: 'elimination', label: 'Ekskresi' },
            { id: 'neuro', label: 'Neurologi' },
            { id: 'pain', label: 'Nyeri' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSection(tab.id)}
              className={`px-4 py-3 text-sm font-medium whitespace-nowrap ${
                activeSection === tab.id
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Vital Signs Section */}
        {activeSection === 'vitals' && (
          <div className="bg-white rounded-b-lg shadow p-6 space-y-4">
            <h3 className="text-lg font-semibold">Tanda Vital</h3>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Suhu (°C)</label>
                <input
                  type="number"
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.vital_signs?.temperature || ''}
                  onChange={(e) => updateVitalSign('temperature', parseFloat(e.target.value) || undefined)}
                  placeholder="36.5"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tekanan Darah</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.vital_signs?.blood_pressure || ''}
                  onChange={(e) => updateVitalSign('blood_pressure', e.target.value)}
                  placeholder="120/80"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nadi (x/menit)</label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.vital_signs?.heart_rate || ''}
                  onChange={(e) => updateVitalSign('heart_rate', parseInt(e.target.value) || undefined)}
                  placeholder="80"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pernapasan (x/menit)</label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.vital_signs?.respiratory_rate || ''}
                  onChange={(e) => updateVitalSign('respiratory_rate', parseInt(e.target.value) || undefined)}
                  placeholder="20"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">SpO2 (%)</label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.vital_signs?.oxygen_saturation || ''}
                  onChange={(e) => updateVitalSign('oxygen_saturation', parseInt(e.target.value) || undefined)}
                  placeholder="98"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Berat (kg)</label>
                <input
                  type="number"
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.vital_signs?.weight || ''}
                  onChange={(e) => updateVitalSign('weight', parseFloat(e.target.value) || undefined)}
                  placeholder="70"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tinggi (cm)</label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.vital_signs?.height || ''}
                  onChange={(e) => updateVitalSign('height', parseInt(e.target.value) || undefined)}
                  placeholder="170"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Gula Darah</label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.vital_signs?.blood_glucose || ''}
                  onChange={(e) => updateVitalSign('blood_glucose', parseInt(e.target.value) || undefined)}
                  placeholder="100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Kesadaran (GCS)</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.vital_signs?.consciousness || ''}
                  onChange={(e) => updateVitalSign('consciousness', e.target.value)}
                  placeholder="E4 V5 M6"
                />
              </div>
            </div>
          </div>
        )}

        {/* Intake/Output Section */}
        {activeSection === 'intake' && (
          <div className="bg-white rounded-b-lg shadow p-6 space-y-4">
            <h3 className="text-lg font-semibold">Input dan Output</h3>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Input Oral (ml)</label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.oral_intake_ml || ''}
                  onChange={(e) => updateField('oral_intake_ml', parseInt(e.target.value) || undefined)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Input IV (ml)</label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.iv_intake_ml || ''}
                  onChange={(e) => updateField('iv_intake_ml', parseInt(e.target.value) || undefined)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Urine Output (ml)</label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.urine_output_ml || ''}
                  onChange={(e) => updateField('urine_output_ml', parseInt(e.target.value) || undefined)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Drainage Output (ml)</label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.drainage_output || ''}
                  onChange={(e) => updateField('drainage_output', parseInt(e.target.value) || undefined)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Stool Output</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.stool_output || ''}
                  onChange={(e) => updateField('stool_output', e.target.value || undefined)}
                >
                  <option value="">Pilih...</option>
                  {STOOL_OUTPUT.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2 h-4 w-4"
                    checked={formData.emesis || false}
                    onChange={(e) => updateField('emesis', e.target.checked)}
                  />
                  <span className="text-sm font-medium text-gray-700">Muntah (Emesis)</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Skin & Wound Care Section */}
        {activeSection === 'skin' && (
          <div className="bg-white rounded-b-lg shadow p-6 space-y-4">
            <h3 className="text-lg font-semibold">Kulit & Perawatan Luka</h3>

            <div className="space-y-4">
              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2 h-4 w-4"
                    checked={formData.skin_intact || false}
                    onChange={(e) => updateField('skin_intact', e.target.checked)}
                  />
                  <span className="text-sm font-medium text-gray-700">Kulit Utuh (Intact)</span>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Masalah Kulit</label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  rows={2}
                  value={formData.skin_issues?.join(', ') || ''}
                  onChange={(e) => updateField('skin_issues', e.target.value.split(',').map(s => s.trim()).filter(s => s))}
                  placeholder="kemerahan, ruam, luka decubitus"
                />
              </div>

              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2 h-4 w-4"
                    checked={formData.wound_care_performed || false}
                    onChange={(e) => updateField('wound_care_performed', e.target.checked)}
                  />
                  <span className="text-sm font-medium text-gray-700">Perawatan Luka Dilakukan</span>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Deskripsi Luka</label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  rows={3}
                  value={formData.wound_description || ''}
                  onChange={(e) => updateField('wound_description', e.target.value)}
                  placeholder="Lokasi, ukuran, kedalaman, tipe jaringan, eksudat"
                />
              </div>
            </div>
          </div>
        )}

        {/* Mobility Section */}
        {activeSection === 'mobility' && (
          <div className="bg-white rounded-b-lg shadow p-6 space-y-4">
            <h3 className="text-lg font-semibold">Aktivitas & Mobilisasi</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tingkat Aktivitas</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.activity_level || ''}
                  onChange={(e) => updateField('activity_level', e.target.value || undefined)}
                >
                  <option value="">Pilih...</option>
                  {ACTIVITY_LEVELS.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Bantuan Mobilitas</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.mobility_assistance || ''}
                  onChange={(e) => updateField('mobility_assistance', e.target.value || undefined)}
                >
                  <option value="">Pilih...</option>
                  <option value="independent">Mandiri</option>
                  <option value="assistive">Dengan Bantuan Alat</option>
                  <option value="dependent">Tergantung Bantuan</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Risiko Jatuh</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.fall_risk || ''}
                  onChange={(e) => updateField('fall_risk', e.target.value || undefined)}
                >
                  <option value="">Pilih...</option>
                  {FALL_RISK_LEVELS.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Nutrition Section */}
        {activeSection === 'nutrition' && (
          <div className="bg-white rounded-b-lg shadow p-6 space-y-4">
            <h3 className="text-lg font-semibold">Nutrisi & Hidrasi</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Toleransi Diet</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.diet_tolerance || ''}
                  onChange={(e) => updateField('diet_tolerance', e.target.value || undefined)}
                >
                  <option value="">Pilih...</option>
                  {DIET_TOLERANCE.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2 h-4 w-4"
                    checked={formData.eating_assistance || false}
                    onChange={(e) => updateField('eating_assistance', e.target.checked)}
                  />
                  <span className="text-sm font-medium text-gray-700">Butuh Bantuan Makan</span>
                </label>
              </div>

              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2 h-4 w-4"
                    checked={formData.swallowing_difficulty || false}
                    onChange={(e) => updateField('swallowing_difficulty', e.target.checked)}
                  />
                  <span className="text-sm font-medium text-gray-700">Kesulitan Menelan (Dysphagia)</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Elimination Section */}
        {activeSection === 'elimination' && (
          <div className="bg-white rounded-b-lg shadow p-6 space-y-4">
            <h3 className="text-lg font-semibold">Ekskresi</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pola BAB</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.bowel_pattern || ''}
                  onChange={(e) => updateField('bowel_pattern', e.target.value)}
                  placeholder="Normal, diare, sembelit"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pola BAK</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.bladder_pattern || ''}
                  onChange={(e) => updateField('bladder_pattern', e.target.value || undefined)}
                >
                  <option value="">Pilih...</option>
                  {BLADDER_PATTERNS.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Perawatan Inkontinensia</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.incontinence_care || ''}
                  onChange={(e) => updateField('incontinence_care', e.target.value)}
                  placeholder="Diaper, kateter, dll"
                />
              </div>
            </div>
          </div>
        )}

        {/* Neurology Section */}
        {activeSection === 'neuro' && (
          <div className="bg-white rounded-b-lg shadow p-6 space-y-4">
            <h3 className="text-lg font-semibold">Perilaku & Kognisi</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tingkat Kesadaran</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.consciousness_level || ''}
                  onChange={(e) => updateField('consciousness_level', e.target.value || undefined)}
                >
                  <option value="">Pilih...</option>
                  {CONSCIOUSNESS_LEVELS.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Orientasi</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  value={formData.orientation || ''}
                  onChange={(e) => updateField('orientation', e.target.value || undefined)}
                >
                  <option value="">Pilih...</option>
                  {ORIENTATION_LEVELS.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Perilaku</label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  rows={2}
                  value={formData.behavior || ''}
                  onChange={(e) => updateField('behavior', e.target.value)}
                  placeholder="Tenang, gelisah, agresif, dll"
                />
              </div>

              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2 h-4 w-4"
                    checked={formData.restlessness || false}
                    onChange={(e) => updateField('restlessness', e.target.checked)}
                  />
                  <span className="text-sm font-medium text-gray-700">Gelisah (Restlessness)</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Pain Section */}
        {activeSection === 'pain' && (
          <div className="bg-white rounded-b-lg shadow p-6 space-y-4">
            <h3 className="text-lg font-semibold">Asesmen Nyeri</h3>

            <div className="space-y-4">
              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2 h-4 w-4"
                    checked={formData.pain_present || false}
                    onChange={(e) => updateField('pain_present', e.target.checked)}
                  />
                  <span className="text-sm font-medium text-gray-700">Nyeri Ada</span>
                </label>
              </div>

              {formData.pain_present && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Lokasi Nyeri</label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      value={formData.pain_location || ''}
                      onChange={(e) => updateField('pain_location', e.target.value)}
                      placeholder="Kepala, dada, perut, dll"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Skala Nyeri (0-10)</label>
                    <div className="flex items-center gap-4">
                      <input
                        type="range"
                        min="0"
                        max="10"
                        className="flex-1"
                        value={formData.pain_score || 0}
                        onChange={(e) => updateField('pain_score', parseInt(e.target.value))}
                      />
                      <span className="text-2xl font-bold w-12 text-center">
                        {formData.pain_score || 0}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>0 (Tidak Nyeri)</span>
                      <span>10 (Nyeri Terburuk)</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Intervensi</label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      rows={2}
                      value={formData.pain_intervention || ''}
                      onChange={(e) => updateField('pain_intervention', e.target.value)}
                      placeholder="Obat nyeri, posisi, kompres, dll"
                    />
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="mt-6 flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-semibold"
          >
            {loading ? 'Menyimpan...' : 'Simpan Lembar Observasi'}
          </button>
        </div>
      </form>
    </div>
  );
}
