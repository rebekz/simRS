"use client";

/**
 * WEB-S-4.6: Patient History Timeline for Consultation Workspace
 *
 * Key Features:
 * - Timeline showing visits, hospitalizations, surgeries
 * - Allergies timeline (when diagnosed, reactions)
 * - Chronic conditions tracking
 * - Medication history visualization
 * - Discontinuation tracking
 */

import { useState, useCallback } from "react";
import {
  Calendar,
  Stethoscope,
  Syringe,
  Shield,
  Pill,
  AlertTriangle,
  Clock,
  User,
  FileText,
  Activity,
  Heart,
  Bone,
  Baby,
  BedDouble,
  Scissors,
  X,
  Filter,
  ChevronDown,
} from "lucide-react";

// ============================================================================
// TYPES
// ============================================================================

export type TimelineEventType =
  | "visit"
  | "hospitalization"
  | "surgery"
  | "allergy"
  | "chronic-condition"
  | "medication"
  | "discontinued"
  | "lab-result"
  | "imaging";

export interface TimelineEvent {
  id: string;
  type: TimelineEventType;
  date: Date;
  title: string;
  details?: string;
  location?: string;
  provider?: string;
  severity?: "mild" | "moderate" | "severe";
  status?: "active" | "resolved" | "chronic";
  metadata?: Record<string, any>;
}

export interface Allergy {
  id: string;
  allergen: string;
  reaction: string;
  severity: "mild" | "moderate" | "severe";
  diagnosedDate: Date;
  diagnosedBy?: string;
  status: "active" | "resolved";
}

export interface ChronicCondition {
  id: string;
  name: string;
  diagnosisDate: Date;
  diagnosedBy: string;
  status: "active" | "resolved" | "controlled";
  medications: string[];
  lastVisit?: Date;
}

export interface MedicationHistory {
  id: string;
  drug: string;
  dose: string;
  frequency: string;
  startDate: Date;
  endDate?: Date;
  prescriber: string;
  indication?: string;
  discontinuedReason?: string;
  status: "active" | "discontinued";
}

export interface PatientTimelineProps {
  patientId: number;
  encounterId?: number;
  events?: TimelineEvent[];
  allergies?: Allergy[];
  chronicConditions?: ChronicCondition[];
  medications?: MedicationHistory[];
  disabled?: boolean;
  onEventClick?: (event: TimelineEvent) => void;
}

// ============================================================================
// MOCK DATA
// ============================================================================

const MOCK_EVENTS: TimelineEvent[] = [
  {
    id: "evt-001",
    type: "visit",
    date: new Date("2026-01-10"),
    title: "Kunjungan Poli Penyakit Dalam",
    details: "Follow-up hipertensi dan diabetes",
    location: "Poli Penyakit Dalam",
    provider: "dr. Ahmad Sp.PD",
  },
  {
    id: "evt-002",
    type: "lab-result",
    date: new Date("2026-01-10"),
    title: "Hasil Lab: HbA1c 7.2%",
    details: "Nilai HbA1c di atas target (target <7%)",
    provider: "Laboratorium RS",
    severity: "moderate",
  },
  {
    id: "evt-003",
    type: "visit",
    date: new Date("2025-12-15"),
    title: "Kunjungan Poli Penyakit Dalam",
    details: "Kontrol rutin diabetes melitus tipe 2",
    location: "Poli Penyakit Dalam",
    provider: "dr. Ahmad Sp.PD",
  },
  {
    id: "evt-004",
    type: "imaging",
    date: new Date("2025-11-20"),
    title: "Foto Thorax PA/AP",
    details: "Hasil: Cor utk, Jantung tidak membesar",
    location: "Radiologi",
  },
  {
    id: "evt-005",
    type: "visit",
    date: new Date("2025-10-05"),
    title: "Kunjungan Poli Mata",
    details: "Keluhan penglihatan kabur",
    location: "Poli Mata",
    provider: "dr. Budi Sp.M",
    status: "resolved",
  },
  {
    id: "evt-006",
    type: "hospitalization",
    date: new Date("2025-08-15"),
    title: "Rawat Inap: Stroke Iskemik",
    details: "Rawat inap 7 hari di stroke unit",
    location: "Bangsal Stroke",
    provider: "dr. Citra Sp.S",
    severity: "severe",
  },
  {
    id: "evt-007",
    type: "surgery",
    date: new Date("2025-08-16"),
    title: "CT Scan Head",
    details: "Imaging untuk konfirmasi diagnosis stroke",
    location: "Radiologi",
    provider: "dr. Dina Sp.R",
  },
  {
    id: "evt-008",
    type: "visit",
    date: new Date("2025-06-10"),
    title: "Kunjungan Poli Gigi",
    details: "Pembersihan karang gigi",
    location: "Poli Gigi",
    provider: "drg. Sara",
  },
  {
    id: "evt-009",
    type: "chronic-condition",
    date: new Date("2024-03-15"),
    title: "Diagnosis: Diabetes Melitus Tipe 2",
    details: "HbA1c awal: 9.5%",
    provider: "dr. Ahmad Sp.PD",
    status: "chronic",
  },
  {
    id: "evt-010",
    type: "chronic-condition",
    date: new Date("2023-10-20"),
    title: "Diagnosis: Hipertensi Esensial",
    details: "Tekanan darah: 160/100 mmHg",
    provider: "dr. Ahmad Sp.PD",
    status: "chronic",
  },
];

