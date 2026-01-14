"""Accounts Receivable Component

Accounts Receivable management with:
- Outstanding invoices list
- Aging analysis (30, 60, 90+ days)
- Customer statements
- Payment reminders
- Collection tracking
"""

import { useState, useEffect } from 'react';
import {
  FileText,
  Calendar,
  User,
  AlertCircle,
  Mail,
  Phone,
  MessageSquare,
  Download,
  RefreshCw,
  Search,
  Filter,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  Activity,
} from 'lucide-react';

// Types
interface OutstandingInvoice {
  id: number;
  invoice_number: string;
  patient_id: number;
  patient_name: string;
  patient_phone: string;
  patient_email: string;
  invoice_date: string;
  due_date: string;
  total_amount: number;
  paid_amount: number;
  balance_due: number;
  days_overdue: number;
  aging_bucket: 'current' | '30_days' | '60_days' | '90_days';
  status: 'sent' | 'overdue' | 'collection';
  last_reminder_date: string | null;
  reminder_count: number;
}

interface AgingSummary {
  current: number;
  days_30: number;
  days_60: number;
  days_90: number;
  total: number;
}

interface CollectionActivity {
  id: number;
  invoice_id: number;
  activity_type: 'call' | 'email' | 'sms' | 'visit';
  activity_date: string;
  notes: string;
  created_by: string;
  outcome: 'contacted' | 'no_answer' | 'promise_to_pay' | 'dispute' | 'paid';
  follow_up_date: string | null;
}

interface Reminder {
  id: number;
  invoice_id: number;
  reminder_type: 'email' | 'sms' | 'whatsapp';
  sent_date: string;
  status: 'sent' | 'delivered' | 'failed';
}

