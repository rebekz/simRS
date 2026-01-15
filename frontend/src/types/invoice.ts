/**
 * Invoice Types for SIMRS Billing System
 * Supports Indonesian billing requirements including BPJS integration
 */

// ============================================================================
// PATIENT TYPES
// ============================================================================

/**
 * Patient information for invoice billing
 */
export interface InvoicePatient {
  id: number;
  medical_record_number: string;
  name: string;
  nik: string;
  date_of_birth: string;
  gender: 'male' | 'female';
  phone: string;
  email?: string;
  address: string;
  bpjs_number?: string;
  bpjs_status?: 'active' | 'inactive' | 'expired' | 'suspended';
  insurance_number?: string;
  insurance_provider?: string;
  corporate_id?: string;
  corporate_name?: string;
}

/**
 * Patient selection for invoice form
 */
export interface PatientSelectOption {
  value: number;
  label: string;
  medical_record_number: string;
  bpjs_number?: string;
  insurance_info?: {
    number: string;
    provider: string;
  };
  corporate_info?: {
    id: number;
    name: string;
  };
}

// ============================================================================
// ENCOUNTER / VISIT TYPES
// ============================================================================

/**
 * Visit/Encounter type for billing
 */
export type VisitType = 'outpatient' | 'inpatient' | 'emergency';

/**
 * Encounter information for invoice
 */
export interface InvoiceEncounter {
  id: number;
  patient_id: number;
  visit_type: VisitType;
  encounter_number: string;
  admission_date?: string;
  discharge_date?: string;
  department: string;
  department_id: number;
  attending_doctor?: string;
  attending_doctor_id?: number;
  room_number?: string;
  room_type?: string;
  bed_number?: string;
  status: 'admitted' | 'discharged' | 'transferred' | 'cancelled';
}

/**
 * Encounter selection for invoice form
 */
export interface EncounterSelectOption {
  value: number;
  label: string;
  visit_type: VisitType;
  department: string;
  admission_date?: string;
  discharge_date?: string;
  status: string;
  can_be_billed: boolean;
}

// ============================================================================
// LINE ITEM TYPES
// ============================================================================

/**
 * Line item category for invoice
 */
export type LineItemType = 'service' | 'medication' | 'room' | 'procedure' | 'diagnostic';

/**
 * Invoice line item
 */
export interface InvoiceLineItem {
  id?: number;
  item_type: LineItemType;
  item_code: string;
  item_name: string;
  description?: string;
  quantity: number;
  unit: string;
  unit_price: number;
  discount_type: 'percentage' | 'fixed' | 'none';
  discount_value: number;
  discount_amount: number;
  subtotal: number;
  tax_rate: number;
  tax_amount: number;
  total: number;

  // BPJS specific fields
  bpjs_tariff?: number;
  bpjs_code?: string;
  is_covered_by_bpjs?: boolean;
  bpjs_coverage_amount?: number;

  // Insurance specific fields
  is_covered_by_insurance?: boolean;
  insurance_coverage_amount?: number;

  // Clinical references
  doctor_id?: number;
  doctor_name?: string;
  service_date?: string;
  notes?: string;
}

/**
 * Form line item (for editing state)
 */
export interface FormLineItem extends Omit<InvoiceLineItem, 'id'> {
  temp_id?: string;
  is_new: boolean;
  is_modified: boolean;
  is_deleted: boolean;
}

// ============================================================================
// BILLING ITEM CATALOG TYPES
// ============================================================================

/**
 * Billing item from catalog
 */
export interface BillingCatalogItem {
  id: number;
  code: string;
  name: string;
  category: LineItemType;
  description?: string;
  unit: string;
  standard_price: number;
  bpjs_tariff?: number;
  bpjs_code?: string;
  is_bpjs_covered?: boolean;
  is_active: boolean;
  department_id?: number;
  requires_doctor: boolean;
  requires_prescription: boolean;
  stock_quantity?: number;
  min_stock_level?: number;
}

/**
 * Catalog search filters
 */
export interface CatalogSearchFilters {
  category?: LineItemType;
  department_id?: number;
  search_query?: string;
  include_inactive?: boolean;
}

/**
 * Catalog search result
 */
export interface CatalogSearchResult {
  items: BillingCatalogItem[];
  total: number;
  page: number;
  per_page: number;
}

// ============================================================================
// INVOICE TYPES
// ============================================================================

/**
 * Invoice status workflow
 */
