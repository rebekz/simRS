import { toast as radixToast } from '@/components/ui/use-toast';

export interface Toast {
  id: string;
  variant: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number;
  title?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const defaultDurations = {
  success: 5000,
  error: 7000,
  info: 5000,
  warning: 6000,
};

export const toast = {
  success: (message: string, options?: Partial<Omit<Toast, 'id' | 'variant' | 'message'>>) => {
    return radixToast({
      variant: 'success',
      message,
      duration: options?.duration ?? defaultDurations.success,
      title: options?.title,
      action: options?.action,
    });
  },

  error: (message: string, options?: Partial<Omit<Toast, 'id' | 'variant' | 'message'>>) => {
    return radixToast({
      variant: 'error',
      message,
      duration: options?.duration ?? defaultDurations.error,
      title: options?.title,
      action: options?.action,
    });
  },

  info: (message: string, options?: Partial<Omit<Toast, 'id' | 'variant' | 'message'>>) => {
    return radixToast({
      variant: 'info',
      message,
      duration: options?.duration ?? defaultDurations.info,
      title: options?.title,
      action: options?.action,
    });
  },

  warning: (message: string, options?: Partial<Omit<Toast, 'id' | 'variant' | 'message'>>) => {
    return radixToast({
      variant: 'warning',
      message,
      duration: options?.duration ?? defaultDurations.warning,
      title: options?.title,
      action: options?.action,
    });
  },

  // Dismiss a specific toast by ID
  dismiss: (toastId: string) => {
    if (typeof window !== 'undefined') {
      const event = new CustomEvent('toast-dismiss', { detail: { toastId } });
      window.dispatchEvent(event);
    }
  },

  // Dismiss all toasts
  dismissAll: () => {
    if (typeof window !== 'undefined') {
      const event = new CustomEvent('toast-dismiss-all');
      window.dispatchEvent(event);
    }
  },
};

export type ToastType = Toast;
