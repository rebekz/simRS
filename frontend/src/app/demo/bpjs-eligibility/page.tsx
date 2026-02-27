"use client";

import { useState } from 'react';
import Link from 'next/link';
import { ChevronRight, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { BPJSVerificationCard } from '@/components/bpjs/BPJSVerificationCard';
import { BPJSStatusBadge } from '@/components/bpjs/BPJSStatusBadge';

export default function BPJSEligibilityDemoPage() {
  const [lastVerification, setLastVerification] = useState<{
    success: boolean;
    data: any;
    message: string;
  } | null>(null);

  const handleVerificationSuccess = (data: any, result: any) => {
    setLastVerification(result);
    console.log('Verification success:', data);
  };

  const handleVerificationError = (error: any) => {
    setLastVerification({
      success: false,
      data: null,
      message: error.message,
    });
    console.log('Verification error:', error);
  };

  const handleVerificationStart = () => {
    console.log('Verification started...');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Breadcrumb */}
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Link href="/demo" className="hover:text-gray-700">Demo</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">BPJS Eligibility Check</span>
        </div>

        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            WEB-S-2.1: BPJS Eligibility Check Demo
          </h1>
          <p className="text-gray-600 mt-2">
            Demonstrasi verifikasi eligibilitas BPJS secara real-time dengan auto-fill.
          </p>
        </div>

        {/* Acceptance Criteria Checklist */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Acceptance Criteria Checklist</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.1.1: Real-time verification with loading indicator</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.1.2: Auto-fill patient data from BPJS response</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.1.3: User-friendly error messages</span>
              </label>
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.1.4: Retry mechanism for failed requests</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.1.5: Audit logging for all BPJS interactions</span>
              </label>
            </div>
          </div>
        </div>

        {/* Component Demo */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">BPJS Verification Card</h2>
          <p className="text-gray-600">
            Komponen ut verifikasi kartu BPJS dengan auto-fill.
          </p>

          <BPJSVerificationCard
            onVerificationSuccess={handleVerificationSuccess}
            onVerificationError={handleVerificationError}
            onVerificationStart={handleVerificationStart}
          />
        </section>

        {/* Status Badge Variants */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">BPJS Status Badge Variants</h2>
          <p className="text-gray-600">
            Badge menampilkan status BPJS dengan different styling.
          </p>

          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">AKTIF:</span>
              <BPJSStatusBadge status="AKTIF" />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">PST Tertanggu:</span>
              <BPJSStatusBadge status="PSTanggu" />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">NonPST:</span>
              <BPJSStatusBadge status="NonPST" />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">Inactive:</span>
              <BPJSStatusBadge status="inactive" />
            </div>
          </div>

          {/* Size Variants */}
          <div className="mt-4">
            <h3 className="font-semibold text-gray-900 mb-2">Size Variants</h3>
            <div className="flex flex-wrap items-center gap-4">
              <BPJSStatusBadge status="AKTIF" size="sm" />
              <BPJSStatusBadge status="AKTIF" size="md" />
              <BPJSStatusBadge status="AKTIF" size="lg" />
            </div>
          </div>
        </section>

        {/* Last Verification Result */}
        {lastVerification && (
          <div className="mt-6">
            <h3 className="font-semibold text-gray-900 mb-4">Last Verification Result</h3>
            <div className="bg-gray-900 text-green-400 rounded-lg p-4 font-mono text-sm">
              <pre className="text-green-300 overflow-x-auto">
                {JSON.stringify(lastVerification, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* Integration Example */}
        <section className="bg-blue-50 rounded-lg p-6 border border-blue-200">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Integration Example</h2>
          <p className="text-sm text-blue-800 mb-3">
            Untuhkan BPJS verification card di halaman pendaftian:
          </p>
          <pre className="bg-gray-900 text-green-400 rounded-lg p-4 text-sm overflow-x-auto">
{`import { BPJSVerificationCard } from '@/components/bpjs';

import { BPJSStatusBadge } from '@/components/bpjs';

// In registration form
&lt;BPJSVerificationCard
  onVerificationSuccess={(data) => {
    // Auto-fill form with BPJS data
    setFormData({
      name: data.nama,
      nik: data.noKart,
      // ... other fields
    });
  }}
  onVerificationError={(error) => {
    showError(error.message);
  }}
/>

// Status display
&lt;BPJSStatusBadge status={patient.bpjsStatus} />
`}
          </pre>
        </section>
      </div>
    </div>
  );
}
