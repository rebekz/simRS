"use client";

import React, { useState, useEffect, useCallback } from "react";
import { CheckCircle, XCircle, AlertCircle, Clock, RefreshCw, Info } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { BPJSStatus } from "@/types";

// ============================================================================
// TYPES
// ============================================================================

export type BPJSPesertaType = 'PBI' | 'Non-PBI' | 'PBPU' | 'Pegawai Negeri' | 'Pensiunan' | 'Unknown';

export interface BPJSStatusData {
  cardNumber: string;
  status: BPJSStatus;
  statusDate: string;
  eligibilityDate: string;
  faskes: string;
  faskesCode?: string;
  currentFaskes?: string;
  lastUpdated: string;
  pesertaType?: BPJSPesertaType;
}

export interface FaskesIndicatorProps {
  eligible: boolean;
  currentFaskes: string;
  registeredFaskes: string;
  showDetails?: boolean;
  className?: string;
}

export interface BPJSPesertaBadgeProps {
  pesertaType: BPJSPesertaType;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export interface BPJSStatusBadgeProps {
  status: BPJSStatus;
  showIcon?: boolean;
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export interface BPJSStatusCardProps {
  data: BPJSStatusData;
  onRefresh?: () => Promise<void>;
  autoRefresh?: boolean;
  refreshInterval?: number; // in milliseconds
  className?: string;
}

export interface BPJSStatusIndicatorProps {
  cardNumber: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
  onStatusChange?: (status: BPJSStatusData) => void;
  className?: string;
}

// ============================================================================
// MOCK API
// ============================================================================

const mockBPJSStatus: Record<string, BPJSStatusData> = {
  "1234567890123": {
    cardNumber: "1234567890123",
    status: "active",
    statusDate: "2026-01-16",
    eligibilityDate: "2026-12-31",
    faskes: "RSUD SEHAT SELALU (KODE: 12345678)",
    faskesCode: "12345678",
    currentFaskes: "RSUD SEHAT SELALU",
    lastUpdated: new Date().toISOString(),
    pesertaType: "PBI",
  },
  "0000000000000": {
    cardNumber: "0000000000000",
    status: "inactive",
    statusDate: "2026-01-10",
    eligibilityDate: "2024-12-31",
    faskes: "PUSKESMAS JAYA (KODE: 87654321)",
    faskesCode: "87654321",
    currentFaskes: "RSUD SEHAT SELALU",
    lastUpdated: new Date().toISOString(),
    pesertaType: "Non-PBI",
  },
  "1111111111111": {
    cardNumber: "1111111111111",
    status: "expired",
    statusDate: "2024-12-31",
    eligibilityDate: "2024-12-31",
    faskes: "RSUD SEHAT SELALU (KODE: 12345678)",
    faskesCode: "12345678",
    currentFaskes: "RSUD SEHAT SELALU",
    lastUpdated: new Date().toISOString(),
    pesertaType: "PBPU",
  },
  "2222222222222": {
    cardNumber: "2222222222222",
    status: "suspended",
    statusDate: "2026-01-15",
    eligibilityDate: "2026-06-30",
    faskes: "KLINIK PRATAMA (KODE: 11223344)",
    faskesCode: "11223344",
    currentFaskes: "RSUD SEHAT SELALU",
    lastUpdated: new Date().toISOString(),
    pesertaType: "Pegawai Negeri",
  },
};

// ============================================================================
// STATUS BADGE COMPONENT
// ============================================================================

/**
 * BPJSStatusBadge Component
 *
 * Displays BPJS membership status with appropriate styling:
 * - Active: Green with check icon
 * - Inactive: Red with X icon
 * - Expired: Gray with clock icon
 * - Suspended: Yellow with alert icon
 */
export function BPJSStatusBadge({
  status,
  showIcon = true,
  showLabel = true,
  size = "md",
  className = "",
}: BPJSStatusBadgeProps) {
  const getStatusConfig = () => {
    switch (status) {
      case "active":
        return {
          variant: "success" as const,
          icon: <CheckCircle className="w-4 h-4" />,
          label: "Aktif",
          bgClass: "bg-green-100",
          textClass: "text-green-700",
          borderClass: "border-green-300",
        };
      case "inactive":
        return {
          variant: "error" as const,
          icon: <XCircle className="w-4 h-4" />,
          label: "Tidak Aktif",
          bgClass: "bg-red-100",
          textClass: "text-red-700",
          borderClass: "border-red-300",
        };
      case "expired":
        return {
          variant: "neutral" as const,
          icon: <Clock className="w-4 h-4" />,
          label: "Kadaluarsa",
          bgClass: "bg-gray-100",
          textClass: "text-gray-700",
          borderClass: "border-gray-300",
        };
      case "suspended":
        return {
          variant: "warning" as const,
          icon: <AlertCircle className="w-4 h-4" />,
          label: "Ditangguhkan",
          bgClass: "bg-yellow-100",
          textClass: "text-yellow-700",
          borderClass: "border-yellow-300",
        };
      default:
        return {
          variant: "neutral" as const,
          icon: <Info className="w-4 h-4" />,
          label: "Tidak Diketahui",
          bgClass: "bg-gray-100",
          textClass: "text-gray-700",
          borderClass: "border-gray-300",
        };
    }
  };

  const config = getStatusConfig();
  const sizeClasses = {
    sm: "px-2 py-1 text-xs",
    md: "px-3 py-1.5 text-sm",
    lg: "px-4 py-2 text-base",
  };

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 rounded-full border-2
        ${config.bgClass} ${config.textClass} ${config.borderClass}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      {showIcon && config.icon}
      {showLabel && <span className="font-medium">{config.label}</span>}
    </span>
  );
}

BPJSStatusBadge.displayName = "BPJSStatusBadge";

// ============================================================================
// PESERTA TYPE BADGE COMPONENT
// ============================================================================

/**
 * BPJSPesertaBadge Component
 *
 * Displays BPJS participant type (PBI, Non-PBI, etc.) with appropriate styling
 */
export function BPJSPesertaBadge({
  pesertaType,
  size = "md",
  className = "",
}: BPJSPesertaBadgeProps) {
  const getPesertaConfig = () => {
    switch (pesertaType) {
      case "PBI":
        return {
          bgClass: "bg-blue-100",
          textClass: "text-blue-700",
          borderClass: "border-blue-300",
          label: "Penerima Bantuan Iuran (PBI)",
          shortLabel: "PBI",
        };
      case "Non-PBI":
        return {
          bgClass: "bg-purple-100",
          textClass: "text-purple-700",
          borderClass: "border-purple-300",
          label: "Non-PBI (Mandiri)",
          shortLabel: "Non-PBI",
        };
      case "PBPU":
        return {
          bgClass: "bg-indigo-100",
          textClass: "text-indigo-700",
          borderClass: "border-indigo-300",
          label: "Penerima Bantuan Partial",
          shortLabel: "PBPU",
        };
      case "Pegawai Negeri":
        return {
          bgClass: "bg-teal-100",
          textClass: "text-teal-700",
          borderClass: "border-teal-300",
          label: "Pegawai Negeri",
          shortLabel: "PNS",
        };
      case "Pensiunan":
        return {
          bgClass: "bg-amber-100",
          textClass: "text-amber-700",
          borderClass: "border-amber-300",
          label: "Pensiunan",
          shortLabel: "Pensiunan",
        };
      default:
        return {
          bgClass: "bg-gray-100",
          textClass: "text-gray-700",
          borderClass: "border-gray-300",
          label: "Tidak Diketahui",
          shortLabel: "Unknown",
        };
    }
  };

  const config = getPesertaConfig();
  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-3 py-1 text-sm",
    lg: "px-4 py-1.5 text-base",
  };

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 rounded-full border
        ${config.bgClass} ${config.textClass} ${config.borderClass}
        ${sizeClasses[size]}
        ${className}
      `}
      title={config.label}
    >
      <span className="font-medium">{config.shortLabel}</span>
    </span>
  );
}

BPJSPesertaBadge.displayName = "BPJSPesertaBadge";

// ============================================================================
// FASKES INDICATOR COMPONENT
// ============================================================================

/**
 * FaskesIndicator Component
 *
 * Displays BPJS faskes (health facility) eligibility status:
 * - Shows if patient's registered faskes matches current facility
 * - Visual indicator for eligible/ineligible status
 * - Optional detailed view with faskes names
 */
export function FaskesIndicator({
  eligible,
  currentFaskes,
  registeredFaskes,
  showDetails = false,
  className = "",
}: FaskesIndicatorProps) {
  return (
    <div className={`rounded-lg border p-3 ${eligible ? "bg-green-50 border-green-200" : "bg-yellow-50 border-yellow-200"} ${className}`}>
      <div className="flex items-center gap-2">
        {eligible ? (
          <>
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-green-700">Faskes Sesuai</span>
          </>
        ) : (
          <>
            <AlertCircle className="w-5 h-5 text-yellow-600" />
            <span className="text-sm font-medium text-yellow-700">Faskes Tidak Sesuai</span>
          </>
        )}
      </div>

      {showDetails && (
        <div className="mt-2 space-y-1 text-xs">
          <div className="flex items-start gap-2">
            <span className="text-gray-500 min-w-[80px]">Faskes Terdaftar:</span>
            <span className="text-gray-900 font-medium">{registeredFaskes}</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-gray-500 min-w-[80px]">Faskes Saat Ini:</span>
            <span className="text-gray-900 font-medium">{currentFaskes}</span>
          </div>
        </div>
      )}

      {!eligible && (
        <p className="mt-2 text-xs text-yellow-600">
          Pasien terdaftar di faskes lain. Untuk pelayanan di RS ini, diperlukan rujukan.
        </p>
      )}
    </div>
  );
}

FaskesIndicator.displayName = "FaskesIndicator";

// ============================================================================
// STATUS CARD COMPONENT
// ============================================================================

/**
 * BPJSStatusCard Component
 *
 * Comprehensive card showing detailed BPJS status information with:
 * - Status badge with icon
 * - Key information (card number, faskes, dates)
 * - Last updated timestamp
 * - Optional refresh button
 * - Optional auto-refresh
 */
export function BPJSStatusCard({
  data,
  onRefresh,
  autoRefresh = false,
  refreshInterval = 60000, // 1 minute default
  className = "",
}: BPJSStatusCardProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date(data.lastUpdated));

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(async () => {
      if (onRefresh) {
        await handleRefresh();
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, onRefresh]);

  const handleRefresh = async () => {
    if (!onRefresh || isRefreshing) return;

    setIsRefreshing(true);
    try {
      await onRefresh();
      setLastUpdate(new Date());
    } finally {
      setIsRefreshing(false);
    }
  };

  const getStatusMessage = () => {
    switch (data.status) {
      case "active":
        return "Kartu BPJS aktif dan dapat digunakan untuk pelayanan.";
      case "inactive":
        return "Kartu BPJS tidak aktif. Silakan hubungi kantor BPJS.";
      case "expired":
        return "Masa berlaku kartu BPJS telah habis. Silakan perpanjang.";
      case "suspended":
        return "Keanggotaan BPJS ditangguhkan sementara.";
      default:
        return "Status kartu tidak dapat ditentukan.";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("id-ID", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  };

  return (
    <div className={`bg-white rounded-lg shadow border-2 ${getBorderClass(data.status)} ${className}`}>
      {/* Header with Status Badge */}
      <div className={`p-4 border-b ${getBgClass(data.status)}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getStatusIcon(data.status)}
            <div>
              <h3 className="font-semibold text-gray-900">Status BPJS</h3>
              <p className={`text-sm ${getTextClass(data.status)}`}>{getStatusMessage()}</p>
            </div>
          </div>
          {onRefresh && (
            <button
              type="button"
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="p-2 hover:bg-white/50 rounded-full transition-colors disabled:opacity-50"
              title="Refresh status"
            >
              <RefreshCw className={`w-5 h-5 ${getTextClass(data.status)} ${isRefreshing ? "animate-spin" : ""}`} />
            </button>
          )}
        </div>
      </div>

      {/* Status Badge */}
      <div className="px-4 py-3">
        <BPJSStatusBadge status={data.status} size="lg" className="w-full justify-center" />
      </div>

      {/* Information */}
      <div className="p-4 space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <InfoRow label="Nomor Kartu" value={data.cardNumber} />
          <InfoRow label="Faskes" value={data.faskes} />
          <InfoRow label="Tanggal Status" value={formatDate(data.statusDate)} />
          <InfoRow label="Berlaku Hingga" value={formatDate(data.eligibilityDate)} />
        </div>

        {/* Last Updated */}
        <div className="pt-3 border-t border-gray-200">
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Clock className="w-3 h-3" />
            <span>
              Terakhir diperbarui:{" "}
              {lastUpdate.toLocaleTimeString("id-ID", {
                hour: "2-digit",
                minute: "2-digit",
              })}
              {autoRefresh && " (Auto-refresh aktif)"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

BPJSStatusCard.displayName = "BPJSStatusCard";

// ============================================================================
// AUTO STATUS INDICATOR COMPONENT
// ============================================================================

/**
 * BPJSStatusIndicator Component
 *
 * Fully automated BPJS status indicator with:
 * - Fetches status by card number
 * - Real-time updates with polling
 * - Status change callbacks
 * - Loading and error states
 */
export function BPJSStatusIndicator({
  cardNumber,
  autoRefresh = true,
  refreshInterval = 60000,
  onStatusChange,
  className = "",
}: BPJSStatusIndicatorProps) {
  const [status, setStatus] = useState<BPJSStatusData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!cardNumber) return;

    setIsLoading(true);
    setError(null);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Mock response
      const mockData = mockBPJSStatus[cardNumber] || {
        cardNumber,
        status: "active",
        statusDate: new Date().toISOString().split("T")[0],
        eligibilityDate: "2026-12-31",
        faskes: "RSUD SEHAT SELALU (KODE: 12345678)",
        lastUpdated: new Date().toISOString(),
      };

      setStatus(mockData);
      onStatusChange?.(mockData);
    } catch (err) {
      setError("Gagal mengambil status BPJS");
    } finally {
      setIsLoading(false);
    }
  }, [cardNumber, onStatusChange]);

  // Initial fetch
  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchStatus, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchStatus]);

  if (isLoading) {
    return (
      <div className={`bg-gray-50 rounded-lg p-6 text-center ${className}`}>
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div>
        <p className="text-sm text-gray-600 mt-3">Memeriksa status BPJS...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center gap-2 text-red-700">
          <XCircle className="w-5 h-5" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      </div>
    );
  }

  if (!status) {
    return null;
  }

  return (
    <BPJSStatusCard
      data={status}
      onRefresh={fetchStatus}
      autoRefresh={autoRefresh}
      refreshInterval={refreshInterval}
      className={className}
    />
  );
}

