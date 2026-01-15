"use client";

import React, { useState, useEffect } from "react";
import { AlertCircle, XCircle, Info, RefreshCw, ChevronDown, ChevronUp, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { BPJSError, BPJSErrorType, ErrorSeverity, getErrorSeverity, translateError, isRetryableError, withRetry } from "@/lib/bpjs-errors";

// ============================================================================
// TYPES
// ============================================================================

export interface BPJSErrorDisplayProps {
  error: BPJSError | Error | unknown;
  onRetry?: () => Promise<void>;
  onDismiss?: () => void;
  showDetails?: boolean;
  className?: string;
}

export interface BPJSErrorAlertProps {
  error: BPJSError;
  onRetry?: () => Promise<void>;
  onDismiss?: () => void;
  showRetry?: boolean;
  className?: string;
}

export interface BPJSErrorRetryButtonProps {
  onRetry: () => Promise<void>;
  isRetrying?: boolean;
  className?: string;
}

// ============================================================================
// ERROR ALERT COMPONENT
// ============================================================================

/**
 * BPJSErrorAlert Component
 *
 * User-friendly error alert display for BPJS errors with:
 * - Color-coded by severity
 * - Clear title and message
 * - Actionable suggestion
 * - Optional retry button
 * - Optional dismiss button
 */
export function BPJSErrorAlert({
  error,
  onRetry,
  onDismiss,
  showRetry = true,
  className = "",
}: BPJSErrorAlertProps) {
  const [isRetrying, setIsRetrying] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const severity = getErrorSeverity(error);
  const canRetry = onRetry && isRetryableError(error);

  const handleRetry = async () => {
    if (!onRetry || isRetrying) return;

    setIsRetrying(true);
    try {
      await onRetry();
    } finally {
      setIsRetrying(false);
    }
  };

  const getSeverityClasses = () => {
    switch (severity) {
      case ErrorSeverity.CRITICAL:
      case ErrorSeverity.HIGH:
        return "bg-red-50 border-red-500 text-red-900";
      case ErrorSeverity.MEDIUM:
        return "bg-yellow-50 border-yellow-500 text-yellow-900";
      case ErrorSeverity.LOW:
        return "bg-blue-50 border-blue-500 text-blue-900";
      default:
        return "bg-gray-50 border-gray-500 text-gray-900";
    }
  };

  const getIcon = () => {
    switch (severity) {
      case ErrorSeverity.CRITICAL:
      case ErrorSeverity.HIGH:
        return <XCircle className="w-5 h-5 text-red-600" />;
      case ErrorSeverity.MEDIUM:
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case ErrorSeverity.LOW:
        return <Info className="w-5 h-5 text-blue-600" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-600" />;
    }
  };

  return (
    <div className={`border-2 rounded-lg ${getSeverityClasses()} ${className}`}>
      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-0.5">
            {getIcon()}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold">{error.title}</h4>
              {onDismiss && (
                <button
                  type="button"
                  onClick={onDismiss}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>

            <p className="text-sm mt-1">{error.message}</p>

            {/* Error Code (for debugging) */}
            <p className="text-xs mt-2 opacity-60">
              Kode Error: {error.code}
            </p>
          </div>
        </div>

        {/* Suggestion */}
        {error.suggestion && (
          <div className="mt-3 pl-8">
            <p className="text-sm font-medium">Saran:</p>
            <p className="text-sm mt-1">{error.suggestion}</p>
          </div>
        )}

        {/* Actions */}
        {(canRetry || error.userAction) && (
          <div className="mt-4 pl-8 flex items-center gap-3">
            {canRetry && showRetry && (
              <button
                type="button"
                onClick={handleRetry}
                disabled={isRetrying}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm font-medium"
              >
                <RefreshCw className={`w-4 h-4 ${isRetrying ? "animate-spin" : ""}`} />
                {isRetrying ? "Mencoba ulang..." : "Coba Lagi"}
              </button>
            )}

            {error.userAction && (
              <span className="text-sm">
                Tindakan: <span className="font-medium">{error.userAction}</span>
              </span>
            )}
          </div>
        )}

        {/* Details Toggle */}
        <button
          type="button"
          onClick={() => setShowDetails(!showDetails)}
          className="mt-3 pl-8 flex items-center gap-1 text-xs text-gray-600 hover:text-gray-900"
        >
          {showDetails ? (
            <>
              <ChevronUp className="w-3 h-3" />
              Sembunyikan detail
            </>
          ) : (
            <>
              <ChevronDown className="w-3 h-3" />
              Tampilkan detail
            </>
          )}
        </button>

        {/* Error Details */}
        {showDetails && (
          <div className="mt-3 pl-8 pr-4 pb-2">
            <div className="bg-white bg-opacity-50 rounded p-3 space-y-2 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <span className="font-medium">Kode:</span> {error.code}
                </div>
                <div>
                  <span className="font-medium">Tipe:</span> {error.type}
                </div>
                <div className="col-span-2">
                  <span className="font-medium">Retryable:</span>{" "}
                  {error.retryable ? "Ya" : "Tidak"}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

BPJSErrorAlert.displayName = "BPJSErrorAlert";

// ============================================================================
// ERROR DISPLAY WRAPPER COMPONENT
// ============================================================================

/**
 * BPJSErrorDisplay Component
 *
 * Wraps any error and displays it as a user-friendly BPJS error alert.
 * Automatically translates unknown errors to BPJS error format.
 */
export function BPJSErrorDisplay({
  error,
  onRetry,
  onDismiss,
  showDetails = false,
  className = "",
}: BPJSErrorDisplayProps) {
  const [translatedError, setTranslatedError] = useState<BPJSError | null>(null);

  useEffect(() => {
    if (error instanceof Error) {
      setTranslatedError(translateError(error));
    } else if (error && typeof error === "object" && "code" in error) {
      // Already a BPJSError
      setTranslatedError(error as BPJSError);
    } else {
      setTranslatedError({
        code: "9999",
        type: BPJSErrorType.UNKNOWN,
        title: "Kesalahan Sistem",
        message: String(error || "Terjadi kesalahan tidak diketahui."),
        suggestion: "Coba lagi atau hubungi administrator.",
        retryable: true,
        userAction: "Coba lagi",
      });
    }
  }, [error]);

  if (!translatedError) {
    return null;
  }

  return (
    <BPJSErrorAlert
      error={translatedError}
      onRetry={onRetry}
      onDismiss={onDismiss}
      showRetry={!!onRetry}
      className={className}
    />
  );
}

BPJSErrorDisplay.displayName = "BPJSErrorDisplay";

// ============================================================================
// RETRY BUTTON COMPONENT
// ============================================================================

/**
 * BPJSErrorRetryButton Component
 *
 * Standalone retry button for BPJS operations with:
 * - Loading state
 * - Attempt counter
 * - Auto-retry with exponential backoff
 */
export function BPJSErrorRetryButton({
  onRetry,
  isRetrying = false,
  className = "",
}: BPJSErrorRetryButtonProps) {
  const [attempt, setAttempt] = useState(0);
  const [nextRetryIn, setNextRetryIn] = useState<number | null>(null);

  const handleRetry = async () => {
    if (isRetrying) return;

    setAttempt(attempt + 1);
    await onRetry();
    setAttempt(0);
    setNextRetryIn(null);
  };

  return (
    <button
      type="button"
      onClick={handleRetry}
      disabled={isRetrying}
      className={`px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2 text-sm font-medium ${className}`}
    >
      <RefreshCw className={`w-4 h-4 ${isRetrying ? "animate-spin" : ""}`} />
      {isRetrying ? "Mencoba ulang..." : attempt > 0 ? `Coba Lagi ( Percobaan ${attempt + 1})` : "Coba Lagi"}
    </button>
  );
}

BPJSErrorRetryButton.displayName = "BPJSErrorRetryButton";

// ============================================================================
// TOAST NOTIFICATION COMPONENT
// ============================================================================

export interface BPJSErrorToastProps {
  error: BPJSError;
  onRetry?: () => Promise<void>;
  onDismiss: () => void;
  autoDismiss?: boolean;
  dismissAfter?: number; // milliseconds
}

/**
 * BPJSErrorToast Component
 *
 * Toast notification for BPJS errors with auto-dismiss.
 */
export function BPJSErrorToast({
  error,
  onRetry,
  onDismiss,
  autoDismiss = true,
  dismissAfter = 5000,
}: BPJSErrorToastProps) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    if (autoDismiss) {
      const timer = setTimeout(() => {
        setVisible(false);
        setTimeout(onDismiss, 300); // Wait for animation
      }, dismissAfter);

      return () => clearTimeout(timer);
    }
  }, [autoDismiss, dismissAfter, onDismiss]);

  const severity = getErrorSeverity(error);
  const canRetry = onRetry && isRetryableError(error);

  const getBgColor = () => {
    switch (severity) {
      case ErrorSeverity.CRITICAL:
      case ErrorSeverity.HIGH:
        return "bg-red-600";
      case ErrorSeverity.MEDIUM:
        return "bg-yellow-600";
      case ErrorSeverity.LOW:
        return "bg-blue-600";
      default:
        return "bg-gray-700";
    }
  };

  if (!visible) return null;

  return (
    <div className={`fixed top-4 right-4 max-w-md w-full shadow-lg rounded-lg ${getBgColor()} text-white z-50 transition-all duration-300`}>
      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <AlertCircle className="w-5 h-5" />
          </div>

          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-semibold">{error.title}</h4>
            <p className="text-sm mt-1 opacity-90">{error.message}</p>

            {canRetry && (
              <button
                type="button"
                onClick={onRetry}
                className="mt-2 px-3 py-1 bg-white bg-opacity-20 rounded hover:bg-opacity-30 text-xs font-medium flex items-center gap-1"
              >
                <RefreshCw className="w-3 h-3" />
                Coba Lagi
              </button>
            )}
          </div>

          <button
            type="button"
            onClick={() => {
              setVisible(false);
              setTimeout(onDismiss, 300);
            }}
            className="flex-shrink-0 opacity-70 hover:opacity-100"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

BPJSErrorToast.displayName = "BPJSErrorToast";

// ============================================================================
// REACT HOOK
// ============================================================================

/**
 * useBPJSErrorRetry Hook
 *
 * Custom hook for managing BPJS error retries with:
 * - Exponential backoff
 * - Attempt tracking
 * - Loading state
 */
export function useBPJSErrorRetry<T>(
  fn: () => Promise<T>,
  options: {
    maxAttempts?: number;
    initialDelay?: number;
    onSuccess?: (result: T) => void;
    onError?: (error: BPJSError) => void;
  } = {}
) {
  const { maxAttempts = 3, onSuccess, onError } = options;

  const [isRetrying, setIsRetrying] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [error, setError] = useState<BPJSError | null>(null);

  const execute = async (): Promise<T | null> => {
    setIsRetrying(true);
    setError(null);

    try {
      const result = await withRetry(fn, { maxAttempts });
      setAttempt(0);
      onSuccess?.(result);
      return result;
    } catch (err) {
      const bpjsError = err instanceof Error ? translateError(err) : err as BPJSError;
      setError(bpjsError);
      onError?.(bpjsError);
      return null;
    } finally {
      setIsRetrying(false);
    }
  };

  const reset = () => {
    setAttempt(0);
    setError(null);
    setIsRetrying(false);
  };

  return {
    execute,
    isRetrying,
    attempt,
    error,
    reset,
  };
}

// ============================================================================
// ERROR BOUNDARY COMPONENT
// ============================================================================

export interface BPJSErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: (error: BPJSError, retry: () => void) => React.ReactNode;
}

interface BPJSErrorBoundaryState {
  error: BPJSError | null;
}

/**
 * BPJSErrorBoundary Component
 *
 * Catches errors in BPJS-related components and displays user-friendly error messages.
 */
export class BPJSErrorBoundary extends React.Component<
  BPJSErrorBoundaryProps,
  BPJSErrorBoundaryState
> {
  constructor(props: BPJSErrorBoundaryProps) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error: Error): BPJSErrorBoundaryState {
    return { error: translateError(error) };
  }

  handleRetry = () => {
    this.setState({ error: null });
  };

  render() {
    if (this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleRetry);
      }

      return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
          <div className="max-w-md w-full p-6">
            <BPJSErrorAlert
              error={this.state.error}
              onRetry={async () => {
                this.handleRetry();
                window.location.reload();
              }}
            />
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
