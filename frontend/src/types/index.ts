/**
 * User Roles in the SIMRS System
 */
export type UserRole =
  | 'admin'
  | 'doctor'
  | 'nurse'
  | 'pharmacist'
  | 'receptionist'
  | 'radiologist'
  | 'lab_tech';

/**
 * User Account Information
 */
export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
  permissions?: string[];
}

/**
 * Patient Medical Record Information
 */
export interface Patient {
  id: string;
  rmNumber: string;
  name: string;
  nik: string;
  bpjsNumber?: string;
  dateOfBirth: Date;
  gender: 'male' | 'female';
  phone: string;
  address: string;
  photo?: string;
  allergies?: string[];
  comorbidities?: string[];
}

/**
 * BPJS (Indonesian National Health Insurance) Data
 */
export interface BPJSData {
  cardNumber: string;
  nama: string;
  nik: string;
  jenisPeserta: string;
  faskes: string;
  status: BPJSStatus;
  eligibilityDate: Date;
}

/**
 * BPJS Membership Status
 */
export type BPJSStatus = 'active' | 'inactive' | 'expired' | 'suspended';

/**
 * Triage Severity Levels
 * merah: Critical/Emergency
 * kuning: Urgent
 * hijau: Semi-urgent
 * biru: Non-urgent
 * hitam: Deceased/Expectant
 */
export type TriageLevel = 'merah' | 'kuning' | 'hijau' | 'biru' | 'hitam';

/**
 * Navigation Menu Item Structure
 */
export interface MenuItem {
  id: string;
  label: string;
  icon?: string;
  href?: string;
  children?: MenuItem[];
  roles?: UserRole[];
}

/**
 * Standard API Response Wrapper
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: ApiError;
}

/**
 * API Error Details
 */
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

// ============================================================================
// REFERRAL TYPES EXPORT
// ============================================================================

export * from './referral';
