"use client";

import React, { useState, useEffect } from 'react';

// Types
interface Patient {
  id: number;
  full_name: string;
  mrn: string;
}

interface Bed {
  bed_id: number;
  bed_number: string;
  room_number: string;
  room_class: string;
  ward_id: number;
  ward_name: string;
  bed_type: string;
  floor: number;
  gender_type: string;
}

interface AdmissionOrder {
  patient_id: number;
  doctor_id: number;
  admission_type: string;
  requested_room_class?: string;
  requested_ward_id?: number;
  priority: string;
  chief_complaint: string;
  diagnosis?: string;
  admission_reason: string;
  expected_discharge_date?: string;
  notes?: string;
}

const ADMISSION_TYPES = [
  { value: 'emergency', label: 'Gawat Darurat (UGD)' },
  { value: 'urgent', label: 'Gawat' },
  { value: 'elective', label: 'Rencana' },
  { value: 'transfer', label: 'Rujukan' },
];

const PRIORITIES = [
  { value: 'emergency', label: 'DARURAT' },
  { value: 'urgent', label: 'GAWAT' },
  { value: 'routine', label: 'ROUTIN' },
];

const ROOM_CLASSES = [
  { value: 'vvip', label: 'VVIP' },
  { value: 'vip', label: 'VIP' },
  { value: '1', label: 'Kelas 1' },
  { value: '2', label: 'Kelas 2' },
  { value: '3', label: 'Kelas 3' },
];

