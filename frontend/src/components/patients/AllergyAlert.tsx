"use client";

/**
 * Allergy Alert Banner Component for STORY-013
 *
 * Displays prominent allergy alerts for patient safety.
 * Always visible in patient header to prevent adverse reactions.
 */

import { AlertTriangle, X } from "lucide-react";

// Types
interface Allergy {
  id: number;
  allergy_type: string;
  allergen: string;
  severity: "mild" | "moderate" | "severe" | "life_threatening";
  reaction: string;
}

interface AllergyAlertProps {
  allergies: Allergy[];
  onDismiss?: () => void;
}

export function AllergyAlert({ allergies, onDismiss }: AllergyAlertProps) {
  if (allergies.length === 0) {
    return null;
  }

  // Sort by severity (life_threatening first)
  const severityOrder = {
    life_threatening: 0,
    severe: 1,
    moderate: 2,
    mild: 3,
  };

  const sortedAllergies = [...allergies].sort(
    (a, b) => severityOrder[a.severity] - severityOrder[b.severity]
  );

  const hasLifeThreatening = sortedAllergies.some((a) => a.severity === "life_threatening");
  const hasSevere = sortedAllergies.some((a) => a.severity === "severe");

  // Determine alert color based on highest severity
  const alertColor = hasLifeThreatening
    ? "bg-red-100 border-red-500 text-red-900"
    : hasSevere
    ? "bg-orange-100 border-orange-500 text-orange-900"
    : "bg-yellow-100 border-yellow-500 text-yellow-900";

  const iconColor = hasLifeThreatening ? "text-red-600" : hasSevere ? "text-orange-600" : "text-yellow-600";

  const getSeverityLabel = (severity: string) => {
    switch (severity) {
      case "life_threatening":
        return "Mengancam Jiwa";
      case "severe":
        return "Parah";
      case "moderate":
        return "Sedang";
      case "mild":
        return "Ringan";
      default:
        return severity;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case "drug":
        return "Obat";
      case "food":
        return "Makanan";
      case "environmental":
        return "Lingkungan";
      default:
        return type;
    }
  };

  return (
    <div className={`${alertColor} border-l-4 p-4 rounded-r-lg`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <AlertTriangle className={`h-6 w-6 ${iconColor} flex-shrink-0 mt-0.5`} />
          <div className="flex-1">
            <h3 className="text-lg font-bold mb-2">
              {hasLifeThreatening
                ? "PERINGATAN ALERGI YANG MENGANCAM JIWA"
                : "Alergi Terdokumentasi"}
            </h3>
            <div className="space-y-2">
              {sortedAllergies.map((allergy) => (
                <div
                  key={allergy.id}
                  className="bg-white bg-opacity-50 rounded-lg p-3"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 flex-wrap gap-1">
                        <span className="font-semibold">{allergy.allergen}</span>
                        <span className="text-xs px-2 py-0.5 rounded-full bg-white bg-opacity-70">
                          {getTypeLabel(allergy.allergy_type)}
                        </span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${
                            allergy.severity === "life_threatening"
                              ? "bg-red-200 text-red-800"
                              : allergy.severity === "severe"
                              ? "bg-orange-200 text-orange-800"
                              : "bg-yellow-200 text-yellow-800"
                          }`}
                        >
                          {getSeverityLabel(allergy.severity)}
                        </span>
                      </div>
                      <p className="text-sm mt-1">{allergy.reaction}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {hasLifeThreatening && (
              <p className="text-sm font-semibold mt-3">
                ⚠️ Hati-hati: Pemeriksaan ulang diperlukan sebelum memberikan pengobatan
              </p>
            )}
          </div>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="p-1 hover:bg-white hover:bg-opacity-30 rounded-full"
            aria-label="Dismiss alert"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>
    </div>
  );
}
