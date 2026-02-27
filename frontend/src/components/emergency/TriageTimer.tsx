"use client";

import React, { useState, useEffect, useCallback, useRef } from 'react';

export interface TriageTimerProps {
  /**
   * Initial time in seconds (default: 0)
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
   * Callback when timer starts
   */
  onStart?: () => void;
  /**
   * Callback when timer pauses
   */
  onPause?: () => void;
  /**
   * Callback when timer resets
   */
  onReset?: () => void;
  /**
   * Callback when warning threshold is reached
   */
  onWarning?: () => void;
  /**
   * Callback when critical threshold is reached
   */
  onCritical?: () => void;
  /**
   * Size variant
   */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /**
   * Show controls (start/pause/reset buttons)
   */
  showControls?: boolean;
  /**
   * Auto-start on mount
   */
  autoStart?: boolean;
  /**
   * Label text
   */
  label?: string;
}

type TimerState = 'idle' | 'running' | 'paused' | 'warning' | 'critical';

/**
 * TriageTimer Component
 *
 * A prominent timer for emergency triage that ensures triage completes in <2 minutes.
 * Visual warnings at 90 seconds (yellow) and critical alert at 120 seconds (red).
 *
 * Features:
 * - Large, prominent display
 * - Color-coded status (green/yellow/red)
 * - Audio alert at critical threshold
 * - Pause/resume functionality
 * - Visual pulse effect when critical
 */
