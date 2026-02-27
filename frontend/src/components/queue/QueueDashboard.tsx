"use client";

import { useState, useEffect, useMemo } from "react";
import {
  Users,
  Clock,
  User,
  Phone,
  Baby,
  Accessibility,
  AlertTriangle,
  Bell,
  CheckCircle,
  XCircle,
  Download,
  RefreshCw,
  Timer,
  Calendar,
} from "lucide-react";

/**
 * WEB-S-3.3: Queue Management Dashboard Components
 *
 * Reusable components for queue management across the SIMRS application.
 */

// ============================================================================
// TYPES
// ============================================================================

export type QueueStatus = "waiting" | "in-service" | "completed" | "skipped";

export type PriorityType = "elderly" | "pregnant" | "disabled" | "emergency";

export type TriageLevel = "merah" | "kuning" | "hijau";

export interface QueuePatient {
  id: string;
  rmNumber: string;
  name: string;
  queueNumber: string;
  department: string;
  status: QueueStatus;
  checkInTime: string;
  waitTime: string;
  age: number;
  priorities: PriorityType[];
  triageLevel?: TriageLevel;
  phone?: string;
}

export interface Department {
  value: string;
  label: string;
  color: string;
  priority?: boolean;
}

export interface QueueStatistics {
  waiting: number;
  inService: number;
  completed: number;
  avgWaitTime: string;
}

export interface QueueDashboardProps {
  patients: QueuePatient[];
  departments: Department[];
  onCallNext?: (patient: QueuePatient) => void;
  onUpdateStatus?: (patientId: string, status: QueueStatus) => void;
  onRefresh?: () => void;
  onExportPDF?: () => void;
  defaultDepartment?: string;
  className?: string;
}

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

/**
 * Status Badge Component
 */
export function StatusBadge({ status }: { status: QueueStatus }) {
  const getStatusConfig = () => {
    switch (status) {
      case "waiting":
        return {
          label: "Menunggu",
          bgClass: "bg-yellow-100",
          textClass: "text-yellow-700",
          borderClass: "border-yellow-300",
          icon: <Clock className="w-3 h-3" />,
        };
      case "in-service":
        return {
          label: "Sedang Diperiksa",
          bgClass: "bg-blue-100",
          textClass: "text-blue-700",
          borderClass: "border-blue-300",
          icon: <Timer className="w-3 h-3" />,
        };
      case "completed":
        return {
          label: "Selesai",
          bgClass: "bg-green-100",
          textClass: "text-green-700",
          borderClass: "border-green-300",
          icon: <CheckCircle className="w-3 h-3" />,
        };
      case "skipped":
        return {
          label: "Dilewati",
          bgClass: "bg-gray-100",
          textClass: "text-gray-700",
          borderClass: "border-gray-300",
          icon: <XCircle className="w-3 h-3" />,
        };
    }
  };

  const config = getStatusConfig();

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-full border-2 text-xs font-medium ${config.bgClass} ${config.textClass} ${config.borderClass}`}
    >
      {config.icon}
      <span>{config.label}</span>
    </span>
  );
}

/**
 * Priority Badge Component
 */
export function PriorityBadge({ type }: { type: PriorityType }) {
  const getPriorityConfig = () => {
    switch (type) {
      case "elderly":
        return {
          label: "Lansia",
          bgClass: "bg-purple-100",
          textClass: "text-purple-700",
          borderClass: "border-purple-300",
          icon: <User className="w-3 h-3" />,
        };
      case "pregnant":
        return {
          label: "Hamil",
          bgClass: "bg-pink-100",
          textClass: "text-pink-700",
          borderClass: "border-pink-300",
          icon: <Baby className="w-3 h-3" />,
        };
      case "disabled":
        return {
          label: "Disabilitas",
          bgClass: "bg-indigo-100",
          textClass: "text-indigo-700",
          borderClass: "border-indigo-300",
          icon: <Accessibility className="w-3 h-3" />,
        };
      case "emergency":
        return {
          label: "DARURAT",
          bgClass: "bg-red-100",
          textClass: "text-red-700",
          borderClass: "border-red-300",
          icon: <AlertTriangle className="w-3 h-3" />,
        };
    }
  };

  const config = getPriorityConfig();

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-full border-2 text-xs font-medium ${config.bgClass} ${config.textClass} ${config.borderClass}`}
    >
      {config.icon}
      <span>{config.label}</span>
    </span>
  );
}

