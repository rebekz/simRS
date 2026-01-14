import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from '@/components/ui/toast-primitive';
import { useToast } from '@/components/ui/use-toast';
import { cn } from '@/lib/utils';
import { CheckCircle, AlertCircle, Info, AlertTriangle, X } from 'lucide-react';

export function Toaster() {
  const { toasts } = useToast();

  const variantConfig = {
    success: {
      icon: CheckCircle,
      className: 'border-success/30 bg-success/10 text-success-900 dark:text-success-100',
    },
    error: {
      icon: AlertCircle,
      className: 'border-error/30 bg-error/10 text-error-900 dark:text-error-100',
    },
    info: {
      icon: Info,
      className: 'border-info/30 bg-info/10 text-info-900 dark:text-info-100',
    },
    warning: {
      icon: AlertTriangle,
      className: 'border-warning/30 bg-warning/10 text-warning-900 dark:text-warning-100',
    },
  };

  return (
    <ToastProvider>
      {toasts.map(function ({ id, title, message, variant = 'info', action, ...props }) {
        const config = variantConfig[variant];
        const Icon = config.icon;

        return (
          <Toast
            key={id}
            {...props}
            className={cn(
              'flex w-full items-start gap-3 rounded-lg border p-4 shadow-lg',
              'animate-in slide-in-from-right-full',
              config.className
            )}
          >
            <Icon className="h-5 w-5 flex-shrink-0 mt-0.5" />
            <div className="flex-1 space-y-1">
              {title && (
                <ToastTitle className="font-semibold text-sm">
                  {title}
                </ToastTitle>
              )}
              {message && (
                <ToastDescription className="text-sm opacity-90">
                  {message}
                </ToastDescription>
              )}
            </div>
            {action && (
              <button
                onClick={action.onClick}
                className="text-sm font-medium underline underline-offset-4"
              >
                {action.label}
              </button>
            )}
            <ToastClose className="flex-shrink-0 rounded-md p-1 hover:bg-black/5 dark:hover:bg-white/10">
              <X className="h-4 w-4" />
            </ToastClose>
          </Toast>
        );
      })}
      <ToastViewport />
    </ToastProvider>
  );
}
