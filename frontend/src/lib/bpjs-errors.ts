/**
 * BPJS Error Handling Utilities
 *
 * Transforms BPJS VClaim API errors into user-friendly messages
 * with retry logic and error categorization.
 */

// ============================================================================
// BPJS ERROR CODES (Based on BPJS VClaim API Documentation)
// ============================================================================

export enum BPJSErrorCode {
  // Authentication Errors (1xxx)
  INVALID_CONS_ID = "1001",
  EXPIRED_SIGNATURE = "1002",
  INVALID_SIGNATURE = "1003",

  // Card Number Errors (2xxx)
  INVALID_CARD_NUMBER = "2001",
  CARD_NOT_FOUND = "2002",
  CARD_EXPIRED = "2003",
  CARD_SUSPENDED = "2004",

  // Eligibility Errors (3xxx)
  INELIGIBLE_PESERTA = "3001",
  FASKES_MISMATCH = "3002",
  COB_ERROR = "3003",

  // SEP Errors (4xxx)
  DUPLICATE_SEP = "4001",
  INVALID_DPJP = "4002",
  SEP_NOT_FOUND = "4003",
  SEP_CANCELLED = "4004",

  // Network Errors (5xxx)
  TIMEOUT = "5001",
  CONNECTION_ERROR = "5002",
  SERVICE_UNAVAILABLE = "5003",

  // Validation Errors (6xxx)
  MISSING_REQUIRED_FIELD = "6001",
  INVALID_FORMAT = "6002",
  INVALID_DATE = "6003",

  // Rate Limiting (7xxx)
  RATE_LIMIT_EXCEEDED = "7001",
  TOO_MANY_REQUESTS = "7002",

  // Unknown Errors
  UNKNOWN_ERROR = "9999",
}

// ============================================================================
// BPJS ERROR TYPES
// ============================================================================

export enum BPJSErrorType {
  AUTHENTICATION = "authentication",
  AUTHORIZATION = "authorization",
  VALIDATION = "validation",
  NOT_FOUND = "not_found",
  BUSINESS_LOGIC = "business_logic",
  NETWORK = "network",
  RATE_LIMIT = "rate_limit",
  UNKNOWN = "unknown",
}

export interface BPJSError {
  code: string;
  type: BPJSErrorType;
  title: string;
  message: string;
  suggestion: string;
  retryable: boolean;
  userAction: string;
}

// ============================================================================
// ERROR MAPPING
// ============================================================================

