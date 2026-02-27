"use client";

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Search,
  User,
  Clock,
  CreditCard,
  FileText,
  Calendar,
  Building2,
  CheckCircle,
  X,
  Loader2,
  Phone,
  Hash,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { BPJSStatusBadge } from '@/components/bpjs/BPJSStatusBadge';

// ============================================================================
// TYPES
// ============================================================================

export interface ReturningPatient {
  id: string;
  mrn: string;
  bpjsCardNumber?: string;
  nik: string;
  nama: string;
  tanggalLahir: string;
  jenisKelamin: 'L' | 'P';
  noTelepon: string;
  alamat: string;
  bpjsStatus?: 'AKTIF' | 'PSTanggu' | 'NonPST';
  lastVisit?: string;
  lastPoli?: string;
  totalVisits: number;
}

export interface CheckInData {
  patientId: string;
  tanggalKunjungan: string;
  poliTujuan: string;
  poliTujuanName: string;
  jenisKunjungan: 'baru' | 'ulang';
  keluhan?: string;
}

export interface QuickCheckInProps {
  onCheckIn: (data: CheckInData) => void;
  polyclinics: { code: string; name: string }[];
  className?: string;
}

export interface QuickCheckInModalProps {
  patient: ReturningPatient | null;
  isOpen: boolean;
  onClose: () => void;
  onCheckIn: (data: CheckInData) => void;
  polyclinics: { code: string; name: string }[];
}

// ============================================================================
// MOCK DATA
// ============================================================================

const mockPatients: ReturningPatient[] = [
  {
    id: '1',
    mrn: 'MRN-001',
    bpjsCardNumber: '0001234567890',
    nik: '3171234567890123',
    nama: 'Ahmad Susanto',
    tanggalLahir: '1985-05-15',
    jenisKelamin: 'L',
    noTelepon: '081234567890',
    alamat: 'Jl. Sudirman No. 123, Jakarta',
    bpjsStatus: 'AKTIF',
    lastVisit: '2026-02-20',
    lastPoli: 'Poli Umum',
    totalVisits: 5,
  },
  {
    id: '2',
    mrn: 'MRN-002',
    bpjsCardNumber: '0009876543210',
    nik: '3171234567890456',
    nama: 'Siti Rahayu',
    tanggalLahir: '1990-08-20',
    jenisKelamin: 'P',
    noTelepon: '082345678901',
    alamat: 'Jl. Gatot Subroto No. 45, Jakarta',
    bpjsStatus: 'AKTIF',
    lastVisit: '2026-02-25',
    lastPoli: 'Poli Penyakit Dalam',
    totalVisits: 12,
  },
  {
    id: '3',
    mrn: 'MRN-003',
    nik: '3171234567890789',
    nama: 'Budi Hartono',
    tanggalLahir: '1978-12-10',
    jenisKelamin: 'L',
    noTelepon: '083456789012',
    alamat: 'Jl. Kuningan No. 78, Jakarta',
    bpjsStatus: 'NonPST',
    lastVisit: '2026-01-15',
    lastPoli: 'Poli Jantung',
    totalVisits: 3,
  },
  {
    id: '4',
    mrn: 'MRN-004',
    bpjsCardNumber: '0001111111111',
    nik: '3171234567890001',
    nama: 'Dewi Lestari',
    tanggalLahir: '1995-03-25',
    jenisKelamin: 'P',
    noTelepon: '084567890123',
    alamat: 'Jl. Thamrin No. 90, Jakarta',
    bpjsStatus: 'AKTIF',
    lastVisit: '2026-02-10',
    lastPoli: 'Poli Kandungan',
    totalVisits: 8,
  },
  {
    id: '5',
    mrn: 'MRN-005',
    nik: '3171234567890022',
    nama: 'Eko Prasetyo',
    tanggalLahir: '1982-07-08',
    jenisKelamin: 'L',
    noTelepon: '085678901234',
    alamat: 'Jl. Rasuna Said No. 55, Jakarta',
    lastVisit: '2026-02-27',
    lastPoli: 'Poli Mata',
    totalVisits: 2,
  },
];

