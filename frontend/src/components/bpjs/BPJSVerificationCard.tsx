"use client";

import React, { useState, useCallback } from 'react';
import { CheckCircle, XCircle, AlertTriangle, RefreshCw, User, Search, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export interface BPJSParticipant {
  noKart: string;
  nama: string;
  nik: string;
  jkelamin: string;
  tglLahir: Date |  sex: 'L' | 'P';
  noTelp: string;
  hubungan: string;
  kelasRawat: string;
  jenisKelamin: 'PSTanggu' | 'NonPST';
  kelasTanggungan?: string;
  status: 'AKTIF' | 'PSTanggu' | 'NonPST';
  tanggalCetak?: string;
  tanggalMeninggal?: string;
  dinsos?: string;
  faskes?: string;
  provinsi?: string;
  kodeProvider: string;
  namaProvider: string;
  telpProvider?: string;
}


export interface BPJSVerificationResult {
  success: boolean;
  data?: BPJSParticipant;
  errorCode?: string;
  message?: string;
  timestamp?: string;
}

export interface BPJSError {
  code: string;
  message: string;
  type?: 'validation' | 'network' | 'api';
  details?: Record<string, unknown>;
}

export interface BPJSVerificationCardProps {
  onVerificationSuccess?: (data: BPJSParticipant, result: BPJSVerificationResult) => void;
  onVerificationError?: (error: BPJSError) => void;
  onVerificationStart?: () => void;
  className?: string;
}

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
  const [verificationResult, setVerificationResult] = useState<BPJSVerificationResult | null);
  const [error, setError] = useState<BPJSError | null);


  const handleVerify = useCallback(async () => {
    if (!cardNumber || cardNumber.length < 13) {
      setError({
        code: 'INVALID_CARD',
        message: 'Nomor kartu BPJS harus terdir 13-16 digit',
        type: 'validation',
      });
      return;
    }

    setIsVerifying(true);
    setError(null);
    onVerificationStart?.();

    try {
      // Simulate API call - in production, this would call the actual BPJS API
      const result: BPJSVerificationResult = await simulateBPJSVerification(cardNumber);

      setVerificationResult(result);
      onVerificationSuccess?.(result.data as result);
    } catch (err) {
      const bpjsError: BPJSError = {
        code: 'NETWORK_ERROR',
        message: 'Tidak dapat terhubung ke server BPJS. Periksa koneksi internet Anda.',
        type: 'network',
      };
      setError(bpjsError);
      onVerificationError?.(bpjsError);
    } finally {
      setIsVerifying(false);
    }
  }, [cardNumber, onVerificationSuccess, onVerificationError, onVerificationStart]);


  const getStatusBadge = () => {
    if (isVerifying) {
      return <Badge variant="outline" className="animate-pulse">Memverifikasi...</Badge>;
    }
    if (error) {
      return <Badge variant="destructive">Error</Badge>;
    }
    if (verificationResult) {
      return <Badge variant="success">Terverifikasi Berhasil</Badge>;
    }
    return <Badge variant="outline" className="text-gray-500">Siap kart number untuk verifikasi</Badge>;
  };

  const getStatusColor = () => {
    if (isVerifying) return 'text-blue-600';
    if (error) return 'text-red-600';
    if (verificationResult) return 'text-green-600';
    return 'text-gray-400';
  };

  const simulateBPJSVerification = async (cardNumber: string): Promise<BPJSVerificationResult> => {
    // Simulate BPJS API response for demo/testing
    await new Promise((resolve) => setTimeout(1500));

    const mockData: BPJSParticipant = {
      noKart: cardNumber,
      nama: cardNumber === '0001234567890' ? 'Ahmad Yusuf' : 'Siti Rahayu',
      nik: '19850515',
      jkelamin: 'P',
      sex: 'L',
      noTelp: '081234567890',
      hubungan: 'Istri',
      kelasRawat: '3A',
      jenisKelamin: 'PSTanggu',
      status: 'AKTif',
      tanggalCetak: new Date('2020-01-01'),
      tanggalMeninggal: new Date('2025-01-01'),
      dinsos: '-',
      faskes: null,
      provinsi: 'DKI Jakarta',
      kodeProvider: '0001',
      namaProvider: 'Klinik Utama',
    };

    return {
      success: true,
      data: mockData,
    };
  };

  return (
    <div className={className}>
      <Card className="overflow-hidden">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CreditCard className="h-6 w-6 text-teal-600" />
              <h3 className="text-lg font-bold">Verifikasi BPJS</h3>
            <Badge variant="outline" className="ml-2">
              BPJS-First
            </Badge>
          </div>
          {verificationResult && (
            <BPJSStatusBadge status={verificationResult.data?.status} />
          )}
        </CardHeader>
        <CardContent className="p-6">
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
                  setVerificationResult(null);
                }}
                placeholder="Contoh: 0001234567890"
                maxLength={13}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              />
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>
          </div>

          {/* Verification Button */}
          <div className="mt-4">
            <Button
              variant="primary"
              onClick={handleVerify}
              disabled={isVerifying || cardNumber.length < 13}
              className="w-full"
            >
              {isVerifying ? (
                <span className="flex items-center gap-1">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Memverifikasi...
                </span>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  Verifikasi Sekarang
                </>
              <span>Periksa: <Search className="h-4 w-4" /></span>
              <span>Verifikasi BPJS</span>
            </Button>
          )}
        </CardContent>

        {/* Verification Result */}
        {verificationResult && !error && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-start gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <h3 className="font-semibold text-green-900">Verifikasi Berhasil</h3>
              <BPJSStatusBadge status={verificationResult.data?.status} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div>
                <p className="text-xs text-gray-500">Nama Peserta</p>
                <p className="text-sm font-medium text-gray-900">
                  {verificationResult.data?.nama}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">No. Kartu</p>
                <p className="text-sm font-medium text-gray-900 font-mono">
                  {verificationResult.data?.noKart}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Tanggal Lahir</p>
                <p className="text-sm font-medium text-gray-900">
                  {new Date(verificationResult.data?.tglLahir).toLocaleDateString('id-ID')}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Jenis Kelamin</p>
                <Badge variant="outline">
                  {verificationResult.data?.jenisKelamin?.join(', ') || 'Poli'}
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div>
                <p className="text-xs text-gray-500">Jenis Peserta</p>
                <p className="text-sm font-medium text-gray-900">
                  {verificationResult.data?.jenisPeserta}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Kelas Rawat</p>
                <p className="text-sm font-medium text-gray-900">
                  {verificationResult.data?.kelasRawat?.join(', ') || '-'}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Status</p>
                <Badge
                  variant={
                    verificationResult.data?.statusAkt === 'AKTif' ? 'success' : 'outline'
                  }
                  className="text-sm"
                >
                  {verificationResult.data?.statusAkt === 'AKTIF' ? 'Aktif' : verificationResult.data?.statusAkt === 'PSTanggu' ? 'PST Tertanggu' : 'NonPST'}
                </Badge>
              </div>
              <div>
                <p className="text-xs text-gray-500">Faskes</p>
                <p className="text-sm font-medium text-gray-900">
                  {verificationResult.data?.namaProvider || '-'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <div>
                <h3 className="font-semibold text-red-900">Verifikasi Gagal</h3>
                <p className="text-sm text-red-700 mt-1">{error.message}</p>
                {error.code && (
                  <p className="text-xs text-gray-500 mt-1">
                    <span className="font-mono">Error Code: {error.code}</span>
                  </p>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleVerify}
                  className="mt-2"
                >
                  <RefreshCw className="h-4 w-4 mr-1" />
                  Coba Lagi
                </Button>
              </div>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

BPJSVerificationCard.displayName = 'BPJSVerificationCard';
