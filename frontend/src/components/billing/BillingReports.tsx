/**
 * Billing Reports Component for STORY-028
 *
 * Comprehensive billing reports with:
 * - Revenue report (daily, weekly, monthly)
 * - Aging report (outstanding invoices by age)
 * - Payer summary (BPJS, insurance, cash breakdown)
 * - Export to CSV/Excel
 */

import { useState, useEffect } from 'react';
import {
  BarChart,
  TrendingUp,
  Clock,
  CreditCard,
  DollarSign,
  Download,
  Calendar,
  Filter,
  RefreshCw,
  FileSpreadsheet,
  FileText,
} from 'lucide-react';

// Types
interface RevenueData {
  period: string;
  gross_revenue: number;
  discounts: number;
  bpjs_payments: number;
  insurance_payments: number;
  cash_payments: number;
  net_revenue: number;
  invoice_count: number;
}

interface AgingData {
  category: string;
  count: number;
  total_amount: number;
  percentage: number;
}

interface PayerSummary {
  payer_type: string;
  invoice_count: number;
  total_billed: number;
  total_collected: number;
  outstanding: number;
  collection_rate: number;
}

interface ReportFilters {
  report_type: 'revenue' | 'aging' | 'payer';
  period: 'daily' | 'weekly' | 'monthly' | 'custom';
  date_from: string;
  date_to: string;
}

