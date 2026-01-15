/**
 * Invoice Constants for SIMRS Billing System
 * Indonesian billing requirements and BPJS integration
 */

import type {
  InvoiceStatus,
  PaymentMethod,
  PayerType,
  LineItemType,
  BPJSClaimStatus,
  VisitType,
} from '@/types/invoice';

// ============================================================================
// PAYMENT METHODS
// ============================================================================

/**
 * Payment method options
 */
export const PAYMENT_METHODS: Record<
  PaymentMethod,
  { label: string; labelId: string; icon: string; description: string }
> = {
  cash: {
    label: 'Tunai',
    labelId: 'payment_method.cash',
    icon: '💵',
    description: 'Pembayaran tunai langsung',
  },
  transfer: {
    label: 'Transfer',
    labelId: 'payment_method.transfer',
    icon: '🏦',
    description: 'Transfer bank atau virtual account',
  },
  card: {
    label: 'Kartu',
    labelId: 'payment_method.card',
    icon: '💳',
    description: 'Kartu debit atau kredit',
  },
  bpjs: {
    label: 'BPJS',
    labelId: 'payment_method.bpjs',
    icon: '🏥',
    description: 'Jaminan Kesehatan Nasional',
  },
  insurance: {
    label: 'Asuransi',
    labelId: 'payment_method.insurance',
    icon: '🛡️',
    description: 'Asuransi swasta',
  },
  mixed: {
    label: 'Campuran',
    labelId: 'payment_method.mixed',
    icon: '🔄',
    description: 'Kombinasi beberapa metode pembayaran',
  },
};

/**
 * Payment method options array
 */
export const PAYMENT_METHOD_OPTIONS = Object.entries(PAYMENT_METHODS).map(([value, config]) => ({
  value,
  label: config.label,
  icon: config.icon,
  description: config.description,
}));

// ============================================================================
// PAYER TYPES
// ============================================================================

/**
 * Payer type options
 */
export const PAYER_TYPES: Record<
  PayerType,
  { label: string; labelId: string; icon: string; description: string; requiresApproval: boolean }
> = {
  patient: {
    label: 'Pasien',
    labelId: 'payer_type.patient',
    icon: '👤',
    description: 'Pasien membayar sendiri (biaya pribadi)',
    requiresApproval: false,
  },
  bpjs: {
    label: 'BPJS',
    labelId: 'payer_type.bpjs',
    icon: '🏥',
    description: 'Ditanggung oleh BPJS Kesehatan',
    requiresApproval: true,
  },
  insurance: {
    label: 'Asuransi',
    labelId: 'payer_type.insurance',
    icon: '🛡️',
    description: 'Ditanggung oleh asuransi swasta',
    requiresApproval: true,
  },
  corporate: {
    label: 'Korporat',
    labelId: 'payer_type.corporate',
    icon: '🏢',
    description: 'Ditanggung oleh perusahaan/korporat',
    requiresApproval: true,
  },
};

/**
 * Payer type options array
 */
export const PAYER_TYPE_OPTIONS = Object.entries(PAYER_TYPES).map(([value, config]) => ({
  value,
  label: config.label,
  icon: config.icon,
  description: config.description,
  requiresApproval: config.requiresApproval,
}));

// ============================================================================
// INVOICE STATUSES
// ============================================================================

/**
 * Invoice status options
 */
export const INVOICE_STATUSES: Record<
  InvoiceStatus,
  {
    label: string;
    labelId: string;
    color: string;
    bgColor: string;
    description: string;
    icon: string;
  }
