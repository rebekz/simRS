import React from 'react';
import { cn } from '@/lib/utils';
import { X, Info, CheckCircle, AlertTriangle, AlertCircle } from 'lucide-react';

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'info' | 'success' | 'warning' | 'error';
  icon?: React.ReactNode;
  title?: string;
  message?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
}

const variantConfig = {
  info: {
    container: 'bg-info/10 border-info/30 text-info-900 dark:text-info-100',
    icon: 'text-info',
    iconBg: 'bg-info/20',
  },
  success: {
    container: 'bg-success/10 border-success/30 text-success-900 dark:text-success-100',
    icon: 'text-success',
    iconBg: 'bg-success/20',
  },
  warning: {
    container: 'bg-warning/10 border-warning/30 text-warning-900 dark:text-warning-100',
    icon: 'text-warning',
    iconBg: 'bg-warning/20',
  },
  error: {
    container: 'bg-error/10 border-error/30 text-error-900 dark:text-error-100',
    icon: 'text-error',
    iconBg: 'bg-error/20',
  },
};

const defaultIcons = {
  info: <Info className="h-5 w-5" />,
  success: <CheckCircle className="h-5 w-5" />,
  warning: <AlertTriangle className="h-5 w-5" />,
  error: <AlertCircle className="h-5 w-5" />,
};

export const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  (
    {
      className,
      variant = 'info',
      icon,
      title,
      message,
      dismissible = false,
      onDismiss,
      children,
      ...props
    },
    ref
  ) => {
    const config = variantConfig[variant];
    const defaultIcon = defaultIcons[variant];

    return (
      <div
        ref={ref}
        role="alert"
        className={cn(
          'relative flex items-start gap-3 rounded-lg border p-4',
          config.container,
          className
        )}
        {...props}
      >
        {/* Icon */}
        <div className={cn('flex-shrink-0 rounded-full p-1', config.iconBg)}>
          {icon || defaultIcon}
        </div>

        {/* Content */}
        <div className="flex-1 space-y-1">
          {title && (
            <div className="font-semibold text-sm">
              {title}
            </div>
          )}
          {(message || children) && (
            <div className="text-sm opacity-90">
              {message}
              {children}
            </div>
          )}
        </div>

        {/* Dismiss Button */}
        {dismissible && (
          <button
            type="button"
            onClick={onDismiss}
            className={cn(
              'flex-shrink-0 rounded-md p-1 transition-colors',
              'hover:bg-black/5 dark:hover:bg-white/10',
              'focus:outline-none focus:ring-2 focus:ring-current focus:ring-offset-2'
            )}
            aria-label="Dismiss alert"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    );
  }
);

Alert.displayName = 'Alert';
