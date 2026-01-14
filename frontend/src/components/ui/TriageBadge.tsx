import React from 'react';

export type TriageLevel = 'merah' | 'kuning' | 'hijau' | 'biru' | 'hitam';

export interface TriageBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  level: TriageLevel;
  showLabel?: boolean;
}

/**
 * TriageBadge Component
 *
 * Medical triage classification badges for emergency room patient sorting.
 * Follows standard Indonesian hospital triage color coding:
 *
 * - Merah (Red): Gawat Darurat - Life-threatening, immediate treatment
 *   Color: #dc2626
 *
 * - Kuning (Yellow): Semi-Urgent - Serious but stable
 *   Color: #f59e0b
 *
 * - Hijau (Green): Non-Urgent - Minor injuries/illnesses
 *   Color: #059669
 *
 * - Biru (Blue): Potentially unstable - Monitor closely
 *   Color: #0284c7
 *
 * - Hitam (Black): Deceased/Expectant - Beyond saving
 *   Color: #1f2937
 *
 * Uses enhanced-simrs-components.css classes:
 * - .badge-triage-{level}: Triage-specific styling
 * - .badge: Base badge styling
 *
 * @example
 * <TriageBadge level="merah" />
 * <TriageBadge level="kuning" showLabel />
 */
export const TriageBadge: React.FC<TriageBadgeProps> = ({
  level,
  showLabel = false,
  className = '',
  ...props
}) => {
  const triageLabels: Record<TriageLevel, string> = {
    merah: 'Gawat Darurat',
    kuning: 'Semi-Urgent',
    hijau: 'Non-Urgent',
    biru: 'Monitoring',
    hitam: 'Expectant'
  };

  const badgeClasses = [
    'badge',
    `badge-triage-${level}`,
    className
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <span className={badgeClasses} {...props}>
      {showLabel ? triageLabels[level] : level.charAt(0).toUpperCase() + level.slice(1)}
    </span>
  );
};

TriageBadge.displayName = 'TriageBadge';
