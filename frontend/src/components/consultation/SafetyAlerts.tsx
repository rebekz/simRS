"use client";

/**
 * WEB-S-4.7: Allergy & Medication Alerts for Consultation Workspace
 *
 * Key Features:
 * - Prominent allergy alerts (cannot be dismissed)
 * - Medication interaction warnings (require confirmation)
 * - Duplicate therapy warnings
 * - Contraindication alerts (drug-disease)
 * - Dose adjustment alerts (renal/hepatic impairment)
 * - Alerts block prescription submission until acknowledged
 */

import { useState, useCallback, useMemo } from "react";
import {
  Shield,
  ShieldAlert,
  Ban,
  AlertTriangle,
  AlertCircle,
  Check,
  X,
  Activity,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

// ============================================================================
// TYPES
// ============================================================================

export type AlertSeverity = "critical" | "severe" | "moderate" | "mild";
export type AlertType = "allergy" | "interaction" | "duplicate" | "contraindication" | "dose-adjustment";

export interface SafetyAlert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  title: string;
  message: string;
  details?: string;
  recommendation?: string;
  requiresAcknowledgment: boolean;
  acknowledged?: boolean;
  canDismiss?: boolean;
  metadata?: Record<string, any>;
}

export interface PatientAllergy {
  id: string;
  allergen: string;
  reaction: string;
  severity: "mild" | "moderate" | "severe";
}

export interface MedicationInteraction {
  id: string;
  drug1: string;
  drug2: string;
  severity: "severe" | "moderate" | "mild";
  effect: string;
  recommendation?: string;
}

export interface DuplicateTherapy {
  id: string;
  drug: string;
  count: number;
  medications: Array<{ id: string; name: string; dose: string }>;
}

export interface Contraindication {
  id: string;
  drug: string;
  condition: string;
  severity: "severe" | "moderate";
  recommendation?: string;
}

export interface DoseAdjustment {
  id: string;
  drug: string;
  condition: "renal" | "hepatic";
  impairment: "mild" | "moderate" | "severe";
  currentDose: string;
  recommendedDose: string;
  reason: string;
}

export interface SafetyAlertsProps {
  patientId: number;
  encounterId?: number;
  patientAllergies?: PatientAllergy[];
  currentMedications?: Array<{ id: string; name: string; dose: string }>;
  newMedications?: Array<{ id: string; name: string; dose: string }>;
  patientDiagnoses?: string[];
  renalImpairment?: "none" | "mild" | "moderate" | "severe";
  hepaticImpairment?: "none" | "mild" | "moderate" | "severe";
  onAlertsChange?: (alerts: SafetyAlert[]) => void;
  disabled?: boolean;
}

// ============================================================================
// MOCK DATA
// ============================================================================

const MOCK_INTERACTIONS: MedicationInteraction[] = [
  {
    id: "int-001",
    drug1: "ACE Inhibitor",
    drug2: "NSAID",
    severity: "moderate",
    effect: "Increased risk of renal impairment and hyperkalemia",
    recommendation: "Pertimbangkan alternatif analgesik atau monitor fungsi ginjal",
  },
];

const MOCK_DUPLICATES: DuplicateTherapy[] = [
  {
    id: "dup-001",
    drug: "Metformin",
    count: 2,
    medications: [
      { id: "med-001", name: "Metformin 500mg", dose: "500mg 2x sehari" },
      { id: "med-002", name: "Metformin XR", dose: "500mg 1x sehari" },
    ],
  },
];

const MOCK_CONTRAINDICATIONS: Contraindication[] = [
  {
    id: "contra-001",
    drug: "Ibuprofen",
    condition: "Hipertensi Grade 3",
    severity: "moderate",
    recommendation: "Gunakan alternatif analgesik yang tidak meningkatkan tekanan darah",
  },
];

