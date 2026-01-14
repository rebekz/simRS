"use client";

import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { id } from 'date-fns/locale';

// Types
interface DischargeOrderData {
  admission_id: number;
  patient_id: number;
  physician_id: number;
  discharge_status: string;
  discharge_destination: string;
  discharge_condition: string;
  discharge_medications: Medication[];
  discharge_instructions: Instruction[];
  activity_restrictions: ActivityRestriction[];
  diet_instructions?: string;
  wound_care_instructions?: string;
  follow_up_appointments: any[];
  medical_equipment?: string[];
  transportation_arranged: boolean;
  transportation_type?: string;
  responsible_adult_name?: string;
  responsible_adult_relationship?: string;
  responsible_adult_contact?: string;
  special_needs?: string[];
  estimated_discharge_date?: string;
  physician_notes?: string;
}

interface Medication {
  medication_name: string;
  dosage: string;
  frequency: string;
  duration: string;
  route: string;
  indication?: string;
  special_instructions?: string;
}

interface Instruction {
  category: string;
  instruction: string;
  priority: string;
}

interface ActivityRestriction {
  activity_type: string;
  restriction_level: string;
  duration?: string;
}

const DISCHARGE_DESTINATIONS = [
  { value: 'home', label: 'Pulang ke Rumah' },
  { value: 'transfer', label: 'Rujukan ke RS Lain' },
  { value: 'facility', label: 'Fasilitas Perawatan' },
  { value: 'left_against_advice', label: 'Pulang Atas Permintaan Sendiri' },
  { value: 'deceased', label: 'Meninggal' },
];

const DISCHARGE_CONDITIONS = [
  { value: 'improved', label: 'Membaik' },
  { value: 'stable', label: 'Stabil' },
  { value: 'unchanged', label: 'Tetap' },
  { value: 'worsened', label: 'Memburuk' },
];

const ACTIVITY_RESTRICTIONS = [
  { type: 'driving', label: 'Mengemudi' },
  { type: 'working', label: 'Bekerja' },
  { type: 'lifting', label: 'Mengangkat Beban' },
  { type: 'exercise', label: 'Olahraga' },
  { type: 'stairs', label: 'Naik Turun Tangga' },
];

const RESTRICTION_LEVELS = [
  { value: 'no_restriction', label: 'Tanpa Pembatasan' },
  { value: 'limited', label: 'Terbatas' },
  { value: 'prohibited', label: 'Dilarang' },
];

