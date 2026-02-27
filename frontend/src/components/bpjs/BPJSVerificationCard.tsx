"use client";

import React, { useState, useCallback } from 'react';
import { CreditCard, User, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { BPJSStatusBadge } from './BPJSStatusBadge';

// ============================================================================
// TYPES
// ============================================================================

export interface BPJSParticipant {
  noKart: string;
  nama: string;
  nik: string;
  tglLahir: string;
  jkelamin: string;
  sex: 'L' | 'P';
  noTelp: string;
  hubungan: string;
  kelasRawat: string;
  jenisKelamin: string;
  kelasTanggungan?: string;
  status: 'AKTIF' | 'PSTanggu' | 'NonPST';
  tanggalCetak?: string;
  tanggalMeninggal?: string;
  dinsos?: string;
  faskes?: string | null;
  provinsi?: string;
  kodeProvider: string;
  namaProvider: string;
  telpProvider?: string;
}

export interface BPJSVerificationResult {
  success: boolean;
  data: BPJSParticipant | null;
  message?: string;
}

export interface BPJSError {
  code: string;
  message: string;
  type: 'validation' | 'network' | 'api' | 'unknown';
}

export interface BPJSVerificationCardProps {
  onVerificationSuccess?: (data: BPJSParticipant, result: BPJSVerificationResult) => void;
  onVerificationError?: (error: BPJSError) => void;
  onVerificationStart?: () => void;
  className?: string;
}

// ============================================================================
// MOCK DATA
// ============================================================================

const mockParticipants: Record<string, BPJSParticipant> = {
  '0001234567890': {
    noKart: '0001234567890',
    nama: 'Ahmad Susanto',
    nik: '3171234567890123',
    tglLahir: '1985-05-15',
    jkelamin: 'Laki-laki',
    sex: 'L',
    noTelp: '081234567890',
    hubungan: 'Peserta Utama',
    kelasRawat: 'KELAS III',
    jenisKelamin: 'PENERIMA BANTUAN IURAN',
    status: 'AKTIF',
    tanggalCetak: '2020-01-01',
    faskes: 'Klinik Utama Sehat',
    provinsi: 'DKI Jakarta',
    kodeProvider: '0001',
    namaProvider: 'Klinik Utama Sehat',
  },
  '0009876543210': {
    noKart: '0009876543210',
    nama: 'Siti Rahayu',
    nik: '3171234567890456',
    tglLahir: '1990-08-20',
    jkelamin: 'Perempuan',
    sex: 'P',
    noTelp: '082345678901',
    hubungan: 'Istri',
    kelasRawat: 'KELAS II',
    jenisKelamin: 'PEGAWAI SWASTA',
    status: 'AKTIF',
    tanggalCetak: '2018-06-15',
    faskes: 'RSUD Sehat Selalu',
    provinsi: 'DKI Jakarta',
    kodeProvider: '0002',
    namaProvider: 'RSUD Sehat Selalu',
  },
};

// ============================================================================
// COMPONENT
// ============================================================================

/**
 * BPJSVerificationCard Component
 *
 * Main component for BPJS eligibility verification. Provides:
 * - Card number input with validation
 * - Real-time verification status indicator
 * - Auto-fill patient data from BPJS response
 * - Display verification result with detailed information
 */
export const BPJSVerificationCard: React.FC<BPJSVerificationCardProps> = ({
  onVerificationSuccess,
  onVerificationError,
  onVerificationStart,
  className = '',
}) => {
  const [cardNumber, setCardNumber] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<BPJSVerificationResult | null>(null);
  const [error, setError] = useState<BPJSError | null>(null);

  const simulateBPJSVerification = async (cardNum: string): Promise<BPJSVerificationResult> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // Check mock data
    const participant = mockParticipants[cardNum];

    if (participant) {
      return {
        success: true,
        data: participant,
      };
    }

    // Random success for demo purposes
    if (cardNum.length === 13) {
      return {
        success: true,
        data: {
          noKart: cardNum,
          nama: 'Demo Pasien',
          nik: '3171234567890001',
          tglLahir: '1990-01-01',
          jkelamin: 'Laki-laki',
          sex: 'L',
          noTelp: '081234567890',
          hubungan: 'Peserta Utama',
          kelasRawat: 'KELAS III',
          jenisKelamin: 'PENERIMA BANTUAN IURAN',
          status: 'AKTIF',
          faskes: 'Klinik Utama Sehat',
          provinsi: 'DKI Jakarta',
          kodeProvider: '0001',
          namaProvider: 'Klinik Utama Sehat',
        },
      };
    }

    return {
      success: false,
      data: null,
      message: 'Nomor kartu BPJS tidak ditemukan',
    };
  };

  const handleVerify = useCallback(async () => {
    if (!cardNumber || cardNumber.length < 13) {
      const validationError: BPJSError = {
        code: 'INVALID_CARD',
        message: 'Nomor kartu BPJS harus terdiri dari 13 digit',
        type: 'validation',
      };
      setError(validationError);
      onVerificationError?.(validationError);
      return;
    }

    setIsVerifying(true);
    setError(null);
    setVerificationResult(null);
    onVerificationStart?.();

    try {
      const result = await simulateBPJSVerification(cardNumber);

      if (result.success && result.data) {
        setVerificationResult(result);
        onVerificationSuccess?.(result.data, result);
      } else {
        const apiError: BPJSError = {
          code: 'NOT_FOUND',
          message: result.message || 'Nomor kartu BPJS tidak ditemukan',
          type: 'api',
        };
        setError(apiError);
        onVerificationError?.(apiError);
      }
    } catch (err) {
      const networkError: BPJSError = {
        code: 'NETWORK_ERROR',
        message: 'Tidak dapat terhubung ke server BPJS. Periksa koneksi internet Anda.',
        type: 'network',
      };
      setError(networkError);
      onVerificationError?.(networkError);
    } finally {
      setIsVerifying(false);
    }
  }, [cardNumber, onVerificationSuccess, onVerificationError, onVerificationStart]);

  const handleReset = () => {
    setCardNumber('');
    setVerificationResult(null);
    setError(null);
  };

  return (
    <div className={className}>
      <Card className="overflow-hidden">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CreditCard className="h-6 w-6 text-teal-600" />
              <h3 className="text-lg font-bold">Verifikasi BPJS</h3>
            </div>
            {verificationResult?.data && (
              <BPJSStatusBadge status={verificationResult.data.status} size="sm" />
            )}
          </div>
        </CardHeader>

        <CardBody className="p-6 pt-0">
          {/* Card Number Input */}
          <div className="mb-4">
            <label htmlFor="cardNumber" className="block text-sm font-medium text-gray-700 mb-1">
              Nomor Kartu BPJS
            </label>
            <div className="relative">
              <input
                id="cardNumber"
                type="text"
                value={cardNumber}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, '').slice(0, 13);
                  setCardNumber(value);
                  setError(null);
                }}
                placeholder="Contoh: 0001234567890"
                maxLength={13}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Masukkan 13 digit nomor kartu BPJS
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-800">{error.message}</p>
                <p className="text-xs text-red-600 mt-1">Kode Error: {error.code}</p>
              </div>
            </div>
          )}

          {/* Verification Result */}
          {verificationResult?.data && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="font-medium text-green-800">Verifikasi Berhasil</span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-gray-500">Nama</p>
                  <p className="font-medium">{verificationResult.data.nama}</p>
                </div>
                <div>
                  <p className="text-gray-500">No. Kartu</p>
                  <p className="font-medium font-mono">{verificationResult.data.noKart}</p>
                </div>
                <div>
                  <p className="text-gray-500">NIK</p>
                  <p className="font-medium font-mono">{verificationResult.data.nik}</p>
                </div>
                <div>
                  <p className="text-gray-500">Kelas Rawat</p>
                  <p className="font-medium">{verificationResult.data.kelasRawat}</p>
                </div>
                <div>
                  <p className="text-gray-500">Jenis Peserta</p>
                  <p className="font-medium">{verificationResult.data.jenisKelamin}</p>
                </div>
                <div>
                  <p className="text-gray-500">Faskes</p>
                  <p className="font-medium">{verificationResult.data.faskes || '-'}</p>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2">
            {!verificationResult ? (
              <Button
                variant="primary"
                onClick={handleVerify}
                disabled={isVerifying || cardNumber.length < 13}
                className="flex-1"
              >
                {isVerifying ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Memverifikasi...
                  </>
                ) : (
                  <>
                    <CreditCard className="w-4 h-4 mr-2" />
                    Verifikasi
                  </>
                )}
              </Button>
            ) : (
              <Button
                variant="secondary"
                onClick={handleReset}
                className="flex-1"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Reset
              </Button>
            )}
          </div>

          {/* Demo Hint */}
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-xs text-blue-700">
              <strong>Demo:</strong> Gunakan nomor kartu <code className="bg-blue-100 px-1 rounded">0001234567890</code> atau <code className="bg-blue-100 px-1 rounded">0009876543210</code> untuk testing, atau masukkan 13 digit apapun.
            </p>
          </div>
        </CardBody>
      </Card>
    </div>
  );
};

BPJSVerificationCard.displayName = 'BPJSVerificationCard';
