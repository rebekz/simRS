"""BPJS Claim Generator Component

Comprehensive BPJS claim generation system with:
- Encounter/invoice selection
- Automatic claim data generation
- Claim validation
- INA-CBG grouping
- Package rate calculation
- e-Claim file generation
- Submission to BPJS gateway
"""

import { useState, useEffect } from 'react';
import {
  FileText,
  Search,
  CheckCircle,
  AlertCircle,
  Upload,
  Send,
  Package,
  User,
  Calendar,
  Clock,
  FileCheck,
  Download,
  RefreshCw,
  Eye,
} from 'lucide-react';

// Types
interface Encounter {
  id: number;
  patient_id: number;
  patient_name: string;
  patient_bpjs_number: string | null;
  encounter_type: string;
  start_date: string;
  end_date: string | null;
  status: string;
  provider_id: number;
  provider_name: string;
  department: string;
  invoice_number?: string;
}

interface ClaimData {
  claim_id: string;
  encounter_id: number;
  patient_name: string;
  patient_bpjs_number: string;
  sep_number: string;
  admission_date: string;
  discharge_date: string;
  facility_code: string;
  facility_name: string;
  provider_type: string;
  class_type: string;
  diagnosis: {
    primary: string;
    secondary: string[];
    procedure: string[];
  };
  package_info: {
    code: string;
    name: string;
    rate: number;
    description: string;
  };
  procedure_info: {
    code: string;
    name: string;
    tariff: number;
  }[];
  status: 'draft' | 'validated' | 'submitted';
}

