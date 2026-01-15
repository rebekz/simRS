"use client";

import React, { useState } from "react";
import { CheckCircle, XCircle, AlertCircle, Loader2, Search, CreditCard } from "lucide-react";
import { FormInput } from "@/components/ui/form/FormInput";
import { Badge } from "@/components/ui/Badge";
import { BPJSData, BPJSStatus } from "@/types";

/**
 * Mock BPJS VClaim API Response
 * This simulates the BPJS VClaim API response for development/testing
 */
const MOCK_BPJS_RESPONSES: Record<string, BPJSData> = {
  "1234567890123": {
    cardNumber: "1234567890123",
    nama: "AHMAD SUSANTO",
    nik: "3201010101010001",
    jenisPeserta: "PESERTA",
    faskes: "RSUD SEHAT SELALU (KODE: 12345678)",
    status: "active",
    eligibilityDate: new Date("2026-12-31"),
  },
  "9876543210987": {
    cardNumber: "9876543210987",
    nama: "SITI RAHAYU",
    nik: "3202020202020002",
    jenisPeserta: "PESERTA",
    faskes: "RSUD SEHAT SELALU (KODE: 12345678)",
    status: "active",
    eligibilityDate: new Date("2026-06-30"),
  },
  "0000000000000": {
    cardNumber: "0000000000000",
    nama: "UNKNOWN",
    nik: "0000000000000000",
    jenisPeserta: "PESERTA",
    faskes: "FASKES TIDAK DIKETAHUI",
    status: "inactive",
    eligibilityDate: new Date("2024-01-01"),
  },
  "1111111111111": {
    cardNumber: "1111111111111",
    nama: "EXPIRED PATIENT",
    nik: "3203030303030003",
    jenisPeserta: "PESERTA",
    faskes: "RSUD SEHAT SELALU (KODE: 12345678)",
    status: "expired",
    eligibilityDate: new Date("2024-12-31"),
  },
  "2222222222222": {
    cardNumber: "2222222222222",
    nama: "SUSPENDED PATIENT",
    nik: "3204040404040004",
    jenisPeserta: "PBI APBN",
    faskes: "PUSKESMAS JAYA (KODE: 87654321)",
    status: "suspended",
    eligibilityDate: new Date("2025-12-31"),
  },
};

export interface BPJSEligibilityCheckProps {
  onVerified?: (data: BPJSData) => void;
  onError?: (error: string) => void;
  className?: string;
  showAutoFillButton?: boolean;
  disabled?: boolean;
}

/**
 * BPJS Eligibility Check Component
 *
 * Real-time BPJS card verification with:
 * - Card number input with validation
 * - Mock BPJS VClaim API response
 * - Status badge display (active/inactive/expired/suspended)
 * - Patient information display
 * - Auto-fill capability for registration
 */
