/**
 * Payment Reconciliation Component
 *
Reconciliation system with:
- Daily transaction list
- Payment method breakdown
- Expected vs actual comparison
- Discrepancy handling
- Export to Excel

 */

import { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  Calendar,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Search,
  Filter,
  TrendingUp,
  TrendingDown,
  DollarSign,
  CreditCard,
  Building,
  Smartphone,
  XCircle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

// Types
interface ReconciliationReport {
  report_date: string;
  total_transactions: number;
  total_expected: number;
  total_actual: number;
  discrepancy: number;
  discrepancy_percentage: number;
  status: 'matched' | 'discrepancy' | 'pending';
  verified_by: string | null;
  verified_at: string | null;
}

interface Transaction {
  id: number;
  transaction_number: string;
  transaction_time: string;
  payment_method: string;
  amount: number;
  reference_number: string;
  patient_name: string;
  invoice_number: string;
  status: 'verified' | 'discrepancy' | 'pending';
  discrepancy_amount: number;
  discrepancy_note: string;
}

interface PaymentMethodSummary {
  method: string;
  method_name: string;
  transaction_count: number;
  total_amount: number;
  expected_amount: number;
  discrepancy: number;
}

interface Discrepancy {
  id: number;
  transaction_id: number;
  transaction_number: string;
  expected_amount: number;
  actual_amount: number;
  discrepancy: number;
  type: 'shortage' | 'excess';
  status: 'pending' | 'resolved' | 'approved';
  resolution_note: string;
  resolved_at: string | null;
}

export function PaymentReconciliation() {
  const [reportDate, setReportDate] = useState(new Date().toISOString().split('T')[0]);
  const [report, setReport] = useState<ReconciliationReport | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [paymentMethodSummaries, setPaymentMethodSummaries] = useState<PaymentMethodSummary[]>([]);
  const [discrepancies, setDiscrepancies] = useState<Discrepancy[]>([]);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [showDiscrepancyModal, setShowDiscrepancyModal] = useState(false);
  const [showResolutionModal, setShowResolutionModal] = useState(false);
  const [discrepancyNote, setDiscrepancyNote] = useState('');
  const [resolutionNote, setResolutionNote] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterMethod, setFilterMethod] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadReconciliationData();
  }, [reportDate]);

  const loadReconciliationData = async () => {
    setIsLoading(true);
    try {
      const [reportRes, transactionsRes, summariesRes, discrepanciesRes] = await Promise.all([
        fetch(`/api/v1/payments/reconciliation/${reportDate}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
        fetch(`/api/v1/payments/reconciliation/${reportDate}/transactions`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
        fetch(`/api/v1/payments/reconciliation/${reportDate}/summaries`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
        fetch(`/api/v1/payments/reconciliation/${reportDate}/discrepancies`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
      ]);

      if (reportRes.ok) {
        const data = await reportRes.json();
        setReport(data);
      }
      if (transactionsRes.ok) {
        const data = await transactionsRes.json();
        setTransactions(data);
      }
      if (summariesRes.ok) {
        const data = await summariesRes.json();
        setPaymentMethodSummaries(data);
      }
      if (discrepanciesRes.ok) {
        const data = await discrepanciesRes.json();
        setDiscrepancies(data);
      }
    } catch (error) {
      console.error('Failed to load reconciliation data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleRowExpansion = (transactionId: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(transactionId)) {
      newExpanded.delete(transactionId);
    } else {
      newExpanded.add(transactionId);
    }
    setExpandedRows(newExpanded);
  };

  const reportDiscrepancy = (transaction: Transaction) => {
    setSelectedTransaction(transaction);
    setShowDiscrepancyModal(true);
  };

  const submitDiscrepancy = async () => {
    if (!selectedTransaction || !discrepancyNote.trim()) {
      alert('Masukkan catatan diskrepansi');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/payments/reconciliation/discrepancies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          transaction_id: selectedTransaction.id,
          note: discrepancyNote,
        }),
      });

      if (response.ok) {
        alert('Diskrepansi berhasil dilaporkan');
        setShowDiscrepancyModal(false);
        setDiscrepancyNote('');
        loadReconciliationData();
      }
    } catch (error) {
      console.error('Failed to report discrepancy:', error);
      alert('Gagal melaporkan diskrepansi');
    } finally {
      setIsLoading(false);
    }
  };

  const resolveDiscrepancy = (discrepancy: Discrepancy) => {
    setSelectedTransaction(transactions.find(t => t.id === discrepancy.transaction_id) || null);
    setResolutionNote(discrepancy.resolution_note);
    setShowResolutionModal(true);
  };

  const submitResolution = async () => {
    if (!resolutionNote.trim()) {
      alert('Masukkan catatan resolusi');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/payments/reconciliation/discrepancies/resolve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          note: resolutionNote,
        }),
      });

      if (response.ok) {
        alert('Resolusi berhasil disimpan');
        setShowResolutionModal(false);
        setResolutionNote('');
        loadReconciliationData();
      }
    } catch (error) {
      console.error('Failed to resolve discrepancy:', error);
      alert('Gagal menyimpan resolusi');
    } finally {
      setIsLoading(false);
    }
  };

  const verifyReconciliation = async () => {
    if (!report) return;

    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/payments/reconciliation/${reportDate}/verify`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        alert('Rekonsiliasi berhasil diverifikasi');
        loadReconciliationData();
      }
    } catch (error) {
      console.error('Failed to verify reconciliation:', error);
      alert('Gagal memverifikasi rekonsiliasi');
    } finally {
      setIsLoading(false);
    }
  };

  const exportToExcel = async () => {
    setIsExporting(true);
    try {
      const response = await fetch(`/api/v1/payments/reconciliation/${reportDate}/export`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Rekonsiliasi-${reportDate}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Failed to export:', error);
      alert('Gagal mengekspor data');
    } finally {
      setIsExporting(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleTimeString('id-ID', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    });
  };

  const getPaymentMethodIcon = (method: string) => {
    const icons = {
      cash: DollarSign,
      card: CreditCard,
      transfer: Building,
      va: CreditCard,
      gateway: Smartphone,
      bpjs: CreditCard,
      insurance: CreditCard,
    };
    return icons[method as keyof typeof icons] || DollarSign;
  };

  const getPaymentMethodName = (method: string) => {
    const names = {
      cash: 'Tunai',
      card: 'Kartu',
      transfer: 'Transfer',
      va: 'Virtual Account',
      gateway: 'Payment Gateway',
      bpjs: 'BPJS',
      insurance: 'Asuransi',
    };
    return names[method as keyof typeof names] || method;
  };

  const getStatusBadge = (status: string) => {
    const config = {
      verified: { bg: 'bg-green-100', text: 'text-green-800', label: 'Terverifikasi' },
      discrepancy: { bg: 'bg-red-100', text: 'text-red-800', label: 'Diskrepansi' },
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Pending' },
    };
    const c = config[status as keyof typeof config] || config.pending;
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>
        {c.label}
      </span>
    );
  };

  const filteredTransactions = transactions.filter(transaction => {
    const matchesSearch =
      !searchTerm ||
      transaction.transaction_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      transaction.patient_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      transaction.invoice_number.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesMethod = !filterMethod || transaction.payment_method === filterMethod;
    const matchesStatus = !filterStatus || transaction.status === filterStatus;

    return matchesSearch && matchesMethod && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <FileText className="h-6 w-6 mr-2" />
            Rekonsiliasi Pembayaran
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Cocokkan transaksi harian dan tangani diskrepansi
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={exportToExcel}
            disabled={isExporting || !report}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            {isExporting ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Mengekspor...
              </>
            ) : (
              <>
                <Download className="h-4 w-4 mr-2" />
                Export Excel
              </>
            )}
          </button>
          <button
            onClick={loadReconciliationData}
            disabled={isLoading}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Date Selector */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Calendar className="h-5 w-5 text-gray-400" />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tanggal Laporan</label>
              <input
                type="date"
                value={reportDate}
                onChange={(e) => setReportDate(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          {report && (
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-gray-600">Status Laporan</p>
                {report.status === 'matched' ? (
                  <div className="flex items-center justify-end mt-1">
                    <CheckCircle className="h-5 w-5 text-green-600 mr-1" />
                    <span className="text-sm font-medium text-green-600">Cocok</span>
                  </div>
                ) : report.status === 'discrepancy' ? (
                  <div className="flex items-center justify-end mt-1">
                    <AlertCircle className="h-5 w-5 text-red-600 mr-1" />
                    <span className="text-sm font-medium text-red-600">Ada Diskrepansi</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-end mt-1">
                    <AlertCircle className="h-5 w-5 text-yellow-600 mr-1" />
                    <span className="text-sm font-medium text-yellow-600">Pending</span>
                  </div>
                )}
              </div>
              {report.status === 'matched' && !report.verified_by && (
                <button
                  onClick={verifyReconciliation}
                  disabled={isLoading}
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Verifikasi
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {report && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Transaksi</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{report.total_transactions}</p>
                </div>
                <FileText className="h-8 w-8 text-blue-600" />
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Diharapkan</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {formatCurrency(report.total_expected)}
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-600" />
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Aktual</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {formatCurrency(report.total_actual)}
                  </p>
                </div>
                <DollarSign className="h-8 w-8 text-blue-600" />
              </div>
            </div>

            <div className={`shadow rounded-lg p-6 ${
              report.discrepancy === 0 ? 'bg-green-50' : 'bg-red-50'
            }`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Diskrepansi</p>
                  <p className={`text-2xl font-bold mt-1 ${
                    report.discrepancy === 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatCurrency(Math.abs(report.discrepancy))}
                  </p>
                  {report.discrepancy !== 0 && (
                    <p className="text-xs text-red-600 mt-1">
                      {report.discrepancy_percentage.toFixed(2)}%
                    </p>
                  )}
                </div>
                {report.discrepancy === 0 ? (
                  <CheckCircle className="h-8 w-8 text-green-600" />
                ) : (
                  <AlertCircle className="h-8 w-8 text-red-600" />
                )}
              </div>
            </div>
          </div>

          {/* Payment Method Breakdown */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Ringkasan Metode Pembayaran</h3>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Metode</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Jumlah Transaksi</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Diharapkan</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Aktual</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Diskrepansi</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {paymentMethodSummaries.map((summary) => {
                    const Icon = getPaymentMethodIcon(summary.method);
                    return (
                      <tr key={summary.method} className="hover:bg-gray-50">
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <Icon className="h-5 w-5 text-gray-400 mr-2" />
                            <span className="text-sm font-medium text-gray-900">
                              {summary.method_name}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm text-center text-gray-900">
                          {summary.transaction_count}
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                          {formatCurrency(summary.expected_amount)}
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                          {formatCurrency(summary.total_amount)}
                        </td>
                        <td className={`px-4 py-4 whitespace-nowrap text-sm text-right font-medium ${
                          summary.discrepancy === 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatCurrency(Math.abs(summary.discrepancy))}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Transactions List */}
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Daftar Transaksi</h3>
                <div className="flex gap-2">
                  <select
                    value={filterMethod}
                    onChange={(e) => setFilterMethod(e.target.value)}
                    className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Semua Metode</option>
                    <option value="cash">Tunai</option>
                    <option value="card">Kartu</option>
                    <option value="transfer">Transfer</option>
                    <option value="gateway">Gateway</option>
                  </select>
                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Semua Status</option>
                    <option value="verified">Terverifikasi</option>
                    <option value="discrepancy">Diskrepansi</option>
                    <option value="pending">Pending</option>
                  </select>
                </div>
              </div>

              <div className="mb-4">
                <div className="relative">
                  <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Cari transaksi..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {filteredTransactions.map((transaction) => {
                  const Icon = getPaymentMethodIcon(transaction.payment_method);
                  const isExpanded = expandedRows.has(transaction.id);

                  return (
                    <div key={transaction.id} className="border rounded-lg">
                      <div
                        className="p-3 cursor-pointer hover:bg-gray-50"
                        onClick={() => toggleRowExpansion(transaction.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center flex-1">
                            <Icon className="h-5 w-5 text-gray-400 mr-2" />
                            <div className="flex-1">
                              <div className="flex items-center justify-between">
                                <p className="text-sm font-medium text-gray-900">
                                  {transaction.transaction_number}
                                </p>
                                <div className="flex items-center gap-2">
                                  {getStatusBadge(transaction.status)}
                                  {isExpanded ? (
                                    <ChevronUp className="h-4 w-4 text-gray-400" />
                                  ) : (
                                    <ChevronDown className="h-4 w-4 text-gray-400" />
                                  )}
                                </div>
                              </div>
                              <p className="text-xs text-gray-500 mt-1">
                                {transaction.patient_name} - {transaction.invoice_number}
                              </p>
                            </div>
                          </div>
                          <div className="ml-4 text-right">
                            <p className="text-sm font-bold text-gray-900">
                              {formatCurrency(transaction.amount)}
                            </p>
                            <p className="text-xs text-gray-500">{formatTime(transaction.transaction_time)}</p>
                          </div>
                        </div>
                      </div>

                      {isExpanded && (
                        <div className="px-3 pb-3 border-t border-gray-100 pt-3">
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                              <span className="text-gray-500">Metode: </span>
                              <span className="font-medium text-gray-900">
                                {getPaymentMethodName(transaction.payment_method)}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-500">Referensi: </span>
                              <span className="font-medium text-gray-900">
                                {transaction.reference_number || '-'}
                              </span>
                            </div>
                          </div>

                          {transaction.status === 'discrepancy' && transaction.discrepancy_note && (
                            <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded">
                              <p className="text-xs text-red-800">
                                <strong>Catatan Diskrepansi:</strong> {transaction.discrepancy_note}
                              </p>
                            </div>
                          )}

                          {transaction.status === 'pending' && (
                            <div className="mt-2">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  reportDiscrepancy(transaction);
                                }}
                                className="text-xs text-red-600 hover:text-red-800"
                              >
                                Laporkan Diskrepansi
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {filteredTransactions.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>Tidak ada transaksi ditemukan</p>
                </div>
              )}
            </div>

            {/* Discrepancies */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Diskrepansi
                <span className="ml-2 text-sm font-normal text-gray-500">
                  ({discrepancies.length})
                </span>
              </h3>

              {discrepancies.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>Tidak ada diskrepansi</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {discrepancies.map((discrepancy) => (
                    <div key={discrepancy.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900">
                            {discrepancy.transaction_number}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            Diharapkan: {formatCurrency(discrepancy.expected_amount)}
                          </p>
                          <p className="text-xs text-gray-500">
                            Aktual: {formatCurrency(discrepancy.actual_amount)}
                          </p>
                        </div>
                        <div className={`flex items-center ${
                          discrepancy.type === 'shortage' ? 'text-red-600' : 'text-orange-600'
                        }`}>
                          {discrepancy.type === 'shortage' ? (
                            <TrendingDown className="h-5 w-5 mr-1" />
                          ) : (
                            <TrendingUp className="h-5 w-5 mr-1" />
                          )}
                          <span className="text-sm font-bold">
                            {formatCurrency(Math.abs(discrepancy.discrepancy))}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between mt-3 pt-3 border-t">
                        <div>
                          {discrepancy.status === 'pending' ? (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              Pending
                            </span>
                          ) : discrepancy.status === 'resolved' ? (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              Terselesaikan
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Disetujui
                            </span>
                          )}
                        </div>
                        {discrepancy.status === 'pending' && (
                          <button
                            onClick={() => resolveDiscrepancy(discrepancy)}
                            className="text-xs text-blue-600 hover:text-blue-800"
                          >
                            Selesaikan
                          </button>
                        )}
                      </div>

                      {discrepancy.resolution_note && (
                        <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded">
                          <p className="text-xs text-blue-800">
                            <strong>Resolusi:</strong> {discrepancy.resolution_note}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Verification Info */}
          {report.verified_by && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center">
                <CheckCircle className="h-6 w-6 text-green-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-green-900">Laporan Terverifikasi</p>
                  <p className="text-xs text-green-700">
                    Oleh {report.verified_by} {report.verified_at ? `pada ${formatDate(report.verified_at)}` : ''}
                  </p>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Discrepancy Modal */}
      {showDiscrepancyModal && selectedTransaction && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Laporkan Diskrepansi</h2>
              <button
                onClick={() => {
                  setShowDiscrepancyModal(false);
                  setDiscrepancyNote('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6">
              <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm font-medium text-gray-900">{selectedTransaction.transaction_number}</p>
                <p className="text-xs text-gray-500 mt-1">
                  Jumlah: {formatCurrency(selectedTransaction.amount)}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Catatan Diskrepansi
                </label>
                <textarea
                  value={discrepancyNote}
                  onChange={(e) => setDiscrepancyNote(e.target.value)}
                  rows={4}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Jelaskan diskrepansi yang ditemukan..."
                />
              </div>
            </div>

            <div className="border-t px-6 py-4 flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowDiscrepancyModal(false);
                  setDiscrepancyNote('');
                }}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={submitDiscrepancy}
                disabled={isLoading}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Memproses...
                  </>
                ) : (
                  <>
                    <AlertCircle className="h-4 w-4 mr-2" />
                    Laporkan
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Resolution Modal */}
      {showResolutionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Selesaikan Diskrepansi</h2>
              <button
                onClick={() => {
                  setShowResolutionModal(false);
                  setResolutionNote('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Catatan Resolusi
                </label>
                <textarea
                  value={resolutionNote}
                  onChange={(e) => setResolutionNote(e.target.value)}
                  rows={4}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Jelaskan bagaimana diskrepansi diselesaikan..."
                />
              </div>
            </div>

            <div className="border-t px-6 py-4 flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowResolutionModal(false);
                  setResolutionNote('');
                }}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={submitResolution}
                disabled={isLoading}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Memproses...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Simpan Resolusi
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
