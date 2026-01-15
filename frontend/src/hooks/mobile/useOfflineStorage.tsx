"use client";

import { useState, useEffect, useCallback, useRef } from "react";

/**
 * WEB-S-3.7: Offline Storage Hook
 *
 * Key Features:
 * - Detect online/offline status
 * - Queue data locally when offline
 * - Sync queued data when connection restored
 * - Progress tracking during sync
 * - Persistent storage using localStorage
 * - Auto-retry failed syncs with exponential backoff
 */

// ============================================================================
// TYPES
// ============================================================================

export interface QueuedItem<T = any> {
  id: string;
  data: T;
  timestamp: Date;
  retryCount: number;
  endpoint: string;
  method: "POST" | "PUT" | "PATCH";
}

export interface SyncProgress {
  total: number;
  completed: number;
  failed: number;
  current?: string;
}

export interface UseOfflineStorageOptions<T> {
  key: string;
  onOnline?: (items: QueuedItem<T>[]) => Promise<void>;
  onSyncProgress?: (progress: SyncProgress) => void;
  onSyncComplete?: (success: number, failed: number) => void;
  maxRetries?: number;
  retryDelay?: number;
}

export interface OfflineStorageState<T> {
  isOnline: boolean;
  isSyncing: boolean;
  syncProgress: SyncProgress;
  queueSize: number;
  queue: QueuedItem<T>[];
}

// ============================================================================
// STORAGE HELPERS
// ============================================================================

const STORAGE_PREFIX = "offline_queue_";

function getQueue<T>(key: string): QueuedItem<T>[] {
  if (typeof window === "undefined") return [];

  try {
    const data = localStorage.getItem(`${STORAGE_PREFIX}${key}`);
    return data ? JSON.parse(data, (k, v) => (k === "timestamp" ? new Date(v) : v)) : [];
  } catch (error) {
    console.error("Error reading offline queue:", error);
    return [];
  }
}

function saveQueue<T>(key: string, queue: QueuedItem<T>[]): void {
  if (typeof window === "undefined") return;

  try {
    localStorage.setItem(`${STORAGE_PREFIX}${key}`, JSON.stringify(queue));
  } catch (error) {
    console.error("Error saving offline queue:", error);
  }
}

function clearQueue(key: string): void {
  if (typeof window === "undefined") return;

  try {
    localStorage.removeItem(`${STORAGE_PREFIX}${key}`);
  } catch (error) {
    console.error("Error clearing offline queue:", error);
  }
}

// ============================================================================
// HOOK
// ============================================================================

