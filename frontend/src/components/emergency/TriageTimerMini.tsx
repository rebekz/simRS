"use client";

import React, { useState, useEffect, useCallback, useRef } from 'react';

export interface TriageTimerMiniProps {
  /**
   * Initial time in seconds
   */
  initialTime?: number;
  /**
   * Warning threshold in seconds (default: 90)
   */
  warningThreshold?: number;
  /**
   * Critical threshold in seconds (default: 120)
   */
  criticalThreshold?: number;
  /**
   * Whether timer is running
   */
  isRunning?: boolean;
  /**
   * Show label
   */
  showLabel?: boolean;
}

type TimerState = 'idle' | 'running' | 'paused' | 'warning' | 'critical';

/**
 * TriageTimerMini Component
 *
 * A compact timer for display in headers, navbars, or status bars.
 * Shows color-coded status with minimal visual footprint.
 */
export const TriageTimerMini: React.FC<TriageTimerMiniProps> = ({
  initialTime = 0,
  warningThreshold = 90,
  criticalThreshold = 120,
  isRunning = false,
  showLabel = true,
}) => {
  const [time, setTime] = useState(initialTime);
  const [running, setRunning] = useState(isRunning);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Determine timer state
  const getTimerState = useCallback((): TimerState => {
    if (!running && time === 0) return 'idle';
    if (time >= criticalThreshold) return 'critical';
    if (time >= warningThreshold) return 'warning';
    if (running) return 'running';
    return 'paused';
  }, [time, running, warningThreshold, criticalThreshold]);

  const timerState = getTimerState();

  // Timer logic
  useEffect(() => {
    if (running) {
      intervalRef.current = setInterval(() => {
        setTime((prevTime) => prevTime + 1);
      }, 1000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [running]);

  // Sync with external isRunning prop
  useEffect(() => {
    setRunning(isRunning);
  }, [isRunning]);

  // Format time as MM:SS
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // State-based styling
  const getStateClasses = (): string => {
    switch (timerState) {
      case 'critical':
        return 'bg-red-600 text-white animate-pulse';
      case 'warning':
        return 'bg-yellow-500 text-white';
      case 'running':
        return 'bg-green-600 text-white';
      case 'paused':
        return 'bg-gray-500 text-white';
      default:
        return 'bg-gray-200 text-gray-700';
    }
  };

  const getStateIcon = (): string => {
    switch (timerState) {
      case 'critical':
        return '🚨';
      case 'warning':
        return '⚠️';
      case 'running':
        return '⏱️';
      case 'paused':
        return '⏸️';
      default:
        return '⏱️';
    }
  };

  return (
    <div
      className={`
        inline-flex items-center gap-2 px-3 py-1.5 rounded-lg
        ${getStateClasses()}
        transition-all duration-300
        font-mono font-bold text-sm
      `}
      role="timer"
      aria-label={`Triage timer: ${formatTime(time)}`}
    >
      <span className={timerState === 'critical' ? 'animate-bounce' : ''}>
        {getStateIcon()}
      </span>
      {showLabel && <span className="text-xs opacity-80">Triage:</span>}
      <span className="tabular-nums">{formatTime(time)}</span>
    </div>
  );
};

TriageTimerMini.displayName = 'TriageTimerMini';

export default TriageTimerMini;