export const TriageTimer: React.FC<TriageTimerProps> = ({
  initialTime = 0,
  warningThreshold = 90,
  criticalThreshold = 120,
  isRunning: externalIsRunning,
  onStart,
  onPause,
  onReset,
  onWarning,
  onCritical,
  size = 'lg',
  showControls = true,
  autoStart = false,
  label = 'Waktu Triage',
}) => {
  const [time, setTime] = useState(initialTime);
  const [isRunning, setIsRunning] = useState(autoStart || externalIsRunning || false);
  const [hasWarned, setHasWarned] = useState(false);
  const [hasCritical, setHasCritical] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  // Determine timer state based on time
  const getTimerState = useCallback((): TimerState => {
    if (!isRunning && time === 0) return 'idle';
    if (time >= criticalThreshold) return 'critical';
    if (time >= warningThreshold) return 'warning';
    if (isRunning) return 'running';
    return 'paused';
  }, [time, isRunning, warningThreshold, criticalThreshold]);

  const timerState = getTimerState();

  // Play audio alert
  const playAlert = useCallback((type: 'warning' | 'critical') => {
    if (typeof window === 'undefined') return;

    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }

      const ctx = audioContextRef.current;
      const oscillator = ctx.createOscillator();
      const gainNode = ctx.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(ctx.destination);

      if (type === 'warning') {
        // Single beep for warning
        oscillator.frequency.value = 600;
        oscillator.type = 'sine';
        gainNode.gain.setValueAtTime(0.3, ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
        oscillator.start(ctx.currentTime);
        oscillator.stop(ctx.currentTime + 0.3);
      } else {
        // Double beep for critical
        oscillator.frequency.value = 800;
        oscillator.type = 'square';
        gainNode.gain.setValueAtTime(0.4, ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);
        oscillator.start(ctx.currentTime);
        oscillator.stop(ctx.currentTime + 0.15);

        // Second beep
        setTimeout(() => {
          if (!audioContextRef.current) return;
          const osc2 = audioContextRef.current.createOscillator();
          const gain2 = audioContextRef.current.createGain();
          osc2.connect(gain2);
          gain2.connect(audioContextRef.current.destination);
          osc2.frequency.value = 800;
          osc2.type = 'square';
          gain2.gain.setValueAtTime(0.4, audioContextRef.current.currentTime);
          gain2.gain.exponentialRampToValueAtTime(0.01, audioContextRef.current.currentTime + 0.15);
          osc2.start(audioContextRef.current.currentTime);
          osc2.stop(audioContextRef.current.currentTime + 0.15);
        }, 200);
      }
    } catch (e) {
      console.warn('Audio alert failed:', e);
    }
  }, []);

  // Timer logic
  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(() => {
        setTime((prevTime) => {
          const newTime = prevTime + 1;

          // Check thresholds
          if (newTime === warningThreshold && !hasWarned) {
            setHasWarned(true);
            playAlert('warning');
            onWarning?.();
          }

          if (newTime === criticalThreshold && !hasCritical) {
            setHasCritical(true);
            playAlert('critical');
            onCritical?.();
          }

          return newTime;
        });
      }, 1000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRunning, warningThreshold, criticalThreshold, hasWarned, hasCritical, playAlert, onWarning, onCritical]);

  // Sync with external isRunning prop
  useEffect(() => {
    if (externalIsRunning !== undefined) {
      setIsRunning(externalIsRunning);
    }
  }, [externalIsRunning]);

  const handleStart = useCallback(() => {
    setIsRunning(true);
    onStart?.();
  }, [onStart]);

  const handlePause = useCallback(() => {
    setIsRunning(false);
    onPause?.();
  }, [onPause]);

  const handleReset = useCallback(() => {
    setIsRunning(false);
    setTime(0);
    setHasWarned(false);
    setHasCritical(false);
    onReset?.();
  }, [onReset]);

  // Format time as MM:SS
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Size classes
  const sizeClasses = {
    sm: 'text-2xl',
    md: 'text-4xl',
    lg: 'text-6xl',
    xl: 'text-8xl',
  };

  const containerSizeClasses = {
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
    xl: 'p-8',
  };

  // State-based styling
  const getStateClasses = (): string => {
    switch (timerState) {
      case 'critical':
        return 'bg-red-600 text-white animate-pulse border-red-700';
      case 'warning':
        return 'bg-yellow-500 text-white border-yellow-600';
      case 'running':
        return 'bg-green-600 text-white border-green-700';
      case 'paused':
        return 'bg-gray-500 text-white border-gray-600';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
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

  const getStateMessage = (): string => {
    switch (timerState) {
      case 'critical':
        return 'WAKTU MELEBIHI BATAS! Segera selesaikan triage';
      case 'warning':
        return 'Peringatan: Triage harus selesai dalam 30 detik';
      case 'running':
        return 'Triage sedang berlangsung...';
      case 'paused':
        return 'Timer dijeda';
      default:
        return 'Tekan Start untuk memulai timer';
    }
  };

  return (
    <div
      className={`
        rounded-xl border-2 shadow-lg
        ${containerSizeClasses[size]}
        ${getStateClasses()}
        transition-all duration-300
      `}
      role="timer"
      aria-live="polite"
      aria-label={`Triage timer: ${formatTime(time)}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{getStateIcon()}</span>
          <span className="font-medium text-sm uppercase tracking-wide">{label}</span>
        </div>
        <span
          className={`
            px-2 py-0.5 rounded text-xs font-bold
            ${timerState === 'critical' ? 'bg-white text-red-600' : ''}
            ${timerState === 'warning' ? 'bg-white text-yellow-600' : ''}
            ${timerState === 'running' ? 'bg-white/20' : ''}
          `}
        >
          {timerState === 'critical' && 'KRITIS'}
          {timerState === 'warning' && 'PERINGATAN'}
          {timerState === 'running' && 'AKTIF'}
          {timerState === 'paused' && 'PAUSED'}
          {timerState === 'idle' && 'SIAP'}
        </span>
      </div>

      {/* Timer Display */}
      <div className="text-center">
        <div
          className={`${sizeClasses[size]} font-mono font-bold tracking-wider`}
          style={{ fontVariantNumeric: 'tabular-nums' }}
        >
          {formatTime(time)}
        </div>
        <p className="text-xs mt-1 opacity-80">
          Target: &lt;2 menit ({formatTime(criticalThreshold)})
        </p>
      </div>

      {/* Status Message */}
      <div className="mt-3 text-center text-sm font-medium">
        {getStateMessage()}
      </div>

      {/* Controls */}
      {showControls && (
        <div className="mt-4 flex justify-center gap-2">
          {timerState === 'idle' && (
            <button
              onClick={handleStart}
              className="px-6 py-2 bg-white text-green-600 rounded-lg font-bold hover:bg-green-50 transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              </svg>
              Start
            </button>
          )}

          {timerState === 'running' && (
            <button
              onClick={handlePause}
              className="px-6 py-2 bg-white text-yellow-600 rounded-lg font-bold hover:bg-yellow-50 transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              Pause
            </button>
          )}

          {(timerState === 'paused' || timerState === 'warning' || timerState === 'critical') && (
            <button
              onClick={handleStart}
              className="px-6 py-2 bg-white text-green-600 rounded-lg font-bold hover:bg-green-50 transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              </svg>
              Resume
            </button>
          )}

          <button
            onClick={handleReset}
            className="px-6 py-2 bg-white/20 text-white rounded-lg font-bold hover:bg-white/30 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Reset
          </button>
        </div>
      )}

      {/* Progress Bar */}
      <div className="mt-4">
        <div className="h-2 bg-white/20 rounded-full overflow-hidden">
          <div
            className={`
              h-full transition-all duration-1000
              ${timerState === 'critical' ? 'bg-white' : 'bg-white'}
            `}
            style={{
              width: `${Math.min((time / criticalThreshold) * 100, 100)}%`,
              opacity: timerState === 'critical' ? 1 : timerState === 'warning' ? 0.8 : 0.6,
            }}
          />
        </div>
        <div className="flex justify-between text-xs mt-1 opacity-70">
          <span>0:00</span>
          <span>1:30</span>
          <span>2:00</span>
        </div>
      </div>
    </div>
  );
};

TriageTimer.displayName = 'TriageTimer';

export default TriageTimer;
