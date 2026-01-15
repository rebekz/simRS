import React, { useState, useEffect } from 'react';

export interface KodeBiruAlertProps {
  isOpen: boolean;
  onClose: () => void;
  onActivate: (reason: string) => void;
  patientName?: string;
  patientId?: string;
  location?: string;
}

/**
 * Kode Biru (Code Blue) Emergency Alert Modal
 *
 * Prominent alert system for activating emergency response
 * when a patient requires immediate resuscitation
 */
export const KodeBiruAlert: React.FC<KodeBiruAlertProps> = ({
  isOpen,
  onClose,
  onActivate,
  patientName = 'Pasien Tidak Diketahui',
  patientId,
  location = 'IGD',
}) => {
  const [reason, setReason] = useState('');
  const [isActivating, setIsActivating] = useState(false);
  const [countdown, setCountdown] = useState(5);

  // Countdown for preventing accidental activation
  useEffect(() => {
    if (!isOpen) {
      setCountdown(5);
      setReason('');
      setIsActivating(false);
      return;
    }

    if (countdown > 0 && !isActivating) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [isOpen, countdown, isActivating]);

  const handleActivate = async () => {
    if (countdown > 0) return;

    setIsActivating(true);
    onActivate(reason || 'Kode Biru diaktifkan - Pasien kritis');

    // Simulate activation delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    setIsActivating(false);
    onClose();
  };

  const handleCancel = () => {
    if (!isActivating) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 animate-pulse"
        onClick={handleCancel}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 overflow-hidden">
        {/* Flashing Header */}
        <div className="bg-red-600 animate-pulse p-6">
          <div className="flex items-center justify-center gap-4">
            <svg
              className="w-16 h-16 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <div className="text-center">
              <h2 className="text-3xl font-bold text-white">KODE BIRU</h2>
              <p className="text-red-100 text-sm">CODE BLUE - RESUSITASI</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Patient Info */}
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-red-900 mb-3">Informasi Pasien</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Nama:</span>
                <span className="font-medium text-gray-900">{patientName}</span>
              </div>
              {patientId && (
                <div className="flex justify-between">
                  <span className="text-gray-600">No RM:</span>
                  <span className="font-medium text-gray-900">{patientId}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-600">Lokasi:</span>
                <span className="font-medium text-gray-900">{location}</span>
              </div>
            </div>
          </div>

          {/* Reason Input */}
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">
              Alasan Aktivasi <span className="text-red-600">*</span>
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Contoh: Henti napas, Henti jantung, GCS &lt; 9, dll"
              className="w-full px-4 py-3 border-2 border-red-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              rows={3}
              disabled={isActivating}
            />
          </div>

          {/* Warning Message */}
          <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <svg
                className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <div className="text-sm">
                <p className="font-semibold text-yellow-900">
                  Tindakan ini akan memicu alarm darurat di seluruh rumah sakit
                </p>
                <p className="text-yellow-800 mt-1">
                  Tim resusitasi akan segera dikirim ke lokasi
                </p>
              </div>
            </div>
          </div>

          {/* Countdown Timer */}
          {countdown > 0 && !isActivating && (
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-red-100 border-4 border-red-500">
                <span className="text-4xl font-bold text-red-600">{countdown}</span>
              </div>
              <p className="text-sm text-gray-600 mt-2">detik sebelum dapat diaktifkan</p>
            </div>
          )}

          {/* Activating State */}
          {isActivating && (
            <div className="text-center space-y-3">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-red-600 border-r-transparent"></div>
              <p className="text-lg font-semibold text-red-600">MENGAKTIFKAN KODE BIRU...</p>
              <p className="text-sm text-gray-600">Mengirim notifikasi ke tim resusitasi</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={handleCancel}
              disabled={isActivating || countdown > 0}
              className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed font-medium"
            >
              Batal
            </button>
            <button
              type="button"
              onClick={handleActivate}
              disabled={countdown > 0 || isActivating}
              className="flex-1 px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-bold text-lg disabled:font-medium flex items-center justify-center gap-2"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              {countdown > 0 ? `Tunggu ${countdown}s` : 'AKTIFKAN'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

KodeBiruAlert.displayName = 'KodeBiruAlert';