const BPJS_ERROR_MESSAGES: Record<BPJSErrorCode, BPJSError> = {
  // Authentication Errors
  [BPJSErrorCode.INVALID_CONS_ID]: {
    code: BPJSErrorCode.INVALID_CONS_ID,
    type: BPJSErrorType.AUTHENTICATION,
    title: "Konsultasi ID Tidak Valid",
    message: "ID konsultasi BPJS tidak valid atau telah kadaluarsa.",
    suggestion: "Hubungi administrator sistem untuk memperbarui konsultasi ID.",
    retryable: false,
    userAction: "Hubungi IT Support",
  },
  [BPJSErrorCode.EXPIRED_SIGNATURE]: {
    code: BPJSErrorCode.EXPIRED_SIGNATURE,
    type: BPJSErrorType.AUTHENTICATION,
    title: "Signature Kadaluarsa",
    message: "Tanda tangan digital untuk BPJS API telah kadaluarsa.",
    suggestion: "Perbarui certificate signature untuk BPJS API.",
    retryable: false,
    userAction: "Hubungi IT Support",
  },
  [BPJSErrorCode.INVALID_SIGNATURE]: {
    code: BPJSErrorCode.INVALID_SIGNATURE,
    type: BPJSErrorType.AUTHENTICATION,
    title: "Signature Tidak Valid",
    message: "Tanda tangan digital untuk BPJS API tidak valid.",
    suggestion: "Periksa konfigurasi signature BPJS API.",
    retryable: false,
    userAction: "Hubungi IT Support",
  },

  // Card Number Errors
  [BPJSErrorCode.INVALID_CARD_NUMBER]: {
    code: BPJSErrorCode.INVALID_CARD_NUMBER,
    type: BPJSErrorType.VALIDATION,
    title: "Nomor Kartu Tidak Valid",
    message: "Nomor kartu BPJS harus 13 digit angka.",
    suggestion: "Periksa kembali nomor kartu BPJS pasien.",
    retryable: false,
    userAction: "Periksa nomor kartu",
  },
  [BPJSErrorCode.CARD_NOT_FOUND]: {
    code: BPJSErrorCode.CARD_NOT_FOUND,
    type: BPJSErrorType.NOT_FOUND,
    title: "Kartu BPJS Tidak Ditemukan",
    message: "Nomor kartu BPJS tidak terdaftar dalam sistem BPJS.",
    suggestion: "Pastikan nomor kartu benar dan pasien telah terdaftar di BPJS.",
    retryable: false,
    userAction: "Periksa nomor kartu",
  },
  [BPJSErrorCode.CARD_EXPIRED]: {
    code: BPJSErrorCode.CARD_EXPIRED,
    type: BPJSErrorType.BUSINESS_LOGIC,
    title: "Masa Berlaku Kartu Habis",
    message: "Masa kepesertaan BPJS pasien telah berakhir.",
    suggestion: "Pasien perlu memperpanjang kepesertaan BPJS.",
    retryable: false,
    userAction: "Perbarui kepesertaan BPJS",
  },
  [BPJSErrorCode.CARD_SUSPENDED]: {
    code: BPJSErrorCode.CARD_SUSPENDED,
    type: BPJSErrorType.BUSINESS_LOGIC,
    title: "Keanggotaan Ditangguhkan",
    message: "Keanggotaan BPJS pasien ditangguhkan sementara.",
    suggestion: "Hubungi kantor BPJS terdekat untuk informasi lebih lanjut.",
    retryable: false,
    userAction: "Hubungi kantor BPJS",
  },

  // Eligibility Errors
  [BPJSErrorCode.INELIGIBLE_PESERTA]: {
    code: BPJSErrorCode.INELIGIBLE_PESERTA,
    type: BPJSErrorType.AUTHORIZATION,
    title: "Pasien Tidak Eligible",
    message: "Pasien tidak eligible untuk pelayanan saat ini.",
    suggestion: "Periksa status kepesertaan dan faskes tujuan.",
    retryable: false,
    userAction: "Periksa status kepesertaan",
  },
  [BPJSErrorCode.FASKES_MISMATCH]: {
    code: BPJSErrorCode.FASKES_MISMATCH,
    type: BPJSErrorType.BUSINESS_LOGIC,
    title: "Faskes Tidak Sesuai",
    message: "Faskes tujuan tidak sesuai dengan kartu BPJS pasien.",
    suggestion: "Pilih faskes yang sesuai dengan kartu BPJS pasien.",
    retryable: false,
    userAction: "Pilih faskes yang sesuai",
  },
  [BPJSErrorCode.COB_ERROR]: {
    code: BPJSErrorCode.COB_ERROR,
    type: BPJSErrorType.BUSINESS_LOGIC,
    title: "Error COB",
    message: "Terjadi masalah dengan Coordinate of Benefit (COB).",
    suggestion: "Periksa status COB pasien.",
    retryable: false,
    userAction: "Periksa status COB",
  },

  // SEP Errors
  [BPJSErrorCode.DUPLICATE_SEP]: {
    code: BPJSErrorCode.DUPLICATE_SEP,
    type: BPJSErrorType.BUSINESS_LOGIC,
    title: "SEP Sudah Ada",
    message: "SEP untuk pasien pada tanggal yang sama sudah pernah dibuat.",
    suggestion: "Gunakan SEP yang sudah ada atau batalkan SEP terlebih dahulu.",
    retryable: false,
    userAction: "Gunakan SEP yang ada",
  },
  [BPJSErrorCode.INVALID_DPJP]: {
    code: BPJSErrorCode.INVALID_DPJP,
    type: BPJSErrorType.VALIDATION,
    title: "DPJP Tidak Valid",
    message: "Dokter penanggung jawab tidak valid untuk poli yang dipilih.",
    suggestion: "Pilih dokter yang sesuai dengan poli tujuan.",
    retryable: false,
    userAction: "Pilih dokter yang sesuai",
  },
  [BPJSErrorCode.SEP_NOT_FOUND]: {
    code: BPJSErrorCode.SEP_NOT_FOUND,
    type: BPJSErrorType.NOT_FOUND,
    title: "SEP Tidak Ditemukan",
    message: "Nomor SEP tidak ditemukan dalam sistem BPJS.",
    suggestion: "Periksa kembali nomor SEP yang dimasukkan.",
    retryable: false,
    userAction: "Periksa nomor SEP",
  },
  [BPJSErrorCode.SEP_CANCELLED]: {
    code: BPJSErrorCode.SEP_CANCELLED,
    type: BPJSErrorType.BUSINESS_LOGIC,
    title: "SEP Dibatalkan",
    message: "SEP telah dibatalkan dan tidak dapat digunakan.",
    suggestion: "Buat SEP baru untuk pelayanan pasien.",
    retryable: false,
    userAction: "Buat SEP baru",
  },

  // Network Errors
  [BPJSErrorCode.TIMEOUT]: {
    code: BPJSErrorCode.TIMEOUT,
    type: BPJSErrorType.NETWORK,
    title: "Koneksi BPJS Timeout",
    message: "Tidak dapat terhubung ke server BPJS. Waktu habis.",
    suggestion: "Periksa koneksi internet dan coba lagi.",
    retryable: true,
    userAction: "Coba lagi",
  },
  [BPJSErrorCode.CONNECTION_ERROR]: {
    code: BPJSErrorCode.CONNECTION_ERROR,
    type: BPJSErrorType.NETWORK,
    title: "Koneksi BPJS Gagal",
    message: "Tidak dapat terhubung ke server BPJS.",
    suggestion: "Periksa koneksi internet dan status server BPJS.",
    retryable: true,
    userAction: "Coba lagi",
  },
  [BPJSErrorCode.SERVICE_UNAVAILABLE]: {
    code: BPJSErrorCode.SERVICE_UNAVAILABLE,
    type: BPJSErrorType.NETWORK,
    title: "Layanan BPJS Tidak Tersedia",
    message: "Layanan BPJS sedang dalam pemeliharaan.",
    suggestion: "Tunggu beberapa saat dan coba lagi.",
    retryable: true,
    userAction: "Coba lagi nanti",
  },

  // Validation Errors
  [BPJSErrorCode.MISSING_REQUIRED_FIELD]: {
    code: BPJSErrorCode.MISSING_REQUIRED_FIELD,
    type: BPJSErrorType.VALIDATION,
    title: "Data Tidak Lengkap",
    message: "Ada data wajib yang belum diisi.",
    suggestion: "Lengkapi semua data yang diperlukan.",
    retryable: false,
    userAction: "Lengkapi data",
  },
  [BPJSErrorCode.INVALID_FORMAT]: {
    code: BPJSErrorCode.INVALID_FORMAT,
    type: BPJSErrorType.VALIDATION,
    title: "Format Data Salah",
    message: "Format data yang dikirim tidak valid.",
    suggestion: "Periksa kembali format data yang dimasukkan.",
    retryable: false,
    userAction: "Perbaiki format data",
  },
  [BPJSErrorCode.INVALID_DATE]: {
    code: BPJSErrorCode.INVALID_DATE,
    type: BPJSErrorType.VALIDATION,
    title: "Tanggal Tidak Valid",
    message: "Tanggal yang dimasukkan tidak valid.",
    suggestion: "Periksa kembali tanggal pelayanan.",
    retryable: false,
    userAction: "Perbaiki tanggal",
  },

  // Rate Limiting
  [BPJSErrorCode.RATE_LIMIT_EXCEEDED]: {
    code: BPJSErrorCode.RATE_LIMIT_EXCEEDED,
    type: BPJSErrorType.RATE_LIMIT,
    title: "Batas Request Terlampaui",
    message: "Terlalu banyak permintaan ke BPJS dalam waktu singkat.",
    suggestion: "Tunggu beberapa saat sebelum mencoba lagi.",
    retryable: true,
    userAction: "Tunggu sebentar",
  },
  [BPJSErrorCode.TOO_MANY_REQUESTS]: {
    code: BPJSErrorCode.TOO_MANY_REQUESTS,
    type: BPJSErrorType.RATE_LIMIT,
    title: "Terlalu Banyak Permintaan",
    message: "Batasi jumlah permintaan BPJS.",
    suggestion: "Kurangi frekuensi permintaan.",
    retryable: true,
    userAction: "Tunggu sebentar",
  },

  // Unknown Errors
  [BPJSErrorCode.UNKNOWN_ERROR]: {
    code: BPJSErrorCode.UNKNOWN_ERROR,
    type: BPJSErrorType.UNKNOWN,
    title: "Terjadi Kesalahan",
    message: "Terjadi kesalahan yang tidak diketahui.",
    suggestion: "Coba lagi atau hubungi administrator jika masalah berlanjut.",
    retryable: true,
    userAction: "Coba lagi",
  },
};

