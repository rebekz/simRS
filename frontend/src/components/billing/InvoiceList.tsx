/**
 * Invoice List Component for STORY-028
 *
Invoice management with:
- List view with filters (patient, status, date, payer)
- Invoice details view
- Approve/reject workflow
- Payment recording
- Export to PDF

 */

import { useState, useEffect } from 'react';
import {
  FileText,
  Search,
  Filter,
  Eye,
  CheckCircle,
  XCircle,
  DollarSign,
  Download,
  Calendar,
  User,
  CreditCard,
  AlertCircle,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

// Types
interface Invoice {
  id: number;
  invoice_number: string;
  patient_id: number;
  patient_name: string;
  patient_bpjs_number: string | null;
  encounter_type: string;
  service_date: string;
  due_date: string;
  subtotal: number;
  total_discount: number;
  bpjs_coverage: number;
  patient_responsibility: number;
  paid_amount: number;
  balance_due: number;
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'partial' | 'paid' | 'overdue';
  payer_type: 'bpjs' | 'insurance' | 'cash' | 'mixed';
  created_at: string;
  approved_by: string | null;
  approved_at: string | null;
}

interface InvoiceDetail extends Invoice {
  items: InvoiceItem[];
  payments: Payment[];
  notes: string;
}

interface InvoiceItem {
  id: string;
  service_code: string;
  service_name: string;
  category: string;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  discount_amount: number;
  final_amount: number;
}

interface Payment {
  id: number;
  payment_date: string;
  payment_method: string;
  amount: number;
  reference_number: string;
  received_by: string;
  notes: string;
}

interface PaymentForm {
  payment_method: 'cash' | 'card' | 'transfer' | 'bpjs' | 'insurance';
  amount: number;
  reference_number: string;
  notes: string;
}

export function InvoiceList() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [selectedInvoice, setSelectedInvoice] = useState<InvoiceDetail | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Filters
  const [filters, setFilters] = useState({
    patient: '',
    status: '',
    payer_type: '',
    date_from: '',
    date_to: '',
  });

  // Payment form
  const [paymentForm, setPaymentForm] = useState<PaymentForm>({
    payment_method: 'cash',
    amount: 0,
    reference_number: '',
    notes: '',
  });

  useEffect(() => {
    loadInvoices();
  }, [page, filters]);

  const loadInvoices = async () => {
    setIsLoading(true);
    try {
      const queryParams = new URLSearchParams({
        page: page.toString(),
        ...(filters.patient && { patient: filters.patient }),
        ...(filters.status && { status: filters.status }),
        ...(filters.payer_type && { payer_type: filters.payer_type }),
        ...(filters.date_from && { date_from: filters.date_from }),
        ...(filters.date_to && { date_to: filters.date_to }),
      });

      const response = await fetch(`/api/v1/billing/invoices?${queryParams}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setInvoices(data.invoices);
        setTotalPages(data.total_pages);
      }
    } catch (error) {
      console.error('Failed to load invoices:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadInvoiceDetail = async (invoiceId: number) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/billing/invoices/${invoiceId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedInvoice(data);
        setShowDetailModal(true);
      }
    } catch (error) {
      console.error('Failed to load invoice detail:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const approveInvoice = async (invoiceId: number) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/billing/invoices/${invoiceId}/approve`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        alert('Faktur berhasil disetujui');
        loadInvoices();
        if (selectedInvoice?.id === invoiceId) {
          setShowDetailModal(false);
        }
      }
    } catch (error) {
      console.error('Failed to approve invoice:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const rejectInvoice = async (invoiceId: number) => {
    const reason = prompt('Alasan penolakan:');
    if (!reason) return;

    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/billing/invoices/${invoiceId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ reason }),
      });

      if (response.ok) {
        alert('Faktur ditolak');
        loadInvoices();
        setShowDetailModal(false);
      }
    } catch (error) {
      console.error('Failed to reject invoice:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const recordPayment = async () => {
    if (!selectedInvoice || paymentForm.amount <= 0) {
      alert('Masukkan jumlah pembayaran yang valid');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/billing/invoices/${selectedInvoice.id}/payments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(paymentForm),
      });

      if (response.ok) {
        alert('Pembayaran berhasil dicatat');
        setShowPaymentModal(false);
        setPaymentForm({
          payment_method: 'cash',
          amount: 0,
          reference_number: '',
          notes: '',
        });
        loadInvoices();
        loadInvoiceDetail(selectedInvoice.id);
      }
    } catch (error) {
      console.error('Failed to record payment:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const exportPDF = async (invoiceNumber: string) => {
    try {
      const response = await fetch(`/api/v1/billing/invoices/${invoiceNumber}/pdf`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Faktur-${invoiceNumber}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Failed to export PDF:', error);
    }
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
      month: 'short',
      year: 'numeric',
    });
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      draft: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Draft' },
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Menunggu' },
      approved: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Disetujui' },
      rejected: { bg: 'bg-red-100', text: 'text-red-800', label: 'Ditolak' },
      partial: { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Sebagian' },
      paid: { bg: 'bg-green-100', text: 'text-green-800', label: 'Lunas' },
      overdue: { bg: 'bg-red-100', text: 'text-red-800', label: 'Terlambat' },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  const getPayerTypeBadge = (payerType: string) => {
    const typeConfig = {
      bpjs: { bg: 'bg-green-100', text: 'text-green-800', label: 'BPJS' },
      insurance: { bg: 'bg-purple-100', text: 'text-purple-800', label: 'Asuransi' },
      cash: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Tunai' },
      mixed: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Campuran' },
    };

    const config = typeConfig[payerType as keyof typeof typeConfig] || typeConfig.cash;
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  const resetFilters = () => {
    setFilters({
      patient: '',
      status: '',
      payer_type: '',
      date_from: '',
      date_to: '',
    });
    setPage(1);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <FileText className="h-6 w-6 mr-2" />
            Daftar Faktur Tagihan
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Kelola faktur dan pantau status pembayaran
          </p>
        </div>
        <button
          onClick={loadInvoices}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            Filter
          </h3>
          <button
            onClick={resetFilters}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Reset Filter
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Pasien</label>
            <input
              type="text"
              placeholder="Cari nama pasien..."
              value={filters.patient}
              onChange={(e) => setFilters({ ...filters, patient: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Semua Status</option>
              <option value="draft">Draft</option>
              <option value="pending">Menunggu</option>
              <option value="approved">Disetujui</option>
              <option value="rejected">Ditolak</option>
              <option value="partial">Sebagian Bayar</option>
              <option value="paid">Lunas</option>
              <option value="overdue">Terlambat</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Penanggung</label>
            <select
              value={filters.payer_type}
              onChange={(e) => setFilters({ ...filters, payer_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Semua</option>
              <option value="bpjs">BPJS</option>
              <option value="insurance">Asuransi</option>
              <option value="cash">Tunai</option>
              <option value="mixed">Campuran</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Rentang Tanggal</label>
            <div className="flex gap-2">
              <input
                type="date"
                value={filters.date_from}
                onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
              />
              <input
                type="date"
                value={filters.date_to}
                onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Invoice List */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">No. Faktur</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pasien</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tanggal</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Penanggung</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Dibayar</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Aksi</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {invoices.map((invoice) => (
                <tr key={invoice.id} className="hover:bg-gray-50">
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                    {invoice.invoice_number}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <User className="h-4 w-4 text-gray-400 mr-2" />
                      <div className="text-sm text-gray-900">{invoice.patient_name}</div>
                    </div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 text-gray-400 mr-1" />
                      {formatDate(invoice.service_date)}
                    </div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    {getPayerTypeBadge(invoice.payer_type)}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-right font-medium text-gray-900">
                    {formatCurrency(invoice.patient_responsibility)}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                    {formatCurrency(invoice.paid_amount)}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    {getStatusBadge(invoice.status)}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => loadInvoiceDetail(invoice.id)}
                        className="text-blue-600 hover:text-blue-800"
                        title="Lihat Detail"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => exportPDF(invoice.invoice_number)}
                        className="text-gray-600 hover:text-gray-800"
                        title="Download PDF"
                      >
                        <Download className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {invoices.length === 0 && !isLoading && (
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>Tidak ada faktur ditemukan</p>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-gray-50 px-4 py-3 border-t flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Halaman {page} dari {totalPages}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {showDetailModal && selectedInvoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Detail Faktur</h2>
              <button
                onClick={() => setShowDetailModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Invoice Header */}
              <div className="border-b pb-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">{selectedInvoice.invoice_number}</h3>
                    <p className="text-sm text-gray-500 mt-1">
                      Tanggal: {formatDate(selectedInvoice.service_date)}
                    </p>
                  </div>
                  {getStatusBadge(selectedInvoice.status)}
                </div>
              </div>

              {/* Patient Info */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-900 mb-3">Informasi Pasien</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">Nama</p>
                    <p className="text-sm font-medium text-gray-900">{selectedInvoice.patient_name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">No. BPJS</p>
                    <p className="text-sm font-medium text-gray-900">
                      {selectedInvoice.patient_bpjs_number || 'Tidak ada'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Tipe Kunjungan</p>
                    <p className="text-sm font-medium text-gray-900">{selectedInvoice.encounter_type}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Jatuh Tempo</p>
                    <p className="text-sm font-medium text-gray-900">{formatDate(selectedInvoice.due_date)}</p>
                  </div>
                </div>
              </div>

              {/* Invoice Items */}
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3">Rincian Layanan</h4>
                <div className="border rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Layanan</th>
                        <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Qty</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {selectedInvoice.items.map((item) => (
                        <tr key={item.id}>
                          <td className="px-4 py-3 text-sm">
                            <p className="font-medium text-gray-900">{item.service_name}</p>
                            <p className="text-xs text-gray-500">{item.service_code}</p>
                          </td>
                          <td className="px-4 py-3 text-sm text-center text-gray-900">
                            {item.quantity}
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
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-900 mb-3">Ringkasan Tagihan</h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Subtotal</span>
                    <span className="font-medium text-gray-900">{formatCurrency(selectedInvoice.subtotal)}</span>
                  </div>
                  {selectedInvoice.total_discount > 0 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Diskon</span>
                      <span className="font-medium text-green-600">-{formatCurrency(selectedInvoice.total_discount)}</span>
                    </div>
                  )}
                  {selectedInvoice.bpjs_coverage > 0 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 flex items-center">
                        <CreditCard className="h-4 w-4 mr-1" />
                        Tanggungan BPJS
                      </span>
                      <span className="font-medium text-blue-600">{formatCurrency(selectedInvoice.bpjs_coverage)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-lg font-bold border-t pt-2">
                    <span className="text-gray-900">Tanggungan Pasien</span>
                    <span className="text-blue-600">{formatCurrency(selectedInvoice.patient_responsibility)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Total Dibayar</span>
                    <span className="font-medium text-green-600">{formatCurrency(selectedInvoice.paid_amount)}</span>
                  </div>
                  <div className="flex justify-between text-lg font-bold border-t pt-2">
                    <span className="text-gray-900">Sisa Tagihan</span>
                    <span className={selectedInvoice.balance_due > 0 ? 'text-red-600' : 'text-green-600'}>
                      {formatCurrency(selectedInvoice.balance_due)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Payments */}
              {selectedInvoice.payments.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Riwayat Pembayaran</h4>
                  <div className="border rounded-lg overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tanggal</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Metode</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Ref</th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Jumlah</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {selectedInvoice.payments.map((payment) => (
                          <tr key={payment.id}>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {formatDate(payment.payment_date)}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900 capitalize">
                              {payment.payment_method}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {payment.reference_number || '-'}
                            </td>
                            <td className="px-4 py-3 text-sm text-right font-medium text-green-600">
                              {formatCurrency(payment.amount)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-4 border-t">
                {selectedInvoice.status === 'pending' && (
                  <>
                    <button
                      onClick={() => rejectInvoice(selectedInvoice.id)}
                      className="inline-flex items-center px-4 py-2 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50"
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Tolak
                    </button>
                    <button
                      onClick={() => approveInvoice(selectedInvoice.id)}
                      className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Setujui
                    </button>
                  </>
                )}
                {(selectedInvoice.status === 'approved' || selectedInvoice.status === 'partial') &&
                  selectedInvoice.balance_due > 0 && (
                    <button
                      onClick={() => {
                        setPaymentForm({
                          ...paymentForm,
                          amount: selectedInvoice.balance_due,
                        });
                        setShowPaymentModal(true);
                      }}
                      className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                    >
                      <DollarSign className="h-4 w-4 mr-2" />
                      Catat Pembayaran
                    </button>
                  )}
                <button
                  onClick={() => exportPDF(selectedInvoice.invoice_number)}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <Download className="h-4 w-4 mr-2" />
                  PDF
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Payment Modal */}
      {showPaymentModal && selectedInvoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="border-b px-6 py-4">
              <h2 className="text-xl font-bold text-gray-900">Catat Pembayaran</h2>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Metode Pembayaran</label>
                <select
                  value={paymentForm.payment_method}
                  onChange={(e) => setPaymentForm({
                    ...paymentForm,
                    payment_method: e.target.value as any
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="cash">Tunai</option>
                  <option value="card">Kartu Debit/Kredit</option>
                  <option value="transfer">Transfer Bank</option>
                  <option value="bpjs">BPJS</option>
                  <option value="insurance">Asuransi</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Jumlah</label>
                <input
                  type="number"
                  value={paymentForm.amount}
                  onChange={(e) => setPaymentForm({
                    ...paymentForm,
                    amount: parseFloat(e.target.value) || 0
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="0"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Sisa tagihan: {formatCurrency(selectedInvoice.balance_due)}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">No. Referensi</label>
                <input
                  type="text"
                  value={paymentForm.reference_number}
                  onChange={(e) => setPaymentForm({
                    ...paymentForm,
                    reference_number: e.target.value
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Nomor referensi transaksi"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Catatan</label>
                <textarea
                  value={paymentForm.notes}
                  onChange={(e) => setPaymentForm({
                    ...paymentForm,
                    notes: e.target.value
                  })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Catatan pembayaran (opsional)"
                />
              </div>
            </div>

            <div className="border-t px-6 py-4 flex justify-end gap-3">
              <button
                onClick={() => setShowPaymentModal(false)}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={recordPayment}
                disabled={isLoading || paymentForm.amount <= 0}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                <DollarSign className="h-4 w-4 mr-2" />
                Simpan Pembayaran
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