> = {
  draft: {
    label: 'Draft',
    labelId: 'invoice_status.draft',
    color: 'text-gray-700',
    bgColor: 'bg-gray-100',
    description: 'Sedang disusun, belum diajukan',
    icon: '📝',
  },
  pending: {
    label: 'Menunggu',
    labelId: 'invoice_status.pending',
    color: 'text-yellow-700',
    bgColor: 'bg-yellow-100',
    description: 'Menunggu persetujuan',
    icon: '⏳',
  },
  approved: {
    label: 'Disetujui',
    labelId: 'invoice_status.approved',
    color: 'text-blue-700',
    bgColor: 'bg-blue-100',
    description: 'Disetujui, siap dibayar',
    icon: '✅',
  },
  submitted: {
    label: 'Diajukan',
    labelId: 'invoice_status.submitted',
    color: 'text-indigo-700',
    bgColor: 'bg-indigo-100',
    description: 'Diajukan ke BPJS/Asuransi',
    icon: '📤',
  },
  partial: {
    label: 'Sebagian',
    labelId: 'invoice_status.partial',
    color: 'text-purple-700',
    bgColor: 'bg-purple-100',
    description: 'Dibayar sebagian',
    icon: '▶️',
  },
  paid: {
    label: 'Lunas',
    labelId: 'invoice_status.paid',
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    description: 'Sudah lunas',
    icon: '💰',
  },
  overdue: {
    label: 'Terlambat',
    labelId: 'invoice_status.overdue',
    color: 'text-red-700',
    bgColor: 'bg-red-100',
    description: 'Jatuh tempo terlewati',
    icon: '⚠️',
  },
  cancelled: {
    label: 'Batal',
    labelId: 'invoice_status.cancelled',
    color: 'text-gray-500',
    bgColor: 'bg-gray-100',
    description: 'Tagihan dibatalkan',
    icon: '❌',
  },
};

/**
 * Invoice status options array
 */
export const INVOICE_STATUS_OPTIONS = Object.entries(INVOICE_STATUSES).map(([value, config]) => ({
  value,
  label: config.label,
  icon: config.icon,
  color: config.color,
  bgColor: config.bgColor,
  description: config.description,
}));

// ============================================================================
// BPJS CLAIM STATUSES
// ============================================================================

/**
 * BPJS claim status options
 */
export const BPJS_CLAIM_STATUSES: Record<
  BPJSClaimStatus,
  { label: string; labelId: string; color: string; bgColor: string; description: string }
> = {
  draft: {
    label: 'Draft',
    labelId: 'bpjs_status.draft',
    color: 'text-gray-700',
    bgColor: 'bg-gray-100',
    description: 'Klaim sedang disusun',
  },
  submitted: {
    label: 'Diajukan',
    labelId: 'bpjs_status.submitted',
    color: 'text-blue-700',
    bgColor: 'bg-blue-100',
    description: 'Klaim diajukan ke BPJS',
  },
  verified: {
    label: 'Diverifikasi',
    labelId: 'bpjs_status.verified',
    color: 'text-indigo-700',
    bgColor: 'bg-indigo-100',
    description: 'Klaim telah diverifikasi',
  },
  approved: {
    label: 'Disetujui',
    labelId: 'bpjs_status.approved',
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    description: 'Klaim disetujui BPJS',
  },
  rejected: {
    label: 'Ditolak',
    labelId: 'bpjs_status.rejected',
    color: 'text-red-700',
    bgColor: 'bg-red-100',
    description: 'Klaim ditolak BPJS',
  },
  paid: {
    label: 'Dibayar',
    labelId: 'bpjs_status.paid',
    color: 'text-emerald-700',
    bgColor: 'bg-emerald-100',
    description: 'Klaim telah dibayar',
  },
  cancelled: {
    label: 'Batal',
    labelId: 'bpjs_status.cancelled',
    color: 'text-gray-500',
    bgColor: 'bg-gray-100',
    description: 'Klaim dibatalkan',
  },
};

// ============================================================================
// LINE ITEM TYPES
// ============================================================================

/**
 * Line item type options
 */
export const LINE_ITEM_TYPES: Record<
  LineItemType,
  {
    label: string;
    labelId: string;
    icon: string;
    description: string;
    color: string;
    requiresDoctor: boolean;
    requiresPrescription: boolean;
  }