interface ValidationResult {
  is_valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

interface ValidationError {
  field: string;
  message: string;
  severity: 'error' | 'warning';
}

interface ValidationWarning {
  field: string;
  message: string;
}

export function BPJSClaimGenerator() {
  const [step, setStep] = useState<'select' | 'generate' | 'validate' | 'submit'>('select');
  const [encounters, setEncounters] = useState<Encounter[]>([]);
  const [selectedEncounter, setSelectedEncounter] = useState<Encounter | null>(null);
  const [claimData, setClaimData] = useState<ClaimData | null>(null);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState({ from: '', to: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadEncounters();
  }, []);

  const loadEncounters = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `/api/v1/bpjs/encounters?status=completed&has_invoice=true`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      if (response.ok) {
        const data = await response.json();
        setEncounters(data);
      }
    } catch (error) {
      console.error('Gagal memuat kunjungan:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const selectEncounter = async (encounter: Encounter) => {
    setSelectedEncounter(encounter);
    setStep('generate');
    await generateClaimData(encounter);
  };

  const generateClaimData = async (encounter: Encounter) => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `/api/v1/bpjs/claims/generate/${encounter.id}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setClaimData(data);
      } else {
        const error = await response.json();
        alert(`Gagal generate klaim: ${error.message}`);
      }
    } catch (error) {
      console.error('Gagal generate data klaim:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const validateClaim = async () => {
    if (!claimData) return;

    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/bpjs/claims/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(claimData),
      });

      if (response.ok) {
        const data = await response.json();
        setValidationResult(data);
        setStep('validate');
      }
    } catch (error) {
      console.error('Gagal validasi klaim:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const submitClaim = async () => {
    if (!claimData) return;

    setIsSubmitting(true);
    try {
      const response = await fetch('/api/v1/bpjs/claims/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(claimData),
      });

      if (response.ok) {
        const data = await response.json();
        alert('Klaim berhasil disubmit ke BPJS!');
        resetForm();
      } else {
        const error = await response.json();
        alert(`Gagal submit klaim: ${error.message}`);
      }
    } catch (error) {
      console.error('Gagal submit klaim:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const downloadEClaimFile = async () => {
    if (!claimData) return;

    try {
      const response = await fetch(
        `/api/v1/bpjs/claims/eclaim/${claimData.claim_id}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `eclaim-${claimData.claim_id}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Gagal download file e-Claim:', error);
    }
  };

  const resetForm = () => {
    setStep('select');
    setSelectedEncounter(null);
    setClaimData(null);
    setValidationResult(null);
    setSearchTerm('');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    });
  };

  const filteredEncounters = encounters.filter(encounter => {
    const matchesSearch =
      !searchTerm ||
      encounter.patient_name.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesDate =
      !dateFilter.from ||
      (new Date(encounter.start_date) >= new Date(dateFilter.from) &&
        (!dateFilter.to || new Date(encounter.start_date) <= new Date(dateFilter.to)));

    return matchesSearch && matchesDate;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <FileText className="h-6 w-6 mr-2" />
            Generator Klaim BPJS
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Buat dan submit klaim BPJS dengan sistem INA-CBG
          </p>
        </div>
        <div className="flex items-center gap-2">
          {step !== 'select' && (
            <button
              onClick={resetForm}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Baru
            </button>
          )}
        </div>
      </div>

      {/* Step Indicator */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className={`flex items-center ${step === 'select' ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'select' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                1
              </div>
              <span className="ml-2 text-sm font-medium">Pilih Kunjungan</span>
            </div>
            <div className={`w-16 h-1 mx-2 ${step !== 'select' ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className={`flex items-center ${step === 'generate' ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'generate' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                2
              </div>
              <span className="ml-2 text-sm font-medium">Generate Data</span>
            </div>
            <div className={`w-16 h-1 mx-2 ${step === 'validate' || step === 'submit' ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className={`flex items-center ${step === 'validate' || step === 'submit' ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'validate' || step === 'submit' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                3
              </div>
              <span className="ml-2 text-sm font-medium">Validasi & Submit</span>
            </div>
          </div>
        </div>
      </div>

      {/* Step 1: Select Encounter */}
      {step === 'select' && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Pilih Kunjungan untuk Klaim</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="relative">
                <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Cari pasien..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500 w-full"
                />
              </div>
              <input
                type="date"
                value={dateFilter.from}
                onChange={(e) => setDateFilter({ ...dateFilter, from: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
              />
              <input
                type="date"
                value={dateFilter.to}
                onChange={(e) => setDateFilter({ ...dateFilter, to: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pasien</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">No. BPJS</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">No. SEP</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipe</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tanggal</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Faktur</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Aksi</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredEncounters.map((encounter) => (
                  <tr key={encounter.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <User className="h-5 w-5 text-gray-400 mr-2" />
                        <div className="text-sm font-medium text-gray-900">
                          {encounter.patient_name}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                      {encounter.patient_bpjs_number || '-'}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                      {encounter.invoice_number || '-'}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {encounter.encounter_type}
                      </span>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 text-gray-400 mr-1" />
                        {formatDate(encounter.start_date)}
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                      {encounter.invoice_number || '-'}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => selectEncounter(encounter)}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                      >
                        Generate
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredEncounters.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Tidak ada kunjungan yang cocok dengan filter</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Step 2: Generate Claim Data */}
      {step === 'generate' && claimData && (
        <div className="space-y-4">
          {/* Encounter Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-blue-900">Kunjungan Terpilih</h3>
                <p className="text-xs text-blue-700 mt-1">
                  {selectedEncounter?.patient_name} - {selectedEncounter?.encounter_type} - {formatDate(selectedEncounter?.start_date || '')}
                </p>
              </div>
              <button
                onClick={() => setStep('select')}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Ubah
              </button>
            </div>
          </div>

          {/* Claim Data Preview */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-medium text-gray-900">Data Klaim</h3>
              <div className="flex gap-2">
                <button
                  onClick={validateClaim}
                  disabled={isLoading}
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:bg-gray-300"
                >
                  <FileCheck className="h-4 w-4 mr-2" />
                  Validasi
                </button>
              </div>
            </div>

            {isLoading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Patient Information */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Informasi Pasien</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-gray-500">Nama Pasien</p>
                        <p className="text-sm font-medium text-gray-900 flex items-center">
                          <User className="h-4 w-4 mr-1" />
                          {claimData.patient_name}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">No. BPJS</p>
                        <p className="text-sm font-medium text-gray-900">{claimData.patient_bpjs_number}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">No. SEP</p>
                        <p className="text-sm font-medium text-gray-900">{claimData.sep_number}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Tipe Fasilitas</p>
                        <p className="text-sm font-medium text-gray-900">{claimData.provider_type}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Dates */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Tanggal Pelayanan</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-gray-500">Tanggal Masuk</p>
                        <p className="text-sm font-medium text-gray-900 flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {formatDate(claimData.admission_date)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Tanggal Keluar</p>
                        <p className="text-sm font-medium text-gray-900 flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {formatDate(claimData.discharge_date)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Package Information */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Paket INA-CBG</h4>
                  <div className="border rounded-lg p-4 bg-blue-50">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <p className="text-sm font-bold text-gray-900">{claimData.package_info.code}</p>
                        <p className="text-xs text-gray-600">{claimData.package_info.name}</p>
                      </div>
                      <p className="text-lg font-bold text-blue-600">
                        {formatCurrency(claimData.package_info.rate)}
                      </p>
                    </div>
                    <p className="text-xs text-gray-600">{claimData.package_info.description}</p>
                  </div>
                </div>

                {/* Diagnosis */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Diagnosis</h4>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                    <div>
                      <p className="text-xs text-gray-500">Diagnosis Utama</p>
                      <p className="text-sm font-medium text-gray-900">{claimData.diagnosis.primary}</p>
                    </div>
                    {claimData.diagnosis.secondary.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500">Diagnosis Sekunder</p>
                        <div className="space-y-1">
                          {claimData.diagnosis.secondary.map((diag, idx) => (
                            <p key={idx} className="text-sm text-gray-900">{diag}</p>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Procedures */}
                {claimData.procedure_info.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-3">Tindakan</h4>
                    <div className="overflow-x-auto border rounded-lg">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Kode</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Nama Tindakan</th>
                            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Tarif</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {claimData.procedure_info.map((proc, idx) => (
                            <tr key={idx}>
                              <td className="px-4 py-3 text-sm font-medium text-gray-900">{proc.code}</td>
                              <td className="px-4 py-3 text-sm text-gray-900">{proc.name}</td>
                              <td className="px-4 py-3 text-sm text-right text-gray-900">
                                {formatCurrency(proc.tariff)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3">
            <button
              onClick={() => setStep('select')}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Kembali
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Validate & Submit */}
      {(step === 'validate' || step === 'submit') && claimData && validationResult && (
        <div className="space-y-4">
          {/* Validation Results */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Hasil Validasi</h3>

            {validationResult.errors.length > 0 && (
              <div className="mb-4">
                <div className="flex items-center mb-2">
                  <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
                  <h4 className="text-sm font-medium text-gray-900">Error</h4>
                </div>
                <div className="space-y-2">
                  {validationResult.errors.map((error, idx) => (
                    <div key={idx} className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <p className="text-sm font-medium text-red-900">{error.field}</p>
                      <p className="text-xs text-red-700 mt-1">{error.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {validationResult.warnings.length > 0 && (
              <div className="mb-4">
                <div className="flex items-center mb-2">
                  <AlertCircle className="h-5 w-5 text-yellow-500 mr-2" />
                  <h4 className="text-sm font-medium text-gray-900">Peringatan</h4>
                </div>
                <div className="space-y-2">
                  {validationResult.warnings.map((warning, idx) => (
                    <div key={idx} className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                      <p className="text-sm text-yellow-900">{warning.field}: {warning.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {validationResult.is_valid && validationResult.errors.length === 0 && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-green-900">Validasi Berhasil</p>
                    <p className="text-xs text-green-700 mt-1">Data klaim lengkap dan valid untuk disubmit</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          {validationResult.is_valid && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Submit Klaim</h3>

              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-blue-900">File e-Claim</p>
                      <p className="text-xs text-blue-700 mt-1">Download file e-Claim untuk keperluan dokumen</p>
                    </div>
                    <button
                      onClick={downloadEClaimFile}
                      className="inline-flex items-center px-3 py-2 border border-blue-300 rounded-md text-sm font-medium text-blue-700 bg-blue-50 hover:bg-blue-100"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </button>
                  </div>
                </div>

                <div className="flex justify-end gap-3">
                  <button
                    onClick={() => setStep('generate')}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Kembali
                  </button>
                  <button
                    onClick={submitClaim}
                    disabled={isSubmitting}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300"
                  >
                    {isSubmitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Submitting...
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4 mr-2" />
                        Submit ke BPJS
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
