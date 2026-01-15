"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Invoice {
  id: number;
  invoice_number: string;
  patient_id: number;
  patient_name: string;
  medical_record_number: string;
  visit_type: "outpatient" | "inpatient" | "emergency";
  department: string;
  invoice_date: string;
  due_date: string;
  subtotal: number;
  discount: number;
  tax: number;
  total_amount: number;
  paid_amount: number;
  remaining_balance: number;
  status: "draft" | "pending" | "approved" | "submitted" | "partial" | "paid" | "overdue" | "cancelled";
  payment_method: "cash" | "transfer" | "card" | "bpjs" | "insurance" | "mixed";
  payer_type: "patient" | "bpjs" | "insurance" | "corporate";
  bpjs_claim_number?: string;
  bpjs_claim_status?: "draft" | "submitted" | "approved" | "rejected" | "paid";
  items: InvoiceItem[];
  notes?: string;
  created_at: string;
  updated_at: string;
}

interface InvoiceItem {
  id: number;
  item_type: "service" | "medication" | "room" | "procedure" | "diagnostic";
  item_code: string;
  item_name: string;
  quantity: number;
  unit_price: number;
  discount: number;
  subtotal: number;
  bpjs_tariff?: number;
  is_covered?: boolean;
}

export default function BillingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [expandedInvoice, setExpandedInvoice] = useState<number | null>(null);
  const [filters, setFilters] = useState({
    status: "",
    paymentMethod: "",
    payerType: "",
    startDate: "",
    endDate: "",
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [stats, setStats] = useState({
    todayTotal: 0,
    pending: 0,
    approved: 0,
    submitted: 0,
    collected: 0,
  });

  useEffect(() => {
    checkAuth();
    fetchInvoices();
    fetchStats();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) {
      router.push("/app/login");
    }
  };

  const fetchInvoices = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const queryParams = new URLSearchParams();
      if (filters.status) queryParams.append("status", filters.status);
      if (filters.paymentMethod) queryParams.append("payment_method", filters.paymentMethod);
      if (filters.payerType) queryParams.append("payer_type", filters.payerType);
      if (filters.startDate) queryParams.append("start_date", filters.startDate);
      if (filters.endDate) queryParams.append("end_date", filters.endDate);
      if (searchQuery) queryParams.append("search", searchQuery);

      const response = await fetch(`/api/v1/billing/invoices?${queryParams}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch invoices");
      }

      const data = await response.json();
      setInvoices(data.items || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load invoices");
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch("/api/v1/billing/statistics", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats({
          todayTotal: data.today_total || 0,
          pending: data.pending || 0,
          approved: data.approved || 0,
          submitted: data.submitted || 0,
          collected: data.collected || 0,
        });
      }
    } catch (err) {
      console.error("Failed to fetch statistics:", err);
    }
  };

  const handleStatusChange = async (invoiceId: number, newStatus: string) => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/billing/invoices/${invoiceId}/status`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error("Failed to update status");
      }

      // Refresh invoices
      fetchInvoices();
      fetchStats();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to update status");
    }
  };

  const handleSubmitBPJS = async (invoiceId: number) => {
    const token = localStorage.getItem("staff_access_token");
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/billing/invoices/${invoiceId}/bpjs-submit`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to submit BPJS claim");
      }

      alert("Klaim BPJS berhasil dikirim");
      fetchInvoices();
      fetchStats();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to submit BPJS claim");
    }
  };

  const handlePrintInvoice = (invoiceId: number) => {
    window.open(`/app/billing/${invoiceId}/print`, "_blank");
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; className: string }> = {
      draft: { label: "Draft", className: "bg-gray-100 text-gray-700" },
      pending: { label: "Menunggu", className: "bg-yellow-100 text-yellow-700" },
      approved: { label: "Disetujui", className: "bg-blue-100 text-blue-700" },
      submitted: { label: "Diajukan", className: "bg-indigo-100 text-indigo-700" },
      partial: { label: "Sebagian", className: "bg-purple-100 text-purple-700" },
      paid: { label: "Lunas", className: "bg-green-100 text-green-700" },
      overdue: { label: "Terlambat", className: "bg-red-100 text-red-700" },
      cancelled: { label: "Batal", className: "bg-gray-100 text-gray-500" },
    };

    const config = statusConfig[status] || statusConfig.draft;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.className}`}>
        {config.label}
      </span>
    );
  };

  const getBPJSStatusBadge = (status?: string) => {
    if (!status) return null;

    const statusConfig: Record<string, { label: string; className: string }> = {
      draft: { label: "Draft", className: "bg-gray-100 text-gray-700" },
      submitted: { label: "Diajukan", className: "bg-blue-100 text-blue-700" },
      approved: { label: "Disetujui", className: "bg-green-100 text-green-700" },
      rejected: { label: "Ditolak", className: "bg-red-100 text-red-700" },
      paid: { label: "Dibayar", className: "bg-indigo-100 text-indigo-700" },
    };

    const config = statusConfig[status] || statusConfig.draft;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.className}`}>
        BPJS: {config.label}
      </span>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("id-ID", {
      style: "currency",
      currency: "IDR",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const getPaymentMethodIcon = (method: string) => {
    const icons: Record<string, string> = {
      cash: "💵",
      transfer: "🏦",
      card: "💳",
      bpjs: "🏥",
      insurance: "🛡️",
      mixed: "🔄",
    };
    return icons[method] || "💰";
  };

  const toggleExpand = (invoiceId: number) => {
    setExpandedInvoice(expandedInvoice === invoiceId ? null : invoiceId);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tagihan & Pembayaran</h1>
          <p className="text-gray-600 mt-1">Kelola tagihan pasien dan klaim BPJS</p>
        </div>
        <button
          onClick={() => router.push("/app/billing/new")}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>Buat Tagihan</span>
        </button>
      </div>

      {/* Statistics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Hari Ini</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.todayTotal)}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">💰</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Menunggu</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⏳</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Disetujui</p>
              <p className="text-2xl font-bold text-blue-600">{stats.approved}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">✅</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Diajukan</p>
              <p className="text-2xl font-bold text-indigo-600">{stats.submitted}</p>
            </div>
            <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📤</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Terkumpul</p>
              <p className="text-2xl font-bold text-green-600">{formatCurrency(stats.collected)}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">💵</span>
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Semua</option>
              <option value="draft">Draft</option>
              <option value="pending">Menunggu</option>
              <option value="approved">Disetujui</option>
              <option value="submitted">Diajukan</option>
              <option value="partial">Sebagian</option>
              <option value="paid">Lunas</option>
              <option value="overdue">Terlambat</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Metode Pembayaran</label>
            <select
              value={filters.paymentMethod}
              onChange={(e) => setFilters({ ...filters, paymentMethod: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Semua</option>
              <option value="cash">Tunai</option>
              <option value="transfer">Transfer</option>
              <option value="card">Kartu</option>
              <option value="bpjs">BPJS</option>
              <option value="insurance">Asuransi</option>
              <option value="mixed">Campuran</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Jenis Penanggung</label>
            <select
              value={filters.payerType}
              onChange={(e) => setFilters({ ...filters, payerType: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Semua</option>
              <option value="patient">Pasien</option>
              <option value="bpjs">BPJS</option>
              <option value="insurance">Asuransi</option>
              <option value="corporate">Korporat</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tanggal Mulai</label>
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tanggal Akhir</label>
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={() => {
                setFilters({ status: "", paymentMethod: "", payerType: "", startDate: "", endDate: "" });
                setSearchQuery("");
                fetchInvoices();
              }}
              className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Reset
            </button>
          </div>
        </div>

        <div className="mt-4">
          <input
            type="text"
            placeholder="Cari berdasarkan nama pasien, No RM, atau nomor tagihan..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Invoices List */}
      {invoices.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada tagihan ditemukan</h3>
          <p className="text-gray-600">Coba sesuaikan filter atau buat tagihan baru</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tagihan</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pasien</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pembayaran</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Dibayar</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Sisa</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Aksi</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {invoices.map((invoice) => (
                  <>
                    <tr key={invoice.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => toggleExpand(invoice.id)}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{invoice.invoice_number}</div>
                        <div className="text-xs text-gray-500">
                          {new Date(invoice.invoice_date).toLocaleDateString("id-ID")}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{invoice.patient_name}</div>
                        <div className="text-xs text-gray-500">{invoice.medical_record_number}</div>
                        <div className="text-xs text-gray-400">{invoice.department}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-col space-y-1">
                          {getStatusBadge(invoice.status)}
                          {invoice.bpjs_claim_status && getBPJSStatusBadge(invoice.bpjs_claim_status)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <span className="text-xl">{getPaymentMethodIcon(invoice.payment_method)}</span>
                          <span className="text-sm text-gray-700 capitalize">{invoice.payer_type}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="text-sm font-medium text-gray-900">{formatCurrency(invoice.total_amount)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="text-sm text-green-600">{formatCurrency(invoice.paid_amount)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className={`text-sm font-medium ${invoice.remaining_balance > 0 ? "text-red-600" : "text-green-600"}`}>
                          {formatCurrency(invoice.remaining_balance)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <div className="flex items-center justify-center space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handlePrintInvoice(invoice.id);
                            }}
                            className="p-1 text-gray-400 hover:text-indigo-600"
                            title="Cetak"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                            </svg>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleExpand(invoice.id);
                            }}
                            className="p-1 text-gray-400 hover:text-indigo-600"
                            title="Detail"
                          >
                            {expandedInvoice === invoice.id ? (
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                              </svg>
                            ) : (
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                              </svg>
                            )}
                          </button>
                        </div>
                      </td>
                    </tr>
                    {expandedInvoice === invoice.id && (
                      <tr>
                        <td colSpan={8} className="px-6 py-4 bg-gray-50">
                          <div className="space-y-4">
                            {/* Invoice Details */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                              <div>
                                <p className="text-xs text-gray-500">Tanggal Jatuh Tempo</p>
                                <p className="text-sm font-medium text-gray-900">
                                  {new Date(invoice.due_date).toLocaleDateString("id-ID")}
                                </p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500">Jenis Kunjungan</p>
                                <p className="text-sm font-medium text-gray-900 capitalize">{invoice.visit_type}</p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500">Nomor Klaim BPJS</p>
                                <p className="text-sm font-medium text-gray-900">{invoice.bpjs_claim_number || "-"}</p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500">Catatan</p>
                                <p className="text-sm text-gray-700">{invoice.notes || "-"}</p>
                              </div>
                            </div>

                            {/* Invoice Items */}
                            <div>
                              <h4 className="text-sm font-medium text-gray-900 mb-2">Rincian Tagihan</h4>
                              <div className="border border-gray-200 rounded-lg overflow-hidden">
                                <table className="w-full">
                                  <thead className="bg-gray-100">
                                    <tr>
                                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Item</th>
                                      <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Qty</th>
                                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Harga</th>
                                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Diskon</th>
                                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Subtotal</th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-gray-200">
                                    {invoice.items.map((item) => (
                                      <tr key={item.id} className="text-sm">
                                        <td className="px-4 py-2">
                                          <div className="font-medium text-gray-900">{item.item_name}</div>
                                          <div className="text-xs text-gray-500">{item.item_code}</div>
                                        </td>
                                        <td className="px-4 py-2 text-center">{item.quantity}</td>
                                        <td className="px-4 py-2 text-right">{formatCurrency(item.unit_price)}</td>
                                        <td className="px-4 py-2 text-right">{formatCurrency(item.discount)}</td>
                                        <td className="px-4 py-2 text-right font-medium">{formatCurrency(item.subtotal)}</td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>

                            {/* Summary */}
                            <div className="flex justify-end">
                              <div className="w-64 space-y-2">
                                <div className="flex justify-between text-sm">
                                  <span className="text-gray-600">Subtotal</span>
                                  <span className="font-medium">{formatCurrency(invoice.subtotal)}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span className="text-gray-600">Diskon</span>
                                  <span className="font-medium text-red-600">-{formatCurrency(invoice.discount)}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span className="text-gray-600">Pajak</span>
                                  <span className="font-medium">{formatCurrency(invoice.tax)}</span>
                                </div>
                                <div className="flex justify-between text-lg font-bold border-t pt-2">
                                  <span>Total</span>
                                  <span className="text-indigo-600">{formatCurrency(invoice.total_amount)}</span>
                                </div>
                              </div>
                            </div>

                            {/* Actions */}
                            <div className="flex flex-wrap gap-2 pt-4 border-t">
                              {invoice.status === "draft" && (
                                <>
                                  <button
                                    onClick={() => handleStatusChange(invoice.id, "pending")}
                                    className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                                  >
                                    Ajukan
                                  </button>
                                  <button
                                    onClick={() => router.push(`/app/billing/${invoice.id}/edit`)}
                                    className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
                                  >
                                    Edit
                                  </button>
                                </>
                              )}
                              {invoice.status === "pending" && (
                                <>
                                  <button
                                    onClick={() => handleStatusChange(invoice.id, "approved")}
                                    className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                                  >
                                    Setujui
                                  </button>
                                  <button
                                    onClick={() => handleStatusChange(invoice.id, "cancelled")}
                                    className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                                  >
                                    Tolak
                                  </button>
                                </>
                              )}
                              {invoice.status === "approved" && invoice.payer_type === "bpjs" && (
                                <button
                                  onClick={() => handleSubmitBPJS(invoice.id)}
                                  className="px-3 py-1 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700"
                                >
                                  Kirim Klaim BPJS
                                </button>
                              )}
                              {invoice.status === "approved" && invoice.payer_type !== "bpjs" && (
                                <button
                                  onClick={() => router.push(`/app/billing/${invoice.id}/payment`)}
                                  className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                                >
                                    Terima Pembayaran
                                </button>
                              )}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
