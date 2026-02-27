"use client";

import React, { useState } from 'react';

export interface EmergencyActivationButtonProps {
  onClick?: () => void;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'solid' | 'outline';
  showLabel?: boolean;
  disabled?: boolean;
  pulseEffect?: boolean;
}

/**
 * EmergencyActivationButton Component
 *
 * A prominent button for activating Kode Biru (Code Blue) emergency response.
 * Designed to be highly visible and accessible from any page.
 *
 * Features:
 * - Animated pulse effect for visibility
 * - Multiple sizes and variants
 * - Keyboard accessible
 * - Touch-friendly for tablet use
 */
export const EmergencyActivationButton: React.FC<EmergencyActivationButtonProps> = ({
  onClick,
  size = 'md',
  variant = 'solid',
  showLabel = true,
  disabled = false,
  pulseEffect = true,
}) => {
  const [isPressed, setIsPressed] = useState(false);

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-base',
    lg: 'px-6 py-4 text-lg',
  };

  const iconSizes = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  const baseClasses = `
    inline-flex items-center justify-center gap-2
    font-bold rounded-lg
    transition-all duration-200
    transform active:scale-95
    focus:outline-none focus:ring-4 focus:ring-red-300
    disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
  `;

  const variantClasses = {
    solid: `
      bg-red-600 text-white
      hover:bg-red-700
      shadow-lg shadow-red-500/30
      ${pulseEffect && !disabled ? 'animate-pulse' : ''}
    `,
    outline: `
      bg-white text-red-600
      border-2 border-red-600
      hover:bg-red-50
    `,
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setIsPressed(true);
      onClick?.();
      setTimeout(() => setIsPressed(false), 150);
    }
  };

  return (
    <button
      type="button"
      onClick={onClick}
      onKeyDown={handleKeyDown}
      disabled={disabled}
      aria-label="Aktifkan Kode Biru - Resusitasi Darurat"
      className={`
        ${baseClasses}
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${isPressed ? 'scale-95' : ''}
      `}
    >
      {/* Bell Icon with Animation */}
      <svg
        className={`${iconSizes[size]} ${pulseEffect && !disabled ? 'animate-bounce' : ''}`}
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>

      {showLabel && (
        <span className="whitespace-nowrap">
          KODE BIRU
        </span>
      )}
    </button>
  );
};

EmergencyActivationButton.displayName = 'EmergencyActivationButton';

export default EmergencyActivationButton;
