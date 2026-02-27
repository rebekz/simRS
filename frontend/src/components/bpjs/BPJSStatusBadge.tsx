"use client";

import React from 'react';
import { Badge } from '@/components/ui/Badge';

export type BPJSStatusType = 'AKTIF' | 'PSTanggu' | 'NonPST' | 'inactive';

export interface BPJSStatusBadgeProps {
  status: BPJSStatusType;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

/**
 * BPJSStatusBadge Component
 *
 * Displays BPJS status with appropriate styling
 */
export const BPJSStatusBadge: React.FC<BPJSStatusBadgeProps> = ({
  status,
  size = 'md',
  showLabel = true,
}) => {
  const statusConfig: Record<BPJSStatusType, { color: string; bgColor: string; label: string }> = {
    AKTIF: {
      color: 'bg-green-600 text-white',
      bgColor: 'bg-green-100',
      label: 'AKTIF',
    },
    PSTanggu: {
      color: 'bg-yellow-600 text-white',
      bgColor: 'bg-yellow-100',
      label: 'PST Tertanggu',
    },
    NonPST: {
      color: 'bg-gray-600 text-white',
      bgColor: 'bg-gray-100',
      label: 'NonPST',
    },
    inactive: {
      color: 'bg-gray-400 text-white',
      bgColor: 'bg-gray-50',
      label: 'NonAktif',
    },
  };

  const config = statusConfig[status] || statusConfig.inactive;
  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5',
  };

  return (
    <Badge
      className={`
        ${sizeClasses[size]}
        ${config.bgColor}
        ${config.color}
        font-medium
      `}
    >
      {showLabel && <span className="ml-1">{config.label}</span>}
    </Badge>
  );
};

BPJSStatusBadge.displayName = 'BPJSStatusBadge';
