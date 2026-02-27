// BPJS Components Index
// Export all BPJS-related components for easy importing

export { BPJSVerificationCard } from './BPJSVerificationCard';
export type { BPJSVerificationCardProps, BPJSParticipant, BPJSVerificationResult, BPJSError } from './BPJSVerificationCard';

export { BPJSStatusBadge } from './BPJSStatusBadge';
export type { BPJSStatusBadgeProps, BPJSStatusType } from './BPJSStatusBadge';

export { SEPWizard } from './SEPWizard';
export type { SEPWizardProps, SEPFormData, SEPCreationResult } from './SEPWizard';

// Status Indicators - WEB-S-2.3
export {
  BPJSStatusBadge as BPJSStatusBadgeNew,
  BPJSStatusCard,
  BPJSStatusIndicator,
  BPJSPesertaBadge,
  FaskesIndicator,
  useBPJSStatus,
} from './BPJSStatusIndicators';
export type {
  BPJSStatusData,
  BPJSStatusBadgeProps as BPJSStatusBadgeNewProps,
  BPJSStatusCardProps,
  BPJSStatusIndicatorProps,
  BPJSPesertaBadgeProps,
  FaskesIndicatorProps,
  BPJSPesertaType,
} from './BPJSStatusIndicators';
