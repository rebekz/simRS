"use client";

import { useState } from 'react';
import Link from 'next/link';
import { ChevronRight, CheckCircle, Shield } from 'lucide-react';
import {
  BPJSHistoryLog,
  SEPHistory,
  exportToCSV,
  exportToJSON,
  mockLogEntries,
  mockSEPHistory,
  type BPJSLogEntry,
} from '@/components/admin/BPJSHistory';

export default function BPJSHistoryAuditDemoPage() {
  const [entries, setEntries] = useState<BPJSLogEntry[]>(mockLogEntries);
  const [isAdmin, setIsAdmin] = useState(true);

  const handleRefresh = () => {
    // Simulate refresh
    console.log('Refreshing history...');
  };

  const handleExport = (format: 'csv' | 'json') => {
    if (!isAdmin) {
      alert('Only admins can export data');
      return;
    }

    if (format === 'csv') {
      exportToCSV(entries, `bpjs-history-${new Date().toISOString().split('T')[0]}.csv`);
    } else {
      exportToJSON(entries, `bpjs-history-${new Date().toISOString().split('T')[0]}.json`);
    }
  };

  const handleViewSEPDetails = (item: typeof mockSEPHistory[0]) => {
    alert(`Viewing SEP: ${item.sepNumber}\n\nPatient: ${item.patientName}\nPoli: ${item.polyclinic}\nDoctor: ${item.doctorName}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Breadcrumb */}
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Link href="/demo" className="hover:text-gray-700">Demo</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">BPJS History & Audit</span>
        </div>

        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            WEB-S-2.5: BPJS History & Audit Demo
          </h1>
          <p className="text-gray-600 mt-2">
            BPJS interaction history, SEP records, and audit trail with export functionality.
          </p>
        </div>

        {/* Acceptance Criteria */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Acceptance Criteria</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.5.1: BPJS eligibility check log</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.5.2: SEP creation history</span>
              </label>
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.5.3: API call success/failure rates</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.5.4: Export to CSV (admin only)</span>
              </label>
            </div>
          </div>
        </div>

        {/* Admin Toggle */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className={`w-6 h-6 ${isAdmin ? 'text-teal-600' : 'text-gray-400'}`} />
              <div>
                <p className="font-medium text-gray-900">
                  Admin Mode: {isAdmin ? 'Enabled' : 'Disabled'}
                </p>
                <p className="text-sm text-gray-500">
                  Toggle to test admin-only export functionality
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsAdmin(!isAdmin)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                isAdmin ? 'bg-teal-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  isAdmin ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>

        {/* Section 1: BPJS History Log */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">1. BPJS Interaction Log (AC-2.5.1)</h2>
          <p className="text-gray-600">
            Complete history of all BPJS API interactions with filtering and search.
          </p>

          <BPJSHistoryLog
            entries={entries}
            onRefresh={handleRefresh}
            onExport={isAdmin ? handleExport : undefined}
            showFilters={true}
          />
        </section>

        {/* Section 2: SEP History */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">2. SEP Creation History (AC-2.5.2)</h2>
          <p className="text-gray-600">
            List of all SEP records created for patients.
          </p>

          <SEPHistory
            items={mockSEPHistory}
            onViewDetails={handleViewSEPDetails}
          />
        </section>

        {/* Section 3: Statistics Dashboard */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">3. API Statistics (AC-2.5.3)</h2>
          <p className="text-gray-600">
            Success rates, response times, and call statistics.
          </p>

          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">83.3%</div>
                <div className="text-sm text-gray-500 mt-1">Success Rate</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">6</div>
                <div className="text-sm text-gray-500 mt-1">Total Calls</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600">1</div>
                <div className="text-sm text-gray-500 mt-1">Failed Calls</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">512ms</div>
                <div className="text-sm text-gray-500 mt-1">Avg Response</div>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="text-sm font-medium text-gray-700 mb-4">Calls by Action Type</h4>
              <div className="space-y-3">
                <div className="flex items-center">
                  <span className="text-sm text-gray-600 w-40">Eligibility Check</span>
                  <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: '33%' }}></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 ml-3">2</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-600 w-40">SEP Create</span>
                  <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-green-500 rounded-full" style={{ width: '17%' }}></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 ml-3">1</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-600 w-40">SEP Cancel</span>
                  <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-red-500 rounded-full" style={{ width: '17%' }}></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 ml-3">1</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-600 w-40">Referral Check</span>
                  <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-purple-500 rounded-full" style={{ width: '17%' }}></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 ml-3">1</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-600 w-40">Manual Entry</span>
                  <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-yellow-500 rounded-full" style={{ width: '17%' }}></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 ml-3">1</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 4: Export Demo */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">4. Export Functionality (AC-2.5.4)</h2>
          <p className="text-gray-600">
            Export BPJS history data to CSV or JSON format (admin only).
          </p>

          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className={`p-4 rounded-lg mb-4 ${isAdmin ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200'}`}>
              <p className={`text-sm ${isAdmin ? 'text-green-700' : 'text-yellow-700'}`}>
                {isAdmin
                  ? '✓ You have admin access. Export buttons are enabled.'
                  : '⚠ Admin access required for export functionality.'}
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => handleExport('csv')}
                disabled={!isAdmin}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Export CSV
              </button>
              <button
                onClick={() => handleExport('json')}
                disabled={!isAdmin}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Export JSON
              </button>
            </div>
          </div>
        </section>

        {/* Technical Notes */}
        <div className="bg-gray-100 rounded-lg p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Technical Notes</h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700 text-sm">
            <li>Complete audit trail of all BPJS interactions</li>
            <li>Filterable by action type, status, and date range</li>
            <li>Search by card number, patient name, or user</li>
            <li>Real-time statistics with success rates</li>
            <li>Response time tracking for performance monitoring</li>
            <li>Export to CSV/JSON for external analysis (admin only)</li>
            <li>Expandable details for each log entry</li>
            <li>SEP history with status tracking</li>
          </ul>
        </div>

        {/* Integration Example */}
        <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Integration Example</h2>
          <pre className="bg-gray-900 text-green-400 rounded-lg p-4 text-sm overflow-x-auto">
{`import { BPJSHistoryLog, SEPHistory, exportToCSV } from '@/components/admin/BPJSHistory';

// In admin dashboard
<BPJSHistoryLog
  entries={bpjsLogs}
  onRefresh={fetchLogs}
  onExport={(format) => {
    if (format === 'csv') {
      exportToCSV(entries);
    }
  }}
/>

// SEP History for patient detail page
<SEPHistory
  items={patientSEPs}
  onViewDetails={(sep) => showSEPModal(sep)}
/>`}
          </pre>
        </div>
      </div>
    </div>
  );
}
