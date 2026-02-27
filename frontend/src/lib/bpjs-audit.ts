/**
 * BPJS Error Logging Utilities
 *
 * Provides error logging to audit system for all BPJS operations.
 */

import type { BPJSError } from './bpjs-errors';

// ============================================================================
// TYPES
// ============================================================================

export interface BPJSAuditLogEntry {
  id: string;
  timestamp: string;
  action: 'BPJS_VERIFY' | 'BPJS_SEP_CREATE' | 'BPJS_SEP_CANCEL' | 'BPJS_ERROR' | 'BPJS_MANUAL_ENTRY';
  resource: string;
  userId?: string;
  userName?: string;
  cardNumber?: string;
  details: {
    code?: string;
    message: string;
    type?: string;
    retryable?: boolean;
    retryAttempt?: number;
    [key: string]: unknown;
  };
  status: 'success' | 'error' | 'warning';
  ipAddress?: string;
  userAgent?: string;
}

export interface UseBPJSErrorLoggingOptions {
  userId?: string;
  userName?: string;
  autoLog?: boolean;
  onLog?: (entry: BPJSAuditLogEntry) => void;
}

// ============================================================================
// AUDIT LOG STORAGE (In-memory for demo, should use API in production)
// ============================================================================

let auditLogStore: BPJSAuditLogEntry[] = [];

/**
 * Get all audit log entries
 */
