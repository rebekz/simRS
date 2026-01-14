import React from 'react';
import { cn } from '@/lib/utils';
import { AlertCircle, Activity } from 'lucide-react';

export interface CriticalAlertProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  message?: string;
  emergencyType?: 'emergency' | 'critical' | 'code-blue' | 'code-red';
  pulse?: boolean;
}

const emergencyConfig = {
  emergency: {
    container: 'bg-emergency/10 border-emergency',
    borderLeft: 'border-l-emergency',
    text: 'text-emergency-900 dark:text-emergency-100',
    icon: 'text-emergency',
    label: 'EMERGENCY',
  },
  critical: {
    container: 'bg-critical/10 border-critical',
    borderLeft: 'border-l-critical',
    text: 'text-critical-900 dark:text-critical-100',
    icon: 'text-critical',
    label: 'CRITICAL',
  },
  'code-blue': {
    container: 'bg-blue-50 dark:bg-blue-950/30 border-blue-600',
    borderLeft: 'border-l-blue-600',
    text: 'text-blue-900 dark:text-blue-100',
    icon: 'text-blue-600',
    label: 'CODE BLUE',
  },
  'code-red': {
    container: 'bg-red-50 dark:bg-red-950/30 border-red-600',
    borderLeft: 'border-l-red-600',
    text: 'text-red-900 dark:text-red-100',
    icon: 'text-red-600',
    label: 'CODE RED',
  },
};

export const CriticalAlert = React.forwardRef<HTMLDivElement, CriticalAlertProps>(
  (
    {
      className,
      title,
      message,
      emergencyType = 'emergency',
      pulse = true,
      children,
      ...props
    },
    ref
  ) => {
    const config = emergencyConfig[emergencyType];

    return (
      <div
        ref={ref}
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        className={cn(
          'relative rounded-lg border border-l-6 p-5 shadow-lg',
          'animate-in fade-in-0 slide-in-from-top-2',
          config.container,
          config.borderLeft,
          className
        )}
        style={{ borderLeftWidth: '6px' }}
        {...props}
      >
        {/* Emergency Type Badge */}
        <div className="absolute -top-3 left-6">
          <span
            className={cn(
              'inline-flex items-center rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wider',
              'shadow-md',
              config.text,
              'bg-white dark:bg-gray-900',
              'border-2',
              config.borderLeft.replace('border-l-', 'border-')
            )}
          >
            {pulse && (
              <span className="mr-2">
                <Activity className={cn('h-3 w-3', pulse && 'animate-pulse')} />
              </span>
            )}
            {config.label}
          </span>
        </div>

        {/* Content */}
        <div className="mt-4 flex items-start gap-4">
          {/* Icon */}
          <div
            className={cn(
              'flex-shrink-0 rounded-full p-2',
              'bg-white dark:bg-gray-900 shadow-sm',
              config.icon
            )}
          >
            <AlertCircle className="h-6 w-6" />
          </div>

          {/* Text Content */}
          <div className="flex-1 space-y-2">
            <h3 className={cn('text-lg font-bold uppercase tracking-wide', config.text)}>
              {title}
            </h3>
            {message && (
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {message}
              </p>
            )}
            {children && (
              <div className="text-sm text-gray-700 dark:text-gray-300">
                {children}
              </div>
            )}
          </div>
        </div>

        {/* Decorative Bottom Bar */}
        <div
          className={cn(
            'absolute bottom-0 left-0 right-0 h-1',
            config.borderLeft.replace('border-l-', 'bg-'),
            pulse && 'animate-pulse'
          )}
        />
      </div>
    );
  }
);

CriticalAlert.displayName = 'CriticalAlert';
