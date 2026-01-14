"use client";

import React, { useState } from 'react';

interface PhysicianDailyNoteData {
  admission_id: number;
  patient_id: number;
  physician_id: number;
  note_date: string;
  subjective?: string;
  objective?: string;
  assessment: string;
  plan: string;
  primary_diagnosis: string;
  secondary_diagnoses?: string[];
  new_orders?: string[];
  continued_orders?: string[];
  discontinued_orders?: string[];
  prognosis?: string;
  signed_by_id: number;
}

export default function PhysicianDailyNote({ admissionId, patientId, physicianId }: {
  admissionId: number;
  patientId: number;
  physicianId: number;
}) {
  const [formData, setFormData] = useState<Partial<PhysicianDailyNoteData>>({
    admission_id: admissionId,
    patient_id: patientId,
    physician_id: physicianId,
    note_date: new Date().toISOString().split('T')[0],
    assessment: '',
    plan: '',
    primary_diagnosis: '',
    signed_by_id: physicianId,
  });

  const [loading, setLoading] = useState(false);
  const [activeSection, setActiveSection] = useState<string>('soap');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch('/api/v1/daily-care/physician-daily-notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to save note');
      }

      alert('Catatan harian dokter berhasil disimpan!');

      // Reset form
      setFormData({
        admission_id: admissionId,
        patient_id: patientId,
        physician_id: physicianId,
        note_date: new Date().toISOString().split('T')[0],
        assessment: '',
        plan: '',
        primary_diagnosis: '',
        signed_by_id: physicianId,
      });
    } catch (error) {
      console.error('Failed to save note:', error);
      alert('Gagal menyimpan catatan harian');
    } finally {
      setLoading(false);
    }
  }

  function addToArrayField(field: 'secondary_diagnoses' | 'new_orders' | 'continued_orders' | 'discontinued_orders', value: string) {
    if (!value.trim()) return;
    const currentArray = formData[field] || [];
    setFormData({
      ...formData,
      [field]: [...currentArray, value.trim()]
    });
  }

  function removeFromArrayField(field: 'secondary_diagnoses' | 'new_orders' | 'continued_orders' | 'discontinued_orders', index: number) {
    const currentArray = formData[field] || [];
    setFormData({
      ...formData,
      [field]: currentArray.filter((_, i) => i !== index)
    });
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Catatan Harian Dokter</h1>
        <p className="text-gray-600">Dokumentasi SOAP format dan perencanaan tatalaksana</p>
      </div>

      {/* Date */}
      <div className="bg-white rounded-lg shadow p-4 mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Tanggal Catatan</label>
        <input
          type="date"
          className="w-full md:w-auto px-3 py-2 border border-gray-300 rounded-lg"
          value={formData.note_date}
          onChange={(e) => setFormData({ ...formData, note_date: e.target.value })}
        />
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-t-lg shadow border-b">
        <div className="flex overflow-x-auto">
          {[
            { id: 'soap', label: 'SOAP Note' },
            { id: 'diagnosis', label: 'Diagnosa' },
            { id: 'orders', label: 'Perintah' },
            { id: 'prognosis', label: 'Prognosa' },
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
        {/* SOAP Note Section */}
        {activeSection === 'soap' && (
          <div className="bg-white rounded-b-lg shadow p-6 space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <strong>S</strong> - Subjective (Keluhan Pasien)
              </label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                rows={4}
                value={formData.subjective || ''}
                onChange={(e) => setFormData({ ...formData, subjective: e.target.value })}
                placeholder="Pasien mengeluh nyeri dada sesak napas sejak 2 jam lalu..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <strong>O</strong> - Objective (Pemeriksaan Fisik & Lab)
              </label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                rows={4}
                value={formData.objective || ''}
                onChange={(e) => setFormData({ ...formData, objective: e.target.value })}
                placeholder="TD: 140/90, N: 88, RR: 20, SpO2: 95%, Temp: 37.5°C&#10;Kepala: CAH&#10;Thorax: Ronkhi basal kanan..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <strong>A</strong> - Assessment (Penilaian) *
              </label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                rows={4}
                value={formData.assessment}
                onChange={(e) => setFormData({ ...formData, assessment: e.target.value })}
                placeholder="Pasien dengan sindrom koroner akut, kemungkinan STEMI anterior..."
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <strong>P</strong> - Plan (Rencana Tatalaksana) *
              </label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                rows={4}
                value={formData.plan}
                onChange={(e) => setFormData({ ...formData, plan: e.target.value })}
                placeholder="1. Monitor EKG telemetri&#10;2. Oksigen 2-3 lpm&#10;3. Nitro sublingual PRN&#10;4. Morfine IV PRN nyeri..."
                required
              />
            </div>
          </div>
        )}

        {/* Diagnosis Section */}
        {activeSection === 'diagnosis' && (
          <div className="bg-white rounded-b-lg shadow p-6 space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Diagnosa Utama *
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                value={formData.primary_diagnosis}
                onChange={(e) => setFormData({ ...formData, primary_diagnosis: e.target.value })}
                placeholder="Sindrom Koroner Akut (SKA)"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Diagnosa Sekunder
              </label>
              <div className="space-y-2">
                {(formData.secondary_diagnoses || []).map((diagnosis, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <span className="flex-1 px-3 py-2 bg-gray-100 rounded-lg">
                      {diagnosis}
                    </span>
                    <button
                      type="button"
                      onClick={() => removeFromArrayField('secondary_diagnoses', index)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                    >
                      Hapus
                    </button>
                  </div>
                ))}
              </div>
              <div className="mt-2 flex gap-2">
                <input
                  type="text"
                  id="new-secondary-diagnosis"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Tambah diagnosa sekunder..."
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      const input = e.currentTarget;
                      addToArrayField('secondary_diagnoses', input.value);
                      input.value = '';
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={() => {
                    const input = document.getElementById('new-secondary-diagnosis') as HTMLInputElement;
                    if (input) {
                      addToArrayField('secondary_diagnoses', input.value);
                      input.value = '';
                    }
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Tambah
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Orders Section */}
        {activeSection === 'orders' && (
          <div className="bg-white rounded-b-lg shadow p-6 space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Perintah Baru (New Orders)
              </label>
              <div className="space-y-2">
                {(formData.new_orders || []).map((order, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <span className="flex-1 px-3 py-2 bg-green-50 rounded-lg">
                      {order}
                    </span>
                    <button
                      type="button"
                      onClick={() => removeFromArrayField('new_orders', index)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                    >
                      Hapus
                    </button>
                  </div>
                ))}
              </div>
              <div className="mt-2 flex gap-2">
                <input
                  type="text"
                  id="new-order"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Tambah perintah baru..."
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      const input = e.currentTarget;
                      addToArrayField('new_orders', input.value);
                      input.value = '';
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={() => {
                    const input = document.getElementById('new-order') as HTMLInputElement;
                    if (input) {
                      addToArrayField('new_orders', input.value);
                      input.value = '';
                    }
                  }}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Tambah
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Perintah Dilanjutkan (Continued Orders)
              </label>
              <div className="space-y-2">
                {(formData.continued_orders || []).map((order, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <span className="flex-1 px-3 py-2 bg-blue-50 rounded-lg">
                      {order}
                    </span>
                    <button
                      type="button"
                      onClick={() => removeFromArrayField('continued_orders', index)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                    >
                      Hapus
                    </button>
                  </div>
                ))}
              </div>
              <div className="mt-2 flex gap-2">
                <input
                  type="text"
                  id="continued-order"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Tambah perintah dilanjutkan..."
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      const input = e.currentTarget;
                      addToArrayField('continued_orders', input.value);
                      input.value = '';
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={() => {
                    const input = document.getElementById('continued-order') as HTMLInputElement;
                    if (input) {
                      addToArrayField('continued_orders', input.value);
                      input.value = '';
                    }
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Tambah
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Perintah Dihentikan (Discontinued Orders)
              </label>
              <div className="space-y-2">
                {(formData.discontinued_orders || []).map((order, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <span className="flex-1 px-3 py-2 bg-red-50 rounded-lg">
                      {order}
                    </span>
                    <button
                      type="button"
                      onClick={() => removeFromArrayField('discontinued_orders', index)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                    >
                      Hapus
                    </button>
                  </div>
                ))}
              </div>
              <div className="mt-2 flex gap-2">
                <input
                  type="text"
                  id="discontinued-order"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Tambah perintah dihentikan..."
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      const input = e.currentTarget;
                      addToArrayField('discontinued_orders', input.value);
                      input.value = '';
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={() => {
                    const input = document.getElementById('discontinued-order') as HTMLInputElement;
                    if (input) {
                      addToArrayField('discontinued_orders', input.value);
                      input.value = '';
                    }
                  }}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Tambah
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Prognosis Section */}
        {activeSection === 'prognosis' && (
          <div className="bg-white rounded-b-lg shadow p-6 space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Prognosa
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                value={formData.prognosis || ''}
                onChange={(e) => setFormData({ ...formData, prognosis: e.target.value || undefined })}
              >
                <option value="">Pilih prognosis...</option>
                <option value="baik">Baik (Good)</option>
                <option value="cukup">Cukup (Fair)</option>
                <option value="buruk">Buruk (Poor)</option>
                <option value="sangat buruk">Sangat Buruk (Grave)</option>
                <option value="kritis">Kritis (Critical)</option>
              </select>
            </div>

            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">Panduan Prognosa</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• <strong>Baik:</strong> Kondisi stabil, respon baik terapi, kemungkinan pulang tinggi</li>
                <li>• <strong>Cukup:</strong> Kondisi stabil namun ada komplikasi, memerlukan monitoring</li>
                <li>• <strong>Buruk:</strong> Kondisi tidak stabil, respon terapi kurang, risiko tinggi</li>
                <li>• <strong>Sangat Buruk:</strong> Kondisi kritis, prognosa survival rendah</li>
                <li>• <strong>Kritis:</strong> Kondisi sangat kritis, memerlukan perawatan intensif</li>
              </ul>
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
            {loading ? 'Menyimpan...' : 'Simpan Catatan Harian'}
          </button>
        </div>
      </form>
    </div>
  );
}