BPJSStatusIndicator.displayName = "BPJSStatusIndicator";

// ============================================================================
// HELPER COMPONENTS
// ============================================================================

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-medium text-gray-900 truncate" title={value}>
        {value}
      </p>
    </div>
  );
}

function getStatusIcon(status: BPJSStatus) {
  switch (status) {
    case "active":
      return <div className="p-2 bg-green-100 rounded-lg"><CheckCircle className="w-6 h-6 text-green-600" /></div>;
    case "inactive":
      return <div className="p-2 bg-red-100 rounded-lg"><XCircle className="w-6 h-6 text-red-600" /></div>;
    case "expired":
      return <div className="p-2 bg-gray-100 rounded-lg"><Clock className="w-6 h-6 text-gray-600" /></div>;
    case "suspended":
      return <div className="p-2 bg-yellow-100 rounded-lg"><AlertCircle className="w-6 h-6 text-yellow-600" /></div>;
    default:
      return <div className="p-2 bg-gray-100 rounded-lg"><Info className="w-6 h-6 text-gray-600" /></div>;
  }
}

function getBorderClass(status: BPJSStatus): string {
  switch (status) {
    case "active": return "border-green-500";
    case "inactive": return "border-red-500";
    case "expired": return "border-gray-400";
    case "suspended": return "border-yellow-500";
    default: return "border-gray-300";
  }
}