export default function DischargeWorkflow({ admissionId, patientId, physicianId }: {
  admissionId: number;
  patientId: number;
  physicianId: number;
}) {
  const [step, setStep] = useState<'readiness' | 'orders' | 'reconciliation' | 'followup' | 'bpjs' | 'summary' | 'complete'>('readiness');
  const [loading, setLoading] = useState(false);

  // Readiness assessment state
  const [readinessCriteria, setReadinessCriteria] = useState({
    clinically_stable: false,
    vital_signs_stable: false,
    afebrile_24h: false,
    pain_controlled: false,
    medications_prescribed: false,
    education_completed: false,
    follow_up_scheduled: false,
    arrangements_made: false,
  });
  const [readinessScore, setReadinessScore] = useState(0);
  const [barriers, setBarriers] = useState<string[]>([]);

  // Discharge order state
  const [dischargeOrder, setDischargeOrder] = useState<Partial<DischargeOrderData>>({
    admission_id: admissionId,
    patient_id: patientId,
    physician_id: physicianId,
    discharge_status: 'ready',
    discharge_destination: 'home',
    discharge_condition: 'improved',
    discharge_medications: [],
    discharge_instructions: [],
    activity_restrictions: [],
    medical_equipment: [],
    special_needs: [],
    transportation_arranged: false,
  });

  // Medication form state
  const [newMedication, setNewMedication] = useState<Medication>({
    medication_name: '',
    dosage: '',
    frequency: '',
    duration: '',
    route: 'oral',
  });

  // Instruction form state
  const [newInstruction, setNewInstruction] = useState({
    category: 'umum',
    instruction: '',
    priority: 'normal',
  });

  // Calculate readiness score
  useEffect(() => {
    const criteria = Object.values(readinessCriteria);
    const metCount = criteria.filter(Boolean).length;
    setReadinessScore(Math.round((metCount / criteria.length) * 100));
  }, [readinessCriteria]);

  async function handleSubmitDischarge() {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/discharge/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dischargeOrder),
      });

      if (!response.ok) {
        throw new Error('Failed to create discharge order');
      }

      const order = await response.json();

      // Complete the discharge
      await fetch(`/api/v1/discharge/admissions/${admissionId}/complete-discharge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          actual_discharge_date: new Date().toISOString(),
        }),
      });

      setStep('complete');
    } catch (error) {
      console.error('Failed to submit discharge:', error);
      alert('Gagal menyelesaikan pemulangan pasien');
    } finally {
      setLoading(false);
    }
  }

  function addMedication() {
    if (!newMedication.medication_name || !newMedication.dosage || !newMedication.frequency || !newMedication.duration) {
      alert('Mohon lengkapi data obat');
      return;
    }

    setDischargeOrder({
      ...dischargeOrder,
      discharge_medications: [...(dischargeOrder.discharge_medications || []), newMedication],
    });

    setNewMedication({
      medication_name: '',
      dosage: '',
      frequency: '',
      duration: '',
      route: 'oral',
    });
  }

  function removeMedication(index: number) {
    setDischargeOrder({
      ...dischargeOrder,
      discharge_medications: dischargeOrder.discharge_medications?.filter((_, i) => i !== index) || [],
    });
  }

  function addInstruction() {
    if (!newInstruction.instruction) {
      alert('Mohon isi instruksi');
      return;
    }

    setDischargeOrder({
      ...dischargeOrder,
      discharge_instructions: [...(dischargeOrder.discharge_instructions || []), newInstruction],
    });

    setNewInstruction({
      category: 'umum',
      instruction: '',
      priority: 'normal',
    });
  }

  function removeInstruction(index: number) {
    setDischargeOrder({
      ...dischargeOrder,
      discharge_instructions: dischargeOrder.discharge_instructions?.filter((_, i) => i !== index) || [],
    });
  }

  function addActivityRestriction() {
    const restriction: ActivityRestriction = {
      activity_type: '',
      restriction_level: 'limited',
    };
    setDischargeOrder({
      ...dischargeOrder,
      activity_restrictions: [...(dischargeOrder.activity_restrictions || []), restriction],
    });
  }

  function updateActivityRestriction(index: number, field: keyof ActivityRestriction, value: any) {
    const restrictions = [...(dischargeOrder.activity_restrictions || [])];
    restrictions[index] = { ...restrictions[index], [field]: value };
    setDischargeOrder({
      ...dischargeOrder,
      activity_restrictions: restrictions,
    });
  }

  function removeActivityRestriction(index: number) {
    setDischargeOrder({
      ...dischargeOrder,
      activity_restrictions: dischargeOrder.activity_restrictions?.filter((_, i) => i !== index) || [],
    });
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Pemulangan Pasien</h1>
        <p className="text-gray-600">Workflow perencanaan dan penyelesaian pemulangan pasien</p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between overflow-x-auto">
          {[
            { num: 1, label: 'Kesiapan', step: 'readiness' },
            { num: 2, label: 'Perintah', step: 'orders' },
            { num: 3, label: 'Rekonsiliasi', step: 'reconciliation' },
            { num: 4, label: 'Follow-up', step: 'followup' },
            { num: 5, label: 'BPJS', step: 'bpjs' },
            { num: 6, label: 'Ringkasan', step: 'summary' },
          ].map((s) => (
            <React.Fragment key={s.step}>
              <div className="flex items-center flex-shrink-0">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  step === s.step ? 'bg-blue-600 text-white' :
                  ['readiness', 'orders', 'reconciliation', 'followup', 'bpjs', 'summary', 'complete'].indexOf(step) > ['readiness', 'orders', 'reconciliation', 'followup', 'bpjs', 'summary', 'complete'].indexOf(s.step)
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {['readiness', 'orders', 'reconciliation', 'followup', 'bpjs', 'summary', 'complete'].indexOf(step) > ['readiness', 'orders', 'reconciliation', 'followup', 'bpjs', 'summary', 'complete'].indexOf(s.step) ? '✓' : s.num}
                </div>
                <span className={`ml-2 font-medium text-sm whitespace-nowrap ${
                  step === s.step ? 'text-blue-600' :
                  ['readiness', 'orders', 'reconciliation', 'followup', 'bpjs', 'summary', 'complete'].indexOf(step) > ['readiness', 'orders', 'reconciliation', 'followup', 'bpjs', 'summary', 'complete'].indexOf(s.step)
                    ? 'text-green-600'
                    : 'text-gray-400'
                }`}>{s.label}</span>
              </div>
              {s.num < 6 && (
                <div className="flex-1 h-1 mx-4 bg-gray-200 min-w-[50px]">
                  <div className={`h-full ${
                    ['readiness', 'orders', 'reconciliation', 'followup', 'bpjs', 'summary', 'complete'].indexOf(step) > ['readiness', 'orders', 'reconciliation', 'followup', 'bpjs', 'summary', 'complete'].indexOf(s.step)
                      ? 'bg-green-500'
                      : 'bg-gray-200'
                  }`} style={{ width: ['readiness', 'orders', 'reconciliation', 'followup', 'bpjs', 'summary', 'complete'].indexOf(step) > ['readiness', 'orders', 'reconciliation', 'followup', 'bpjs', 'summary', 'complete'].indexOf(s.step) ? '100%' : '0%' }}></div>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Step 1: Discharge Readiness Assessment */}
      {step === 'readiness' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Asesmen Kesiapan Pemulangan</h2>

          {/* Readiness Score */}
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-blue-900">Skor Kesiapan</h3>
                <p className="text-sm text-blue-700">Berdasarkan kriteria pemulangan</p>
              </div>
              <div className={`text-4xl font-bold ${
                readinessScore >= 80 ? 'text-green-600' :
                readinessScore >= 60 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {readinessScore}%
              </div>
            </div>
          </div>

          {/* Criteria Checklist */}
          <div className="space-y-3 mb-6">
            <h3 className="font-semibold text-gray-900 mb-3">Kriteria Pemulangan</h3>

            {[
              { key: 'clinically_stable', label: 'Pasien secara klinis stabil' },
              { key: 'vital_signs_stable', label: 'Tanda vital stabil 24 jam terakhir' },
              { key: 'afebrile_24h', label: 'Tidak demam 24 jam terakhir' },
              { key: 'pain_controlled', label: 'Nyeri terkontrol' },
              { key: 'medications_prescribed', label: 'Obat sudah diresepkan' },
              { key: 'education_completed', label: 'Edukasi pasien selesai' },
              { key: 'follow_up_scheduled', label: 'Follow-up dijadwalkan' },
              { key: 'arrangements_made', label: 'Aransemen pulang siap' },
            ].map((criterion) => (
              <label key={criterion.key} className="flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  className="mr-3 h-5 w-5"
                  checked={readinessCriteria[criterion.key as keyof typeof readinessCriteria]}
                  onChange={(e) => setReadinessCriteria({
                    ...readinessCriteria,
                    [criterion.key]: e.target.checked
                  })}
                />
                <span className="text-gray-700">{criterion.label}</span>
              </label>
            ))}
          </div>

          {/* Barriers */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Hambatan Pemulangan (Opsional)
            </label>
            <textarea
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              rows={3}
              value={barriers.join('\n')}
              onChange={(e) => setBarriers(e.target.value.split('\n').filter(b => b.trim()))}
              placeholder="Masukkan hambatan pemulangan (satu per baris)"
            />
          </div>

          <div className="flex gap-4">
            <button
              onClick={() => setStep('orders')}
              disabled={readinessScore < 60}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-semibold"
            >
              Lanjut ke Perintah Pemulangan
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Discharge Orders */}
      {step === 'orders' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Perintah Pemulangan</h2>
            <button onClick={() => setStep('readiness')} className="text-blue-600 hover:text-blue-800">
              ← Kembali
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tujuan Pemulangan *</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                value={dischargeOrder.discharge_destination}
                onChange={(e) => setDischargeOrder({ ...dischargeOrder, discharge_destination: e.target.value })}
              >
                {DISCHARGE_DESTINATIONS.map((dest) => (
                  <option key={dest.value} value={dest.value}>{dest.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Kondisi Saat Pemulangan *</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                value={dischargeOrder.discharge_condition}
                onChange={(e) => setDischargeOrder({ ...dischargeOrder, discharge_condition: e.target.value })}
              >
                {DISCHARGE_CONDITIONS.map((cond) => (
                  <option key={cond.value} value={cond.value}>{cond.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Perkiraan Tanggal Pemulangan</label>
              <input
                type="date"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                value={dischargeOrder.estimated_discharge_date || ''}
                onChange={(e) => setDischargeOrder({ ...dischargeOrder, estimated_discharge_date: e.target.value || undefined })}
                min={new Date().toISOString().split('T')[0]}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Transportasi</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                value={dischargeOrder.transportation_type || ''}
                onChange={(e) => setDischargeOrder({
                  ...dischargeOrder,
                  transportation_arranged: !!e.target.value,
                  transportation_type: e.target.value || undefined,
                })}
              >
                <option value="">Pilih transportasi...</option>
                <option value="pribadi">Kendaraan Pribadi</option>
                <option value="antar-jemput">Antar-Jemput RS</option>
                <option value="ambulan">Ambulan</option>
              </select>
            </div>
          </div>

          {/* Discharge Medications */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-900 mb-3">Obat Pemulangan</h3>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-2 mb-2 p-4 bg-gray-50 rounded-lg">
              <input
                type="text"
                placeholder="Nama obat"
                className="px-2 py-1 border border-gray-300 rounded"
                value={newMedication.medication_name}
                onChange={(e) => setNewMedication({ ...newMedication, medication_name: e.target.value })}
              />
              <input
                type="text"
                placeholder="Dosis"
                className="px-2 py-1 border border-gray-300 rounded"
                value={newMedication.dosage}
                onChange={(e) => setNewMedication({ ...newMedication, dosage: e.target.value })}
              />
              <input
                type="text"
                placeholder="Frekuensi"
                className="px-2 py-1 border border-gray-300 rounded"
                value={newMedication.frequency}
                onChange={(e) => setNewMedication({ ...newMedication, frequency: e.target.value })}
              />
              <input
                type="text"
                placeholder="Durasi"
                className="px-2 py-1 border border-gray-300 rounded"
                value={newMedication.duration}
                onChange={(e) => setNewMedication({ ...newMedication, duration: e.target.value })}
              />
              <button
                type="button"
                onClick={addMedication}
                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                + Tambah
              </button>
            </div>

            {(dischargeOrder.discharge_medications || []).map((med, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg mb-2">
                <div className="flex-1">
                  <div className="font-medium">{med.medication_name}</div>
                  <div className="text-sm text-gray-600">
                    {med.dosage} - {med.frequency} - {med.duration} - {med.route}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => removeMedication(index)}
                  className="px-3 py-1 text-red-600 hover:bg-red-50 rounded"
                >
                  Hapus
                </button>
              </div>
            ))}
          </div>

          {/* Discharge Instructions */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-900 mb-3">Instruksi Pemulangan</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-2 p-4 bg-gray-50 rounded-lg">
              <select
                className="px-2 py-1 border border-gray-300 rounded"
                value={newInstruction.category}
                onChange={(e) => setNewInstruction({ ...newInstruction, category: e.target.value })}
              >
                <option value="umum">Umum</option>
                <option value="aktivitas">Aktivitas</option>
                <option value="diet">Diet</option>
                <option value="luka">Perawatan Luka</option>
                <option value="gejala">Gejala Peringatan</option>
              </select>
              <input
                type="text"
                placeholder="Instruksi..."
                className="px-2 py-1 border border-gray-300 rounded"
                value={newInstruction.instruction}
                onChange={(e) => setNewInstruction({ ...newInstruction, instruction: e.target.value })}
              />
              <button
                type="button"
                onClick={addInstruction}
                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                + Tambah
              </button>
            </div>

            {(dischargeOrder.discharge_instructions || []).map((inst, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg mb-2">
                <div className="flex-1">
                  <span className="inline-block px-2 py-1 bg-gray-100 rounded text-xs mr-2">
                    {inst.category}
                  </span>
                  {inst.instruction}
                </div>
                <button
                  type="button"
                  onClick={() => removeInstruction(index)}
                  className="px-3 py-1 text-red-600 hover:bg-red-50 rounded"
                >
                  Hapus
                </button>
              </div>
            ))}
          </div>

          {/* Activity Restrictions */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-semibold text-gray-900">Pembatasan Aktivitas</h3>
              <button
                type="button"
                onClick={addActivityRestriction}
                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                + Tambah Pembatasan
              </button>
            </div>

            {(dischargeOrder.activity_restrictions || []).map((restriction, index) => (
              <div key={index} className="flex items-center gap-2 p-3 border rounded-lg mb-2">
                <select
                  className="flex-1 px-2 py-1 border border-gray-300 rounded"
                  value={restriction.activity_type}
                  onChange={(e) => updateActivityRestriction(index, 'activity_type', e.target.value)}
                >
                  <option value="">Pilih aktivitas...</option>
                  {ACTIVITY_RESTRICTIONS.map((act) => (
                    <option key={act.type} value={act.type}>{act.label}</option>
                  ))}
                </select>
                <select
                  className="flex-1 px-2 py-1 border border-gray-300 rounded"
                  value={restriction.restriction_level}
                  onChange={(e) => updateActivityRestriction(index, 'restriction_level', e.target.value)}
                >
                  {RESTRICTION_LEVELS.map((level) => (
                    <option key={level.value} value={level.value}>{level.label}</option>
                  ))}
                </select>
                <input
                  type="text"
                  placeholder="Durasi (opsional)"
                  className="flex-1 px-2 py-1 border border-gray-300 rounded"
                  value={restriction.duration || ''}
                  onChange={(e) => updateActivityRestriction(index, 'duration', e.target.value)}
                />
                <button
                  type="button"
                  onClick={() => removeActivityRestriction(index)}
                  className="px-3 py-1 text-red-600 hover:bg-red-50 rounded"
                >
                  Hapus
                </button>
              </div>
            ))}
          </div>

          {/* Special Instructions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Instruksi Diet</label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                rows={2}
                value={dischargeOrder.diet_instructions || ''}
                onChange={(e) => setDischargeOrder({ ...dischargeOrder, diet_instructions: e.target.value })}
                placeholder="Instruksi diet pemulangan"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Perawatan Luka</label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                rows={2}
                value={dischargeOrder.wound_care_instructions || ''}
                onChange={(e) => setDischargeOrder({ ...dischargeOrder, wound_care_instructions: e.target.value })}
                placeholder="Instruksi perawatan luka"
              />
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={() => setStep('reconciliation')}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-semibold"
            >
              Lanjut ke Rekonsiliasi Obat
            </button>
            <button onClick={() => setStep('readiness')} className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              Kembali
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Medication Reconciliation */}
      {step === 'reconciliation' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Rekonsiliasi Obat</h2>
            <button onClick={() => setStep('orders')} className="text-blue-600 hover:text-blue-800">
              ← Kembali
            </button>
          </div>

          <div className="text-center py-8">
            <p className="text-gray-600 mb-4">Fitur rekonsiliasi obat akan diimplementasikan oleh apoteker</p>
            <button
              onClick={() => setStep('followup')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Lewati
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Follow-up Appointments */}
      {step === 'followup' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Jadwal Follow-up</h2>
            <button onClick={() => setStep('reconciliation')} className="text-blue-600 hover:text-blue-800">
              ← Kembali
            </button>
          </div>

          <div className="text-center py-8">
            <p className="text-gray-600 mb-4">Jadwal follow-up akan diatur secara terpisah</p>
            <button
              onClick={() => setStep('bpjs')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Lewati
            </button>
          </div>
        </div>
      )}

      {/* Step 5: BPJS Claims */}
      {step === 'bpjs' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Finalisasi Klaim BPJS</h2>
            <button onClick={() => setStep('followup')} className="text-blue-600 hover:text-blue-800">
              ← Kembali
            </button>
          </div>

          <div className="text-center py-8">
            <p className="text-gray-600 mb-4">Finalisasi klaim BPJS akan dilakukan secara terpisah</p>
            <button
              onClick={() => setStep('summary')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Lanjut ke Ringkasan
            </button>
          </div>
        </div>
      )}

      {/* Step 6: Summary */}
      {step === 'summary' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Ringkasan Pemulangan</h2>
            <button onClick={() => setStep('bpjs')} className="text-blue-600 hover:text-blue-800">
              ← Kembali
            </button>
          </div>

          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">Detail Pemulangan</h3>
              <div className="text-blue-800 space-y-1">
                <div><strong>Tujuan:</strong> {DISCHARGE_DESTINATIONS.find(d => d.value === dischargeOrder.discharge_destination)?.label}</div>
                <div><strong>Kondisi:</strong> {DISCHARGE_CONDITIONS.find(c => c.value === dischargeOrder.discharge_condition)?.label}</div>
                <div><strong>Transportasi:</strong> {dischargeOrder.transportation_type || 'Belum diatur'}</div>
              </div>
            </div>

            <div className="p-4 bg-green-50 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-2">Obat Pemulangan ({(dischargeOrder.discharge_medications || []).length})</h3>
              <ul className="text-green-800 space-y-1">
                {(dischargeOrder.discharge_medications || []).map((med, index) => (
                  <li key={index}>{med.medication_name} - {med.dosage} {med.frequency}</li>
                ))}
              </ul>
            </div>

            <div className="p-4 bg-yellow-50 rounded-lg">
              <h3 className="font-semibold text-yellow-900 mb-2">Instruksi Pemulangan ({(dischargeOrder.discharge_instructions || []).length})</h3>
              <ul className="text-yellow-800 space-y-1">
                {(dischargeOrder.discharge_instructions || []).map((inst, index) => (
                  <li key={index}>{inst.instruction}</li>
                ))}
              </ul>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg">
              <h3 className="font-semibold text-purple-900 mb-2">Pembatasan Aktivitas ({(dischargeOrder.activity_restrictions || []).length})</h3>
              <ul className="text-purple-800 space-y-1">
                {(dischargeOrder.activity_restrictions || []).map((restriction, index) => (
                  <li key={index}>
                    {ACTIVITY_RESTRICTIONS.find(a => a.type === restriction.activity_type)?.label}: {
                      RESTRICTION_LEVELS.find(l => l.value === restriction.restriction_level)?.label
                    }
                    {restriction.duration && ` (${restriction.duration})`}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mt-6 flex gap-4">
            <button
              onClick={handleSubmitDischarge}
              disabled={loading}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-semibold"
            >
              {loading ? 'Memproses...' : 'Selesaikan Pemulangan'}
            </button>
            <button onClick={() => setStep('bpjs')} className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              Kembali
            </button>
          </div>
        </div>
      )}

      {/* Step 7: Complete */}
      {step === 'complete' && (
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <div className="mb-6">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Pemulangan Selesai!</h2>
            <p className="text-gray-600">Pasien berhasil dipulangkan</p>
          </div>

          <div className="p-4 bg-blue-50 rounded-lg mb-6">
            <p className="text-blue-800">
              Pastikan semua instruksi pemulangan telah dipahami oleh pasien dan keluarga.
              Jangan lupa untuk menyerahkan resep obat dan jadwal follow-up.
            </p>
          </div>

          <button
            onClick={() => window.location.href = '/admissions'}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Kembali ke Daftar Penerimaan
          </button>
        </div>
      )}
    </div>
  );
}
