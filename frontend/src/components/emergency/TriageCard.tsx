"use client";

import { ReactNode } from "react";
import { AlertTriangle, Clock, Activity } from "lucide-react";

/**
 * WEB-S-5.4: Triage Result Display
 *
 * Large, color-coded triage cards for emergency department triage.
 * Supports MERAH (red), KUNING (yellow), HIJAU (green) triage levels.
 */

export type TriageLevel = "merah" | "kuning" | "hijau";

export interface TriageCardProps {
  level: TriageLevel;
  size?: "small" | "medium" | "large";
  description?: string;
  recommendations?: TriageRecommendation[];
  estimatedWait?: string;
  onAction?: (action: string) => void;
  patientName?: string;
  queueNumber?: string;
}

interface TriageRecommendation {
  priority: "critical" | "warning" | "info";
  icon?: string;
  text: string;
}

const TRIAGE_CONFIG = {
  merah: {
    color: "bg-red-600",
    borderColor: "border-red-800",
    textColor: "text-red-600",
    lightColor: "bg-red-50",
    description: "EMERGENSI - Pasien memerlukan perhatian segera",
    waitTime: "Segera (0 menit)",
    recommendations: [
      { priority: "critical", icon: "🚨", text: "Pasang di Resusitasi" },
      { priority: "critical", icon: "❤️", text: "Pantau ECG Kontinyu" },
      { priority: "critical", icon: "💉", text: "Akses IV Tambah" },
    ],
  },
  kuning: {
    color: "bg-yellow-500",
    borderColor: "border-yellow-700",
    textColor: "text-yellow-600",
    lightColor: "bg-yellow-50",
    description: "URGENT - Pasien memerlukan pemeriksaan segera",
    waitTime: "<15 menit",
    recommendations: [
      { priority: "warning", icon: "⏱️", text: "Prioritaskan pemeriksaan" },
      { priority: "warning", icon: "👀", text: "Pantau tanda vital berkala" },
    ],
  },
  hijau: {
    color: "bg-green-600",
    borderColor: "border-green-800",
    textColor: "text-green-600",
    lightColor: "bg-green-50",
    description: "STABIL - Pasien dapat menunggu",
    waitTime: "30-60 menit",
    recommendations: [
      { priority: "info", icon: "🪑", text: "Pasang di ruang tunggu" },
      { priority: "info", icon: "📋", text: "Antri sesuai nomor" },
    ],
  },
};

export function TriageCard({
  level,
  size = "large",
  description,
  recommendations,
  estimatedWait,
  onAction,
  patientName,
  queueNumber,
}: TriageCardProps) {
  const config = TRIAGE_CONFIG[level];
  const sizeClasses = {
    small: "w-32 h-32",
    medium: "w-48 h-48",
    large: "w-64 h-64",
  };

  return (
    <div className={`${config.lightColor} ${config.borderColor} border-4 rounded-2xl p-6 shadow-lg`}>
      {/* Triage Level Badge */}
      <div
        className={`${config.color} ${sizeClasses[size]} rounded-xl flex items-center justify-center mb-4 shadow-md`}
      >
        <div className="text-center text-white">
          <div className="text-4xl font-black">{level.toUpperCase()}</div>
          {size === "large" && (
            <div className="text-sm mt-2 opacity-90">TRIAGE</div>
          )}
        </div>
      </div>

      {/* Description */}
      <p className="text-lg font-semibold text-gray-800 mb-2">
        {description || config.description}
      </p>

      {/* Patient Info */}
      {patientName && (
        <div className="mb-3">
          <div className="text-sm text-gray-600">Nama Pasien</div>
          <div className="font-semibold text-gray-900">{patientName}</div>
        </div>
      )}

      {queueNumber && (
        <div className="mb-3">
          <div className="text-sm text-gray-600">Nomor Antrian</div>
          <div className="font-bold text-2xl text-gray-900">{queueNumber}</div>
        </div>
      )}

      {/* Estimated Wait Time */}
      {estimatedWait && (
        <div className="flex items-center gap-2 mb-4 text-gray-700">
          <Clock className="w-4 h-4" />
          <span className="font-medium">Estimasi: {estimatedWait || config.waitTime}</span>
        </div>
      )}

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="space-y-2 mb-4">
          <div className="text-sm font-semibold text-gray-700 mb-2">
            Rekomendasi:
          </div>
          {recommendations.map((rec, index) => (
            <div
              key={index}
              className={`flex items-start gap-2 p-2 rounded-lg ${
                rec.priority === "critical"
                  ? "bg-red-100 border-l-4 border-red-600"
                  : rec.priority === "warning"
                  ? "bg-yellow-100 border-l-4 border-yellow-600"
                  : "bg-gray-100 border-l-4 border-gray-600"
              }`}
            >
              {rec.icon && <span className="text-xl">{rec.icon}</span>}
              <span className="text-sm font-medium text-gray-800">{rec.text}</span>
            </div>
          ))}
        </div>
      )}

      {/* Quick Actions */}
      {onAction && level === "merah" && (
        <div className="space-y-2">
          <button
            onClick={() => onAction("code-blue")}
            className="w-full px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 font-medium flex items-center justify-center gap-2 shadow-md"
          >
            <Activity className="w-4 h-4" />
            AKTIVASI KODE BIRU
          </button>
          <button
            onClick={() => onAction("assign-bed")}
            className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium flex items-center justify-center gap-2"
          >
            Pasang di Ruang Resusitasi
          </button>
        </div>
      )}
    </div>
  );
}