// ============================================================================
// PATIENT SEARCH COMPONENT
// ============================================================================

interface PatientSearchBarProps {
  onSearch: (query: string) => void;
  onClear: () => void;
  isLoading?: boolean;
  resultCount?: number;
}

function PatientSearchBar({
  onSearch,
  onClear,
  isLoading = false,
  resultCount,
}: PatientSearchBarProps) {
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Keyboard shortcut (Ctrl+K / Cmd+K)
  useEffect(() => {
    const handleShortcut = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
      // Escape to clear
      if (e.key === 'Escape' && document.activeElement === inputRef.current) {
        setQuery('');
        onClear();
        inputRef.current?.blur();
      }
    };

    document.addEventListener('keydown', handleShortcut);
    return () => document.removeEventListener('keydown', handleShortcut);
  }, [onClear]);

  const handleSearch = (value: string) => {
    setQuery(value);
    if (value.length >= 2) {
      onSearch(value);
    } else if (value.length === 0) {
      onClear();
    }
  };

  const handleClear = () => {
    setQuery('');
    onClear();
    inputRef.current?.focus();
  };

  return (
    <div className="relative">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Cari pasien... (Ctrl+K)"
          className="w-full pl-12 pr-20 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          autoFocus
        />
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
          {isLoading && <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />}
          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          )}
          <kbd className="hidden md:inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-gray-400 bg-gray-100 border border-gray-200 rounded">
            <span className="text-xs">⌘</span>K
          </kbd>
        </div>
      </div>

      {/* Search hints */}
      <div className="mt-2 flex flex-wrap gap-2 text-xs text-gray-500">
        <span>Cari berdasarkan:</span>
        <span className="flex items-center gap-1">
          <Hash className="w-3 h-3" /> RM
        </span>
        <span className="flex items-center gap-1">
          <CreditCard className="w-3 h-3" /> BPJS
        </span>
        <span className="flex items-center gap-1">
          <FileText className="w-3 h-3" /> NIK
        </span>
        <span className="flex items-center gap-1">
          <User className="w-3 h-3" /> Nama
        </span>
        <span className="flex items-center gap-1">
          <Phone className="w-3 h-3" /> Telepon
        </span>
      </div>

      {resultCount !== undefined && resultCount > 0 && (
        <p className="mt-2 text-sm text-gray-600">
          Ditemukan <strong>{resultCount}</strong> pasien
        </p>
      )}
    </div>
  );
}

// ============================================================================
// SEARCH RESULT ITEM COMPONENT
// ============================================================================

interface SearchResultItemProps {
  patient: ReturningPatient;
  onSelect: (patient: ReturningPatient) => void;
}

function SearchResultItem({ patient, onSelect }: SearchResultItemProps) {
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <div
      className="p-4 border border-gray-200 rounded-lg hover:border-teal-300 hover:bg-teal-50/50 transition-all cursor-pointer"
      onClick={() => onSelect(patient)}
    >
      <div className="flex items-start justify-between gap-4">
        {/* Patient Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-2">
            <h4 className="font-semibold text-gray-900">{patient.nama}</h4>
            {patient.bpjsStatus && (
              <BPJSStatusBadge status={patient.bpjsStatus} size="sm" />
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-1 text-sm">
            <div>
              <span className="text-gray-500">RM:</span>
              <span className="ml-1 font-mono font-medium">{patient.mrn}</span>
            </div>
            {patient.bpjsCardNumber && (
              <div>
                <span className="text-gray-500">BPJS:</span>
                <span className="ml-1 font-mono">{patient.bpjsCardNumber.slice(-4)}</span>
              </div>
            )}
            <div>
              <span className="text-gray-500">Terakhir:</span>
              <span className="ml-1">{formatDate(patient.lastVisit)}</span>
            </div>
            <div>
              <span className="text-gray-500">Poli:</span>
              <span className="ml-1">{patient.lastPoli || '-'}</span>
            </div>
          </div>

          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Phone className="w-3 h-3" />
              {patient.noTelepon}
            </span>
            <span>
              {patient.totalVisits} kunjungan
            </span>
          </div>
        </div>

        {/* Action */}
        <Button
          variant="primary"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onSelect(patient);
          }}
        >
          Pilih
        </Button>
      </div>
    </div>
  );
}

