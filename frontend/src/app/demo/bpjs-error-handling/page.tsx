"use client";

import { useState } from 'react';
import Link from 'next/link';
import { ChevronRight, CheckCircle, RefreshCw, AlertTriangle, FileText } from 'lucide-react';
import { BPJSErrorAlert, BPJSErrorDisplay, BPJSErrorToast, useBPJSErrorRetry } from '@/components/bpjs/BPJSErrorDisplay';
import { BPJSManualEntry, type ManualBPJSData } from '@/components/bpjs/BPJSManualEntry';
import {
  BPJSErrorCode,
  BPJSErrorType,
  translateBPJSError,
  type BPJSError,
} from '@/lib/bpjs-errors';
import {
  useBPJSErrorLogging,
  getBPJSAuditLogs,
  clearBPJSAuditLogs,
  formatAuditLogEntry,
} from '@/lib/bpjs-audit';

export default function BPJSErrorHandlingDemoPage() {
  const [selectedError, setSelectedError] = useState<string>('2002');
  const [showManualEntry, setShowManualEntry] = useState(false);
  const [toasts, setToasts] = useState<BPJSError[]>([]);
  const { logError, getLogs, clearLogs } = useBPJSErrorLogging({
    userId: 'demo-user',
    userName: 'Demo User',
  });

  // Demo error scenarios
  const errorScenarios = [
    { code: '2002', label: 'Card Not Found', severity: 'high' },
    { code: '2003', label: 'Card Expired', severity: 'high' },
    { code: '2004', label: 'Card Suspended', severity: 'medium' },
    { code: '3002', label: 'Faskes Mismatch', severity: 'medium' },
    { code: '4001', label: 'Duplicate SEP', severity: 'medium' },
    { code: '5001', label: 'Timeout', severity: 'medium' },
    { code: '5002', label: 'Connection Error', severity: 'high' },
    { code: '5003', label: 'Service Unavailable', severity: 'high' },
    { code: '7001', label: 'Rate Limit', severity: 'low' },
    { code: '9999', label: 'Unknown Error', severity: 'medium' },
  ];

  const currentError = translateBPJSError(selectedError as BPJSErrorCode);

  const handleRetry = async () => {
    console.log('Retrying...');
    await new Promise(resolve => setTimeout(resolve, 2000));
    console.log('Retry complete');
  };

  const handleShowToast = () => {
    setToasts(prev => [...prev, currentError]);
    logError(currentError, { operation: 'demo-toast' });
  };

  const handleDismissToast = (index: number) => {
    setToasts(prev => prev.filter((_, i) => i !== index));
  };

  const handleManualSubmit = (data: ManualBPJSData) => {
    console.log('Manual entry submitted:', data);
    setShowManualEntry(false);
    alert(`Data manual berhasil disimpan!\n\nNama: ${data.nama}\nNo. Kartu: ${data.cardNumber}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Breadcrumb */}
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Link href="/demo" className="hover:text-gray-700">Demo</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">BPJS Error Handling</span>
        </div>

        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            WEB-S-2.4: BPJS Error Handling Demo
          </h1>
          <p className="text-gray-600 mt-2">
            User-friendly error messages, retry mechanisms, and manual entry fallback.
          </p>
        </div>

        {/* Acceptance Criteria */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Acceptance Criteria</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.4.1: User-friendly error messages</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.4.2: Retry button on failures</span>
              </label>
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.4.3: Fallback to manual entry</span>
              </label>
              <label className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-2.4.4: Error logging to audit system</span>
              </label>
            </div>
          </div>
        </div>

        {/* Section 1: Error Messages Demo */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">1. User-Friendly Error Messages (AC-2.4.1)</h2>
          <p className="text-gray-600">
            Select an error scenario to see the user-friendly message.
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Error Selector */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Select Error Scenario</h3>
              <div className="grid grid-cols-2 gap-2">
                {errorScenarios.map((scenario) => (
                  <button
                    key={scenario.code}
                    onClick={() => setSelectedError(scenario.code)}
                    className={`px-3 py-2 rounded-lg text-sm text-left transition-colors ${
                      selectedError === scenario.code
                        ? 'bg-teal-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <span className="font-mono text-xs opacity-75">#{scenario.code}</span>
                    <br />
                    {scenario.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Error Display */}
            <div className="space-y-4">
              <BPJSErrorAlert
                error={currentError}
                onRetry={currentError.retryable ? handleRetry : undefined}
                showRetry={currentError.retryable}
              />

              {/* Raw Error Code */}
              <div className="bg-gray-900 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-400 mb-2">Raw Error Data:</h4>
                <pre className="text-green-400 text-xs overflow-x-auto">
                  {JSON.stringify(currentError, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </section>

        {/* Section 2: Retry Mechanism */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">2. Retry Mechanism (AC-2.4.2)</h2>
          <p className="text-gray-600">
            Retry button with loading state and exponential backoff.
          </p>

          <div className="bg-white rounded-lg shadow p-6">
            <RetryDemo />
          </div>
        </section>

        {/* Section 3: Manual Entry Fallback */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">3. Manual Entry Fallback (AC-2.4.3)</h2>
          <p className="text-gray-600">
            Fallback form when BPJS API is unavailable.
          </p>

          {!showManualEntry ? (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <AlertTriangle className="w-5 h-5 text-yellow-600" />
                <p className="text-gray-700">
                  When BPJS API fails, users can enter data manually.
                </p>
              </div>
              <button
                onClick={() => setShowManualEntry(true)}
                className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
              >
                Show Manual Entry Form
              </button>
            </div>
          ) : (
            <BPJSManualEntry
              reason="BPJS API tidak dapat diakses (simulasi)"
              onSubmit={handleManualSubmit}
              onCancel={() => setShowManualEntry(false)}
              initialData={{ cardNumber: '0001234567890' }}
            />
          )}
        </section>

        {/* Section 4: Error Logging */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">4. Error Logging to Audit (AC-2.4.4)</h2>
          <p className="text-gray-600">
            All BPJS errors are logged to the audit system.
          </p>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Audit Log</h3>
              <div className="flex gap-2">
                <button
                  onClick={handleShowToast}
                  className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                >
                  Log Error
                </button>
                <button
                  onClick={() => clearLogs()}
                  className="px-3 py-1.5 bg-gray-200 text-gray-700 rounded text-sm hover:bg-gray-300"
                >
                  Clear
                </button>
              </div>
            </div>

            <div className="bg-gray-900 rounded-lg p-4 max-h-64 overflow-y-auto">
              {getLogs().length === 0 ? (
                <p className="text-gray-500 text-sm">No audit logs yet. Click "Log Error" to add one.</p>
              ) : (
                <div className="space-y-2">
                  {getLogs().map((entry) => (
                    <div
                      key={entry.id}
                      className={`p-2 rounded text-sm ${
                        entry.status === 'error'
                          ? 'bg-red-900/50 text-red-300'
                          : entry.status === 'warning'
                          ? 'bg-yellow-900/50 text-yellow-300'
                          : 'bg-green-900/50 text-green-300'
                      }`}
                    >
                      <div className="font-mono text-xs opacity-75">
                        {new Date(entry.timestamp).toLocaleString('id-ID')}
                      </div>
                      <div>{entry.action}: {entry.details.message}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Section 5: Toast Notifications */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">5. Toast Notifications</h2>
          <p className="text-gray-600">
            Quick error notifications with auto-dismiss.
          </p>

          <div className="bg-white rounded-lg shadow p-6">
            <button
              onClick={handleShowToast}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
            >
              Show Toast Notification
            </button>
          </div>
        </section>

        {/* Technical Notes */}
        <div className="bg-gray-100 rounded-lg p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Technical Notes</h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700 text-sm">
            <li>Error codes mapped to user-friendly Indonesian messages</li>
            <li>Retry with exponential backoff (1s, 2s, 4s...)</li>
            <li>Maximum 3 retry attempts by default</li>
            <li>Manual entry includes audit trail note</li>
            <li>All errors logged with timestamp, user, and context</li>
            <li>Error severity classification: Low, Medium, High, Critical</li>
            <li>Toast notifications auto-dismiss after 5 seconds</li>
          </ul>
        </div>
      </div>

      {/* Toast Notifications */}
      {toasts.map((toast, index) => (
        <BPJSErrorToast
          key={`toast-${index}`}
          error={toast}
          onRetry={toast.retryable ? handleRetry : undefined}
          onDismiss={() => handleDismissToast(index)}
          autoDismiss={true}
          dismissAfter={5000}
        />
      ))}
    </div>
  );
}

// Retry Demo Component
function RetryDemo() {
  const [attemptCount, setAttemptCount] = useState(0);

  const simulateBPJSCall = async (): Promise<string> => {
    // Simulate API that fails first 2 times
    setAttemptCount(prev => prev + 1);
    await new Promise(resolve => setTimeout(resolve, 1500));

    if (attemptCount < 2) {
      throw new Error('Simulated BPJS API failure');
    }

    return 'Success!';
  };

  const { execute, isRetrying, attempt, error, reset } = useBPJSErrorRetry(
    simulateBPJSCall,
    {
      maxAttempts: 3,
      onSuccess: (result) => {
        console.log('Success:', result);
        alert('BPJS API call succeeded after ' + (attempt + 1) + ' attempts!');
      },
      onError: (err) => {
        console.error('All retries failed:', err);
      },
    }
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">
            Click to simulate a BPJS API call with retry logic.
          </p>
          <p className="text-xs text-gray-500 mt-1">
            (Demo: Will fail first 2 times, succeed on 3rd attempt)
          </p>
        </div>
        <button
          onClick={() => {
            setAttemptCount(0);
            reset();
            execute();
          }}
          disabled={isRetrying}
          className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50 flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${isRetrying ? 'animate-spin' : ''}`} />
          {isRetrying ? `Retrying (${attempt + 1}/3)...` : 'Test Retry'}
        </button>
      </div>

      {error && (
        <BPJSErrorAlert
          error={error}
          onRetry={async () => {
            setAttemptCount(0);
            reset();
            await execute();
          }}
        />
      )}

      {attemptCount >= 3 && !error && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <span className="text-green-800">API call succeeded after {attemptCount} attempts!</span>
        </div>
      )}
    </div>
  );
}