export function getBPJSAuditLogs(): BPJSAuditLogEntry[] {
  return [...auditLogStore].sort((a, b) =>
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
}

/**
 * Clear audit log (for testing)
 */
export function clearBPJSAuditLogs(): void {
  auditLogStore = [];
}

/**
 * Create audit log entry
 */
export function createBPJSAuditLog(
  action: BPJSAuditLogEntry['action'],
  resource: string,
  details: BPJSAuditLogEntry['details'],
  options: {
    cardNumber?: string;
    userId?: string;
    userName?: string;
    status?: BPJSAuditLogEntry['status'];
  } = {}
): BPJSAuditLogEntry {
  const entry: BPJSAuditLogEntry = {
    id: `audit-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date().toISOString(),
    action,
    resource,
    userId: options.userId || 'system',
    userName: options.userName || 'System',
    cardNumber: options.cardNumber,
    details,
    status: options.status || 'success',
    userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : 'server',
  };

  // Store in memory (in production, send to API)
  auditLogStore.push(entry);

  // Log to console for debugging
  console.log('[BPJS Audit]', entry.action, entry.status.toUpperCase(), entry);

  return entry;
}

/**
 * Log BPJS error to audit system
 */
export function logBPJSError(
  error: BPJSError,
  context: {
    cardNumber?: string;
    operation?: string;
    retryAttempt?: number;
    userId?: string;
    userName?: string;
  } = {}
): BPJSAuditLogEntry {
  return createBPJSAuditLog(
    'BPJS_ERROR',
    `BPJS:${context.cardNumber || 'unknown'}`,
    {
      code: error.code,
      message: error.message,
      type: error.type,
      retryable: error.retryable,
      operation: context.operation || 'unknown',
      retryAttempt: context.retryAttempt,
      suggestion: error.suggestion,
    },
    {
      cardNumber: context.cardNumber,
      userId: context.userId,
      userName: context.userName,
      status: 'error',
    }
  );
}

/**
 * Log successful BPJS verification
 */
export function logBPJSVerification(
  cardNumber: string,
  result: { success: boolean; nama?: string },
  options: { userId?: string; userName?: string } = {}
): BPJSAuditLogEntry {
  return createBPJSAuditLog(
    'BPJS_VERIFY',
    `BPJS:${cardNumber}`,
    {
      message: result.success
        ? `Verifikasi berhasil: ${result.nama}`
        : 'Verifikasi gagal',
      nama: result.nama,
      success: result.success,
    },
    {
      cardNumber,
      userId: options.userId,
      userName: options.userName,
      status: result.success ? 'success' : 'error',
    }
  );
}

/**
 * Log SEP creation
 */
export function logSEPCreation(
  sepNumber: string,
  cardNumber: string,
  details: {
    patientName: string;
    serviceType: string;
    polyclinic: string;
    doctorName?: string;
  },
  options: { userId?: string; userName?: string } = {}
): BPJSAuditLogEntry {
  return createBPJSAuditLog(
    'BPJS_SEP_CREATE',
    `SEP:${sepNumber}`,
    {
      message: `SEP berhasil dibuat untuk ${details.patientName}`,
      cardNumber,
      serviceType: details.serviceType,
      polyclinic: details.polyclinic,
      doctorName: details.doctorName,
    },
    {
      cardNumber,
      userId: options.userId,
      userName: options.userName,
      status: 'success',
    }
  );
}

/**
 * Log manual BPJS entry
 */
export function logBPJSManualEntry(
  cardNumber: string,
  reason: string,
  options: { userId?: string; userName?: string } = {}
): BPJSAuditLogEntry {
  return createBPJSAuditLog(
    'BPJS_MANUAL_ENTRY',
    `BPJS:${cardNumber}`,
    {
      message: `Entry manual: ${reason}`,
      reason,
      warning: 'Data entered manually without API verification',
    },
    {
      cardNumber,
      userId: options.userId,
      userName: options.userName,
      status: 'warning',
    }
  );
}

// ============================================================================
// REACT HOOK
// ============================================================================

/**
 * useBPJSErrorLogging Hook
 *
 * React hook for BPJS error logging with:
 * - Automatic error logging
 * - Audit trail management
 * - User context tracking
 */
export function useBPJSErrorLogging(options: UseBPJSErrorLoggingOptions = {}) {
  const { userId, userName, autoLog = true, onLog } = options;

  const logError = (
    error: BPJSError,
    context?: {
      cardNumber?: string;
      operation?: string;
      retryAttempt?: number;
    }
  ) => {
    const entry = logBPJSError(error, {
      ...context,
      userId,
      userName,
    });

    onLog?.(entry);
    return entry;
  };

  const logVerification = (
    cardNumber: string,
    result: { success: boolean; nama?: string }
  ) => {
    const entry = logBPJSVerification(cardNumber, result, { userId, userName });
    onLog?.(entry);
    return entry;
  };

  const logSEP = (
    sepNumber: string,
    cardNumber: string,
    details: {
      patientName: string;
      serviceType: string;
      polyclinic: string;
      doctorName?: string;
    }
  ) => {
    const entry = logSEPCreation(sepNumber, cardNumber, details, { userId, userName });
    onLog?.(entry);
    return entry;
  };

  const logManualEntry = (cardNumber: string, reason: string) => {
    const entry = logBPJSManualEntry(cardNumber, reason, { userId, userName });
    onLog?.(entry);
    return entry;
  };

  const getLogs = () => getBPJSAuditLogs();

  const clearLogs = () => clearBPJSAuditLogs();

  return {
    logError,
    logVerification,
    logSEP,
    logManualEntry,
    getLogs,
    clearLogs,
  };
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Format audit log entry for display
 */
export function formatAuditLogEntry(entry: BPJSAuditLogEntry): string {
  const timestamp = new Date(entry.timestamp).toLocaleString('id-ID');
  const status = entry.status.toUpperCase();
  return `[${timestamp}] ${entry.action} - ${status} - ${entry.details.message}`;
}

/**
 * Get audit log entries for a specific card number
 */
export function getAuditLogsByCard(cardNumber: string): BPJSAuditLogEntry[] {
  return auditLogStore.filter(entry => entry.cardNumber === cardNumber);
}

/**
 * Get audit log entries by action type
 */
export function getAuditLogsByAction(action: BPJSAuditLogEntry['action']): BPJSAuditLogEntry[] {
  return auditLogStore.filter(entry => entry.action === action);
}

/**
 * Export audit logs as JSON
 */
export function exportAuditLogsAsJSON(): string {
  return JSON.stringify(auditLogStore, null, 2);
}
