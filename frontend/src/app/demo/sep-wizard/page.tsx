"use client";

import { useState } from 'react';
import Link from 'next/link';
import { ChevronRight, CheckCircle } from 'lucide-react';
import { SEPWizard, type SEPFormData } from '@/components/bpjs';
import type { BPJSData } from '@/types';

export default function SEPWizardDemoPage() {
  const [isComplete, setIsComplete] = useState(false);
  const [createdSep, setCreatedSep] = useState<SEPFormData | null>(null);

  // Mock BPJS data for demo
  const mockBpjsData: BPJSData = {
    cardNumber: '0001234567890',
    nik: '3171234567890123',
    nama: 'Ahmad Susanto',
    tanggalLahir: '1985-05-15',
    jenisKelamin: 'L',
    alamat: 'Jl. Sudirman No. 123, Jakarta Selatan',
    status: 'AKTIF',
    kelasRawat: 'KELAS III',
    jenisPeserta: 'PENERIMA BANTUAN IURAN',
    tglMulaiAktif: '2020-01-01',
    tglAkhirAktif: '2027-12-31',
    namaFaskes: 'Klinik Utama Sehat',
    kodeFaskes: '0001',
    noTelepon: '081234567890',
  };

  const handleSubmit = (data: SEPFormData) => {
    console.log('SEP Created:', data);
    setCreatedSep(data);
    setIsComplete(true);
  };

  const handleCancel = () => {
    console.log('SEP Creation Cancelled');
    setIsComplete(false);
    setCreatedSep(null);
  };

  const handleReset = () => {
    setIsComplete(false);
    setCreatedSep(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Breadcrumb */}
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Link href="/demo" className="hover:text-gray-700">Demo</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">SEP Wizard</span>
        </div>

        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            WEB-S-2.2: BPJS SEP Creation Wizard Demo
          </h1>
          <p className="text-gray-600 mt-2">
            Multi-step wizard for creating BPJS SEP (Surat Eligibility Peserta).
          </p>
        </div>

        {/* Acceptance Criteria */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Acceptance Criteria</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.2.1: Multi-step wizard with progress indicators</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.2.2: Auto-populate referral data from BPJS response</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.2.3: Diagnosis/care type selection with ICD-10 search</span>
              </label>
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.2.4: Real-time validation before SEP creation</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.2.5: Audit logging for all SEP operations</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.2.6: PDF generation for SEP document</span>
              </label>
            </div>
          </div>
        </div>

        {/* Demo Section */}
        {!isComplete ? (
          <SEPWizard
            bpjsData={mockBpjsData}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
          />
        ) : (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">SEP Berhasil Dibuat!</h2>
              <p className="text-gray-600 mt-2">
                Surat Eligibilitas Peserta telah berhasil dibuat untuk pasien.
              </p>

              {createdSep && (
                <div className="mt-6 bg-gray-50 rounded-lg p-4 text-left">
                  <h3 className="font-semibold text-gray-900 mb-3">Detail SEP</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Nama Pasien</p>
                      <p className="font-medium">{createdSep.patientName}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">No. Kartu BPJS</p>
                      <p className="font-medium font-mono">{createdSep.bpjsCardNumber}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Tanggal SEP</p>
                      <p className="font-medium">{new Date(createdSep.sepDate).toLocaleDateString('id-ID')}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Jenis Pelayanan</p>
                      <p className="font-medium">{createdSep.serviceType === 'RJ' ? 'Rawat Jalan' : 'Rawat Inap'}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Poli</p>
                      <p className="font-medium">{createdSep.polyclinicCode}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Diagnosis</p>
                      <p className="font-medium">{createdSep.initialDiagnosisName}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Dokter</p>
                      <p className="font-medium">{createdSep.doctorName}</p>
                    </div>
                  </div>
                </div>
              )}

              <button
                onClick={handleReset}
                className="mt-6 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700"
              >
                Buat SEP Baru
              </button>
            </div>
          </div>
        )}

        {/* Technical Notes */}
        <div className="bg-gray-100 rounded-lg p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Technical Notes</h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700 text-sm">
            <li>5-step wizard dengan progress indicators</li>
            <li>Auto-populate data dari verifikasi BPJS</li>
            <li>Validasi real-time sebelum submit</li>
            <li>Simulasi BPJS SEP API (2.5 detik delay)</li>
            <li>Support untuk Rawat Jalan (RJ) dan Rawat Inap (RI)</li>
            <li>Diagnosis search dengan ICD-10 codes</li>
            <li>Pilih dokter dari list</li>
            <li>Cetak SEP ke PDF (downloadable)</li>
            <li>Integrasi dengan audit logging</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
