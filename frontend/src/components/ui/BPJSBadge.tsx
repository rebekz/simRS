import React from 'react';
import { Badge, BadgeProps } from './Badge';

export interface BPJSBadgeProps extends Omit<BadgeProps, 'variant'> {
  showDot?: boolean;
}

/**
 * BPJSBadge Component
 *
 * Specialized badge for BPJS (Badan Penyelenggara Jaminan Sosial)
 * Indonesia's national health insurance indicator.
 *
 * Features:
 * - BPJS brand colors (blue theme)
 * - Optional dot indicator for visual prominence
 * - Semibold weight for emphasis
 *
 * Uses enhanced-simrs-components.css classes:
 * - .badge-bpjs: BPJS-specific blue styling
 * - .badge-dot: Optional indicator dot
 *
 * @example
 * <BPJSBadge>Peserta BPJS</BPJSBadge>
 * <BPJSBadge showDot>BPJS Aktif</BPJSBadge>
 */
export const BPJSBadge: React.FC<BPJSBadgeProps> = ({
  showDot = false,
  className = '',
  children,
  ...props
}) => {
  const badgeClasses = [
    'badge',
    'badge-bpjs',
    showDot && 'badge-dot',
    className
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <span className={badgeClasses} {...props}>
      {children}
    </span>
  );
};

BPJSBadge.displayName = 'BPJSBadge';