export type InvoiceStatus =
  | 'draft'        // Initial state, being edited
  | 'pending'      // Submitted for approval
  | 'approved'     // Approved, ready for payment
  | 'submitted'    // Submitted to BPJS/Insurance
  | 'partial'      // Partially paid
  | 'paid'         // Fully paid
  | 'overdue'      // Payment overdue
  | 'cancelled';   // Cancelled/voided

/**
 * Payment method
 */
export type PaymentMethod =
  | 'cash'
  | 'transfer'
  | 'card'
  | 'bpjs'
  | 'insurance'
  | 'mixed';

/**
 * Payer type
 */
export type PayerType = 'patient' | 'bpjs' | 'insurance' | 'corporate';

/**
 * BPJS claim status
 */
export type BPJSClaimStatus =
  | 'draft'
  | 'submitted'
  | 'verified'
  | 'approved'
  | 'rejected'
  | 'paid'
  | 'cancelled';

/**
 * Complete invoice structure
 */
export interface Invoice {
  id: number;
  invoice_number: string;
  invoice_date: string;
  due_date: string;

  // Patient & Encounter
  patient_id: number;
  patient_name: string;
  medical_record_number: string;
  encounter_id?: number;
  visit_type: VisitType;
  department: string;
  department_id: number;

  // Financial summary
  subtotal: number;
  discount_type: 'percentage' | 'fixed' | 'none';
  discount_value: number;
  discount_amount: number;
  tax_rate: number;
  tax_amount: number;
  total_amount: number;
  paid_amount: number;
  remaining_balance: number;

  // Status
  status: InvoiceStatus;
  payment_method: PaymentMethod;
  payer_type: PayerType;

  // Line items
  items: InvoiceLineItem[];

  // BPJS specific
  bpjs_claim_number?: string;
  bpjs_claim_status?: BPJSClaimStatus;
  bpjs_submission_date?: string;
  bpjs_approval_date?: string;
  bpjs_approved_amount?: number;
  bpjs_rejection_reason?: string;

  // Insurance specific
  insurance_claim_number?: string;
  insurance_claim_status?: 'draft' | 'submitted' | 'approved' | 'rejected' | 'paid';
  insurance_approval_date?: string;
  insurance_approved_amount?: number;

  // Corporate billing
  corporate_id?: number;
  corporate_name?: string;
  corporate_billing_number?: string;
  corporate_due_date?: string;

  // Payment details
  payment_details?: InvoicePaymentDetail[];

  // Additional information
  notes?: string;
  internal_notes?: string;
  cancellation_reason?: string;

  // Metadata
  created_by: string;
  created_at: string;
  updated_at: string;
  approved_by?: string;
  approved_at?: string;
}

/**
 * Invoice payment detail
 */
export interface InvoicePaymentDetail {
  id: number;
  payment_date: string;
  payment_method: PaymentMethod;
  amount: number;
  reference_number?: string;
  bank_name?: string;
  card_last_four?: string;
  card_type?: string;
  notes?: string;
  created_by: string;
  created_at: string;
}

/**
 * Invoice summary for list view
 */
export interface InvoiceSummary {
  id: number;
  invoice_number: string;
  invoice_date: string;
  due_date: string;
  patient_name: string;
  medical_record_number: string;
  visit_type: VisitType;
  department: string;
  total_amount: number;
  paid_amount: number;
  remaining_balance: number;
  status: InvoiceStatus;
  payment_method: PaymentMethod;
  payer_type: PayerType;
  bpjs_claim_status?: BPJSClaimStatus;
  is_overdue: boolean;
  days_until_due: number;
}

// ============================================================================
// FORM STATE TYPES
// ============================================================================

/**
 * Invoice form state
 */
export interface InvoiceFormState {
  // Basic information
  patient_id: number | null;
  patient_name: string;
  encounter_id: number | null;
  visit_type: VisitType;
  department_id: number | null;
  department_name: string;
  invoice_date: string;
  due_date: string;

  // Financial settings
  discount_type: 'percentage' | 'fixed' | 'none';
  discount_value: number;
  tax_rate: number;

  // Payer information
  payer_type: PayerType;
  payment_method: PaymentMethod;

  // BPJS fields
  bpjs_number?: string;
  bpjs_diagnosis_code?: string;
  bpjs_procedure_codes?: string[];
  bpjs_severity_level?: 1 | 2 | 3;

  // Insurance fields
  insurance_number?: string;
  insurance_provider?: string;
  insurance_policy_number?: string;

  // Corporate fields
  corporate_id?: number;
  corporate_billing_number?: string;

  // Line items
  items: FormLineItem[];

  // Additional information
  notes: string;
  internal_notes: string;

  // Status tracking
  status: InvoiceStatus;
  is_dirty: boolean;
  is_valid: boolean;
  validation_errors: FormValidationError[];
}

