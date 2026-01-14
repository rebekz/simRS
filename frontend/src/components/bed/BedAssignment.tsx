"use client";

import React, { useState, useEffect } from 'react';

// Types
interface Patient {
  id: number;
  full_name: string;
  mrn: string;
}

interface Bed {
  id: number;
  bed_number: string;
  room_number: string;
  room_class: string;
  ward_id: number;
  bed_type: string;
  status: string;
}

interface AssignmentRequest {
  patient_id: number;
  bed_id: number;
  admission_id?: number;
  expected_discharge_date?: string;
  notes?: string;
  assign_for_isolation: boolean;
}

const ROOM_CLASS_NAMES: Record<string, string> = {
  'vvip': 'VVIP',
  'vip': 'VIP',
  '1': 'Kelas 1',
  '2': 'Kelas 2',
  '3': 'Kelas 3',
};

export default function BedAssignment() {
  const [step, setStep] = useState<'select-patient' | 'select-bed' | 'confirm'>('select-patient');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [selectedBed, setSelectedBed] = useState<Bed | null>(null);
  const [notes, setNotes] = useState('');
  const [isolation, setIsolation] = useState(false);
  const [expectedDischarge, setExpectedDischarge] = useState('');
  const [loading, setLoading] = useState(false);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [availableBeds, setAvailableBeds] = useState<Bed[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [wardFilter, setWardFilter] = useState<number | null>(null);
  const [classFilter, setClassFilter] = useState<string | null>(null);

  useEffect(() => {
    if (step === 'select-patient') {
      fetchPatients();
    }
  }, [step, searchTerm]);

  useEffect(() => {
    if (step === 'select-bed') {
      fetchAvailableBeds();
    }
  }, [step, wardFilter, classFilter]);

  async function fetchPatients() {
    try {
      const url = searchTerm
        ? `/api/v1/patients?search=${searchTerm}&limit=20`
        : `/api/v1/patients?limit=20`;
      const response = await fetch(url);
      const data = await response.json();
      setPatients(data.patients || []);
    } catch (error) {
      console.error('Failed to fetch patients:', error);
    }
  }

  async function fetchAvailableBeds() {
    try {
      let url = '/api/v1/bed/availability?limit=100';
      if (wardFilter) url += `&ward_id=${wardFilter}`;
      if (classFilter) url += `&room_class=${classFilter}`;

      const response = await fetch(url);
      const data = await response.json();
      setAvailableBeds(data.beds || []);
    } catch (error) {
      console.error('Failed to fetch available beds:', error);
    }
  }

  async function handleAssignBed() {
    if (!selectedPatient || !selectedBed) return;

    setLoading(true);
    try {
      const request: AssignmentRequest = {
        patient_id: selectedPatient.id,
        bed_id: selectedBed.id,
        expected_discharge_date: expectedDischarge || undefined,
        notes: notes || undefined,
        assign_for_isolation: isolation,
      };

      const response = await fetch('/api/v1/bed/assignments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error('Failed to assign bed');
      }

      alert('Pasien berhasil diassign ke tempat tidur');
      resetForm();
    } catch (error) {
      console.error('Failed to assign bed:', error);
      alert('Gagal melakukan assignment tempat tidur');
    } finally {
      setLoading(false);
    }
  }

  function resetForm() {
    setStep('select-patient');
    setSelectedPatient(null);
    setSelectedBed(null);
    setNotes('');
    setIsolation(false);
    setExpectedDischarge('');
    setSearchTerm('');
    setWardFilter(null);
    setClassFilter(null);
  }

  function handlePatientSelect(patient: Patient) {
    setSelectedPatient(patient);
    setStep('select-bed');
  }

  function handleBedSelect(bed: Bed) {
    setSelectedBed(bed);
    setStep('confirm');
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Assignment Tempat Tidur</h1>
        <p className="text-gray-600">Assign pasien ke tempat tidur yang tersedia</p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              step === 'select-patient' ? 'bg-blue-600 text-white' : 'bg-green-500 text-white'
            }`}>
              {step === 'select-patient' ? '1' : '✓'}
            </div>
            <span className={`ml-2 font-medium ${
              step === 'select-patient' ? 'text-blue-600' : 'text-green-600'
            }`}>Pilih Pasien</span>
          </div>
          <div className="flex-1 h-1 mx-4 bg-gray-200">
            <div className={`h-full ${
              step !== 'select-patient' ? 'bg-green-500' : 'bg-gray-200'
            }`} style={{ width: step !== 'select-patient' ? '100%' : '0%' }}></div>
          </div>
          <div className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              step === 'select-bed' ? 'bg-blue-600 text-white' :
              step === 'confirm' ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-600'
            }`}>
              {step === 'select-bed' ? '2' : step === 'confirm' ? '✓' : '2'}
            </div>
            <span className={`ml-2 font-medium ${
              step === 'select-bed' ? 'text-blue-600' :
              step === 'confirm' ? 'text-green-600' : 'text-gray-400'
            }`}>Pilih Tempat Tidur</span>
          </div>
          <div className="flex-1 h-1 mx-4 bg-gray-200">
            <div className={`h-full ${
              step === 'confirm' ? 'bg-green-500' : 'bg-gray-200'
            }`} style={{ width: step === 'confirm' ? '100%' : '0%' }}></div>
          </div>
          <div className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              step === 'confirm' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
            }`}>
              {step === 'confirm' ? '3' : '3'}
            </div>
            <span className={`ml-2 font-medium ${
              step === 'confirm' ? 'text-blue-600' : 'text-gray-400'
            }`}>Konfirmasi</span>
          </div>
        </div>
      </div>

      {/* Step 1: Select Patient */}
      {step === 'select-patient' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Pilih Pasien</h2>
          <div className="mb-4">
            <input
              type="text"
              placeholder="Cari pasien berdasarkan nama atau MRN..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {patients.map(patient => (
              <div
                key={patient.id}
                onClick={() => handlePatientSelect(patient)}
                className="p-4 border border-gray-200 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors"
              >
                <div className="font-semibold text-gray-900">{patient.full_name}</div>
                <div className="text-sm text-gray-600">MRN: {patient.mrn}</div>
              </div>
            ))}
            {patients.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                {searchTerm ? 'Tidak ada pasien ditemukan' : 'Masukkan kata kunci pencarian'}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Step 2: Select Bed */}
      {step === 'select-bed' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Pilih Tempat Tidur</h2>
            <button
              onClick={() => setStep('select-patient')}
              className="text-blue-600 hover:text-blue-800"
            >
              ← Kembali
            </button>
          </div>

          <div className="mb-4 flex gap-4">
            <select
              className="px-4 py-2 border border-gray-300 rounded-lg"
              value={wardFilter || ''}
              onChange={(e) => setWardFilter(e.target.value ? parseInt(e.target.value) : null)}
            >
              <option value="">Semua Ruang Rawat</option>
              <option value="1">Ruang Rawat 1</option>
              <option value="2">Ruang Rawat 2</option>
              <option value="3">Ruang Rawat 3</option>
            </select>
            <select
              className="px-4 py-2 border border-gray-300 rounded-lg"
              value={classFilter || ''}
              onChange={(e) => setClassFilter(e.target.value || null)}
            >
              <option value="">Semua Kelas</option>
              <option value="vvip">VVIP</option>
              <option value="vip">VIP</option>
              <option value="1">Kelas 1</option>
              <option value="2">Kelas 2</option>
              <option value="3">Kelas 3</option>
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
            {availableBeds.map(bed => (
              <div
                key={bed.id}
                onClick={() => handleBedSelect(bed)}
                className="p-4 border-2 border-green-300 bg-green-50 rounded-lg hover:shadow-lg cursor-pointer transition-all"
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <div className="text-lg font-bold text-gray-900">{bed.bed_number}</div>
                    <div className="text-sm text-gray-600">Kamar {bed.room_number}</div>
                  </div>
                  <span className="px-2 py-1 bg-green-500 text-white rounded text-xs">
                    Tersedia
                  </span>
                </div>
                <div className="text-sm text-gray-700">
                  <div>Kelas: {ROOM_CLASS_NAMES[bed.room_class] || bed.room_class}</div>
                  <div>Tipe: {bed.bed_type}</div>
                </div>
              </div>
            ))}
            {availableBeds.length === 0 && (
              <div className="col-span-3 text-center py-8 text-gray-500">
                Tidak ada tempat tidur tersedia dengan filter yang dipilih
              </div>
            )}
          </div>

          {/* Selected Patient Summary */}
          <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-sm font-semibold text-blue-900">Pasien Terpilih:</div>
            <div className="text-blue-800">{selectedPatient?.full_name} (MRN: {selectedPatient?.mrn})</div>
          </div>
        </div>
      )}

      {/* Step 3: Confirm */}
      {step === 'confirm' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Konfirmasi Assignment</h2>
            <button
              onClick={() => setStep('select-bed')}
              className="text-blue-600 hover:text-blue-800"
            >
              ← Kembali
            </button>
          </div>

          <div className="space-y-4">
            {/* Patient Summary */}
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h3 className="font-semibold text-blue-900 mb-2">Pasien</h3>
              <div className="text-blue-800">
                <div>Nama: {selectedPatient?.full_name}</div>
                <div>MRN: {selectedPatient?.mrn}</div>
              </div>
            </div>

            {/* Bed Summary */}
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <h3 className="font-semibold text-green-900 mb-2">Tempat Tidur</h3>
              <div className="text-green-800">
                <div>Nomor: {selectedBed?.bed_number}</div>
                <div>Kamar: {selectedBed?.room_number}</div>
                <div>Kelas: {ROOM_CLASS_NAMES[selectedBed?.room_class || '']}</div>
                <div>Tipe: {selectedBed?.bed_type}</div>
              </div>
            </div>

            {/* Additional Options */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Perkiraan Tanggal Pulang
                </label>
                <input
                  type="date"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  value={expectedDischarge}
                  onChange={(e) => setExpectedDischarge(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Catatan
                </label>
                <textarea
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  rows={3}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Catatan tambahan..."
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="isolation"
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  checked={isolation}
                  onChange={(e) => setIsolation(e.target.checked)}
                />
                <label htmlFor="isolation" className="ml-2 text-sm text-gray-700">
                  Assign untuk isolasi
                </label>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 pt-4">
              <button
                onClick={handleAssignBed}
                disabled={loading}
                className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-semibold"
              >
                {loading ? 'Memproses...' : 'Konfirmasi Assignment'}
              </button>
              <button
                onClick={resetForm}
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Batal
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