function getBgClass(status: BPJSStatus): string {
  switch (status) {
    case "active": return "bg-green-50";
    case "inactive": return "bg-red-50";
    case "expired": return "bg-gray-50";
    case "suspended": return "bg-yellow-50";
    default: return "bg-gray-50";
  }
}

function getTextClass(status: BPJSStatus): string {
  switch (status) {
    case "active": return "text-green-700";
    case "inactive": return "text-red-700";
    case "expired": return "text-gray-700";
    case "suspended": return "text-yellow-700";
    default: return "text-gray-700";
  }
}

// ============================================================================
// REACT HOOK
// ============================================================================

/**
 * useBPJSStatus Hook
 *
 * Custom hook for managing BPJS status with polling
 */
export function useBPJSStatus(
  cardNumber: string,
  options: {
    autoRefresh?: boolean;
    refreshInterval?: number;
    onStatusChange?: (status: BPJSStatusData) => void;
  } = {}
) {
  const { autoRefresh = true, refreshInterval = 60000, onStatusChange } = options;
  const [status, setStatus] = useState<BPJSStatusData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!cardNumber) return;

    setIsLoading(true);
    setError(null);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));

      const mockData = mockBPJSStatus[cardNumber] || {
        cardNumber,
        status: "active",
        statusDate: new Date().toISOString().split("T")[0],
        eligibilityDate: "2026-12-31",
        faskes: "RSUD SEHAT SELALU (KODE: 12345678)",
        lastUpdated: new Date().toISOString(),
      };

      setStatus(mockData);
      onStatusChange?.(mockData);
    } catch (err) {
      setError("Gagal mengambil status BPJS");
    } finally {
      setIsLoading(false);
    }
  }, [cardNumber, onStatusChange]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchStatus, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchStatus]);

  return {
    status,
    isLoading,
    error,
    refetch: fetchStatus,
  };
}
