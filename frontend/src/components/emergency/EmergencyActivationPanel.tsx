"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { EmergencyActivationButton } from './EmergencyActivationButton';
import { EmergencyStatusIndicator, ActiveEmergency } from './EmergencyStatusIndicator';
import { KodeBiruAlert } from './KodeBiruAlert';

export interface EmergencyLog {
  id: string;
  emergencyId: string;
  timestamp: Date;
  action: string;
  actor: string;
  details?: string;
}

export interface EmergencyActivationPanelProps {
  location?: string;
  currentUserId?: string;
  currentUserName?: string;
  onEmergencyActivate?: (emergency: {
    type: 'code_blue' | 'code_red' | 'code_pink' | 'code_orange' | 'code_yellow';
    reason: string;
    location: string;
    patientName?: string;
  }) => void;
  onEmergencyRespond?: (emergencyId: string) => void;
  onEmergencyResolve?: (emergencyId: string) => void;
  enableAudioAlert?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

/**
 * EmergencyActivationPanel Component
 *
 * A comprehensive emergency activation panel that provides:
 * - Quick access to emergency activation buttons
 * - Real-time status of active emergencies
 * - Emergency response logging
 * - Audio alert functionality
 *
 * Features:
 * - One-tap emergency activation
 * - Visual and audio alerts
 * - Response team notification status
 * - Emergency timer
 * - Deactivation workflow
 * - Audit logging
 */
export const EmergencyActivationPanel: React.FC<EmergencyActivationPanelProps> = ({
  location = 'IGD',
  currentUserId,
  currentUserName = 'Staff',
  onEmergencyActivate,
  onEmergencyRespond,
  onEmergencyResolve,
  enableAudioAlert = true,
  autoRefresh = true,
  refreshInterval = 5000,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeEmergencies, setActiveEmergencies] = useState<ActiveEmergency[]>([]);
  const [emergencyLogs, setEmergencyLogs] = useState<EmergencyLog[]>([]);
  const [audioEnabled, setAudioEnabled] = useState(enableAudioAlert);

  // Audio reference for alert sound
  const playAlertSound = useCallback(() => {
    if (!audioEnabled || typeof window === 'undefined') return;

    // Create oscillator for alert sound
    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.frequency.value = 800;
      oscillator.type = 'sine';

      gainNode.gain.setValueAtTime(0.5, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.5);
    } catch (e) {
      console.warn('Audio alert failed:', e);
    }
  }, [audioEnabled]);

  const handleActivateEmergency = useCallback((reason: string) => {
    const newEmergency: ActiveEmergency = {
      id: `EMG-${Date.now()}`,
      type: 'code_blue',
      location,
      activatedAt: new Date(),
      activatedBy: currentUserName,
      status: 'active',
    };

    setActiveEmergencies(prev => [newEmergency, ...prev]);

    // Add log entry
    const logEntry: EmergencyLog = {
      id: `LOG-${Date.now()}`,
      emergencyId: newEmergency.id,
      timestamp: new Date(),
      action: 'EMERGENCY_ACTIVATED',
      actor: currentUserName,
      details: reason,
    };
    setEmergencyLogs(prev => [logEntry, ...prev]);

    // Play alert sound
    playAlertSound();

    // Notify parent
    onEmergencyActivate?.({
      type: 'code_blue',
      reason,
      location,
    });

    setIsModalOpen(false);
  }, [location, currentUserName, playAlertSound, onEmergencyActivate]);

  const handleRespond = useCallback((emergencyId: string) => {
    setActiveEmergencies(prev =>
      prev.map(e =>
        e.id === emergencyId
          ? { ...e, status: 'responding' as const }
          : e
      )
    );

    // Add log entry
    const logEntry: EmergencyLog = {
      id: `LOG-${Date.now()}`,
      emergencyId,
      timestamp: new Date(),
      action: 'EMERGENCY_RESPONDING',
      actor: currentUserName,
    };
    setEmergencyLogs(prev => [logEntry, ...prev]);

    onEmergencyRespond?.(emergencyId);
  }, [currentUserName, onEmergencyRespond]);

  const handleResolve = useCallback((emergencyId: string) => {
    setActiveEmergencies(prev =>
      prev.map(e =>
        e.id === emergencyId
          ? { ...e, status: 'resolved' as const }
          : e
      )
    );

    // Add log entry
    const logEntry: EmergencyLog = {
      id: `LOG-${Date.now()}`,
      emergencyId,
      timestamp: new Date(),
      action: 'EMERGENCY_RESOLVED',
      actor: currentUserName,
    };
    setEmergencyLogs(prev => [logEntry, ...prev]);

    onEmergencyResolve?.(emergencyId);
  }, [currentUserName, onEmergencyResolve]);

  const handleViewDetails = useCallback((emergencyId: string) => {
    // In a real implementation, this would navigate to a details page or open a modal
    console.log('View details for emergency:', emergencyId);
  }, []);

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-600 to-red-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Emergency Activation</h2>
              <p className="text-red-100 text-sm">Sistem Respons Darurat</p>
            </div>
          </div>