const MOCK_DOSE_ADJUSTMENTS: DoseAdjustment[] = [
  {
    id: "dose-001",
    drug: "Metformin",
    condition: "renal",
    impairment: "moderate",
    currentDose: "500mg 2x sehari",
    recommendedDose: "500mg 1x sehari",
    reason: "eGFR 45-59 mL/min/1.73m²",
  },
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getAlertColor(severity: AlertSeverity) {
  switch (severity) {
    case "critical":
      return "bg-red-50 border-l-4 border-red-600 text-red-900";
    case "severe":
      return "bg-orange-50 border-l-4 border-orange-600 text-orange-900";
    case "moderate":
      return "bg-yellow-50 border-l-4 border-yellow-600 text-yellow-900";
    case "mild":
      return "bg-blue-50 border-l-4 border-blue-600 text-blue-900";
    default:
      return "bg-gray-50 border-l-4 border-gray-600 text-gray-900";
  }
}

function getAlertIcon(type: AlertType, severity: AlertSeverity) {
  switch (type) {
    case "allergy":
      return ShieldAlert;
    case "interaction":
      return AlertTriangle;
    case "duplicate":
      return AlertTriangle;
    case "contraindication":
      return Ban;
    case "dose-adjustment":
      return Activity;
    default:
      return AlertCircle;
  }
}

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

interface SafetyAlertCardProps {
  alert: SafetyAlert;
  onAcknowledge?: (id: string) => void;
  onDismiss?: (id: string) => void;
}

function SafetyAlertCard({ alert, onAcknowledge, onDismiss }: SafetyAlertCardProps) {
  const AlertIcon = getAlertIcon(alert.type, alert.severity);

  return (
    <div className={`p-4 rounded-lg ${getAlertColor(alert.severity)} mb-3`}>
      <div className="flex items-start gap-3">
        <AlertIcon className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
          alert.severity === "critical" ? "text-red-600" :
          alert.severity === "severe" ? "text-orange-600" :
          alert.severity === "moderate" ? "text-yellow-600" :
          "text-blue-600"
        }`} />

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className="text-sm font-bold">{alert.title}</h4>
            {alert.canDismiss && onDismiss && (
              <button
                type="button"
                onClick={() => onDismiss(alert.id)}
                className="p-1 hover:bg-black/10 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <p className="text-sm mt-1">{alert.message}</p>

          {alert.details && (
            <p className="text-xs mt-2 opacity-80">{alert.details}</p>
          )}

          {alert.recommendation && (
            <div className="mt-3 p-2 bg-black/5 rounded">
              <p className="text-xs font-medium">
                💡 Rekomendasi: {alert.recommendation}
              </p>
            </div>
          )}

          {alert.requiresAcknowledgment && !alert.canDismiss && (
            <div className="mt-3 flex items-center gap-3">
              {alert.acknowledged ? (
                <div className="flex items-center gap-2 text-xs font-medium text-green-800 bg-green-100 px-3 py-1.5 rounded-full">
                  <Check className="w-3 h-3" />
                  Dikonfirmasi
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => onAcknowledge?.(alert.id)}
                  className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 border border-current rounded-lg text-sm font-medium"
                >
                  Saya memahami risiko ini
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function SafetyAlerts({
  patientId,
  encounterId,
  patientAllergies = [],
  currentMedications = [],
  newMedications = [],
  patientDiagnoses = [],
  renalImpairment = "none",
  hepaticImpairment = "none",
  onAlertsChange,
  disabled = false,
}: SafetyAlertsProps) {
  const [alerts, setAlerts] = useState<SafetyAlert[]>([]);
  const [acknowledged, setAcknowledged] = useState<Set<string>>(new Set());
  const [expanded, setExpanded] = useState<boolean>(true);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  // Generate alerts whenever dependencies change
  useMemo(() => {
    const generatedAlerts: SafetyAlert[] = [];

    // 1. Allergy Alerts (CRITICAL - always show, cannot dismiss)
    if (patientAllergies.length > 0) {
      patientAllergies.forEach((allergy) => {
        generatedAlerts.push({
          id: `allergy-${allergy.id}`,
          type: "allergy",
          severity: allergy.severity === "severe" ? "critical" : "severe",
          title: `ALERGI ${allergy.allergen.toUpperCase()}`,
          message: `Pasien memiliki alergi terhadap ${allergy.allergen}`,
          details: `Reaksi: ${allergy.reaction}`,
          requiresAcknowledgment: true,
          canDismiss: false,
        });
      });
    }

    // 2. Medication Interactions (require acknowledgment)
    if (currentMedications.length >= 2) {
      MOCK_INTERACTIONS.forEach((interaction) => {
        const isAcked = acknowledged.has(interaction.id);
        generatedAlerts.push({
          id: interaction.id,
          type: "interaction",
          severity: interaction.severity === "severe" ? "severe" : "moderate",
          title: "Interaksi Obat Terdeteksi",
          message: `${interaction.drug1} ↔ ${interaction.drug2}`,
          details: interaction.effect,
          recommendation: interaction.recommendation,
          requiresAcknowledgment: true,
          canDismiss: false,
          acknowledged: isAcked,
        });
      });
    }

    // 3. Duplicate Therapy Warnings
    if (newMedications.length > 0) {
      MOCK_DUPLICATES.forEach((duplicate) => {
        const hasDuplicateInNew = newMedications.some((med) =>
          med.name.toLowerCase().includes(duplicate.drug.toLowerCase())
        );

        if (hasDuplicateInNew) {
          generatedAlerts.push({
            id: duplicate.id,
            type: "duplicate",
            severity: "moderate",
            title: "Duplikat Terapi Terdeteksi",
            message: `${duplicate.drug} ada di ${duplicate.count} obat yang diresepkan`,
            details: duplicate.medications.map((m) => m.name).join(", "),
            recommendation: "Hapus salah satu obat duplikat sebelum melanjutkan",
            requiresAcknowledgment: true,
            canDismiss: false,
          });
        }
      });
    }

    // 4. Contraindication Alerts (CRITICAL)
    MOCK_CONTRAINDICATIONS.forEach((contra) => {
      const hasContraindication = newMedications.some((med) =>
        med.name.toLowerCase().includes(contra.drug.toLowerCase())
      );

      if (hasContraindication) {
        generatedAlerts.push({
          id: contra.id,
          type: "contraindication",
          severity: contra.severity === "severe" ? "critical" : "severe",
          title: "KONTRAINDIKASI",
          message: `${contra.drug} tidak boleh digunakan untuk ${contra.condition}`,
          recommendation: contra.recommendation,
          requiresAcknowledgment: true,
          canDismiss: false,
        });
      }
    });

    // 5. Dose Adjustment Alerts
    if (renalImpairment !== "none" || hepaticImpairment !== "none") {
      MOCK_DOSE_ADJUSTMENTS.forEach((adjustment) => {
        const needsAdjustment = newMedications.some((med) =>
          med.name.toLowerCase().includes(adjustment.drug.toLowerCase())
        );

        if (needsAdjustment) {
          generatedAlerts.push({
            id: adjustment.id,
            type: "dose-adjustment",
            severity: "moderate",
            title: `Penyesuaian Dosis Diperlukan`,
            message: `Dose ${adjustment.drug} perlu disesuaikan untuk gangguan ${adjustment.condition === "renal" ? "ginjal" : "hati"}`,
            details: `Kondisi: ${adjustment.impairment} (${adjustment.reason})`,
            recommendation: `${adjustment.currentDose} → ${adjustment.recommendedDose}`,
            requiresAcknowledgment: true,
            canDismiss: false,
          });
        }
      });
    }

    setAlerts(generatedAlerts);
    onAlertsChange?.(generatedAlerts);
  }, [patientAllergies, currentMedications, newMedications, patientDiagnoses, renalImpairment, hepaticImpairment, acknowledged, onAlertsChange]);

  // ============================================================================
  // COMPUTED VALUES
  // ============================================================================

  const criticalAlerts = alerts.filter((a) => a.severity === "critical");
  const unacknowledgedRequired = alerts.filter((a) => a.requiresAcknowledgment && !a.acknowledged && !a.canDismiss);
  const canSubmitPrescription = unacknowledgedRequired.length === 0;

  // Group alerts by severity
  const alertSummary = {
    critical: alerts.filter((a) => a.severity === "critical").length,
    severe: alerts.filter((a) => a.severity === "severe").length,
    moderate: alerts.filter((a) => a.severity === "moderate").length,
    mild: alerts.filter((a) => a.severity === "mild").length,
  };

  // ============================================================================
  // HANDLERS
  // ============================================================================

  const handleAcknowledge = useCallback(
    (alertId: string) => {
      setAcknowledged((prev) => new Set(prev).add(alertId));
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, acknowledged: true } : a))
      );
    },
    []
  );

  const handleDismiss = useCallback(
    (alertId: string) => {
      setAlerts((prev) => prev.filter((a) => a.id !== alertId));
    },
    []
  );

  // ============================================================================
  // RENDER
  // ============================================================================

  // No alerts - show patient is clear
  if (alerts.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center gap-2">
          <Check className="w-5 h-5 text-green-600" />
          <span className="text-sm font-medium text-green-900">
            Tidak ada peringatan keamanan untuk pasien ini
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary Bar */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <Shield className="w-5 h-5 text-orange-500" />
            <span className="font-semibold text-gray-900">
              Peringatan Keamanan ({alerts.length})
            </span>
            <div className="flex items-center gap-2 text-xs">
              {alertSummary.critical > 0 && (
                <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full font-medium">
                  {alertSummary.critical} Kritis
                </span>
              )}
              {alertSummary.severe > 0 && (
                <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded-full font-medium">
                  {alertSummary.severe} Berat
                </span>
              )}
              {alertSummary.moderate > 0 && (
                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full font-medium">
                  {alertSummary.moderate} Sedang
                </span>
              )}
            </div>
          </div>
          {expanded ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </button>

        {/* Required Acknowledgment Warning */}
        {!canSubmitPrescription && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded text-sm">
            <div className="flex items-center gap-2 text-red-900 font-medium">
              <Ban className="w-4 h-4" />
              Tindakan Diperlukan
            </div>
            <p className="text-red-800 mt-1">
              Mohon konfirmasi semua peringatan sebelum mengirim resep
            </p>
          </div>
        )}
      </div>

      {/* Expanded Alerts */}
      {expanded && (
        <div className="space-y-2">
          {/* Critical Alerts Section */}
          {criticalAlerts.length > 0 && (
            <div className="bg-red-50 border-2 border-red-300 rounded-lg p-3 mb-4">
              <div className="flex items-center gap-2 text-red-900 font-bold mb-3">
                <ShieldAlert className="w-5 h-5" />
                PERINGATAN KRITIS - Harap Perhatikan
              </div>
              <div className="space-y-2">
                {criticalAlerts.map((alert) => (
                  <SafetyAlertCard
                    key={alert.id}
                    alert={alert}
                    onAcknowledge={handleAcknowledge}
                    onDismiss={handleDismiss}
                  />
                ))}
              </div>
            </div>
          )}

          {/* All Other Alerts */}
          {alerts
            .filter((a) => a.severity !== "critical")
            .map((alert) => (
              <SafetyAlertCard
                key={alert.id}
                alert={alert}
                onAcknowledge={handleAcknowledge}
                onDismiss={handleDismiss}
              />
            ))}
        </div>
      )}
    </div>
  );
}

export default SafetyAlerts;