const MOCK_ALLERGIES: Allergy[] = [
  {
    id: "allg-001",
    allergen: "Penisilin",
    reaction: "Ruam, gatal, sesak napas",
    severity: "severe",
    diagnosedDate: new Date("2020-05-10"),
    diagnosedBy: "dr. Spesialis Alergi",
    status: "active",
  },
  {
    id: "allg-002",
    allergen: "Seafood (Udang)",
    reaction: "Bengkak bibir, gatal",
    severity: "moderate",
    diagnosedDate: new Date("2019-08-22"),
    diagnosedBy: "dr. Umum",
    status: "active",
  },
];

const MOCK_CHRONIC_CONDITIONS: ChronicCondition[] = [
  {
    id: "chron-001",
    name: "Diabetes Melitus Tipe 2",
    diagnosisDate: new Date("2024-03-15"),
    diagnosedBy: "dr. Ahmad Sp.PD",
    status: "active",
    medications: ["Metformin 500mg", "Sitagliptin 50mg"],
    lastVisit: new Date("2026-01-10"),
  },
  {
    id: "chron-002",
    name: "Hipertensi Esensial",
    diagnosisDate: new Date("2023-10-20"),
    diagnosedBy: "dr. Ahmad Sp.PD",
    status: "controlled",
    medications: ["Amlodipine 10mg", "Captopril 25mg"],
    lastVisit: new Date("2026-01-10"),
  },
  {
    id: "chron-003",
    name: "Dyslipidemia",
    diagnosisDate: new Date("2024-03-15"),
    diagnosedBy: "dr. Ahmad Sp.PD",
    status: "active",
    medications: ["Atorvastatin 20mg"],
    lastVisit: new Date("2026-01-10"),
  },
];