export function AccountsReceivable() {
  const [invoices, setInvoices] = useState<OutstandingInvoice[]>([]);
  const [agingSummary, setAgingSummary] = useState<AgingSummary | null>(null);
  const [selectedInvoice, setSelectedInvoice] = useState<OutstandingInvoice | null>(null);
  const [collectionActivities, setCollectionActivities] = useState<CollectionActivity[]>([]);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showReminderModal, setShowReminderModal] = useState(false);
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    aging_bucket: '',
    status: '',
    min_amount: '',
  });
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [activityNote, setActivityNote] = useState('');
  const [activityType, setActivityType] = useState<'call' | 'email' | 'sms' | 'visit'>('call');
  const [activityOutcome, setActivityOutcome] = useState<'contacted' | 'no_answer' | 'promise_to_pay' | 'dispute' | 'paid'>('contacted');
  const [followUpDate, setFollowUpDate] = useState('');
  const [reminderType, setReminderType] = useState<'email' | 'sms' | 'whatsapp'>('email');

  useEffect(() => {
    loadARData();
  }, []);

  const loadARData = async () => {
    setIsLoading(true);
    try {
      const [invoicesRes, agingRes] = await Promise.all([
        fetch('/api/v1/payments/accounts-receivable/outstanding', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
        fetch('/api/v1/payments/accounts-receivable/aging-summary', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
      ]);

      if (invoicesRes.ok) {
        const data = await invoicesRes.json();
        setInvoices(data);
      }
      if (agingRes.ok) {
        const data = await agingRes.json();
        setAgingSummary(data);
      }
    } catch (error) {
      console.error('Failed to load AR data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadInvoiceDetails = async (invoiceId: number) => {
    setIsLoading(true);
    try {
      const [activitiesRes, remindersRes] = await Promise.all([
        fetch(`/api/v1/payments/accounts-receivable/invoices/${invoiceId}/activities`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
        fetch(`/api/v1/payments/accounts-receivable/invoices/${invoiceId}/reminders`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
      ]);

      if (activitiesRes.ok) {
        const data = await activitiesRes.json();
        setCollectionActivities(data);
      }
      if (remindersRes.ok) {
        const data = await remindersRes.json();
        setReminders(data);
      }
    } catch (error) {
      console.error('Failed to load invoice details:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleRowExpansion = (invoiceId: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(invoiceId)) {
      newExpanded.delete(invoiceId);
    } else {
      newExpanded.add(invoiceId);
    }
    setExpandedRows(newExpanded);
  };

  const viewInvoiceDetails = (invoice: OutstandingInvoice) => {
    setSelectedInvoice(invoice);
    loadInvoiceDetails(invoice.id);
    setShowDetailModal(true);
  };

  const sendReminder = async () => {
    if (!selectedInvoice) return;

    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/payments/accounts-receivable/reminders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          invoice_id: selectedInvoice.id,
          reminder_type: reminderType,
        }),
      });

      if (response.ok) {
        alert('Pengingat berhasil dikirim');
        setShowReminderModal(false);
        loadInvoiceDetails(selectedInvoice.id);
        loadARData();
      } else {
        alert('Gagal mengirim pengingat');
      }
    } catch (error) {
      console.error('Failed to send reminder:', error);
      alert('Gagal mengirim pengingat');
    } finally {
      setIsLoading(false);
    }
  };

  const logActivity = async () => {
    if (!selectedInvoice || !activityNote.trim()) {
      alert('Masukkan catatan aktivitas');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/payments/accounts-receivable/activities', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({
          invoice_id: selectedInvoice.id,
          activity_type: activityType,
          notes: activityNote,
          outcome: activityOutcome,
          follow_up_date: followUpDate || null,
        }),
      });

      if (response.ok) {
        alert('Aktivitas berhasil dicatat');
        setShowActivityModal(false);
        setActivityNote('');
        setFollowUpDate('');
        loadInvoiceDetails(selectedInvoice.id);
      } else {
        alert('Gagal mencatat aktivitas');
      }
    } catch (error) {
      console.error('Failed to log activity:', error);
      alert('Gagal mencatat aktivitas');
    } finally {
      setIsLoading(false);
    }
  };

  const generateStatement = async () => {
    if (!selectedInvoice) return;

    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/payments/accounts-receivable/statements/${selectedInvoice.patient_id}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`},
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Statement-${selectedInvoice.patient_name}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Failed to generate statement:', error);
      alert('Gagal membuat statement');
    } finally {
      setIsLoading(false);
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

  const getAgingBadge = (bucket: string) => {
    const config = {
      current: { bg: 'bg-green-100', text: 'text-green-800', label: 'Current' },
      '30_days': { bg: 'bg-yellow-100', text: 'text-yellow-800', label: '30 Hari' },
      '60_days': { bg: 'bg-orange-100', text: 'text-orange-800', label: '60 Hari' },
      '90_days': { bg: 'bg-red-100', text: 'text-red-800', label: '90+ Hari' },
    };
    const c = config[bucket as keyof typeof config] || config.current;
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>
        {c.label}
      </span>
    );
  };

  const getStatusBadge = (status: string) => {
    const config = {
      sent: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Terkirim' },
      overdue: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Jatuh Tempo' },
      collection: { bg: 'bg-red-100', text: 'text-red-800', label: 'Penagihan' },
    };
    const c = config[status as keyof typeof config] || config.sent;
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>
        {c.label}
      </span>
    );
  };

  const getActivityIcon = (type: string) => {
    const icons = {
      call: Phone,
      email: Mail,
      sms: MessageSquare,
      visit: User,
    };
    return icons[type as keyof typeof icons] || Activity;
  };

  const getOutcomeBadge = (outcome: string) => {
    const config = {
      contacted: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Terhubung' },
      no_answer: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Tidak Jawab' },
      promise_to_pay: { bg: 'bg-green-100', text: 'text-green-800', label: 'Janji Bayar' },
      dispute: { bg: 'bg-red-100', text: 'text-red-800', label: 'Disputasi' },
      paid: { bg: 'bg-green-100', text: 'text-green-800', label: 'Lunas' },
    };
    const c = config[outcome as keyof typeof config] || config.contacted;
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>
        {c.label}
      </span>
    );
  };

  const filteredInvoices = invoices.filter(invoice => {
    const matchesSearch =
      !searchTerm ||
      invoice.patient_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      invoice.invoice_number.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesAging = !filters.aging_bucket || invoice.aging_bucket === filters.aging_bucket;
    const matchesStatus = !filters.status || invoice.status === filters.status;
    const matchesMinAmount = !filters.min_amount || invoice.balance_due >= parseFloat(filters.min_amount);

    return matchesSearch && matchesAging && matchesStatus && matchesMinAmount;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <FileText className="h-6 w-6 mr-2" />
            Piutang Usaha
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Kelola faktur belum lunas dan aktivitas penagihan
          </p>
        </div>
        <button
          onClick={loadARData}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Aging Summary */}
      {agingSummary && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-700">Current</p>
                <p className="text-2xl font-bold text-green-900 mt-1">
                  {formatCurrency(agingSummary.current)}
                </p>
              </div>
              <Clock className="h-8 w-8 text-green-600" />
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-yellow-700">30 Hari</p>
                <p className="text-2xl font-bold text-yellow-900 mt-1">
                  {formatCurrency(agingSummary.days_30)}
                </p>
              </div>
              <AlertCircle className="h-8 w-8 text-yellow-600" />
            </div>
          </div>

          <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-orange-700">60 Hari</p>
                <p className="text-2xl font-bold text-orange-900 mt-1">
                  {formatCurrency(agingSummary.days_60)}
                </p>
              </div>
              <AlertCircle className="h-8 w-8 text-orange-600" />
            </div>
          </div>

          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-red-700">90+ Hari</p>
                <p className="text-2xl font-bold text-red-900 mt-1">
                  {formatCurrency(agingSummary.days_90)}
                </p>
              </div>
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-700">Total Piutang</p>
                <p className="text-2xl font-bold text-blue-900 mt-1">
                  {formatCurrency(agingSummary.total)}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-blue-600" />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            Filter
          </h3>
          <button
            onClick={() => setFilters({ aging_bucket: '', status: '', min_amount: '' })}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Reset Filter
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Pencarian</label>
            <div className="relative">
              <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Cari nama atau no. faktur..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Umur Piutang</label>
            <select
              value={filters.aging_bucket}
              onChange={(e) => setFilters({ ...filters, aging_bucket: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Semua</option>
              <option value="current">Current</option>
              <option value="30_days">30 Hari</option>
              <option value="60_days">60 Hari</option>
              <option value="90_days">90+ Hari</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Semua Status</option>
              <option value="sent">Terkirim</option>
              <option value="overdue">Jatuh Tempo</option>
              <option value="collection">Penagihan</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Minimum Jumlah</label>
            <input
              type="number"
              placeholder="Minimum Rp"
              value={filters.min_amount}
              onChange={(e) => setFilters({ ...filters, min_amount: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Outstanding Invoices */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            Faktur Belum Lunas
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({filteredInvoices.length} faktur)
            </span>
          </h3>
        </div>

        <div className="space-y-3">
          {filteredInvoices.map((invoice) => {
            const isExpanded = expandedRows.has(invoice.id);

            return (
              <div key={invoice.id} className="border rounded-lg">
                <div
                  className="p-4 cursor-pointer hover:bg-gray-50"
                  onClick={() => toggleRowExpansion(invoice.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center flex-1">
                      <User className="h-5 w-5 text-gray-400 mr-3" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {invoice.patient_name}
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                              {invoice.invoice_number} - {formatDate(invoice.invoice_date)}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            {getAgingBadge(invoice.aging_bucket)}
                            {getStatusBadge(invoice.status)}
                            {isExpanded ? (
                              <ChevronUp className="h-4 w-4 text-gray-400" />
                            ) : (
                              <ChevronDown className="h-4 w-4 text-gray-400" />
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="ml-4 text-right">
                      <p className="text-lg font-bold text-gray-900">
                        {formatCurrency(invoice.balance_due)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {invoice.days_overdue > 0
                          ? `${invoice.days_overdue} hari terlambat`
                          : 'Jatuh tempo: ' + formatDate(invoice.due_date)
                        }
                      </p>
                    </div>
                  </div>
                </div>

                {isExpanded && (
                  <div className="px-4 pb-4 border-t border-gray-100 pt-4">
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <p className="text-xs text-gray-500">Telepon</p>
                        <p className="text-sm font-medium text-gray-900">{invoice.patient_phone}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Email</p>
                        <p className="text-sm font-medium text-gray-900">{invoice.patient_email}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Total Tagihan</p>
                        <p className="text-sm font-medium text-gray-900">
                          {formatCurrency(invoice.total_amount)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Sisa Tagihan</p>
                        <p className="text-sm font-bold text-red-600">
                          {formatCurrency(invoice.balance_due)}
                        </p>
                      </div>
                    </div>

                    {invoice.reminder_count > 0 && (
                      <div className="mb-3 p-2 bg-yellow-50 border border-yellow-200 rounded">
                        <p className="text-xs text-yellow-800">
                          <strong>{invoice.reminder_count} pengingat</strong> telah dikirim
                          {invoice.last_reminder_date && ` (Terakhir: ${formatDate(invoice.last_reminder_date)})`}
                        </p>
                      </div>
                    )}

                    <div className="flex gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          viewInvoiceDetails(invoice);
                        }}
                        className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                      >
                        <Activity className="h-4 w-4 mr-2" />
                        Lihat Detail
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedInvoice(invoice);
                          setShowReminderModal(true);
                        }}
                        className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-blue-300 rounded-md text-sm font-medium text-blue-700 bg-white hover:bg-blue-50"
                      >
                        <Mail className="h-4 w-4 mr-2" />
                        Kirim Pengingat
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {filteredInvoices.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>Tidak ada faktur belum lunas ditemukan</p>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {showDetailModal && selectedInvoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Detail Faktur & Penagihan</h2>
              <button
                onClick={() => setShowDetailModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Invoice Info */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-900 mb-3">Informasi Faktur</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">No. Faktur</p>
                    <p className="text-sm font-medium text-gray-900">{selectedInvoice.invoice_number}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Pasien</p>
                    <p className="text-sm font-medium text-gray-900">{selectedInvoice.patient_name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Tanggal Faktur</p>
                    <p className="text-sm font-medium text-gray-900">{formatDate(selectedInvoice.invoice_date)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Jatuh Tempo</p>
                    <p className="text-sm font-medium text-gray-900">{formatDate(selectedInvoice.due_date)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Total Tagihan</p>
                    <p className="text-sm font-medium text-gray-900">
                      {formatCurrency(selectedInvoice.total_amount)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Sisa Tagihan</p>
                    <p className="text-sm font-bold text-red-600">
                      {formatCurrency(selectedInvoice.balance_due)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Collection Activities */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-medium text-gray-900">Aktivitas Penagihan</h3>
                  <button
                    onClick={() => setShowActivityModal(true)}
                    className="text-xs text-blue-600 hover:text-blue-800"
                  >
                    + Tambah Aktivitas
                  </button>
                </div>

                {collectionActivities.length === 0 ? (
                  <div className="text-center py-4 text-gray-500 text-sm">
                    Belum ada aktivitas penagihan
                  </div>
                ) : (
                  <div className="space-y-2">
                    {collectionActivities.map((activity) => {
                      const Icon = getActivityIcon(activity.activity_type);
                      return (
                        <div key={activity.id} className="border rounded-lg p-3">
                          <div className="flex items-start justify-between">
                            <div className="flex items-start">
                              <Icon className="h-5 w-5 text-gray-400 mr-2 mt-0.5" />
                              <div>
                                <p className="text-sm font-medium text-gray-900">
                                  {activity.activity_type === 'call' && 'Telepon'}
                                  {activity.activity_type === 'email' && 'Email'}
                                  {activity.activity_type === 'sms' && 'SMS'}
                                  {activity.activity_type === 'visit' && 'Kunjungan'}
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                  {formatDate(activity.activity_date)} oleh {activity.created_by}
                                </p>
                                {activity.notes && (
                                  <p className="text-xs text-gray-700 mt-2">{activity.notes}</p>
                                )}
                              </div>
                            </div>
                            <div className="flex flex-col items-end gap-1">
                              {getOutcomeBadge(activity.outcome)}
                              {activity.follow_up_date && (
                                <p className="text-xs text-gray-500">
                                  Follow-up: {formatDate(activity.follow_up_date)}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Reminders */}
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-3">Riwayat Pengingat</h3>

                {reminders.length === 0 ? (
                  <div className="text-center py-4 text-gray-500 text-sm">
                    Belum ada pengingat dikirim
                  </div>
                ) : (
                  <div className="space-y-2">
                    {reminders.map((reminder) => (
                      <div key={reminder.id} className="border rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            {reminder.reminder_type === 'email' && <Mail className="h-5 w-5 text-gray-400 mr-2" />}
                            {reminder.reminder_type === 'sms' && <MessageSquare className="h-5 w-5 text-gray-400 mr-2" />}
                            {reminder.reminder_type === 'whatsapp' && <MessageSquare className="h-5 w-5 text-gray-400 mr-2" />}
                            <div>
                              <p className="text-sm font-medium text-gray-900">
                                {reminder.reminder_type === 'email' && 'Email'}
                                {reminder.reminder_type === 'sms' && 'SMS'}
                                {reminder.reminder_type === 'whatsapp' && 'WhatsApp'}
                              </p>
                              <p className="text-xs text-gray-500">
                                {formatDate(reminder.sent_date)}
                              </p>
                            </div>
                          </div>
                          <div>
                            {reminder.status === 'sent' && (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Terkirim
                              </span>
                            )}
                            {reminder.status === 'delivered' && (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                Diterima
                              </span>
                            )}
                            {reminder.status === 'failed' && (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                Gagal
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t">
                <button
                  onClick={() => {
                    setSelectedInvoice(selectedInvoice);
                    setShowReminderModal(true);
                  }}
                  className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-blue-300 rounded-md text-sm font-medium text-blue-700 bg-white hover:bg-blue-50"
                >
                  <Mail className="h-4 w-4 mr-2" />
                  Kirim Pengingat
                </button>
                <button
                  onClick={generateStatement}
                  disabled={isLoading}
                  className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Statement
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Reminder Modal */}
      {showReminderModal && selectedInvoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Kirim Pengingat</h2>
              <button
                onClick={() => setShowReminderModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6">
              <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm font-medium text-gray-900">{selectedInvoice.patient_name}</p>
                <p className="text-xs text-gray-500 mt-1">
                  Faktur: {selectedInvoice.invoice_number}
                </p>
                <p className="text-xs text-gray-500">
                  Sisa: {formatCurrency(selectedInvoice.balance_due)}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Metode Pengingat
                </label>
                <select
                  value={reminderType}
                  onChange={(e) => setReminderType(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="email">Email</option>
                  <option value="sms">SMS</option>
                  <option value="whatsapp">WhatsApp</option>
                </select>
              </div>
            </div>

            <div className="border-t px-6 py-4 flex justify-end gap-3">
              <button
                onClick={() => setShowReminderModal(false)}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={sendReminder}
                disabled={isLoading}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Mengirim...
                  </>
                ) : (
                  <>
                    <Mail className="h-4 w-4 mr-2" />
                    Kirim
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Activity Modal */}
      {showActivityModal && selectedInvoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Catat Aktivitas</h2>
              <button
                onClick={() => {
                  setShowActivityModal(false);
                  setActivityNote('');
                  setFollowUpDate('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Jenis Aktivitas
                </label>
                <select
                  value={activityType}
                  onChange={(e) => setActivityType(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="call">Telepon</option>
                  <option value="email">Email</option>
                  <option value="sms">SMS</option>
                  <option value="visit">Kunjungan</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hasil
                </label>
                <select
                  value={activityOutcome}
                  onChange={(e) => setActivityOutcome(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="contacted">Terhubung</option>
                  <option value="no_answer">Tidak Jawab</option>
                  <option value="promise_to_pay">Janji Bayar</option>
                  <option value="dispute">Disputasi</option>
                  <option value="paid">Lunas</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Catatan
                </label>
                <textarea
                  value={activityNote}
                  onChange={(e) => setActivityNote(e.target.value)}
                  rows={3}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Catat detail aktivitas..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tanggal Follow-up (Opsional)
                </label>
                <input
                  type="date"
                  value={followUpDate}
                  onChange={(e) => setFollowUpDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div className="border-t px-6 py-4 flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowActivityModal(false);
                  setActivityNote('');
                  setFollowUpDate('');
                }}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                onClick={logActivity}
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
                    Simpan
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