> = {
  service: {
    label: 'Layanan',
    labelId: 'item_type.service',
    icon: '🩺',
    description: 'Layanan medis dan konsultasi',
    color: 'text-blue-600',
    requiresDoctor: true,
    requiresPrescription: false,
  },
  medication: {
    label: 'Obat',
    labelId: 'item_type.medication',
    icon: '💊',
    description: 'Obat dan farmasi',
    color: 'text-green-600',
    requiresDoctor: false,
    requiresPrescription: true,
  },
  room: {
    label: 'Kamar',
    labelId: 'item_type.room',
    icon: '🛏️',
    description: 'Biaya kamar rawat inap',
    color: 'text-purple-600',
    requiresDoctor: false,
    requiresPrescription: false,
  },
  procedure: {
    label: 'Tindakan',
    labelId: 'item_type.procedure',
    icon: '🔧',
    description: 'Tindakan medis dan operasi',
    color: 'text-red-600',
    requiresDoctor: true,
    requiresPrescription: false,
  },
  diagnostic: {
    label: 'Diagnostik',
    labelId: 'item_type.diagnostic',
    icon: '🔬',
    description: 'Laboratorium dan radiologi',
    color: 'text-yellow-600',
    requiresDoctor: true,
    requiresPrescription: false,
  },
};

/**
 * Line item type options array
 */
export const LINE_ITEM_TYPE_OPTIONS = Object.entries(LINE_ITEM_TYPES).map(([value, config]) => ({
  value,
  label: config.label,
  icon: config.icon,
  description: config.description,
  color: config.color,
  requiresDoctor: config.requiresDoctor,
  requiresPrescription: config.requiresPrescription,
}));

// ============================================================================
// VISIT TYPES
// ============================================================================

/**
 * Visit type options
 */
export const VISIT_TYPES: Record<
  VisitType,
  { label: string; labelId: string; icon: string; description: string }
> = {
  outpatient: {
    label: 'Rawat Jalan',
    labelId: 'visit_type.outpatient',
    icon: '🚶',
    description: 'Kunjungan rawat jalan',
  },
  inpatient: {
    label: 'Rawat Inap',
    labelId: 'visit_type.inpatient',
    icon: '🛏️',
    description: 'Perawatan rawat inap',
  },
  emergency: {
    label: 'IGD',
    labelId: 'visit_type.emergency',
    icon: '🚨',
    description: 'Instalasi Gawat Darurat',
  },
};

/**
 * Visit type options array
 */
export const VISIT_TYPE_OPTIONS = Object.entries(VISIT_TYPES).map(([value, config]) => ({
  value,
  label: config.label,
  icon: config.icon,
  description: config.description,
}));

// ============================================================================
// DISCOUNT TYPES
// ============================================================================

/**
 * Discount type options
 */
export const DISCOUNT_TYPES = [
  { value: 'none', label: 'Tidak Ada', labelId: 'discount.none' },
  { value: 'fixed', label: 'Nominal Tetap', labelId: 'discount.fixed' },
  { value: 'percentage', label: 'Persentase', labelId: 'discount.percentage' },
] as const;

export type DiscountType = typeof DISCOUNT_TYPES[number]['value'];

// ============================================================================
// TAX RATES
// ============================================================================

/**
 * Tax rate options (Indonesian VAT rates)
 */
export const TAX_RATES = [
  { value: 0, label: '0%', labelId: 'tax.0' },
  { value: 10, label: '10%', labelId: 'tax.10' },
  { value: 11, label: '11%', labelId: 'tax.11' },
] as const;

/**
 * Default tax rate
 */
export const DEFAULT_TAX_RATE = 11;

/**
 * Get tax rate label
 */
export function getTaxRateLabel(rate: number): string {
  const taxRate = TAX_RATES.find((t) => t.value === rate);
  return taxRate?.label || `${rate}%`;
}

// ============================================================================
// BPJS SPECIFIC CONSTANTS
// ============================================================================

/**
 * BPJS severity levels
 */
export const BPJS_SEVERITY_LEVELS = [
  { value: 1, label: 'Level 1 - Ringan', labelId: 'bpjs.severity.1' },
  { value: 2, label: 'Level 2 - Sedang', labelId: 'bpjs.severity.2' },
  { value: 3, label: 'Level 3 - Berat', labelId: 'bpjs.severity.3' },
] as const;

/**
 * BPJS participant types
 */
export const BPJS_PARTICIPANT_TYPES = [
  { value: 'peserta', label: 'Peserta', labelId: 'bpjs.participant.participant' },
  { value: 'peserta_pbi', label: 'PBI', labelId: 'bpjs.participant.pbi' },
  { value: 'peserta_ppu', label: 'PPU', labelId: 'bpjs.participant.ppu' },
  { value: 'peserta_swasta', label: 'Swasta', labelId: 'bpjs.participant.private' },
] as const;

