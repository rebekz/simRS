"use client";

import React, { useState, useMemo } from 'react';
import {
  History,
  CheckCircle,
  XCircle,
  RefreshCw,
  Download,
  Filter,
  Calendar,
  User,
  CreditCard,
  FileText,
  TrendingUp,
  TrendingDown,
  Clock,
  AlertCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

// ============================================================================
// TYPES
// ============================================================================

export type BPJSActionType =
  | 'ELIGIBILITY_CHECK'
  | 'SEP_CREATE'
  | 'SEP_CANCEL'
  | 'REFERRAL_CHECK'
  | 'Rujukan_CREATE'
  | 'MANUAL_ENTRY';

export interface BPJSLogEntry {
  id: string;
  timestamp: string;
  action: BPJSActionType;
  cardNumber: string;
  patientName?: string;
  userId: string;
  userName: string;
  success: boolean;
  errorMessage?: string;
  errorCode?: string;
  responseTime?: number; // milliseconds
  details?: Record<string, unknown>;
}

export interface BPJSStatistics {
  totalCalls: number;
  successCalls: number;
  failedCalls: number;
  successRate: number;
  avgResponseTime: number;
  callsByAction: Record<BPJSActionType, number>;
  callsByDay: { date: string; count: number }[];
}

export interface BPJSHistoryLogProps {
  entries: BPJSLogEntry[];
  onRefresh?: () => void;
  onExport?: (format: 'csv' | 'json') => void;
  isLoading?: boolean;
  showFilters?: boolean;
  className?: string;
}

export interface BPJSStatisticsCardProps {
  statistics: BPJSStatistics;
  className?: string;
}

export interface SEPHistoryItem {
  id: string;
  sepNumber: string;
  cardNumber: string;
  patientName: string;
  created_at: string;
  serviceType: 'RJ' | 'RI';
  polyclinic: string;
  doctorName?: string;
  status: 'active' | 'used' | 'cancelled';
  createdBy: string;
}

export interface SEPHistoryProps {
  items: SEPHistoryItem[];
  onViewDetails?: (item: SEPHistoryItem) => void;
  className?: string;
}

// ============================================================================
// MOCK DATA
// ============================================================================

const mockLogEntries: BPJSLogEntry[] = [
  {
    id: '1',
    timestamp: '2026-02-27T14:30:00Z',
    action: 'ELIGIBILITY_CHECK',
    cardNumber: '0001234567890',
    patientName: 'Ahmad Susanto',
    userId: 'user1',
    userName: 'Registration Staff',
    success: true,
    responseTime: 450,
  },
  {
    id: '2',
    timestamp: '2026-02-27T14:25:00Z',
    action: 'SEP_CREATE',
    cardNumber: '0001234567890',
    patientName: 'Ahmad Susanto',
    userId: 'user1',
    userName: 'Registration Staff',
    success: true,
    responseTime: 890,
    details: { sepNumber: '0301R0010226V000001' },
  },
  {
    id: '3',
    timestamp: '2026-02-27T14:20:00Z',
    action: 'ELIGIBILITY_CHECK',
    cardNumber: '0009876543210',
    patientName: 'Siti Rahayu',
    userId: 'user2',
    userName: 'Doctor Staff',
    success: false,
    errorMessage: 'Nomor kartu BPJS tidak ditemukan',
    errorCode: '2002',
    responseTime: 320,
  },
  {
    id: '4',
    timestamp: '2026-02-27T14:15:00Z',
    action: 'REFERRAL_CHECK',
    cardNumber: '0001234567890',
    patientName: 'Ahmad Susanto',
    userId: 'user1',
    userName: 'Registration Staff',
    success: true,
    responseTime: 520,
  },
  {
    id: '5',
    timestamp: '2026-02-27T14:10:00Z',
    action: 'MANUAL_ENTRY',
    cardNumber: '0001111111111',
    patientName: 'Budi Hartono',
    userId: 'user3',
    userName: 'Admin',
    success: true,
    details: { reason: 'BPJS API tidak dapat diakses' },
  },
  {
    id: '6',
    timestamp: '2026-02-27T14:05:00Z',
    action: 'SEP_CANCEL',
    cardNumber: '0001234567890',
    patientName: 'Ahmad Susanto',
    userId: 'user1',
    userName: 'Registration Staff',
    success: true,
    responseTime: 380,
    details: { sepNumber: '0301R0010226V000000' },
  },
];

const mockSEPHistory: SEPHistoryItem[] = [
  {
    id: '1',
    sepNumber: '0301R0010226V000001',
    cardNumber: '0001234567890',
    patientName: 'Ahmad Susanto',
    created_at: '2026-02-27T14:25:00Z',
    serviceType: 'RJ',
    polyclinic: 'Poli Umum',
    doctorName: 'dr. Budi Santoso',
    status: 'active',
    createdBy: 'Registration Staff',
  },
  {
    id: '2',
    sepNumber: '0301R0010226V000002',
    cardNumber: '0009876543210',
    patientName: 'Siti Rahayu',
    created_at: '2026-02-26T10:15:00Z',
    serviceType: 'RI',
    polyclinic: 'Poli Penyakit Dalam',
    doctorName: 'dr. Dewi Lestari, Sp.PD',
    status: 'used',
    createdBy: 'Registration Staff',
  },
  {
    id: '3',
    sepNumber: '0301R0010226V000003',
    cardNumber: '0001111111111',
    patientName: 'Budi Hartono',
    created_at: '2026-02-25T09:00:00Z',
    serviceType: 'RJ',
    polyclinic: 'Poli Jantung',
    doctorName: 'dr. Andi Wijaya, Sp.JP',
    status: 'cancelled',
    createdBy: 'Admin',
  },
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getActionLabel(action: BPJSActionType): string {
  const labels: Record<BPJSActionType, string> = {
    ELIGIBILITY_CHECK: 'Cek Eligibilitas',
    SEP_CREATE: 'Buat SEP',
    SEP_CANCEL: 'Batalkan SEP',
    REFERRAL_CHECK: 'Cek Rujukan',
    Rujukan_CREATE: 'Buat Rujukan',
    MANUAL_ENTRY: 'Entry Manual',
  };
  return labels[action] || action;
}

function getActionColor(action: BPJSActionType): string {
  const colors: Record<BPJSActionType, string> = {
    ELIGIBILITY_CHECK: 'bg-blue-100 text-blue-700',
    SEP_CREATE: 'bg-green-100 text-green-700',
    SEP_CANCEL: 'bg-red-100 text-red-700',
    REFERRAL_CHECK: 'bg-purple-100 text-purple-700',
    Rujukan_CREATE: 'bg-indigo-100 text-indigo-700',
    MANUAL_ENTRY: 'bg-yellow-100 text-yellow-700',
  };
  return colors[action] || 'bg-gray-100 text-gray-700';
}

function formatTimestamp(isoString: string): string {
  return new Date(isoString).toLocaleString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function maskCardNumber(cardNumber: string): string {
  if (cardNumber.length <= 4) return cardNumber;
  return `${cardNumber.slice(0, 4)}****${cardNumber.slice(-4)}`;
}

// ============================================================================
// STATISTICS CARD COMPONENT
// ============================================================================

export function BPJSStatisticsCard({
  statistics,
  className = '',
}: BPJSStatisticsCardProps) {
  const statItems = [
    {
      label: 'Success Rate',
      value: `${statistics.successRate.toFixed(1)}%`,
      icon: statistics.successRate >= 95 ? TrendingUp : TrendingDown,
      iconColor: statistics.successRate >= 95 ? 'text-green-600' : 'text-yellow-600',
    },
    {
      label: 'Total Calls',
      value: statistics.totalCalls.toLocaleString('id-ID'),
      icon: RefreshCw,
      iconColor: 'text-blue-600',
    },
    {
      label: 'Failed Calls',
      value: statistics.failedCalls.toLocaleString('id-ID'),
      icon: XCircle,
      iconColor: 'text-red-600',
    },
    {
      label: 'Avg Response',
      value: `${Math.round(statistics.avgResponseTime)}ms`,
      icon: Clock,
      iconColor: 'text-purple-600',
    },
  ];

  return (
    <div className={`bg-white rounded-lg shadow border border-gray-200 ${className}`}>
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-teal-600" />
          BPJS API Statistics
        </h3>
      </div>
      <div className="p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        {statItems.map((stat) => (
          <div key={stat.label} className="text-center">
            <stat.icon className={`w-6 h-6 mx-auto mb-2 ${stat.iconColor}`} />
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            <p className="text-xs text-gray-500">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Calls by Action */}
      <div className="p-4 border-t border-gray-200">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Calls by Action</h4>
        <div className="space-y-2">
          {Object.entries(statistics.callsByAction).map(([action, count]) => (
            <div key={action} className="flex items-center justify-between text-sm">
              <span className="text-gray-600">{getActionLabel(action as BPJSActionType)}</span>
              <span className="font-medium text-gray-900">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// LOG ENTRY ITEM COMPONENT
// ============================================================================

function LogEntryItem({ entry }: { entry: BPJSLogEntry }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={`p-4 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 transition-colors ${
        !entry.success ? 'bg-red-50/50' : ''
      }`}
    >
      <div className="flex items-start gap-4">
        {/* Status Icon */}
        <div className="flex-shrink-0 mt-1">
          {entry.success ? (
            <CheckCircle className="w-5 h-5 text-green-600" />
          ) : (
            <XCircle className="w-5 h-5 text-red-600" />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <Badge className={getActionColor(entry.action)}>
              {getActionLabel(entry.action)}
            </Badge>
            <span className="text-sm font-mono text-gray-600">
              {maskCardNumber(entry.cardNumber)}
            </span>
            {entry.responseTime && (
              <span className="text-xs text-gray-400">
                {entry.responseTime}ms
              </span>
            )}
          </div>

          {entry.patientName && (
            <p className="text-sm font-medium text-gray-900 mt-1">
              {entry.patientName}
            </p>
          )}

          {!entry.success && entry.errorMessage && (
            <p className="text-sm text-red-600 mt-1 flex items-center gap-1">
              <AlertCircle className="w-4 h-4" />
              {entry.errorMessage}
              {entry.errorCode && (
                <span className="text-xs font-mono">(#{entry.errorCode})</span>
              )}
            </p>
          )}

          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatTimestamp(entry.timestamp)}
            </span>
            <span className="flex items-center gap-1">
              <User className="w-3 h-3" />
              {entry.userName}
            </span>
          </div>

          {/* Expandable Details */}
          {entry.details && Object.keys(entry.details).length > 0 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-xs text-blue-600 hover:text-blue-700 mt-2"
            >
              {expanded ? 'Hide details' : 'Show details'}
            </button>
          )}

          {expanded && entry.details && (
            <div className="mt-2 p-2 bg-gray-100 rounded text-xs font-mono">
              <pre className="text-gray-700 overflow-x-auto">
                {JSON.stringify(entry.details, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// HISTORY LOG COMPONENT
// ============================================================================

export function BPJSHistoryLog({
  entries,
  onRefresh,
  onExport,
  isLoading = false,
  showFilters = true,
  className = '',
}: BPJSHistoryLogProps) {
  const [filter, setFilter] = useState<{
    action?: BPJSActionType;
    success?: boolean;
    dateFrom?: string;
    dateTo?: string;
  }>({});

  const [searchTerm, setSearchTerm] = useState('');

  const filteredEntries = useMemo(() => {
    return entries.filter((entry) => {
      // Action filter
      if (filter.action && entry.action !== filter.action) return false;

      // Success filter
      if (filter.success !== undefined && entry.success !== filter.success)
        return false;

      // Date filters
      if (filter.dateFrom) {
        const entryDate = new Date(entry.timestamp);
        const fromDate = new Date(filter.dateFrom);
        if (entryDate < fromDate) return false;
      }
      if (filter.dateTo) {
        const entryDate = new Date(entry.timestamp);
        const toDate = new Date(filter.dateTo);
        toDate.setHours(23, 59, 59);
        if (entryDate > toDate) return false;
      }

      // Search filter
      if (searchTerm) {
        const search = searchTerm.toLowerCase();
        return (
          entry.cardNumber.includes(search) ||
          entry.patientName?.toLowerCase().includes(search) ||
          entry.userName.toLowerCase().includes(search) ||
          entry.errorMessage?.toLowerCase().includes(search)
        );
      }

      return true;
    });
  }, [entries, filter, searchTerm]);

  const statistics: BPJSStatistics = useMemo(() => {
    const total = entries.length;
    const success = entries.filter((e) => e.success).length;
    const failed = total - success;
    const responseTimes = entries
      .filter((e) => e.responseTime)
      .map((e) => e.responseTime as number);

    const callsByAction: Record<BPJSActionType, number> = {
      ELIGIBILITY_CHECK: 0,
      SEP_CREATE: 0,
      SEP_CANCEL: 0,
      REFERRAL_CHECK: 0,
      Rujukan_CREATE: 0,
      MANUAL_ENTRY: 0,
    };

    entries.forEach((e) => {
      callsByAction[e.action]++;
    });

    return {
      totalCalls: total,
      successCalls: success,
      failedCalls: failed,
      successRate: total > 0 ? (success / total) * 100 : 0,
      avgResponseTime:
        responseTimes.length > 0
          ? responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length
          : 0,
      callsByAction,
      callsByDay: [], // Would be calculated from entries
    };
  }, [entries]);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Statistics */}
      <BPJSStatisticsCard statistics={statistics} />

      {/* Filters */}
      {showFilters && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5 text-gray-500" />
            <h3 className="font-semibold text-gray-900">Filters</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by card number, name..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              />
            </div>

            {/* Action Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Action Type
              </label>
              <select
                value={filter.action || ''}
                onChange={(e) =>
                  setFilter((prev) => ({
                    ...prev,
                    action: e.target.value as BPJSActionType || undefined,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              >
                <option value="">All Actions</option>
                <option value="ELIGIBILITY_CHECK">Eligibility Check</option>
                <option value="SEP_CREATE">SEP Create</option>
                <option value="SEP_CANCEL">SEP Cancel</option>
                <option value="REFERRAL_CHECK">Referral Check</option>
                <option value="MANUAL_ENTRY">Manual Entry</option>
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={filter.success === undefined ? '' : filter.success ? 'true' : 'false'}
                onChange={(e) =>
                  setFilter((prev) => ({
                    ...prev,
                    success: e.target.value === '' ? undefined : e.target.value === 'true',
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              >
                <option value="">All Status</option>
                <option value="true">Success</option>
                <option value="false">Failed</option>
              </select>
            </div>
          </div>

          {/* Date Range */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Calendar className="w-4 h-4 inline mr-1" />
                Date From
              </label>
              <input
                type="date"
                value={filter.dateFrom || ''}
                onChange={(e) =>
                  setFilter((prev) => ({ ...prev, dateFrom: e.target.value }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Calendar className="w-4 h-4 inline mr-1" />
                Date To
              </label>
              <input
                type="date"
                value={filter.dateTo || ''}
                onChange={(e) =>
                  setFilter((prev) => ({ ...prev, dateTo: e.target.value }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-2 mt-4">
            {onRefresh && (
              <Button
                variant="outline"
                onClick={onRefresh}
                disabled={isLoading}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            )}
            {onExport && (
              <>
                <Button
                  variant="outline"
                  onClick={() => onExport('csv')}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export CSV
                </Button>
                <Button
                  variant="outline"
                  onClick={() => onExport('json')}
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Export JSON
                </Button>
              </>
            )}
          </div>
        </div>
      )}

      {/* Log Entries */}
      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            <History className="w-5 h-5 text-teal-600" />
            BPJS Interaction Log
            <Badge variant="outline" className="ml-2">
              {filteredEntries.length} entries
            </Badge>
          </h3>
        </div>

        <div className="max-h-96 overflow-y-auto">
          {filteredEntries.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <History className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No log entries found</p>
            </div>
          ) : (
            filteredEntries.map((entry) => (
              <LogEntryItem key={entry.id} entry={entry} />
            ))
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// SEP HISTORY COMPONENT
// ============================================================================

export function SEPHistory({
  items,
  onViewDetails,
  className = '',
}: SEPHistoryProps) {
  const getStatusBadge = (status: SEPHistoryItem['status']) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-700">Active</Badge>;
      case 'used':
        return <Badge className="bg-blue-100 text-blue-700">Used</Badge>;
      case 'cancelled':
        return <Badge className="bg-red-100 text-red-700">Cancelled</Badge>;
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow border border-gray-200 ${className}`}>
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <FileText className="w-5 h-5 text-teal-600" />
          SEP History
        </h3>
      </div>

      <div className="divide-y divide-gray-100">
        {items.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <CreditCard className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No SEP history found</p>
          </div>
        ) : (
          items.map((item) => (
            <div
              key={item.id}
              className="p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-mono text-sm text-gray-900">
                      {item.sepNumber}
                    </span>
                    {getStatusBadge(item.status)}
                    <Badge variant="outline">
                      {item.serviceType === 'RJ' ? 'Rawat Jalan' : 'Rawat Inap'}
                    </Badge>
                  </div>

                  <p className="font-medium text-gray-900 mt-1">
                    {item.patientName}
                  </p>

                  <div className="grid grid-cols-2 gap-x-4 gap-y-1 mt-2 text-sm text-gray-600">
                    <span>Poli: {item.polyclinic}</span>
                    {item.doctorName && <span>Dokter: {item.doctorName}</span>}
                    <span>
                      <Clock className="w-3 h-3 inline mr-1" />
                      {formatTimestamp(item.created_at)}
                    </span>
                    <span>
                      <User className="w-3 h-3 inline mr-1" />
                      {item.createdBy}
                    </span>
                  </div>
                </div>

                {onViewDetails && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onViewDetails(item)}
                  >
                    View Details
                  </Button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// ============================================================================
// EXPORT UTILITY
// ============================================================================

export function exportToCSV(entries: BPJSLogEntry[], filename = 'bpjs-history.csv'): void {
  const headers = [
    'Timestamp',
    'Action',
    'Card Number',
    'Patient Name',
    'User',
    'Success',
    'Error Message',
    'Response Time (ms)',
  ];

  const rows = entries.map((entry) => [
    entry.timestamp,
    entry.action,
    entry.cardNumber,
    entry.patientName || '',
    entry.userName,
    entry.success ? 'Yes' : 'No',
    entry.errorMessage || '',
    entry.responseTime?.toString() || '',
  ]);

  const csvContent = [
    headers.join(','),
    ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

export function exportToJSON(entries: BPJSLogEntry[], filename = 'bpjs-history.json'): void {
  const jsonContent = JSON.stringify(entries, null, 2);
  const blob = new Blob([jsonContent], { type: 'application/json' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

// Re-export mock data for demo
export { mockLogEntries, mockSEPHistory };