const MOCK_MEDICATIONS: MedicationHistory[] = [
  {
    id: "med-001",
    drug: "Metformin 500mg",
    dose: "500mg",
    frequency: "2x sehari",
    startDate: new Date("2024-03-20"),
    prescriber: "dr. Ahmad Sp.PD",
    indication: "Diabetes Melitus Tipe 2",
    status: "active",
  },
  {
    id: "med-002",
    drug: "Amlodipine 10mg",
    dose: "10mg",
    frequency: "1x sehari",
    startDate: new Date("2023-10-25"),
    prescriber: "dr. Ahmad Sp.PD",
    indication: "Hipertensi",
    status: "active",
  },
  {
    id: "med-003",
    drug: "Sitagliptin 50mg",
    dose: "50mg",
    frequency: "1x sehari",
    startDate: new Date("2024-09-01"),
    endDate: new Date("2025-02-15"),
    prescriber: "dr. Ahmad Sp.PD",
    indication: "Diabetes Mellitus",
    discontinuedReason: "Efek samping gastrointestinal",
    status: "discontinued",
  },
  {
    id: "med-004",
    drug: "Captopril 25mg",
    dose: "25mg",
    frequency: "3x sehari",
    startDate: new Date("2023-11-01"),
    prescriber: "dr. Ahmad Sp.PD",
    indication: "Hipertensi",
    status: "active",
  },
  {
    id: "med-005",
    drug: "Atorvastatin 20mg",
    dose: "20mg",
    frequency: "1x sehari malam",
    startDate: new Date("2024-04-01"),
    prescriber: "dr. Ahmad Sp.PD",
    indication: "Dyslipidemia",
    status: "active",
  },
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getEventIcon(type: TimelineEventType) {
  switch (type) {
    case "visit":
      return Stethoscope;
    case "hospitalization":
      return BedDouble;
    case "surgery":
      return Scissors;
    case "allergy":
      return Shield;
    case "chronic-condition":
      return Activity;
    case "medication":
      return Pill;
    case "discontinued":
      return X;
    case "lab-result":
      return FileText;
    case "imaging":
      return Activity;
    default:
      return Calendar;
  }
}

function getEventColor(type: TimelineEventType) {
  switch (type) {
    case "visit":
      return "bg-blue-100 text-blue-600 border-blue-300";
    case "hospitalization":
      return "bg-red-100 text-red-600 border-red-300";
    case "surgery":
      return "bg-purple-100 text-purple-600 border-purple-300";
    case "allergy":
      return "bg-orange-100 text-orange-600 border-orange-300";
    case "chronic-condition":
      return "bg-amber-100 text-amber-600 border-amber-300";
    case "medication":
      return "bg-green-100 text-green-600 border-green-300";
    case "discontinued":
      return "bg-gray-100 text-gray-600 border-gray-300";
    case "lab-result":
      return "bg-cyan-100 text-cyan-600 border-cyan-300";
    case "imaging":
      return "bg-indigo-100 text-indigo-600 border-indigo-300";
    default:
      return "bg-gray-100 text-gray-600 border-gray-300";
  }
}

function getSeverityColor(severity?: "mild" | "moderate" | "severe") {
  switch (severity) {
    case "mild":
      return "bg-yellow-100 text-yellow-800";
    case "moderate":
      return "bg-orange-100 text-orange-800";
    case "severe":
      return "bg-red-100 text-red-800";
    default:
      return "bg-gray-100 text-gray-800";
  }
}

function getStatusColor(status?: "active" | "resolved" | "controlled" | "chronic") {
  switch (status) {
    case "active":
      return "bg-green-100 text-green-800";
    case "resolved":
      return "bg-gray-100 text-gray-800";
    case "controlled":
      return "bg-blue-100 text-blue-800";
    case "chronic":
      return "bg-amber-100 text-amber-800";
    default:
      return "bg-gray-100 text-gray-800";
  }
}

function formatDate(date: Date): string {
  return date.toLocaleDateString("id-ID", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function formatDateTime(date: Date): string {
  return date.toLocaleDateString("id-ID", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

interface TimelineEventCardProps {
  event: TimelineEvent;
  onClick?: () => void;
}

function TimelineEventCard({ event, onClick }: TimelineEventCardProps) {
  const Icon = getEventIcon(event.type);

  return (
    <div
      onClick={onClick}
      className="relative pl-8 pb-8 border-l-2 border-gray-200 last:border-0 hover:bg-gray-50 p-4 rounded-r-lg cursor-pointer transition-colors group"
    >
      {/* Timeline Dot */}
      <div className={`absolute left-0 top-4 transform -translate-x-1/2 w-10 h-10 rounded-full border-2 flex items-center justify-center ${getEventColor(event.type)} group-hover:scale-110 transition-transform`}>
        <Icon className="w-5 h-5" />
      </div>

      {/* Event Content */}
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="font-semibold text-gray-900">{event.title}</h4>
              {event.severity && (
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${getSeverityColor(event.severity)}`}>
                  {event.severity}
                </span>
              )}
              {event.status && (
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(event.status)}`}>
                  {event.status}
                </span>
              )}
            </div>
            <p className="text-sm text-gray-600 mt-1">{event.details}</p>
            <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {formatDateTime(event.date)}
              </span>
              {event.location && (
                <span className="flex items-center gap-1">
                  <User className="w-3 h-3" />
                  {event.location}
                </span>
              )}
              {event.provider && <span>{event.provider}</span>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

interface AllergyTimelineProps {
  allergies: Allergy[];
}

function AllergyTimeline({ allergies }: AllergyTimelineProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
        <Shield className="w-4 h-4 text-orange-500" />
        Riwayat Alergi ({allergies.length})
      </h3>
      <div className="space-y-3">
        {allergies.map((allergy) => (
          <div key={allergy.id} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-semibold text-gray-900">{allergy.allergen}</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${getSeverityColor(allergy.severity)}`}>
                    {allergy.severity}
                  </span>
                  {allergy.status === "active" && (
                    <span className="px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                      Aktif
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-700 mb-2">
                  <span className="font-medium">Reaksi:</span> {allergy.reaction}
                </p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    Didagnosis: {formatDate(allergy.diagnosedDate)}
                  </span>
                  {allergy.diagnosedBy && <span>Oleh: {allergy.diagnosedBy}</span>}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

interface ChronicConditionsProps {
  conditions: ChronicCondition[];
}

function ChronicConditions({ conditions }: ChronicConditionsProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
        <Activity className="w-4 h-4 text-amber-500" />
        Penyakit Kronis ({conditions.length})
      </h3>
      <div className="space-y-3">
        {conditions.map((condition) => (
          <div key={condition.id} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-start justify-between gap-4 mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-gray-900">{condition.name}</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(condition.status)}`}>
                    {condition.status === "controlled" ? "Terkontrol" : condition.status === "active" ? "Aktif" : condition.status}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-500 mb-2">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    Diagnosis: {formatDate(condition.diagnosisDate)}
                  </span>
                  <span>Oleh: {condition.diagnosedBy}</span>
                  {condition.lastVisit && (
                    <span>Kontrol terakhir: {formatDate(condition.lastVisit)}</span>
                  )}
                </div>
              </div>
            </div>
            <div className="border-t border-gray-100 pt-3">
              <p className="text-xs font-medium text-gray-700 mb-2">Obat saat ini:</p>
              <div className="flex flex-wrap gap-2">
                {condition.medications.map((med, idx) => (
                  <span key={idx} className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 text-green-800 text-xs rounded border border-green-200">
                    <Pill className="w-3 h-3" />
                    {med}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

interface MedicationTimelineProps {
  medications: MedicationHistory[];
}

function MedicationTimeline({ medications }: MedicationTimelineProps) {
  const activeMeds = medications.filter((m) => m.status === "active");
  const discontinuedMeds = medications.filter((m) => m.status === "discontinued");

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
        <Pill className="w-4 h-4 text-green-500" />
        Riwayat Obat ({medications.length})
      </h3>

      {/* Active Medications */}
      {activeMeds.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-xs font-medium text-gray-700">Obat Aktif ({activeMeds.length})</h4>
          {activeMeds.map((med) => (
            <div key={med.id} className="bg-white border border-gray-200 rounded-lg p-3">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Pill className="w-4 h-4 text-green-600" />
                    <span className="font-medium text-gray-900">{med.drug}</span>
                    <span className="text-xs text-gray-600">({med.dose})</span>
                    <span className="text-xs text-gray-600">{med.frequency}</span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      Mulai: {formatDate(med.startDate)}
                    </span>
                    <span>Oleh: {med.prescriber}</span>
                  </div>
                  {med.indication && (
                    <p className="text-xs text-gray-600 mt-1">
                      <span className="font-medium">Indikasi:</span> {med.indication}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Discontinued Medications */}
      {discontinuedMeds.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-xs font-medium text-gray-700 flex items-center gap-1">
            <X className="w-3 h-3" />
            Obat Dihentikan ({discontinuedMeds.length})
          </h4>
          {discontinuedMeds.map((med) => (
            <div key={med.id} className="bg-white border border-gray-200 rounded-lg p-3 opacity-75">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <X className="w-4 h-4 text-gray-500" />
                    <span className="font-medium text-gray-700 line-through">{med.drug}</span>
                    <span className="text-xs text-gray-500 line-through">({med.dose})</span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(med.startDate)} - {formatDate(med.endDate!)}
                    </span>
                  </div>
                  {med.discontinuedReason && (
                    <p className="text-xs text-red-600 mt-1">
                      <span className="font-medium">Alasan:</span> {med.discontinuedReason}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function PatientTimeline({
  patientId,
  encounterId,
  events = MOCK_EVENTS,
  allergies = MOCK_ALLERGIES,
  chronicConditions = MOCK_CHRONIC_CONDITIONS,
  medications = MOCK_MEDICATIONS,
  disabled = false,
  onEventClick,
}: PatientTimelineProps) {
  const [activeTab, setActiveTab] = useState<"timeline" | "allergies" | "conditions" | "medications">("timeline");
  const [filterType, setFilterType] = useState<TimelineEventType | "all">("all");
  const [showFilters, setShowFilters] = useState(false);

  // Filter events by type
  const filteredEvents = filterType === "all" ? events : events.filter((e) => e.type === filterType);

  // Sort events by date (newest first)
  const sortedEvents = [...filteredEvents].sort((a, b) => b.date.getTime() - a.date.getTime());

  const handleEventClick = useCallback(
    (event: TimelineEvent) => {
      if (onEventClick) {
        onEventClick(event);
      }
    },
    [onEventClick]
  );

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab("timeline")}
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
              activeTab === "timeline"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            <Clock className="w-4 h-4" />
            Timeline ({events.length})
          </button>
          <button
            onClick={() => setActiveTab("allergies")}
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
              activeTab === "allergies"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            <Shield className="w-4 h-4" />
            Alergi ({allergies.length})
          </button>
          <button
            onClick={() => setActiveTab("conditions")}
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
              activeTab === "conditions"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            <Activity className="w-4 h-4" />
            Kronis ({chronicConditions.length})
          </button>
          <button
            onClick={() => setActiveTab("medications")}
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
              activeTab === "medications"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            <Pill className="w-4 h-4" />
            Obat ({medications.length})
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "timeline" && (
        <div className="space-y-6">
          {/* Filters */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700">Filter:</span>
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center gap-1 px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm"
              >
                <Filter className="w-4 h-4" />
                {filterType === "all" ? "Semua Tipe" : filterType}
                <ChevronDown className="w-4 h-4" />
              </button>
              {filterType !== "all" && (
                <button
                  onClick={() => setFilterType("all")}
                  className="text-xs text-blue-600 hover:text-blue-700"
                >
                  Reset
                </button>
              )}
            </div>
          </div>

          {/* Filter Dropdown */}
          {showFilters && (
            <div className="absolute z-10 bg-white border border-gray-300 rounded-lg shadow-lg p-2 mt-1">
              <div className="space-y-1">
                <button
                  onClick={() => {
                    setFilterType("all");
                    setShowFilters(false);
                  }}
                  className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded text-sm"
                >
                  Semua Tipe
                </button>
                <button
                  onClick={() => {
                    setFilterType("visit");
                    setShowFilters(false);
                  }}
                  className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded text-sm flex items-center gap-2"
                >
                  <Stethoscope className="w-4 h-4 text-blue-600" />
                  Kunjungan
                </button>
                <button
                  onClick={() => {
                    setFilterType("hospitalization");
                    setShowFilters(false);
                  }}
                  className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded text-sm flex items-center gap-2"
                >
                  <BedDouble className="w-4 h-4 text-red-600" />
                  Rawat Inap
                </button>
                <button
                  onClick={() => {
                    setFilterType("surgery");
                    setShowFilters(false);
                  }}
                  className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded text-sm flex items-center gap-2"
                >
                  <Scissors className="w-4 h-4 text-purple-600" />
                  Tindakan Operasi
                </button>
                <button
                  onClick={() => {
                    setFilterType("lab-result");
                    setShowFilters(false);
                  }}
                  className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded text-sm flex items-center gap-2"
                >
                  <FileText className="w-4 h-4 text-cyan-600" />
                  Hasil Lab
                </button>
                <button
                  onClick={() => {
                    setFilterType("imaging");
                    setShowFilters(false);
                  }}
                  className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded text-sm flex items-center gap-2"
                >
                  <Activity className="w-4 h-4 text-indigo-600" />
                  Radiologi
                </button>
              </div>
            </div>
          )}

          {/* Timeline Events */}
          <div className="space-y-2">
            {sortedEvents.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Clock className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-sm">Tidak ada riwayat medis</p>
              </div>
            ) : (
              sortedEvents.map((event) => (
                <TimelineEventCard
                  key={event.id}
                  event={event}
                  onClick={() => handleEventClick(event)}
                />
              ))
            )}
          </div>
        </div>
      )}

      {activeTab === "allergies" && <AllergyTimeline allergies={allergies} />}
      {activeTab === "conditions" && <ChronicConditions conditions={chronicConditions} />}
      {activeTab === "medications" && <MedicationTimeline medications={medications} />}
    </div>
  );
}

export default PatientTimeline;