          {/* Audio Toggle */}
          <button
            onClick={() => setAudioEnabled(!audioEnabled)}
            className={`p-2 rounded-lg transition-colors ${
              audioEnabled
                ? 'bg-white/20 text-white'
                : 'bg-white/10 text-white/50'
            }`}
            title={audioEnabled ? 'Nonaktifkan Audio' : 'Aktifkan Audio'}
          >
            {audioEnabled ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
              </svg>
            )}
          </button>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Code Blue Button */}
          <div className="bg-red-50 rounded-lg p-4 border-2 border-red-200">
            <h3 className="text-lg font-bold text-red-900 mb-2">Kode Biru (Code Blue)</h3>
            <p className="text-sm text-red-700 mb-4">
              Resusitasi darurat untuk pasien dengan henti jantung/napas
            </p>
            <EmergencyActivationButton
              onClick={() => setIsModalOpen(true)}
              size="lg"
              variant="solid"
              showLabel={true}
              pulseEffect={true}
            />
          </div>

          {/* Other Emergency Codes */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h3 className="text-lg font-bold text-gray-900 mb-2">Kode Darurat Lainnya</h3>
            <p className="text-sm text-gray-600 mb-4">
              Pilih kode darurat sesuai jenis keadaan
            </p>
            <div className="grid grid-cols-2 gap-2">
              <button
                className="px-3 py-2 bg-red-500 text-white rounded-lg text-sm font-medium hover:bg-red-600 transition-colors flex items-center justify-center gap-2"
                onClick={() => {
                  // Code Red - Fire
                  const emergency: ActiveEmergency = {
                    id: `EMG-${Date.now()}`,
                    type: 'code_red',
                    location,
                    activatedAt: new Date(),
                    activatedBy: currentUserName,
                    status: 'active',
                  };
                  setActiveEmergencies(prev => [emergency, ...prev]);
                  playAlertSound();
                }}
              >
                <span>🔥</span> Kode Merah
              </button>
              <button
                className="px-3 py-2 bg-pink-500 text-white rounded-lg text-sm font-medium hover:bg-pink-600 transition-colors flex items-center justify-center gap-2"
                onClick={() => {
                  // Code Pink - Missing Infant
                  const emergency: ActiveEmergency = {
                    id: `EMG-${Date.now()}`,
                    type: 'code_pink',
                    location,
                    activatedAt: new Date(),
                    activatedBy: currentUserName,
                    status: 'active',
                  };
                  setActiveEmergencies(prev => [emergency, ...prev]);
                  playAlertSound();
                }}
              >
                <span>👶</span> Kode Pink
              </button>
              <button
                className="px-3 py-2 bg-orange-500 text-white rounded-lg text-sm font-medium hover:bg-orange-600 transition-colors flex items-center justify-center gap-2"
                onClick={() => {
                  // Code Orange - Evacuation
                  const emergency: ActiveEmergency = {
                    id: `EMG-${Date.now()}`,
                    type: 'code_orange',
                    location,
                    activatedAt: new Date(),
                    activatedBy: currentUserName,
                    status: 'active',
                  };
                  setActiveEmergencies(prev => [emergency, ...prev]);
                  playAlertSound();
                }}
              >
                <span>⚠️</span> Kode Oranye
              </button>
              <button
                className="px-3 py-2 bg-yellow-500 text-white rounded-lg text-sm font-medium hover:bg-yellow-600 transition-colors flex items-center justify-center gap-2"
                onClick={() => {
                  // Code Yellow - Disaster
                  const emergency: ActiveEmergency = {
                    id: `EMG-${Date.now()}`,
                    type: 'code_yellow',
                    location,
                    activatedAt: new Date(),
                    activatedBy: currentUserName,
                    status: 'active',
                  };
                  setActiveEmergencies(prev => [emergency, ...prev]);
                  playAlertSound();
                }}
              >
                <span>⚡</span> Kode Kuning
              </button>
            </div>
          </div>
        </div>

        {/* Active Emergencies */}
        <EmergencyStatusIndicator
          emergencies={activeEmergencies}
          onViewDetails={handleViewDetails}
          onRespond={handleRespond}
        />

        {/* Emergency Log */}
        {emergencyLogs.length > 0 && (
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h3 className="text-lg font-bold text-gray-900 mb-3">Log Aktivitas</h3>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {emergencyLogs.slice(0, 10).map((log) => (
                <div
                  key={log.id}
                  className="flex items-start gap-3 text-sm bg-white p-2 rounded border"
                >
                  <span className="text-gray-400 font-mono text-xs">
                    {new Date(log.timestamp).toLocaleTimeString('id-ID')}
                  </span>
                  <span className={`font-medium ${
                    log.action === 'EMERGENCY_ACTIVATED'
                      ? 'text-red-600'
                      : log.action === 'EMERGENCY_RESPONDING'
                      ? 'text-yellow-600'
                      : 'text-green-600'
                  }`}>
                    {log.action === 'EMERGENCY_ACTIVATED' && '🚨 Diaktifkan'}
                    {log.action === 'EMERGENCY_RESPONDING' && '⏳ Ditanggapi'}
                    {log.action === 'EMERGENCY_RESOLVED' && '✅ Selesai'}
                  </span>
                  <span className="text-gray-600">oleh {log.actor}</span>
                  {log.details && (
                    <span className="text-gray-500 italic">- {log.details}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Location Info */}
        <div className="text-sm text-gray-500 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span>Lokasi: {location}</span>
        </div>
      </div>

      {/* Kode Biru Modal */}
      <KodeBiruAlert
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onActivate={handleActivateEmergency}
        location={location}
      />
    </div>
  );
};

EmergencyActivationPanel.displayName = 'EmergencyActivationPanel';

export default EmergencyActivationPanel;
