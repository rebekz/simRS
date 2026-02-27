"use client";

import { useState } from 'react';
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';
import { EmergencyActivationButton } from '@/components/emergency/EmergencyActivationButton';
import { EmergencyStatusIndicator, ActiveEmergency } from '@/components/emergency/EmergencyStatusIndicator';
import { EmergencyActivationPanel } from '@/components/emergency/EmergencyActivationPanel';
import { KodeBiruAlert } from '@/components/emergency/KodeBiruAlert';

export default function EmergencyActivationDemoPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeEmergencies, setActiveEmergencies] = useState<ActiveEmergency[]>([
    {
      id: 'EMG-001',
      type: 'code_blue',
      location: 'IGD - Ruang Resusitasi 1',
      activatedAt: new Date(Date.now() - 120000), // 2 minutes ago
      activatedBy: 'Dr. Ahmad',
      patientName: 'Pasien A (Demo)',
      status: 'responding',
    },
    {
      id: 'EMG-002',
      type: 'code_pink',
      location: 'Ruang Bersalin',
      activatedAt: new Date(Date.now() - 300000), // 5 minutes ago
      activatedBy: 'Bidan Siti',
      status: 'active',
    },
  ]);

  const handleActivateEmergency = (data: {
    type: 'code_blue' | 'code_red' | 'code_pink' | 'code_orange' | 'code_yellow';
    reason: string;
    location: string;
    patientName?: string;
  }) => {
    const newEmergency: ActiveEmergency = {
      id: `EMG-${Date.now()}`,
      type: data.type,
      location: data.location,
      activatedAt: new Date(),
      activatedBy: 'Demo User',
      patientName: data.patientName,
      status: 'active',
    };
    setActiveEmergencies(prev => [newEmergency, ...prev]);
    console.log('Emergency activated:', data);
  };

  const handleRespond = (emergencyId: string) => {
    setActiveEmergencies(prev =>
      prev.map(e =>
        e.id === emergencyId
          ? { ...e, status: 'responding' as const }
          : e
      )
    );
    console.log('Responding to emergency:', emergencyId);
  };

  const handleResolve = (emergencyId: string) => {
    setActiveEmergencies(prev =>
      prev.map(e =>
        e.id === emergencyId
          ? { ...e, status: 'resolved' as const }
          : e
      )
    );
    console.log('Emergency resolved:', emergencyId);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Breadcrumb */}
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Link href="/demo" className="hover:text-gray-700">Demo</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-900">Emergency Activation</span>
        </div>

        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            WEB-S-5.5: Emergency Activation Demo
          </h1>
          <p className="text-gray-600 mt-2">
            Demonstrasi sistem aktivasi darurat dengan Kode Biru, alert, dan respons tim.
          </p>
        </div>

        {/* Acceptance Criteria Checklist */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-blue-900 mb-4">Acceptance Criteria Checklist</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-5.5.1: Prominent Kode Biru button visible</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-5.5.2: One-tap activation with confirmation</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-5.5.3: Visual/audio alerts triggered</span>
              </label>
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-5.5.4: Emergency response team notification</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-5.5.5: Timer starts on activation</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-5.5.6: Deactivation/cancel workflow</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600" />
                <span className="text-sm">AC-5.5.7: Emergency log entry created</span>
              </label>
            </div>
          </div>
        </div>

        {/* Section 1: Emergency Activation Buttons */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">1. Emergency Activation Buttons</h2>
          <p className="text-gray-600">
            Tombol aktivasi darurat dengan berbagai ukuran dan varian.
          </p>

          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="font-semibold text-gray-900 mb-4">Size Variants</h3>
            <div className="flex flex-wrap items-center gap-4">
              <div className="text-center">
                <p className="text-xs text-gray-500 mb-2">Small</p>
                <EmergencyActivationButton
                  onClick={() => setIsModalOpen(true)}
                  size="sm"
                  showLabel={true}
                />
              </div>
              <div className="text-center">
                <p className="text-xs text-gray-500 mb-2">Medium (Default)</p>
                <EmergencyActivationButton
                  onClick={() => setIsModalOpen(true)}
                  size="md"
                  showLabel={true}
                />
              </div>
              <div className="text-center">
                <p className="text-xs text-gray-500 mb-2">Large</p>
                <EmergencyActivationButton
                  onClick={() => setIsModalOpen(true)}
                  size="lg"
                  showLabel={true}
                />
              </div>
            </div>

            <h3 className="font-semibold text-gray-900 mb-4 mt-6">Style Variants</h3>
            <div className="flex flex-wrap items-center gap-4">
              <div className="text-center">
                <p className="text-xs text-gray-500 mb-2">Solid (Default)</p>
                <EmergencyActivationButton
                  onClick={() => setIsModalOpen(true)}
                  variant="solid"
                  pulseEffect={false}
                />
              </div>
              <div className="text-center">
                <p className="text-xs text-gray-500 mb-2">Outline</p>
                <EmergencyActivationButton
                  onClick={() => setIsModalOpen(true)}
                  variant="outline"
                />
              </div>
              <div className="text-center">
                <p className="text-xs text-gray-500 mb-2">Icon Only</p>
                <EmergencyActivationButton
                  onClick={() => setIsModalOpen(true)}
                  showLabel={false}
                  size="md"
                />
              </div>
              <div className="text-center">
                <p className="text-xs text-gray-500 mb-2">Disabled</p>
                <EmergencyActivationButton
                  onClick={() => setIsModalOpen(true)}
                  disabled={true}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Section 2: Emergency Status Indicator */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">2. Emergency Status Indicator</h2>
          <p className="text-gray-600">
            Tampilan status emergency aktif dengan timer real-time dan aksi respons.
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Full View */}
            <div className="bg-white rounded-lg p-6 shadow">
              <h3 className="font-semibold text-gray-900 mb-4">Full View</h3>
              <EmergencyStatusIndicator
                emergencies={activeEmergencies}
                onViewDetails={(id) => console.log('View details:', id)}
                onRespond={handleRespond}
              />
            </div>

            {/* Compact View */}
            <div className="bg-white rounded-lg p-6 shadow">
              <h3 className="font-semibold text-gray-900 mb-4">Compact View</h3>
              <EmergencyStatusIndicator
                emergencies={activeEmergencies}
                onViewDetails={(id) => console.log('View details:', id)}
                onRespond={handleRespond}
                compact={true}
              />
            </div>
          </div>

          {/* No Emergency State */}
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="font-semibold text-gray-900 mb-4">No Active Emergency State</h3>
            <EmergencyStatusIndicator
              emergencies={[]}
              onViewDetails={() => {}}
            />
          </div>
        </section>

        {/* Section 3: Full Emergency Activation Panel */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">3. Full Emergency Activation Panel</h2>
          <p className="text-gray-600">
            Panel lengkap dengan semua kode darurat, status, dan log aktivitas.
          </p>

          <EmergencyActivationPanel
            location="Demo Room"
            currentUserName="Demo User"
            onEmergencyActivate={handleActivateEmergency}
            onEmergencyRespond={handleRespond}
            onEmergencyResolve={handleResolve}
            enableAudioAlert={true}
          />
        </section>

        {/* Section 4: Kode Biru Modal Standalone */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">4. Kode Biru Modal (Standalone)</h2>
          <p className="text-gray-600">
            Modal aktivasi Kode Biru dengan countdown timer dan konfirmasi.
          </p>

          <div className="bg-white rounded-lg p-6 shadow">
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-bold"
            >
              Buka Modal Kode Biru
            </button>
          </div>
        </section>

        {/* Technical Notes */}
        <section className="bg-gray-100 rounded-lg p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Technical Notes</h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700 text-sm">
            <li>Audio alert menggunakan Web Audio API (tidak perlu file audio eksternal)</li>
            <li>Timer real-time diupdate setiap detik</li>
            <li>Modal memiliki countdown 5 detik untuk mencegah aktivasi tidak sengaja</li>
            <li>Log aktivitas mencatat semua aksi emergency</li>
            <li>Komponen responsif untuk desktop dan tablet</li>
            <li>Keyboard accessible dengan focus management</li>
            <li>Animasi pulse untuk visibilitas maksimal</li>
          </ul>
        </section>

        {/* Emergency Types Reference */}
        <section className="bg-gray-100 rounded-lg p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Emergency Code Reference</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-blue-600 text-white p-4 rounded-lg text-center">
              <span className="text-2xl">🚨</span>
              <p className="font-bold mt-2">Kode Biru</p>
              <p className="text-xs opacity-80">Resusitasi</p>
            </div>
            <div className="bg-red-600 text-white p-4 rounded-lg text-center">
              <span className="text-2xl">🔥</span>
              <p className="font-bold mt-2">Kode Merah</p>
              <p className="text-xs opacity-80">Kebakaran</p>
            </div>
            <div className="bg-pink-500 text-white p-4 rounded-lg text-center">
              <span className="text-2xl">👶</span>
              <p className="font-bold mt-2">Kode Pink</p>
              <p className="text-xs opacity-80">Bayi Hilang</p>
            </div>
            <div className="bg-orange-500 text-white p-4 rounded-lg text-center">
              <span className="text-2xl">⚠️</span>
              <p className="font-bold mt-2">Kode Oranye</p>
              <p className="text-xs opacity-80">Evakuasi</p>
            </div>
            <div className="bg-yellow-500 text-white p-4 rounded-lg text-center">
              <span className="text-2xl">⚡</span>
              <p className="font-bold mt-2">Kode Kuning</p>
              <p className="text-xs opacity-80">Bencana</p>
            </div>
          </div>
        </section>
      </div>

      {/* Kode Biru Modal */}
      <KodeBiruAlert
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onActivate={(reason) => {
          console.log('Code Blue activated:', reason);
          handleActivateEmergency({
            type: 'code_blue',
            reason,
            location: 'Demo Room',
          });
          setIsModalOpen(false);
        }}
        location="Demo Room"
        patientName="Demo Patient"
      />
    </div>
  );
}
