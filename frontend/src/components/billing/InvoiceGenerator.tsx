/**
 * Invoice Generator Component for STORY-028
 *
Comprehensive invoice generation system with:
- Encounter selection
- Charge capture from medical services
- BPJS INA-CBG calculation
- Fee-for-service calculation
- Discount and adjustment application
- Invoice preview and PDF generation

 */

import { useState, useEffect } from 'react';
import {
  FileText,
  Search,
  Plus,
  Minus,
  Calculator,
  Eye,
  Download,
  CheckCircle,
  AlertCircle,
  Package,
  User,
  Calendar,
  CreditCard,
  Percent,
  Save,
  RefreshCw,
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
}

interface ServiceCharge {
  id: number;
  service_id: number;
  service_code: string;
  service_name: string;
  service_category: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  is_bpjs_covered: boolean;
  bpjs_tariff: number | null;
}

interface InvoiceItem {
  id: string;
  charge_id: number | null;
  service_code: string;
  service_name: string;
  category: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
  is_discountable: boolean;
  discount_percent: number;
  discount_amount: number;
  final_amount: number;
}

interface BillingRule {
  id: number;
  name: string;
  rule_type: 'discount' | 'surcharge' | 'waiver';
  condition: string;
  action: string;
  value: number;
  priority: number;
  is_active: boolean;
}

interface InvoicePreview {
  invoice_number: string;
  patient_name: string;
  patient_bpjs_number: string | null;
  encounter_type: string;
  service_date: string;
  items: InvoiceItem[];
  subtotal: number;
  total_discount: number;
  bpjs_coverage: number;
  patient_responsibility: number;
  status: 'draft' | 'pending' | 'approved' | 'paid';
}

