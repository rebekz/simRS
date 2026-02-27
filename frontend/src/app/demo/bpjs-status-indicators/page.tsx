"use client";

import { useState } from 'react';
import Link from 'next/link';
import { ChevronRight, CheckCircle, RefreshCw } from 'lucide-react';
import {
  BPJSStatusCard,
  BPJSStatusIndicator,
  BPJSPesertaBadge,
  FaskesIndicator,
  useBPJSStatus,
  type BPJSStatusData,
  type BPJSPesertaType,
} from '@/components/bpjs';
import { BPJSStatusBadge } from '@/components/bpjs/BPJSStatusBadge';

export default function BPJSStatusIndicatorsDemoPage() {
  const [selectedCardNumber, setSelectedCardNumber] = useState('1234567890123');
  const [lastStatus, setLastStatus] = useState<BPJSStatusData | null>(null);

  // Demo card numbers with their statuses
  const demoCards = [
    { number: '1234567890123', status: 'active', pesertaType: 'PBI' as BPJSPesertaType },
    { number: '0000000000000', status: 'inactive', pesertaType: 'Non-PBI' as BPJSPesertaType },
    { number: '1111111111111', status: 'expired', pesertaType: 'PBPU' as BPJSPesertaType },
    { number: '2222222222222', status: 'suspended', pesertaType: 'Pegawai Negeri' as BPJSPesertaType },
  ];

  const handleStatusChange = (status: BPJSStatusData) => {
    setLastStatus(status);
    console.log('Status updated:', status);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Breadcrumb */}
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Link href="/demo" className="hover:text-gray-700">Demo</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">BPJS Status Indicators</span>
        </div>

        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            WEB-S-2.3: BPJS Status Indicators Demo
          </h1>
          <p className="text-gray-600 mt-2">
            Real-time BPJS status indicators with badges, peserta types, and faskes eligibility.
          </p>
        </div>

        {/* Acceptance Criteria */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Acceptance Criteria</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.3.1: BPJS badge on patient cards</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.3.2: Color-coded status (active=green, inactive=red)</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.3.3: Status shows peserta type (PBI, Non-PBI)</span>
              </label>
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.3.4: Faskes eligibility indicator</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.3.5: Status updates in real-time (polling)</span>
              </label>
            </div>
          </div>
        </div>

        {/* Section 1: Status Badge Variants */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">1. Status Badge Variants</h2>
          <p className="text-gray-600">
            Color-coded badges for different BPJS membership statuses.
          </p>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex flex-wrap gap-4 mb-6">
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
                <span className="text-sm text-gray-500">NonAktif:</span>
                <BPJSStatusBadge status="inactive" />
              </div>
            </div>

            <h3 className="font-semibold text-gray-900 mb-3">Size Variants</h3>
            <div className="flex flex-wrap items-center gap-4">
              <BPJSStatusBadge status="AKTIF" size="sm" />
              <BPJSStatusBadge status="AKTIF" size="md" />
              <BPJSStatusBadge status="AKTIF" size="lg" />
            </div>
          </div>
        </section>

        {/* Section 2: Peserta Type Badges */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">2. Peserta Type Badges (AC-2.3.3)</h2>
          <p className="text-gray-600">
            Badges showing BPJS participant types.
          </p>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex flex-wrap gap-4">
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">PBI:</span>
                <BPJSPesertaBadge pesertaType="PBI" />
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Non-PBI:</span>
                <BPJSPesertaBadge pesertaType="Non-PBI" />
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">PBPU:</span>
                <BPJSPesertaBadge pesertaType="PBPU" />
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Pegawai Negeri:</span>
                <BPJSPesertaBadge pesertaType="Pegawai Negeri" />
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Pensiunan:</span>
                <BPJSPesertaBadge pesertaType="Pensiunan" />
              </div>
            </div>

            <h3 className="font-semibold text-gray-900 mb-3 mt-6">Size Variants</h3>
            <div className="flex flex-wrap items-center gap-4">
              <BPJSPesertaBadge pesertaType="PBI" size="sm" />
              <BPJSPesertaBadge pesertaType="PBI" size="md" />
              <BPJSPesertaBadge pesertaType="PBI" size="lg" />
            </div>
          </div>
        </section>

        {/* Section 3: Faskes Eligibility Indicator */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">3. Faskes Eligibility Indicator (AC-2.3.4)</h2>
          <p className="text-gray-600">
            Shows whether patient&apos;s registered faskes matches the current facility.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Eligible (Faskes Sesuai)</h3>
              <FaskesIndicator
                eligible={true}
                currentFaskes="RSUD SEHAT SELALU"
                registeredFaskes="RSUD SEHAT SELALU"
                showDetails={true}
              />
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Not Eligible (Faskes Tidak Sesuai)</h3>
              <FaskesIndicator
                eligible={false}
                currentFaskes="RSUD SEHAT SELALU"
                registeredFaskes="PUSKESMAS JAYA"
                showDetails={true}
              />
            </div>
          </div>
        </section>

        {/* Section 4: Status Card with Auto-Refresh */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">4. Status Card with Auto-Refresh (AC-2.3.5)</h2>
          <p className="text-gray-600">
            Comprehensive status card with real-time polling updates.
          </p>

          {/* Card Number Selector */}
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold text-gray-900 mb-3">Select Demo Card Number:</h3>
            <div className="flex flex-wrap gap-2">
              {demoCards.map((card) => (
                <button
                  key={card.number}
                  onClick={() => setSelectedCardNumber(card.number)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedCardNumber === card.number
                      ? 'bg-teal-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <span className="font-mono">{card.number}</span>
                  <span className="ml-2 text-xs opacity-75">({card.status})</span>
                </button>
              ))}
            </div>
          </div>

          {/* Status Indicator with Auto-Refresh */}
          <BPJSStatusIndicator
            cardNumber={selectedCardNumber}
            autoRefresh={true}
            refreshInterval={60000}
            onStatusChange={handleStatusChange}
          />
        </section>

        {/* Section 5: useBPJSStatus Hook Demo */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">5. useBPJSStatus Hook</h2>
          <p className="text-gray-600">
            Custom hook for managing BPJS status with polling in your own components.
          </p>

          <HookDemoCard cardNumber="1234567890123" />
        </section>

        {/* Section 6: Patient Card Integration Example */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">6. Patient Card Integration (AC-2.3.1)</h2>
          <p className="text-gray-600">
            Example of BPJS badges integrated into patient cards.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {demoCards.map((card) => (
              <div key={card.number} className="bg-white rounded-lg shadow p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-gray-900">Pasien Demo</h4>
                    <p className="text-sm text-gray-500 font-mono">{card.number}</p>
                  </div>
                  <BPJSStatusBadge status={card.status === 'active' ? 'AKTIF' : 'NonPST'} size="sm" />
                </div>
                <div className="flex items-center gap-2">
                  <BPJSPesertaBadge pesertaType={card.pesertaType} size="sm" />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Technical Notes */}
        <div className="bg-gray-100 rounded-lg p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Technical Notes</h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700 text-sm">
            <li>Real-time polling every 60 seconds (configurable)</li>
            <li>Color-coded status badges: Green (Active), Red (Inactive), Gray (Expired), Yellow (Suspended)</li>
            <li>Peserta type badges: PBI, Non-PBI, PBPU, Pegawai Negeri, Pensiunan</li>
            <li>Faskes eligibility indicator for referral requirements</li>
            <li>Auto-refresh with manual refresh option</li>
            <li>useBPJSStatus hook for custom integrations</li>
            <li>All components are TypeScript typed</li>
          </ul>
        </div>

        {/* Last Status Log */}
        {lastStatus && (
          <div className="bg-gray-900 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 mb-2">Last Status Update:</h3>
            <pre className="text-green-400 text-sm overflow-x-auto">
              {JSON.stringify(lastStatus, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

// Hook Demo Component
function HookDemoCard({ cardNumber }: { cardNumber: string }) {
  const { status, isLoading, error, refetch } = useBPJSStatus(cardNumber, {
    autoRefresh: true,
    refreshInterval: 30000,
  });

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">Hook Status</h3>
        <button
          onClick={refetch}
          disabled={isLoading}
          className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {isLoading && !status && (
        <p className="text-gray-500">Loading...</p>
      )}

      {error && (
        <p className="text-red-600">{error}</p>
      )}

      {status && (
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Status:</span>
            <span className="font-medium">{status.status}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Peserta Type:</span>
            <span className="font-medium">{status.pesertaType || 'Unknown'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Faskes:</span>
            <span className="font-medium truncate max-w-[200px]">{status.faskes}</span>
          </div>
        </div>
      )}
    </div>
  );
}