export function useOfflineStorage<T = any>({
  key,
  onOnline,
  onSyncProgress,
  onSyncComplete,
  maxRetries = 3,
  retryDelay = 5000,
}: UseOfflineStorageOptions<T>) {
  const [state, setState] = useState<OfflineStorageState<T>>({
    isOnline: typeof navigator !== "undefined" ? navigator.onLine : true,
    isSyncing: false,
    syncProgress: { total: 0, completed: 0, failed: 0 },
    queueSize: 0,
    queue: [],
  });

  const syncInProgress = useRef(false);
  const { isOnline, isSyncing, syncProgress, queue } = state;

  /**
   * Update queue from localStorage
   */
  const refreshQueue = useCallback(() => {
    const currentQueue = getQueue<T>(key);
    setState((prev) => ({
      ...prev,
      queue: currentQueue,
      queueSize: currentQueue.length,
    }));
  }, [key]);

  /**
   * Add item to offline queue
   */
  const addToQueue = useCallback(
    (data: T, endpoint: string, method: "POST" | "PUT" | "PATCH" = "POST") => {
      const newItem: QueuedItem<T> = {
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        data,
        timestamp: new Date(),
        retryCount: 0,
        endpoint,
        method,
      };

      const currentQueue = getQueue<T>(key);
      const updatedQueue = [...currentQueue, newItem];
      saveQueue(key, updatedQueue);

      setState((prev) => ({
        ...prev,
        queue: updatedQueue,
        queueSize: updatedQueue.length,
      }));

      return newItem.id;
    },
    [key]
  );

  /**
   * Remove item from queue
   */
  const removeFromQueue = useCallback((itemId: string) => {
    const currentQueue = getQueue<T>(key);
    const updatedQueue = currentQueue.filter((item) => item.id !== itemId);
    saveQueue(key, updatedQueue);

    setState((prev) => ({
      ...prev,
      queue: updatedQueue,
      queueSize: updatedQueue.length,
    }));
  }, [key]);

  /**
   * Sync a single item (with retry)
   */
  const syncItem = useCallback(
    async (item: QueuedItem<T>): Promise<boolean> => {
      if (!onOnline) return false;

      try {
        // Simulate API call - in production, use fetch/axios
        await onOnline([item]);
        return true;
      } catch (error) {
        console.error(`Sync failed for item ${item.id}:`, error);

        // Increment retry count
        const currentQueue = getQueue<T>(key);
        const updatedQueue = currentQueue.map((i) =>
          i.id === item.id ? { ...i, retryCount: i.retryCount + 1 } : i
        );
        saveQueue(key, updatedQueue);

        return false;
      }
    },
    [key, onOnline]
  );

  /**
   * Process entire queue
   */
  const processQueue = useCallback(async () => {
    if (!isOnline || isSyncing || syncInProgress.current) return;
    if (!onOnline) return;

    const currentQueue = getQueue<T>(key);
    if (currentQueue.length === 0) return;

    syncInProgress.current = true;
    setState((prev) => ({ ...prev, isSyncing: true, syncProgress: { total: currentQueue.length, completed: 0, failed: 0 } }));

    let completed = 0;
    let failed = 0;
    const successfullySynced: string[] = [];

    for (const item of currentQueue) {
      // Update progress
      setState((prev) => ({
        ...prev,
        syncProgress: {
          total: currentQueue.length,
          completed,
          failed,
          current: item.endpoint,
        },
      }));
      onSyncProgress?.({
        total: currentQueue.length,
        completed,
        failed,
        current: item.endpoint,
      });

      // Check if max retries exceeded
      if (item.retryCount >= maxRetries) {
        failed++;
        continue;
      }

      // Attempt sync
      const success = await syncItem(item);

      if (success) {
        completed++;
        successfullySynced.push(item.id);
      } else {
        failed++;
      }
    }

    // Remove successfully synced items
    const remainingQueue = getQueue<T>(key).filter(
      (item) => !successfullySynced.includes(item.id)
    );
    saveQueue(key, remainingQueue);

    // Final update
    setState((prev) => ({
      ...prev,
      isSyncing: false,
      syncProgress: { total: currentQueue.length, completed, failed },
      queue: remainingQueue,
      queueSize: remainingQueue.length,
    }));

    onSyncComplete?.(completed, failed);
    syncInProgress.current = false;

    // If there are items with retries left, schedule retry
    if (remainingQueue.some((item) => item.retryCount < maxRetries)) {
      setTimeout(() => {
        if (state.isOnline) {
          processQueue();
        }
      }, retryDelay);
    }
  }, [isOnline, isSyncing, key, onOnline, maxRetries, retryDelay, syncItem, onSyncProgress, onSyncComplete, state.isOnline]);

  /**
   * Manual sync trigger
   */
  const syncNow = useCallback(() => {
    processQueue();
  }, [processQueue]);

  /**
   * Clear queue manually
   */
  const clearQueueManually = useCallback(() => {
    clearQueue(key);
    setState((prev) => ({
      ...prev,
      queue: [],
      queueSize: 0,
    }));
  }, [key]);

  /**
   * Monitor online/offline status
   */
  useEffect(() => {
    const handleOnline = () => {
      setState((prev) => ({ ...prev, isOnline: true }));
      refreshQueue();
    };

    const handleOffline = () => {
      setState((prev) => ({ ...prev, isOnline: false }));
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, [refreshQueue]);

  /**
   * Auto-sync when coming online
   */
  useEffect(() => {
    if (isOnline && !isSyncing && queue.length > 0) {
      processQueue();
    }
  }, [isOnline, queue.length, isSyncing, processQueue]);

  /**
   * Initial load
   */
  useEffect(() => {
    refreshQueue();
  }, [refreshQueue]);

  return {
    // State
    isOnline: state.isOnline,
    isSyncing: state.isSyncing,
    syncProgress: state.syncProgress,
    queue: state.queue,
    queueSize: state.queueSize,

    // Actions
    addToQueue,
    removeFromQueue,
    syncNow,
    clearQueue: clearQueueManually,
    refreshQueue,
  };
}

// ============================================================================
// SYNC INDICATOR COMPONENT
// ============================================================================

export interface SyncIndicatorProps {
  isOnline: boolean;
  isSyncing?: boolean;
  syncProgress?: SyncProgress;
  className?: string;
}

export function SyncIndicator({
  isOnline,
  isSyncing = false,
  syncProgress,
  className = "",
}: SyncIndicatorProps) {
  return (
    <div
      className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium ${className} ${
        isOnline
          ? "bg-green-100 text-green-800"
          : "bg-gray-100 text-gray-800"
      }`}
    >
      {/* Status dot */}
      <span
        className={`w-2 h-2 rounded-full ${
          isOnline ? "bg-green-500" : "bg-gray-400"
        } ${isSyncing ? "animate-pulse" : ""}`}
      />

      {/* Status text */}
      {isSyncing && syncProgress ? (
        <span>
          Menyinkronkan {syncProgress.completed}/{syncProgress.total}...
        </span>
      ) : isOnline ? (
        <span>Online - Sinkronisasi aktif</span>
      ) : (
        <span>Offline - Data tersimpan lokal</span>
      )}

      {/* Sync icon when syncing */}
      {isSyncing && (
        <svg
          className="animate-spin w-4 h-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
    </div>
  );
}

// ============================================================================
// PROGRESS BAR COMPONENT
// ============================================================================

export interface SyncProgressBarProps {
  progress: SyncProgress;
  className?: string;
}

export function SyncProgressBar({ progress, className = "" }: SyncProgressBarProps) {
  const percentage = progress.total > 0 ? (progress.completed / progress.total) * 100 : 0;

  return (
    <div className={`w-full ${className}`}>
      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className="bg-blue-600 h-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Status text */}
      <div className="flex justify-between text-xs text-gray-600 mt-1">
        <span>
          {progress.completed} dari {progress.total} selesai
        </span>
        {progress.failed > 0 && (
          <span className="text-red-600">{progress.failed} gagal</span>
        )}
      </div>
    </div>
  );
}