/**
 * Triage Badge Component (for Emergency)
 */
export function TriageBadge({ level }: { level: TriageLevel }) {
  const getTriageConfig = () => {
    switch (level) {
      case "merah":
        return {
          label: "MERAH",
          bgClass: "bg-red-600",
          textClass: "text-white",
        };
      case "kuning":
        return {
          label: "KUNING",
          bgClass: "bg-yellow-500",
          textClass: "text-white",
        };
      case "hijau":
        return {
          label: "HIJAU",
          bgClass: "bg-green-500",
          textClass: "text-white",
        };
    }
  };

  const config = getTriageConfig();

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold ${config.bgClass} ${config.textClass}`}
    >
      <AlertTriangle className="w-3 h-3" />
      <span>{config.label}</span>
    </span>
  );
}

/**
 * Department Tabs Component
 */
export function DepartmentTabs({
  departments,
  selectedDepartment,
  onSelect,
  queueData,
}: {
  departments: Department[];
  selectedDepartment: string;
  onSelect: (dept: string) => void;
  queueData: QueuePatient[];
}) {
  const departmentCounts = useMemo(() => {
    return departments.map((dept) => ({
      ...dept,
      count: queueData.filter(
        (p) => p.department === dept.value && p.status !== "completed" && p.status !== "skipped"
      ).length,
    }));
  }, [departments, queueData]);

  return (
    <div className="bg-white rounded-xl shadow-md p-2 mb-6">
      <div className="flex gap-2 overflow-x-auto">
        {departmentCounts.map((dept) => (
          <button
            key={dept.value}
            type="button"
            onClick={() => onSelect(dept.value)}
            className={`flex-1 min-w-[150px] px-4 py-3 rounded-lg font-medium transition-all ${
              selectedDepartment === dept.value
                ? "bg-blue-600 text-white shadow-md"
                : "bg-gray-50 text-gray-700 hover:bg-gray-100"
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <span>{dept.label}</span>
              <span
                className={`px-2 py-1 rounded-full text-xs font-bold ${
                  selectedDepartment === dept.value
                    ? "bg-white bg-opacity-20"
                    : "bg-gray-200 text-gray-700"
                }`}
              >
                {dept.count}
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

/**
 * Queue Statistics Cards Component
 */
export function QueueStatisticsCards({ statistics }: { statistics: QueueStatistics }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Menunggu</p>
            <p className="text-3xl font-bold text-yellow-600">{statistics.waiting}</p>
          </div>
          <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
            <Clock className="w-6 h-6 text-yellow-600" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Sedang Diperiksa</p>
            <p className="text-3xl font-bold text-blue-600">{statistics.inService}</p>
          </div>
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <Timer className="w-6 h-6 text-blue-600" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Selesai</p>
            <p className="text-3xl font-bold text-green-600">{statistics.completed}</p>
          </div>
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <CheckCircle className="w-6 h-6 text-green-600" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Rata-rata Tunggu</p>
            <p className="text-3xl font-bold text-purple-600">{statistics.avgWaitTime}</p>
          </div>
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <Users className="w-6 h-6 text-purple-600" />
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Queue Item Component
 */
export function QueueItem({
  patient,
  onCallPatient,
  onUpdateStatus,
  onSkip,
}: {
  patient: QueuePatient;
  onCallPatient?: (patient: QueuePatient) => void;
  onUpdateStatus?: (patientId: string, status: QueueStatus) => void;
  onSkip?: (patientId: string) => void;
}) {
  return (
    <div
      className={`p-6 hover:bg-gray-50 transition-colors ${
        patient.status === "in-service" ? "bg-blue-50" : ""
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        {/* Left Section: Queue Number & Patient Info */}
        <div className="flex-1">
          <div className="flex items-center gap-4 mb-3">
            {/* Queue Number */}
            <div
              className={`w-16 h-16 rounded-lg flex items-center justify-center text-2xl font-bold ${
                patient.status === "in-service"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700"
              }`}
            >
              {patient.queueNumber}
            </div>

            {/* Patient Info */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-lg font-semibold text-gray-900">{patient.name}</h3>
                <StatusBadge status={patient.status} />
              </div>

              <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600">
                <span>RM: {patient.rmNumber}</span>
                <span>•</span>
                <span>{patient.age} tahun</span>
                {patient.phone && (
                  <>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Phone className="w-3 h-3" />
                      {patient.phone}
                    </span>
                  </>
                )}
              </div>

              {/* Priority Badges */}
              {patient.priorities.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {patient.priorities.map((priority) => (
                    <PriorityBadge key={priority} type={priority} />
                  ))}
                </div>
              )}

              {/* Triage Badge (Emergency Only) */}
              {patient.triageLevel && (
                <div className="mt-2">
                  <TriageBadge level={patient.triageLevel} />
                </div>
              )}
            </div>
          </div>

          {/* Check-in Time & Wait Time */}
          <div className="flex items-center gap-4 text-sm ml-20">
            <div className="flex items-center gap-1 text-gray-600">
              <Calendar className="w-4 h-4" />
              <span>Check-in: {patient.checkInTime}</span>
            </div>
            <div className="flex items-center gap-1 text-gray-600">
              <Clock className="w-4 h-4" />
              <span>Tunggu: {patient.waitTime}</span>
            </div>
          </div>
        </div>

        {/* Right Section: Actions */}
        <div className="flex flex-col gap-2">
          {patient.status === "waiting" && (
            <>
              <button
                type="button"
                onClick={() => onCallPatient?.(patient)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
              >
                Panggil
              </button>
              <button
                type="button"
                onClick={() => onSkip?.(patient.id)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm font-medium"
              >
                Lewati
              </button>
            </>
          )}

          {patient.status === "in-service" && (
            <>
              <button
                type="button"
                onClick={() => onUpdateStatus?.(patient.id, "completed")}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium"
              >
                Selesai
              </button>
              <button
                type="button"
                onClick={() => onUpdateStatus?.(patient.id, "waiting")}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm font-medium"
              >
                Kembali ke Antrian
              </button>
            </>
          )}

          {patient.status === "completed" && (
            <div className="px-4 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium">
              Selesai
            </div>
          )}

          {patient.status === "skipped" && (
            <div className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium">
              Dilewati
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Queue List Component
 */
export function QueueList({
  patients,
  departmentLabel,
  onCallPatient,
  onUpdateStatus,
  onSkip,
}: {
  patients: QueuePatient[];
  departmentLabel: string;
  onCallPatient?: (patient: QueuePatient) => void;
  onUpdateStatus?: (patientId: string, status: QueueStatus) => void;
  onSkip?: (patientId: string) => void;
}) {
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      {/* Queue Header */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
        <h2 className="text-xl font-semibold text-white">
          Antrian {departmentLabel}
        </h2>
      </div>

      {/* Queue Items */}
      <div className="divide-y divide-gray-200">
        {patients.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            <Users className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium">Tidak ada antrian</p>
            <p className="text-sm">Belum ada pasien yang mendaftar untuk poli ini</p>
          </div>
        ) : (
          patients.map((patient) => (
            <QueueItem
              key={patient.id}
              patient={patient}
              onCallPatient={onCallPatient}
              onUpdateStatus={onUpdateStatus}
              onSkip={onSkip}
            />
          ))
        )}
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

/**
 * Queue Dashboard Component
 */
export function QueueDashboard({
  patients,
  departments,
  onCallNext,
  onUpdateStatus,
  onRefresh,
  onExportPDF,
  defaultDepartment = "igd",
  className = "",
}: QueueDashboardProps) {
  const [selectedDepartment, setSelectedDepartment] = useState(defaultDepartment);
  const [queueData, setQueueData] = useState<QueuePatient[]>(patients);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [isCalling, setIsCalling] = useState(false);

  /**
   * Filter queue by selected department
   */
  const filteredQueue = useMemo(() => {
    return queueData.filter((patient) => patient.department === selectedDepartment);
  }, [queueData, selectedDepartment]);

  /**
   * Calculate statistics for selected department
   */
  const statistics = useMemo((): QueueStatistics => {
    const deptQueue = filteredQueue;
    return {
      waiting: deptQueue.filter((p) => p.status === "waiting").length,
      inService: deptQueue.filter((p) => p.status === "in-service").length,
      completed: deptQueue.filter((p) => p.status === "completed").length,
      avgWaitTime: "15 menit", // Mock average
    };
  }, [filteredQueue]);

  /**
   * Simulate real-time updates
   */
  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  /**
   * Call next patient
   */
  const handleCallNext = async () => {
    const nextPatient = filteredQueue.find((p) => p.status === "waiting");
    if (!nextPatient) return;

    setIsCalling(true);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));

    setQueueData((prev) =>
      prev.map((p) =>
        p.id === nextPatient.id ? { ...p, status: "in-service" as const } : p
      )
    );

    onCallNext?.(nextPatient);
    setIsCalling(false);
  };

  /**
   * Handle call patient from list
   */
  const handleCallPatient = (patient: QueuePatient) => {
    setQueueData((prev) =>
      prev.map((p) =>
        p.id === patient.id ? { ...p, status: "in-service" as const } : p
      )
    );
    onCallNext?.(patient);
  };

  /**
   * Update patient status
   */
  const handleUpdateStatus = (patientId: string, newStatus: QueueStatus) => {
    setQueueData((prev) =>
      prev.map((p) =>
        p.id === patientId ? { ...p, status: newStatus } : p
      )
    );
    onUpdateStatus?.(patientId, newStatus);
  };

  /**
   * Skip patient
   */
  const handleSkip = (patientId: string) => {
    setQueueData((prev) =>
      prev.map((p) =>
        p.id === patientId ? { ...p, status: "skipped" as const } : p
      )
    );
  };

  /**
   * Refresh queue data
   */
  const handleRefresh = () => {
    setLastUpdate(new Date());
    onRefresh?.();
  };

  /**
   * Export queue to PDF
   */
  const handleExportPDF = () => {
    onExportPDF?.();
  };

  const selectedDeptConfig = departments.find((d) => d.value === selectedDepartment);

  return (
    <div className={`min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-white ${className}`}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Dashboard Antrian</h1>
                <p className="text-sm text-gray-600">
                  Terakhir diperbarui: {lastUpdate.toLocaleTimeString("id-ID")}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={handleRefresh}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2 text-sm font-medium"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
              <button
                type="button"
                onClick={handleExportPDF}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 text-sm font-medium"
              >
                <Download className="w-4 h-4" />
                Export PDF
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Department Tabs */}
        <DepartmentTabs
          departments={departments}
          selectedDepartment={selectedDepartment}
          onSelect={setSelectedDepartment}
          queueData={queueData}
        />

        {/* Statistics Cards */}
        <QueueStatisticsCards statistics={statistics} />

        {/* Action Bar */}
        <div className="bg-white rounded-xl shadow-md p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={handleCallNext}
                disabled={statistics.waiting === 0 || isCalling}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Bell className="w-5 h-5" />
                {isCalling ? "Memanggil..." : "Panggil Berikutnya"}
              </button>
              {selectedDepartment === "igd" && (
                <span className="text-sm text-red-600 font-medium flex items-center gap-1">
                  <AlertTriangle className="w-4 h-4" />
                  Prioritas IGD
                </span>
              )}
            </div>

            <div className="text-sm text-gray-600">
              Total Antrian: {filteredQueue.length} pasien
            </div>
          </div>
        </div>

        {/* Queue List */}
        <QueueList
          patients={filteredQueue}
          departmentLabel={selectedDeptConfig?.label || ""}
          onCallPatient={handleCallPatient}
          onUpdateStatus={handleUpdateStatus}
          onSkip={handleSkip}
        />
      </div>
    </div>
  );
}

export default QueueDashboard;
