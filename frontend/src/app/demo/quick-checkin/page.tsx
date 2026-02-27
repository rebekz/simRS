"use client";

import { useState } from 'react';
import Link from 'next/link';
import { ChevronRight, CheckCircle } from 'lucide-react';
import { QuickCheckIn, type CheckInData } from '@/components/registration';

export default function QuickCheckInDemoPage() {
  const [lastCheckIn, setLastCheckIn] = useState<CheckInData | null>(null);

  const polyclinics = [
    { code: 'PU', name: 'Poli Umum' },
    { code: 'PS', name: 'Poli Penyakit Dalam' },
    { code: 'PJ', name: 'Poli Jantung' },
    { code: 'PK', name: 'Poli Kandungan' },
    { code: 'PA', name: 'Poli Anak' },
    { code: 'PM', name: 'Poli Mata' },
    { code: 'PT', name: 'Poli THT' },
    { code: 'PG', name: 'Poli Gigi' },
    { code: 'PKU', name: 'Poli Kulit' },
    { code: 'PO', name: 'Poli Orthopedi' },
  ];

  const handleCheckIn = (data: CheckInData) => {
    console.log('Check-in completed:', data);
    setLastCheckIn(data);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Breadcrumb */}
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Link href="/demo" className="hover:text-gray-700">Demo</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Quick Check-In</span>
        </div>

        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            WEB-S-3.2: Returning Patient Quick Check-In
          </h1>
          <p className="text-gray-600 mt-2">
            Quick check-in flow for returning patients in under 30 seconds.
          </p>
        </div>

        {/* Acceptance Criteria */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Acceptance Criteria</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-3.2.1: Patient search bar (RM, BPJS, NIK, name, phone)</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-3.2.2: Keyboard shortcut (Ctrl+K / Cmd+K)</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-3.2.3: Search results with patient info</span>
              </label>
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-3.2.4: Quick check-in modal</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-3.2.5: Pre-fill: today's date, default department</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-3.2.6: Select poli tujuan (dropdown)</span>
              </label>
            </div>
          </div>
        </div>

        {/* Demo Section */}
        <QuickCheckIn
          onCheckIn={handleCheckIn}
          polyclinics={polyclinics}
        />

        {/* Last Check-In Info */}
        {lastCheckIn && (
          <div className="bg-gray-900 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 mb-2">Last Check-In Data:</h3>
            <pre className="text-green-400 text-sm overflow-x-auto">
              {JSON.stringify(lastCheckIn, null, 2)}
            </pre>
          </div>
        )}

        {/* Demo Hint */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <h3 className="font-medium text-amber-800 mb-2">Demo Hints</h3>
          <ul className="text-sm text-amber-700 space-y-1">
            <li>• Try searching with: <code className="bg-amber-100 px-1 rounded">Ahmad</code>, <code className="bg-amber-100 px-1 rounded">MRN-002</code>, or <code className="bg-amber-100 px-1 rounded">000123</code></li>
            <li>• Use <kbd className="px-1 bg-amber-100 rounded">Ctrl+K</kbd> or <kbd className="px-1 bg-amber-100 rounded">Cmd+K</kbd> to focus search</li>
            <li>• Press <kbd className="px-1 bg-amber-100 rounded">Escape</kbd> to clear search</li>
          </ul>
        </div>

        {/* Technical Notes */}
        <div className="bg-gray-100 rounded-lg p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Technical Notes</h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700 text-sm">
            <li>Global search by RM, BPJS, NIK, name, or phone</li>
            <li>Keyboard shortcut Ctrl+K / Cmd+K for quick access</li>
            <li>Search results display patient info and BPJS status</li>
            <li>Quick check-in modal with pre-filled date</li>
            <li>Default polyclinic based on last visit</li>
            <li>Check-in completes in under 30 seconds</li>
            <li>Visit type auto-detected (baru/ulang)</li>
          </ul>
        </div>

        {/* Integration Example */}
        <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Integration Example</h2>
          <pre className="bg-gray-900 text-green-400 rounded-lg p-4 text-sm overflow-x-auto">
{`import { QuickCheckIn } from '@/components/registration';

const polyclinics = [
  { code: 'PU', name: 'Poli Umum' },
  { code: 'PS', name: 'Poli Penyakit Dalam' },
  // ...
];

// In registration page
<QuickCheckIn
  onCheckIn={(data) => {
    // Create visit record
    createVisit(data);
    // Generate queue number
    generateQueue(data.patientId, data.poliTujuan);
    // Print queue ticket
    printTicket(data);
  }}
  polyclinics={polyclinics}
/>`}
          </pre>
        </div>
      </div>
    </div>
  );
}