export default function AdmissionWorkflow() {
  const [step, setStep] = useState<'select-patient' | 'order-details' | 'select-bed' | 'confirm'>('select-patient');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [orderDetails, setOrderDetails] = useState<Partial<AdmissionOrder>>({});
  const [selectedBed, setSelectedBed] = useState<Bed | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [patients, setPatients] = useState<Patient[]>([]);
  const [availableBeds, setAvailableBeds] = useState<Bed[]>([]);
  const [filters, setFilters] = useState({ room_class: '', ward_id: '' });

  useEffect(() => {
    if (step === 'select-patient' && searchTerm.length >= 2) {
      searchPatients();
    }
  }, [searchTerm, step]);

  useEffect(() => {
    if (step === 'select-bed') {
      fetchAvailableBeds();
    }
  }, [step, filters]);

  async function searchPatients() {
    try {
      const response = await fetch(`/api/v1/patients?search=${searchTerm}&limit=20`);
      const data = await response.json();
      setPatients(data.patients || []);
    } catch (error) {
      console.error('Failed to search patients:', error);
    }
  }

  async function fetchAvailableBeds() {
    setLoading(true);
    try {
      let url = '/api/v1/admission/available-beds';
      const params = new URLSearchParams();
      if (filters.room_class) params.append('room_class', filters.room_class);
      if (filters.ward_id) params.append('ward_id', filters.ward_id);
      if (params.toString()) url += `?${params}`;

      const response = await fetch(url);
      const beds = await response.json();
      setAvailableBeds(beds);
    } catch (error) {
      console.error('Failed to fetch available beds:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit() {
    setLoading(true);
    try {
      // Create admission order
      const orderResponse = await fetch('/api/v1/admission/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...orderDetails,
          patient_id: selectedPatient?.id,
          expected_discharge_date: orderDetails.expected_discharge_date || undefined,
        }),
      });

      if (!orderResponse.ok) {
        throw new Error('Failed to create admission order');
      }

      const order = await orderResponse.json();

      // Assign bed if selected
      if (selectedBed) {
        await fetch(`/api/v1/admission/orders/${order.id}/assign-bed`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            admission_id: order.id,
            bed_id: selectedBed.bed_id,
          }),
        });
      }

      alert('Pasien berhasil diterima!');
      resetForm();
    } catch (error) {
      console.error('Failed to admit patient:', error);
      alert('Gagal melakukan penerimaan pasien');
    } finally {
      setLoading(false);
    }
  }

  function resetForm() {
    setStep('select-patient');
    setSelectedPatient(null);
    setOrderDetails({});
    setSelectedBed(null);
    setSearchTerm('');
    setFilters({ room_class: '', ward_id: '' });
  }

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Penerimaan Pasien Rawat Inap</h1>
        <p className="text-gray-600">Workflow penerimaan pasien ke ruang rawat inap</p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {[
            { num: 1, label: 'Pilih Pasien', step: 'select-patient' },
            { num: 2, label: 'Detail Penerimaan', step: 'order-details' },
            { num: 3, label: 'Pilih Tempat Tidur', step: 'select-bed' },
            { num: 4, label: 'Konfirmasi', step: 'confirm' },
          ].map((s) => (
            <React.Fragment key={s.step}>
              <div className="flex items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  step === s.step ? 'bg-blue-600 text-white' :
                  ['select-patient', 'order-details', 'select-bed', 'confirm'].indexOf(step) > ['select-patient', 'order-details', 'select-bed', 'confirm'].indexOf(s.step)
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {['select-patient', 'order-details', 'select-bed', 'confirm'].indexOf(step) > ['select-patient', 'order-details', 'select-bed', 'confirm'].indexOf(s.step) ? '✓' : s.num}
                </div>
                <span className={`ml-2 font-medium text-sm ${
                  step === s.step ? 'text-blue-600' :
                  ['select-patient', 'order-details', 'select-bed', 'confirm'].indexOf(step) > ['select-patient', 'order-details', 'select-bed', 'confirm'].indexOf(s.step)
                    ? 'text-green-600'
                    : 'text-gray-400'
                }`}>{s.label}</span>
              </div>
              {s.num < 4 && (
                <div className="flex-1 h-1 mx-4 bg-gray-200">
                  <div className={`h-full ${
                    ['select-patient', 'order-details', 'select-bed', 'confirm'].indexOf(step) > ['select-patient', 'order-details', 'select-bed', 'confirm'].indexOf(s.step)
                      ? 'bg-green-500'
                      : 'bg-gray-200'
                  }`} style={{ width: ['select-patient', 'order-details', 'select-bed', 'confirm'].indexOf(step) > ['select-patient', 'order-details', 'select-bed', 'confirm'].indexOf(s.step) ? '100%' : '0%' }}></div>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Step 1: Select Patient */}
      {step === 'select-patient' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Pilih Pasien</h2>
          <input
            type="text"
            placeholder="Cari pasien berdasarkan nama atau MRN (minimal 2 karakter)..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {patients.length > 0 && (
            <div className="mt-4 space-y-2 max-h-96 overflow-y-auto">
              {patients.map((patient) => (
                <div
                  key={patient.id}
                  onClick={() => { setSelectedPatient(patient); setStep('order-details'); }}
                  className="p-4 border border-gray-200 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors"
                >
                  <div className="font-semibold text-gray-900">{patient.full_name}</div>
                  <div className="text-sm text-gray-600">MRN: {patient.mrn}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Step 2: Order Details */}
      {step === 'order-details' && selectedPatient && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Detail Penerimaan</h2>
            <button onClick={() => setStep('select-patient')} className="text-blue-600 hover:text-blue-800">← Kembali</button>
          </div>

          <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-sm font-semibold text-blue-900">Pasien Terpilih:</div>
            <div className="text-blue-800">{selectedPatient.full_name} (MRN: {selectedPatient.mrn})</div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tipe Penerimaan *</label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                value={orderDetails.admission_type || ''}
                onChange={(e) => setOrderDetails({ ...orderDetails, admission_type: e.target.value })}
              >
                <option value="">Pilih tipe...</option>
                {ADMISSION_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Prioritas *</label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                value={orderDetails.priority || ''}
                onChange={(e) => setOrderDetails({ ...orderDetails, priority: e.target.value })}
              >
                {PRIORITIES.map((p) => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Kelas Kamar (opsional)</label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                value={orderDetails.requested_room_class || ''}
                onChange={(e) => setOrderDetails({ ...orderDetails, requested_room_class: e.target.value || undefined })}
              >
                <option value="">Semua kelas</option>
                {ROOM_CLASSES.map((rc) => (
                  <option key={rc.value} value={rc.value}>{rc.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Perkiraan Tanggal Pulang</label>
              <input
                type="date"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                value={orderDetails.expected_discharge_date || ''}
                onChange={(e) => setOrderDetails({ ...orderDetails, expected_discharge_date: e.target.value || undefined })}
                min={new Date().toISOString().split('T')[0]}
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Keluhan Utama *</label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                value={orderDetails.chief_complaint || ''}
                onChange={(e) => setOrderDetails({ ...orderDetails, chief_complaint: e.target.value })}
                placeholder="Contoh: Nyeri dada sesak napas"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Diagnosa Awal</label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                value={orderDetails.diagnosis || ''}
                onChange={(e) => setOrderDetails({ ...orderDetails, diagnosis: e.target.value || undefined })}
                placeholder="Contoh: Sindrom koroner akut"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Alasan Masuk *</label>
              <textarea
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                rows={3}
                value={orderDetails.admission_reason || ''}
                onChange={(e) => setOrderDetails({ ...orderDetails, admission_reason: e.target.value })}
                placeholder="Jelaskan alasan pasien perlu dirawat..."
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Catatan Tambahan</label>
              <textarea
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                rows={2}
                value={orderDetails.notes || ''}
                onChange={(e) => setOrderDetails({ ...orderDetails, notes: e.target.value || undefined })}
                placeholder="Catatan tambahan..."
              />
            </div>
          </div>

          <div className="mt-6 flex gap-4">
            <button
              onClick={() => setStep('select-bed')}
              disabled={!orderDetails.admission_type || !orderDetails.chief_complaint || !orderDetails.admission_reason}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-semibold"
            >
              Lanjut
            </button>
            <button onClick={() => setStep('select-patient')} className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              Kembali
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Select Bed */}
      {step === 'select-bed' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Pilih Tempat Tidur</h2>
            <button onClick={() => setStep('order-details')} className="text-blue-600 hover:text-blue-800">← Kembali</button>
          </div>

          <div className="mb-4 flex gap-4">
            <select
              className="px-4 py-2 border border-gray-300 rounded-lg"
              value={filters.room_class}
              onChange={(e) => setFilters({ ...filters, room_class: e.target.value })}
            >
              <option value="">Semua Kelas</option>
              {ROOM_CLASSES.map((rc) => (
                <option key={rc.value} value={rc.value}>{rc.label}</option>
              ))}
            </select>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : availableBeds.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Tidak ada tempat tidur tersedia dengan filter yang dipilih
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
              {availableBeds.map((bed) => (
                <div
                  key={bed.bed_id}
                  onClick={() => { setSelectedBed(bed); setStep('confirm'); }}
                  className="p-4 border-2 border-green-300 bg-green-50 rounded-lg hover:shadow-lg cursor-pointer transition-all"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className="text-lg font-bold text-gray-900">{bed.bed_number}</div>
                      <div className="text-sm text-gray-600">Kamar {bed.room_number}</div>
                    </div>
                    <span className="px-2 py-1 bg-green-500 text-white rounded text-xs">Tersedia</span>
                  </div>
                  <div className="text-sm text-gray-700">
                    <div>Kelas: {bed.room_class}</div>
                    <div>Lantai: {bed.floor}</div>
                    <div>Ward: {bed.ward_name}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Step 4: Confirm */}
      {step === 'confirm' && selectedPatient && selectedBed && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Konfirmasi Penerimaan</h2>
            <button onClick={() => setStep('select-bed')} className="text-blue-600 hover:text-blue-800">← Kembali</button>
          </div>

          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h3 className="font-semibold text-blue-900 mb-2">Pasien</h3>
              <div className="text-blue-800">
                <div>Nama: {selectedPatient.full_name}</div>
                <div>MRN: {selectedPatient.mrn}</div>
              </div>
            </div>

            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <h3 className="font-semibold text-green-900 mb-2">Tempat Tidur</h3>
              <div className="text-green-800">
                <div>Nomor: {selectedBed.bed_number}</div>
                <div>Kamar: {selectedBed.room_number}</div>
                <div>Kelas: {selectedBed.room_class}</div>
                <div>Ward: {selectedBed.ward_name}</div>
              </div>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">Detail Penerimaan</h3>
              <div className="text-gray-700 space-y-1">
                <div><strong>Tipe:</strong> {ADMISSION_TYPES.find(t => t.value === orderDetails.admission_type)?.label}</div>
                <div><strong>Prioritas:</strong> {PRIORITIES.find(p => p.value === orderDetails.priority)?.label}</div>
                <div><strong>Keluhan Utama:</strong> {orderDetails.chief_complaint}</div>
                {orderDetails.diagnosis && <div><strong>Diagnosa:</strong> {orderDetails.diagnosis}</div>}
                <div><strong>Alasan:</strong> {orderDetails.admission_reason}</div>
                {orderDetails.expected_discharge_date && (
                  <div><strong>Perkiraan Pulang:</strong> {new Date(orderDetails.expected_discharge_date).toLocaleDateString('id-ID')}</div>
                )}
              </div>
            </div>
          </div>

          <div className="mt-6 flex gap-4">
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-semibold"
            >
              {loading ? 'Memproses...' : 'Konfirmasi Penerimaan'}
            </button>
            <button onClick={resetForm} className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              Batal
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