export function BillingReports() {
  const [reportType, setReportType] = useState<'revenue' | 'aging' | 'payer'>('revenue');
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly'>('monthly');
  const [revenueData, setRevenueData] = useState<RevenueData[]>([]);
  const [agingData, setAgingData] = useState<AgingData[]>([]);
  const [payerSummary, setPayerSummary] = useState<PayerSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [dateRange, setDateRange] = useState({ from: '', to: '' });

  useEffect(() => {
    loadReports();
  }, [reportType, period]);

  const loadReports = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        period,
        ...(dateRange.from && { date_from: dateRange.from }),
        ...(dateRange.to && { date_to: dateRange.to }),
      });

      if (reportType === 'revenue') {
        const response = await fetch(`/api/v1/billing/reports/revenue?${params}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setRevenueData(data);
        }
      } else if (reportType === 'aging') {
        const response = await fetch(`/api/v1/billing/reports/aging?${params}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setAgingData(data);
        }
      } else if (reportType === 'payer') {
        const response = await fetch(`/api/v1/billing/reports/payer?${params}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setPayerSummary(data);
        }
      }
    } catch (error) {
      console.error('Failed to load reports:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const exportToCSV = async () => {
    try {
      const params = new URLSearchParams({
        report_type: reportType,
        period,
        ...(dateRange.from && { date_from: dateRange.from }),
        ...(dateRange.to && { date_to: dateRange.to }),
      });

      const response = await fetch(`/api/v1/billing/reports/export?${params}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Billing-Report-${reportType}-${period}-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Failed to export report:', error);
    }
  };

  const exportToExcel = async () => {
    try {
      const params = new URLSearchParams({
        report_type: reportType,
        period,
        format: 'excel',
        ...(dateRange.from && { date_from: dateRange.from }),
        ...(dateRange.to && { date_to: dateRange.to }),
      });

      const response = await fetch(`/api/v1/billing/reports/export?${params}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Billing-Report-${reportType}-${period}-${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Failed to export report:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercent = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const calculateTotals = () => {
    if (reportType === 'revenue' && revenueData.length > 0) {
      return revenueData.reduce((acc, item) => ({
        gross_revenue: acc.gross_revenue + item.gross_revenue,
        discounts: acc.discounts + item.discounts,
        bpjs_payments: acc.bpjs_payments + item.bpjs_payments,
        insurance_payments: acc.insurance_payments + item.insurance_payments,
        cash_payments: acc.cash_payments + item.cash_payments,
        net_revenue: acc.net_revenue + item.net_revenue,
        invoice_count: acc.invoice_count + item.invoice_count,
      }), {
        gross_revenue: 0,
        discounts: 0,
        bpjs_payments: 0,
        insurance_payments: 0,
        cash_payments: 0,
        net_revenue: 0,
        invoice_count: 0,
      });
    }
    return null;
  };

  const totals = calculateTotals();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <BarChart className="h-6 w-6 mr-2" />
            Laporan Penagihan
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Analisis pendapatan dan status pembayaran
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={exportToCSV}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <FileSpreadsheet className="h-4 w-4 mr-2" />
            CSV
          </button>
          <button
            onClick={exportToExcel}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <FileText className="h-4 w-4 mr-2" />
            Excel
          </button>
        </div>
      </div>

      {/* Report Type Selector */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            <button
              onClick={() => setReportType('revenue')}
              className={`inline-flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                reportType === 'revenue'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <TrendingUp className="h-4 w-4 mr-2" />
              Laporan Pendapatan
            </button>
            <button
              onClick={() => setReportType('aging')}
              className={`inline-flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                reportType === 'aging'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Clock className="h-4 w-4 mr-2" />
              Laporan Umur Piutang
            </button>
            <button
              onClick={() => setReportType('payer')}
              className={`inline-flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                reportType === 'payer'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <CreditCard className="h-4 w-4 mr-2" />
              Ringkasan Penanggung
            </button>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value as any)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="daily">Harian</option>
                <option value="weekly">Mingguan</option>
                <option value="monthly">Bulanan</option>
              </select>
            </div>
            <button
              onClick={loadReports}
              disabled={isLoading}
              className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Revenue Report */}
      {reportType === 'revenue' && (
        <div className="space-y-6">
          {/* Summary Cards */}
          {totals && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white shadow rounded-lg p-4">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <DollarSign className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Pendapatan Kotor</p>
                    <p className="text-xl font-bold text-gray-900">{formatCurrency(totals.gross_revenue)}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-4">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <TrendingUp className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Pendapatan Bersih</p>
                    <p className="text-xl font-bold text-gray-900">{formatCurrency(totals.net_revenue)}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-4">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <CreditCard className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Pembayaran BPJS</p>
                    <p className="text-xl font-bold text-gray-900">{formatCurrency(totals.bpjs_payments)}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-4">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <FileText className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Total Faktur</p>
                    <p className="text-xl font-bold text-gray-900">{totals.invoice_count}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Revenue Table */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Periode</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Pendapatan Kotor</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Diskon</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Pembayaran BPJS</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Pembayaran Asuransi</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Pembayaran Tunai</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Pendapatan Bersih</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Jumlah Faktur</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {revenueData.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {item.period}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        {formatCurrency(item.gross_revenue)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-red-600">
                        -{formatCurrency(item.discounts)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-blue-600">
                        {formatCurrency(item.bpjs_payments)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-purple-600">
                        {formatCurrency(item.insurance_payments)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-green-600">
                        {formatCurrency(item.cash_payments)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right font-bold text-gray-900">
                        {formatCurrency(item.net_revenue)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        {item.invoice_count}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {revenueData.length === 0 && !isLoading && (
              <div className="text-center py-8 text-gray-500">
                <BarChart className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Tidak ada data pendapatan untuk periode ini</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Aging Report */}
      {reportType === 'aging' && (
        <div className="space-y-6">
          {/* Aging Chart */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Distribusi Umur Piutang</h3>
            <div className="space-y-4">
              {agingData.map((item) => {
                const categoryColors: Record<string, string> = {
                  '0-30': 'bg-green-500',
                  '31-60': 'bg-yellow-500',
                  '61-90': 'bg-orange-500',
                  '90+': 'bg-red-500',
                };
                const barColor = categoryColors[item.category] || 'bg-gray-500';

                return (
                  <div key={item.category}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm font-medium text-gray-900">
                          {item.category} Hari
                        </span>
                      </div>
                      <span className="text-sm font-bold text-gray-900">
                        {formatCurrency(item.total_amount)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-4">
                      <div
                        className={`${barColor} h-4 rounded-full transition-all`}
                        style={{ width: `${item.percentage}%` }}
                      ></div>
                    </div>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-xs text-gray-500">
                        {item.count} faktur
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatPercent(item.percentage)} dari total
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>

            {agingData.length === 0 && !isLoading && (
              <div className="text-center py-8 text-gray-500">
                <Clock className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Tidak ada piutang tertunggak</p>
              </div>
            )}
          </div>

          {/* Aging Table */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kategori</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Jumlah Faktur</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total Nilai</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Persentase</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {agingData.map((item) => (
                    <tr key={item.category} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {item.category} Hari
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        {item.count}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right font-bold text-gray-900">
                        {formatCurrency(item.total_amount)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        {formatPercent(item.percentage)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Payer Summary */}
      {reportType === 'payer' && (
        <div className="space-y-6">
          {/* Payer Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {payerSummary.map((payer) => {
              const payerIcons: Record<string, any> = {
                'bpjs': CreditCard,
                'insurance': FileText,
                'cash': DollarSign,
              };
              const payerColors: Record<string, string> = {
                'bpjs': 'bg-green-100 text-green-600',
                'insurance': 'bg-purple-100 text-purple-600',
                'cash': 'bg-blue-100 text-blue-600',
              };
              const Icon = payerIcons[payer.payer_type] || DollarSign;
              const iconColor = payerColors[payer.payer_type] || 'bg-gray-100 text-gray-600';

              return (
                <div key={payer.payer_type} className="bg-white shadow rounded-lg p-6">
                  <div className="flex items-center mb-4">
                    <div className={`p-3 rounded-lg ${iconColor}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-500 capitalize">
                        {payer.payer_type === 'bpjs' ? 'BPJS' :
                         payer.payer_type === 'insurance' ? 'Asuransi' : 'Tunai'}
                      </p>
                      <p className="text-2xl font-bold text-gray-900">
                        {formatCurrency(payer.total_collected)}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Jumlah Faktur</span>
                      <span className="font-medium text-gray-900">{payer.invoice_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total Ditagih</span>
                      <span className="font-medium text-gray-900">{formatCurrency(payer.total_billed)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Tertunggak</span>
                      <span className="font-medium text-orange-600">{formatCurrency(payer.outstanding)}</span>
                    </div>
                    <div className="flex justify-between pt-2 border-t">
                      <span className="text-gray-900 font-medium">Rate Penagihan</span>
                      <span className={`font-bold ${
                        payer.collection_rate >= 80 ? 'text-green-600' :
                        payer.collection_rate >= 60 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {formatPercent(payer.collection_rate)}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Payer Table */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Penanggung</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Jumlah Faktur</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total Ditagih</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Ter koleksi</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tertunggak</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Rate Penagihan</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {payerSummary.map((payer) => (
                    <tr key={payer.payer_type} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900 capitalize">
                        {payer.payer_type === 'bpjs' ? 'BPJS' :
                         payer.payer_type === 'insurance' ? 'Asuransi' : 'Tunai'}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        {payer.invoice_count}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        {formatCurrency(payer.total_billed)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-green-600 font-medium">
                        {formatCurrency(payer.total_collected)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right text-orange-600 font-medium">
                        {formatCurrency(payer.outstanding)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          payer.collection_rate >= 80 ? 'bg-green-100 text-green-800' :
                          payer.collection_rate >= 60 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {formatPercent(payer.collection_rate)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {payerSummary.length === 0 && !isLoading && (
              <div className="text-center py-8 text-gray-500">
                <CreditCard className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Tidak ada data penanggung</p>
              </div>
            )}
          </div>
        </div>
      )}

      {isLoading && (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )}
    </div>
  );
}
