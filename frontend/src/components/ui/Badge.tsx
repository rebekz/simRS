import React from 'react';

export type BadgeVariant = 'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  dot?: boolean;
  children: React.ReactNode;
}

/**
 * Badge Component
 *
 * Display badges with semantic color coding:
 * - primary: Medical teal for general information
 * - success: Green for completed/active status
 * - warning: Yellow/amber for caution states
 * - error: Red for errors or critical issues
 * - info: Blue for informational content
 * - neutral: Gray for neutral/default states
 *
 * Uses enhanced-simrs-components.css classes:
 * - .badge: Base badge styling
 * - .badge-{variant}: Color variants
 * - .badge-dot: Adds indicator dot before text
 */
export const Badge: React.FC<BadgeProps> = ({
  variant = 'primary',
  dot = false,
  className = '',
  children,
  ...props
}) => {
  const badgeClasses = [
    'badge',
    `badge-${variant}`,
    dot && 'badge-dot',
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

Badge.displayName = 'Badge';