export function BPJSEligibilityCheck({
  onVerified,
  onError,
  className = "",
  showAutoFillButton = true,
  disabled = false,
}: BPJSEligibilityCheckProps) {
  const [cardNumber, setCardNumber] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [bpjsData, setBpjsData] = useState<BPJSData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isValidCardNumber = (number: string): boolean => {
    // BPJS card number should be 13 digits
    return /^\d{13}$/.test(number);
  };

  const handleVerify = async () => {
    setError(null);
    setBpjsData(null);

    if (!isValidCardNumber(cardNumber)) {
      const errorMsg = "Nomor kartu BPJS harus 13 digit angka";
      setError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    setIsLoading(true);

    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // Check mock data
    const mockData = MOCK_BPJS_RESPONSES[cardNumber];

    if (mockData) {
      setBpjsData(mockData);
      if (mockData.status === "active") {
        onVerified?.(mockData);
      } else {
        const errorMsg = getStatusMessage(mockData.status);
        setError(errorMsg);
        onError?.(errorMsg);
      }
    } else {
      // Default to active status for unknown cards (demo purposes)
      const defaultData: BPJSData = {
        cardNumber,
        nama: `BPJS PESERTA ${cardNumber.slice(-4)}`,
        nik: "32".concat(cardNumber.slice(2, 12)),
        jenisPeserta: "PESERTA",
        faskes: "RSUD SEHAT SELALU (KODE: 12345678)",
        status: "active",
        eligibilityDate: new Date("2026-12-31"),
      };
      setBpjsData(defaultData);
      onVerified?.(defaultData);
    }

    setIsLoading(false);
  };

  const handleReset = () => {
    setCardNumber("");
    setBpjsData(null);
    setError(null);
  };

  const getStatusMessage = (status: BPJSStatus): string => {
    switch (status) {
      case "active":
        return "Kartu BPJS Aktif";
      case "inactive":
        return "Kartu BPJS Tidak Aktif";
      case "expired":
        return "Masa berlaku kartu BPJS telah habis";
      case "suspended":
        return "Keanggotaan BPJS ditangguhkan";
      default:
        return "Status kartu tidak diketahui";
    }
  };

  const getStatusVariant = (status: BPJSStatus): "success" | "error" | "warning" | "neutral" => {
    switch (status) {
      case "active":
        return "success";
      case "inactive":
      case "expired":
      case "suspended":
        return "error";
      default:
        return "neutral";
    }
  };

  const getStatusIcon = (status: BPJSStatus) => {
    switch (status) {
      case "active":
        return <CheckCircle className="w-5 h-5" />;
      case "inactive":
      case "expired":
      case "suspended":
        return <XCircle className="w-5 h-5" />;
      default:
        return <AlertCircle className="w-5 h-5" />;
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <CreditCard className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Verifikasi BPJS</h3>
            <p className="text-sm text-gray-600">Masukkan nomor kartu BPJS untuk verifikasi eligibility</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* Card Number Input */}
        <div className="flex gap-3">
          <FormInput
            label="Nomor Kartu BPJS"
            type="text"
            placeholder="Masukkan 13 digit nomor kartu"
            value={cardNumber}
            onChange={(e) => {
              // Only allow numbers
              const value = e.target.value.replace(/\D/g, "");
              setCardNumber(value);
            }}
            disabled={disabled || isLoading}
            hint="13 digit angka"
            error={error ?? undefined}
            maxLength={13}
            className="flex-1"
          />
          <button
            type="button"
            onClick={handleVerify}
            disabled={disabled || isLoading || !cardNumber}
            className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            Verifikasi
          </button>
        </div>

        {/* Verification Result */}
        {bpjsData && (
          <div className="border-2 border-gray-200 rounded-lg overflow-hidden">
            {/* Status Bar */}
            <div className={`px-6 py-4 flex items-center gap-3 ${
              bpjsData.status === "active" ? "bg-green-50" : "bg-red-50"
            }`}>
              {getStatusIcon(bpjsData.status)}
              <Badge variant={getStatusVariant(bpjsData.status)}>
                {getStatusMessage(bpjsData.status)}
              </Badge>
            </div>

            {/* Patient Information */}
            <div className="p-6 bg-white">
              <h4 className="text-sm font-medium text-gray-900 mb-4">Informasi Peserta</h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Nama Peserta</p>
                  <p className="text-sm font-medium text-gray-900">{bpjsData.nama}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Nomor Kartu</p>
                  <p className="text-sm font-medium text-gray-900">{bpjsData.cardNumber}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">NIK</p>
                  <p className="text-sm font-medium text-gray-900">{bpjsData.nik}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Jenis Peserta</p>
                  <p className="text-sm font-medium text-gray-900">{bpjsData.jenisPeserta}</p>
                </div>
                <div className="md:col-span-2">
                  <p className="text-xs text-gray-500">Faskes Tujuan</p>
                  <p className="text-sm font-medium text-gray-900">{bpjsData.faskes}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Masa Berlaku</p>
                  <p className="text-sm font-medium text-gray-900">
                    {bpjsData.eligibilityDate instanceof Date
                      ? bpjsData.eligibilityDate.toLocaleDateString("id-ID", {
                          day: "numeric",
                          month: "long",
                          year: "numeric",
                        })
                      : new Date(bpjsData.eligibilityDate).toLocaleDateString("id-ID", {
                          day: "numeric",
                          month: "long",
                          year: "numeric",
                        })}
                  </p>
                </div>
              </div>

              {showAutoFillButton && bpjsData.status === "active" && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <button
                    type="button"
                    onClick={() => onVerified?.(bpjsData)}
                    className="w-full px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 flex items-center justify-center gap-2"
                  >
                    <CheckCircle className="w-4 h-4" />
                    Auto-Fill Data Pasien
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Demo Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm font-medium text-blue-900 mb-2">Demo Numbers (Mock Data)</p>
          <ul className="text-xs text-blue-800 space-y-1">
            <li><strong>1234567890123:</strong> AHMAD SUSANTO (Aktif)</li>
            <li><strong>9876543210987:</strong> SITI RAHAYU (Aktif)</li>
            <li><strong>0000000000000:</strong> Inactive</li>
            <li><strong>1111111111111:</strong> Expired</li>
            <li><strong>2222222222222:</strong> Suspended</li>
            <li><strong>Any other 13 digits:</strong> Active (default)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

BPJSEligibilityCheck.displayName = "BPJSEligibilityCheck";