export function InvoiceGenerator() {
  const [step, setStep] = useState<'select' | 'capture' | 'calculate' | 'preview'>('select');
  const [encounters, setEncounters] = useState<Encounter[]>([]);
  const [selectedEncounter, setSelectedEncounter] = useState<Encounter | null>(null);
  const [charges, setCharges] = useState<ServiceCharge[]>([]);
  const [selectedCharges, setSelectedCharges] = useState<Set<number>>(new Set());
  const [billingRules, setBillingRules] = useState<BillingRule[]>([]);
  const [invoicePreview, setInvoicePreview] = useState<InvoicePreview | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState({ from: '', to: '' });

  // Load encounters for invoicing
  useEffect(() => {
    loadEncounters();
    loadBillingRules();
  }, []);

  const loadEncounters = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `/api/v1/billing/encounters?status=completed&unbilled=true`,
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
      console.error('Failed to load encounters:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadBillingRules = async () => {
    try {
      const response = await fetch('/api/v1/billing/rules?active=true', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setBillingRules(data);
      }
    } catch (error) {
      console.error('Failed to load billing rules:', error);
    }
  };

  const loadCharges = async (encounterId: number) => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `/api/v1/billing/encounters/${encounterId}/charges`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      if (response.ok) {
        const data = await response.json();
        setCharges(data);
      }
    } catch (error) {
      console.error('Failed to load charges:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const selectEncounter = (encounter: Encounter) => {
    setSelectedEncounter(encounter);
    setSelectedCharges(new Set());
    setStep('capture');
    loadCharges(encounter.id);
  };

  const toggleCharge = (chargeId: number) => {
    const newSelected = new Set(selectedCharges);
    if (newSelected.has(chargeId)) {
      newSelected.delete(chargeId);
    } else {
      newSelected.add(chargeId);
    }
    setSelectedCharges(newSelected);
  };

  const selectAllCharges = () => {
    if (selectedCharges.size === charges.length) {
      setSelectedCharges(new Set());
    } else {
      setSelectedCharges(new Set(charges.map(c => c.id)));
    }
  };

  const calculateInvoice = async () => {
    setIsLoading(true);
    try {
      const selectedChargeData = charges.filter(c => selectedCharges.has(c.id));

      const response = await fetch('/api/v1/billing/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          encounter_id: selectedEncounter?.id,
          charges: selectedChargeData,
          billing_rules: billingRules,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setInvoicePreview(data);
        setStep('preview');
      }
    } catch (error) {
      console.error('Failed to calculate invoice:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateInvoice = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/billing/invoices', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(invoicePreview),
      });

      if (response.ok) {
        alert('Faktur berhasil dibuat!');
        resetForm();
      }
    } catch (error) {
      console.error('Failed to generate invoice:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generatePDF = async () => {
    try {
      const response = await fetch(`/api/v1/billing/invoices/${invoicePreview?.invoice_number}/pdf`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Faktur-${invoicePreview?.invoice_number}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Failed to generate PDF:', error);
    }
  };

  const resetForm = () => {
    setStep('select');
    setSelectedEncounter(null);
    setSelectedCharges(new Set());
    setCharges([]);
    setInvoicePreview(null);
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
            Generator Faktur Tagihan
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Buat faktur dari layanan medis yang telah diberikan
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
            <div className={`flex items-center ${step === 'capture' ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'capture' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                2
              </div>
              <span className="ml-2 text-sm font-medium">Pilih Layanan</span>
            </div>
            <div className={`w-16 h-1 mx-2 ${step === 'preview' ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className={`flex items-center ${step === 'preview' ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'preview' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                3
              </div>
              <span className="ml-2 text-sm font-medium">Pratinjau & Buat</span>
            </div>
          </div>
        </div>
      </div>

      {/* Step 1: Select Encounter */}
      {step === 'select' && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Pilih Kunjungan Pasien</h3>
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
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipe</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tanggal</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dokter</th>
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
                      {encounter.provider_name}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => selectEncounter(encounter)}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                      >
                        Pilih
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

      {/* Step 2: Capture Charges */}
      {step === 'capture' && selectedEncounter && (
        <div className="space-y-4">
          {/* Encounter Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-blue-900">Kunjungan Terpilih</h3>
                <p className="text-xs text-blue-700 mt-1">
                  {selectedEncounter.patient_name} - {selectedEncounter.encounter_type} - {formatDate(selectedEncounter.start_date)}
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

          {/* Charges Selection */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Pilih Layanan untuk Ditagihkan</h3>
              <button
                onClick={selectAllCharges}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                {selectedCharges.size === charges.length ? 'Batal Pilih Semua' : 'Pilih Semua'}
              </button>
            </div>

            {isLoading && charges.length === 0 ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {charges.map((charge) => (
                  <div
                    key={charge.id}
                    className={`border rounded-lg p-4 transition-colors ${
                      selectedCharges.has(charge.id) ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start flex-1">
                        <input
                          type="checkbox"
                          checked={selectedCharges.has(charge.id)}
                          onChange={() => toggleCharge(charge.id)}
                          className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <div className="ml-3 flex-1">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-gray-900">
                                {charge.service_name}
                              </p>
                              <p className="text-xs text-gray-500 mt-1">
                                {charge.service_code} - {charge.service_category}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-medium text-gray-900">
                                {formatCurrency(charge.total_price)}
                              </p>
                              <p className="text-xs text-gray-500">
                                {charge.quantity} x {formatCurrency(charge.unit_price)}
                              </p>
                            </div>
                          </div>
                          {charge.is_bpjs_covered && charge.bpjs_tariff && (
                            <div className="mt-2 flex items-center text-xs">
                              <CheckCircle className="h-3 w-3 text-green-500 mr-1" />
                              <span className="text-green-700">
                                Ditanggung BPJS: {formatCurrency(charge.bpjs_tariff)}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {charges.length === 0 && !isLoading && (
              <div className="text-center py-8 text-gray-500">
                <Package className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Tidak ada layanan yang dapat ditagihkan</p>
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
            <button
              onClick={calculateInvoice}
              disabled={selectedCharges.size === 0 || isLoading}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              <Calculator className="h-4 w-4 mr-2" />
              Hitung Tagihan
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Preview & Generate */}
      {step === 'preview' && invoicePreview && (
        <div className="space-y-4">
          {/* Invoice Preview */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-medium text-gray-900">Pratinjau Faktur</h3>
              <div className="flex gap-2">
                <button
                  onClick={generatePDF}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <Download className="h-4 w-4 mr-2" />
                  PDF
                </button>
              </div>
            </div>

            {/* Invoice Header */}
            <div className="border-b pb-4 mb-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{invoicePreview.invoice_number}</h2>
                  <p className="text-sm text-gray-500 mt-1">Tanggal: {formatDate(invoicePreview.service_date)}</p>
                </div>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  invoicePreview.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                  invoicePreview.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {invoicePreview.status.toUpperCase()}
                </span>
              </div>
            </div>

            {/* Patient Info */}
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Nama Pasien</p>
                  <p className="text-sm font-medium text-gray-900 flex items-center">
                    <User className="h-4 w-4 mr-1" />
                    {invoicePreview.patient_name}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">No. BPJS</p>
                  <p className="text-sm font-medium text-gray-900">
                    {invoicePreview.patient_bpjs_number || 'Tidak ada'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Tipe Kunjungan</p>
                  <p className="text-sm font-medium text-gray-900">{invoicePreview.encounter_type}</p>
                </div>
              </div>
            </div>

            {/* Invoice Items */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900 mb-3">Rincian Layanan</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Layanan</th>
                      <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Qty</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Harga</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Diskon</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {invoicePreview.items.map((item) => (
                      <tr key={item.id}>
                        <td className="px-4 py-3 text-sm">
                          <p className="font-medium text-gray-900">{item.service_name}</p>
                          <p className="text-xs text-gray-500">{item.service_code}</p>
                        </td>
                        <td className="px-4 py-3 text-sm text-center text-gray-900">
                          {item.quantity}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-gray-900">
                          {formatCurrency(item.unit_price)}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-gray-900">
                          {item.discount_percent > 0 ? (
                            <span className="text-green-600">
                              -{item.discount_percent}% ({formatCurrency(item.discount_amount)})
                            </span>
                          ) : '-'}
                        </td>
                        <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">
                          {formatCurrency(item.final_amount)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Totals */}
            <div className="border-t pt-4">
              <div className="flex justify-end">
                <div className="w-72 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Subtotal</span>
                    <span className="font-medium text-gray-900">{formatCurrency(invoicePreview.subtotal)}</span>
                  </div>
                  {invoicePreview.total_discount > 0 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Total Diskon</span>
                      <span className="font-medium text-green-600">-{formatCurrency(invoicePreview.total_discount)}</span>
                    </div>
                  )}
                  {invoicePreview.bpjs_coverage > 0 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 flex items-center">
                        <CreditCard className="h-4 w-4 mr-1" />
                        Tanggungan BPJS
                      </span>
                      <span className="font-medium text-blue-600">{formatCurrency(invoicePreview.bpjs_coverage)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-lg font-bold border-t pt-2">
                    <span className="text-gray-900">Tanggungan Pasien</span>
                    <span className="text-blue-600">{formatCurrency(invoicePreview.patient_responsibility)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3">
            <button
              onClick={() => setStep('capture')}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Kembali
            </button>
            <button
              onClick={generateInvoice}
              disabled={isLoading}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              <Save className="h-4 w-4 mr-2" />
              Buat Faktur
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
