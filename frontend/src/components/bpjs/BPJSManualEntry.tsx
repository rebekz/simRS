"use client";

import React, { useState } from 'react';
import { AlertTriangle, Save, X, User, CreditCard, Building2, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';

// ============================================================================
// TYPES
// ============================================================================

export interface ManualBPJSData {
  cardNumber: string;
  nik: string;
  nama: string;
  tanggalLahir: string;
  jenisKelamin: 'L' | 'P';
  alamat: string;
  noTelepon: string;
  kelasRawat: string;
  jenisPeserta: string;
  faskes: string;
  faskesCode: string;
  status: string;
  catatan?: string;
}

export interface BPJSManualEntryProps {
  initialData?: Partial<ManualBPJSData>;
  onSubmit: (data: ManualBPJSData) => void;
  onCancel?: () => void;
  reason?: string;
  className?: string;
}

// ============================================================================
// MANUAL ENTRY FORM COMPONENT
// ============================================================================

/**
 * BPJSManualEntry Component
 *
 * Fallback form for manual BPJS data entry when API is unavailable.
 * Provides:
 * - Warning message explaining why manual entry is needed
 * - Form fields for all essential BPJS data
 * - Validation before submission
 * - Audit trail note field
 */
export function BPJSManualEntry({
  initialData,
  onSubmit,
  onCancel,
  reason = 'BPJS API tidak dapat diakses',
  className = '',
}: BPJSManualEntryProps) {
  const [formData, setFormData] = useState<ManualBPJSData>({
    cardNumber: initialData?.cardNumber || '',
    nik: initialData?.nik || '',
    nama: initialData?.nama || '',
    tanggalLahir: initialData?.tanggalLahir || '',
    jenisKelamin: initialData?.jenisKelamin || 'L',
    alamat: initialData?.alamat || '',
    noTelepon: initialData?.noTelepon || '',
    kelasRawat: initialData?.kelasRawat || 'KELAS III',
    jenisPeserta: initialData?.jenisPeserta || '',
    faskes: initialData?.faskes || '',
    faskesCode: initialData?.faskesCode || '',
    status: initialData?.status || 'AKTIF',
    catatan: initialData?.catatan || '',
  });

  const [errors, setErrors] = useState<Partial<Record<keyof ManualBPJSData, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof ManualBPJSData, string>> = {};

    if (!formData.cardNumber || formData.cardNumber.length !== 13) {
      newErrors.cardNumber = 'Nomor kartu harus 13 digit';
    }

    if (!formData.nik || formData.nik.length !== 16) {
      newErrors.nik = 'NIK harus 16 digit';
    }

    if (!formData.nama || formData.nama.length < 3) {
      newErrors.nama = 'Nama harus diisi';
    }

    if (!formData.tanggalLahir) {
      newErrors.tanggalLahir = 'Tanggal lahir harus diisi';
    }

    if (!formData.alamat) {
      newErrors.alamat = 'Alamat harus diisi';
    }

    if (!formData.noTelepon) {
      newErrors.noTelepon = 'Nomor telepon harus diisi';
    }

    if (!formData.faskes) {
      newErrors.faskes = 'Faskes harus diisi';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Add audit note about manual entry
      const dataWithAudit: ManualBPJSData = {
        ...formData,
        catatan: `[ENTRY MANUAL - ${new Date().toISOString()}] ${reason}. ${formData.catatan || ''}`.trim(),
      };

      onSubmit(dataWithAudit);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (field: keyof ManualBPJSData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when field is edited
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const kelasRawatOptions = ['KELAS I', 'KELAS II', 'KELAS III'];
  const statusOptions = ['AKTIF', 'TIDAK AKTIF', 'PST TERTANGGUH'];

  return (
    <div className={`bg-white rounded-lg shadow border border-gray-200 ${className}`}>
      {/* Warning Header */}
      <div className="bg-yellow-50 border-b border-yellow-200 p-4 rounded-t-lg">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-medium text-yellow-800">Mode Entry Manual</h4>
            <p className="text-sm text-yellow-700 mt-1">{reason}</p>
            <p className="text-xs text-yellow-600 mt-2">
              Silakan masukkan data BPJS secara manual. Data akan dicatat dalam audit log.
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        {/* Card Number & NIK */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <CreditCard className="w-4 h-4 inline mr-1" />
              Nomor Kartu BPJS *
            </label>
            <input
              type="text"
              value={formData.cardNumber}
              onChange={(e) => handleChange('cardNumber', e.target.value.replace(/\D/g, '').slice(0, 13))}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 ${
                errors.cardNumber ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="0001234567890"
              maxLength={13}
            />
            {errors.cardNumber && (
              <p className="text-xs text-red-500 mt-1">{errors.cardNumber}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <User className="w-4 h-4 inline mr-1" />
              NIK *
            </label>
            <input
              type="text"
              value={formData.nik}
              onChange={(e) => handleChange('nik', e.target.value.replace(/\D/g, '').slice(0, 16))}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 ${
                errors.nik ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="3171234567890123"
              maxLength={16}
            />
            {errors.nik && (
              <p className="text-xs text-red-500 mt-1">{errors.nik}</p>
            )}
          </div>
        </div>

        {/* Name & DOB */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nama Lengkap *
            </label>
            <input
              type="text"
              value={formData.nama}
              onChange={(e) => handleChange('nama', e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 ${
                errors.nama ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Nama sesuai kartu BPJS"
            />
            {errors.nama && (
              <p className="text-xs text-red-500 mt-1">{errors.nama}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Calendar className="w-4 h-4 inline mr-1" />
              Tanggal Lahir *
            </label>
            <input
              type="date"
              value={formData.tanggalLahir}
              onChange={(e) => handleChange('tanggalLahir', e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 ${
                errors.tanggalLahir ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.tanggalLahir && (
              <p className="text-xs text-red-500 mt-1">{errors.tanggalLahir}</p>
            )}
          </div>
        </div>

        {/* Gender & Phone */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Jenis Kelamin *
            </label>
            <select
              value={formData.jenisKelamin}
              onChange={(e) => handleChange('jenisKelamin', e.target.value)}
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
              onChange={(e) => handleChange('noTelepon', e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 ${
                errors.noTelepon ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="081234567890"
            />
            {errors.noTelepon && (
              <p className="text-xs text-red-500 mt-1">{errors.noTelepon}</p>
            )}
          </div>
        </div>

        {/* Address */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Alamat *
          </label>
          <textarea
            value={formData.alamat}
            onChange={(e) => handleChange('alamat', e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 ${
              errors.alamat ? 'border-red-500' : 'border-gray-300'
            }`}
            rows={2}
            placeholder="Alamat lengkap"
          />
          {errors.alamat && (
            <p className="text-xs text-red-500 mt-1">{errors.alamat}</p>
          )}
        </div>

        {/* Kelas Rawat & Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kelas Rawat
            </label>
            <select
              value={formData.kelasRawat}
              onChange={(e) => handleChange('kelasRawat', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
            >
              {kelasRawatOptions.map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status Kepesertaan
            </label>
            <select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
            >
              {statusOptions.map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Faskes */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Building2 className="w-4 h-4 inline mr-1" />
              Nama Faskes *
            </label>
            <input
              type="text"
              value={formData.faskes}
              onChange={(e) => handleChange('faskes', e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 ${
                errors.faskes ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Nama faskes pendaftaran"
            />
            {errors.faskes && (
              <p className="text-xs text-red-500 mt-1">{errors.faskes}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kode Faskes
            </label>
            <input
              type="text"
              value={formData.faskesCode}
              onChange={(e) => handleChange('faskesCode', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              placeholder="0001"
            />
          </div>
        </div>

        {/* Jenis Peserta */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Jenis Peserta
          </label>
          <input
            type="text"
            value={formData.jenisPeserta}
            onChange={(e) => handleChange('jenisPeserta', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
            placeholder="Contoh: PBI, Non-PBI, Pegawai Negeri"
          />
        </div>

        {/* Catatan */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Catatan Tambahan
          </label>
          <textarea
            value={formData.catatan}
            onChange={(e) => handleChange('catatan', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
            rows={2}
            placeholder="Catatan untuk audit trail"
          />
          <p className="text-xs text-gray-500 mt-1">
            Catatan ini akan tercatat dalam audit log bersama data manual entry.
          </p>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          {onCancel && (
            <Button
              type="button"
              variant="secondary"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              <X className="w-4 h-4 mr-2" />
              Batal
            </Button>
          )}
          <Button
            type="submit"
            variant="primary"
            disabled={isSubmitting}
          >
            <Save className="w-4 h-4 mr-2" />
            {isSubmitting ? 'Menyimpan...' : 'Simpan Data Manual'}
          </Button>
        </div>
      </form>
    </div>
  );
}

BPJSManualEntry.displayName = 'BPJSManualEntry';