/**
 * BPJS facility tiers (Kelas Rawat)
 */
export const BPJS_FACILITY_TIERS = [
  { value: '1', label: 'Kelas 1', labelId: 'bpjs.tier.1' },
  { value: '2', label: 'Kelas 2', labelId: 'bpjs.tier.2' },
  { value: '3', label: 'Kelas 3', labelId: 'bpjs.tier.3' },
  { value: 'vip', label: 'VIP/VVIP', labelId: 'bpjs.tier.vip' },
] as const;

// ============================================================================
// DEFAULT VALUES
// ============================================================================

/**
 * Default invoice form values
 */
export const DEFAULT_INVOICE_FORM_VALUES = {
  patient_id: null,
  patient_name: '',
  encounter_id: null,
  visit_type: 'outpatient' as VisitType,
  department_id: null,
  department_name: '',
  invoice_date: new Date().toISOString().split('T')[0],
  due_date: getDefaultDueDate(),
  discount_type: 'none' as DiscountType,
  discount_value: 0,
  tax_rate: DEFAULT_TAX_RATE,
  payer_type: 'patient' as PayerType,
  payment_method: 'cash' as PaymentMethod,
  bpjs_number: '',
  bpjs_diagnosis_code: '',
  bpjs_procedure_codes: [],
  bpjs_severity_level: 1,
  insurance_number: '',
  insurance_provider: '',
  insurance_policy_number: '',
  corporate_id: undefined,
  corporate_billing_number: '',
  items: [],
  notes: '',
  internal_notes: '',
  status: 'draft' as InvoiceStatus,
  is_dirty: false,
  is_valid: false,
  validation_errors: [],
} as const;

/**
 * Default line item values
 */
export const DEFAULT_LINE_ITEM_VALUES = {
  item_type: 'service' as LineItemType,
  item_code: '',
  item_name: '',
  description: '',
  quantity: 1,
  unit: '',
  unit_price: 0,
  discount_type: 'none' as DiscountType,
  discount_value: 0,
  discount_amount: 0,
  subtotal: 0,
  tax_rate: DEFAULT_TAX_RATE,
  tax_amount: 0,
  total: 0,
  bpjs_tariff: undefined,
  bpjs_code: undefined,
  is_covered_by_bpjs: false,
  bpjs_coverage_amount: 0,
  is_covered_by_insurance: false,
  insurance_coverage_amount: 0,
  doctor_id: undefined,
  doctor_name: undefined,
  service_date: new Date().toISOString().split('T')[0],
  notes: '',
  is_new: true,
  is_modified: false,
  is_deleted: false,
} as const;

/**
 * Get default due date (7 days from now)
 */
export function getDefaultDueDate(): string {
  const date = new Date();
  date.setDate(date.getDate() + 7);
  return date.toISOString().split('T')[0];
}

// ============================================================================
// VALIDATION MESSAGES
// ============================================================================

/**
 * Validation error messages (Indonesian)
 */
export const VALIDATION_MESSAGES = {
  PATIENT_REQUIRED: 'Pasien harus dipilih',
  PATIENT_MUST_HAVE_BPJS: 'Pasien harus memiliki nomor BPJS untuk penanggung BPJS',
  ENCOUNTER_REQUIRED: 'Kunjungan harus dipilih',
  ENCOUNTER_INACTIVE: 'Kunjungan tidak aktif',
  MIN_ITEMS: 'Minimal satu item harus ditambahkan',
  MAX_ITEMS: 'Maksimal 100 item diperbolehkan',
  ITEM_REQUIRED: 'Item harus dipilih',
  INVALID_QUANTITY: 'Jumlah tidak valid',
  INVALID_PRICE: 'Harga tidak valid',
  INVALID_DISCOUNT: 'Diskon tidak valid',
  INVALID_TAX: 'Pajak tidak valid',
  INVALID_DATE: 'Tanggal tidak valid',
  DUE_DATE_BEFORE_INVOICE: 'Tanggal jatuh tempo tidak boleh sebelum tanggal tagihan',
  BPJS_NUMBER_REQUIRED: 'Nomor BPJS diperlukan',
  INSURANCE_NUMBER_REQUIRED: 'Nomor asuransi diperlukan',
  CORPORATE_REQUIRED: 'Perusahaan harus dipilih',
  NOTES_TOO_LONG: 'Catatan terlalu panjang',
} as const;

