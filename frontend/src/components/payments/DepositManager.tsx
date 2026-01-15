/**
 * Deposit Manager Component
 *
Deposit management system with:
- Deposit creation
- Deposit usage tracking
- Balance inquiry
- Deposit history
- Refund handling

 */

import { useState, useEffect } from 'react';
import {
  Wallet,
  Plus,
  Search,
  Calendar,
  User,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  FileText,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  Receipt,
  XCircle,
} from 'lucide-react';

// Types
interface Deposit {
  id: number;
  deposit_number: string;
  patient_id: number;
  patient_name: string;
  deposit_date: string;
  amount: number;
  balance: number;
  status: 'active' | 'frozen' | 'closed';
  created_by: string;
  notes: string;
}

interface DepositTransaction {
  id: number;
  deposit_id: number;
  transaction_type: 'credit' | 'debit' | 'refund';
  amount: number;
  balance_after: number;
  reference_number: string;
  reference_type: string;
  transaction_date: string;
  description: string;
}

interface DepositForm {
  patient_id: number;
  amount: number;
  payment_method: string;
  reference_number: string;
  notes: string;
}

export function DepositManager() {
  const [deposits, setDeposits] = useState<Deposit[]>([]);
  const [selectedDeposit, setSelectedDeposit] = useState<Deposit | null>(null);
  const [transactions, setTransactions] = useState<DepositTransaction[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [showRefundModal, setShowRefundModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [depositForm, setDepositForm] = useState<DepositForm>({
    patient_id: 0,
    amount: 0,
    payment_method: 'cash',
    reference_number: '',
    notes: '',
  });
  const [refundAmount, setRefundAmount] = useState(0);
  const [refundReason, setRefundReason] = useState('');

  useEffect(() => {
    loadDeposits();
  }, []);

  const loadDeposits = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/payments/deposits', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDeposits(data);
      }
    } catch (error) {
      console.error('Failed to load deposits:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadDepositTransactions = async (depositId: number) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/payments/deposits/${depositId}/transactions`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTransactions(data);
      }
    } catch (error) {
      console.error('Failed to load transactions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const selectDeposit = (deposit: Deposit) => {
    setSelectedDeposit(deposit);
    loadDepositTransactions(deposit.id);
  };

  const createDeposit = async () => {
    if (depositForm.patient_id === 0) {
      alert('Pilih pasien');
      return;
    }

    if (depositForm.amount <= 0) {
      alert('Masukkan jumlah deposit yang valid');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/payments/deposits', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(depositForm),
      });

      if (response.ok) {
        alert('Deposit berhasil dibuat');
        setShowCreateModal(false);
        resetDepositForm();
        loadDeposits();
      } else {
        alert('Gagal membuat deposit');
      }
    } catch (error) {
      console.error('Failed to create deposit:', error);
      alert('Gagal membuat deposit');
    } finally {
      setIsLoading(false);
    }
  };

  const processRefund = async () => {
    if (!selectedDeposit) return;

    if (refundAmount <= 0 || refundAmount > selectedDeposit.balance) {
      alert('Masukkan jumlah refund yang valid');
      return;
    }

    if (!refundReason.trim()) {
      alert('Masukkan alasan refund');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/payments/deposits/${selectedDeposit.id}/refund`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          amount: refundAmount,
          reason: refundReason,
        }),
      });

      if (response.ok) {
        alert('Refund berhasil diproses');
        setShowRefundModal(false);
        setRefundAmount(0);
        setRefundReason('');
        loadDeposits();
        if (selectedDeposit) {
          loadDepositTransactions(selectedDeposit.id);
        }
      } else {
        alert('Gagal memproses refund');
      }
    } catch (error) {
      console.error('Failed to process refund:', error);
      alert('Gagal memproses refund');
    } finally {
      setIsLoading(false);
    }
  };

  const resetDepositForm = () => {
    setDepositForm({
      patient_id: 0,
      amount: 0,
      payment_method: 'cash',
      reference_number: '',
      notes: '',
    });
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
    const config = {
      active: { bg: 'bg-green-100', text: 'text-green-800', label: 'Aktif' },
      frozen: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Dibekukan' },
      closed: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Tutup' },
    };
    const c = config[status as keyof typeof config] || config.active;
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>
        {c.label}
      </span>
    );
  };

  const filteredDeposits = deposits.filter(deposit =>
    deposit.patient_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    deposit.deposit_number.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalActiveDeposits = deposits
    .filter(d => d.status === 'active')
    .reduce((sum, d) => sum + d.balance, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Wallet className="h-6 w-6 mr-2" />
            Manajemen Deposit Pasien
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Kelola deposit pasien dan pantau penggunaan
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Buat Deposit Baru
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Deposit Aktif</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {formatCurrency(totalActiveDeposits)}
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Jumlah Deposit Aktif</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {deposits.filter(d => d.status === 'active').length}
              </p>
            </div>
            <Wallet className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Deposit Bulan Ini</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {formatCurrency(
                  deposits
                    .filter(d => {
                      const depositDate = new Date(d.deposit_date);
                      const now = new Date();
                      return depositDate.getMonth() === now.getMonth() &&
                             depositDate.getFullYear() === now.getFullYear();
                    })
                    .reduce((sum, d) => sum + d.amount, 0)
                )}
              </p>
            </div>
            <Calendar className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Deposits List */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Daftar Deposit</h3>
            <button
              onClick={loadDeposits}
              disabled={isLoading}
              className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <RefreshCw className={`h-4 w-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          <div className="mb-4">
            <div className="relative">
              <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Cari nama pasien atau no. deposit..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {filteredDeposits.map((deposit) => (
              <div
                key={deposit.id}
                onClick={() => selectDeposit(deposit)}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  selectedDeposit?.id === deposit.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <User className="h-5 w-5 text-gray-400 mr-2" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {deposit.patient_name}
                      </p>
                      <p className="text-xs text-gray-500">{deposit.deposit_number}</p>
                    </div>
                  </div>
                  {getStatusBadge(deposit.status)}
                </div>

                <div className="flex items-center justify-between text-sm">
                  <div>
                    <p className="text-gray-600">Saldo</p>
                    <p className="text-lg font-bold text-blue-600">
                      {formatCurrency(deposit.balance)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-gray-600">Total Deposit</p>
                    <p className="text-sm font-medium text-gray-900">
                      {formatCurrency(deposit.amount)}
                    </p>
                  </div>
                </div>

                <div className="mt-2 pt-2 border-t border-gray-200">
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span className="flex items-center">
                      <Calendar className="h-3 w-3 mr-1" />
                      {formatDate(deposit.deposit_date)}
                    </span>
                    <span>{deposit.created_by}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredDeposits.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Wallet className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Tidak ada deposit ditemukan</p>
            </div>
          )}
        </div>

        {/* Right Column - Deposit Details */}
        {selectedDeposit ? (
          <div className="space-y-6">
            {/* Deposit Info */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Detail Deposit</h3>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-500">Nomor Deposit</p>
                  <p className="text-sm font-medium text-gray-900">{selectedDeposit.deposit_number}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Status</p>
                  <div className="mt-1">{getStatusBadge(selectedDeposit.status)}</div>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Pasien</p>
                  <p className="text-sm font-medium text-gray-900">{selectedDeposit.patient_name}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Tanggal Deposit</p>
                  <p className="text-sm font-medium text-gray-900">{formatDate(selectedDeposit.deposit_date)}</p>
                </div>
              </div>

              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-blue-700">Saldo Tersedia</p>
                    <p className="text-2xl font-bold text-blue-900">
                      {formatCurrency(selectedDeposit.balance)}
                    </p>
                  </div>
                  <Wallet className="h-8 w-8 text-blue-600" />
                </div>
              </div>

              {selectedDeposit.notes && (
                <div className="mt-4">
                  <p className="text-xs text-gray-500">Catatan</p>
                  <p className="text-sm text-gray-900 mt-1">{selectedDeposit.notes}</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => setShowHistoryModal(true)}
                  className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <Receipt className="h-4 w-4 mr-2" />
                  Riwayat Transaksi
                </button>
                {selectedDeposit.status === 'active' && selectedDeposit.balance > 0 && (
                  <button
                    onClick={() => setShowRefundModal(true)}
                    className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-red-300 rounded-md text-sm font-medium text-red-700 bg-white hover:bg-red-50"
                  >
                    <TrendingDown className="h-4 w-4 mr-2" />
                    Refund
                  </button>
                )}
              </div>
            </div>

            {/* Recent Transactions */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Transaksi Terakhir</h3>

              {transactions.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Receipt className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>Belum ada transaksi</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {transactions.slice(0, 5).map((transaction) => {
                    const isCredit = transaction.transaction_type === 'credit';
                    const isRefund = transaction.transaction_type === 'refund';

                    return (
                      <div key={transaction.id} className="border rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            {isCredit ? (
                              <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
                            ) : isRefund ? (
                              <ArrowRight className="h-5 w-5 text-orange-600 mr-2" />
                            ) : (
                              <TrendingDown className="h-5 w-5 text-red-600 mr-2" />
                            )}
                            <div>
                              <p className="text-sm font-medium text-gray-900">
                                {transaction.description}
                              </p>
                              <p className="text-xs text-gray-500">
                                {transaction.reference_type}: {transaction.reference_number}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className={`text-sm font-bold ${
                              isCredit ? 'text-green-600' : isRefund ? 'text-orange-600' : 'text-red-600'
                            }`}>
                              {isCredit ? '+' : '-'}{formatCurrency(transaction.amount)}
                            </p>
                            <p className="text-xs text-gray-500">
                              {formatDate(transaction.transaction_date)}
                            </p>
                          </div>
                        </div>
                        <div className="mt-2 pt-2 border-t border-gray-100">
                          <p className="text-xs text-gray-500">
                            Saldo setelah: {formatCurrency(transaction.balance_after)}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-white shadow rounded-lg p-6">
            <div className="text-center py-16 text-gray-500">
              <Wallet className="h-16 w-16 mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-medium">Pilih Deposit</p>
              <p className="text-sm mt-1">Pilih deposit dari daftar untuk melihat detail</p>
            </div>
          </div>
        )}
      </div>

      {/* Create Deposit Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Buat Deposit Baru</h2>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  resetDepositForm();
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pasien</label>
                <input
                  type="text"
                  placeholder="Cari pasien..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">Masukkan nama atau RM pasien</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Jumlah Deposit</label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 font-medium">
                    Rp
                  </span>
                  <input
                    type="number"
                    value={depositForm.amount}
                    onChange={(e) => setDepositForm({
                      ...depositForm,
                      amount: parseFloat(e.target.value) || 0
                    })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                    placeholder="0"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Metode Pembayaran</label>
                <select
                  value={depositForm.payment_method}
                  onChange={(e) => setDepositForm({
                    ...depositForm,
                    payment_method: e.target.value
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="cash">Tunai</option>
                  <option value="card">Kartu Debit/Kredit</option>
                  <option value="transfer">Transfer Bank</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nomor Referensi</label>
                <input
                  type="text"
                  value={depositForm.reference_number}
                  onChange={(e) => setDepositForm({
                    ...depositForm,
                    reference_number: e.target.value
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Nomor referensi pembayaran"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Catatan</label>
                <textarea
                  value={depositForm.notes}
                  onChange={(e) => setDepositForm({
                    ...depositForm,
                    notes: e.target.value
                  })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Catatan untuk deposit ini"
                />
              </div>
            </div>

            <div className="border-t px-6 py-4 flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  resetDepositForm();
                }}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={createDeposit}
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
                    Buat Deposit
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Refund Modal */}
      {showRefundModal && selectedDeposit && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Refund Deposit</h2>
              <button
                onClick={() => {
                  setShowRefundModal(false);
                  setRefundAmount(0);
                  setRefundReason('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-blue-700">Saldo Tersedia</p>
                <p className="text-xl font-bold text-blue-900">
                  {formatCurrency(selectedDeposit.balance)}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Jumlah Refund</label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 font-medium">
                    Rp
                  </span>
                  <input
                    type="number"
                    value={refundAmount}
                    onChange={(e) => setRefundAmount(parseFloat(e.target.value) || 0)}
                    max={selectedDeposit.balance}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                    placeholder="0"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Maksimum: {formatCurrency(selectedDeposit.balance)}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Alasan Refund</label>
                <textarea
                  value={refundReason}
                  onChange={(e) => setRefundReason(e.target.value)}
                  rows={3}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Jelaskan alasan refund..."
                />
              </div>
            </div>

            <div className="border-t px-6 py-4 flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowRefundModal(false);
                  setRefundAmount(0);
                  setRefundReason('');
                }}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={processRefund}
                disabled={isLoading || refundAmount <= 0}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Memproses...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Proses Refund
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Transaction History Modal */}
      {showHistoryModal && selectedDeposit && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Riwayat Transaksi</h2>
              <button
                onClick={() => setShowHistoryModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6">
              <div className="mb-4 pb-4 border-b">
                <p className="text-sm text-gray-600">Deposit: {selectedDeposit.deposit_number}</p>
                <p className="text-xs text-gray-500">Pasien: {selectedDeposit.patient_name}</p>
              </div>

              {transactions.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Receipt className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>Belum ada transaksi</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {transactions.map((transaction) => {
                    const isCredit = transaction.transaction_type === 'credit';
                    const isRefund = transaction.transaction_type === 'refund';

                    return (
                      <div key={transaction.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center">
                            {isCredit ? (
                              <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
                            ) : isRefund ? (
                              <ArrowRight className="h-5 w-5 text-orange-600 mr-2" />
                            ) : (
                              <TrendingDown className="h-5 w-5 text-red-600 mr-2" />
                            )}
                            <div>
                              <p className="text-sm font-medium text-gray-900">
                                {transaction.description}
                              </p>
                              <p className="text-xs text-gray-500">
                                {formatDate(transaction.transaction_date)}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className={`text-lg font-bold ${
                              isCredit ? 'text-green-600' : isRefund ? 'text-orange-600' : 'text-red-600'
                            }`}>
                              {isCredit ? '+' : '-'}{formatCurrency(transaction.amount)}
                            </p>
                            <p className="text-xs text-gray-500">
                              Saldo: {formatCurrency(transaction.balance_after)}
                            </p>
                          </div>
                        </div>
                        <div className="pt-2 border-t border-gray-100">
                          <p className="text-xs text-gray-500">
                            Ref: {transaction.reference_type} - {transaction.reference_number}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
