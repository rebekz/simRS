"use client";

import { useState } from 'react';
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';
import { TriageTimer } from '@/components/emergency/TriageTimer';
import { TriageTimerMini } from '@/components/emergency/TriageTimerMini';

export default function TriageTimerDemoPage() {
  const [timerEvents, setTimerEvents] = useState<string[]>([]);

  const logEvent = (event: string) => {
    const timestamp = new Date().toLocaleTimeString('id-ID');
    setTimerEvents(prev => [...prev, `[${timestamp}] ${event}`]);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Breadcrumb */}
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Link href="/demo" className="hover:text-gray-700">Demo</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Triage Timer</span>
        </div>

        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            WEB-S-5.6: Triage Timer Demo
          </h1>
          <p className="text-gray-600 mt-2">
            Timer prominentlyang memastikan triage selesai dalam &lt;2 menit.
          </p>
        </div>

        {/* Acceptance Criteria Checklist */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Acceptance Criteria Checklist</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-5.6.1: Timer visible and prominent on triage page</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-5.6.2: Timer starts when triage begins</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-5.6.3: Visual warning at 90 seconds (yellow)</span>
              </label>
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-5.6.4: Visual/alert at 120 seconds (red)</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-5.6.5: Timer can be paused/resumed</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-5.6.6: Timer resets on new patient</span>
              </label>
            </div>
          </div>
        </div>

        {/* Section 1: Size Variants */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">1. Size Variants</h2>
          <p className="text-gray-600">
            Timer tersedia dalam berbagai ukuran untuk berbagai konteks.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Small */}
            <div className="bg-white rounded-lg p-6 shadow">
              <h3 className="font-semibold text-gray-900 mb-4">Small</h3>
              <TriageTimer
                size="sm"
                showControls={true}
                onStart={() => logEvent('Small timer: Started')}
                onPause={() => logEvent('Small timer: Paused')}
                onReset={() => logEvent('Small timer: Reset')}
                onWarning={() => logEvent('Small timer: Warning threshold reached')}
                onCritical={() => logEvent('Small timer: Critical threshold reached')}
              />
            </div>

            {/* Medium */}
            <div className="bg-white rounded-lg p-6 shadow">
              <h3 className="font-semibold text-gray-900 mb-4">Medium</h3>
              <TriageTimer
                size="md"
                showControls={true}
                onStart={() => logEvent('Medium timer: Started')}
                onPause={() => logEvent('Medium timer: Paused')}
                onReset={() => logEvent('Medium timer: Reset')}
                onWarning={() => logEvent('Medium timer: Warning threshold reached')}
                onCritical={() => logEvent('Medium timer: Critical threshold reached')}
              />
            </div>

            {/* Large (Default) */}
            <div className="bg-white rounded-lg p-6 shadow">
              <h3 className="font-semibold text-gray-900 mb-4">Large (Default)</h3>
              <TriageTimer
                size="lg"
                showControls={true}
                onStart={() => logEvent('Large timer: Started')}
                onPause={() => logEvent('Large timer: Paused')}
                onReset={() => logEvent('Large timer: Reset')}
                onWarning={() => logEvent('Large timer: Warning threshold reached')}
                onCritical={() => logEvent('Large timer: Critical threshold reached')}
              />
            </div>

            {/* Extra Large */}
            <div className="bg-white rounded-lg p-6 shadow">
              <h3 className="font-semibold text-gray-900 mb-4">Extra Large</h3>
              <TriageTimer
                size="xl"
                showControls={true}
                onStart={() => logEvent('XL timer: Started')}
                onPause={() => logEvent('XL timer: Paused')}
                onReset={() => logEvent('XL timer: Reset')}
                onWarning={() => logEvent('XL timer: Warning threshold reached')}
                onCritical={() => logEvent('XL timer: Critical threshold reached')}
              />
            </div>
          </div>
        </section>

        {/* Section 2: Mini Timer for Headers */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">2. Mini Timer (for Headers/Navbars)</h2>
          <p className="text-gray-600">
            Versi kompak untuk ditampilkan di header atau status bar.
          </p>

          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="font-semibold text-gray-900 mb-4">Mini Timer Display</h3>

            {/* Simulated Header */}
            <div className="bg-gray-800 text-white px-4 py-3 rounded-t-lg flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="font-bold">SIMRS</span>
                <span className="text-gray-400">|</span>
                <span>Emergency Triage</span>
              </div>
              <div className="flex items-center gap-4">
                <TriageTimerMini isRunning={false} showLabel={true} />
                <span className="text-gray-400">User: Dr. Ahmad</span>
              </div>
            </div>

            {/* Running state examples */}
            <div className="bg-gray-100 p-4 rounded-b-lg space-y-3">
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600 w-24">Idle:</span>
                <TriageTimerMini isRunning={false} initialTime={0} />
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600 w-24">Running:</span>
                <TriageTimerMini isRunning={true} initialTime={45} />
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600 w-24">Warning (90s):</span>
                <TriageTimerMini isRunning={true} initialTime={90} />
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600 w-24">Critical (120s):</span>
                <TriageTimerMini isRunning={true} initialTime={120} />
              </div>
            </div>
          </div>
        </section>

        {/* Section 3: Custom Thresholds Demo */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">3. Custom Thresholds (Demo: 10s/15s)</h2>
          <p className="text-gray-600">
            Versi dengan threshold singkat untuk testing cepat (10 detik warning, 15 detik critical).
          </p>

          <div className="bg-white rounded-lg p-6 shadow">
            <TriageTimer
              size="lg"
              warningThreshold={10}
              criticalThreshold={15}
              showControls={true}
              label="Demo Timer (10s/15s)"
              onStart={() => logEvent('Demo timer: Started')}
              onPause={() => logEvent('Demo timer: Paused')}
              onReset={() => logEvent('Demo timer: Reset')}
              onWarning={() => logEvent('Demo timer: ⚠️ WARNING at 10 seconds!')}
              onCritical={() => logEvent('Demo timer: 🚨 CRITICAL at 15 seconds!')}
            />
          </div>
        </section>

        {/* Section 4: Event Log */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">4. Event Log</h2>
          <p className="text-gray-600">
            Log semua event timer (onStart, onPause, onReset, onWarning, onCritical).
          </p>

          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold text-gray-900">Events</h3>
              <button
                onClick={() => setTimerEvents([])}
                className="px-3 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300"
              >
                Clear Log
              </button>
            </div>
            <div className="bg-gray-900 text-green-400 rounded-lg p-4 font-mono text-sm max-h-48 overflow-y-auto">
              {timerEvents.length === 0 ? (
                <p className="text-gray-500">{'// No events yet. Start a timer to see events.'}</p>
              ) : (
                timerEvents.map((event, idx) => (
                  <div key={idx} className="py-1">{event}</div>
                ))
              )}
            </div>
          </div>
        </section>

        {/* Technical Notes */}
        <section className="bg-gray-100 rounded-lg p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Technical Notes</h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700 text-sm">
            <li>Timer menggunakan <code className="bg-gray-200 px-1 rounded">setInterval</code> dengan interval 1 detik</li>
            <li>Audio alert menggunakan Web Audio API (tanpa file eksternal)</li>
            <li>Warning threshold default: 90 detik (1:30)</li>
            <li>Critical threshold default: 120 detik (2:00)</li>
            <li>Visual state: Green (running) → Yellow (warning) → Red (critical)</li>
            <li>Progress bar menunjukkan progres menuju critical threshold</li>
            <li>Timer dapat di-pause dan di-resume</li>
            <li>Reset mengembalikan timer ke 0 dan menghapus semua flags</li>
            <li>Accessible dengan ARIA labels dan role="timer"</li>
          </ul>
        </section>

        {/* Integration Example */}
        <section className="bg-blue-50 rounded-lg p-6 border border-blue-200">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Integration Example</h2>
          <p className="text-sm text-blue-800 mb-3">
            Untuk menggunakan timer di halaman triage:
          </p>
          <pre className="bg-gray-900 text-green-400 rounded-lg p-4 text-sm overflow-x-auto">
{`import { TriageTimer, TriageTimerMini } from '@/components/emergency';

// In header/navbar:
<TriageTimerMini isRunning={isTriageActive} />

// In triage form:
<TriageTimer
  isRunning={isTriageActive}
  onWarning={() => showToast('Hurry up!')}
  onCritical={() => playAlert()}
/>`}
          </pre>
        </section>
      </div>
    </div>
  );
}