// ============================================================================
// ERROR TRANSLATION FUNCTIONS
// ============================================================================

/**
 * Translate BPJS API error code to user-friendly error object
 */
export function translateBPJSError(
  errorCode: string,
  originalMessage?: string
): BPJSError {
  const knownError = BPJS_ERROR_MESSAGES[errorCode as BPJSErrorCode];

  if (knownError) {
    return knownError;
  }

  // For unknown errors, try to provide some context
  if (originalMessage) {
    return {
      code: errorCode,
      type: BPJSErrorType.UNKNOWN,
      title: "Kesalahan BPJS",
      message: originalMessage,
      suggestion: "Coba lagi atau hubungi administrator.",
      retryable: true,
      userAction: "Coba lagi",
    };
  }

  return BPJS_ERROR_MESSAGES[BPJSErrorCode.UNKNOWN_ERROR];
}

/**
 * Translate HTTP status to BPJS error
 */
export function translateHttpError(status: number, statusText?: string): BPJSError {
  switch (status) {
    case 400:
      return translateBPJSError(BPJSErrorCode.INVALID_FORMAT, statusText);
    case 401:
      return translateBPJSError(BPJSErrorCode.INVALID_CONS_ID);
    case 403:
      return translateBPJSError(BPJSErrorCode.INELIGIBLE_PESERTA);
    case 404:
      return translateBPJSError(BPJSErrorCode.CARD_NOT_FOUND);
    case 408:
      return translateBPJSError(BPJSErrorCode.TIMEOUT);
    case 429:
      return translateBPJSError(BPJSErrorCode.RATE_LIMIT_EXCEEDED);
    case 500:
    case 502:
    case 503:
      return translateBPJSError(BPJSErrorCode.SERVICE_UNAVAILABLE);
    default:
      return translateBPJSError(BPJSErrorCode.CONNECTION_ERROR, statusText);
  }
}

