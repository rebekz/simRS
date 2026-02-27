"use client";

import React, { useState, useCallback } from 'react';
import {
  CreditCard,
  User,
  Search,
  Camera,
  Upload,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Phone,
  Users,
  FileText,
  ChevronDown,
  ChevronUp,
  X,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { BPJSStatusBadge } from '@/components/bpjs/BPJSStatusBadge';

// ============================================================================
// TYPES
// ============================================================================

export type InsuranceType = 'bpjs' | 'asuransi' | 'umum';

export interface EmergencyContact {
  name: string;
  relationship: string;
  phone: string;
}

export interface PatientRegistrationData {
  // BPJS Data (auto-filled)
  bpjsCardNumber: string;
  bpjsVerified: boolean;

  // Personal Data
  nik: string;
  nama: string;
  tanggalLahir: string;
  jenisKelamin: 'L' | 'P';
  alamat: string;
  noTelepon: string;
  email?: string;

  // Insurance
  insuranceType: InsuranceType;
  insuranceNumber?: string;
  insuranceName?: string;

  // Emergency Contact
  emergencyContact: EmergencyContact;

  // Photo
  photoUrl?: string;

  // Additional
  catatan?: string;
}

export interface BPJSVerificationResult {
  success: boolean;
  data?: {
    noKart: string;
    nama: string;
    nik: string;
    tglLahir: string;
    jkelamin: 'L' | 'P';
    alamat?: string;
    noTelp?: string;
    status: 'AKTIF' | 'PSTanggu' | 'NonPST';
    kelasRawat: string;
    jenisPeserta: string;
    faskes?: string;
  };
  message?: string;
}

export interface PatientRegistrationFormProps {
  onSubmit: (data: PatientRegistrationData) => void;
  onCancel?: () => void;
  initialData?: Partial<PatientRegistrationData>;
  isLoading?: boolean;
  className?: string;
}

// ============================================================================
// BPJS VERIFICATION CARD COMPONENT
// ============================================================================

interface BPJSVerificationCardProps {
  onVerify: (cardNumber: string) => Promise<BPJSVerificationResult>;
  onUseData: (data: BPJSVerificationResult['data']) => void;
  onManualEntry: () => void;
  verifiedData?: BPJSVerificationResult['data'];
}

function BPJSVerificationCard({
  onVerify,
  onUseData,
  onManualEntry,
  verifiedData,
}: BPJSVerificationCardProps) {
  const [cardNumber, setCardNumber] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [result, setResult] = useState<BPJSVerificationResult | null>(null);

  const handleVerify = async () => {
    if (cardNumber.length < 13) return;

    setIsVerifying(true);
    try {
      const res = await onVerify(cardNumber);
      setResult(res);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleUseData = () => {
    if (result?.data) {
      onUseData(result.data);
    }
  };

  return (
    <div className="bg-gradient-to-br from-teal-50 to-blue-50 rounded-xl p-6 border-2 border-teal-200">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="p-3 bg-teal-600 rounded-lg">
          <CreditCard className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-gray-900">Verifikasi Kartu BPJS</h3>
          <p className="text-sm text-gray-600">Masukkan nomor kartu untuk auto-fill data</p>
        </div>
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <input
            type="text"
            value={cardNumber}
            onChange={(e) => {
              const value = e.target.value.replace(/\D/g, '').slice(0, 13);
              setCardNumber(value);
              setResult(null);
            }}
            placeholder="0001R00101XXXX"
            className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 text-lg font-mono"
            maxLength={13}
            autoFocus
          />
          <CreditCard className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        </div>
        <Button
          variant="primary"
          onClick={handleVerify}
          disabled={isVerifying || cardNumber.length < 13}
          className="px-6"
        >
          {isVerifying ? (
            <>
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              Mengecek...
            </>
          ) : (
            <>
              <Search className="w-4 h-4 mr-2" />
              Cek Eligibility
            </>
          )}
        </Button>
      </div>

      {/* Verification Result */}
      {result && (
        <div className={`mt-4 p-4 rounded-lg ${result.success ? 'bg-green-100 border border-green-300' : 'bg-red-100 border border-red-300'}`}>
          {result.success && result.data ? (
            <>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span className="font-medium text-green-800">Data BPJS Ditemukan!</span>
                </div>
                <BPJSStatusBadge status={result.data.status} size="sm" />
              </div>

              <div className="grid grid-cols-2 gap-2 text-sm mb-4">
                <div>
                  <span className="text-gray-600">Nama:</span>
                  <span className="ml-2 font-medium">{result.data.nama}</span>
                </div>
                <div>
                  <span className="text-gray-600">NIK:</span>
                  <span className="ml-2 font-mono">{result.data.nik}</span>
                </div>
                <div>
                  <span className="text-gray-600">Kelas:</span>
                  <span className="ml-2">{result.data.kelasRawat}</span>
                </div>
                <div>
                  <span className="text-gray-600">Jenis:</span>
                  <span className="ml-2">{result.data.jenisPeserta}</span>
                </div>
              </div>

              <Button
                variant="primary"
                onClick={handleUseData}
                className="w-full"
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                Gunakan Data BPJS
              </Button>
            </>
          ) : (
            <div className="flex items-center gap-2 text-red-700">
              <AlertCircle className="w-5 h-5" />
              <span>{result.message || 'Data BPJS tidak ditemukan'}</span>
            </div>
          )}
        </div>
      )}

      {/* Divider */}
      <div className="flex items-center gap-4 my-6">
        <div className="flex-1 border-t border-gray-300"></div>
        <span className="text-sm text-gray-500 font-medium">ATAU</span>
        <div className="flex-1 border-t border-gray-300"></div>
      </div>

      {/* Manual Entry Button */}
      <Button
        variant="outline"
        onClick={onManualEntry}
        className="w-full border-2"
      >
        <User className="w-4 h-4 mr-2" />
        Daftar Tanpa BPJS (Manual)
      </Button>
    </div>
  );
}

// ============================================================================
// PHOTO UPLOAD COMPONENT
// ============================================================================

interface PhotoUploadProps {
  photoUrl?: string;
  onPhotoCapture: (url: string) => void;
  onPhotoRemove: () => void;
}

function PhotoUpload({ photoUrl, onPhotoCapture, onPhotoRemove }: PhotoUploadProps) {
  const [showCamera, setShowCamera] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const canvasRef = React.useRef<HTMLCanvasElement>(null);
  const streamRef = React.useRef<MediaStream | null>(null);

  const startCamera = async () => {
    try {
      setCameraError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setShowCamera(true);
    } catch (err) {
      setCameraError('Tidak dapat mengakses kamera');
      console.error('Camera error:', err);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setShowCamera(false);
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0);
        const url = canvas.toDataURL('image/jpeg', 0.8);
        onPhotoCapture(url);
        stopCamera();
      }
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        if (ev.target?.result) {
          onPhotoCapture(ev.target.result as string);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-gray-700">
          <Camera className="w-4 h-4 inline mr-1" />
          Foto Pasien (Opsional)
        </h4>
        {photoUrl && (
          <button
            type="button"
            onClick={onPhotoRemove}
            className="text-xs text-red-600 hover:text-red-700"
          >
            Hapus Foto
          </button>
        )}
      </div>

      {photoUrl ? (
        <div className="relative">
          <img
            src={photoUrl}
            alt="Patient"
            className="w-32 h-32 object-cover rounded-lg mx-auto"
          />
        </div>
      ) : showCamera ? (
        <div className="space-y-3">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full max-w-xs mx-auto rounded-lg"
          />
          <canvas ref={canvasRef} className="hidden" />
          <div className="flex justify-center gap-2">
            <Button variant="primary" onClick={capturePhoto}>
              <Camera className="w-4 h-4 mr-2" />
              Ambil Foto
            </Button>
            <Button variant="outline" onClick={stopCamera}>
              Batal
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex gap-2">
          <Button variant="outline" onClick={startCamera} className="flex-1">
            <Camera className="w-4 h-4 mr-2" />
            Kamera
          </Button>
          <label className="flex-1">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              className="hidden"
            />
            <Button variant="outline" className="w-full" as="span">
              <Upload className="w-4 h-4 mr-2" />
              Upload
            </Button>
          </label>
        </div>
      )}

      {cameraError && (
        <p className="text-xs text-red-600 mt-2">{cameraError}</p>
      )}
    </div>
  );
}

// ============================================================================
// INSURANCE SELECTION COMPONENT
// ============================================================================

interface InsuranceSelectionProps {
  value: InsuranceType;
  onChange: (type: InsuranceType) => void;
  insuranceNumber?: string;
  insuranceName?: string;
  onInsuranceNumberChange: (value: string) => void;
  onInsuranceNameChange: (value: string) => void;
}

function InsuranceSelection({
  value,
  onChange,
  insuranceNumber,
  insuranceName,
  onInsuranceNumberChange,
  onInsuranceNameChange,
}: InsuranceSelectionProps) {
  const options: { value: InsuranceType; label: string; description: string }[] = [
    { value: 'bpjs', label: 'BPJS Kesehatan', description: 'Jaminan kesehatan nasional' },
    { value: 'asuransi', label: 'Asuransi Swasta', description: 'Prudential, Allianz, dll' },
    { value: 'umum', label: 'Umum / Biaya Pribadi', description: 'Bayar langsung' },
  ];

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        <FileText className="w-4 h-4 inline mr-1" />
        Jenis Penjamin
      </label>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={`p-4 rounded-lg border-2 text-left transition-all ${
              value === option.value
                ? 'border-teal-500 bg-teal-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <div
                className={`w-4 h-4 rounded-full border-2 ${
                  value === option.value
                    ? 'border-teal-500 bg-teal-500'
                    : 'border-gray-300'
                }`}
              >
                {value === option.value && (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
                  </div>
                )}
              </div>
              <span className="font-medium text-gray-900">{option.label}</span>
            </div>
            <p className="text-xs text-gray-500 mt-1 ml-6">{option.description}</p>
          </button>
        ))}
      </div>

      {value === 'asuransi' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 p-4 bg-gray-50 rounded-lg">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Nama Asuransi</label>
            <input
              type="text"
              value={insuranceName || ''}
              onChange={(e) => onInsuranceNameChange(e.target.value)}
              placeholder="Contoh: Prudential"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">No. Polis</label>
            <input
              type="text"
              value={insuranceNumber || ''}
              onChange={(e) => onInsuranceNumberChange(e.target.value)}
              placeholder="Nomor polis asuransi"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
            />
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// EMERGENCY CONTACT COMPONENT
// ============================================================================

interface EmergencyContactFormProps {
  value: EmergencyContact;
  onChange: (contact: EmergencyContact) => void;
}

function EmergencyContactForm({ value, onChange }: EmergencyContactFormProps) {
  const [expanded, setExpanded] = useState(false);

  const handleChange = (field: keyof EmergencyContact, newValue: string) => {
    onChange({ ...value, [field]: newValue });
  };

  const relationshipOptions = [
    'Suami/Istri',
    'Anak',
    'Orang Tua',
    'Saudara',
    'Teman',
    'Lainnya',
  ];

  return (
    <div className="border border-gray-200 rounded-lg">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between text-left hover:bg-gray-50"
      >
        <div className="flex items-center gap-2">
          <Users className="w-5 h-5 text-orange-600" />
          <span className="font-medium text-gray-900">Kontak Darurat</span>
          {value.name && (
            <Badge variant="outline" className="bg-green-100 text-green-700">
              Terisi
            </Badge>
          )}
        </div>
        {expanded ? (
          <ChevronUp className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        )}
      </button>

      {expanded && (
        <div className="p-4 pt-0 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nama Kontak *
              </label>
              <input
                type="text"
                value={value.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                placeholder="Nama lengkap kontak"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Hubungan *
              </label>
              <select
                value={value.relationship}
                onChange={(e) => handleChange('relationship', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              >
                <option value="">Pilih hubungan</option>
                {relationshipOptions.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Phone className="w-4 h-4 inline mr-1" />
              Nomor Telepon *
            </label>
            <input
              type="tel"
              value={value.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              placeholder="08xxxxxxxxxx"
            />
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// MAIN REGISTRATION FORM COMPONENT
// ============================================================================

export function PatientRegistrationForm({
  onSubmit,
  onCancel,
  initialData,
  isLoading = false,
  className = '',
}: PatientRegistrationFormProps) {
  const [formData, setFormData] = useState<PatientRegistrationData>({
    bpjsCardNumber: initialData?.bpjsCardNumber || '',
    bpjsVerified: initialData?.bpjsVerified || false,
    nik: initialData?.nik || '',
    nama: initialData?.nama || '',
    tanggalLahir: initialData?.tanggalLahir || '',
    jenisKelamin: initialData?.jenisKelamin || 'L',
    alamat: initialData?.alamat || '',
    noTelepon: initialData?.noTelepon || '',
    email: initialData?.email || '',
    insuranceType: initialData?.insuranceType || 'bpjs',
    insuranceNumber: initialData?.insuranceNumber || '',
    insuranceName: initialData?.insuranceName || '',
    emergencyContact: initialData?.emergencyContact || {
      name: '',
      relationship: '',
      phone: '',
    },
    photoUrl: initialData?.photoUrl,
    catatan: initialData?.catatan || '',
  });

  const [showManualForm, setShowManualForm] = useState(false);
  const [errors, setErrors] = useState<Partial<Record<keyof PatientRegistrationData, string>>>({});

  const verifyBPJS = async (cardNumber: string): Promise<BPJSVerificationResult> => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // Mock response
    if (cardNumber === '0001234567890') {
      return {
        success: true,
        data: {
          noKart: cardNumber,
          nama: 'Ahmad Susanto',
          nik: '3171234567890123',
          tglLahir: '1985-05-15',
          jkelamin: 'L',
          alamat: 'Jl. Sudirman No. 123, Jakarta',
          noTelp: '081234567890',
          status: 'AKTIF',
          kelasRawat: 'KELAS III',
          jenisPeserta: 'PENERIMA BANTUAN IURAN',
          faskes: 'Klinik Utama Sehat',
        },
      };
    }

    return {
      success: false,
      message: 'Nomor kartu BPJS tidak ditemukan',
    };
  };

  const handleUseBPJSData = (data: NonNullable<BPJSVerificationResult['data']>) => {
    setFormData((prev) => ({
      ...prev,
      bpjsCardNumber: data.noKart,
      bpjsVerified: true,
      nik: data.nik,
      nama: data.nama,
      tanggalLahir: data.tglLahir,
      jenisKelamin: data.jkelamin,
      alamat: data.alamat || prev.alamat,
      noTelepon: data.noTelp || prev.noTelepon,
      insuranceType: 'bpjs' as InsuranceType,
    }));
    setShowManualForm(true);
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof PatientRegistrationData, string>> = {};

    if (!formData.nama) newErrors.nama = 'Nama harus diisi';
    if (!formData.nik || formData.nik.length !== 16) newErrors.nik = 'NIK harus 16 digit';
    if (!formData.tanggalLahir) newErrors.tanggalLahir = 'Tanggal lahir harus diisi';
    if (!formData.alamat) newErrors.alamat = 'Alamat harus diisi';
    if (!formData.noTelepon) newErrors.noTelepon = 'Nomor telepon harus diisi';

    if (!formData.emergencyContact.name) {
      newErrors.emergencyContact = 'Kontak darurat harus diisi';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className={`space-y-6 ${className}`}>
      {/* Step 1: BPJS Verification (Primary) */}
      {!showManualForm ? (
        <BPJSVerificationCard
          onVerify={verifyBPJS}
          onUseData={handleUseBPJSData}
          onManualEntry={() => setShowManualForm(true)}
        />
      ) : (
        <>
          {/* BPJS Card Info (if verified) */}
          {formData.bpjsVerified && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <div>
                  <p className="font-medium text-green-800">Data BPJS Terverifikasi</p>
                  <p className="text-sm text-green-600">
                    No. Kartu: {formData.bpjsCardNumber}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowManualForm(false)}
                className="text-sm text-green-700 hover:text-green-800"
              >
                Ganti
              </button>
            </div>
          )}

          {/* Manual Form Header */}
          {!formData.bpjsVerified && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-600" />
              <p className="text-sm text-yellow-700">
                Pendaftaran manual tanpa verifikasi BPJS
              </p>
            </div>
          )}

          {/* Personal Data Section */}
          <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <User className="w-5 h-5 text-teal-600" />
              Data Pribadi
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nama Lengkap *
                </label>
                <input
                  type="text"
                  value={formData.nama}
                  onChange={(e) => setFormData({ ...formData, nama: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 ${
                    errors.nama ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.nama && <p className="text-xs text-red-500 mt-1">{errors.nama}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  NIK *
                </label>
                <input
                  type="text"
                  value={formData.nik}
                  onChange={(e) => setFormData({ ...formData, nik: e.target.value.replace(/\D/g, '').slice(0, 16) })}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 ${
                    errors.nik ? 'border-red-500' : 'border-gray-300'
                  }`}
                  maxLength={16}
                />
                {errors.nik && <p className="text-xs text-red-500 mt-1">{errors.nik}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tanggal Lahir *
                </label>
                <input
                  type="date"
                  value={formData.tanggalLahir}
                  onChange={(e) => setFormData({ ...formData, tanggalLahir: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 ${
                    errors.tanggalLahir ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.tanggalLahir && <p className="text-xs text-red-500 mt-1">{errors.tanggalLahir}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Jenis Kelamin
                </label>
                <select
                  value={formData.jenisKelamin}
                  onChange={(e) => setFormData({ ...formData, jenisKelamin: e.target.value as 'L' | 'P' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                >
                  <option value="L">Laki-laki</option>
                  <option value="P">Perempuan</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  No. Telepon *
                </label>
                <input
                  type="tel"
                  value={formData.noTelepon}
                  onChange={(e) => setFormData({ ...formData, noTelepon: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 ${
                    errors.noTelepon ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.noTelepon && <p className="text-xs text-red-500 mt-1">{errors.noTelepon}</p>}
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Alamat *
                </label>
                <textarea
                  value={formData.alamat}
                  onChange={(e) => setFormData({ ...formData, alamat: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 ${
                    errors.alamat ? 'border-red-500' : 'border-gray-300'
                  }`}
                  rows={2}
                />
                {errors.alamat && <p className="text-xs text-red-500 mt-1">{errors.alamat}</p>}
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email (Opsional)
                </label>
                <input
                  type="email"
                  value={formData.email || ''}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                />
              </div>
            </div>
          </div>

          {/* Insurance Selection */}
          <InsuranceSelection
            value={formData.insuranceType}
            onChange={(type) => setFormData({ ...formData, insuranceType: type })}
            insuranceNumber={formData.insuranceNumber}
            insuranceName={formData.insuranceName}
            onInsuranceNumberChange={(value) => setFormData({ ...formData, insuranceNumber: value })}
            onInsuranceNameChange={(value) => setFormData({ ...formData, insuranceName: value })}
          />

          {/* Photo Upload */}
          <PhotoUpload
            photoUrl={formData.photoUrl}
            onPhotoCapture={(url) => setFormData({ ...formData, photoUrl: url })}
            onPhotoRemove={() => setFormData({ ...formData, photoUrl: undefined })}
          />

          {/* Emergency Contact */}
          <EmergencyContactForm
            value={formData.emergencyContact}
            onChange={(contact) => setFormData({ ...formData, emergencyContact: contact })}
          />

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Catatan Tambahan
            </label>
            <textarea
              value={formData.catatan || ''}
              onChange={(e) => setFormData({ ...formData, catatan: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              rows={2}
              placeholder="Catatan khusus untuk pasien"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            {onCancel && (
              <Button type="button" variant="outline" onClick={onCancel}>
                Batal
              </Button>
            )}
            <Button type="submit" variant="primary" disabled={isLoading}>
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Menyimpan...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Daftarkan Pasien
                </>
              )}
            </Button>
          </div>
        </>
      )}
    </form>
  );
}

PatientRegistrationForm.displayName = 'PatientRegistrationForm';
