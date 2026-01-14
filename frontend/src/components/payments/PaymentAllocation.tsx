"""Payment Allocation Component

Payment allocation system with:
- Unpaid invoices list
- Auto-allocate logic (FIFO, by date, by amount)
- Manual allocation
- Allocation history
- Balance tracking
"""

import { useState, useEffect } from 'react';
import {
  DollarSign,
  ArrowRight,
  Calendar,
  User,
  FileText,
  Scale,
  History,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Settings,
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

// Types
interface UnpaidInvoice {
  id: number;
  invoice_number: string;
  patient_id: number;
  patient_name: string;
  invoice_date: string;
  due_date: string;
  total_amount: number;
  paid_amount: number;
  balance_due: number;
  days_overdue: number;
  priority: 'high' | 'medium' | 'low';
}

interface Payment {
  id: number;
  payment_date: string;
  amount: number;
  payment_method: string;
  reference_number: string;
  unallocated_amount: number;
  status: 'pending' | 'allocated' | 'partial';
}

interface Allocation {
  id: number;
  payment_id: number;
  invoice_id: number;
  allocated_amount: number;
  allocation_date: string;
  allocated_by: string;
}

interface AllocationRule {
  id: string;
  name: string;
  name_id: string;
  description: string;
}

export function PaymentAllocation() {
  const [unpaidInvoices, setUnpaidInvoices] = useState<UnpaidInvoice[]>([]);
  const [pendingPayments, setPendingPayments] = useState<Payment[]>([]);
  const [allocations, setAllocations] = useState<Allocation[]>([]);
  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
  const [selectedInvoices, setSelectedInvoices] = useState<Set<number>>(new Set());
  const [allocationAmounts, setAllocationAmounts] = useState<Map<number, number>>(new Map());
  const [showHistory, setShowHistory] = useState(false);
  const [showAutoAllocate, setShowAutoAllocate] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [filters, setFilters] = useState({
    patient: '',
    priority: '',
    date_from: '',
    date_to: '',
  });

  const allocationRules: AllocationRule[] = [
    {
      id: 'fifo',
      name: 'FIFO',
      name_id: 'FIFO (First In First Out)',
      description: 'Alokasikan pembayaran ke faktur tertua terlebih dahulu',
    },
    {
      id: 'due_date',
      name: 'Due Date',
      name_id: 'Tanggal Jatuh Tempo',
      description: 'Alokasikan pembayaran ke faktur dengan jatuh tempo terdekat',
    },
    {
      id: 'amount',
      name: 'Amount',
      name_id: 'Jumlah Terkecil',
      description: 'Alokasikan pembayaran ke faktur dengan jumlah terkecil',
    },
    {
      id: 'priority',
      name: 'Priority',
      name_id: 'Prioritas',
      description: 'Alokasikan pembayaran berdasarkan prioritas faktur',
    },
  ];

  const [selectedRule, setSelectedRule] = useState('fifo');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [invoicesRes, paymentsRes, allocationsRes] = await Promise.all([
        fetch('/api/v1/payments/invoices/unpaid', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
        fetch('/api/v1/payments/pending', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
        fetch('/api/v1/payments/allocations', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
      ]);

      if (invoicesRes.ok) {
        const data = await invoicesRes.json();
        setUnpaidInvoices(data);
      }
      if (paymentsRes.ok) {
        const data = await paymentsRes.json();
        setPendingPayments(data);
      }
      if (allocationsRes.ok) {
        const data = await allocationsRes.json();
        setAllocations(data);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleInvoiceSelection = (invoiceId: number) => {
    const newSelected = new Set(selectedInvoices);
    if (newSelected.has(invoiceId)) {
      newSelected.delete(invoiceId);
      allocationAmounts.delete(invoiceId);
    } else {
      newSelected.add(invoiceId);
    }
    setSelectedInvoices(newSelected);
    setAllocationAmounts(new Map(allocationAmounts));
  };

  const updateAllocationAmount = (invoiceId: number, amount: number) => {
    const newAmounts = new Map(allocationAmounts);
    newAmounts.set(invoiceId, amount);
    setAllocationAmounts(newAmounts);
  };

  const getTotalAllocated = () => {
    let total = 0;
    allocationAmounts.forEach((amount) => {
      total += amount;
    });
    return total;
  };

  const getRemainingAllocation = () => {
    if (!selectedPayment) return 0;
    return selectedPayment.unallocated_amount - getTotalAllocated();
  };

  const autoAllocate = () => {
    if (!selectedPayment) return;

    let sortedInvoices = [...unpaidInvoices];
    const availableAmount = selectedPayment.unallocated_amount;

    // Sort based on selected rule
    switch (selectedRule) {
      case 'fifo':
        sortedInvoices.sort((a, b) => new Date(a.invoice_date).getTime() - new Date(b.invoice_date).getTime());
        break;
      case 'due_date':
        sortedInvoices.sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime());
        break;
      case 'amount':
        sortedInvoices.sort((a, b) => a.balance_due - b.balance_due);
        break;
      case 'priority':
        const priorityOrder = { high: 0, medium: 1, low: 2 };
        sortedInvoices.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
        break;
    }

    const newSelected = new Set<number>();
    const newAmounts = new Map<number, number>();
    let remaining = availableAmount;

    for (const invoice of sortedInvoices) {
      if (remaining <= 0) break;

      const allocateAmount = Math.min(invoice.balance_due, remaining);
      newSelected.add(invoice.id);
      newAmounts.set(invoice.id, allocateAmount);
      remaining -= allocateAmount;
    }

    setSelectedInvoices(newSelected);
    setAllocationAmounts(newAmounts);
    setShowAutoAllocate(false);
  };

  const allocatePayment = async () => {
    if (!selectedPayment || selectedInvoices.size === 0) {
      alert('Pilih faktur untuk alokasi pembayaran');
      return;
    }

    const totalAllocated = getTotalAllocated();
    if (totalAllocated > selectedPayment.unallocated_amount) {
      alert('Total alokasi melebihi jumlah pembayaran yang tersedia');
      return;
    }

    setIsLoading(true);
    try {
      const allocationsData = Array.from(selectedInvoices).map(invoiceId => ({
        payment_id: selectedPayment.id,
        invoice_id: invoiceId,
        amount: allocationAmounts.get(invoiceId) || 0,
      }));

      const response = await fetch('/api/v1/payments/allocations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ allocations: allocationsData }),
      });

      if (response.ok) {
        alert('Pembayaran berhasil dialokasikan');
        resetAllocation();
        loadData();
      } else {
        alert('Gagal mengalokasikan pembayaran');
      }
    } catch (error) {
      console.error('Failed to allocate payment:', error);
      alert('Gagal mengalokasikan pembayaran');
    } finally {
      setIsLoading(false);
    }
  };

  const resetAllocation = () => {
    setSelectedPayment(null);
    setSelectedInvoices(new Set());
    setAllocationAmounts(new Map());
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

  const getPriorityBadge = (priority: string) => {
    const config = {
      high: { bg: 'bg-red-100', text: 'text-red-800', label: 'Tinggi' },
      medium: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Sedang' },
      low: { bg: 'bg-green-100', text: 'text-green-800', label: 'Rendah' },
    };
    const c = config[priority as keyof typeof config] || config.low;
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>
        {c.label}
      </span>
    );
  };

  const filteredInvoices = unpaidInvoices.filter(invoice => {
    const matchesPatient = !filters.patient || invoice.patient_name.toLowerCase().includes(filters.patient.toLowerCase());
    const matchesPriority = !filters.priority || invoice.priority === filters.priority;
    const matchesFromDate = !filters.date_from || new Date(invoice.invoice_date) >= new Date(filters.date_from);
    const matchesToDate = !filters.date_to || new Date(invoice.invoice_date) <= new Date(filters.date_to);

    return matchesPatient && matchesPriority && matchesFromDate && matchesToDate;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Scale className="h-6 w-6 mr-2" />
            Alokasi Pembayaran
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Kelola alokasi pembayaran ke faktur yang belum lunas
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <History className="h-4 w-4 mr-2" />
            Riwayat Alokasi
          </button>
          <button
            onClick={loadData}
            disabled={isLoading}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Pending Payments */}
        <div className="space-y-6">
          {/* Pending Payments List */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Pembayaran Tertunda</h3>

            {pendingPayments.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <DollarSign className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Tidak ada pembayaran yang perlu dialokasikan</p>
              </div>
            ) : (
              <div className="space-y-3">
                {pendingPayments.map((payment) => (
                  <div
                    key={payment.id}
                    onClick={() => {
                      setSelectedPayment(payment);
                      setSelectedInvoices(new Set());
                      setAllocationAmounts(new Map());
                    }}
                    className={`border rounded-lg p-4 cursor-pointer transition-all ${
                      selectedPayment?.id === payment.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <DollarSign className="h-5 w-5 text-gray-400 mr-2" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {formatDate(payment.payment_date)}
                          </p>
                          <p className="text-xs text-gray-500">{payment.payment_method}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-bold text-green-600">
                          {formatCurrency(payment.unallocated_amount)}
                        </p>
                        <p className="text-xs text-gray-500">Tersedia</p>
                      </div>
                    </div>
                    {payment.reference_number && (
                      <p className="text-xs text-gray-500">Ref: {payment.reference_number}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Allocation Summary */}
          {selectedPayment && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-blue-900 mb-4">Ringkasan Alokasi</h3>

              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-blue-700">Total Pembayaran</span>
                  <span className="font-medium text-blue-900">
                    {formatCurrency(selectedPayment.unallocated_amount)}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-blue-700">Total Dialokasikan</span>
                  <span className="font-medium text-blue-900">
                    {formatCurrency(getTotalAllocated())}
                  </span>
                </div>
                <div className="flex justify-between text-lg font-bold border-t border-blue-300 pt-3">
                  <span className="text-blue-900">Sisa</span>
                  <span className={getRemainingAllocation() >= 0 ? 'text-blue-600' : 'text-red-600'}>
                    {formatCurrency(Math.abs(getRemainingAllocation()))}
                  </span>
                </div>
              </div>

              {/* Auto Allocate Button */}
              <button
                onClick={() => setShowAutoAllocate(!showAutoAllocate)}
                className="mt-4 w-full inline-flex items-center justify-center px-4 py-2 border border-blue-300 rounded-md text-sm font-medium text-blue-700 bg-white hover:bg-blue-50"
              >
                <Settings className="h-4 w-4 mr-2" />
                Auto Alokasi
              </button>

              {/* Auto Allocate Options */}
              {showAutoAllocate && (
                <div className="mt-4 p-4 bg-white rounded-lg border border-blue-200">
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Pilih Metode Auto Alokasi</h4>
                  <div className="space-y-2">
                    {allocationRules.map((rule) => (
                      <label
                        key={rule.id}
                        className={`flex items-start p-3 border rounded-md cursor-pointer ${
                          selectedRule === rule.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                        }`}
                      >
                        <input
                          type="radio"
                          name="allocation-rule"
                          value={rule.id}
                          checked={selectedRule === rule.id}
                          onChange={(e) => setSelectedRule(e.target.value)}
                          className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500"
                        />
                        <div className="ml-3">
                          <p className="text-sm font-medium text-gray-900">{rule.name_id}</p>
                          <p className="text-xs text-gray-500">{rule.description}</p>
                        </div>
                      </label>
                    ))}
                  </div>
                  <button
                    onClick={autoAllocate}
                    className="mt-3 w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Terapkan Auto Alokasi
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column - Unpaid Invoices */}
        <div className="space-y-6">
          {/* Filters */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <Filter className="h-5 w-5 mr-2" />
                Filter Faktur
              </h3>
              <button
                onClick={() => setFilters({ patient: '', priority: '', date_from: '', date_to: '' })}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Reset
              </button>
            </div>

            <div className="space-y-3">
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
                <label className="block text-sm font-medium text-gray-700 mb-1">Prioritas</label>
                <select
                  value={filters.priority}
                  onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Semua Prioritas</option>
                  <option value="high">Tinggi</option>
                  <option value="medium">Sedang</option>
                  <option value="low">Rendah</option>
                </select>
              </div>
            </div>
          </div>

          {/* Unpaid Invoices List */}
          {selectedPayment && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Faktur Belum Lunas
                <span className="ml-2 text-sm font-normal text-gray-500">
                  ({selectedInvoices.size} dipilih)
                </span>
              </h3>

              <div className="space-y-3 max-h-96 overflow-y-auto">
                {filteredInvoices.map((invoice) => (
                  <div
                    key={invoice.id}
                    className={`border rounded-lg p-4 transition-all ${
                      selectedInvoices.has(invoice.id)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start flex-1">
                        <input
                          type="checkbox"
                          checked={selectedInvoices.has(invoice.id)}
                          onChange={() => toggleInvoiceSelection(invoice.id)}
                          className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <div className="ml-3 flex-1">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-gray-900">
                                {invoice.invoice_number}
                              </p>
                              <p className="text-xs text-gray-500 flex items-center mt-1">
                                <User className="h-3 w-3 mr-1" />
                                {invoice.patient_name}
                              </p>
                            </div>
                            {getPriorityBadge(invoice.priority)}
                          </div>
                          <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                            <span className="flex items-center">
                              <Calendar className="h-3 w-3 mr-1" />
                              {formatDate(invoice.due_date)}
                            </span>
                            {invoice.days_overdue > 0 && (
                              <span className="text-red-600">
                                {invoice.days_overdue} hari terlambat
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>

                    {selectedInvoices.has(invoice.id) && (
                      <div className="mt-3 pt-3 border-t border-blue-200">
                        <div className="flex items-center justify-between text-sm mb-2">
                          <span className="text-gray-600">Jumlah Alokasi</span>
                          <span className="font-medium text-gray-900">
                            {formatCurrency(invoice.balance_due)}
                          </span>
                        </div>
                        <input
                          type="number"
                          value={allocationAmounts.get(invoice.id) || ''}
                          onChange={(e) => updateAllocationAmount(invoice.id, parseFloat(e.target.value) || 0)}
                          max={invoice.balance_due}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Masukkan jumlah alokasi"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Maksimum: {formatCurrency(invoice.balance_due)}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Allocate Button */}
              <button
                onClick={allocatePayment}
                disabled={selectedInvoices.size === 0 || isLoading}
                className="mt-4 w-full inline-flex items-center justify-center px-4 py-3 border border-transparent rounded-md text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Memproses...
                  </>
                ) : (
                  <>
                    <ArrowRight className="h-4 w-4 mr-2" />
                    Alokasikan Pembayaran
                  </>
                )}
              </button>
            </div>
          )}

          {!selectedPayment && (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="text-center py-8 text-gray-500">
                <DollarSign className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Pilih pembayaran untuk mulai mengalokasikan</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Allocation History Modal */}
      {showHistory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Riwayat Alokasi</h2>
              <button
                onClick={() => setShowHistory(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <AlertCircle className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6">
              {allocations.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <History className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>Belum ada riwayat alokasi</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {allocations.map((allocation) => (
                    <div key={allocation.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            Payment ID: {allocation.payment_id}
                          </p>
                          <p className="text-xs text-gray-500">
                            Invoice ID: {allocation.invoice_id}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-bold text-green-600">
                            {formatCurrency(allocation.allocated_amount)}
                          </p>
                          <p className="text-xs text-gray-500">
                            {formatDate(allocation.allocation_date)}
                          </p>
                        </div>
                      </div>
                      <p className="text-xs text-gray-500 mt-2">
                        Oleh: {allocation.allocated_by}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
