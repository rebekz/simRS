"use client";

/**
 * Staff Payroll & Documents Page - STORY-020-04: Pay Stub Access & Tax Documents
 *
 * Comprehensive payroll and tax document access for staff including:
 * - View and download monthly pay stubs (slip gaji)
 * - Access historical pay records (up to 5 years)
 * - View earnings breakdown (basic salary, allowances, bonuses, overtime)
 * - View deductions (tax, BPJS Kesehatan, BPJS Ketenagakerjaan, other)
 * - Download tax documents (Form 1721, SPT Yearly)
 * - View tax summary and withheld tax (PPh 21)
 * - Access BPJS contribution details
 * - Download payslips in PDF format
 * - Year-to-date earnings summary
 * - Reimbursement history and status
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  FileText,
  Download,
  Calendar,
  DollarSign,
  TrendingUp,
  Shield,
  PieChart,
  Filter,
  Search,
  ChevronDown,
  ChevronUp,
  Eye,
  AlertCircle,
  CheckCircle,
  Clock,
  Info,
  Wallet,
  Receipt,
} from "lucide-react";

// Types
interface PayStub {
  id: number;
  staff_id: number;
  pay_period: string;
  pay_date: string;
  gross_pay: number;
  net_pay: number;
  currency: string;
  status: "draft" | "final" | "paid";
  created_at: string;
  payment_method: string;

  // Earnings breakdown
  earnings: {
    basic_salary: number;
    allowances: {
      position: number;
      family: number;
      transport: number;
      housing: number;
      medical: number;
      communication: number;
      other: number;
    };
    bonuses: {
      performance: number;
      attendance: number;
      project: number;
      other: number;
    };
    overtime: {
      regular_hours: number;
      regular_pay: number;
      holiday_hours: number;
      holiday_pay: number;
      total_overtime_pay: number;
    };
  };

  // Deductions breakdown
  deductions: {
    income_tax: number;
    bpjs_kesehatan: number;
    bpjs_ketenagakerjaan: number;
    insurance: {
      pension: number;
      life: number;
      health: number;
      other: number;
    };
    loans: {
      description: string;
      amount: number;
      remaining: number;
    }[];
    other: number;
  };

  // Contribution details
  contributions: {
    bpjs_kesehatan: {
      employee: number;
      employer: number;
      total: number;
    };
    bpjs_ketenagakerjaan: {
      jht: number; // Jaminan Hari Tua
      jkm: number; // Jaminan Kematian
      jkk: number; // Jaminan Kecelakaan Kerja
      jp: number; // Jaminan Pensiun
      employee_total: number;
      employer_total: number;
      total: number;
    };
  };
}

interface TaxDocument {
  id: number;
  staff_id: number;
  document_type: "form_1721" | "spt_yearly" | "tax_summary";
  tax_year: number;
  period?: string;
  gross_income: number;
  taxable_income: number;
  tax_paid: number;
  tax_withheld: number;
  tax_refund?: number;
  document_url: string;
  generated_date: string;
  status: "draft" | "final";
}

interface Reimbursement {
  id: number;
  staff_id: number;
  request_date: string;
  category: "medical" | "transport" | "accommodation" | "meal" | "other";
  description: string;
  amount: number;
  status: "pending" | "approved" | "rejected" | "paid";
  approval_date?: string;
  payment_date?: string;
  receipt_url?: string;
  notes?: string;
}

interface YearToDateSummary {
  year: number;
  total_gross_pay: number;
  total_net_pay: number;
  total_deductions: number;
  total_overtime_pay: number;
  total_bonus_pay: number;
  month_count: number;
}

export default function StaffPayrollPage() {
  const router = useRouter();
  const [payStubs, setPayStubs] = useState<PayStub[]>([]);
  const [taxDocuments, setTaxDocuments] = useState<TaxDocument[]>([]);
  const [reimbursements, setReimbursements] = useState<Reimbursement[]>([]);
  const [ytdSummary, setYtdSummary] = useState<YearToDateSummary | null>(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [yearFilter, setYearFilter] = useState(new Date().getFullYear().toString());
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  // UI state
  const [expandedPayStub, setExpandedPayStub] = useState<number | null>(null);
  const [selectedTab, setSelectedTab] = useState<"payslips" | "tax" | "reimbursements">("payslips");

  useEffect(() => {
    fetchPayrollData();
  }, [yearFilter, statusFilter]);

  const fetchPayrollData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("staff_access_token");
      const params = new URLSearchParams();
      params.append("year", yearFilter);
      if (statusFilter !== "all") params.append("status", statusFilter);

      const [payslipsRes, taxRes, reimbursementsRes, ytdRes] = await Promise.all([
        fetch(`/api/v1/staff/payroll/payslips?${params}`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`/api/v1/staff/payroll/tax-documents`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`/api/v1/staff/payroll/reimbursements`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`/api/v1/staff/payroll/ytd-summary?year=${new Date().getFullYear()}`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (payslipsRes.ok) {
        const payslipsData = await payslipsRes.json();
        setPayStubs(payslipsData.items || []);
      }

      if (taxRes.ok) {
        const taxData = await taxRes.json();
        setTaxDocuments(taxData.items || []);
      }

      if (reimbursementsRes.ok) {
        const reimbursementsData = await reimbursementsRes.json();
        setReimbursements(reimbursementsData.items || []);
      }

      if (ytdRes.ok) {
        const ytdData = await ytdRes.json();
        setYtdSummary(ytdData);
      }
    } catch (error) {
      console.error("Failed to fetch payroll data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPayStub = async (payslipId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/staff/payroll/payslips/${payslipId}/download`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `slip-gaji-${payslipId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert("Gagal mengunduh slip gaji");
      }
    } catch (error) {
      console.error("Failed to download pay stub:", error);
      alert("Gagal mengunduh slip gaji");
    }
  };

  const handleDownloadTaxDocument = async (docId: number) => {
    try {
      const token = localStorage.getItem("staff_access_token");
      const response = await fetch(`/api/v1/staff/payroll/tax-documents/${docId}/download`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `dokumen-pajak-${docId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert("Gagal mengunduh dokumen pajak");
      }
    } catch (error) {
      console.error("Failed to download tax document:", error);
      alert("Gagal mengunduh dokumen pajak");
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "final":
      case "paid":
        return "bg-green-100 text-green-800";
      case "approved":
        return "bg-blue-100 text-blue-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "draft":
        return "bg-gray-100 text-gray-800";
      case "rejected":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "draft":
        return "Draf";
      case "final":
        return "Final";
      case "paid":
        return "Dibayar";
      case "approved":
        return "Disetujui";
      case "pending":
        return "Menunggu";
      case "rejected":
        return "Ditolak";
      default:
        return status;
    }
  };

  const getReimbursementCategoryLabel = (category: string) => {
    switch (category) {
      case "medical":
        return "Medis";
      case "transport":
        return "Transportasi";
      case "accommodation":
        return "Akomodasi";
      case "meal":
        return "Makan";
      case "other":
        return "Lainnya";
      default:
        return category;
    }
  };

  const getTaxDocumentLabel = (type: string) => {
    switch (type) {
      case "form_1721":
        return "Form 1721";
      case "spt_yearly":
        return "SPT Tahunan";
      case "tax_summary":
        return "Ringkasan Pajak";
      default:
        return type;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("id-ID", {
      style: "currency",
      currency: "IDR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("id-ID", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  };

  const formatMonthYear = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("id-ID", {
      month: "long",
      year: "numeric",
    });
  };

  const filteredPayStubs = payStubs.filter((payslip) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return formatMonthYear(payslip.pay_period).toLowerCase().includes(query);
    }
    return true;
  });

  const filteredReimbursements = reimbursements.filter((reimb) => {
    if (statusFilter !== "all") return reimb.status === statusFilter;
    return true;
  });

  const calculateTotalEarnings = (earnings: PayStub["earnings"]) => {
    return (
      earnings.basic_salary +
      Object.values(earnings.allowances).reduce((sum, val) => sum + val, 0) +
      Object.values(earnings.bonuses).reduce((sum, val) => sum + val, 0) +
      earnings.overtime.total_overtime_pay
    );
  };

  const calculateTotalDeductions = (deductions: PayStub["deductions"]) => {
    const insuranceTotal = Object.values(deductions.insurance).reduce((sum, val) => sum + val, 0);
    const loansTotal = deductions.loans.reduce((sum, loan) => sum + loan.amount, 0);
    return (
      deductions.income_tax +
      deductions.bpjs_kesehatan +
      deductions.bpjs_ketenagakerjaan +
      insuranceTotal +
      loansTotal +
      deductions.other
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Slip Gaji & Pajak</h1>
          <p className="text-sm text-gray-600 mt-1">Akses dokumen penggajian dan pajak</p>
        </div>
      </div>

      {/* Year-to-Date Summary */}
      {ytdSummary && (
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold">Ringkasan Tahun Berjalan {ytdSummary.year}</h2>
              <p className="text-blue-100 text-sm">Total pendapatan dari {ytdSummary.month_count} bulan</p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-200" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/10 rounded-lg p-4">
              <p className="text-blue-100 text-sm">Total Pendapatan Kotor</p>
              <p className="text-2xl font-bold">{formatCurrency(ytdSummary.total_gross_pay)}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <p className="text-blue-100 text-sm">Total Pendapatan Bersih</p>
              <p className="text-2xl font-bold">{formatCurrency(ytdSummary.total_net_pay)}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <p className="text-blue-100 text-sm">Total Lembur</p>
              <p className="text-2xl font-bold">{formatCurrency(ytdSummary.total_overtime_pay)}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <p className="text-blue-100 text-sm">Total Bonus</p>
              <p className="text-2xl font-bold">{formatCurrency(ytdSummary.total_bonus_pay)}</p>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setSelectedTab("payslips")}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                selectedTab === "payslips"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              <div className="flex items-center space-x-2">
                <Receipt className="w-4 h-4" />
                <span>Slip Gaji</span>
              </div>
            </button>
            <button
              onClick={() => setSelectedTab("tax")}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                selectedTab === "tax"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4" />
                <span>Dokumen Pajak</span>
              </div>
            </button>
            <button
              onClick={() => setSelectedTab("reimbursements")}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                selectedTab === "reimbursements"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              <div className="flex items-center space-x-2">
                <Wallet className="w-4 h-4" />
                <span>Reimburse</span>
                {reimbursements.filter((r) => r.status === "pending").length > 0 && (
                  <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                    {reimbursements.filter((r) => r.status === "pending").length}
                  </span>
                )}
              </div>
            </button>
          </nav>
        </div>

        <div className="p-6">
          {/* Payslips Tab */}
          {selectedTab === "payslips" && (
            <div className="space-y-4">
              {/* Filters */}
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center space-x-2">
                  <label className="text-sm font-medium text-gray-700">Tahun:</label>
                  <select
                    value={yearFilter}
                    onChange={(e) => setYearFilter(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map((year) => (
                      <option key={year} value={year.toString()}>
                        {year}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="relative flex-1 max-w-xs">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Cari bulan..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Payslips List */}
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
              ) : filteredPayStubs.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada slip gaji</h3>
                  <p className="text-gray-600">
                    {searchQuery ? "Tidak ada slip gaji yang sesuai dengan pencarian" : "Belum ada slip gaji untuk tahun ini"}
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredPayStubs.map((payslip) => {
                    const isExpanded = expandedPayStub === payslip.id;
                    const totalEarnings = calculateTotalEarnings(payslip.earnings);
                    const totalDeductions = calculateTotalDeductions(payslip.deductions);

                    return (
                      <div key={payslip.id} className="border border-gray-200 rounded-lg overflow-hidden">
                        {/* Summary Row */}
                        <div
                          className="bg-gray-50 p-4 cursor-pointer hover:bg-gray-100 transition-colors"
                          onClick={() => setExpandedPayStub(isExpanded ? null : payslip.id)}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                                <Calendar className="w-6 h-6 text-blue-600" />
                              </div>
                              <div>
                                <p className="font-semibold text-gray-900">
                                  {formatMonthYear(payslip.pay_period)}
                                </p>
                                <p className="text-sm text-gray-500">Tanggal Bayar: {formatDate(payslip.pay_date)}</p>
                              </div>
                              <span
                                className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                                  payslip.status
                                )}`}
                              >
                                {getStatusLabel(payslip.status)}
                              </span>
                            </div>

                            <div className="flex items-center space-x-6">
                              <div className="text-right">
                                <p className="text-sm text-gray-500">Pendapatan Bersih</p>
                                <p className="text-lg font-bold text-gray-900">
                                  {formatCurrency(payslip.net_pay)}
                                </p>
                              </div>
                              <div className="flex items-center space-x-2">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDownloadPayStub(payslip.id);
                                  }}
                                  className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                                  title="Unduh PDF"
                                >
                                  <Download className="w-5 h-5" />
                                </button>
                                {isExpanded ? (
                                  <ChevronUp className="w-5 h-5 text-gray-400" />
                                ) : (
                                  <ChevronDown className="w-5 h-5 text-gray-400" />
                                )}
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Expanded Details */}
                        {isExpanded && (
                          <div className="p-6 border-t border-gray-200 space-y-6">
                            {/* Earnings Section */}
                            <div>
                              <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                                <DollarSign className="w-4 h-4 mr-2 text-green-600" />
                                Pendapatan
                              </h4>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                  <div className="flex justify-between text-sm">
                                    <span className="text-gray-600">Gaji Pokok</span>
                                    <span className="font-medium">{formatCurrency(payslip.earnings.basic_salary)}</span>
                                  </div>
                                  <div className="border-t pt-2">
                                    <p className="text-xs text-gray-500 mb-2">Tunjangan</p>
                                    {Object.entries(payslip.earnings.allowances).map(([key, value]) => {
                                      if (value === 0) return null;
                                      const labels: Record<string, string> = {
                                        position: "Jabatan",
                                        family: "Keluarga",
                                        transport: "Transport",
                                        housing: "Perumahan",
                                        medical: "Kesehatan",
                                        communication: "Komunikasi",
                                        other: "Lainnya",
                                      };
                                      return (
                                        <div key={key} className="flex justify-between text-sm">
                                          <span className="text-gray-600 ml-2">{labels[key]}</span>
                                          <span className="font-medium">{formatCurrency(value)}</span>
                                        </div>
                                      );
                                    })}
                                  </div>
                                  <div className="border-t pt-2">
                                    <p className="text-xs text-gray-500 mb-2">Bonus</p>
                                    {Object.entries(payslip.earnings.bonuses).map(([key, value]) => {
                                      if (value === 0) return null;
                                      const labels: Record<string, string> = {
                                        performance: "Kinerja",
                                        attendance: "Kehadiran",
                                        project: "Proyek",
                                        other: "Lainnya",
                                      };
                                      return (
                                        <div key={key} className="flex justify-between text-sm">
                                          <span className="text-gray-600 ml-2">{labels[key]}</span>
                                          <span className="font-medium">{formatCurrency(value)}</span>
                                        </div>
                                      );
                                    })}
                                  </div>
                                  <div className="border-t pt-2">
                                    <p className="text-xs text-gray-500 mb-2">Lembur</p>
                                    {payslip.earnings.overtime.total_overtime_pay > 0 && (
                                      <>
                                        <div className="flex justify-between text-sm">
                                          <span className="text-gray-600 ml-2">Reguler ({payslip.earnings.overtime.regular_hours}j)</span>
                                          <span className="font-medium">{formatCurrency(payslip.earnings.overtime.regular_pay)}</span>
                                        </div>
                                        {payslip.earnings.overtime.holiday_pay > 0 && (
                                          <div className="flex justify-between text-sm">
                                            <span className="text-gray-600 ml-2">Libur ({payslip.earnings.overtime.holiday_hours}j)</span>
                                            <span className="font-medium">{formatCurrency(payslip.earnings.overtime.holiday_pay)}</span>
                                          </div>
                                        )}
                                      </>
                                    )}
                                  </div>
                                  <div className="border-t pt-2">
                                    <div className="flex justify-between text-sm font-semibold">
                                      <span className="text-gray-900">Total Pendapatan</span>
                                      <span className="text-green-600">{formatCurrency(totalEarnings)}</span>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* Deductions Section */}
                            <div>
                              <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                                <TrendingUp className="w-4 h-4 mr-2 text-red-600" />
                                Potongan
                              </h4>
                              <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                  <span className="text-gray-600">PPh 21 (Pajak Penghasilan)</span>
                                  <span className="font-medium">{formatCurrency(payslip.deductions.income_tax)}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span className="text-gray-600">BPJS Kesehatan</span>
                                  <span className="font-medium">{formatCurrency(payslip.deductions.bpjs_kesehatan)}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span className="text-gray-600">BPJS Ketenagakerjaan</span>
                                  <span className="font-medium">{formatCurrency(payslip.deductions.bpjs_ketenagakerjaan)}</span>
                                </div>
                                {Object.entries(payslip.deductions.insurance).map(([key, value]) => {
                                  if (value === 0) return null;
                                  const labels: Record<string, string> = {
                                    pension: "Asuransi Pensiun",
                                    life: "Asuransi Jiwa",
                                    health: "Asuransi Kesehatan",
                                    other: "Asuransi Lainnya",
                                  };
                                  return (
                                    <div key={key} className="flex justify-between text-sm">
                                      <span className="text-gray-600">{labels[key]}</span>
                                      <span className="font-medium">{formatCurrency(value)}</span>
                                    </div>
                                  );
                                })}
                                {payslip.deductions.loans.map((loan, idx) => (
                                  <div key={idx} className="flex justify-between text-sm">
                                    <span className="text-gray-600">Pinjaman: {loan.description}</span>
                                    <span className="font-medium">{formatCurrency(loan.amount)}</span>
                                  </div>
                                ))}
                                {payslip.deductions.other > 0 && (
                                  <div className="flex justify-between text-sm">
                                    <span className="text-gray-600">Lainnya</span>
                                    <span className="font-medium">{formatCurrency(payslip.deductions.other)}</span>
                                  </div>
                                )}
                                <div className="border-t pt-2">
                                  <div className="flex justify-between text-sm font-semibold">
                                    <span className="text-gray-900">Total Potongan</span>
                                    <span className="text-red-600">{formatCurrency(totalDeductions)}</span>
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* BPJS Contributions Section */}
                            <div>
                              <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                                <Shield className="w-4 h-4 mr-2 text-blue-600" />
                                Kontribusi BPJS
                              </h4>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="bg-blue-50 rounded-lg p-4">
                                  <p className="text-sm font-medium text-blue-900 mb-2">BPJS Kesehatan</p>
                                  <div className="space-y-1">
                                    <div className="flex justify-between text-xs">
                                      <span className="text-blue-700">Karyawan</span>
                                      <span className="font-medium">{formatCurrency(payslip.contributions.bpjs_kesehatan.employee)}</span>
                                    </div>
                                    <div className="flex justify-between text-xs">
                                      <span className="text-blue-700">Perusahaan</span>
                                      <span className="font-medium">{formatCurrency(payslip.contributions.bpjs_kesehatan.employer)}</span>
                                    </div>
                                    <div className="border-t border-blue-200 pt-1 mt-2">
                                      <div className="flex justify-between text-xs font-semibold">
                                        <span className="text-blue-900">Total</span>
                                        <span className="text-blue-900">{formatCurrency(payslip.contributions.bpjs_kesehatan.total)}</span>
                                      </div>
                                    </div>
                                  </div>
                                </div>

                                <div className="bg-green-50 rounded-lg p-4">
                                  <p className="text-sm font-medium text-green-900 mb-2">BPJS Ketenagakerjaan</p>
                                  <div className="space-y-1">
                                    <div className="grid grid-cols-2 gap-2 text-xs">
                                      <div className="flex justify-between">
                                        <span className="text-green-700">JHT</span>
                                        <span className="font-medium">{formatCurrency(payslip.contributions.bpjs_ketenagakerjaan.jht)}</span>
                                      </div>
                                      <div className="flex justify-between">
                                        <span className="text-green-700">JKM</span>
                                        <span className="font-medium">{formatCurrency(payslip.contributions.bpjs_ketenagakerjaan.jkm)}</span>
                                      </div>
                                      <div className="flex justify-between">
                                        <span className="text-green-700">JKK</span>
                                        <span className="font-medium">{formatCurrency(payslip.contributions.bpjs_ketenagakerjaan.jkk)}</span>
                                      </div>
                                      <div className="flex justify-between">
                                        <span className="text-green-700">JP</span>
                                        <span className="font-medium">{formatCurrency(payslip.contributions.bpjs_ketenagakerjaan.jp)}</span>
                                      </div>
                                    </div>
                                    <div className="border-t border-green-200 pt-1 mt-2">
                                      <div className="flex justify-between text-xs">
                                        <span className="text-green-700">Karyawan</span>
                                        <span className="font-medium">{formatCurrency(payslip.contributions.bpjs_ketenagakerjaan.employee_total)}</span>
                                      </div>
                                      <div className="flex justify-between text-xs">
                                        <span className="text-green-700">Perusahaan</span>
                                        <span className="font-medium">{formatCurrency(payslip.contributions.bpjs_ketenagakerjaan.employer_total)}</span>
                                      </div>
                                      <div className="flex justify-between text-xs font-semibold mt-1">
                                        <span className="text-green-900">Total</span>
                                        <span className="text-green-900">{formatCurrency(payslip.contributions.bpjs_ketenagakerjaan.total)}</span>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* Net Pay */}
                            <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-4">
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="text-sm text-green-700">Pendapatan Bersih (Take Home Pay)</p>
                                  <p className="text-xs text-green-600">{payslip.payment_method}</p>
                                </div>
                                <p className="text-2xl font-bold text-green-700">{formatCurrency(payslip.net_pay)}</p>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* Tax Documents Tab */}
          {selectedTab === "tax" && (
            <div className="space-y-4">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
              ) : taxDocuments.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada dokumen pajak</h3>
                  <p className="text-gray-600">Dokumen pajak akan tersedia setelah akhir tahun pajak</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Jenis Dokumen
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Tahun Pajak
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Pendapatan Kotor
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Pajak Ditahan
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Status
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          Aksi
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {taxDocuments.map((doc) => (
                        <tr key={doc.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4">
                            <div className="flex items-center space-x-3">
                              <FileText className="w-5 h-5 text-gray-400" />
                              <span className="font-medium text-gray-900">{getTaxDocumentLabel(doc.document_type)}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">{doc.tax_year}</td>
                          <td className="px-6 py-4 text-sm text-gray-900">
                            {formatCurrency(doc.gross_income)}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">
                            {formatCurrency(doc.tax_withheld)}
                          </td>
                          <td className="px-6 py-4">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                                doc.status
                              )}`}
                            >
                              {getStatusLabel(doc.status)}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <button
                              onClick={() => handleDownloadTaxDocument(doc.id)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                              title="Unduh"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Reimbursements Tab */}
          {selectedTab === "reimbursements" && (
            <div className="space-y-4">
              {/* Status Filter */}
              <div className="flex items-center space-x-4">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">Semua Status</option>
                  <option value="pending">Menunggu</option>
                  <option value="approved">Disetujui</option>
                  <option value="paid">Dibayar</option>
                  <option value="rejected">Ditolak</option>
                </select>
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
              ) : filteredReimbursements.length === 0 ? (
                <div className="text-center py-12">
                  <Wallet className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Tidak ada reimbursement</h3>
                  <p className="text-gray-600">
                    {statusFilter !== "all"
                      ? "Tidak ada reimbursement yang sesuai dengan filter"
                      : "Belum ada pengajuan reimbursement"}
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredReimbursements.map((reimb) => (
                    <div key={reimb.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                                reimb.status
                              )}`}
                            >
                              {getStatusLabel(reimb.status)}
                            </span>
                            <span className="text-xs text-gray-500">{formatDate(reimb.request_date)}</span>
                          </div>
                          <p className="font-medium text-gray-900">{reimb.description}</p>
                          <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                            <span>Kategori: {getReimbursementCategoryLabel(reimb.category)}</span>
                            <span className="font-semibold text-gray-900">
                              {formatCurrency(reimb.amount)}
                            </span>
                          </div>
                          {reimb.notes && (
                            <p className="text-sm text-gray-500 mt-2">Catatan: {reimb.notes}</p>
                          )}
                          {reimb.payment_date && (
                            <p className="text-sm text-green-600 mt-2">
                              Dibayar pada: {formatDate(reimb.payment_date)}
                            </p>
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          {reimb.receipt_url && (
                            <a
                              href={reimb.receipt_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                              title="Lihat Bukti"
                            >
                              <Eye className="w-4 h-4" />
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
