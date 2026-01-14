"""BPJS Claim Reports Component

Comprehensive BPJS claim reports with:
- Claim statistics dashboard
- Upcoming deadlines
- Claim summary by package
- Claim summary by status
- Export to Excel
"""

import { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  FileText,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  Download,
  Calendar,
  DollarSign,
  Package,
  Filter,
  RefreshCw,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

// Types
interface ClaimStatistics {
  total_claims: number;
  submitted_claims: number;
  approved_claims: number;
  rejected_claims: number;
  pending_claims: number;
  total_value: number;
  approved_value: number;
  pending_value: number;
  rejection_rate: number;
  approval_rate: number;
  average_processing_days: number;
}

interface PackageSummary {
  package_code: string;
  package_name: string;
  package_type: string;
  total_claims: number;
  approved_claims: number;
  rejected_claims: number;
  total_value: number;
  approved_value: number;
  average_rate: number;
}

interface StatusSummary {
  status: string;
  count: number;
  value: number;
  percentage: number;
}

interface UpcomingDeadline {
  claim_id: string;
  patient_name: string;
  sep_number: string;
  deadline_type: 'response' | 'verification';
  deadline_date: string;
  days_remaining: number;
  status: string;
}

interface ReportFilters {
  period: 'month' | 'quarter' | 'year' | 'custom';
  date_from: string;
  date_to: string;
  package_type: string;
  status: string;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export function BPJSClaimReports() {
  const [statistics, setStatistics] = useState<ClaimStatistics | null>(null);
  const [packageSummary, setPackageSummary] = useState<PackageSummary[]>([]);
  const [statusSummary, setStatusSummary] = useState<StatusSummary[]>([]);
  const [upcomingDeadlines, setUpcomingDeadlines] = useState<UpcomingDeadline[]>([]);
  const [filters, setFilters] = useState<ReportFilters>({
    period: 'month',
    date_from: '',
    date_to: '',
    package_type: 'all',
    status: 'all',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    loadReportData();
  }, [filters]);

  const loadReportData = async () => {
    setIsLoading(true);
    try {
      const queryParams = new URLSearchParams();
      if (filters.period !== 'custom') {
        queryParams.append('period', filters.period);
      } else {
        if (filters.date_from) queryParams.append('date_from', filters.date_from);
        if (filters.date_to) queryParams.append('date_to', filters.date_to);
      }
      if (filters.package_type !== 'all') queryParams.append('package_type', filters.package_type);
      if (filters.status !== 'all') queryParams.append('status', filters.status);

      const response = await fetch(`/api/v1/bpjs/reports?${queryParams}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStatistics(data.statistics);
        setPackageSummary(data.package_summary);
        setStatusSummary(data.status_summary);
        setUpcomingDeadlines(data.upcoming_deadlines);
      }
    } catch (error) {
      console.error('Gagal memuat laporan:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const exportToExcel = async () => {
    setIsExporting(true);
    try {
      const queryParams = new URLSearchParams();
      if (filters.period !== 'custom') {
        queryParams.append('period', filters.period);
      } else {
        if (filters.date_from) queryParams.append('date_from', filters.date_from);
        if (filters.date_to) queryParams.append('date_to', filters.date_to);
      }

      const response = await fetch(`/api/v1/bpjs/reports/export?${queryParams}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `BPJS-Claim-Report-${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Gagal export laporan:', error);
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const getDeadlineStatus = (days: number) => {
    if (days < 0) return 'expired';
    if (days <= 2) return 'urgent';
    if (days <= 7) return 'warning';
    return 'normal';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <FileText className="h-6 w-6 mr-2" />
            Laporan Klaim BPJS
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Statistik dan analisis klaim BPJS
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadReportData}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </button>
          <button
            onClick={exportToExcel}
            disabled={isExporting}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:bg-gray-300"
          >
            {isExporting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Exporting...
              </>
            ) : (
              <>
                <Download className="h-4 w-4 mr-2" />
                Export Excel
              </>
            )}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Filter className="h-5 w-5 text-gray-400 mr-2" />
          <h3 className="text-sm font-medium text-gray-900">Filter Laporan</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select
            value={filters.period}
            onChange={(e) => setFilters({ ...filters, period: e.target.value as 'month' | 'quarter' | 'year' | 'custom' })}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="month">Bulan Ini</option>
            <option value="quarter">Quarter Ini</option>
            <option value="year">Tahun Ini</option>
            <option value="custom">Custom</option>
          </select>

          {filters.period === 'custom' && (
            <>
              <input
                type="date"
                value={filters.date_from}
                onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
              />
              <input
                type="date"
                value={filters.date_to}
                onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </>
          )}

          <select
            value={filters.package_type}
            onChange={(e) => setFilters({ ...filters, package_type: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">Semua Tipe Paket</option>
            <option value="inap">Rawat Inap</option>
            <option value="jalan">Rawat Jalan</option>
            <option value="igd">IGD</option>
            <option value="katarak">Katarak</option>
            <option value="klinis">Klinis</option>
          </select>

          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">Semua Status</option>
            <option value="submitted">Submitted</option>
            <option value="verified">Verified</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : statistics ? (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Klaim</p>
                  <p className="text-2xl font-bold text-gray-900">{statistics.total_claims}</p>
                </div>
                <FileText className="h-8 w-8 text-blue-500" />
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Disetujui</p>
                  <p className="text-2xl font-bold text-green-600">{statistics.approved_claims}</p>
                  <p className="text-xs text-gray-500 mt-1">{statistics.approval_rate.toFixed(1)}%</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Ditolak</p>
                  <p className="text-2xl font-bold text-red-600">{statistics.rejected_claims}</p>
                  <p className="text-xs text-gray-500 mt-1">{statistics.rejection_rate.toFixed(1)}%</p>
                </div>
                <AlertCircle className="h-8 w-8 text-red-500" />
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Nilai Total</p>
                  <p className="text-2xl font-bold text-blue-600">{formatCurrency(statistics.total_value)}</p>
                  <p className="text-xs text-gray-500 mt-1">Approved: {formatCurrency(statistics.approved_value)}</p>
                </div>
                <DollarSign className="h-8 w-8 text-blue-500" />
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Status Distribution */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Distribusi Status</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={statusSummary}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.status}: ${entry.percentage.toFixed(1)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {statusSummary.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Package Summary */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Ringkasan Paket</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={packageSummary.slice(0, 5)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="package_code" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="approved_claims" fill="#10b981" name="Approved" />
                  <Bar dataKey="rejected_claims" fill="#ef4444" name="Rejected" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Package Summary Table */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Ringkasan per Paket INA-CBG</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kode</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nama Paket</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipe</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Total</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Approved</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Rejected</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Nilai Total</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Nilai Approved</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {packageSummary.map((pkg) => (
                    <tr key={pkg.package_code} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {pkg.package_code}
                      </td>
                      <td className="px-4 py-4 text-sm text-gray-900">{pkg.package_name}</td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <Badge variant="neutral">{pkg.package_type}</Badge>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-center text-gray-900">
                        {pkg.total_claims}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-center text-green-600">
                        {pkg.approved_claims}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-center text-red-600">
                        {pkg.rejected_claims}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        {formatCurrency(pkg.total_value)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-green-600">
                        {formatCurrency(pkg.approved_value)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Upcoming Deadlines */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Deadline Mendatang</h3>
              <div className="flex items-center">
                <Clock className="h-5 w-5 text-orange-500 mr-2" />
                <span className="text-sm text-gray-600">{upcomingDeadlines.length} deadline</span>
              </div>
            </div>

            <div className="space-y-3">
              {upcomingDeadlines.map((deadline) => {
                const status = getDeadlineStatus(deadline.days_remaining);
                return (
                  <div key={deadline.claim_id} className={`border rounded-lg p-4 ${
                      status === 'expired' ? 'bg-red-50 border-red-200' :
                      status === 'urgent' ? 'bg-orange-50 border-orange-200' :
                      status === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                      'bg-gray-50 border-gray-200'
                    }`}>
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-sm font-medium text-gray-900">{deadline.patient_name}</span>
                          <Badge variant="neutral" dot>{deadline.deadline_type}</Badge>
                        </div>
                        <div className="flex items-center gap-4 text-xs text-gray-600">
                          <span>SEP: {deadline.sep_number}</span>
                          <span>Deadline: {formatDate(deadline.deadline_date)}</span>
                        </div>
                      </div>
                      <div className={`text-sm font-medium ${
                        status === 'expired' ? 'text-red-600' :
                        status === 'urgent' ? 'text-orange-600' :
                        status === 'warning' ? 'text-yellow-600' :
                        'text-gray-600'
                      }`}>
                        {deadline.days_remaining < 0 ? `${Math.abs(deadline.days_remaining)} hari terlambat` :
                         deadline.days_remaining === 0 ? 'Hari ini' :
                         `${deadline.days_remaining} hari lagi`}
                      </div>
                    </div>
                  </div>
                );
              })}

              {upcomingDeadlines.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Clock className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>Tidak ada deadline mendatang</p>
                </div>
              )}
            </div>
          </div>

          {/* Additional Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center mb-4">
                <TrendingUp className="h-5 w-5 text-blue-500 mr-2" />
                <h3 className="text-sm font-medium text-gray-900">Rata-rata Proses</h3>
              </div>
              <p className="text-3xl font-bold text-gray-900">{statistics.average_processing_days.toFixed(1)}</p>
              <p className="text-xs text-gray-500 mt-1">hari per klaim</p>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Package className="h-5 w-5 text-green-500 mr-2" />
                <h3 className="text-sm font-medium text-gray-900">Tingkat Approval</h3>
              </div>
              <p className="text-3xl font-bold text-green-600">{statistics.approval_rate.toFixed(1)}%</p>
              <p className="text-xs text-gray-500 mt-1">dari total klaim</p>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center mb-4">
                <DollarSign className="h-5 w-5 text-blue-500 mr-2" />
                <h3 className="text-sm font-medium text-gray-900">Nilai Pending</h3>
              </div>
              <p className="text-2xl font-bold text-orange-600">{formatCurrency(statistics.pending_value)}</p>
              <p className="text-xs text-gray-500 mt-1">{statistics.pending_claims} klaim pending</p>
            </div>
          </div>
        </>
      ) : (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-500">Tidak ada data laporan tersedia</p>
        </div>
      )}
    </div>
  );
}