/**
 * Form validation error
 */
export interface FormValidationError {
  field: string;
  message: string;
  severity: 'error' | 'warning';
}

/**
 * Form actions
 */
export type InvoiceFormAction =
  | { type: 'SET_PATIENT'; payload: InvoicePatient }
  | { type: 'SET_ENCOUNTER'; payload: InvoiceEncounter }
  | { type: 'SET_FIELD'; field: keyof InvoiceFormState; value: any }
  | { type: 'ADD_ITEM'; payload: FormLineItem }
  | { type: 'UPDATE_ITEM'; payload: { temp_id: string; updates: Partial<FormLineItem> } }
  | { type: 'REMOVE_ITEM'; payload: { temp_id: string } }
  | { type: 'CALCULATE_TOTALS' }
  | { type: 'VALIDATE' }
  | { type: 'RESET' };

// ============================================================================
// VALIDATION CONSTRAINTS
// ============================================================================

/**
 * Invoice validation constraints
 */
export interface InvoiceValidationConstraints {
  // Patient
  patient_required: boolean;
  patient_must_have_bpjs_for_bpjs_payer: boolean;

  // Encounter
  encounter_required: boolean;
  encounter_must_be_active: boolean;

  // Items
  min_items: number;
  max_items: number;
  item_quantity_max: number;
  item_quantity_min: number;

  // Financial
  min_invoice_total: number;
  max_invoice_total: number;
  discount_max_percentage: number;
  tax_min_rate: number;
  tax_max_rate: number;

  // Dates
  invoice_date_min_offset_days: number;
  invoice_date_max_offset_days: number;
  due_date_min_days: number;
  due_date_max_days: number;

  // Notes
  notes_max_length: number;
  internal_notes_max_length: number;
}

/**
 * Default validation constraints
 */
export const DEFAULT_VALIDATION_CONSTRAINTS: InvoiceValidationConstraints = {
  patient_required: true,
  patient_must_have_bpjs_for_bpjs_payer: true,
  encounter_required: false,
  encounter_must_be_active: false,
  min_items: 1,
  max_items: 100,
  item_quantity_max: 9999,
  item_quantity_min: 1,
  min_invoice_total: 0,
  max_invoice_total: 999999999,
  discount_max_percentage: 100,
  tax_min_rate: 0,
  tax_max_rate: 100,
  invoice_date_min_offset_days: -30,
  invoice_date_max_offset_days: 30,
  due_date_min_days: 0,
  due_date_max_days: 365,
  notes_max_length: 1000,
  internal_notes_max_length: 2000,
};

// ============================================================================
// API REQUEST/RESPONSE TYPES
// ============================================================================

/**
 * Create invoice request
 */
export interface CreateInvoiceRequest {
  patient_id: number;
  encounter_id?: number;
  visit_type: VisitType;
  department_id: number;
  invoice_date: string;
  due_date: string;
  discount_type: 'percentage' | 'fixed' | 'none';
  discount_value: number;
  tax_rate: number;
  payer_type: PayerType;
  payment_method: PaymentMethod;
  bpjs_number?: string;
  bpjs_diagnosis_code?: string;
  bpjs_procedure_codes?: string[];
  insurance_number?: string;
  insurance_provider?: string;
  corporate_id?: number;
  items: Omit<InvoiceLineItem, 'id'>[];
  notes?: string;
  internal_notes?: string;
}

/**
 * Update invoice request
 */
export interface UpdateInvoiceRequest extends Partial<CreateInvoiceRequest> {
  id: number;
}

/**
 * Invoice list query parameters
 */
export interface InvoiceListQuery {
  page?: number;
  per_page?: number;
  status?: InvoiceStatus;
  payment_method?: PaymentMethod;
  payer_type?: PayerType;
  patient_id?: number;
  start_date?: string;
  end_date?: string;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

/**
 * Invoice list response
 */
export interface InvoiceListResponse {
  items: InvoiceSummary[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

/**
 * Invoice statistics
 */
export interface InvoiceStatistics {
  today_total: number;
  today_count: number;
  pending: number;
  pending_count: number;
  approved: number;
  approved_count: number;
  submitted: number;
  submitted_count: number;
  collected: number;
  collected_count: number;
  overdue: number;
  overdue_count: number;
}

/**
 * Invoice calculation result
 */
export interface InvoiceCalculation {
  subtotal: number;
  discount_amount: number;
  tax_amount: number;
  total_amount: number;
  bpjs_covered_amount: number;
  insurance_covered_amount: number;
  patient_responsibility: number;
}