// ============================================================================
// QUICK CHECK-IN MODAL COMPONENT
// ============================================================================

function QuickCheckInModal({
  patient,
  isOpen,
  onClose,
  onCheckIn,
  polyclinics,
}: QuickCheckInModalProps) {
  const [formData, setFormData] = useState({
    poliTujuan: polyclinics[0]?.code || '',
    keluhan: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Reset form when patient changes
  useEffect(() => {
    if (patient) {
      setFormData({
        poliTujuan: patient.lastPoli
          ? polyclinics.find(p => p.name === patient.lastPoli)?.code || polyclinics[0]?.code || ''
          : polyclinics[0]?.code || '',
        keluhan: '',
      });
    }
  }, [patient, polyclinics]);

  if (!isOpen || !patient) return null;

  const today = new Date().toLocaleDateString('id-ID', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    const selectedPoli = polyclinics.find(p => p.code === formData.poliTujuan);

    try {
      await new Promise(resolve => setTimeout(resolve, 800)); // Simulate API call

      onCheckIn({
        patientId: patient.id,
        tanggalKunjungan: new Date().toISOString().split('T')[0],
        poliTujuan: formData.poliTujuan,
        poliTujuanName: selectedPoli?.name || '',
        jenisKunjungan: patient.totalVisits > 0 ? 'ulang' : 'baru',
        keluhan: formData.keluhan,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900">Quick Check-In</h2>
            <button
              type="button"
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Patient Info */}
        <div className="p-6 bg-gray-50 border-b border-gray-200">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center">
              <User className="w-6 h-6 text-teal-600" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-gray-900">{patient.nama}</h3>
                {patient.bpjsStatus && (
                  <BPJSStatusBadge status={patient.bpjsStatus} size="sm" />
                )}
              </div>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1 mt-2 text-sm">
                <div>
                  <span className="text-gray-500">RM:</span>
                  <span className="ml-1 font-mono">{patient.mrn}</span>
                </div>
                <div>
                  <span className="text-gray-500">Lahir:</span>
                  <span className="ml-1">{formatDate(patient.tanggalLahir)}</span>
                </div>
                <div>
                  <span className="text-gray-500">Telepon:</span>
                  <span className="ml-1">{patient.noTelepon}</span>
                </div>
                <div>
                  <span className="text-gray-500">Kunjungan ke:</span>
                  <span className="ml-1 font-medium">{patient.totalVisits + 1}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Check-In Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Date (pre-filled) */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-blue-700">
              <Calendar className="w-5 h-5" />
              <div>
                <p className="text-sm font-medium">Tanggal Kunjungan</p>
                <p className="font-semibold">{today}</p>
              </div>
            </div>
          </div>

          {/* Polyclinic Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Building2 className="w-4 h-4 inline mr-1" />
              Poli Tujuan *
            </label>
            <select
              value={formData.poliTujuan}
              onChange={(e) => setFormData({ ...formData, poliTujuan: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              required
            >
              {polyclinics.map((poli) => (
                <option key={poli.code} value={poli.code}>
                  {poli.name}
                </option>
              ))}
            </select>
          </div>

          {/* Chief Complaint */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Keluhan Utama (Opsional)
            </label>
            <textarea
              value={formData.keluhan}
              onChange={(e) => setFormData({ ...formData, keluhan: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              rows={2}
              placeholder="Keluhan pasien hari ini"
            />
          </div>

          {/* Visit Type Info */}
          <div className="flex items-center gap-2 p-3 bg-gray-100 rounded-lg text-sm">
            <Clock className="w-4 h-4 text-gray-500" />
            <span className="text-gray-600">
              Jenis kunjungan: <strong className="text-gray-900">
                {patient.totalVisits > 0 ? 'Kunjungan Ulang' : 'Kunjungan Baru'}
              </strong>
            </span>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              className="flex-1"
              disabled={isSubmitting}
            >
              Batal
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Memproses...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Check-In
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN QUICK CHECK-IN COMPONENT
// ============================================================================

export function QuickCheckIn({
  onCheckIn,
  polyclinics,
  className = '',
}: QuickCheckInProps) {
  const [searchResults, setSearchResults] = useState<ReturningPatient[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<ReturningPatient | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [checkInComplete, setCheckInComplete] = useState<CheckInData | null>(null);

  const searchPatients = useCallback(async (query: string) => {
    setIsSearching(true);

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));

    const results = mockPatients.filter(patient => {
      const searchLower = query.toLowerCase();
      return (
        patient.mrn.toLowerCase().includes(searchLower) ||
        patient.bpjsCardNumber?.includes(query) ||
        patient.nik.includes(query) ||
        patient.nama.toLowerCase().includes(searchLower) ||
        patient.noTelepon.includes(query)
      );
    });

    setSearchResults(results);
    setIsSearching(false);
  }, []);

  const clearSearch = () => {
    setSearchResults([]);
  };

  const handleSelectPatient = (patient: ReturningPatient) => {
    setSelectedPatient(patient);
    setShowModal(true);
  };

  const handleCheckIn = (data: CheckInData) => {
    onCheckIn(data);
    setCheckInComplete(data);
    setShowModal(false);
    setSelectedPatient(null);
    setSearchResults([]);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedPatient(null);
  };

  const handleNewCheckIn = () => {
    setCheckInComplete(null);
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {checkInComplete ? (
        /* Check-In Complete State */
        <div className="bg-white rounded-xl shadow border border-gray-200 p-8 text-center">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Check-In Berhasil!</h2>
          <p className="text-gray-600 mb-6">
            Pasien telah berhasil di-check-in untuk kunjungan hari ini.
          </p>

          <div className="bg-gray-50 rounded-lg p-4 text-left max-w-sm mx-auto mb-6">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Poli:</span>
                <span className="font-medium">{checkInComplete.poliTujuanName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Tanggal:</span>
                <span className="font-medium">
                  {new Date(checkInComplete.tanggalKunjungan).toLocaleDateString('id-ID')}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Jenis:</span>
                <span className="font-medium">
                  {checkInComplete.jenisKunjungan === 'ulang' ? 'Kunjungan Ulang' : 'Kunjungan Baru'}
                </span>
              </div>
            </div>
          </div>

          <Button variant="primary" onClick={handleNewCheckIn}>
            Check-In Pasien Lain
          </Button>
        </div>
      ) : (
        <>
          {/* Search Bar */}
          <div className="bg-white rounded-xl shadow border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Search className="w-5 h-5 text-teal-600" />
              Quick Check-In Pasien Lama
            </h2>
            <PatientSearchBar
              onSearch={searchPatients}
              onClear={clearSearch}
              isLoading={isSearching}
              resultCount={searchResults.length}
            />
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-medium text-gray-700">Hasil Pencarian</h3>
              {searchResults.map((patient) => (
                <SearchResultItem
                  key={patient.id}
                  patient={patient}
                  onSelect={handleSelectPatient}
                />
              ))}
            </div>
          )}

          {/* Empty State */}
          {searchResults.length === 0 && !isSearching && (
            <div className="bg-gray-50 rounded-xl p-8 text-center">
              <User className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">
                Ketik minimal 2 karakter untuk mencari pasien
              </p>
              <p className="text-sm text-gray-400 mt-2">
                Cari berdasarkan RM, BPJS, NIK, Nama, atau Telepon
              </p>
            </div>
          )}
        </>
      )}

      {/* Check-In Modal */}
      <QuickCheckInModal
        patient={selectedPatient}
        isOpen={showModal}
        onClose={handleCloseModal}
        onCheckIn={handleCheckIn}
        polyclinics={polyclinics}
      />
    </div>
  );
}

QuickCheckIn.displayName = 'QuickCheckIn';
