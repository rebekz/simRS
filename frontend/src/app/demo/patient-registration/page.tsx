"use client";

import { useState } from 'react';
import Link from 'next/link';
import { ChevronRight, CheckCircle } from 'lucide-react';
import {
  PatientRegistrationForm,
  type PatientRegistrationData,
} from '@/components/registration';

export default function PatientRegistrationDemoPage() {
  const [isComplete, setIsComplete] = useState(false);
  const [registeredPatient, setRegisteredPatient] = useState<PatientRegistrationData | null>(null);

  const handleSubmit = (data: PatientRegistrationData) => {
    console.log('Patient registered:', data);
    setRegisteredPatient(data);
    setIsComplete(true);
  };

  const handleReset = () => {
    setIsComplete(false);
    setRegisteredPatient(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Breadcrumb */}
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Link href="/demo" className="hover:text-gray-700">Demo</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Patient Registration</span>
        </div>

        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            WEB-S-3.1: BPJS-First New Patient Registration
          </h1>
          <p className="text-gray-600 mt-2">
            BPJS-first registration flow with auto-fill from BPJS verification.
          </p>
        </div>

        {/* Acceptance Criteria */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Acceptance Criteria</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-3.1.1: BPJS card number is PRIMARY input</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-3.1.2: Verify BPJS button with loading state</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-3.1.3: Auto-fill patient data from BPJS</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-3.1.4: Manual registration as secondary option</span>
              </label>
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-3.1.5: Photo upload (optional, with camera)</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-3.1.6: Emergency contact section</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-3.1.7: Insurance selection (BPJS/Asuransi/Umum)</span>
              </label>
            </div>
          </div>
        </div>

        {/* Demo Section */}
        {!isComplete ? (
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">
              Form Pendaftaran Pasien Baru
            </h2>

            <PatientRegistrationForm
              onSubmit={handleSubmit}
              onCancel={() => console.log('Cancelled')}
            />

            {/* Demo Hint */}
            <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <p className="text-sm text-amber-800">
                <strong>Demo Hint:</strong> Gunakan nomor kartu BPJS <code className="bg-amber-100 px-1 rounded">0001234567890</code> untuk melihat auto-fill dari BPJS.
              </p>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Pasien Berhasil Didaftarkan!</h2>
              <p className="text-gray-600 mt-2">
                Data pasien telah berhasil disimpan dalam sistem.
              </p>

              {registeredPatient && (
                <div className="mt-6 bg-gray-50 rounded-lg p-4 text-left">
                  <h3 className="font-semibold text-gray-900 mb-3">Ringkasan Data Pasien</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Nama</p>
                      <p className="font-medium">{registeredPatient.nama}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">NIK</p>
                      <p className="font-medium font-mono">{registeredPatient.nik}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">No. Telepon</p>
                      <p className="font-medium">{registeredPatient.noTelepon}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Jenis Penjamin</p>
                      <p className="font-medium uppercase">{registeredPatient.insuranceType}</p>
                    </div>
                    {registeredPatient.bpjsVerified && (
                      <div className="col-span-2">
                        <p className="text-gray-500">BPJS</p>
                        <p className="font-medium text-green-600 flex items-center gap-1">
                          <CheckCircle className="w-4 h-4" />
                          Terverifikasi - {registeredPatient.bpjsCardNumber}
                        </p>
                      </div>
                    )}
                    {registeredPatient.emergencyContact.name && (
                      <div className="col-span-2">
                        <p className="text-gray-500">Kontak Darurat</p>
                        <p className="font-medium">
                          {registeredPatient.emergencyContact.name} ({registeredPatient.emergencyContact.relationship})
                          - {registeredPatient.emergencyContact.phone}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              <button
                onClick={handleReset}
                className="mt-6 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700"
              >
                Daftarkan Pasien Baru
              </button>
            </div>
          </div>
        )}

        {/* Technical Notes */}
        <div className="bg-gray-100 rounded-lg p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Technical Notes</h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700 text-sm">
            <li>BPJS card number is the primary input with prominent display</li>
            <li>Auto-fill from BPJS verification results</li>
            <li>Manual registration available as secondary option</li>
            <li>Photo capture via camera or file upload</li>
            <li>Emergency contact section (collapsible)</li>
            <li>Insurance selection: BPJS, Asuransi Swasta, or Umum</li>
            <li>Form validation with error messages</li>
            <li>Loading states for async operations</li>
          </ul>
        </div>

        {/* Integration Example */}
        <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Integration Example</h2>
          <pre className="bg-gray-900 text-green-400 rounded-lg p-4 text-sm overflow-x-auto">
{`import { PatientRegistrationForm } from '@/components/registration';

// In registration page
<PatientRegistrationForm
  onSubmit={(data) => {
    // Save to database
    registerPatient(data);
    // Create queue number
    generateQueueNumber(data);
  }}
  onCancel={() => router.back()}
/>`}
          </pre>
        </div>
      </div>
    </div>
  );
}