// ============================================================================
// FORMATTING HELPERS
// ============================================================================

/**
 * Format currency to Indonesian Rupiah
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format date to Indonesian locale
 */
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
}

/**
 * Format date and time to Indonesian locale
 */
export function formatDateTime(dateString: string): string {
  return new Date(dateString).toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format number with thousands separator
 */
export function formatNumber(amount: number): string {
  return new Intl.NumberFormat('id-ID').format(amount);
}

// ============================================================================
// CALCULATION HELPERS
// ============================================================================

/**
 * Calculate line item subtotal
 */
export function calculateLineItemSubtotal(quantity: number, unitPrice: number): number {
  return quantity * unitPrice;
}

/**
 * Calculate discount amount
 */
export function calculateDiscountAmount(
  subtotal: number,
  discountType: 'percentage' | 'fixed' | 'none',
  discountValue: number
): number {
  if (discountType === 'none' || discountValue <= 0) {
    return 0;
  }

  if (discountType === 'percentage') {
    return (subtotal * Math.min(discountValue, 100)) / 100;
  }

  return Math.min(discountValue, subtotal);
}

/**
 * Calculate tax amount
 */
export function calculateTaxAmount(subtotal: number, discountAmount: number, taxRate: number): number {
  const taxableAmount = Math.max(0, subtotal - discountAmount);
  return (taxableAmount * taxRate) / 100;
}

/**
 * Calculate line item total
 */
export function calculateLineItemTotal(
  quantity: number,
  unitPrice: number,
  discountType: 'percentage' | 'fixed' | 'none',
  discountValue: number,
  taxRate: number
): number {
  const subtotal = calculateLineItemSubtotal(quantity, unitPrice);
  const discountAmount = calculateDiscountAmount(subtotal, discountType, discountValue);
  const taxAmount = calculateTaxAmount(subtotal, discountAmount, taxRate);

  return subtotal - discountAmount + taxAmount;
}

/**
 * Calculate invoice totals
 */
export function calculateInvoiceTotals(
  items: Array<{
    subtotal: number;
    discount_amount: number;
    tax_amount: number;
    total: number;
  }>,
  invoiceDiscountType: 'percentage' | 'fixed' | 'none',
  invoiceDiscountValue: number,
  invoiceTaxRate: number
): {
  subtotal: number;
  discount_amount: number;
  tax_amount: number;
  total_amount: number;
} {
  const subtotal = items.reduce((sum, item) => sum + item.subtotal, 0);
  const itemDiscountTotal = items.reduce((sum, item) => sum + item.discount_amount, 0);
  const itemTaxTotal = items.reduce((sum, item) => sum + item.tax_amount, 0);

  const invoiceDiscountAmount = calculateDiscountAmount(
    subtotal,
    invoiceDiscountType,
    invoiceDiscountValue
  );

  const taxableAmount = Math.max(0, subtotal - itemDiscountTotal - invoiceDiscountAmount);
  const invoiceTaxAmount = (taxableAmount * invoiceTaxRate) / 100;

  const totalAmount = subtotal - itemDiscountTotal - invoiceDiscountAmount + itemTaxTotal + invoiceTaxAmount;

  return {
    subtotal,
    discount_amount: itemDiscountTotal + invoiceDiscountAmount,
    tax_amount: itemTaxTotal + invoiceTaxAmount,
    total_amount: totalAmount,
  };
}

// ============================================================================
// EXPORT ALL CONSTANTS
// ============================================================================

export const INVOICE_CONSTANTS = {
  PAYMENT_METHODS,
  PAYER_TYPES,
  INVOICE_STATUSES,
  BPJS_CLAIM_STATUSES,
  LINE_ITEM_TYPES,
  VISIT_TYPES,
  DISCOUNT_TYPES,
  TAX_RATES,
  DEFAULT_TAX_RATE,
  BPJS_SEVERITY_LEVELS,
  BPJS_PARTICIPANT_TYPES,
  BPJS_FACILITY_TIERS,
  VALIDATION_MESSAGES,
} as const;
