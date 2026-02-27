"use client";

import React, { useState, useEffect } from 'react';

export interface ActiveEmergency {
  id: string;
  type: 'code_blue' | 'code_red' | 'code_pink' | 'code_orange' | 'code_yellow';
  location: string;
  activatedAt: Date;
  activatedBy: string;
  patientName?: string;
  status: 'active' | 'responding' | 'resolved';
}

export interface EmergencyStatusIndicatorProps {
  emergencies: ActiveEmergency[];
  onViewDetails?: (emergencyId: string) => void;
  onRespond?: (emergencyId: string) => void;
  maxVisible?: number;
  compact?: boolean;
}

const EMERGENCY_CONFIGS = {
  code_blue: {
    label: 'KODE BIRU',
    description: 'Resusitasi',
    icon: '🚨',
    bgColor: 'bg-blue-600',
    textColor: 'text-white',
    pulseColor: 'bg-blue-400',
  },
  code_red: {
    label: 'KODE MERAH',
    description: 'Kebakaran',
    icon: '🔥',
    bgColor: 'bg-red-600',
    textColor: 'text-white',
    pulseColor: 'bg-red-400',
  },
  code_pink: {
    label: 'KODE PINK',
    description: 'Bayi Hilang',
    icon: '👶',
    bgColor: 'bg-pink-500',
    textColor: 'text-white',
    pulseColor: 'bg-pink-300',
  },
  code_orange: {
    label: 'KODE ORANYE',
    description: 'Evakuasi',
    icon: '⚠️',
    bgColor: 'bg-orange-500',
    textColor: 'text-white',
    pulseColor: 'bg-orange-300',
  },
  code_yellow: {
    label: 'KODE KUNING',
    description: 'Bencana',
    icon: '⚡',
    bgColor: 'bg-yellow-500',
    textColor: 'text-white',
    pulseColor: 'bg-yellow-300',
  },
};

/**
 * EmergencyStatusIndicator Component
 *
 * Displays active emergencies with real-time status updates.
 * Shows emergency type, location, duration, and response status.
 *
 * Features:
 * - Real-time duration timer
 * - Visual pulse effect for active emergencies
 * - Response status tracking
 * - Quick action buttons
 */
export const EmergencyStatusIndicator: React.FC<EmergencyStatusIndicatorProps> = ({
  emergencies,
  onViewDetails,
  onRespond,
  maxVisible = 3,
  compact = false,
}) => {
  const [now, setNow] = useState(new Date());

  // Update timer every second
  useEffect(() => {
    const interval = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  const activeEmergencies = emergencies.filter(e => e.status !== 'resolved');
  const visibleEmergencies = activeEmergencies.slice(0, maxVisible);
  const hiddenCount = activeEmergencies.length - maxVisible;

  const formatDuration = (startTime: Date): string => {
    const diff = Math.floor((now.getTime() - new Date(startTime).getTime()) / 1000);

    if (diff < 60) {
      return `${diff}d`;
    } else if (diff < 3600) {
      const minutes = Math.floor(diff / 60);
      const seconds = diff % 60;
      return `${minutes}m ${seconds}d`;
    } else {
      const hours = Math.floor(diff / 3600);
      const minutes = Math.floor((diff % 3600) / 60);
      return `${hours}j ${minutes}m`;
    }
  };

  const getStatusBadge = (status: string) => {
    const configs = {
      active: { label: 'AKTIF', className: 'bg-red-500 text-white animate-pulse' },
      responding: { label: 'DITANGGAPI', className: 'bg-yellow-500 text-white' },
      resolved: { label: 'SELESAI', className: 'bg-green-500 text-white' },
    };
    const config = configs[status as keyof typeof configs] || configs.active;
    return (
      <span className={`px-2 py-0.5 rounded text-xs font-bold ${config.className}`}>
        {config.label}
      </span>
    );
  };

  if (activeEmergencies.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-3 flex items-center gap-3">
        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
        <span className="text-green-700 text-sm font-medium">Tidak ada emergency aktif</span>
      </div>
    );
  }

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        {visibleEmergencies.map((emergency) => {
          const config = EMERGENCY_CONFIGS[emergency.type];
          return (
            <button
              key={emergency.id}
              onClick={() => onViewDetails?.(emergency.id)}
              className={`
                inline-flex items-center gap-2 px-3 py-1.5 rounded-lg
                ${config.bgColor} ${config.textColor}
                animate-pulse shadow-lg
                hover:opacity-90 transition-opacity
              `}
            >
              <span>{config.icon}</span>
              <span className="font-bold text-sm">{config.label}</span>
              <span className="text-xs opacity-80">{formatDuration(emergency.activatedAt)}</span>
            </button>
          );
        })}
        {hiddenCount > 0 && (
          <span className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-sm font-medium">
            +{hiddenCount} lagi
          </span>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <span className="animate-pulse">🚨</span>
          Emergency Aktif
          <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded-full text-sm">
            {activeEmergencies.length}
          </span>
        </h3>
      </div>

      <div className="space-y-2">
        {visibleEmergencies.map((emergency) => {
          const config = EMERGENCY_CONFIGS[emergency.type];

          return (
            <div
              key={emergency.id}
              className={`
                relative overflow-hidden rounded-lg border-2
                ${emergency.status === 'active' ? 'border-red-300 animate-pulse' : 'border-gray-200'}
              `}
            >
              {/* Pulse Animation Background */}
              {emergency.status === 'active' && (
                <div
                  className={`absolute inset-0 ${config.pulseColor} opacity-20 animate-ping`}
                  style={{ animationDuration: '2s' }}
                />
              )}

              <div className={`relative ${config.bgColor} ${config.textColor} p-4`}>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <span className="text-3xl">{config.icon}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-xl font-bold">{config.label}</h4>
                        {getStatusBadge(emergency.status)}
                      </div>
                      <p className="text-sm opacity-90">{config.description}</p>
                    </div>
                  </div>

                  {/* Timer */}
                  <div className="text-right">
                    <div className="text-2xl font-bold font-mono">
                      {formatDuration(emergency.activatedAt)}
                    </div>
                    <p className="text-xs opacity-80">berlalu</p>
                  </div>
                </div>

                {/* Details */}
                <div className="mt-3 pt-3 border-t border-white/20 grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-xs opacity-70">Lokasi</p>
                    <p className="font-semibold">{emergency.location}</p>
                  </div>
                  <div>
                    <p className="text-xs opacity-70">Diaktifkan Oleh</p>
                    <p className="font-semibold">{emergency.activatedBy}</p>
                  </div>
                  {emergency.patientName && (
                    <div>
                      <p className="text-xs opacity-70">Pasien</p>
                      <p className="font-semibold">{emergency.patientName}</p>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="mt-3 flex gap-2">
                  <button
                    onClick={() => onViewDetails?.(emergency.id)}
                    className="flex-1 px-3 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-medium transition-colors"
                  >
                    Lihat Detail
                  </button>
                  {emergency.status === 'active' && (
                    <button
                      onClick={() => onRespond?.(emergency.id)}
                      className="flex-1 px-3 py-2 bg-white text-gray-900 hover:bg-gray-100 rounded-lg text-sm font-bold transition-colors"
                    >
                      Tanggapi
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {hiddenCount > 0 && (
        <button
          onClick={() => onViewDetails?.('all')}
          className="w-full py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 text-sm font-medium transition-colors"
        >
          Lihat {hiddenCount} emergency lainnya
        </button>
      )}
    </div>
  );
};

EmergencyStatusIndicator.displayName = 'EmergencyStatusIndicator';

export default EmergencyStatusIndicator;
