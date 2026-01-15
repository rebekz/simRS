"use client";

import { useState, useEffect, useMemo } from "react";
import {
  Users,
  Clock,
  User,
  Calendar,
  Phone,
  Baby,
  Accessibility,
  AlertTriangle,
  Bell,
  CheckCircle,
  XCircle,
  MoreVertical,
  Download,
  RefreshCw,
  Timer,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";

/**
 * WEB-S-3.3: Queue Management Dashboard
 *
 * Key Features:
 * - Real-time queue monitoring by department
 * - Patient details with queue numbers and wait times
 * - Status management (waiting, in-service, completed)
 * - Priority indicators (elderly, pregnant, disabled)
 * - Emergency queue for IGD
 * - Queue statistics
 * - Call next patient functionality
 * - Export to PDF
 */

// ============================================================================
// TYPES
// ============================================================================

type QueueStatus = "waiting" | "in-service" | "completed" | "skipped";

type PriorityType = "elderly" | "pregnant" | "disabled" | "emergency";

interface QueuePatient {
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
  triageLevel?: "merah" | "kuning" | "hijau";
  phone?: string;
}

interface QueueStatistics {
  waiting: number;
  inService: number;
  completed: number;
  avgWaitTime: string;
}

// ============================================================================
// MOCK DATA
// ============================================================================

const MOCK_QUEUE_PATIENTS: QueuePatient[] = [
  // Poli Anak (Children)
  {
    id: "1",
    rmNumber: "RM2024001",
    name: "AHMAD SUSANTO",
    queueNumber: "ANA-001",
    department: "ana",
    status: "in-service",
    checkInTime: "08:15",
    waitTime: "15 menit",
    age: 8,
    priorities: [],
    phone: "081234567890",
  },
  {
    id: "2",
    rmNumber: "RM2024002",
    name: "SITI RAHAYU",
    queueNumber: "ANA-002",
    department: "ana",
    status: "waiting",
    checkInTime: "08:30",
    waitTime: "0 menit",
    age: 5,
    priorities: [],
    phone: "081234567891",
  },
  {
    id: "3",
    rmNumber: "RM2024003",
    name: "BUDI SANTOSO",
    queueNumber: "ANA-003",
    department: "ana",
    status: "waiting",
    checkInTime: "08:45",
    waitTime: "0 menit",
    age: 12,
    priorities: ["disabled"],
    phone: "081234567892",
  },
  {
    id: "4",
    rmNumber: "RM2024004",
    name: "DEWI LESTARI",
    queueNumber: "ANA-004",
    department: "ana",
    status: "completed",
    checkInTime: "07:45",
    waitTime: "45 menit",
    age: 6,
    priorities: [],
    phone: "081234567893",
  },
  {
    id: "5",
    rmNumber: "RM2024005",
    name: "EKO PRASETYO",
    queueNumber: "ANA-005",
    department: "ana",
    status: "waiting",
    checkInTime: "08:50",
    waitTime: "0 menit",
    age: 10,
    priorities: [],
    phone: "081234567894",
  },

  // Poli Penyakit Dalam (Internal Medicine)
  {
    id: "6",
    rmNumber: "RM2024006",
    name: "RINA WATI",
    queueNumber: "INT-001",
    department: "int",
    status: "in-service",
    checkInTime: "08:00",
    waitTime: "30 menit",
    age: 45,
    priorities: ["elderly"],
    phone: "081234567895",
  },
  {
    id: "7",
    rmNumber: "RM2024007",
    name: "AGUS SETIAWAN",
    queueNumber: "INT-002",
    department: "int",
    status: "waiting",
    checkInTime: "08:20",
    waitTime: "10 menit",
    age: 52,
    priorities: ["elderly"],
    phone: "081234567896",
  },
  {
    id: "8",
    rmNumber: "RM2024008",
    name: "LILIS SURYANI",
    queueNumber: "INT-003",
    department: "int",
    status: "waiting",
    checkInTime: "08:35",
    waitTime: "0 menit",
    age: 38,
    priorities: ["pregnant"],
    phone: "081234567897",
  },
  {
    id: "9",
    rmNumber: "RM2024009",
    name: "DEDI KURNIAWAN",
    queueNumber: "INT-004",
    department: "int",
    status: "completed",
    checkInTime: "07:30",
    waitTime: "1 jam",
    age: 48,
    priorities: [],
    phone: "081234567898",
  },

  // IGD (Emergency)
  {
    id: "10",
    rmNumber: "RM2024010",
    name: "SUTRISNO",
    queueNumber: "IGD-001",
    department: "igd",
    status: "in-service",
    checkInTime: "08:10",
    waitTime: "5 menit",
    age: 55,
    priorities: ["emergency"],
    triageLevel: "merah",
    phone: "081234567899",
  },
  {
    id: "11",
    rmNumber: "RM2024011",
    name: "MURNIATI",
    queueNumber: "IGD-002",
    department: "igd",
    status: "waiting",
    checkInTime: "08:25",
    waitTime: "0 menit",
    age: 62,
    priorities: ["emergency", "elderly"],
    triageLevel: "kuning",
    phone: "081234567900",
  },
  {
    id: "12",
    rmNumber: "RM2024012",
    name: "JOKO SUSILO",
    queueNumber: "IGD-003",
    department: "igd",
    status: "waiting",
    checkInTime: "08:40",
    waitTime: "0 menit",
    age: 35,
    priorities: ["emergency"],
    triageLevel: "hijau",
    phone: "081234567901",
  },
];

const DEPARTMENTS = [
  { value: "igd", label: "IGD", color: "red", priority: true },
  { value: "ana", label: "Poli Anak", color: "blue", priority: false },
  { value: "int", label: "Penyakit Dalam", color: "green", priority: false },
  { value: "bed", label: "Poli Bedah", color: "purple", priority: false },
  { value: "obg", label: "Poli Kandungan", color: "pink", priority: false },
  { value: "mat", label: "Poli Mata", color: "teal", priority: false },
];

// ============================================================================
// COMPONENTS
// ============================================================================

/**
 * Status Badge Component
 */
function StatusBadge({ status }: { status: QueueStatus }) {
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
function PriorityBadge({ type }: { type: PriorityType }) {
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
function TriageBadge({ level }: { level: "merah" | "kuning" | "hijau" }) {
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

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function QueueDashboardPage() {
  const [selectedDepartment, setSelectedDepartment] = useState("igd");
  const [queueData, setQueueData] = useState<QueuePatient[]>(MOCK_QUEUE_PATIENTS);
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
   * Get department counts for tabs
   */
  const departmentCounts = useMemo(() => {
    return DEPARTMENTS.map((dept) => ({
      ...dept,
      count: queueData.filter((p) => p.department === dept.value && p.status !== "completed" && p.status !== "skipped")
        .length,
    }));
  }, [queueData]);

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

    setIsCalling(false);
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
  };

  /**
   * Skip patient
   */
  const handleSkip = async (patientId: string) => {
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
  };

  /**
   * Export queue to PDF
   */
  const handleExportPDF = () => {
    alert("Fitur export PDF akan segera tersedia");
  };

  const selectedDeptConfig = DEPARTMENTS.find((d) => d.value === selectedDepartment);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-white">
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
        <div className="bg-white rounded-xl shadow-md p-2 mb-6">
          <div className="flex gap-2 overflow-x-auto">
            {departmentCounts.map((dept) => (
              <button
                key={dept.value}
                type="button"
                onClick={() => setSelectedDepartment(dept.value)}
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

        {/* Statistics Cards */}
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
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          {/* Queue Header */}
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
            <h2 className="text-xl font-semibold text-white">
              Antrian {selectedDeptConfig?.label}
            </h2>
          </div>

          {/* Queue Items */}
          <div className="divide-y divide-gray-200">
            {filteredQueue.length === 0 ? (
              <div className="p-12 text-center text-gray-500">
                <Users className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium">Tidak ada antrian</p>
                <p className="text-sm">Belum ada pasien yang mendaftar untuk poli ini</p>
              </div>
            ) : (
              filteredQueue.map((patient) => (
                <div
                  key={patient.id}
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
                            onClick={() => handleUpdateStatus(patient.id, "in-service")}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
                          >
                            Panggil
                          </button>
                          <button
                            type="button"
                            onClick={() => handleSkip(patient.id)}
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
                            onClick={() => handleUpdateStatus(patient.id, "completed")}
                            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium"
                          >
                            Selesai
                          </button>
                          <button
                            type="button"
                            onClick={() => handleUpdateStatus(patient.id, "waiting")}
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
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