export interface TriageTicketProps {
  hospitalName: string;
  triageLevel: TriageLevel;
  patientName: string;
  queueNumber: string;
  timestamp?: string;
}

export function TriageTicket({
  hospitalName,
  triageLevel,
  patientName,
  queueNumber,
  timestamp = new Date().toLocaleString("id-ID"),
}: TriageTicketProps) {
  const config = TRIAGE_CONFIG[triageLevel];

  return (
    <div className="bg-white p-8 rounded-lg shadow-xl max-w-md mx-auto border-2 border-gray-300">
      {/* Header */}
      <div className="text-center mb-6 border-b pb-4">
        <h1 className="text-2xl font-bold text-gray-900">{hospitalName}</h1>
        <p className="text-sm text-gray-600 mt-1">Tiket Triage Gawat Darurat</p>
      </div>

      {/* Triage Level */}
      <div className={`${config.color} text-white text-center py-6 rounded-lg mb-6`}>
        <div className="text-5xl font-black">{triageLevel.toUpperCase()}</div>
      </div>

      {/* Patient Info */}
      <div className="space-y-3 mb-6">
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Nama Pasien:</span>
          <span className="font-semibold text-gray-900">{patientName}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Nomor Antrian:</span>
          <span className="font-bold text-2xl text-gray-900">{queueNumber}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Waktu:</span>
          <span className="text-gray-900">{timestamp}</span>
        </div>
      </div>

      {/* Barcode (simplified - just a visual placeholder) */}
      <div className="border-t pt-4 text-center">
        <div className="flex justify-center gap-px mb-2">
          {[...Array(40)].map((_, i) => (
            <div
              key={i}
              className="w-1 bg-black"
              style={{ height: i % 3 === 0 ? "40px" : i % 2 === 0 ? "30px" : "20px" }}
            />
          ))}
        </div>
        <p className="text-xs text-gray-500">{queueNumber}</p>
      </div>

      {/* Footer */}
      <div className="text-center mt-6 text-xs text-gray-500">
        Simpan tiket ini sebagai bukti pendaftaran triage
      </div>
    </div>
  );
}

export interface TriageDisplayProps {
  triageLevel: TriageLevel;
  patientName: string;
  queueNumber: string;
  hospitalName?: string;
  showTicket?: boolean;
  onAction?: (action: string) => void;
}

export function TriageDisplay({
  triageLevel,
  patientName,
  queueNumber,
  hospitalName = "RS SIMRS",
  showTicket = false,
  onAction,
}: TriageDisplayProps) {
  return (
    <div className="space-y-6">
      {/* Main Triage Card */}
      <TriageCard
        level={triageLevel}
        patientName={patientName}
        queueNumber={queueNumber}
        onAction={onAction}
      />

      {/* Print Ticket (when shown) */}
      {showTicket && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-900">Tiket Triage</h3>
          <TriageTicket
            hospitalName={hospitalName}
            triageLevel={triageLevel}
            patientName={patientName}
            queueNumber={queueNumber}
          />
        </div>
      )}
    </div>
  );
}