/**
 * Translate network/error object to BPJS error
 */
export function translateError(error: any): BPJSError {
  // Handle fetch/axios errors
  if (error?.response) {
    // Axios error
    const { status, data } = error.response;
    if (data?.code) {
      return translateBPJSError(data.code, data.message);
    }
    return translateHttpError(status, data?.message);
  }

  if (error?.status) {
    // Fetch error
    return translateHttpError(error.status, error.statusText);
  }

  if (error?.code) {
    return translateBPJSError(error.code, error.message);
  }

  // Handle network errors
  if (error instanceof TypeError && error.message.includes("fetch")) {
    return translateBPJSError(BPJSErrorCode.CONNECTION_ERROR);
  }

  // Default unknown error
  return {
    code: BPJSErrorCode.UNKNOWN_ERROR,
    type: BPJSErrorType.UNKNOWN,
    title: "Kesalahan Sistem",
    message: error?.message || "Terjadi kesalahan tidak diketahui.",
    suggestion: "Coba lagi atau hubungi administrator.",
    retryable: true,
    userAction: "Coba lagi",
  };
}

// ============================================================================
// RETRY LOGIC
// ============================================================================

export interface RetryOptions {
  maxAttempts?: number;
  initialDelay?: number; // milliseconds
  maxDelay?: number; // milliseconds
  backoffMultiplier?: number;
  shouldRetry?: (error: BPJSError) => boolean;
}

export interface RetryState {
  attempt: number;
  isRetrying: boolean;
  nextRetryIn?: number; // milliseconds until next retry
}

/**
 * Calculate delay with exponential backoff
 */
export function calculateRetryDelay(
  attempt: number,
  options: RetryOptions = {}
): number {
  const {
    initialDelay = 1000,
    maxDelay = 30000,
    backoffMultiplier = 2,
  } = options;

  const delay = Math.min(
    initialDelay * Math.pow(backoffMultiplier, attempt - 1),
    maxDelay
  );

  return delay;
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error: BPJSError): boolean {
  return error.retryable;
}

/**
 * Execute function with retry logic
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxAttempts = 3,
    shouldRetry = isRetryableError,
  } = options;

  let lastError: BPJSError = {
    code: BPJSErrorCode.UNKNOWN_ERROR,
    type: BPJSErrorType.UNKNOWN,
    title: "Kesalahan Sistem",
    message: "Terjadi kesalahan tidak diketahui.",
    suggestion: "Coba lagi atau hubungi administrator.",
    retryable: true,
    userAction: "Coba lagi",
  };

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = translateError(error);

      if (attempt === maxAttempts || !shouldRetry(lastError)) {
        throw lastError;
      }

      const delay = calculateRetryDelay(attempt, options);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError;
}

// ============================================================================
// ERROR SEVERITY
// ============================================================================

export enum ErrorSeverity {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
}

export function getErrorSeverity(error: BPJSError): ErrorSeverity {
  switch (error.type) {
    case BPJSErrorType.NETWORK:
      return ErrorSeverity.MEDIUM;
    case BPJSErrorType.AUTHENTICATION:
      return ErrorSeverity.CRITICAL;
    case BPJSErrorType.AUTHORIZATION:
      return ErrorSeverity.HIGH;
    case BPJSErrorType.VALIDATION:
      return ErrorSeverity.LOW;
    case BPJSErrorType.BUSINESS_LOGIC:
      return ErrorSeverity.MEDIUM;
    case BPJSErrorType.RATE_LIMIT:
      return ErrorSeverity.MEDIUM;
    default:
      return ErrorSeverity.MEDIUM;
  }
}
